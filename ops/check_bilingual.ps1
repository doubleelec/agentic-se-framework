[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$ZhPath,

    [Parameter(Mandatory)]
    [string]$EnPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-HeadingTree {
    param([Parameter(Mandatory)][string]$Path)

    $tree = @()
    foreach ($line in Get-Content -Path $Path -Encoding utf8) {
        if ($line -match '^(#{1,6})\s+(.*)$') {
            $level = $Matches[1].Length
            $text = ($Matches[2] -replace '\{#.*\}', '').Trim()
            $num = ''
            if ($text -match '^(Appendix|附录)') {
                $num = 'APPENDIX'
            }
            elseif ($text -match '^(\d+(\.\d+)*)') {
                $num = $Matches[1]
            }
            $tree += "L$level|$num"
        }
    }
    return ,$tree
}

$zh = Get-HeadingTree -Path $ZhPath
$en = Get-HeadingTree -Path $EnPath

if ($zh.Count -ne $en.Count) {
    throw "Heading count mismatch: zh=$($zh.Count) en=$($en.Count)"
}

$mismatches = @()
for ($i = 0; $i -lt $zh.Count; $i++) {
    if ($zh[$i] -ne $en[$i]) {
        $mismatches += "heading $($i + 1): zh='$($zh[$i])' en='$($en[$i])'"
    }
}

if ($mismatches.Count -gt 0) {
    throw "Heading tree mismatch:`n" + ($mismatches -join "`n")
}

Write-Host "Bilingual parity OK: $($zh.Count) headings aligned between '$(Split-Path -Leaf $ZhPath)' and '$(Split-Path -Leaf $EnPath)'"
