#!/usr/bin/env bash
# fal_video.sh — generate a short video via fal.ai queue API (image-to-video) and download.
#
# Usage:   fal_video.sh "<motion prompt>" <keyframe_image_url> <output_path.mp4>
#   keyframe_image_url: a public URL — typically the fal.media URL printed by fal_image.sh
#   (generate the keyframe first for visual consistency, then animate it).
# Env:     FAL_KEY (required)
#          FAL_VIDEO_MODEL (default fal-ai/kling-video/v2.1/standard/image-to-video)
# Output:  {"file": "<path>", "url": "<fal.media url>"} on success; {"error": "..."} + exit 1
#          on failure. Callers degrade gracefully (deliver the keyframe image instead).
set -u

PROMPT="${1:-}"
IMAGE_URL="${2:-}"
OUT="${3:-}"
MODEL="${FAL_VIDEO_MODEL:-fal-ai/kling-video/v2.1/standard/image-to-video}"

fail() { printf '{"error": "%s"}\n' "$1" >&2; exit 1; }

[ -n "$PROMPT" ] && [ -n "$IMAGE_URL" ] && [ -n "$OUT" ] || fail "usage: fal_video.sh <prompt> <keyframe_url> <output_path>"
[ -n "${FAL_KEY:-}" ] || fail "FAL_KEY not set"
command -v curl >/dev/null 2>&1 || fail "curl not found"
command -v python3 >/dev/null 2>&1 || fail "python3 not found"

json_get() {
  python3 -c "import sys,json
try: print(json.load(sys.stdin).get('$1',''))
except Exception: print('')"
}

BODY=$(python3 -c "import json,sys;print(json.dumps({'prompt':sys.argv[1],'image_url':sys.argv[2]}))" "$PROMPT" "$IMAGE_URL")

SUBMIT=$(curl -sS --max-time 30 -X POST "https://queue.fal.run/${MODEL}" \
  -H "Authorization: Key ${FAL_KEY}" \
  -H "Content-Type: application/json" \
  -d "$BODY") || fail "submit request failed"

STATUS_URL=$(printf '%s' "$SUBMIT" | json_get status_url)
RESPONSE_URL=$(printf '%s' "$SUBMIT" | json_get response_url)
[ -n "$STATUS_URL" ] && [ -n "$RESPONSE_URL" ] || fail "submit rejected: $(printf '%s' "$SUBMIT" | tr -d '\n' | cut -c1-200)"

# Video takes minutes — poll every 10s, cap ~15min. Callers run this async ("the film
# reel is developing...") and deliver on completion; never block a game turn on it.
TRIES=0
while [ "$TRIES" -lt 90 ]; do
  STATE=$(curl -sS --max-time 15 -H "Authorization: Key ${FAL_KEY}" "$STATUS_URL" | json_get status)
  [ "$STATE" = "COMPLETED" ] && break
  case "$STATE" in IN_QUEUE|IN_PROGRESS|"") sleep 10 ;; *) fail "generation status: $STATE" ;; esac
  TRIES=$((TRIES + 1))
done
[ "$STATE" = "COMPLETED" ] || fail "timed out waiting for video"

RESULT=$(curl -sS --max-time 30 -H "Authorization: Key ${FAL_KEY}" "$RESPONSE_URL") || fail "result fetch failed"
VID_URL=$(printf '%s' "$RESULT" | python3 -c "import sys,json
try:
  d=json.load(sys.stdin)
  v=d.get('video') or (d.get('videos') or [{}])[0]
  print(v.get('url',''))
except Exception: print('')")
[ -n "$VID_URL" ] || fail "no video in result: $(printf '%s' "$RESULT" | tr -d '\n' | cut -c1-200)"

mkdir -p "$(dirname "$OUT")"
curl -sS --max-time 600 -o "$OUT" "$VID_URL" || fail "download failed"
[ -s "$OUT" ] || fail "downloaded file is empty"

python3 -c "import json,sys;print(json.dumps({'file':sys.argv[1],'url':sys.argv[2]}))" "$OUT" "$VID_URL"
