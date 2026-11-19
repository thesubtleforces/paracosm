"""A01 - Build the derived page table and corpus summary from the ZL transliteration.

Usage:  python -I src/a01_build_corpus.py [codex.json from the Voynich Viewer project, optional cross-check]
Writes: data/derived/pages.csv, data/derived/tokens.csv.gz, results/tables/corpus_summary.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pandas as pd  # noqa: E402

import corpora  # noqa: E402

DER = corpora.PROJECT / "data" / "derived"
OUT = corpora.PROJECT / "results" / "tables"
SECOND_LEAF = {"z": "a", "y": "b", "x": "c", "w": "d", "v": "e", "u": "f"}


def build() -> tuple[pd.DataFrame, pd.DataFrame]:
    p, t = corpora.voynich_frames()
    p = p.copy()
    # bifolium id: quire + sheet number counted from the outside of the quire ($B)
    p["bifolio"] = p.apply(lambda r: f"Q{int(r.quire):02d}-{r.bifolio_num}" if pd.notna(r.quire) else None, axis=1)
    p["leaf_half"] = p.bifolio_pos.map(lambda x: None if pd.isna(x) else ("second" if x in SECOND_LEAF else "first"))
    n_all = t.groupby("page").size().rename("n_tokens")
    n_par = t[t.generic == "P"].groupby("page").size().rename("n_paragraph_tokens")
    n_lab = t[t.generic == "L"].groupby("page").size().rename("n_label_tokens")
    p = p.join(n_all, on="page").join(n_par, on="page").join(n_lab, on="page").fillna(
        {"n_tokens": 0, "n_paragraph_tokens": 0, "n_label_tokens": 0})
    for c in ("n_tokens", "n_paragraph_tokens", "n_label_tokens"):
        p[c] = p[c].astype(int)
    return p, t


def main() -> None:
    DER.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    p, t = build()
    p.to_csv(DER / "pages.csv", index=False)
    t.to_csv(DER / "tokens.csv.gz", index=False, compression="gzip")

    clean = t[t.clean]
    summary = {
        "source": "ZL transliteration v3b (13 May 2025), EVA, uncertain spaces counted as spaces",
        "pages": int(len(p)),
        "folios_extant": int(p.folio.nunique()),
        "tokens": int(len(t)),
        "tokens_clean": int(len(clean)),
        "types_clean": int(clean.token.nunique()),
        "hapax_types": int((clean.token.value_counts() == 1).sum()),
        "tokens_by_locus_kind": {k: int(v) for k, v in t.groupby("generic").size().items()},
        "paragraphs": int(t[t.generic == "P"].groupby("page").para.nunique().sum()),
        "paragraph_lines": int(t[t.generic == "P"].groupby(["page", "line_on_page"]).ngroups),
        "tokens_by_language": {str(k): int(v) for k, v in t.groupby("language", dropna=False).size().items()},
        "tokens_by_scribe": {str(k): int(v) for k, v in t.groupby("hand").size().items()},
        "tokens_by_illustration": {str(k): int(v) for k, v in t.groupby("illustration").size().items()},
        "pages_by_illustration": {str(k): int(v) for k, v in p.groupby("illustration").size().items()},
        "pages_by_scribe": {str(k): int(v) for k, v in p.groupby("hand").size().items()},
        "top20": clean.token.value_counts().head(20).to_dict(),
    }
    (OUT / "corpus_summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps({k: v for k, v in summary.items() if k != "top20"}, indent=1))

    # which scribes share a bifolium? (Davis: with two exceptions every bifolium is single-scribe)
    by = p.dropna(subset=["bifolio"]).groupby("bifolio").hand.agg(lambda s: "".join(sorted(set(s))))
    mixed = by[by.str.len() > 1]
    print(f"\nbifolia: {len(by)}; single-scribe: {(by.str.len() == 1).sum()}; mixed: {dict(mixed)}")
    print("mixed bifolia pages:", p[p.bifolio.isin(mixed.index)][["page", "bifolio", "hand"]].values.tolist())

    codex_path = Path(sys.argv[1]) if len(sys.argv) > 1 else corpora.default_root() / "writtenbyalina" / "voynichviewer" / "data" / "codex.json"
    if codex_path.exists():
        codex = json.load(open(codex_path))
        dav = {}
        for sh in codex["sheets"]:
            for side in ("inside", "outside"):
                for leaf in sh.get(side, []):
                    for pg in leaf or []:
                        dav[pg["page"]] = "".join(str(x) for x in pg.get("scribes") or [])
        diff = [(r.page, r.hand, dav.get(r.page)) for r in p.itertuples()
                if r.page in dav and dav[r.page] and dav[r.page] != r.hand]
        print(f"\ncross-check of scribe attribution, ZL $H vs Voynich Viewer codex (Davis): "
              f"{sum(1 for r in p.itertuples() if dav.get(r.page))} pages compared, {len(diff)} differ: {diff[:12]}")


if __name__ == "__main__":
    main()
