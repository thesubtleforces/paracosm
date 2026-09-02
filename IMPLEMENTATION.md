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

During `hermes setup`, choose your **model provider**. The GM is only as good as the brain,
and this is the single biggest quality dial you own. From live A/B testing (8 models,
same test script, July 2026):

- **`x-ai/grok-4.5`** — recommended default: fast turns, honest visible dice, playful
  "yes, and" improvisation, obeys the game's procedural rules, mid-tier price.
- **`openai/gpt-5.6`** — the prose champion; a touch slower and pricier. Lovely for
  one-shots where atmosphere is the point.
- **`z-ai/glm-5.2`** — budget pick: ~90% of the experience at a fraction of the cost;
  occasionally narrates its own file work.
- Avoid dialogue-only models (no tool calling — the GM can't roll dice or save state)
  and small/fast tiers (slow, handholding prose).

Note: the in-chat `/model <slug>` switch is **session-only** — set your pick with
`--global` (or via `hermes model`) so `/new` doesn't silently revert it.

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

## 3b. Reactor (optional: cinematic cutscenes)

[Reactor](https://reactor.inc) hosts real-time *world models* — video you can steer while
it generates. With a key, the three cutscene beats per campaign become 20–45 s clips
that open on the campaign's own keyframe and follow one or two narrative beats the GM
writes ("the gate grinds open…"), instead of a 5–10 s Kling loop. Without a key nothing
changes: cutscenes use fal.ai exactly as before.

1. Create an account, mint an API key (`rk_…`) in the Reactor dashboard, and **set a
   spend limit there** — Reactor bills per connected second.
2. Add `REACTOR_API_KEY=rk_...` to `~/.hermes/.env`.
3. Install the SDK for the `python3` the gateway's terminal uses:
   `python3 -m pip install reactor-sdk` (Python ≥ 3.10; Linux needs glibc ≥ 2.34 —
   Raspberry Pi OS Bookworm 64-bit, Ubuntu 22.04+, Debian 12 all qualify).
4. Optional: `apt install ffmpeg` so clips carry a seekable duration bar in Telegram.
5. Re-run `./install.sh` — it reports the key, the SDK import, and ffmpeg.
6. Smoke test from the workspace: `python3 scripts/reactor_clip.py --probe` should
   print a session id and a `main_video` track, then exit.

Optional override: `REACTOR_VIDEO_MODEL` (default `reactor/helios`). Costs: see §8.
The cutscene skill always tries Reactor → fal → keyframe still, so a missing SDK or a
dead key just means the fal clip arrives instead.

## 3c. Scene walks (optional: a web app)

A walk is a link the GM drops on big moments: a real-time, navigable world seeded with
the turn's keyframe that the player explores for a capped minute or so. It is the one
hosted component in Paracosm — a small Next.js app in `web/scene-walk/` that keeps the
Reactor key server-side and only serves links the GM has signed.

1. Deploy `web/scene-walk` (Vercel free tier; see its README) with
   `REACTOR_API_KEY`, a fresh `WALK_SIGNING_SECRET` (`openssl rand -hex 32`), and
   `NEXT_PUBLIC_BOT_USERNAME`.
2. On the box, add to `~/.hermes/.env`:
   ```
   PARACOSM_WALK_URL=https://<your-deployment>
   WALK_SIGNING_SECRET=<the same secret>
   ```
3. Re-run `./install.sh` — "Scene walks: configured".

Walks are spectacle: **nothing seen on a walk changes the game.** Each campaign has a
`meta.walk_budget_seconds` (default 600) the GM charges against; in party mode one link
serves the table and every opener is a separate session. Skip this section entirely
and walks are simply never offered.

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
group_sessions_per_user: false   # REQUIRED for group play — one shared table per chat (see below)
cron:
  wrap_response: false   # world-tick messages arrive in the GM's voice, no cron header
skills:
  write_approval: true   # any agent-authored skill change waits for your review
stt:
  enabled: true          # voice-message actions at the table (needs faster-whisper — below)
display:
  tool_progress: off            # hide terminal/read/write tool cards — pure fiction in chat
  file_mutation_verifier: false # keep the file-verifier footer out of the narration
```

**`group_sessions_per_user: false` is not optional if you play in groups.** Hermes's
default keys group sessions per *sender*: every player gets their own GM brain, and one
user's sessions can span multiple group chats. In live play this produced both failure
modes — party desync (a player's message answered without the table's context) and
**cross-campaign interference between concurrently running games** (one user's session
carrying another chat's fiction mid-message). `false` gives each group chat one shared
session: the whole table talks to one GM, and different chats get different sessions.
DMs are unaffected (always keyed per chat). The trade-off the Hermes docs note — group
members share context and interrupt state — is exactly what a game table wants.

**Voice at the table:** install the local transcriber so spoken actions work —
`uv pip install faster-whisper` in the Hermes venv (or `pip install faster-whisper`) —
plus the `stt.enabled: true` above. Without it, voice messages bounce with a setup
lecture in the middle of the fiction.

**No approval prompts mid-fiction:** the GM's terminal use (dice, fal scripts, campaign
file ops) triggers exec-approval prompts (`✅ Approved once by …`) inside the story
unless pre-approved. Use your Hermes version's approval allowlist to pre-approve the
game's command shapes (`python3 -c …`, `bash scripts/fal_*.sh …`, `cp -r
templates/campaign …`, file ops under `games/`) — or set this profile's approval mode to
auto-accept, which is reasonable given its deliberately minimal toolset.

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
7. **Concurrency drill (N-chat)** — run at least THREE campaigns at once: two group
   chats + one DM, three different worlds. Interleave turns across all three, including
   sending from two chats at effectively the same moment. Expect zero bleed anywhere:
   each chat stays locked to its own campaign, narration never references another
   table's fiction, and `ls games/.active/` shows one marker file per chat (group ids
   negative, DM id positive) each containing the right slug. Then, in ONE chat, say
   "ooc: clear this chat and start over" — expect only that chat's marker removed; the
   other two campaigns keep playing untouched and every campaign folder still exists.
   The marker-file registry has no shared state to contend on, so this scales to any
   number of chats — rerun the drill with more whenever a new group joins.
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
16. **Reactor cutscene** (if §3b) — the title card after Scene 1 arrives as an inline
    video of ~20 s that clearly opens on the keyframe; `story_position.cutscenes_used.
    title` is true and `art.reactor.clips.title` holds a session id. Then rename
    `REACTOR_API_KEY` in `.env` and start another campaign: the Kling clip arrives
    instead, with no error text in chat. Remove `FAL_KEY` too: the keyframe still
    arrives. Restore both.
17. **Scene walk** (if §3c) — on a set piece, the GM offers a link. Open it on a phone
    from Telegram: video within ~10 s, the pad walks, an action button plays its beat,
    the countdown ends on a "the story waits" screen. Open the same link again past
    `max_sessions`: a polite refusal, not a session. `state.json →
    art.reactor.walk_seconds_used` advanced by `cap_seconds × max_sessions`. Rerun
    the concurrency drill (step 7) with a walk and a Reactor cutscene in two campaigns
    at once — every id lands in the right `state.json`.

## 8. Costs & tuning

| Lever | Effect |
|---|---|
| Per-turn art (default: most turns, fast tier) | Turn art runs on `FAL_IMAGE_MODEL_FAST` (flux/schnell ≈ fractions of a cent, 2–4s) — art-most-turns costs a few cents per session. Key moments (title, act breaks, chronicle cover) use the quality tier (flux/dev ≈ a few cents each). `ooc: fewer pictures` is the brake, stored per campaign. |
| Video (fal) | 3 cutscenes/campaign hard cap ≈ tens of cents to ~$1 each depending on model. Skip by declining video when offered. |
| Video (Reactor) | Per connected second (Helios ≈ $6/hour at time of writing — verify at `GET https://api.reactor.inc/pricing`). A 30 s clip plus setup is a few cents; the risk is an *open* session, which is why `reactor_clip.py` caps every session both client- and server-side. |
| Walks | LingBot World 2 ≈ $12/hour → a 90 s walk ≈ $0.30 per opener; a party of four is four sessions. Governed by `meta.walk_budget_seconds` (default 600 s per campaign) and the token's `max_sessions`. Set a dashboard spend limit as the backstop. |
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
| Bot narrates a DIFFERENT campaign's scene (cross-campaign bleed) | Two causes, check both: (1) `group_sessions_per_user` not set to `false` (§5) — one user's session spans multiple groups and carries fiction between them; (2) this chat's marker `games/.active/<chat_id>` missing/wrong — `ls games/.active/`, fix with `/saves load <name>`. Ensure you're on the marker-file registry (post-2026-07-18 build); the old shared `.active.json` could be clobbered cross-chat. |
| Two concurrent games broke each other | Same as above — the session-keying config is the root cause; the marker-file registry + chat-id-from-metadata rules are the containment. Run the §7 concurrency drill after fixing config to verify. |
| "Clear this chat" deleted campaigns from ANOTHER chat | Pre-2026-07-18 skills. Update: clears now only remove the requesting chat's marker; deletion requires per-campaign confirmation and chat ownership. Restore lost campaigns from `/saves export` zips or ask the GM to reconstruct from the session ledger (it can). |
| Voice messages bounce with "no speech-to-text provider" | faster-whisper not installed in this instance's venv or `stt.enabled` not set for the profile (§5) — each Hermes home/profile configures STT separately. |
| `/saves load <name>` returns nothing at all | Known pre-2026-07-18 bug on fuzzy-miss; updated skill always replies with the shelf. If it persists, check gateway logs for a crashed turn. |
| Same scene posted twice | Gateway resend after a stream stall — cosmetic, Hermes platform behavior. Play on. |
| Tool cards / "⚠️ file verifier" text in the fiction | `display.tool_progress: off` and `display.file_mutation_verifier: false` not set (§5); restart the gateway after adding. |
| Cutscenes still come from fal though `REACTOR_API_KEY` is set | Run `python3 scripts/reactor_clip.py --probe` from the workspace; the JSON error says why: `reactor-sdk not importable` → install it for *that* `python3` (§3b); `could not exchange the API key` → key/spend limit; old glibc (< 2.34) → the SDK wheel won't load on that box, stay on fal. |
| Reactor clip plays but shows no duration / can't seek | Fragmented MP4 without ffmpeg on the box. `apt install ffmpeg`; the script remuxes automatically when it finds it. |
| Reactor clip errors with `command_error` | The model rejected a prompt or image (rating filter, > 2000 chars, non-image keyframe). The skill falls back to fal; check the journal note for the reason. |
| Walk link says "This link is not valid" | `WALK_SIGNING_SECRET` differs between the box's `.env` and the web app's env. They must be byte-identical. |
| Walk link says "This walk has expired" | Links live 30 minutes from signing. Ask the GM for a fresh one (it re-signs the same manifest). |
| Walk opens but "the fog closes" immediately | The token route failed: `REACTOR_API_KEY` missing on the web host, Reactor spend limit hit, or `max_sessions` already spent for that link. Check the deployment logs. |
| Walk shows the curtain but no video ever forms | WebRTC blocked by the in-app browser or a corporate network. Open the link in Safari/Chrome; if it still fails, the Reactor status page is the next stop. |
