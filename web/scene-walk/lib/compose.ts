import type { WalkManifest } from "./manifest";

/**
 * Compose the single prose string LingBot World 2 sees, from the manifest's layers.
 *
 * Order matters and mirrors the reference "world contract" recipe:
 *   identity → camera → environment → movement (static | moving) → held actions → invariants
 * The model only ever sees the flattened string, so each layer must stand on its own.
 */
export interface ComposeState {
  moving: boolean;
  heldActions: number[]; // indexes into manifest.actions, in press order
}

const MAX_PROMPT_CHARS = 2000;

export function composePrompt(m: WalkManifest, s: ComposeState): string {
  const parts: string[] = [
    m.contract.identity,
    m.contract.camera,
    m.contract.environment,
    s.moving ? m.moving_prompt : m.static_prompt,
  ];
  for (const i of s.heldActions) {
    const a = m.actions[i];
    if (a) parts.push(a.prompt);
  }
  parts.push(m.contract.invariants);
  const text = parts
    .map((p) => p.trim().replace(/\s+/g, " "))
    .filter(Boolean)
    .map((p) => (/[.!?]$/.test(p) ? p : p + "."))
    .join(" ");
  return text.length > MAX_PROMPT_CHARS ? text.slice(0, MAX_PROMPT_CHARS) : text;
}
