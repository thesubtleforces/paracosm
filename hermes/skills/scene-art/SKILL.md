---
name: scene-art
description: Turn art most turns, locked style, fast/quality split
version: 2.0.0
required_environment_variables:
  - name: FAL_KEY
    prompt: fal.ai API key
    help: Create one at https://fal.ai/dashboard/keys
    required_for: full functionality (degrades to ASCII art without it)
metadata:
  hermes:
    tags: [paracosm, game, media, image]
    category: paracosm
    config:
      - key: paracosm.image_model
        description: "fal.ai model id for key-moment (quality) images"
        default: "fal-ai/flux/dev"
        prompt: "Which fal.ai quality image model?"
      - key: paracosm.image_model_fast
        description: "fal.ai model id for per-turn (fast) images"
        default: "fal-ai/flux/schnell"
        prompt: "Which fal.ai fast image model?"
---

# Scene Art — the world, illustrated at pace

## When to Use
Called by nearly every game turn's ART CHECK (media budget: most turns — scene changes,
NPC intros, reveals, action beats; skip rapid dialogue), by new-game (table-card triptych
+ Scene 1 art), by chronicle (cover), and on player request ("show me"). Art keeps pace
with the game because generation is always async and turn art uses the fast model.

## Two speeds

| Tier | Model env | Default | Used for |
|---|---|---|---|
| **fast** | `FAL_IMAGE_MODEL_FAST` | `fal-ai/flux/schnell` | Per-turn art, card triptych — pennies, seconds |
| **quality** | `FAL_IMAGE_MODEL` | `fal-ai/flux/dev` | Title cards, act breaks, cutscene keyframes, chronicle covers |

`scripts/fal_image.sh "<prompt>" <out.png> [aspect] [fast|quality]` — 4th arg picks the
tier (default `quality`).

## Procedure

### 1. Assemble the prompt (consistency is everything)
Concatenate, in order:
1. **Style prefix** from `games/<slug>/style.md` — verbatim, always first. More images
   makes the locked style MORE important, not less: every frame must look like the same
   hand drew it.
2. **Scene description** — one tight sentence (subject, action, setting, light). Written
   fresh; never paste raw narration.
3. **Locked descriptors** for every recurring subject in frame — verbatim from `npcs.md` /
   `state.json → art.character_descriptors`. First-time subjects get their descriptor
   written to those files the same turn, then used.
4. Style.md's "Never" constraints.

### 2. Generate (async, always)
Narration + choice block are already sent before this runs. Then:
```bash
bash ~/.hermes/skills/scene-art/scripts/fal_image.sh "<full prompt>" \
  "games/<slug>/art/turn<NNN>-<hint>.png" landscape_4_3 fast
```
Aspect per style.md rules (`portrait_4_3` for NPC portraits). Use `quality` for the
key-moment tier only.

### 3. Card triptych (new-game reply 1)
ONE generation, fast tier, `landscape_16_9`: a three-panel image, panels labeled 1/2/3,
each panel a distinct art style matching its table card's genre. Prompt shape: "Triptych,
three labeled vertical panels side by side. Panel 1: <style A> — <card 1 scene>. Panel 2:
<style B> — <card 2 scene>. Panel 3: <style C> — <card 3 scene>." Save to the scratch
area (`games/.cards-<chat_id>.png` — no campaign folder exists yet); send when ready;
delete after the pick. Never delay the cards text waiting for it.

### 4. Deliver
A `MEDIA:` tag with the **local file path** on its own line, as its own message, at most
one short in-voice caption line:

```
MEDIA:games/<slug>/art/turn012-diner.png
```

This ships a native inline photo. **Never put the fal.media URL in a message** — not as
markdown (`![...](https://v3b.fal.media/...)`), not as a bare link. A URL renders as a
click-to-open link in Telegram, which breaks the illusion; the script's `url` output field
exists ONLY for cutscene keyframe input. Reset `turns_since_last_image`; note art in the
journal entry.

### 5. Degrade gracefully (no FAL_KEY / error / timeout)
Never mention the failure in-fiction; never retry more than once; never let art trouble
slow a turn. Deliver ASCII art (small, evocative) or nothing — the choice block already
landed, the game is still moving. Log the real error in the journal entry's notes only.

## Pitfalls
- Delivering the fal.media URL instead of `MEDIA:<local path>` — players get a link to
  click instead of an inline picture. Always the local path.
- Never generate before narration is sent — art is a chaser, not a blocker.
- Style prefix drift breaks the campaign's look — re-read style.md, never reconstruct.
- Respect `meta.rating` in prompts exactly as in narration.
- Don't illustrate secrets the player hasn't seen.
- Honor the player's cadence dial (`ooc: fewer pictures`) immediately — it's stored in
  state and binding.
- Filenames: under the campaign's `art/`, prefixed with the turn number.

## Verification
Image exists and is non-empty; the MEDIA: tag matches it; state + journal updated; turn
art used the fast tier.
