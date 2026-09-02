#!/usr/bin/env bash
# Paracosm installer — copies the Game Master persona, protocol, skills, and campaign
# templates into a Hermes Agent install. Idempotent: safe to re-run after `git pull`.
#
# Usage: ./install.sh [--dry-run]
# Env:   HERMES_HOME  (default ~/.hermes)   — Hermes config/skills root
#        HERMES_WORKSPACE (default $HERMES_HOME/workspace) — agent working directory
#
# Portable: bash 3.2+ (macOS stock), Linux, Raspberry Pi OS, Git Bash / WSL on Windows.
set -u

DRY_RUN=0
[ "${1:-}" = "--dry-run" ] && DRY_RUN=1

SRC_DIR=$(cd "$(dirname "$0")" && pwd)
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
WORKSPACE="${HERMES_WORKSPACE:-$HERMES_HOME/workspace}"

say()  { printf '%s\n' "$*"; }
act()  { # act <description> <command...>
  desc="$1"; shift
  if [ "$DRY_RUN" -eq 1 ]; then
    say "[dry-run] $desc"
  else
    "$@" || { say "ERROR: failed: $desc"; exit 1; }
    say "  ok: $desc"
  fi
}

say "Paracosm installer"
say "  source:    $SRC_DIR"
say "  hermes:    $HERMES_HOME"
say "  workspace: $WORKSPACE"
[ "$DRY_RUN" -eq 1 ] && say "  (dry run — nothing will be written)"
say ""

# --- sanity checks -----------------------------------------------------------
if [ ! -d "$HERMES_HOME" ] && [ "$DRY_RUN" -eq 0 ]; then
  say "WARNING: $HERMES_HOME does not exist yet."
  say "Install Hermes first (https://github.com/nousresearch/hermes-agent), or set HERMES_HOME."
  printf 'Create it anyway and continue? [y/N] '
  read -r ans
  case "$ans" in y|Y|yes|YES) ;; *) say "Aborted."; exit 1 ;; esac
fi

for dep in curl python3; do
  if command -v "$dep" >/dev/null 2>&1; then
    say "  dep ok: $dep"
  else
    say "  dep MISSING: $dep (needed by dice + fal.ai scripts)"
  fi
done
say ""

# --- persona + protocol --------------------------------------------------------
# SOUL.md MUST live at $HERMES_HOME/SOUL.md directly (Hermes loads it from
# HERMES_HOME only, never a subdirectory). AGENTS.md loads from the gateway's
# CWD at startup, which is NOT fixed by default (terminal.cwd defaults to the
# launch directory) — it goes in the workspace, and terminal.cwd must be
# pinned there in config.yaml (see the printed reminder below) for it to load
# reliably regardless of how the gateway service is started.
act "create workspace $WORKSPACE"           mkdir -p "$WORKSPACE"
act "install SOUL.md -> \$HERMES_HOME"      cp "$SRC_DIR/hermes/SOUL.md"   "$HERMES_HOME/SOUL.md"
act "install AGENTS.md -> workspace"        cp "$SRC_DIR/hermes/AGENTS.md" "$WORKSPACE/AGENTS.md"

# --- skills into ~/.hermes/skills/ --------------------------------------------
act "create $HERMES_HOME/skills"            mkdir -p "$HERMES_HOME/skills"
for skill_dir in "$SRC_DIR"/hermes/skills/*/; do
  name=$(basename "$skill_dir")
  act "install skill: $name"                rm -rf "$HERMES_HOME/skills/$name"
  act "  copy $name"                        cp -R "${skill_dir%/}" "$HERMES_HOME/skills/$name"
done
if [ "$DRY_RUN" -eq 0 ]; then
  find "$HERMES_HOME/skills" -name '*.sh' -exec chmod +x {} \; 2>/dev/null
fi

# --- campaign templates + games dir into the workspace ------------------------
act "install campaign templates"            mkdir -p "$WORKSPACE/templates"
act "  copy templates/campaign"             cp -R "$SRC_DIR/templates/campaign" "$WORKSPACE/templates/"
act "create games/ directory"               mkdir -p "$WORKSPACE/games"

# --- media scripts into the workspace (skills call them as scripts/<name>.sh,
#     relative to the pinned terminal.cwd, so the right instance's copy always runs) ---
act "install media scripts -> workspace"    mkdir -p "$WORKSPACE/scripts"
act "  copy fal_image.sh"                   cp "$SRC_DIR/hermes/skills/scene-art/scripts/fal_image.sh" "$WORKSPACE/scripts/fal_image.sh"
act "  copy fal_video.sh"                   cp "$SRC_DIR/hermes/skills/cutscene/scripts/fal_video.sh"  "$WORKSPACE/scripts/fal_video.sh"
act "  copy reactor_clip.py"                cp "$SRC_DIR/hermes/skills/cutscene/scripts/reactor_clip.py" "$WORKSPACE/scripts/reactor_clip.py"
act "  copy walk_link.py"                   cp "$SRC_DIR/hermes/skills/scene-walk/scripts/walk_link.py"  "$WORKSPACE/scripts/walk_link.py"
if [ "$DRY_RUN" -eq 0 ]; then
  chmod +x "$WORKSPACE/scripts/"*.sh "$WORKSPACE/scripts/"*.py 2>/dev/null
fi

# --- environment check ---------------------------------------------------------
say ""
if [ -n "${FAL_KEY:-}" ] || grep -qs '^FAL_KEY=' "$HERMES_HOME/.env" 2>/dev/null; then
  say "FAL_KEY: found — scene art & cutscenes enabled."
else
  say "FAL_KEY: NOT found. Paracosm still works (ASCII art fallback)."
  say "  To enable images/video: get a key at https://fal.ai/dashboard/keys and add"
  say "  FAL_KEY=... to $HERMES_HOME/.env"
fi

# Reactor (optional): steered cutscene clips + scene walks. Cutscenes fall back to fal
# without it; walks are simply never offered.
if [ -n "${REACTOR_API_KEY:-}" ] || grep -qs '^REACTOR_API_KEY=' "$HERMES_HOME/.env" 2>/dev/null; then
  say "REACTOR_API_KEY: found — cinematic cutscenes via Reactor enabled."
  if python3 -c 'import reactor_sdk' >/dev/null 2>&1; then
    say "  reactor-sdk: ok"
  else
    say "  reactor-sdk: NOT importable by python3 — run: python3 -m pip install reactor-sdk"
    say "  (until then cutscenes use fal.ai)"
  fi
  if command -v ffmpeg >/dev/null 2>&1; then
    say "  ffmpeg: ok (clips get a seekable duration bar)"
  else
    say "  ffmpeg: not found (optional — clips still play, without a duration bar)"
  fi
else
  say "REACTOR_API_KEY: not found — cutscenes use fal.ai (IMPLEMENTATION.md §3b to enable Reactor)."
fi
if grep -qs '^PARACOSM_WALK_URL=' "$HERMES_HOME/.env" 2>/dev/null && grep -qs '^WALK_SIGNING_SECRET=' "$HERMES_HOME/.env" 2>/dev/null; then
  say "Scene walks: configured (PARACOSM_WALK_URL + WALK_SIGNING_SECRET)."
else
  say "Scene walks: not configured — optional, see IMPLEMENTATION.md §3c."
fi

say ""
say "IMPORTANT — one manual config step (installer won't touch config.yaml):"
say "  Add this to $HERMES_HOME/config.yaml so AGENTS.md and games/ resolve"
say "  correctly no matter how the gateway service is launched:"
say ""
say "    terminal:"
say "      cwd: \"$WORKSPACE\""
say ""
say "  Without this, terminal.cwd defaults to the gateway's launch directory,"
say "  and AGENTS.md / games/ / templates/ may silently fail to load."
say ""
say "Done. Next steps (full guide: IMPLEMENTATION.md):"
say "  1. hermes gateway setup     # connect Telegram if you haven't"
say "  2. hermes gateway install   # keep the gateway (and cron ticks) running"
say "  3. Message your bot — the lobby answers. /new-game to begin."
