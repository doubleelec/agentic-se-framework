[CmdletBinding()]
param(
    # Optional free-text note appended to the release commit message.
    [string]$Note,
    
    # By default the script aborts when the working tree is dirty. Use
    # -AllowDirty to stash the working tree at the top and pop it at the end;
    # only do this for trivial untracked files (notes-draft, etc.).
    [switch]$AllowDirty,
    
    # By default the script aborts when local master is ahead of origin/master.
    # Use -AllowUnpushedMaster to release anyway (e.g. when you intentionally
    # committed in this terminal and will push origin in a separate step).
    [switch]$AllowUnpushedMaster
)

# Release automation: build and push one cumulative sanitized snapshot to the
# public outlet. Canonical flow - AGENTS.md's manual command list documents
# what this does; run this script instead of typing those commands by hand.
#
# Pre-flight (hard, non-negotiable):
#   * Current branch MUST be `master` (never release from a feature branch,
#     detached HEAD, or public-main).
#   * Working tree MUST be clean by default (no uncommitted or untracked
#     files). Use -AllowDirty only for trivial untracked scratch that you
#     know is safe to stash-and-pop.
#   * Local `master` MUST be in sync with `origin/master` by default. Use
#     -AllowUnpushedMaster only when you intentionally committed in this
#     terminal and will push origin separately.
#
# During the run:
#   * `git fetch public` is a hard gate - a snapshot built on a stale
#     `public/main` base makes the next push a non-fast-forward rejection.
#   * public-main is reset to the exact remote tip before overlaying, so a
#     push from this script is always a fast-forward.
#   * The commit is skipped when the overlay produces no delta - rebuilding
#     an identical snapshot would diverge public-main from public/main.
#   * The red-line scan must be empty before anything is committed.
#
# Error codes (stable strings for log filtering and CI):
#   E_WRONG_BRANCH       - not on master
#   E_DIRTY_WORKTREE     - working tree not clean (and -AllowDirty not set)
#   E_MASTER_NOT_PUSHED  - local master ahead of origin/master (and
#                          -AllowUnpushedMaster not set)
#   E_FETCH_FAILED       - git fetch public failed (e.g. no creds)
#   E_REDLINE_HIT        - private-signal tokens found in snapshot
#   E_PERSONAL_FILE      - manifests/install-targets.toml is staged
#   E_PUSH_FAILED        - push rejected (commit is safe on local
#                          public-main, retry from a credentialed terminal)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $repoRoot

# Stash/cleanup state for the finally block.
$stashed = $false
$releaseBranch = ""
$restoreBranch = (git rev-parse --abbrev-ref HEAD)

function Die([string]$Code, [string]$Message) {
    # Emit a single structured error line to stderr and exit 3 (distinct
    # from mid-run failures which exit 2). Write-Host is used instead of
    # Write-Error because $ErrorActionPreference=Stop converts Write-Error
    # to a terminating error that prevents the exit 3 from executing.
    Write-Host "$Code`: $Message" -ForegroundColor Red
    exit 3
}

function Assert-LastExit([string]$Step) {
    if ($LASTEXITCODE -ne 0) {
        throw "Step failed: $Step (exit $LASTEXITCODE)."
    }
}

# -- PRE-FLIGHT: branch + working tree + sync, all before any destructive ----
#                action (no stash, no checkout, no fetch). -----------------
Write-Host "release.ps1 pre-flight: branch, working tree, sync checks"

# 1. Current branch must be `master`.
if ($restoreBranch -ne 'master') {
    Die 'E_WRONG_BRANCH' ("current branch is '$restoreBranch'; release.ps1 must be run from 'master'. Switch with: git checkout master")
}

# 2. Working tree must be clean (unless -AllowDirty).
$workingTreeDirty = @(git status --porcelain).Count -gt 0
if ($workingTreeDirty -and -not $AllowDirty) {
    Die 'E_DIRTY_WORKTREE' ("working tree is not clean; commit/stash/discard local changes first (or pass -AllowDirty to stash-and-pop untracked files):`n" + (git status --short | Out-String))
}

# 3. master must be in sync with origin/master (unless -AllowUnpushedMaster).
git fetch origin | Out-Null
if ($LASTEXITCODE -ne 0) {
    # fetch origin may fail in restricted environments; that doesn't block
    # the release itself (public fetch is the one that matters), but we
    # cannot verify sync without it. Refuse rather than guess.
    Die 'E_MASTER_NOT_PUSHED' 'git fetch origin failed; cannot verify local master is in sync with origin/master. Push the failed fetch through or run from a terminal with origin access.'
}
if (-not $AllowUnpushedMaster) {
    $ahead = git rev-list --count origin/master..master
    $behind = git rev-list --count master..origin/master
    if ($ahead -gt 0) {
        Die 'E_MASTER_NOT_PUSHED' ("local master is $ahead commit(s) ahead of origin/master. Push first (git push origin master) or pass -AllowUnpushedMaster.")
    }
    if ($behind -gt 0) {
        Die 'E_MASTER_NOT_PUSHED' ("local master is $behind commit(s) behind origin/master. Pull first (git pull --rebase origin master) or pass -AllowUnpushedMaster.")
    }
}

Write-Host "pre-flight OK; proceeding with release"

# Stash only AFTER pre-flight is green (so a dirty tree that pre-flight
# rejected never gets touched).
if ($workingTreeDirty -and $AllowDirty) {
    git stash push --include-untracked -m "release.ps1: pre-release stash" | Out-Null
    Assert-LastExit 'git stash push'
    $stashed = $true
}

try {
    # -- 1. Sync from the public remote ------------------------------------
    git fetch public
    if ($LASTEXITCODE -ne 0) {
        Die "E_FETCH_FAILED" "git fetch public failed (no GitHub credentials in this terminal, or network error). Do NOT build a snapshot on a stale base."
    }

    git show-ref --verify --quiet refs/heads/public-main
    if ($LASTEXITCODE -ne 0) {
        git checkout -B public-main public/main
        Assert-LastExit 'git checkout -B public-main public/main'
    }
    else {
        git checkout public-main
        Assert-LastExit 'git checkout public-main'
        git reset --hard public/main
        Assert-LastExit 'git reset --hard public/main'
    }
    $releaseBranch = "public-main"

    # -- 2. Overlay the milestone content from master -----------------------
    # Tracked files only; .gitignore keeps personal files out, and origin
    # history is never copied. The overlay only adds/overwrites - a file that
    # must stop shipping has to be removed explicitly (see release.md).
    git checkout master -- .
    Assert-LastExit 'git checkout master -- .'

    git add -A
    $staged = @(git status --porcelain)

    # -- 3. Idempotence: no delta means no new snapshot commit --------------
    if ($staged.Count -eq 0) {
        Write-Host "No tracked-file changes between master and public/main - nothing to release."
        return
    }

    # -- 4. Red-line scan: must be empty before anything is committed -------
    $hits = @(git grep -I -i -n -E "doubleelec|qq\.com|weixin|[CDE]:[/\\]Users" -- . ":!docs/agents/release.md" ":!ops/release.ps1" ":!LICENSE" ":!README.md")
    if ($hits.Count -gt 0) {
        Die "E_REDLINE_HIT" "private-signal tokens found in snapshot; aborting. Lines:`n$($hits -join "`n")"
    }

    if ($staged | Where-Object { $_ -match "install-targets.toml" }) {
        Die "E_PERSONAL_FILE" "manifests/install-targets.toml (personal) is staged; aborting."
    }

    # -- 5. Commit with the public identity, fingerprinting the master tip --
    $masterSha = (git rev-parse --short master)
    $notePart = ""
    if ($Note) { $notePart = " ($Note)" }
    git -c user.name="agentic-se-framework" -c user.email="public-noreply@example.com" commit -m "chore: release agentic-se-framework (master@$masterSha)$notePart"
    Assert-LastExit 'release commit'

    # -- 6. Push -----------------------------------------------------------
    git push public public-main:main
    if ($LASTEXITCODE -ne 0) {
        # Mid-run failure: commit is already safe on local public-main.
        # Distinct from E_PUSH_FAILED pre-flight (impossible), so it just
        # throws - the catch below formats the message.
        throw 'E_PUSH_FAILED: git push public public-main:main was rejected. The snapshot commit is safe on local public-main; do NOT rebuild it. Retry from a credentialed terminal: git checkout public-main; git push public public-main:main; git checkout $restoreBranch'
    }

    Write-Host "Release pushed: public/main advanced to the new snapshot."
}
catch {
    # Distinguish E_PUSH_FAILED (mid-run) from pre-flight (exit 3 above).
    # Just print the message and exit 2; the pre-flight Die already exited.
    Write-Warning $_.Exception.Message
    exit 2
}
finally {
    # Always return to the start branch and restore any stashed changes.
    git checkout $restoreBranch 2>$null | Out-Null
    if ($stashed) {
        git stash pop | Out-Null
    }
}
