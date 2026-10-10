"""A target "(name)=" defined on two pages: a link to "page.md#name" then goes wherever the build read last.

Sphinx keeps one page for each target name. With -j auto, as on Read the Docs, which page that is depends on
how the pages were split between the workers, so such a link builds on one machine and fails on another."""
import collections
import re
import unittest
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"
TARGET = re.compile(r"^\(([^)\s]+)\)=\s*$", re.M)


def sources():
    return [p for p in sorted(DOCS.rglob("*")) if p.suffix in (".md", ".inc") and p.is_file()
            and not {"_build", "superpowers"} & set(p.relative_to(DOCS).parts)]


class Labels(unittest.TestCase):
    def test_no_link_names_a_target_that_two_pages_define(self):
        pages = collections.defaultdict(set)
        for p in sources():
            for name in TARGET.findall(p.read_text()):
                pages[name].add(p.relative_to(DOCS).as_posix())
        twice = {name: sorted(where) for name, where in pages.items() if len(where) > 1}
        text = "\n".join(p.read_text() for p in sources())
        for name, where in twice.items():
            self.assertIsNone(re.search(r"\.md#" + re.escape(name) + r"\)", text),
                              f"a link goes to #{name}, a target that {where} all define")


if __name__ == "__main__":
    unittest.main()
