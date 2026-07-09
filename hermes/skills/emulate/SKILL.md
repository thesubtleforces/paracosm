---
name: emulate
description: Turn any media property URL into a playable world
version: 1.0.0
metadata:
  hermes:
    tags: [paracosm, game, setup, web]
    category: paracosm
---

# Emulate — play inside any world

## When to Use
`/emulate <URL>` or `/emulate <title>` — a wiki page, review, official site, or just a
name ("The Expanse", "Studio Ghibli", "Blade Runner"). Produces a world bible that riffs
on the property, then hands off to new-game.

## Procedure

### 1. Source the property
- URL given: fetch it (this is the ONE sanctioned web access in Paracosm — see AGENTS.md
  guardrails). Extract: setting & era, rules of the world (tech/magic/physics), major
  factions, iconic characters, tone, and visual identity. One page is usually enough;
  follow at most 1-2 obvious links (e.g. a "world/setting" page) if the first is thin.
- Title only: build from knowledge, saying so ("working from memory of the property —
  correct me if my Middle-earth is off").

### 2. Frame the fiction (ask the player, 2 questions max)
- **Your place in it:** a NEW character in that world (default — most room to play), or
  an existing character (playable, with a "canon-adjacent" caveat: the story will diverge,
  that's the point).
- **When:** during the canon events, before, after, or a corner of the world canon never
  visited (default).

### 3. Build the bible — riff, don't transcribe
Write `world.md` as a NEW story in that world: canon-adjacent, honoring the rules and tone,
but with original plot, original supporting cast (canon characters may cameo per the
player's framing), and original secrets/puzzles in `secrets.md`. Derive `style.md` from
the property's visual identity described in your own words (e.g. "hand-painted watercolor
backgrounds, soft natural light, pastoral warmth" — describe the look, don't invoke
trademarks as style tokens if a description serves).

**Homage note (bake into behavior, mention at setup):** this is personal-use homage at a
private table — never reproduce copyrighted text passages, song lyrics, or scripts
verbatim; the property inspires the world, the play is original.

### 4. Hand off
Jump into new-game's procedure at step 2 with genre/tone/rating pre-filled from the
property (player can still adjust every dial), then folder build, character, title card,
Scene 1 as normal.

## Pitfalls
- Don't fetch beyond the property page(s) — no general web wandering.
- Rating still governs: emulating a violent property doesn't override the table's rating
  dial.
- If the fetch fails, fall back to title-only mode rather than erroring out.
- Beloved properties earn extra care with tone — getting the *feel* right matters more
  than lore completeness.

## Verification
world.md names the property as inspiration and contains an original premise; secrets.md
has original content; style.md describes (not just names) the visual identity.
