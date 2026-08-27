[CmdletBinding(SupportsShouldProcess)]
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
$target = Get-TargetConfig -TargetConfig $targetsConfig -TargetName $TargetName
$targetNameResolved = $target["Name"]
$targetConfig = $target["Config"]

$installRoot = $targetConfig["path"]
if ($installRoot -like "REPLACE_WITH*") {
    throw "Target '$targetNameResolved' still uses a placeholder path."
}

$backupRoot = Resolve-WorkspacePath "logs/source-backups"
New-Item -ItemType Directory -Force -Path $backupRoot | Out-Null

$skills = Get-PublishedSkills -SkillsConfig $skillsConfig -SkillName $SkillName
if ($skills.Count -eq 0) {
    throw "No published skills matched the requested filter."
}

foreach ($skill in $skills) {
    $publishName = Get-SkillPublishName -Skill $skill
    $sourcePathRelative = Get-SkillSourcePath -Skill $skill
    $repoRoot = Get-RepoPath -SkillsConfig $skillsConfig -RepoName $skill["repo"]
    $sourcePath = Join-Path $repoRoot $sourcePathRelative
    $targetPath = Join-Path $installRoot $publishName

    if (-not (Test-Path -LiteralPath $targetPath)) {
        Write-Warning "Skip '$publishName': install path not found: $targetPath"
        continue
    }

    if ($PSCmdlet.ShouldProcess($sourcePath, "Capture hotfix from $targetPath")) {
        if (Test-Path -LiteralPath $sourcePath) {
            $backup = Backup-Directory -SourcePath $sourcePath -BackupRoot $backupRoot -Name $publishName
            Write-Host "Backed up source $publishName to $backup"
            Remove-Item -LiteralPath $sourcePath -Recurse -Force
        }

        Copy-DirectoryFiltered -SourcePath $targetPath -DestinationPath $sourcePath
        Write-Host "Captured $publishName -> $sourcePath"
    }
}
