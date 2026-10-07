#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Tests for sync_repos.py: the parts that change text, the tables and the command line. No network: run with
`python -m unittest discover -s tools -p 'test_*.py'`."""

import unittest
import unittest.mock

import sync_repos as s

GH = f"https://github.com/{s.TEST_DESIGNS.full}"


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
                         "[a](../boards/acorn/packages.md#installing-the-acorn-packages)")

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

    def test_an_anchor_with_only_an_id_passes_unchanged(self):
        text = '<a id="common-failures"></a>\n- [Common failures](verify/common-failures.md)'
        self.assertIn('<a id="common-failures"></a>', self.page(text))

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
        dests = [d for repo in s.REPOS.values() for d in repo.dests()]
        self.assertEqual(len(dests), len(set(dests)))
        s.check_tables()

    def test_an_anchor_in_any_other_form_stops_the_sync(self):
        for line in ('<a id="Upper"></a>', '<a id="x"></a> ', '<a name="x"></a>', '<a id="x" class="y"></a>',
                     'text <a id="x"></a>'):
            with self.assertRaises(SystemExit, msg=line):
                s.anchors_to_targets(line)

    def test_an_indented_fence_is_still_a_fence(self):
        text = '  ```\n<a id="kept"></a>\n  ```'
        self.assertEqual(s.anchors_to_targets(text), text)

    def test_a_link_to_a_page_this_run_writes_is_a_link_inside_the_site(self):
        page = "verify/not-written-yet"
        self.assertFalse((s.DOCS / "docs" / f"{page}.md").exists())
        text = f"[x](https://docs.fpgas.online/en/latest/{page}.html#y)"
        self.assertEqual(s.own_links(text), text)  # not a page of this site: left alone
        with unittest.mock.patch.dict(s.TEST_DESIGNS.PAGES, {"docs/elsewhere.md": f"docs/{page}.md"}):
            self.assertEqual(s.own_links(text), f"[x](/{page}.md#y)")

    def test_an_id_anchor_line_becomes_a_myst_target_outside_fenced_code(self):
        text = '<a id="common-failures"></a>\n- x\n```\n<a id="kept"></a>\n```'
        self.assertEqual(s.anchors_to_targets(text), '(common-failures)=\n- x\n```\n<a id="kept"></a>\n```')

    def test_a_landing_page_gets_a_hidden_toctree_of_pages_that_are_pulled(self):
        for dest, entries in s.TEST_DESIGNS.TOCTREES.items():
            self.assertIn(dest, s.TEST_DESIGNS.PAGES.values())
            text = s.toctree(dest)
            self.assertTrue(text.startswith("\n```{toctree}\n:hidden:\n\n"), dest)
            here = dest.rsplit("/", 1)[0]
            for title, doc in entries:
                self.assertIn(f"{title} <{doc}>\n", text)
                self.assertIn(f"{here}/{doc}.md", s.TEST_DESIGNS.PAGES.values())
        self.assertEqual(s.toctree("docs/verify/identity.md"), "")

    def test_every_destination_is_in_a_directory_the_tool_owns(self):
        for repo in s.REPOS.values():
            for dest in [*repo.PAGES.values(), *(d for d, _ in repo.SECTIONS.values()),
                         *(w.dest for w in repo.WRAPPERS if w.own_dir)]:
                self.assertIn(dest.rsplit("/", 1)[0], repo.owned_dirs())


INFRA = f"https://github.com/{s.ORG}/fpgas.online-infra"


def repos_with(**infra):
    """REPOS with the infra entry given these tables (for a test)."""
    return unittest.mock.patch.dict(s.REPOS, {"infra": s.Repo("infra", **infra)})


class Ownership(unittest.TestCase):
    def tables(self, *repos):
        return {r.name: r for r in repos}

    def test_two_repositories_claiming_one_directory_is_an_error(self):
        a = s.Repo("a", PAGES={"x.md": "docs/shared/x.md"})
        b = s.Repo("b", PAGES={"y.md": "docs/shared/y.md"})
        with self.assertRaisesRegex(SystemExit, "directory docs/shared is claimed by a and by b"):
            s.check_tables(self.tables(a, b))

    def test_two_rows_writing_one_destination_is_an_error(self):
        a = s.Repo("a", PAGES={"x.md": "docs/a/x.md"})
        b = s.Repo("b", WRAPPERS=[s.Wrapper("docs/a/x.md", "X", own_dir=False)])
        with self.assertRaisesRegex(SystemExit, "docs/a/x.md is written by a and by b"):
            s.check_tables(self.tables(a, b))

    def test_a_destination_in_a_directory_another_repository_owns_is_an_error(self):
        a = s.Repo("a", PAGES={"x.md": "docs/a/x.md"})
        b = s.Repo("b", WRAPPERS=[s.Wrapper("docs/a/w.md", "W", own_dir=False)])
        with self.assertRaisesRegex(SystemExit, "which a owns"):
            s.check_tables(self.tables(a, b))

    def test_a_wrapper_includes_only_what_is_written_or_named_as_the_docs_own(self):
        a = s.Repo("a", WRAPPERS=[s.Wrapper("docs/a/w.md", "W", includes=(s.Include("docs/a/gone.md"),))])
        with self.assertRaisesRegex(SystemExit, "which no row writes"):
            s.check_tables(self.tables(a))
        b = s.Repo("b", PAGES={"x.md": "docs/b/x.md"},
                   WRAPPERS=[s.Wrapper("docs/b/w.md", "W", includes=(s.Include("docs/b/x.md", docs_owned=True),))])
        with self.assertRaisesRegex(SystemExit, "as the docs' own, but this tool writes it"):
            s.check_tables(self.tables(b))

    def test_the_tables_as_they_are_agree(self):
        s.check_tables()
        self.assertEqual(list(s.REPOS), ["test-designs", "infra", "site", "tt", "setup-pi", "poe", "cam", "mechanical"])
        for name, repo in s.REPOS.items():
            self.assertEqual(repo.full, f"fpgas-online/fpgas.online-{name}")
            if name != "test-designs":
                self.assertTrue(repo.empty(), name)


class LinksAcrossRepositories(unittest.TestCase):
    def test_a_github_url_to_a_file_another_repository_publishes_here_is_a_link_inside_the_site(self):
        with repos_with(PAGES={"docs/deploy.md": "docs/infra/deploy.md"}):
            out = s.rewrite_links(f"[d]({INFRA}/blob/main/docs/deploy.md#step-2) [n]({INFRA}/blob/main/docs/other.md)",
                                  "docs/verify.md", "docs/verify/fpgas-verify.md", "main")
            self.assertEqual(out, f"[d](../infra/deploy.md#step-2) [n]({INFRA}/blob/main/docs/other.md)")
            # in a copied file, written from the source root
            self.assertEqual(s.own_links(f"[d]({INFRA}/blob/some-branch/docs/deploy.md#x)"), "[d](/infra/deploy.md#x)")

    def test_a_relative_link_in_another_repository_goes_to_its_page_here_or_to_its_own_github(self):
        with repos_with(PAGES={"docs/a.md": "docs/infra/a.md", "docs/b.md": "docs/infra/b.md"}):
            out = s.rewrite_links("[b](b.md#x) [c](../roles/x/tasks.yml) [t](../README.md)", "docs/a.md",
                                  "docs/infra/a.md", "main", repo="infra")
            self.assertEqual(out, f"[b](b.md#x) [c]({INFRA}/blob/main/roles/x/tasks.yml) [t]({INFRA}/blob/main/README.md)")

    def test_a_link_from_another_repository_to_a_test_designs_page_goes_to_it(self):
        with repos_with(PAGES={"docs/a.md": "docs/infra/a.md"}):
            out = s.rewrite_links(f"[v]({GH}/blob/main/docs/verify.md#installing)", "docs/a.md", "docs/infra/a.md",
                                  "main", repo="infra")
            self.assertEqual(out, "[v](../verify/fpgas-verify.md#installing)")

    def test_a_github_url_to_a_section_s_other_heading_stays_on_github(self):
        url = f"{GH}/blob/main/docs/hardware/acorn.md#clock"
        self.assertEqual(s.rewrite_links(f"[a]({url})", "docs/verify.md", "docs/verify/fpgas-verify.md", "main"),
                         f"[a]({url})")

    def test_a_repository_not_in_the_tables_is_left_alone(self):
        url = "https://github.com/fpgas-online/fpgas.online-unknown/blob/main/docs/verify.md"
        self.assertEqual(s.rewrite_links(f"[a]({url})", "docs/verify.md", "docs/verify/fpgas-verify.md", "main"),
                         f"[a]({url})")


class Labels(unittest.TestCase):
    TITLES = {("test-designs", "docs/verify-goals.md"): "fpgas-verify: what it must do",
              ("test-designs", "docs/plans/design.md"): "The design",
              ("infra", "docs/deploy.md"): "Deploying"}

    def titles(self, name, path):
        return self.TITLES.get((name, path))

    def page(self, text, notes=None):
        return s.rewrite_links(text, "docs/verify.md", "docs/verify/fpgas-verify.md", "main",
                               titles=self.titles, notes=notes)

    def test_a_file_name_as_link_text_becomes_the_title_of_the_page(self):
        self.assertEqual(self.page("[verify-goals.md](verify-goals.md#x)"), "[fpgas-verify: what it must do](goals.md#x)")
        self.assertEqual(self.page("[`plans/design.md`](plans/design.md)"),
                         f"[The design]({GH}/blob/main/docs/plans/design.md)")
        self.assertEqual(self.page(f"[docs/deploy.md]({INFRA}/blob/main/docs/deploy.md)"),
                         f"[Deploying]({INFRA}/blob/main/docs/deploy.md)")

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
        for text in ("[Goals](verify-goals.md)", "```\n[verify-goals.md](verify-goals.md)\n```"):
            out = self.page(text)
            self.assertNotIn("what it must do", out, text)
        self.assertEqual(s.rewrite_links("[verify-goals.md](verify-goals.md)", "docs/verify.md",
                                         "docs/verify/fpgas-verify.md", "main"), "[verify-goals.md](goals.md)")

    def test_a_copied_file_s_labels_too(self):
        notes = []
        self.assertEqual(s.own_links(f"[verify-goals.md]({GH}/blob/main/docs/verify-goals.md)", self.titles, "f", notes),
                         "[fpgas-verify: what it must do](/verify/goals.md)")
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

    def test_the_acorn_building_guide_is_generated(self):
        dests = {w.dest for w in s.TEST_DESIGNS.WRAPPERS}
        for page in (s.DOCS / "docs/boards/acorn/building").rglob("*.md"):
            self.assertIn(str(page.relative_to(s.DOCS)), dests)
        self.assertIn("docs/boards/acorn/packages.md", dests)

    def test_interim_leads_are_listed_on_every_run(self):
        notes = []
        w = s.Wrapper("docs/w/a.md", "A", s.Interim("**Lead.**"), (s.Include("docs/w/g.md"),))
        repo = s.Repo("infra", FILES={"docs/w": ("gen", ["g.md"])}, WRAPPERS=[w])
        with repos_with(FILES=repo.FILES, WRAPPERS=repo.WRAPPERS), \
                unittest.mock.patch.object(s, "fetch", return_value=b"g\n"):
            wanted, missing = s.take(s.REPOS["infra"], "main", "c0ffee", lambda _: None, notes)
        self.assertEqual(missing, [])
        self.assertEqual(notes, ["docs/w/a.md: interim lead, not yet in infra: move it there and give the row a Lead"])
        self.assertEqual(wanted[s.DOCS / "docs/w/a.md"].decode(),
                         s.wrapper_marker(s.REPOS["infra"]) + "# A\n\n**Lead.**\n\n```{include} g.md\n```\n")

    def test_a_lead_is_its_section_of_the_home_repository_verbatim_with_its_links_rewritten(self):
        leads = ("# Leads\n\n## w/a.md\n\n**Lead** of [b](b.md) and\n[the site](https://docs.fpgas.online/en/latest/"
                 "index.html#x).\n\nSecond paragraph.\n\n## w/other.md\n\nno\n")
        w = s.Wrapper("docs/w/a.md", "A", s.Lead("docs/leads.md", "w/a.md"),
                      (s.Include("docs/sites/ps1-login.inc", docs_owned=True), s.Include("docs/w/b.md", True)),
                      s.Toctree(("b", ("Bee", "b")), heading="Pages", maxdepth=1, hidden=False))
        with repos_with(PAGES={"docs/b.md": "docs/w/b.md"}, WRAPPERS=[w]), \
                unittest.mock.patch.object(s, "fetch", side_effect=lambda f, c, p: leads.encode() if p == "docs/leads.md" else b"# B\n"):
            notes = []
            wanted, missing = s.take(s.REPOS["infra"], "main", "c0ffee", lambda _: None, notes)
        self.assertEqual((missing, notes), ([], []))
        self.assertEqual(wanted[s.DOCS / "docs/w/a.md"].decode().split("\n\n", 1)[1],
                         "# A\n\n**Lead** of [b](b.md) and\n[the site](../index.md#x).\n\nSecond paragraph.\n\n"
                         "```{include} ../sites/ps1-login.inc\n```\n\n```{include} b.md\n:relative-images:\n```\n\n"
                         "## Pages\n\n```{toctree}\n:maxdepth: 1\n\nb\nBee <b>\n```\n")

    def test_a_lead_section_that_is_not_there_is_missing(self):
        w = s.Wrapper("docs/w/a.md", "A", s.Lead("docs/leads.md", "w/gone.md"))
        with repos_with(WRAPPERS=[w]), unittest.mock.patch.object(s, "fetch", return_value=b"# Leads\n"):
            _, missing = s.take(s.REPOS["infra"], "main", "c0ffee", lambda _: None, [])
        self.assertEqual(missing, ['docs/leads.md: no "## w/gone.md" section'])


class CommandLine(unittest.TestCase):
    def test_ref_needs_exactly_one_repo(self):
        for argv in (["--ref", "x"], ["--ref", "x", "--repo", "infra", "--repo", "tt"]):
            with self.assertRaises(SystemExit) as e, unittest.mock.patch("sys.stderr"):
                s.main(argv)
            self.assertEqual(e.exception.code, 2)

    def test_an_empty_repository_makes_no_network_call(self):
        with unittest.mock.patch.object(s, "resolve") as resolve, unittest.mock.patch.object(s, "fetch") as fetch, \
                unittest.mock.patch("builtins.print"):
            self.assertEqual(s.main(["--repo", "infra", "--repo", "mechanical", "--check"]), 0)
        resolve.assert_not_called()
        fetch.assert_not_called()

    def test_a_missing_file_stops_with_2_naming_the_repository_and_the_file(self):
        def gone(full, commit, path):
            raise s.Missing(path)
        with repos_with(PAGES={"docs/deploy.md": "docs/infra-pages/deploy.md"}), \
                unittest.mock.patch.object(s, "resolve", return_value="c0ffee" * 6 + "c0ff"), \
                unittest.mock.patch.object(s, "fetch", side_effect=gone), \
                unittest.mock.patch("builtins.print") as printed:
            self.assertEqual(s.main(["--repo", "infra", "--check"]), 2)
        text = "\n".join(" ".join(map(str, c.args)) for c in printed.call_args_list)
        self.assertIn("fpgas-online/fpgas.online-infra", text)
        self.assertIn("docs/deploy.md", text)


class Alerts(unittest.TestCase):
    def test_each_kind_of_alert_becomes_its_admonition(self):
        for kind in ("NOTE", "TIP", "IMPORTANT", "WARNING", "CAUTION"):
            text = f"before\n\n> [!{kind}]\n> One [link](x.md) and `code`.\n>\n> Second paragraph.\n\nafter"
            self.assertEqual(s.alerts_to_admonitions(text),
                             f"before\n\n:::{{{kind.lower()}}}\nOne [link](x.md) and `code`.\n\nSecond paragraph.\n"
                             f":::\n\nafter")

    def test_a_body_with_a_colon_fence_gets_a_longer_one(self):
        text = "> [!TIP]\n> :::{note}\n> inner\n> :::"
        self.assertEqual(s.alerts_to_admonitions(text), "::::{tip}\n:::{note}\ninner\n:::\n::::")

    def test_an_alert_in_a_list_item_keeps_its_indentation(self):
        text = "1. Step one.\n\n   > [!WARNING]\n   > Unplug it first.\n   > Really.\n\n2. Step two."
        self.assertEqual(s.alerts_to_admonitions(text),
                         "1. Step one.\n\n   :::{warning}\n   Unplug it first.\n   Really.\n   :::\n\n2. Step two.")

    def test_plain_blockquotes_other_markers_and_code_are_left_alone(self):
        for text in ("> just a quote\n> more", "> [!NOTE] with text\n> body", "> [!note]\n> body",
                     "> [!DANGER]\n> body", "```\n> [!NOTE]\n> in code\n```", "~~~\n> [!NOTE]\n~~~"):
            self.assertEqual(s.alerts_to_admonitions(text), text)

    def test_a_line_continuing_the_quote_without_its_marker_stops_the_sync(self):
        with self.assertRaisesRegex(SystemExit, "has no '> '"):
            s.alerts_to_admonitions("> [!NOTE]\n> body\nlazy continuation")
        self.assertEqual(s.alerts_to_admonitions("> [!NOTE]\n> body"), ":::{note}\nbody\n:::")


if __name__ == "__main__":
    unittest.main()
