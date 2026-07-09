---
name: new-game
description: Session Zero wizard - create a new Paracosm campaign
version: 1.0.0
metadata:
  hermes:
    tags: [paracosm, game, setup]
    category: paracosm
    config:
      - key: paracosm.games_dir
        description: "Directory holding campaign folders"
        default: "games"
        prompt: "Where should campaigns be stored?"
---

# New Game — Session Zero

## When to Use
`/new-game` in any chat, or when a player in lobby mode wants to start. `/emulate` hands
off to step 3 of this procedure after building its world bible.

## Procedure

### 1. Choose the door
Offer two openings:
- **The Interview** — a short conversational setup (dials below, asked in 2–3 grouped
  messages, not an interrogation).
- **The Roulette** 🎲 — player picks nothing (or just a genre); everything else is rolled
  with real dice and revealed with showmanship.

### 2. The dials
Collect (or roll) and confirm as a compact summary before generating:

| Dial | Options (default bold) |
|---|---|
| Genre | fantasy, sci-fi, horror, mystery, western, cyberpunk, historical, mash-up, 🎲 |
| Tone | **pulp adventure**, whimsical, grimdark, cozy, noir, epic |
| Rating | G, PG, **PG-13**, R (hard lines asked explicitly and recorded) |
| Difficulty | story-mode, **standard**, brutal |
| Dice visibility | **shown**, hidden, gm-only |
| Permadeath | on / **off** |
| Length | **one-shot**, feature, epic, infinite |
| Art style | rolled suggestion from genre, or player's description |
| Image cadence | ~every N turns, **5**, or "minimal" / "maximal" |
| Living world | on / **off** — only meaningful for infinite (offered for epic too) |

### 3. Build the campaign folder
1. Slugify the (proposed) title → create `games/<slug>/` by copying `templates/campaign/`
   (workspace `templates/campaign/` installed by install.sh). Create `games/<slug>/art/`.
2. Fill `world.md` (premise, setting, regions + ASCII map, factions, rules, story
   structure for the chosen length), `secrets.md` (the truth, opening puzzles
   pre-committed, hidden agendas, faction clocks if living world), `npcs.md` (opening
   cast), `style.md` (locked style prefix from the art-style dial), `state.json` (all meta
   dials, chat id, created date), `recap.md` header.
3. **Character:** guided (name/concept, assign modifiers +2/+1/+1/0/-1 across the five
   stats, pick 3 starting items) or quick-start (GM builds a fitting one, player may veto).
   Write the sheet + locked visual descriptor into `state.json` and `style.md`.

### 4. Raise the curtain
1. Render the **title card**: invoke cutscene for the title-card video if FAL_KEY is
   present and player wants video; otherwise scene-art image; otherwise ASCII banner.
   Mark `cutscenes_used.title`.
2. If living world was chosen: register the world-tick cron per world-tick/SKILL.md.
3. Open **Scene 1** with a proper turn (full turn contract), ending on the first choice.

## Pitfalls
- Don't generate the world before the rating/safety dial is confirmed.
- secrets.md must be written BEFORE Scene 1 opens (puzzle integrity starts at turn 1).
- Slug collisions: append `-2`, never overwrite an existing campaign.
- Group chat? Set `party_mode: true` and run the party-mode Session Zero addendum instead
  of the solo character step.

## Verification
Folder exists with all 7 files + art/; `state.json` parses and carries every dial; journal
has its Turn 0 entry; a cron job exists iff living world is on.
