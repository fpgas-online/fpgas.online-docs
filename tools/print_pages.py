#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["beautifulsoup4==4.12.3"]
# ///
"""Render published pages of docs.fpgas.online to one PDF for printing.

    uv run tools/print_pages.py --paper A4 --title "Wiring an Acorn" \\
        --output acorn.pdf boards/acorn/wiring/rpi-5 sites/ps1

Each PAGE is a path under the published site, without ".html". The pages are
fetched from the live site, so the PDF holds what is published and nothing
else: to change the text, change the page and publish it.

A page may be cut down to some of its sections, named by their anchors:

    boards/acorn/wiring/rpi-5#p2-serial-pair-and-spare-gpios,p1-jtag

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
A step's words print on one sheet with its pictures, which are shrunk for that
if need be, but not below a size whose labels can still be read; a picture that
would have to be smaller goes on the next sheet under a line naming the chapter and the step ("JTAG
connector 1, step 3, continued: find wire 1 of the P1 cable"). After printing, every step's words and
pictures are found in the PDF, and the run stops if any picture is on another sheet than its step's words,
other than on a sheet the tool began with such a line.
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
import math
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
# A code span in a table cell up to WHOLE_CODE characters, with no space in it, is printed on one line,
# as long as the longest such spans of its row's cells come to WHOLE_ROW characters or fewer. Both guard the
# sheet's width: at the code size about 96 characters fill an A4 sheet's printable width.
WHOLE_CODE = 24
WHOLE_ROW = 48
PAPERS = {"A4": "A4", "Letter": "letter"}
# A listing is printed at CODE_SIZE pt if its longest line fits the width it has, smaller down to CODE_FLOOR pt
# if that is what it takes, and a line still too long is broken by fit_code, never by the browser. The width:
# CODE_WIDTH pt inside a top-level listing on A4 (180 mm less the listing's padding and border, and the 1 pt the
# body keeps from the edge), less INDENT pt for each list or definition it is in and BOX pt for each box.
# DejaVu Sans Mono is CODE_EM wide (1233/2048 em). A little is kept spare for rounding.
CODE_SIZE, CODE_FLOOR, CODE_EM, CODE_SPARE = 8.0, 6.5, 0.60205, 6.0
CODE_WIDTH, INDENT, BOX = 497.1, {"ul": 17.0, "ol": 17.0, "dd": 30.0}, 19.4
CONTINUED = "\u21aa "  # the mark at the start of a continuation line
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
# A table with at most this many rows, and at most this many characters of text, is kept on one sheet; a longer
# one may run over between its rows, so that it does not leave the rest of a sheet blank.
SHORT_ROWS = 12
SHORT_CHARS = 900
# A step (its words, any list, and its pictures) is printed on one sheet: fit_steps estimates how tall its
# words print and shrinks its pictures to one common scale if that is what it takes. The scale is that of a
# picture as wide as the column: the site's drawings are drawn for it, with labels of 9 to 11 pt there. No
# picture is printed below PICTURE_MIN_SCALE of that (labels of 5.5 to 6.5 pt), the smallest that can still
# be read at the bench; a picture that would have to be smaller goes on the next sheet under a line "Step N,
# continued". The estimate errs on the tall side, and STEP_SPARE_MM of the sheet is left over for what it
# misses. A picture is at most PICTURE_MAX_MM tall, as the stylesheet says.
# TEXT_MM: the width and height of a sheet's text area (the paper less the @page margins, and the 1 pt the
# body keeps from the right edge). At 10 pt DejaVu Sans a character of text is CHAR_MM wide on average (a
# little wider than measured, to err on the tall side); a heading's bold is BOLD times as wide. A line of
# text is 1.4 times its size; a heading's, 1.2.
PICTURE_MIN_SCALE, PICTURE_MAX_MM, STEP_SPARE_MM = 0.6, 200.0, 10.0
TEXT_MM = {"A4": (210 - 30 - 0.35, 297 - 34), "Letter": (215.9 - 30 - 0.35, 279.4 - 34)}
CHAR_MM, BOLD, PT_MM = 2.0, 1.1, 25.4 / 72
# Each heading's size in pt and its margins, top and bottom, in mm (h2 with its rule).
HEADING_SIZES = {"h1": (20, 4.0), "h2": (15, 9.7), "h3": (12, 7.0), "h4": (10.5, 5.5), "h5": (10, 4.5),
                 "h6": (10, 4.5)}
# The chapter's source line (8 pt, up to two lines with its rule and margins) is above a step at its top.
SOURCE_MM = 2 * 8 * 1.4 * PT_MM + 5.6
# Below a picture's image: its paragraph's margin and the line's descent (a figure: its margin and caption).
PICTURE_BELOW_MM, FIGURE_BELOW_MM = 5.0, 3.5
CONTINUED_MM = 2 * 10 * 1.4 * PT_MM + 2.5  # the line naming the step whose pictures go on, up to two lines
# The paragraphs ending a section after a step's last picture are kept on its sheet when they are no taller.
TAIL_MAX_MM = 60.0
# A step's words: the blocks that print on lines of their own, and so are counted apart from the text around
# them; a code span's padding (0.6 mm each side) in characters; a listing's padding, border and margin in mm.
WORD_BLOCKS = ("p", "ul", "ol", "pre", "div", "blockquote", "dl", "table", "figure")
CODE_PAD_CHARS, PRE_EXTRA_MM = 1, 2 * 2 + 2 * 0.15 + 3
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
  @bottom-right { content: "Page " counter(page) " of " counter(pages) "%(after)s";
                  font: 8pt sans-serif; color: #444; }
}
@page wide { size: %(paper)s landscape; margin: 10mm 10mm 14mm 10mm; }
html { font: 10pt/1.4 "DejaVu Sans", "Liberation Sans", Arial, sans-serif; color: #000; }
/* Chrome cuts whatever touches the right edge of the printable area: a full-width
   box (a warning, a command block) lost its right border there. So nothing is as
   wide as that area. */
body { margin: 0 1pt 0 0; }
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
pre code { background: none; padding: 0; font-size: inherit; }
/* fit_code has sized or broken every listing line to fit, so the browser never wraps one. */
pre { white-space: pre; overflow-wrap: normal; }
.code-note { font-size: 8pt; font-style: italic; margin-bottom: 1mm; break-after: avoid; }
sup.ref { font-size: 6.5pt; line-height: 0; color: #333; }
.links .together { break-inside: avoid; }
.links ol { margin-bottom: 0; }
.links ol { font-size: 8pt; overflow-wrap: anywhere; }
.inflow { margin: 0 0 3.5mm; break-inside: avoid; }
.inflow figcaption { font-style: italic; }
table.short { break-inside: avoid; }
table { border-collapse: collapse; width: 100%%; margin: 0 0 3.5mm; font-size: 8.8pt; }
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
/* ...but a short code span in a cell (whole_codes) stays in one piece. */
td code.whole { white-space: nowrap; overflow-wrap: normal; }
/* A heading's code span does not break either (code breaks anywhere by default). */
th code { overflow-wrap: normal; }
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
/* The pictures of a step too tall for one sheet (fit_steps), on the next sheet under the step's number. */
.continued { break-before: page; }
.continued-line { font-weight: bold; break-after: avoid; }
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
    # Paper is white: of a picture drawn for each theme, only the light one is printed. The theme hides
    # .only-dark in light mode; a link that held nothing but the dark picture goes with it.
    for dark in body.select(".only-dark"):
        holder = dark.find_parent("a")
        dark.decompose()
        if holder is not None and holder.find("img") is None and not holder.get_text(strip=True):
            holder.decompose()
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


def png_size(content: bytes) -> tuple[int, int] | None:
    if content[:8] == b"\x89PNG\r\n\x1a\n" and len(content) >= 24:
        return int.from_bytes(content[16:20], "big"), int.from_bytes(content[20:24], "big")
    return None


def jpeg_size(content: bytes) -> tuple[int, int] | None:
    """The width and height in the first start-of-frame marker of a JPEG."""
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
            return (int.from_bytes(content[position + 7:position + 9], "big"),
                    int.from_bytes(content[position + 5:position + 7], "big"))
        position += 2 + length
    return None


def gif_size(content: bytes) -> tuple[int, int] | None:
    if content[:6] in (b"GIF87a", b"GIF89a") and len(content) >= 10:
        return int.from_bytes(content[6:8], "little"), int.from_bytes(content[8:10], "little")
    return None


def svg_size(content: bytes) -> tuple[int, int] | None:
    """The size an SVG states: its width and height attributes, else its viewBox.

    A width without a height takes the height from the viewBox's proportions."""
    root = re.search(rb"<svg\b[^>]*>", content)
    if root is None:
        return None
    tag = root.group(0).decode("utf-8", "replace")
    width = re.search(r"""\swidth\s*=\s*["']\s*([0-9.]+)\s*(px)?\s*["']""", tag)
    height = re.search(r"""\sheight\s*=\s*["']\s*([0-9.]+)\s*(px)?\s*["']""", tag)
    box = re.search(r"""\sviewBox\s*=\s*["']\s*[-0-9.]+[\s,]+[-0-9.]+[\s,]+([0-9.]+)[\s,]+([0-9.]+)\s*["']""", tag)
    if width and height:
        return round(float(width.group(1))), round(float(height.group(1)))
    if box and float(box.group(1)) > 0:
        box_width, box_height = float(box.group(1)), float(box.group(2))
        if width:
            return round(float(width.group(1))), round(float(width.group(1)) * box_height / box_width)
        return round(box_width), round(box_height)
    if width:
        return round(float(width.group(1))), 0
    return None


def image_size(content: bytes, kind: str) -> tuple[int, int] | None:
    """The pixel width and height of a PNG, JPEG, GIF or SVG; None when they cannot be read.

    An SVG that states only its width has height 0."""
    if kind == "image/svg+xml":
        return svg_size(content)
    return png_size(content) or jpeg_size(content) or gif_size(content)


def png_width(content: bytes) -> int | None:
    return (png_size(content) or (None,))[0]


def jpeg_width(content: bytes) -> int | None:
    return (jpeg_size(content) or (None,))[0]


def gif_width(content: bytes) -> int | None:
    return (gif_size(content) or (None,))[0]


def svg_width(content: bytes) -> int | None:
    """The width an SVG states: its width attribute, else its viewBox."""
    return (svg_size(content) or (None,))[0]


def image_width(content: bytes, kind: str) -> int | None:
    """The pixel width of a PNG, JPEG, GIF or SVG; None when it cannot be read."""
    return (image_size(content, kind) or (None,))[0]


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


def code_chars(block: Tag) -> tuple[int, int]:
    """How many characters of a listing fit on its line at CODE_SIZE and at CODE_FLOOR, where it sits."""
    width = CODE_WIDTH - CODE_SPARE
    for parent in block.parents:
        width -= INDENT.get(parent.name, 0)
        if "admonition" in (parent.get("class") or []):
            width -= BOX
    return int(width / (CODE_EM * CODE_SIZE)), int(width / (CODE_EM * CODE_FLOOR))


def fit_code(body: Tag, soup: BeautifulSoup) -> None:
    """Print every line of a listing as one line a reader can type: smaller if it must be, broken by hand if
    even that is not enough, with each continuation marked and a note saying the marks are not typed."""
    for block in body.find_all("pre"):
        chars, floor_chars = code_chars(block)
        lines = block.get_text().expandtabs(8).rstrip("\n").split("\n")  # Chrome's tab stops are every 8
        longest = max((len(line) for line in lines), default=0)
        if longest <= chars:
            continue
        size = max(CODE_FLOOR, CODE_SIZE * chars / longest)
        block["style"] = f"font-size: {size:.2f}pt"
        if longest <= floor_chars:
            continue
        width = floor_chars - len(CONTINUED)
        out = []
        for line in lines:
            out.append(line[:floor_chars])
            rest = line[floor_chars:]
            while rest:
                out.append(CONTINUED + rest[:width])
                rest = rest[width:]
        block.clear()
        block.append("\n".join(out))
        note = soup.new_tag("p", attrs={"class": "code-note"})
        note.string = (f"A line below is too long for the sheet: where a line starts with {CONTINUED.strip()}, it "
                       "continues the line above. Type the two as one line, leaving out the arrow and the one "
                       "space after it.")
        block.insert_before(note)


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
    are wrapped together so the sheet does not end between them; fit_steps
    then sizes the step to one sheet and takes in the pictures after it.
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


def text_mm(text: str, width: float, size: float = 10.0, line: float = 1.4, char: float = CHAR_MM) -> float:
    """How tall text prints in a column width mm wide at size pt, as whole lines of the average character."""
    per_line = max(1, int(width / (char * size / 10)))
    return max(1, math.ceil(len(" ".join(text.split())) / per_line)) * size * line * PT_MM


def line_runs(node: Tag) -> list[int]:
    """How many average characters each line run of node's own text holds: a <br> starts a new run, and a
    block inside node (a list in a list item, say) is left out, for words_mm counts it on its own. A code span
    counts its characters as text (DejaVu Sans Mono is no wider) and one more for its padding."""
    runs = [0]
    text = [""]

    def close() -> None:
        runs[-1] += len(" ".join(text[0].split()))
        text[0] = ""

    def walk(element: Tag) -> None:
        for child in element.children:
            if isinstance(child, Comment):
                continue
            if not isinstance(child, Tag):
                text[0] += str(child)
            elif child.name == "br":
                close()
                runs.append(0)
                walk(child)  # html.parser may hang what follows a <br> on it
            elif child.name in WORD_BLOCKS:
                text[0] += " "
            elif child.name == "code":
                # The padding counts as characters that are not spaces, so that it is not folded away.
                text[0] += " " + " ".join(child.get_text().split()) + "\0" * CODE_PAD_CHARS
            else:
                walk(child)

    walk(node)
    close()
    if len(runs) > 1 and runs[-1] == 0:
        runs.pop()  # a <br> at the end starts no line
    return runs


def lines_mm(node: Tag, width: float) -> float:
    """How tall node's own text prints at 10 pt, each run between <br>s on whole lines of its own."""
    per_line = max(1, int(width / CHAR_MM))
    return sum(max(1, math.ceil(chars / per_line)) for chars in line_runs(node)) * 10 * 1.4 * PT_MM


def words_mm(block: Tag, width: float) -> float:
    """How tall a step's paragraph, list or listing prints, with its margin below (and that of each paragraph,
    list and listing inside it). A list item is indented, and a list inside it again."""
    if block.name in ("ol", "ul"):
        items = block.find_all("li", recursive=False) or [block]
        return sum(words_mm(item, width - 6) for item in items) + 2.5
    if block.name == "pre":
        size = re.search(r"font-size:\s*([0-9.]+)pt", block.get("style", ""))
        lines = block.get_text().rstrip("\n").count("\n") + 1
        return lines * (float(size.group(1)) if size else CODE_SIZE) * 1.3 * PT_MM + PRE_EXTRA_MM
    inner = [child for child in block.find_all(recursive=False) if child.name in WORD_BLOCKS]
    own = lines_mm(block, width) if block.name == "p" or line_runs(block) != [0] else 0.0
    return own + sum(words_mm(child, width) for child in inner) + (2.5 if block.name == "p" else 0.0)


def heading_mm(heading: Tag, width: float) -> float:
    size, margins = HEADING_SIZES[heading.name]
    return text_mm(heading.get_text(" ", strip=True), width, size, 1.2, CHAR_MM * BOLD) + margins


def lead_mm(step: Tag, body: Tag, width: float) -> float:
    """How tall the headings print that go to a new sheet with the step, since none is a sheet's last line.

    A step at the top of its chapter brings the chapter's source line too."""
    total, node = 0.0, step
    while True:
        before = node.find_previous_sibling()
        if before is None:
            if node.parent is body or node.parent is None:
                return total + SOURCE_MM
            node = node.parent
        elif before.name in HEADING_SIZES:
            total += heading_mm(before, width)
            node = before
        else:
            return total


def picture_mm(picture: Tag, width: float) -> tuple[float, float, float]:
    """How tall a picture's image prints at its natural size (no wider than the column, no taller than
    PICTURE_MAX_MM); how tall it would be as wide as the column; and how much its paragraph or figure adds
    below it."""
    image = picture.find("img")
    source = image.get("src", "")
    data = re.match(r"data:([^;,]+);base64,(.*)", source, re.DOTALL)
    size = image_size(base64.b64decode(data.group(2)), data.group(1)) if data else None
    if not size or not size[0] or not size[1]:
        raise SystemExit(f"cannot read the size of a step's picture: {image.get('alt') or source[:80]!r}")
    shown = min(width, size[0] * 25.4 / 96)  # 96 image pixels to the inch
    below = PICTURE_BELOW_MM
    if picture.name == "figure":
        caption = picture.find("figcaption")
        below = FIGURE_BELOW_MM + (text_mm(caption.get_text(" ", strip=True), width) if caption else 0)
    return min(PICTURE_MAX_MM, shown * size[1] / size[0]), width * size[1] / size[0], below


def fit_pictures(naturals: list[float], fulls: list[float], room: float) -> list[float] | None:
    """The heights at which pictures fit room mm together, or None when they do not even at PICTURE_MIN_SCALE.

    naturals: each picture's height at its natural size; fulls: its height as wide as the column. Each is
    printed at one common scale of its full height, the largest that fits, and never above its natural."""
    if sum(naturals) <= room:
        return list(naturals)

    def heights(scale: float) -> list[float]:
        return [min(natural, scale * full) for natural, full in zip(naturals, fulls)]

    if sum(heights(PICTURE_MIN_SCALE)) > room:
        return None
    low, high = PICTURE_MIN_SCALE, 1.0
    for _ in range(40):
        middle = (low + high) / 2
        low, high = (middle, high) if sum(heights(middle)) <= room else (low, middle)
    return heights(low)


def place_pictures(pictures: list[Tag], room: float, width: float,
                   at_least_one: bool) -> list[tuple[float, float, float]]:
    """The pictures, from the first, that fit room mm: for each, the height to print it at, its natural height
    and its height as wide as the column. Nothing is changed.

    at_least_one: the first is counted even when it does not fit; it then has a sheet to itself, as it is."""
    sizes = [picture_mm(picture, width) for picture in pictures]
    for count in range(len(pictures), 0, -1):
        heights = fit_pictures([natural for natural, _, _ in sizes[:count]], [full for _, full, _ in sizes[:count]],
                               room - sum(below for _, _, below in sizes[:count]))
        if heights is not None:
            return [(height, natural, full) for height, (natural, full, _) in zip(heights, sizes)]
    return [(sizes[0][0], sizes[0][0], sizes[0][1])] if at_least_one else []


def say(message: str) -> None:
    """Tell the person printing what was changed to fit a sheet."""
    print(f"print_pages: {message}", file=sys.stderr)


def chapter_name(title: str) -> str:
    """A chapter's short name for the lines that say where a step goes on: "JTAG connector 1" for the title
    "Compute Blade cables: JTAG connector 1, prepare the wires" (after its first colon, before its first
    comma), with a capital first letter, for it starts a line."""
    name = title.split(": ", 1)[-1].split(", ", 1)[0].strip()
    return name[:1].upper() + name[1:]


def first_words(text: str, most: int = 12) -> str:
    """The first words of a step, to name it: its first clause without the step's number, at most most words,
    and with a small first letter unless the first word is a name like "P1" or "GND"."""
    text = re.sub(r"^\d+\.\s*", "", " ".join(text.split()))
    words = re.split(r"[,;:]|\.(?:\s|$)", text, maxsplit=1)[0].split()
    said = " ".join(words[:most]) + ("\u2026" if len(words) > most else "")
    if words and not any(c.isupper() or c.isdigit() for c in words[0][1:]):
        said = said[:1].lower() + said[1:]
    return said


def step_names(words: Tag, name: str) -> tuple[str, str]:
    """The name of the step that starts with the paragraph words, and the line over its pictures on a sheet
    after its own: "JTAG connector 1, step 3" and "JTAG connector 1, step 3, continued: find wire 1 of the P1
    cable". A step without a number is named by the heading it is under."""
    number = re.match(r"\s*(\d+)\.", words.get_text())
    first = first_words(words.get_text(" ", strip=True))
    if number:
        label = f"{name}, step {number.group(1)}"
        return label, f"{label}, continued: {first}"
    heading = words.find_previous(HEADINGS)
    label = name if heading is None or heading.name == "h1" else f"{name}, \u201c{heading.get_text(' ', strip=True)}\u201d"
    return label, f"{label}, continued from the sheet before: {first}"


def tail_after(last: Tag) -> list[Tag]:
    """The paragraphs and lists after a step's last picture that end its section, or none if anything else
    (a heading, a table, another picture) comes before the section ends."""
    tail = list(last.find_next_siblings())
    if not tail or any(part.name not in ("p", "ul", "ol") or "picture" in part.get("class", []) for part in tail):
        return []
    return tail


def fit_steps(body: Tag, soup: BeautifulSoup, paper: str, name: str) -> None:
    """Print each step whole on one sheet: its words and all its pictures.

    A step's pictures are the one step_pictures wrapped with its words and those right after it. They are
    shrunk if the step would not fit a sheet otherwise, to no less than PICTURE_MIN_SCALE. Pictures that still
    do not fit go on the next sheet under a line naming the step (step_names), as many to a sheet as fit there.

    A few short paragraphs that end the section after the step (tail_after) stay on the sheet of its last
    pictures, which are shrunk a little more for them if need be: printed after a sheet the pictures fill,
    they would stand alone on a sheet of their own. name: the chapter's short name (chapter_name).

    Each picture shrunk and each moved to a later sheet is said on stderr."""
    width, height = TEXT_MM[paper]
    room = height - STEP_SPARE_MM
    for step in body.find_all("div", class_="step"):
        parts = step.find_all(recursive=False)
        pictures = [parts[-1]]
        after = step.find_next_sibling()
        while after is not None and "picture" in after.get("class", []):
            pictures.append(after)
            after = after.find_next_sibling()
        label, line = step_names(parts[0], name)
        words = sum(words_mm(part, width) for part in parts[:-1])
        # One entry for each sheet the step takes: the room its pictures have there, and the pictures.
        first_room = room - lead_mm(step, body, width) - words
        placed = place_pictures(pictures, first_room, width, False)
        sheets = [(first_room, pictures[:len(placed)], placed)]
        rest = pictures[len(placed):]
        while rest:
            placed = place_pictures(rest, room - CONTINUED_MM, width, True)
            sheets.append((room - CONTINUED_MM, rest[:len(placed)], placed))
            rest = rest[len(placed):]
        tail = tail_after(pictures[-1] if len(pictures) > 1 else step)  # the first picture is inside the step
        if tail:
            last_room, last_pictures, _ = sheets[-1]
            tail_mm = sum(words_mm(part, width) for part in tail)
            placed = place_pictures(last_pictures, last_room - tail_mm, width, False) if tail_mm <= TAIL_MAX_MM else []
            if len(placed) == len(last_pictures):
                sheets[-1] = (last_room, last_pictures, placed)
            else:
                tail = []
        last = step
        for number, (_, group, placed) in enumerate(sheets):
            if number:
                block = soup.new_tag("div", attrs={"class": "step continued"})
                said = soup.new_tag("p", attrs={"class": "continued-line"})
                said.string = line
                block.append(said)
                last.insert_after(block)
                last = block
            for picture, (height_mm, natural, full) in zip(group, placed):
                alt = picture.find("img").get("alt") or "picture"
                if picture.parent is not last:
                    last.append(picture.extract())
                if number:
                    say(f"{label}: picture {alt!r} moved to the next sheet, under \u201c{line}\u201d")
                if height_mm < natural - 0.05:
                    picture.find("img")["style"] = f"max-height: {height_mm:.1f}mm"
                    say(f"{label}: picture {alt!r} shrunk to {height_mm:.0f} mm from {natural:.0f} mm "
                        f"({height_mm / full:.2f} of the column's width)")
        if tail:
            kept = soup.new_tag("div", attrs={"class": "step-tail"})
            for part in tail:
                kept.append(part.extract())
            last.append(kept)
            say(f"{label}: the {len(tail)} paragraph(s) ending its section kept on the sheet of its last picture")


def short_tables(body: Tag) -> None:
    """Keep a short table on one sheet; a long one may run over."""
    for table in body.find_all("table"):
        if len(table.find_all("tr")) <= SHORT_ROWS and len(table.get_text(" ", strip=True)) <= SHORT_CHARS:
            table["class"] = [*table.get("class", []), "short"]


def whole_codes(body: Tag) -> None:
    """Keep a short code span in a table cell on one line: an address, an ID.

    A cell may break a word so that no table is wider than its sheet (the stylesheet says why); a short code
    span broken in two ("0000:" / "01") is harder to read than a slightly wider column. A long one, or one
    with spaces, still breaks. So does every one in a row whose spans together would take most of a sheet's
    width: keeping those whole is what would push the table past the edge."""
    for row in body.select("tr"):
        cells = []
        for cell in row.find_all("td", recursive=False):
            codes = [code for code in cell.find_all("code")
                     if len(code.get_text()) <= WHOLE_CODE and not any(c.isspace() for c in code.get_text())]
            if codes:
                cells.append(codes)
        if sum(max(len(code.get_text()) for code in codes) for codes in cells) > WHOLE_ROW:
            continue
        for code in (code for codes in cells for code in codes):
            code["class"] = [*code.get("class", []), "whole"]


def chapter(number: int, spec: str, commit: str, fetched: str, paper: str,
            link_lists: bool = True) -> tuple[str, str]:
    """The title and the printable HTML of one page, as chapter number of the PDF.

    link_lists: number each link and list the addresses at the chapter's end. Without it a link is printed
    as its words alone, for a reader who has the paper and nothing to follow an address with."""
    path, wanted = parse_spec(spec)
    url = page_url(path)
    page, _ = fetch(url)
    soup = BeautifulSoup("", "html.parser")
    body = article(page.decode("utf-8"), url)
    if wanted:
        keep_sections(body, wanted, url)
    absolute_links(body, url)
    sheets = inline_images(body, url, soup, number)
    links = link_notes(body, url, soup) if link_lists else None
    fit_code(body, soup)
    long_blocks(body)
    short_tables(body)
    whole_codes(body)
    heading = body.find("h1")
    title = heading.get_text(strip=True) if heading else path
    step_pictures(body, soup)
    fit_steps(body, soup, paper, chapter_name(title))
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
             last_sheet: str | None = None, link_lists: bool = True, appended: int = 0) -> str:
    """The joined page, with a place on the cover for each chapter's sheet number.

    appended: how many sheets of other PDFs follow the printed ones. They carry no foot of ours, so each
    foot says they are there: "Page 3 of 56 + 2 unnumbered".

    cover_notes and last_sheet are the text of a notes file, or None when not
    given; a given one that holds no heading stops the run.
    """
    css_string(title)  # refuse a bad title before any fetching
    for text in (cover_notes, last_sheet):
        if text is not None:
            note_boxes(text)
    commit = built_commit()
    fetched = datetime.date.today().isoformat()
    chapters = [chapter(number, spec, commit, fetched, paper, link_lists) for number, spec in enumerate(specs, 1)]
    foot = css_string(f"{title} · docs.fpgas.online · commit {commit[:10]} · {fetched}")
    after = f" + {appended} unnumbered" if appended else ""
    css = CSS % {"paper": PAPERS[paper], "foot": foot, "after": after}
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


def check_paper(path: Path, paper: str) -> int:
    """How many pages the PDF has; stops unless every one is on the chosen paper, in either orientation."""
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
    return len(sizes)


def appended_sheets(extra: list[Path], paper: str) -> int:
    """How many sheets the PDFs to append have in all; stops on a missing file or one on other paper."""
    if extra and (shutil.which("pdfunite") is None or shutil.which("pdfinfo") is None):
        raise SystemExit("pdfunite and pdfinfo (poppler-utils) are not installed; --append needs them")
    total = 0
    for path in extra:
        if not path.is_file():
            raise SystemExit(f"--append {path}: no such file")
        total += check_paper(path, paper)
    return total


def append_pdfs(printed: Path, extra: list[Path], paper: str, result: Path) -> None:
    """Write result: the printed pages, then the extra PDFs (label sheets, say) as they are.

    The extra PDFs were checked by appended_sheets before anything was printed."""
    joiner = shutil.which("pdfunite")
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
    parser.add_argument("--no-link-lists", action="store_true",
                        help="do not number the links or list their addresses at each chapter's end: for a "
                        "reader who has the paper only")
    parser.add_argument("pages", nargs="+", metavar="PAGE", help='e.g. "boards/acorn/wiring/rpi-5#p1-jtag"')
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
        # Counted before anything is fetched or printed: a wrong PDF stops the run at once.
        appended = appended_sheets(args.append, args.paper)
        page = document(args.title, args.paper, args.pages, cover_notes, last_sheet, not args.no_link_lists,
                        appended)
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
