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
campaign this chat's marker file `games/.active/<chat_id>` points to (if any) as ▶ active.

### load <name>
1. Match name/slug fuzzily. Ambiguity → ask. **No match → SAY SO** — "nothing on the
   shelf matching *orbital ballroom*; here's what exists: …" and list the shelf. A silent
   or empty reply to a `/saves` command is a bug, full stop.
2. Set as the chat's active campaign: **write the slug into THIS chat's marker file
   `games/.active/<chat_id>`** (chat id from the current message's metadata, never from
   session memory); also update `meta.telegram_chat_id` + `meta.last_played` in the
   campaign's state. Never touch another chat's marker.
3. Re-read state.json + recap.md + last ~10 journal entries (never trust prior chat
   context — this is a hard context reset for the fiction).
4. Deliver a "previously on..." recap (3-6 sentences from recap + journal tail), then
   re-establish the current scene and end on the numbered choice block.

### branch <name> [new-name]
Copy the ENTIRE folder `games/<slug>/` → `games/<new-slug>/` (default `<slug>-branch-N`).
Append a journal entry in the copy noting the fork point ("a timeline diverges here").
Original untouched. Then offer to load the branch.

### delete <name>
**Scope check first:** deletion is allowed ONLY if the campaign's
`meta.telegram_chat_id` equals the CURRENT chat's id. A campaign registered to another
chat is not yours to delete — refuse and say which chat owns it. Then confirm explicitly
(show the shelf card, list exactly what will be removed, require a yes — in party mode,
from a human, not a vote). Then remove the folder, THIS chat's marker file if it points
at the deleted slug, and the campaign's living-world cron if one exists. Offer
`/saves export` first as a courtesy.

### clear ("start over", "wipe this chat", "clear history")
Remove THIS chat's marker file. **That is the entire operation.** Campaigns are never
deleted by a clear — they go back on the shelf, loadable by any chat that owns them.
Confirm what happened in one line ("this table's blank; your campaigns are still on the
shelf"). If the player explicitly wants campaign folders gone too, that's `/saves delete
<name>`, one at a time, with its scope check.

### export <name>
Zip the campaign folder from the terminal, portably:
`cd games && python3 -m zipfile -c <slug>-export.zip <slug>/` — then send the archive with
a `MEDIA:` tag with the ABSOLUTE zip path (the gateway ships it as a file; add `[[as_document]]` to preserve
bytes). Remove the zip after delivery.

## Pitfalls
- Loading must actually re-read files; a recap generated from chat memory will drift.
- Never delete without the explicit confirmation in this same conversation, and never
  delete outside the chat-ownership scope check — a real playtest lost a live campaign
  to an over-broad "clear history" wipe.
- Every `/saves` subcommand replies with SOMETHING — an empty message on a fuzzy-miss
  (`/saves load orbital ballroom` → silence) is a known bug pattern; name what didn't
  match and show the shelf instead.
- Branch copies journal history verbatim — do not summarize or trim it.
- Two campaigns may share a chat over time, but only ONE is active per chat at a moment.
- The chat id in every registry operation comes from the current message's metadata —
  session memory once produced a user id in a group and cross-linked two tables.

## Verification
After load: the active campaign's `telegram_chat_id` matches this chat and the recap cites
real journal entries. After branch: both folders parse and diverge only in meta + the fork
journal entry.
