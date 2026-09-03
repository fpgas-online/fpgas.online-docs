#!/usr/bin/env python3
"""Report Markdown table rows present in SOURCE files but absent from DEST files.

Usage: check_tables.py SOURCE.md [SOURCE.md ...] -- DEST.md [DEST.md ...]

Rows are compared after normalisation: links reduced to their text, backticks
and bold markers removed, whitespace collapsed, trailing pipes stripped.
Separator rows (|---|) and header rows are ignored. Exit status is 1 when any
row is missing so the check can gate a commit.
"""
import re
import sys
from pathlib import Path

LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
SEP = re.compile(r"^\|?\s*:?-{2,}")


def normalise(row: str) -> str:
    row = LINK.sub(r"\1", row)
    row = row.replace("`", "").replace("**", "").replace("&nbsp;", " ")
    row = re.sub(r"\s+", " ", row).strip().strip("|").strip()
    return row


def rows(path: Path) -> list[str]:
    out = []
    lines = path.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        if not line.lstrip().startswith("|") or SEP.match(line.lstrip()):
            continue
        # A header row is followed by a separator row.
        if i + 1 < len(lines) and SEP.match(lines[i + 1].lstrip()):
            continue
        out.append(normalise(line))
    return out


def main(argv: list[str]) -> int:
    if "--" not in argv:
        print(__doc__)
        return 2
    split = argv.index("--")
    sources = [Path(p) for p in argv[:split]]
    dests = [Path(p) for p in argv[split + 1:]]
    have = set()
    for d in dests:
        have.update(rows(d))
    missing = 0
    for s in sources:
        for r in rows(s):
            if r not in have:
                missing += 1
                print(f"{s}: {r}")
    print(f"{missing} row(s) missing")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
