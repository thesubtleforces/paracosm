"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";
import { isExpired, parseFragment, type SignedWalk } from "@/lib/manifest";
import { BackLink } from "@/components/BackLink";

// The Reactor SDK is browser-only (WebRTC + wasm); never render it on the server.
const WalkExperience = dynamic(
  () => import("@/components/WalkExperience").then((m) => m.WalkExperience),
  { ssr: false, loading: () => <div className="stage" /> },
);

type Parsed = { ok: true; walk: SignedWalk } | { ok: false; message: string };

export default function WalkPage() {
  const [parsed, setParsed] = useState<Parsed | null>(null);

  useEffect(() => {
    try {
      const walk = parseFragment(window.location.hash);
      if (isExpired(walk.manifest)) {
        setParsed({ ok: false, message: "This walk has expired. Ask the Game Master for a fresh one." });
      } else {
        setParsed({ ok: true, walk });
      }
    } catch (e) {
      setParsed({ ok: false, message: e instanceof Error ? e.message : "This link cannot be opened." });
    }
  }, []);

  if (!parsed) return <div className="stage" />;
  if (!parsed.ok) {
    return (
      <div className="stage">
        <div className="curtain">
          <div>
            <h2>THE FOG CLOSES</h2>
            <p>{parsed.message}</p>
            <BackLink />
          </div>
        </div>
      </div>
    );
  }
  return <WalkExperience walk={parsed.walk} />;
}
