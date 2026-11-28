<#
.SYNOPSIS
One-line remote installer for agent-learn-skills (Windows PowerShell).

.EXAMPLE
irm https://raw.githubusercontent.com/hikarilucky79/agent-learn-skills/main/scripts/remote-install.ps1 | iex
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/hikarilucky79/agent-learn-skills/main/scripts/remote-install.ps1))) -Agent cursor -Scope global
#>
[CmdletBinding()]
param(
    [ValidateSet("claude", "cursor", "codex", "opencode", "antigravity")]
    [string]$Agent = "claude",

    [ValidateSet("global", "project")]
    [string]$Scope = "global",

    [string]$Target = "",

    [string[]]$Skill = @(),

    [switch]$Force,

    [switch]$Uninstall
)

$ErrorActionPreference = "Stop"

$repoUrl = if ($env:AGENT_LEARN_SKILLS_REPO) { $env:AGENT_LEARN_SKILLS_REPO } else { "https://github.com/hikarilucky79/agent-learn-skills" }
$ref = if ($env:AGENT_LEARN_SKILLS_REF) { $env:AGENT_LEARN_SKILLS_REF } else { "main" }

$tmpDir = Join-Path ([System.IO.Path]::GetTempPath()) ("agent-learn-skills-" + [System.Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $tmpDir | Out-Null

try {
    $srcDir = Join-Path $tmpDir "repo"
    if (Get-Command git -ErrorAction SilentlyContinue) {
        git clone --depth 1 --branch $ref "$repoUrl.git" $srcDir | Out-Null
    } else {
        $zipPath = Join-Path $tmpDir "repo.zip"
        $extractDir = Join-Path $tmpDir "extracted"
        Invoke-WebRequest -Uri "$repoUrl/archive/refs/heads/$ref.zip" -OutFile $zipPath -UseBasicParsing
        Expand-Archive -Path $zipPath -DestinationPath $extractDir -Force
        $srcDir = (Get-ChildItem -LiteralPath $extractDir -Directory | Select-Object -First 1).FullName
    }

    $installer = Join-Path $srcDir "scripts\install.ps1"
    $forwardArgs = @{
        Agent = $Agent
        Scope = $Scope
    }
    if (-not [string]::IsNullOrWhiteSpace($Target)) { $forwardArgs["Target"] = $Target }
    if ($Skill.Count -gt 0) { $forwardArgs["Skill"] = $Skill }
    if ($Force) { $forwardArgs["Force"] = $true }
    if ($Uninstall) { $forwardArgs["Uninstall"] = $true }

    & $installer @forwardArgs
} finally {
    if (Test-Path -LiteralPath $tmpDir) {
        Remove-Item -LiteralPath $tmpDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}
