"""A07 - Do labels and opening words behave like names?

If the short words written next to drawings are names of the things drawn, and the running text on
the same page discusses those things, labels should recur in their own page's text more often than
in the text of other pages of the same section. Local copying would predict the same thing, so a
positive result is necessary for the "names" reading but not sufficient.

Also tested: are paragraph-opening words special lexical items (e.g. plant names), or ordinary
words wearing an added first glyph?

Usage:  python -I src/a07_labels.py
Writes: results/tables/label_binding.csv, results/tables/label_summary.json
"""
from __future__ import annotations

import json
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
SAMPLE = 80          # running-text tokens drawn from every page, so page length cannot drive the result
N_DRAWS = 200


def main() -> None:
    rng = random.Random(7)
    _, t = corpora.voynich_frames()
    t = t[t.clean]
    lab = t[(t.generic == "L") & (t.locus_type != "Lx") & (t.token.str.len() >= 3)]
    run = t[t.generic.isin(["P", "C", "R"])]
    run_tokens = {pg: list(g.token) for pg, g in run.groupby("page")}
    sect = dict(zip(t.page, t.illustration))
    hand = dict(zip(t.page, t.hand))

    rows = []
    for pg, g in lab.groupby("page"):
        labels = sorted(set(g.token))
        own = run_tokens.get(pg, [])
        if len(labels) < 4 or len(own) < SAMPLE:
            continue
        others = [q for q, toks in run_tokens.items()
                  if q != pg and sect[q] == sect[pg] and hand[q] == hand[pg] and len(toks) >= SAMPLE]
        if len(others) < 2:
            continue
        own_rate, other_rate = [], []
        for _ in range(N_DRAWS):
            s = set(rng.sample(own, SAMPLE))
            own_rate.append(np.mean([w in s for w in labels]))
            q = rng.choice(others)
            s2 = set(rng.sample(run_tokens[q], SAMPLE))
            other_rate.append(np.mean([w in s2 for w in labels]))
        rows.append({"page": pg, "section": sect[pg], "scribe": hand[pg], "n_label_types": len(labels),
                     "own_page_rate": float(np.mean(own_rate)), "other_page_rate": float(np.mean(other_rate)),
                     "n_other_pages": len(others)})
    b = pd.DataFrame(rows)
    b.to_csv(OUT / "label_binding.csv", index=False)
    diff = (b.own_page_rate - b.other_page_rate).values
    lo, hi = stats.bootstrap_ci(diff, seed=3)
    print(f"label binding: {len(b)} pages with >=4 label types and >={SAMPLE} running tokens")
    print(f"  share of a page's labels found in {SAMPLE} random tokens of its own text : {b.own_page_rate.mean():.3f}")
    print(f"  ... of another page, same section and scribe                         : {b.other_page_rate.mean():.3f}")
    print(f"  difference {diff.mean():+.3f} [95% CI {lo:+.3f}, {hi:+.3f}]; pages with own > other: {(diff > 0).sum()}/{len(diff)}")
    print(b.groupby("section")[["own_page_rate", "other_page_rate", "n_label_types"]].mean().round(3).to_string())

    # ---- label vocabulary against running text
    run_types = Counter(run.token)
    all_types = Counter(t.token)
    lab_tok = lab.token
    summary = {
        "label_tokens": int(len(lab_tok)),
        "label_types": int(lab_tok.nunique()),
        "share_of_label_types_never_in_running_text": float(np.mean([w not in run_types for w in set(lab_tok)])),
        "share_of_label_types_unique_in_whole_manuscript": float(np.mean([all_types[w] == 1 for w in set(lab_tok)])),
        "share_of_running_types_unique_in_whole_manuscript(len>=3)": float(np.mean(
            [all_types[w] == 1 for w in run_types if len(w) >= 3])),
        "labels_first_glyph": {k: round(v / len(lab_tok), 3) for k, v in Counter(w[0] for w in lab_tok).most_common(6)},
        "running_first_glyph": {k: round(v / len(run), 3) for k, v in Counter(w[0] for w in run.token).most_common(6)},
        "label_binding_pages": int(len(b)),
        "label_binding_own": float(b.own_page_rate.mean()),
        "label_binding_other": float(b.other_page_rate.mean()),
        "label_binding_diff_ci": [float(diff.mean()), lo, hi],
    }

    # ---- paragraph-opening words: names, or ordinary words with a prefixed gallows?
    par = t[t.generic == "P"]
    opening = par[(par.para_first_line) & (par.idx == 0)].token
    line_first = par[(~par.para_first_line) & (par.idx == 0)].token
    mid = par[(par.idx > 0) & (par.idx < par.n_in_line - 1)].token
    types = set(all_types)

    def describe(words) -> dict:
        w = [x for x in words if len(x) >= 3]
        return {
            "n": len(w),
            "unique_in_manuscript": float(np.mean([all_types[x] == 1 for x in w])),
            "without_first_glyph_is_a_known_word": float(np.mean([x[1:] in types for x in w])),
            "unique_but_known_once_first_glyph_dropped": float(np.mean(
                [all_types[x] == 1 and x[1:] in types for x in w])),
        }

    summary["paragraph_opening_words"] = describe(opening)
    summary["other_line_first_words"] = describe(line_first)
    summary["mid_line_words"] = describe(mid)
    herbal_first = par[(par.illustration == "H") & (par.para == 0) & (par.line_in_para == 0) & (par.idx == 0)].token
    summary["herbal_page_first_word"] = describe(herbal_first)
    (OUT / "label_summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
