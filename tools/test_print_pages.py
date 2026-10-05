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
        self.assertIsNotNone(article.select_one("figure.inflow img"))
        self.assertIsNone(article.find("p"))
        self.assertIn("full size at the end", article.select_one("figcaption").get_text())
        self.assertIn("wide", sheets[0]["class"])

    def test_a_wide_png_among_text_keeps_the_text_and_no_figure_is_inside_a_paragraph(self):
        article, sheets = self.run_images(
            '<p>before <img src="w.png"> after</p>', {"w.png": (png(3000), "image/png")})
        self.assertEqual(len(sheets), 1)
        self.assertEqual(article.find("p").get_text(), "before  after")
        self.assertIsNone(article.select_one("p figure"))
        self.assertIsNotNone(article.select_one("p + figure.inflow img"))

    def test_a_wide_png_in_a_list_item_stays_in_the_item(self):
        article, _ = self.run_images('<ul><li>step <img src="w.png"></li></ul>', {"w.png": (png(3000), "image/png")})
        self.assertIsNotNone(article.select_one("li figure.inflow img"))
        self.assertIn("step", article.find("li").get_text())

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

    def test_two_wide_images_in_one_link_do_not_crash_and_each_gets_a_sheet(self):
        article, sheets = self.run_images(
            '<p><a href="https://example.org/x"><img src="a.png"><img src="b.png"></a></p>',
            {"a.png": (png(3000), "image/png"), "b.png": (png(2000), "image/png")})
        self.assertEqual(len(sheets), 2)
        self.assertEqual(len(article.select("figure.inflow img")), 2)
        self.assertIsNone(article.select_one("p a"))

    def test_text_in_the_same_link_as_a_wide_image_is_kept(self):
        article, _ = self.run_images(
            '<p><a href="https://example.org/x">the sheet <img src="a.png"></a></p>', {"a.png": (png(3000), "image/png")})
        self.assertEqual(article.find("a").get_text(strip=True), "the sheet")
        self.assertIsNotNone(article.select_one("figure img"))

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


class Notes(unittest.TestCase):
    def test_an_empty_file_stops_the_run(self):
        with self.assertRaises(SystemExit):
            p.notes("\n  \n")

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
        p.chapter = lambda spec, commit, fetched: (f"Chapter {spec}", f"<div>{spec} {commit[:10]}</div>")
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


HERE = Path(__file__).parent


class Printing(unittest.TestCase):
    """main() with the browser and poppler faked: no output file unless a checked PDF came."""

    def setUp(self):
        self.work = tempfile.TemporaryDirectory(dir=HERE)
        self.addCleanup(self.work.cleanup)
        self.dir = Path(self.work.name)
        self.commands = []
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
            if self.chrome_writes:
                Path(target.split("=", 1)[1]).write_bytes(b"%PDF fresh")
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
