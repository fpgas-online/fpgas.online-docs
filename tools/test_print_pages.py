#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Tests for the parts of print_pages.py that choose and change page content. No network
and no browser: run with `python -m unittest discover -s tools -p 'test_*.py'`."""

import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
import urllib.parse
from pathlib import Path

import print_pages as p

URL = "https://docs.fpgas.online/en/latest/boards/acorn/wiring.html"

PAGE = """<html><body><nav>theme</nav><article role="main">
<section id="acorn-wiring"><h1>Acorn wiring<a class="headerlink" href="#acorn-wiring">¶</a></h1>
<p>Lead text. <a href="index.html">board</a> <a href="../../sites/ps1.html#compute-blades">ps1</a>
<a href="#raspberry-pi-5">pi5</a> <a href="https://example.org/x">out</a></p>
<section id="bill-of-materials"><h2>Bill of Materials</h2><p>parts</p></section>
<section id="raspberry-pi-5"><h2>Raspberry Pi 5</h2><p>pi text</p>
<section id="p1-jtag"><h3>P1</h3><p>jtag</p></section>
<section id="p2-serial"><h3>P2</h3><p>serial</p></section></section>
<section id="compute-blade"><h2>Compute Blade</h2><p>blade text</p>
<section id="housings"><h3>Housings</h3><p>housing text</p></section></section>
</section></article></body></html>"""


def body():
    return p.article(PAGE, URL)


class ParseSpec(unittest.TestCase):
    def test_plain_path(self):
        self.assertEqual(p.parse_spec("boards/acorn/wiring"), ("boards/acorn/wiring", []))

    def test_html_suffix_and_slashes_are_dropped(self):
        self.assertEqual(p.parse_spec("/sites/ps1.html"), ("sites/ps1", []))

    def test_sections(self):
        self.assertEqual(p.parse_spec("sites/ps1#compute-blades,power-control"),
                         ("sites/ps1", ["compute-blades", "power-control"]))

    def test_empty_path_and_parent_directories_are_refused(self):
        for bad in ("", "#a", "../../etc/passwd", "a/../b"):
            with self.assertRaises(SystemExit):
                p.parse_spec(bad)

    def test_url_is_under_the_site(self):
        self.assertEqual(p.page_url("boards/acorn/wiring"), URL)


class Article(unittest.TestCase):
    def test_theme_and_header_links_are_dropped(self):
        text = str(body())
        self.assertNotIn("theme", text)
        self.assertNotIn("headerlink", text)
        self.assertIn("Lead text.", text)

    def test_an_html_comment_of_the_page_is_dropped(self):
        page = PAGE.replace("<p>parts</p>", "<p>parts</p><!--sheet-of-chapter-1-->")
        text = str(p.article(page, URL))
        self.assertNotIn("<!--", text)
        self.assertIn("parts", text)

    def test_a_page_that_is_not_of_the_site_stops_the_run(self):
        with self.assertRaises(SystemExit):
            p.article("<html><body><p>404</p></body></html>", URL)

    # A picture drawn for each theme, as the site builds it: the light one, then its dark twin.
    TWINS = (
        '<p><img alt="Fitting" class="only-light" src="../_images/fit.png" />\n'
        '<img alt="Fitting" class="only-dark" src="../_images/fit-dark.png" /></p>'
        '<p><a class="only-light reference download internal" download="" href="../_downloads/1/sheet.svg">'
        '<span class="xref download myst"><img alt="Sheet" src="../_images/sheet.png" />'
        '</span></a>\n<a class="only-dark reference download internal" download="" href="../_downloads/2/sheet-dark.svg">'
        '<span class="xref download myst"><img alt="Sheet" src="../_images/sheet-dark.png" />'
        "</span></a></p>"
        '<figure class="only-light align-default" id="id1"><img alt="Pads" src="../_images/pads.jpg" />'
        '<figcaption><p>Photo: <a href="https://example.org/photo">source</a></p></figcaption></figure>'
        '<figure class="only-dark align-default" id="id2"><img alt="Pads" src="../_images/pads-dark.jpg" />'
        '<figcaption><p>Photo: <a href="https://example.org/photo">source</a></p></figcaption></figure>'
    )

    def test_only_the_light_picture_of_a_theme_pair_is_printed(self):
        article = p.article(PAGE.replace("<p>parts</p>", self.TWINS), URL)
        sources = [img["src"] for img in article.find_all("img")]
        self.assertEqual(sources, ["../_images/fit.png", "../_images/sheet.png", "../_images/pads.jpg"])
        self.assertEqual(len(article.find_all("figcaption")), 1)  # the dark figure goes with its caption
        self.assertEqual(article.select(".only-dark"), [])

    def test_the_link_that_held_only_the_dark_picture_goes_too(self):
        article = p.article(PAGE.replace("<p>parts</p>", self.TWINS), URL)
        self.assertEqual([a["href"] for a in article.select("a.download")], ["../_downloads/1/sheet.svg"])

    def test_a_dark_picture_in_a_link_with_words_leaves_the_words(self):
        page = PAGE.replace(
            "<p>parts</p>", '<p><a href="x.svg">the sheet <img class="only-dark" src="x-dark.png" /></a></p>'
        )
        article = p.article(page, URL)
        self.assertEqual(article.find("a", href="x.svg").get_text(strip=True), "the sheet")
        self.assertIsNone(article.find("img"))


class KeepSections(unittest.TestCase):
    def kept(self, wanted):
        article = body()
        p.keep_sections(article, wanted, URL)
        return article.get_text()

    def test_title_lead_and_wanted_sections_stay_in_page_order(self):
        text = self.kept(["raspberry-pi-5", "bill-of-materials"])
        for part in ("Acorn wiring", "Lead text.", "parts", "pi text", "jtag", "serial"):
            self.assertIn(part, text)
        self.assertLess(text.index("parts"), text.index("pi text"))
        self.assertNotIn("blade text", text)
        self.assertNotIn("housing text", text)

    def test_a_subsection_keeps_its_parents_heading_but_not_its_siblings(self):
        text = self.kept(["housings"])
        self.assertIn("housing text", text)
        self.assertIn("Compute Blade", text)
        self.assertNotIn("blade text", text)
        self.assertNotIn("pi text", text)
        self.assertNotIn("parts", text)

    def test_one_subsection_of_two(self):
        text = self.kept(["p1-jtag"])
        self.assertIn("jtag", text)
        self.assertNotIn("serial", text)

    def test_a_missing_section_stops_the_run_and_is_named(self):
        with self.assertRaises(SystemExit) as stop:
            self.kept(["raspberry-pi-5", "no-such-section"])
        self.assertIn("#no-such-section", str(stop.exception))


    def test_the_pages_own_section_cannot_be_the_wanted_one(self):
        with self.assertRaises(SystemExit) as stop:
            self.kept(["acorn-wiring"])
        self.assertIn("without sections", str(stop.exception))

    def test_a_wanted_section_inside_a_div_is_not_silently_lost(self):
        page = PAGE.replace('<section id="housings">', '<div><section id="housings">').replace(
            "housing text</p></section>", "housing text</p></section></div>")
        article = p.article(page, URL)
        with self.assertRaises(SystemExit) as stop:
            p.keep_sections(article, ["housings"], URL)
        self.assertIn("#housings", str(stop.exception))


class FakeFetch:
    """Stands in for p.fetch: answers from a dict of url -> (body, content type)."""

    def __init__(self, answers):
        self.answers = answers

    def __enter__(self):
        self.real = p.fetch
        p.fetch = self
        return self

    def __exit__(self, *exc):
        p.fetch = self.real

    def __call__(self, url):
        if url not in self.answers:
            raise SystemExit(f"cannot fetch {url}: not in the fake")
        return self.answers[url]


class BuiltCommit(unittest.TestCase):
    def commit_from(self, body):
        with FakeFetch({p.ADDONS: (body, "application/json")}):
            return p.built_commit()

    def test_the_commit_is_read(self):
        self.assertEqual(self.commit_from(b'{"builds": {"current": {"commit": "abc123"}}}'), "abc123")

    def test_a_missing_key_stops_the_run(self):
        with self.assertRaises(SystemExit):
            self.commit_from(b'{"builds": {}}')

    def test_a_null_or_empty_or_non_string_commit_stops_the_run(self):
        for value in ("null", '""', "5", '" "'):
            with self.assertRaises(SystemExit, msg=value):
                self.commit_from(('{"builds": {"current": {"commit": %s}}}' % value).encode())


class AbsoluteLinks(unittest.TestCase):
    def test_every_link_points_at_the_published_site(self):
        article = body()
        p.absolute_links(article, URL)
        links = [a["href"] for a in article.find_all("a")]
        self.assertEqual(links, [
            "https://docs.fpgas.online/en/latest/boards/acorn/index.html",
            "https://docs.fpgas.online/en/latest/sites/ps1.html#compute-blades",
            URL + "#raspberry-pi-5",
            "https://example.org/x",
        ])


class PngWidth(unittest.TestCase):
    def test_width_is_read_from_the_header(self):
        header = b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + (3200).to_bytes(4, "big") + (1800).to_bytes(4, "big")
        self.assertEqual(p.png_width(header), 3200)

    def test_other_formats_have_no_width(self):
        self.assertIsNone(p.png_width(b"<svg xmlns='http://www.w3.org/2000/svg'/>"))


def png(width):
    return b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + width.to_bytes(4, "big") + (100).to_bytes(4, "big")


def jpeg(width):
    return (b"\xff\xd8\xff\xe0\x00\x04ab" + b"\xff\xc0\x00\x11\x08" + (50).to_bytes(2, "big")
            + width.to_bytes(2, "big") + b"\x03" * 10)


def svg(attributes):
    return f"<?xml version='1.0'?><svg xmlns='http://www.w3.org/2000/svg' {attributes}><rect/></svg>".encode()


IMAGES = "https://docs.fpgas.online/en/latest/"


class ImageWidth(unittest.TestCase):
    def test_jpeg_width_is_read_from_the_frame_marker(self):
        self.assertEqual(p.jpeg_width(jpeg(2400)), 2400)
        self.assertEqual(p.image_width(jpeg(2400), "image/jpeg"), 2400)

    def test_gif_width_is_read_from_the_header(self):
        self.assertEqual(p.gif_width(b"GIF89a" + (640).to_bytes(2, "little") + (480).to_bytes(2, "little")), 640)

    def test_the_height_comes_with_the_width(self):
        self.assertEqual(p.image_size(png(1560), "image/png"), (1560, 100))
        self.assertEqual(p.image_size(jpeg(2400), "image/jpeg"), (2400, 50))
        self.assertEqual(p.image_size(b"GIF89a" + (640).to_bytes(2, "little") + (480).to_bytes(2, "little"),
                                      "image/gif"), (640, 480))
        self.assertEqual(p.image_size(svg("width='300' height='200px'"), "image/svg+xml"), (300, 200))
        self.assertEqual(p.image_size(svg("viewBox='0 0 3200 1800'"), "image/svg+xml"), (3200, 1800))
        self.assertEqual(p.image_size(svg("width='1600' viewBox='0 0 3200 1800'"), "image/svg+xml"), (1600, 900))
        self.assertIsNone(p.image_size(b"<html>not an image</html>", "text/html"))

    def test_svg_width_is_the_attribute_else_the_view_box(self):
        self.assertEqual(p.image_width(svg("width='1500px' viewBox='0 0 10 10'"), "image/svg+xml"), 1500)
        self.assertEqual(p.image_width(svg("viewBox='0 0 3200 1800'"), "image/svg+xml"), 3200)
        self.assertIsNone(p.image_width(svg(""), "image/svg+xml"))

    def test_an_unknown_type_has_no_width(self):
        self.assertIsNone(p.image_width(b"<html>not an image</html>", "text/html"))

    def test_a_vague_content_type_yields_to_the_extension(self):
        self.assertEqual(p.content_kind("https://x/a.svg", "application/octet-stream"), "image/svg+xml")
        self.assertEqual(p.content_kind("https://x/a.png", "image/png"), "image/png")


class InlineImages(unittest.TestCase):
    def run_images(self, html_text, answers):
        soup = p.BeautifulSoup("", "html.parser")
        article = p.BeautifulSoup(html_text, "html.parser")
        with FakeFetch({IMAGES + name: value for name, value in answers.items()}):
            sheets = p.inline_images(article, IMAGES + "page.html", soup)
        return article, sheets

    def test_a_wide_png_alone_in_a_paragraph_is_a_figure_and_a_sheet(self):
        article, sheets = self.run_images('<p><img src="w.png" alt="Wiring"></p>', {"w.png": (png(3000), "image/png")})
        self.assertEqual(len(sheets), 1)
        self.assertIsNotNone(article.select_one("figure.inflow > img"))
        self.assertIsNone(article.find("p"))
        self.assertEqual(article.select_one("figure.inflow figcaption").get_text(),
                         "[Wiring: full size on a landscape sheet of its own.]")
        key = sheets[0]["data-wide"]
        self.assertIn(f"<!--sheet-of-wide-{key}-->", str(article))
        self.assertEqual(p.with_sheets(str(article.figcaption), {}, {key: 31}),
                         "<figcaption>[Wiring: full size on a landscape sheet of its own, sheet 31.]</figcaption>")
        self.assertNotIn("sheet-of-wide", p.without_sheets(str(article)))
        self.assertIn("wide", sheets[0]["class"])
        self.assertIsNotNone(sheets[0].find("img"))
        self.assertIn(IMAGES + "w.png", sheets[0].find("figcaption").get_text())

    def test_a_wide_png_among_text_keeps_the_text_and_no_figure_is_inside_a_paragraph(self):
        article, sheets = self.run_images(
            '<p>before <img src="w.png"> after</p>', {"w.png": (png(3000), "image/png")})
        self.assertEqual(len(sheets), 1)
        self.assertEqual(article.find("p").get_text(), "before  after")
        self.assertIsNone(article.select_one("p figure"))
        self.assertIsNotNone(article.select_one("p + figure.inflow figcaption"))
        self.assertIsNone(article.select_one("p img"))
        self.assertIsNotNone(article.select_one("figure.inflow > img"))

    def test_a_wide_image_alone_in_a_paragraph_removes_the_paragraph_and_keeps_the_pointer(self):
        article, sheets = self.run_images(
            '<p>one</p><p><img src="w.png" alt="Wiring"></p><p>two</p>', {"w.png": (png(3000), "image/png")})
        self.assertEqual([tag.name for tag in article.find_all(True, recursive=False)], ["p", "figure", "p"])
        self.assertEqual(len(article.find_all("p")), 2)
        self.assertEqual(len(article.select("figure.inflow figcaption")), 1)

    def test_a_wide_image_with_text_keeps_the_text_and_puts_the_pointer_after_the_paragraph(self):
        article, sheets = self.run_images(
            '<p>before <img src="w.png"> after</p>', {"w.png": (png(3000), "image/png")})
        self.assertEqual([tag.name for tag in article.find_all(True, recursive=False)], ["p", "figure"])
        self.assertIn("before", article.find("p").get_text())
        self.assertIn("after", article.find("p").get_text())
        self.assertIsNone(article.select_one("p figure"))

    def test_several_wide_images_of_one_paragraph_keep_their_order(self):
        article, sheets = self.run_images(
            '<p>text <img src="a.png" alt="First"> and <img src="b.png" alt="Second"> and <img src="c.png" alt="Third"></p>',
            {name: (png(3000), "image/png") for name in ("a.png", "b.png", "c.png")})
        self.assertEqual([tag.name for tag in article.find_all(True, recursive=False)],
                         ["p", "figure", "figure", "figure"])
        self.assertEqual([c.get_text()[1:6] for c in article.select("figure.inflow figcaption")],
                         ["First", "Secon", "Third"])
        self.assertEqual([s.find("figcaption").get_text()[:6] for s in sheets], ["First ", "Second", "Third "])

    def test_a_wide_png_in_a_list_item_leaves_its_pointer_in_the_item(self):
        article, sheets = self.run_images(
            '<ul><li>step <img src="w.png"></li></ul>', {"w.png": (png(3000), "image/png")})
        self.assertIsNotNone(article.select_one("li figure.inflow figcaption"))
        self.assertIn("step", article.find("li").get_text())
        self.assertIsNotNone(article.select_one("li figure.inflow > img"))
        self.assertEqual(len(sheets), 1)

    def test_a_narrow_png_stays_inline_as_a_data_uri_without_sizes(self):
        article, sheets = self.run_images(
            '<p><img src="n.png" width="50" height="20" srcset="n2.png 2x" style="x:y"></p>',
            {"n.png": (png(400), "image/png")})
        self.assertEqual(sheets, [])
        image = article.find("img")
        self.assertTrue(image["src"].startswith("data:image/png;base64,"))
        for attribute in ("width", "height", "srcset", "style"):
            self.assertNotIn(attribute, image.attrs)
        self.assertIsNone(article.find("figure"))

    def test_an_svg_link_gives_an_svg_data_uri_and_one_landscape_sheet(self):
        article, sheets = self.run_images(
            '<p><a href="big.svg"><img src="big.png" alt="Pins"></a></p>',
            {"big.png": (png(1500), "image/png"), "big.svg": (svg("viewBox='0 0 3000 1000'"), "image/svg+xml")})
        self.assertEqual(len(sheets), 1)
        self.assertTrue(sheets[0].find("img")["src"].startswith("data:image/svg+xml;base64,"))
        self.assertIn(IMAGES + "big.svg", sheets[0].find("figcaption").get_text())

    def test_a_narrow_image_linked_to_a_narrow_svg_stays_in_the_text_as_vector(self):
        article, sheets = self.run_images(
            '<p><a href="s.svg"><img src="s.png"></a></p>',
            {"s.png": (png(300), "image/png"), "s.svg": (svg("width='300'"), "image/svg+xml")})
        self.assertEqual(sheets, [])
        self.assertTrue(article.find("img")["src"].startswith("data:image/svg+xml;base64,"))

    def test_a_step_picture_rendered_at_double_size_stays_in_the_text(self):
        article, sheets = self.run_images('<p><img src="step.png" alt="Step"></p>', {"step.png": (png(1560), "image/png")})
        self.assertEqual(sheets, [])
        self.assertIsNotNone(article.find("img"))

    def test_an_svg_drawn_wide_is_a_sheet_at_its_drawn_width(self):
        article, sheets = self.run_images(
            '<p><img src="w.svg" alt="Sheet"></p>', {"w.svg": (svg("viewBox='0 0 1600 900'"), "image/svg+xml")})
        self.assertEqual(len(sheets), 1)

    def test_two_wide_images_in_one_link_do_not_crash_and_each_gets_a_sheet(self):
        article, sheets = self.run_images(
            '<p><a href="https://example.org/x"><img src="a.png"><img src="b.png"></a></p>',
            {"a.png": (png(3000), "image/png"), "b.png": (png(2400), "image/png")})
        self.assertEqual(len(sheets), 2)
        self.assertEqual(len(article.select("figure.inflow figcaption")), 2)
        self.assertEqual(len(article.select("figure.inflow img")), 2)
        self.assertIsNone(article.select_one("p img"))
        self.assertEqual(len([s for s in sheets if s.find("img") is not None]), 2)

    def test_text_in_the_same_link_as_a_wide_image_is_kept(self):
        article, sheets = self.run_images(
            '<p><a href="https://example.org/x">the sheet <img src="a.png"></a></p>', {"a.png": (png(3000), "image/png")})
        self.assertEqual(article.find("a").get_text(strip=True), "the sheet")
        self.assertIsNone(article.select_one("a img"))
        self.assertIsNotNone(article.select_one("figure.inflow > img"))
        self.assertIsNotNone(article.select_one("figure.inflow figcaption"))
        self.assertIsNotNone(sheets[0].find("img"))

    def test_a_wide_picture_shown_twice_in_a_chapter_has_one_sheet_and_two_lines_naming_it(self):
        article, sheets = self.run_images(
            '<p><img src="w.png" alt="Wiring"></p><p>steps</p><p><img src="w.png" alt="Wiring"></p>',
            {"w.png": (png(3000), "image/png")})
        self.assertEqual(len(sheets), 1)
        self.assertEqual(len(article.select("figure.inflow > img")), 2)
        self.assertEqual(str(article).count(f"<!--sheet-of-wide-{sheets[0]['data-wide']}-->"), 2)

    def test_a_png_and_a_link_to_its_svg_are_one_sheet_and_the_sheet_is_the_vector(self):
        article, sheets = self.run_images(
            '<p><img src="_images/sheet.png" alt="Wiring"></p>'
            '<p><a href="_downloads/abc/sheet.svg"><img src="_images/sheet.png" alt="Wiring"></a></p>',
            {"_images/sheet.png": (png(3200), "image/png"),
             "_downloads/abc/sheet.svg": (svg("viewBox='0 0 1600 900'"), "image/svg+xml")})
        self.assertEqual(len(sheets), 1)
        self.assertTrue(sheets[0].find("img")["src"].startswith("data:image/svg+xml;base64,"))
        self.assertIn("sheet.svg", sheets[0].find("figcaption").get_text())
        self.assertEqual(len(article.select("figure.inflow > img, figure.inflow > a > img")), 2)

    def test_the_same_page_as_two_chapters_gives_each_its_own_sheet_and_key(self):
        keys = []
        for chapter in (1, 2):
            article = p.BeautifulSoup('<p><img src="w.png" alt="Wiring"></p>', "html.parser")
            with FakeFetch({IMAGES + "w.png": (png(3000), "image/png")}):
                sheets = p.inline_images(article, IMAGES + "page.html", p.BeautifulSoup("", "html.parser"), chapter)
            keys.append(sheets[0]["data-wide"])
        self.assertNotEqual(keys[0], keys[1])

    def test_two_different_wide_pictures_with_one_name_stop_the_run(self):
        with self.assertRaises(SystemExit) as stop:
            self.run_images(
                '<p><img src="a/sheet.png"></p><p><img src="b/sheet.png"></p>',
                {"a/sheet.png": (png(3000), "image/png"), "b/sheet.png": (png(3000), "image/png")})
        self.assertIn("sheet", str(stop.exception))

    def test_a_png_is_wide_from_twice_the_drawn_width_and_an_svg_from_the_drawn_width(self):
        for name, content, kind, wide in (
            ("a.png", png(p.RASTER_WIDE_PX - 1), "image/png", 0),
            ("b.png", png(p.RASTER_WIDE_PX), "image/png", 1),
            ("c.svg", svg(f"width='{p.WIDE_PX - 1}'"), "image/svg+xml", 0),
            ("d.svg", svg(f"width='{p.WIDE_PX}'"), "image/svg+xml", 1),
        ):
            _, sheets = self.run_images(f'<p><img src="{name}"></p>', {name: (content, kind)})
            self.assertEqual(len(sheets), wide, name)

    def test_an_unreadable_image_stops_the_run_naming_its_url(self):
        with self.assertRaises(SystemExit) as stop:
            self.run_images('<img src="bad.png">', {"bad.png": (b"<html>404</html>", "text/html")})
        self.assertIn(IMAGES + "bad.png", str(stop.exception))

    def test_a_wide_image_in_a_heading_stops_the_run(self):
        with self.assertRaises(SystemExit):
            self.run_images('<h2>Title <img src="w.png"></h2>', {"w.png": (png(3000), "image/png")})


class LinkNotes(unittest.TestCase):
    def notes_for(self, html_text):
        soup = p.BeautifulSoup("", "html.parser")
        article = p.BeautifulSoup(html_text, "html.parser")
        return article, p.link_notes(article, URL, soup)

    def test_a_link_is_numbered_and_listed_once_even_when_used_twice(self):
        article, box = self.notes_for(
            '<p><a href="https://example.org/a">one</a> <a href="https://example.org/a">again</a>'
            ' <a href="https://example.org/b">two</a></p>')
        self.assertEqual([m.get_text() for m in article.select("sup.ref")], ["[1]", "[1]", "[2]"])
        self.assertEqual([li.get_text() for li in box.select("li")], ["https://example.org/a", "https://example.org/b"])

    def test_a_link_to_a_heading_printed_in_the_chapter_gets_no_number(self):
        article, box = self.notes_for(f'<h2 id="here">Here</h2><p><a href="{URL}#here">up</a></p>')
        self.assertIsNone(box)
        self.assertEqual(article.select("sup.ref"), [])

    def test_the_heading_stays_with_the_first_addresses_and_numbering_runs_on(self):
        links = ''.join(f'<a href="https://example.org/{n}">l{n}</a> ' for n in range(1, 8))
        _, box = self.notes_for(f'<p>{links}</p>')
        together = box.select_one('div.together')
        self.assertEqual(together.find('h2').get_text(), 'Links in this chapter')
        self.assertEqual(len(together.select('li')), p.LINKS_WITH_HEADING)
        rest = box.find_all('ol')[1]
        self.assertEqual(rest['start'], str(p.LINKS_WITH_HEADING + 1))
        self.assertEqual([li.get_text() for li in box.select('li')],
                         [f'https://example.org/{n}' for n in range(1, 8)])

    def test_a_link_in_a_listing_gets_no_mark(self):
        article, box = self.notes_for('<pre>see <a href="https://example.org/a">a</a></pre>')
        self.assertIsNone(box)
        self.assertEqual(article.select("sup.ref"), [])

    def test_a_link_in_a_heading_is_numbered_like_any_other(self):
        article, box = self.notes_for('<h2>Using <a href="https://example.org/a">a</a></h2>')
        self.assertEqual([m.get_text() for m in article.select("h2 sup.ref")], ["[1]"])
        self.assertEqual([li.get_text() for li in box.select("li")], ["https://example.org/a"])

    def test_a_link_that_only_wraps_an_image_gets_no_number_but_one_with_words_does(self):
        _, box = self.notes_for('<p><a href="https://example.org/a"><img src="x"/></a></p>')
        self.assertIsNone(box)
        _, box = self.notes_for('<p><a href="https://example.org/a"><img src="x"/> the sheet</a></p>')
        self.assertEqual([li.get_text() for li in box.select("li")], ["https://example.org/a"])

    def test_a_link_to_a_heading_that_was_cut_away_keeps_its_address(self):
        _, box = self.notes_for(f'<p><a href="{URL}#gone">elsewhere</a></p>')
        self.assertEqual([li.get_text() for li in box.select("li")], [URL + "#gone"])

    def test_a_link_whose_text_is_its_address_gets_no_number(self):
        _, box = self.notes_for('<p><a href="https://example.org/a">https://example.org/a</a></p>')
        self.assertIsNone(box)


class LongBlocks(unittest.TestCase):
    def test_a_long_listing_may_break_and_a_short_one_stays_whole(self):
        article = p.BeautifulSoup("<pre>%s</pre><pre>a\nb</pre>" % ("x\n" * 30), "html.parser")
        p.long_blocks(article)
        long_one, short_one = article.find_all("pre")
        self.assertIn("long", long_one["class"])
        self.assertNotIn("class", short_one.attrs)


class WideSheets(unittest.TestCase):
    INFO = ("Pages:           4\nPage    1 size:      612 x 792 pts (letter)\nPage    2 size:      792 x 612 pts\n"
            "Page    3 size:      612 x 792 pts (letter)\nPage    4 size:      792 x 612 pts\n")
    PAGE = '<figure class="wide" data-wide="aa11"></figure><figure class="wide" data-wide="bb22"></figure>'

    def answer(self, *args, **kwargs):
        return unittest.mock.Mock(stdout=self.INFO)

    def test_each_wide_picture_gets_the_landscape_sheet_in_its_turn(self):
        with unittest.mock.patch.object(p, "run", self.answer):
            self.assertEqual(p.wide_sheets(Path("a.pdf"), self.PAGE), {"aa11": 2, "bb22": 4})

    def test_a_different_number_of_landscape_sheets_stops_the_run(self):
        with unittest.mock.patch.object(p, "run", self.answer), self.assertRaises(SystemExit):
            p.wide_sheets(Path("a.pdf"), self.PAGE + '<figure class="wide" data-wide="cc33"></figure>')

    def test_the_same_key_twice_stops_the_run(self):
        twice = '<figure class="wide" data-wide="aa11"></figure>' * 2
        with unittest.mock.patch.object(p, "run", self.answer), self.assertRaises(SystemExit):
            p.wide_sheets(Path("a.pdf"), twice)

    def test_words_that_look_like_a_wide_sheet_are_not_counted(self):
        with unittest.mock.patch.object(p, "run", self.answer):
            page = self.PAGE + '<p>data-wide="cc33"</p>'
            self.assertEqual(p.wide_sheets(Path("a.pdf"), page), {"aa11": 2, "bb22": 4})

    def test_no_wide_picture_asks_nothing(self):
        self.assertEqual(p.wide_sheets(Path("a.pdf"), "<p>text</p>"), {})

    def test_a_wide_place_without_its_sheet_stops_the_run(self):
        with self.assertRaises(SystemExit):
            p.with_sheets("<figcaption>x<!--sheet-of-wide-aa11--></figcaption>", {}, {})


class StepPictures(unittest.TestCase):
    def run_steps(self, html_text):
        article = p.BeautifulSoup(html_text, "html.parser")
        p.step_pictures(article, p.BeautifulSoup("", "html.parser"))
        return article

    def test_a_picture_is_wrapped_with_the_paragraph_before_it(self):
        article = self.run_steps('<p>1. Cut.</p><p><img src="a.png"></p><p>after</p>')
        step = article.select_one("div.step")
        self.assertEqual([child.name for child in step.children], ["p", "p"])
        self.assertEqual(step.find("p").get_text(), "1. Cut.")
        self.assertIn("picture", step.find_all("p")[1]["class"])
        self.assertEqual(article.find_all("p")[-1].parent.name, "[document]")

    def test_a_list_between_the_words_and_the_picture_comes_along_in_order(self):
        article = self.run_steps('<p>14. Fit.</p><ol><li>off</li></ol><p><a href="x"><img src="a.png"></a></p>')
        self.assertEqual([child.name for child in article.select_one("div.step").children], ["p", "ol", "p"])

    def test_a_second_picture_of_a_step_stays_outside_and_is_still_a_picture(self):
        article = self.run_steps('<p>5. Fill.</p><p><img src="a.png"></p><p><img src="b.png"></p>')
        self.assertEqual(len(article.select("div.step")), 1)
        self.assertEqual(len(article.select("div.step img")), 1)
        self.assertEqual(len(article.select("p.picture")), 2)

    def test_the_small_copy_of_a_wide_picture_stays_with_the_words_before_it(self):
        article = self.run_steps(
            '<p>What you will have.</p><figure class="inflow"><img src="a.png"><figcaption>[x]</figcaption></figure>')
        self.assertEqual([child.name for child in article.select_one("div.step").children], ["p", "figure"])
        self.assertIn("picture", article.find("figure")["class"])

    def test_a_step_whose_words_hold_a_small_image_is_still_kept_with_its_picture(self):
        article = self.run_steps('<p>3. Press <img src="key.png"> twice.</p><p><img src="a.png"></p>')
        self.assertEqual([child.name for child in article.select_one("div.step").children], ["p", "p"])

    def test_a_picture_after_a_heading_or_with_words_around_it_is_not_wrapped(self):
        article = self.run_steps('<h3>Sheet</h3><p><img src="a.png"></p><p>see <img src="b.png"> here</p>')
        self.assertIsNone(article.find("div"))
        self.assertEqual(len(article.select("p.picture")), 1)


def picture(width, height):
    """An image-only paragraph holding a PNG of this many pixels, as inline_images leaves it."""
    content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + width.to_bytes(4, "big") + height.to_bytes(4, "big")
    return f'<p><img alt="pic {width}x{height}" src="{p.as_data_uri(content, "image/png")}"></p>'


def words(count):
    return " ".join(["word"] * (count // 5))


class FitSteps(unittest.TestCase):
    """A step's words and pictures on one sheet (issue #94): shrink the pictures if need be, never below
    PICTURE_MIN_SCALE, and put what still does not fit on the next sheet under a "continued" line."""

    def fit(self, html_text, paper="Letter"):
        soup = p.BeautifulSoup("", "html.parser")
        article = p.BeautifulSoup(html_text, "html.parser")
        p.step_pictures(article, soup)
        p.own_pictures(article, soup)
        said = io.StringIO()
        with contextlib.redirect_stderr(said):
            p.fit_steps(article, soup, paper, "Fitting")
        self.said = said.getvalue().splitlines()
        return article

    def height(self, image):
        style = image.get("style", "")
        self.assertRegex(style, r"^max-height: [0-9.]+mm$")
        return float(style.split()[1][:-2])

    def test_a_step_that_fits_is_left_as_it_is(self):
        article = self.fit("<p>1. Cut.</p>" + picture(1560, 1118))
        self.assertEqual(len(article.select("div.step")), 1)
        self.assertNotIn("style", article.find("img").attrs)
        self.assertIsNone(article.select_one(".continued"))

    def test_a_step_too_tall_for_a_sheet_has_its_picture_shrunk_inside_the_step(self):
        article = self.fit(f"<p>3. {words(1500)}</p>" + picture(1560, 1560))
        image = article.select_one("div.step img")
        width = p.TEXT_MM["Letter"][0]
        self.assertLess(self.height(image), width)  # its natural height: a square as wide as the column
        self.assertGreaterEqual(self.height(image), p.PICTURE_MIN_SCALE * width)
        self.assertIsNone(article.select_one(".continued"))

    def test_the_words_of_a_list_count(self):
        items = "".join(f"<li><p>{words(300)}</p></li>" for _ in range(3))
        self.assertNotIn("style", self.fit("<p>3. Find.</p>" + picture(1560, 1560)).find("img").attrs)
        article = self.fit(f"<p>3. Find.</p><ol>{items}</ol>" + picture(1560, 1560))
        self.assertIn("style", article.select_one("div.step").find("img").attrs)
        self.assertIsNone(article.select_one(".continued"))

    def test_a_second_picture_comes_into_the_step_when_the_whole_fits(self):
        article = self.fit("<p>5. Fill.</p>" + picture(1560, 600) + picture(1560, 600) + "<h2>Next</h2><p>after</p>")
        step = article.select_one("div.step")
        self.assertEqual(len(step.find_all("img")), 2)
        self.assertEqual(step.find_next_sibling().get_text(), "Next")
        self.assertNotIn("style", step.find_all("img")[1].attrs)

    def test_two_pictures_shrink_to_one_common_scale(self):
        article = self.fit("<p>5. Fill.</p>" + picture(1560, 1560) + picture(1560, 780))
        first, second = article.select("div.step img")
        self.assertAlmostEqual(self.height(first), 2 * self.height(second), delta=0.2)

    def test_a_second_picture_that_does_not_fit_goes_on_the_next_sheet_under_the_step_number(self):
        article = self.fit("<p>5. Fill.</p>" + picture(1560, 2116) + picture(1560, 2116) + "<h2>Next</h2>")
        step, continued = article.select("div.step")
        self.assertEqual(continued["class"], ["step", "continued"])
        self.assertEqual(continued.find_previous_sibling(), step)
        self.assertEqual(continued.select_one("p.continued-line").get_text(), "Fitting, step 5, continued: fill")
        self.assertEqual(continued.find("img")["alt"], "pic 1560x2116")
        self.assertEqual(len(step.find_all("img")), 1)
        self.assertEqual(continued.find_next_sibling().get_text(), "Next")
        self.assertIn("print_pages: Fitting, step 5: picture 'pic 1560x2116' moved to the next sheet, under "
                      "\u201cFitting, step 5, continued: fill\u201d", self.said)

    def test_a_first_picture_that_cannot_fit_at_the_smallest_scale_goes_on_the_next_sheet(self):
        article = self.fit(f"<p>2. {words(2500)}</p>" + picture(1560, 2116))
        step, continued = article.select("div.step")
        self.assertIsNone(step.find("img"))
        self.assertEqual(continued.select_one("p.continued-line").get_text(), "Fitting, step 2, continued: " + " ".join(["word"] * 12) + "\u2026")
        self.assertNotIn("style", continued.find("img").attrs)

    def test_a_step_without_a_number_says_it_continues_naming_its_heading_and_first_words(self):
        article = self.fit("<h1>Compute Blade cables: verifying 2, when a test fails</h1><h2>From a line to the wire</h2>"
                           "<p>The two cavity pictures are the ones the cables were built from, shown again.</p>"
                           + picture(1560, 2116) + picture(1560, 2116))
        self.assertEqual(article.select_one("p.continued-line").get_text(),
                         "Fitting, \u201cFrom a line to the wire\u201d, \u201cthe two cavity pictures are the ones the "
                         "cables were built from\u201d, continued from the sheet before")

    def test_a_step_without_a_number_under_the_title_alone_is_named_by_the_chapter(self):
        article = self.fit("<h1>Fitting</h1><p>GND and TCK are the names.</p>" + picture(1560, 2116) * 2)
        self.assertEqual(article.select_one("p.continued-line").get_text(),
                         "Fitting, \u201cGND and TCK are the names\u201d, continued from the sheet before")

    def test_two_steps_without_numbers_under_one_heading_have_two_names(self):
        article = self.fit("<h2>Steps</h2><p>The P1 cavity picture again.</p>" + picture(1560, 600)
                           + "<p>The P2 cavity picture again.</p>" + picture(1560, 600))
        self.assertEqual([div["data-label"] for div in article.select("div.step")],
                         ["Fitting, \u201cSteps\u201d, \u201cthe P1 cavity picture again\u201d",
                          "Fitting, \u201cSteps\u201d, \u201cthe P2 cavity picture again\u201d"])

    def test_a_shrunk_picture_is_said_on_stderr(self):
        self.fit(f"<p>3. {words(1500)}</p>" + picture(1560, 1560))
        self.assertEqual(len(self.said), 1)
        self.assertRegex(self.said[0], r"^print_pages: Fitting, step 3: picture 'pic 1560x1560' shrunk to \d+ mm "
                         r"from \d+ mm \(0\.\d\d of the column's width\)$")

    def test_a_step_that_fits_says_nothing(self):
        self.fit("<p>1. Cut.</p>" + picture(1560, 1118))
        self.assertEqual(self.said, [])

    def test_short_paragraphs_ending_the_section_stay_on_the_sheet_of_the_last_picture(self):
        # Verifying 2 in copy 21: the second cavity picture filled its sheet, and the last of three short
        # paragraphs after it stood alone on the next one.
        ending = "".join(f"<p>{words(180)}</p>" for _ in range(3))
        article = self.fit("<section><p>The two cavity pictures:</p>" + picture(1560, 2116) + picture(1560, 2144)
                           + ending + "</section>")
        step, continued = article.select("div.step")
        tail = continued.find_all(recursive=False)[-1]
        self.assertEqual(tail["class"], ["step-tail"])
        self.assertEqual(len(tail.find_all("p")), 3)
        image = continued.find("img")
        width, height = p.TEXT_MM["Letter"]
        words_mm = sum(p.words_mm(part, width) for part in tail.find_all("p"))
        self.assertLessEqual(self.height(image) + p.PICTURE_BELOW_MM + p.CONTINUED_MM + words_mm,
                             height - p.STEP_SPARE_MM + 0.06)  # the style rounds to 0.1 mm
        self.assertGreaterEqual(self.height(image), p.PICTURE_MIN_SCALE * width * 2144 / 1560)
        self.assertTrue(any("3 paragraph(s) ending its section kept" in line for line in self.said))

    def test_a_step_that_fits_keeps_its_ending_paragraphs_inside_it(self):
        article = self.fit("<section><p>1. Cut.</p>" + picture(1560, 1118) + "<p>Done.</p></section>")
        step = article.select_one("div.step")
        self.assertEqual(step.select_one("div.step-tail").get_text(), "Done.")
        self.assertNotIn("style", step.find("img").attrs)

    def test_paragraphs_followed_by_anything_else_in_the_section_are_left_where_they_are(self):
        for after in ("<h2>Next</h2>", "<table><tr><td>x</td></tr></table>", picture(1560, 600)):
            article = self.fit("<section><p>1. Cut.</p>" + picture(1560, 1118) + "<p>Done.</p>" + after + "</section>")
            self.assertIsNone(article.select_one("div.step-tail"), after)

    def test_paragraphs_too_long_to_keep_are_left_where_they_are(self):
        ending = "".join(f"<p>{words(900)}</p>" for _ in range(3))
        article = self.fit("<section><p>1. Cut.</p>" + picture(1560, 1118) + ending + "</section>")
        self.assertIsNone(article.select_one("div.step-tail"))

    def test_ending_paragraphs_that_would_push_the_picture_below_the_smallest_scale_are_left(self):
        ending = "".join(f"<p>{words(500)}</p>" for _ in range(3))  # under TAIL_MAX_MM, but no room beside it
        article = self.fit(f"<section><p>3. {words(2000)}</p>" + picture(1560, 1560) + ending + "</section>")
        self.assertIsNone(article.select_one("div.step-tail"))

    def test_more_pictures_than_one_sheet_holds_go_on_as_many_sheets_as_they_need(self):
        article = self.fit("<p>4. Look.</p>" + picture(1560, 2116) * 3)
        self.assertEqual(len(article.select("div.continued")), 2)
        self.assertEqual(len(article.select("img")), 3)

    def test_a_heading_before_the_step_goes_to_its_sheet_and_takes_room(self):
        plain = self.fit(f"<p>x</p><p>3. {words(1500)}</p>" + picture(1560, 1560))
        headed = self.fit(f"<p>x</p><h2>Steps</h2><p>3. {words(1500)}</p>" + picture(1560, 1560))
        self.assertLess(self.height(headed.find("img")), self.height(plain.find("img")))

    def test_a4_has_more_room_than_letter(self):
        html_text = f"<p>3. {words(1500)}</p>" + picture(1560, 1560)
        self.assertGreater(self.height(self.fit(html_text, "A4").find("img")),
                           self.height(self.fit(html_text, "Letter").find("img")))

    def test_a_picture_whose_size_cannot_be_read_stops_the_run(self):
        with self.assertRaises(SystemExit):
            self.fit('<p>1. Cut.</p><p><img alt="x" src="a.png"></p>')

    def test_fit_pictures(self):
        self.assertEqual(p.fit_pictures([100, 50], [100, 50], 200), [100, 50])
        heights = p.fit_pictures([100, 50], [100, 50], 120)
        self.assertAlmostEqual(heights[0], 80, delta=0.01)
        self.assertAlmostEqual(heights[1], 40, delta=0.01)
        # The first is already printed at 200/300 of its full height; at the common scale of 0.73 the
        # second shrinks and the first keeps its height, since no picture is printed above its natural size.
        heights = p.fit_pictures([200, 75], [300, 75], 255)
        self.assertEqual(heights[0], 200)
        self.assertAlmostEqual(heights[1], 55, delta=0.01)
        self.assertIsNone(p.fit_pictures([200], [250], p.PICTURE_MIN_SCALE * 250 - 1))

    def test_the_continued_block_starts_a_sheet(self):
        self.assertIn(".continued { break-before: page; }", p.CSS)


class StepNames(unittest.TestCase):
    def test_the_chapter_name_is_the_title_up_to_the_first_comma_after_its_colon(self):
        self.assertEqual(p.chapter_name("Compute Blade cables: JTAG connector 1, prepare the wires"),
                         "Compute Blade cables: JTAG connector 1")
        self.assertEqual(p.chapter_name("Compute Blade cables: fitting"), "Compute Blade cables: fitting")
        self.assertEqual(p.chapter_name("Bootloader EEPROM on a Compute Module in a Compute Blade: does it need "
                                        "anything?"),
                         "Bootloader EEPROM on a Compute Module in a Compute Blade: does it need anything?")
        self.assertEqual(p.chapter_name("Bootloader EEPROM: upgrade and lock"), "Bootloader EEPROM: upgrade and lock")
        self.assertEqual(p.chapter_name("What fpgas.online ran on the ps1 blades, 7 October 2026"),
                         "What fpgas.online ran on the ps1 blades")

    def test_first_words_are_the_first_clause_without_the_number(self):
        self.assertEqual(p.first_words("3. Find wire 1 of the P1 cable and flag the wires, before cutting."),
                         "find wire 1 of the P1 cable and flag the wires")
        self.assertEqual(p.first_words("1. Cut. Then strip."), "cut")
        self.assertEqual(p.first_words("Measure 2.5 mm: then cut"), "measure 2.5 mm")

    def test_a_name_keeps_its_capital(self):
        self.assertEqual(p.first_words("GND and TCK are the names"), "GND and TCK are the names")
        self.assertEqual(p.first_words("P1 goes first"), "P1 goes first")

    def test_long_first_clauses_are_cut_with_an_ellipsis(self):
        self.assertEqual(p.first_words("a b c d e f g h i j k l m n", 3), "a b c\u2026")

    def test_a_numbered_step_is_named_by_chapter_and_number(self):
        words = p.BeautifulSoup("<p>3. Find wire 1 of the P1 cable and flag the wires, before cutting.</p>",
                                "html.parser").p
        self.assertEqual(p.step_names(words, "JTAG connector 1"),
                         ("JTAG connector 1, step 3",
                          "JTAG connector 1, step 3, continued: find wire 1 of the P1 cable and flag the wires"))


class WordsHeight(unittest.TestCase):
    """words_mm: how tall a step's words print, counting what the flat text alone would miss."""

    WIDTH = p.TEXT_MM["Letter"][0]
    LINE = 10 * 1.4 * p.PT_MM

    def mm(self, html_text):
        return p.words_mm(p.BeautifulSoup(html_text, "html.parser").find(), self.WIDTH)

    def test_a_short_paragraph_is_one_line_and_its_margin(self):
        self.assertAlmostEqual(self.mm("<p>Cut.</p>"), self.LINE + 2.5)

    def test_each_br_starts_a_line(self):
        self.assertAlmostEqual(self.mm("<p>a<br>b<br/>c</p>"), 3 * self.LINE + 2.5)
        self.assertAlmostEqual(self.mm("<p>a<br></p>"), self.LINE + 2.5)

    def test_a_nested_list_counts_its_items_its_indent_and_its_margin(self):
        flat = self.mm("<ol><li>a b c</li></ol>")
        nested = self.mm("<ol><li>a<ul><li>b</li><li>c</li></ul></li></ol>")
        self.assertAlmostEqual(flat, self.LINE + 2.5)
        self.assertAlmostEqual(nested, 3 * self.LINE + 2 * 2.5)

    def test_a_nested_list_is_narrower(self):
        text = "word " * 35  # 174 characters: two lines of 89 at the list's width, three of 86 indented again
        self.assertAlmostEqual(self.mm(f"<ul><li>{text}</li></ul>"), 2 * self.LINE + 2.5)
        self.assertAlmostEqual(self.mm(f"<ul><li><ul><li>{text}</li></ul></li></ul>"), 3 * self.LINE + 2 * 2.5)

    def test_code_spans_count_their_padding(self):
        plain = " ".join(["ab"] * 30)  # 89 characters: one line of 92
        coded = " ".join(["<code>ab</code>"] * 30)
        self.assertAlmostEqual(self.mm(f"<p>{plain}</p>"), self.LINE + 2.5)
        self.assertAlmostEqual(self.mm(f"<p>{coded}</p>"), 2 * self.LINE + 2.5)

    def test_a_listing_in_a_step_counts_its_lines(self):
        listing = "<pre>" + "\n".join(["x"] * 10) + "\n</pre>"
        self.assertAlmostEqual(self.mm(listing), 10 * p.CODE_SIZE * 1.3 * p.PT_MM + p.PRE_EXTRA_MM)
        self.assertAlmostEqual(self.mm(f"<ol><li><p>Run:</p>{listing}</li></ol>"),
                               self.LINE + 2.5 + 10 * p.CODE_SIZE * 1.3 * p.PT_MM + p.PRE_EXTRA_MM + 2.5)

    def test_a_listing_printed_smaller_is_shorter(self):
        listing = "\n".join(["x"] * 10)
        self.assertLess(self.mm(f'<pre style="font-size: 6.50pt">{listing}</pre>'), self.mm(f"<pre>{listing}</pre>"))


def marked(html_text, number=3, title="Compute Blade cables: fitting"):
    """html_text as chapter number of a PDF: its steps fitted to Letter, then marked."""
    soup = p.BeautifulSoup("", "html.parser")
    article = p.BeautifulSoup(html_text, "html.parser")
    p.step_pictures(article, soup)
    p.own_pictures(article, soup)
    with contextlib.redirect_stderr(io.StringIO()):
        p.fit_steps(article, soup, "Letter", p.chapter_name(title))
    p.mark_steps(article, soup, number, title)
    return article


TWO_SHEETS = "<p>1. Fit the cables.</p>" + picture(1560, 2116) + picture(1560, 2116) + "<h2>Next</h2>"


def again(first=900, second=1000):
    """A numbered step with a picture, then a repeated picture with its own lead-in line (issue #102)."""
    return ("<section><h2>Steps</h2><p>2. Check each wire with a meter.</p>" + picture(1560, first)
            + "<p>The P1 cavity picture again, to read each wire's cavity from:</p>" + picture(1560, second)
            + "</section>")


AGAIN = again()


class OwnPictures(unittest.TestCase):
    """A picture with its own lead-in words after a numbered step serves that step (issue #102)."""

    def own(self, html_text):
        soup = p.BeautifulSoup("", "html.parser")
        article = p.BeautifulSoup(html_text, "html.parser")
        p.step_pictures(article, soup)
        p.own_pictures(article, soup)
        return article

    def test_an_again_paragraph_and_its_picture_become_a_picture_of_the_step_before(self):
        article = self.own(AGAIN)
        step = article.select_one("div.step")
        self.assertEqual(len(article.select("div.step")), 1)
        unit = step.find_next_sibling()
        self.assertEqual(unit["class"], ["picture", "again"])
        self.assertEqual([part.name for part in unit.find_all(recursive=False)], ["p", "p"])
        self.assertEqual(p.picture_image(unit)["alt"], "pic 1560x1000")

    def test_two_again_pictures_both_serve_the_step(self):
        article = self.own(AGAIN.replace("</section>", "<p>The P2 cavity picture again.</p>"
                                         + picture(1560, 1000) + "</section>"))
        self.assertEqual(len(article.select("div.step")), 1)
        self.assertEqual(len(article.select("div.again")), 2)

    def test_a_numbered_step_with_no_picture_of_its_own_becomes_the_step_of_the_again_picture(self):
        article = self.own("<h2>Steps</h2><p>2. Check each wire.</p><ol><li>beep</li></ol>"
                           "<p>The P1 cavity picture again:</p>" + picture(1560, 1000))
        step = article.select_one("div.step")
        # Its words, and those up to its first picture, are the step's words; the picture is the step's.
        self.assertEqual([part.name for part in step.find_all(recursive=False)], ["p", "ol", "p", "p"])
        self.assertTrue(p.numbered_step(step.p))
        self.assertIn("picture", step.find_all(recursive=False)[-1]["class"])
        self.assertEqual(len(article.select("div.step")), 1)

    def test_a_section_of_pictures_with_no_numbered_step_keeps_its_own_steps(self):
        html_text = ("<h2>From a failing line to the wire</h2><p>The two cavity pictures are these.</p>"
                     + picture(1560, 900) + "<p>The P2 one again.</p>" + picture(1560, 900))
        article = self.own(html_text)
        self.assertEqual(len(article.select("div.step")), 2)
        self.assertIsNone(article.select_one("div.again"))

    def test_a_heading_ends_what_a_step_owns(self):
        article = self.own("<p>2. Check.</p>" + picture(1560, 900) + "<h3>Then</h3><p>Again:</p>"
                           + picture(1560, 900))
        last = article.find_all("img")[-1].parent.parent
        self.assertEqual((last.name, last.get("class")), ("div", ["step"]))
        self.assertFalse(p.numbered_step(last.p))
        self.assertIsNone(article.select_one("div.again"))

    def test_the_next_numbered_step_ends_what_a_step_owns(self):
        article = self.own("<p>2. Check.</p>" + picture(1560, 900) + "<p>3. Then.</p>" + picture(1560, 900))
        self.assertEqual([div.p.get_text() for div in article.select("div.step")], ["2. Check.", "3. Then."])
        self.assertIsNone(article.select_one("div.again"))

    def owned(self, between, own=1):
        """The again picture after a step with own pictures of its own and between before the again line."""
        article = self.own("<section><p>2. Check.</p>" + picture(1560, 900) * own + between
                           + "<p>The P1 cavity picture again:</p>" + picture(1560, 1000) + "</section>")
        self.assertEqual(len(article.select("div.step")), 1, between)
        unit = article.select("div.again")[-1]
        self.assertEqual(p.picture_image(unit)["alt"], "pic 1560x1000", between)
        self.assertIs(unit.find_previous_sibling("div", class_="step"), article.select_one("div.step"), between)
        return unit

    def test_a_listing_a_table_or_a_note_box_before_an_again_picture_comes_along_with_it(self):
        for between, name in (("<pre>make check</pre>", "pre"), ("<table><tr><td>J2</td></tr></table>", "table"),
                              ('<div class="admonition note"><p>Note</p><p>Mind the pins.</p></div>', "div")):
            unit = self.owned(between)
            self.assertEqual([part.name for part in unit.find_all(recursive=False)], [name, "p", "p"], between)

    def test_words_between_pictures_come_along_after_one_or_two_own_pictures(self):
        for own in (1, 2):
            unit = self.owned("<p>Note.</p>", own)
            self.assertEqual([part.get_text() for part in unit.find_all(recursive=False)[:2]],
                             ["Note.", "The P1 cavity picture again:"], own)

    def test_a_second_pair_after_words_is_the_steps_too(self):
        article = self.own(AGAIN.replace("</section>", "<p>A note.</p><p>The P2 cavity picture again.</p>"
                                         + picture(1560, 1100) + "<p>Last words.</p></section>"))
        self.assertEqual(len(article.select("div.step")), 1)
        first, second = article.select("div.again")
        self.assertEqual(p.picture_image(second)["alt"], "pic 1560x1100")
        self.assertEqual([part.get_text() for part in second.find_all(recursive=False)[:2]],
                         ["A note.", "The P2 cavity picture again."])
        self.assertEqual(second.find_next_sibling().get_text(), "Last words.")  # after the last picture: left

    def test_a_number_with_decimals_is_not_a_step(self):
        self.assertFalse(p.numbered_step(p.BeautifulSoup("<p>3.3 V comes from the Acorn.</p>", "html.parser").p))
        self.assertTrue(p.numbered_step(p.BeautifulSoup("<p><strong>3.</strong> Find.</p>", "html.parser").p))
        article = self.own("<p>3.3 V comes from the Acorn.</p>" + picture(1560, 900))
        self.assertFalse(p.owns(article.select_one("div.step")))
        words = p.BeautifulSoup("<p>3.3 V comes from the Acorn.</p>", "html.parser").p
        self.assertEqual(p.step_names(words, "Fitting")[0], "Fitting, \u201c3.3 V comes from the Acorn\u201d")

    def test_fitting_moves_an_again_picture_that_does_not_fit_under_the_steps_continued_line(self):
        article = marked(again(2116, 2116))
        step, continued = article.select("div.step")
        self.assertEqual(continued.select_one("p.continued-line").get_text(" ").split("Z", 1)[-1].strip(),
                         "Compute Blade cables: fitting, step 2, continued: check each wire with a meter")
        self.assertIn("again", continued.find_all(recursive=False)[-1]["class"])
        unit = continued.find_all(recursive=False)[-1]
        self.assertEqual([span.get_text() for span in unit.select("span.step-mark")],
                         ["PPSTEP-L-3-1-1-1-1-Z", "PPSTEP-P-3-1-1-1-Z"])


class MarkSteps(unittest.TestCase):
    def test_each_step_continued_block_and_picture_is_marked_where_it_prints(self):
        article = marked(TWO_SHEETS)
        step, continued = article.select("div.step")
        self.assertEqual((step["data-step"], step["data-block"], step["data-label"], step["data-title"]),
                         ("3-1", "0", "Compute Blade cables: fitting, step 1", "Compute Blade cables: fitting"))
        self.assertEqual((continued["data-step"], continued["data-block"]), ("3-1", "1"))
        self.assertEqual(step.p.contents[0].get_text(), "PPSTEP-W-3-1-Z")
        self.assertEqual(step.find("img").find_previous_sibling().get_text(), "PPSTEP-P-3-1-0-1-Z")
        self.assertEqual(continued.p.contents[0].get_text(), "PPSTEP-K-3-1-1-Z")
        self.assertEqual(continued.find("img").find_previous_sibling().get_text(), "PPSTEP-P-3-1-1-1-Z")
        self.assertEqual([span["class"] for span in article.select("span")], [["step-mark"]] * 4)

    def test_steps_are_numbered_in_order_and_a_picture_in_a_link_is_marked_beside_its_image(self):
        linked = picture(1560, 600).replace("<p><img", '<p><a href="x.svg"><img').replace("></p>", "></a></p>")
        article = marked("<p>1. Cut.</p>" + linked + "<p>2. Strip.</p>" + picture(1560, 600), number=5)
        self.assertEqual([div["data-step"] for div in article.select("div.step")], ["5-1", "5-2"])
        self.assertEqual(article.find("a").contents[0].get_text(), "PPSTEP-P-5-1-0-1-Z")

    def test_the_end_of_each_paragraph_or_list_kept_after_the_last_picture_is_marked(self):
        article = marked("<section><p>2. Cut.</p>" + picture(1560, 1118)
                         + "<p>One.</p><ul><li>a</li><li><p>b</p><ul><li>c</li></ul></li></ul></section>")
        tail = article.select_one("div.step > div.step-tail")
        marks = tail.select("span.step-mark")
        self.assertEqual([mark.get_text() for mark in marks], ["PPSTEP-T-3-1-0-1-Z", "PPSTEP-T-3-1-0-2-Z"])
        self.assertIs(tail.p.contents[-1], marks[0])
        self.assertEqual(marks[1].parent.name, "li")
        self.assertEqual(marks[1].parent.get_text(), "c" + marks[1].get_text())

    def test_a_mark_is_hidden_and_takes_no_room(self):
        self.assertIn(".step-mark { display: inline-block; width: 0; overflow: visible; font-size: 0.1pt;", p.CSS)
        self.assertIn("color: #fff; white-space: nowrap; }", p.CSS)

    def test_the_mark_pattern_does_not_run_into_a_digit_after_it(self):
        self.assertEqual(p.re.findall(p.STEP_MARK_RE, "PPSTEP-W-3-1-Z1. Fit"), [("W", "3-1")])


class CheckSteps(unittest.TestCase):
    """check_steps on a fake PDF: the text of each sheet, made from where each mark is said to print."""

    def sheets(self, article, where, count):
        """The text of count sheets with each mark on the sheet where gives it (1 if not given), and each
        continued line first on its sheet after its mark."""
        texts = [""] * count
        for span in article.select("span.step-mark"):
            mark = span.get_text()
            text = span.parent.get_text() if mark.startswith("PPSTEP-K") else mark
            texts[where.get(mark, 1) - 1] += text.replace(mark, mark + "\n") + "\n"
        return texts

    def test_words_and_pictures_on_one_sheet_pass(self):
        article = marked("<p>1. Cut.</p>" + picture(1560, 1118) + picture(1560, 300))
        self.assertEqual(p.check_steps(self.sheets(article, {}, 1), str(article)), [])

    def test_a_picture_on_the_next_sheet_fails_naming_the_chapter_the_step_and_the_sheets(self):
        article = marked("<p>2. Cut.</p>" + picture(1560, 1118))
        problems = p.check_steps(self.sheets(article, {"PPSTEP-P-3-1-0-1-Z": 2}, 2), str(article))
        self.assertEqual(problems, ["chapter 3, Compute Blade cables: fitting, step 2: its words are on "
                                    "sheet 1 and its picture 'pic 1560x1118' on sheet 2"])

    def test_the_two_sides_of_one_leaf_are_still_a_split(self):
        article = marked("<p>2. Cut.</p>" + picture(1560, 1118))
        where = {"PPSTEP-W-3-1-Z": 3, "PPSTEP-P-3-1-0-1-Z": 4}
        self.assertEqual(len(p.check_steps(self.sheets(article, where, 4), str(article))), 1)

    def test_a_declared_continuation_that_starts_its_sheet_passes(self):
        article = marked(TWO_SHEETS)
        where = {"PPSTEP-K-3-1-1-Z": 2, "PPSTEP-P-3-1-1-1-Z": 2}
        self.assertEqual(p.check_steps(self.sheets(article, where, 2), str(article)), [])

    def test_a_continued_picture_off_its_line_sheet_fails(self):
        article = marked(TWO_SHEETS)
        where = {"PPSTEP-K-3-1-1-Z": 2, "PPSTEP-P-3-1-1-1-Z": 3}
        problems = p.check_steps(self.sheets(article, where, 3), str(article))
        self.assertEqual(len(problems), 1)
        self.assertIn("its continued line (block 1) is on sheet 2 and its picture 'pic 1560x2116' on sheet 3",
                      problems[0])

    def test_a_continued_line_that_does_not_start_its_sheet_fails(self):
        article = marked(TWO_SHEETS)
        texts = self.sheets(article, {"PPSTEP-K-3-1-1-Z": 2, "PPSTEP-P-3-1-1-1-Z": 2}, 2)
        texts[1] = "the end of a paragraph\n" + texts[1]
        problems = p.check_steps(texts, str(article))
        self.assertEqual(len(problems), 1)
        self.assertIn("does not start sheet 2", problems[0])

    def test_a_continued_line_on_the_sheet_of_its_words_fails(self):
        article = marked(TWO_SHEETS)
        problems = p.check_steps(self.sheets(article, {}, 1), str(article))
        self.assertTrue(any("not after its words on sheet 1" in problem for problem in problems))

    def test_a_continued_line_that_does_not_name_its_step_fails(self):
        article = marked(TWO_SHEETS)
        line = article.select_one("p.continued-line")
        line.contents[1].replace_with("Continued from the sheet before")
        where = {"PPSTEP-K-3-1-1-Z": 2, "PPSTEP-P-3-1-1-1-Z": 2}
        problems = p.check_steps(self.sheets(article, where, 2), str(article))
        self.assertEqual(len(problems), 1)
        self.assertIn("does not name the step", problems[0])

    def tailed(self):
        return marked("<section><p>1. Fit the cables.</p>" + picture(1560, 2116) + picture(1560, 2116)
                      + "<p>A failing line.</p><p>Another.</p></section>")

    def test_paragraphs_kept_after_the_last_picture_on_its_sheet_pass(self):
        article = self.tailed()
        self.assertIsNotNone(article.select_one("div.continued > div.step-tail"))
        where = {"PPSTEP-K-3-1-1-Z": 2, "PPSTEP-P-3-1-1-1-Z": 2, "PPSTEP-T-3-1-1-1-Z": 2, "PPSTEP-T-3-1-1-2-Z": 2}
        self.assertEqual(p.check_steps(self.sheets(article, where, 2), str(article)), [])

    def test_paragraphs_kept_after_the_last_picture_ending_on_the_next_sheet_fail(self):
        article = self.tailed()
        where = {"PPSTEP-K-3-1-1-Z": 2, "PPSTEP-P-3-1-1-1-Z": 2, "PPSTEP-T-3-1-1-1-Z": 2, "PPSTEP-T-3-1-1-2-Z": 3}
        self.assertEqual(p.check_steps(self.sheets(article, where, 3), str(article)),
                         ["chapter 3, Compute Blade cables: fitting, step 1: paragraph 2 kept after its last picture "
                          "(on sheet 2) ends on sheet 3: \u201canother\u201d"])

    def test_the_two_sides_of_one_leaf_are_a_split_for_kept_paragraphs_too(self):
        article = marked("<section><p>2. Cut.</p>" + picture(1560, 1118) + "<p>Done.</p></section>")
        where = {"PPSTEP-W-3-1-Z": 3, "PPSTEP-P-3-1-0-1-Z": 3, "PPSTEP-T-3-1-0-1-Z": 4}
        self.assertEqual(len(p.check_steps(self.sheets(article, where, 4), str(article))), 1)

    def test_an_again_picture_on_another_sheet_than_its_steps_words_fails_naming_the_step(self):
        # Issue #102: printed as a step of its own, the pair passed the check sheets away from step 2.
        article = marked(AGAIN)
        self.assertEqual(len(article.select("div.step")), 1)
        where = {"PPSTEP-P-3-1-0-2-Z": 2, "PPSTEP-L-3-1-0-2-1-Z": 2}
        problems = p.check_steps(self.sheets(article, where, 2), str(article))
        self.assertEqual(problems, ["chapter 3, Compute Blade cables: fitting, step 2: its words are on sheet 1 and "
                                    "its picture 'pic 1560x1000' on sheet 2"])
        self.assertEqual(p.check_steps(self.sheets(article, {}, 1), str(article)), [])

    def test_lead_in_words_left_on_another_sheet_than_their_picture_fail(self):
        article = marked(AGAIN)
        where = {"PPSTEP-L-3-1-0-2-1-Z": 1, "PPSTEP-P-3-1-0-2-Z": 2}
        problems = p.check_steps(self.sheets(article, where, 2), str(article))
        self.assertIn("chapter 3, Compute Blade cables: fitting, step 2: the words over its picture 'pic 1560x1000' "
                      "(on sheet 2) end on sheet 1: \u201cthe P1 cavity picture again\u201d", problems)

    def test_an_again_picture_after_a_note_box_is_checked_as_the_steps(self):
        article = marked(again().replace("<p>The P1", '<div class="admonition"><p>Note</p><p>Mind.</p></div><p>The P1'))
        self.assertEqual(len(article.select("div.step")), 1)
        where = {"PPSTEP-P-3-1-0-2-Z": 2, "PPSTEP-L-3-1-0-2-1-Z": 2, "PPSTEP-L-3-1-0-2-2-Z": 2}
        self.assertEqual(len(p.check_steps(self.sheets(article, where, 2), str(article))), 1)

    def test_a_mark_not_found_or_found_twice_cannot_be_checked(self):
        article = marked("<p>2. Cut.</p>" + picture(1560, 1118))
        texts = self.sheets(article, {}, 2)
        self.assertIn("not on exactly one", p.check_steps([texts[0].replace("PPSTEP-W", "x")], str(article))[0])
        self.assertIn("not on exactly one", p.check_steps([texts[0], texts[0]], str(article))[0])
        self.assertIn("not in the page", p.check_steps([texts[0] + "PPSTEP-W-9-9-Z"], str(article))[0])

    def test_marks_are_left_out_of_the_text_a_reader_sees(self):
        self.assertEqual(p.visible("PPSTEP-K-3-1-1-Z\nFitting,  step 1,\ncontinued: \ufb01t"),
                         "Fitting, step 1, continued: fit")


class ShortTables(unittest.TestCase):
    def table(self, rows):
        return "<table>%s</table>" % "".join("<tr><td>%d</td></tr>" % n for n in range(rows))

    def test_a_table_of_at_most_the_limit_is_kept_on_one_sheet_and_a_longer_one_is_not(self):
        article = p.BeautifulSoup(self.table(p.SHORT_ROWS) + self.table(p.SHORT_ROWS + 1), "html.parser")
        p.short_tables(article)
        short_one, long_one = article.find_all("table")
        self.assertIn("short", short_one["class"])
        self.assertNotIn("class", long_one.attrs)

    def test_a_table_of_few_rows_but_much_text_may_run_over(self):
        cell = "y" * (p.SHORT_CHARS + 1)
        article = p.BeautifulSoup(f"<table><tr><td>{cell}</td></tr></table>", "html.parser")
        p.short_tables(article)
        self.assertNotIn("class", article.find("table").attrs)

    def test_a_table_with_a_class_keeps_it(self):
        article = p.BeautifulSoup('<table class="docutils"><tr><td>1</td></tr></table>', "html.parser")
        p.short_tables(article)
        self.assertEqual(article.find("table")["class"], ["docutils", "short"])


class Chapter(unittest.TestCase):
    def make(self, number=3, spec="boards/acorn/wiring#raspberry-pi-5"):
        with FakeFetch({URL: (PAGE.encode(), "text/html")}):
            return p.chapter(number, spec, "0123456789abcdef", "2026-10-05", "A4")

    def test_without_link_lists_no_link_is_numbered_and_no_address_list_is_printed(self):
        with FakeFetch({URL: (PAGE.encode(), "text/html")}):
            _, with_lists = p.chapter(3, "boards/acorn/wiring#raspberry-pi-5", "0123456789abcdef", "2026-10-05",
                                      "A4")
            _, without = p.chapter(3, "boards/acorn/wiring#raspberry-pi-5", "0123456789abcdef", "2026-10-05", "A4",
                                   link_lists=False)
        self.assertIn("Links in this chapter", with_lists)  # the page under test has links to list
        self.assertNotIn("Links in this chapter", without)
        self.assertNotIn('class="ref"', without)
        self.assertNotIn('class="links"', without)

    def test_the_source_line_starts_with_the_chapter_number(self):
        title, text = self.make()
        self.assertEqual(title, "Acorn wiring")
        self.assertIn(f"Chapter 3 · Source: {URL} (sections: raspberry-pi-5)", text)
        self.assertIn("docs commit 0123456789 · fetched 2026-10-05", text)

    def test_the_number_is_the_one_given(self):
        _, text = self.make(number=12, spec="boards/acorn/wiring")
        self.assertIn(f"Chapter 12 · Source: {URL} ·", text)


class RightEdge(unittest.TestCase):
    def test_nothing_is_as_wide_as_the_printable_area(self):
        # Chrome cuts the right border of a box that reaches the area's edge (seen on warning boxes and command
        # blocks, 6 October 2026); the one allowance is on body, so boxes, blocks and tables all get it.
        self.assertIn("body { margin: 0 1pt 0 0; }", p.CSS)
        self.assertNotIn("calc(100%% - 1pt)", p.CSS)


class WholeCodes(unittest.TestCase):
    def test_a_short_code_span_in_a_cell_is_kept_whole_and_a_long_or_spaced_one_is_not(self):
        body = p.BeautifulSoup(
            "<table><tr><td><code>0000:01</code> <code>0x0028e5c45e304854</code> "
            "<code>sudo fpgas-verify --no-publish</code> <code>" + "a" * 25 + "</code></td></tr></table>"
            "<p><code>0000:01</code></p>", "html.parser")
        p.whole_codes(body)
        marked = [c.get_text() for c in body.select("code.whole")]
        self.assertEqual(marked, ["0000:01", "0x0028e5c45e304854"])
        self.assertIn("td code.whole { white-space: nowrap;", p.CSS)


class WholeCodesLimits(unittest.TestCase):
    def marked(self, html):
        body = p.BeautifulSoup(html, "html.parser")
        p.whole_codes(body)
        return [c.get_text() for c in body.select("code.whole")]

    def test_the_length_limit_is_inclusive(self):
        at, over = "a" * p.WHOLE_CODE, "a" * (p.WHOLE_CODE + 1)
        self.assertEqual(self.marked(f"<table><tr><td><code>{at}</code></td><td><code>{over}</code></td></tr></table>"),
                         [at])

    def test_a_row_whose_spans_would_fill_the_sheet_keeps_none_whole_and_other_rows_are_not_affected(self):
        long = "b" * p.WHOLE_CODE
        wide = "".join(f"<td><code>{long}</code></td>" for _ in range(p.WHOLE_ROW // p.WHOLE_CODE + 1))
        fits = "".join(f"<td><code>{long}</code> <code>0000:01</code></td>" for _ in range(p.WHOLE_ROW // p.WHOLE_CODE))
        self.assertEqual(self.marked(f"<table><tr>{wide}</tr><tr>{fits}</tr></table>"),
                         [long, "0000:01"] * (p.WHOLE_ROW // p.WHOLE_CODE))

    def test_a_heading_code_span_does_not_break(self):
        self.assertIn("th code { overflow-wrap: normal; }", p.CSS)


class FitCode(unittest.TestCase):
    def fit(self, *lines):
        soup = p.BeautifulSoup("<div><pre>" + "\n".join(lines) + "</pre></div>", "html.parser")
        p.fit_code(soup.div, soup)
        return soup.div

    def test_a_listing_that_fits_is_left_alone(self):
        body = self.fit("x" * p.code_chars(p.BeautifulSoup("<pre></pre>", "html.parser").pre)[0])
        self.assertIsNone(body.pre.get("style"))
        self.assertIsNone(body.find("p"))

    def test_a_longer_line_is_printed_smaller_and_not_broken(self):
        line = "y" * (p.code_chars(p.BeautifulSoup("<pre></pre>", "html.parser").pre)[0] + 10)
        body = self.fit(line)
        self.assertIn("font-size:", body.pre["style"])
        self.assertEqual(body.pre.get_text(), line)
        self.assertIsNone(body.find("p"))

    def test_a_line_too_long_even_at_the_floor_is_broken_with_marks_that_rebuild_it(self):
        line = "".join(str(i % 10) for i in range(300))
        body = self.fit("short", line)
        self.assertIn(f"font-size: {p.CODE_FLOOR:.2f}pt", body.pre["style"])
        printed = body.pre.get_text().split("\n")
        self.assertEqual(printed[0], "short")
        self.assertTrue(all(row.startswith(p.CONTINUED) for row in printed[2:]))
        rebuilt = printed[1] + "".join(row[len(p.CONTINUED):] for row in printed[2:])
        self.assertEqual(rebuilt, line)
        floor_chars = p.code_chars(p.BeautifulSoup("<pre></pre>", "html.parser").pre)[1]
        self.assertTrue(all(len(row) <= floor_chars for row in printed))
        self.assertIn("leaving out the arrow and the one space after it", body.find("p", class_="code-note").get_text())

    def test_a_listing_in_lists_and_a_box_has_fewer_characters_and_every_place_fits_at_the_floor(self):
        top = p.BeautifulSoup("<pre></pre>", "html.parser").pre
        deep = p.BeautifulSoup('<ul><li><ol><li><div class="admonition"><pre></pre></div></li></ol></li></ul>',
                               "html.parser").pre
        self.assertLess(p.code_chars(deep)[0], p.code_chars(top)[0])
        for block in (top, deep):  # the widths measured in Chrome on A4 (review of PR #50): 497.1 and 443.7 pt
            chars, floor_chars = p.code_chars(block)
            room = 497.1 if block is top else 443.7
            self.assertLessEqual(chars * p.CODE_EM * p.CODE_SIZE, room)
            self.assertLessEqual(floor_chars * p.CODE_EM * p.CODE_FLOOR, room)

    def test_a_tab_counts_as_the_columns_chrome_gives_it(self):
        top = p.code_chars(p.BeautifulSoup("<pre></pre>", "html.parser").pre)[0]
        body = self.fit("\t" * (top // 8 + 1))
        self.assertIn("font-size:", body.pre["style"])

    def test_a_chapter_fits_its_listings(self):
        page = PAGE.replace('<article role="main">', '<article role="main"><pre>' + 'z' * 300 + '</pre>', 1)
        with FakeFetch({URL: (page.encode(), "text/html")}):
            _, text = p.chapter(3, "boards/acorn/wiring", "0123456789abcdef", "2026-10-05", "A4")
        self.assertIn("code-note", text)
        self.assertIn(p.CONTINUED.strip(), text)

    def test_the_browser_never_wraps_a_listing(self):
        self.assertIn("pre { white-space: pre; overflow-wrap: normal; }", p.CSS)


class Notes(unittest.TestCase):
    def test_an_empty_file_stops_the_run(self):
        with self.assertRaises(SystemExit):
            p.notes("\n  \n")

    def test_a_file_of_only_separators_stops_the_run(self):
        with self.assertRaises(SystemExit):
            p.note_boxes("\n---\n  ----  \n")

    def test_several_boxes_are_split_at_lines_of_three_or_more_dashes(self):
        text = "One\na\nb\n---\nTwo\nc\n\n------\nThree\n"
        self.assertEqual(p.note_boxes(text), [("One", ["a", "b"]), ("Two", ["c"]), ("Three", [])])

    def test_windows_line_endings_split_and_trim_like_unix_ones(self):
        text = "One\r\na\r\n---\r\nTwo\r\nb\r\n"
        self.assertEqual(p.note_boxes(text), [("One", ["a"]), ("Two", ["b"])])

    def test_a_box_with_a_heading_and_no_items_is_kept(self):
        self.assertEqual(p.note_boxes("Only a heading\n"), [("Only a heading", [])])
        self.assertIn("<ul></ul>", p.notes("Only a heading\n"))

    def test_two_dashes_or_dashes_in_a_line_do_not_split(self):
        self.assertEqual(p.note_boxes("One\n--\na --- b\n"), [("One", ["--", "a --- b"])])

    def test_notes_renders_every_box(self):
        text = p.notes("One\na\n---\nTwo\nb\nc\n")
        self.assertEqual(text.count('class="admonition"'), 2)
        self.assertIn('<p class="admonition-title">One</p>', text)
        self.assertIn('<p class="admonition-title">Two</p>', text)
        self.assertEqual(text.count("<li>"), 3)

    def test_heading_and_items_are_rendered(self):
        text = p.notes("Parts\n\none\ntwo\n")
        self.assertIn('<p class="admonition-title">Parts</p>', text)
        self.assertEqual(text.count("<li>"), 2)

    def test_items_numbered_in_order_are_a_numbered_list_without_the_typed_numbers(self):
        text = p.notes("Order\n1. first\n2.  second\n---\nOther\n1. only this one is numbered\nplain\n")
        self.assertIn("<ol><li>first</li><li>second</li></ol>", text)
        self.assertIn("<ul><li>1. only this one is numbered</li><li>plain</li></ul>", text)

    def test_a_measurement_at_the_start_of_an_item_is_not_a_number_of_the_list(self):
        self.assertIn("<ul><li>1.5 mm wire</li><li>3.3 V must never reach the host</li></ul>",
                      p.notes("Parts\n1.5 mm wire\n3.3 V must never reach the host\n"))
        self.assertIsNone(p.numbered([]))
        self.assertEqual(p.numbered(["1. only"]), ["only"])
        self.assertEqual(p.numbered([f"{n}. x" for n in range(1, 11)]), ["x"] * 10)

    def test_numbers_that_do_not_count_up_from_one_stop_the_run(self):
        with self.assertRaises(SystemExit):
            p.notes("Order\n1. first\n3. third\n")

    def test_html_is_escaped(self):
        text = p.notes("<b>Head</b>\n<script>x</script>")
        self.assertNotIn("<script>", text)
        self.assertIn("&lt;script&gt;", text)


class Document(unittest.TestCase):
    def make(self, title="Wiring", paper="A4", **notes):
        real = p.chapter
        p.chapter = lambda number, spec, commit, fetched, paper, link_lists: (
            f"Chapter {spec}", f"<div>{spec} {commit[:10]} lists={link_lists}</div>")
        try:
            with FakeFetch({p.ADDONS: (b'{"builds": {"current": {"commit": "0123456789abcdef"}}}', "application/json")}):
                return p.document(title, paper, ["boards/acorn/wiring#a,b", "sites/ps1"], **notes)
        finally:
            p.chapter = real

    def test_the_cover_lists_each_spec_and_the_foot_has_ten_characters_of_commit(self):
        text = self.make()
        self.assertIn("Chapter boards/acorn/wiring#a,b", text)
        self.assertIn("(boards/acorn/wiring: a, b)", text)
        self.assertIn("(sites/ps1)", text)
        self.assertIn("commit 0123456789 ·", text)
        self.assertNotIn("0123456789a", text.split("</style>")[0])

    def test_the_foot_counts_the_appended_sheets_that_carry_no_foot(self):
        self.assertIn('counter(pages) "";', self.make())
        self.assertIn('counter(pages) " + 2 unnumbered";', self.make(appended=2))

    def test_link_lists_are_printed_unless_asked_not_to(self):
        self.assertIn("lists=True", self.make())
        text = self.make(link_lists=False)
        self.assertIn("lists=False", text)
        self.assertNotIn("lists=True", text)

    def test_cover_notes_and_last_sheet_appear(self):
        text = self.make(cover_notes="Cover head\nitem one", last_sheet="Last head\nitem two")
        self.assertIn("Cover head", text)
        self.assertIn("item one", text)
        self.assertIn("Last head", text)
        self.assertLess(text.index("Last head"), text.index("</body>"))

    def test_each_cover_entry_has_a_place_for_its_sheet_number(self):
        text = self.make()
        self.assertEqual(text.count("<!--sheet-of-chapter-"), 2)
        self.assertIn("Chapter boards/acorn/wiring#a,b" + p.SHEET_PLACE % 1 + " <small>", text)
        self.assertIn("Chapter sites/ps1" + p.SHEET_PLACE % 2 + " <small>", text)

    def test_a_last_sheet_is_listed_on_the_cover_as_the_next_chapter(self):
        text = self.make(last_sheet="Last head\nitem two\n---\nSecond box\nx")
        self.assertIn("<li>Last head" + p.SHEET_PLACE % 3 + "</li>", text)
        self.assertIn("Chapter 3 · Added to this copy; not a page of the site", text)
        self.assertIn("Second box", text)
        self.assertEqual(text.count("<!--sheet-of-chapter-"), 3)

    def test_notes_that_are_given_but_empty_stop_the_run(self):
        for name in ("cover_notes", "last_sheet"):
            with self.assertRaises(SystemExit, msg=name):
                self.make(**{name: ""})

    def test_without_a_last_sheet_there_is_no_third_entry(self):
        text = self.make()
        self.assertNotIn(p.SHEET_PLACE % 3, text)
        self.assertNotIn("Added to this copy", text)

    def test_a_quote_or_backslash_in_the_title_does_not_break_the_css_string(self):
        text = self.make(title='Say "hi" \\ there')
        style = text.split("<style>")[1].split("</style>")[0]
        self.assertIn(r'content: "Say \"hi\" \\ there · docs.fpgas.online', style)

    def test_a_title_with_a_line_break_or_angle_bracket_is_refused(self):
        for bad in ("a\nb", "a</style>b"):
            with self.assertRaises(SystemExit):
                self.make(title=bad)

    def test_letter_maps_to_letter(self):
        self.assertIn("size: letter portrait", self.make(paper="Letter"))


class WithSheets(unittest.TestCase):
    PAGE = "<li>A%s</li><li>B%s</li>" % (p.SHEET_PLACE % 1, p.SHEET_PLACE % 2)

    def test_without_sheets_every_place_is_removed(self):
        self.assertEqual(p.without_sheets(self.PAGE), "<li>A</li><li>B</li>")

    def test_no_sheets_at_all_is_not_taken_for_not_yet_known(self):
        with self.assertRaises(SystemExit) as stop:
            p.with_sheets(self.PAGE, {})
        self.assertIn("chapter 1", str(stop.exception))

    def test_with_sheets_each_chapter_gets_its_number(self):
        self.assertEqual(p.with_sheets(self.PAGE, {1: 2, 2: 7}), "<li>A, sheet 2</li><li>B, sheet 7</li>")

    def test_a_chapter_missing_from_the_sheets_stops_the_run(self):
        with self.assertRaises(SystemExit) as stop:
            p.with_sheets(self.PAGE, {1: 2})
        self.assertIn("chapter 2", str(stop.exception))


class ChapterSheets(unittest.TestCase):
    def setUp(self):
        self.saved = (p.shutil.which, p.subprocess.run)
        self.text = ""
        p.shutil.which = lambda name: "/fake/" + name
        p.subprocess.run = self.fake_run
        self.addCleanup(self.restore)
        self.commands = []

    def restore(self):
        p.shutil.which, p.subprocess.run = self.saved

    def fake_run(self, command, **options):
        self.commands.append(command)
        return subprocess.CompletedProcess(command, 0, stdout=self.text, stderr="")

    def stops(self, text, chapters):
        self.text = text
        with self.assertRaises(SystemExit) as stop:
            p.chapter_sheets(Path("a.pdf"), chapters)
        return str(stop.exception)

    def test_each_chapter_is_on_the_sheet_with_its_marker_line(self):
        self.text = ("Cover\n1. Wiring, sheet 2\n\f"
                     "Chapter 1 · Source: https://x/a\ntext\n\f"
                     "more text mentioning Chapter 2 · in a line\n\f"
                     "  Chapter 2 · Source: https://x/b (sections: a)\n\f"
                     "Chapter 3 · Added to this copy; not a page of the site\n")
        self.assertEqual(p.chapter_sheets(Path("a.pdf"), 3), {1: 2, 2: 4, 3: 5})
        self.assertEqual(self.commands, [["pdftotext", "a.pdf", "-"]])

    def test_two_chapters_may_start_on_one_sheet_in_order(self):
        self.text = "Chapter 1 · Source: a\nChapter 2 · Source: b\n"
        self.assertEqual(p.chapter_sheets(Path("a.pdf"), 2), {1: 1, 2: 1})

    def test_a_cover_note_that_starts_like_a_chapter_does_not_count(self):
        self.text = ("Cover\nChapter 2 · see the wiring\n\f"
                     "Chapter 1 · Source: https://x/a\n\f"
                     "Chapter 2 · Source: https://x/b\n")
        self.assertEqual(p.chapter_sheets(Path("a.pdf"), 2), {1: 2, 2: 3})

    def test_a_chapter_found_twice_stops_the_run_naming_it_and_both_sheets(self):
        said = self.stops("Chapter 1 · Source: a\n\fChapter 2 · Source: b\n\fChapter 2 · Source: b\n", 2)
        self.assertIn("chapter 2", said)
        self.assertIn("sheet 2", said)
        self.assertIn("sheet 3", said)

    def test_a_missing_chapter_stops_the_run(self):
        self.assertIn("expected 1 to 3", self.stops("Chapter 1 · Source: a\n\fChapter 3 · Source: c\n", 3))
        self.assertIn("expected 1 to 2", self.stops("Chapter 1 · Source: a\n", 2))

    def test_a_chapter_beyond_the_expected_ones_stops_the_run(self):
        self.stops("Chapter 1 · Source: a\n\fChapter 2 · Source: b\n", 1)

    def test_no_text_at_all_stops_the_run(self):
        self.stops("", 1)

    def test_sheets_going_backwards_stop_the_run(self):
        said = self.stops("Chapter 2 · Source: b\n\fChapter 1 · Source: a\n", 2)
        self.assertIn("chapter 2", said)

    def test_a_missing_pdftotext_stops_the_run(self):
        p.shutil.which = lambda name: None
        with self.assertRaises(SystemExit) as stop:
            p.chapter_sheets(Path("a.pdf"), 1)
        self.assertIn("pdftotext", str(stop.exception))
        self.assertEqual(self.commands, [])


HERE = Path(__file__).parent


class Printing(unittest.TestCase):
    """main() with the browser and poppler faked: no output file unless a checked PDF came."""

    def setUp(self):
        self.work = tempfile.TemporaryDirectory(dir=HERE)
        self.addCleanup(self.work.cleanup)
        self.dir = Path(self.work.name)
        self.commands = []
        self.printed_pages = []
        self.sheet_texts = []
        self.chrome_writes = True
        self.united_fails = False
        self.pages = "Pages:          1\nPage    1 size: 612 x 792 pts (letter)\n"
        self.saved = (p.document, p.shutil.which, p.subprocess.run)
        self.document_args = []
        p.document = lambda *args: self.document_args.append(args) or "<html></html>"
        p.shutil.which = lambda name: "/fake/" + name
        p.subprocess.run = self.fake_run
        self.addCleanup(self.restore)

    def restore(self):
        p.document, p.shutil.which, p.subprocess.run = self.saved

    def fake_run(self, command, **options):
        self.commands.append(command)
        name = Path(command[0]).name
        if name == "chrome" or name == CHROME:
            target = next(c for c in command if c.startswith("--print-to-pdf="))
            # What Chrome was asked to print, as the page held at that moment.
            self.printed_pages.append(Path(urllib.parse.urlparse(command[-1]).path).read_text(encoding="utf-8"))
            if self.chrome_writes:
                Path(target.split("=", 1)[1]).write_bytes(b"%PDF fresh")
        elif name == "pdftotext":
            return subprocess.CompletedProcess(command, 0, stdout=self.sheet_texts.pop(0), stderr="")
        elif name == "pdfinfo":
            return subprocess.CompletedProcess(command, 0, stdout=self.pages, stderr="")
        elif name == "pdfunite":
            if self.united_fails:
                raise subprocess.CalledProcessError(1, command)
            Path(command[-1]).write_bytes(b"%PDF united")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    def main(self, *extra, output="x.pdf"):
        argv = ["print_pages", "--paper", "Letter", "--title", "T", "--output", str(self.dir / output), *extra, "a/b"]
        saved = sys.argv
        sys.argv = argv
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                return p.main()
        finally:
            sys.argv = saved

    def names(self):
        return sorted(path.name for path in self.dir.iterdir())

    def test_a_good_run_writes_the_pdf_and_leaves_nothing_else(self):
        self.assertEqual(self.main(), 0)
        self.assertEqual((self.dir / "x.pdf").read_bytes(), b"%PDF fresh")
        self.assertEqual(self.names(), ["x.pdf"])

    def marked_page(self):
        article = marked("<p>2. Cut.</p>" + picture(1560, 1118))
        p.document = lambda *args: str(article)
        return article

    def test_a_page_whose_steps_print_whole_is_written(self):
        self.marked_page()
        self.sheet_texts = ["PPSTEP-W-3-1-Z\n2. Cut.\nPPSTEP-P-3-1-0-1-Z\n"]
        self.assertEqual(self.main(), 0)
        self.assertEqual(self.names(), ["x.pdf"])

    def test_a_step_split_from_its_picture_stops_the_run_and_leaves_the_print_under_a_marked_name(self):
        self.marked_page()
        self.sheet_texts = ["PPSTEP-W-3-1-Z\n2. Cut.\n\fPPSTEP-P-3-1-0-1-Z\n"]
        with self.assertRaises(SystemExit) as stop:
            self.main()
        self.assertIn("chapter 3, Compute Blade cables: fitting, step 2: its words are on sheet 1 and its picture "
                      "'pic 1560x1118' on sheet 2", str(stop.exception))
        self.assertEqual(self.names(), ["x.STEPS-SPLIT.pdf"])

    def test_paragraphs_kept_after_a_picture_that_run_onto_the_next_sheet_stop_the_run(self):
        # The reviewer's harness for PR #97: a step-tail grown after fit_steps ran onto a sheet of its own.
        article = marked("<section><p>2. Cut.</p>" + picture(1560, 1118) + "<p>A failing line.</p></section>")
        p.document = lambda *args: str(article)
        self.sheet_texts = ["PPSTEP-W-3-1-Z\n2. Cut.\nPPSTEP-P-3-1-0-1-Z\n\fA failing line.PPSTEP-T-3-1-0-1-Z\n"]
        with self.assertRaises(SystemExit) as stop:
            self.main()
        self.assertIn("chapter 3, Compute Blade cables: fitting, step 2: paragraph 1 kept after its last picture "
                      "(on sheet 1) ends on sheet 2: \u201ca failing line\u201d", str(stop.exception))
        self.assertEqual(self.names(), ["x.STEPS-SPLIT.pdf"])

    def test_an_again_picture_split_from_its_step_stops_the_run_with_status_1(self):
        article = marked(AGAIN)
        p.document = lambda *args: str(article)
        self.sheet_texts = ["PPSTEP-W-3-1-Z\n2. Check.\nPPSTEP-P-3-1-0-1-Z\n\fThe P1 cavity picture again\n"
                            "PPSTEP-L-3-1-0-2-1-Z\nPPSTEP-P-3-1-0-2-Z\n"]
        with self.assertRaises(SystemExit) as stop:
            self.main()
        self.assertIn("chapter 3, Compute Blade cables: fitting, step 2: its words are on sheet 1 and its picture "
                      "'pic 1560x1000' on sheet 2", str(stop.exception))
        self.assertIsInstance(stop.exception.code, str)  # a message, so the status is 1
        self.assertEqual(self.names(), ["x.STEPS-SPLIT.pdf"])

    def test_a_page_without_sheet_places_is_printed_once_and_not_read_back(self):
        self.main()
        self.assertEqual(len(self.printed_pages), 1)
        self.assertNotIn("pdftotext", [Path(c[0]).name for c in self.commands])

    def test_a_page_with_sheet_places_is_printed_twice_with_the_numbers_on_the_cover(self):
        p.document = lambda *args: "<html><li>One%s</li></html>" % (p.SHEET_PLACE % 1)
        same = "Cover\n\fChapter 1 · Source: https://x/a\n"
        self.sheet_texts = [same, same]
        self.assertEqual(self.main(), 0)
        self.assertEqual(self.printed_pages, ["<html><li>One</li></html>", "<html><li>One, sheet 2</li></html>"])
        self.assertEqual(self.sheet_texts, [])
        self.assertEqual((self.dir / "x.pdf").read_bytes(), b"%PDF fresh")
        self.assertEqual(self.names(), ["x.pdf"])

    def test_chapters_that_moved_when_the_numbers_were_added_stop_the_run_and_leave_no_output(self):
        p.document = lambda *args: "<html><li>One%s</li></html>" % (p.SHEET_PLACE % 1)
        self.sheet_texts = ["Cover\n\fChapter 1 · Source: a\n", "Cover\n\f\fChapter 1 · Source: a\n"]
        with self.assertRaises(SystemExit) as stop:
            self.main()
        self.assertIn("sheets moved", str(stop.exception))
        self.assertEqual(self.names(), [])

    def test_no_text_from_pdftotext_stops_the_run_and_leaves_no_file(self):
        p.document = lambda *args: "<html><li>One%s</li></html>" % (p.SHEET_PLACE % 1)
        self.sheet_texts = [""]
        with self.assertRaises(SystemExit):
            self.main()
        self.assertEqual(self.names(), [])
        self.assertEqual(len(self.printed_pages), 1)

    def test_a_zero_byte_cover_notes_file_stops_the_run_and_leaves_no_file(self):
        p.document = self.saved[0]
        notes = self.dir / "notes.txt"
        notes.write_bytes(b"")
        with self.assertRaises(SystemExit):
            self.main("--cover-notes", str(notes))
        self.assertEqual(self.names(), ["notes.txt"])
        self.assertEqual(self.printed_pages, [])

    def test_a_zero_byte_last_sheet_file_stops_the_run_and_leaves_no_file(self):
        p.document = self.saved[0]
        notes = self.dir / "last.txt"
        notes.write_bytes(b"")
        with self.assertRaises(SystemExit):
            self.main("--last-sheet", str(notes))
        self.assertEqual(self.names(), ["last.txt"])
        self.assertEqual(self.printed_pages, [])

    def test_a_missing_pdftotext_stops_the_run_before_chrome_is_called(self):
        p.document = lambda *args: "<html><li>One%s</li></html>" % (p.SHEET_PLACE % 1)
        p.shutil.which = lambda name: None if name == "pdftotext" else "/fake/" + name
        with self.assertRaises(SystemExit) as stop:
            self.main()
        self.assertIn("pdftotext", str(stop.exception))
        self.assertEqual(self.commands, [])
        self.assertEqual(self.names(), [])

    def test_a_file_named_like_the_output_but_html_is_not_touched(self):
        (self.dir / "x.html").write_text("precious")
        self.assertEqual(self.main(), 0)
        self.chrome_writes = False
        with self.assertRaises(SystemExit):
            self.main()
        self.assertEqual((self.dir / "x.html").read_text(), "precious")
        self.assertEqual(self.names(), ["x.html", "x.pdf"])

    def test_keep_html_leaves_the_joined_page_beside_a_good_pdf_only(self):
        self.assertEqual(self.main("--keep-html"), 0)
        self.assertEqual(self.names(), ["x.pdf", "x.pdf.html"])
        self.assertEqual((self.dir / "x.pdf.html").read_text(), "<html></html>")
        (self.dir / "x.pdf.html").unlink()
        self.chrome_writes = False
        with self.assertRaises(SystemExit):
            self.main("--keep-html")
        self.assertEqual(self.names(), ["x.pdf"])

    def test_chrome_writing_nothing_stops_the_run_and_leaves_no_output(self):
        self.chrome_writes = False
        with self.assertRaises(SystemExit):
            self.main()
        self.assertEqual(self.names(), [])

    def test_a_stale_pdf_is_not_taken_for_a_new_one(self):
        (self.dir / "x.pdf").write_bytes(b"%PDF stale")
        self.chrome_writes = False
        with self.assertRaises(SystemExit):
            self.main()
        self.assertEqual((self.dir / "x.pdf").read_bytes(), b"%PDF stale")
        self.assertEqual(self.names(), ["x.pdf"])

    def test_an_output_that_is_not_a_pdf_name_is_refused_and_nothing_is_written(self):
        with self.assertRaises(SystemExit) as stop:
            self.main(output="x.html")
        self.assertEqual(stop.exception.code, 2)
        self.assertEqual(self.names(), [])
        self.assertEqual(self.commands, [])

    def test_a_chrome_timeout_is_a_clean_stop(self):
        def slow(command, **options):
            raise subprocess.TimeoutExpired(command, 300)
        p.subprocess.run = slow
        with self.assertRaises(SystemExit) as stop:
            self.main()
        self.assertIn("did not finish", str(stop.exception))
        self.assertEqual(self.names(), [])

    def test_a_chrome_failure_is_a_clean_stop(self):
        def broken(command, **options):
            raise subprocess.CalledProcessError(1, command)
        p.subprocess.run = broken
        with self.assertRaises(SystemExit):
            self.main()
        self.assertEqual(self.names(), [])

    def test_append_joins_after_the_printed_pages(self):
        label = self.dir / "labels.pdf"
        label.write_bytes(b"%PDF label")
        self.main("--append", str(label))
        self.assertEqual((self.dir / "x.pdf").read_bytes(), b"%PDF united")
        self.assertEqual(self.names(), ["labels.pdf", "x.pdf"])
        self.assertEqual([args[-1] for args in self.document_args], [1])  # the foot is told of the label sheet

    def test_without_append_the_foot_counts_no_unnumbered_sheets(self):
        self.main()
        self.assertEqual([args[-1] for args in self.document_args], [0])

    def test_a_failing_pdfunite_leaves_neither_output_nor_partial_file(self):
        label = self.dir / "labels.pdf"
        label.write_bytes(b"%PDF label")
        self.united_fails = True
        with self.assertRaises(SystemExit):
            self.main("--append", str(label))
        self.assertEqual(self.names(), ["labels.pdf"])

    def test_an_appended_pdf_on_the_wrong_paper_stops_the_run_naming_file_and_size(self):
        label = self.dir / "labels.pdf"
        label.write_bytes(b"%PDF label")
        self.pages = "Pages:          1\nPage    1 size: 595.28 x 841.89 pts (A4)\n"
        with self.assertRaises(SystemExit) as stop:
            self.main("--append", str(label))
        self.assertIn("labels.pdf", str(stop.exception))
        self.assertIn("595.28 x 841.89", str(stop.exception))
        self.assertEqual(self.names(), ["labels.pdf"])

    def test_an_appended_pdf_on_the_right_paper_either_way_up_is_accepted(self):
        label = self.dir / "labels.pdf"
        label.write_bytes(b"%PDF label")
        self.pages = "Pages:          2\nPage    1 size: 792 x 612 pts\nPage    2 size: 612.5 x 791 pts\n"
        self.assertEqual(p.appended_sheets([label, label], "Letter"), 4)
        self.main("--append", str(label))
        self.assertEqual((self.dir / "x.pdf").read_bytes(), b"%PDF united")

    def test_a_missing_appended_file_stops_the_run(self):
        with self.assertRaises(SystemExit):
            self.main("--append", str(self.dir / "none.pdf"))
        self.assertEqual(self.names(), [])
        self.assertEqual(self.printed_pages, [])  # stopped before anything was printed


CHROME = p.CHROME


class Css(unittest.TestCase):
    def test_the_stylesheet_takes_each_paper_size(self):
        for paper, size in p.PAPERS.items():
            css = p.CSS % {"paper": size, "foot": "x", "after": ""}
            self.assertIn(f"size: {size} portrait", css)
            self.assertIn(f"size: {size} landscape", css)


if __name__ == "__main__":
    unittest.main()
