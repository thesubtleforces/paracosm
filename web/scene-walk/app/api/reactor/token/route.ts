import { NextResponse } from "next/server";
import { verifySigned, WalkAuthError } from "@/lib/verify";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const REACTOR_API_URL = process.env.REACTOR_API_URL ?? "https://api.reactor.inc";
const MODEL = "reactor/lingbot-world-2";
const TOKEN_TTL_SECONDS = 30 * 60;
/** Grace beyond the walk cap for connect + seed upload before the server kills it. */
const SESSION_GRACE_SECONDS = 120;

/**
 * Mint a Reactor session token for one signed walk.
 *
 * The API key never leaves the server. The token is downscoped to the walk model,
 * capped at the manifest's `max_sessions`, and every session it creates is
 * force-terminated server-side after `cap_seconds + grace`. Without a valid HMAC
 * signature from the Paracosm box nothing is minted — a copied link is not a GPU
 * faucet.
 */
export async function POST(req: Request) {
  const noStore = { "Cache-Control": "private, no-store" };
  let body: { payload?: unknown; sig?: unknown };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Bad request." }, { status: 400, headers: noStore });
  }

  let manifest;
  try {
    manifest = verifySigned(body.payload, body.sig);
  } catch (e) {
    const status = e instanceof WalkAuthError ? e.status : 401;
    const message = e instanceof Error ? e.message : "Not authorized.";
    return NextResponse.json({ error: message }, { status, headers: noStore });
  }

  const apiKey = process.env.REACTOR_API_KEY;
  if (!apiKey) {
    return NextResponse.json({ error: "Server is not configured." }, { status: 500, headers: noStore });
  }

  const upstream = await fetch(`${REACTOR_API_URL.replace(/\/$/, "")}/tokens`, {
    method: "POST",
    headers: { "Reactor-API-Key": apiKey, "Content-Type": "application/json" },
    body: JSON.stringify({
      expires_after: TOKEN_TTL_SECONDS,
      authorization_details: [
        {
          type: "session",
          resources: { models: { match: [MODEL] } },
          constraints: {
            max_sessions: manifest.max_sessions,
            max_session_duration_seconds: manifest.cap_seconds + SESSION_GRACE_SECONDS,
          },
        },
      ],
    }),
    cache: "no-store",
  }).catch(() => null);

  if (!upstream) {
    return NextResponse.json({ error: "The projector is unreachable." }, { status: 502, headers: noStore });
  }
  const data = (await upstream.json().catch(() => ({}))) as { jwt?: string; expires_at?: number };
  if (!upstream.ok || typeof data.jwt !== "string") {
    return NextResponse.json({ error: "The projector refused." }, { status: 502, headers: noStore });
  }
  const expires_at =
    typeof data.expires_at === "number" ? data.expires_at : Math.floor(Date.now() / 1000) + TOKEN_TTL_SECONDS;
  return NextResponse.json({ jwt: data.jwt, expires_at, model: MODEL }, { headers: noStore });
}
