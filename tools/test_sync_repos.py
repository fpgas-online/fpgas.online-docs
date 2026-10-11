#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Tests for sync_repos.py: the parts that change text, the tables and the command line. No network: run with
`python -m unittest discover -s tools -p 'test_*.py'`."""

import contextlib
import io
import shutil
import unittest
import unittest.mock

import sync_repos as s

GH = f"https://github.com/{s.TEST_DESIGNS.full}"
INFRA = f"https://github.com/{s.ORG}/fpgas.online-infra"
VERIFY = ("docs/verify.md", "docs/verify/fpgas-verify.md")


def rewrite(text, src=VERIFY[0], at=VERIFY[1], repo="test-designs", **kw):
    return s.rewrite_links(text, src, at, "main", repo=repo, **kw)


def copied(text, names=(), **kw):
    """text as a copied FILES Markdown file of test-designs."""
    return s.rewrite_links(text, "docs/wiring/acorn/generated/x.md", None, "main", repo="test-designs",
                           own_fragments=s.fragments_in(text), files=set(names), **kw)


def repos_with(**infra):
    """REPOS with the infra entry given these tables (for a test)."""
    return unittest.mock.patch.dict(s.REPOS, {"infra": s.Repo("infra", **infra)})


class RewriteLinks(unittest.TestCase):
    def test_link_to_another_pulled_page_goes_to_it_and_keeps_the_fragment(self):
        self.assertEqual(rewrite("[i](identity.md#tiny-tapeout-fields)"), "[i](identity.md#tiny-tapeout-fields)")
        self.assertEqual(rewrite("[g](verify-goals.md)"), f"[g]({GH}/blob/main/docs/verify-goals.md)")

    def test_a_link_from_the_repository_root_is_resolved_there(self):
        self.assertEqual(rewrite("[g](/docs/verify-goals.md#x)"), f"[g]({GH}/blob/main/docs/verify-goals.md#x)")
        self.assertEqual(rewrite("[r](/verify/src/runner.py)"), f"[r]({GH}/blob/main/verify/src/runner.py)")
        self.assertEqual(copied("[g](/docs/identity.md)"), "[g](/verify/identity.md)")
        with self.assertRaises(s.Stop):
            rewrite("[x](/../elsewhere.md)")

    def test_link_to_source_code_goes_to_github(self):
        self.assertEqual(rewrite("[r](../verify/src/runner.py)"), f"[r]({GH}/blob/main/verify/src/runner.py)")
        self.assertEqual(rewrite("[d](../verify/)"), f"[d]({GH}/tree/main/verify)")

    def test_link_to_a_board_install_section_goes_to_the_board_page_here(self):
        self.assertEqual(rewrite("[a](hardware/acorn.md#installing-the-acorn-packages)"),
                         "[a](../boards/acorn/setup/packages.md#installing-the-acorn-packages)")

    def test_other_heading_of_a_board_document_goes_to_github(self):
        self.assertEqual(rewrite("[a](hardware/acorn.md#clock)"), f"[a]({GH}/blob/main/docs/hardware/acorn.md#clock)")

    def test_document_with_a_page_here_on_the_same_subject(self):
        self.assertEqual(rewrite("[p](hardware/acorn-pcie-programming.md)"), "[p](../boards/acorn/pcie-programming.md)")
        self.assertEqual(rewrite("[p](hardware/acorn-pcie-programming.md#x)"),
                         f"[p]({GH}/blob/main/docs/hardware/acorn-pcie-programming.md#x)")

    def test_absolute_and_same_page_links_are_left_alone(self):
        for link in ("[x](https://example.org/a.md)", "[x](mailto:a@example.org)", "[x](#the-jtag-idcode)"):
            self.assertEqual(rewrite(link), link)

    def test_fenced_code_is_left_alone(self):
        text = "```bash\necho '[x](../verify/)'\n```\n[y](../verify/)"
        self.assertEqual(rewrite(text), f"```bash\necho '[x](../verify/)'\n```\n[y]({GH}/tree/main/verify)")

    def test_a_fence_closes_only_with_its_own_character_and_length(self):
        self.assertEqual(rewrite("~~~\n```\n~~~\n[g](verify-goals.md)"), f"~~~\n```\n~~~\n[g]({GH}/blob/main/docs/verify-goals.md)")
        self.assertEqual(rewrite("````\n```\n[g](verify-goals.md)\n````\n[g](verify-goals.md)"),
                         f"````\n```\n[g](verify-goals.md)\n````\n[g]({GH}/blob/main/docs/verify-goals.md)")
        self.assertEqual(rewrite("```\n~~~\n[g](verify-goals.md)\n```\n[g](verify-goals.md)"),
                         f"```\n~~~\n[g](verify-goals.md)\n```\n[g]({GH}/blob/main/docs/verify-goals.md)")

    def test_a_link_whose_label_began_on_the_line_before_is_rewritten(self):
        self.assertEqual(rewrite("see [the\ngoals](verify-goals.md) and [x](identity.md)"),
                         f"see [the\ngoals]({GH}/blob/main/docs/verify-goals.md) and [x](identity.md)")

    def test_section_links_resolve_from_the_including_page(self):
        out = rewrite("[v](../verify.md#installing) [b](#via-jtag) [o](#own)", "docs/hardware/acorn.md",
                      "docs/boards/acorn/index.md", own_fragments={"own"})
        self.assertEqual(out, f"[v](../../verify/fpgas-verify.md#installing) "
                              f"[b]({GH}/blob/main/docs/hardware/acorn.md#via-jtag) [o](#own)")

    def test_link_out_of_the_repository_stops_the_sync(self):
        with self.assertRaises(s.Stop):
            rewrite("[x](../../elsewhere.md)")

    def test_a_link_to_a_page_of_this_site_becomes_a_link_inside_the_site(self):
        out = rewrite("[a](https://docs.fpgas.online/en/latest/boards/acorn/wiring.html#assembly) "
                      "[b](https://docs.fpgas.online/en/latest/index.html) "
                      "[c](https://docs.fpgas.online/en/latest/no/such/page.html) "
                      "[d](https://docs.fpgas.online/en/latest/)")
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
            self.assertEqual(rewrite(same), same)

    def test_a_copied_files_links_are_written_from_the_source_root(self):
        text = (
            "[a](https://docs.fpgas.online/en/latest/verify/fpgas-verify.html#common-failures) "
            "[b](https://docs.fpgas.online/en/latest/boards/acorn/pcie-programming.html) "
            "[c](https://docs.fpgas.online/en/latest/no/such/page.html#x) "
            "[d](https://github.com/fpgas-online/fpgas.online-test-designs/issues/127)\n"
            "```\n[e](https://docs.fpgas.online/en/latest/index.html)\n```\n"
            "https://docs.fpgas.online/en/latest/verify/fpgas-verify.html#common-failures as bare text\n"
            "[f](../../../identity.md) [g](gen.py) [h](#own) [i](#other)\n\n## Own")
        self.assertEqual(
            copied(text),
            "[a](/verify/fpgas-verify.md#common-failures) [b](/boards/acorn/pcie-programming.md) "
            "[c](https://docs.fpgas.online/en/latest/no/such/page.html#x) "
            "[d](https://github.com/fpgas-online/fpgas.online-test-designs/issues/127)\n"
            "```\n[e](https://docs.fpgas.online/en/latest/index.html)\n```\n"
            "https://docs.fpgas.online/en/latest/verify/fpgas-verify.html#common-failures as bare text\n"
            f"[f](/verify/identity.md) [g]({GH}/blob/main/docs/wiring/acorn/generated/gen.py) [h](#own) "
            f"[i]({GH}/blob/main/docs/wiring/acorn/generated/x.md#other)\n\n## Own")

    def test_a_copied_file_shows_only_pictures_copied_beside_it(self):
        text = "![w](w.png){.only-light} [![z](w.png)](w.png)"
        self.assertEqual(copied(text, ["w.png"]), f"![w](w.png){{.only-light}} [![z](w.png)]({GH}/blob/main/docs/wiring/acorn/generated/w.png)")
        with self.assertRaisesRegex(s.Stop, "not copied beside it"):
            copied("![w](other.png)", ["w.png"])
        with self.assertRaises(s.Stop):
            copied("[x](<a b.md>)")

    def test_link_forms_it_cannot_rewrite_stop_the_sync(self):
        for text in ("[x]: other.md", "![shot](shot.png)", "[x](<other file.md>)", '[x](other.md "title")',
                     '<a href="other.md">x</a>', '<img src="shot.png">'):
            with self.assertRaises(s.Stop, msg=text):
                rewrite(text)

    def test_an_anchor_with_only_an_id_passes_unchanged(self):
        text = '<a id="common-failures"></a>\n- [Common failures](verify/common-failures.md)'
        self.assertIn('<a id="common-failures"></a>', rewrite(text))

    def test_those_forms_inside_fenced_code_are_left_alone(self):
        text = "```\n[x]: other.md\n![shot](shot.png)\n```"
        self.assertEqual(rewrite(text), text)


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

    def test_a_section_heading_that_is_there_twice_stops_the_sync(self):
        with self.assertRaisesRegex(s.Stop, "2 times"):
            s.section(self.TEXT + "\n## Next\n", "Next", "x.md")
        self.assertEqual(s.headings_twice(self.TEXT + "\n## Next\n```\n## Installing\n```\n"), ["## Next"])

    def test_a_section_that_is_a_page_s_body_keeps_its_anchor_and_raises_its_headings(self):
        part = "## Installing\n\n```bash\n### fenced\n#### deeper fenced\n```\n\n### Sub\n\n#### Deeper\n\nbody\n"
        self.assertEqual(s.as_body(part, "Installing"),
                         "(installing)=\n\n```bash\n### fenced\n#### deeper fenced\n```\n\n## Sub\n\n### Deeper\n\nbody\n")

    def test_fragments_in_ignores_fenced_code_and_reads_targets(self):
        self.assertEqual(s.fragments_in(self.TEXT + "(kept-id)=\n"), {"board", "installing", "sub", "next", "kept-id"})


class Tables(unittest.TestCase):
    def test_no_destination_is_written_twice(self):
        dests = [d for repo in s.REPOS.values() for d in repo.dests()]
        self.assertEqual(len(dests), len(set(dests)))
        s.check_tables()

    def test_an_anchor_in_any_other_form_stops_the_sync(self):
        for line in ('<a id="Upper"></a>', '<a id="x"></a> ', '<a name="x"></a>', '<a id="x" class="y"></a>',
                     'text <a id="x"></a>'):
            with self.assertRaises(s.Stop, msg=line):
                s.anchors_to_targets(line)

    def test_an_indented_fence_is_still_a_fence(self):
        text = '  ```\n<a id="kept"></a>\n  ```'
        self.assertEqual(s.anchors_to_targets(text), text)

    def test_a_link_to_a_page_this_run_writes_is_a_link_inside_the_site(self):
        page = "verify/not-written-yet"
        self.assertFalse((s.DOCS / "docs" / f"{page}.md").exists())
        text = f"[x](https://docs.fpgas.online/en/latest/{page}.html#y)"
        self.assertEqual(copied(text), text)  # not a page of this site: left alone
        with unittest.mock.patch.dict(s.TEST_DESIGNS.PAGES, {"docs/elsewhere.md": f"docs/{page}.md"}):
            self.assertEqual(copied(text), f"[x](/{page}.md#y)")

    def test_an_id_anchor_line_becomes_a_myst_target_outside_fenced_code(self):
        text = '<a id="common-failures"></a>\n- x\n```\n<a id="kept"></a>\n```'
        self.assertEqual(s.anchors_to_targets(text), '(common-failures)=\n- x\n```\n<a id="kept"></a>\n```')

    def test_an_id_with_an_underscore_is_an_anchor_too(self):
        # GitHub keeps "_" in a heading's slug, as in "who-owns-authorized_keys-and-why"
        self.assertEqual(s.anchors_to_targets('<a id="owns-authorized_keys"></a>'), "(owns-authorized_keys)=")

    def test_an_id_in_shared_stays_the_raw_anchor(self):
        text = '<a id="sources"></a>\n<a id="own"></a>'
        self.assertEqual(s.anchors_to_targets(text, {"sources"}), '<a id="sources"></a>\n(own)=')

    def test_anchor_ids_are_the_id_anchor_lines_outside_fenced_code(self):
        self.assertEqual(s.anchor_ids('<a id="a"></a>\nx <a id="b"></a>\n```\n<a id="c"></a>\n```'), {"a"})

    def test_an_id_anchored_on_two_pages_of_a_repository_is_no_site_label(self):
        texts = {"docs/a.md": '# A\n\n<a id="sources"></a>\n<a id="only-a"></a>\n',
                 "docs/b.md": '# B\n\n<a id="sources"></a>\n'}
        with repos_with(PAGES={"docs/a.md": "docs/x/a.md", "docs/b.md": "docs/x/b.md"}), \
                unittest.mock.patch.object(s, "fetch", side_effect=lambda f, c, p: texts[p].encode()):
            wanted, missing = s.take(s.REPOS["infra"], "main", "c0ffee", lambda _: None, [])
        self.assertEqual(missing, [])
        a, b = (wanted[s.DOCS / f"docs/x/{n}.md"].decode() for n in "ab")
        self.assertIn('\n<a id="sources"></a>\n(only-a)=\n', a)
        self.assertIn('\n<a id="sources"></a>\n', b)
        self.assertNotIn("(sources)=", a + b)

    def test_a_landing_page_gets_a_hidden_toctree_of_pages_that_are_pulled(self):
        for dest, entries in s.TEST_DESIGNS.TOCTREES.items():
            self.assertIn(dest, s.TEST_DESIGNS.PAGES.values())
            text = s.toctree(dest, s.TEST_DESIGNS)
            self.assertTrue(text.startswith("\n```{toctree}\n:hidden:\n\n"), dest)
            here = dest.rsplit("/", 1)[0]
            for title, doc in entries:
                self.assertIn(f"{title} <{doc}>\n", text)
                self.assertIn(f"{here}/{doc}.md", s.TEST_DESIGNS.PAGES.values())
        self.assertEqual(s.toctree("docs/verify/identity.md", s.TEST_DESIGNS), "")

    def test_every_destination_is_in_a_directory_the_tool_owns(self):
        for repo in s.REPOS.values():
            for dest in [*(p.dest for p in repo.pages().values() if p.own_dir),
                         *(d for d, _ in repo.SECTIONS.values()), *(w.dest for w in repo.WRAPPERS if w.own_dir)]:
                self.assertIn(dest.rsplit("/", 1)[0], repo.owned_dirs())


class Ownership(unittest.TestCase):
    def tables(self, *repos):
        return {r.name: r for r in repos}

    def test_two_repositories_claiming_one_directory_is_an_error(self):
        a = s.Repo("a", PAGES={"x.md": "docs/shared/x.md"})
        b = s.Repo("b", PAGES={"y.md": "docs/shared/y.md"})
        with self.assertRaisesRegex(s.Stop, "directory docs/shared is claimed by a and by b"):
            s.check_tables(self.tables(a, b))

    def test_an_owned_directory_inside_another_is_an_error(self):
        a = s.Repo("a", PAGES={"x.md": "docs/a/x.md"})
        b = s.Repo("b", PAGES={"y.md": "docs/a/b/y.md"})
        with self.assertRaisesRegex(s.Stop, r"directory docs/a/b \(b\) is inside directory docs/a \(a\)"):
            s.check_tables(self.tables(a, b))
        one = s.Repo("a", PAGES={"x.md": "docs/a/x.md", "y.md": "docs/a/b/y.md"})
        with self.assertRaisesRegex(s.Stop, "is inside directory docs/a"):
            s.check_tables(self.tables(one))

    def test_two_rows_writing_one_destination_is_an_error(self):
        a = s.Repo("a", PAGES={"x.md": "docs/a/x.md"})
        b = s.Repo("b", WRAPPERS=[s.Wrapper("docs/a/x.md", "X", own_dir=False)])
        with self.assertRaisesRegex(s.Stop, "docs/a/x.md is written by a and by b"):
            s.check_tables(self.tables(a, b))

    def test_a_destination_in_a_directory_another_repository_owns_is_an_error(self):
        a = s.Repo("a", PAGES={"x.md": "docs/a/x.md"})
        b = s.Repo("b", WRAPPERS=[s.Wrapper("docs/a/w.md", "W", own_dir=False)])
        with self.assertRaisesRegex(s.Stop, "which a owns"):
            s.check_tables(self.tables(a, b))

    def test_a_wrapper_includes_only_what_is_written_or_named_as_the_docs_own(self):
        a = s.Repo("a", WRAPPERS=[s.Wrapper("docs/a/w.md", "W", includes=(s.Include("docs/a/gone.md"),))])
        with self.assertRaisesRegex(s.Stop, "which no row writes"):
            s.check_tables(self.tables(a))
        b = s.Repo("b", PAGES={"x.md": "docs/b/x.md"},
                   WRAPPERS=[s.Wrapper("docs/b/w.md", "W", includes=(s.Include("docs/b/x.md", docs_owned=True),))])
        with self.assertRaisesRegex(s.Stop, "as the docs' own, but this tool writes it"):
            s.check_tables(self.tables(b))

    def test_the_tables_as_they_are_agree(self):
        s.check_tables()
        self.assertEqual(list(s.REPOS), ["test-designs", "infra", "site", "tt", "setup-pi", "poe", "cam", "mechanical"])
        for name, repo in s.REPOS.items():
            self.assertEqual(repo.full, f"fpgas-online/fpgas.online-{name}")
            self.assertEqual(repo.empty(), name not in ("test-designs", "infra", "cam"), name)

    def test_a_toctree_lists_only_what_some_row_writes(self):
        a = s.Repo("a", PAGES={"x.md": s.Page("docs/a.md", own_dir=False)}, TOCTREES={"docs/a.md": [("G", "a/gone")]})
        with self.assertRaisesRegex(s.Stop, "the toctree of docs/a.md lists a/gone, which no row writes"):
            s.check_tables(self.tables(a))
        b = s.Repo("b", PAGES={"y.md": s.Page("docs/a/there.md", own_dir=False)})
        a.TOCTREES["docs/a.md"] = [("T", "a/there")]
        s.check_tables(self.tables(a, b))
        a.TOCTREES["docs/other.md"] = []
        with self.assertRaisesRegex(s.Stop, "names docs/other.md, which none of its rows writes"):
            s.check_tables(self.tables(a, b))


class SharedPages(unittest.TestCase):
    """A Page with own_dir=False claims its path and nothing else in its directory."""

    def tables(self, *repos):
        return {r.name: r for r in repos}

    def test_a_shared_page_never_makes_its_directory_owned(self):
        a = s.Repo("a", PAGES={"x.md": s.Page("docs/setup/x.md", own_dir=False), "y.md": "docs/setup/x/y.md"})
        self.assertEqual(a.owned_dirs(), ["docs/setup/x"])
        self.assertEqual(a.dests(), ["docs/setup/x.md", "docs/setup/x/y.md"])
        b = s.Repo("b", PAGES={"z.md": s.Page("docs/setup/z.md", own_dir=False)})
        s.check_tables(self.tables(a, b))

    def test_two_repositories_may_not_claim_one_path(self):
        a = s.Repo("a", PAGES={"x.md": s.Page("docs/setup/x.md", own_dir=False)})
        b = s.Repo("b", PAGES={"y.md": s.Page("docs/setup/x.md", own_dir=False)})
        with self.assertRaisesRegex(s.Stop, "docs/setup/x.md is written by a and by b"):
            s.check_tables(self.tables(a, b))

    def test_a_shared_page_in_a_directory_another_repository_owns_is_an_error(self):
        a = s.Repo("a", PAGES={"x.md": "docs/setup/x/x.md"})
        b = s.Repo("b", PAGES={"y.md": s.Page("docs/setup/x/y.md", own_dir=False)})
        with self.assertRaisesRegex(s.Stop, "which a owns"):
            s.check_tables(self.tables(a, b))

    def test_the_docs_own_file_beside_a_shared_page_is_never_touched_nor_reported(self):
        d = s.DOCS / "docs/zz-shared"
        d.mkdir()
        self.addCleanup(shutil.rmtree, d)
        own = d / "own.md"
        own.write_text("# The docs' own page, mentioning tools/sync_repos.py\n")
        (d / "page.md").write_text("# Written by hand before the sync took it\n")
        tables = {"zz-a": s.Repo("zz-a", PAGES={"docs/a.md": s.Page("docs/zz-shared/page.md", own_dir=False)})}
        with unittest.mock.patch.dict(s.REPOS, tables), \
                unittest.mock.patch.object(s, "resolve", return_value="c0ffee" * 6 + "c0ff"), \
                unittest.mock.patch.object(s, "fetch", return_value=b"# A\n"):
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(s.main(["--repo", "zz-a"]), 0)
            self.assertIn("update docs/zz-shared/page.md", out.getvalue())
            self.assertNotIn("own.md", out.getvalue())
            self.assertEqual(s.stale_files(), {})
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(s.main(["--repo", "zz-a", "--check"]), 0)
        self.assertEqual(sorted(p.name for p in d.iterdir()), ["own.md", "page.md"])
        self.assertEqual(own.read_text(), "# The docs' own page, mentioning tools/sync_repos.py\n")
        self.assertTrue((d / "page.md").read_text().endswith("# A\n"))


class StaleFiles(unittest.TestCase):
    def setUp(self):
        self.dir = s.DOCS / "docs" / "zz-stale-test"
        self.dir.mkdir()
        self.addCleanup(shutil.rmtree, self.dir)

    def test_the_docs_as_they_are_have_none(self):
        shutil.rmtree(self.dir)
        self.dir.mkdir()
        self.assertEqual(s.stale_files(), {})

    def test_a_page_or_source_no_row_accounts_for_is_found_and_named_by_its_repository(self):
        (self.dir / "page.md").write_text(s.marker(s.REPOS["infra"], "docs/x.md", "This page", "main") + "# X\n")
        (self.dir / "wrapper.md").write_text(s.wrapper_marker(s.TEST_DESIGNS) + "# W\n")
        (self.dir / "SOURCE").write_text(s.source_text(s.REPOS["cam"], "main", "c0ffee"))
        (self.dir / "own.md").write_text("# Written by hand, mentioning tools/sync_repos.py\n")
        self.assertEqual(s.stale_files(), {"infra": ["docs/zz-stale-test/page.md"],
                                           "test-designs": ["docs/zz-stale-test/wrapper.md"],
                                           "cam": ["docs/zz-stale-test/SOURCE"]})

    def test_a_stale_file_fails_its_repository_in_check_and_in_a_run(self):
        (self.dir / "page.md").write_text(s.marker(s.REPOS["infra"], "docs/x.md", "This page", "main") + "# X\n")
        for argv in (["--repo", "infra", "--check"], ["--repo", "infra"]):
            err = io.StringIO()
            with repos_with(), contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(s.main(argv), 2)
            self.assertIn("sync: FAILED. fpgas-online/fpgas.online-infra: docs/zz-stale-test/page.md", err.getvalue())
            self.assertTrue((self.dir / "page.md").exists())


class LinksAcrossRepositories(unittest.TestCase):
    def test_a_github_url_to_a_file_another_repository_publishes_here_is_a_link_inside_the_site(self):
        with repos_with(PAGES={"docs/deploy.md": "docs/infra/deploy.md"}):
            out = rewrite(f"[d]({INFRA}/blob/main/docs/deploy.md#step-2) [n]({INFRA}/blob/main/docs/other.md)")
            self.assertEqual(out, f"[d](../infra/deploy.md#step-2) [n]({INFRA}/blob/main/docs/other.md)")
            # in a copied file, written from the source root
            self.assertEqual(copied(f"[d]({INFRA}/blob/some-branch/docs/deploy.md#x)"), "[d](/infra/deploy.md#x)")

    def test_a_relative_link_in_another_repository_goes_to_its_page_here_or_to_its_own_github(self):
        with repos_with(PAGES={"docs/a.md": "docs/infra/a.md", "docs/b.md": "docs/infra/b.md"}):
            out = rewrite("[b](b.md#x) [c](../roles/x/tasks.yml) [t](/README.md)", "docs/a.md", "docs/infra/a.md",
                          repo="infra")
            self.assertEqual(out, f"[b](b.md#x) [c]({INFRA}/blob/main/roles/x/tasks.yml) [t]({INFRA}/blob/main/README.md)")

    def test_a_link_from_another_repository_to_a_test_designs_page_goes_to_it(self):
        with repos_with(PAGES={"docs/a.md": "docs/infra/a.md"}):
            out = rewrite(f"[v]({GH}/blob/main/docs/verify.md#installing)", "docs/a.md", "docs/infra/a.md", repo="infra")
            self.assertEqual(out, "[v](../verify/fpgas-verify.md#installing)")

    def test_a_github_url_to_a_section_s_other_heading_stays_on_github(self):
        url = f"{GH}/blob/main/docs/hardware/acorn.md#clock"
        self.assertEqual(rewrite(f"[a]({url})"), f"[a]({url})")

    def test_a_repository_not_in_the_tables_is_left_alone(self):
        url = "https://github.com/fpgas-online/fpgas.online-unknown/blob/main/docs/verify.md"
        self.assertEqual(rewrite(f"[a]({url})"), f"[a]({url})")


class Labels(unittest.TestCase):
    TITLES = {("repo", "test-designs", "docs/plans/design.md"): "The design",
              ("repo", "infra", "docs/deploy.md"): "Deploying",
              ("page", "docs/verify/identity.md"): "Board identity",
              ("page", "docs/index.md"): "fpgas.online"}

    def titles(self, opens):
        return self.TITLES.get(opens[:3])

    def page(self, text, notes=None):
        return rewrite(text, titles=self.titles, notes=notes)

    def test_a_file_name_as_link_text_becomes_the_title_of_the_page_the_link_opens(self):
        self.assertEqual(self.page("[identity.md](identity.md#x)"), "[Board identity](identity.md#x)")
        self.assertEqual(self.page("[`plans/design.md`](plans/design.md)"),
                         f"[The design]({GH}/blob/main/docs/plans/design.md)")
        self.assertEqual(self.page(f"[docs/deploy.md]({INFRA}/blob/main/docs/deploy.md)"),
                         f"[Deploying]({INFRA}/blob/main/docs/deploy.md)")
        self.assertEqual(self.page("[index.md](https://docs.fpgas.online/en/latest/index.html)"),
                         "[fpgas.online](../index.md)")

    def test_a_published_address_of_a_page_that_moved_goes_to_the_page_that_took_its_place(self):
        moved = {"boards/acorn/old": "boards/acorn/index", "boards/acorn/old#part": "boards/acorn/wiring#assembly",
                 "boards/acorn/gone#part": "boards/acorn/index", "boards/acorn/split": "boards/acorn/wiring#assembly"}
        site = "https://docs.fpgas.online/en/latest/boards/acorn"
        with unittest.mock.patch.dict(s.MOVED, moved, clear=True):
            out = rewrite(f"[a]({site}/old.html) [b]({site}/old.html#part) [c]({site}/old.html#other) "
                          f"[d]({site}/gone.html#part) [e]({site}/split.html) [f]({site}/split.html#mine)")
        # an entry's own "#fragment" is where a section went; a link to the page keeps the fragment it gave
        self.assertEqual(out, "[a](../boards/acorn/index.md) [b](../boards/acorn/wiring.md#assembly) "
                              "[c](../boards/acorn/index.md#other) [d](../boards/acorn/index.md) "
                              "[e](../boards/acorn/wiring.md) [f](../boards/acorn/wiring.md#mine)")

    def test_the_label_names_what_the_rewritten_link_opens(self):
        # a section's document opens the page that includes the section, or, for another heading, the document
        # on GitHub: the label is the title of that one
        titles = {("page", "docs/boards/acorn/setup/packages.md"): "Acorn packages",
                  ("repo", "test-designs", "docs/hardware/acorn.md"): "Acorn (on GitHub)"}.get
        out = rewrite("[acorn.md](hardware/acorn.md#installing-the-acorn-packages) [acorn.md](hardware/acorn.md#clock)",
                      titles=lambda o: titles(o[:3]))
        self.assertEqual(out, "[Acorn packages](../boards/acorn/setup/packages.md#installing-the-acorn-packages) "
                              f"[Acorn (on GitHub)]({GH}/blob/main/docs/hardware/acorn.md#clock)")

    def test_a_label_is_left_and_reported_when_the_title_cannot_be_read(self):
        notes = []
        for text in ("[runner.md](../verify/src/)", "[gone.md](gone.md)", "[x.md](https://example.org/x.md)"):
            label = text.split("]")[0] + "]"
            self.assertTrue(self.page(text, notes).startswith(label), text)
        self.assertEqual(len(notes), 3)
        self.assertIn("not point at a Markdown file", notes[0])
        self.assertIn("could not be read", notes[1])
        self.assertIn("not point at a file of a repository", notes[2])

    def test_other_labels_and_code_are_left_alone(self):
        for text in ("[Goals](identity.md)", "```\n[identity.md](identity.md)\n```"):
            out = self.page(text)
            self.assertNotIn("what it must do", out, text)
        self.assertEqual(rewrite("[verify-goals.md](verify-goals.md)"), f"[verify-goals.md]({GH}/blob/main/docs/verify-goals.md)")

    def test_a_copied_file_s_labels_too(self):
        notes = []
        self.assertEqual(copied(f"[identity.md]({GH}/blob/main/docs/identity.md)", titles=self.titles,
                                notes=notes),
                         "[Board identity](/verify/identity.md)")
        self.assertEqual(notes, [])

    def test_title_of_is_the_first_level_one_heading_outside_code(self):
        self.assertEqual(s.title_of("```\n# not\n```\n<!-- c -->\n# The title\n## b\n# second\n"), "The title")
        self.assertIsNone(s.title_of("## only lower\n"))


class Wrappers(unittest.TestCase):
    def test_every_wrapper_is_today_s_page_byte_for_byte(self):
        for repo in s.REPOS.values():
            for w in repo.WRAPPERS:
                self.assertIsInstance(w.lead, (s.Interim, s.Lead), w.dest)
                if isinstance(w.lead, s.Interim):
                    self.assertEqual((s.DOCS / w.dest).read_text(), s.wrapper_text(repo, w, w.lead.text), w.dest)

    def test_the_acorn_cable_and_check_pages_are_generated(self):
        dests = {w.dest for w in s.TEST_DESIGNS.WRAPPERS}
        for carrier in ("rpi-5", "compute-blade"):
            for page in ("cables", "parts", "jtag-wires", "jtag-housing", "uart-wires", "uart-housing", "bench-check",
                         "fitting"):
                self.assertIn(f"docs/boards/acorn/setup/{carrier}/{page}.md", dests)
            self.assertIn(f"docs/boards/acorn/checks/{carrier}.md", dests)
        self.assertIn("docs/boards/acorn/setup/packages.md", dests)

    def test_a_wrapper_sits_among_hand_written_pages_so_it_claims_only_its_own_path(self):
        # an owned directory is emptied of what the sync does not list: the Acorn tree mixes both kinds of page
        for w in s.TEST_DESIGNS.WRAPPERS:
            self.assertFalse(w.own_dir, w.dest)

    def test_every_wrapper_has_a_type_a_reader_and_a_title_that_fits(self):
        titles = [w.title for w in s.TEST_DESIGNS.WRAPPERS]
        self.assertEqual(len(titles), len(set(titles)))
        for w in s.TEST_DESIGNS.WRAPPERS:
            self.assertIn(w.kind, ("tutorial", "how-to", "reference", "explanation"), w.dest)
            self.assertTrue(w.reader, w.dest)
            self.assertLessEqual(len(w.title), 65, w.title)
            self.assertEqual(w.title.startswith("How to "), w.kind == "how-to", w.title)

    def test_a_wrapper_with_a_type_opens_with_its_front_matter(self):
        w = s.Wrapper("docs/w/a.md", "How to a", s.Interim("**Lead.**"), kind="how-to", reader="someone doing a")
        text = s.wrapper_text(s.REPOS["infra"], w, "**Lead.**")
        self.assertTrue(text.startswith("---\ntype: how-to\nowner: infra maintainers\nreader: someone doing a\n"
                                        f"review: {s.WRAPPER_REVIEW}\n---\n\n% This page is generated"), text)
        self.assertRegex(text[:600], s.OUR_COMMENT)

    def test_interim_leads_are_listed_on_every_run(self):
        notes = []
        w = s.Wrapper("docs/w/a.md", "A", s.Interim("**Lead.**"), (s.Include("docs/w/g.md"),))
        with repos_with(FILES={"docs/w": ("gen", ["g.md"])}, WRAPPERS=[w]), \
                unittest.mock.patch.object(s, "fetch", return_value=b"g\n"):
            wanted, missing = s.take(s.REPOS["infra"], "main", "c0ffee", lambda _: None, notes)
        self.assertEqual(missing, [])
        self.assertEqual(notes, ["docs/w/a.md: interim lead, not yet in infra: move it there and give the row a Lead"])
        self.assertEqual(wanted[s.DOCS / "docs/w/a.md"].decode(),
                         s.wrapper_marker(s.REPOS["infra"]) + "# A\n\n**Lead.**\n\n```{include} g.md\n```\n")

    LEADS = ("# Leads\n\n## w/a.md\n\n**Lead** of [b](b.md) and\n[the site](https://docs.fpgas.online/en/latest/"
             "index.html#x), [g](#from-g).\n\nSecond paragraph.\n\n## w/other.md\n\nno\n")

    def take_lead(self, leads, heading="w/a.md"):
        w = s.Wrapper("docs/w/a.md", "A", s.Lead("docs/leads.md", heading),
                      (s.Include("docs/sites/ps1-login.inc", docs_owned=True), s.Include("docs/w/g.md", True)),
                      s.Toctree(("b", ("Bee", "b")), heading="Pages", maxdepth=1, hidden=False))
        texts = {"docs/leads.md": leads, "gen/g.md": "## From g\n", "docs/b.md": "# B\n"}
        with repos_with(PAGES={"docs/b.md": "docs/w/b.md"}, FILES={"docs/w": ("gen", ["g.md"])}, WRAPPERS=[w]), \
                unittest.mock.patch.object(s, "fetch", side_effect=lambda f, c, p: texts[p].encode()):
            notes = []
            wanted, missing = s.take(s.REPOS["infra"], "main", "c0ffee", lambda _: None, notes)
        return wanted, missing, notes

    def test_a_lead_is_its_section_of_the_home_repository_verbatim_with_its_links_rewritten(self):
        wanted, missing, notes = self.take_lead(self.LEADS)
        self.assertEqual((missing, notes), ([], []))
        self.assertEqual(wanted[s.DOCS / "docs/w/a.md"].decode().split("\n\n", 1)[1],
                         "# A\n\n**Lead** of [b](b.md) and\n[the site](../index.md#x), [g](#from-g).\n\n"
                         "Second paragraph.\n\n"
                         "```{include} ../sites/ps1-login.inc\n```\n\n```{include} g.md\n:relative-images:\n```\n\n"
                         "## Pages\n\n```{toctree}\n:maxdepth: 1\n\nb\nBee <b>\n```\n")

    def test_an_anchor_in_a_lead_that_is_in_neither_it_nor_its_includes_stops_the_sync(self):
        with self.assertRaisesRegex(s.Stop, "#nowhere is not a heading"):
            self.take_lead(self.LEADS.replace("#from-g", "#nowhere"))

    def test_a_leads_file_with_a_heading_twice_stops_the_sync(self):
        with self.assertRaisesRegex(s.Stop, "## w/other.md"):
            self.take_lead(self.LEADS + "\n## w/other.md\n\nagain\n")

    def test_a_lead_section_that_is_not_there_is_missing(self):
        _, missing, _ = self.take_lead(self.LEADS, "w/gone.md")
        self.assertEqual(missing, ['docs/leads.md: no "## w/gone.md" section'])


class CommandLine(unittest.TestCase):
    def run_main(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = s.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_ref_needs_exactly_one_repo(self):
        for argv in (["--ref", "x"], ["--ref", "x", "--repo", "infra", "--repo", "tt"]):
            with self.assertRaises(SystemExit) as e, unittest.mock.patch("sys.stderr"):
                s.main(argv)
            self.assertEqual(e.exception.code, 2)

    def test_an_empty_repository_makes_no_network_call(self):
        with unittest.mock.patch.object(s, "resolve") as resolve, unittest.mock.patch.object(s, "fetch") as fetch:
            self.assertEqual(self.run_main(["--repo", "site", "--repo", "mechanical", "--check"])[0], 0)
        resolve.assert_not_called()
        fetch.assert_not_called()

    def test_a_missing_file_stops_with_2_naming_the_repository_and_the_file(self):
        def gone(full, commit, path):
            raise s.Missing(path)
        with repos_with(PAGES={"docs/deploy.md": "docs/infra-pages/deploy.md"}), \
                unittest.mock.patch.object(s, "resolve", return_value="c0ffee" * 6 + "c0ff"), \
                unittest.mock.patch.object(s, "fetch", side_effect=gone):
            code, _, err = self.run_main(["--repo", "infra", "--check"])
        self.assertEqual(code, 2)
        self.assertIn("sync: FAILED. fpgas-online/fpgas.online-infra: main (c0ffeec0ffee) does not have "
                      "docs/deploy.md", err)

    def test_a_failing_repository_blocks_no_other(self):
        dest = s.DOCS / "docs/zz-healthy/page.md"
        self.addCleanup(shutil.rmtree, dest.parent, True)
        # repositories of their own, so the real ones' synced pages stay accounted for
        tables = {"zz-a": s.Repo("zz-a", PAGES={"docs/a.md": "docs/zz-healthy/page.md"}),
                  "zz-b": s.Repo("zz-b", PAGES={"docs/b.md": "docs/zz-broken/page.md"})}

        def fetch(full, commit, path):
            return b"# A\n" if full.endswith("-zz-a") else b"# B\n[x](../../outside.md)\n"
        with unittest.mock.patch.dict(s.REPOS, tables), \
                unittest.mock.patch.object(s, "resolve", return_value="c0ffee" * 6 + "c0ff"), \
                unittest.mock.patch.object(s, "fetch", side_effect=fetch):
            code, out, err = self.run_main(["--repo", "zz-a", "--repo", "zz-b"])
        self.assertEqual(code, 2)
        self.assertIn("sync: FAILED. fpgas-online/fpgas.online-zz-b: docs/b.md links outside the repository", err)
        self.assertNotIn("fpgas.online-zz-a:", err)
        self.assertTrue(dest.exists(), out)
        self.assertTrue((dest.parent / "SOURCE").exists())
        self.assertFalse((s.DOCS / "docs/zz-broken").exists())

    def test_a_directory_in_an_owned_directory_fails_its_repository_before_anything_is_written(self):
        owned = s.DOCS / "docs/zz-owned"
        (owned / "subdir").mkdir(parents=True)
        (owned / "old.md").write_text("old\n")
        self.addCleanup(shutil.rmtree, owned)
        with repos_with(PAGES={"docs/a.md": "docs/zz-owned/page.md"}), \
                unittest.mock.patch.object(s, "resolve", return_value="c0ffee" * 6 + "c0ff"), \
                unittest.mock.patch.object(s, "fetch", return_value=b"# A\n"):
            code, _, err = self.run_main(["--repo", "infra"])
        self.assertEqual(code, 2)
        self.assertIn("docs/zz-owned/subdir is not a file", err)
        self.assertEqual(sorted(p.name for p in owned.iterdir()), ["old.md", "subdir"])


class Alerts(unittest.TestCase):
    def test_each_kind_of_alert_becomes_its_admonition(self):
        for kind in ("NOTE", "TIP", "IMPORTANT", "WARNING", "CAUTION"):
            text = f"before\n\n> [!{kind}]\n> One [link](x.md) and `code`.\n>\n> Second paragraph.\n\nafter"
            self.assertEqual(s.alerts_to_admonitions(text),
                             f"before\n\n:::{{{kind.lower()}}}\nOne [link](x.md) and `code`.\n\nSecond paragraph.\n"
                             f":::\n\nafter")

    def test_any_letter_case_a_trailing_space_or_no_space_after_the_marker(self):
        for first in ("> [!note]", "> [!Note] ", ">[!NOTE]"):
            self.assertEqual(s.alerts_to_admonitions(f"{first}\n>body\n> more"), ":::{note}\nbody\nmore\n:::", first)

    def test_a_body_with_a_colon_fence_gets_a_longer_one(self):
        text = "> [!TIP]\n> :::{note}\n> inner\n> :::"
        self.assertEqual(s.alerts_to_admonitions(text), "::::{tip}\n:::{note}\ninner\n:::\n::::")

    def test_an_alert_in_a_list_item_keeps_its_indentation(self):
        text = "1. Step one.\n\n   > [!WARNING]\n   > Unplug it first.\n   > Really.\n\n2. Step two."
        self.assertEqual(s.alerts_to_admonitions(text),
                         "1. Step one.\n\n   :::{warning}\n   Unplug it first.\n   Really.\n   :::\n\n2. Step two.")

    def test_plain_blockquotes_and_code_are_left_alone(self):
        for text in ("> just a quote\n> more", "```\n> [!NOTE]\n> in code\n```", "~~~\n> [!NOTE]\n~~~",
                     "> see [!x] here"):
            self.assertEqual(s.alerts_to_admonitions(text), text)

    def test_an_alert_it_cannot_convert_stops_the_sync(self):
        for text in ("> [!DANGER]\n> body", "> [!NOTE] with text\n> body", "  >[!info]\n  > x"):
            with self.assertRaisesRegex(s.Stop, "not an alert this tool can turn", msg=text):
                s.alerts_to_admonitions(text)

    def test_a_line_continuing_the_quote_without_its_marker_stops_the_sync(self):
        with self.assertRaisesRegex(s.Stop, "has no '>'"):
            s.alerts_to_admonitions("> [!NOTE]\n> body\nlazy continuation")
        self.assertEqual(s.alerts_to_admonitions("> [!NOTE]\n> body"), ":::{note}\nbody\n:::")


if __name__ == "__main__":
    unittest.main()
