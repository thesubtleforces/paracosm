# Paracosm — scene-walk web app

The one hosted piece of Paracosm. The Game Master (running on your box) generates a
style-locked keyframe, writes a small *walk manifest*, signs it, and drops a link in the
chat. Opening the link runs a real-time, navigable world model (LingBot World 2 on
[Reactor](https://github.com/reactor-team)) seeded with that keyframe for a capped
minute or so. WASD/arrows on desktop; on-screen pad on phones; 1–4 fire the scene's
actions.

**Nothing here talks back to the game.** A walk is spectacle; the campaign files on
your box remain the only truth.

## Security model in one paragraph

The Reactor API key lives only on this server. A walk link carries
`#<payload>.<sig>` where `sig` is an HMAC-SHA256 over `payload` using a secret shared
between your Paracosm box and this app. The page posts both to `/api/reactor/token`;
the server verifies the signature and expiry, then mints a Reactor token **downscoped**
to the walk model, capped at the manifest's `max_sessions`, with every session
force-terminated after `cap_seconds + 120`. A copied link without a valid signature
gets nothing. `/api/seed` fetches the seed image the same way (signed request only,
allow-listed hosts only) so the page never needs the image host to send CORS headers.

## Deploy (Vercel, free tier)

1. Import this repository in Vercel; set **Root Directory** to `web/scene-walk`.
2. Environment variables (Production):
   - `REACTOR_API_KEY` — your `rk_…` key from the Reactor dashboard
   - `WALK_SIGNING_SECRET` — a long random string (e.g. `openssl rand -hex 32`)
   - `NEXT_PUBLIC_BOT_USERNAME` — your bot's Telegram username, without `@` (baked in
     at build time, like every `NEXT_PUBLIC_*` variable — redeploy after changing it)
   - optional `SEED_IMAGE_HOSTS` — extra comma-separated image hosts (default `fal.media`)
3. Deploy. Note the URL, e.g. `https://paracosm-walk.vercel.app`.
4. On the Paracosm box, add to `~/.hermes/.env` (or the profile's `.env`):
   ```
   PARACOSM_WALK_URL=https://paracosm-walk.vercel.app
   WALK_SIGNING_SECRET=<the same secret>
   ```
   Then re-run `./install.sh` (it reports "Scene walks: configured").

Cloudflare Pages works too (Next.js via `@cloudflare/next-on-pages`); the routes use
the Node runtime, so keep the default adapter settings that support it.

## Local development

```bash
cp .env.example .env.local   # fill in the values
pnpm install
pnpm dev                     # http://localhost:3000
```

Make a test link from any manifest (see `hermes/skills/scene-walk/SKILL.md` for the
schema):

```bash
PARACOSM_WALK_URL=http://localhost:3000 WALK_SIGNING_SECRET=<same secret> \
  python3 ../../hermes/skills/scene-walk/scripts/walk_link.py manifest.json
```

Open the printed URL. Without a real `REACTOR_API_KEY` the page reaches "the fog
closes" with the token route's error — that is the expected failure path.

## Costs

Reactor bills per connected second (LingBot World 2 ≈ $12/hour at the time of
writing — check `GET https://api.reactor.inc/pricing`). A 90-second walk is therefore
about $0.30 per opener; a party of four sharing one link is four sessions. The Game
Master charges every walk against the campaign's `meta.walk_budget_seconds`, and the
minted token cannot outlive `max_sessions` × (`cap_seconds` + 120 s) on the server side
either. Set a spend limit in the Reactor dashboard as the final backstop.

## Files

| Path | Role |
|---|---|
| `app/walk/page.tsx` | parses `#payload.sig`, shows expiry/malformed errors, mounts the experience client-side only |
| `components/WalkExperience.tsx` | connect → seed image → prompt → start; input → commands; countdown → disconnect |
| `lib/compose.ts` | flattens the manifest's layers (identity/camera/environment/movement/actions/invariants) into the single prompt the model sees |
| `lib/manifest.ts` | manifest schema, fragment parsing, validation (pure; shared by page and server) |
| `lib/verify.ts` | server-only HMAC verification, identical to `walk_link.py` |
| `app/api/reactor/token/route.ts` | signed request → downscoped Reactor JWT |
| `app/api/seed/route.ts` | signed request → seed image bytes (allow-listed hosts) |
