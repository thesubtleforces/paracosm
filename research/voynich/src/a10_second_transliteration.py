"""A10 - Validation: do the results depend on whose reading of the script we use?

The manuscript's text exists for analysis only as transliterations, and they disagree on about half
of all lines. Round 1 used Zandbergen and Landini's (ZL). Here the headline measurements are
repeated on two independent ones: Takahashi's (IT, 1998, EVA alphabet) and Claston's (GC, v101
alphabet, which splits the script into about three times as many glyph types).

Page metadata (scribe, sheet, section) is the same in all three files.

Usage:  python -I src/a10_second_transliteration.py
Writes: results/tables/v3_transliterations.csv
"""
from __future__ import annotations

import itertools
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import corpora  # noqa: E402
import stats  # noqa: E402
from a03_line_effects import test as line_test  # noqa: E402
from a04_local_similarity import lag_table, vertical_table, voynich_pages  # noqa: E402
from a06_bifolio_order import LSA, QUIRES, pairs_for_quire, quire_layout  # noqa: E402

OUT = corpora.PROJECT / "results" / "tables"
TDIR = corpora.PROJECT / "data" / "transliterations"
FILES = [("ZL 3b (Zandbergen-Landini, EVA)", "ZL3b-n.txt"), ("IT 2a (Takahashi, EVA)", "IT2a-n.txt"), ("GC 2a (Claston, v101)", "GC2a-n.txt")]


def headline(label: str, fname: str) -> dict:
    corpora.use_transliteration(TDIR / fname)
    rng = random.Random(10)
    p, t = corpora.voynich_frames()
    par = t[(t.generic == "P") & t.clean]
    row = {"transliteration": label, "words": int(len(t)), "distinct_forms": int(t[t.clean].token.nunique())}

    toks = list(par.token)
    row["h2"] = float(np.mean([stats.char_entropies(w)[1] for w in stats.windows(toks, 10000, 3)]))

    pages = voynich_pages("all")
    lt = lag_table(label, "voynich", pages, rng)
    l1 = lt[lt.lag == 1].iloc[0]
    row["near_lag1"] = l1.p_near / l1.p_near_shuffled
    row["exact_lag1"] = l1.p_exact / l1.p_exact_shuffled

    le = line_test([ln for pg in pages for ln in pg], rng, n_perm=200)
    row["line_start_jsd"], row["line_start_z"] = le["jsd_first"], le["jsd_first_z"]
    row["line_end_jsd"], row["line_end_z"] = le["jsd_last"], le["jsd_last_z"]

    vt = vertical_table(label, "voynich", pages, rng, n_null=200)
    v0 = vt[vt.offset == 0].iloc[0]
    row["above_ratio"], row["above_z"] = v0.ratio, v0.z

    # sheets: LSA similarity by pair type, against the own-quire same-scribe baseline
    meta = pd.read_csv(corpora.PROJECT / "data" / "derived" / "pages.csv", dtype={"hand": str, "panel": str}).fillna({"panel": ""})
    hand = dict(zip(meta.page, meta.hand))
    sheet = dict(zip(meta.page, meta.bifolio))
    lsa = LSA(t)
    rows = []
    for q in QUIRES:
        for r in pairs_for_quire(meta, q):
            r["lsa"] = lsa.sim(r["a"], r["b"])
            r["same_scribe"] = hand[r["a"]] == hand[r["b"]]
            rows.append(r)
    pairs = pd.DataFrame(rows)
    for typ in ("confoliate", "facing", "conjoint"):
        row[f"lsa_{typ}"] = pairs[pairs.type == typ].lsa.mean()
    base = {}
    for q in QUIRES:
        pq = [x for lf in quire_layout(meta, q) for x in (lf["r"], lf["v"])]
        vals = [lsa.sim(a, b) for a, b in itertools.combinations(pq, 2) if hand[a] == hand[b] and sheet[a] != sheet[b]]
        base[q] = np.nanmean(vals)
    cj = pairs[pairs.type == "conjoint"].dropna(subset=["lsa"])
    d = (cj.lsa - cj.quire.map(base)).values
    row["inner_pair_excess"] = d.mean()
    row["inner_pair_ci_lo"], row["inner_pair_ci_hi"] = stats.bootstrap_ci(d, seed=1)
    ou = pairs[pairs.type == "outer"].dropna(subset=["lsa"])
    row["outer_pair_excess"] = (ou.lsa - ou.quire.map(base)).mean()
    fc = pairs[(pairs.type == "facing") & pairs.same_scribe & ~pairs.central.fillna(False).astype(bool)].dropna(subset=["lsa"])
    row["facing_other_sheet_excess"] = (fc.lsa - fc.quire.map(base)).mean()

    # scribe against subject
    m = meta[(meta.n_tokens >= 40) & meta.hand.isin(list("12345"))]

    def cell(h, ill):
        return list(m[(m.hand == h) & (m.illustration == ill)].page)

    def kept(a, b):
        wa = [lsa.sim(x, y) for x, y in itertools.combinations(a, 2) if sheet[x] != sheet[y]]
        wb = [lsa.sim(x, y) for x, y in itertools.combinations(b, 2) if sheet[x] != sheet[y]]
        ab = [lsa.sim(x, y) for x, y in itertools.product(a, b)]
        return np.nanmean(ab) / np.nanmean(wa + wb)

    row["kept_scribe1_to_2_herbal"] = kept(cell("1", "H"), cell("2", "H"))
    row["kept_scribe1_herbal_to_pharma"] = kept(cell("1", "H"), cell("1", "P"))
    row["kept_scribe2_herbal_to_bathing"] = kept(cell("2", "H"), cell("2", "B"))
    return row


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = [headline(label, fname) for label, fname in FILES]
    corpora.use_transliteration(corpora.ZL)
    df = pd.DataFrame(rows).set_index("transliteration").T
    df.to_csv(OUT / "v3_transliterations.csv")
    with pd.option_context("display.width", 200, "display.float_format", "{:.3f}".format):
        print(df.to_string())


if __name__ == "__main__":
    main()
