#!/usr/bin/env python3
"""
Docs Microservice — Markdown documentation server with TOC navigation.

Usage:
    python server.py [--port PORT] [--host HOST]

Serves documentation from the docs/ folder with:
- Interactive sidebar navigation from toc.yaml
- Markdown-to-HTML rendering
- Previous/Next page navigation
- Responsive design
"""

import argparse
import os
import re
import sys
from pathlib import Path
from urllib.parse import quote, unquote

import yaml
from markdown import markdown
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "content"  # markdown files live here
TOC_FILE = BASE_DIR / "toc.yaml"

# ---------------------------------------------------------------------------
# Markdown helpers
# ---------------------------------------------------------------------------

# Custom markdown extensions for navigation links
# We support: << [Label](/doc/page) | [Label](/doc/page) >>
NAV_PATTERN = re.compile(
    r"<<\s*\[([^\]]+)\]\((/doc/[^\)]+)\)\s*\|\s*\[([^\]]+)\]\((/doc/[^\)]+)\)\s*>>"
)


def _convert_nav_link(match: re.Match) -> str:
    """Convert << [Prev](/doc/x) | [Next](/doc/y) >> into HTML buttons."""
    prev_label, prev_url = match.group(1), match.group(2)
    next_label, next_url = match.group(3), match.group(4)
    return (
        f'<div class="nav-links">'
        f'<a href="{prev_url}" class="nav-link prev">&larr; {prev_label}</a>'
        f'<a href="{next_url}" class="nav-link next">{next_label} &rarr;</a>'
        f'</div>'
    )


def render_markdown(text: str) -> str:
    """Render markdown text to HTML, converting nav links."""
    # Replace nav link pattern before markdown processing
    text = NAV_PATTERN.sub(_convert_nav_link, text)
    html = markdown(
        text,
        extensions=[
            "tables",
            "fenced_code",
            "codehilite",
            "toc",
            "attr_list",
            "md_in_html",
        ],
    )
    return html


# ---------------------------------------------------------------------------
# TOC loader
# ---------------------------------------------------------------------------

def load_toc(path: Path = TOC_FILE) -> list[dict]:
    """Load and validate the table of contents from toc.yaml."""
    if not path.exists():
        print(f"[ERROR] toc.yaml not found at {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        toc = yaml.safe_load(f)
    return toc


def flatten_toc(toc: list[dict]) -> list[dict]:
    """Flatten nested TOC into a list of {title, file, url} dicts."""
    items = []
    for entry in toc:
        # Use full relative path without .md extension as URL
        file_stem = str(Path(entry['file']).with_suffix(''))
        url = f"/doc/{file_stem}"
        items.append({"title": entry["title"], "file": entry["file"], "url": url})
        for child in entry.get("children", []):
            child_stem = str(Path(child['file']).with_suffix(''))
            child_url = f"/doc/{child_stem}"
            items.append({"title": child["title"], "file": child["file"], "url": child_url})
    return items


def find_page_index(url: str, items: list[dict]) -> int:
    """Find the index of a page by URL."""
    for i, item in enumerate(items):
        if item["url"] == url:
            return i
    return 0


def get_prev_next(url: str, items: list[dict]):
    """Return (prev, next) page info for the given URL."""
    idx = find_page_index(url, items)
    prev = items[idx - 1] if idx > 0 else None
    nxt = items[idx + 1] if idx < len(items) - 1 else None
    return prev, nxt


# ---------------------------------------------------------------------------
# Flask application
# ---------------------------------------------------------------------------

app = Flask(__name__)


@app.template_filter("filestem")
def filestem_filter(filepath: str) -> str:
    """Extract just the filename stem from a path like 'modules/map_generator.md' -> 'map_generator'."""
    return Path(filepath).stem

# Global TOC — reloaded on each request for hot-reload feel
def get_toc_data():
    toc = load_toc()
    flat = flatten_toc(toc)
    return toc, flat


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Redirect to the first page in the TOC."""
    toc, flat = get_toc_data()
    if flat:
        return redirect(flat[0]["url"])
    return "No documentation found.", 404


@app.route("/doc/<page_name>")
def serve_doc(page_name: str):
    """Render a markdown page as HTML."""
    toc, flat = get_toc_data()

    # Debug: print what we're looking for
    print(f"[DEBUG] Looking for page: '{page_name}'", file=sys.stderr)

    # Resolve the markdown file (files live in content/)
    # Match by full relative path without .md extension
    md_file = None
    for item in flat:
        # Strip /doc/ prefix from URL to get relative path
        item_path = item["url"].replace("/doc/", "")
        if item_path == page_name:
            md_file = BASE_DIR / "content" / item["file"]
            print(f"[DEBUG] MATCHED: {item['file']} -> {md_file}", file=sys.stderr)
            break

    if md_file is None or not md_file.exists():
        print(f"[DEBUG] NOT FOUND: md_file={md_file}, exists={md_file.exists() if md_file else 'N/A'}", file=sys.stderr)
        return render_template("404.html", page_name=page_name), 404

    # Read and render markdown
    with open(md_file, encoding="utf-8") as f:
        md_content = f.read()

    html_content = render_markdown(md_content)
    page_title = Path(md_file.stem).name.replace("_", " ").title()

    # Get prev/next
    page_url = f"/doc/{page_name}"
    prev_page, next_page = get_prev_next(page_url, flat)

    return render_template(
        "docs.html",
        content=html_content,
        title=page_title,
        toc=toc,
        flat_toc=flat,
        prev_page=prev_page,
        next_page=next_page,
        current_url=page_url,
    )


@app.route("/api/toc")
def api_toc():
    """API endpoint returning the TOC as JSON."""
    toc, flat = get_toc_data()
    return jsonify({"toc": toc, "flat": flat})


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Docs Microservice")
    parser.add_argument("--port", type=int, default=5001, help="Port to serve on (default: 5001)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    args = parser.parse_args()

    print(f"  Docs Microservice")
    print(f"  {'=' * 40}")
    print(f"  Serving docs from: {DOCS_DIR}")
    print(f"  TOC file: {TOC_FILE}")
    print(f"  Opening: http://{args.host}:{args.port}")
    print(f"  {'=' * 40}")

    app.run(host=args.host, port=args.port, debug=True)


if __name__ == "__main__":
    main()
