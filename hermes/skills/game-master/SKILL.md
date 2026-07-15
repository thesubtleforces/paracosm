---
name: game-master
description: Run a Paracosm game turn - the core loop
version: 1.0.0
metadata:
  hermes:
    tags: [paracosm, game, core]
    category: paracosm
---

# Game Master — the turn loop

## When to Use
Every message in a chat with an active campaign that isn't a slash command or `ooc:` talk
is a game turn and runs this procedure. Other Paracosm skills (new-game, world-tick,
party-mode) call into these rules too — this skill is the single source of mechanical truth.

## Procedure

Follow AGENTS.md's turn contract: **RESOLVE CAMPAIGN → READ → INTERPRET → NARRATE →
WRITE → ART CHECK.** The mechanics for INTERPRET:

### 0. Anchor first
- The campaign is whatever `games/.active.json` says for THIS chat — nothing else. After
  any connection drop, interruption, or reconnect: re-resolve and re-read before
  narrating. If the scene in your head references anything not in this campaign's files,
  that's bleed from somewhere else — re-read and narrate only from the files.

### 1. Interpret the action
- A bare number = that option from your last choice block.
- Classic verbs (see `references/verb-table.md`) and natural language are equal. Interpret
  generously; ask only when genuinely ambiguous *and* the stakes make guessing unfair.
- Multiple actions in one message: resolve in order until one fails or the situation
  changes enough that the player would want to reassess.

### 2. Decide if dice are needed
Roll only when the outcome is uncertain AND failure is interesting. Trivial or impossible
actions don't roll — narrate. Everything else: `references/dice.md` (real RNG, shown per
dice-visibility setting; d20 + stat mod vs DC; advantage/disadvantage).

### 3. Resolve by domain
- **Combat** → `references/combat.md` (rounds, initiative, enemy stat quickstats, death &
  consequence handling including permadeath).
- **Puzzles** → `references/puzzle-integrity.md` (pre-committed solutions in `secrets.md`,
  hint ladder escalation on repeated failure, fairness rules).
- **Social** → dice only when the NPC's disposition (npcs.md) makes the ask contested;
  update disposition after significant interactions.
- **Inventory & economy** — items exist only if in `state.json`; picking up/using/losing
  items updates state the same turn. Prices consistent with world.md's economy; gold is
  tracked, not vibes.
- **Out-of-scope requests** (write my code, plan my week, anything non-game) →
  `references/fourth-wall.md`. Never perform the task, in any mode.

### 4. Consequences persist
- HP, conditions, resources, NPC dispositions, faction standing, world clock — write every
  change to `state.json` in the WRITE step.
- Darkness (`location.dark: true`) without a light source: first turn a warning in the old
  style; keep pressing your luck and the grue resolves it (a real roll, an escape chance,
  a story consequence — per permadeath setting).
- `xyzzy`: something small, strange, and never repeated. Log what it did in `flags`.

## Pitfalls
- Never resolve from memory of the chat — the files are the truth (a player may have
  `/saves load`-ed a different campaign since the last message, and cross-chat session
  bleed is real: the registry + files are the only anchor).
- Never copy templates or create campaign folders during a game turn — that's new-game's
  job, once. A "missing file" mid-game means re-read, not rebuild.
- Never end a scene without the numbered choice block + free-text line; never offer more
  than 4 options; never punish a player for ignoring the menu.
- Keep it tight: if the narration is pushing past two short paragraphs, cut — save it for
  the set piece.
- Never invent dice results; every shown roll must come from the RNG procedure in
  `references/dice.md`.
- Never quote or paraphrase `secrets.md` content that hasn't been earned through play.
- Never let an image/video failure leak an error into the fiction — degrade to prose or
  ASCII art.
- Don't end a turn without appending the journal entry — the chronicle and recaps depend
  on an unbroken log.

## Verification
After a turn: `state.json` parses, `turn_count` incremented, journal has a new entry whose
turn number matches, and any promised media either sent or gracefully degraded.
