#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Tests for the parts of print_pages.py that choose and change page content. No network
and no browser: run with `python -m unittest discover -s tools -p 'test_*.py'`."""

import unittest

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


class Css(unittest.TestCase):
    def test_the_stylesheet_takes_each_paper_size(self):
        for paper, size in p.PAPERS.items():
            css = p.CSS % {"paper": size, "foot": "x"}
            self.assertIn(f"size: {size} portrait", css)
            self.assertIn(f"size: {size} landscape", css)


if __name__ == "__main__":
    unittest.main()
