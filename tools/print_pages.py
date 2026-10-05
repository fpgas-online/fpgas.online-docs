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
the commit and a page number in its foot. Links are numbered and their
addresses listed at the end of the chapter, because paper cannot follow them.
An image drawn at least WIDE_PX wide (a PNG of twice that, since the site's
PNGs are rendered at double size) stays in the text at the column's width as
an overview; the line under it names the landscape sheet at the end of the
chapter where it is printed once at the full width of the paper (in vector
form when the page links one).
--append puts existing PDFs (label sheets) after the printed pages unchanged
and not renumbered; every page of them must already be on the chosen paper,
either way up, or the run stops.

The PDF is printed beside the output under a ".part" name and takes the output's
name only after it is checked, so a failed run leaves no PDF that looks new.

Needs google-chrome-stable, which does the printing, and from poppler-utils:
pdftotext and pdfinfo to read the sheet numbers back, and pdfunite for --append.
"""

from __future__ import annotations

import argparse
import base64
import datetime
import hashlib
import html
import http.client
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup, Comment, Tag

SITE = "https://docs.fpgas.online/en/latest/"
ADDONS = (
    "https://docs.fpgas.online/_/addons/?client-version=0.22.0&api-version=1.0.0"
    "&project-slug=fpgasonline-docs&version-slug=latest"
)
# The site answers 403 to urllib's own user agent.
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) fpgas.online-docs print_pages"}
CHROME = "google-chrome-stable"
PAPERS = {"A4": "A4", "Letter": "letter"}
# Sheet sizes in points (width, height, portrait), for checking appended PDFs.
PAPER_POINTS = {"A4": (595.28, 841.89), "Letter": (612.0, 792.0)}
# An image drawn at least this many pixels wide (a wiring sheet) gets a
# landscape sheet to itself; anything narrower stays in the text.
WIDE_PX = 1200
# The site's PNGs are rendered at twice the size they are drawn at, so a PNG
# (or any other raster) is that wide only from twice as many pixels. A step
# picture drawn 780 px wide is a 1560 px PNG and belongs in the text.
RASTER_WIDE_PX = 2 * WIDE_PX
# A listing with more lines than this may run over the end of a sheet.
LONG_LINES = 18
# A table with at most this many rows is kept on one sheet.
SHORT_ROWS = 12
# Where a chapter's sheet number goes in the cover's list, once it is known.
SHEET_PLACE = "<!--sheet-of-chapter-%d-->"
SHEET_PLACE_RE = r"<!--sheet-of-chapter-(\d+)-->"
# Where the number of a wide picture's own sheet goes, in the line under its small copy in the text.
WIDE_PLACE = "sheet-of-wide-%s"
WIDE_PLACE_RE = r"<!--sheet-of-wide-([0-9a-f]+)-->"
WIDE_SHEET_RE = r'<figure class="wide" data-wide="([0-9a-f]+)">'
# This many addresses stay on the sheet of the "Links in this chapter" heading.
LINKS_WITH_HEADING = 4
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
.cover small { color: #444; }
.cover .admonition { margin-top: 8mm; }
.cover h1 { font-size: 26pt; border: 0; }
.cover li { margin: 2mm 0; }
.chapter { break-before: page; }
.source { font-size: 8pt; color: #333; border-bottom: 0.4pt solid #888;
          padding-bottom: 1.5mm; margin-bottom: 4mm; overflow-wrap: anywhere; }
h1 { font-size: 20pt; margin: 0 0 4mm; }
h2 { font-size: 15pt; margin: 7mm 0 2.5mm; border-bottom: 0.6pt solid #000; }
h3 { font-size: 12pt; margin: 5mm 0 2mm; }
h4 { font-size: 10.5pt; margin: 4mm 0 1.5mm; }
h5, h6 { font-size: 10pt; margin: 3mm 0 1.5mm; }
h1, h2, h3, h4, h5, h6 { break-after: avoid; line-height: 1.2; }
p { margin: 0 0 2.5mm; orphans: 3; widows: 3; }
ul, ol { margin: 0 0 2.5mm; padding-left: 6mm; }
a { color: #000; text-decoration: underline; text-decoration-color: #999; }
code, pre { font-family: "DejaVu Sans Mono", "Liberation Mono", monospace; }
code { font-size: 8.8pt; background: #eee; padding: 0 0.6mm; overflow-wrap: anywhere; }
pre { font-size: 8pt; line-height: 1.3; border: 0.4pt solid #888; background: #f6f6f6;
      padding: 2mm; margin: 0 0 3mm; white-space: pre-wrap; overflow-wrap: anywhere;
      break-inside: avoid; }
pre.long { break-inside: auto; }
pre code { background: none; padding: 0; }
sup.ref { font-size: 6.5pt; line-height: 0; color: #333; }
.links .together { break-inside: avoid; }
.links ol { margin-bottom: 0; }
.links ol { font-size: 8pt; overflow-wrap: anywhere; }
.inflow { margin: 0 0 3.5mm; break-inside: avoid; }
.inflow figcaption { font-style: italic; }
table.short { break-inside: avoid; }
table { border-collapse: collapse; width: calc(100%% - 1pt); margin: 0 0 3.5mm; font-size: 8.8pt; }
/* A table that ran over a sheet's end loses its own bottom margin; its wrapper keeps the gap. */
.table-wrapper { margin: 0 0 3.5mm; }
.table-wrapper table { margin: 0; }
th, td { border: 0.4pt solid #555; padding: 1mm 1.6mm; text-align: left; vertical-align: top; }
th { background: #ddd; }
/* A cell whose longest word is wider than its column would push the table past
   the sheet's edge, and Chrome then shrinks every sheet of the PDF to fit it.
   A cell may break a word; a heading may not, so no column is narrower than
   the words of its heading. */
td { overflow-wrap: anywhere; }
thead { display: table-header-group; }
tr { break-inside: avoid; }
.admonition { border: 1.2pt solid #000; padding: 2mm 3mm; margin: 0 0 3.5mm; break-inside: avoid; }
.admonition-title { font-weight: bold; text-transform: uppercase; margin-bottom: 1mm; }
.admonition p:last-child { margin-bottom: 0; }
img { max-width: 100%%; }
/* A picture is never cut by the end of a sheet, and leaves room for its step's words above it. */
.picture { break-inside: avoid; text-align: center; }
.picture img { max-height: 200mm; }
.step { break-inside: avoid; }
.wide { page: wide; break-before: page; break-inside: avoid;
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
    except (OSError, http.client.HTTPException) as error:
        # URLError, HTTPError and TimeoutError are all OSError.
        raise SystemExit(f"cannot fetch {url}: {error!r}") from error


def built_commit() -> str:
    """The commit the published site was built from, as Read the Docs reports it."""
    body, _ = fetch(ADDONS)
    try:
        commit = json.loads(body)["builds"]["current"]["commit"]
    except (KeyError, TypeError, ValueError) as error:
        raise SystemExit(f"cannot read the built commit from {ADDONS}: {error!r}") from error
    if not isinstance(commit, str) or not commit.strip():
        raise SystemExit(f"the built commit from {ADDONS} is not a commit: {commit!r}")
    return commit


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
    # A comment of the page must never look like one of our sheet places.
    for comment in body.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    return body


def keep_sections(body: Tag, wanted: list[str], url: str) -> None:
    """Cut body down to the wanted sections and the page's lead text."""
    missing = [anchor for anchor in wanted if body.find("section", id=anchor) is None]
    if missing:
        raise SystemExit(f"{url}: no section {', '.join('#' + m for m in missing)}")
    top = body.find("section")
    if top.get("id") in wanted:
        raise SystemExit(
            f"{url}: #{top['id']} is the whole page, not a section of it; "
            "give the page without sections instead"
        )
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
    for section in top.find_all("section", recursive=False):
        if not prune(section):
            section.decompose()
    # A wanted section that does not hang from the page's own section through
    # sections alone was pruned away: stop rather than print less than asked.
    lost = [anchor for anchor in wanted if body.find("section", id=anchor) is None]
    if lost:
        raise SystemExit(f"{url}: cannot keep {', '.join('#' + m for m in lost)}: it is not nested in sections only")


def absolute_links(body: Tag, url: str) -> None:
    """Point every link at the published site, so none is relative to the PDF."""
    for link in body.find_all("a", href=True):
        link["href"] = urllib.parse.urljoin(url, link["href"])


def content_kind(url: str, kind: str) -> str:
    """The content type to trust: a server's vague answer yields to the file's extension."""
    if kind in ("application/octet-stream", "text/plain"):
        return mimetypes.guess_type(urllib.parse.urlparse(url).path)[0] or kind
    return kind


def as_data_uri(content: bytes, kind: str) -> str:
    return f"data:{kind};base64,{base64.b64encode(content).decode()}"


def data_uri(url: str) -> str:
    content, kind = fetch(url)
    return as_data_uri(content, content_kind(url, kind))


def png_width(content: bytes) -> int | None:
    if content[:8] == b"\x89PNG\r\n\x1a\n":
        return int.from_bytes(content[16:20], "big")
    return None


def jpeg_width(content: bytes) -> int | None:
    """The width in the first start-of-frame marker of a JPEG."""
    if content[:2] != b"\xff\xd8":
        return None
    position = 2
    while position + 4 <= len(content):
        if content[position] != 0xFF:
            return None
        marker = content[position + 1]
        if marker == 0xFF:  # fill byte
            position += 1
            continue
        if marker in (0x01, *range(0xD0, 0xDA)):  # markers with no length
            position += 2
            continue
        length = int.from_bytes(content[position + 2:position + 4], "big")
        if marker in range(0xC0, 0xD0) and marker not in (0xC4, 0xC8, 0xCC):
            if position + 9 > len(content):
                return None
            return int.from_bytes(content[position + 7:position + 9], "big")
        position += 2 + length
    return None


def gif_width(content: bytes) -> int | None:
    if content[:6] in (b"GIF87a", b"GIF89a") and len(content) >= 10:
        return int.from_bytes(content[6:8], "little")
    return None


def svg_width(content: bytes) -> int | None:
    """The width an SVG states: its width attribute, else its viewBox."""
    root = re.search(rb"<svg\b[^>]*>", content)
    if root is None:
        return None
    tag = root.group(0).decode("utf-8", "replace")
    width = re.search(r"""\swidth\s*=\s*["']\s*([0-9.]+)\s*(px)?\s*["']""", tag)
    if width:
        return round(float(width.group(1)))
    box = re.search(r"""\sviewBox\s*=\s*["']\s*[-0-9.]+[\s,]+[-0-9.]+[\s,]+([0-9.]+)[\s,]+[0-9.]+\s*["']""", tag)
    if box:
        return round(float(box.group(1)))
    return None


def image_width(content: bytes, kind: str) -> int | None:
    """The pixel width of a PNG, JPEG, GIF or SVG; None when it cannot be read."""
    if kind == "image/svg+xml":
        return svg_width(content)
    return png_width(content) or jpeg_width(content) or gif_width(content)


def place_figure(movable: Tag, figure: Tag, lifted: dict[int, Tag]) -> None:
    """Put figure where movable (an image, or the link holding only it) was, and movable in figure.

    A figure cannot sit inside a paragraph: it goes after the paragraph, and
    the paragraph's other text stays.
    """
    if movable.find_parent([*HEADINGS, "pre", "code"]) is not None:
        raise SystemExit(f"cannot print a wide image inside a heading or a listing: {str(movable)[:80]}")
    paragraph = movable.find_parent("p")
    if paragraph is None:
        movable.replace_with(figure)
    else:
        movable.extract()
        # Several images of one paragraph keep their order after it.
        lifted.get(id(paragraph), paragraph).insert_after(figure)
        lifted[id(paragraph)] = figure
        if not paragraph.get_text(strip=True) and paragraph.find("img") is None:
            paragraph.decompose()
    figure.append(movable)


def inline_images(body: Tag, url: str, soup: BeautifulSoup, chapter: int = 0) -> list[Tag]:
    """Embed every image, as vector when the page links one.

    A wide image stays in the text at the width of the column, as an overview,
    over a line saying which sheet holds it at full size; the sheets returned
    hold it at the full width of a landscape page, once however often the
    chapter shows it.
    """
    sheets = []
    made: dict[str, tuple[Tag, bool, str]] = {}
    lifted: dict[int, Tag] = {}
    for image in body.find_all("img", src=True):
        source = urllib.parse.urljoin(url, image["src"])
        content, kind = fetch(source)
        kind = content_kind(source, kind)
        width = image_width(content, kind)
        if width is None:
            raise SystemExit(f"{source}: cannot read the type or width of this image (content type {kind})")
        link = image.find_parent("a", href=True)
        vector = None
        vector_width = None
        if link is not None:
            target = urllib.parse.urljoin(url, link["href"])
            if urllib.parse.urlparse(target).path.lower().endswith(".svg"):
                vector = target
        if vector:
            svg, svg_kind = fetch(vector)
            svg_kind = content_kind(vector, svg_kind)
            if svg_kind != "image/svg+xml":
                raise SystemExit(f"{vector}: linked as an SVG but served as {svg_kind}")
            vector_width = svg_width(svg)
            image["src"] = as_data_uri(svg, svg_kind)
        else:
            image["src"] = as_data_uri(content, kind)
        for attribute in ("width", "height", "style", "srcset"):
            image.attrs.pop(attribute, None)
        limit = WIDE_PX if kind == "image/svg+xml" else RASTER_WIDE_PX
        if width < limit and (vector_width or 0) < WIDE_PX:
            continue
        name = image.get("alt", "").strip() or "Figure"
        figure = soup.new_tag("figure", attrs={"class": "inflow"})
        # The link goes with the image only when it holds nothing else.
        alone = link is not None and len(link.find_all("img")) == 1 and not link.get_text(strip=True)
        place_figure(link if alone else image, figure, lifted)
        caption = soup.new_tag("figcaption")
        # The same drawing is one sheet whether it is shown as its PNG or through a link to its SVG:
        # the two files differ only in their directory and ending.
        drawing = Path(urllib.parse.urlparse(vector or source).path).stem
        # The chapter's number is part of the key: the same page may be two chapters of one PDF.
        key = hashlib.sha1(f"{chapter}\n{url}\n{drawing}".encode()).hexdigest()[:12]
        caption.append(f"[{name}: full size on a landscape sheet of its own")
        caption.append(Comment(WIDE_PLACE % key))
        caption.append(".]")
        figure.append(caption)
        if key in made:
            sheet, is_vector, first = made[key]
            if source != first:
                raise SystemExit(
                    f"{url}: two different wide pictures are both named {drawing!r} ({first} and {source}); "
                    "they would share one sheet"
                )
            if vector and not is_vector:
                # Its sheet was made from a PNG; this place links the SVG, which prints sharper.
                sheet.find("img")["src"] = image["src"]
                sheet.find("figcaption").string = f"{name} ({vector})"
                made[key] = (sheet, True, first)
            continue
        sheet = soup.new_tag("figure", attrs={"class": "wide", "data-wide": key})
        sheet.append(soup.new_tag("img", src=image["src"], alt=name))
        caption = soup.new_tag("figcaption")
        caption.string = f"{name} ({vector or source})"
        sheet.append(caption)
        sheets.append(sheet)
        made[key] = (sheet, bool(vector), source)
    return sheets


def link_notes(body: Tag, url: str, soup: BeautifulSoup) -> Tag | None:
    """Number each link and list the addresses, which paper cannot follow.

    A link to a heading that is printed in this chapter needs no address, and
    neither does one whose text is its address or one that only wraps an
    image. A listing is left as it is: a mark inside it would look like part
    of what to type.
    """
    numbers: dict[str, int] = {}
    for link in body.find_all("a", href=True):
        target = link["href"]
        page, _, fragment = target.partition("#")
        if page == url and fragment and body.find(id=fragment) is not None:
            continue
        words = link.get_text(strip=True)
        if not words or words == target or link.find_parent("pre") is not None:
            continue
        number = numbers.setdefault(target, len(numbers) + 1)
        mark = soup.new_tag("sup", attrs={"class": "ref"})
        mark.string = f"[{number}]"
        link.insert_after(mark)
    if not numbers:
        return None
    box = soup.new_tag("div", attrs={"class": "links"})
    # The heading and the first few addresses are one block that is not split,
    # so the heading is never the last line of a sheet.
    head = soup.new_tag("div", attrs={"class": "together"})
    heading = soup.new_tag("h2")
    heading.string = "Links in this chapter"
    head.append(heading)
    box.append(head)
    first = soup.new_tag("ol")
    rest = soup.new_tag("ol", start=str(LINKS_WITH_HEADING + 1))
    for number, target in enumerate(numbers, 1):
        item = soup.new_tag("li")
        item.string = target
        (first if number <= LINKS_WITH_HEADING else rest).append(item)
    head.append(first)
    if rest.find("li") is not None:
        box.append(rest)
    return box


def long_blocks(body: Tag) -> None:
    """Let a long listing run over a sheet's end; a short one stays whole."""
    for block in body.find_all("pre"):
        if block.get_text().count("\n") > LONG_LINES:
            block["class"] = [*block.get("class", []), "long"]


def step_pictures(body: Tag, soup: BeautifulSoup) -> None:
    """Keep a picture whole, and on the sheet of the words it belongs to.

    A paragraph that holds only an image, or the small copy of a wide picture
    over its line, is the picture of what comes just
    before it: the paragraph of a step, or that paragraph and its list. They
    are wrapped together so the sheet does not end between them. A second
    picture of the same step stays whole but may start the next sheet.
    """
    for paragraph in body.find_all(["p", "figure"]):
        overview = paragraph.name == "figure" and "inflow" in paragraph.get("class", [])
        if paragraph.find("img") is None or paragraph.name == "figure" and not overview:
            continue
        if not overview and paragraph.get_text(strip=True):
            continue
        paragraph["class"] = [*paragraph.get("class", []), "picture"]
        words = []
        before = paragraph.find_previous_sibling()
        if before is not None and before.name in ("ol", "ul"):
            words.append(before)
            before = before.find_previous_sibling()
        # A picture paragraph before this one was marked "picture" on its own turn, earlier in this loop.
        if before is None or before.name != "p" or "picture" in before.get("class", []):
            continue
        step = soup.new_tag("div", attrs={"class": "step"})
        before.insert_before(step)
        for part in (before, *reversed(words), paragraph):
            step.append(part.extract())


def short_tables(body: Tag) -> None:
    """Keep a short table on one sheet; a long one may run over."""
    for table in body.find_all("table"):
        if len(table.find_all("tr")) <= SHORT_ROWS:
            table["class"] = [*table.get("class", []), "short"]


def chapter(number: int, spec: str, commit: str, fetched: str) -> tuple[str, str]:
    """The title and the printable HTML of one page, as chapter number of the PDF."""
    path, wanted = parse_spec(spec)
    url = page_url(path)
    page, _ = fetch(url)
    soup = BeautifulSoup("", "html.parser")
    body = article(page.decode("utf-8"), url)
    if wanted:
        keep_sections(body, wanted, url)
    absolute_links(body, url)
    sheets = inline_images(body, url, soup, number)
    links = link_notes(body, url, soup)
    long_blocks(body)
    short_tables(body)
    step_pictures(body, soup)
    heading = body.find("h1")
    title = heading.get_text(strip=True) if heading else path
    note = f"Chapter {number} · Source: {url}"
    if wanted:
        note += " (sections: " + ", ".join(wanted) + ")"
    note += f" · docs commit {commit[:10]} · fetched {fetched}"
    return title, (
        f'<div class="chapter"><div class="source">{html.escape(note)}</div>'
        f"{body.decode_contents()}{links or ''}{''.join(map(str, sheets))}</div>"
    )


def shown(spec: str) -> str:
    """A page spec as the cover prints it, with room to wrap between sections."""
    path, wanted = parse_spec(spec)
    return path + (": " + ", ".join(wanted) if wanted else "")


def note_boxes(text: str) -> list[tuple[str, list[str]]]:
    """The boxes of a notes file: (heading, items) for each part between lines of dashes.

    In each part the first line is the heading and each later line an item.
    """
    boxes = []
    for part in re.split(r"(?m)^\s*-{3,}\s*$", text):
        lines = [line.strip() for line in part.splitlines() if line.strip()]
        if lines:
            boxes.append((lines[0], lines[1:]))
    if not boxes:
        raise SystemExit("a notes file needs a heading line")
    return boxes


def numbered(items: list[str]) -> list[str] | None:
    """The items without their numbers when they are written "1. ", "2. ", ... in order; None when they are not.

    A box in which every item starts with a number but the numbers do not count up from 1 stops the run:
    printed as bullets it would show both a bullet and a wrong number.
    """
    found = [re.match(r"(\d+)\.\s+(.*)", item) for item in items]
    if not items or not all(found):
        return None
    if [int(m[1]) for m in found] != list(range(1, len(items) + 1)):
        raise SystemExit(f"a numbered notes box must count 1, 2, 3, ...: {[m[1] for m in found]}")
    return [m[2] for m in found]


def notes(text: str) -> str:
    """The boxes of a notes file as HTML: a box whose items are numbered in order is a numbered list."""
    out = []
    for heading, items in note_boxes(text):
        steps = numbered(items)
        listed = "".join(f"<li>{html.escape(item)}</li>" for item in (items if steps is None else steps))
        kind = "ul" if steps is None else "ol"
        out.append(
            f'<div class="admonition"><p class="admonition-title">{html.escape(heading)}</p>'
            f"<{kind}>{listed}</{kind}></div>"
        )
    return "".join(out)


def css_string(text: str) -> str:
    """text for the inside of a double-quoted CSS string in a <style> element."""
    if "\n" in text or "\r" in text or "<" in text:
        raise SystemExit(f"the title may not hold a line break or '<': {text!r}")
    return text.replace("\\", "\\\\").replace('"', '\\"')


def document(title: str, paper: str, specs: list[str], cover_notes: str | None = None,
             last_sheet: str | None = None) -> str:
    """The joined page, with a place on the cover for each chapter's sheet number.

    cover_notes and last_sheet are the text of a notes file, or None when not
    given; a given one that holds no heading stops the run.
    """
    css_string(title)  # refuse a bad title before any fetching
    for text in (cover_notes, last_sheet):
        if text is not None:
            note_boxes(text)
    commit = built_commit()
    fetched = datetime.date.today().isoformat()
    chapters = [chapter(number, spec, commit, fetched) for number, spec in enumerate(specs, 1)]
    foot = css_string(f"{title} · docs.fpgas.online · commit {commit[:10]} · {fetched}")
    css = CSS % {"paper": PAPERS[paper], "foot": foot}
    contents = "".join(
        f"<li>{html.escape(name)}{SHEET_PLACE % number} <small>({html.escape(shown(spec))})</small></li>"
        for number, (spec, (name, _)) in enumerate(zip(specs, chapters), 1)
    )
    last = ""
    if last_sheet is not None:
        number = len(chapters) + 1
        contents += f"<li>{html.escape(note_boxes(last_sheet)[0][0])}{SHEET_PLACE % number}</li>"
        last = (
            f'<div class="chapter"><div class="source">Chapter {number} · '
            f"Added to this copy; not a page of the site</div>{notes(last_sheet)}</div>"
        )
    cover = (
        f'<div class="cover"><h1>{html.escape(title)}</h1>'
        f"<p>Printed from the pages published at {html.escape(SITE)}, "
        f"built from commit {html.escape(commit)} of fpgas-online/fpgas.online-docs, "
        f"fetched {fetched}. The published pages are the current ones; this is a copy.</p>"
        f"<ol>{contents}</ol>{notes(cover_notes) if cover_notes is not None else ''}</div>"
    )
    return (
        f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
        f"<title>{html.escape(title)}</title><style>{css}</style></head>"
        f"<body>{cover}{''.join(text for _, text in chapters)}{last}</body></html>"
    )


def need_pdftotext() -> None:
    """Stop unless pdftotext and pdfinfo are there; the sheet numbers are read back with them."""
    if shutil.which("pdftotext") is None:
        raise SystemExit("pdftotext (poppler-utils) is not installed; the cover's sheet numbers need it")
    if shutil.which("pdfinfo") is None:
        raise SystemExit("pdfinfo (poppler-utils) is not installed; a wide picture's sheet number needs it")


def chapter_sheets(pdf: Path, chapters: int) -> dict[int, int]:
    """The sheet each chapter starts on, read back from a printed PDF.

    Only a chapter's own first line counts, not text that happens to start
    "Chapter 2 · ". The chapters found must be exactly 1 to chapters, each once,
    in order; anything else means the PDF or this reading of it is wrong.
    """
    need_pdftotext()
    pages = run(["pdftotext", str(pdf), "-"], f"pdftotext {pdf}", timeout=120,
                capture_output=True, text=True).stdout.split("\f")
    sheets: dict[int, int] = {}
    for sheet, page in enumerate(pages, 1):
        for found in re.findall(r"(?m)^\s*Chapter (\d+) · (?:Source: |Added to this copy)", page):
            number = int(found)
            if number in sheets:
                raise SystemExit(f"{pdf}: chapter {number} starts on sheet {sheets[number]} and again on sheet {sheet}")
            sheets[number] = sheet
    if sorted(sheets) != list(range(1, chapters + 1)):
        raise SystemExit(f"{pdf}: found chapters {sorted(sheets)} in the text, expected 1 to {chapters}")
    for number in range(2, chapters + 1):
        if sheets[number] < sheets[number - 1]:
            raise SystemExit(
                f"{pdf}: chapter {number} starts on sheet {sheets[number]}, "
                f"before chapter {number - 1} on sheet {sheets[number - 1]}"
            )
    return sheets


def wide_sheets(pdf: Path, page: str) -> dict[str, int]:
    """The sheet each wide picture is on at full size: the landscape sheets of the PDF, in the page's order."""
    keys = re.findall(WIDE_SHEET_RE, page)
    if not keys:
        return {}
    info = run(["pdfinfo", "-f", "1", "-l", "100000", str(pdf)], f"pdfinfo {pdf}", timeout=60,
               capture_output=True, text=True).stdout
    sizes = re.findall(r"^Page\s+(\d+) size:\s*([0-9.]+) x ([0-9.]+) pts", info, re.MULTILINE)
    landscape = [int(number) for number, width, height in sizes if float(width) > float(height)]
    if len(landscape) != len(keys):
        raise SystemExit(
            f"{pdf}: {len(landscape)} landscape sheets for {len(keys)} wide pictures; "
            "cannot say which sheet each is on"
        )
    if len(set(keys)) != len(keys):
        raise SystemExit(f"{pdf}: two wide pictures have the same key; cannot say which sheet each is on")
    return dict(zip(keys, landscape, strict=True))


def without_sheets(page: str) -> str:
    """The joined page for the first print, before any sheet number is known."""
    return re.sub(WIDE_PLACE_RE, "", re.sub(SHEET_PLACE_RE, "", page))


def with_sheets(page: str, sheets: dict[int, int], wide: dict[str, int] | None = None) -> str:
    """The joined page with each chapter's sheet number in the cover's list, and each wide picture's in its line."""
    def wide_place(match: re.Match) -> str:
        if wide is None or match.group(1) not in wide:
            raise SystemExit(f"the sheet of wide picture {match.group(1)} was not found in the printed PDF")
        return f", sheet {wide[match.group(1)]}"
    page = re.sub(WIDE_PLACE_RE, wide_place, page)

    def place(match: re.Match) -> str:
        number = int(match.group(1))
        if number not in sheets:
            raise SystemExit(f"chapter {number} was not found in the printed PDF")
        return f", sheet {sheets[number]}"
    return re.sub(SHEET_PLACE_RE, place, page)


def run(command: list[str], what: str, timeout: int, **options) -> subprocess.CompletedProcess:
    """Run a program; any way it can fail stops the run with a message."""
    try:
        return subprocess.run(command, check=True, timeout=timeout, **options)
    except subprocess.CalledProcessError as error:
        said = (error.stderr or "").strip().splitlines() if isinstance(error.stderr, str) else []
        why = f": {said[0]}" if said else ""
        raise SystemExit(f"{what} failed with status {error.returncode}{why}") from error
    except subprocess.TimeoutExpired as error:
        raise SystemExit(f"{what} did not finish in {timeout} s") from error
    except OSError as error:
        raise SystemExit(f"cannot run {what}: {error}") from error


def remove_profile(profile: Path) -> None:
    """Remove Chrome's profile directory, which its helpers write to for a moment after it exits."""
    for _ in range(50):
        shutil.rmtree(profile, ignore_errors=True)
        if not profile.exists():
            return
        time.sleep(0.1)
    print(f"could not remove {profile}; remove it by hand", file=sys.stderr)


def print_pdf(page: Path, target: Path) -> None:
    """Have Chrome print page to target, which must not exist yet and must hold a PDF after."""
    chrome = shutil.which(CHROME)
    if chrome is None:
        raise SystemExit(f"{CHROME} is not installed; it does the printing")
    # The profile sits beside the output: /tmp is not for this project's files.
    profile = tempfile.mkdtemp(dir=target.parent, prefix=".print-pages-profile-")
    try:
        run(
            [
                chrome,
                "--headless",
                "--disable-gpu",
                f"--user-data-dir={profile}",
                "--no-pdf-header-footer",
                f"--print-to-pdf={target}",
                page.resolve().as_uri(),
            ],
            f"{CHROME} printing {page}",
            timeout=300,
            # Printing needs nothing from the desktop session. Given a session
            # bus, Chrome waits minutes on it before it exits; given an address
            # it cannot use, it logs that and prints in seconds.
            env={**os.environ, "DBUS_SESSION_BUS_ADDRESS": "disabled:"},
        )
    finally:
        remove_profile(Path(profile))
    if not target.is_file() or target.stat().st_size == 0:
        raise SystemExit(f"{CHROME} wrote no PDF at {target}")


def check_paper(path: Path, paper: str) -> None:
    """Stop unless every page of the PDF is on the chosen paper, in either orientation."""
    info = run(["pdfinfo", "-f", "1", "-l", "100000", str(path)], f"pdfinfo {path}", timeout=60,
               capture_output=True, text=True).stdout
    sizes = re.findall(r"^Page\s+\d+ size:\s*([0-9.]+) x ([0-9.]+) pts", info, re.MULTILINE)
    pages = re.search(r"^Pages:\s*(\d+)", info, re.MULTILINE)
    if not sizes or pages is None or len(sizes) != int(pages.group(1)):
        raise SystemExit(f"--append {path}: pdfinfo did not give a size for every page")
    wide, high = PAPER_POINTS[paper]
    for number, (width, height) in enumerate(sizes, 1):
        w, h = float(width), float(height)
        if not (abs(w - wide) <= 2 and abs(h - high) <= 2 or abs(w - high) <= 2 and abs(h - wide) <= 2):
            raise SystemExit(
                f"--append {path}: page {number} is {width} x {height} pt, not {paper} "
                f"({wide} x {high} pt, either way up); appended PDFs are not resized"
            )


def append_pdfs(printed: Path, extra: list[Path], paper: str, result: Path) -> None:
    """Write result: the printed pages, then the extra PDFs (label sheets, say) as they are."""
    joiner = shutil.which("pdfunite")
    if joiner is None or shutil.which("pdfinfo") is None:
        raise SystemExit("pdfunite and pdfinfo (poppler-utils) are not installed; --append needs them")
    for path in extra:
        if not path.is_file():
            raise SystemExit(f"--append {path}: no such file")
        check_paper(path, paper)
    run([joiner, str(printed), *map(str, extra), str(result)], "pdfunite", timeout=120)
    if not result.is_file() or result.stat().st_size == 0:
        raise SystemExit(f"pdfunite wrote no PDF at {result}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--paper", choices=sorted(PAPERS), required=True)
    parser.add_argument("--title", required=True, help="printed on the cover and in each foot")
    parser.add_argument("--output", type=Path, required=True, help="the PDF to write; its name ends in .pdf")
    parser.add_argument("--keep-html", action="store_true", help="leave the joined page as OUTPUT.html (x.pdf.html for x.pdf)")
    parser.add_argument("--append", type=Path, action="append", default=[], metavar="PDF",
                        help="a PDF to put after the printed pages, unchanged (may be repeated)")
    parser.add_argument("--cover-notes", type=Path, metavar="FILE",
                        help="a box for the cover: the file's first line is its heading, each later line an item "
                        "(items written 1., 2., ... print as a numbered list); "
                        "several boxes may be separated by a line of dashes")
    parser.add_argument("--last-sheet", type=Path, metavar="FILE",
                        help="a box on a sheet of its own after the pages, in the same form "
                        "(several boxes may be separated by a line of dashes)")
    parser.add_argument("pages", nargs="+", metavar="PAGE", help='e.g. "boards/acorn/wiring#raspberry-pi-5"')
    args = parser.parse_args()
    if args.output.suffix.lower() != ".pdf":
        parser.error(f"--output {args.output} must end in .pdf")

    # Every page has chapters, so every run reads sheet numbers back: refuse
    # now rather than after a print.
    need_pdftotext()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    # Only these names are written, never the output itself or a file the user
    # may have beside it: the output is only ever replaced by a PDF that passed
    # the checks, and --keep-html leaves the joined page as OUTPUT.html.
    # The joined page's name must end in .html: Chrome goes by the name of a
    # local file, and waits for ever on one it does not take for a page.
    joined = output.with_name(output.name + ".part.html")
    kept = output.with_name(output.name + ".html")
    printed = output.with_name(output.name + ".part")
    united = output.with_name(output.name + ".united.part")
    cover_notes = None if args.cover_notes is None else args.cover_notes.read_text(encoding="utf-8")
    last_sheet = None if args.last_sheet is None else args.last_sheet.read_text(encoding="utf-8")
    try:
        printed.unlink(missing_ok=True)
        united.unlink(missing_ok=True)
        page = document(args.title, args.paper, args.pages, cover_notes, last_sheet)
        places = set(re.findall(SHEET_PLACE_RE, page))
        joined.write_text(without_sheets(page), encoding="utf-8")
        print_pdf(joined, printed)
        if places:
            # Printed once to learn which sheet each chapter starts on, and again
            # with those numbers on the cover; they must not have moved.
            sheets = chapter_sheets(printed, len(places))
            wide = wide_sheets(printed, page)
            printed.unlink()
            joined.write_text(with_sheets(page, sheets, wide), encoding="utf-8")
            print_pdf(joined, printed)
            if chapter_sheets(printed, len(places)) != sheets or wide_sheets(printed, page) != wide:
                raise SystemExit("the sheets moved when their numbers were put in")
        if args.append:
            append_pdfs(printed, args.append, args.paper, united)
            united.replace(output)
        else:
            printed.replace(output)
        if args.keep_html:
            joined.replace(kept)
    finally:
        printed.unlink(missing_ok=True)
        united.unlink(missing_ok=True)
        joined.unlink(missing_ok=True)
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
