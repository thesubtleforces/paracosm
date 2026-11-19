"""Build the origin-story page ("Five Hands") from its template and the result tables.

Numbers quoted in the story come from the same tables as the report, so the narrative cannot
drift from the analysis. Markers {{name}} are filled from the report's facts plus the few
story-specific ones computed here; {{img:name}} embeds report/img/name.jpg.

Usage:  python -I src/build_story.py
Writes: report/five-hands.html
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pandas as pd  # noqa: E402

import corpora  # noqa: E402
from build_dossier import REPORT, T, esc, facts, img, load  # noqa: E402


def story_facts() -> dict:
    f, _ = facts(load())
    meta = pd.read_csv(corpora.PROJECT / "data" / "derived" / "pages.csv", dtype={"hand": str})
    by_page = meta[meta.hand.isin(list("12345"))].groupby("hand").size()
    by_sheet = meta.dropna(subset=["bifolio"]).groupby("bifolio").hand.first().value_counts()
    for h in "12345":
        f[f"pages_{h}"] = str(int(by_page.get(h, 0)))
        f[f"sheets_{h}"] = str(int(by_sheet.get(h, 0)))
    f["n_sheets"] = str(int(meta.bifolio.nunique()))
    f["herbal_median"] = f"{meta[meta.illustration == 'H'].n_tokens.median():.0f}"
    _, t = corpora.voynich_frames()
    s = t[(t.illustration == "S") & (t.generic == "P")]
    f["stars_paras"] = str(int(s.groupby("page").para.nunique().sum()))
    f["stars_pages"] = str(int(meta[meta.illustration == "S"].page.nunique()))
    z = t[(t.illustration == "Z") & (t.locus_type == "Lz")]
    f["zodiac_labels"] = str(int(z.groupby("page").locus.nunique().sum()))
    wp = json.loads((T / "word_parts.json").read_text())
    f["parts_cov"] = f"{100 * wp['coverage']:.0f}%"
    f["parts_attested"] = str(wp["attested"])
    f["parts_possible"] = str(wp["possible"])
    f["parts_n"] = f"{len(wp['starts'])}, {len(wp['mids'])} and {len(wp['ends'])}"
    pal = json.loads((T / "page_palette.json").read_text())
    for k, v in pal.items():
        f[f"pal_{k}"] = v
    return f, wp


def word_grid(wp: dict) -> str:
    """Counts of words built from a beginning (row) and an ending (column); brighter = more."""
    ends = wp["ends"]
    rows = wp["order"][:9]
    top = max(max(wp["rows"][r].values()) for r in rows)
    head = '<th scope="col" class="corner">begins / ends</th>' + "".join(f'<th scope="col">-{esc(e)}</th>' for e in ends)
    body = ""
    for r in rows:
        cells = ""
        for e in ends:
            c = wp["rows"][r].get(e, 0)
            if not c:
                cells += '<td class="zero">·</td>'
                continue
            a = 0.10 + 0.70 * (c / top) ** 0.5     # square-root ramp, so rare words stay visible
            cls = ' class="hi"' if a >= 0.5 else ""
            tip = esc(f"{r}{e}: written {c:,} times")
            cells += f'<td{cls} style="--a:{a:.2f}" data-tip="{tip}">{c:,}</td>'
        body += f'<tr><th scope="row">{esc(r) + "-" if r else "(none)"}</th>{cells}</tr>'
    return ('<div class="scroll"><table class="grid"><caption class="mono" style="caption-side:top;text-align:left;'
            'font-size:.72rem;color:var(--soft);padding-bottom:.6rem">Words by their beginning and ending, counts in '
            f'{wp["n_tokens"]:,} words of running text</caption><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')


def pair_bars() -> str:
    """Excess likeness of page pairs on one sheet, over same-scribe same-gathering pages (all nine gatherings, LSA)."""
    d = pd.read_csv(T / "lsa_pair_types.csv")
    r = d[(d.section == "all nine quires") & (d.measure == "lsa")].iloc[0]
    rows = [
        ("0110", "The two pages that lie open together", r.conjoint_minus_baseline, int(r.conjoint_n)),
        ("1100", "Two sides of one leaf", r.confoliate_minus_baseline, int(r.confoliate_n)),
        ("1010", "One page apart on the sheet", r.diagonal_minus_baseline, int(r.diagonal_n)),
        ("1001", "The first and last pages of the sheet", r.outer_minus_baseline, int(r.outer_n)),
        (None, "Facing pages that sit on different sheets", r.facing_minus_baseline, int(r.facing_same_scribe_n)),
    ]
    top = 0.16
    out = ""
    for code, label, v, n in rows:
        if code:
            pp = '<span class="pp" aria-hidden="true">' + "".join(f'<b{" class=\"on\"" if ch == "1" else ""}></b>' for ch in code) + "</span>"
        else:
            pp = '<span class="pp far" aria-hidden="true"><b></b><b></b></span>'
        w = max(0.0, 100 * v / top)
        shown = f"{v:+.3f}".replace("-", "\u2212")
        out += (f'<div class="bar" data-tip="{esc(label)}: {shown} ({n} pairs)">{pp}<span class="lab">{esc(label)}</span>'
                f'<span class="val">{shown}</span><span class="track"><i style="width:{w:.1f}%"></i></span></div>')
    return f'<div class="bars" role="img" aria-label="Bar chart of excess likeness for five kinds of page pair">{out}</div>'


def main() -> None:
    f, wp = story_facts()
    blocks = {"word_grid": word_grid(wp), "pair_bars": pair_bars()}
    tpl = (REPORT / "story.template.html").read_text(encoding="utf-8")
    missing = []

    def fill(m: re.Match) -> str:
        key = m.group(1)
        if key.startswith("img:"):
            return img(key[4:])
        if key in blocks:
            return blocks[key]
        if key in f:
            return esc(f[key])
        missing.append(key)
        return m.group(0)

    page = re.sub(r"\{\{([a-zA-Z0-9_:]+)\}\}", fill, tpl)
    if missing:
        raise SystemExit(f"unknown markers in template: {sorted(set(missing))}")
    (REPORT / "five-hands.html").write_text(page, encoding="utf-8")
    print(f"wrote report/five-hands.html ({len(page) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
