<#
.SYNOPSIS
Instala skills do repositório agent-learn-skills para agentes CLI/IDE compatíveis com SKILL.md.

.EXAMPLE
.\scripts\install.ps1 -Agent claude -Scope global
.\scripts\install.ps1 -Agent cursor -Scope project -Skill quiz-master,code-mentor
.\scripts\install.ps1 -Target C:\caminho\custom\skills -Symlink -Force
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

    [switch]$Force
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$SkillsSrc = Join-Path $RepoRoot "skills"

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

$DestDir = Resolve-TargetDirectory
New-Item -ItemType Directory -Force -Path $DestDir | Out-Null

if ($Skill.Count -eq 0) {
    $Skill = Get-ChildItem -Path $SkillsSrc -Directory | Select-Object -ExpandProperty Name
}

$installed = 0
$skipped = 0
$mode = if ($Symlink) { "symlink" } else { "copy" }

foreach ($name in $Skill) {
    $src = Join-Path $SkillsSrc $name
    $dst = Join-Path $DestDir $name

    if (-not (Test-Path (Join-Path $src "SKILL.md"))) {
        throw "Skill '$name' não encontrada em $src"
    }

    if (Test-Path $dst) {
        if ($Force) {
            Remove-Item -Path $dst -Recurse -Force
        } else {
            Write-Host "PULADA: $name (já existe em $dst; use -Force para substituir)"
            $skipped++
            continue
        }
    }

    if ($Symlink) {
        New-Item -ItemType SymbolicLink -Path $dst -Target $src | Out-Null
    } else {
        Copy-Item -Path $src -Destination $dst -Recurse
    }

    Write-Host "INSTALADA ($mode): $name -> $dst"
    $installed++
}

Write-Host "Concluído: $installed instalada(s), $skipped pulada(s) em $DestDir"
