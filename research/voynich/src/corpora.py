"""Uniform loaders for the Voynich text and for the control corpora.

Every corpus is returned as a `Corpus`: a name, a kind, and a list of *lines*, each line a list of
word tokens. Kinds:

  voynich        the manuscript itself (paragraph text unless stated otherwise)
  natural        meaningful natural-language text (line breaks are imposed, see `wrap`)
  cipher         meaningful text under the Naibbe cipher (Greshko 2025) - positive control for
                 "meaning hidden by a period-plausible cipher"
  algo_gibberish meaningless text from the Timm & Schinner self-citation generator
  human_gibberish meaningless text written by volunteers (Gaskell & Bowern 2022)

External sources are read from a root directory holding the cloned repositories
(`<root>/<owner>/<repo>`); see data/SOURCES.md and fetch_sources.sh.
"""
from __future__ import annotations

import random
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # scripts run with `python -I`
import ivtff  # noqa: E402

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
ZL = PROJECT / "data" / "transliterations" / "ZL3b-n.txt"

WORD_RE = re.compile(r"[^\W\d_]+", re.UNICODE)


def default_root() -> Path:
    """Where the third-party sources live: ./sources (made by fetch_sources.sh) or $VOYNICH_SOURCES."""
    import os

    env = os.environ.get("VOYNICH_SOURCES")
    return Path(env) if env else PROJECT / "sources"


@dataclass
class Corpus:
    name: str
    kind: str
    lines: list[list[str]]
    note: str = ""
    native_lines: bool = False     # True if the line breaks come from the source, not from wrap()

    @property
    def tokens(self) -> list[str]:
        return [w for line in self.lines for w in line]

    def __len__(self) -> int:
        return sum(len(line) for line in self.lines)


# ----------------------------------------------------------------------------- Voynich

_cache: dict = {}


def voynich_frames(path: Path = ZL, comma_is_space: bool = True):
    key = (str(path), comma_is_space)
    if key not in _cache:
        _cache[key] = ivtff.to_frames(*ivtff.parse(path, comma_is_space=comma_is_space))
    return _cache[key]


def voynich(subset: str = "all", path: Path = ZL, comma_is_space: bool = True,
            clean_only: bool = True) -> Corpus:
    """Paragraph text of the manuscript as lines of tokens, in current binding order.

    subset: 'all', 'A', 'B' (Currier language), 'hand1'..'hand5', or an illustration code
            prefixed by 'sec' (e.g. 'secH', 'secB', 'secS').
    """
    _, t = voynich_frames(path, comma_is_space)
    t = t[t.generic == "P"]
    if subset in ("A", "B"):
        t = t[t.language == subset]
    elif subset.startswith("hand"):
        t = t[t.hand == subset[4:]]
    elif subset.startswith("sec"):
        t = t[t.illustration == subset[3:]]
    elif subset != "all":
        raise ValueError(subset)
    lines = []
    for _, g in t.groupby(["seq", "line_on_page"], sort=True):
        toks = [w for w, ok in zip(g.token, g.clean) if ok or not clean_only]
        if toks:
            lines.append(toks)
    return Corpus(f"Voynich {subset}", "voynich", lines, native_lines=True)


def voynich_line_lengths(path: Path = ZL) -> list[int]:
    return [len(line) for line in voynich("all", path).lines]


# ----------------------------------------------------------------------------- helpers

def normalise(text: str, keep_diacritics: bool = False) -> list[str]:
    """Lower-case, strip punctuation/digits, optionally strip diacritics; return word tokens."""
    text = text.lower()
    if not keep_diacritics:
        text = "".join(ch for ch in unicodedata.normalize("NFD", text)
                       if unicodedata.category(ch) != "Mn")
    return WORD_RE.findall(text)


def wrap(tokens: list[str], line_lengths: list[int], seed: int = 0) -> list[list[str]]:
    """Impose line breaks on a token stream by sampling line lengths from `line_lengths`.

    This gives control texts the same line-length distribution as the manuscript while keeping
    the breaks independent of the words - the null model for any line-position effect."""
    rng = random.Random(seed)
    lines, i = [], 0
    while i < len(tokens):
        n = rng.choice(line_lengths)
        lines.append(tokens[i:i + n])
        i += n
    return lines


def _read(path: Path, encoding: str = "utf-8") -> str:
    return path.read_text(encoding=encoding, errors="replace")


def _tess(path: Path) -> str:
    """Tesserae .tess files: '<tag>\\ttext' per line."""
    out = []
    for line in _read(path).splitlines():
        out.append(line.split("\t", 1)[1] if "\t" in line else re.sub(r"^<[^>]*>", "", line))
    return "\n".join(out)


def _gutenberg_body(text: str) -> str:
    m1 = re.search(r"\*\*\* ?START OF.*?\*\*\*", text, flags=re.S)
    m2 = re.search(r"\*\*\* ?END OF", text)
    return text[m1.end() if m1 else 0: m2.start() if m2 else len(text)]


# ----------------------------------------------------------------------------- controls

def controls(root: Path, line_lengths: list[int] | None = None, max_tokens: int = 60000) -> list[Corpus]:
    """Load every control corpus that is present under `root`."""
    root = Path(root)
    ll = line_lengths or voynich_line_lengths()
    out: list[Corpus] = []

    def natural(name, text, note="", keep_diacritics=False):
        toks = normalise(text, keep_diacritics)[:max_tokens]
        if len(toks) >= 2000:
            out.append(Corpus(name, "natural", wrap(toks, ll, seed=len(out)), note))

    vu = root / "lrozanova" / "voynich-units" / "data" / "voynich-units"
    if vu.exists():
        natural("Latin: Pliny, Nat. Hist. 16-20 (botany)",
                _tess(vu / "herbal" / "pliny_the_elder.naturalis_historia.part.4.books_16-20.tess"),
                "classical Latin, botanical subject matter")
        natural("Latin: Pliny, Nat. Hist. 21-25 (medicinal plants)",
                _tess(vu / "herbal" / "pliny_the_elder.naturalis_historia.part.5.books_21-25.tess"),
                "classical Latin, herbal-medical subject matter")
        natural("Latin: Celsus, De Medicina",
                "\n".join(_tess(p) for p in sorted((vu / "latin").glob("celsus*.tess"))),
                "classical Latin, medical")
        natural("Latin: Caesar, De Bello Gallico",
                "\n".join(_tess(p) for p in sorted((vu / "latin").glob("caesar*.tess"))),
                "classical Latin, narrative")
        natural("English: Culpeper, Complete Herbal",
                _gutenberg_body(_read(vu / "herbal" / "culpeper_en.txt")),
                "17th-c. English herbal")

    hist = root / "chirila" / "Voynich-public" / "Corpora" / "Historical_texts"
    if hist.exists():
        for fname, name, note in [
            ("Secreta_Secretorum_LAT", "Latin: Secreta Secretorum (medieval)", "13th-c. Latin, Bacon's edition"),
            ("Rettorica", "Italian: Brunetto Latini, Rettorica", "13th-c. Tuscan"),
            ("Cirurgie", "Middle English: Science of Cirurgie", "c. 1400 medical text"),
            ("Hebrew_Bereshit", "Hebrew: Genesis (unvowelled)", "abjad: vowels unwritten"),
            ("Steganographia", "Latin: Trithemius, Steganographia", "c. 1500; includes invented spirit names"),
        ]:
            if (hist / fname).exists():
                natural(name, _read(hist / fname), note, keep_diacritics=True)

    bible = root / "mzattera" / "v4j" / "eclipse" / "io.github.mzattera.v4j" / "src" / "main" / "resources" / "Transcriptions" / "Bible"
    if bible.exists():
        for lang in ("Latin", "Italian", "German"):
            if (bible / f"{lang}.txt").exists():
                natural(f"{lang}: Bible", _read(bible / f"{lang}.txt")[:1_200_000], "Vulgate" if lang == "Latin" else "")

    gm = root / "_controls" / "gaskell_meaningful" / "texts"
    if gm.exists():
        for p in sorted(gm.glob("Historical - Latin (Abbreviated) - *.txt")):
            natural("Latin (abbreviated): " + p.stem.split(" - ")[-1], _read(p), "scribal abbreviations kept", True)

    # --- Naibbe cipher (Greshko 2025): Latin plaintext, Voynich-like ciphertext
    nb = root / "lrozanova" / "voynich-units" / "data" / "controls" / "naibbe"
    f = nb / "greshko_nathist_output_ciphertext.txt"
    if f.exists():
        src_lines = [ln.split() for ln in _read(f).splitlines() if ln.strip()]
        toks = [w for ln in src_lines for w in ln][:max_tokens]
        out.append(Corpus("Naibbe cipher of Pliny NH 16 (Greshko)", "cipher", wrap(toks, ll, seed=101),
                          "Greshko's own encryption; meaningful Latin underneath"))
    f = nb / "naibbe_caesar_ciphertext_lines.txt"
    if f.exists():
        lines = [ln.split() for ln in _read(f).splitlines() if ln.strip()]
        toks = [w for ln in lines for w in ln][:max_tokens]
        out.append(Corpus("Naibbe cipher of Caesar (re-implementation)", "cipher", wrap(toks, ll, seed=102),
                          "Rozanova & Temerev's re-implementation from the published tables"))

    # --- self-citation generator (Timm & Schinner 2019): meaningless by construction
    f = root / "TorstenTimm" / "SelfCitationTextgenerator" / "executable" / "generate" / "generated_text.txt"
    if f.exists():
        lines = [ln.split() for ln in _read(f).splitlines() if ln.strip() and not ln.startswith("#")]
        out.append(Corpus("Self-citation generator (Timm & Schinner, original)", "algo_gibberish", lines,
                          "authors' own sample output; line breaks are the generator's", native_lines=True))
    sc = root / "lrozanova" / "voynich-units" / "data" / "controls" / "selfcitation"
    for p in sorted(sc.glob("selfcite_seed*.txt")):
        lines = [ln.split() for ln in _read(p).splitlines() if ln.strip()]
        out.append(Corpus(f"Self-citation generator (port, {p.stem[-5:]})", "algo_gibberish", lines,
                          "Python port by Rozanova & Temerev", native_lines=True))

    # --- human gibberish (Gaskell & Bowern 2022): 38 short samples
    gg = root / "_controls" / "gaskell_gibberish"
    if gg.exists():
        for p in sorted(gg.glob("Gibberish - *.txt")):
            lines = [normalise(ln, keep_diacritics=True) for ln in _read(p).splitlines()]
            lines = [ln for ln in lines if ln]
            if lines:
                out.append(Corpus(f"Human gibberish {p.stem.split(' - ')[-1]}", "human_gibberish", lines,
                                  "volunteer-written meaningless text", native_lines=True))
    return out


if __name__ == "__main__":
    import sys

    root = Path(sys.argv[1]) if len(sys.argv) > 1 else default_root()
    v = voynich("all")
    print(f"{v.name}: {len(v)} tokens, {len(v.lines)} lines")
    for c in controls(root):
        print(f"{c.kind:16s} {len(c):6d} tok {len(c.lines):5d} lines  {c.name}")
