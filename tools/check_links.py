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

Every page on our sites counts, a board's page too. A page named for a port or
a host (`https://welland.fpgas.online/fpgas/pi-sw2-p34.html`) is there only
while a board there passes its check this boot, so it comes and goes as boards
are moved and checked; a link to one is wrong as soon as the board moves, as
fpgas.online-docs issue #105 found. The documentation links the page of the
board or its Pi instead, which stays whether the board is up or not
(`https://welland.fpgas.online/fleet/<the Pi's serial>/`,
`https://tinytapeout.fpgas.online/board/<slug>/`), and a link to a page that
comes and goes fails here whenever its page is gone.

Not ours to fail on, although on our sites: a link the check could not judge
because the server limited the rate of requests (429).
"""

import json
import re
import sys
from pathlib import Path

OURS = re.compile(r"^https?://(github\.com/(fpgas-online|mithro)(/|$)|([a-z0-9-]+\.)*fpgas\.online([:/?#]|$))", re.I)
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
        fails = OURS.match(uri) and not RATE_LIMITED.search(entry["info"])
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
