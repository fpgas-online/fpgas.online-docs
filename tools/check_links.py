#!/usr/bin/env python3
"""Fail when the link check found a broken link that is ours to keep working.

    sphinx-build -b linkcheck docs docs/_build/linkcheck
    python tools/check_links.py docs/_build/linkcheck/output.json

The link check itself may not fail the build: other people's sites go down, or
refuse a robot, for reasons that have nothing to do with a change here. A link
into one of our own repositories or sites is different: when it breaks, a file
was renamed or a page removed, and the documentation is wrong until it follows.
Those fail; the rest are listed as warnings.

A link of ours that timed out fails too: the check could not show that it
works. So does a link check that judged nothing (an empty output.json is what
a check that died leaves behind).

Not ours to fail on, although on our sites: a board's live page
(`https://welland.fpgas.online/fpgas/pi-sw2-p34.html`), which answers 404
whenever that board is not up; and any link the check could not judge because
the server limited the rate of requests (429).
"""

import json
import re
import sys
from pathlib import Path

OURS = re.compile(r"^https?://(github\.com/(fpgas-online|mithro)(/|$)|([a-z0-9-]+\.)*fpgas\.online([:/?#]|$))", re.I)
# https://welland.fpgas.online/fpgas/pi-sw2-p34.html, https://tinytapeout.fpgas.online/board/fpga-2/
LIVE_BOARD_PAGE = re.compile(r"^https?://[a-z0-9-]+\.fpgas\.online/(fpgas/pi[a-z0-9-]*\.html|board/[a-z0-9-]+/?)$", re.I)
RATE_LIMITED = re.compile(r"^429\b")  # the info starts with the status: "429 Client Error: ..."


def broken(lines):
    """The link check's broken links, from the lines of its output.json: (must be fixed, only warned about).

    A timeout counts as broken for a link of ours. Stops the run if the lines hold no entry at all.
    """
    ours, others, entries = [], [], 0
    for line in lines:
        if not line.strip():
            continue
        entry = json.loads(line)
        entries += 1
        if entry["status"] not in ("broken", "timeout"):
            continue
        where = f"{entry['filename']}:{entry['lineno']}: {entry['uri']} ({entry['info']})"
        uri = entry["uri"]
        fails = OURS.match(uri) and not LIVE_BOARD_PAGE.match(uri) and not RATE_LIMITED.search(entry["info"])
        if entry["status"] == "timeout" and not fails:
            continue  # somebody else's slow site: not even a warning
        (ours if fails else others).append(where)
    if not entries:
        raise SystemExit("check_links: the link check judged no link at all: it did not run to its end")
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
