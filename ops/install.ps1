[CmdletBinding()]
param(
    [string]$TargetName,
    [string[]]$SkillName
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "lib.ps1")

$skillsConfig = Get-SkillsManifest
$targetsConfig = Get-InstallTargetsManifest

# Resolve the targets to install: an explicit -TargetName installs only that
# target; otherwise install to every enabled target in install-targets.toml.
if ($TargetName) {
    $targets = @(Get-TargetConfig -TargetConfig $targetsConfig -TargetName $TargetName)
}
else {
    $targets = @(Get-EnabledTargets -TargetConfig $targetsConfig)
}

$skills = Get-PublishedSkills -SkillsConfig $skillsConfig -SkillName $SkillName
if ($skills.Count -eq 0) {
    throw "No published skills matched the requested filter."
}

foreach ($target in $targets) {
    $targetNameResolved = $target["Name"]
    $targetConfig = $target["Config"]

    if ($targetConfig["enabled"] -ne $true) {
        throw "Target '$targetNameResolved' is disabled. Update manifests/install-targets.toml first."
    }

    $installRoot = $targetConfig["path"]
    if ($installRoot -like "REPLACE_WITH*") {
        throw "Target '$targetNameResolved' still uses a placeholder path."
    }

    $backupRoot = Resolve-WorkspacePath $targetConfig["backup_root"]
    New-Item -ItemType Directory -Force -Path $installRoot | Out-Null
    New-Item -ItemType Directory -Force -Path $backupRoot | Out-Null

    Write-Host ""
    Write-Host "=== Installing to target: $targetNameResolved -> $installRoot ==="

    # Pre-flight: judge every skill against the target BEFORE touching anything,
    # so an IDE-side edit can never be clobbered halfway through a batch.
    $plan = @()
    $conflicts = @()
    foreach ($skill in $skills) {
        $publishName = Get-SkillPublishName -Skill $skill
        $sourcePathRelative = Get-SkillSourcePath -Skill $skill
        $repoRoot = Get-RepoPath -SkillsConfig $skillsConfig -RepoName $skill["repo"]
        $sourcePath = Join-Path $repoRoot $sourcePathRelative
        $targetPath = Join-Path $installRoot $publishName

        if (-not (Test-Path -LiteralPath $sourcePath)) {
            Write-Warning "Skip '$publishName': source path not found: $sourcePath"
            continue
        }

        $conflict = Test-InstallConflict -TargetName $targetNameResolved -PublishName $publishName -TargetPath $targetPath -SourcePath $sourcePath
        if ($conflict.Conflict) {
            $conflicts += @{ PublishName = $publishName; Reason = $conflict.Reason }
            continue
        }

        $plan += @{
            Skill = $skill
            PublishName = $publishName
            SourcePath = $sourcePath
            TargetPath = $targetPath
            SourceMap = (Get-FileHashMap -RootPath $sourcePath)
        }
    }

    if ($conflicts.Count -gt 0) {
        foreach ($conflict in $conflicts) {
            Write-Warning "CONFLICT: $($conflict.Reason)"
        }

        throw "Install aborted before any change: $($conflicts.Count) skill(s) on '$targetNameResolved' are not in a clean (repo-matching) state, so nothing was written. `n" +
              "The installer never overwrites a diverged target - choose how to resolve the divergence: `n" +
              "  - To KEEP the installed copy (it is a deliberate edit): first run 'ops/capture_hotfix.ps1 -TargetName <target> -SkillName <name>' to fold it back into source, then re-run this install. `n" +
              "  - To DISCARD it and redeploy from source: run 'ops/uninstall.ps1 -TargetName <target> -SkillName <name>' (backs up first), then re-run this install."
    }

    foreach ($entry in $plan) {
        $publishName = $entry.PublishName

        if (Test-Path -LiteralPath $entry.TargetPath) {
            $backup = Backup-Directory -SourcePath $entry.TargetPath -BackupRoot $backupRoot -Name $publishName
            Write-Host "Backed up $publishName to $backup"
            Remove-Item -LiteralPath $entry.TargetPath -Recurse -Force
        }

        Copy-DirectoryFiltered -SourcePath $entry.SourcePath -DestinationPath $entry.TargetPath
        Set-SkillInstallState -TargetName $targetNameResolved -PublishName $publishName -InstalledAt (Get-Date) -FileManifest $entry.SourceMap
        Write-Host "Installed $publishName <- $($entry.SourcePath)"
    }
}

Write-Host ""
Write-Host "Install complete for $($targets.Count) target(s)."
