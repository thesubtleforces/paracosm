"""A02 - Size-matched baseline statistics: the manuscript against meaningful text, a Voynich-mimicking
cipher, and meaningless generators.

Every corpus is cut into windows of the same number of word tokens, so that statistics which
depend on sample size (type/token ratio, entropies) are comparable.

Usage:  python -I src/a02_baselines.py [sources_root] [--window 10000]
Writes: results/tables/baselines.csv, results/tables/baselines_small_window.csv,
        results/tables/alphabet_sensitivity.csv
"""
from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pandas as pd  # noqa: E402

import corpora  # noqa: E402
import ivtff  # noqa: E402
import stats  # noqa: E402

OUT = corpora.PROJECT / "results" / "tables"


def run(root: Path, window: int) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(20261119)
    rows = []

    cs = [corpora.voynich(s) for s in ("all", "A", "B", "hand1", "hand2", "hand3")]
    cs += [c for c in corpora.controls(root) if c.kind != "human_gibberish"]
    for c in cs:
        ws = stats.windows(c.tokens, window)
        if not ws:
            continue
        m = stats.mean_dict([stats.window_metrics(w, rng) for w in ws])
        rows.append({"corpus": c.name, "kind": c.kind, **m})
        print(f"{c.name[:52]:52s} h2={m['h2_char']:.2f} len={m['mean_word_len']:.2f} ttr={m['ttr']:.3f} "
              f"rep={m['repeat_exact']*100:.2f}% (shuf {m['repeat_exact_shuffled']*100:.2f}%) "
              f"near={m['repeat_near']*100:.2f}% (shuf {m['repeat_near_shuffled']*100:.2f}%) "
              f"MI+={m['adjacent_mi_excess']:.2f} lenAC={m['len_autocorr']:+.3f}")
    pd.DataFrame(rows).to_csv(OUT / "baselines.csv", index=False)

    # ---- small windows, so the short human-gibberish samples can sit on the same scale
    small = 200
    rows = []
    human = [c for c in corpora.controls(root) if c.kind == "human_gibberish" and len(c) >= small]
    for c in human:
        m = stats.window_metrics(c.tokens[:small], rng)
        rows.append({"corpus": c.name, "kind": c.kind, **m})
    for c in cs:
        toks = c.tokens
        k = min(40, len(toks) // small)
        step = max(small, len(toks) // k)
        ms = [stats.window_metrics(toks[i:i + small], rng, n_shuffles=3)
              for i in range(0, step * k, step) if len(toks[i:i + small]) == small]
        rows.append({"corpus": c.name, "kind": c.kind, **stats.mean_dict(ms)})
    pd.DataFrame(rows).to_csv(OUT / "baselines_small_window.csv", index=False)

    # ---- how much does the low character entropy depend on the transliteration alphabet?
    rows = []
    tdir = corpora.PROJECT / "data" / "transliterations"
    for label, fname in [("EVA (ZL 3b)", "ZL3b-n.txt"), ("EVA (Takahashi IT 2a)", "IT2a-n.txt"),
                         ("v101 (Claston GC 2a)", "GC2a-n.txt"), ("Currier (CD 2a, partial)", "CD2a-n.txt")]:
        _, t = ivtff.to_frames(*ivtff.parse(tdir / fname))
        toks = list(t[(t.generic == "P") & t.clean].token)
        for w_i, w in enumerate(stats.windows(toks, window, 3)):
            h1, h2 = stats.char_entropies(w)
            rows.append({"transliteration": label, "window": w_i, "h1_char": h1, "h2_char": h2,
                         "alphabet": len(set("".join(w))), "mean_word_len": sum(map(len, w)) / len(w)})
    # EVA with multi-stroke glyphs merged into single symbols (a conservative "glyph-level" reading)
    merges = [("cth", "T"), ("ckh", "K"), ("cph", "P"), ("cfh", "F"), ("ch", "C"), ("sh", "S"),
              ("iin", "M"), ("in", "N"), ("ee", "E")]
    eva = corpora.voynich("all").tokens

    def merge(w: str) -> str:
        for a, b in merges:
            w = w.replace(a, b)
        return w

    for w_i, w in enumerate(stats.windows([merge(x) for x in eva], window, 3)):
        h1, h2 = stats.char_entropies(w)
        rows.append({"transliteration": "EVA, strokes merged into glyphs", "window": w_i, "h1_char": h1,
                     "h2_char": h2, "alphabet": len(set("".join(w))), "mean_word_len": sum(map(len, w)) / len(w)})
    a = pd.DataFrame(rows)
    a.to_csv(OUT / "alphabet_sensitivity.csv", index=False)
    print("\nalphabet sensitivity (mean over windows):")
    print(a.groupby("transliteration")[["h1_char", "h2_char", "alphabet", "mean_word_len"]].mean().round(3).to_string())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=str(corpora.default_root()))
    ap.add_argument("--window", type=int, default=10000)
    a = ap.parse_args()
    run(Path(a.root), a.window)
