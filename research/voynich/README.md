# Voynich manuscript research workspace

A self-contained working area for one question: what is Beinecke MS 408 most likely to be, and
what would it take to show it. It is unrelated to the rest of this repository and touches
nothing outside `research/voynich/`.

**Read the report first:** https://claude.ai/artifact/RUmX9pVU2m24pmBDDEnWaM
(the same page is `report/voynich-dossier.html`). It contains the primer, a check of the
[video](https://www.youtube.com/watch?v=7SPquufK2VI) that prompted this, the first test results
with charts, five candidate tableaus, and the validation method.

## What is here

```
data/transliterations/   the manuscript's text: eight IVTFF files from voynich.nu (CC0), with SHA-256s
data/derived/pages.csv   one row per page: section, Currier language, scribe, quire, sheet
data/SOURCES.md          provenance, licences, pinned versions, and what was not gathered
notes/fact-sheet.md      ~100 sourced, dated claims behind the primer
notes/layfield_davis_2026_singulion.md   text of the 2026 page-order paper (CC BY 4.0)
src/                     parser, corpus loaders, seven analyses, report builder
results/tables/          every number the report cites
report/                  the page, its template, and five page thumbnails
fetch_sources.sh         fetches controls, word positions and page images at pinned commits
run_all.sh               re-runs everything
```

## Findings in brief

All figures are computed by the scripts here from the ZL v3b transliteration (227 page panels,
39,026 words, 8,048 distinct forms). Controls are texts of known origin run through the same
code.

| Measurement | Voynich | Natural languages | Naibbe cipher | Copy-and-modify generator |
|---|---|---|---|---|
| Glyph predictability (bits per glyph, given the one before) | 2.07 | 3.08–3.48 | 2.08 | 1.93–2.07 |
| Next word is a one-glyph variant of this one (× chance) | 1.30 | 0.36–0.85 | 0.81–0.84 | 1.11–1.42 |
| Next word is identical (× chance within the page) | 1.19 | 0.01–0.38 | 0.37–0.40 | 0.49–1.02 |
| Word-length correlation between neighbours | +0.12 | −0.20 to +0.14 | −0.04 to −0.03 | −0.03 to +0.03 |
| Line-start words differ from the rest (z-score) | +419 | −1.2 to +2.3 | −0.6 to −0.3 | +74 to +294 |
| Word matches the word above it (× chance) | 1.08 | 0.94–1.06 | 1.02–1.04 | 1.00–1.19 |

1. **Low glyph entropy rules out a plainly written language, and nothing more.** Cipher text and
   generated text both reproduce it.
2. **Neighbouring words attract; in every language and in the cipher they repel.** The
   copy-and-modify generator is the only control that behaves like the manuscript on this.
3. **The line is a unit.** `p` begins 9.6% of line-first words and 0.5% of others; `m` ends 15.8%
   of line-last words and 0.9% of others; 85% of paragraphs open with a gallows glyph.
4. **Layfield & Davis (2026) replicate.** A re-implementation from the paper's text gives the
   same pattern (0.419 / 0.297 / 0.468 against their 0.383 / 0.298 / 0.433) and the same
   top-ranked sheet order in quires 13 and 20.
5. **Sheets are units even after controlling for scribe.** The inner pair of a sheet is +0.155
   more similar (95% interval +0.103 to +0.205) than other same-scribe pages of the quire.
   Similarity falls in the order 1r, 1v, 2r, 2v. Facing pages on different sheets sit at baseline.
6. **The proposed re-ordering is not yet supported.** The same search run on scrambled score
   tables finds an order at least as good 56% (quire 13) and 29% (quire 20) of the time.
7. **Currier's two "languages" follow the scribe more than the subject.** Changing scribe on
   herbal pages keeps 34–41% of vocabulary similarity; changing subject within a scribe keeps
   56–64%.
8. **Labels and opening words do not yet behave like names.** A page's labels occur in its own
   text barely more than in a sister page's (+1.1 points, interval −0.4 to +2.8).

What this supports: the book was made sheet by sheet, by a team, in a process that worked line by
line and reused nearby words. What it does not settle: whether the text carries meaning. The
report sets out five tableaus with working weights and the tests that would move them.

## Reproduce

Python 3.11+ with `numpy`, `pandas` (and `Pillow` for thumbnails). No other dependencies.

```bash
cd research/voynich
./fetch_sources.sh        # controls, word boxes, metadata (about 400 MB; add --images for page photographs)
./run_all.sh              # about ten minutes; rewrites results/tables and report/voynich-dossier.html
```

Individual analyses:

| Script | Question | Output |
|---|---|---|
| `a01_build_corpus.py` | What is in the corpus? | `pages.csv`, `corpus_summary.json` |
| `a02_baselines.py` | How does the text compare with controls of the same size? | `baselines.csv`, `alphabet_sensitivity.csv` |
| `a03_line_effects.py` | Is the line a unit? | `line_effects.csv`, `line_edge_glyphs.csv` |
| `a04_local_similarity.py` | Where do similar words sit, in reading order and vertically? | `lag_similarity.csv`, `vertical_alignment.csv` |
| `a04b_vertical_geometry.py` | The same vertical test with pixel positions of words | `vertical_geometry.csv` |
| `a05_sections_scribes.py` | Does vocabulary follow subject or scribe? | `cell_similarity.csv`, `scribe_vs_section.csv` |
| `a06_bifolio_order.py` | Replication and controls for the sheet-order result | `lsa_*.csv` |
| `a07_labels.py` | Do labels and opening words behave like names? | `label_binding.csv`, `label_summary.json` |
| `build_dossier.py` | Builds the report from the tables | `report/voynich-dossier.html` |

Scripts are run with `python -I` because they read downloaded files; nothing is executed from the
fetched directories. Random seeds are fixed.

## Limits

- One transliteration (ZL v3b) carries most results. ZL and Takahashi differ on about half of all
  lines, usually by a glyph or a space. The entropy result was checked on four; the rest should
  be.
- The cipher control is a single cipher designed as a proof of concept. A different design might
  reproduce more of the table above.
- Every meaningful control is continuous prose. Lists, recipe collections, calendars and tables
  have not been run and may echo their neighbours.
- Control texts had line breaks imposed, so their lack of line effects is by construction.
- The vertical-position effect is small (about 10%, z ≈ 3).
- The tableau weights in the report are judgement, not computed.

## Next steps

Listed in the report under "What to do next". The first five need only what is already here:
add list-like and line-preserving controls, fit and score explicit simulators on held-out sheets,
count scribal corrections from the images, test repeated plants across sections, and repeat
every result on a second transliteration.
