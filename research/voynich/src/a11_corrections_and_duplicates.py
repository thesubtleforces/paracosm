"""A11 - Validation: two small checks that need no new data.

1. Corrections. How often did the scribes visibly fix something? Copying a meaningful text from an
   exemplar leaves characteristic slips and fixes; improvising text leaves few. A real census needs
   the photographs. Here we only count what the ZL transcribers flagged in passing (possible
   corrections, erasures, glyphs written above the line), which is a lower bound.

2. Duplicate drawings. The Landini-Stolfi file (1998) records, independently of any hypothesis
   here, that the plant on f39r is drawn again on f95r2, and that one plant on f89v1 and one on
   f102v2 have similar roots and the "same" label. If the text refers to what is drawn, pages that
   show the same plant should share words, and the same thing should carry the same label.

Usage:  python -I src/a11_corrections_and_duplicates.py
Writes: results/tables/v4_corrections.json, results/tables/v5_duplicates.json
"""
from __future__ import annotations

import itertools
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import corpora  # noqa: E402
from a06_bifolio_order import LSA, tfidf_cosine  # noqa: E402

OUT = corpora.PROJECT / "results" / "tables"


def corrections() -> dict:
    meta = pd.read_csv(corpora.PROJECT / "data" / "derived" / "pages.csv", dtype={"hand": str})
    hand = dict(zip(meta.page, meta.hand))
    flags = Counter()
    by_scribe = Counter()
    pages = set()
    kinds = {"corr?": "possible correction", "erased?": "possible erasure", "above": "glyph written above the line",
             "subscript": "glyph written below the line"}
    for line in open(corpora.ZL, encoding="latin-1"):
        m = re.match(r"^<(f[^.>]+)\.\d+,", line)
        if not m:
            continue
        for c in re.findall(r"<!([^>]*)>", line):
            for key, name in kinds.items():
                if key in c and not re.match(r"^\d", c):
                    flags[name] += 1
                    by_scribe[hand.get(m.group(1), "?")] += 1
                    pages.add(m.group(1))
    _, t = corpora.voynich_frames()
    words = len(t)
    words_by = t.groupby("hand").size().to_dict()
    total = sum(flags.values())
    return {
        "source": "in-line notes in the ZL 3b transliteration; a lower bound, not a census",
        "flags": dict(flags), "total": total, "pages_with_a_flag": len(pages), "pages": int(len(meta)),
        "words": int(words), "words_per_flag": round(words / total) if total else None,
        "per_10000_words_by_scribe": {k: round(10000 * by_scribe[k] / words_by[k], 1) for k in sorted(words_by)},
        "uncertain_readings_marked_by_transcribers": int(t.alt.sum()),
    }


def duplicates() -> dict:
    _, t = corpora.voynich_frames()
    meta = pd.read_csv(corpora.PROJECT / "data" / "derived" / "pages.csv", dtype={"hand": str})
    hand = dict(zip(meta.page, meta.hand))
    ill = dict(zip(meta.page, meta.illustration))
    sheet = dict(zip(meta.page, meta.bifolio))
    lang = dict(zip(meta.page, meta.language))
    ntok = dict(zip(meta.page, meta.n_tokens))
    lsa = LSA(t)
    cos = tfidf_cosine(t)
    clean = t[t.clean]
    freq = Counter(clean.token)
    out = {}

    # --- the same plant drawn twice: f39r and f95r2
    a, b = "f39r", "f95r2"
    wa = set(clean[(clean.page == a)].token)
    wb = set(clean[(clean.page == b)].token)
    shared = sorted(wa & wb, key=lambda w: freq[w])
    res = {"pages": [a, b], "scribes": [hand[a], hand[b]], "languages": [lang[a], lang[b]], "words": [int(ntok[a]), int(ntok[b])],
           "shared_word_forms": len(shared), "shared_forms_rarest_first": [f"{w} ({freq[w]})" for w in shared[:12]]}
    for name, f in (("lsa", lsa.sim), ("tfidf", cos)):
        s = f(a, b)
        # reference: f39r against every other herbal page by f95r2's scribe, and the reverse
        ref = [f(a, x) for x in meta.page if x not in (a, b) and ill[x] == "H" and hand[x] == hand[b] and ntok[x] >= 40]
        ref += [f(b, x) for x in meta.page if x not in (a, b) and ill[x] == "H" and hand[x] == hand[a] and ntok[x] >= 40 and sheet[x] != sheet[b]]
        ref = np.array([v for v in ref if not np.isnan(v)])
        res[name] = {"similarity": round(float(s), 3), "reference_pairs": int(len(ref)), "reference_median": round(float(np.median(ref)), 3),
                     "percentile": round(float((ref < s).mean() * 100), 1)}
    out["same_plant_f39r_f95r2"] = res

    # --- labels shared between pharmaceutical pages
    lab = clean[(clean.generic == "L") & (clean.locus_type != "Lx") & (clean.token.str.len() >= 3)]
    pharma = [pg for pg in meta.page if ill[pg] == "P"]
    labs = {pg: set(lab[lab.page == pg].token) for pg in pharma}
    labs = {pg: s for pg, s in labs.items() if len(s) >= 3}
    pair_shared = {(x, y): labs[x] & labs[y] for x, y in itertools.combinations(sorted(labs), 2)}
    n_pairs = len(pair_shared)
    with_any = sum(1 for s in pair_shared.values() if s)
    target = pair_shared.get(("f102v2", "f89v1")) or pair_shared.get(("f89v1", "f102v2")) or set()
    out["labels_shared_between_pharmaceutical_pages"] = {
        "pages_with_labels": len(labs), "label_forms": int(sum(len(s) for s in labs.values())),
        "page_pairs": n_pairs, "pairs_sharing_any_label": with_any,
        "share_of_pairs": round(with_any / n_pairs, 3),
        "f89v1_and_f102v2_share": sorted(target),
        "frequency_of_those_forms_in_whole_text": {w: int(freq[w]) for w in sorted(target)},
        "all_shared": {f"{x}+{y}": sorted(s) for (x, y), s in pair_shared.items() if s},
    }

    # --- a pharmaceutical plant said to resemble the herbal page f93r
    l101 = sorted(labs.get("f101v", lab[lab.page == "f101v"].token))
    t93 = set(clean[(clean.page == "f93r") & (clean.generic == "P")].token)
    out["f101v_labels_in_f93r_text"] = {"f101v_labels": l101, "found_in_f93r_text": sorted(set(l101) & t93)}
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    c = corrections()
    (OUT / "v4_corrections.json").write_text(json.dumps(c, indent=1))
    print(json.dumps(c, indent=1))
    d = duplicates()
    (OUT / "v5_duplicates.json").write_text(json.dumps(d, indent=1))
    print(json.dumps(d, indent=1)[:3500])


if __name__ == "__main__":
    main()
