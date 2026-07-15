---
name: cutscene
description: Cinematic video for the three big beats
version: 1.1.0
metadata:
  hermes:
    tags: [paracosm, game, media, video]
    category: paracosm
    config:
      - key: paracosm.video_model
        description: "fal.ai image-to-video model id"
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

## Procedure

### 1. Keyframe first (consistency trick)
Generate a still with scene-art's pipeline (same style prefix + locked descriptors) —
this both guarantees the video matches campaign art AND provides the image-to-video
source. Keep the printed fal.media `url` from fal_image.sh output.

### 2. Announce, then generate async
Video takes minutes. Send the narration/moment first, plus one line in voice:
> *The film reel is developing...*
Then run:
```bash
bash scripts/fal_video.sh "<motion prompt>" \
  "<keyframe fal.media url>" "games/<slug>/art/cutscene-<beat>.mp4"
```
(Path relative to the workspace working directory — never the `~/.hermes/skills/...`
copy, which may belong to a different Hermes instance.)
Motion prompt = one sentence of camera + motion ("slow push-in as embers rise, cloak
stirring in the wind"), not a scene re-description. **Always attempt the script — it finds
its own FAL key** (reads the Hermes home's `.env`; the gateway environment is irrelevant).
Degrade only on an actual returned error.

### 3. Deliver
On success, send with a `MEDIA:` tag using the ABSOLUTE file path (relative paths render
as literal text) and a title-card-style caption. Mark the beat in
`cutscenes_used`, journal it.

### 4. Degrade
Script failure or timeout → deliver the keyframe image as the beat's art instead (it
already exists and matches the style). Mark the beat used anyway — the moment was honored;
don't burn retries on spectacle.

## Pitfalls
- Never block a game turn waiting for video — announce and deliver when ready.
- The keyframe URL must be the fal.media URL (public); a local file path will not work as
  `image_url`.
- One video per beat, three beats per campaign — the budget is the aesthetic (and the
  fal bill).

## Verification
`cutscenes_used` shows the beat true; either an .mp4 or the keyframe .png was delivered.
