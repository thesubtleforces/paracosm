---
name: saves
description: List, load, branch, delete, export Paracosm campaigns
version: 1.0.0
metadata:
  hermes:
    tags: [paracosm, game, saves]
    category: paracosm
---

# Saves — the campaign shelf

## When to Use
`/saves` and subcommands: `/saves` (list), `/saves load <name>`, `/saves branch <name>
[new-name]`, `/saves delete <name>`, `/saves export <name>`. Also lobby-mode "continue my
game" requests.

## Procedure

### list (default)
Scan `games/*/state.json`. For each campaign show one shelf card:

> 🎮 **The Salt-Glass Crown** — fantasy · feature · Act 2, turn 31 · last played 2026-07-01
> *Previously on: you bargained the ferryman down to one memory, and he chose your name.*

The "previously on" line is distilled from the last journal entry (or recap.md). Mark the
campaign `games/.active.json` maps to THIS chat (if any) as ▶ active.

### load <name>
1. Match name/slug fuzzily; ambiguity → ask.
2. Set as the chat's active campaign: **update this chat's entry in `games/.active.json`**
   (the registry is the single source of truth for chat→campaign); also update
   `meta.telegram_chat_id` + `meta.last_played` in the campaign's state.
3. Re-read state.json + recap.md + last ~10 journal entries (never trust prior chat
   context — this is a hard context reset for the fiction).
4. Deliver a "previously on..." recap (3-6 sentences from recap + journal tail), then
   re-establish the current scene and end on the numbered choice block.

### branch <name> [new-name]
Copy the ENTIRE folder `games/<slug>/` → `games/<new-slug>/` (default `<slug>-branch-N`).
Append a journal entry in the copy noting the fork point ("a timeline diverges here").
Original untouched. Then offer to load the branch.

### delete <name>
Confirm explicitly (show the shelf card, require a yes — in party mode, require it from a
human, not a vote). Then remove the folder AND any `games/.active.json` entries pointing
at it. Offer `/saves export` first as a courtesy. If a living-world cron exists for it,
remove that too.

### export <name>
Zip the campaign folder from the terminal, portably:
`cd games && python3 -m zipfile -c <slug>-export.zip <slug>/` — then send the archive with
a `MEDIA:` path tag (the gateway ships it as a file; add `[[as_document]]` to preserve
bytes). Remove the zip after delivery.

## Pitfalls
- Loading must actually re-read files; a recap generated from chat memory will drift.
- Never delete without the explicit confirmation in this same conversation.
- Branch copies journal history verbatim — do not summarize or trim it.
- Two campaigns may share a chat over time, but only ONE is active per chat at a moment.

## Verification
After load: the active campaign's `telegram_chat_id` matches this chat and the recap cites
real journal entries. After branch: both folders parse and diverge only in meta + the fork
journal entry.
