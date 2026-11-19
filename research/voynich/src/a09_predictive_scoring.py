"""A09 - Validation: which mechanism predicts the next word, scored on held-out sheets.

Step 4 of the method in the report: stop comparing summary statistics and ask each candidate
mechanism to predict words it has not seen. Every word of a held-out sheet is given a probability
by a mixture of four simple predictors, and we measure how many bits each predictor saves.

  unigram  how common the word is in the rest of the book (new words get a glyph-trigram guess)
  grammar  the word tends to follow the previous word            (bigram counts from other sheets)
  repeat   the word already occurred among the last 40 words of this page   (exact copy)
  vary     the word is one glyph different from one of the last 40 words    (copy and modify)

Meaningful prose leans on "grammar" and, for topical words, on "repeat". A copy-and-modify writing
routine leans on "repeat" and "vary". The same code scores the manuscript and every control, so the
controls show what each kind of text looks like before the manuscript is read off the same scale.

Sheets are the held-out unit for the manuscript (five folds over sheets); controls are cut into
30-line pages and held out in five contiguous blocks. Mixture weights are fitted by EM on a slice
of the training folds, never on the test fold.

Usage:  python -I src/a09_predictive_scoring.py
Writes: results/tables/v2_predictive_scores.csv, results/tables/v2_class_profile.csv
"""
from __future__ import annotations

import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import corpora  # noqa: E402
import stats  # noqa: E402
from a04_local_similarity import pseudo_pages  # noqa: E402
from a08_more_controls import manuscript, tess_lines  # noqa: E402

OUT = corpora.PROJECT / "results" / "tables"
WINDOW = 40
FOLDS = 5
CAP = 35000
MODELS = {
    "unigram": ["uni"],
    "+grammar": ["uni", "bi"],
    "+repeat": ["uni", "cache"],
    "+repeat+vary": ["uni", "cache", "near"],
    "all four": ["uni", "bi", "cache", "near"],
}


class CharModel:
    """Glyph trigram model over word types, for words never seen in training."""

    def __init__(self, types, k: float = 0.1):
        self.k = k
        self.tri = Counter()
        self.bi = Counter()
        self.alpha = {"$"} | {c for w in types for c in w}
        for w in types:
            s = "^^" + w + "$"
            for a, b, c in zip(s, s[1:], s[2:]):
                self.tri[a, b, c] += 1
                self.bi[a, b] += 1
        self.v = len(self.alpha) + 1          # +1 for glyphs unseen in training

    def logp(self, w: str) -> float:
        s = "^^" + w + "$"
        lp = 0.0
        for a, b, c in zip(s, s[1:], s[2:]):
            lp += math.log((self.tri[a, b, c] + self.k) / (self.bi[a, b] + self.k * self.v))
        return lp


def history_components(pages: list[list[str]], near: dict[str, set[str]], alphabet: int):
    """Probabilities that depend only on the page so far: exact repeat and one-glyph variation."""
    cache, vary = [], []
    for toks in pages:
        for i, w in enumerate(toks):
            win = toks[max(0, i - WINDOW):i]
            if not win:
                cache.append(0.0)
                vary.append(0.0)
                continue
            counts = Counter(win)
            cache.append(counts[w] / len(win))
            nw = near.get(w, ())
            v = 0.0
            for h, c in counts.items():
                if h in nw:
                    # a uniform choice among all strings one edit from h: delete, substitute or insert
                    v += c / ((2 * len(h) + 1) * alphabet)
            vary.append(v / len(win))
    return np.array(cache), np.array(vary)


def train_components(train_pages: list[list[str]], eval_pages: list[list[str]]):
    """Unigram (with glyph-model back-off for new words) and bigram probabilities for eval tokens."""
    uni = Counter(w for pg in train_pages for w in pg)
    n, t = sum(uni.values()), len(uni)
    big = Counter()
    ctx = Counter()
    for pg in train_pages:
        prev = "<s>"
        for w in pg:
            big[prev, w] += 1
            ctx[prev] += 1
            prev = w
    cm = CharModel(uni.keys())
    p_uni, p_bi = [], []
    for pg in eval_pages:
        prev = "<s>"
        for w in pg:
            if w in uni:
                p_uni.append(uni[w] / (n + t))
            else:
                p_uni.append(t / (n + t) * math.exp(cm.logp(w)))
            p_bi.append(big[prev, w] / ctx[prev] if ctx[prev] else 0.0)
            prev = w
    return np.array(p_uni), np.array(p_bi)


def em(P: np.ndarray, iters: int = 60) -> np.ndarray:
    lam = np.full(P.shape[1], 1.0 / P.shape[1])
    for _ in range(iters):
        mix = P * lam
        tot = mix.sum(1, keepdims=True)
        lam = (mix / tot).mean(0)
    return lam


def score(pages: list[list[str]], groups: list) -> dict:
    """Cross-validated bits per word for each nested model. `groups` assigns pages to held-out units."""
    all_tokens = [w for pg in pages for w in pg]
    near = stats.neighbor_map(all_tokens)
    alphabet = len({c for w in set(all_tokens) for c in w})
    cache, vary = history_components(pages, near, alphabet)
    offsets = np.cumsum([0] + [len(pg) for pg in pages])
    uniq = list(dict.fromkeys(groups))
    fold_of = {g: i % FOLDS for i, g in enumerate(uniq)}
    page_fold = np.array([fold_of[g] for g in groups])
    logp = {m: 0.0 for m in MODELS}
    lam_full = []
    n_tok = 0
    for f in range(FOLDS):
        test_idx = [i for i in range(len(pages)) if page_fold[i] == f]
        train_idx = [i for i in range(len(pages)) if page_fold[i] != f]
        if not test_idx or not train_idx:
            continue
        tune_idx = train_idx[::5]
        fit_idx = [i for i in train_idx if i not in set(tune_idx)]

        def comps(fit, ev):
            u, b = train_components([pages[i] for i in fit], [pages[i] for i in ev])
            sl = np.concatenate([np.arange(offsets[i], offsets[i + 1]) for i in ev])
            return {"uni": u, "bi": b, "cache": cache[sl], "near": vary[sl]}

        tune = comps(fit_idx, tune_idx)
        test = comps(train_idx, test_idx)
        for m, names in MODELS.items():
            lam = em(np.stack([tune[k] for k in names], 1))
            p = (np.stack([test[k] for k in names], 1) * lam).sum(1)
            logp[m] += np.log2(p).sum()
            if m == "all four":
                lam_full.append(lam)
        n_tok += len(test["uni"])
    bits = {m: -v / n_tok for m, v in logp.items()}
    lam = np.mean(lam_full, 0)
    return {
        "n_tokens": n_tok,
        "bits_unigram": bits["unigram"],
        "bits_all": bits["all four"],
        "gain_grammar": bits["unigram"] - bits["+grammar"],
        "gain_repeat": bits["unigram"] - bits["+repeat"],
        "gain_vary": bits["+repeat"] - bits["+repeat+vary"],
        "gain_grammar_after_copy": bits["+repeat+vary"] - bits["all four"],
        "w_unigram": lam[0], "w_grammar": lam[1], "w_repeat": lam[2], "w_vary": lam[3],
    }


def cap_pages(pages: list[list[str]], cap: int = CAP) -> list[list[str]]:
    out, n = [], 0
    for pg in pages:
        if n >= cap:
            break
        out.append(pg)
        n += len(pg)
    return out


def contiguous_groups(n_pages: int) -> list[int]:
    return [min(FOLDS - 1, i * FOLDS // max(n_pages, 1)) for i in range(n_pages)]


def voynich_sets():
    _, t = corpora.voynich_frames()
    p = pd.read_csv(corpora.PROJECT / "data" / "derived" / "pages.csv", dtype={"hand": str})
    sheet = dict(zip(p.page, p.bifolio.fillna(p.page)))
    t = t[(t.generic == "P") & t.clean]
    out = []
    for label, sel in [("Voynich, whole text", t), ("Voynich, Currier B", t[t.language == "B"]), ("Voynich, Currier A", t[t.language == "A"]),
                       ("Voynich, scribe 1", t[t.hand == "1"]), ("Voynich, scribe 2", t[t.hand == "2"]), ("Voynich, scribe 3", t[t.hand == "3"])]:
        pages, groups = [], []
        for pg, g in sel.groupby("page", sort=False):
            pages.append(list(g.token))
            groups.append(sheet[pg])
        out.append((label, "voynich", pages, groups))
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    random.seed(9)
    root = corpora.default_root()
    sets = voynich_sets()

    kind_name = {"natural": "prose", "cipher": "Naibbe cipher", "algo_gibberish": "copy-and-modify generator"}
    for c in corpora.controls(root):
        if c.kind == "human_gibberish":
            continue
        pages = cap_pages([[w for ln in pg for w in ln] for pg in pseudo_pages(c.lines)])
        sets.append((c.name, kind_name[c.kind], pages, contiguous_groups(len(pages))))

    tess = root / "tesserae" / "tesserae" / "texts" / "la"
    import re

    def chapters(book, wanted):
        return lambda tag: (m := re.search(book + r"\.(\d+)\.", tag)) is not None and int(m.group(1)) in wanted

    extra = [
        ("vergil.georgics.tess", "Virgil, Georgics", "verse", None),
        ("vergil.aeneid.tess", "Virgil, Aeneid", "verse", None),
        ("lucretius.de_rerum_natura.tess", "Lucretius, De rerum natura", "verse", None),
        ("ovid.fasti.tess", "Ovid, Fasti", "verse", None),
        ("wandalbertus.martyrologium.tess", "Wandalbert, Martyrology", "verse", None),
        ("jerome.vulgate/jerome.vulgate.part.4.numbers.tess", "Numbers 1-4, 7, 26 (lists)", "list", chapters("Numbers", {1, 2, 3, 4, 7, 26})),
        ("jerome.vulgate/jerome.vulgate.part.12.1_chronicles.tess", "1 Chronicles 1-9 (genealogies)", "list", chapters("Chronicles", set(range(1, 10)))),
        ("jerome.vulgate/jerome.vulgate.part.21.psalms.tess", "Psalms", "list", None),
        ("cato_the_elder.de_agricultura.tess", "Cato, De agricultura", "list", None),
    ]
    for fname, name, kind, sel in extra:
        p = tess / fname
        if p.exists():
            pages = cap_pages([[w for ln in pg for w in ln] for pg in pseudo_pages(tess_lines(p, sel))])
            sets.append((name, kind, pages, contiguous_groups(len(pages))))

    cremma = root / "HTR-United" / "CREMMA-Medieval-LAT"
    if cremma.exists():
        reg = pd.read_csv(cremma / "data-registry.csv")
        pages, groups = [], []
        for r in reg.itertuples():
            for pg in manuscript(cremma / r.Folder, True):
                pages.append([w for ln in pg for w in ln])
                groups.append(r.Folder)
        # manuscripts differ in subject and spelling, so score each on itself: hold out pages, not manuscripts
        sets.append(("21 Latin manuscripts, line-by-line transcription", "manuscript lines", pages, list(range(len(pages)))))

    rows = []
    for name, kind, pages, groups in sets:
        pages = [pg for pg in pages if pg]
        groups = groups[:len(pages)]
        if sum(len(pg) for pg in pages) < 3000:
            continue
        r = score(pages, groups)
        rows.append({"text": name, "class": kind, **r})
        print(f"{name[:50]:50s} {kind[:14]:14s} N={r['n_tokens']:6d} uni {r['bits_unigram']:5.2f} all {r['bits_all']:5.2f} | "
              f"grammar {r['gain_grammar']:+.3f} repeat {r['gain_repeat']:+.3f} vary {r['gain_vary']:+.3f} | "
              f"weights g {r['w_grammar']:.3f} r {r['w_repeat']:.3f} v {r['w_vary']:.3f}", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "v2_predictive_scores.csv", index=False)

    prof = df.groupby("class")[["gain_grammar", "gain_repeat", "gain_vary", "w_grammar", "w_repeat", "w_vary"]].agg(["min", "median", "max"])
    prof.to_csv(OUT / "v2_class_profile.csv")
    with pd.option_context("display.width", 250):
        print("\nby class:")
        print(df.groupby("class")[["gain_grammar", "gain_repeat", "gain_vary"]].agg(["min", "median", "max"]).round(3).to_string())

    # which class of control does each Voynich sample sit nearest to, in (grammar, repeat, vary) gain space?
    ctrl = df[df["class"] != "voynich"]
    feats = ["gain_grammar", "gain_repeat", "gain_vary"]
    sd = ctrl[feats].std().replace(0, 1)
    cent = ctrl.groupby("class")[feats].median()
    print("\nnearest control class (standardised distance to class medians):")
    for r in df[df["class"] == "voynich"].itertuples():
        d = (((cent - np.array([getattr(r, f) for f in feats])) / sd) ** 2).sum(1) ** 0.5
        print(f"  {r.text:24s} " + "  ".join(f"{k}: {v:.2f}" for k, v in d.sort_values().items()))
    # leave-one-out check that the same rule recovers the class of the controls themselves
    ok = 0
    for i, r in ctrl.iterrows():
        rest = ctrl.drop(i)
        c2 = rest.groupby("class")[feats].median()
        d = (((c2 - r[feats].values.astype(float)) / sd) ** 2).sum(1) ** 0.5
        ok += d.idxmin() == r["class"]
    print(f"leave-one-out accuracy of that rule on the controls: {ok}/{len(ctrl)}")


if __name__ == "__main__":
    main()
