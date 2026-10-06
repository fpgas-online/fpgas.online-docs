#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Tests for the parts of sync_test_designs.py that change text. No network: run with
`python -m unittest discover -s tools -p 'test_*.py'`."""

import unittest

import sync_test_designs as s

GH = f"https://github.com/{s.REPO}"


class RewriteLinks(unittest.TestCase):
    def page(self, text):
        return s.rewrite_links(text, "docs/verify.md", "docs/verify/fpgas-verify.md", "main")

    def test_link_to_another_pulled_page_goes_to_it_and_keeps_the_fragment(self):
        self.assertEqual(self.page("[i](identity.md#tiny-tapeout-fields)"), "[i](identity.md#tiny-tapeout-fields)")
        self.assertEqual(self.page("[g](verify-goals.md)"), "[g](goals.md)")

    def test_link_to_source_code_goes_to_github(self):
        self.assertEqual(self.page("[r](../verify/src/runner.py)"), f"[r]({GH}/blob/main/verify/src/runner.py)")
        self.assertEqual(self.page("[d](../verify/)"), f"[d]({GH}/tree/main/verify)")

    def test_link_to_a_board_install_section_goes_to_the_board_page_here(self):
        self.assertEqual(self.page("[a](hardware/acorn.md#installing-the-acorn-packages)"),
                         "[a](../boards/acorn/index.md#installing-the-acorn-packages)")

    def test_other_heading_of_a_board_document_goes_to_github(self):
        self.assertEqual(self.page("[a](hardware/acorn.md#clock)"), f"[a]({GH}/blob/main/docs/hardware/acorn.md#clock)")

    def test_document_with_a_page_here_on_the_same_subject(self):
        self.assertEqual(self.page("[p](hardware/acorn-pcie-programming.md)"), "[p](../boards/acorn/pcie-programming.md)")
        self.assertEqual(self.page("[p](hardware/acorn-pcie-programming.md#x)"),
                         f"[p]({GH}/blob/main/docs/hardware/acorn-pcie-programming.md#x)")

    def test_absolute_and_same_page_links_are_left_alone(self):
        for link in ("[x](https://example.org/a.md)", "[x](mailto:a@example.org)", "[x](#the-jtag-idcode)"):
            self.assertEqual(self.page(link), link)

    def test_fenced_code_is_left_alone(self):
        text = "```bash\necho '[x](../verify/)'\n```\n[y](../verify/)"
        self.assertEqual(self.page(text), f"```bash\necho '[x](../verify/)'\n```\n[y]({GH}/tree/main/verify)")

    def test_section_links_resolve_from_the_including_page(self):
        out = s.rewrite_links("[v](../verify.md#installing) [b](#via-jtag) [o](#own)", "docs/hardware/acorn.md",
                              "docs/boards/acorn/index.md", "main", own_fragments={"own"})
        self.assertEqual(out, f"[v](../../verify/fpgas-verify.md#installing) "
                              f"[b]({GH}/blob/main/docs/hardware/acorn.md#via-jtag) [o](#own)")

    def test_link_out_of_the_repository_stops_the_sync(self):
        with self.assertRaises(SystemExit):
            self.page("[x](../../elsewhere.md)")

    def test_a_link_to_a_page_of_this_site_becomes_a_link_inside_the_site(self):
        out = s.rewrite_links(
            "[a](https://docs.fpgas.online/en/latest/boards/acorn/wiring.html#assembly) "
            "[b](https://docs.fpgas.online/en/latest/index.html) "
            "[c](https://docs.fpgas.online/en/latest/no/such/page.html) "
            "[d](https://docs.fpgas.online/en/latest/)",
            "docs/verify.md", "docs/verify/fpgas-verify.md", "main")
        self.assertEqual(
            out,
            "[a](../boards/acorn/wiring.md#assembly) [b](../index.md) "
            "[c](https://docs.fpgas.online/en/latest/no/such/page.html) [d](https://docs.fpgas.online/en/latest/)")
        # only a page's own published address is turned: not a query, not a name without .html, not code
        for same in (
            "[e](https://docs.fpgas.online/en/latest/boards/acorn/wiring.html?highlight=jtag)",
            "[f](https://docs.fpgas.online/en/latest/boards/acorn/wiring)",
            "[g](https://docs.fpgas.online/en/latest/boards/acorn/wiring.md)",
            "```\n[h](https://docs.fpgas.online/en/latest/index.html)\n```",
        ):
            self.assertEqual(s.rewrite_links(same, "docs/verify.md", "docs/verify/fpgas-verify.md", "main"), same)

    def test_a_copied_files_links_to_this_site_are_written_from_the_source_root(self):
        text = (
            "[a](https://docs.fpgas.online/en/latest/verify/fpgas-verify.html#common-failures) "
            "[b](https://docs.fpgas.online/en/latest/boards/acorn/pcie-programming.html) "
            "[c](https://docs.fpgas.online/en/latest/no/such/page.html#x) "
            "[d](https://github.com/fpgas-online/fpgas.online-test-designs/issues/127)\n"
            "```\n[e](https://docs.fpgas.online/en/latest/index.html)\n```\n"
            "https://docs.fpgas.online/en/latest/verify/fpgas-verify.html#common-failures as bare text")
        self.assertEqual(
            s.own_links(text),
            "[a](/verify/fpgas-verify.md#common-failures) [b](/boards/acorn/pcie-programming.md) "
            "[c](https://docs.fpgas.online/en/latest/no/such/page.html#x) "
            "[d](https://github.com/fpgas-online/fpgas.online-test-designs/issues/127)\n"
            "```\n[e](https://docs.fpgas.online/en/latest/index.html)\n```\n"
            "https://docs.fpgas.online/en/latest/verify/fpgas-verify.html#common-failures as bare text")

    def test_link_forms_it_cannot_rewrite_stop_the_sync(self):
        for text in ("[x]: other.md", "![shot](shot.png)", "[x](<other file.md>)", '[x](other.md "title")',
                     '<a href="other.md">x</a>', '<img src="shot.png">'):
            with self.assertRaises(SystemExit, msg=text):
                self.page(text)

    def test_those_forms_inside_fenced_code_are_left_alone(self):
        text = "```\n[x]: other.md\n![shot](shot.png)\n```"
        self.assertEqual(self.page(text), text)


class Section(unittest.TestCase):
    TEXT = "# Board\n\nintro\n\n## Installing\n\n```bash\n## not a heading\n```\n\n### Sub\n\nbody\n\n## Next\n\nmore\n"

    def test_section_runs_to_the_next_heading_of_its_level(self):
        self.assertEqual(s.section(self.TEXT, "Installing", "x.md"),
                         "## Installing\n\n```bash\n## not a heading\n```\n\n### Sub\n\nbody\n")

    def test_last_section_runs_to_the_end(self):
        self.assertEqual(s.section(self.TEXT, "Next", "x.md"), "## Next\n\nmore\n")

    def test_missing_section_is_an_error_naming_it(self):
        with self.assertRaisesRegex(s.Missing, 'x.md: no "## Gone" section'):
            s.section(self.TEXT, "Gone", "x.md")

    def test_fragments_in_ignores_fenced_code(self):
        self.assertEqual(s.fragments_in(self.TEXT), {"board", "installing", "sub", "next"})


class Tables(unittest.TestCase):
    def test_no_destination_is_written_twice(self):
        dests = [*s.PAGES.values(), *(d for d, _ in s.SECTIONS.values())]
        self.assertEqual(len(dests), len(set(dests)))

    def test_every_destination_is_in_a_directory_the_tool_owns(self):
        for dest in [*s.PAGES.values(), *(d for d, _ in s.SECTIONS.values())]:
            self.assertIn(dest.rsplit("/", 1)[0], s.OWNED)


if __name__ == "__main__":
    unittest.main()
