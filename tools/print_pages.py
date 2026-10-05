#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["beautifulsoup4==4.12.3"]
# ///
"""Render published pages of docs.fpgas.online to one PDF for printing.

    uv run tools/print_pages.py --paper A4 --title "Wiring an Acorn" \\
        --output acorn.pdf boards/acorn/wiring sites/ps1

Each PAGE is a path under the published site, without ".html". The pages are
fetched from the live site, so the PDF holds what is published and nothing
else: to change the text, change the page and publish it.

A page may be cut down to some of its sections, named by their anchors:

    boards/acorn/wiring#bill-of-materials,raspberry-pi-5

keeps the page's title, the text before its first section, and those sections
(with everything inside them), in the page's own order. A section kept only
for one inside it keeps just its heading. A section that is not on the page
stops the run.

Every chapter starts on a new sheet under a line giving its source URL, the
commit the site was built from and the date it was fetched; every sheet has
the commit and a page number in its foot. An image wider than WIDE_PX is put
on a landscape sheet of its own, at the full width of the paper, in its vector
form when the page links one. --append puts existing PDFs (label sheets) after
the printed pages unchanged; they must already be on the right paper.

Needs google-chrome-stable, which does the printing, and pdfunite for --append.
"""

from __future__ import annotations

import argparse
import base64
import datetime
import html
import json
import mimetypes
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup, Tag

SITE = "https://docs.fpgas.online/en/latest/"
ADDONS = (
    "https://docs.fpgas.online/_/addons/?client-version=0.22.0&api-version=1.0.0"
    "&project-slug=fpgasonline-docs&version-slug=latest"
)
# The site answers 403 to urllib's own user agent.
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) fpgas.online-docs print_pages"}
CHROME = "google-chrome-stable"
PAPERS = {"A4": "A4", "Letter": "letter"}
# An image at least this many pixels wide (a wiring sheet) gets a landscape
# sheet to itself; anything narrower stays in the text.
WIDE_PX = 1200
HEADINGS = ("h1", "h2", "h3", "h4", "h5", "h6")

CSS = """
@page {
  size: %(paper)s portrait;
  margin: 16mm 15mm 18mm 15mm;
  @bottom-left { content: "%(foot)s"; font: 8pt sans-serif; color: #444; }
  @bottom-right { content: "Page " counter(page) " of " counter(pages);
                  font: 8pt sans-serif; color: #444; }
}
@page wide { size: %(paper)s landscape; margin: 10mm 10mm 14mm 10mm; }
html { font: 10pt/1.4 "DejaVu Sans", "Liberation Sans", Arial, sans-serif; color: #000; }
body { margin: 0; }
.cover { break-after: page; padding-top: 30mm; }
.cover small { color: #444; word-break: break-all; }
.cover .admonition { margin-top: 8mm; }
.cover h1 { font-size: 26pt; border: 0; }
.cover li { margin: 2mm 0; }
.chapter { break-before: page; }
.source { font-size: 8pt; color: #333; border-bottom: 0.4pt solid #888;
          padding-bottom: 1.5mm; margin-bottom: 4mm; word-break: break-all; }
h1 { font-size: 20pt; margin: 0 0 4mm; }
h2 { font-size: 15pt; margin: 7mm 0 2.5mm; border-bottom: 0.6pt solid #000; }
h3 { font-size: 12pt; margin: 5mm 0 2mm; }
h4 { font-size: 10.5pt; margin: 4mm 0 1.5mm; }
h1, h2, h3, h4 { break-after: avoid; line-height: 1.2; }
p { margin: 0 0 2.5mm; orphans: 3; widows: 3; }
ul, ol { margin: 0 0 2.5mm; padding-left: 6mm; }
a { color: #000; text-decoration: underline; text-decoration-color: #999; }
code, pre { font-family: "DejaVu Sans Mono", "Liberation Mono", monospace; }
code { font-size: 8.8pt; background: #eee; padding: 0 0.6mm; }
pre { font-size: 8pt; line-height: 1.3; border: 0.4pt solid #888; background: #f6f6f6;
      padding: 2mm; margin: 0 0 3mm; white-space: pre-wrap; overflow-wrap: anywhere;
      break-inside: avoid; }
pre code { background: none; padding: 0; }
table { border-collapse: collapse; width: calc(100%% - 1pt); margin: 0 0 3.5mm; font-size: 8.8pt; }
th, td { border: 0.4pt solid #555; padding: 1mm 1.6mm; text-align: left; vertical-align: top; }
th { background: #ddd; }
thead { display: table-header-group; }
tr { break-inside: avoid; }
.admonition { border: 1.2pt solid #000; padding: 2mm 3mm; margin: 0 0 3.5mm; break-inside: avoid; }
.admonition-title { font-weight: bold; text-transform: uppercase; margin-bottom: 1mm; }
.admonition p:last-child { margin-bottom: 0; }
img { max-width: 100%%; }
.wide { page: wide; break-before: page; break-after: page; break-inside: avoid;
        margin: 0; text-align: center; }
.wide img { width: 100%%; max-height: 172mm; object-fit: contain; }
.wide figcaption { font-size: 8pt; color: #333; text-align: left; }
"""


def fetch(url: str) -> tuple[bytes, str]:
    """The body and content type at url. Any failure stops the run."""
    request = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.read(), response.headers.get_content_type()
    except urllib.error.URLError as error:
        raise SystemExit(f"cannot fetch {url}: {error}") from error


def built_commit() -> str:
    """The commit the published site was built from, as Read the Docs reports it."""
    body, _ = fetch(ADDONS)
    try:
        return json.loads(body)["builds"]["current"]["commit"]
    except (KeyError, TypeError, ValueError) as error:
        raise SystemExit(f"cannot read the built commit from {ADDONS}: {error!r}") from error


def parse_spec(spec: str) -> tuple[str, list[str]]:
    """Split "path#a,b" into the page path and the anchors to keep."""
    path, _, wanted = spec.partition("#")
    path = path.strip("/").removesuffix(".html")
    if not path or ".." in path.split("/"):
        raise SystemExit(f"not a page path: {spec!r}")
    return path, [anchor for anchor in wanted.split(",") if anchor]


def page_url(path: str) -> str:
    return urllib.parse.urljoin(SITE, path + ".html")


def article(page: str, url: str) -> Tag:
    """The content of a published page, without the theme around it."""
    body = BeautifulSoup(page, "html.parser").select_one("article[role=main]")
    if body is None:
        raise SystemExit(f"{url}: no <article role=main>; is this a page of the site?")
    for junk in body.select("a.headerlink, button, script, style, .toc-drawer, .related-pages"):
        junk.decompose()
    return body


def keep_sections(body: Tag, wanted: list[str], url: str) -> None:
    """Cut body down to the wanted sections and the page's lead text."""
    missing = [anchor for anchor in wanted if body.find("section", id=anchor) is None]
    if missing:
        raise SystemExit(f"{url}: no section {', '.join('#' + m for m in missing)}")
    kept = set(wanted)

    def prune(section: Tag) -> bool:
        """Drop what is not wanted under section; say whether anything is left."""
        if section.get("id") in kept:
            return True
        children = [child for child in section.find_all("section", recursive=False)]
        alive = [child for child in children if prune(child)]
        if not alive:
            return False
        # Kept only for what is inside it: its heading stays to say where the
        # wanted sections sit, its own text and its other sections go.
        for child in list(section.children):
            if not isinstance(child, Tag):
                child.extract()
            elif child not in alive and child.name not in HEADINGS:
                child.decompose()
        return True

    # The page's own section keeps its lead text whatever is wanted under it.
    top = body.find("section")
    for section in top.find_all("section", recursive=False):
        if not prune(section):
            section.decompose()


def absolute_links(body: Tag, url: str) -> None:
    """Point every link at the published site, so none is relative to the PDF."""
    for link in body.find_all("a", href=True):
        link["href"] = urllib.parse.urljoin(url, link["href"])


def data_uri(url: str) -> str:
    content, kind = fetch(url)
    if kind in ("application/octet-stream", "text/plain"):
        kind = mimetypes.guess_type(urllib.parse.urlparse(url).path)[0] or kind
    return f"data:{kind};base64,{base64.b64encode(content).decode()}"


def png_width(content: bytes) -> int | None:
    if content[:8] == b"\x89PNG\r\n\x1a\n":
        return int.from_bytes(content[16:20], "big")
    return None


def inline_images(body: Tag, url: str, soup: BeautifulSoup) -> None:
    """Embed every image; give a wide one a landscape sheet, as vector if linked."""
    for image in body.find_all("img", src=True):
        source = urllib.parse.urljoin(url, image["src"])
        content, kind = fetch(source)
        width = png_width(content)
        link = image.find_parent("a", href=True)
        vector = link["href"] if link and link["href"].lower().endswith(".svg") else None
        if vector:
            image["src"] = data_uri(urllib.parse.urljoin(url, vector))
        else:
            image["src"] = f"data:{kind};base64,{base64.b64encode(content).decode()}"
        for attribute in ("width", "height", "style", "srcset"):
            image.attrs.pop(attribute, None)
        if vector or (width is not None and width >= WIDE_PX):
            figure = soup.new_tag("figure", attrs={"class": "wide"})
            caption = soup.new_tag("figcaption")
            caption.string = f"{image.get('alt', '')} ({vector or source})".strip()
            holder = link or image
            # A block cannot sit inside the paragraph that held the image.
            parent = holder.parent
            target = parent if parent.name == "p" and not parent.get_text(strip=True) else holder
            target.replace_with(figure)
            figure.append(image)
            figure.append(caption)


def chapter(spec: str, commit: str, fetched: str) -> tuple[str, str]:
    """The title and the printable HTML of one page."""
    path, wanted = parse_spec(spec)
    url = page_url(path)
    page, _ = fetch(url)
    soup = BeautifulSoup("", "html.parser")
    body = article(page.decode("utf-8"), url)
    if wanted:
        keep_sections(body, wanted, url)
    absolute_links(body, url)
    inline_images(body, url, soup)
    heading = body.find("h1")
    title = heading.get_text(strip=True) if heading else path
    note = f"Source: {url}"
    if wanted:
        note += " (sections: " + ", ".join(wanted) + ")"
    note += f" · docs commit {commit[:10]} · fetched {fetched}"
    return title, (
        f'<div class="chapter"><div class="source">{html.escape(note)}</div>'
        f"{body.decode_contents()}</div>"
    )


def notes(text: str) -> str:
    """A box from a notes file: its first line is the heading, each later line an item."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        raise SystemExit("a notes file needs a heading line")
    items = "".join(f"<li>{html.escape(line)}</li>" for line in lines[1:])
    return (
        f'<div class="admonition"><p class="admonition-title">{html.escape(lines[0])}</p>'
        f"<ul>{items}</ul></div>"
    )


def document(title: str, paper: str, specs: list[str], cover_notes: str = "", last_sheet: str = "") -> str:
    commit = built_commit()
    fetched = datetime.date.today().isoformat()
    chapters = [chapter(spec, commit, fetched) for spec in specs]
    foot = f"{title} · docs.fpgas.online · commit {commit[:10]} · {fetched}".replace('"', "'")
    css = CSS % {"paper": PAPERS[paper], "foot": foot}
    contents = "".join(
        f"<li>{html.escape(name)} <small>({html.escape(spec)})</small></li>"
        for spec, (name, _) in zip(specs, chapters)
    )
    cover = (
        f'<div class="cover"><h1>{html.escape(title)}</h1>'
        f"<p>Printed from the pages published at {html.escape(SITE)}, "
        f"built from commit {html.escape(commit)} of fpgas-online/fpgas.online-docs, "
        f"fetched {fetched}. The published pages are the current ones; this is a copy.</p>"
        f"<ol>{contents}</ol>{notes(cover_notes) if cover_notes else ''}</div>"
    )
    last = f'<div class="chapter">{notes(last_sheet)}</div>' if last_sheet else ""
    return (
        f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
        f"<title>{html.escape(title)}</title><style>{css}</style></head>"
        f"<body>{cover}{''.join(text for _, text in chapters)}{last}</body></html>"
    )


def print_pdf(page: Path, output: Path) -> None:
    chrome = shutil.which(CHROME)
    if chrome is None:
        raise SystemExit(f"{CHROME} is not installed; it does the printing")
    with tempfile.TemporaryDirectory(dir=output.parent) as profile:
        subprocess.run(
            [
                chrome,
                "--headless",
                "--disable-gpu",
                f"--user-data-dir={profile}",
                "--no-pdf-header-footer",
                f"--print-to-pdf={output}",
                page.resolve().as_uri(),
            ],
            check=True,
            timeout=300,
            # Printing needs nothing from the desktop session. Given a session
            # bus, Chrome waits minutes on it before it exits; given an address
            # it cannot use, it logs that and prints in seconds.
            env={**os.environ, "DBUS_SESSION_BUS_ADDRESS": "disabled:"},
        )
    if not output.is_file() or output.stat().st_size == 0:
        raise SystemExit(f"{CHROME} wrote no PDF at {output}")


def append_pdfs(output: Path, extra: list[Path]) -> None:
    """Put the extra PDFs (label sheets, say) after the printed pages, as they are."""
    joiner = shutil.which("pdfunite")
    if joiner is None:
        raise SystemExit("pdfunite (poppler-utils) is not installed; --append needs it")
    for path in extra:
        if not path.is_file():
            raise SystemExit(f"--append {path}: no such file")
    printed = output.with_suffix(".printed.pdf")
    output.rename(printed)
    try:
        subprocess.run([joiner, str(printed), *map(str, extra), str(output)], check=True)
    finally:
        printed.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--paper", choices=sorted(PAPERS), required=True)
    parser.add_argument("--title", required=True, help="printed on the cover and in each foot")
    parser.add_argument("--output", type=Path, required=True, help="the PDF to write")
    parser.add_argument("--keep-html", action="store_true", help="leave the joined page beside the PDF")
    parser.add_argument("--append", type=Path, action="append", default=[], metavar="PDF",
                        help="a PDF to put after the printed pages, unchanged (may be repeated)")
    parser.add_argument("--cover-notes", type=Path, metavar="FILE",
                        help="a box for the cover: the file's first line is its heading, each later line an item")
    parser.add_argument("--last-sheet", type=Path, metavar="FILE",
                        help="a box on a sheet of its own after the pages, in the same form")
    parser.add_argument("pages", nargs="+", metavar="PAGE", help='e.g. "boards/acorn/wiring#raspberry-pi-5"')
    args = parser.parse_args()

    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    joined = output.with_suffix(".html")
    cover_notes = args.cover_notes.read_text(encoding="utf-8") if args.cover_notes else ""
    last_sheet = args.last_sheet.read_text(encoding="utf-8") if args.last_sheet else ""
    joined.write_text(
        document(args.title, args.paper, args.pages, cover_notes, last_sheet), encoding="utf-8"
    )
    try:
        print_pdf(joined, output)
    finally:
        if not args.keep_html:
            joined.unlink()
    if args.append:
        append_pdfs(output, args.append)
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
