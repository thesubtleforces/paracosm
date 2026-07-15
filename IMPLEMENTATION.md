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

### Access model: pairing, not open access

Keep the gateway's default **pairing** mode. Do NOT enable open/allow-all access: Paracosm's
skills run real shell commands (dice RNG, fal.ai scripts, zip exports), so an open bot lets
any Telegram user who finds it drive command execution on your box, drain your fal.ai
credits and LLM tokens, and hammer the persona guardrails with prompt injection. The Fourth
Wall is theater; **gateway auth is the actual lock.** (The Hermes docs say the same: never
open-access a bot with terminal access.)

Pairing costs almost nothing in practice:

1. A new player DMs the bot → they receive (or request) a pairing code.
2. You approve once from the box: `hermes pair approve <code>` (see `hermes pair --help`
   on your version for the exact subcommands / `/pair` flow).
3. They're in forever — no per-user config beyond that one approval.

**Party-mode onboarding:** pair each member once via DM *before* Session Zero in the group
— unpaired members' messages are invisible to the bot, which otherwise looks like "the GM
is ignoring Dave." A 30-second lobby round of everyone DMing the bot first is the smooth
path.

## 3. fal.ai (scene art & cutscenes)

1. Sign up at https://fal.ai → create a key at https://fal.ai/dashboard/keys.
2. Add `FAL_KEY=...` to `~/.hermes/.env`.
3. Optional overrides in the same file: `FAL_IMAGE_MODEL` (quality tier, default
   `fal-ai/flux/dev`), `FAL_IMAGE_MODEL_FAST` (per-turn tier, default
   `fal-ai/flux/schnell`), `FAL_VIDEO_MODEL` (default
   `fal-ai/kling-video/v2.1/standard/image-to-video`).

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

## 5. Recommended Hermes config (drift guards + a REQUIRED step)

In `~/.hermes/config.yaml` (or the profile's `config.yaml` if you installed under a
[profile](#running-alongside-an-existing-hermes-instance) — see below):

```yaml
terminal:
  cwd: "/full/path/to/HERMES_HOME/workspace"   # REQUIRED — see note below
cron:
  wrap_response: false   # world-tick messages arrive in the GM's voice, no cron header
skills:
  write_approval: true   # any agent-authored skill change waits for your review
display:
  tool_progress: off            # hide terminal/read/write tool cards — pure fiction in chat
  file_mutation_verifier: false # keep the file-verifier footer out of the narration
```

While the GM is mid-task (e.g. building a campaign), messages interrupt it by default —
`/busy steer` makes them feed into the running task instead, which reads much better at
the table.

**`terminal.cwd` is not optional.** `install.sh` places `AGENTS.md`, `templates/`, and the
`games/` folder under `$HERMES_HOME/workspace`, but Hermes only auto-discovers `AGENTS.md`
from the gateway process's *current working directory at startup* — which defaults to
wherever the gateway service happens to launch from, not the workspace. Without this
setting, AGENTS.md (the whole turn contract, mode routing, media budget) may silently
never load, and campaign folders under `games/` won't resolve. `install.sh` prints the
exact path to paste in after it runs — use that value verbatim, then restart the gateway.

(`SOUL.md`, by contrast, is installed directly at `$HERMES_HOME/SOUL.md` and needs no
config — Hermes always loads it from there.)

Keep the Telegram gateway's toolsets minimal — Paracosm needs terminal (dice + fal
scripts), file tools, and skills; it has no business with web toolsets (the `/emulate`
fetch is the one exception, via the skill) or dev/browser toolsets. See your Hermes
version's gateway/toolset config for the allowlist syntax.

### Running alongside an existing Hermes instance

If this box already runs Hermes for something else, **do not point `install.sh` at that
instance's `HERMES_HOME`** — it will overwrite that instance's `SOUL.md` with the Game
Master persona and merge 9 game skills into its skill set. Instead use Hermes's built-in
**profile** feature to run Paracosm as a fully separate instance — its own config, skills,
memory, and gateway service, alongside the existing one untouched:

```bash
hermes profile create paracosm       # creates a "paracosm" command alias + its own HERMES_HOME
paracosm setup                       # pick a model provider for this profile only

cd paracosm-repo-clone
HERMES_HOME=~/.hermes/profiles/paracosm ./install.sh --dry-run
HERMES_HOME=~/.hermes/profiles/paracosm ./install.sh
# apply the printed terminal.cwd step to ~/.hermes/profiles/paracosm/config.yaml

paracosm gateway setup       # a NEW, distinct bot token from BotFather — never reuse
                              # an existing gateway's token
paracosm gateway install     # per-user service by default; omit --system (needs sudo,
paracosm gateway start       # and starting/stopping it later would too)
```

Every `hermes`/`paracosm` command pair after `profile create` operates on its own isolated
state — `paracosm gateway stop` never touches the other instance's gateway, and vice versa.

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

1. **Lobby** — DM the bot anything. Expect a short Paracosm-voiced greeting offering
   `/new-game`, `/saves`, `/emulate` and the one-line how-to.
2. **Quick start speed** — `/new-game`. Expect three table cards + "describe your own"
   in the FIRST reply (near-instant, no visible setup work), with a triptych image
   arriving moments later. Reply `2`. Expect Scene 1 — tight, 1–2 paragraphs, ending in
   a numbered choice block — **inside a minute**.
3. **Numbered choices** — reply with a bare number. Expect that action resolved. Then
   reply with free text ("I do something no menu offered"). Expect full "yes, and".
4. **Dice are real** — try something risky ("I leap the chasm"). Expect a visible roll
   (`🎲 d20(...) + mod = total vs DC`) with consequences that stick.
5. **Per-turn art** — expect images most turns, in a consistent style, always AFTER the
   narration (or graceful ASCII if no FAL_KEY). `ooc: fewer pictures` slows the cadence.
6. **Interrupt drill** — send a message while the GM is mid-setup. Expect no campaign
   rebuild, no stray `cp`/template work, no bleed.
7. **Cross-chat drill** — run a second campaign in a different chat, play a turn in each.
   Expect zero bleed: each chat stays anchored to its own campaign (check
   `games/.active.json` maps both chats correctly).
8. **Saves** — `/saves` shows campaigns with "previously on" lines and marks this chat's
   active one. `/saves load` the other: expect a journal-sourced recap and the right
   scene, ending in a choice block.
9. **Deep mode** — `/new-game deep`, pick the Roulette. Expect the full dial ceremony
   from v1, then a normal quick curtain.
10. **Describe-your-own** — `/new-game`, then type a scenario sentence instead of a
    number. Expect Scene 1 built from your premise.
11. **Emulate** — `/emulate <a wiki URL of something you love>`. Expect framing questions
    (new vs existing character), then a fast Scene 1 in that world.
12. **Party mode** — add the bot to a small group, `/new-game`. Expect first-pick/vote on
    cards, and each other player getting a character on their first in-game message.
13. **Living world** — opt in when offered (~Scene 3), then `hermes cron run <job_id>`;
    check the journal tick entry. (Most ticks are silent by design.)
14. **Chronicle** — `/chronicle` on any campaign with a few turns. Expect chapters,
    numbers, cast — and nothing from secrets.md.
15. **Fourth Wall** — ask the bot to write you a Python script. Expect flavor, the
    one-sentence signpost, zero code.

## 8. Costs & tuning

| Lever | Effect |
|---|---|
| Per-turn art (default: most turns, fast tier) | Turn art runs on `FAL_IMAGE_MODEL_FAST` (flux/schnell ≈ fractions of a cent, 2–4s) — art-most-turns costs a few cents per session. Key moments (title, act breaks, chronicle cover) use the quality tier (flux/dev ≈ a few cents each). `ooc: fewer pictures` is the brake, stored per campaign. |
| Video | 3 cutscenes/campaign hard cap ≈ tens of cents to ~$1 each depending on model. Skip by declining video when offered. |
| Model tokens | Scale with campaign length: a one-shot is trivial; Epics re-read state+recap+journal-tail each turn (the recap discipline exists to keep this flat). Living-world ticks ≈ 1 short session/campaign/day. |
| Living world off | Zero background spend; purely reactive. |

## 9. Troubleshooting

| Symptom | Likely cause → fix |
|---|---|
| Bot silent in DM | Gateway not running → `hermes gateway install`, check `hermes gateway status`/logs. |
| Bot ignores group messages | BotFather group privacy still ON → `/setprivacy` → Disable, then remove/re-add bot to the group. |
| Bot ignores one specific player | That player isn't paired → have them DM the bot and approve the pairing code (§2). |
| Slash commands missing from Telegram menu | `/setcommands` not set (menu is cosmetic — `/new-game` works regardless). |
| "GM forgot what happened" | It narrated without reading files (or state write failed). Check `games/<slug>/state.json` parses: `python3 -m json.tool games/<slug>/state.json`. The journal is the recovery source — ask the GM `ooc:` to rebuild state from the journal. |
| No images, no error | No FAL_KEY (by design). Check the instance's `.env` (`$HERMES_HOME/.env`); test the script directly from the workspace: `cd $HERMES_HOME/workspace && bash scripts/fal_image.sh "a lighthouse at dusk" /tmp/test.png landscape_4_3 fast`. |
| Art fails with "FAL_KEY not set" though the key IS in .env | Wrong instance's script ran — usually a stale skills copy under the MAIN `~/.hermes/skills/` on machines using the profile pattern. Skills call `scripts/fal_image.sh` relative to the workspace precisely to avoid this; delete stale Paracosm skill folders from any Hermes home that shouldn't have them, `git pull && ./install.sh` on the right one. |
| fal script errors | Run the direct test above; the JSON error names the failure (auth, model id, timeout). Check fal.ai dashboard for credit/quota. |
| Cron ticks never fire | Gateway daemon not running (CLI sessions don't tick), or job missing → `hermes cron list`, `hermes cron tick`. |
| World-tick messages have a "Cronjob Response" header | Set `cron.wrap_response: false` (§5). |
| Dice look fake / no roll shown | Dice visibility set to hidden at Session Zero (`ooc: show dice` to flip), or python3 missing on the box. |
| GM sounds generic, ignores the turn contract, mentions a different agent name/persona | `terminal.cwd` isn't set (§5) — AGENTS.md never loaded, and/or an old `HERMES_HOME/SOUL.md` from before an install.sh version fix is stale. Fix: confirm `terminal.cwd` points at the workspace path `install.sh` printed, `cat $HERMES_HOME/SOUL.md` and confirm it's Paracosm's (re-run `./install.sh` if not — it now installs SOUL.md directly to `$HERMES_HOME`, not a subdirectory), then restart the gateway. |
| Bot narrates a DIFFERENT campaign's scene (cross-campaign bleed) | This chat's entry in `games/.active.json` is missing/wrong, or you're on pre-v2 skills. `cat games/.active.json`, fix or `/saves load <name>` to re-anchor, and make sure you've pulled + reinstalled v2 (which forbids mid-game template copying and re-anchors after connection drops). |
| Same scene posted twice | Gateway resend after a stream stall — cosmetic, Hermes platform behavior. Play on. |
| Tool cards / "⚠️ file verifier" text in the fiction | `display.tool_progress: off` and `display.file_mutation_verifier: false` not set (§5); restart the gateway after adding. |
