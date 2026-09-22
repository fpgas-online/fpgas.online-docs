#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Copy the files these docs take from fpgas.online-test-designs, so the docs build needs nothing else.

Usage: sync_test_designs.py [--ref REF] [--check]

Resolves REF (default main) to a commit, downloads every file in FILES at that commit, and makes each
destination directory an exact copy: changed files are rewritten, files no longer listed are removed,
and SOURCE records the commit they came from. --check writes nothing and exits 1 if anything would
change.

If test-designs no longer has a listed file, this stops with exit status 2 and names it. That means the
file moved or was renamed there: update FILES below to match, never paper over it. The scheduled
workflow (.github/workflows/sync-test-designs.yml) runs this and opens a pull request with the result.
"""

import argparse
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent
REPO = "fpgas-online/fpgas.online-test-designs"

# destination directory here: (source directory in test-designs, [file names])
FILES = {
    "docs/boards/acorn/generated": (
        "docs/wiring/acorn/generated",
        [
            "acorn-wiring-pi5.svg",
            "acorn-wiring-pi5.png",
            "acorn-wiring-computeblade.svg",
            "acorn-wiring-computeblade.png",
            "acorn-connectors.md",
            "acorn-pi5-p1.md",
            "acorn-pi5-p2.md",
            "acorn-blade-p1.md",
            "acorn-blade-p2.md",
            "acorn-blade-ext.md",
            "acorn-blade-uart.md",
        ],
    ),
}
SOURCE = "SOURCE"


class Missing(Exception):
    pass


def resolve(ref):
    out = subprocess.run(["git", "ls-remote", f"https://github.com/{REPO}.git", ref],
                         check=True, capture_output=True, text=True).stdout.split()
    if not out:
        raise SystemExit(f"sync: {REPO} has no ref {ref!r}")
    return out[0]


def fetch(commit, path):
    url = f"https://raw.githubusercontent.com/{REPO}/{commit}/{path}"
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise Missing(path) from e
        raise


def source_text(ref, commit):
    return (f"These files are copied from https://github.com/{REPO}\n"
            f"by tools/sync_test_designs.py. Do not edit them here: change them in test-designs.\n\n"
            f"ref: {ref}\ncommit: {commit}\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ref", default="main")
    ap.add_argument("--check", action="store_true", help="write nothing; exit 1 if anything would change")
    args = ap.parse_args(argv)

    commit = resolve(args.ref)
    print(f"{REPO} {args.ref} = {commit}")
    wanted, missing = {}, []
    for dest, (src, names) in FILES.items():
        for name in names:
            try:
                wanted[DOCS / dest / name] = fetch(commit, f"{src}/{name}")
            except Missing as e:
                missing.append(str(e))
    if missing:
        print(f"\nsync: FAILED. {REPO} at {commit[:12]} ({args.ref}) no longer has:", file=sys.stderr)
        for m in missing:
            print(f"  {m}", file=sys.stderr)
        print("It moved or was renamed there. Update FILES in tools/sync_test_designs.py to match.", file=sys.stderr)
        return 2

    changes = []
    for path, data in wanted.items():
        if not path.exists() or path.read_bytes() != data:
            changes.append(("update" if path.exists() else "add", path))
    for dest in FILES:
        d = DOCS / dest
        if d.exists():
            for p in d.iterdir():
                if p.name != SOURCE and p not in wanted:
                    changes.append(("remove", p))
    for what, path in changes:
        print(f"  {what:6} {path.relative_to(DOCS)}")
    if not changes:
        print("up to date")
        return 0
    if args.check:
        return 1
    for what, path in changes:
        if what == "remove":
            path.unlink()
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(wanted[path])
    for dest in FILES:  # SOURCE moves only with the files, so a new upstream commit alone changes nothing here
        (DOCS / dest / SOURCE).write_text(source_text(args.ref, commit))
    print(f"{len(changes)} file(s) changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
