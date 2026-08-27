Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-WorkspaceRoot {
    param(
        [string]$StartPath = $PSScriptRoot
    )

    return (Resolve-Path (Join-Path $StartPath "..")).Path
}

function Resolve-WorkspacePath {
    param(
        [Parameter(Mandatory)]
        [string]$RelativePath
    )

    $root = Get-WorkspaceRoot
    return (Join-Path $root $RelativePath)
}

function Parse-TomlValue {
    param(
        [Parameter(Mandatory)]
        [string]$RawValue
    )

    $value = $RawValue.Trim()

    if ($value -eq "true") { return $true }
    if ($value -eq "false") { return $false }

    if ($value.StartsWith('"') -and $value.EndsWith('"')) {
        return $value.Substring(1, $value.Length - 2)
    }

    if ($value -match "^-?\d+$") {
        return [int]$value
    }

    return $value
}

function Import-SimpleToml {
    param(
        [Parameter(Mandatory)]
        [string]$Path
    )

    $result = @{}
    $current = $result

    foreach ($rawLine in Get-Content -Path $Path -Encoding utf8) {
        $line = $rawLine.Trim()

        if (-not $line) { continue }
        if ($line.StartsWith("#")) { continue }

        if ($line -match '^\[\[(.+)\]\]$') {
            $tableName = $Matches[1]
            if (-not $result.ContainsKey($tableName)) {
                $result[$tableName] = @()
            }
            $item = @{}
            $result[$tableName] += $item
            $current = $item
            continue
        }

        if ($line -match '^\[(.+)\]$') {
            $pathParts = $Matches[1].Split(".")
            $current = $result
            foreach ($part in $pathParts) {
                if (-not $current.ContainsKey($part)) {
                    $current[$part] = @{}
                }
                $current = $current[$part]
            }
            continue
        }

        if ($line -match '^([A-Za-z0-9_\-]+)\s*=\s*(.+)$') {
            $key = $Matches[1]
            $value = Parse-TomlValue -RawValue $Matches[2]
            $current[$key] = $value
        }
    }

    return $result
}

function Get-SkillsManifest {
    $path = Resolve-WorkspacePath "manifests/skills.toml"
    return Import-SimpleToml -Path $path
}

function Get-InstallTargetsManifest {
    $path = Resolve-WorkspacePath "manifests/install-targets.toml"
    if (-not (Test-Path $path)) {
        $examplePath = Resolve-WorkspacePath "manifests/install-targets.example.toml"
        throw ("Missing manifests/install-targets.toml. Create it from the template first: " +
            "Copy-Item `"$examplePath`" `"$path`"")
    }
    return Import-SimpleToml -Path $path
}

function Get-UpstreamLockManifest {
    $path = Resolve-WorkspacePath "vendor/mattpocock/local/upstream_lock.toml"
    return Import-SimpleToml -Path $path
}

function Get-RepoPath {
    param(
        [Parameter(Mandatory)]
        [hashtable]$SkillsConfig,

        [Parameter(Mandatory)]
        [string]$RepoName
    )

    if (-not $SkillsConfig.ContainsKey("repos")) {
        throw "Missing [repos.*] sections in skills.toml."
    }

    if (-not $SkillsConfig["repos"].ContainsKey($RepoName)) {
        throw "Unknown repo '$RepoName' in skills.toml."
    }

    return Resolve-WorkspacePath $SkillsConfig["repos"][$RepoName]["path"]
}

function Get-TargetConfig {
    param(
        [Parameter(Mandatory)]
        [hashtable]$TargetConfig,

        [string]$TargetName
    )

    if (-not $TargetName) {
        $TargetName = $TargetConfig["workspace"]["default_target"]
    }

    if (-not $TargetConfig.ContainsKey("targets")) {
        throw "Missing [targets.*] sections in install-targets.toml."
    }

    if (-not $TargetConfig["targets"].ContainsKey($TargetName)) {
        throw "Unknown target '$TargetName' in install-targets.toml."
    }

    return @{
        Name = $TargetName
        Config = $TargetConfig["targets"][$TargetName]
    }
}

function Get-EnabledTargets {
    param(
        [Parameter(Mandatory)]
        [hashtable]$TargetConfig
    )

    if (-not $TargetConfig.ContainsKey("targets")) {
        throw "Missing [targets.*] sections in install-targets.toml."
    }

    $enabled = @()
    foreach ($name in $TargetConfig["targets"].Keys) {
        $config = $TargetConfig["targets"][$name]
        if ($config["enabled"] -eq $true) {
            $enabled += @{
                Name = $name
                Config = $config
            }
        }
    }

    if ($enabled.Count -eq 0) {
        throw "No enabled targets in install-targets.toml."
    }

    return @($enabled)
}

function Get-PublishedSkills {
    param(
        [Parameter(Mandatory)]
        [hashtable]$SkillsConfig,

        [string[]]$SkillName
    )

    $skills = @($SkillsConfig["skill"])
    $published = $skills | Where-Object { $_["publish"] -eq $true }

    if ($SkillName -and $SkillName.Count -gt 0) {
        $nameSet = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
        foreach ($name in $SkillName) {
            [void]$nameSet.Add($name)
        }
        $published = $published | Where-Object { $nameSet.Contains((Get-SkillPublishName -Skill $_)) }
    }

    return @($published)
}

function Get-SkillPublishName {
    param(
        [Parameter(Mandatory)]
        [hashtable]$Skill
    )

    if ($Skill.ContainsKey("publish_name")) {
        return $Skill["publish_name"]
    }

    return $Skill["name"]
}

function Get-SkillSourcePath {
    param(
        [Parameter(Mandatory)]
        [hashtable]$Skill
    )

    if ($Skill.ContainsKey("source_path")) {
        return $Skill["source_path"]
    }

    return $Skill["path"]
}

function Get-UpstreamLockEntry {
    param(
        [Parameter(Mandatory)]
        [hashtable]$UpstreamLock,

        [Parameter(Mandatory)]
        [string]$PublishName
    )

    foreach ($entry in @($UpstreamLock["skill"])) {
        if ($entry["publish_name"] -eq $PublishName) {
            return $entry
        }
    }

    return $null
}

function Test-CacheArtifactPath {
    param(
        [Parameter(Mandatory)]
        [string]$Path
    )

    if ($Path -match '(^|\\)__pycache__(\\|$)') {
        return $true
    }

    if ($Path -like '*.pyc' -or $Path -like '*.pyo') {
        return $true
    }

    return $false
}

function Copy-DirectoryFiltered {
    param(
        [Parameter(Mandatory)]
        [string]$SourcePath,

        [Parameter(Mandatory)]
        [string]$DestinationPath
    )

    $sourceFull = [System.IO.Path]::GetFullPath($SourcePath).TrimEnd('\')
    New-Item -ItemType Directory -Force -Path $DestinationPath | Out-Null

    foreach ($file in Get-ChildItem -LiteralPath $SourcePath -File -Recurse) {
        if (Test-CacheArtifactPath -Path $file.FullName) {
            continue
        }

        $fileFull = [System.IO.Path]::GetFullPath($file.FullName)
        $relative = $fileFull.Substring($sourceFull.Length).TrimStart('\')
        $destinationFile = Join-Path $DestinationPath $relative
        New-Item -ItemType Directory -Force -Path (Split-Path $destinationFile) | Out-Null
        Copy-Item -LiteralPath $file.FullName -Destination $destinationFile -Force
    }
}

function Get-FileHashMap {
    param(
        [Parameter(Mandatory)]
        [string]$RootPath
    )

    $map = @{}
    if (-not (Test-Path -LiteralPath $RootPath)) {
        return $map
    }

    $rootFull = [System.IO.Path]::GetFullPath($RootPath).TrimEnd('\')
    foreach ($file in Get-ChildItem -LiteralPath $RootPath -File -Recurse) {
        if (Test-CacheArtifactPath -Path $file.FullName) {
            continue
        }
        $fileFull = [System.IO.Path]::GetFullPath($file.FullName)
        $relative = $fileFull.Substring($rootFull.Length).TrimStart('\')
        $map[$relative] = (Get-FileHash -Algorithm SHA256 -LiteralPath $file.FullName).Hash
    }

    return $map
}

function Compare-FileHashMaps {
    param(
        [Parameter(Mandatory)]
        [hashtable]$BaselineMap,

        [Parameter(Mandatory)]
        [hashtable]$CurrentMap
    )

    $baselineKeys = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    foreach ($key in $BaselineMap.Keys) { [void]$baselineKeys.Add([string]$key) }

    $changed = @()
    $added = @()
    foreach ($key in $CurrentMap.Keys) {
        $keyString = [string]$key
        if ($baselineKeys.Contains($keyString)) {
            if ($BaselineMap[$keyString] -ne $CurrentMap[$key]) {
                $changed += $keyString
            }
        }
        else {
            $added += $keyString
        }
    }

    $currentKeys = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    foreach ($key in $CurrentMap.Keys) { [void]$currentKeys.Add([string]$key) }

    $removed = @($baselineKeys | Where-Object { -not $currentKeys.Contains($_) })

    return @{
        Changed = @($changed | Sort-Object)
        Added = @($added | Sort-Object)
        Removed = @($removed | Sort-Object)
    }
}

function Format-DriftSummary {
    param(
        [Parameter(Mandatory)]
        [hashtable]$Drift
    )

    $parts = @()
    foreach ($kind in @("Changed", "Added", "Removed")) {
        $files = @($Drift[$kind])
        if ($files.Count -eq 0) { continue }
        $preview = ($files | Select-Object -First 5) -join ", "
        if ($files.Count -gt 5) {
            $preview = "$preview, ..."
        }
        $parts += "$($files.Count) $($kind.ToLower()): $preview"
    }

    return ($parts -join "; ")
}

function Backup-Directory {
    param(
        [Parameter(Mandatory)]
        [string]$SourcePath,

        [Parameter(Mandatory)]
        [string]$BackupRoot,

        [Parameter(Mandatory)]
        [string]$Name
    )

    if (-not (Test-Path -LiteralPath $SourcePath)) {
        return $null
    }

    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backupDir = Join-Path $BackupRoot $timestamp
    $backupPath = Join-Path $backupDir $Name

    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
    Copy-Item -LiteralPath $SourcePath -Destination $backupPath -Recurse -Force
    return $backupPath
}

function Get-InstallStateRoot {
    return Resolve-WorkspacePath "logs/install-state"
}

function Get-SkillInstallStateFile {
    param(
        [Parameter(Mandatory)]
        [string]$TargetName,

        [Parameter(Mandatory)]
        [string]$PublishName
    )

    $root = Get-InstallStateRoot
    $safeTarget = $TargetName -replace '[^A-Za-z0-9_\-]', '_'
    $safeSkill = $PublishName -replace '[^A-Za-z0-9_\-]', '_'
    return Join-Path $root ("{0}__{1}.json" -f $safeTarget, $safeSkill)
}

function Set-SkillInstallState {
    param(
        [Parameter(Mandatory)]
        [string]$TargetName,

        [Parameter(Mandatory)]
        [string]$PublishName,

        [Parameter(Mandatory)]
        [datetime]$InstalledAt,

        [hashtable]$FileManifest
    )

    $file = Get-SkillInstallStateFile -TargetName $TargetName -PublishName $PublishName
    New-Item -ItemType Directory -Force -Path (Split-Path $file) | Out-Null
    $state = @{
        target = $TargetName
        skill = $PublishName
        installed_at = $InstalledAt.ToString("o")
    }
    if ($FileManifest) {
        $state["files"] = $FileManifest
    }
    $state | ConvertTo-Json -Depth 8 | Set-Content -Path $file -Encoding utf8
}

function Get-SkillInstallState {
    param(
        [Parameter(Mandatory)]
        [string]$TargetName,

        [Parameter(Mandatory)]
        [string]$PublishName
    )

    $file = Get-SkillInstallStateFile -TargetName $TargetName -PublishName $PublishName
    if (-not (Test-Path -LiteralPath $file)) {
        return $null
    }
    $json = Get-Content -Path $file -Raw | ConvertFrom-Json
    $manifest = @{}
    if ($json.PSObject.Properties["files"]) {
        foreach ($property in $json.files.PSObject.Properties) {
            $manifest[$property.Name] = [string]$property.Value
        }
    }
    return @{
        TargetName = $json.target
        PublishName = $json.skill
        InstalledAt = [datetime]::Parse($json.installed_at)
        FileManifest = $manifest
    }
}

function Get-DirectoryLatestWriteTime {
    param(
        [Parameter(Mandatory)]
        [string]$RootPath
    )

    if (-not (Test-Path -LiteralPath $RootPath)) {
        return $null
    }

    $latest = [datetime]::MinValue
    foreach ($file in Get-ChildItem -LiteralPath $RootPath -File -Recurse) {
        if (Test-CacheArtifactPath -Path $file.FullName) {
            continue
        }
        if ($file.LastWriteTime -gt $latest) {
            $latest = $file.LastWriteTime
        }
    }
    if ($latest -eq [datetime]::MinValue) {
        return $null
    }
    return $latest
}

function Test-InstallConflict {
    param(
        [Parameter(Mandatory)]
        [string]$TargetName,

        [Parameter(Mandatory)]
        [string]$PublishName,

        [Parameter(Mandatory)]
        [string]$TargetPath,

        [string]$SourcePath
    )

    $state = Get-SkillInstallState -TargetName $TargetName -PublishName $PublishName

    if ($state -and $state.FileManifest.Count -gt 0) {
        if (-not (Test-Path -LiteralPath $TargetPath)) {
            return @{ Conflict = $false; Reason = "" }
        }

        $targetMap = Get-FileHashMap -RootPath $TargetPath
        $drift = Compare-FileHashMaps -BaselineMap $state.FileManifest -CurrentMap $targetMap
        if ($drift.Changed.Count -gt 0 -or $drift.Added.Count -gt 0 -or $drift.Removed.Count -gt 0) {
            return @{
                Conflict = $true
                Reason = "skill '$PublishName' at '$TargetPath' differs from its last installed content baseline ($(Format-DriftSummary -Drift $drift)). Likely modified inside the IDE after install."
            }
        }

        return @{ Conflict = $false; Reason = "" }
    }

    if (-not $state) {
        # No recorded install state yet; judge against the current source so a
        # pre-existing (possibly IDE-edited) copy is never replaced blindly.
        if (-not (Test-Path -LiteralPath $TargetPath)) {
            return @{ Conflict = $false; Reason = "" }
        }

        if ($SourcePath -and (Test-Path -LiteralPath $SourcePath)) {
            $sourceMap = Get-FileHashMap -RootPath $SourcePath
            $targetMap = Get-FileHashMap -RootPath $TargetPath
            $drift = Compare-FileHashMaps -BaselineMap $sourceMap -CurrentMap $targetMap
            if ($drift.Changed.Count -gt 0 -or $drift.Added.Count -gt 0 -or $drift.Removed.Count -gt 0) {
                return @{
                    Conflict = $true
                    Reason = "skill '$PublishName' at '$TargetPath' has no install-state record and already differs from source ($(Format-DriftSummary -Drift $drift)). Cannot prove the target was not modified locally."
                }
            }

            return @{ Conflict = $false; Reason = "" }
        }

        return @{ Conflict = $false; Reason = "" }
    }

    if (-not (Test-Path -LiteralPath $TargetPath)) {
        return @{ Conflict = $false; Reason = "" }
    }

    $latestWrite = Get-DirectoryLatestWriteTime -RootPath $TargetPath
    if (-not $latestWrite) {
        return @{ Conflict = $false; Reason = "" }
    }

    if ($latestWrite -gt $state.InstalledAt) {
        return @{
            Conflict = $true
            Reason = "skill '$PublishName' at '$TargetPath' has files modified later than last install ($($state.InstalledAt.ToString('yyyy-MM-dd HH:mm:ss'))); newest file $($latestWrite.ToString('yyyy-MM-dd HH:mm:ss')). Likely modified by the IDE after install."
        }
    }

    return @{ Conflict = $false; Reason = "" }
}
