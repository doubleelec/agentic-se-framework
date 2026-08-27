[CmdletBinding()]
param(
    [switch]$Check
)

# Keep the English panorama diagram single-sourced: docs/html/panorama.en.svg is
# the one place the SVG is edited. The inline <svg> block inside the source
# Markdown and inside the generated HTML are refreshed from it.
#
#   -Update (default): re-inject the standalone SVG block into
#       docs/new_project_skill_panorama.en.md
#       docs/html/new_project_skill_panorama.en.html
#   -Check:             verify md + html match the standalone SVG (EOL-insensitive);
#                       exit 1 on drift (for the release checklist)
#
# Run from anywhere; paths are derived from this script's own location.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$SvgSource = Join-Path $Root 'docs/html/panorama.en.svg'
$Targets = @(
    (Join-Path $Root 'docs/new_project_skill_panorama.en.md'),
    (Join-Path $Root 'docs/html/new_project_skill_panorama.en.html')
)

$SvgPattern = '<svg[\s\S]*?</svg>'

function Get-SvgBlock {
    param([Parameter(Mandatory)][string]$Text)
    $m = [regex]::Match($Text, $SvgPattern)
    if (-not $m.Success) { throw "No <svg>...</svg> block found in input" }
    return $m.Value
}

function Normalize-Eol {
    param([Parameter(Mandatory)][string]$Text)
    return $Text -replace "`r`n", "`n"
}

function Read-Raw {
    param([Parameter(Mandatory)][string]$Path)
    return [System.IO.File]::ReadAllText($Path)
}

function Write-Raw {
    param([Parameter(Mandatory)][string]$Path, [Parameter(Mandatory)][string]$Text)
    $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::WriteAllText($Path, $Text, $utf8NoBom)
}

if (-not (Test-Path -LiteralPath $SvgSource)) {
    throw "Source SVG not found: $SvgSource"
}

$svgRaw = Read-Raw -Path $SvgSource
$svgBlock = Get-SvgBlock -Text $svgRaw
if ($svgRaw.Trim() -ne $svgBlock.Trim()) {
    throw "Source $SvgSource must contain exactly one <svg>...</svg> block and nothing else"
}

if ($Check) {
    $drift = @()
    foreach ($target in $Targets) {
        if (-not (Test-Path -LiteralPath $target)) {
            $drift += "missing: $target"
            continue
        }
        $targetBlock = Get-SvgBlock -Text (Read-Raw -Path $target)
        if ((Normalize-Eol -Text $targetBlock) -ne (Normalize-Eol -Text $svgBlock)) {
            $drift += "drift: $target"
        }
    }
    if ($drift.Count -gt 0) {
        Write-Host "Panorama SVG out of sync with $SvgSource :"
        $drift | ForEach-Object { Write-Host "  - $_" }
        Write-Host "Run 'ops/refresh_panorama.ps1' to re-inject from $SvgSource"
        exit 1
    }
    Write-Host "Panorama SVG sync OK: md and html match $SvgSource"
    exit 0
}

foreach ($target in $Targets) {
    if (-not (Test-Path -LiteralPath $target)) {
        Write-Warning "Target not found, skipping: $target"
        continue
    }
    $targetText = Read-Raw -Path $target
    $eol = if ($targetText.Contains("`r`n")) { "`r`n" } else { "`n" }
    $inject = (Normalize-Eol -Text $svgBlock) -replace "`n", $eol
    $newText = [regex]::Replace($targetText, $SvgPattern, { param($m) $inject }, 1)
    Write-Raw -Path $target -Text $newText
    Write-Host "Injected SVG block into $target"
}
Write-Host "Panorama refreshed from $SvgSource"
