---
name: chronicle
description: Illustrated recap of a campaign's story so far
version: 1.0.0
metadata:
  hermes:
    tags: [paracosm, game, recap]
    category: paracosm
---

# Chronicle — the story, bound in leather

## When to Use
`/chronicle [campaign]` — at a campaign's end (offered proactively when an ending lands,
including character death), or any time a player wants the tale-so-far as a keepsake.
Defaults to the chat's active campaign.

## Procedure

### 1. Compile
Read the FULL `journal.md` (the one operation that reads the whole log) plus recap.md and
state.json. Extract:
- Title & epigraph (one in-world quotation from the journey).
- **Chapter beats** — the journal distilled into chapters (act boundaries, or every ~10-15
  turns), each 2-4 sentences in past-tense storyteller voice (a shift from the GM's
  present tense: this is the tale being told after).
- **The numbers**: 🎲 best roll & worst roll (from journal dice fields), ⚔️ body count,
  💰 gold arc, 🗺 places visited, 📅 days elapsed, favorite verb.
- **The cast**: each significant NPC, one line on where the story left them.
- **The ending** (or "...the tale continues" for ongoing campaigns).

### 2. Cover art (optional, offered)
One commemorative image via scene-art's pipeline: style prefix + a "book cover" composition
of the campaign's defining moment. Saved as `games/<slug>/art/chronicle-cover.png`.

### 3. Deliver
As a formatted message series in Telegram: cover image first (MEDIA: tag), then title +
epigraph, then chapters (one message per 2-3 chapters — respect message length), then the
numbers, then the cast. ALSO write the whole chronicle to
`games/<slug>/chronicle.md` so `/saves export` carries it.

## Pitfalls
- Chronicles include only what the player experienced — secrets.md stays sealed even
  after the ending, UNLESS the campaign is truly complete and the player asks for the
  "behind the curtain" appendix (then, and only then, reveal with showmanship).
- Long campaigns: compile chapters act-by-act to keep each read bounded; never dump the
  raw journal at the player.
- Ongoing campaigns get a chronicle too — it just ends mid-story, like all the best ones.

## Verification
chronicle.md exists in the campaign folder; every chapter cites events that are actually
in the journal; the numbers come from journal data, not invention.
