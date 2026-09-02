# Reactor × Paracosm — integration research (2026-09-01)

Scope: what [reactor-team](https://github.com/reactor-team) actually ships, what Paracosm
actually needs, and the realistic pathways between the two — ranked by fit, effort, and
risk. Sources are listed at the end. Note: `reactor.inc`, `docs.reactor.inc` and
`api.reactor.inc` were unreachable from the research sandbox (egress-blocked), so pricing
comes from search snippets of the docs — verify against `GET https://api.reactor.inc/pricing`
(public, no auth) before budgeting. Command names and payloads, however, were taken
from the published packages themselves (`reactor-sdk` 1.2.0 wheel, `@reactor-models/*`
typings), which is why the HappyOyster caveat below is stated with confidence.

---

## 1. What Reactor is (and isn't)

**Reactor is not an open-world game engine or a rules simulator.** It is *"the developer
platform for world models"*: a hosted inference network that streams **real-time
generative video** over WebRTC (sub-50 ms claimed), where a client sends **commands mid-
stream** (change the prompt, move the camera, press an action key) and the model keeps
rendering. Think "a video that you can steer," not "a world with entities, physics and
state you can query."

That framing matters for Paracosm: Reactor can make the *pictures* move and respond, but
it cannot own the *fiction* — HP, inventory, faction clocks, secrets. Those stay in the
campaign folder. Every pathway below treats Reactor as a **renderer** fed by the campaign
files, never as a source of truth.

### The pieces

| Repo | What it is | Relevance |
|---|---|---|
| `reactor-client-sdks` | JS (`@reactor-team/js-sdk`), **Python (`reactor-sdk`, pip, zero deps, Linux aarch64 wheels)**, C++17. Connect to a named model, receive video/audio tracks, `send_command()`, `download_clip()` / `download_recording()` → **MP4**. | The Python SDK is the integration surface for Paracosm (bash/python scripts on a Pi/VPS). |
| `reactor-runtime` | Python framework: subclass `ReactorModel`, write `load()`/`run()`, declare `@event` commands; `reactor build/run/deploy` ships it to Reactor's GPU cloud. | Only needed if we host our own world model (Pathway F). |
| `reactor-cookbook` | `examples/api-models-examples` — one reference Next.js app per hosted model. `examples/world-model-arcade` — seven "games" layered on LingBot World 2 (the closest thing to a game on the platform). `models/` — 15 self-hostable world-model workspaces. | Templates for a web viewer; the arcade's prompt-contract technique is directly reusable. |
| `skills` | Agent-Skills-format `SKILL.md` files: `helios-prompts`, `lingbot-world-2-prompts`, `lingbot-world`, `sana-streaming-prompts`, `reactor-sdk`. Installable via `npx skills add reactor-team/reactor-skills`. | **Same SKILL.md format Hermes uses** — vendorable straight into `hermes/skills/`. |
| `infinite-livestream` | Chat `!prompt` → LLM prompt expansion → FastH3 on Reactor Runtime → paced **RTMP** broadcast (Twitch/YouTube). | The reference architecture for a "live table stream" (Pathway E). |
| `open-dreamer` | Minecraft action-conditioned world model (JAX). | Curiosity only. |
| `reactor-webrtc`, `reactor-queue`, `homebrew-tools`, `semantic` | Infra plumbing. | Not relevant. |

### Hosted model catalog (what you can call today, no GPU of your own)

| Model | Inputs | What it does | Paracosm fit |
|---|---|---|---|
| **HappyOyster** (Alibaba) — `reactor/happy-oyster-adventure` / `reactor/happy-oyster-director` | Text prompt + optional image (landscape 1.5–2.0, ≤2 MB); Adventure: WASD + arrow look + world-advertised verbs; Director: text `instruct()`, pause/rewind, up to ~3 min | Build a world, then *travel* it like a game or *direct* it like a film; persistent worlds you can re-attach to. | **Browser-only.** The typed package (`@reactor-models/happy-oyster`) shows the Reactor session only carries a `status_video` state frame; the actual world video streams from Alibaba's gateway via `aliyun-rtc-sdk` using travel credentials. So it **cannot be recorded server-side** through the Reactor SDK — no use for cutscene clips. Viable only for a browser walk (Pathway D). |
| **LingBot World 2** (Ant Group) — `reactor/lingbot-world-2` | Seed image + layered prose prompt; `set_move_longitudinal/lateral`, `set_camera_pose`, hold-keys **1–9 fire "event" clauses**, jump/crouch/roll | Navigable world from a still; hour-long stability claimed. Prompt is composed from `base + camera + movement + heldEvents + vertical` layers. | Style-lock friendly (seed = our fal keyframe). The **1–9 event slots rhyme with Paracosm's numbered choice block.** Self-hostable (CC BY-NC-SA). |
| **LingBot (v1)** | Seed image + WASD; dynamic overlays (rain, fog) | Simpler navigable world. | Cheaper cousin of the above. |
| **Helios** (Peking U.) — `reactor/helios` | `set_conditioning {prompt, image}` (uploaded keyframe), `start`, hot-swap `set_prompt` / `schedule_prompt {chunk, prompt}`, `set_image_strength`, snapshots + `rewind`; video on `main_video` | Infinite continuous video, 14B DiT, ~19.5 fps on one H100; "base state + one new action" prompt continuation. | **The cutscene backend.** Keyframe-anchored, steerable by beats, recordable with `download_clip()` from Python. Cheapest per second of the bunch. |
| **LongLive 2** | Text only (no image input); `set_shot` / `schedule_*` / `start`; **shots** (soft, spend a 48-chunk ≈ 58 s budget) vs **cuts** (hard, reset budget) | Multi-shot "director's storyboard" video. | `/chronicle` recap reel; title sequences. Weak on style lock (no seed image). |
| **LTX2** | Face image + script + audio | Lip-synced talking-head avatar. | NPC "video letters" — a raven with a face. Niche. |
| **SANA-Streaming**, **X2** | Source video + edit instruction (+ reference image) | Real-time video-to-video *editing* (restyle, swap, remove). | Restyle any clip into the campaign's style bible; low priority. |

### Pricing (from docs snippets — verify)

Per-second while a session is connected; 10,000 credits = $1.
- Helios ≈ 17 credits/s ≈ **$6/hour**
- LingBot World 2 ≈ 33 credits/s ≈ **$12/hour**
- HappyOyster: not captured; assume the same order of magnitude.

So a 30-second clip is a few cents plus session spin-up, but an *idle connected session*
bleeds money. Every script must have a hard wall-clock cap and a guaranteed
`disconnect()`.

### Auth & ops facts that shape the design

- API key `rk_...` from the dashboard. Python: pass the key directly. Browser: mint a JWT
  server-side (`POST https://api.reactor.inc/tokens`), 6-hour expiry, scoped to a model.
- Python SDK needs Python 3.10+ and glibc 2.34+ (Ubuntu 22.04, Debian 12 / Pi OS
  Bookworm 64-bit all qualify). Zero runtime deps — fits the Pi story.
- Connection lifecycle `disconnected → connecting → waiting → ready`; commands only in
  `ready`; `send_command()` awaits a real reply.
- Output is a WebRTC track. **Telegram cannot render WebRTC.** Bridges are: (a) record →
  MP4 → `MEDIA:` tag; (b) a web page the player taps; (c) RTMP into a Telegram
  group/channel live stream (Telegram supports RTMP ingest natively).

---

## 2. What Paracosm actually needs (constraints that filter the pathways)

From `AGENTS.md`, the skills, and the July design review:

1. **Delivery is Telegram via the Hermes gateway.** Media = `MEDIA:<absolute local path>`
   (png/mp4). No inline players, no WebRTC.
2. **Media never blocks a turn.** Narration + choice block first; art is a chaser. Turn
   latency is already 20–35 s; anything added must be async.
3. **Style lock is sacred.** Every image starts with `style.md`'s prefix; recurring
   subjects use locked descriptors. Any video path that can't take a seed image weakens
   this.
4. **Rating/safety bind media prompts** exactly like narration.
5. **Three video beats per campaign** (title / midpoint / ending), tracked in
   `story_position.cutscenes_used`. Video is deliberately rationed.
6. **"No app, no server code of its own"** is a stated design value. Pathways that add a
   web page or daemon are a real ethos change, not just work.
7. **Concurrency scars.** The July review's worst failures were cross-campaign bleed.
   Any Reactor session, world id, or stream must be keyed by campaign slug and stored in
   that campaign's `state.json`, never in session memory or a shared file.
8. **Budget posture:** fal FLUX schnell turn art costs pennies; Reactor is $6–12/hour
   connected. Reactor belongs in the *rationed* tier, not the per-turn tier.

---

## 3. Pathways, ranked

### A. Reactor as a second cutscene backend — *implemented* (`hermes/skills/cutscene/scripts/reactor_clip.py`)

**What:** The cutscene skill already builds a style-locked keyframe (fal quality tier,
returns a local PNG and a fal.media URL) and then calls Kling image-to-video. Add a
`scripts/reactor_clip.py` that: connects to **Helios** (`reactor/helios`), uploads the
keyframe with `upload_file`, sends `set_conditioning {prompt, image}`, `start`, lets it
run for N seconds sending 1–3 `set_prompt` beats composed as "base prompt + beat", calls
`download_clip(N)`, writes the MP4, disconnects. (HappyOyster was the first candidate
but its video never touches the Reactor session — see the catalog note — so it is out.) The skill picks the backend via config
(`paracosm.video_backend: fal | reactor`) with a degrade chain **reactor → fal →
keyframe still**.

**Why it fits:** Zero change to the turn contract, delivery, or ethos (it's one more
script under `scripts/`). Same three-beat budget. The seed image preserves the style
bible. Gains over Kling: longer clips (director mode runs minutes, not 5–10 s), narrative
steering mid-clip ("now the gate opens"), pause/rewind for retakes, and audio.

**Verified wire contract** (read from the published `@reactor-models/helios` typings and
the `reactor-sdk` 1.2.0 wheel, not from docs): `Reactor(model, api_key=…,
max_session_duration_seconds=…)` → `connect()` → `upload_file(path) -> FileRef` →
`send_command("set_conditioning", {"prompt", "image": FileRef})` → `send_command("start",
{})` → messages `generation_started` / `chunk_complete` / `command_error` via
`on_message` → `send_command("set_prompt", {"prompt"})` per beat → `download_clip(N,
path)` (fragmented MP4; `ffmpeg -c copy -movflags +faststart` for a seekable file) →
`disconnect()`. Token minting is `POST /tokens` with header `Reactor-API-Key`, body
`{expires_after, authorization_details:[{type:"session", resources:{models:{match:[…]}},
constraints:{max_sessions, max_session_duration_seconds}}]}`, response `{jwt}`.

**Effort:** a weekend. **Risk:** low. **Cost:** cents per beat.

### B. `/chronicle` recap reel via LongLive 2

**What:** The chronicle already distills the journal into chapters. Map chapters →
LongLive 2 **cuts** (new scene) and beats within a chapter → **shots** (soft transitions),
respecting the 48-chunk (~58 s) budget per scene. Output one MP4 "the story so far" reel
delivered with the chronicle cover.

**Why it fits:** Chronicle is already an end-of-campaign ceremony where spending a
minute of GPU is fine. Storyboard = `set_shot` list compiled from `chronicle.md`.

**Caveat:** LongLive 2 is text-only — no seed image — so the style bible is enforced only
through prose. Acceptable for a keepsake; not for turn art.

**Effort:** small once A exists. **Risk:** low.

### C. Vendor Reactor's prompt skills as Paracosm references

**What:** `reactor-team/skills` is in the same Agent Skills `SKILL.md` format Hermes
reads. Copy `helios-prompts` and `lingbot-world-2-prompts` (trimmed) into
`hermes/skills/cutscene/references/` so the GM writes prompts the models actually parse
(the LingBot guide's rules — no imperative camera verbs, six anchors, ≤512 tokens,
"describe position not motion" — are the kind of thing the GM will otherwise violate
every time).

**Mapping campaign files → LingBot World 2 prompt layers** (this is the reusable idea
even if the live-world pathway never ships):

| LingBot layer | Paracosm source |
|---|---|
| `base` (subject identity, environment, style) | `style.md` prefix + `state.json.location` + the `world.md` section for that region + `art.character_descriptors[pc]` |
| `camera.static / dynamic` | fixed per campaign from `style.md` composition rules |
| `movement.static / dynamic` | idle vs travelling; derived from the current verb |
| `events[1..9]` (hold-keys) | **the numbered choice block** — each option becomes an event clause |
| seed image | the turn's fal keyframe |
| moderation / content constraints | `meta.rating` + Session Zero safety lines |

**Effort:** hours. **Risk:** none. Prerequisite for D and E.

### D. "Walk the scene" — an explorable link (spectacle, not mechanics) — *implemented* (`web/scene-walk/`, `hermes/skills/scene-walk/`)

**What:** On a big set piece, the GM offers *"step into the scene"*: a URL to a tiny web
page (start from `npx create-reactor-app --model=lingbot-world-2` or the
`world-model-arcade` recipe) that mints a JWT scoped to the model and runs a 60–90 s
session seeded with the turn's keyframe and the composed prompt. The player explores
with WASD/touch; the page hard-stops at the cap. Could be wrapped as a Telegram Mini
App.

**What it does *not* do:** feed anything back into the game. Nothing the player "finds"
while walking exists in `state.json`. It is a toy the GM hands over, like a map
handout. Making exploration mechanically meaningful (Pathway F territory) is a
different project.

**Costs:** ~$12/hour → a 90-second walk ≈ $0.30 per player per use; group chats
multiply that. Needs a token-minting endpoint (Vercel/Cloudflare free tier is enough)
— this is the first pathway that breaks "no server code."

**Effort:** 1–2 weeks incl. hosting. **Risk:** medium (cost control, drift, ethos).

### E. Party-mode live table stream (the infinite-livestream pattern)

**What:** A per-campaign daemon holds one HappyOyster-director or Helios session,
watches a `games/<slug>/scene-prompt.txt` the GM rewrites each turn (composed per C),
sends `instruct()` / `set_prompt` on change, pipes the video track through ffmpeg into
the Telegram group's **RTMP live stream**. The table watches a continuous cinematic of
the scene while playing in text. This is exactly `infinite-livestream` with Telegram
chat as the prompt source and Telegram RTMP as the sink.

**Blockers to name honestly:**
- Getting the RTMP URL/key programmatically requires an MTProto *user* client
  (`phone.getGroupCallStreamRtmpUrl`), not the Bot API. Simpler: a human starts the
  stream and pastes the key once per session.
- $6–12 per table-hour, continuously.
- Coherence drift over long sessions (the arcade recipe explicitly "re-anchors a world
  when it drifts"); the daemon must periodically re-seed from a fresh fal keyframe.
- A second long-running process per campaign — new failure modes for the exact
  concurrency class the July review flagged.

**Effort:** weeks. **Risk:** high. **Payoff:** the most striking demo of anything here.

### F. Self-host / bring-your-own world model on Reactor Runtime (research track)

**What:** The cookbook's `models/` workspaces (`lingbot-world-v2`, `hy-world-1-5`,
`matrix-game-3-5`, …) are deployable with `reactor build && reactor deploy`. A custom
`ReactorModel` adapter could accept a `scene_json` command built directly from the
campaign files, run the arcade-style prompt contracts server-side, and eventually
expose model messages (e.g. "player reached the gate") back to the GM.

**Reality check:** needs a B200-class GPU (rented through Reactor), the interesting
models are CC BY-NC-SA (fine for a personal-use project), and the "exploration feeds the
fiction" loop is unsolved research — world models emit pixels, not facts. Park this
until A–C are live and D has taught us whether players even want to walk around.

---

## 4. Recommended sequence

| Phase | Deliverable | Gate |
|---|---|---|
| 0 | Reactor account + `rk_` key in `~/.hermes/.env`; `pip install reactor-sdk` on the box; run the SDK's `01_connect_and_receive.py`; hit `/pricing` and record real numbers here. | Key works from the Pi/VPS. |
| 1 | Pathway **A**: `scripts/reactor_clip.py`, cutscene skill v1.2 with `paracosm.video_backend`, degrade chain, absolute-path `MEDIA:` delivery, hard time cap. | Three beats of a test campaign render via Reactor; fal fallback verified by pulling the key. |
| 2 | Pathway **C**: vendored prompt references; GM prompt quality checked with `scene_report.py`-style validation. | Prompts pass the LingBot/Helios red-flag lists. |
| 3 | Pathway **B**: chronicle reel. | One campaign's `/chronicle` ships an MP4. |
| 4 | Pathway **D** prototype behind an opt-in `ooc:` flag, with a per-campaign spend cap in `state.json`. | Decide from playtest whether exploration earns its cost. |
| 5 | Pathway **E** as a one-night party experiment, human-started RTMP. | Only if D showed real appetite. |

## 5. Things that could bite

- **Per-second billing on open sessions.** Every script: `asyncio.wait_for` + `finally:
  disconnect()`. Journal the seconds used so a runaway is visible.
- **Telegram limits.** Bot API uploads cap at 50 MB; keep clips ≤ 60 s at 480p, and
  transcode with ffmpeg if `download_clip()` returns something larger.
- **Style drift.** Prefer models that accept a seed image (HappyOyster, LingBot, Helios,
  HY-World) for anything that must match campaign art; LongLive 2 only for keepsakes.
- **Rating enforcement.** Reactor `InputField` moderation exists at the runtime level for
  self-hosted models; for hosted ones our prompt composer is the only gate — reuse the
  same rating language as narration.
- **Identity discipline.** Store `reactor.world_id`, `reactor.session_seconds_used` under
  the campaign's `state.json`; never a global registry (see July review A1–A4).
- **Sandbox blind spots.** Exact hosted-model command payloads were read from cookbook
  reference apps, not the API reference; confirm against `docs.reactor.inc/model-api-reference`
  before writing the script.

---

## Sources

- Org: https://github.com/reactor-team · Client SDKs (JS/Python/C++): https://github.com/reactor-team/reactor-client-sdks · Python SDK README: https://github.com/reactor-team/reactor-client-sdks/tree/main/sdks/python
- Runtime: https://github.com/reactor-team/reactor-runtime · Deprecated js-sdk: https://github.com/reactor-team/js-sdk
- Cookbook: https://github.com/reactor-team/reactor-cookbook — `examples/api-models-examples` (Helios, LingBot, LingBot World 2, LongLive 2, LTX2, SANA, X2, HappyOyster), `examples/world-model-arcade`, `models/` (lingbot-world-v2, hy-world-1-5, matrix-game-3-5, …)
- Skills: https://github.com/reactor-team/skills (`helios-prompts`, `lingbot-world`, `lingbot-world-2-prompts`, `sana-streaming-prompts`, `reactor-sdk`)
- Infinite livestream: https://github.com/reactor-team/infinite-livestream · Open Dreamer: https://github.com/reactor-team/open-dreamer
- Funding / positioning: https://lsvp.com/stories/the-developer-platform-for-world-models-our-series-a-in-reactor/ · https://press.aboutamazon.com/aws/2026/5/reactor-emerges-from-stealth-with-59m-to-build-the-platform-for-real-time-ai-worlds
- Helios paper: https://arxiv.org/abs/2603.04379 · LingBot-World 2: https://github.com/robbyant/lingbot-world-v2 · HappyOyster 1.0: https://gigazine.net/gsc_news/en/20260618-happyoyster-real-time-world-model/
- Pricing (docs snippet, unverified from sandbox): https://docs.reactor.inc/resources/billing · public endpoint `GET https://api.reactor.inc/pricing`
- Telegram RTMP: https://core.telegram.org/method/phone.getGroupCallStreamRtmpUrl
