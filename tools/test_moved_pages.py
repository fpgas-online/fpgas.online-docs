"""tools/moved_pages.json: the pages that moved, old document name to new, for the sync's link rewriting."""
import json
import unittest
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"
MOVED = json.loads((Path(__file__).resolve().parent / "moved_pages.json").read_text())


class MovedPages(unittest.TestCase):
    def test_an_old_page_is_gone_and_its_new_page_is_here(self):
        for old, new in MOVED.items():
            page, _, fragment = old.partition("#")
            if not fragment:
                self.assertFalse((DOCS / f"{page}.md").exists(), f"{page} still exists, so it has not moved")
            self.assertTrue((DOCS / f"{new.partition('#')[0]}.md").exists(), f"{old} goes to {new}, which is not a page")

    def test_no_entry_goes_to_a_page_that_itself_moved(self):
        for old, new in MOVED.items():
            self.assertNotIn(new.partition("#")[0], MOVED, f"{old} goes to {new}, which has moved again")

    def test_a_section_s_entry_belongs_to_a_page_that_moved(self):
        for old in MOVED:
            page, _, fragment = old.partition("#")
            if fragment:
                self.assertIn(page, MOVED, f"{old}: a section of a page that has no entry of its own")


if __name__ == "__main__":
    unittest.main()
