#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Copy the mechanical drawings these docs show from fpgas.online-mechanical, at one pinned commit.

Usage: sync_mechanical.py [--commit SHA] [--check]

The drawings are rendered by fpgas.online-mechanical's own build, light and dark, and copied here unchanged
into docs/_static/mechanical/; SOURCE there records the commit. --commit pins a new commit and copies from it;
without it the commit in SOURCE is used. --check writes nothing and exits 1 if a file differs from that commit's.
"""

import argparse
import pathlib
import re
import sys
import urllib.error
import urllib.request

REPO = "fpgas-online/fpgas.online-mechanical"
DEST = pathlib.Path(__file__).resolve().parent.parent / "docs/_static/mechanical"
SOURCE = DEST / "SOURCE"
# (directory in fpgas.online-mechanical, {stem: extensions}); each stem comes as -light and -dark.
DRAWINGS = [
    ("raspberry_pi_camera/output/docs", {"over-acorn-cle-215-plus-views": ("svg", "png"),
                                        "over-acorn-cle-215-plus-sheet": ("svg", "png")}),
    ("tinytapeout/mounting_plate/output/docs", {"tt-generic-mounting-plate-views": ("svg", "png"),
                                               "tt-generic-mounting-plate-sheet": ("png",),
                                               "tt-generic-mounting-plate-fitting-guide-views-a": ("svg", "png"),
                                               "tt-generic-mounting-plate-fitting-guide-views-b": ("svg", "png"),
                                               "tt-generic-mounting-plate-fitting-guide-sheet": ("png",)}),
]
# Whole drawings copied as they are (vector, for zooming), where a sheet has no SVG picture.
DOCUMENTS = ["tinytapeout/mounting_plate/output/tt-generic-mounting-plate.pdf",
             "tinytapeout/mounting_plate/output/tt-generic-mounting-plate-fitting-guide.pdf"]
COMMIT = re.compile(r"^commit: ([0-9a-f]{40})$", re.M)


def files():
    """[(path in fpgas.online-mechanical, file name here)] for every drawing."""
    out = [(f"{src}/{stem}-{theme}.{ext}", f"{stem}-{theme}.{ext}")
           for src, stems in DRAWINGS for stem, exts in stems.items() for theme in ("light", "dark") for ext in exts]
    return out + [(path, path.rsplit("/", 1)[1]) for path in DOCUMENTS]


def pinned():
    """The commit SOURCE names; stops if there is none."""
    match = COMMIT.search(SOURCE.read_text()) if SOURCE.exists() else None
    if match is None:
        sys.exit(f"{SOURCE} names no commit: run with --commit SHA")
    return match.group(1)


def fetch(commit, path):
    url = f"https://raw.githubusercontent.com/{REPO}/{commit}/{path}"
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"{url}: {e}")


def source_text(commit):
    return (f"These files are copied from https://github.com/{REPO}\n"
            "by tools/sync_mechanical.py. Do not edit them here: change them there.\n\n"
            f"commit: {commit}\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--commit", help="pin this full commit SHA and copy from it")
    ap.add_argument("--check", action="store_true", help="write nothing; exit 1 if anything differs")
    args = ap.parse_args(argv)
    if args.commit and not re.fullmatch(r"[0-9a-f]{40}", args.commit):
        sys.exit("--commit takes a full 40-character SHA")
    commit = args.commit or pinned()
    wanted = {DEST / name: fetch(commit, path) for path, name in files()}
    wanted[SOURCE] = source_text(commit).encode()
    stale = [p for p, data in wanted.items() if not p.exists() or p.read_bytes() != data]
    extra = [p for p in DEST.glob("*") if p not in wanted] if DEST.exists() else []
    if args.check:
        for p in stale + extra:
            print(f"differs from {REPO}@{commit[:12]}: {p.name}")
        print("up to date" if not stale + extra else f"{len(stale + extra)} file(s) differ")
        return 1 if stale + extra else 0
    DEST.mkdir(parents=True, exist_ok=True)
    for p in stale:
        p.write_bytes(wanted[p])
    for p in extra:
        p.unlink()
        print(f"removed {p.name}")
    print(f"{len(stale)} file(s) written from {REPO}@{commit[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
