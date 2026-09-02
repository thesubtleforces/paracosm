/**
 * The walk manifest — written by the scene-walk skill on the Paracosm box, signed by
 * `walk_link.py`, carried in the URL fragment, verified by the token route.
 *
 * This module is pure (no Node/browser-only APIs) so both sides can use it.
 */

export interface WalkContract {
  identity: string;
  camera: string;
  environment: string;
  invariants: string;
}

export interface WalkAction {
  label: string;
  prompt: string;
}

export interface WalkManifest {
  slug: string;
  turn: number;
  seed_image_url: string;
  contract: WalkContract;
  static_prompt: string;
  moving_prompt: string;
  actions: WalkAction[];
  cap_seconds: number;
  max_sessions: number;
  rating?: string;
  iat?: number;
  exp: number;
}

export interface SignedWalk {
  payload: string; // base64url(JSON manifest) — the exact bytes that were signed
  sig: string; // base64url(HMAC-SHA256(secret, payload))
  manifest: WalkManifest;
}

export function b64uToBytes(s: string): Uint8Array {
  const pad = "=".repeat((4 - (s.length % 4)) % 4);
  const b64 = (s + pad).replace(/-/g, "+").replace(/_/g, "/");
  const bin = typeof atob === "function" ? atob(b64) : Buffer.from(b64, "base64").toString("binary");
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

export function decodePayload(payload: string): WalkManifest {
  const json = new TextDecoder().decode(b64uToBytes(payload));
  const m = JSON.parse(json) as WalkManifest;
  validateManifest(m);
  return m;
}

/** Parse `#<payload>.<sig>` from a location hash. Throws on malformed input. */
export function parseFragment(hash: string): SignedWalk {
  const frag = hash.startsWith("#") ? hash.slice(1) : hash;
  const dot = frag.lastIndexOf(".");
  if (dot <= 0 || dot === frag.length - 1) throw new Error("This link is incomplete.");
  const payload = frag.slice(0, dot);
  const sig = frag.slice(dot + 1);
  if (!/^[A-Za-z0-9_-]+$/.test(payload) || !/^[A-Za-z0-9_-]+$/.test(sig)) {
    throw new Error("This link is malformed.");
  }
  return { payload, sig, manifest: decodePayload(payload) };
}

export function validateManifest(m: WalkManifest): void {
  const need = (cond: unknown, msg: string) => {
    if (!cond) throw new Error(`Invalid walk: ${msg}`);
  };
  need(typeof m.slug === "string" && m.slug.length > 0, "slug");
  need(Number.isInteger(m.turn), "turn");
  need(typeof m.seed_image_url === "string" && m.seed_image_url.startsWith("https://"), "seed image");
  need(m.contract && ["identity", "camera", "environment", "invariants"].every((k) => typeof (m.contract as never)[k] === "string"), "contract");
  need(typeof m.static_prompt === "string" && typeof m.moving_prompt === "string", "prompts");
  need(Array.isArray(m.actions) && m.actions.length >= 1 && m.actions.length <= 4, "actions");
  need(m.actions.every((a) => typeof a.label === "string" && typeof a.prompt === "string"), "action shape");
  need(Number.isInteger(m.cap_seconds) && m.cap_seconds >= 30 && m.cap_seconds <= 180, "cap_seconds");
  need(Number.isInteger(m.max_sessions) && m.max_sessions >= 1 && m.max_sessions <= 6, "max_sessions");
  need(Number.isInteger(m.exp), "exp");
}

export function isExpired(m: WalkManifest, nowSeconds = Date.now() / 1000): boolean {
  return m.exp < nowSeconds;
}
