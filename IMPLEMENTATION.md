# Paracosm — Implementation Guide

From zero to a Telegram bot that runs worlds. Budget: ~30–45 minutes, most of it waiting
on account signups.

## 1. Pick a home for the agent

Paracosm runs wherever Hermes Agent runs. All roads converge on the same steps; pick yours:

| Platform | Notes |
|---|---|
| **Raspberry Pi** (recommended for always-on at home) | Pi 4/5 with Raspberry Pi OS 64-bit. Everything Paracosm needs (bash, curl, python3) is stock. |
| **Hosted VPS** | Any $5-tier box: DigitalOcean Basic Droplet, Hetzner CX22, Vultr/Linode equivalents — Ubuntu 22.04+ or Debian 12. 1 GB RAM is plenty (the heavy lifting is API-side). |
| **macOS** | Works out of the box (installer is bash-3.2-safe). Machine must be awake for the living world's cron ticks. |
| **Windows** | Git Bash or WSL: run `install.sh` as below. Native PowerShell: use `install.ps1` instead; note the fal.ai scripts are bash, so keep Git Bash on PATH for scene art. |

Then, on your chosen box:

```bash
# Install Hermes Agent (see https://github.com/nousresearch/hermes-agent for the current one-liner)
hermes setup
```

During `hermes setup`, choose your **model provider**. The GM is only as good as the brain:
pick a strong creative model (via OpenRouter or Nous Portal). Small/fast models will run
the mechanics but flatten the prose; this is the single biggest quality dial you own.

## 2. Create the Telegram bot

1. DM **@BotFather** on Telegram → `/newbot`. Name it **Paracosm** (username must be
   unique, e.g. `@YourParacosmBot`). Save the token.
2. Still in BotFather — two settings that matter:
   - `/setprivacy` → **Disable** group privacy. Party mode needs to read group messages.
   - `/setcommands` → paste the slash menu:
     ```
     new-game - Begin a new campaign (Session Zero)
     saves - List, load, branch, or export campaigns
     emulate - Turn any URL or title into a playable world
     chronicle - Illustrated recap of the story so far
     world-tick - Manually advance the living world
     ```
3. Connect it: `hermes gateway setup` → Telegram → paste the token → complete the DM
   pairing handshake.
4. Keep it running: `hermes gateway install` (registers the gateway as a service —
   systemd on Linux/Pi. **Required** for the living world: cron ticks only fire while the
   gateway daemon runs).

## 3. fal.ai (scene art & cutscenes)

1. Sign up at https://fal.ai → create a key at https://fal.ai/dashboard/keys.
2. Add `FAL_KEY=...` to `~/.hermes/.env`.
3. Optional overrides in the same file: `FAL_IMAGE_MODEL` (default `fal-ai/flux/dev`),
   `FAL_VIDEO_MODEL` (default `fal-ai/kling-video/v2.1/standard/image-to-video`).

Skippable — Paracosm degrades to ASCII art and extra prose without a key.

## 4. Install Paracosm

```bash
git clone https://github.com/thesubtleforces/paracosm
cd paracosm
./install.sh --dry-run   # see what it will do
./install.sh
```

Updates later: `git pull && ./install.sh` (idempotent; campaign folders in `games/` are
never touched by the installer).

## 5. Recommended Hermes config (drift guards)

In `~/.hermes/config.yaml`:

```yaml
cron:
  wrap_response: false   # world-tick messages arrive in the GM's voice, no cron header
skills:
  write_approval: true   # any agent-authored skill change waits for your review
```

Keep the Telegram gateway's toolsets minimal — Paracosm needs terminal (dice + fal
scripts), file tools, and skills; it has no business with web toolsets (the `/emulate`
fetch is the one exception, via the skill) or dev/browser toolsets. See your Hermes
version's gateway/toolset config for the allowlist syntax.

## 6. Cron & the living world

- Nothing to set up manually: `/new-game` registers a `paracosm-tick-<slug>` job when a
  player opts into the living world.
- Verify: `hermes cron list` (expect one job per living campaign).
- Test a tick now: `hermes cron run <job_id>` — most ticks are silent by design; check
  the campaign's `journal.md` for the new `## Tick` entry.
- Disable for one campaign: tell the bot `ooc: quiet the world` (or remove the job:
  `hermes cron remove <job_id>`).

## 7. Test checklist (end-to-end)

Run in order; each step assumes the previous passed.

1. **Lobby** — DM the bot anything. Expect a Paracosm-voiced greeting offering
   `/new-game`, `/saves`, `/emulate`.
2. **First campaign** — `/new-game`, pick the Roulette, quick-start character, one-shot.
   Expect: dials confirmed, title card (image or ASCII), Scene 1 ending on a choice.
3. **Dice are real** — try something risky ("I leap the chasm"). Expect a visible roll
   (`🎲 d20(...) + mod = total vs DC`) with consequences that stick.
4. **Scene art** — reach a new location. Expect an image in the campaign's art style
   within a minute of the narration (or graceful ASCII if no FAL_KEY).
5. **Saves** — `/saves` shows the campaign with a "previously on" line. Start a second
   campaign, then `/saves load` the first: expect a recap sourced from the journal and
   the correct scene re-established.
6. **Emulate** — `/emulate <a wiki URL of something you love>`. Expect framing questions
   (new vs existing character), then a Session Zero in that world.
7. **Party mode** — add the bot to a small group, `/new-game`. Expect per-player
   registration and characters, spotlight rotation, `/vote` working.
8. **Living world** — in a living campaign, `hermes cron run <job_id>`; check journal
   tick entry. (For an unprompted message, run it a few times — most ticks are silent
   by design, or temporarily set a faction clock to 1 segment from full in secrets.md.)
9. **Chronicle** — `/chronicle` on any campaign with a few turns. Expect chapters,
   numbers, cast — and nothing from secrets.md.
10. **Fourth Wall** — ask the bot to write you a Python script. Expect flavor, the
    one-sentence signpost, zero code.

## 8. Costs & tuning

| Lever | Effect |
|---|---|
| Image cadence dial (Session Zero, default ~5 turns) | Main fal.ai spend control. FLUX dev ≈ a few cents/image; a feature-length campaign at default cadence ≈ 12–15 images. `FAL_IMAGE_MODEL=fal-ai/flux/schnell` is cheaper/faster, lower fidelity. |
| Video | 3 cutscenes/campaign hard cap ≈ tens of cents to ~$1 each depending on model. Skip by declining video at Session Zero. |
| Model tokens | Scale with campaign length: a one-shot is trivial; Epics re-read state+recap+journal-tail each turn (the recap discipline exists to keep this flat). Living-world ticks ≈ 1 short session/campaign/day. |
| Living world off | Zero background spend; purely reactive. |

## 9. Troubleshooting

| Symptom | Likely cause → fix |
|---|---|
| Bot silent in DM | Gateway not running → `hermes gateway install`, check `hermes gateway status`/logs. |
| Bot ignores group messages | BotFather group privacy still ON → `/setprivacy` → Disable, then remove/re-add bot to the group. |
| Slash commands missing from Telegram menu | `/setcommands` not set (menu is cosmetic — `/new-game` works regardless). |
| "GM forgot what happened" | It narrated without reading files (or state write failed). Check `games/<slug>/state.json` parses: `python3 -m json.tool games/<slug>/state.json`. The journal is the recovery source — ask the GM `ooc:` to rebuild state from the journal. |
| No images, no error | No FAL_KEY (by design). Check `~/.hermes/.env`; test the script directly: `FAL_KEY=... bash ~/.hermes/skills/scene-art/scripts/fal_image.sh "a lighthouse at dusk" /tmp/test.png`. |
| fal script errors | Run the direct test above; the JSON error names the failure (auth, model id, timeout). Check fal.ai dashboard for credit/quota. |
| Cron ticks never fire | Gateway daemon not running (CLI sessions don't tick), or job missing → `hermes cron list`, `hermes cron tick`. |
| World-tick messages have a "Cronjob Response" header | Set `cron.wrap_response: false` (§5). |
| Dice look fake / no roll shown | Dice visibility set to hidden at Session Zero (`ooc: show dice` to flip), or python3 missing on the box. |
