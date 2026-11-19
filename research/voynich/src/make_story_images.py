"""Crop the page details used by the origin-story page.

Usage: python -I src/make_story_images.py [panels_dir]   (default: sources/.../panels from fetch_sources.sh --images)
Images: Beinecke Rare Book & Manuscript Library, Yale University (MS 408), public domain.

Three kinds of output, all written to report/img/:
  hand1..hand5      one strip of writing per scribe, at the scan's own resolution
  sheet_78_81       the inner side of one folded sheet as its makers saw it
  fr_*              storyboard frames cut from real pages at the film's 1.37:1 ratio
"""
import sys
from pathlib import Path

from PIL import Image

OUT = Path(__file__).resolve().parent.parent / "report" / "img"
HANDS = {   # scribe -> (page, crop box as fractions: left, top, right, bottom)
    "hand1": ("f88r", (0.20, 0.215, 0.90, 0.315)),
    "hand2": ("f78v", (0.31, 0.085, 0.97, 0.185)),
    "hand3": ("f103r", (0.08, 0.025, 0.92, 0.135)),
    "hand4": ("f71r", (0.20, 0.115, 0.84, 0.235)),
    "hand5": ("f48v", (0.19, 0.105, 0.98, 0.215)),
}
ASPECT = 1.37
FRAMES = {  # name -> (page, centre x, centre y, width), all as fractions of the page
    "fr_f1r": ("f1r", 0.52, 0.22, 0.86),
    "fr_plant": ("f17r", 0.50, 0.27, 0.92),
    "fr_jars": ("f88r", 0.50, 0.30, 0.92),
    "fr_aries": ("f71r", 0.50, 0.47, 0.90),
    "fr_pool": ("f78v", 0.57, 0.50, 0.84),
    "fr_castle": ("fRos-tr", 0.29, 0.335, 0.36),
    "fr_stars": ("f103r", 0.50, 0.20, 0.94),
    "fr_charm": ("f116v", 0.42, 0.075, 0.74),
    "fr_pisces": ("f70v2-1", 0.40, 0.50, 0.62),
    "fr_two_hands": ("f115r", 0.50, 0.30, 0.94),
}


def crop(im, box):
    w, h = im.size
    l, t, r, b = box
    return im.crop((int(l * w), int(t * h), int(r * w), int(b * h)))


def fit(im, width):
    return im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)


def frame(im, cx, cy, width):
    w, h = im.size
    cw = width * w
    ch = cw / ASPECT
    left = max(0, min(w - cw, cx * w - cw / 2))
    top = max(0, min(h - ch, cy * h - ch / 2))
    return im.crop((int(left), int(top), int(left + cw), int(top + ch)))


if __name__ == "__main__":
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "sources" / "writtenbyalina" / "voynichviewer" / "data" / "panels"
    OUT.mkdir(parents=True, exist_ok=True)

    def page(name):
        return Image.open(src / f"{name}_l.jpg").convert("RGB")

    for name, (pg, box) in HANDS.items():
        im = crop(page(pg), box)
        im.save(OUT / f"{name}.jpg", quality=76, optimize=True, progressive=True)
        print(name, pg, im.size, (OUT / f"{name}.jpg").stat().st_size)

    # the inner side of one folded sheet as its makers saw it: f78v on the left, f81r on the right
    left = crop(page("f78v"), (0.17, 0.02, 1.0, 0.98))
    right = crop(page("f81r"), (0.0, 0.02, 0.90, 0.98))
    h = 640
    left = left.resize((round(left.width * h / left.height), h), Image.LANCZOS)
    right = right.resize((round(right.width * h / right.height), h), Image.LANCZOS)
    sheet = Image.new("RGB", (left.width + right.width, h), (201, 182, 165))
    sheet.paste(left, (0, 0))
    sheet.paste(right, (left.width, 0))
    sheet.save(OUT / "sheet_78_81.jpg", quality=72, optimize=True, progressive=True)
    print("sheet_78_81", sheet.size, (OUT / "sheet_78_81.jpg").stat().st_size)

    for name, (pg, cx, cy, width) in FRAMES.items():
        im = frame(page(pg), cx, cy, width)
        im = im.resize((520, round(520 / ASPECT)), Image.LANCZOS)
        im.save(OUT / f"{name}.jpg", quality=70, optimize=True, progressive=True)
        print(name, pg, im.size, (OUT / f"{name}.jpg").stat().st_size)
