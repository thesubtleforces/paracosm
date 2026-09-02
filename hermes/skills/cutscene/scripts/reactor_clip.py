#!/usr/bin/env python3
"""reactor_clip.py — record a short, narratively steered video clip from a Reactor
world model (Helios by default) and save it locally as MP4.

Usage:
  reactor_clip.py "<scene prompt>" <keyframe.png> <out.mp4> [--seconds N]
                  [--beat "<instruction>"]... [--model reactor/helios]
                  [--image-strength 0.0-1.0] [--probe]

  scene prompt   style prefix first, then one paragraph: subject, setting, framing,
                 lighting (<= 2000 chars). This is the base state the clip opens on.
  keyframe.png   the style-locked still from scene-art (quality tier). It anchors the
                 first frame so the clip matches campaign art.
  out.mp4        where to write the clip (parent dirs are created).
  --seconds      clip length in seconds (default 30, clamped to 10..150).
  --beat         a short instruction sent mid-clip ("the gate grinds open"). Up to 3;
                 they are spaced evenly across the clip. Each is composed as
                 "<scene prompt>. <beat>" so the base state persists.
  --model        Reactor model name (default reactor/helios).
  --probe        connect, print tracks + every message for ~15s, exit 0. For setup.

Env:
  REACTOR_API_KEY   required — or found in the nearest .env walking up from this
                    script (the Hermes home's .env), same as the fal scripts.
  REACTOR_VIDEO_MODEL   overrides --model default.

Output (stdout), mirroring fal_video.sh so the cutscene skill's degrade chain is
uniform:
  success: {"file": "<abs path>", "seconds": N, "model": "...", "session_id": "..."}
  failure: {"error": "..."} on stderr and exit 1 — callers fall back to fal_video.sh,
           then to the keyframe still. Never surface the error in the fiction.

Cost note: Reactor bills per connected second. This script hard-caps the session both
client-side (asyncio timeout) and server-side (max_session_duration_seconds) and always
disconnects in a `finally`.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Wire contract for reactor/helios (from @reactor-models/helios v1.0.1 typings).
# If you point --model at a different Reactor model, adjust these.
# ---------------------------------------------------------------------------
CMD_SET_CONDITIONING = "set_conditioning"   # {"prompt": str, "image": FileRef}
CMD_SET_PROMPT = "set_prompt"               # {"prompt": str}  hot-swap, next chunk
CMD_SET_IMAGE_STRENGTH = "set_image_strength"  # {"image_strength": 0..1}
CMD_START = "start"                         # {}
CMD_PAUSE = "pause"                         # {}
MSG_STARTED = "generation_started"
MSG_CHUNK = "chunk_complete"
MSG_ERROR = "command_error"
VIDEO_TRACK = "main_video"

DEFAULT_MODEL = os.environ.get("REACTOR_VIDEO_MODEL", "reactor/helios")
MIN_SECONDS, MAX_SECONDS = 10, 150
SETUP_GRACE = 150          # seconds allowed for connect + conditioning + first chunk
DOWNLOAD_GRACE = 120       # seconds allowed for the clip manifest + download


def fail(msg: str) -> None:
    sys.stderr.write(json.dumps({"error": msg}) + "\n")
    sys.exit(1)


def find_api_key() -> str | None:
    """REACTOR_API_KEY from env, else the nearest .env walking up from this script.

    Mirrors fal_image.sh: the Hermes gateway may not export custom .env vars to
    terminal subprocesses, and the script may live under $HERMES_HOME/skills/... or
    $HERMES_HOME/workspace/scripts/, so walk upward until a .env appears.
    """
    key = os.environ.get("REACTOR_API_KEY", "").strip()
    if key:
        return key
    d = Path(__file__).resolve().parent
    for _ in range(5):
        env = d / ".env"
        if env.is_file():
            for line in env.read_text(errors="ignore").splitlines():
                if line.startswith("REACTOR_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
            if key:
                return key
        if d.parent == d:
            break
        d = d.parent
    return None


def remux_faststart(path: Path) -> None:
    """download_clip yields fragmented MP4. Telegram plays it, but a faststart moov
    gives a proper duration bar and seeking. Best effort; skipped without ffmpeg."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return
    tmp = path.with_suffix(".faststart.mp4")
    try:
        subprocess.run(
            [ffmpeg, "-y", "-loglevel", "error", "-i", str(path), "-c", "copy",
             "-movflags", "+faststart", str(tmp)],
            check=True, timeout=120,
        )
        if tmp.is_file() and tmp.stat().st_size > 0:
            tmp.replace(path)
    except Exception:
        tmp.unlink(missing_ok=True)


async def probe(model: str, api_key: str) -> None:
    from reactor_sdk import Reactor

    async with Reactor(model, api_key=api_key, max_session_duration_seconds=60) as r:
        r.on_message(lambda m: print("message:", json.dumps(m)[:400]))
        r.on_error(lambda e: print("error:", e))
        r.on_status(lambda s: print("status:", s.value))
        await r.connect()
        print("session:", r.session_id)
        for t in r.tracks:
            print("track:", t.name, t.kind, t.direction)
        await asyncio.sleep(15)


async def record(args: argparse.Namespace, api_key: str) -> dict:
    from reactor_sdk import Reactor

    seconds = max(MIN_SECONDS, min(MAX_SECONDS, args.seconds))
    beats = [b.strip() for b in (args.beat or []) if b.strip()][:3]
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    started = asyncio.Event()
    chunks = 0
    last_error: str | None = None

    def on_message(msg: dict) -> None:
        nonlocal chunks, last_error
        t = msg.get("type") if isinstance(msg, dict) else None
        if t == MSG_STARTED:
            started.set()
        elif t == MSG_CHUNK:
            chunks += 1
        elif t == MSG_ERROR:
            last_error = f"{msg.get('command')}: {msg.get('reason')}"

    hard_cap = seconds + SETUP_GRACE + DOWNLOAD_GRACE
    r = Reactor(args.model, api_key=api_key, max_session_duration_seconds=hard_cap)
    r.on_message(on_message)
    try:
        await r.connect()
        image = await r.upload_file(str(Path(args.keyframe).resolve()))
        reply = await r.send_command(CMD_SET_CONDITIONING, {"prompt": args.prompt, "image": image})
        if last_error:
            raise RuntimeError(last_error)
        if args.image_strength is not None:
            await r.send_command(CMD_SET_IMAGE_STRENGTH, {"image_strength": args.image_strength})
        await r.send_command(CMD_START, {})
        if last_error:
            raise RuntimeError(last_error)
        try:
            await asyncio.wait_for(started.wait(), timeout=SETUP_GRACE)
        except asyncio.TimeoutError:
            raise RuntimeError("generation did not start in time")

        # Beats are spaced evenly across the clip; each keeps the base state so the
        # scene doesn't reset, per Helios's "base state + one new action" guidance.
        t0 = time.monotonic()
        schedule = [(seconds * (i + 1) / (len(beats) + 1), b) for i, b in enumerate(beats)]
        for at, beat in schedule:
            delay = at - (time.monotonic() - t0)
            if delay > 0:
                await asyncio.sleep(delay)
            await r.send_command(CMD_SET_PROMPT, {"prompt": f"{args.prompt} {beat}".strip()})
        remaining = seconds - (time.monotonic() - t0)
        if remaining > 0:
            await asyncio.sleep(remaining)
        # A little extra so the last chunk containing the clip window closes; the
        # media clock lags wall clock when the model runs below real time.
        await asyncio.sleep(3)
        if chunks == 0:
            raise RuntimeError("no video chunks were produced")

        await r.send_command(CMD_PAUSE, {})
        await r.download_clip(seconds, str(out), ready_timeout=DOWNLOAD_GRACE)
        session_id = r.session_id
    finally:
        try:
            await r.disconnect()
        except Exception:
            pass

    if not out.is_file() or out.stat().st_size == 0:
        raise RuntimeError("downloaded clip is empty")
    remux_faststart(out)
    return {"file": str(out), "seconds": seconds, "model": args.model, "session_id": session_id}


def main() -> None:
    p = argparse.ArgumentParser(add_help=True)
    p.add_argument("prompt", nargs="?")
    p.add_argument("keyframe", nargs="?")
    p.add_argument("out", nargs="?")
    p.add_argument("--seconds", type=int, default=30)
    p.add_argument("--beat", action="append")
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--image-strength", type=float, default=None)
    p.add_argument("--probe", action="store_true")
    args = p.parse_args()

    api_key = find_api_key()
    if not api_key:
        fail("REACTOR_API_KEY not set (env or $HERMES_HOME/.env)")
    try:
        import reactor_sdk  # noqa: F401
    except Exception as e:  # ImportError or a native-lib load failure
        fail(f"reactor-sdk not importable: {e} (pip install reactor-sdk)")

    if args.probe:
        try:
            asyncio.run(asyncio.wait_for(probe(args.model, api_key), timeout=90))
        except Exception as e:
            fail(f"probe failed: {e}")
        return

    if not (args.prompt and args.keyframe and args.out):
        fail("usage: reactor_clip.py <prompt> <keyframe.png> <out.mp4> [--seconds N] [--beat ...]")
    if len(args.prompt) > 2000:
        fail("prompt exceeds 2000 characters")
    if not Path(args.keyframe).is_file():
        fail(f"keyframe not found: {args.keyframe}")

    total_cap = max(MIN_SECONDS, min(MAX_SECONDS, args.seconds)) + SETUP_GRACE + DOWNLOAD_GRACE
    try:
        result = asyncio.run(asyncio.wait_for(record(args, api_key), timeout=total_cap))
    except asyncio.TimeoutError:
        fail("timed out waiting for the clip")
    except Exception as e:
        fail(str(e) or e.__class__.__name__)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
