import "server-only";
import { createHmac, timingSafeEqual } from "node:crypto";
import { decodePayload, isExpired, type WalkManifest } from "./manifest";

/**
 * Verify a signed walk exactly the way `walk_link.py` produced it:
 * HMAC-SHA256 over the base64url payload *string*, base64url-encoded, no padding.
 * Throws with a user-safe message on any failure.
 */
export function verifySigned(payload: unknown, sig: unknown): WalkManifest {
  const secret = process.env.WALK_SIGNING_SECRET;
  if (!secret) throw new WalkAuthError("Server is not configured.", 500);
  if (typeof payload !== "string" || typeof sig !== "string") {
    throw new WalkAuthError("This link is malformed.");
  }
  if (!/^[A-Za-z0-9_-]+$/.test(payload) || !/^[A-Za-z0-9_-]+$/.test(sig)) {
    throw new WalkAuthError("This link is malformed.");
  }
  const expected = createHmac("sha256", secret).update(payload).digest("base64url");
  const a = Buffer.from(expected);
  const b = Buffer.from(sig);
  if (a.length !== b.length || !timingSafeEqual(a, b)) {
    throw new WalkAuthError("This link is not valid.");
  }
  let manifest: WalkManifest;
  try {
    manifest = decodePayload(payload);
  } catch {
    throw new WalkAuthError("This link is not valid.");
  }
  if (isExpired(manifest)) throw new WalkAuthError("This walk has expired.");
  return manifest;
}

export class WalkAuthError extends Error {
  readonly status: number;
  constructor(message: string, status = 401) {
    super(message);
    this.status = status;
  }
}
