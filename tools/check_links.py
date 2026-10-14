#!/usr/bin/env python3
"""Fail when the link check found a broken link that is ours to keep working.

    sphinx-build -b linkcheck docs docs/_build/linkcheck
    GITHUB_TOKEN=... python tools/check_links.py docs/_build/linkcheck/output.json

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

github.com answers the Actions runner's page requests with 500s and 429s that
say nothing about the link (docs #216 lost 22 links of ours to 500s in one
run). So a link into github.com/fpgas-online or github.com/mithro that the
check marked broken with a 5xx or a 429 is asked again through GitHub's REST
API, with GITHUB_TOKEN. It fails only when the API says 404 or 410, or gives no
answer after spaced retries. Any other answer, or a link the API cannot be
asked about, stops the run as a fault in this tool: it never counts as working.
"""

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

OURS = re.compile(r"^https?://(github\.com/(fpgas-online|mithro)(/|$)|([a-z0-9-]+\.)*fpgas\.online([:/?#]|$))", re.I)
# https://welland.fpgas.online/fpgas/pi-sw2-p34.html, https://tinytapeout.fpgas.online/board/fpga-2/
LIVE_BOARD_PAGE = re.compile(r"^https?://[a-z0-9-]+\.fpgas\.online/(fpgas/pi[a-z0-9-]*\.html|board/[a-z0-9-]+/?)$", re.I)
RATE_LIMITED = re.compile(r"^429\b")  # the info starts with the status: "429 Client Error: ..."
NOT_JUDGED = re.compile(r"^(429|5\d\d)\b")  # "500 Server Error: ...": the server did not say whether the link works
OUR_GITHUB = re.compile(r"^https?://github\.com/(fpgas-online|mithro)(/|$)", re.I)

API = "https://api.github.com/"
WAITS = (10, 30, 90)  # seconds before each retry of a GitHub API request that got no answer
NO_ANSWER = re.compile(r"^(429|5\d\d)$")


def api_path(uri):
    """The REST API path that tells whether a github.com link of ours works.

    Raises ValueError for a link of a form the API cannot be asked about.
    """
    m = re.match(r"^https?://github\.com/([^?#]*)", uri, re.I)
    if not m:
        raise ValueError(f"not a github.com link: {uri}")
    parts = [p for p in m.group(1).split("/") if p]
    if len(parts) == 1:
        return f"users/{parts[0]}"  # an organisation or a user
    repo = f"repos/{parts[0]}/{parts[1]}"
    rest = parts[2:]
    if not rest:
        return repo
    if len(rest) == 2 and rest[0] == "issues" and rest[1].isdigit():
        return f"{repo}/issues/{rest[1]}"
    if len(rest) == 2 and rest[0] == "pull" and rest[1].isdigit():
        return f"{repo}/pulls/{rest[1]}"
    if len(rest) == 2 and rest[0] == "commit" and re.fullmatch(r"[0-9a-f]{7,40}", rest[1]):
        return f"{repo}/commits/{rest[1]}"
    if len(rest) >= 2 and rest[0] in ("blob", "tree"):
        # The ref is taken as one path segment: main, or a commit. A branch with a / in its name is not told apart.
        return f"{repo}/contents/{'/'.join(rest[2:])}?ref={rest[1]}"
    raise ValueError(f"no GitHub API check for this form of link: {uri}")


def fetch(path, token):
    """GET path from the GitHub API: its HTTP status, or "no answer" for a network failure."""
    request = urllib.request.Request(API + path, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return str(response.status)
    except urllib.error.HTTPError as e:
        return str(e.code)
    except (urllib.error.URLError, TimeoutError) as e:
        return f"no answer ({e})"


def verdict(uri, get, sleep=time.sleep):
    """Whether a github.com link of ours works, asked through the API: "ok" or "broken (...)".

    get(path) returns the HTTP status as a string, or "no answer (...)". A 5xx, a 429 or no answer is
    asked again after each of WAITS. Raises SystemExit on any other status: a fault in this tool.
    """
    path = api_path(uri)
    answers = []
    for wait in (0, *WAITS):
        if wait:
            sleep(wait)
        status = get(path)
        answers.append(status)
        if status == "200":
            return "ok"
        if status in ("404", "410"):
            return f"broken (GitHub API {status} for {path})"
        if not (NO_ANSWER.match(status) or status.startswith("no answer")):
            raise SystemExit(f"check_links: GitHub API answered {status} for {path} ({uri}): neither working nor broken")
    return f"broken (GitHub API gave no answer for {path}: {', '.join(answers)})"


def broken(lines):
    """The link check's broken links, from the lines of its output.json: (must be fixed, only warned about, to ask GitHub).

    A timeout counts as broken for a link of ours. A link of ours on github.com that the check could not judge
    (a 5xx or a 429) goes to the third list as (where, uri). Stops the run if the lines hold no entry at all.
    """
    ours, others, ask, entries = [], [], [], 0
    for line in lines:
        if not line.strip():
            continue
        entry = json.loads(line)
        entries += 1
        if entry["status"] not in ("broken", "timeout"):
            continue
        where = f"{entry['filename']}:{entry['lineno']}: {entry['uri']} ({entry['info']})"
        uri = entry["uri"]
        if entry["status"] == "broken" and OUR_GITHUB.match(uri) and NOT_JUDGED.search(entry["info"]):
            ask.append((where, uri))
            continue
        fails = OURS.match(uri) and not LIVE_BOARD_PAGE.match(uri) and not RATE_LIMITED.search(entry["info"])
        if entry["status"] == "timeout" and not fails:
            continue  # somebody else's slow site: not even a warning
        (ours if fails else others).append(where)
    if not entries:
        raise SystemExit("check_links: the link check judged no link at all: it did not run to its end")
    return ours, others, ask


def main(argv, get=None, sleep=time.sleep):
    if len(argv) != 2:
        raise SystemExit("usage: check_links.py docs/_build/linkcheck/output.json")
    ours, others, ask = broken(Path(argv[1]).read_text(encoding="utf-8").splitlines())
    if ask and get is None:
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            raise SystemExit(f"check_links: {len(ask)} GitHub link(s) of ours to ask the API about, and no GITHUB_TOKEN")
        get = lambda path: fetch(path, token)  # noqa: E731
    for where, uri in ask:
        result = verdict(uri, get, sleep)
        print(f"asked GitHub: {uri}: {result}")
        if result != "ok":
            ours.append(f"{where}; {result}")
    for where in others:
        print(f"warning: {where}")
    for where in ours:
        print(f"BROKEN, ours: {where}")
    print(f"{len(ours)} broken link(s) into our own repositories and sites; {len(others)} other(s), not failing;"
          f" {len(ask)} asked of the GitHub API")
    return 1 if ours else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
