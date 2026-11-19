"""A03 - Is the line a unit? Positional structure of words within lines.

Currier (1976) observed that in the manuscript "the line is a functional entity": words at the
start and end of lines differ from words elsewhere. Ordinary prose copied onto a page shows no
such effect, because where a line breaks is an accident of word widths.

For each corpus we measure, against a null in which the words of every line are shuffled:
  first_len / last_len  mean length of the line-first / line-last word minus mean of interior words
  jsd_first             divergence between first-glyph distributions of line-first vs other words
  jsd_last              divergence between last-glyph distributions of line-last vs other words

Controls with imposed line breaks (wrap) are the built-in negative control: they must come out null.

Usage:  python -I src/a03_line_effects.py [sources_root]
Writes: results/tables/line_effects.csv, results/tables/line_edge_glyphs.csv
"""
from __future__ import annotations

import random
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import corpora  # noqa: E402
import stats  # noqa: E402

OUT = corpora.PROJECT / "results" / "tables"
MIN_LINE = 4          # lines need a first, a last and at least two interior words
N_PERM = 300


def measure(lines: list[list[str]]) -> dict:
    first = [ln[0] for ln in lines]
    last = [ln[-1] for ln in lines]
    interior = [w for ln in lines for w in ln[1:-1]]
    not_first = [w for ln in lines for w in ln[1:]]
    not_last = [w for ln in lines for w in ln[:-1]]
    mi = np.mean([len(w) for w in interior])
    return {
        "first_len": float(np.mean([len(w) for w in first]) - mi),
        "last_len": float(np.mean([len(w) for w in last]) - mi),
        "jsd_first": stats.jsd(Counter(w[0] for w in first), Counter(w[0] for w in not_first)),
        "jsd_last": stats.jsd(Counter(w[-1] for w in last), Counter(w[-1] for w in not_last)),
    }


def test(lines: list[list[str]], rng: random.Random, n_perm: int = N_PERM) -> dict:
    lines = [ln for ln in lines if len(ln) >= MIN_LINE]
    obs = measure(lines)
    null = {k: [] for k in obs}
    for _ in range(n_perm):
        sh = []
        for ln in lines:
            ln = list(ln)
            rng.shuffle(ln)
            sh.append(ln)
        for k, v in measure(sh).items():
            null[k].append(v)
    out = {"n_lines": len(lines)}
    for k in obs:
        mu, sd = float(np.mean(null[k])), float(np.std(null[k]))
        out[k] = obs[k]
        out[k + "_null"] = mu
        out[k + "_z"] = (obs[k] - mu) / sd if sd > 0 else float("nan")
    return out


def edge_glyphs(lines: list[list[str]], top: int = 8) -> pd.DataFrame:
    """Glyphs most over-represented at line start (word-initial) and line end (word-final)."""
    lines = [ln for ln in lines if len(ln) >= MIN_LINE]
    rows = []
    for where, pick_edge, pick_rest, glyph in [
        ("line-first word, first glyph", lambda ln: [ln[0]], lambda ln: ln[1:], lambda w: w[0]),
        ("line-last word, last glyph", lambda ln: [ln[-1]], lambda ln: ln[:-1], lambda w: w[-1]),
    ]:
        e = Counter(glyph(w) for ln in lines for w in pick_edge(ln))
        r = Counter(glyph(w) for ln in lines for w in pick_rest(ln))
        ne, nr = sum(e.values()), sum(r.values())
        for g in set(e) | set(r):
            pe, pr = e[g] / ne, r[g] / nr
            if e[g] + r[g] >= 50:
                rows.append({"where": where, "glyph": g, "share_at_edge": pe, "share_elsewhere": pr,
                             "ratio": (pe / pr) if pr > 0 else float("inf"), "n_at_edge": e[g]})
    df = pd.DataFrame(rows).sort_values(["where", "ratio"], ascending=[True, False])
    return df.groupby("where").head(top)


def main(root: Path) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(3)
    cs = [corpora.voynich(s) for s in ("all", "A", "B")]
    cs += [c for c in corpora.controls(root) if c.kind != "human_gibberish" and len(c) >= 10000]
    rows = []
    for c in cs:
        r = test(c.lines, rng)
        rows.append({"corpus": c.name, "kind": c.kind, "native_lines": c.native_lines, **r})
        print(f"{c.name[:50]:50s} first_len {r['first_len']:+.2f} (z {r['first_len_z']:+6.1f})  "
              f"last_len {r['last_len']:+.2f} (z {r['last_len_z']:+6.1f})  "
              f"jsd_first {r['jsd_first']:.4f} (z {r['jsd_first_z']:+6.1f})  "
              f"jsd_last {r['jsd_last']:.4f} (z {r['jsd_last_z']:+6.1f})")
    pd.DataFrame(rows).to_csv(OUT / "line_effects.csv", index=False)

    eg = edge_glyphs(corpora.voynich("all").lines)
    eg.to_csv(OUT / "line_edge_glyphs.csv", index=False)
    print("\nVoynich: glyphs over-represented at line edges")
    print(eg.round(4).to_string(index=False))

    # paragraph-first-line gallows ("Grove words"): share of tokens containing p or f
    _, t = corpora.voynich_frames()
    p = t[(t.generic == "P") & t.clean]
    pf = p.token.str.contains("[pf]")
    print("\nshare of tokens containing 'p' or 'f':")
    print("  first line of paragraph: %.3f   other lines: %.3f" %
          (pf[p.para_first_line].mean(), pf[~p.para_first_line].mean()))
    first_tok = p[(p.para_first_line) & (p.idx == 0)]
    print("  paragraph-initial word begins with p/t/k/f: %.3f   (all words: %.3f)" %
          (first_tok.token.str.match("[ptkf]").mean(), p.token.str.match("[ptkf]").mean()))


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else corpora.default_root())
