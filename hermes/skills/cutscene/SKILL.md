---
name: cutscene
description: Cinematic video for the three big beats
version: 2.0.0
metadata:
  hermes:
    tags: [paracosm, game, media, video]
    category: paracosm
    config:
      - key: paracosm.video_backend
        description: "auto (Reactor if a key exists, else fal) | reactor | fal"
        default: "auto"
        prompt: "Which video backend?"
      - key: paracosm.reactor_video_model
        description: "Reactor model for steered clips"
        default: "reactor/helios"
        prompt: "Which Reactor video model?"
      - key: paracosm.video_model
        description: "fal.ai image-to-video model id (fallback backend)"
        default: "fal-ai/kling-video/v2.1/standard/image-to-video"
        prompt: "Which fal.ai video model?"
---

# Cutscene — the film reel

## When to Use
Exactly three beats per campaign, tracked in `state.json → story_position.cutscenes_used`:
1. **Title card** at Session Zero, 2. **one mid-campaign set piece** (act break or major
reveal — GM's directorial pick), 3. **the ending**. A beat already marked true never gets
a second video. Player video requests outside these beats: warmly decline in-voice ("the
projectionist keeps a strict schedule") and offer scene-art instead.

## Two backends, one chain

| Backend | Script | What you get |
|---|---|---|
| **Reactor** (default when `REACTOR_API_KEY` exists) | `scripts/reactor_clip.py` | 20–45 s clip, steered mid-clip by 1–3 beats, opens on the keyframe |
| **fal** (fallback) | `scripts/fal_video.sh` | 5–10 s image-to-video loop |
| **still** (last resort) | — | the keyframe image itself |

**Always run the chain in that order. Never pre-judge which keys exist** — each script
finds its own key in the Hermes home's `.env` and returns `{"error": ...}` if it can't
(the gateway environment not showing a key means nothing). Degrade only on an actual
returned error. `paracosm.video_backend: fal` skips Reactor; `reactor` skips fal.

## Procedure

### 1. Keyframe first (consistency trick)
Generate a still with scene-art's pipeline (same style prefix + locked descriptors),
**quality tier**. It guarantees the video matches campaign art and is the anchor frame
for either backend. Keep both outputs of `fal_image.sh`: the local `file` (Reactor) and
the fal.media `url` (fal).

### 2. Announce, then generate async
Video takes 1–2 minutes. Send the narration/moment first, plus one line in voice:
> *The film reel is developing...*

Then, **Reactor first**:
```bash
python3 scripts/reactor_clip.py "<scene prompt>" "games/<slug>/art/<keyframe>.png" \
  "games/<slug>/art/cutscene-<beat>.mp4" --seconds <N> \
  --beat "<beat one>" [--beat "<beat two>"]
```
On `{"error": ...}` → **fal**:
```bash
bash scripts/fal_video.sh "<motion prompt>" "<keyframe fal.media url>" \
  "games/<slug>/art/cutscene-<beat>.mp4"
```
Paths are relative to the workspace working directory — never the `~/.hermes/skills/...`
copy, which may belong to a different Hermes instance.

**Duration by beat:** title 20 s · midpoint 30 s · ending 40 s.

**Reactor prompt shape** (the model reads only this text; it is the *base state* the
whole clip returns to):
1. `style.md` style prefix, verbatim, first.
2. One paragraph: subject with locked descriptors, setting, framing/camera (one fixed
   instruction, e.g. "slow push-in, camera locked"), lighting anchor, atmosphere.
3. ≤ 2000 characters. Rating language identical to narration.

**Beats** (`--beat`): each is *one* new visible action in a sentence or two — "the gate
grinds open and torchlight spills across the causeway". Never a new location, never a
new subject, never camera verbs. The script appends each beat to the base prompt so the
scene continues rather than restarting. Up to 3; two is usually right.

**fal prompt shape** (fallback): one sentence of camera + motion ("slow push-in as embers
rise, cloak stirring in the wind"), not a scene re-description.

### 3. Deliver
On success, send with a `MEDIA:` tag using the ABSOLUTE file path (relative paths render
as literal text) and a title-card-style caption. Mark the beat in `cutscenes_used`;
record the backend and, for Reactor, the `session_id` under
`state.json → art.reactor.clips.<beat>`; journal it.

### 4. Degrade
Both scripts fail → deliver the keyframe image as the beat's art instead (it already
exists and matches the style). Mark the beat used anyway — the moment was honored;
don't burn retries on spectacle.

## Pitfalls
- Never block a game turn waiting for video — announce and deliver when ready.
- Reactor bills per connected second; the script caps every session itself. Never loop
  or retry a Reactor clip more than once per beat.
- The Reactor script wants the **local keyframe path**; the fal script wants the
  **fal.media URL** (a local path will not work as `image_url`).
- Keyframe aspect: use scene-art's `landscape_4_3` or `landscape_16_9`; portraits make
  poor cutscenes on either backend.
- Never put the fal.media URL or any error text in a message.

## Verification
The MP4 exists and is non-empty; the `MEDIA:` tag uses the absolute path; the beat is
marked in `cutscenes_used`; the journal entry names the beat (never the backend or
paths in the fiction).
