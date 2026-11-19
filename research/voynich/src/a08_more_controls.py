"""A08 - Validation: the control classes the first round lacked.

Round 1 compared the manuscript with continuous prose, one cipher and one generator. Three kinds of
meaningful text were missing, and each could in principle produce the manuscript's fingerprints
without any hoax:

  verse           lines are units by design (Virgil, Lucretius, Ovid's calendar poem, a verse herbal,
                  a verse martyrology)
  lists           formulaic, repetitive entries (census and offering lists of Numbers, genealogies of
                  Chronicles), and recipe prose (Cato)
  manuscript      21 real Latin manuscripts of the 11th-15th centuries transcribed line by line with
  lines           their abbreviations and line-end word breaks (CREMMA Medieval LAT), including
                  medical recipe collections and a late-medieval prayer book

Every text is put through the same measurements as before: glyph predictability, echo between
neighbouring words, line-edge behaviour, and resemblance to the word above. Line tests use only
line breaks that are native to the source.

Usage:  python -I src/a08_more_controls.py
Writes: results/tables/v1_more_controls.csv, results/tables/v1_class_summary.csv
"""
from __future__ import annotations

import random
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import corpora  # noqa: E402
import stats  # noqa: E402
from a03_line_effects import test as line_test  # noqa: E402
from a04_local_similarity import lag_counts, pseudo_pages, vertical_table, voynich_pages  # noqa: E402

OUT = corpora.PROJECT / "results" / "tables"
# letters, combining marks and the scribal signs that stand for whole words or syllables
MS_WORD = re.compile(r"(?:[^\W\d_]|[̀-ͯ᷀-᷿꜠-ꟿ⁊⹀-⹏])+")
LINE_BREAK_MARK = re.compile(r"[/\-¬=]\s*$")


def tess_lines(path: Path, select=None) -> list[list[str]]:
    """Tesserae file -> one token list per source unit (a verse line, a Bible verse, a chapter)."""
    out = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^<([^>]*)>\s*(.*)$", raw)
        if not m:
            continue
        if select and not select(m.group(1)):
            continue
        toks = corpora.normalise(m.group(2))
        if toks:
            out.append(toks)
    return out


def ms_tokens(line: str) -> list[str]:
    line = unicodedata.normalize("NFC", line.lower())
    return MS_WORD.findall(line)


def manuscript(folder: Path, rejoin: bool) -> list[list[list[str]]]:
    """A transcribed manuscript as pages -> lines -> tokens. With `rejoin`, a word broken across a
    line end is restored and counted on the line where it starts."""
    pages = []
    for f in sorted(folder.glob("*.txt")):
        lines, carry = [], None
        for raw in f.read_text(encoding="utf-8", errors="replace").splitlines():
            raw = raw.strip()
            if not raw:
                continue
            broken = bool(LINE_BREAK_MARK.search(raw))
            toks = ms_tokens(raw)
            if not toks:
                continue
            if rejoin and carry is not None and lines:
                lines[-1][-1] = lines[-1][-1] + toks[0]
                toks = toks[1:]
            carry = True if (rejoin and broken) else None
            if toks:
                lines.append(toks)
            elif carry:
                carry = None
        if lines:
            pages.append(lines)
    return pages


def measure(name: str, kind: str, pages: list[list[list[str]]], native: bool, rng: random.Random, note: str = "") -> dict:
    lines = [ln for pg in pages for ln in pg]
    toks = [w for ln in lines for w in ln]
    row = {"text": name, "class": kind, "native_lines": native, "words": len(toks), "lines": len(lines), "note": note}
    h1, h2 = stats.char_entropies(toks[:10000])
    row["h2"] = h2
    row["mean_word_len"] = float(np.mean([len(w) for w in toks]))

    flat = [[w for ln in pg for w in ln] for pg in pages]
    near = stats.neighbor_map(toks)
    e, c, tot = lag_counts(flat, near)
    se = np.zeros_like(e)
    sc = np.zeros_like(c)
    n_sh = 30
    for _ in range(n_sh):
        e2, c2, _ = lag_counts([stats.shuffled(pg, rng) for pg in flat], near)
        se += e2
        sc += c2
    se /= n_sh
    sc /= n_sh
    row["near_lag1"] = c[1] / sc[1] if sc[1] else np.nan
    row["near_lag2_6"] = c[2:7].sum() / sc[2:7].sum() if sc[2:7].sum() else np.nan
    row["exact_lag1"] = e[1] / se[1] if se[1] else np.nan
    row["exact_lag1_pct"] = 100 * e[1] / tot[1]

    if native:
        lt = line_test(lines, rng, n_perm=200)
        for k in ("n_lines", "jsd_first", "jsd_first_z", "jsd_last", "jsd_last_z", "first_len", "first_len_z", "last_len", "last_len_z"):
            row[k] = lt[k]
        vt = vertical_table(name, kind, pages, rng, n_null=200)
        v0 = vt[vt.offset == 0].iloc[0]
        row["above_ratio"], row["above_z"] = v0.ratio, v0.z
    return row


def subsample_lines(pages, n_lines, rng):
    """A random set of whole pages holding about n_lines lines (for size-matched comparisons)."""
    idx = list(range(len(pages)))
    rng.shuffle(idx)
    out, total = [], 0
    for i in idx:
        out.append(pages[i])
        total += len(pages[i])
        if total >= n_lines:
            break
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(8)
    root = corpora.default_root()
    tess = root / "tesserae" / "tesserae" / "texts" / "la"
    vul = tess / "jerome.vulgate"
    rows = []

    v_all = voynich_pages("all")
    rows.append(measure("Voynich manuscript (ZL)", "voynich", v_all, True, rng))
    rows.append(measure("Voynich, Currier A", "voynich", voynich_pages("A"), True, rng))
    rows.append(measure("Voynich, Currier B", "voynich", voynich_pages("B"), True, rng))

    def add_tess(fname, name, kind, select=None, cap=None, note=""):
        p = tess / fname
        if not p.exists():
            print("missing", p)
            return
        lines = tess_lines(p, select)
        if cap:
            lines = lines[:cap]
        rows.append(measure(name, kind, pseudo_pages(lines), True, rng, note))

    # verse: the line is the unit of composition
    add_tess("vergil.georgics.tess", "Virgil, Georgics", "verse", note="didactic verse on farming")
    add_tess("vergil.aeneid.tess", "Virgil, Aeneid 1-4", "verse", cap=3000)
    add_tess("lucretius.de_rerum_natura.tess", "Lucretius, De rerum natura 1-3", "verse", cap=3400)
    add_tess("ovid.fasti.tess", "Ovid, Fasti", "verse", note="a calendar in verse")
    add_tess("wandalbertus.martyrologium.tess", "Wandalbert, Martyrology", "verse", note="9th-c. verse calendar of saints")
    add_tess("walafrid_strabo.de_cultu_hortorum_carmen.tess", "Walafrid Strabo, Hortulus", "verse", note="9th-c. verse herbal; short")

    # lists and formulaic prose: one Bible verse or one chapter per unit
    def chapters(book, wanted):
        return lambda tag: (m := re.search(book + r"\.(\d+)\.", tag)) is not None and int(m.group(1)) in wanted

    add_tess(str(Path("jerome.vulgate") / "jerome.vulgate.part.4.numbers.tess"), "Numbers 1-4, 7, 26 (census and offering lists)", "list",
             chapters("Numbers", {1, 2, 3, 4, 7, 26}), note="highly formulaic lists")
    add_tess(str(Path("jerome.vulgate") / "jerome.vulgate.part.12.1_chronicles.tess"), "1 Chronicles 1-9 (genealogies)", "list",
             chapters("Chronicles", set(range(1, 10))), note="name lists")
    add_tess(str(Path("jerome.vulgate") / "jerome.vulgate.part.21.psalms.tess"), "Psalms", "list", cap=2400, note="parallel verse units with refrains")
    add_tess("cato_the_elder.de_agricultura.tess", "Cato, De agricultura (recipes and instructions)", "list", note="units are short chapters")
    del vul

    # real manuscripts, line by line
    cremma = root / "HTR-United" / "CREMMA-Medieval-LAT"
    reg = pd.read_csv(cremma / "data-registry.csv")
    pooled_raw, pooled_joined = [], []
    for r in reg.itertuples():
        folder = cremma / r.Folder
        if not folder.exists():
            continue
        for label, rejoin, pool in (("as written", False, pooled_raw), ("words rejoined", True, pooled_joined)):
            pages = manuscript(folder, rejoin)
            pool += pages
            n_lines = sum(len(p) for p in pages)
            if n_lines >= 250 and not rejoin:
                rows.append(measure(f"MS {r._1} ({r.Type} {r.notBefore}-{r.notAfter})", "manuscript lines", pages, True, rng,
                                    str(r.Content)[:80]))
    rows.append(measure("21 Latin manuscripts pooled, as written", "manuscript lines", pooled_raw, True, rng,
                        "line-end word fragments counted as words"))
    rows.append(measure("21 Latin manuscripts pooled, broken words rejoined", "manuscript lines", pooled_joined, True, rng,
                        "the fairer comparison: Voynich words are not visibly broken at line ends"))

    df = pd.DataFrame(rows)

    # size-matched reference: how big would the Voynich z-scores be with only as many lines as each control has?
    ref = []
    for n in sorted({int(x) for x in df[df["class"] != "voynich"].lines.dropna()}):
        if n >= 4000:
            continue
        zs = []
        for _ in range(5):
            sub = subsample_lines(v_all, n, rng)
            lt = line_test([ln for pg in sub for ln in pg], rng, n_perm=100)
            zs.append((lt["jsd_first_z"], lt["jsd_last_z"], lt["jsd_first"], lt["jsd_last"]))
        z = np.mean(zs, axis=0)
        ref.append({"lines": n, "voynich_jsd_first_z": z[0], "voynich_jsd_last_z": z[1]})
    ref = pd.DataFrame(ref)
    df = df.merge(ref, on="lines", how="left")
    df.to_csv(OUT / "v1_more_controls.csv", index=False)

    show = ["text", "class", "words", "lines", "h2", "near_lag1", "near_lag2_6", "exact_lag1", "jsd_first", "jsd_first_z",
            "voynich_jsd_first_z", "jsd_last", "jsd_last_z", "above_ratio", "above_z"]
    with pd.option_context("display.width", 280, "display.max_colwidth", 46):
        print(df[show].round(3).to_string(index=False))

    summ = df.groupby("class").agg(
        texts=("text", "count"), h2_min=("h2", "min"), h2_max=("h2", "max"),
        near1_min=("near_lag1", "min"), near1_max=("near_lag1", "max"),
        exact1_min=("exact_lag1", "min"), exact1_max=("exact_lag1", "max"),
        jsd_first_min=("jsd_first", "min"), jsd_first_max=("jsd_first", "max"),
        jsd_last_min=("jsd_last", "min"), jsd_last_max=("jsd_last", "max"),
        above_min=("above_ratio", "min"), above_max=("above_ratio", "max"),
    )
    summ.to_csv(OUT / "v1_class_summary.csv")
    with pd.option_context("display.width", 280):
        print("\nby class (min-max):")
        print(summ.round(3).to_string())


if __name__ == "__main__":
    main()
