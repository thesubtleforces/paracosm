"""A05 - What does the vocabulary track: the subject (illustration), the scribe, or both?

Pages are compared by vocabulary (LSA vectors as in A06, and plain TF-IDF cosine). The manuscript
lets us pull the two factors apart in a few places:

  same subject, different scribe   herbal pages by scribes 1, 2, 3 and 5
  same scribe, different subject   scribe 1: herbal vs pharmaceutical; scribe 2: herbal vs
                                   biological; scribe 3: herbal vs starred paragraphs

Usage:  python -I src/a05_sections_scribes.py
Writes: results/tables/cell_similarity.csv, results/tables/cell_keywords.csv,
        results/tables/scribe_vs_section.csv
"""
from __future__ import annotations

import itertools
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import corpora  # noqa: E402
import stats  # noqa: E402
from a06_bifolio_order import LSA, tfidf_cosine  # noqa: E402

OUT = corpora.PROJECT / "results" / "tables"
MIN_TOKENS = 40
SECTION = {"H": "herbal", "P": "pharma", "B": "biological", "S": "stars", "Z": "zodiac",
           "A": "astro", "C": "cosmo", "T": "text"}


def main() -> None:
    p, t = corpora.voynich_frames()
    p = pd.read_csv(corpora.PROJECT / "data" / "derived" / "pages.csv", dtype={"hand": str})
    p = p[(p.n_tokens >= MIN_TOKENS) & p.hand.isin(list("12345"))].copy()
    p["cell"] = "S" + p.hand + " " + p.illustration.map(SECTION)
    lsa = LSA(t)
    cos = tfidf_cosine(t)

    cells = [c for c, n in p.cell.value_counts().items() if n >= 5]
    pages = {c: list(p[p.cell == c].page) for c in cells}
    sheet = dict(zip(p.page, p.bifolio))
    print("cells (scribe x illustration) with >= 5 pages:", {c: len(v) for c, v in pages.items()})

    def mean_sim(a_pages, b_pages, f, same):
        vals = []
        for a, b in (itertools.combinations(a_pages, 2) if same else itertools.product(a_pages, b_pages)):
            if sheet[a] == sheet[b]:
                continue                      # leave out same-sheet pairs: A06 shows they are special
            v = f(a, b)
            if not np.isnan(v):
                vals.append(v)
        return float(np.mean(vals)) if vals else float("nan"), len(vals)

    rows = []
    for a in cells:
        for b in cells:
            m, n = mean_sim(pages[a], pages[b], lsa.sim, a == b)
            m2, _ = mean_sim(pages[a], pages[b], cos, a == b)
            rows.append({"cell_a": a, "cell_b": b, "lsa": m, "tfidf": m2, "n_pairs": n})
    cs = pd.DataFrame(rows)
    cs.to_csv(OUT / "cell_similarity.csv", index=False)
    with pd.option_context("display.width", 250):
        print("\nmean LSA similarity between cells (diagonal = within cell, same-sheet pairs excluded):")
        print(cs.pivot(index="cell_a", columns="cell_b", values="lsa").loc[cells, cells].round(2).to_string())

    # ---- targeted contrasts
    def contrast(label, within_a, within_b, f=lsa.sim):
        wa = [f(x, y) for x, y in itertools.combinations(pages[within_a], 2) if sheet[x] != sheet[y]]
        wb = [f(x, y) for x, y in itertools.combinations(pages[within_b], 2) if sheet[x] != sheet[y]]
        ab = [f(x, y) for x, y in itertools.product(pages[within_a], pages[within_b])]
        wa, wb, ab = (np.array([v for v in z if not np.isnan(v)]) for z in (wa, wb, ab))
        within = np.concatenate([wa, wb]).mean()
        return {"contrast": label, "cells": f"{within_a} | {within_b}", "within_a": wa.mean(), "within_b": wb.mean(),
                "between": ab.mean(), "drop": within - ab.mean(), "between_over_within": ab.mean() / within}

    out = []
    for label, a, b in [
        ("same subject, other scribe", "S1 herbal", "S2 herbal"),
        ("same subject, other scribe", "S1 herbal", "S3 herbal"),
        ("same subject, other scribe", "S2 herbal", "S3 herbal"),
        ("same subject, other scribe", "S1 herbal", "S5 herbal"),
        ("same scribe, other subject", "S1 herbal", "S1 pharma"),
        ("same scribe, other subject", "S2 herbal", "S2 biological"),
        ("same scribe, other subject", "S3 herbal", "S3 stars"),
    ]:
        if a in pages and b in pages:
            out.append(contrast(label, a, b))
    sv = pd.DataFrame(out)
    sv.to_csv(OUT / "scribe_vs_section.csv", index=False)
    with pd.option_context("display.width", 250):
        print("\ncontrasts (LSA): how far similarity falls when one factor changes")
        print(sv.round(3).to_string(index=False))

    # ---- most characteristic words of each cell (log-odds with a uniform prior), for orientation
    t = t[t.clean & t.generic.isin(["P", "C", "R"])].merge(p[["page", "cell"]], on="page")
    tot = Counter(t.token)
    n_tot = sum(tot.values())
    kw = []
    for c in cells:
        cc = Counter(t[t.cell == c].token)
        n_c = sum(cc.values())
        scored = []
        for w, k in cc.items():
            if k < 8:
                continue
            rest = tot[w] - k
            lo = np.log((k + 0.5) / (n_c - k + 0.5)) - np.log((rest + 0.5) / (n_tot - n_c - rest + 0.5))
            se = np.sqrt(1 / (k + 0.5) + 1 / (rest + 0.5))
            scored.append((lo / se, w, k, rest))
        scored.sort(reverse=True)
        kw.append({"cell": c, "tokens": n_c, "top_words": " ".join(f"{w}({k}/{k + r})" for _, w, k, r in scored[:10])})
    k = pd.DataFrame(kw)
    k.to_csv(OUT / "cell_keywords.csv", index=False)
    with pd.option_context("display.width", 250, "display.max_colwidth", 200):
        print("\nmost characteristic words per cell: word(count in cell / count in whole text)")
        print(k.to_string(index=False))

    # Currier's best-known A/B marker: the glyph sequence 'ed'
    lang = t.merge(pd.read_csv(corpora.PROJECT / "data" / "derived" / "pages.csv")[["page", "language"]], on="page", suffixes=("", "_p"))
    for L in ("A", "B"):
        sub = lang[lang.language_p == L].token
        print(f"language {L}: {len(sub)} tokens; share containing 'ed': {sub.str.contains('ed').mean():.3f}; "
              f"share beginning 'qo': {sub.str.startswith('qo').mean():.3f}; share ending 'dy': {sub.str.endswith('dy').mean():.3f}")


if __name__ == "__main__":
    main()
