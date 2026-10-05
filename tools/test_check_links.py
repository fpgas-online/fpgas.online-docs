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
            ours, others = c.broken([line(uri)])
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
        # the list of boards itself is not a board's page
        self.assertEqual(len(c.broken([line("https://welland.fpgas.online/fpgas/")])[0]), 1)

    def test_a_rate_limited_request_proves_nothing(self):
        info = "429 Client Error: Too Many Requests for url: https://github.com/fpgas-online/x"
        self.assertEqual(c.broken([line("https://github.com/fpgas-online/x", info=info)])[0], [])

    def test_working_redirected_and_ignored_links_are_not_reported(self):
        lines = [line("https://github.com/fpgas-online/x", status=s) for s in ("working", "redirected", "ignored", "unchecked")]
        self.assertEqual(c.broken([*lines, "", "  "]), ([], []))

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


if __name__ == "__main__":
    unittest.main()
