[CmdletBinding()]
param(
    # Optional free-text note appended to the release commit message.
    [string]$Note
)

# Release automation: build and push one cumulative sanitized snapshot to the
# public outlet. Canonical flow - AGENTS.md's manual command list documents
# what this does; run this script instead of typing those commands by hand.
#
# Hard gates that prevent the classic release failure modes:
#   1. "git fetch public" is a hard gate - a snapshot built on a stale
#      "public/main" base makes the next push a non-fast-forward rejection.
#   2. public-main is reset to the exact remote tip before overlaying, so a
#      push from this script is always a fast-forward.
#   3. The commit is skipped when the overlay produces no delta - rebuilding
#      an identical snapshot would diverge public-main from public/main.
#   4. The red-line scan must be empty before anything is committed.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Resolve the repo root (this script lives in ops/).
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $repoRoot

function Assert-LastExit([string]$Step) {
    if ($LASTEXITCODE -ne 0) {
        throw "Step failed: $Step (exit $LASTEXITCODE)."
    }
}

# -- 1. Sync from the public remote ------------------------------------------
git fetch public
Assert-LastExit "git fetch public (needs GitHub credentials; never build a snapshot on a stale base)"

git show-ref --verify --quiet refs/heads/public-main
if ($LASTEXITCODE -ne 0) {
    git checkout -B public-main public/main
    Assert-LastExit "git checkout -B public-main public/main"
}
else {
    git checkout public-main
    Assert-LastExit "git checkout public-main"
    git reset --hard public/main
    Assert-LastExit "git reset --hard public/main"
}

# -- 2. Overlay the milestone content from master -----------------------------
# Tracked files only; .gitignore keeps personal files out, and origin history
# is never copied. The overlay only adds/overwrites - a file that must stop
# shipping has to be removed explicitly (see docs/agents/release.md).
git checkout master -- .
Assert-LastExit "git checkout master -- ."

git add -A
$staged = @(git status --porcelain)

# -- 3. Idempotence: no delta means no new snapshot commit --------------------
if ($staged.Count -eq 0) {
    Write-Host "No tracked-file changes between master and public/main - nothing to release."
    git checkout master
    return
}

# -- 4. Red-line scan: must be empty before anything is committed -------------
$hits = @(git grep -I -i -n -E "doubleelec|qq\.com|weixin|[CDE]:[/\\]Users" -- . ":!docs/agents/release.md" ":!LICENSE" ":!README.md")
if ($hits.Count -gt 0) {
    git reset --hard public/main | Out-Null
    git checkout master
    throw ("Red-line scan found private-signal matches; snapshot aborted and public-main restored")
}

if ($staged | Where-Object { $_ -match "install-targets\.toml" }) {
    git reset --hard public/main | Out-Null
    git checkout master
    throw "manifests/install-targets.toml (personal) is staged; snapshot aborted."
}

# -- 5. Commit with the public identity, fingerprinting the master tip --------
$masterSha = (git rev-parse --short master)
$notePart = ""
if ($Note) { $notePart = " ($Note)" }
git -c user.name="agentic-se-framework" -c user.email="public-noreply@example.com" commit -m "chore: release agentic-se-framework (master@$masterSha)$notePart"
Assert-LastExit "release commit"

# -- 6. Push -------------------------------------------------------------------
git push public public-main:main
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Push failed. The snapshot commit is safe on local 'public-main'; do NOT rebuild it - rebuilding diverges the branch."
    Write-Host "Retry from a terminal that has GitHub credentials:"
    Write-Host "  git checkout public-main; git push public public-main:main; git checkout master"
    git checkout master
    exit 2
}

Write-Host "Release pushed: public/main advanced to the new snapshot."
git checkout master
