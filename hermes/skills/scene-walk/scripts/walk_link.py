#!/usr/bin/env python3
"""walk_link.py — turn a walk manifest into a signed, expiring URL for the
scene-walk web app.

Usage:
  walk_link.py <manifest.json>            print the signed URL
  walk_link.py --verify "<url>"           print the decoded manifest if the
                                          signature and expiry check out (exit 1 if not)

Env (or the nearest .env walking up from this script — the Hermes home's .env):
  PARACOSM_WALK_URL     base URL of the deployed web app, e.g. https://walk.example.app
  WALK_SIGNING_SECRET   shared secret; the same value is set on the web app

The manifest is a JSON object (see the scene-walk skill for the fields). This script
adds `exp` (now + 30 min) and `iat` if missing, encodes the manifest as base64url,
signs it with HMAC-SHA256, and prints:

  <PARACOSM_WALK_URL>/walk#<payload>.<signature>

The fragment never reaches any server log. The page sends payload+signature to its
own token route, which verifies both before minting a Reactor session token. Without
a valid signature nobody can spend GPU minutes with a copied link.

Output: the URL on stdout on success; {"error": "..."} on stderr and exit 1 otherwise.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import sys
import time
from pathlib import Path

DEFAULT_TTL_SECONDS = 30 * 60
REQUIRED = ("slug", "turn", "seed_image_url", "contract", "static_prompt",
            "moving_prompt", "actions", "cap_seconds", "max_sessions")


def fail(msg: str) -> None:
    sys.stderr.write(json.dumps({"error": msg}) + "\n")
    sys.exit(1)


def env_lookup(name: str) -> str | None:
    val = os.environ.get(name, "").strip()
    if val:
        return val
    d = Path(__file__).resolve().parent
    for _ in range(5):
        env = d / ".env"
        if env.is_file():
            for line in env.read_text(errors="ignore").splitlines():
                if line.startswith(f"{name}="):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
            if val:
                return val
        if d.parent == d:
            break
        d = d.parent
    return None


def b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def b64u_decode(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def sign(payload: str, secret: str) -> str:
    return b64u(hmac.new(secret.encode(), payload.encode(), hashlib.sha256).digest())


def build_url(manifest: dict, base_url: str, secret: str) -> str:
    now = int(time.time())
    manifest.setdefault("iat", now)
    manifest.setdefault("exp", now + DEFAULT_TTL_SECONDS)
    payload = b64u(json.dumps(manifest, separators=(",", ":"), sort_keys=True).encode())
    return f"{base_url.rstrip('/')}/walk#{payload}.{sign(payload, secret)}"


def verify_url(url: str, secret: str) -> dict:
    frag = url.split("#", 1)[1] if "#" in url else ""
    if "." not in frag:
        raise ValueError("no payload.signature fragment")
    payload, sig = frag.rsplit(".", 1)
    if not hmac.compare_digest(sign(payload, secret), sig):
        raise ValueError("bad signature")
    manifest = json.loads(b64u_decode(payload))
    if int(manifest.get("exp", 0)) < time.time():
        raise ValueError("link expired")
    return manifest


def validate(m: dict) -> None:
    missing = [k for k in REQUIRED if k not in m]
    if missing:
        raise ValueError(f"manifest missing: {', '.join(missing)}")
    if not isinstance(m["contract"], dict) or not all(
        k in m["contract"] for k in ("identity", "camera", "environment", "invariants")
    ):
        raise ValueError("contract needs identity, camera, environment, invariants")
    if not (1 <= len(m["actions"]) <= 4):
        raise ValueError("actions must have 1-4 entries")
    for a in m["actions"]:
        if not ("label" in a and "prompt" in a):
            raise ValueError("each action needs label and prompt")
    if not (30 <= int(m["cap_seconds"]) <= 180):
        raise ValueError("cap_seconds must be 30-180")
    if not (1 <= int(m["max_sessions"]) <= 6):
        raise ValueError("max_sessions must be 1-6")
    if not str(m["seed_image_url"]).startswith("https://"):
        raise ValueError("seed_image_url must be https")


def main() -> None:
    argv = sys.argv[1:]
    secret = env_lookup("WALK_SIGNING_SECRET")
    if not secret:
        fail("WALK_SIGNING_SECRET not set (env or $HERMES_HOME/.env)")

    if argv[:1] == ["--verify"]:
        if len(argv) < 2:
            fail("usage: walk_link.py --verify <url>")
        try:
            print(json.dumps(verify_url(argv[1], secret), indent=2))
        except Exception as e:
            fail(str(e))
        return

    if len(argv) != 1:
        fail("usage: walk_link.py <manifest.json> | --verify <url>")
    base_url = env_lookup("PARACOSM_WALK_URL")
    if not base_url:
        fail("PARACOSM_WALK_URL not set (env or $HERMES_HOME/.env)")
    try:
        manifest = json.loads(Path(argv[0]).read_text())
        validate(manifest)
        print(build_url(manifest, base_url, secret))
    except Exception as e:
        fail(str(e))


if __name__ == "__main__":
    main()
