"""Build the report page from the result tables.

Every number and chart in report/voynich-dossier.html comes from results/tables/* (or is computed
here from the parsed text), so the prose cannot drift from the analysis. The page's wording lives
in report/dossier.template.html; markers of the form {{name}} are filled from FACTS / CHARTS, and
the build fails if a marker is unknown or left unfilled.

Usage:  python -I src/build_dossier.py
Writes: report/voynich-dossier.html, results/tables/calibration_matrix.csv
"""
from __future__ import annotations

import base64
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import corpora  # noqa: E402

ROOT = corpora.PROJECT
T = ROOT / "results" / "tables"
REPORT = ROOT / "report"
esc = html.escape


# --------------------------------------------------------------------------------------- data

def load() -> dict:
    d = {
        "base": pd.read_csv(T / "baselines.csv"),
        "alpha": pd.read_csv(T / "alphabet_sensitivity.csv"),
        "lag": pd.read_csv(T / "lag_similarity.csv"),
        "line": pd.read_csv(T / "line_effects.csv"),
        "edge": pd.read_csv(T / "line_edge_glyphs.csv"),
        "vert": pd.read_csv(T / "vertical_alignment.csv"),
        "geom": pd.read_csv(T / "vertical_geometry.csv"),
        "pairs": pd.read_csv(T / "lsa_pair_scores.csv"),
        "ptypes": pd.read_csv(T / "lsa_pair_types.csv"),
        "quire": pd.read_csv(T / "lsa_quire_averages.csv"),
        "reorder": pd.read_csv(T / "lsa_reorder.csv"),
        "svs": pd.read_csv(T / "scribe_vs_section.csv"),
        "labels": json.loads((T / "label_summary.json").read_text()),
        "corpus": json.loads((T / "corpus_summary.json").read_text()),
    }
    return d


GROUPS = [("voynich", "Voynich manuscript"), ("natural", "Natural languages"),
          ("cipher", "Naibbe cipher"), ("algo_gibberish", "Copy-and-modify generator")]


def rng_txt(vals, fmt="{:.2f}", sep="–") -> str:
    lo, hi = min(vals), max(vals)
    a, b = fmt.format(lo), fmt.format(hi)
    return a if a == b else f"{a}{sep}{b}"


def signed_range(vals, fmt="{:+.2f}") -> str:
    lo, hi = min(vals), max(vals)
    a, b = fmt.format(lo), fmt.format(hi)
    return a if a == b else f"{a} to {b}"


# --------------------------------------------------------------------------------------- facts

def facts(d: dict) -> tuple[dict, pd.DataFrame]:
    f: dict[str, str] = {}
    c = d["corpus"]
    f["n_pages"] = f"{c['pages']}"
    f["n_folios"] = f"{c['folios_extant']}"
    f["n_tokens"] = f"{c['tokens']:,}"
    f["n_tokens_clean"] = f"{c['tokens_clean']:,}"
    f["n_types"] = f"{c['types_clean']:,}"
    f["n_hapax"] = f"{c['hapax_types']:,}"
    f["hapax_pct"] = f"{100 * c['hapax_types'] / c['types_clean']:.0f}%"
    f["n_paragraphs"] = f"{c['paragraphs']}"
    f["n_lines"] = f"{c['paragraph_lines']:,}"
    for k, v in c["pages_by_illustration"].items():
        f[f"pages_{k}"] = str(v)
    f["pages_AC"] = str(c["pages_by_illustration"]["A"] + c["pages_by_illustration"]["C"])
    for k, v in c["tokens_by_scribe"].items():
        f[f"tokens_s{k}"] = f"{v:,}"
    top = list(c["top20"].items())
    f["top1"], f["top1_n"] = top[0][0], str(top[0][1])
    f["top2"], f["top2_n"] = top[1][0], str(top[1][1])
    f["top_ratio"] = f"{top[0][1] / top[1][1]:.1f}"

    b = d["base"]
    voy = b[b.corpus == "Voynich all"].iloc[0]
    nat = b[b.kind == "natural"]
    cip = b[b.kind == "cipher"]
    gen = b[b.kind == "algo_gibberish"]
    f["h2_voy"] = f"{voy.h2_char:.2f}"
    f["h2_nat"] = rng_txt(nat.h2_char)
    f["h2_nat_lo"] = f"{nat.h2_char.min():.1f}"
    f["h2_nat_hi"] = f"{nat.h2_char.max():.1f}"
    f["h2_cip"] = rng_txt(cip.h2_char)
    f["h2_gen"] = rng_txt(gen.h2_char)
    f["n_nat"] = str(len(nat))
    a = d["alpha"].groupby("transliteration").h2_char.mean()
    f["h2_merged"] = f"{a['EVA, strokes merged into glyphs']:.2f}"
    f["h2_currier"] = f"{a['Currier (CD 2a, partial)']:.2f}"
    f["h2_v101"] = f"{a['v101 (Claston GC 2a)']:.2f}"
    f["rep_voy"] = f"{100 * voy.repeat_exact:.2f}%"
    f["rep_voy_shuf"] = f"{100 * voy.repeat_exact_shuffled:.2f}%"
    f["rep_voy_x"] = f"{voy.repeat_exact / voy.repeat_exact_shuffled:.1f}"
    f["rep_nat"] = rng_txt(100 * nat.repeat_exact, "{:.2f}") + "%"
    f["rep_cip"] = rng_txt(100 * cip.repeat_exact, "{:.2f}") + "%"
    f["lenac_voy"] = f"{voy.len_autocorr:+.2f}"
    f["lenac_nat_neg"] = str(int((nat.len_autocorr < 0).sum()))

    # neighbour similarity, pooled into distance bands
    lag = d["lag"].copy()
    lag["group"] = [("voynich" if n == "Voynich all" else None) if k == "voynich" else k
                    for n, k in zip(lag.corpus, lag.kind)]
    lag = lag.dropna(subset=["group"])
    bands = [("1", 1, 1), ("2–3", 2, 3), ("4–6", 4, 6), ("7–12", 7, 12), ("13–24", 13, 24), ("25–40", 25, 40)]
    rows = []
    for name, lo, hi in bands:
        sub = lag[(lag.lag >= lo) & (lag.lag <= hi)]
        per = sub.groupby(["group", "corpus"]).apply(
            lambda x: pd.Series({"near": x.p_near.mean() / x.p_near_shuffled.mean(),
                                 "exact": x.p_exact.mean() / x.p_exact_shuffled.mean()}), include_groups=False).reset_index()
        for g, gg in per.groupby("group"):
            rows.append({"band": name, "group": g, "mean": gg.near.mean(), "min": gg.near.min(), "max": gg.near.max(),
                         "exact_mean": gg.exact.mean(), "exact_min": gg.exact.min(), "exact_max": gg.exact.max(), "n": len(gg)})
    lagb = pd.DataFrame(rows)
    d["lagb"] = lagb
    g1 = lagb[lagb.band == "1"].set_index("group")
    f["near1_voy"] = f"{g1.loc['voynich', 'mean']:.2f}"
    f["near1_voy_pct"] = f"{100 * (g1.loc['voynich', 'mean'] - 1):.0f}%"
    f["near1_nat"] = rng_txt([g1.loc["natural", "min"], g1.loc["natural", "max"]])
    f["near1_cip"] = rng_txt([g1.loc["cipher", "min"], g1.loc["cipher", "max"]])
    f["near1_gen"] = rng_txt([g1.loc["algo_gibberish", "min"], g1.loc["algo_gibberish", "max"]])
    f["n_nat_lag"] = str(int(g1.loc["natural", "n"]))
    f["exact1_voy"] = f"{g1.loc['voynich', 'exact_mean']:.2f}"
    f["exact1_nat"] = rng_txt([g1.loc["natural", "exact_min"], g1.loc["natural", "exact_max"]])
    f["exact1_cip"] = rng_txt([g1.loc["cipher", "exact_min"], g1.loc["cipher", "exact_max"]])
    f["exact1_gen"] = rng_txt([g1.loc["algo_gibberish", "exact_min"], g1.loc["algo_gibberish", "exact_max"]])

    # line effects
    ln = d["line"]
    lv = ln[ln.corpus == "Voynich all"].iloc[0]
    lnat, lcip, lgen = ln[ln.kind == "natural"], ln[ln.kind == "cipher"], ln[ln.kind == "algo_gibberish"]
    f["line_z_first"] = f"{lv.jsd_first_z:.0f}"
    f["line_z_last"] = f"{lv.jsd_last_z:.0f}"
    f["line_first_len"] = f"{lv.first_len:+.2f}"
    allz_nat = pd.concat([lnat.jsd_first_z, lnat.jsd_last_z, lnat.first_len_z, lnat.last_len_z]).abs().max()
    f["line_nat_maxz"] = f"{allz_nat:.1f}"
    f["line_nat_z"] = signed_range(lnat.jsd_first_z, "{:+.1f}")
    f["line_cip_z"] = signed_range(lcip.jsd_first_z, "{:+.1f}")
    f["line_gen_z"] = signed_range(lgen.jsd_first_z, "{:+.0f}")
    e = d["edge"]

    def edge(where, g):
        r = e[(e["where"].str.startswith(where)) & (e.glyph == g)].iloc[0]
        return r

    for where, g in [("line-first", "p"), ("line-first", "t"), ("line-first", "y"), ("line-last", "m"), ("line-last", "g")]:
        r = edge(where, g)
        key = f"edge_{g}"
        f[key + "_at"] = f"{100 * r.share_at_edge:.1f}%"
        f[key + "_else"] = f"{100 * r.share_elsewhere:.1f}%" if r.share_elsewhere >= 0.001 else f"{100 * r.share_elsewhere:.2f}%"
        f[key + "_x"] = f"{r.ratio:.0f}"

    _, t = corpora.voynich_frames()
    p = t[(t.generic == "P") & t.clean]
    pf = p.token.str.contains("[pf]")
    f["pf_first"] = f"{100 * pf[p.para_first_line].mean():.0f}%"
    f["pf_other"] = f"{100 * pf[~p.para_first_line].mean():.1f}%"
    opening = p[(p.para_first_line) & (p.idx == 0)].token
    f["gallows_open"] = f"{100 * opening.str.match('[ptkf]').mean():.0f}%"
    f["gallows_all"] = f"{100 * p.token.str.match('[ptkf]').mean():.0f}%"

    # vertical
    gm = d["geom"]
    con = gm[(gm.subset == "all") & gm.distance_bin.str.startswith("contrast")].iloc[0]
    f["geo_near"] = f"{100 * con.p_match:.2f}%"
    f["geo_far"] = f"{100 * con.p_null:.2f}%"
    f["geo_pct"] = f"{100 * (con.ratio - 1):.0f}%"
    f["geo_z"] = f"{con.z:.1f}"
    v = d["vert"]
    v0 = v[v.offset == 0]
    vv = v0[v0.corpus == "Voynich all"].iloc[0]
    f["vert_voy"] = f"{100 * (vv.ratio - 1):.0f}%"
    f["vert_voy_x"] = f"{vv.ratio:.2f}"
    f["vert_voy_z"] = f"{vv.z:.1f}"
    vn = v0[v0.kind == "natural"]
    f["vert_nat"] = rng_txt(vn.ratio)
    f["vert_nat_maxz"] = f"{vn.z.abs().max():.1f}"
    f["vert_cip"] = rng_txt(v0[v0.kind == "cipher"].ratio)
    f["vert_gen"] = rng_txt(v0[v0.kind == "algo_gibberish"].ratio)
    f["vert_gen_max_pct"] = f"{100 * (v0[v0.kind == 'algo_gibberish'].ratio.max() - 1):.0f}%"

    # sheets
    q = d["quire"].set_index("quire")
    ov = q.loc["overall (mean of pairs)"]
    f["lsa_conf"], f["lsa_face"], f["lsa_conj"] = (f"{ov[k]:.3f}" for k in ("confoliate", "facing", "conjoint"))
    pr = d["pairs"]
    fc = pr[pr.type == "facing"]
    f["face_same"] = f"{fc[fc.same_scribe].lsa.mean():.2f}"
    f["face_diff"] = f"{fc[~fc.same_scribe].lsa.mean():.2f}"
    f["face_diff_n"] = str(int((~fc.same_scribe).sum()))
    f["face_n"] = str(len(fc))
    fh = fc[fc.quire <= 7]
    f["face_h_diff_n"] = str(int((~fh.same_scribe).sum()))
    f["face_h_n"] = str(len(fh))
    f["face_h_same"] = f"{fh[fh.same_scribe].lsa.mean():.2f}"
    f["face_h_diff"] = f"{fh[~fh.same_scribe].lsa.mean():.2f}"
    pt = d["ptypes"]
    allq = pt[(pt.section == "all nine quires") & (pt.measure == "lsa")].iloc[0]
    f["ex_conj"] = f"{allq.conjoint_minus_baseline:+.3f}"
    f["ex_conj_ci"] = f"{allq.ci95_lo:+.3f} to {allq.ci95_hi:+.3f}"
    f["ex_face"] = f"{allq.facing_minus_baseline:+.3f}"
    for sec, key in [("herbal quires 1-7", "h"), ("quire 13 (balneological)", "q13"), ("quire 20 (starred paragraphs)", "q20")]:
        r = pt[(pt.section == sec) & (pt.measure == "lsa")].iloc[0]
        f[f"ex_conj_{key}"] = f"{r.conjoint_minus_baseline:+.2f}"
    ro = d["reorder"]
    for qn in (13, 20):
        rq = ro[ro.quire == qn]
        f[f"ro{qn}_best"] = f"{float(rq[rq['rank'] == '1'].score.iloc[0]):.3f}"
        f[f"ro{qn}_seq"] = rq[rq["rank"] == "1"].sequence.iloc[0]
        s = rq[rq["rank"] == "all orders"].sequence.iloc[0]
        f[f"ro{qn}_p"] = re.search(r"= ([0-9.]+)$", s).group(1)
        f[f"ro{qn}_null"] = re.search(r"median ([0-9.]+)", s).group(1)
        f[f"ro{qn}_bound"] = re.search(r"as bound ([0-9.]+)", s).group(1)
        f[f"ro{qn}_pct"] = f"{100 * float(f[f'ro{qn}_p']):.0f}%"

    # scribe vs subject
    sv = d["svs"]
    scribe = sv[sv.contrast.str.contains("other scribe")]
    subj = sv[sv.contrast.str.contains("other subject")]
    ab = scribe[scribe.cells.str.contains("S1")]
    f["scribe_keep"] = rng_txt(100 * ab.between_over_within, "{:.0f}") + "%"
    f["subject_keep"] = rng_txt(100 * subj.between_over_within, "{:.0f}") + "%"
    f["s2s3_keep"] = f"{100 * scribe[scribe.cells == 'S2 herbal | S3 herbal'].between_over_within.iloc[0]:.0f}%"
    lang = t[t.clean & t.generic.isin(["P", "C", "R"])]
    for L in ("A", "B"):
        f[f"ed_{L}"] = f"{100 * lang[lang.language == L].token.str.contains('ed').mean():.1f}%"

    # labels
    L = d["labels"]
    f["lab_types"] = f"{L['label_types']}"
    f["lab_tokens"] = f"{L['label_tokens']:,}"
    f["lab_o"] = f"{100 * L['labels_first_glyph']['o']:.0f}%"
    f["run_o"] = f"{100 * L['running_first_glyph']['o']:.0f}%"
    f["lab_never"] = f"{100 * L['share_of_label_types_never_in_running_text']:.0f}%"
    f["lab_own"] = f"{100 * L['label_binding_own']:.1f}%"
    f["lab_other"] = f"{100 * L['label_binding_other']:.1f}%"
    dm, lo, hi = L["label_binding_diff_ci"]
    f["lab_diff"] = f"{100 * dm:+.1f}"
    f["lab_ci"] = f"{100 * lo:+.1f} to {100 * hi:+.1f}"
    f["lab_pages"] = str(L["label_binding_pages"])
    po, mid = L["paragraph_opening_words"], L["mid_line_words"]
    f["open_unique"] = f"{100 * po['unique_in_manuscript']:.0f}%"
    f["mid_unique"] = f"{100 * mid['unique_in_manuscript']:.0f}%"
    f["open_known"] = f"{100 * po['without_first_glyph_is_a_known_word']:.0f}%"
    f["mid_known"] = f"{100 * mid['without_first_glyph_is_a_known_word']:.0f}%"
    f["linefirst_known"] = f"{100 * L['other_line_first_words']['without_first_glyph_is_a_known_word']:.0f}%"

    # calibration matrix: which measurements separate the known-answer controls?
    def row(label, voy_v, nat_v, cip_v, gen_v, note):
        return {"measurement": label, "Voynich": voy_v, "Natural languages": nat_v, "Naibbe cipher": cip_v,
                "Copy-and-modify generator": gen_v, "separates": note}

    cal = pd.DataFrame([
        row("Glyph predictability (bits per glyph given the previous one)", f["h2_voy"], f["h2_nat"], f["h2_cip"], f["h2_gen"],
            "languages from the rest"),
        row("Next word is a one-glyph variant of this one (× chance)", f["near1_voy"], f["near1_nat"], f["near1_cip"], f["near1_gen"],
            "generator from cipher and languages"),
        row("Next word is identical (× chance within the page)", f["exact1_voy"], f["exact1_nat"], f["exact1_cip"], f["exact1_gen"],
            "languages and cipher sit far below; generator in between; none reaches the manuscript"),
        row("Word-length correlation between neighbours", f"{voy.len_autocorr:+.2f}", signed_range(nat.len_autocorr),
            signed_range(cip.len_autocorr), signed_range(gen.len_autocorr), "no control group matches the manuscript"),
        row("Line-start words differ from the rest (z-score)", f"+{f['line_z_first']}", f["line_nat_z"], f["line_cip_z"], f["line_gen_z"],
            "generator from cipher and languages"),
        row("Word matches the word above it (× chance)", f["vert_voy_x"], f["vert_nat"], f["vert_cip"], f["vert_gen"],
            "weakly, generator from the rest"),
    ])
    cal.to_csv(T / "calibration_matrix.csv", index=False)
    return f, cal


# --------------------------------------------------------------------------------------- charts

def table_view(df: pd.DataFrame, caption: str) -> str:
    head = "".join(f"<th>{esc(str(c))}</th>" for c in df.columns)
    body = "".join("<tr>" + "".join(f"<td>{esc(str(v))}</td>" for v in r) + "</tr>" for r in df.itertuples(index=False))
    return (f'<details class="tableview"><summary>Show the numbers</summary><div class="scroll"><table class="data">'
            f'<caption>{esc(caption)}</caption><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></details>')


def chart_h2(d: dict) -> str:
    b = d["base"].copy()
    lo, hi = 1.6, 3.6
    pos = lambda v: 100 * (v - lo) / (hi - lo)
    names = {"voynich": ("Voynich manuscript", "whole text, two dialects, three scribes"),
             "natural": ("Natural languages", f"{(b.kind == 'natural').sum()} texts, six languages"),
             "cipher": ("Naibbe cipher", "Latin underneath"),
             "algo_gibberish": ("Copy-and-modify generator", "meaningless by construction")}
    ticks = (2.0, 2.5, 3.0, 3.5)
    grid = "".join(f'<span class="st-grid" style="left:{pos(t):.2f}%"></span>' for t in ticks)
    out = ['<div class="strip">']
    for kind, (name, sub) in names.items():
        g = b[b.kind == kind].sort_values("h2_char")
        placed: list[tuple[float, float]] = []
        dots = []
        for r in g.itertuples():
            x = pos(r.h2_char) / 100 * 300          # beeswarm solved for a narrow (300px) track: wider only spreads it
            for dy in (0, -11, 11, -22, 22):
                if all((x - px) ** 2 + (dy - py) ** 2 >= 11.5 ** 2 for px, py in placed):
                    break
            placed.append((x, dy))
            cls = "s1" if kind == "voynich" else "ctx"
            dots.append(f'<span class="st-dot {cls} hit" tabindex="0" style="left:{pos(r.h2_char):.2f}%;margin-top:{dy}px" '
                        f'data-v="{r.h2_char:.2f} bits" data-tip="{esc(r.corpus)}"></span>')
        lo_v, hi_v = g.h2_char.min(), g.h2_char.max()
        label = f"{lo_v:.2f}–{hi_v:.2f}" if hi_v - lo_v >= 0.005 else f"{lo_v:.2f}"
        out.append(f'<div class="st-row"><span class="st-label">{esc(name)}<small>{esc(sub)}</small></span>'
                   f'<div class="st-track">{grid}{"".join(dots)}</div><span class="st-val">{label}</span></div>')
    out.append('<div class="st-axis" aria-hidden="true"><span></span><div class="st-scale">'
               + "".join(f'<i style="left:{pos(t):.2f}%">{t:.1f}</i>' for t in ticks) + "</div><span></span></div>")
    out.append('<div class="st-axis"><span></span><div class="st-title">bits per glyph, given the glyph before it (lower = more predictable)</div><span></span></div>')
    out.append("</div>")
    tv = b[b.kind.isin(names)][["corpus", "kind", "h2_char", "mean_word_len", "n_windows"]].copy()
    tv["kind"] = tv.kind.map(dict(GROUPS))
    tv["h2_char"] = tv.h2_char.map("{:.2f}".format)
    tv["mean_word_len"] = tv.mean_word_len.map("{:.2f}".format)
    tv.columns = ["Text", "Kind", "Bits per glyph", "Mean word length", "10,000-word windows"]
    return "".join(out) + table_view(tv, "Conditional glyph entropy, averaged over windows of 10,000 words")


def chart_lag(d: dict) -> str:
    lagb = d["lagb"]
    bands = list(dict.fromkeys(lagb.band))
    W, H = 720, 340
    x0, x1, y0, y1 = 64, 700, 286, 26
    lo, hi = 0.3, 1.5
    sx = lambda i: x0 + 190 + i * (x1 - x0 - 220) / (len(bands) - 1)
    sy = lambda v: y0 - (v - lo) / (hi - lo) * (y0 - y1)
    series = [("voynich", "s1", "Voynich manuscript"), ("natural", "s2", "Natural languages (mean of 7)"),
              ("cipher", "s3", "Naibbe cipher (mean of 2)"), ("algo_gibberish", "s4", "Copy-and-modify generator (mean of 4)")]
    out = [f'<svg class="chart" id="lag-svg" viewBox="0 0 {W} {H}" role="img" aria-label="Line chart: how much more alike neighbouring words are than chance, by distance">']
    for tick in (0.4, 0.6, 0.8, 1.0, 1.2, 1.4):
        cls = "baseline" if tick == 1.0 else "grid"
        out.append(f'<line class="{cls}" x1="{x0}" y1="{sy(tick):.1f}" x2="{x1}" y2="{sy(tick):.1f}"/>')
        out.append(f'<text class="tick" x="{x0 - 8}" y="{sy(tick) + 4:.1f}" text-anchor="end">{tick:.1f}×</text>')
    out.append('<text class="axis-title" x="14" y="13">times chance (1.0× = the same page with its words shuffled)</text>')
    for i, bname in enumerate(bands):
        out.append(f'<text class="tick" x="{sx(i):.1f}" y="{y0 + 18}" text-anchor="middle">{esc(bname)}</text>')
    out.append(f'<text class="axis-title" x="{(x0 + x1) / 2:.0f}" y="{H - 6}" text-anchor="middle">distance between the two words, in words</text>')
    data = {}
    for key, cls, name in series:
        g = lagb[lagb.group == key].set_index("band").loc[bands]
        pts = [(sx(i), sy(v)) for i, v in enumerate(g["mean"])]
        if g["n"].iloc[0] > 1:
            for i, (mn, mx) in enumerate(zip(g["min"], g["max"])):
                out.append(f'<line class="whisker {cls}" x1="{sx(i):.1f}" y1="{sy(max(mn, lo)):.1f}" x2="{sx(i):.1f}" y2="{sy(min(mx, hi)):.1f}"/>')
        out.append(f'<polyline class="line {cls}" points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}"/>')
        for x, y in pts:
            out.append(f'<circle class="dot {cls}" cx="{x:.1f}" cy="{y:.1f}" r="4"/>')
        data[key] = {"name": name, "cls": cls, "mean": [round(float(v), 2) for v in g["mean"]],
                     "min": [round(float(v), 2) for v in g["min"]], "max": [round(float(v), 2) for v in g["max"]]}
    # direct labels in a column left of the first point, where the four lines are furthest apart
    short = {"voynich": "Voynich", "algo_gibberish": "generator", "natural": "natural languages", "cipher": "Naibbe cipher"}
    labs = sorted(((sy(data[k]["mean"][0]), k) for k in short), key=lambda t: t[0])
    ys: list[float] = []
    for y, _ in labs:                       # keep at least 16px between neighbouring labels
        ys.append(max(y, ys[-1] + 16) if ys else y)
    pushed = ys[1] - labs[1][0]             # the top two coincide: centre the pair on their shared position
    for n, ((_, k), y) in enumerate(zip(labs, ys)):
        if n < 2 and pushed > 0:
            y -= pushed / 2
        out.append(f'<text class="value" x="{sx(0) - 12:.1f}" y="{y + 4:.1f}" text-anchor="end">{esc(short[k])} {data[k]["mean"][0]:.2f}×</text>')
    out.append(f'<line id="lag-cross" class="cross" x1="0" y1="{y1}" x2="0" y2="{y0}" visibility="hidden"/>')
    out.append(f'<rect id="lag-hit" x="{x0}" y="{y1}" width="{x1 - x0}" height="{y0 - y1}" fill="transparent" tabindex="0" aria-label="Move across the chart to read values"/>')
    out.append("</svg>")
    legend = '<ul class="legend">' + "".join(
        f'<li><span class="key line-key {cls}"></span>{esc(name)}</li>' for _, cls, name in series) + "</ul>"
    payload = {"bands": bands, "xs": [round(sx(i), 1) for i in range(len(bands))], "series": data, "w": W}
    tv = pd.DataFrame({"Distance (words)": bands})
    for key, _, name in series:
        s = data[key]
        tv[name] = [f"{m:.2f}" + (f" ({a:.2f}–{b:.2f})" if key != "voynich" else "") for m, a, b in zip(s["mean"], s["min"], s["max"])]
    return (legend + "".join(out) + f'<script type="application/json" id="lag-data">{json.dumps(payload)}</script>'
            + table_view(tv, "Probability that two words are one glyph apart, relative to the same page with words shuffled; range across texts in brackets"))


def chart_edges(d: dict) -> str:
    e = d["edge"]
    panels = [("line-first word, first glyph", "First glyph of the first word in a line", ["p", "t", "y", "d"]),
              ("line-last word, last glyph", "Last glyph of the last word in a line", ["m", "g", "d", "l"])]
    top = 0.20
    out = ['<div class="dumbbells">']
    rows_tv = []
    for where, title, glyphs in panels:
        out.append(f'<div class="db-panel"><h4>{esc(title)}</h4>')
        out.append('<div class="db-axis" aria-hidden="true"><span></span><div class="db-scale"><i style="left:0%">0</i><i style="left:50%">10%</i><i style="left:100%">20%</i></div><span></span></div>')
        sub = e[e["where"] == where].set_index("glyph")
        for g in glyphs:
            if g not in sub.index:
                continue
            r = sub.loc[g]
            a, b = float(r.share_elsewhere), float(r.share_at_edge)
            la, lb = 100 * min(a, top) / top, 100 * min(b, top) / top
            left, width = min(la, lb), abs(lb - la)
            ratio = f"{r.ratio:.0f}×" if r.ratio >= 2 else f"{r.ratio:.1f}×"
            out.append(
                f'<div class="db-row hit" tabindex="0" data-v="{100 * b:.1f}% at the line edge" data-tip="glyph {g}: {100 * a:.1f}% elsewhere ({ratio})">'
                f'<span class="glyph">{esc(g)}</span>'
                f'<div class="db-track"><span class="db-link" style="left:{left:.2f}%;width:{width:.2f}%"></span>'
                f'<span class="db-dot ctx" style="left:{la:.2f}%"></span><span class="db-dot s1" style="left:{lb:.2f}%"></span></div>'
                f'<span class="db-val">{100 * b:.1f}%<small>{ratio}</small></span></div>')
            rows_tv.append({"Position": title, "Glyph (EVA)": g, "Share at the line edge": f"{100 * b:.1f}%",
                            "Share elsewhere": f"{100 * a:.2f}%", "Ratio": ratio, "Count at edge": int(r.n_at_edge)})
        out.append("</div>")
    out.append("</div>")
    legend = ('<ul class="legend"><li><span class="key dot-key ctx"></span>same glyph position in other words</li>'
              '<li><span class="key dot-key s1"></span>in the word at the line edge</li></ul>')
    return legend + "".join(out) + table_view(pd.DataFrame(rows_tv), "Share of words carrying each glyph at the line edge and elsewhere (lines of four or more words)")


def _ci(s: str) -> tuple[float, float]:
    a, b = re.findall(r"[-+]?[0-9.]+", s)
    return float(a), float(b)


def chart_pairs(d: dict) -> str:
    pt = d["ptypes"]
    r = pt[(pt.section == "all nine quires") & (pt.measure == "lsa")].iloc[0]
    items = [
        ("Inner pair of a sheet", "1v and 2r", r.conjoint_minus_baseline, (r.ci95_lo, r.ci95_hi), int(r.conjoint_n)),
        ("Two sides of one leaf", "1r and 1v, 2r and 2v", r.confoliate_minus_baseline, _ci(r.confoliate_ci), int(r.confoliate_n)),
        ("Diagonal across the sheet", "1r and 2r, 1v and 2v", r.diagonal_minus_baseline, _ci(r.diagonal_ci), int(r.diagonal_n)),
        ("Outer pair of a sheet", "1r and 2v", r.outer_minus_baseline, _ci(r.outer_ci), int(r.outer_n)),
        ("Facing pages on different sheets", "as bound today, same scribe", r.facing_minus_baseline, _ci(r.facing_ci), int(r.facing_same_scribe_n)),
    ]
    lo, hi = -0.05, 0.25
    pos = lambda v: 100 * (v - lo) / (hi - lo)
    out = ['<div class="intervals">',
           '<div class="iv-axis" aria-hidden="true"><span></span><div class="iv-scale">'
           + "".join(f'<i style="left:{pos(t):.1f}%">{t:+.2f}</i>' if t else f'<i style="left:{pos(0):.1f}%">0</i>' for t in (0, 0.1, 0.2))
           + "</div><span></span></div>"]
    rows_tv = []
    for name, sub, v, (a, b), n in items:
        out.append(
            f'<div class="iv-row hit" tabindex="0" data-v="{v:+.3f}" data-tip="{esc(name)} ({esc(sub)}): 95% interval {a:+.3f} to {b:+.3f}, {n} pairs">'
            f'<span class="iv-label">{esc(name)}<small>{esc(sub)}</small></span>'
            f'<div class="iv-track"><span class="iv-zero" style="left:{pos(0):.1f}%"></span>'
            f'<span class="iv-ci" style="left:{pos(a):.2f}%;width:{pos(b) - pos(a):.2f}%"></span>'
            f'<span class="iv-dot" style="left:{pos(v):.2f}%"></span></div>'
            f'<span class="iv-val">{v:+.3f}</span></div>')
        rows_tv.append({"Pair of pages": f"{name} ({sub})", "Extra similarity": f"{v:+.3f}", "95% interval": f"{a:+.3f} to {b:+.3f}", "Pairs": n})
    out.append("</div>")
    note = ('<p class="chart-note">Zero is the average similarity of two pages by the same scribe in the same quire that are '
            'not on the same sheet. Dots are means; bars are 95% bootstrap intervals over pairs.</p>')
    return "".join(out) + note + table_view(pd.DataFrame(rows_tv), "LSA cosine similarity minus the own-quire, same-scribe baseline; quires 1–7, 13 and 20")


def diagram_sheet(d: dict) -> str:
    pt = d["ptypes"]
    r = pt[(pt.section == "all nine quires") & (pt.measure == "lsa")].iloc[0]
    v = {"inner": r.conjoint_minus_baseline, "leaf": r.confoliate_minus_baseline, "diag": r.diagonal_minus_baseline,
         "outer": r.outer_minus_baseline, "next": r.facing_minus_baseline}
    fmt = lambda x: f"{x:+.3f}".replace("-", "−")
    top = 116

    def arc(x1, x2, h, cls="arc", extra=""):
        return f'<path class="{cls}" d="M {x1} {top} Q {(x1 + x2) / 2:.0f} {top - 2 * h} {x2} {top}"{extra}/>'

    def lab(x, h, text):
        return f'<text class="val" x="{x}" y="{top - h - 6}" text-anchor="middle">{text}</text>'

    px = [16, 100, 184, 268]
    out = ['<svg class="sheet" viewBox="0 0 430 196" role="img" aria-label="Diagram of the four pages of one folded sheet in reading order, '
           'with arcs giving the extra similarity between each pair of pages, and the first page of the next sheet as bound">']
    out += [arc(30, 312, 74, "arc weak"), arc(40, 208, 42, "arc", ' opacity=".6"'), arc(124, 292, 42, "arc", ' opacity=".6"'),
            arc(55, 119, 16), arc(139, 203, 16, "arc", ' stroke-width="3"'), arc(223, 287, 16), arc(307, 375, 16, "arc weak")]
    out += [lab(171, 74, fmt(v["outer"])), lab(124, 42, fmt(v["diag"])), lab(208, 42, fmt(v["diag"])),
            lab(87, 16, fmt(v["leaf"])), lab(171, 16, fmt(v["inner"])), lab(255, 16, fmt(v["leaf"])), lab(341, 16, fmt(v["next"]))]
    for x, name in zip(px, ("1r", "1v", "2r", "2v")):
        out.append(f'<rect class="pg" x="{x}" y="120" width="58" height="46" rx="2"/>')
        out.append(f'<text class="pn" x="{x + 29}" y="148" text-anchor="middle">{name}</text>')
    out.append('<rect class="pg-next" x="356" y="120" width="58" height="46" rx="2"/>')
    out.append('<text x="385" y="141" text-anchor="middle">next</text><text x="385" y="155" text-anchor="middle">sheet</text>')
    out.append('<line class="fold" x1="171" y1="120" x2="171" y2="172"/>')
    out.append('<text x="87" y="188" text-anchor="middle">leaf 1</text><text x="171" y="188" text-anchor="middle">fold</text>'
               '<text x="255" y="188" text-anchor="middle">leaf 2</text>')
    out.append("</svg>")
    return "".join(out)


def chart_scribe_subject(d: dict) -> str:
    sv = d["svs"]
    nice = {"S1 herbal | S2 herbal": "Scribe 1 → scribe 2, herbal pages", "S1 herbal | S3 herbal": "Scribe 1 → scribe 3, herbal pages",
            "S1 herbal | S5 herbal": "Scribe 1 → scribe 5, herbal pages", "S2 herbal | S3 herbal": "Scribe 2 → scribe 3, herbal pages",
            "S1 herbal | S1 pharma": "Scribe 1: herbal → pharmaceutical", "S2 herbal | S2 biological": "Scribe 2: herbal → bathing pages",
            "S3 herbal | S3 stars": "Scribe 3: herbal → starred paragraphs"}
    groups = [("Change the scribe, keep the subject", sv[sv.contrast.str.contains("other scribe")]),
              ("Change the subject, keep the scribe", sv[sv.contrast.str.contains("other subject")])]
    out = ['<div class="bars">']
    rows_tv = []
    for title, g in groups:
        out.append(f'<h4>{esc(title)}</h4>')
        for r in g.itertuples():
            pct = 100 * r.between_over_within
            out.append(
                f'<div class="bar-row hit" tabindex="0" data-v="{pct:.0f}% kept" data-tip="{esc(nice[r.cells])}: similarity {r.between:.2f} across, {(r.within_a + r.within_b) / 2:.2f} within">'
                f'<span class="bar-label">{esc(nice[r.cells])}</span>'
                f'<div class="bar-track"><span class="bar-fill" style="width:{min(pct, 100):.1f}%"></span></div>'
                f'<span class="bar-val">{pct:.0f}%</span></div>')
            rows_tv.append({"Contrast": nice[r.cells], "Similarity within each group": f"{r.within_a:.2f} / {r.within_b:.2f}",
                            "Similarity across": f"{r.between:.2f}", "Kept": f"{pct:.0f}%"})
    out.append('<div class="bar-axis" aria-hidden="true"><span></span><div class="bar-scale"><i style="left:0%">0</i><i style="left:50%">50%</i><i style="left:100%">100%</i></div><span></span></div>')
    out.append("</div>")
    return "".join(out) + table_view(pd.DataFrame(rows_tv), "Mean LSA similarity between pages; 'kept' = similarity across the two groups as a share of similarity within them. Same-sheet pairs excluded.")


def calibration_table(cal: pd.DataFrame) -> str:
    head = "".join(f"<th>{esc(c)}</th>" for c in ["Measurement", "Voynich", "Natural languages", "Naibbe cipher", "Copy-and-modify generator", "What it separates"])
    body = ""
    for r in cal.itertuples(index=False):
        body += ("<tr>" + f"<th scope=\"row\">{esc(r[0])}</th>" + f'<td class="num hl">{esc(r[1])}</td>'
                 + "".join(f'<td class="num">{esc(v)}</td>' for v in r[2:5]) + f"<td>{esc(r[5])}</td></tr>")
    return f'<div class="scroll"><table class="data calib"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def img(name: str) -> str:
    p = REPORT / "img" / f"{name}.jpg"
    return "data:image/jpeg;base64," + base64.b64encode(p.read_bytes()).decode()


# --------------------------------------------------------------------------------------- build

def main() -> None:
    d = load()
    f, cal = facts(d)
    charts = {
        "chart_h2": chart_h2(d), "chart_lag": chart_lag(d), "chart_edges": chart_edges(d),
        "chart_pairs": chart_pairs(d), "chart_scribe_subject": chart_scribe_subject(d), "diagram_sheet": diagram_sheet(d),
        "calibration_table": calibration_table(cal),
    }
    tpl = (REPORT / "dossier.template.html").read_text(encoding="utf-8")
    missing = []

    def fill(m: re.Match) -> str:
        key = m.group(1)
        if key.startswith("img:"):
            return img(key[4:])
        if key in charts:
            return charts[key]
        if key in f:
            return esc(f[key])
        missing.append(key)
        return m.group(0)

    page = re.sub(r"\{\{([a-zA-Z0-9_:]+)\}\}", fill, tpl)
    if missing:
        raise SystemExit(f"unknown markers in template: {sorted(set(missing))}")
    (REPORT / "voynich-dossier.html").write_text(page, encoding="utf-8")
    unused = sorted(k for k in f if "{{" + k + "}}" not in tpl)
    print(f"wrote report/voynich-dossier.html ({len(page) / 1024:.0f} KB); {len(f)} facts, {len(unused)} unused")
    (T / "facts.json").write_text(json.dumps(f, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--facts":
        ff, cc = facts(load())
        for k, v in ff.items():
            print(f"{k:22s} {v}")
        print(cc.to_string())
    else:
        main()
