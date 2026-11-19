"""Crop the page details used by the origin-story page.

Usage: python -I src/make_story_images.py [panels_dir]   (default: sources/.../panels from fetch_sources.sh --images)
Images: Beinecke Rare Book & Manuscript Library, Yale University (MS 408), public domain.
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


def crop(im, box):
    w, h = im.size
    l, t, r, b = box
    return im.crop((int(l * w), int(t * h), int(r * w), int(b * h)))


def fit(im, width):
    return im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)


if __name__ == "__main__":
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "sources" / "writtenbyalina" / "voynichviewer" / "data" / "panels"
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (page, box) in HANDS.items():
        im = fit(crop(Image.open(src / f"{page}_l.jpg").convert("RGB"), box), 560)
        im.save(OUT / f"{name}.jpg", quality=74, optimize=True, progressive=True)
        print(name, page, im.size, (OUT / f"{name}.jpg").stat().st_size)

    # the inner side of one folded sheet as its makers saw it: f78v on the left, f81r on the right
    left = crop(Image.open(src / "f78v_l.jpg").convert("RGB"), (0.17, 0.02, 1.0, 0.98))
    right = crop(Image.open(src / "f81r_l.jpg").convert("RGB"), (0.0, 0.02, 0.90, 0.98))
    h = 560
    left = left.resize((round(left.width * h / left.height), h), Image.LANCZOS)
    right = right.resize((round(right.width * h / right.height), h), Image.LANCZOS)
    sheet = Image.new("RGB", (left.width + right.width, h), (201, 182, 165))
    sheet.paste(left, (0, 0))
    sheet.paste(right, (left.width, 0))
    sheet.save(OUT / "sheet_78_81.jpg", quality=72, optimize=True, progressive=True)
    print("sheet_78_81", sheet.size, (OUT / "sheet_78_81.jpg").stat().st_size)

    im = fit(crop(Image.open(src / "f103r_l.jpg").convert("RGB"), (0.03, 0.0, 1.0, 0.62)), 420)
    im.save(OUT / "f103r.jpg", quality=72, optimize=True, progressive=True)
    print("f103r", im.size, (OUT / "f103r.jpg").stat().st_size)
