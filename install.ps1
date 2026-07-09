# Paracosm installer (native Windows PowerShell). Same behavior as install.sh.
# Usage: .\install.ps1 [-DryRun]
# Env:   HERMES_HOME (default ~\.hermes), HERMES_WORKSPACE (default $HERMES_HOME\workspace)
param([switch]$DryRun)

$ErrorActionPreference = 'Stop'
$SrcDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$HermesHome = if ($env:HERMES_HOME) { $env:HERMES_HOME } else { Join-Path $HOME '.hermes' }
$Workspace  = if ($env:HERMES_WORKSPACE) { $env:HERMES_WORKSPACE } else { Join-Path $HermesHome 'workspace' }

function Act($desc, [scriptblock]$block) {
  if ($DryRun) { Write-Host "[dry-run] $desc" } else { & $block; Write-Host "  ok: $desc" }
}

Write-Host "Paracosm installer"
Write-Host "  source:    $SrcDir"
Write-Host "  hermes:    $HermesHome"
Write-Host "  workspace: $Workspace"
if ($DryRun) { Write-Host "  (dry run - nothing will be written)" }
Write-Host ""

if (-not (Test-Path $HermesHome) -and -not $DryRun) {
  Write-Host "WARNING: $HermesHome does not exist yet. Install Hermes first, or set HERMES_HOME."
  $ans = Read-Host "Create it anyway and continue? [y/N]"
  if ($ans -notmatch '^(y|yes)$') { Write-Host "Aborted."; exit 1 }
}

foreach ($dep in @('curl', 'python3')) {
  if (Get-Command $dep -ErrorAction SilentlyContinue) { Write-Host "  dep ok: $dep" }
  else { Write-Host "  dep MISSING: $dep (needed by dice + fal.ai scripts)" }
}
Write-Host "  note: the fal.ai scripts are bash - on native Windows, Hermes needs Git Bash on PATH to run them."
Write-Host ""

# SOUL.md MUST live at $HermesHome\SOUL.md directly (Hermes loads it from
# HERMES_HOME only, never a subdirectory). AGENTS.md loads from the gateway's
# CWD at startup (terminal.cwd, default = launch dir) - it goes in the
# workspace, and terminal.cwd must be pinned there in config.yaml (see the
# printed reminder below).
Act "create workspace $Workspace" { New-Item -ItemType Directory -Force $Workspace | Out-Null }
Act "install SOUL.md -> HermesHome"  { Copy-Item (Join-Path $SrcDir 'hermes\SOUL.md')   (Join-Path $HermesHome 'SOUL.md')   -Force }
Act "install AGENTS.md -> workspace" { Copy-Item (Join-Path $SrcDir 'hermes\AGENTS.md') (Join-Path $Workspace 'AGENTS.md') -Force }

$SkillsDst = Join-Path $HermesHome 'skills'
Act "create $SkillsDst" { New-Item -ItemType Directory -Force $SkillsDst | Out-Null }
Get-ChildItem (Join-Path $SrcDir 'hermes\skills') -Directory | ForEach-Object {
  $name = $_.Name
  $src = $_.FullName
  $dst = Join-Path $SkillsDst $name
  Act "install skill: $name" {
    if (Test-Path $dst) { Remove-Item -Recurse -Force $dst }
    Copy-Item -Recurse $src $dst
  }.GetNewClosure()
}

Act "install campaign templates" {
  $tpl = Join-Path $Workspace 'templates'
  New-Item -ItemType Directory -Force $tpl | Out-Null
  Copy-Item -Recurse -Force (Join-Path $SrcDir 'templates\campaign') $tpl
}
Act "create games/ directory" { New-Item -ItemType Directory -Force (Join-Path $Workspace 'games') | Out-Null }

Write-Host ""
$envFile = Join-Path $HermesHome '.env'
$hasFal = $env:FAL_KEY -or ((Test-Path $envFile) -and (Select-String -Path $envFile -Pattern '^FAL_KEY=' -Quiet))
if ($hasFal) { Write-Host "FAL_KEY: found - scene art & cutscenes enabled." }
else {
  Write-Host "FAL_KEY: NOT found. Paracosm still works (ASCII art fallback)."
  Write-Host "  To enable images/video: get a key at https://fal.ai/dashboard/keys and add FAL_KEY=... to $envFile"
}

Write-Host ""
Write-Host "IMPORTANT - one manual config step (installer won't touch config.yaml):"
Write-Host "  Add this to $HermesHome\config.yaml so AGENTS.md and games/ resolve"
Write-Host "  correctly no matter how the gateway service is launched:"
Write-Host ""
Write-Host "    terminal:"
Write-Host "      cwd: `"$Workspace`""
Write-Host ""
Write-Host "  Without this, terminal.cwd defaults to the gateway's launch directory,"
Write-Host "  and AGENTS.md / games/ / templates/ may silently fail to load."
Write-Host ""
Write-Host "Done. Next steps (full guide: IMPLEMENTATION.md):"
Write-Host "  1. hermes gateway setup     # connect Telegram if you haven't"
Write-Host "  2. hermes gateway install   # keep the gateway (and cron ticks) running"
Write-Host "  3. Message your bot - the lobby answers. /new-game to begin."
