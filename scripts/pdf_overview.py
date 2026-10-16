"""Renders every page of a PDF into one contact sheet, for choosing pages for the site.

Usage:
    python scripts/pdf_overview.py <pdf path> <output.jpg> [--columns 10] [--tile 200] [--pages 1,4,9]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image


def build_overview(
    pdf_path: Path,
    out_path: Path,
    columns: int,
    tile: int,
    pages: list[int] | None = None,
    gap: int = 4,
) -> int:
    doc = pdfium.PdfDocument(str(pdf_path))
    indexes = [p - 1 for p in pages] if pages else list(range(len(doc)))
    count = len(indexes)
    rows = (count + columns - 1) // columns
    sheet = Image.new(
        "RGB",
        (columns * (tile + gap) + gap, rows * (tile + gap) + gap),
        (26, 26, 26),
    )

    for position, index in enumerate(indexes):
        page = doc[index]
        width, height = page.get_size()
        scale = tile / max(width, height)
        image = page.render(scale=scale).to_pil().convert("RGB")
        x = gap + (position % columns) * (tile + gap) + (tile - image.width) // 2
        y = gap + (position // columns) * (tile + gap) + (tile - image.height) // 2
        sheet.paste(image, (x, y))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path, "JPEG", quality=76, optimize=True)
    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf")
    parser.add_argument("output")
    parser.add_argument("--columns", type=int, default=10)
    parser.add_argument("--tile", type=int, default=200)
    parser.add_argument("--pages", type=str, default="", help="comma separated 1-based page numbers")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    pages = [int(part) for part in args.pages.split(",") if part.strip()] if args.pages else None
    count = build_overview(pdf_path, Path(args.output), args.columns, args.tile, pages)
    print(f"{pdf_path.name}: {count} pages -> {args.output}")


if __name__ == "__main__":
    main()
