"""A12 - Two small tables used by the origin-story page.

1. Word parts. How much of the running text is covered by words of the form
   beginning + middle + ending, for a short hand-picked list of each. This is a description of the
   most frequent word shapes, not a grammar: the lists were chosen by eye from the frequency table
   and the result says only how far so small a set reaches.

2. Page palette. Nine colours taken from the page photographs by fixed hue, saturation and
   lightness windows over a fixed set of pages (median of the pixels in each window). Used as the
   colour card for the film treatment.

Usage:  python -I src/a12_story_tables.py [panels_dir]
Writes: results/tables/word_parts.json, results/tables/page_palette.json (the second only if the
        page images are present; see fetch_sources.sh --images)
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import corpora  # noqa: E402

OUT = corpora.PROJECT / "results" / "tables"
STARTS = ["", "o", "qo", "ch", "sh", "d", "y", "l"]
MIDS = ["", "k", "t"]
ENDS = ["y", "dy", "edy", "eedy", "ey", "eey", "aiin", "ain", "ol", "or", "al", "ar", "am"]
PALETTE_PAGES = ["f2r", "f9v", "f17r", "f33v", "f34r", "f47v", "f71r", "f75r", "f78v", "f88r", "f99r", "f102v2"]
# name -> (hue lo, hue hi in degrees; saturation lo, hi; lightness (HSV value) lo, hi)
WINDOWS = {
    "parchment": ((20, 50), (0.10, 0.32), (0.72, 0.90)),
    "parchment_shadow": ((20, 50), (0.14, 0.36), (0.55, 0.70)),
    "ink": ((10, 45), (0.25, 0.60), (0.20, 0.38)),
    "ink_faded": ((10, 45), (0.25, 0.50), (0.40, 0.52)),
    "blue": ((185, 250), (0.25, 1.0), (0.25, 0.60)),
    "green": ((130, 175), (0.22, 1.0), (0.30, 0.62)),
    "green_yellow": ((62, 110), (0.30, 1.0), (0.25, 0.50)),
    "red": ((0, 16), (0.45, 1.0), (0.45, 0.80)),
    "ochre": ((24, 38), (0.42, 0.75), (0.50, 0.70)),
}


def word_parts() -> dict:
    _, t = corpora.voynich_frames()
    run = t[(t.generic == "P") & t.clean]
    counts = Counter(run.token)
    n = int(sum(counts.values()))

    def table(mids):
        cells = {}
        covered = set()
        for s in STARTS:
            for m in mids:
                for e in ENDS:
                    w = s + m + e
                    c = counts.get(w, 0)
                    if c:
                        cells[(s + m, e)] = c
                        covered.add(w)
        return cells, sum(counts[w] for w in covered)

    cells, cov = table(MIDS)
    rows: dict[str, dict[str, int]] = {}
    for (head, e), c in cells.items():
        rows.setdefault(head, {})[e] = c
    order = sorted(rows, key=lambda h: -sum(rows[h].values()))
    return {
        "starts": STARTS, "mids": MIDS, "ends": ENDS,
        "n_tokens": n, "coverage": cov / n,
        "attested": len({h + e for h, e in cells}),
        "possible": len({s + m + e for s in STARTS for m in MIDS for e in ENDS}),
        "rows": {h: {e: rows[h][e] for e in ENDS if e in rows[h]} for h in order},
        "order": order[:12],
        "note": "attested and possible count distinct words; dy can be built two ways (d+y, or the ending dy alone) and is shown in both cells",
    }


def palette(panels: Path) -> dict:
    from PIL import Image

    px, hs = [], []
    for page in PALETTE_PAGES:
        f = panels / f"{page}_l.jpg"
        if not f.exists():
            continue
        im = Image.open(f).convert("RGB")
        im = im.resize((im.width // 2, im.height // 2), Image.BOX)
        px.append(np.asarray(im, dtype=float).reshape(-1, 3) / 255)
        hs.append(np.asarray(im.convert("HSV"), dtype=float).reshape(-1, 3) / 255)
    if not px:
        return {}
    rgb = np.vstack(px)
    hsv = np.vstack(hs)
    out = {}
    for name, ((h0, h1), (s0, s1), (v0, v1)) in WINDOWS.items():
        m = (hsv[:, 0] * 360 >= h0) & (hsv[:, 0] * 360 <= h1) & (hsv[:, 1] >= s0) & (hsv[:, 1] <= s1) & (hsv[:, 2] >= v0) & (hsv[:, 2] <= v1)
        if m.sum() < 30:
            continue
        r, g, b = (np.median(rgb[m], axis=0) * 255).round().astype(int)
        out[name] = f"#{r:02x}{g:02x}{b:02x}"
        print(f"{name:17s} {out[name]}  from {int(m.sum()):6d} pixels")
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    wp = word_parts()
    (OUT / "word_parts.json").write_text(json.dumps(wp, indent=1))
    print(f"word parts: {wp['attested']} of {wp['possible']} combinations occur; they cover {100 * wp['coverage']:.1f}% of {wp['n_tokens']:,} running words")
    panels = Path(sys.argv[1]) if len(sys.argv) > 1 else corpora.default_root() / "writtenbyalina" / "voynichviewer" / "data" / "panels"
    pal = palette(panels) if panels.exists() else {}
    if pal:
        (OUT / "page_palette.json").write_text(json.dumps(pal, indent=1))
    else:
        print("page images not found; page_palette.json left as it is")


if __name__ == "__main__":
    main()
