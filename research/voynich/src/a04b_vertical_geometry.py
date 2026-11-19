"""A04b - Vertical copying test with real word positions on the page.

Uses word bounding boxes (The Voynichese Project 2014, Apache-2.0, as fitted to Yale's photographs by
the Voynich Viewer project) together with the voynichese.com transliteration (VT) they index.
For every word in a paragraph line we ask whether the words in the line directly above that
overlap it horizontally are more similar to it (identical or one edit apart) than the other words
of that same upper line. The null permutes the interior words of the upper line among its boxes.

Lines whose word count differs between boxes and transliteration are skipped.

Usage:  python -I src/a04b_vertical_geometry.py [boxes_dir]
Writes: results/tables/vertical_geometry.csv
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import corpora  # noqa: E402
import ivtff  # noqa: E402
import stats  # noqa: E402

OUT = corpora.PROJECT / "results" / "tables"
BINS = [0, 0.5, 1.5, 2.5, 3.5, 5.5, 99]          # |horizontal centre distance| in median word widths
LABELS = ["<0.5", "0.5-1.5", "1.5-2.5", "2.5-3.5", "3.5-5.5", ">5.5"]


def load(boxes_dir: Path):
    pages, toks = ivtff.parse(corpora.PROJECT / "data" / "transliterations" / "VT0e-n.txt")
    p, t = ivtff.to_frames(pages, toks)
    pairs = []          # (page, language, upper[(word, cx, w)], lower[...])
    skipped = used = 0
    for page, g in t.groupby("page", sort=False):
        f = boxes_dir / f"{page}.json"
        if not f.exists():
            continue
        by_line: dict[int, list] = {}
        for rec in json.load(open(f))["words"]:
            ln, wi, x, y, w, h = rec[:6]
            img = rec[6] if len(rec) > 6 else 0      # foldouts are photographed in several images
            # offset other images far to the right so their words never count as "above"
            by_line.setdefault(ln, []).append((wi, x + 100000 * img, y, w, h))
        lines = {}
        for ln, lg in g.groupby("line_on_page"):
            bx = sorted(by_line.get(ln, []))
            if lg.generic.iloc[0] != "P" or len(bx) != len(lg):
                skipped += 1
                continue
            used += 1
            lines[ln] = [(tok, x + w / 2, w, y + h / 2, ok) for tok, ok, (_, x, y, w, h) in zip(lg.token, lg.clean, bx)]
        lang = g.language.iloc[0]
        for ln in sorted(lines):
            if ln + 1 in lines and len(lines[ln]) >= 5 and len(lines[ln + 1]) >= 5:
                up, lo = lines[ln], lines[ln + 1]
                dy = np.median([b[3] for b in lo]) - np.median([b[3] for b in up])
                if dy <= 0:        # not physically below (e.g. a new column or block)
                    continue
                pairs.append((page, lang, up, lo))
    print(f"lines used {used}, skipped {skipped}; consecutive line pairs {len(pairs)}")
    return pairs


def tally(pairs, near, rng: random.Random | None):
    hit = np.zeros(len(LABELS))
    tot = np.zeros(len(LABELS))
    for _, _, up, lo in pairs:
        up_core = up[1:-1]
        words = [u[0] for u in up_core]
        if rng is not None:
            rng.shuffle(words)
        med_w = np.median([b[2] for b in up + lo])
        for a, cx, _, _, ok in lo[1:-1]:
            if not ok:
                continue
            na = near.get(a, ())
            for b_word, (_, ucx, _, _, uok) in zip(words, up_core):
                d = abs(cx - ucx) / med_w
                if d > 60:          # the two words are on different photographs of a foldout
                    continue
                k = min(np.searchsorted(BINS, d, side="right") - 1, len(LABELS) - 1)
                tot[k] += 1
                if a == b_word or b_word in na:
                    hit[k] += 1
    return hit, tot


def main(boxes_dir: Path) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    pairs = load(boxes_dir)
    near = stats.neighbor_map(w[0] for _, _, up, lo in pairs for w in up + lo)
    rng = random.Random(44)
    rows = []
    for label, sel in [("all", pairs), ("A", [x for x in pairs if x[1] == "A"]), ("B", [x for x in pairs if x[1] == "B"])]:
        hit, tot = tally(sel, near, None)
        null = []
        for _ in range(500):
            h, t = tally(sel, near, rng)
            null.append(h / t)
        null = np.array(null)
        for k, name in enumerate(LABELS):
            p = hit[k] / tot[k]
            mu, sd = null[:, k].mean(), null[:, k].std()
            rows.append({"subset": label, "distance_bin": name, "pairs": int(tot[k]), "p_match": p,
                         "p_null": mu, "ratio": p / mu, "z": (p - mu) / sd})
        # one pre-specified contrast: words within 1.5 word-widths horizontally vs. the rest
        near_obs = hit[:2].sum() / tot[:2].sum()
        far_obs = hit[2:].sum() / tot[2:].sum()
        null_hits = null * tot                      # back to counts per permutation
        contrast_null = null_hits[:, :2].sum(1) / tot[:2].sum() - null_hits[:, 2:].sum(1) / tot[2:].sum()
        obs = near_obs - far_obs
        rows.append({"subset": label, "distance_bin": "contrast: <1.5 minus >=1.5", "pairs": int(tot.sum()),
                     "p_match": near_obs, "p_null": far_obs, "ratio": near_obs / far_obs,
                     "z": (obs - contrast_null.mean()) / contrast_null.std()})
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "vertical_geometry.csv", index=False)
    print(df.round(4).to_string(index=False))


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else corpora.default_root() / "writtenbyalina" / "voynichviewer" / "data" / "text" / "boxes")
