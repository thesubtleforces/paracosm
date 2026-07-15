#!/usr/bin/env bash
# fal_image.sh — generate an image via fal.ai queue API and download it locally.
#
# Usage:   fal_image.sh "<prompt>" <output_path.png> [aspect] [tier]
#   aspect: landscape_4_3 (default) | portrait_4_3 | square | landscape_16_9 | portrait_16_9
#   tier:   quality (default) | fast
# Env:     FAL_KEY (required)
#          FAL_IMAGE_MODEL      quality-tier model (default fal-ai/flux/dev)
#          FAL_IMAGE_MODEL_FAST fast-tier model    (default fal-ai/flux/schnell)
# Output:  quality tier: {"file": "<path>", "url": "<fal.media url>"} on success (exit 0)
#          fast tier:    {"file": "<path>"} — no URL, so turn art can only be delivered
#                        as a MEDIA: local-path attachment (the url field exists solely
#                        for cutscene keyframe input, which uses quality tier).
#          On failure prints {"error": "..."} and exits non-zero — callers degrade to
#          ASCII art / prose per AGENTS.md; never surface this error in the fiction.
set -u

PROMPT="${1:-}"
OUT="${2:-}"
ASPECT="${3:-landscape_4_3}"
TIER="${4:-quality}"

fail() { printf '{"error": "%s"}\n' "$1" >&2; exit 1; }

case "$TIER" in
  fast)    MODEL="${FAL_IMAGE_MODEL_FAST:-fal-ai/flux/schnell}" ;;
  quality) MODEL="${FAL_IMAGE_MODEL:-fal-ai/flux/dev}" ;;
  *) fail "unknown tier '$TIER' (use fast|quality)" ;;
esac

[ -n "$PROMPT" ] && [ -n "$OUT" ] || fail "usage: fal_image.sh <prompt> <output_path> [aspect] [fast|quality]"

# The gateway may not export custom .env vars to terminal subprocesses — fall back to
# reading FAL_KEY from the Hermes home this copy is installed under. The script may live
# at $HERMES_HOME/skills/<skill>/scripts/ or $HERMES_HOME/workspace/scripts/, so walk
# upward until a .env appears.
if [ -z "${FAL_KEY:-}" ]; then
  DIR="$(cd "$(dirname "$0")" && pwd)"
  i=0
  while [ "$i" -lt 5 ] && [ "$DIR" != "/" ]; do
    if [ -f "$DIR/.env" ]; then
      FAL_KEY=$(sed -n 's/^FAL_KEY=//p' "$DIR/.env" | tail -1 | tr -d '"' | tr -d "'")
      [ -n "$FAL_KEY" ] && break
    fi
    DIR=$(dirname "$DIR"); i=$((i + 1))
  done
fi
[ -n "${FAL_KEY:-}" ] || fail "FAL_KEY not set (env or \$HERMES_HOME/.env)"
command -v curl >/dev/null 2>&1 || fail "curl not found"
command -v python3 >/dev/null 2>&1 || fail "python3 not found"

json_get() { # json_get <key>  — reads JSON on stdin, prints string value or empty
  python3 -c "import sys,json
try: print(json.load(sys.stdin).get('$1',''))
except Exception: print('')"
}

BODY=$(python3 -c "import json,sys;print(json.dumps({'prompt':sys.argv[1],'image_size':sys.argv[2],'num_images':1}))" "$PROMPT" "$ASPECT")

SUBMIT=$(curl -sS --max-time 30 -X POST "https://queue.fal.run/${MODEL}" \
  -H "Authorization: Key ${FAL_KEY}" \
  -H "Content-Type: application/json" \
  -d "$BODY") || fail "submit request failed"

STATUS_URL=$(printf '%s' "$SUBMIT" | json_get status_url)
RESPONSE_URL=$(printf '%s' "$SUBMIT" | json_get response_url)
[ -n "$STATUS_URL" ] && [ -n "$RESPONSE_URL" ] || fail "submit rejected: $(printf '%s' "$SUBMIT" | tr -d '\n' | cut -c1-200)"

# Poll (images are usually <30s; cap at ~2min)
TRIES=0
while [ "$TRIES" -lt 60 ]; do
  STATE=$(curl -sS --max-time 15 -H "Authorization: Key ${FAL_KEY}" "$STATUS_URL" | json_get status)
  [ "$STATE" = "COMPLETED" ] && break
  case "$STATE" in IN_QUEUE|IN_PROGRESS|"") sleep 2 ;; *) fail "generation status: $STATE" ;; esac
  TRIES=$((TRIES + 1))
done
[ "$STATE" = "COMPLETED" ] || fail "timed out waiting for generation"

RESULT=$(curl -sS --max-time 30 -H "Authorization: Key ${FAL_KEY}" "$RESPONSE_URL") || fail "result fetch failed"
IMG_URL=$(printf '%s' "$RESULT" | python3 -c "import sys,json
try:
  d=json.load(sys.stdin); print(d['images'][0]['url'])
except Exception: print('')")
[ -n "$IMG_URL" ] || fail "no image in result: $(printf '%s' "$RESULT" | tr -d '\n' | cut -c1-200)"

mkdir -p "$(dirname "$OUT")"
curl -sS --max-time 120 -o "$OUT" "$IMG_URL" || fail "download failed"
[ -s "$OUT" ] || fail "downloaded file is empty"

if [ "$TIER" = "fast" ]; then
  python3 -c "import json,sys;print(json.dumps({'file':sys.argv[1]}))" "$OUT"
else
  python3 -c "import json,sys;print(json.dumps({'file':sys.argv[1],'url':sys.argv[2]}))" "$OUT" "$IMG_URL"
fi
