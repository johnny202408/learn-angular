"""Build the book PDF from Markdown chapters.

Usage:
    python build.py                 # writes build/learn_angular.pdf
    python build.py --html          # also emit build/learn_angular.html for previewing
    python build.py --chapter 05    # build a single chapter (useful while drafting)

Chapters live in content/ as NN_slug.md and are assembled in filename order.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import markdown
import yaml
from weasyprint import CSS, HTML

ROOT = Path(__file__).parent
CONTENT_DIR = ROOT / "content"
BUILD_DIR = ROOT / "build"
STYLE = ROOT / "style.css"
METADATA = ROOT / "metadata.yaml"

MD_EXTENSIONS = [
    "fenced_code",
    "codehilite",
    "tables",
    "toc",
    "attr_list",
    "def_list",
    "footnotes",
    "sane_lists",
]

MD_EXT_CONFIGS = {
    "codehilite": {"guess_lang": False, "css_class": "highlight"},
    "toc": {"title": "Contents", "toc_depth": "2-3"},
}


def load_metadata() -> dict:
    if METADATA.exists():
        return yaml.safe_load(METADATA.read_text()) or {}
    return {"title": "Learn Angular by Building Compass", "author": ""}


def render_chapter(path: Path) -> str:
    md = markdown.Markdown(extensions=MD_EXTENSIONS, extension_configs=MD_EXT_CONFIGS)
    body = md.convert(path.read_text(encoding="utf-8"))
    # Wrap each chapter in a section so CSS can break-before it.
    return f'<section class="chapter" data-source="{path.name}">\n{body}\n</section>\n'


def assemble_html(chapter_paths: list[Path], meta: dict) -> str:
    parts = [render_chapter(p) for p in chapter_paths]
    body = "\n".join(parts)
    title = meta.get("title", "Untitled")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
</head>
<body>
{body}
</body>
</html>
"""


def select_chapters(chapter_filter: str | None) -> list[Path]:
    all_chapters = sorted(CONTENT_DIR.glob("*.md"))
    if not all_chapters:
        sys.exit(f"No chapters found in {CONTENT_DIR}")
    if chapter_filter is None:
        return all_chapters
    matched = [p for p in all_chapters if re.match(rf"^{chapter_filter}[_\.]", p.name)]
    if not matched:
        sys.exit(f"No chapter matches prefix '{chapter_filter}'")
    return matched


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", action="store_true", help="Also emit HTML for previewing")
    parser.add_argument("--chapter", help="Build only chapters starting with this prefix (e.g. 01)")
    args = parser.parse_args()

    BUILD_DIR.mkdir(exist_ok=True)
    meta = load_metadata()
    chapters = select_chapters(args.chapter)

    html_str = assemble_html(chapters, meta)
    stem = "learn_angular" if args.chapter is None else f"learn_angular_ch{args.chapter}"

    if args.html:
        (BUILD_DIR / f"{stem}.html").write_text(html_str, encoding="utf-8")

    css = CSS(filename=str(STYLE)) if STYLE.exists() else None
    stylesheets = [css] if css else []
    HTML(string=html_str, base_url=str(ROOT)).write_pdf(
        target=str(BUILD_DIR / f"{stem}.pdf"),
        stylesheets=stylesheets,
    )
    print(f"Wrote {BUILD_DIR / f'{stem}.pdf'}")


if __name__ == "__main__":
    main()
