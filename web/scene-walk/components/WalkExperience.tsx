"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  LingbotWorld2MainVideoView,
  LingbotWorld2Provider,
  useLingbotWorld2,
  useLingbotWorld2CommandError,
} from "@reactor-models/lingbot-world-2/react";
import { composePrompt } from "@/lib/compose";
import type { SignedWalk } from "@/lib/manifest";
import { BackLink } from "./BackLink";

type Long = "idle" | "forward" | "back";
type Lat = "idle" | "strafe_left" | "strafe_right";
type LookH = "idle" | "left" | "right";
type LookV = "idle" | "up" | "down";
type Phase = "connecting" | "seeding" | "live" | "ended" | "error";

const ACTION_HOLD_MS = 1500;
const PROMPT_DEBOUNCE_MS = 120;

/* ------------------------------------------------------------------ token --- */

const tokenCache = new Map<string, { jwt: string; expires_at: number }>();
/** The token route's own words, kept so the curtain can show them instead of the
 *  SDK's "http transport error: jwt resolver rejected: …" wrapper. */
let lastTokenError: string | null = null;

async function mintToken(payload: string, sig: string): Promise<string> {
  const cached = tokenCache.get(payload);
  if (cached && cached.expires_at - Date.now() / 1000 > 60) return cached.jwt;
  const res = await fetch("/api/reactor/token", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ payload, sig }),
  });
  const data = (await res.json().catch(() => ({}))) as { jwt?: string; expires_at?: number; error?: string };
  if (!res.ok || !data.jwt) {
    lastTokenError = data.error ?? "The projector refused.";
    throw new Error(lastTokenError);
  }
  lastTokenError = null;
  tokenCache.set(payload, { jwt: data.jwt, expires_at: data.expires_at ?? Date.now() / 1000 + 1500 });
  return data.jwt;
}

function humanError(e: unknown, fallback: string): string {
  if (lastTokenError) return lastTokenError;
  if (!(e instanceof Error) || !e.message) return fallback;
  // Keep only the innermost clause of a nested "a: b: c" SDK message.
  const parts = e.message.split(": ");
  return parts[parts.length - 1] || fallback;
}

/* --------------------------------------------------------------- component --- */

export function WalkExperience({ walk }: { walk: SignedWalk }) {
  const fetchToken = useCallback(() => mintToken(walk.payload, walk.sig), [walk.payload, walk.sig]);
  return (
    <LingbotWorld2Provider jwtToken={fetchToken}>
      <Stage walk={walk} />
    </LingbotWorld2Provider>
  );
}

function Stage({ walk }: { walk: SignedWalk }) {
  const { manifest } = walk;
  const lw2 = useLingbotWorld2();
  const [phase, setPhase] = useState<Phase>("connecting");
  const [message, setMessage] = useState<string | null>(null);
  const [remaining, setRemaining] = useState(manifest.cap_seconds);
  const [held, setHeld] = useState<number[]>([]);
  const [moving, setMoving] = useState(false);

  const phaseRef = useRef<Phase>("connecting");
  const bootedRef = useRef(false);
  const seededRef = useRef(false);
  const longRef = useRef<Long>("idle");
  const latRef = useRef<Lat>("idle");
  const lookHRef = useRef<LookH>("idle");
  const lookVRef = useRef<LookV>("idle");
  const heldRef = useRef<number[]>([]);
  const holdTimers = useRef<Map<number, number>>(new Map());
  const promptTimer = useRef<number | null>(null);
  const lw2Ref = useRef(lw2);
  lw2Ref.current = lw2;

  const setPhaseBoth = (p: Phase) => {
    phaseRef.current = p;
    setPhase(p);
  };

  useLingbotWorld2CommandError((m) => setMessage(m.reason));

  /* prompt recomposition, debounced, only while live */
  const pushPrompt = useCallback(() => {
    if (promptTimer.current) window.clearTimeout(promptTimer.current);
    promptTimer.current = window.setTimeout(() => {
      if (phaseRef.current !== "live") return;
      const isMoving = longRef.current !== "idle" || latRef.current !== "idle";
      const prompt = composePrompt(manifest, { moving: isMoving, heldActions: heldRef.current });
      void lw2Ref.current.setPrompt({ prompt });
    }, PROMPT_DEBOUNCE_MS);
  }, [manifest]);

  /* movement + look senders (stateful: always send the neutral value on release) */
  const setLong = useCallback(
    (v: Long) => {
      if (longRef.current === v) return;
      longRef.current = v;
      if (phaseRef.current === "live") void lw2Ref.current.setMoveLongitudinal({ move_longitudinal: v });
      setMoving(longRef.current !== "idle" || latRef.current !== "idle");
      pushPrompt();
    },
    [pushPrompt],
  );
  const setLat = useCallback(
    (v: Lat) => {
      if (latRef.current === v) return;
      latRef.current = v;
      if (phaseRef.current === "live") void lw2Ref.current.setMoveLateral({ move_lateral: v });
      setMoving(longRef.current !== "idle" || latRef.current !== "idle");
      pushPrompt();
    },
    [pushPrompt],
  );
  const setLookH = useCallback((v: LookH) => {
    if (lookHRef.current === v) return;
    lookHRef.current = v;
    if (phaseRef.current === "live") void lw2Ref.current.setLookHorizontal({ look_horizontal: v });
  }, []);
  const setLookV = useCallback((v: LookV) => {
    if (lookVRef.current === v) return;
    lookVRef.current = v;
    if (phaseRef.current === "live") void lw2Ref.current.setLookVertical({ look_vertical: v });
  }, []);

  const releaseAction = useCallback(
    (i: number) => {
      const t = holdTimers.current.get(i);
      if (t) window.clearTimeout(t);
      holdTimers.current.delete(i);
      if (!heldRef.current.includes(i)) return;
      heldRef.current = heldRef.current.filter((x) => x !== i);
      setHeld([...heldRef.current]);
      pushPrompt();
    },
    [pushPrompt],
  );
  /** Actions are held state that auto-releases: a tap plays the whole beat. */
  const pressAction = useCallback(
    (i: number) => {
      if (!manifest.actions[i] || phaseRef.current !== "live") return;
      if (!heldRef.current.includes(i)) {
        heldRef.current = [...heldRef.current, i];
        setHeld([...heldRef.current]);
        pushPrompt();
      }
      const prev = holdTimers.current.get(i);
      if (prev) window.clearTimeout(prev);
      holdTimers.current.set(i, window.setTimeout(() => releaseAction(i), ACTION_HOLD_MS));
    },
    [manifest.actions, pushPrompt, releaseAction],
  );

  const releaseAll = useCallback(() => {
    setLong("idle");
    setLat("idle");
    setLookH("idle");
    setLookV("idle");
    for (const i of [...heldRef.current]) releaseAction(i);
  }, [setLong, setLat, setLookH, setLookV, releaseAction]);

  const end = useCallback(async () => {
    if (phaseRef.current === "ended") return;
    releaseAll();
    setPhaseBoth("ended");
    try {
      await lw2Ref.current.disconnect();
    } catch {
      /* already gone */
    }
  }, [releaseAll]);

  /* boot: connect once (StrictMode-safe) */
  useEffect(() => {
    if (bootedRef.current) return;
    bootedRef.current = true;
    lw2Ref.current.connect().catch((e: unknown) => {
      setMessage(humanError(e, "Could not reach the projector."));
      setPhaseBoth("error");
    });
  }, []);

  /* when ready: seed image → prompt → start */
  useEffect(() => {
    if (lw2.status !== "ready" || seededRef.current) return;
    seededRef.current = true;
    setPhaseBoth("seeding");
    (async () => {
      try {
        const res = await fetch("/api/seed", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ payload: walk.payload, sig: walk.sig }),
        });
        if (!res.ok) throw new Error("The scene's picture would not load.");
        const blob = await res.blob();
        const image = await lw2Ref.current.uploadFile(blob, { name: "seed.png" });
        await lw2Ref.current.setImage({ image });
        await lw2Ref.current.setPrompt({ prompt: composePrompt(manifest, { moving: false, heldActions: [] }) });
        await lw2Ref.current.start();
        setPhaseBoth("live");
      } catch (e) {
        setMessage(humanError(e, "The scene would not form."));
        setPhaseBoth("error");
        try {
          await lw2Ref.current.disconnect();
        } catch {
          /* ignore */
        }
      }
    })();
  }, [lw2.status, manifest, walk.payload, walk.sig]);

  /* countdown */
  useEffect(() => {
    if (phase !== "live") return;
    const startedAt = Date.now();
    const id = window.setInterval(() => {
      const left = Math.max(0, manifest.cap_seconds - Math.floor((Date.now() - startedAt) / 1000));
      setRemaining(left);
      if (left === 0) void end();
    }, 500);
    return () => window.clearInterval(id);
  }, [phase, manifest.cap_seconds, end]);

  /* keyboard: WASD move, arrows look, 1-4 actions */
  useEffect(() => {
    const isTyping = (t: EventTarget | null) =>
      t instanceof HTMLElement && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable);
    const down = (e: KeyboardEvent) => {
      if (e.repeat || isTyping(e.target)) return;
      switch (e.key) {
        case "w": case "W": setLong("forward"); break;
        case "s": case "S": setLong("back"); break;
        case "a": case "A": setLat("strafe_left"); break;
        case "d": case "D": setLat("strafe_right"); break;
        case "ArrowLeft": setLookH("left"); break;
        case "ArrowRight": setLookH("right"); break;
        case "ArrowUp": setLookV("up"); break;
        case "ArrowDown": setLookV("down"); break;
        case "1": case "2": case "3": case "4": pressAction(Number(e.key) - 1); break;
        default: return;
      }
      e.preventDefault();
    };
    const up = (e: KeyboardEvent) => {
      switch (e.key) {
        case "w": case "W": if (longRef.current === "forward") setLong("idle"); break;
        case "s": case "S": if (longRef.current === "back") setLong("idle"); break;
        case "a": case "A": if (latRef.current === "strafe_left") setLat("idle"); break;
        case "d": case "D": if (latRef.current === "strafe_right") setLat("idle"); break;
        case "ArrowLeft": case "ArrowRight": setLookH("idle"); break;
        case "ArrowUp": case "ArrowDown": setLookV("idle"); break;
        default: return;
      }
      e.preventDefault();
    };
    window.addEventListener("keydown", down);
    window.addEventListener("keyup", up);
    window.addEventListener("blur", releaseAll);
    return () => {
      window.removeEventListener("keydown", down);
      window.removeEventListener("keyup", up);
      window.removeEventListener("blur", releaseAll);
    };
  }, [setLong, setLat, setLookH, setLookV, pressAction, releaseAll]);

  /* leave = disconnect: never leave a session running */
  useEffect(() => {
    const bye = () => void end();
    window.addEventListener("pagehide", bye);
    return () => {
      window.removeEventListener("pagehide", bye);
      void end();
    };
  }, [end]);

  const mmss = useMemo(() => {
    const m = Math.floor(remaining / 60);
    const s = remaining % 60;
    return `${m}:${s.toString().padStart(2, "0")}`;
  }, [remaining]);

  const hold = (on: () => void, off: () => void) => ({
    onPointerDown: (e: React.PointerEvent) => {
      e.preventDefault();
      (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
      on();
    },
    onPointerUp: off,
    onPointerCancel: off,
    onPointerLeave: off,
  });

  return (
    <div className="stage">
      <LingbotWorld2MainVideoView className="video" videoObjectFit="cover" muted />

      <div className="hud">
        <div className="topbar">
          <span className="pill">
            {phase === "connecting" && "finding the projector…"}
            {phase === "seeding" && "the scene is forming…"}
            {phase === "live" && (remaining <= 10 ? <b>{mmss}</b> : mmss)}
            {phase === "ended" && "the reel has ended"}
            {phase === "error" && "the fog closes"}
          </span>
          {message && phase === "live" ? <span className="pill warn">{message}</span> : null}
          {phase === "live" ? (
            <button className="pill" onClick={() => void end()}>
              leave
            </button>
          ) : null}
        </div>

        {phase === "live" ? (
          <div>
            <div className="actions">
              {manifest.actions.map((a, i) => (
                <button
                  key={i}
                  className={`action${held.includes(i) ? " held" : ""}`}
                  onPointerDown={(e) => {
                    e.preventDefault();
                    pressAction(i);
                  }}
                >
                  <span className="n">{i + 1}</span>
                  {a.label}
                </button>
              ))}
            </div>
            <div className="controls touch-only">
              <div className="dpad">
                <button className={`key c${longRef.current === "forward" ? " held" : ""}`} {...hold(() => setLong("forward"), () => setLong("idle"))}>▲</button>
                <button className="key l" {...hold(() => setLat("strafe_left"), () => setLat("idle"))}>◀</button>
                <button className="key r" {...hold(() => setLat("strafe_right"), () => setLat("idle"))}>▶</button>
                <button className="key d" {...hold(() => setLong("back"), () => setLong("idle"))}>▼</button>
              </div>
              <div className="look">
                <button className="key" {...hold(() => setLookH("left"), () => setLookH("idle"))}>↶</button>
                <button className="key" {...hold(() => setLookH("right"), () => setLookH("idle"))}>↷</button>
                <button className="key" {...hold(() => setLookV("up"), () => setLookV("idle"))}>⤒</button>
                <button className="key" {...hold(() => setLookV("down"), () => setLookV("idle"))}>⤓</button>
              </div>
            </div>
            <p className="hint">{moving ? "walking" : "WASD to walk · arrows to look · 1–4 to act"}</p>
          </div>
        ) : null}
      </div>

      {phase === "ended" || phase === "error" ? (
        <div className="curtain">
          <div>
            <h2>{phase === "ended" ? "THE STORY WAITS" : "THE FOG CLOSES"}</h2>
            <p>
              {phase === "ended"
                ? "You wandered; the world held its breath. Nothing you saw here changes what happens next — that part is still yours to play."
                : message ?? "The scene would not form. Open this link in Safari or Chrome, or ask the Game Master for another."}
            </p>
            <BackLink />
          </div>
        </div>
      ) : null}
    </div>
  );
}
