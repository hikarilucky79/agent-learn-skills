<#
.SYNOPSIS
Instala ou desinstala skills do repositório agent-learn-skills para agentes CLI/IDE compatíveis com SKILL.md.

.EXAMPLE
.\scripts\install.ps1 -Agent claude -Scope global
.\scripts\install.ps1 -Agent cursor -Scope project -Skill quiz-master,code-mentor
.\scripts\install.ps1 -Target C:\caminho\custom\skills -Symlink -Force
.\scripts\install.ps1 -Uninstall -Agent claude -Scope global
.\scripts\install.ps1 -Uninstall -Agent cursor -Scope project -Skill quiz-master
#>
[CmdletBinding()]
param(
    [ValidateSet("claude", "cursor", "codex", "opencode", "antigravity")]
    [string]$Agent = "claude",

    [ValidateSet("global", "project")]
    [string]$Scope = "global",

    [string]$Target = "",

    [string[]]$Skill = @(),

    [switch]$Symlink,

    [switch]$Uninstall,

    [switch]$Force
)

$ErrorActionPreference = "Stop"

if ($Uninstall -and $Symlink) {
    throw "Não é possível combinar -Uninstall com -Symlink."
}

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$SkillsSrc = Join-Path $RepoRoot "skills"
$SkillNamePattern = '^[a-z0-9]+(-[a-z0-9]+)*$'

function Resolve-TargetDirectory {
    if (-not [string]::IsNullOrWhiteSpace($Target)) {
        return $Target
    }

    $base = if ($Scope -eq "global") { $HOME } else { (Get-Location).Path }

    switch ($Agent) {
        "claude"      { return (Join-Path $base ".claude\skills") }
        "cursor"      { return (Join-Path $base ".cursor\skills") }
        "codex"       { return (Join-Path $base ".agents\skills") }
        "opencode"    { return (Join-Path $base ".agents\skills") }
        "antigravity" {
            if ($Scope -eq "global") {
                return (Join-Path $HOME ".gemini\antigravity\skills")
            }
            return (Join-Path $base ".agent\skills")
        }
    }
}

function Get-NormalizedFullPath {
    param([Parameter(Mandatory)][string]$Path)
    $full = [System.IO.Path]::GetFullPath($Path)
    $root = [System.IO.Path]::GetPathRoot($full)
    if ($full -eq $root) {
        return $full
    }
    return $full.TrimEnd('\', '/')
}

function Test-SamePath {
    param(
        [Parameter(Mandatory)][string]$PathA,
        [Parameter(Mandatory)][string]$PathB
    )
    $normA = Get-NormalizedFullPath -Path $PathA
    $normB = Get-NormalizedFullPath -Path $PathB
    $comparison = if ([System.Environment]::OSVersion.Platform -eq [System.PlatformID]::Win32NT) {
        [System.StringComparison]::OrdinalIgnoreCase
    } else {
        [System.StringComparison]::Ordinal
    }
    return [string]::Equals($normA, $normB, $comparison)
}

function Get-ReparsePointTargetPath {
    param([Parameter(Mandatory)][System.IO.FileSystemInfo]$Item)
    $rawTarget = $Item.Target
    if ($rawTarget -is [System.Array]) {
        $rawTarget = if ($rawTarget.Count -gt 0) { $rawTarget[0] } else { $null }
    }
    if ([string]::IsNullOrWhiteSpace($rawTarget)) {
        return $null
    }
    if ([System.IO.Path]::IsPathRooted($rawTarget)) {
        return (Get-NormalizedFullPath -Path $rawTarget)
    }
    $parentDir = Split-Path -Parent $Item.FullName
    return (Get-NormalizedFullPath -Path (Join-Path $parentDir $rawTarget))
}

function Remove-SkillEntry {
    param([Parameter(Mandatory)][System.IO.FileSystemInfo]$Item)

    $isReparse = ($Item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0
    if ($isReparse) {
        if ($Item -is [System.IO.DirectoryInfo]) {
            [System.IO.Directory]::Delete($Item.FullName, $false)
        } else {
            [System.IO.File]::Delete($Item.FullName)
        }
    } else {
        Remove-Item -LiteralPath $Item.FullName -Recurse -Force
    }
}

$DestDir = Resolve-TargetDirectory

if ($Skill.Count -eq 0) {
    $Skill = @(Get-ChildItem -LiteralPath $SkillsSrc -Directory | Select-Object -ExpandProperty Name)
} else {
    $Skill = @($Skill | ForEach-Object { $_ -split ',' } | ForEach-Object { $_.Trim() })
}

foreach ($name in $Skill) {
    if ($name -notmatch $SkillNamePattern) {
        throw "Nome de skill inválido: '$name'"
    }
    $src = Join-Path $SkillsSrc $name
    if (-not (Test-Path -LiteralPath (Join-Path $src "SKILL.md"))) {
        throw "Skill '$name' não encontrada em $src"
    }
}

if ($Uninstall) {
    if (-not (Test-Path -LiteralPath $DestDir)) {
        Write-Host "Diretório destino não existe: $DestDir"
        Write-Host "Concluído: 0 removida(s), $($Skill.Count) pulada(s) em $DestDir"
        return
    }

    if (-not (Test-Path -LiteralPath $DestDir -PathType Container)) {
        throw "Destino não é um diretório: $DestDir"
    }

    $removed = 0
    $skipped = 0

    foreach ($name in $Skill) {
        $src = Join-Path $SkillsSrc $name
        $dst = Join-Path $DestDir $name
        $existing = Get-Item -LiteralPath $dst -Force -ErrorAction SilentlyContinue

        if ($null -eq $existing) {
            Write-Host "NÃO ENCONTRADA: $name (ausente em $dst)"
            $skipped++
            continue
        }

        $isReparse = ($existing.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0
        if ($isReparse) {
            $targetPath = Get-ReparsePointTargetPath -Item $existing
            if ($targetPath -and (Test-SamePath -PathA $targetPath -PathB $src)) {
                Remove-SkillEntry -Item $existing
                Write-Host "REMOVIDA (symlink): $name <- $dst"
                $removed++
            } elseif ($Force) {
                Remove-SkillEntry -Item $existing
                Write-Host "REMOVIDA (symlink externo): $name <- $dst"
                $removed++
            } else {
                $displayTarget = if ($targetPath) { $targetPath } else { "<desconhecido>" }
                Write-Host "PULADA: $name (symlink aponta para outro destino: $displayTarget; use -Force para remover)"
                $skipped++
            }
        } else {
            Remove-SkillEntry -Item $existing
            Write-Host "REMOVIDA (copy): $name <- $dst"
            $removed++
        }
    }

    Write-Host "Concluído: $removed removida(s), $skipped pulada(s) em $DestDir"
    return
}

New-Item -ItemType Directory -Force -Path $DestDir | Out-Null

$installed = 0
$skipped = 0
$mode = if ($Symlink) { "symlink" } else { "copy" }

foreach ($name in $Skill) {
    $src = Join-Path $SkillsSrc $name
    $dst = Join-Path $DestDir $name
    $existing = Get-Item -LiteralPath $dst -Force -ErrorAction SilentlyContinue

    if ($null -ne $existing) {
        if ($Force) {
            Remove-SkillEntry -Item $existing
        } else {
            Write-Host "PULADA: $name (já existe em $dst; use -Force para substituir)"
            $skipped++
            continue
        }
    }

    if ($Symlink) {
        New-Item -ItemType SymbolicLink -Path $dst -Target $src | Out-Null
    } else {
        Copy-Item -LiteralPath $src -Destination $dst -Recurse
    }

    Write-Host "INSTALADA ($mode): $name -> $dst"
    $installed++
}

Write-Host "Concluído: $installed instalada(s), $skipped pulada(s) em $DestDir"
