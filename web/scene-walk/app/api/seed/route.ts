import { NextResponse } from "next/server";
import { verifySigned, WalkAuthError } from "@/lib/verify";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const MAX_BYTES = 10 * 1024 * 1024;
const DEFAULT_HOSTS = ["fal.media"];

function hostAllowed(url: URL): boolean {
  const extra = (process.env.SEED_IMAGE_HOSTS ?? "")
    .split(",")
    .map((h) => h.trim().toLowerCase())
    .filter(Boolean);
  const allowed = [...DEFAULT_HOSTS, ...extra];
  const host = url.hostname.toLowerCase();
  return url.protocol === "https:" && allowed.some((h) => host === h || host.endsWith("." + h));
}

/**
 * Fetch the walk's seed image server-side and hand it to the page as bytes.
 *
 * Exists because the image host may not send CORS headers, and the page must
 * upload the bytes to the Reactor session itself. Only the image named in a
 * validly signed manifest is fetched, and only from allow-listed hosts — this is
 * not an open proxy.
 */
export async function POST(req: Request) {
  let body: { payload?: unknown; sig?: unknown };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Bad request." }, { status: 400 });
  }
  let manifest;
  try {
    manifest = verifySigned(body.payload, body.sig);
  } catch (e) {
    const status = e instanceof WalkAuthError ? e.status : 401;
    return NextResponse.json({ error: e instanceof Error ? e.message : "Not authorized." }, { status });
  }

  let url: URL;
  try {
    url = new URL(manifest.seed_image_url);
  } catch {
    return NextResponse.json({ error: "Bad seed image." }, { status: 400 });
  }
  if (!hostAllowed(url)) {
    return NextResponse.json({ error: "Seed image host not allowed." }, { status: 403 });
  }

  const upstream = await fetch(url, { cache: "no-store", redirect: "follow" }).catch(() => null);
  if (!upstream || !upstream.ok) {
    return NextResponse.json({ error: "Seed image unavailable." }, { status: 502 });
  }
  const type = upstream.headers.get("content-type") ?? "";
  const len = Number(upstream.headers.get("content-length") ?? "0");
  if (!type.startsWith("image/") || len > MAX_BYTES) {
    return NextResponse.json({ error: "Seed image rejected." }, { status: 502 });
  }
  const bytes = await upstream.arrayBuffer();
  if (bytes.byteLength === 0 || bytes.byteLength > MAX_BYTES) {
    return NextResponse.json({ error: "Seed image rejected." }, { status: 502 });
  }
  return new NextResponse(bytes, {
    headers: { "Content-Type": type, "Cache-Control": "private, no-store" },
  });
}
