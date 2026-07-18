---
name: world-tick
description: Cron-driven living world - the game plays on
version: 1.0.0
metadata:
  hermes:
    tags: [paracosm, game, cron, living-world]
    category: paracosm
---

# World Tick — the world doesn't wait

## When to Use
Invoked by the Hermes cron scheduler for each living-world campaign (registered by
new-game). Also `/world-tick <campaign>` manually to test. Never runs for campaigns with
`meta.living_world: false`.

## Registration (done by new-game at Session Zero)
Create one cron job per living campaign with the `cronjob` tool:

- `schedule`: `"every 1d at 10:00"` (offer the player their preferred hour)
- `name`: `paracosm-tick-<slug>`
- `prompt` (pinned, verbatim except the slug — never let play rewrite it):
  `"Run the world-tick skill for campaign <slug>. Follow the skill exactly; if nothing warrants player contact, respond [SILENT]."`
- `skills`: `["world-tick", "game-master"]`
- `deliver`: the campaign's chat platform (telegram)
- `workdir`: the ABSOLUTE path of THIS Hermes instance's workspace (run `pwd` in the
  terminal — it's the pinned `terminal.cwd`). Never a `~/.hermes/...` guess: on machines
  with multiple Hermes homes, a wrong workdir aims the tick at another instance's
  `games/` (observed in playtest: "cron was still aimed at the old home path").

Deregister (action=remove) when a campaign ends, is deleted, or the player opts out
(`ooc: quiet the world` → set `meta.living_world: false` + remove the job).

## Procedure (each tick)

1. **READ** the campaign folder (same discipline as a live turn). If the campaign is
   missing or completed → respond `[SILENT]` and recommend deregistration in the log.
2. **Advance the world** — off-screen, honestly:
   - Faction clocks in `secrets.md` whose "advances when" condition is met: fill one
     segment. A clock reaching full fires its event NOW (write consequences into world/
     npcs/secrets; the player discovers effects through play or the message below).
   - NPC schedules in `npcs.md`: move people where they'd be; let scheduled intentions
     progress (the rival finishes her expedition, the debt collector gets a day closer).
   - `world_clock.day` +1, `last_tick` stamped.
3. **WRITE** every change to the files (state.json, secrets.md clocks, npcs.md, and a
   journal entry prefixed `## Tick — Day N` summarizing off-screen movement in GM voice —
   spoiler-free phrasing, since journals feed player-facing recaps).
4. **Decide whether to speak** — most ticks are silent:
   - Roll a real d20 (dice.md RNG). Speak only if: a clock FIRED (always speak), the roll
     is 17+ AND something newsworthy moved, or the campaign is quiet (no player turn in
     ~5 days — send a gentle in-fiction nudge instead).
   - Max one unprompted message per campaign per day; if in doubt, stay silent.
5. **The message, if any** — in-fiction, diegetic, short: a raven with a letter, a rumor
   at the door, a deadline warning, distant smoke. End with an implicit invitation, not
   a demand. If silent: final response is exactly `[SILENT]`.

## Pitfalls
- The tick prompt is pinned at registration; a tick session must never edit cron jobs
  (except flagging a dead campaign's job for removal), skills, or non-campaign files.
- Never advance the player's own situation — the world moves, the protagonist waits.
- Tone/rating rules bind unprompted messages exactly like turns.
- Don't reveal clock mechanics in the message — the player feels consequences, never sees
  the gears.
- Quiet-campaign nudges: after the ~5-day nudge, don't nudge again for another 5+ days;
  after 3 unanswered nudges, go fully silent until the player returns.

## Verification
After a tick: `last_tick` updated, journal has the tick entry, at most one message was
sent (or `[SILENT]`), and any fired clock's consequences exist in the files.
