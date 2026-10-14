import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import check_links as c  # noqa: E402


def line(uri, status="broken", info="404 Client Error: Not Found"):
    return json.dumps({"filename": "setup/pi.md", "lineno": 7, "status": status, "code": 0, "uri": uri, "info": info})


class Broken(unittest.TestCase):
    def test_a_broken_link_into_our_repositories_or_sites_must_be_fixed(self):
        for uri in (
            "https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/cam/pi/tasks/main.yml",
            "https://github.com/mithro/apt-repo-action",
            "https://docs.fpgas.online/en/latest/nowhere.html",
            "https://apt.fpgas.online/trixie/",
            "https://fpgas.online/fpgas.online-fpga-tools/",
        ):
            ours, others, _ = c.broken([line(uri)])
            self.assertEqual((len(ours), others), (1, []), uri)
            self.assertIn("setup/pi.md:7: " + uri, ours[0])

    def test_other_peoples_links_only_warn(self):
        for uri in (
            "https://digilent.com/reference/pmod/start",
            "https://github.com/enjoy-digital/litex",
            "https://notfpgas.online/x",
            "https://example.org/github.com/fpgas-online/x",
        ):
            self.assertEqual(c.broken([line(uri)])[0], [], uri)
            self.assertEqual(len(c.broken([line(uri)])[1]), 1, uri)

    def test_a_board_that_is_down_does_not_fail_the_documentation(self):
        for uri in (
            "https://welland.fpgas.online/fpgas/pi-sw2-p34.html",
            "https://ps1.fpgas.online/fpgas/pi3.html",
            "https://tinytapeout.fpgas.online/board/fpga-2/",
        ):
            self.assertEqual(c.broken([line(uri)])[0], [], uri)
        # the list of boards, and a file beside the board pages, are not a board's page
        for uri in (
            "https://welland.fpgas.online/fpgas/",
            "https://welland.fpgas.online/fpgas/static/site.css",
            "https://tinytapeout.fpgas.online/board/fpga-2/other/page.html",
        ):
            self.assertEqual(len(c.broken([line(uri)])[0]), 1, uri)

    def test_a_rate_limited_request_proves_nothing(self):
        info = "429 Client Error: Too Many Requests for url: https://github.com/fpgas-online/x"
        self.assertEqual(c.broken([line("https://github.com/fpgas-online/x", info=info)])[0], [])
        # a 404 on an address that happens to hold the digits is not a rate limit
        info = "404 Client Error: Not Found for url: https://github.com/fpgas-online/x/issues/429"
        self.assertEqual(len(c.broken([line("https://github.com/fpgas-online/x/issues/429", info=info)])[0]), 1)

    def test_a_timeout_of_ours_fails_and_somebody_elses_is_not_reported(self):
        ours, others, _ = c.broken([line("https://docs.fpgas.online/en/latest/", status="timeout", info="timed out")])
        self.assertEqual((len(ours), others), (1, []))
        self.assertEqual(c.broken([line("https://digilent.com/x", status="timeout", info="timed out")]), ([], [], []))

    def test_a_check_that_judged_nothing_stops_the_run(self):
        for lines in ([], ["", "  "]):
            with self.assertRaises(SystemExit):
                c.broken(lines)

    def test_ours_is_told_by_the_host_whatever_its_case_port_or_query(self):
        for uri in (
            "https://GitHub.com/Mithro/apt-repo-action",
            "https://welland.fpgas.online:8443/x",
            "https://fpgas.online?x=1",
        ):
            self.assertEqual(len(c.broken([line(uri)])[0]), 1, uri)
        for uri in (
            "https://fpgas.online.example.com/x",
            "https://github.com/fpgas-online-x/y",
            "https://github.com/mithrox/y",
        ):
            self.assertEqual(c.broken([line(uri)])[0], [], uri)

    def test_working_redirected_and_ignored_links_are_not_reported(self):
        lines = [line("https://github.com/fpgas-online/x", status=s) for s in ("working", "redirected", "ignored", "unchecked")]
        self.assertEqual(c.broken([*lines, "", "  "]), ([], [], []))

    def test_main_exits_1_only_when_one_of_ours_is_broken(self):
        import contextlib
        import io
        import tempfile

        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as d, contextlib.redirect_stdout(io.StringIO()):
            path = Path(d) / "output.json"
            path.write_text(line("https://digilent.com/x") + "\n")
            self.assertEqual(c.main(["check_links.py", str(path)]), 0)
            path.write_text(line("https://digilent.com/x") + "\n" + line("https://github.com/fpgas-online/x") + "\n")
            self.assertEqual(c.main(["check_links.py", str(path)]), 1)


class Answers:
    """A recorded run of GitHub API answers: get(path) returns the next one; the paths and waits are kept."""

    def __init__(self, *answers):
        self.answers, self.paths, self.waits = list(answers), [], []

    def get(self, path):
        self.paths.append(path)
        return self.answers.pop(0)

    def sleep(self, seconds):
        self.waits.append(seconds)


class AskGitHub(unittest.TestCase):
    def test_each_form_of_link_maps_to_its_api_path(self):
        for uri, path in (
            ("https://github.com/fpgas-online", "users/fpgas-online"),
            ("https://github.com/mithro/", "users/mithro"),
            ("https://github.com/fpgas-online/fpgas.online-setup-pi", "repos/fpgas-online/fpgas.online-setup-pi"),
            ("https://github.com/fpgas-online/fpgas.online-fpga-tools#debian-packages-bookworm-trixie-sid-arm64-armhf",
             "repos/fpgas-online/fpgas.online-fpga-tools"),
            ("https://github.com/fpgas-online/fpgas.online-tt/issues/19", "repos/fpgas-online/fpgas.online-tt/issues/19"),
            ("https://github.com/fpgas-online/fpgas.online-docs/pull/216", "repos/fpgas-online/fpgas.online-docs/pulls/216"),
            ("https://github.com/fpgas-online/fpgas.online-cam/blob/main/README.md",
             "repos/fpgas-online/fpgas.online-cam/contents/README.md?ref=main"),
            ("https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/site/tasks/pistat.yml#L3",
             "repos/fpgas-online/fpgas.online-infra/contents/ansible/roles/site/tasks/pistat.yml?ref=main"),
            ("https://github.com/fpgas-online/fpgas.online-infra/tree/main/ansible/roles/ssh_key_fetch",
             "repos/fpgas-online/fpgas.online-infra/contents/ansible/roles/ssh_key_fetch?ref=main"),
            ("https://github.com/fpgas-online/tinytapeout-fpga-demos/tree/da7d10db1ff62b0a346381530c7c59505ea6b2ad/demos/tt_um_uart_hello",
             "repos/fpgas-online/tinytapeout-fpga-demos/contents/demos/tt_um_uart_hello?ref=da7d10db1ff62b0a346381530c7c59505ea6b2ad"),
            ("https://github.com/fpgas-online/fpgas.online-docs/tree/main", "repos/fpgas-online/fpgas.online-docs/contents/?ref=main"),
            ("https://github.com/fpgas-online/fpgas.online-tt/commit/1cf6b40", "repos/fpgas-online/fpgas.online-tt/commits/1cf6b40"),
        ):
            self.assertEqual(c.api_path(uri), path, uri)

    def test_a_form_the_api_cannot_be_asked_about_is_a_fault(self):
        for uri in (
            "https://github.com/fpgas-online/fpgas.online-docs/actions/runs/1",
            "https://github.com/fpgas-online/fpgas.online-docs/issues",
            "https://github.com/fpgas-online/x/issues/not-a-number",
            "https://example.org/fpgas-online/x",
        ):
            with self.assertRaises(ValueError, msg=uri):
                c.api_path(uri)

    def test_a_200_works_and_a_404_or_410_is_broken(self):
        uri = "https://github.com/fpgas-online/fpgas.online-tt/issues/19"
        self.assertEqual(c.verdict(uri, Answers("200").get), "ok")
        for status in ("404", "410"):
            self.assertIn(f"broken (GitHub API {status}", c.verdict(uri, Answers(status).get))

    def test_no_answer_is_asked_again_after_growing_waits(self):
        uri = "https://github.com/fpgas-online/fpgas.online-setup-pi"
        a = Answers("500", "429", "no answer (timed out)", "200")
        self.assertEqual(c.verdict(uri, a.get, a.sleep), "ok")
        self.assertEqual(a.waits, list(c.WAITS))
        self.assertEqual(a.paths, ["repos/fpgas-online/fpgas.online-setup-pi"] * 4)
        self.assertEqual(sorted(c.WAITS), list(c.WAITS))

    def test_no_answer_after_every_retry_is_broken(self):
        a = Answers("502", "500", "503", "500")
        result = c.verdict("https://github.com/fpgas-online/x", a.get, a.sleep)
        self.assertTrue(result.startswith("broken (GitHub API gave no answer"), result)
        self.assertIn("502, 500, 503, 500", result)

    def test_any_other_answer_stops_the_run_and_never_counts_as_working(self):
        for status in ("401", "403", "301", "422"):
            with self.assertRaises(SystemExit) as e:
                c.verdict("https://github.com/fpgas-online/x", Answers(status).get, Answers().sleep)
            self.assertIn(f"answered {status}", str(e.exception))

    def test_only_our_github_links_the_check_could_not_judge_are_asked(self):
        asked = "https://github.com/fpgas-online/fpgas.online-infra/issues/240"
        lines = [
            line(asked, info="500 Server Error: Internal Server Error for url: " + asked),
            line("https://github.com/mithro/x", info="429 Client Error: Too Many Requests"),
            line("https://github.com/fpgas-online/gone", info="404 Client Error: Not Found"),
            line("https://github.com/enjoy-digital/litex", info="500 Server Error: Internal Server Error"),
            line("https://docs.fpgas.online/x", info="502 Server Error: Bad Gateway"),
            line("https://github.com/fpgas-online/slow", status="timeout", info="timed out"),
        ]
        ours, others, ask = c.broken(lines)
        self.assertEqual([uri for _, uri in ask], [asked, "https://github.com/mithro/x"])
        self.assertEqual(len(ours), 3)  # the 404, our own site's 502 and our timeout still fail as before
        self.assertEqual(len(others), 1)

    def test_main_fails_only_on_what_the_api_says_is_broken(self):
        import contextlib
        import io
        import tempfile

        def run(*answers):
            a = Answers(*answers)
            out = io.StringIO()
            with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as d, contextlib.redirect_stdout(out):
                path = Path(d) / "output.json"
                path.write_text(line("https://github.com/fpgas-online/x", info="500 Server Error: Internal Server Error") + "\n")
                return c.main(["check_links.py", str(path)], get=a.get, sleep=a.sleep), out.getvalue()

        self.assertEqual(run("500", "200")[0], 0)
        rc, out = run("404")
        self.assertEqual(rc, 1)
        self.assertIn("BROKEN, ours: setup/pi.md:7: https://github.com/fpgas-online/x", out)

    def test_main_without_a_token_stops_when_there_is_something_to_ask(self):
        import contextlib
        import io
        import os
        import tempfile
        from unittest import mock

        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as d, contextlib.redirect_stdout(io.StringIO()), \
                mock.patch.dict(os.environ, {}, clear=True):
            path = Path(d) / "output.json"
            path.write_text(line("https://github.com/fpgas-online/x", info="500 Server Error") + "\n")
            with self.assertRaises(SystemExit):
                c.main(["check_links.py", str(path)])
            path.write_text(line("https://digilent.com/x") + "\n")
            self.assertEqual(c.main(["check_links.py", str(path)]), 0)  # nothing to ask: no token needed


if __name__ == "__main__":
    unittest.main()
