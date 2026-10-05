#!/usr/bin/env python3
"""Fail when the link check found a broken link that is ours to keep working.

    sphinx-build -b linkcheck docs docs/_build/linkcheck
    python tools/check_links.py docs/_build/linkcheck/output.json

The link check itself may not fail the build: other people's sites go down, or
refuse a robot, for reasons that have nothing to do with a change here. A link
into one of our own repositories or sites is different: when it breaks, a file
was renamed or a page removed, and the documentation is wrong until it follows.
Those fail; the rest are listed as warnings.

Not ours to fail on, although on our sites: a board's live page
(`https://welland.fpgas.online/fpgas/pi-sw2-p34.html`), which answers 404
whenever that board is not up; and any link the check could not judge because
the server limited the rate of requests (429).
"""

import json
import re
import sys
from pathlib import Path

OURS = re.compile(r"^https?://(github\.com/(fpgas-online|mithro)(/|$)|([a-z0-9-]+\.)*fpgas\.online(/|$))")
LIVE_BOARD_PAGE = re.compile(r"^https?://[a-z0-9-]+\.fpgas\.online/(fpgas|board)/.")
RATE_LIMITED = re.compile(r"\b429\b")


def broken(lines):
    """The link check's broken links, from the lines of its output.json: (must be fixed, only warned about)."""
    ours, others = [], []
    for line in lines:
        if not line.strip():
            continue
        entry = json.loads(line)
        if entry["status"] != "broken":
            continue
        where = f"{entry['filename']}:{entry['lineno']}: {entry['uri']} ({entry['info']})"
        uri = entry["uri"]
        fails = OURS.match(uri) and not LIVE_BOARD_PAGE.match(uri) and not RATE_LIMITED.search(entry["info"])
        (ours if fails else others).append(where)
    return ours, others


def main(argv):
    if len(argv) != 2:
        raise SystemExit("usage: check_links.py docs/_build/linkcheck/output.json")
    ours, others = broken(Path(argv[1]).read_text(encoding="utf-8").splitlines())
    for where in others:
        print(f"warning: {where}")
    for where in ours:
        print(f"BROKEN, ours: {where}")
    print(f"{len(ours)} broken link(s) into our own repositories and sites; {len(others)} other(s), not failing")
    return 1 if ours else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
