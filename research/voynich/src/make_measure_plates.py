"""Measure plates: counts drawn onto photographs of the real pages.

Two stills for the film treatment's "measure" register, both cut at the film's 1.37:1 ratio:

  m_parts   every word on the page that is built from the short list of stock beginnings and
            endings (results/tables/word_parts.json) is tinted
  m_echo    every pair of neighbouring words on a line that are identical, or one glyph apart, is
            boxed and joined

Word positions are the bounding boxes of The Voynichese Project (2014, Apache-2.0) as fitted to
Yale's photographs by the Voynich Viewer project, with the transliteration they index (VT). Lines
whose word count differs between boxes and transliteration are left unmarked and reported.

Usage:  python -I src/make_measure_plates.py [viewer_data_dir]
        (default: sources/writtenbyalina/voynichviewer/data from fetch_sources.sh --images)
Writes: report/img/m_parts.jpg, report/img/m_echo.jpg (and _s storyboard sizes), results/tables/measure_plates.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from PIL import Image, ImageDraw  # noqa: E402

import corpora  # noqa: E402
import ivtff  # noqa: E402

OUT = corpora.PROJECT / "report" / "img"
T = corpora.PROJECT / "results" / "tables"
ASPECT = 1.37
BLUE = (30, 92, 150)            # azurite at full strength; the one colour the measure register uses
PARTS_PAGE, ECHO_PAGE = "f75r", "f108v"


def one_apart(a: str, b: str) -> bool:
    """True when the two words differ by exactly one glyph changed, added or dropped."""
    if a == b or abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    if len(a) > len(b):
        a, b = b, a
    i = 0
    while i < len(a) and a[i] == b[i]:
        i += 1
    return a[i:] == b[i + 1:]


def page_lines(tokens, boxes_dir: Path, page: str, size):
    """-> (lines, n_lines_total): each line a list of (word, x, y, w, h) in pixels of the photograph,
    only where boxes and words agree. The box files give positions in thousandths of the image
    width and height, so they are scaled to the photograph here."""
    g = tokens[tokens.page == page]
    sx, sy = size[0] / 1000, size[1] / 1000
    by_line: dict[int, list] = {}
    for rec in json.load(open(boxes_dir / f"{page}.json"))["words"]:
        wi, x, y, w, h = rec[1:6]
        by_line.setdefault(rec[0], []).append((wi, x * sx, y * sy, w * sx, h * sy))
    lines, total = [], 0
    for ln, lg in g.groupby("line_on_page"):
        total += 1
        bx = sorted(by_line.get(ln, []))
        if len(bx) != len(lg):
            continue
        lines.append([(tok, x, y, w, h) for tok, (_, x, y, w, h) in zip(lg.token, bx)])
    return lines, total


def crop_box(size, lines, pad=0.04):
    """A 1.37:1 window, as wide as the text block plus padding, starting at its top."""
    W, H = size
    xs = [x for ln in lines for _, x, _, w, _ in ln] + [x + w for ln in lines for _, x, _, w, _ in ln]
    ys = [y for ln in lines for _, _, y, _, _ in ln]
    left = max(0, min(xs) - pad * W)
    right = min(W, max(xs) + pad * W)
    width = right - left
    height = width / ASPECT
    top = max(0, min(ys) - pad * W)
    return int(left), int(top), int(left + width), int(min(H, top + height))


def finish(page_im: Image.Image, layer: Image.Image, box, name: str) -> None:
    out = Image.alpha_composite(page_im.convert("RGBA"), layer).convert("RGB").crop(box)
    out.save(OUT / f"{name}.jpg", quality=74, optimize=True, progressive=True)
    print(name, out.size, (OUT / f"{name}.jpg").stat().st_size)
    small = out.resize((520, round(520 * out.height / out.width)), Image.LANCZOS)   # storyboard size
    small.save(OUT / f"{name}_s.jpg", quality=72, optimize=True, progressive=True)


def main() -> None:
    data = Path(sys.argv[1]) if len(sys.argv) > 1 else corpora.default_root() / "writtenbyalina" / "voynichviewer" / "data"
    boxes, panels = data / "text" / "boxes", data / "panels"
    pages, toks = ivtff.parse(corpora.PROJECT / "data" / "transliterations" / "VT0e-n.txt")
    _, t = ivtff.to_frames(pages, toks)
    wp = json.loads((T / "word_parts.json").read_text())
    stock = {s + m + e for s in wp["starts"] for m in wp["mids"] for e in wp["ends"]}
    facts = {}

    # --- words built from the stock parts
    im = Image.open(panels / f"{PARTS_PAGE}_l.jpg").convert("RGB")
    lines, total = page_lines(t, boxes, PARTS_PAGE, im.size)
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    box = crop_box(im.size, lines)
    n = hit = 0
    for ln in lines:
        for word, x, y, w, h in ln:
            if not (box[1] <= y and y + h <= box[3]):
                continue
            n += 1
            if word in stock:
                hit += 1
                d.rectangle((x - 1, y - 1, x + w + 1, y + h + 1), fill=BLUE + (84,), outline=BLUE + (235,), width=1)
    finish(im, layer, box, "m_parts")
    facts["parts"] = {"page": PARTS_PAGE, "words_in_frame": n, "built_from_stock_parts": hit, "share": hit / n,
                      "lines_marked": len(lines), "lines_on_page": total}

    # --- neighbours that repeat or differ by one glyph
    im = Image.open(panels / f"{ECHO_PAGE}_l.jpg").convert("RGB")
    lines, total = page_lines(t, boxes, ECHO_PAGE, im.size)
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    box = crop_box(im.size, lines)
    n = same = near = 0
    for ln in lines:
        in_frame = [(wd, x, y, w, h) for wd, x, y, w, h in ln if box[1] <= y and y + h <= box[3]]
        n += len(in_frame)
        for (a, ax, ay, aw, ah), (b, bx, by, bw, bh) in zip(in_frame, in_frame[1:]):
            exact = a == b
            if not (exact or one_apart(a, b)):
                continue
            same += exact
            near += not exact
            for x, y, w, h in ((ax, ay, aw, ah), (bx, by, bw, bh)):
                d.rectangle((x - 1, y - 1, x + w + 1, y + h + 1), fill=BLUE + (120 if exact else 40,), outline=BLUE + (240,), width=2 if exact else 1)
            yy = max(ay + ah, by + bh) + 3
            d.line((ax + aw / 2, yy, bx + bw / 2, yy), fill=BLUE + (240,), width=2)
    finish(im, layer, box, "m_echo")
    facts["echo"] = {"page": ECHO_PAGE, "words_in_frame": n, "identical_neighbours": int(same), "one_glyph_apart": int(near),
                     "lines_marked": len(lines), "lines_on_page": total}

    (T / "measure_plates.json").write_text(json.dumps(facts, indent=1))
    print(json.dumps(facts, indent=1))


if __name__ == "__main__":
    main()
