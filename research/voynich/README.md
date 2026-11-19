# The Voynich manuscript: what it most likely is, and how to check

One question, worked in the open: what is Yale's Beinecke MS 408 most likely to be, what would it
take to show it, and what is the most plausible account of how it came to exist.

Nothing here reads the manuscript. Nothing here should be cited as a solution.

## Three things to read

| | Page | Same page in this repository |
|---|---|---|
| **The dossier** — primer, tests with controls, validation round, five tableaus, what the exercise adds and takes away, method | https://claude.ai/artifact/RUmX9pVU2m24pmBDDEnWaM | `report/voynich-dossier.html` |
| **Five Hands** — the leading tableau told as nine evidence-tagged scenes, then the foundation for a documentary | https://claude.ai/artifact/QGrVZKsyHBXHCfXtPNLjwT | `report/five-hands.html` |
| **The fact sheets** — dated, sourced claims behind both | | `notes/fact-sheet.md`, `notes/story-background.md` |

The artifact links are private to their owner until shared.

## Where the question stands

All figures are computed by the scripts here from the Zandbergen–Landini transliteration (227
page panels, 39,026 words, 8,048 distinct forms) and repeated on two others. Controls are texts
of known origin run through the same code: 15 prose texts, 6 verse texts, 4 list and recipe
texts, 21 Latin manuscripts transcribed line by line, one cipher (Naibbe), one family of
generator (Timm and Schinner), and 38 samples of gibberish written by volunteers.

**What held up**

1. **The next glyph is far easier to guess than in any real text**: 2.07 bits against 3.08–3.71
   in more than forty texts, verse, lists and abbreviated manuscripts included. A cipher and a
   generator both reproduce it, so it rules out a plainly written language and nothing more.
2. **A written word does not stand for a word.** Knowing the previous word helps predict the next
   by 0.002–0.013 bits. Every one of 25 meaningful texts gains at least 0.066, and typical prose
   0.43. This closes word-for-word readings. A cipher survives only if it works below the word.
3. **Each folded sheet is a unit**, after controlling for scribe. The two pages that lie open
   together are +0.155 more alike (95% interval +0.103 to +0.205) than other pages by the same
   scribe in the same gathering, and likeness falls in page order within the sheet. Facing pages
   on different sheets show none (−0.001). Holds on three transliterations.
4. **The two "languages" follow the scribe more than the subject.**
5. **Line starts are marked 3 to 18 times more strongly than in any control**, verse and lists
   included.
6. **Layfield and Davis (2026) replicate** from the text of their paper, to the same top-ranked
   sheet sequences.

**What did not**

- Line-end effects, likeness to the word above, and exact repetition of the neighbouring word
  were read in the first round as signs of a copying routine. Verse, lists and real manuscripts
  show the first two as strongly or more so, and the third vanishes in a finer alphabet. All
  three are withdrawn.
- The proposed re-ordering of sheets: the same search on scrambled data does as well 56% and 29%
  of the time.
- The claim that the published generator matches the manuscript. It matches in kind and repeats
  itself 2 to 12 times too much. The Naibbe cipher matches the look and none of the local habits.

**Working weights after validation** (judgement, not computed)

| Tableau | Weight |
|---|---|
| A book made to look learned, with no message in its text | 35–40% |
| A real compendium whose meaning was lost in the making | 25–30% |
| A real compendium in a cipher that works below the word | 20–25% |
| An invented or revealed language | about 5% |
| An unknown language, plainly written | under 2% |

`report/five-hands.html` stages the first of these and says what would overturn it.

## What is here

```
data/transliterations/   the manuscript's text: eight IVTFF files from voynich.nu (CC0), with SHA-256s
data/derived/pages.csv   one row per page: section, Currier language, scribe, quire, sheet
data/SOURCES.md          provenance, licences, pinned versions, and what was not gathered
notes/                   fact sheets; the text of the 2026 page-order paper (CC BY 4.0)
src/                     parser, corpus loaders, twelve analyses, two page builders, three image scripts
results/tables/          every number the two pages cite
report/                  the two pages, their templates, and the page crops and plates they embed
fetch_sources.sh         fetches controls, word positions and page photographs at pinned commits
run_all.sh               re-runs everything
```

## Reproduce

Python 3.11+ with `numpy`, `pandas` and `Pillow`. No other dependencies.

```bash
./fetch_sources.sh --images   # controls, word positions, page photographs (about 650 MB, not committed)
./run_all.sh                  # about fifty minutes on four cores; rewrites results/tables and both pages
```

Without `--images` the analyses still run, and the committed crops in `report/img/` are used.

| Script | Question | Output |
|---|---|---|
| `a01_build_corpus.py` | What is in the corpus? | `pages.csv`, `corpus_summary.json` |
| `a02_baselines.py` | How does the text compare with controls of the same size? | `baselines.csv`, `alphabet_sensitivity.csv` |
| `a03_line_effects.py` | Is the line a unit? | `line_effects.csv`, `line_edge_glyphs.csv` |
| `a04_local_similarity.py` | Where do similar words sit, in reading order and vertically? | `lag_similarity.csv`, `vertical_alignment.csv` |
| `a04b_vertical_geometry.py` | The same vertical test with measured word positions | `vertical_geometry.csv` |
| `a05_sections_scribes.py` | Does vocabulary follow subject or scribe? | `cell_similarity.csv`, `scribe_vs_section.csv` |
| `a06_bifolio_order.py` | Replication, scribe control and null test for the sheet-order result | `lsa_*.csv` |
| `a07_labels.py` | Do labels and opening words behave like names? | `label_binding.csv`, `label_summary.json` |
| `a08_more_controls.py` | Do verse, lists and line-by-line manuscripts show the same habits? | `v1_*.csv` |
| `a09_predictive_scoring.py` | How much do grammar, repetition and variation help predict held-out sheets? | `v2_*.csv` |
| `a10_second_transliteration.py` | Do the headline results survive two other transliterations? | `v3_transliterations.csv` |
| `a11_corrections_and_duplicates.py` | How many corrections are flagged; does a plant drawn twice share wording? | `v4_*.json`, `v5_*.json` |
| `a12_story_tables.py` | Word shapes built from stock parts; colours sampled from the pages | `word_parts.json`, `page_palette.json` |
| `make_thumbs.py`, `make_story_images.py` | Page crops, one strip per scribe, storyboard frames | `report/img/` |
| `make_measure_plates.py` | Counts drawn onto photographs of real pages | `report/img/m_*.jpg`, `measure_plates.json` |
| `build_dossier.py`, `build_story.py` | Fill the two templates from the tables | `report/*.html` |

Scripts are run with `python -I` because they read downloaded files; nothing is executed from the
fetched directories. Random seeds are fixed. Every number in either page is filled from
`results/tables/`, and a build fails on a marker it cannot fill.

## Limits

- Produced in a single working session by an AI system under one person's direction. Not reviewed
  by specialists.
- One cipher and one family of generator stand in for two whole classes of explanation. A
  different design of either might land closer to the manuscript.
- The predictors in `a09` are deliberately crude. The grammar result does not depend on their
  detail; the repeat and vary numbers might.
- Corrections were counted from transcribers' notes, a lower bound. Nobody has counted them from
  the photographs.
- One pair of duplicate plant drawings is one pair.
- The tableau weights are judgement.
- The story in `five-hands.html` invents a town, a trade and a motive. Each invention is marked.

## Next

**At the desk.** Build and score the two missing simulators (a generator with adjustable
locality; a letter-level cipher with line-start rules and a drifting scribe). Census corrections
from the photographs with a matched count from real manuscripts. Match pharmacy plants to herbal
plants blind to the text and repeat the shared-wording test. Model the line start. Seal a set of
sheets before any further modelling.

**With the library.** Map the water stain, offsets and sewing holes across all sheets. Image the
whole book multispectrally. Sample parchment and ink sheet by sheet.

**With the community.** Publish the measurement panel and a blind challenge set, and invite both
sides to register predictions before the sealed sheets are opened.

**For the film.** Shoot or generate the eight reconstruction frames briefed in `five-hands.html`,
license the 1639 letter from the Gregorian University archive, and cut the cold open against the
narration draft.

## Credits

Page photographs: Beinecke Rare Book and Manuscript Library, Yale University (public domain).
Transliterations: René Zandbergen and Gabriel Landini, Takeshi Takahashi, Glen Claston and the
other transcribers named in `data/SOURCES.md`, as released on voynich.nu under CC0. Scribe
attributions: Lisa Fagin Davis. Word positions: The Voynichese Project (Apache-2.0), fitted to
the photographs by the Voynich Viewer project. Controls and their licences are listed in
`data/SOURCES.md`; none of their files are redistributed here.
