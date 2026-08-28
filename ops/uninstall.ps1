<#
Rule 1 of target hygiene: retiring a skill is a two-step operation --
remove its [[skill]] entry from manifests/skills.toml AND run this script
so every enabled target stops carrying the retired copy. A manifest-only
retirement leaves orphan installs that no pipeline tool can see again.

This script always backs up before removing, so retirement stays reversible.
(Rule 2 -- unknown directories are reported by diff_installed.ps1, never
deleted on sight -- because install targets are shared across projects.)
#>
[CmdletBinding()]
param(
    [string]$TargetName,

    [Parameter(Mandatory)]
    [string[]]$SkillName
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "lib.ps1")

$skillsConfig = Get-SkillsManifest
$targetsConfig = Get-InstallTargetsManifest

if ($TargetName) {
    $targets = @(Get-TargetConfig -TargetConfig $targetsConfig -TargetName $TargetName)
}
else {
    $targets = @(Get-EnabledTargets -TargetConfig $targetsConfig)
}

$skills = @(Get-PublishedSkills -SkillsConfig $skillsConfig -SkillName $SkillName)
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

    Write-Host ""
    Write-Host "=== Uninstalling from target: $targetNameResolved -> $installRoot ==="

    foreach ($skill in $skills) {
        $publishName = Get-SkillPublishName -Skill $skill
        $targetPath = Join-Path $installRoot $publishName

        if (-not (Test-Path -LiteralPath $targetPath)) {
            Write-Warning "Skip '$publishName': not present on target '$targetNameResolved'."
            continue
        }

        $backup = Backup-Directory -SourcePath $targetPath -BackupRoot $backupRoot -Name $publishName
        Remove-Item -LiteralPath $targetPath -Recurse -Force

        $stateFile = Get-SkillInstallStateFile -TargetName $targetNameResolved -PublishName $publishName
        if (Test-Path -LiteralPath $stateFile) {
            Remove-Item -LiteralPath $stateFile -Force
        }

        Write-Host "Uninstalled $publishName (backed up to $backup)"
    }
}

Write-Host ""
Write-Host "Uninstall complete for $($targets.Count) target(s)."
