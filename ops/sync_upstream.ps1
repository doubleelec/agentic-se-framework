[CmdletBinding()]
param(
    [string]$Branch,
    [switch]$BootstrapIfMissing
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "lib.ps1")

function Invoke-GitAndCaptureExitCode {
    param(
        [Parameter(Mandatory)]
        [string[]]$Arguments
    )

    & git @Arguments | Out-Host
    return [int]$LASTEXITCODE
}

function Initialize-ReportFile {
    param(
        [Parameter(Mandatory)]
        [string]$Path,

        [Parameter(Mandatory)]
        [AllowEmptyString()]
        [string[]]$Lines
    )

    [System.IO.File]::WriteAllLines($Path, $Lines, [System.Text.Encoding]::UTF8)
}

function Add-ReportLines {
    param(
        [Parameter(Mandatory)]
        [string]$Path,

        [Parameter(Mandatory)]
        [AllowEmptyString()]
        [string[]]$Lines
    )

    [System.IO.File]::AppendAllLines($Path, $Lines, [System.Text.Encoding]::UTF8)
}

$skillsConfig = Get-SkillsManifest
$upstreamLock = Get-UpstreamLockManifest
$upstreamConfig = $skillsConfig["repos"]["mattpocock_upstream"]
$upstreamRoot = Get-RepoPath -SkillsConfig $skillsConfig -RepoName "mattpocock_upstream"
$localRoot = Get-RepoPath -SkillsConfig $skillsConfig -RepoName "mattpocock_local"
$upstreamRemote = $upstreamConfig["remote"]

if (-not $Branch) {
    $Branch = $upstreamConfig["default_branch"]
}

if (-not (Test-Path -LiteralPath (Join-Path $upstreamRoot ".git"))) {
    if (-not $BootstrapIfMissing) {
        Write-Warning "Upstream clone not found."
        Write-Host "Re-run with -BootstrapIfMissing to clone automatically."
        Write-Host "Manual clone command:"
        Write-Host "  git clone $upstreamRemote `"$upstreamRoot`""
        exit 0
    }

    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $upstreamRoot) | Out-Null
    $cloneExitCode = Invoke-GitAndCaptureExitCode -Arguments @("clone", $upstreamRemote, $upstreamRoot)
    if ($cloneExitCode -ne 0) {
        throw "Failed to clone upstream repository from '$upstreamRemote' (exit code $cloneExitCode)."
    }
}

Write-Host "Fetching upstream in $upstreamRoot"
$syncWarnings = New-Object System.Collections.Generic.List[string]

$fetchExitCode = Invoke-GitAndCaptureExitCode -Arguments @("-C", $upstreamRoot, "fetch", "--all", "--prune")
if ($fetchExitCode -ne 0) {
    $syncWarnings.Add("Fetch failed; continuing with the existing local upstream snapshot.")
}

$checkoutExitCode = Invoke-GitAndCaptureExitCode -Arguments @("-C", $upstreamRoot, "checkout", $Branch)
if ($checkoutExitCode -ne 0) {
    throw "Failed to checkout upstream branch '$Branch' (exit code $checkoutExitCode)."
}

$pullExitCode = Invoke-GitAndCaptureExitCode -Arguments @("-C", $upstreamRoot, "pull", "--ff-only", "origin", $Branch)
if ($pullExitCode -ne 0) {
    $syncWarnings.Add("Pull failed; report is based on the current local upstream snapshot.")
}

Write-Host ""
Write-Host "Upstream status:"
$statusExitCode = Invoke-GitAndCaptureExitCode -Arguments @("-C", $upstreamRoot, "status", "-sb")
if ($statusExitCode -ne 0) {
    throw "Failed to read upstream status (exit code $statusExitCode)."
}

$currentCommit = (& git -C $upstreamRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) {
    throw "Failed to resolve upstream HEAD commit (exit code $LASTEXITCODE)."
}
$trackedCommit = $upstreamLock["upstream"]["tracked_commit"]

$skills = Get-PublishedSkills -SkillsConfig $skillsConfig
$reportRoot = Resolve-WorkspacePath "logs/reports"
New-Item -ItemType Directory -Force -Path $reportRoot | Out-Null
$reportFile = Join-Path $reportRoot ("upstream-diff-" + (Get-Date -Format "yyyyMMdd-HHmmss") + ".txt")

Initialize-ReportFile -Path $reportFile -Lines @("Upstream diff report")
Add-ReportLines -Path $reportFile -Lines @(
    "Remote        : $upstreamRemote"
    "Branch        : $Branch"
    "Current commit: $currentCommit"
    "Tracked commit: $trackedCommit"
)

if ($syncWarnings.Count -eq 0) {
    Add-ReportLines -Path $reportFile -Lines @("Sync status   : refreshed")
} else {
    Add-ReportLines -Path $reportFile -Lines @("Sync status   : stale_local_snapshot")
    foreach ($warning in $syncWarnings) {
        Add-ReportLines -Path $reportFile -Lines @("Warning       : $warning")
    }
}

foreach ($skill in $skills) {
    if (-not $skill.ContainsKey("upstream_repo")) {
        continue
    }

    $publishName = Get-SkillPublishName -Skill $skill
    $sourcePathRelative = Get-SkillSourcePath -Skill $skill
    $localPath = Join-Path $localRoot $sourcePathRelative
    $lockEntry = Get-UpstreamLockEntry -UpstreamLock $upstreamLock -PublishName $publishName

    Add-ReportLines -Path $reportFile -Lines @(
        ""
        "=== $publishName ==="
        "Local   : $localPath"
    )

    if (-not $lockEntry) {
        Add-ReportLines -Path $reportFile -Lines @("Status  : missing_from_upstream_lock")
        continue
    }

    if ($lockEntry["source_path"] -ne $sourcePathRelative) {
        Add-ReportLines -Path $reportFile -Lines @(
            "Status  : source_path_mismatch"
            "Manifest: $sourcePathRelative"
            "Lock    : $($lockEntry["source_path"])"
        )
        continue
    }

    $status = $lockEntry["status"]
    Add-ReportLines -Path $reportFile -Lines @("Status  : $status")

    if (-not $lockEntry.ContainsKey("upstream_path")) {
        Add-ReportLines -Path $reportFile -Lines @("Upstream: none")
        continue
    }

    $upstreamPath = Join-Path $upstreamRoot $lockEntry["upstream_path"]
    Add-ReportLines -Path $reportFile -Lines @("Upstream: $upstreamPath")

    if ((Test-Path -LiteralPath $upstreamPath) -and (Test-Path -LiteralPath $localPath)) {
        $diffOutput = & git diff --no-index --stat -- $upstreamPath $localPath 2>&1
        $diffExitCode = $LASTEXITCODE
        if ($diffExitCode -gt 1) {
            throw "git diff failed for '$publishName' with exit code $diffExitCode."
        }
        $global:LASTEXITCODE = 0
        if (-not $diffOutput) {
            $diffOutput = "No diff."
        }
        Add-ReportLines -Path $reportFile -Lines @($diffOutput)
    } else {
        Add-ReportLines -Path $reportFile -Lines @("Missing upstream or local path.")
    }
}

Write-Host ""
Write-Host "Report written to $reportFile"

if ($syncWarnings.Count -gt 0) {
    foreach ($warning in $syncWarnings) {
        Write-Warning $warning
    }
    $global:LASTEXITCODE = 1
    exit 1
}

$global:LASTEXITCODE = 0
