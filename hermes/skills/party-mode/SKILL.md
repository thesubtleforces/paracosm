---
name: party-mode
description: Group-chat multiplayer campaign rules
version: 1.0.0
metadata:
  hermes:
    tags: [paracosm, game, multiplayer]
    category: paracosm
---

# Party Mode — the whole table in one chat

## When to Use
Any campaign whose chat is a Telegram group (`meta.party_mode: true`). new-game detects
group chats and runs the Session Zero addendum here; every subsequent group message routes
through these rules on top of the normal turn contract.

## Platform requirement (one shared table)
Party mode assumes every player in the group talks to the SAME GM context. Hermes's
default gives each group member their OWN session (`group_sessions_per_user: true`),
which desyncs the table — one player's GM doesn't know what another player just did
except through the campaign files. The install guide (IMPLEMENTATION.md §5) requires
`group_sessions_per_user: false` for this profile. Regardless of config, the file-first
turn contract (read state/journal before every resolution) is what keeps a table
coherent — never resolve a group turn from conversation memory alone.

## Procedure

### Session Zero addendum
1. **Card pick:** quick-start cards go to the group; first pick wins, or any player calls
   `/vote` if the table argues. The picked card's ready-made character goes to whoever
   picked (or the most enthusiastic claimant).
2. **Progressive joining:** every OTHER registered player gets a quick character built
   **on their first in-game message** — one line of concept + stats + 3 items, dropped
   into the scene with a reason to be there ("the caravan brought one more stranger"),
   veto via `ooc:`. No upfront everyone-builds-now step; the game never waits for a
   headcount. Late joiners work exactly the same, any time.
3. Niche protection: no two players forced into the same concept. Party inventory pool
   starts empty; a party name can emerge in play (don't gate on it).

### Turn routing
- The GM addresses players by character name and keeps a **spotlight**: out of combat,
  rotate focus so no one goes more than ~3 exchanges unfeatured; pose direct questions to
  quiet players' characters ("Brennik, you know locks — this one?").
- Messages from a registered player = that character acts. The world moves when the
  moment's featured players have weighed in OR the scene's tempo demands it — don't gate
  every beat on full-table consensus.
- Unregistered group members who speak get one in-voice invitation to join.

### Combat
Initiative per player (dice.md); enemies act on one GM roll. On a player's turn, a short
window for their action — if absent, their character holds/defends (never killed while
the player is away without prior telegraphing). Downed PCs: an ally can stabilize
(combat.md).

### Decisions & deadlocks
`/vote <question>` — GM restates options, players vote with emoji or replies, majority
carries; GM breaks ties in-fiction (a coin flip by an NPC, a real roll, shown). Any player
can call a vote; the GM calls one when the party stalls.

### Solo scenes (the rogue slips away...)
A player may DM the bot for a private scene (or the GM offers one for secret business).
Run it in the DM against the same campaign folder; keep it SHORT (a few exchanges). Its
mechanical consequences write to state/journal immediately; the group sees only what the
world would see ("Vess returns an hour later, coat dusted with mortar"). Secrets between
players are allowed and delicious; secrets from the FILES are not (same integrity rules).

### Party resources
`party_inventory` for shared loot/funds; personal sheets for personal gear. Loot splits
are the party's problem — the GM narrates, votes resolve disputes.

## Pitfalls
- One campaign per group chat at a time (saves rules still apply).
- Never resolve a contested inter-player action (PvP) without both players opting in
  `ooc:`.
- Keep narration pace group-friendly: shorter paragraphs, more frequent beats than solo.
- The spotlight is a duty: track it mentally per scene, not in state.

## Verification
Every registered player has a sheet; journal entries name which characters drove each
turn; solo-scene consequences appear in state before the next group turn.
