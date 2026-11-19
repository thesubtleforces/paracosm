"""Parser for IVTFF transliteration files of Beinecke MS 408 (the Voynich manuscript).

IVTFF = "Intermediate Voynich MS Transliteration File Format" (R. Zandbergen, voynich.nu).
This module reads the single-transcriber files (ZL, IT, GC, CD, FG, RF, VT) and turns them into
two flat tables:

  pages  - one row per page (panel), with the page variables from the header
  tokens - one row per word token, with its position in page / paragraph / line

Markup handling (IVTFF 2.0, see data/SOURCES.md for the spec reference):

  <! ... >     free in-line comment                      -> removed
  <@H=n>       in-line change of a page variable         -> applied to following tokens
  <->          text interrupted by a drawing             -> word break, flag `after_break`
  <~>          left/right parts badly aligned            -> word break
  <%> / <$>    paragraph start / paragraph end           -> recorded, removed
  [a:b:c]      uncertain reading, most likely first      -> first option kept, flag `alt`
  {abc}        ligature                                  -> inner glyphs kept (apostrophes dropped)
  @nnn;        rare glyph outside the basic alphabet     -> one private-use codepoint, flag `rare`
  ?            unreadable glyph                          -> kept as '?', flag `unreadable`
  .            word space
  ,            uncertain word space                      -> configurable (default: a space)

Nothing here interprets the text; it only normalises the transcribers' notation.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Iterable

PAGE_RE = re.compile(r"^<(f(?:\d+[rv]\d*|Ros))>\s*(?:<!\s*(.*?)\s*>)?\s*$")
LOCUS_RE = re.compile(r"^<(f(?:\d+[rv]\d*|Ros))\.(\d+),(.)(..)(?:;(.))?>\s*(.*)$")
VAR_RE = re.compile(r"\$([A-Z])=(\S)")
INLINE_VAR_RE = re.compile(r"<@([A-Z])=(\S)>")
COMMENT_RE = re.compile(r"<![^>]*>")
ALT_RE = re.compile(r"\[([^\]]*)\]")
RARE_RE = re.compile(r"@(\d{3});")
FOLIO_RE = re.compile(r"^f(\d+)([rv])(\d*)$")

BREAK = "\x1f"      # drawing interruption inside a line

QUIRE_LETTERS = "ABCDEFGHIJKLMNOPQRST"
ILLUSTRATION = {
    "A": "astronomical", "B": "biological", "C": "cosmological", "H": "herbal",
    "P": "pharmaceutical", "S": "stars", "T": "text", "Z": "zodiac",
}


@dataclass
class Page:
    page: str
    seq: int                      # order of appearance in the file (= current binding order)
    folio: int | None = None
    side: str | None = None       # r / v
    panel: str = ""               # foldout panel number, '' for ordinary pages
    quire: int | None = None      # 1..20
    page_in_quire: str | None = None
    bifolio_pos: str | None = None   # $F: a,b,c.. first leaves; z,y,x.. their conjoints
    bifolio_num: str | None = None   # $B: 1 = outermost sheet of the quire
    illustration: str | None = None  # $I
    language: str | None = None      # $L: Currier A / B
    hand: str | None = None          # $H: scribe (Davis 2020 numbering in ZL 3b)
    currier_hand: str | None = None  # $C
    extraneous: str | None = None    # $X
    vars: dict = field(default_factory=dict)


@dataclass
class Token:
    page: str
    locus: int
    locator: str
    locus_type: str               # P0, Lz, Cc, ...
    generic: str                  # P / L / C / R
    line_on_page: int             # running index of loci on the page (0-based)
    para: int                     # running paragraph index on the page (-1 if not paragraph text)
    line_in_para: int             # 0-based line index inside the paragraph (-1 otherwise)
    idx: int                      # 0-based position in the line
    n_in_line: int
    token: str
    hand: str | None
    unreadable: bool
    rare: bool
    alt: bool
    after_break: bool
    uncertain_space_before: bool
    para_first_line: bool
    para_last_line: bool


def _rare(m: re.Match) -> str:
    return chr(0xE000 + int(m.group(1)))


def _first_alt(m: re.Match) -> str:
    inner = m.group(1)
    if ":" in inner:
        return "\x01" + inner.split(":")[0]
    # "[ao]" form: two single-glyph options without a colon
    return "\x01" + inner[:1]


def clean_text(raw: str) -> tuple[str, list[tuple[int, str, str]], bool, bool]:
    """Strip comments, resolve alternatives/ligatures.

    Returns (text, in-line variable changes, starts_paragraph, ends_paragraph); a change is
    (character offset in the text before glyph normalisation, variable, value)."""
    changes: list[tuple[int, str, str]] = []
    s = COMMENT_RE.sub("", raw).strip()
    starts_para, ends_para = "<%>" in s, "<$>" in s
    s = s.replace("<%>", "").replace("<$>", "")
    s = s.replace("<->", BREAK).replace("<~>", BREAK)
    # in-line variable changes: remember where they happen, then drop them
    out, pos = [], 0
    for m in INLINE_VAR_RE.finditer(s):
        out.append(s[pos:m.start()])
        changes.append((sum(len(x) for x in out), m.group(1), m.group(2)))
        pos = m.end()
    out.append(s[pos:])
    s = "".join(out)
    s = RARE_RE.sub(_rare, s)
    s = ALT_RE.sub(_first_alt, s)          # \x01 marks "came from an uncertain reading"
    s = s.replace("{", "").replace("}", "").replace("'", "")
    return s.strip(), changes, starts_para, ends_para


def parse(path: str | Path, comma_is_space: bool = True) -> tuple[list[Page], list[Token]]:
    pages: list[Page] = []
    tokens: list[Token] = []
    cur: Page | None = None
    line_on_page = 0
    para = -1
    line_in_para = -1
    in_para = False
    hand: str | None = None

    with open(path, encoding="latin-1") as fh:
        pending = ""
        for raw_line in fh:
            line = raw_line.rstrip("\n").rstrip("\r")
            if not line or line.startswith("#"):
                continue
            if line.startswith("/"):       # continuation of previous locus
                pending = pending.rstrip("/") + line.lstrip("/")
                continue
            m = PAGE_RE.match(line)
            if m and "." not in line.split(">")[0]:
                v = dict(VAR_RE.findall(m.group(2) or ""))
                fm = FOLIO_RE.match(m.group(1))
                cur = Page(
                    page=m.group(1), seq=len(pages),
                    folio=int(fm.group(1)) if fm else None,
                    side=fm.group(2) if fm else None,
                    panel=fm.group(3) if fm else "",
                    quire=(QUIRE_LETTERS.index(v["Q"]) + 1) if "Q" in v else None,
                    page_in_quire=v.get("P"), bifolio_pos=v.get("F"), bifolio_num=v.get("B"),
                    illustration=v.get("I"), language=v.get("L"), hand=v.get("H"),
                    currier_hand=v.get("C"), extraneous=v.get("X"), vars=v,
                )
                pages.append(cur)
                line_on_page, para, line_in_para, in_para = 0, -1, -1, False
                hand = cur.hand
                continue
            m = LOCUS_RE.match(line)
            if not m or cur is None:
                continue
            page, num, locator, ltype, _transcriber, text = m.groups()
            if page != cur.page:
                raise ValueError(f"locus {page}.{num} outside its page {cur.page}")
            text, changes, starts_para, ends_para = clean_text(text)
            generic = ltype[0]
            if generic == "P":
                # A paragraph starts at <%>; if the transcriber omitted it, a locator of '@' or '*'
                # (new unit / back at the left margin) also opens one.
                if starts_para or not in_para:
                    para += 1
                    line_in_para = 0
                    in_para = True
                else:
                    line_in_para += 1
                this_para, this_lip = para, line_in_para
            else:
                this_para, this_lip = -1, -1

            # split into words, remembering what separated them
            sep_pattern = r"([.,%s])" % BREAK if comma_is_space else r"([.%s])" % BREAK
            if not comma_is_space:
                text = text.replace(",", "")
            parts = re.split(sep_pattern, text)
            line_tokens: list[tuple[str, bool, bool, int]] = []
            offset = 0
            prev_sep = ""
            for part in parts:
                if part in (".", ",", BREAK):
                    prev_sep = BREAK if (part == BREAK or prev_sep == BREAK) else part
                    offset += len(part)
                    continue
                if part == "":
                    continue
                line_tokens.append((part, prev_sep == BREAK, prev_sep == ",", offset))
                offset += len(part)
                prev_sep = ""
            n = len(line_tokens)
            for i, (tok, after_break, unc_space, off) in enumerate(line_tokens):
                while changes and changes[0][0] <= off:
                    _, var, val = changes.pop(0)
                    if var == "H":
                        hand = val
                alt = "\x01" in tok
                tok = tok.replace("\x01", "")
                if not tok:
                    continue
                tokens.append(Token(
                    page=cur.page, locus=int(num), locator=locator, locus_type=ltype, generic=generic,
                    line_on_page=line_on_page, para=this_para, line_in_para=this_lip,
                    idx=i, n_in_line=n, token=tok, hand=hand,
                    unreadable="?" in tok,
                    rare=any(0xE000 <= ord(ch) < 0xE100 for ch in tok),
                    alt=alt, after_break=after_break, uncertain_space_before=unc_space,
                    para_first_line=(generic == "P" and this_lip == 0),
                    para_last_line=(generic == "P" and ends_para),
                ))
            if generic == "P" and ends_para:
                in_para = False
            line_on_page += 1
    return pages, tokens


def to_frames(pages: Iterable[Page], tokens: Iterable[Token]):
    """Return (pages_df, tokens_df) as pandas DataFrames with page metadata joined onto tokens."""
    import pandas as pd

    p = pd.DataFrame([{k: v for k, v in asdict(x).items() if k != "vars"} for x in pages])
    t = pd.DataFrame([asdict(x) for x in tokens])
    meta = p[["page", "seq", "folio", "side", "quire", "bifolio_num", "illustration", "language"]]
    t = t.merge(meta, on="page", how="left")
    t["clean"] = ~(t["unreadable"] | t["rare"])
    return p, t


if __name__ == "__main__":
    import sys

    pgs, toks = parse(sys.argv[1])
    print(f"{len(pgs)} pages, {len(toks)} tokens, {len({t.token for t in toks})} types")
    print(" ".join(t.token for t in toks[:10]))
