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
$target = Get-TargetConfig -TargetConfig $targetsConfig -TargetName $TargetName
$targetNameResolved = $target["Name"]
$targetConfig = $target["Config"]

$installRoot = $targetConfig["path"]
if ($installRoot -like "REPLACE_WITH*") {
    throw "Target '$targetNameResolved' still uses a placeholder path."
}

$skills = @(Get-PublishedSkills -SkillsConfig $skillsConfig -SkillName $SkillName)
if ($skills.Count -eq 0) {
    throw "No published skills matched the requested filter."
}

foreach ($skill in $skills) {
    $publishName = Get-SkillPublishName -Skill $skill
    $sourcePathRelative = Get-SkillSourcePath -Skill $skill
    $repoRoot = Get-RepoPath -SkillsConfig $skillsConfig -RepoName $skill["repo"]
    $sourcePath = Join-Path $repoRoot $sourcePathRelative
    $targetPath = Join-Path $installRoot $publishName

    $sourceMap = Get-FileHashMap -RootPath $sourcePath
    $targetMap = Get-FileHashMap -RootPath $targetPath

    $sourceKeys = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    $targetKeys = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)

    foreach ($key in $sourceMap.Keys) { [void]$sourceKeys.Add($key) }
    foreach ($key in $targetMap.Keys) { [void]$targetKeys.Add($key) }

    $missingInInstall = @($sourceKeys | Where-Object { -not $targetKeys.Contains($_) } | Sort-Object)
    $extraInInstall = @($targetKeys | Where-Object { -not $sourceKeys.Contains($_) } | Sort-Object)
    $changed = @(
        $sourceKeys |
        Where-Object { $targetKeys.Contains($_) -and $sourceMap[$_] -ne $targetMap[$_] } |
        Sort-Object
    )

    Write-Host ""
    Write-Host "=== $publishName ==="
    Write-Host "Source : $sourcePath"
    Write-Host "Install: $targetPath"

    if (($missingInInstall.Count + $extraInInstall.Count + $changed.Count) -eq 0) {
        Write-Host "Status : clean"
        continue
    }

    Write-Host "Status : drift detected"

    if ($missingInInstall.Count -gt 0) {
        Write-Host "Missing in install:"
        $missingInInstall | ForEach-Object { Write-Host "  $_" }
    }

    if ($extraInInstall.Count -gt 0) {
        Write-Host "Extra in install:"
        $extraInInstall | ForEach-Object { Write-Host "  $_" }
    }

    if ($changed.Count -gt 0) {
        Write-Host "Changed:"
        $changed | ForEach-Object { Write-Host "  $_" }
    }
}

# Rule 2 of target hygiene: report unknown directories, never touch them.
# Install targets are shared scopes; an unmanifested directory may belong to
# another project or be a retired skill awaiting cleanup. Investigate first
# (e.g. git log -S <name> -- manifests/skills.toml, plus logs/ backups).
$managedNames = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
foreach ($published in @(Get-PublishedSkills -SkillsConfig $skillsConfig)) {
    [void]$managedNames.Add((Get-SkillPublishName -Skill $published))
}

$unknown = @(
    Get-ChildItem -LiteralPath $installRoot -Directory |
    Where-Object { -not $managedNames.Contains($_.Name) } |
    Sort-Object Name
)

if ($unknown.Count -gt 0) {
    Write-Host ""
    Write-Host "=== Unknown directories on target '$targetNameResolved' (reported only, NOT managed by this repo) ==="
    $unknown | ForEach-Object { Write-Warning "Unknown skill directory: $($_.Name)" }
}
