"""Builds web-optimized assets for the portfolio site from the source portfolio folder.

Usage:
    python scripts/prepare_assets.py

Outputs:
    assets/*.jpg|*.webp|*.gif      web-optimized media
    assets/manifest.json           ordered list of grid items with metadata
    .review/contact-*.jpg          contact sheets used for visual review
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from PIL import Image, ImageFile, ImageOps

ImageFile.LOAD_TRUNCATED_IMAGES = True

SRC = Path(r"C:\Users\Administrator\Desktop\作品集")
SITE = Path(__file__).resolve().parent.parent
ASSETS = SITE / "assets"
REVIEW = SITE / ".review"

MAX_LONG_EDGE = 1500
JPEG_QUALITY = 80


def natural_key(text: str):
    return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", text)]


def export_image(
    src: Path,
    dest: Path,
    max_edge: int = MAX_LONG_EDGE,
    quality: int = JPEG_QUALITY,
) -> tuple[int, int] | None:
    """Resize one still image and save it as a progressive JPEG."""
    try:
        with Image.open(src) as img:
            img = ImageOps.exif_transpose(img)
            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")
            width, height = img.size
            scale = min(1.0, max_edge / max(width, height))
            if scale < 1.0:
                img = img.resize((round(width * scale), round(height * scale)), Image.LANCZOS)
            dest.parent.mkdir(parents=True, exist_ok=True)
            img.save(dest, "JPEG", quality=quality, optimize=True, progressive=True)
            return img.size
    except Exception as exc:  # noqa: BLE001
        print(f"  ! skipped {src.name}: {exc}")
        return None


def export_animation(src: Path, dest: Path, max_edge: int = 900) -> tuple[int, int] | None:
    """Convert an animated GIF into a smaller animated WebP."""
    try:
        with Image.open(src) as img:
            frames = []
            durations = []
            for frame in range(getattr(img, "n_frames", 1)):
                img.seek(frame)
                rgba = img.convert("RGBA")
                width, height = rgba.size
                scale = min(1.0, max_edge / max(width, height))
                if scale < 1.0:
                    rgba = rgba.resize((round(width * scale), round(height * scale)), Image.LANCZOS)
                frames.append(rgba.copy())
                durations.append(max(40, int(img.info.get("duration", 80))))
            if len(frames) > 160:
                frames = frames[::2]
                durations = durations[::2]
            width, height = frames[0].size
            dest.parent.mkdir(parents=True, exist_ok=True)
            frames[0].save(
                dest,
                "WEBP",
                save_all=True,
                append_images=frames[1:],
                duration=durations,
                loop=0,
                quality=72,
                method=4,
            )
            return width, height
    except Exception as exc:  # noqa: BLE001
        print(f"  ! skipped animation {src.name}: {exc}")
        return None


def contact_sheet(paths: list[Path], dest: Path, tile: int = 300, columns: int = 6) -> None:
    """Build a review sheet: every candidate for one project in a grid."""
    if not paths:
        return
    rows = (len(paths) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * tile, rows * tile), (24, 24, 24))
    for index, path in enumerate(paths):
        try:
            with Image.open(path) as img:
                img = ImageOps.exif_transpose(img)
                if img.mode not in ("RGB", "L"):
                    img = img.convert("RGB")
                img = ImageOps.fit(img, (tile - 6, tile - 6), method=Image.LANCZOS)
        except Exception:  # noqa: BLE001
            continue
        sheet.paste(img, ((index % columns) * tile + 3, (index // columns) * tile + 3))
    dest.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(dest, "JPEG", quality=72, optimize=True)


PROJECTS = [
    {
        "slug": "ebook-nature",
        "title": "重庆自然风貌 · 电子书",
        "subtitle": "Chongqing Nature — E-book Design",
        "category": "编辑设计",
        "source": Path("2.电子书设计"),
        "pattern": "书籍*.jpg",
        "limit": 12,
        "skip": {"书籍.jpg"},
    },
    {
        "slug": "brand-cis",
        "title": "标志与 CIS 系统",
        "subtitle": "Brand Mark & CIS System",
        "category": "品牌设计",
        "render_pdf": Path("标志与CIS.pdf"),
        "pdf_pages": 8,
    },
    {
        "slug": "sichuan-opera",
        "title": "川剧变脸 · 视觉方案",
        "subtitle": "Sichuan Opera — Visual Proposal",
        "category": "文化视觉",
        "render_pdf": Path(r"C:\Users\Administrator\Desktop\川剧变脸.pdf"),
        "pages": [1, 4, 8, 9, 10, 19, 20, 22, 25],
    },
    {
        "slug": "yangtze-cableway",
        "title": "长江索道 · 视觉方案",
        "subtitle": "Yangtze Cableway — Visual Proposal",
        "category": "文化视觉",
        "render_pdf": Path(r"C:\Users\Administrator\Desktop\长江索道.pdf"),
        "pages": [1, 3, 20, 27, 35, 44, 53, 57, 64, 69, 74, 76, 86],
    },
    {
        "slug": "flower-gods",
        "title": "花神 · 插画系列",
        "subtitle": "Flower Deities — Illustration Series",
        "category": "插画",
        "source": Path("花神"),
        "pattern": "*.jpg",
    },
    {
        "slug": "postcards",
        "title": "花神明信片",
        "subtitle": "Flower Deity Postcards",
        "category": "编辑设计",
        "source": Path("花神明信片"),
        "pattern": "*.jpg",
        "limit": 8,
    },
    {
        "slug": "illustration",
        "title": "插画作品",
        "subtitle": "Illustration",
        "category": "插画",
        "source": Path("插画"),
        "pattern": "*.jpg",
    },
    {
        "slug": "dunhuang",
        "title": "寻梦敦煌",
        "subtitle": "Dunhuang Dreaming",
        "category": "插画",
        "source": Path("敦煌"),
        "pattern": "*.*",
        "extensions": {".jpg", ".png"},
    },
    {
        "slug": "solar-terms",
        "title": "二十四节气",
        "subtitle": "24 Solar Terms",
        "category": "文化视觉",
        "source": Path("二十四节气"),
        "pattern": "*.jpg",
    },
    {
        "slug": "infovis-tea",
        "title": "茶 · 信息可视化",
        "subtitle": "Tea — Information Visualization",
        "category": "信息可视化",
        "source": Path("信息可视化"),
        "pattern": "*.jpg",
    },
    {
        "slug": "papercut",
        "title": "剪纸 · 纸上舞蹈",
        "subtitle": "Paper-cut — Dance on Paper",
        "category": "文化视觉",
        "source": Path("剪纸"),
        "pattern": "*.jpg",
    },
    {
        "slug": "ganzhou",
        "title": "赣州 · 城市形象",
        "subtitle": "Ganzhou — City Identity",
        "category": "品牌设计",
        "source": Path("赣州"),
        "pattern": "*.jpg",
    },
    {
        "slug": "motion-animals",
        "title": "动物动态图形",
        "subtitle": "Animal Motion Graphics",
        "category": "动态影像",
        "source": Path("AN"),
        "pattern": "*.gif",
        "animate": True,
    },
]

# Images that follow the cursor on the first screen (exported smaller — they are preloaded).
HERO_TRAIL = {
    "slug": "hero-trail",
    "title": "首屏跟随图",
    "subtitle": "Hero Trail",
    "category": "hero",
    "hero_only": True,
    "source": Path(r"C:\Users\Administrator\Desktop\图片"),
    "files": [
        "Aa06-22-060-0090(2).jpg",
        "茶_画板 1.jpg",
        "芙蓉花.jpg",
        "剪纸魅力.jpg",
        "立春.jpg",
        "脐橙.jpg",
        "书籍7.jpg",
        "书籍8.jpg",
        "书籍11.jpg",
        "系列画2.jpg",
        "杏花.jpg",
    ],
    "max_edge": 1000,
    "quality": 78,
}


def collect_sources(project: dict) -> list[Path]:
    if "files" in project:
        source_dir = project["source"]
        found: list[Path] = []
        for name in project["files"]:
            candidate = source_dir / name
            if candidate.exists():
                found.append(candidate)
            else:
                print(f"  ! missing source image: {candidate}")
        return found

    source = SRC / project["source"]
    if not source.exists():
        return []
    extensions = project.get("extensions")
    files = [p for p in source.glob(project["pattern"]) if p.is_file()]
    if extensions:
        files = [p for p in files if p.suffix.lower() in extensions]
    files = [p for p in files if p.name not in project.get("skip", set())]
    files.sort(key=lambda p: natural_key(p.name))
    limit = project.get("limit")
    if limit and len(files) > limit:
        step = len(files) / limit
        files = [files[min(len(files) - 1, round(i * step))] for i in range(limit)]
    return files


def render_pdf_pages(pdf_path: Path, slug: str, pages: list[int] | None, limit: int) -> list[Path]:
    """Render selected pages (1-based) of a PDF, or the first `limit` pages."""
    try:
        import pypdfium2 as pdfium
    except ImportError:
        print("  ! pypdfium2 unavailable, skipping PDF")
        return []

    out_dir = REVIEW / "render" / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    doc = pdfium.PdfDocument(str(pdf_path))
    indexes = [p - 1 for p in pages] if pages else list(range(min(limit, len(doc))))
    count = len(indexes)
    for position, index in enumerate(indexes):
        if index < 0 or index >= len(doc):
            print(f"  ! page {index + 1} out of range in {pdf_path.name}")
            continue
        page = doc[index]
        bitmap = page.render(scale=2.2)
        image = bitmap.to_pil()
        target = out_dir / f"{slug}-src{position + 1:02d}-p{index + 1}.png"
        image.save(target)
        written.append(target)
        print(f"  rendered {pdf_path.name} page {index + 1} ({position + 1}/{count})")
    return written


def extract_pptx_images(pptx_path: Path, slug: str, slides: int) -> list[Path]:
    """Pull the largest embedded picture from each slide of a .pptx deck."""
    from pptx import Presentation
    from pptx.util import Emu  # noqa: F401

    out_dir = REVIEW / "render" / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    prs = Presentation(str(pptx_path))
    written: list[Path] = []

    for index, slide in enumerate(prs.slides):
        if index >= slides:
            break
        candidates = []
        for shape in slide.shapes:
            try:
                blob = shape.image.blob
            except Exception:  # noqa: BLE001  (not a picture shape)
                continue
            area = (shape.width or 0) * (shape.height or 0)
            candidates.append((area, shape.name, blob))
        if not candidates:
            continue
        candidates.sort(key=lambda item: item[0], reverse=True)
        _, name, blob = candidates[0]
        suffix = ".png" if blob[:4] == b"\x89PNG" else ".jpg"
        target = out_dir / f"{slug}-src{index + 1:02d}{suffix}"
        target.write_bytes(blob)
        written.append(target)
        print(f"  extracted {pptx_path.name} slide {index + 1} image ({name})")
    return written


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    REVIEW.mkdir(parents=True, exist_ok=True)
    manifest: list[dict] = []
    hero_items: list[dict] = []

    for project in PROJECTS + [HERO_TRAIL]:
        slug = project["slug"]
        print(f"{slug}:")

        if "render_pdf" in project:
            pdf_path = project["render_pdf"]
            if not pdf_path.is_absolute():
                pdf_path = SRC / pdf_path
            sources = render_pdf_pages(pdf_path, slug, project.get("pages"), project.get("pdf_pages", 8))
        elif "pptx" in project:
            sources = extract_pptx_images(SRC / project["pptx"], slug, project.get("pptx_slides", 10))
        else:
            sources = collect_sources(project)

        contact_sheet(sources, REVIEW / f"contact-{slug}.jpg")

        # drop previously exported files for this project so renames never leave strays
        for stale in list(ASSETS.glob(f"{slug}-*")):
            if stale.is_file() and stale.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
                stale.unlink()

        for index, source in enumerate(sources, start=1):
            hero_only = project.get("hero_only", False)
            animate = project.get("animate", False)
            extension = ".webp" if animate else ".jpg"
            dest = ASSETS / f"{slug}-{index:02d}{extension}"
            if animate:
                size = export_animation(source, dest)
            else:
                size = export_image(
                    source,
                    dest,
                    max_edge=project.get("max_edge", MAX_LONG_EDGE),
                    quality=project.get("quality", JPEG_QUALITY),
                )
            if not size:
                continue
            record = {
                "src": f"assets/{dest.name}",
                "width": size[0],
                "height": size[1],
                "project": project["title"],
                "subtitle": project["subtitle"],
                "category": project["category"],
                "slug": slug,
                "animate": animate,
                "origin": str(source.relative_to(SRC)) if SRC in source.parents else source.name,
            }
            (hero_items if hero_only else manifest).append(record)
        bucket = hero_items if project.get("hero_only") else manifest
        print(f"  exported {sum(1 for item in bucket if item['slug'] == slug)} items")

    manifest_path = ASSETS / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    hero_path = ASSETS / "hero-trail.json"
    hero_path.write_text(json.dumps(hero_items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nwrote {manifest_path.name} with {len(manifest)} items")
    print(f"wrote {hero_path.name} with {len(hero_items)} hero images")


if __name__ == "__main__":
    main()
