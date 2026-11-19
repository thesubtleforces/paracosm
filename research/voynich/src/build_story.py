"""Build the origin-story page ("Five Hands") from its template and the result tables.

Numbers quoted in the story come from the same tables as the report, so the narrative cannot
drift from the analysis. Markers {{name}} are filled from the report's facts plus the few
story-specific ones computed here; {{img:name}} embeds report/img/name.jpg.

Usage:  python -I src/build_story.py
Writes: report/five-hands.html, and report/five-hands.md as a plain reading copy
"""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
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
    mp = json.loads((T / "measure_plates.json").read_text())
    f["mp_parts_hit"] = str(mp["parts"]["built_from_stock_parts"])
    f["mp_parts_n"] = str(mp["parts"]["words_in_frame"])
    f["mp_echo_same"] = str(mp["echo"]["identical_neighbours"])
    f["mp_echo_near"] = str(mp["echo"]["one_glyph_apart"])
    f["mp_echo_n"] = str(mp["echo"]["words_in_frame"])
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


class Markdown(HTMLParser):
    """A plain reading copy of the page for the repository. Handles only the tags the template uses."""

    BLOCK = {"p", "h1", "h2", "h3", "h4", "figcaption", "dt", "dd", "summary", "caption"}
    SKIP = {"style", "script", "title", "svg"}
    VOID = {"img", "br", "meta", "link", "hr", "input"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self.buf: list[str] = []
        self.skip = 0
        self.lists: list[list] = []        # [kind, counter]
        self.items: list[list] = []        # per open <li>: [marker written yet?, indent width]
        self.table: list[list[str]] | None = None
        self.row: list[str] | None = None
        self.prefix = ""                   # a scene number waiting for its heading
        self.closers: list[str] = []

    # -- helpers
    def text(self) -> str:
        t = re.sub(r"\s+", " ", "".join(self.buf)).strip()
        self.buf = []
        return t

    def emit(self, line: str) -> None:
        if not line:
            return
        if self.items:
            pad = " " * sum(w for _, w in self.items[:-1])
            if not self.items[-1][0]:
                kind, n = self.lists[-1]
                marker = f"{n}. " if kind == "ol" else "- "
                self.items[-1] = [True, len(marker)]
                self.out.append(pad + marker + line)
            else:
                self.out.append("")
                self.out.append(pad + " " * self.items[-1][1] + line)
        else:
            self.out.extend(["", line])

    # -- parser events
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class") or ""
        if self.skip or tag in self.SKIP or "contents" in cls.split():
            if tag == "svg" and not self.skip and a.get("aria-label"):
                self.emit(f"*[{a['aria-label']}]*")
            self.skip += 1
            self.closers.append("skip")
            return
        if tag in self.VOID:
            if tag == "img":
                self.emit(self.text())
                self.emit(f"![{a.get('alt', '')}]({a.get('src', '')})")
            return
        closer = ""
        if tag in self.BLOCK or tag in ("li", "tr", "table", "ul", "ol") or "bar" in cls.split():
            self.emit(self.text())
        if tag in ("ul", "ol"):
            if not self.items:
                self.out.append("")
            self.lists.append([tag, 0])
        elif tag == "li":
            self.lists[-1][1] += 1
            self.items.append([False, 2])
        elif tag == "table":
            self.table = []
        elif tag == "tr":
            self.row = []
        elif tag in ("em", "i") and tag != "i" or (tag == "i" and not a.get("style")):
            self.buf.append("*")
            closer = "*"
        elif tag in ("b", "strong") and "on" not in cls:
            self.buf.append("**")
            closer = "**"
        elif tag == "a" and a.get("href"):
            self.buf.append("[")
            closer = f"]({a['href']})"
        elif tag == "span" and "tag" in cls.split():
            self.buf.append("**")
            closer = ".** "
        elif tag == "span" and "kind" in cls.split():
            self.buf.append("*")
            closer = ".* "
        elif tag == "span" and ("no" in cls.split() or "lab" in cls.split()):
            closer = " \u00b7 "
        elif tag == "div" and a.get("role") == "img" and a.get("aria-label") and "bars" not in cls.split():
            self.emit(f"*[{a['aria-label']}]*")
        self.closers.append(closer if closer else tag)

    def handle_endtag(self, tag):
        if tag in self.VOID or not self.closers:
            return
        closer = self.closers.pop()
        if closer == "skip":
            self.skip -= 1
            return
        if closer not in (tag,):
            self.buf.append(closer + (" " if tag in ("b", "strong", "span") else ""))
            if tag == "span" and closer == " \u00b7 " and not self.items and self.table is None:
                # a scene number: hold it for the heading that follows
                held = self.text()
                if held.lower().startswith("scene"):
                    self.prefix = held + " "
                else:
                    self.buf.append(held + " ")
            return
        if tag in ("span", "b"):
            self.buf.append(" ")
        elif tag in ("td", "th"):
            if self.row is not None:
                self.row.append(self.text().replace("|", "/"))
        elif tag == "tr":
            if self.table is not None and self.row is not None:
                self.table.append(self.row)
            self.row = None
        elif tag == "table":
            rows = self.table or []
            self.table = None
            if rows:
                width = max(len(r) for r in rows)
                rows = [r + [""] * (width - len(r)) for r in rows]
                self.out.append("")
                self.out.append("| " + " | ".join(rows[0]) + " |")
                self.out.append("|" + "---|" * width)
                self.out.extend("| " + " | ".join(r) + " |" for r in rows[1:])
        elif tag in ("h1", "h2", "h3", "h4"):
            t = self.text()
            if t:
                self.out.extend(["", "#" * int(tag[1]) + " " + self.prefix + t])
                self.prefix = ""
        elif tag == "dt":
            t = self.text()
            self.emit(f"**{t}**" if t else "")
        elif tag in self.BLOCK or tag == "div":
            self.emit(self.text())
        elif tag == "li":
            self.emit(self.text())
            self.items.pop()
        elif tag in ("ul", "ol"):
            self.lists.pop()
            if not self.items:
                self.out.append("")

    def handle_data(self, data):
        if not self.skip:
            self.buf.append(data)

    def result(self) -> str:
        self.emit(self.text())
        md = "\n".join(self.out)
        md = re.sub(r" +([.,;:)])", r"\1", md)          # spaces left by closed inline marks
        md = re.sub(r"\n{3,}", "\n\n", md).strip()
        return md + "\n"


def to_markdown(html: str) -> str:
    m = Markdown()
    m.feed(html)
    return m.result()


def main() -> None:
    f, wp = story_facts()
    blocks = {"word_grid": word_grid(wp), "pair_bars": pair_bars()}
    tpl = (REPORT / "story.template.html").read_text(encoding="utf-8")
    missing = []

    def filler(embed: bool):
        def fill(m: re.Match) -> str:
            key = m.group(1)
            if key.startswith("img:"):
                return img(key[4:]) if embed else f"img/{key[4:]}.jpg"
            if key in blocks:
                return blocks[key]
            if key in f:
                return esc(f[key])
            missing.append(key)
            return m.group(0)
        return fill

    marker = re.compile(r"\{\{([a-zA-Z0-9_:]+)\}\}")
    page = marker.sub(filler(True), tpl)
    if missing:
        raise SystemExit(f"unknown markers in template: {sorted(set(missing))}")
    (REPORT / "five-hands.html").write_text(page, encoding="utf-8")
    print(f"wrote report/five-hands.html ({len(page) / 1024:.0f} KB)")
    note = ("<!-- Reading copy of five-hands.html, written by src/build_story.py. Edit report/story.template.html, not this file. -->\n\n")
    md = note + to_markdown(marker.sub(filler(False), tpl))
    (REPORT / "five-hands.md").write_text(md, encoding="utf-8")
    print(f"wrote report/five-hands.md ({len(md.split()):,} words)")


if __name__ == "__main__":
    main()
