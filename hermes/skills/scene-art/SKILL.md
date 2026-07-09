---
name: scene-art
description: Generate a scene illustration with locked style
version: 1.0.0
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
        description: "fal.ai model id for scene images"
        default: "fal-ai/flux/dev"
        prompt: "Which fal.ai image model?"
---

# Scene Art — illustrated moments

## When to Use
Called by the game turn's ART CHECK when a moment qualifies under AGENTS.md's media budget
(new location, key NPC intro, dramatic reveal, boss), by new-game (title card fallback),
by chronicle (cover art), and on explicit player request ("show me"). Not a per-turn
default — scarcity is what makes the pictures land.

## Procedure

### 1. Assemble the prompt (consistency is everything)
Concatenate, in order:
1. **Style prefix** from `games/<slug>/style.md` — verbatim, always first.
2. **Scene description** — one tight sentence of the moment being illustrated (subject,
   action, setting, lighting/mood). Written fresh; never paste raw narration.
3. **Locked descriptors** for every recurring subject in frame — copied verbatim from
   `npcs.md` "Descriptor (locked)" / `state.json → art.character_descriptors`. A character
   appearing in art for the FIRST time: write their locked descriptor to those files in
   the same turn, then use it.
4. Style.md's "Never" constraints.

### 2. Generate
```bash
bash ~/.hermes/skills/scene-art/scripts/fal_image.sh "<full prompt>" \
  "games/<slug>/art/turn<NNN>-<slug-hint>.png" <aspect>
```
Aspect per style.md composition rules (default `landscape_4_3`; NPC portraits
`portrait_4_3`). The script prints `{"file": ..., "url": ...}` on success.

### 3. Deliver
Send narration FIRST (never block the turn), then attach the image with a `MEDIA:` path
tag on its own line, plus a one-line caption in scene voice:

```
MEDIA:games/<slug>/art/turn031-ferry.png
```

Reset `turns_since_last_image` in state.json; note the art in the journal entry.

### 4. Degrade gracefully (no FAL_KEY / script error / timeout)
Never mention the failure in-fiction and never retry more than once. Instead deliver ASCII
art (a small, evocative sketch — 10-20 lines max) or an extra flourish of descriptive
prose. Log the real error to the journal entry's notes only.

## Pitfalls
- Style prefix drift breaks the campaign's visual identity — always re-read style.md,
  never reconstruct it from memory.
- Respect `meta.rating` in prompts exactly as in narration.
- Don't illustrate secrets the player hasn't seen (art leaks are still leaks).
- Filenames: always under the campaign's `art/` dir, prefixed with the turn number.

## Verification
Image file exists and is non-empty; the MEDIA: tag path matches it; state + journal updated.
