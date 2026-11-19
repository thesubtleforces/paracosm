"""A06 - Page-order structure: replicating and stress-testing the "singulion" result.

Layfield & Davis (2026, Digital Medievalist 19) compare, with Latent Semantic Analysis, three kinds
of page pairs inside the bound quires:

  confoliate  recto and verso of the same leaf            (cannot change when sheets are reordered)
  conjoint    the two inner pages of one folded sheet     (cannot change either)
  facing      verso of a leaf and recto of the next leaf  (changes when sheets are reordered)

In two Latin manuscripts with normal quires, confoliate ~ facing > conjoint. In the Voynich
manuscript they find conjoint ~ confoliate > facing, and conclude that each sheet was meant to be
read on its own, in sequence.

This script (1) re-implements their LSA pipeline from the paper's description and reproduces the
pattern, then (2) asks what the pattern can and cannot show, with two controls they did not run:

  * scribe/dialect control: in the herbal quires the sheets of different scribes are interleaved,
    so facing pages are often by different scribes while conjoint pages never are. We therefore
    compare conjoint pairs with other SAME-SCRIBE pairs of the same quire.
  * all six page pairs of a sheet: inner (1v-2r), outer (1r-2v), confoliate (1r-1v, 2r-2v) and
    diagonal (1r-2r, 1v-2v). "Read in sequence 1r,1v,2r,2v" predicts inner > diagonal > outer;
    "each sheet is one unit of production, no reading order implied" predicts all six alike.

Usage:  python -I src/a06_bifolio_order.py
Writes: results/tables/lsa_pair_scores.csv, results/tables/lsa_quire_averages.csv,
        results/tables/lsa_pair_types.csv, results/tables/lsa_reorder.csv
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

OUT = corpora.PROJECT / "results" / "tables"
CHUNK, MIN_CHUNK, K = 40, 20, 75
QUIRES = [1, 2, 3, 4, 5, 6, 7, 13, 20]          # the quires analysed in the paper


def stop_words(tf: Counter, w: int = 6, v: float = 3.0) -> set[str]:
    """Paper's heuristic: slide a window of w terms down the frequency list until the average
    drop in frequency between neighbouring terms inside the window falls below v."""
    ranked = [t for t, _ in tf.most_common()]
    freqs = [tf[t] for t in ranked]
    x = 0
    while x + w <= len(freqs) and (freqs[x] - freqs[x + w - 1]) / (w - 1) >= v:
        x += 1
    return set(ranked[:w + x - 1])


def chunks(tokens: list[str]) -> list[list[str]]:
    n = len(tokens)
    if n < MIN_CHUNK:
        return []
    k = max(1, round(n / CHUNK))
    bounds = np.linspace(0, n, k + 1).astype(int)
    return [tokens[a:b] for a, b in zip(bounds[:-1], bounds[1:])]


class LSA:
    def __init__(self, t: pd.DataFrame, k: int = K):
        t = t[t.clean & ~t.alt & t.generic.isin(["P", "C", "R"])]
        self.stop = stop_words(Counter(t.token))
        t = t[~t.token.isin(self.stop)]
        self.page_tokens = {pg: list(g.token) for pg, g in t.groupby("page", sort=False)}
        docs = []
        for (_, _), g in t.groupby(["seq", "generic"], sort=True):
            docs += chunks(list(g.token))
        df = Counter(w for d in docs for w in set(d))
        self.vocab = sorted(w for w, c in df.items() if c >= 2)
        self.index = {w: i for i, w in enumerate(self.vocab)}
        n = len(docs)
        self.idf = np.array([np.log(n / df[w]) for w in self.vocab])
        A = np.zeros((len(self.vocab), n))
        for j, d in enumerate(docs):
            for w, c in Counter(d).items():
                i = self.index.get(w)
                if i is not None:
                    A[i, j] = c
        A *= self.idf[:, None]
        U, S, _ = np.linalg.svd(A, full_matrices=False)
        self.Tk = U[:, :k]
        self.n_docs, self.k = n, k
        self._vec: dict[str, np.ndarray] = {}

    def vector(self, page: str) -> np.ndarray | None:
        """Fold a whole page into the space; the S-scaled document vector equals d^T T_k."""
        if page not in self._vec:
            d = np.zeros(len(self.vocab))
            for w, c in Counter(self.page_tokens.get(page, [])).items():
                i = self.index.get(w)
                if i is not None:
                    d[i] = c
            d *= self.idf
            self._vec[page] = d @ self.Tk if d.any() else None
        return self._vec[page]

    def sim(self, a: str, b: str) -> float:
        va, vb = self.vector(a), self.vector(b)
        if va is None or vb is None:
            return float("nan")
        return float(va @ vb / (np.linalg.norm(va) * np.linalg.norm(vb)))


def tfidf_cosine(t: pd.DataFrame):
    """A plain alternative to LSA: cosine of TF-IDF vectors over whole pages (no SVD)."""
    t = t[t.clean & t.generic.isin(["P", "C", "R"])]
    counts = {pg: Counter(g.token) for pg, g in t.groupby("page", sort=False)}
    df = Counter(w for c in counts.values() for w in c)
    n = len(counts)
    vecs = {}
    for pg, c in counts.items():
        v = {w: f * np.log(n / df[w]) for w, f in c.items() if df[w] >= 2}
        norm = np.sqrt(sum(x * x for x in v.values()))
        vecs[pg] = (v, norm)

    def sim(a: str, b: str) -> float:
        if a not in vecs or b not in vecs:
            return float("nan")
        (va, na), (vb, nb) = vecs[a], vecs[b]
        if na == 0 or nb == 0:
            return float("nan")
        if len(va) > len(vb):
            va, vb = vb, va
        return sum(x * vb.get(w, 0.0) for w, x in va.items()) / (na * nb)

    return sim


def quire_layout(p: pd.DataFrame, q: int):
    """Leaves of a quire in bound order, with sheet membership. Only ordinary (non-foldout) leaves."""
    g = p[(p.quire == q) & (p.panel == "")]
    leaves = []
    for folio, fg in g.groupby("folio", sort=True):
        sides = dict(zip(fg.side, fg.page))
        if "r" in sides and "v" in sides:
            leaves.append({"folio": int(folio), "r": sides["r"], "v": sides["v"],
                           "sheet": fg.bifolio.iloc[0], "half": fg.leaf_half.iloc[0],
                           "hand": fg.hand.iloc[0]})
    return leaves


def pairs_for_quire(p: pd.DataFrame, q: int) -> list[dict]:
    leaves = quire_layout(p, q)
    rows = []
    by_sheet: dict[str, list[dict]] = {}
    for lf in leaves:
        by_sheet.setdefault(lf["sheet"], []).append(lf)
        rows.append({"quire": q, "type": "confoliate", "a": lf["r"], "b": lf["v"], "sheet": lf["sheet"]})
    for a, b in zip(leaves, leaves[1:]):
        if b["folio"] == a["folio"] + 1:           # no lost leaf in between
            rows.append({"quire": q, "type": "facing", "a": a["v"], "b": b["r"],
                         "sheet": a["sheet"] if a["sheet"] == b["sheet"] else None,
                         "central": a["sheet"] == b["sheet"]})
    for sheet, ls in by_sheet.items():
        if len(ls) == 2:
            first, second = sorted(ls, key=lambda x: x["folio"])
            rows += [
                {"quire": q, "type": "conjoint", "a": first["v"], "b": second["r"], "sheet": sheet},
                {"quire": q, "type": "outer", "a": first["r"], "b": second["v"], "sheet": sheet},
                {"quire": q, "type": "diagonal", "a": first["r"], "b": second["r"], "sheet": sheet},
                {"quire": q, "type": "diagonal", "a": first["v"], "b": second["v"], "sheet": sheet},
            ]
    return rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    p, t = corpora.voynich_frames()
    p = pd.read_csv(corpora.PROJECT / "data" / "derived" / "pages.csv", dtype={"hand": str, "panel": str}).fillna({"panel": ""})
    hand = dict(zip(p.page, p.hand))
    lang = dict(zip(p.page, p.language))
    quire_of = dict(zip(p.page, p.quire))
    sheet_of = dict(zip(p.page, p.bifolio))

    lsa = LSA(t)
    cos = tfidf_cosine(t)
    print(f"LSA space: {len(lsa.vocab)} terms x {lsa.n_docs} documents, k={lsa.k}; "
          f"{len(lsa.stop)} stop words: {sorted(lsa.stop, key=len)[:40]}")
    print("  (paper: 2,161 terms x 606 documents, k=75, on ZL v2a)")

    rows = []
    for q in QUIRES:
        for r in pairs_for_quire(p, q):
            r["lsa"] = lsa.sim(r["a"], r["b"])
            r["tfidf"] = cos(r["a"], r["b"])
            r["same_scribe"] = hand[r["a"]] == hand[r["b"]]
            r["scribes"] = f"{hand[r['a']]}-{hand[r['b']]}"
            r["same_language"] = lang[r["a"]] == lang[r["b"]]
            rows.append(r)
    pairs = pd.DataFrame(rows)
    pairs.to_csv(OUT / "lsa_pair_scores.csv", index=False)

    main3 = pairs[pairs.type.isin(["confoliate", "facing", "conjoint"])]
    qa = main3.pivot_table(index="quire", columns="type", values="lsa", aggfunc="mean")[["confoliate", "facing", "conjoint"]]
    qa.loc["overall (mean of pairs)"] = main3.groupby("type").lsa.mean()[["confoliate", "facing", "conjoint"]]
    qa.to_csv(OUT / "lsa_quire_averages.csv")
    print("\nLSA quire averages (paper's Table 8: overall .383 / .298 / .433):")
    print(qa.round(3).to_string())
    print("\nsame with plain TF-IDF cosine:")
    print(main3.groupby("type").tfidf.mean()[["confoliate", "facing", "conjoint"]].round(3).to_string())

    # ---- control 1: is "facing is low" just "facing pages are often by another scribe"?
    f = pairs[pairs.type == "facing"]
    print("\nfacing pairs by scribe agreement (LSA):")
    print(f.groupby(["same_scribe"]).lsa.agg(["mean", "count"]).round(3).to_string())
    print("facing pairs, herbal quires only, by scribe agreement:")
    print(f[f.quire <= 7].groupby("same_scribe").lsa.agg(["mean", "count"]).round(3).to_string())

    # baseline: every same-scribe pair of pages in the same quire that is NOT on the same sheet
    base = []
    for q in QUIRES:
        pages_q = [x for lf in quire_layout(p, q) for x in (lf["r"], lf["v"])]
        for a, b in itertools.combinations(pages_q, 2):
            if hand[a] == hand[b] and sheet_of[a] != sheet_of[b]:
                base.append({"quire": q, "a": a, "b": b, "lsa": lsa.sim(a, b), "tfidf": cos(a, b),
                             "facing": bool(((f.a == a) & (f.b == b)).any())})
    base = pd.DataFrame(base)

    summary = []
    for label, sel in [("herbal quires 1-7", lambda d: d.quire <= 7), ("quire 13 (balneological)", lambda d: d.quire == 13),
                       ("quire 20 (starred paragraphs)", lambda d: d.quire == 20), ("all nine quires", lambda d: d.quire > 0)]:
        d = pairs[sel(pairs)]
        b = base[sel(base)]
        for measure in ("lsa", "tfidf"):
            row = {"section": label, "measure": measure}
            for typ in ("confoliate", "conjoint", "outer", "diagonal"):
                v = d[d.type == typ][measure].dropna()
                row[typ] = v.mean()
                row[typ + "_n"] = len(v)
            fs = d[(d.type == "facing") & d.same_scribe & ~d.central.fillna(False).astype(bool)][measure].dropna()
            fd = d[(d.type == "facing") & ~d.same_scribe][measure].dropna()
            row["facing_same_scribe_other_sheet"], row["facing_same_scribe_n"] = fs.mean(), len(fs)
            row["facing_other_scribe"], row["facing_other_scribe_n"] = fd.mean(), len(fd)
            bb = b[measure].dropna()
            row["same_scribe_same_quire_other_sheet"], row["baseline_n"] = bb.mean(), len(bb)
            # effect size: each conjoint pair minus the baseline OF ITS OWN QUIRE (sections differ a lot
            # in overall similarity), with a bootstrap interval over sheets
            q_base = b.groupby("quire")[measure].mean()
            cjd = d[d.type == "conjoint"].dropna(subset=[measure])
            diff = (cjd[measure] - cjd.quire.map(q_base)).values
            lo, hi = stats.bootstrap_ci(diff, seed=1)
            row["conjoint_minus_baseline"] = diff.mean()
            row["ci95_lo"], row["ci95_hi"] = lo, hi
            for typ in ("confoliate", "outer", "diagonal"):
                td = d[d.type == typ].dropna(subset=[measure])
                tdiff = (td[measure] - td.quire.map(q_base)).values
                tlo, thi = stats.bootstrap_ci(tdiff, seed=1)
                row[typ + "_minus_baseline"] = tdiff.mean()
                row[typ + "_ci"] = f"[{tlo:+.3f}, {thi:+.3f}]"
            fsd = d[(d.type == "facing") & d.same_scribe & ~d.central.fillna(False).astype(bool)].dropna(subset=[measure])
            fdiff = (fsd[measure] - fsd.quire.map(q_base)).values
            flo, fhi = stats.bootstrap_ci(fdiff, seed=1)
            row["facing_minus_baseline"] = fdiff.mean()
            row["facing_ci"] = f"[{flo:+.3f}, {fhi:+.3f}]"
            summary.append(row)
    s = pd.DataFrame(summary)
    s.to_csv(OUT / "lsa_pair_types.csv", index=False)
    show = ["section", "measure", "confoliate", "conjoint", "outer", "diagonal", "facing_same_scribe_other_sheet",
            "facing_other_scribe", "same_scribe_same_quire_other_sheet", "conjoint_minus_baseline", "ci95_lo", "ci95_hi"]
    print("\nmean similarity by pair type (control 1 baseline = same scribe, same quire, different sheet):")
    with pd.option_context("display.width", 250):
        print(s[show].round(3).to_string(index=False))
    print("\nexcess over own-quire same-scribe baseline (LSA), mean [95% CI over pairs]:")
    for r in s[s.measure == "lsa"].itertuples():
        print(f"  {r.section:30s} conjoint {r.conjoint_minus_baseline:+.3f} [{r.ci95_lo:+.3f}, {r.ci95_hi:+.3f}]  "
              f"confoliate {r.confoliate_minus_baseline:+.3f} {r.confoliate_ci}  outer {r.outer_minus_baseline:+.3f} {r.outer_ci}  "
              f"diagonal {r.diagonal_minus_baseline:+.3f} {r.diagonal_ci}  facing(same scribe, other sheet) {r.facing_minus_baseline:+.3f} {r.facing_ci}")
    print("\ncounts:", s[s.measure == "lsa"][["section", "confoliate_n", "conjoint_n", "outer_n", "diagonal_n",
                                              "facing_same_scribe_n", "facing_other_scribe_n", "baseline_n"]].to_string(index=False))

    # ---- control 2: within-sheet pair types, paired by sheet (each sheet contributes one difference)
    print("\nwithin-sheet contrasts, paired by sheet (LSA), mean difference [95% bootstrap CI], n sheets")
    for label, sel in [("herbal 1-7", lambda d: d.quire <= 7), ("Q13+Q20", lambda d: d.quire.isin([13, 20])), ("all", lambda d: d.quire > 0)]:
        d = pairs[sel(pairs) & pairs.sheet.notna()]
        w = d.pivot_table(index="sheet", columns="type", values="lsa", aggfunc="mean")
        w = w.dropna(subset=["conjoint", "outer", "diagonal", "confoliate"])
        for a, b in [("conjoint", "outer"), ("conjoint", "diagonal"), ("confoliate", "diagonal"), ("conjoint", "confoliate")]:
            diff = (w[a] - w[b]).values
            lo, hi = stats.bootstrap_ci(diff, seed=2)
            print(f"  {label:10s} {a:10s} - {b:10s}: {diff.mean():+.3f} [{lo:+.3f}, {hi:+.3f}]  n={len(diff)}")

    # ---- re-ordering experiment for quires 13 and 20 (paper's Table 14)
    out = []
    for q in (13, 20):
        leaves = quire_layout(p, q)
        sheets: dict[str, list[dict]] = {}
        for lf in leaves:
            sheets.setdefault(lf["sheet"], []).append(lf)
        units = {s: sorted(ls, key=lambda x: x["folio"]) for s, ls in sheets.items() if len(ls) == 2}
        cur = pairs[(pairs.quire == q) & (pairs.type == "facing")].lsa.mean()
        name = lambda s: "|".join(str(lf["folio"]) for lf in units[s])
        # f116v has no main text: its sheet can only stand last (as the paper also concludes)
        last = [s for s in units if lsa.vector(units[s][1]["v"]) is None]
        free = [s for s in units if s not in last]
        scored = []
        for perm in itertools.permutations(free):
            perm = list(perm) + last
            # singulions read in sequence: transition = last page of one sheet -> first page of the next
            sc = np.mean([lsa.sim(units[a][1]["v"], units[b][0]["r"]) for a, b in zip(perm, perm[1:])])
            scored.append((sc, perm))
        scored.sort(reverse=True, key=lambda x: x[0])
        allsc = np.array([x[0] for x in scored])
        bound = [s for s in sorted(units, key=lambda s: units[s][0]["folio"])]
        for rank in (0, 1, 2):
            out.append({"quire": q, "rank": rank + 1, "score": scored[rank][0],
                        "sequence": ", ".join(name(s) for s in scored[rank][1])})
        # How surprising is the best score? Searching 120 orders always finds one that beats the binding.
        # Null: keep the set of sheet-to-sheet transition scores but deal them out at random to the
        # (from-sheet, to-sheet) slots, then search again. If the sheets had a real linear order, the
        # true best path should beat what the same search finds in scrambled score tables.
        n = len(allsc)
        every = free + last
        trans = {(a, b): lsa.sim(units[a][1]["v"], units[b][0]["r"]) for a in free for b in every if a != b}
        keys, vals = list(trans), np.array(list(trans.values()))
        rng = np.random.default_rng(6)
        perms = [list(pm) + last for pm in itertools.permutations(free)]
        null_best = []
        for _ in range(2000):
            sh = dict(zip(keys, rng.permutation(vals)))
            null_best.append(max(np.mean([sh[(a, b)] for a, b in zip(pm, pm[1:])]) for pm in perms))
        null_best = np.array(null_best)
        pval = float((null_best >= allsc.max()).mean())
        out.append({"quire": q, "rank": "all orders", "score": allsc.mean(),
                    "sequence": f"n {n}, sd {allsc.std():.3f}, min {allsc.min():.3f}; as bound {cur:.3f}; "
                                f"best found by the same search in scrambled score tables: median {np.median(null_best):.3f} "
                                f"(95% range {np.percentile(null_best, 2.5):.3f}-{np.percentile(null_best, 97.5):.3f}); "
                                f"P(scrambled best >= observed best) = {pval:.2f}"})
    ro = pd.DataFrame(out)
    ro.to_csv(OUT / "lsa_reorder.csv", index=False)
    print("\nre-ordering quires 13 and 20 as singulions (paper: Q13 best 0.517 = 77|82, 78|81, 75|84, 76|83, 79|80;")
    print("   Q20 best 0.526 = 105|114, 104|115, 106|113, 107|112, 108|111, 103|116)")
    with pd.option_context("display.width", 250, "display.max_colwidth", 120):
        print(ro.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
