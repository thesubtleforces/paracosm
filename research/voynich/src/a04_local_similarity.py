"""A04 - Where do similar words sit? Local repetition in reading order and in vertical alignment.

Two processes predict different geometries of word similarity:

  * Meaningful prose (plain or enciphered word by word): topical words recur, so similarity decays
    smoothly with distance *in reading order*. Where on the page a word sits is irrelevant.
  * Copy-and-modify generation ("self-citation", Timm & Schinner 2019): the scribe adapts words
    already visible on the page, so a word resembles words *physically near it* - in particular
    words in the line directly above, at about the same horizontal position.

Part 1 measures the probability that word i equals / is one edit from word i-d, for d = 1..40,
relative to the same text with words shuffled inside each page (so the page vocabulary is kept).

Part 2 looks at consecutive lines: for a word at position j in a line and a word at position k in
the line above, how does the match probability depend on the offset k-j? The null rotates the
upper line by a random amount, which keeps its words and their order but destroys the alignment.

Usage:  python -I src/a04_local_similarity.py [sources_root]
Writes: results/tables/lag_similarity.csv, results/tables/vertical_alignment.csv
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import corpora  # noqa: E402
import stats  # noqa: E402

OUT = corpora.PROJECT / "results" / "tables"
MAX_LAG = 40
LINES_PER_PSEUDO_PAGE = 30
OFFSETS = range(-6, 7)


def voynich_pages(subset: str = "all") -> list[list[list[str]]]:
    """Paragraph text as pages -> lines -> tokens (clean tokens only)."""
    _, t = corpora.voynich_frames()
    t = t[(t.generic == "P") & t.clean]
    if subset in ("A", "B"):
        t = t[t.language == subset]
    pages = []
    for _, pg in t.groupby("seq", sort=True):
        lines = [list(g.token) for _, g in pg.groupby("line_on_page", sort=True)]
        pages.append([ln for ln in lines if ln])
    return pages


def pseudo_pages(lines: list[list[str]]) -> list[list[list[str]]]:
    return [lines[i:i + LINES_PER_PSEUDO_PAGE] for i in range(0, len(lines), LINES_PER_PSEUDO_PAGE)]


def lag_counts(pages_tokens: list[list[str]], near: dict[str, set[str]]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    exact = np.zeros(MAX_LAG + 1)
    close = np.zeros(MAX_LAG + 1)
    total = np.zeros(MAX_LAG + 1)
    for toks in pages_tokens:
        n = len(toks)
        for d in range(1, min(MAX_LAG, n - 1) + 1):
            total[d] += n - d
            e = c = 0
            for a, b in zip(toks[d:], toks[:-d]):
                if a == b:
                    e += 1
                elif b in near[a]:
                    c += 1
            exact[d] += e
            close[d] += c
    return exact, close, total


def lag_table(name: str, kind: str, pages: list[list[list[str]]], rng: random.Random, n_shuffle: int = 20) -> pd.DataFrame:
    flat = [[w for ln in pg for w in ln] for pg in pages]
    near = stats.neighbor_map(w for pg in flat for w in pg)
    e, c, tot = lag_counts(flat, near)
    se, sc = np.zeros(MAX_LAG + 1), np.zeros(MAX_LAG + 1)
    for _ in range(n_shuffle):
        sh = [stats.shuffled(pg, rng) for pg in flat]
        e2, c2, _ = lag_counts(sh, near)
        se += e2
        sc += c2
    se /= n_shuffle
    sc /= n_shuffle
    d = np.arange(1, MAX_LAG + 1)
    return pd.DataFrame({
        "corpus": name, "kind": kind, "lag": d,
        "p_exact": e[1:] / tot[1:], "p_exact_shuffled": se[1:] / tot[1:],
        "p_near": c[1:] / tot[1:], "p_near_shuffled": sc[1:] / tot[1:],
    })


def vertical_counts(pages: list[list[list[str]]], near: dict[str, set[str]], rng: random.Random | None,
                    trim_edges: bool) -> tuple[dict, dict]:
    hit = {o: 0 for o in OFFSETS}
    tot = {o: 0 for o in OFFSETS}
    for pg in pages:
        for upper, lower in zip(pg, pg[1:]):
            if len(upper) < 5 or len(lower) < 5:
                continue
            up = list(upper)
            lo_idx = range(1, len(lower) - 1) if trim_edges else range(len(lower))
            up_idx = range(1, len(up) - 1) if trim_edges else range(len(up))
            if rng is not None:
                core = [up[k] for k in up_idx]
                r = rng.randrange(1, len(core)) if len(core) > 1 else 0
                core = core[r:] + core[:r]
                for k, w in zip(up_idx, core):
                    up[k] = w
            for j in lo_idx:
                a = lower[j]
                na = near[a]
                for o in OFFSETS:
                    k = j + o
                    if k in up_idx:
                        tot[o] += 1
                        b = up[k]
                        if a == b or b in na:
                            hit[o] += 1
    return hit, tot


def vertical_table(name: str, kind: str, pages: list[list[list[str]]], rng: random.Random,
                   n_null: int = 200, trim_edges: bool = True) -> pd.DataFrame:
    near = stats.neighbor_map(w for pg in pages for ln in pg for w in ln)
    hit, tot = vertical_counts(pages, near, None, trim_edges)
    null = {o: [] for o in OFFSETS}
    for _ in range(n_null):
        h, t = vertical_counts(pages, near, rng, trim_edges)
        for o in OFFSETS:
            null[o].append(h[o] / t[o] if t[o] else np.nan)
    rows = []
    for o in OFFSETS:
        p = hit[o] / tot[o] if tot[o] else np.nan
        mu, sd = float(np.nanmean(null[o])), float(np.nanstd(null[o]))
        rows.append({"corpus": name, "kind": kind, "offset": o, "pairs": tot[o], "p_match": p,
                     "p_null": mu, "ratio": p / mu if mu else np.nan, "z": (p - mu) / sd if sd else np.nan})
    return pd.DataFrame(rows)


def main(root: Path) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(4)
    sets = [("Voynich all", "voynich", voynich_pages("all")),
            ("Voynich A", "voynich", voynich_pages("A")),
            ("Voynich B", "voynich", voynich_pages("B"))]
    wanted = ("Pliny, Nat. Hist. 16-20", "Celsus", "Secreta", "Rettorica", "Cirurgie", "Hebrew",
              "Latin: Bible", "Naibbe", "Self-citation")
    for c in corpora.controls(root):
        if c.kind != "human_gibberish" and any(k in c.name for k in wanted):
            sets.append((c.name, c.kind, pseudo_pages(c.lines)))

    lag, vert = [], []
    for name, kind, pages in sets:
        lt = lag_table(name, kind, pages, rng)
        lag.append(lt)
        r1, r5, r20 = (lt.loc[lt.lag == d].iloc[0] for d in (1, 5, 20))
        vt = vertical_table(name, kind, pages, rng)
        vert.append(vt)
        v0 = vt.loc[vt.offset == 0].iloc[0]
        vfar = vt.loc[vt.offset.abs() >= 4, "ratio"].mean()
        print(f"{name[:46]:46s} near/shuf lag1 {r1.p_near / r1.p_near_shuffled:5.2f} lag5 {r5.p_near / r5.p_near_shuffled:5.2f} "
              f"lag20 {r20.p_near / r20.p_near_shuffled:5.2f} | exact lag1 {r1.p_exact / r1.p_exact_shuffled:5.2f} "
              f"| above: ratio@0 {v0.ratio:5.2f} (z {v0.z:+5.1f}), |offset|>=4 {vfar:5.2f}")
    pd.concat(lag).to_csv(OUT / "lag_similarity.csv", index=False)
    pd.concat(vert).to_csv(OUT / "vertical_alignment.csv", index=False)

    v = pd.concat(vert)
    print("\nMatch ratio vs offset to the line above (observed / rotated-line null)")
    piv = v.pivot(index="corpus", columns="offset", values="ratio").round(2)
    print(piv.to_string())


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else corpora.default_root())
