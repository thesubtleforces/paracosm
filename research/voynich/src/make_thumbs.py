"""Make small page thumbnails for the report from the full page images.

Usage: python -I src/make_thumbs.py [panels_dir]      (default: sources/.../panels from fetch_sources.sh --images)
Images: Beinecke Rare Book & Manuscript Library, Yale University (MS 408), public domain.
"""
import sys
from pathlib import Path

from PIL import Image

OUT = Path(__file__).resolve().parent.parent / "report" / "img"
PAGES = {          # page -> crop box as fractions (left, top, right, bottom) of the photograph
    "f33v": (0.08, 0.0, 1.0, 1.0),
    "f88r": (0.03, 0.0, 0.97, 1.0),
    "f71r": (0.03, 0.06, 1.0, 0.86),
    "f78v": (0.17, 0.02, 1.0, 0.98),
    "f116v": (0.08, 0.0, 0.96, 0.30),
}

if __name__ == "__main__":
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "sources" / "writtenbyalina" / "voynichviewer" / "data" / "panels"
    OUT.mkdir(parents=True, exist_ok=True)
    for page, (l, t, r, b) in PAGES.items():
        im = Image.open(src / f"{page}_l.jpg").convert("RGB")
        w, h = im.size
        im = im.crop((int(l * w), int(t * h), int(r * w), int(b * h)))
        target_w = 520 if page == "f116v" else 380
        im = im.resize((target_w, round(im.height * target_w / im.width)), Image.LANCZOS)
        im.save(OUT / f"{page}.jpg", quality=72, optimize=True, progressive=True)
        print(page, im.size, (OUT / f"{page}.jpg").stat().st_size, "bytes")
