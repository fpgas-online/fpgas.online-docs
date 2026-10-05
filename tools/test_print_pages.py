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


class ShortTables(unittest.TestCase):
    def table(self, rows):
        return "<table>%s</table>" % "".join("<tr><td>%d</td></tr>" % n for n in range(rows))

    def test_a_table_of_at_most_the_limit_is_kept_on_one_sheet_and_a_longer_one_is_not(self):
        article = p.BeautifulSoup(self.table(p.SHORT_ROWS) + self.table(p.SHORT_ROWS + 1), "html.parser")
        p.short_tables(article)
        short_one, long_one = article.find_all("table")
        self.assertIn("short", short_one["class"])
        self.assertNotIn("class", long_one.attrs)

    def test_a_table_with_a_class_keeps_it(self):
        article = p.BeautifulSoup('<table class="docutils"><tr><td>1</td></tr></table>', "html.parser")
        p.short_tables(article)
        self.assertEqual(article.find("table")["class"], ["docutils", "short"])


class Chapter(unittest.TestCase):
    def make(self, number=3, spec="boards/acorn/wiring#raspberry-pi-5"):
        with FakeFetch({URL: (PAGE.encode(), "text/html")}):
            return p.chapter(number, spec, "0123456789abcdef", "2026-10-05")

    def test_the_source_line_starts_with_the_chapter_number(self):
        title, text = self.make()
        self.assertEqual(title, "Acorn wiring")
        self.assertIn(f"Chapter 3 · Source: {URL} (sections: raspberry-pi-5)", text)
        self.assertIn("docs commit 0123456789 · fetched 2026-10-05", text)

    def test_the_number_is_the_one_given(self):
        _, text = self.make(number=12, spec="boards/acorn/wiring")
        self.assertIn(f"Chapter 12 · Source: {URL} ·", text)


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

    def test_html_is_escaped(self):
        text = p.notes("<b>Head</b>\n<script>x</script>")
        self.assertNotIn("<script>", text)
        self.assertIn("&lt;script&gt;", text)


class Document(unittest.TestCase):
    def make(self, title="Wiring", paper="A4", **notes):
        real = p.chapter
        p.chapter = lambda number, spec, commit, fetched: (f"Chapter {spec}", f"<div>{spec} {commit[:10]}</div>")
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
        p.document = lambda *args: "<html></html>"
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
        self.main("--append", str(label))
        self.assertEqual((self.dir / "x.pdf").read_bytes(), b"%PDF united")

    def test_a_missing_appended_file_stops_the_run(self):
        with self.assertRaises(SystemExit):
            self.main("--append", str(self.dir / "none.pdf"))
        self.assertEqual(self.names(), [])


CHROME = p.CHROME


class Css(unittest.TestCase):
    def test_the_stylesheet_takes_each_paper_size(self):
        for paper, size in p.PAPERS.items():
            css = p.CSS % {"paper": size, "foot": "x"}
            self.assertIn(f"size: {size} portrait", css)
            self.assertIn(f"size: {size} landscape", css)


if __name__ == "__main__":
    unittest.main()
