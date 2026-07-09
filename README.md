# PARACOSM

*n. — a richly detailed imaginary world.*

A text-adventure Game Master that lives in your Telegram. Modern AI wearing the skin of
the classics — Zork's `>` prompt, the basement D&D table, the MUD at 2am — with real dice,
real consequences, illustrated scenes, and worlds generated the moment you ask for them.

Built as a persona + skill pack for [NousResearch Hermes Agent](https://github.com/nousresearch/hermes-agent).
No app, no server code of its own: markdown, a few small scripts, and a good brain.

```
> You stand at the edge of the ruined causeway. Below, the salt marsh
> exhales its evening fog. Something in the reeds is wearing a lantern
> the way a angler-fish wears its lure.
>
> The ferryman said three coins. You have two.

what do you do?
```

## What it does

- **🎲 Real gameplay** — d20 + stats vs DC, rolled by an actual RNG and shown in the open.
  Combat, skill checks, inventory, economy. Puzzles whose solutions are pre-committed
  before you ever see them (no "the GM made it up when you guessed").
- **🌍 Worlds on demand** — `/new-game` interviews you (or you spin the Roulette): genre,
  tone, rating, difficulty, permadeath, campaign length from one-shot to infinite sandbox.
- **🎨 Illustrated** — scene art at the big moments via fal.ai FLUX, with a locked
  per-campaign style bible so turn 40 looks like turn 1. Three cinematic video cutscenes
  per campaign: title, set piece, ending.
- **💾 Real saves** — every campaign is a folder of readable files: world bible, character
  sheet, append-only journal, GM secrets. List, load, **branch into what-if timelines**,
  export as a zip.
- **📼 Emulation mode** — `/emulate <URL or title>` turns any media property into a
  playable, canon-adjacent campaign in that world's rules, tone, and look.
- **👥 Party mode** — drop the bot in a group chat: everyone gets a sheet, initiative
  order in fights, spotlight rotation, `/vote`, and private DM side-scenes for the rogue
  who slips away.
- **🌒 A living world** — opt in and the world moves while you're away: faction clocks
  advance on a daily cron, and sometimes a raven finds you — an unprompted, in-fiction
  message. Quiet worlds nudge gently; they never spam.
- **📖 The chronicle** — `/chronicle` binds your journal into an illustrated recap:
  chapters, best rolls, body count, the cast, the ending.

And it is *only* a Game Master. Ask it to write code and you'll meet the Fourth Wall — an
unwinnable meta-mystery with escalating flavor text. (Your actual answer is one polite
sentence: it only runs games.)

## Repo tour

```
hermes/SOUL.md            the Game Master persona & ethics
hermes/AGENTS.md          operating protocol: turn contract, media budget, guardrails
hermes/skills/            nine skills: new-game, game-master (+ dice/combat/puzzle/
                          fourth-wall references), saves, emulate, scene-art, cutscene,
                          party-mode, world-tick, chronicle
templates/campaign/       the save-file schema every campaign is born from
install.sh / install.ps1  idempotent installers (--dry-run supported)
IMPLEMENTATION.md         the full setup guide: Pi / VPS / macOS / Windows
```

## Quick start

```bash
git clone https://github.com/thesubtleforces/paracosm
cd paracosm && ./install.sh
```

Prereqs: a working Hermes Agent install with a Telegram bot connected, and (optionally) a
`FAL_KEY` for images/video. **[IMPLEMENTATION.md](IMPLEMENTATION.md)** walks the whole
path — box provisioning to test checklist — in ~30 minutes.

## License & the emulation note

Personal-use project. Emulation mode is homage at a private table: it riffs on worlds,
never reproduces copyrighted text.
