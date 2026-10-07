#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Copy the files these docs take from fpgas.online-test-designs, so the docs build needs nothing else.

Usage: sync_test_designs.py [--ref REF] [--check]

Resolves REF (default main) to a commit, downloads every listed file at that commit, and makes each
destination directory an exact copy: changed files are rewritten, files no longer listed are removed,
and SOURCE records the commit they came from. --check writes nothing and exits 1 if anything would
change.

Three kinds of thing are taken (the tables below):

FILES     copied byte for byte (the Acorn wiring sheets and pin tables).
PAGES     whole Markdown documents, published as pages here.
SECTIONS  one "## heading" section of a Markdown document, written as a fragment that a page here
          includes (each board's "Installing the ... Packages").

PAGES and SECTIONS are written to be read on GitHub, so their relative links are rewritten (rewrite_links):
a link to something that is also published here goes to it, and any other goes to the file on GitHub. Each
starts with a comment saying where to edit it.

If test-designs does not have a listed file or section, this stops with exit status 2 and names it. That
means it moved or was renamed there: update the tables below to match, never paper over it. Only what is
listed is copied; a new file in test-designs is not picked up until it is added here. The scheduled
workflow (.github/workflows/sync-test-designs.yml) runs this and opens a pull request with the result.
"""

import argparse
import posixpath
import re
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
            "acorn-pi5-bom.md",
            "acorn-blade-bom.md",
            "acorn-cables-blade.md",
            "acorn-cables-pi5.md",
            "acorn-card-underside.svg",
            "acorn-card-underside.png",
            "acorn-cable-cut.png",
            "acorn-cable-p1-flag.png",
            "acorn-cable-p1-ground-check.png",
            "acorn-cable-p2-flag.png",
            "acorn-cable-p2-ground-check.png",
            "acorn-cable-crimp.png",
            "acorn-cable-push.png",
            "acorn-cable-check.png",
            "acorn-cable-check-blade-p2.png",
            "acorn-cable-blade-p1-prepare.png",
            "acorn-cable-blade-p1.png",
            "acorn-cable-blade-p2-prepare.png",
            "acorn-cable-blade-p2-resistor.png",
            "acorn-cable-blade-p2.png",
            "acorn-cable-pi5-p1-prepare.png",
            "acorn-cable-pi5-p1.png",
            "acorn-cable-pi5-p2-prepare.png",
            "acorn-cable-pi5-p2.png",
            "acorn-fit-blade.md",
            "acorn-fit-pi5.md",
            "acorn-cable-blade-fit.png",
            "acorn-cable-pi5-fit.png",
            "acorn-cable-blade-shell-check.png",
            "acorn-cable-pi5-shell-check.png",
            "acorn-build-blade-bench.md",
            "acorn-build-blade-fit.md",
            "acorn-build-blade-jtag-1.md",
            "acorn-build-blade-jtag-2.md",
            "acorn-build-blade-overview.md",
            "acorn-build-blade-uart-1.md",
            "acorn-build-blade-uart-2.md",
            "acorn-build-pi5-bench.md",
            "acorn-build-pi5-fit.md",
            "acorn-build-pi5-jtag-1.md",
            "acorn-build-pi5-jtag-2.md",
            "acorn-build-pi5-overview.md",
            "acorn-build-pi5-uart-1.md",
            "acorn-build-pi5-uart-2.md",
            "acorn-check-blade-1.md",
            "acorn-check-blade-2.md",
            "acorn-check-blade-2b.md",
            "acorn-check-blade-3.md",
            "acorn-check-blade-wires.png",
            "acorn-check-pi5-1.md",
            "acorn-check-pi5-2.md",
            "acorn-check-pi5-2b.md",
            "acorn-check-pi5-wires.png",
        ],
    ),
}
SOURCE = "SOURCE"
# Where this site is published: a link to it from a pulled page is turned into a link inside the site.
PUBLISHED = "https://docs.fpgas.online/en/latest/"

# source document in test-designs: the page it becomes here (relative to the repository root)
PAGES = {
    "docs/verify.md": "docs/verify/fpgas-verify.md",
    "docs/identity.md": "docs/verify/identity.md",
    "docs/verify-goals.md": "docs/verify/goals.md",
}

# (source document, its "## " heading): the fragment written here, and the page here that includes it
SECTIONS = {
    ("docs/hardware/acorn.md", "Installing the Acorn Packages"):
        ("docs/boards/generated/install-acorn.md", "docs/boards/acorn/packages.md"),
    ("docs/hardware/arty-a7.md", "Installing the Arty Packages"):
        ("docs/boards/generated/install-arty-a7.md", "docs/boards/arty-a7.md"),
    ("docs/hardware/netv2.md", "Installing the NeTV2 Packages"):
        ("docs/boards/generated/install-netv2.md", "docs/boards/netv2.md"),
    ("docs/hardware/fomu-evt.md", "Installing the Fomu Packages"):
        ("docs/boards/generated/install-fomu-evt.md", "docs/boards/fomu-evt.md"),
    ("docs/hardware/tt-fpga.md", "Installing the TT FPGA Packages"):
        ("docs/boards/generated/install-tt-fpga.md", "docs/boards/tt-fpga.md"),
}

# Source documents that are not taken whole but have a page here on the same subject. A link to one of
# them with no #fragment goes to that page; with a fragment it goes there only if the fragment is a
# section taken above (the page's other headings are not the source's).
ALSO_HERE = {
    "docs/hardware/acorn-pcie-programming.md": "docs/boards/acorn/pcie-programming.md",
    "docs/hardware/acorn-pinmap.md": "docs/boards/acorn/wiring.md",
}

# Directories this tool owns outright: everything in them is listed above, or is removed.
OWNED = sorted({*FILES, *(posixpath.dirname(d) for d in PAGES.values()),
                *(posixpath.dirname(d) for d, _ in SECTIONS.values())})

LINK = re.compile(r"(?<=\]\()([^)\s]+)(?=\))")
FENCE = re.compile(r"^(```|~~~)")
# Link forms LINK does not match. None is in the documents taken today; one appearing stops the sync, because
# a relative link left as written would be wrong on this site.
UNSUPPORTED = {
    "a reference-style link definition": re.compile(r"^\s{0,3}\[[^\]]+\]:\s+\S"),
    "an image": re.compile(r"!\[[^\]]*\]\("),
    "an angle-bracket link target": re.compile(r"\]\(<"),
    "a link with a title": re.compile(r"\]\([^)\s]+\s+[\"'(]"),
    "a raw HTML link or image": re.compile(r"<(a|img)\s", re.I),
}


def slug(heading):
    """The anchor GitHub and MyST both give a heading (lower case, punctuation dropped, spaces to hyphens)."""
    text = re.sub(r"[`*_]", "", heading.strip().lower())
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def link_targets():
    """source path -> (destination path, fragments that exist there or None for 'the source's own')."""
    targets = {src: (dest, None) for src, dest in PAGES.items()}
    for (src, heading), (_, page) in SECTIONS.items():
        targets.setdefault(src, (page, set()))[1].add(slug(heading))
    for src, dest in ALSO_HERE.items():
        targets.setdefault(src, (dest, set()))
    return targets


OWN_LINK = re.compile(r"(?<=\]\()" + re.escape(PUBLISHED) + r"([^)\s#?]+)\.html(#[^)\s]*)?(?=\))")


def own_links(text):
    """A copied Markdown file's links to pages of this site, as links inside the site.

    Such a file is included by pages at any depth, so the link is written from the source root
    (`/verify/fpgas-verify.md#heading`), which MyST resolves wherever the including page is. The build then
    checks the page and the heading; by its published address the link check would test it against what is
    published, where a heading's address is not the one MyST knows it by and a new page is not there yet.
    A link to a page that is not in this repository is left as it is. Fenced code is left alone."""

    def one(match):
        page, fragment = match.group(1), match.group(2) or ""
        return f"/{page}.md{fragment}" if (DOCS / "docs" / f"{page}.md").exists() else match.group(0)

    out, fenced = [], False
    for line in text.split("\n"):
        if FENCE.match(line.lstrip()):
            fenced = not fenced
        out.append(line if fenced else OWN_LINK.sub(one, line))
    return "\n".join(out)


def rewrite_links(text, src, at, ref, own_fragments=None):
    """Rewrite the relative links of the Markdown document src so they work from the page `at` here.

    `at` is the page a reader sees the text on: the destination for a page, and for a section the page
    that includes it (Sphinx resolves the links of an included file from the including page; checked by
    building, 2026-10-05). own_fragments is given for a section: the anchors inside it; a "#fragment"
    link to any other heading of the source goes to the source on GitHub. Fenced code is left alone."""
    targets = link_targets()

    def github(path, fragment):
        kind = "tree" if path.endswith("/") or "." not in posixpath.basename(path) else "blob"
        return f"https://github.com/{REPO}/{kind}/{ref}/{path.rstrip('/')}" + (f"#{fragment}" if fragment else "")

    def one(match):
        target = match.group(1)
        if target.startswith(PUBLISHED):
            # A link to a page of this site, written in test-designs by its published address: here it is a link
            # inside the site, which the build checks. (By its address it would be checked against what is
            # published, and a page added in the same change is not published yet.)
            page, _, fragment = target[len(PUBLISHED) :].partition("#")
            here = "docs/" + page.removesuffix(".html") + ".md"
            if page.endswith(".html") and (DOCS / here).exists():
                return posixpath.relpath(here, posixpath.dirname(at)) + (f"#{fragment}" if fragment else "")
            return target
        if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target):
            return target
        path, _, fragment = target.partition("#")
        if not path:
            if own_fragments is None or fragment in own_fragments:
                return target
            return github(src, fragment)
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(src), path))
        if resolved.startswith(".."):
            raise SystemExit(f"sync: {src} links outside the repository: {target}")
        if path.endswith("/"):
            resolved += "/"
        if resolved in targets:
            dest, fragments = targets[resolved]
            if not fragment or fragments is None or fragment in fragments:
                rel = posixpath.relpath(dest, posixpath.dirname(at))
                return rel + (f"#{fragment}" if fragment else "")
        return github(resolved, fragment)

    out, fenced = [], False
    for number, line in enumerate(text.split("\n"), 1):
        if FENCE.match(line.lstrip()):
            fenced = not fenced
        if not fenced:
            for what, pattern in UNSUPPORTED.items():
                if pattern.search(line):
                    raise SystemExit(f"sync: {src}:{number}: {what}, which rewrite_links does not handle. "
                                     f"Teach it to, or write the link inline in test-designs.")
        out.append(line if fenced else LINK.sub(one, line))
    return "\n".join(out)


def section(text, heading, src):
    """The "## heading" section of text, up to the next "## " or "# " heading outside fenced code."""
    lines, start, fenced = text.split("\n"), None, False
    for i, line in enumerate(lines):
        if FENCE.match(line.lstrip()):
            fenced = not fenced
        if fenced:
            continue
        if start is None:
            if line.strip() == f"## {heading}":
                start = i
        elif re.match(r"#{1,2} ", line):
            return "\n".join(lines[start:i]).rstrip() + "\n"
    if start is None:
        raise Missing(f'{src}: no "## {heading}" section')
    return "\n".join(lines[start:]).rstrip() + "\n"


def fragments_in(text):
    """The anchors of the headings in text, outside fenced code."""
    found, fenced = set(), False
    for line in text.split("\n"):
        if FENCE.match(line.lstrip()):
            fenced = not fenced
        m = None if fenced else re.match(r"#{1,6} (.+)", line)
        if m:
            found.add(slug(m.group(1)))
    return found


def marker(src, what):
    return (f"% {what} is copied from https://github.com/{REPO}/blob/main/{src}\n"
            f"% by tools/sync_test_designs.py. Do not edit it here: change it in test-designs.\n\n")


class Missing(Exception):
    pass


def resolve(ref):
    """The commit a branch of test-designs points at; exactly that branch, not any ref ending in its name."""
    full = f"refs/heads/{ref}"
    lines = subprocess.run(["git", "ls-remote", f"https://github.com/{REPO}.git", full],
                           check=True, capture_output=True, text=True).stdout.splitlines()
    matches = [line.split()[0] for line in lines if line.split()[1] == full]
    if len(matches) != 1:
        raise SystemExit(f"sync: {REPO} has no branch {ref!r}")
    return matches[0]


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
                data = fetch(commit, f"{src}/{name}")
                wanted[DOCS / dest / name] = own_links(data.decode("utf-8")).encode("utf-8") if name.endswith(".md") else data
            except Missing as e:
                missing.append(str(e))
    texts = {}
    for src in sorted({*PAGES, *(s for s, _ in SECTIONS)}):
        try:
            texts[src] = fetch(commit, src).decode("utf-8")
        except Missing as e:
            missing.append(str(e))
    for src, dest in PAGES.items():
        if src in texts:
            body = rewrite_links(texts[src], src, dest, args.ref)
            wanted[DOCS / dest] = (marker(src, "This page") + body).encode("utf-8")
    for (src, heading), (dest, page) in SECTIONS.items():
        if src in texts:
            try:
                part = section(texts[src], heading, src)
            except Missing as e:
                missing.append(str(e))
                continue
            body = rewrite_links(part, src, page, args.ref, own_fragments=fragments_in(part))
            wanted[DOCS / dest] = (marker(src, f'This section ("{heading}")') + body).encode("utf-8")
    if missing:
        print(f"\nsync: FAILED. {REPO} at {commit[:12]} ({args.ref}) does not have:", file=sys.stderr)
        for m in missing:
            print(f"  {m}", file=sys.stderr)
        print("It was moved, renamed or removed there (or never added). Update the tables in "
              "tools/sync_test_designs.py to match what test-designs has.", file=sys.stderr)
        return 2

    changes = []
    for path, data in wanted.items():
        if not path.exists() or path.read_bytes() != data:
            changes.append(("update" if path.exists() else "add", path))
    for dest in OWNED:
        d = DOCS / dest
        if d.exists():
            for p in d.iterdir():
                if p.name != SOURCE and p not in wanted:
                    changes.append(("remove", p))
    # A new upstream commit alone is not a change (see below), but a different ref is: the files are
    # then vouched for by another branch, and SOURCE has to say so.
    for dest in OWNED:
        src = DOCS / dest / SOURCE
        if src.exists() and f"\nref: {args.ref}\n" not in src.read_text():
            changes.append(("source", src))
    for what, path in changes:
        print(f"  {what:6} {path.relative_to(DOCS)}")
    if not changes:
        print("up to date")
        return 0
    if args.check:
        return 1
    for what, path in changes:
        if what == "remove":
            if not path.is_file():
                raise SystemExit(f"sync: {path.relative_to(DOCS)} is not a file. The directories in OWNED hold "
                                 f"only what this tool writes; move it out.")
            path.unlink()
        elif what == "source":
            pass  # rewritten below
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(wanted[path])
    for dest in OWNED:  # SOURCE moves only with the files or the ref, so a new upstream commit alone changes nothing
        (DOCS / dest / SOURCE).write_text(source_text(args.ref, commit))
    print(f"{len(changes)} file(s) changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
