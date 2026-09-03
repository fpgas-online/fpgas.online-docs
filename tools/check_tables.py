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
from collections import Counter
from pathlib import Path

LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
SEP = re.compile(r"^\|?[\s:|-]*-{2,}[\s:|-]*$")


def normalise(row: str) -> str:
    row = LINK.sub(r"\1", row)
    row = row.replace("`", "").replace("**", "").replace("&nbsp;", " ")
    row = re.sub(r"\s+", " ", row).strip().strip("|").strip()
    return row


def rows(path: Path) -> list[str]:
    out = []
    lines = path.read_text(encoding="utf-8").splitlines()
    in_fence = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
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
    if not sources or not dests:
        print("need at least one SOURCE and one DEST")
        return 2
    have = Counter()
    for d in dests:
        have.update(rows(d))
    checked = 0
    missing = 0
    for s in sources:
        for r in rows(s):
            checked += 1
            if have[r] > 0:
                have[r] -= 1
            else:
                missing += 1
                print(f"{s}: {r}")
    print(f"{checked} row(s) checked, {missing} missing")
    return 1 if missing else 0


def self_test() -> None:
    import tempfile

    content = (
        "| A | B |\n"
        "| --- | --- |\n"
        "| --no-project | Skip |\n"
        "| -q | Quiet |\n"
        "| Normal | Row |\n"
        "| -- | placeholder |\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(content)
        path = Path(f.name)
    try:
        got = rows(path)
        expected = [
            normalise("| --no-project | Skip |"),
            normalise("| -q | Quiet |"),
            normalise("| Normal | Row |"),
            normalise("| -- | placeholder |"),
        ]
        assert got == expected, f"{got!r} != {expected!r}"
    finally:
        path.unlink()

    fence_content = "```\n| x | y |\n```\n"
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(fence_content)
        fence_path = Path(f.name)
    try:
        assert rows(fence_path) == [], rows(fence_path)
    finally:
        fence_path.unlink()

    print("self-test ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        self_test()
        sys.exit(0)
    sys.exit(main(sys.argv[1:]))
