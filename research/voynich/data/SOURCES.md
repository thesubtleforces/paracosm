# Sources and provenance

Gathered 19 November 2026. The manuscript is Yale University, Beinecke Rare Book & Manuscript
Library, MS 408. It is in the public domain.

## What is committed here

### `data/transliterations/` — the text of the manuscript

Eight transliteration files in IVTFF format, as published on René Zandbergen's
[voynich.nu](https://www.voynich.nu/transcr.html), which releases them under CC0-1.0.

| File | What it is | Alphabet | Upstream version |
|---|---|---|---|
| `ZL3b-n.txt` | Zandbergen–Landini transliteration. The reference for all analyses here. | EVA | 3b, 13 May 2025 |
| `IT2a-n.txt` | Takeshi Takahashi's complete transliteration (1998) | EVA | 2a, Feb 2023 (mod. Jun 2025) |
| `GC2a-n.txt` | Glen Claston's transliteration | v101 | 2a, Feb 2023 (mod. Jun 2025) |
| `CD2a-n.txt` | Currier and D'Imperio (partial) | Currier | 2a, Feb 2023 |
| `FG2a-n.txt` | Friedman's First Study Group, 1940s (partial) | FSG | 2a, Feb 2023 |
| `RF1b-e.txt` | Zandbergen's reference transliteration (merge of ZL and GC) | EVA | 1b |
| `VT0e-n.txt` | voynichese.com transliteration, mainly Takahashi; the word boxes index this file | EVA | 0e |
| `LSI_ivtff_0d.txt` | Landini–Stolfi interlinear file: several transcribers per line | EVA | 1.6e6, Dec 1998 |

`SHA256SUMS` lists the checksums; `./fetch_sources.sh` verifies them.

**How they got here.** This environment's network policy blocks voynich.nu, so the files were
copied from the cache of the [voynich-data](https://github.com/noah-chelednik/voynich-data)
project (commit `ecd4c81`), which records each file's upstream URL and the SHA-256 it had when
fetched from voynich.nu on 17 October 2026. Our copies match those pinned checksums. As a second
check, an independent copy of ZL 3b in the
[voynich-units](https://github.com/lrozanova/voynich-units) archive carries identical text on
every one of its 5,385 loci; the two files differ only by one block of comment lines and one
blank line.

**Format.** IVTFF 2.0. The specification is `resources/IVTFF_format.pdf` in the v4j repository
(fetched by `fetch_sources.sh`). `src/ivtff.py` documents how each piece of markup is handled.
In ZL 3b the page variable `$H` holds the scribe in Lisa Fagin Davis's numbering and `$C` holds
Currier's older hand numbers.

### `data/derived/pages.csv`

One row per photographed panel (227): folio, side, quire, sheet, illustration type, Currier
language, scribe, token counts. Built by `src/a01_build_corpus.py` from the ZL headers. Scribe
attributions were cross-checked against the Voynich Viewer project's compilation of Davis's
tables: 225 of 226 pages identical, the last differing only in how the two-scribe page f115r is
written.

### `report/img/`

Reduced crops of Yale's photographs, embedded in the two pages. Credit: Beinecke Rare Book &
Manuscript Library, Yale University.

- Five page thumbnails for the dossier (ff. 33v, 71r, 78v, 88r, 116v), from `src/make_thumbs.py`.
- One strip of writing per scribe (`hand1`–`hand5`: ff. 88r, 78v, 103r, 71r, 48v), the inner side
  of sheet 78|81 as one image, and ten storyboard frames at 1.37:1 (`fr_*`), from
  `src/make_story_images.py`.
- Two measure plates (`m_parts` on f75r, `m_echo` on f108v): the photographs with computed marks
  drawn on them, from `src/make_measure_plates.py`. The marks use the word positions of The
  Voynichese Project (Apache-2.0).

### `notes/`

- `fact-sheet.md`: about a hundred dated claims on the manuscript's materials, provenance,
  decipherment history and internal evidence, each with its source and a verified/unverified tag.
- `layfield_davis_2026_singulion.md`: the text of Layfield and Davis, "Singulion Structure and
  the Voynich Manuscript", *Digital Medievalist* 19 (2026), which is published under CC BY 4.0.
- `story-background.md`: the period sources behind the reconstruction in
  `report/five-hands.html`, each with what was read and where.

## What is fetched on demand (`./fetch_sources.sh`, into `sources/`, not committed)

Each repository is fetched at the exact commit used for the committed results.

| Repository | Commit | Licence | What we use |
|---|---|---|---|
| [lrozanova/voynich-units](https://github.com/lrozanova/voynich-units) | `956a7c4` | MIT (code); third-party data keep their terms | Latin controls (Pliny *Nat. Hist.* 16–25, Celsus, Caesar; Tesserae texts), Culpeper's herbal, Greshko's Naibbe ciphertext of Pliny with tables (Greshko's modified MIT: cite the Cryptologia paper), a Naibbe encryption of Caesar, three seeds of a Python port of the self-citation generator |
| [TorstenTimm/SelfCitationTextgenerator](https://github.com/TorstenTimm/SelfCitationTextgenerator) | `a6ede22` | MIT | The authors' own sample output of the Timm & Schinner generator |
| [danielgaskell/voynich](https://github.com/danielgaskell/voynich) | `d076a7d` | Modified MIT for code and gibberish data | 38 samples of meaningless text written by volunteers; abbreviated-Latin comparison texts |
| [chirila/Voynich-public](https://github.com/chirila/Voynich-public) | `decc4ca` | Not stated | Lindemann & Bowern's historical comparison texts (*Secreta Secretorum*, Brunetto Latini, *Science of Cirurgie*, Hebrew Genesis, Trithemius) |
| [mzattera/v4j](https://github.com/mzattera/v4j) | `f3387f1` | GPL-3.0 (code) | Bible texts in Latin, Italian and German; the IVTFF specification |
| [writtenbyalina/voynichviewer](https://github.com/writtenbyalina/voynichviewer) | `c4117bb` | Images: Yale. Word boxes: The Voynichese Project (2014), Apache-2.0 | 236 page panels in two sizes; boxes for about 37,000 words, given in thousandths of the image width and height; collation and scribe table after Davis |
| [tesserae/tesserae](https://github.com/tesserae/tesserae) | `5e0ae30` | None stated in the files fetched | Latin verse (Virgil's *Georgics* and *Aeneid*, Lucretius, Ovid's *Fasti*, Walafrid Strabo's *Hortulus*, Wandalbert's martyrology), Cato's *De agricultura*, and Vulgate Numbers, 1 Chronicles and Psalms, each with its own verse or chapter divisions |
| [HTR-United/CREMMA-Medieval-LAT](https://github.com/HTR-United/CREMMA-Medieval-LAT) | `2925259` | CC BY 4.0 | CREMMA Medii Aevi (Clérice, Chagué, Vlachou-Efstathiou): 21 Latin manuscripts of the twelfth to sixteenth centuries transcribed line by line with their abbreviations, used as controls that keep original line breaks |
| [noah-chelednik/voynich-data](https://github.com/noah-chelednik/voynich-data) | `ecd4c81` | MIT (code), CC0 (transliterations) | Upstream of `data/transliterations/`; IIIF canvas list for Yale's images |

Because some of these carry their own terms or none, none of their files are redistributed in
this repository. Only numbers computed from them appear in `results/`.

## What was not gathered

- Yale's full-resolution photographs and IIIF tiles (blocked by the network policy; the panel
  images above are reductions of them).
- The 2014 multispectral images of ten pages that Lisa Fagin Davis released in 2024.
- The Aberdeen Bestiary and *Speculum Humanae Salvationis* transcriptions that Layfield and Davis
  used as their baseline manuscripts.
- Line-by-line transcriptions of fifteenth-century manuscripts in German, and of herbals, bath
  books and house books of medical astrology in particular. The line-preserving controls used
  here are Latin and mostly literary or theological.
- A photograph of Georg Baresch's letter of 1639 (Rome, Gregorian University archive, APUG 557,
  f. 353). Its Latin text was read in Philip Neal's transcription.
- Any generated imagery. The reconstruction frames in the film treatment are briefs only.
