---
name: new-game
description: Start a campaign - quick cards default, deep wizard opt-in
version: 2.0.0
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

# New Game — from zero to playing in two messages

## When to Use
`/new-game` in any chat (quick start, the default), `/new-game deep` (the full Session Zero
wizard), or a lobby-mode player wanting to start. `/emulate` hands off to the **seed write**
step of quick start after building its world bible.

## Procedure — QUICK START (default)

The contract: **the player is playing by their second message.** Reply 1 = the cards.
Reply 2 = Scene 1. No file I/O before reply 1, no bulk writes ever, no narrating your setup
work.

### Reply 1 — the table cards (instant, zero file I/O)
Post three pre-rolled **table cards** — distinct genres, each 2 lines — plus the
describe-your-own line. Then (art) fire the triptych. Specimen shape:

> 🎴 **1 — THE LONG HAUL** *(trucker noir)*
> Your rig, a corpse in the trailer you didn't load, and 800 miles of witnesses. You: Dee "Redline" Calloway, owes the wrong people.
>
> 🎴 **2 — EMBERWOOD** *(cozy fantasy w/ teeth)*
> The village hedge-witch died and named you successor. The hedge has opinions. You: a baker who knows exactly one spell.
>
> 🎴 **3 — DERELICT** *(deep-space salvage horror)*
> The wreck's black box is still warm. You: last-shift salvager, three days of air, one company lie.
>
> Reply **1**, **2**, or **3** — or **describe your own scenario in a sentence** and I'll build that instead.

- Cards must be freshly invented each time (never reuse the specimen), tonally distinct,
  each with a hook + a ready-made character.
- **Card art:** immediately after posting the text, generate ONE triptych image via
  scene-art (single fal call, fast model): three labeled panels, one per card, each in an
  art style fitting its genre. Send it as its own message when ready — never make the
  player wait for it.
- Group chat: first pick wins, or `/vote` if the table argues.

### Reply 2 — Scene 1 (seed write, then curtain; target under ~60s)
On the pick (a bare number or a described scenario):

1. **Seed write — three small files only.** Create `games/<slug>/` from the template
   (slug from card title; collision → `-2`), then write ONLY:
   - `state.json` — quick-start defaults: PG-13, standard difficulty, dice **shown**,
     permadeath **off**, feature length, image cadence "most turns", living world **off**;
     player sheet from the card's character (stats +2/+1/+1/0/-1 fitting the concept,
     3 starting items); `meta.telegram_chat_id` set.
   - `secrets.md` — a stub: The Truth in 2 sentences + ONE pre-committed opening
     puzzle/lead (solution + hint ladder). That's enough integrity to open fair.
   - `style.md` — the style prefix line (from the card's panel style) + the player
     character's locked descriptor.
   Register the chat in `games/.active.json` (`{"<chat_id>": "<slug>"}` — create the file
   if missing, update the key if present).
2. **Curtain.** Narrate Scene 1 per the turn contract: 1–2 tight paragraphs, straight into
   a situation with stakes, ending on a numbered choice block. One line of orientation for
   first-timers above the scene: *"(Reply with a number, or type anything you want to do.
   `HELP` shows the ropes, `ooc:` talks to me out of character.)"* — first scene only.
3. **Art follows** (scene-art, fast model) as its own message.

**Do NOT write** `world.md`, `npcs.md`, `recap.md`, `journal.md` beyond their template
stubs at seed time — they fill progressively (see below). Do NOT announce any of this
file work in chat; the player sees cards, then a scene.

### Progressive world-building (every turn after)
The world deepens as it's touched, one file section per turn as needed:
- First named NPC → their `npcs.md` entry (with locked descriptor) that same turn.
- First new region → its `world.md` section (+ premise/tone sections on first expansion).
- Journal appends every turn as normal (turn contract); `recap.md` starts at act breaks.
- Secrets grow ahead of play: invent a twist or puzzle → commit it to `secrets.md` in the
  same turn it's introduced, before the player responds.
- **Hard rule: never a bulk multi-file write, never re-copy templates for an existing
  campaign.** If a file seems missing mid-game, re-read the folder — do not rebuild.

### Settings after the fact
Any dial changes any time via `ooc:` ("ooc: make it R-rated", "ooc: permadeath on",
"ooc: fewer pictures") — confirm in one line, write to `state.json`. Offer living world
once, briefly, around Scene 3 ("want this world to keep moving between sessions?") —
if yes, register the world-tick cron per world-tick/SKILL.md.

## Procedure — DEEP MODE (`/new-game deep`)

The full Session Zero ceremony, for tables that want it. Two doors:
- **The Interview** — conversational setup in 2–3 grouped messages.
- **The Roulette** 🎲 — player picks nothing (or just a genre); everything else rolled
  with real dice, revealed with showmanship.

Dials (collect or roll, confirm as a compact summary): genre, tone, rating (ask hard
lines), difficulty, dice visibility, permadeath, length (one-shot/feature/epic/infinite),
art style, image cadence, living world. Then: seed write as in quick start (state +
secrets stub + style), register `.active.json`, character build (guided: name/concept,
+2/+1/+1/0/-1, 3 items — or quick-start with veto), title card via cutscene/scene-art
(quality model), open Scene 1 with the choice block. World files still fill progressively
— deep mode buys richer *dials*, not a 7-file upfront write.

Group chats (either mode): each registered player gets a quick character built **on their
first in-game message** (one line + 3 items, veto via `ooc:`), not as an upfront
everyone-at-once step. Party rules per party-mode/SKILL.md.

## Pitfalls
- Reply 1 before ANY file/tool work — the cards are pure invention.
- Never open Scene 1 before the secrets stub exists (puzzle integrity starts at turn 1).
- Rating: quick start defaults PG-13 without asking; honor `ooc:` changes immediately.
- Slug collisions: append `-2`, never overwrite.
- The specimen cards above are a SHAPE reference; shipping them verbatim is a bug.
- `.active.json`: update the entry — a chat starting a second campaign points at the new
  slug (the old campaign stays on the shelf for `/saves load`).

## Verification
After reply 2: `games/<slug>/` exists with seeded state/secrets/style + template stubs;
`.active.json` maps this chat to the slug; journal has Turn 0 + Scene 1 entries; the
scene ended with a numbered choice block.
