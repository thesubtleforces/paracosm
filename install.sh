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

# --- persona + protocol into the workspace -----------------------------------
act "create workspace $WORKSPACE"           mkdir -p "$WORKSPACE"
act "install SOUL.md -> workspace"          cp "$SRC_DIR/hermes/SOUL.md"   "$WORKSPACE/SOUL.md"
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

# --- environment check ---------------------------------------------------------
say ""
if [ -n "${FAL_KEY:-}" ] || grep -qs '^FAL_KEY=' "$HERMES_HOME/.env" 2>/dev/null; then
  say "FAL_KEY: found — scene art & cutscenes enabled."
else
  say "FAL_KEY: NOT found. Paracosm still works (ASCII art fallback)."
  say "  To enable images/video: get a key at https://fal.ai/dashboard/keys and add"
  say "  FAL_KEY=... to $HERMES_HOME/.env"
fi

say ""
say "Done. Next steps (full guide: IMPLEMENTATION.md):"
say "  1. hermes gateway setup     # connect Telegram if you haven't"
say "  2. hermes gateway install   # keep the gateway (and cron ticks) running"
say "  3. Message your bot — the lobby answers. /new-game to begin."
