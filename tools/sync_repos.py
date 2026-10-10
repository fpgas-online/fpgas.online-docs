#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Copy the pages and files these docs take from the other fpgas.online repositories, so the docs build
needs nothing else.

Usage: sync_repos.py [--repo NAME ...] [--ref REF] [--check]

Docs content lives in the repository it is about; these docs import it and keep only what has no other
home. REPOS below has one entry per repository (fpgas-online/fpgas.online-<name>). For each one taken
(every one, or those named with --repo), this resolves REF (default main; --ref only with exactly one
--repo) to a commit, downloads every listed file at that commit, and makes each destination directory an
exact copy: changed files are rewritten, files no longer listed are removed, and SOURCE records the
repository, ref and commit they came from. An entry with nothing listed makes no network call. --check
writes nothing and exits 1 if anything would change.

Each entry has these tables:

FILES      files copied per destination directory: pictures byte for byte, Markdown with its links
           handled as below (the Acorn wiring sheets and pin tables).
PAGES      whole Markdown documents, published as pages here. A value is the destination, or
           Page(destination, own_dir=False) for a page among pages these docs (or another repository) keep
           in that directory: it claims only its own path.
SECTIONS   one "## heading" section of a Markdown document, written as a fragment that a page here
           includes (each board's "Installing the ... Packages").
ALSO_HERE  documents not taken whole that have a page here on the same subject (a link to one goes there).
TOCTREES   the hidden toctree appended to a pulled landing page.
WRAPPERS   pages here that are only a title, a lead and includes of synced files. A wrapper may exist only
           as a row here: this tool writes it, and nothing in it is written by hand in these docs. Its lead
           is a "## " section of a file in the home repository, taken verbatim (Lead), or, until that file
           exists there, the text itself (Interim, listed on every run so it does not stay).

Ownership: a destination directory belongs to exactly one repository (the directories of its FILES,
PAGES, SECTIONS and WRAPPERS; a page or wrapper with own_dir=False claims only its own path), and no
owned directory lies inside another. Everything in an owned directory is written by this tool or removed. Two
repositories claiming one directory, two rows one destination path, or a path claimed in a directory
another repository owns, is an error. A path claimed alone is written and nothing beside it is touched;
the files of these docs next to it stay theirs. A file anywhere in
docs/ that carries this tool's "copied"/"generated" comment, or a SOURCE of it, that no row accounts for
stops the sync for its repository: remove it by hand, or give it its row back.

Text that is synced (PAGES, SECTIONS, leads, and the Markdown among FILES) was written to be read on
GitHub, so its links are rewritten (rewrite_links). A link is resolved in its own repository: relative to
the file, or from the repository root when it starts with "/". Then:
- a link to a file that this tool publishes here, from ANY repository, becomes a link inside the site: a
  relative link to a file in the same repository, or an absolute
  https://github.com/fpgas-online/fpgas.online-<repo>/blob/<ref>/<path> URL to another;
- a link to this site's published address (https://docs.fpgas.online/en/latest/...html) becomes a link
  inside the site when that page is here;
- any other relative link becomes the file's GitHub URL in its own repository.
Fragments are kept. In a copied FILES Markdown file (included by pages at any depth) a link inside the site
is written from the source root (/verify/fpgas-verify.md); its pictures must be files copied beside it. A
link form that cannot be rewritten stops the sync. A link whose text is a file name or path ending in .md
gets as its text the title (the first "# " heading) of the page the rewritten link opens; when that cannot
be read, the text is left and the output says so. A GitHub alert (a blockquote opening `> [!NOTE]`, TIP,
IMPORTANT, WARNING or CAUTION, in any letter case) becomes the MyST admonition of its kind
(alerts_to_admonitions); any other `> [!...]` stops the sync. Fenced code is left alone. Each synced page
starts with a comment saying where to edit it.

If a repository does not have a listed file or section, or its text cannot be synced, that repository
stops: each such stop prints "sync: FAILED. fpgas-online/fpgas.online-<name>: <reason>". It means a file
moved or was renamed there: update the tables below to match, never paper over it. A failing repository
blocks no other: the others are written, and the run exits 2 naming each failing one. Only what is listed
is copied; a new file there is not picked up until it is added here. The scheduled workflow
(.github/workflows/sync-repos.yml) runs this daily for every repository, opens a pull request with what
synced and an issue for what failed.

fpgas.online-mechanical: its PAGES go here; its drawings are copied by tools/sync_mechanical.py, which
pins one commit for them.
"""
import argparse
import collections
import json
import posixpath
import re
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent
ORG = "fpgas-online"
SOURCE = "SOURCE"
# Where this site is published: a link to it from a pulled page is turned into a link inside the site.
PUBLISHED = "https://docs.fpgas.online/en/latest/"
WRAPPER_REVIEW = "2026-11-10"  # the review date in a wrapper page's front matter
# tools/moved_pages.json: {old page or "old page#fragment": new page, with its "#fragment" if it has one}, as
# document names. A repository that still writes a link by a page's old published address gets the page that
# took its place. The site itself serves no redirect from an old address: an entry goes once no repository
# writes the old address any more.
MOVED = json.loads((DOCS / "tools" / "moved_pages.json").read_text())


@dataclass(frozen=True)
class Lead:
    """A wrapper's lead: the "## heading" section of `path` in the home repository, without its heading line."""
    path: str
    heading: str


@dataclass(frozen=True)
class Interim:
    """A wrapper's lead written in its row, until the home repository has it (then the row takes a Lead)."""
    text: str


@dataclass(frozen=True)
class Include:
    """A file a wrapper includes: a destination this tool writes, or (docs_owned) a file of these docs."""
    path: str
    relative_images: bool = False
    docs_owned: bool = False


@dataclass(frozen=True)
class Toctree:
    """A toctree at the end of a wrapper; entries are document names, or (title, document)."""
    entries: tuple
    heading: str = None  # a "## " heading written before it
    maxdepth: int = None
    hidden: bool = True


@dataclass(frozen=True)
class Page:
    """A PAGES destination given with its ownership (a plain string is Page(dest), owning its directory)."""
    dest: str
    own_dir: bool = True  # False: the page sits among pages of these docs and claims only its own path


@dataclass(frozen=True)
class Wrapper:
    dest: str
    title: str
    lead: object = None  # Lead, Interim or None
    includes: tuple = ()
    toctree: Toctree = None
    own_dir: bool = True  # False: the page sits among pages of these docs and claims only its own path
    kind: str = None  # the page's type, for its front matter: tutorial, how-to, reference, explanation, landing
    reader: str = None  # who the page is for, for its front matter


@dataclass
class Repo:
    name: str
    FILES: dict = field(default_factory=dict)      # destination directory: (source directory, [file names])
    PAGES: dict = field(default_factory=dict)      # source document: the page it becomes here (or a Page)
    # (source document, "## " heading): (fragment here, page including it)
    SECTIONS: dict = field(default_factory=dict)
    ALSO_HERE: dict = field(default_factory=dict)  # source document: the page here on the same subject
    TOCTREES: dict = field(default_factory=dict)   # page here: [(navigation title, document relative to it)]
    WRAPPERS: list = field(default_factory=list)   # [Wrapper]

    @property
    def full(self):
        return f"{ORG}/fpgas.online-{self.name}"

    def empty(self):
        return not (self.FILES or self.PAGES or self.SECTIONS or self.WRAPPERS)

    def pages(self):
        """{source document: Page} of PAGES."""
        return {src: v if isinstance(v, Page) else Page(v) for src, v in self.PAGES.items()}

    def dests(self):
        """Every path this repository's rows write here."""
        out = [f"{d}/{n}" for d, (_, names) in self.FILES.items() for n in names]
        out += [*(p.dest for p in self.pages().values()), *(d for d, _ in self.SECTIONS.values()),
                *(w.dest for w in self.WRAPPERS)]
        return out

    def owned_dirs(self):
        return sorted({*self.FILES, *(posixpath.dirname(p.dest) for p in self.pages().values() if p.own_dir),
                       *(posixpath.dirname(d) for d, _ in self.SECTIONS.values()),
                       *(posixpath.dirname(w.dest) for w in self.WRAPPERS if w.own_dir)})

    def lead_sources(self):
        return {w.lead.path for w in self.WRAPPERS if isinstance(w.lead, Lead)}


# The pages under a cables page, listed on it: the landing page above holds only the cables page itself.
_CABLE_PAGES = Toctree(("parts", "jtag-wires", "jtag-housing", "uart-wires", "uart-housing", "bench-check"),
                       heading="The pages that build the cables", maxdepth=1, hidden=False)

_PS1_LOGIN = Include("docs/sites/ps1-login.inc", docs_owned=True)

TEST_DESIGNS = Repo(
    "test-designs",
    FILES={
        "docs/boards/acorn/generated": (
            "docs/wiring/acorn/generated",
            [
                "acorn-wiring-pi5.svg",
                "acorn-wiring-pi5-dark.svg",
                "acorn-wiring-pi5.png",
                "acorn-wiring-pi5-dark.png",
                "acorn-wiring-computeblade.svg",
                "acorn-wiring-computeblade-dark.svg",
                "acorn-wiring-computeblade.png",
                "acorn-wiring-computeblade-dark.png",
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
                "acorn-card-underside-dark.svg",
                "acorn-card-underside.png",
                "acorn-card-underside-dark.png",
                "acorn-cable-cut.png",
                "acorn-cable-cut-dark.png",
                "acorn-cable-p1-flag.png",
                "acorn-cable-p1-flag-dark.png",
                "acorn-cable-p1-ground-check.png",
                "acorn-cable-p1-ground-check-dark.png",
                "acorn-cable-p2-flag.png",
                "acorn-cable-p2-flag-dark.png",
                "acorn-cable-p2-ground-check.png",
                "acorn-cable-p2-ground-check-dark.png",
                "acorn-cable-crimp.png",
                "acorn-cable-crimp-dark.png",
                "acorn-cable-push.png",
                "acorn-cable-push-dark.png",
                "acorn-cable-check.png",
                "acorn-cable-check-dark.png",
                "acorn-cable-check-blade-p2.png",
                "acorn-cable-check-blade-p2-dark.png",
                "acorn-cable-blade-p1-prepare.png",
                "acorn-cable-blade-p1-prepare-dark.png",
                "acorn-cable-blade-p1.png",
                "acorn-cable-blade-p1-dark.png",
                "acorn-cable-blade-p2-prepare.png",
                "acorn-cable-blade-p2-prepare-dark.png",
                "acorn-cable-blade-p2-resistor.png",
                "acorn-cable-blade-p2-resistor-dark.png",
                "acorn-cable-blade-p2.png",
                "acorn-cable-blade-p2-dark.png",
                "acorn-cable-pi5-p1-prepare.png",
                "acorn-cable-pi5-p1-prepare-dark.png",
                "acorn-cable-pi5-p1.png",
                "acorn-cable-pi5-p1-dark.png",
                "acorn-cable-pi5-p2-prepare.png",
                "acorn-cable-pi5-p2-prepare-dark.png",
                "acorn-cable-pi5-p2.png",
                "acorn-cable-pi5-p2-dark.png",
                "acorn-fit-blade.md",
                "acorn-fit-pi5.md",
                "acorn-cable-blade-reach.png",
                "acorn-cable-blade-reach-dark.png",
                "acorn-cable-pi5-reach.png",
                "acorn-cable-pi5-reach-dark.png",
                "acorn-cable-blade-fit-1.png",
                "acorn-cable-blade-fit-1-dark.png",
                "acorn-cable-blade-fit-2.png",
                "acorn-cable-blade-fit-2-dark.png",
                "acorn-cable-pi5-fit-1.png",
                "acorn-cable-pi5-fit-1-dark.png",
                "acorn-cable-pi5-fit-2.png",
                "acorn-cable-pi5-fit-2-dark.png",
                "acorn-cable-blade-shell-check.png",
                "acorn-cable-blade-shell-check-dark.png",
                "acorn-cable-pi5-shell-check.png",
                "acorn-cable-pi5-shell-check-dark.png",
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
                "acorn-check-about.md",
                "acorn-check-blade-1.md",
                "acorn-check-blade-tests.md",
                "acorn-check-blade-2.md",
                "acorn-check-blade-2b.md",
                "acorn-check-blade-3.md",
                "acorn-check-blade-wires.png",
                "acorn-check-blade-wires-dark.png",
                "acorn-check-pi5-1.md",
                "acorn-check-pi5-tests.md",
                "acorn-check-pi5-2.md",
                "acorn-check-pi5-2b.md",
                "acorn-check-pi5-wires.png",
                "acorn-check-pi5-wires-dark.png",
            ],
        ),
    },
    PAGES={
        "docs/verify.md": "docs/verify/fpgas-verify.md",
        "docs/verify/installing.md": "docs/verify/installing.md",
        "docs/verify/running.md": "docs/verify/running.md",
        "docs/verify/identity-and-labels.md": "docs/verify/identity-and-labels.md",
        "docs/verify/reading-the-result.md": "docs/verify/reading-the-result.md",
        "docs/verify/more-results.md": "docs/verify/more-results.md",
        "docs/verify/help.md": "docs/verify/help.md",
        "docs/verify/tests.md": "docs/verify/tests.md",
        "docs/verify/tt-fpga.md": "docs/verify/tt-fpga.md",
        "docs/verify/acorn.md": "docs/verify/acorn.md",
        "docs/verify/acorn-power-cycle.md": "docs/verify/acorn-power-cycle.md",
        "docs/verify/idcode-and-dna.md": "docs/verify/idcode-and-dna.md",
        "docs/verify/not-done-yet.md": "docs/verify/not-done-yet.md",
        "docs/verify/acorn-wiring.md": "docs/verify/acorn-wiring.md",
        "docs/verify/common-failures.md": "docs/verify/common-failures.md",
        "docs/verify/report-and-state.md": "docs/verify/report-and-state.md",
        "docs/verify/fleet.md": "docs/verify/fleet.md",
        "docs/verify/current-results.md": "docs/verify/current-results.md",
        "docs/identity.md": "docs/verify/identity.md",
        "docs/verify-goals.md": "docs/verify/goals.md",
    },
    # On GitHub the landing page lists them itself; Sphinx needs them in a toctree to place them in the
    # sidebar under it.
    TOCTREES={
        "docs/verify/fpgas-verify.md": [
            ("Installing", "installing"),
            ("Running it", "running"),
            ("Identity and labels", "identity-and-labels"),
            ("Reading the result", "reading-the-result"),
            ("Reading the result: more", "more-results"),
            ("--help", "help"),
            ("What each check tests", "tests"),
            ("TT FPGA", "tt-fpga"),
            ("Acorn", "acorn"),
            ("Acorn: power-cycle check", "acorn-power-cycle"),
            ("JTAG IDCODE and DNA", "idcode-and-dna"),
            ("Not done yet", "not-done-yet"),
            ("Checking an Acorn's wiring", "acorn-wiring"),
            ("Common failures", "common-failures"),
            ("The report and state", "report-and-state"),
            ("In fpgas.online", "fleet"),
            ("Current results", "current-results"),
        ],
    },
    SECTIONS={
        ("docs/hardware/acorn.md", "Installing the Acorn Packages"):
            ("docs/boards/generated/install-acorn.md", "docs/boards/acorn/setup/packages.md"),
        ("docs/hardware/arty-a7.md", "Installing the Arty Packages"):
            ("docs/boards/generated/install-arty-a7.md", "docs/boards/arty-a7/setup/packages.md"),
        ("docs/hardware/netv2.md", "Installing the NeTV2 Packages"):
            ("docs/boards/generated/install-netv2.md", "docs/boards/netv2/setup/packages.md"),
        ("docs/hardware/fomu-evt.md", "Installing the Fomu Packages"):
            ("docs/boards/generated/install-fomu-evt.md", "docs/boards/fomu-evt/setup/packages.md"),
        ("docs/hardware/tt-fpga.md", "Installing the TT FPGA Packages"):
            ("docs/boards/generated/install-tt-fpga.md", "docs/boards/tt-fpga/setup/packages.md"),
    },
    # A link to one of them with no #fragment goes to that page; with a fragment it goes there only if the
    # fragment is a section taken above (the page's other headings are not the source's).
    ALSO_HERE={
        "docs/hardware/acorn-pcie-programming.md": "docs/boards/acorn/pcie-programming.md",
        "docs/hardware/acorn-pinmap.md": "docs/boards/acorn/wiring.md",
    },
    WRAPPERS=[
        # The Acorn building guide, and the Acorn's packages page around its install section.
        Wrapper(
            'docs/boards/acorn/setup/compute-blade/bench-check.md',
            'How to check the cables on the bench (Compute Blade)',
            Interim('**You have built both cables for an Acorn on a Compute Blade. Before anything is '
                    'powered, a check on the host with a meter that ground reaches the plugs and that the 3.3 '
                    'V wire reaches nothing.**'),
            (Include('docs/boards/acorn/generated/acorn-build-blade-bench.md', relative_images=True),),
            kind='how-to',
            reader='someone who has built both cables for an Acorn on a Compute Blade',
            own_dir=False,
        ),
        Wrapper(
            'docs/boards/acorn/setup/compute-blade/parts.md',
            'Parts and tools for the Compute Blade cables',
            Interim('**You are about to build the two cables for an Acorn on a Compute Blade: tick off every '
                    'line before you start.**'),
            (Include('docs/boards/acorn/generated/acorn-blade-bom.md'),),
            kind='reference',
            reader='someone gathering the parts and tools for the Compute Blade cables',
            own_dir=False,
        ),
        Wrapper(
            'docs/boards/acorn/setup/compute-blade/fitting.md',
            'How to fit the cables and the card (Compute Blade)',
            Interim('**Your two cables for an Acorn on a Compute Blade have passed the bench check, and you '
                    'are fitting them and the card.**'),
            (Include('docs/boards/acorn/generated/acorn-build-blade-fit.md', relative_images=True),),
            kind='how-to',
            reader='someone fitting the cables and the Acorn on a Compute Blade',
            own_dir=False,
        ),
        Wrapper(
            'docs/boards/acorn/setup/compute-blade/cables.md',
            'The two cables on a Compute Blade',
            Interim('**You have an Acorn and a Compute Blade, and want to build the two cables between them, '
                    'fit them and check them.** An Acorn on a Raspberry Pi 5 has [its own '
                    'guide](../rpi-5/cables.md); nothing there is for a Compute Blade.'),
            (Include('docs/boards/acorn/generated/acorn-build-blade-overview.md', relative_images=True),),
            toctree=_CABLE_PAGES,
            kind='explanation',
            reader='someone with an Acorn and a Compute Blade who is about to build the two cables',
            own_dir=False,
        ),
        Wrapper(
            'docs/boards/acorn/setup/compute-blade/jtag-wires.md',
            "How to prepare the JTAG cable's wires (Compute Blade)",
            Interim('**You have the parts for an Acorn on a Compute Blade and are making the first of its two '
                    "cables, from the Acorn's P1 socket (JTAG). On this page: cut the bought cable in half, "
                    'find wire 1, check it with a meter, cut back the wires that are not used, crimp the '
                    'rest.**'),
            (Include('docs/boards/acorn/generated/acorn-build-blade-jtag-1.md', relative_images=True),),
            kind='how-to',
            reader='someone making the JTAG cable for an Acorn on a Compute Blade',
            own_dir=False,
        ),
        Wrapper(
            'docs/boards/acorn/setup/compute-blade/jtag-housing.md',
            "How to fill the JTAG cable's housing (Compute Blade)",
            Interim('**You have the P1 cable for an Acorn on a Compute Blade with its wires flagged and '
                    'crimped, and are putting them into their housing. On this page: which wire goes in which '
                    'cavity, and a meter check of every wire.**'),
            (Include('docs/boards/acorn/generated/acorn-build-blade-jtag-2.md', relative_images=True),),
            kind='how-to',
            reader='someone making the JTAG cable for an Acorn on a Compute Blade',
            own_dir=False,
        ),
        Wrapper(
            'docs/boards/acorn/setup/compute-blade/uart-wires.md',
            "How to prepare the UART cable's wires (Compute Blade)",
            Interim('**You have the parts for an Acorn on a Compute Blade and are making the second of its '
                    "two cables, from the Acorn's P2 socket (the serial port). On this page: find wire 1, "
                    'check it with a meter, cut back the wires that are not used, solder the resistor into '
                    'the J2 wire, crimp the rest.**'),
            (Include('docs/boards/acorn/generated/acorn-build-blade-uart-1.md', relative_images=True),),
            kind='how-to',
            reader='someone making the UART cable for an Acorn on a Compute Blade',
            own_dir=False,
        ),
        Wrapper(
            'docs/boards/acorn/setup/compute-blade/uart-housing.md',
            "How to fill the UART cable's housing (Compute Blade)",
            Interim('**You have the P2 cable for an Acorn on a Compute Blade with its wires flagged and '
                    'crimped, and are putting them into their housing. On this page: which wire goes in which '
                    'cavity, and a meter check of every wire.**'),
            (Include('docs/boards/acorn/generated/acorn-build-blade-uart-2.md', relative_images=True),),
            kind='how-to',
            reader='someone making the UART cable for an Acorn on a Compute Blade',
            own_dir=False,
        ),
        Wrapper(
            'docs/boards/acorn/checks/compute-blade.md',
            'How to run the Acorn check on a Compute Blade',
            Interim('**You have an Acorn on a Compute Blade, its two cables built and fitted, and want to '
                    'know what the check on the blade says about the wiring. On a Compute Blade today it '
                    'cannot yet prove the cables: the paragraph "What to expect on a Compute Blade today" '
                    'below says why.**\n\nLog in to the blade first. At ps1:'),
            (_PS1_LOGIN, Include('docs/boards/acorn/generated/acorn-check-blade-1.md', relative_images=True)),
            toctree=Toctree(("compute-blade-jtag",)),
            kind='how-to',
            reader='someone with an Acorn fitted on a Compute Blade who wants to check its wiring',
            own_dir=False,
        ),
        Wrapper(
            'docs/boards/acorn/troubleshooting/compute-blade-failing-test.md',
            'A failing Acorn test on a Compute Blade',
            Interim('**The check of your Acorn on a Compute Blade printed a failing line, and you want to '
                    'know which wire it means.**'),
            (Include('docs/boards/acorn/generated/acorn-check-blade-2.md', relative_images=True),),
            kind='reference',
            reader='someone whose Acorn check on a Compute Blade printed a failing line',
            own_dir=False,
        ),
        Wrapper(
            'docs/boards/acorn/troubleshooting/compute-blade-other-messages.md',
            'Other Acorn check messages on a Compute Blade',
            Interim('**The check of your Acorn on a Compute Blade printed a line that is not about one of the '
                    "cables' wires (the card's image, its memory, the tool itself), and you want to know what "
                    'it means.**'),
            (Include('docs/boards/acorn/generated/acorn-check-blade-2b.md', relative_images=True),),
            kind='reference',
            reader='someone whose Acorn check on a Compute Blade printed a message that is not about a wire',
            own_dir=False,
        ),
        Wrapper(
            'docs/boards/acorn/checks/compute-blade-jtag.md',
            'How to make a Compute Blade boot ready for JTAG',
            Interim("**Your Compute Blade's check fails at `jtag` although the wiring is right, or you want "
                    'to know what to expect before you start: what has and has not been run on a blade, and '
                    'the pin JTAG shares with the serial port.**'),
            (Include('docs/boards/acorn/generated/acorn-check-blade-3.md', relative_images=True),),
            kind='how-to',
            reader='someone with an Acorn on a Compute Blade whose boot does not let JTAG run',
            own_dir=False,
        ),
        Wrapper(
            'docs/boards/acorn/setup/rpi-5/bench-check.md',
            'How to check the cables on the bench (Raspberry Pi 5)',
            Interim('**You have built both cables for an Acorn on a Raspberry Pi 5. Before anything is '
                    'powered, a check on the host with a meter that ground reaches the plugs and that the 3.3 '
                    'V wire reaches nothing.**'),
            (Include('docs/boards/acorn/generated/acorn-build-pi5-bench.md', relative_images=True),),
            kind='how-to',
            reader='someone who has built both cables for an Acorn on a Raspberry Pi 5',
            own_dir=False,
        ),
        Wrapper(
            'docs/boards/acorn/setup/rpi-5/parts.md',
            'Parts and tools for the Raspberry Pi 5 cables',
            Interim('**You are about to build the two cables for an Acorn on a Raspberry Pi 5: tick off every '
                    'line before you start.**'),
            (Include('docs/boards/acorn/generated/acorn-pi5-bom.md'),),
            kind='reference',
            reader='someone gathering the parts and tools for the Raspberry Pi 5 cables',
            own_dir=False,
        ),
        Wrapper(
            'docs/boards/acorn/setup/rpi-5/fitting.md',
            'How to fit the cables and the card (Raspberry Pi 5)',
            Interim('**Your two cables for an Acorn on a Raspberry Pi 5 have passed the bench check, and you '
                    'are fitting them and the card.**'),
            (Include('docs/boards/acorn/generated/acorn-build-pi5-fit.md', relative_images=True),),
            kind='how-to',
            reader='someone fitting the cables and the Acorn on a Raspberry Pi 5',
            own_dir=False,
        ),
        Wrapper(
            'docs/boards/acorn/setup/rpi-5/cables.md',
            'The two cables on a Raspberry Pi 5',
            Interim('**You have an Acorn and a Raspberry Pi 5, and want to build the two cables between them, '
                    'fit them and check them.** An Acorn on a Compute Blade has [its own '
                    'guide](../compute-blade/cables.md); nothing there is for a Raspberry Pi 5.'),
            (Include('docs/boards/acorn/generated/acorn-build-pi5-overview.md', relative_images=True),),
            toctree=_CABLE_PAGES,
            kind='explanation',
            reader='someone with an Acorn and a Raspberry Pi 5 who is about to build the two cables',
            own_dir=False,
        ),
        Wrapper(
            'docs/boards/acorn/setup/rpi-5/jtag-wires.md',
            "How to prepare the JTAG cable's wires (Raspberry Pi 5)",
            Interim('**You have the parts for an Acorn on a Raspberry Pi 5 and are making the first of its '
                    "two cables, from the Acorn's P1 socket (JTAG). On this page: cut the bought cable in "
                    'half, find wire 1, check it with a meter, cut back the wires that are not used, crimp '
                    'the rest.**'),
            (Include('docs/boards/acorn/generated/acorn-build-pi5-jtag-1.md', relative_images=True),),
            kind='how-to',
            reader='someone making the JTAG cable for an Acorn on a Raspberry Pi 5',
            own_dir=False,
        ),
        Wrapper(
            'docs/boards/acorn/setup/rpi-5/jtag-housing.md',
            "How to fill the JTAG cable's housing (Raspberry Pi 5)",
            Interim('**You have the P1 cable for an Acorn on a Raspberry Pi 5 with its wires flagged and '
                    'crimped, and are putting them into their housing. On this page: which wire goes in which '
                    'cavity, and a meter check of every wire.**'),
            (Include('docs/boards/acorn/generated/acorn-build-pi5-jtag-2.md', relative_images=True),),
            kind='how-to',
            reader='someone making the JTAG cable for an Acorn on a Raspberry Pi 5',
            own_dir=False,
        ),
        Wrapper(
            'docs/boards/acorn/setup/rpi-5/uart-wires.md',
            "How to prepare the UART cable's wires (Raspberry Pi 5)",
            Interim('**You have the parts for an Acorn on a Raspberry Pi 5 and are making the second of its '
                    "two cables, from the Acorn's P2 socket (the serial port). On this page: find wire 1, "
                    'check it with a meter, cut back the wires that are not used, crimp the rest.**'),
            (Include('docs/boards/acorn/generated/acorn-build-pi5-uart-1.md', relative_images=True),),
            kind='how-to',
            reader='someone making the UART cable for an Acorn on a Raspberry Pi 5',
            own_dir=False,
        ),
        Wrapper(
            'docs/boards/acorn/setup/rpi-5/uart-housing.md',
            "How to fill the UART cable's housing (Raspberry Pi 5)",
            Interim('**You have the P2 cable for an Acorn on a Raspberry Pi 5 with its wires flagged and '
                    'crimped, and are putting them into their housing. On this page: which wire goes in which '
                    'cavity, and a meter check of every wire.**'),
            (Include('docs/boards/acorn/generated/acorn-build-pi5-uart-2.md', relative_images=True),),
            kind='how-to',
            reader='someone making the UART cable for an Acorn on a Raspberry Pi 5',
            own_dir=False,
        ),
        Wrapper(
            'docs/boards/acorn/checks/rpi-5.md',
            'How to run the Acorn check on a Raspberry Pi 5',
            Interim('**You have an Acorn on a Raspberry Pi 5, its two cables built and fitted, and want to '
                    "know whether the wiring is right.**\n\nLog in to the Pi 5 first. At welland, the board's "
                    'page on <https://welland.fpgas.online/fpgas/> shows its ssh command under "Use your own '
                    'ssh client".'),
            (Include('docs/boards/acorn/generated/acorn-check-pi5-1.md', relative_images=True),),
            kind='how-to',
            reader='someone with an Acorn fitted on a Raspberry Pi 5 who wants to check its wiring',
            own_dir=False,
        ),
        Wrapper(
            'docs/boards/acorn/checks/about.md',
            'The Acorn check',
            Interim('**This page explains what the check of an Acorn is, what it does to the card, and what it can show on each carrier.**'),
            (Include('docs/boards/acorn/generated/acorn-check-about.md', relative_images=True),),
            kind='explanation',
            reader='someone who wants to know what the Acorn check is before running it',
            own_dir=False,
        ),
        Wrapper(
            'docs/boards/acorn/checks/rpi-5-tests.md',
            'Acorn tests and their wires on a Raspberry Pi 5',
            Interim('**The tests of the Acorn check on a Raspberry Pi 5: the wires each test uses, and what a pass shows.**'),
            (Include('docs/boards/acorn/generated/acorn-check-pi5-tests.md', relative_images=True),),
            kind='reference',
            reader='someone reading the result of an Acorn check on a Raspberry Pi 5',
            own_dir=False,
        ),
        Wrapper(
            'docs/boards/acorn/checks/compute-blade-tests.md',
            'Acorn tests and their wires on a Compute Blade',
            Interim('**The tests of the Acorn check on a Compute Blade: the wires each test uses, and what a pass shows.**'),
            (Include('docs/boards/acorn/generated/acorn-check-blade-tests.md', relative_images=True),),
            kind='reference',
            reader='someone reading the result of an Acorn check on a Compute Blade',
            own_dir=False,
        ),
        Wrapper(
            'docs/boards/acorn/troubleshooting/rpi-5-failing-test.md',
            'A failing Acorn test on a Raspberry Pi 5',
            Interim('**The check of your Acorn on a Raspberry Pi 5 printed a failing line, and you want to '
                    'know which wire it means.**'),
            (Include('docs/boards/acorn/generated/acorn-check-pi5-2.md', relative_images=True),),
            kind='reference',
            reader='someone whose Acorn check on a Raspberry Pi 5 printed a failing line',
            own_dir=False,
        ),
        Wrapper(
            'docs/boards/acorn/troubleshooting/rpi-5-other-messages.md',
            'Other Acorn check messages on a Raspberry Pi 5',
            Interim('**The check of your Acorn on a Raspberry Pi 5 printed a line that is not about one of '
                    "the cables' wires (the card's image, its memory, the tool itself), and you want to know "
                    'what it means.**'),
            (Include('docs/boards/acorn/generated/acorn-check-pi5-2b.md', relative_images=True),),
            kind='reference',
            reader='someone whose Acorn check on a Raspberry Pi 5 printed a message that is not about a wire',
            own_dir=False,
        ),
        Wrapper(
            'docs/boards/acorn/setup/packages.md',
            'How to install the Acorn packages',
            Interim('**You have an Acorn on a Raspberry Pi 5 with an M.2 HAT and want to install the '
                    'fpgas.online packages for it and run the check.**\n\nBefore '
                    'the check is run: its `p2-uart` and `p2-serial` tests need the '
                    "header's serial\nport on (`/dev/ttyAMA0`) and the kernel console off it: [the Pi's "
                    'settings](rpi-5/pi-settings.md#the-serial-port).'),
            (Include('docs/boards/generated/install-acorn.md'),),
            kind='how-to',
            reader='someone with an Acorn on a Raspberry Pi 5 who wants to install the fpgas.online packages for it',
            own_dir=False,
        ),
    ],
)

# The operator pages. Each landing page keeps the URL its hand-written copy had in these docs, so it sits in
# docs/setup/ among the docs' own pages and claims only its path; its split pages own their directory, but
# for docs/setup/pi/, which also holds the camera page of fpgas.online-cam.
_SHARED = dict(own_dir=False)
INFRA = Repo(
    "infra",
    PAGES={
        "docs/network.md": Page("docs/setup/network.md", **_SHARED),
        "docs/network/power-cycle.md": "docs/setup/network/power-cycle.md",
        "docs/network/switches.md": "docs/setup/network/switches.md",
        "docs/network/isolation.md": "docs/setup/network/isolation.md",
        "docs/network/poe-scripts.md": "docs/setup/network/poe-scripts.md",
        "docs/network/sources.md": "docs/setup/network/sources.md",
        "docs/netboot.md": Page("docs/setup/netboot.md", **_SHARED),
        "docs/netboot/update-root.md": "docs/setup/netboot/update-root.md",
        "docs/netboot/not-booting.md": "docs/setup/netboot/not-booting.md",
        "docs/netboot/root.md": "docs/setup/netboot/root.md",
        "docs/netboot/eeprom.md": "docs/setup/netboot/eeprom.md",
        "docs/netboot/history.md": "docs/setup/netboot/history.md",
        "docs/netboot/sources.md": "docs/setup/netboot/sources.md",
        "docs/gateway.md": Page("docs/setup/gateway.md", **_SHARED),
        "docs/gateway/deploy.md": "docs/setup/gateway/deploy.md",
        "docs/gateway/rebuild.md": "docs/setup/gateway/rebuild.md",
        "docs/gateway/certificates.md": "docs/setup/gateway/certificates.md",
        "docs/gateway/services.md": "docs/setup/gateway/services.md",
        "docs/gateway/sources.md": "docs/setup/gateway/sources.md",
        "docs/pi.md": Page("docs/setup/pi.md", **_SHARED),
        "docs/pi/services.md": Page("docs/setup/pi/services.md", **_SHARED),
        "docs/pi/setup-pi-units.md": Page("docs/setup/pi/setup-pi-units.md", **_SHARED),
        "docs/pi/boot-config.md": Page("docs/setup/pi/boot-config.md", **_SHARED),
        "docs/pi/models.md": Page("docs/setup/pi/models.md", **_SHARED),
        "docs/pi/sources.md": Page("docs/setup/pi/sources.md", **_SHARED),
        "docs/orange-pi.md": Page("docs/setup/orange-pi.md", **_SHARED),
        "docs/orange-pi/recover.md": "docs/setup/orange-pi/recover.md",
        "docs/orange-pi/add.md": "docs/setup/orange-pi/add.md",
        "docs/orange-pi/hub-host.md": "docs/setup/orange-pi/hub-host.md",
        "docs/orange-pi/design.md": "docs/setup/orange-pi/design.md",
        "docs/access.md": Page("docs/setup/access.md", **_SHARED),
        "docs/access/tweed.md": "docs/setup/access/tweed.md",
        "docs/access/pi-root.md": "docs/setup/access/pi-root.md",
        "docs/access/logging-in.md": "docs/setup/access/logging-in.md",
        "docs/access/people.md": "docs/setup/access/people.md",
        "docs/access/keys.md": "docs/setup/access/keys.md",
        "docs/access/verifying.md": "docs/setup/access/verifying.md",
        "docs/upstream-gateway.md": Page("docs/setup/upstream-gateway.md", **_SHARED),
        "docs/upstream-gateway/ipv4.md": "docs/setup/upstream-gateway/ipv4.md",
        "docs/upstream-gateway/ipv6-dns.md": "docs/setup/upstream-gateway/ipv6-dns.md",
        "docs/upstream-gateway/outbound.md": "docs/setup/upstream-gateway/outbound.md",
    },
    # in each landing page's order of its pages
    TOCTREES={
        "docs/setup/network.md": [
            ("Power-cycling a board", "network/power-cycle"),
            ("Converging the switches", "network/switches"),
            ("Checking isolation", "network/isolation"),
            ("The PoE scripts", "network/poe-scripts"),
            ("Sources", "network/sources"),
        ],
        "docs/setup/netboot.md": [
            ("Updating the NFS root", "netboot/update-root"),
            ("A Pi not booting", "netboot/not-booting"),
            ("What is in the NFS root", "netboot/root"),
            ("The EEPROM lock", "netboot/eeprom"),
            ("Historical tooling", "netboot/history"),
            ("Sources", "netboot/sources"),
        ],
        "docs/setup/gateway.md": [
            ("Deploying a gateway", "gateway/deploy"),
            ("Rebuilding a gateway", "gateway/rebuild"),
            ("Certificates at welland", "gateway/certificates"),
            ("Services", "gateway/services"),
            ("Sources", "gateway/sources"),
        ],
        "docs/setup/pi.md": [
            ("Services", "pi/services"),
            ("Units shipped by fpgas-online-setup-pi", "pi/setup-pi-units"),
            ("Boot-time configuration", "pi/boot-config"),
            ("Models and serial consoles", "pi/models"),
            ("Camera", "pi/camera"),
            ("Sources", "pi/sources"),
        ],
        "docs/setup/access.md": [
            ("The gateway, tweed", "access/tweed"),
            ("The Pi NFS root", "access/pi-root"),
            ("Logging in", "access/logging-in"),
            ("Adding or removing a person", "access/people"),
            ("Where the keys come from", "access/keys"),
            ("Verifying access", "access/verifying"),
        ],
        "docs/setup/upstream-gateway.md": [
            ("The uplink and inbound IPv4", "upstream-gateway/ipv4"),
            ("IPv6 and DNS", "upstream-gateway/ipv6-dns"),
            ("Outbound, from the gateway", "upstream-gateway/outbound"),
        ],
        "docs/setup/orange-pi.md": [
            ("Reading and recovering", "orange-pi/recover"),
            ("Adding and deploying", "orange-pi/add"),
            ("The hub host", "orange-pi/hub-host"),
            ("Why they boot this way", "orange-pi/design"),
        ],
    },
)

CAM = Repo(
    "cam",
    # beside infra's split pages of setup/pi.md, whose toctree lists it
    PAGES={"docs/camera.md": Page("docs/setup/pi/camera.md", **_SHARED)},
)

REPOS = {repo.name: repo for repo in (
    TEST_DESIGNS,
    INFRA,
    Repo("site"),
    Repo("tt"),
    Repo("setup-pi"),
    Repo("poe"),
    CAM,
    Repo("mechanical"),
)}


# A link or a picture: "!" for a picture, the label (one level of brackets inside it), the target.
FULL_LINK = re.compile(r"(!?)\[((?:[^\[\]]|\[[^\[\]]*\])*)\]\(([^)\s]+)\)")
# The end of a link whose label began on an earlier line.
LINK_END = re.compile(r"\]\(([^)\s]+)\)")
LINK_OR_END = re.compile(FULL_LINK.pattern + "|" + LINK_END.pattern)
IMAGE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)\)")
# A label that is a file name or path ending in .md, in backticks or not.
FILE_LABEL = re.compile(r"(`?)([\w./-]+\.md)\1")
OPENING_FENCE = re.compile(r"(`{3,}|~{3,})")
CLOSING_FENCE = re.compile(r"(`{3,}|~{3,})\s*$")
GITHUB_BLOB = re.compile(r"https://github\.com/" + ORG + r"/fpgas\.online-([\w.-]+)/blob/([^/#?]+)/([^#?]+)(?:#(.*))?$")
SCHEME = re.compile(r"[a-zA-Z][a-zA-Z0-9+.-]*:")
# Link forms rewrite_links does not handle. One appearing stops the sync, because a relative link left as
# written would be wrong on this site.
UNSUPPORTED = {
    "a reference-style link definition": re.compile(r"^\s{0,3}\[[^\]]+\]:\s+\S"),
    "an image": re.compile(r"!\[[^\]]*\]\("),
    "an angle-bracket link target": re.compile(r"\]\(<"),
    "a link with a title": re.compile(r"\]\([^)\s]+\s+[\"'(]"),
    # an <a id="..."></a> anchor carries no link, so it passes: it keeps an old heading's id on a landing page
    "a raw HTML link or image": re.compile(r"<(a\s[^>]*\bhref|img\s)", re.I),
}
ANCHOR = re.compile(r'^<a id="([a-z0-9_-]+)"></a>$')  # a GitHub heading slug keeps "_"
ALERT = re.compile(r"^(\s*)>\s*\[!([A-Za-z]+)\]\s*$")
ANY_ALERT = re.compile(r"^\s*>\s*\[!\w+\]")
KINDS = ("note", "tip", "important", "warning", "caution")
# The comment the sync (and its earlier name) puts at the top of what it writes, and of SOURCE.
OUR_COMMENT = re.compile(r"by tools/sync_(?:repos|test_designs)\.py\b[^\n]*\n?[^\n]*Do not edit (?:it|them) here")


class Missing(Exception):
    pass


class Stop(SystemExit):
    """Text of a repository that cannot be synced: that repository stops, with this reason."""


def in_code(lines):
    """For each line, whether it is fenced code (its fence lines included). A fence closes only with its own
    character, at least as long as it opened, and nothing after it."""
    mask, fence = [], None
    for line in lines:
        s = line.lstrip()
        if fence is None:
            m = OPENING_FENCE.match(s)
            if m and not (m.group(1)[0] == "`" and "`" in s[len(m.group(1)):]):
                fence = m.group(1)
                mask.append(True)
                continue
            mask.append(False)
        else:
            mask.append(True)
            m = CLOSING_FENCE.match(s)
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence):
                fence = None
    return mask


def outside_code(text, fn):
    """text with fn(line, line number) applied to every line outside fenced code."""
    lines = text.split("\n")
    return "\n".join(line if code else fn(line, n) for n, (line, code) in enumerate(zip(lines, in_code(lines)), 1))


def check_tables(repos=None):
    """Stop if two rows write one destination path, or two repositories claim one directory, or an owned
    directory lies in another, or a destination of one repository lies in a directory another owns, or a
    wrapper includes what nobody writes, or a toctree lists what nobody writes. Returns nothing; raises Stop
    naming the repositories."""
    repos = REPOS if repos is None else repos
    errors, by_path, by_dir = [], {}, {}
    for repo in repos.values():
        for dest in repo.dests():
            if dest in by_path:
                errors.append(f"{dest} is written by {by_path[dest]} and by {repo.name}")
            by_path[dest] = repo.name
        for d in repo.owned_dirs():
            if d in by_dir and by_dir[d] != repo.name:
                errors.append(f"directory {d} is claimed by {by_dir[d]} and by {repo.name}")
            by_dir.setdefault(d, repo.name)
    for d, name in by_dir.items():
        for other, owner in by_dir.items():
            if d != other and d.startswith(other + "/"):
                errors.append(f"directory {d} ({name}) is inside directory {other} ({owner})")
    for dest, name in by_path.items():
        owner = by_dir.get(posixpath.dirname(dest))
        if owner and owner != name:
            errors.append(f"{dest} ({name}) is in directory {posixpath.dirname(dest)}, which {owner} owns")
    for repo in repos.values():
        for w in repo.WRAPPERS:
            for inc in w.includes:
                if inc.docs_owned:
                    if posixpath.dirname(inc.path) in by_dir or inc.path in by_path:
                        errors.append(f"{w.dest} includes {inc.path} as the docs' own, but this tool writes it")
                elif inc.path not in by_path:
                    errors.append(f"{w.dest} includes {inc.path}, which no row writes (or name it docs_owned)")
            if w.toctree and w.dest in repo.TOCTREES:
                errors.append(f"{w.dest} has a toctree in its row and in TOCTREES")
        for page, entries in repo.TOCTREES.items():
            if page not in repo.dests():
                errors.append(f"TOCTREES of {repo.name} names {page}, which none of its rows writes")
            for _, doc in entries:
                target = posixpath.normpath(posixpath.join(posixpath.dirname(page), doc)) + ".md"
                if target not in by_path:
                    errors.append(f"the toctree of {page} lists {doc}, which no row writes")
    if errors:
        raise Stop("the tables disagree: " + "; ".join(errors))


def anchor_ids(text):
    """The ids of the lines of `text` that are only an id anchor, <a id="x"></a>, outside fenced code."""
    lines = text.split("\n")
    return {m.group(1) for line, code in zip(lines, in_code(lines)) if not code and (m := ANCHOR.match(line))}


def anchors_to_targets(text, shared=frozenset()):
    """A line that is only an id anchor, <a id="x"></a>, becomes the MyST target (x)=: on GitHub the anchor
    keeps an old heading's id on a landing page without showing anything; here the target does the same and
    lets this site's links to page.md#x resolve, which a raw HTML id does not. A MyST target is a label of the
    whole site, so an id in `shared` (anchored on more than one page of the repository, as "sources" can be)
    stays the raw anchor: the page keeps the id, and a link here to page.md#x, which needs the label, fails
    the build rather than going to the wrong page. Fenced code is left alone."""

    def one(line, _):
        m = ANCHOR.match(line)
        if not m and re.search(r"<a\s", line, re.IGNORECASE):
            raise Stop(f"a raw <a> that is not a line of its own reading exactly <a id=\"lower-case-id\"></a>: "
                       f"{line.strip()!r}. Only that form keeps an anchor here; write it so.")
        if not m or m.group(1) in shared:
            return line
        return f"({m.group(1)})="

    return outside_code(text, one)


def alerts_to_admonitions(text):
    """A GitHub alert, a blockquote whose first line is `> [!NOTE]` (or TIP, IMPORTANT, WARNING, CAUTION; any
    letter case, with or without a space after the `>`), becomes the MyST admonition of the same kind:
    `:::{note}`, the quoted lines without their `>` (and one space after it), then `:::`. Any other `> [!...]`
    stops the sync, and so does a line right after the quote without its `>`. The fence is longer than any run
    of colons the body starts a line with. An indented alert (in a list item) keeps its indentation on every
    line. A plain blockquote stays one. Fenced code is left alone."""
    lines, out, i = text.split("\n"), [], 0
    code = in_code(lines)
    while i < len(lines):
        line = lines[i]
        m = None if code[i] else ALERT.match(line)
        if not m or m.group(2).lower() not in KINDS:
            if not code[i] and ANY_ALERT.match(line):
                raise Stop(f"{line.strip()!r} is not an alert this tool can turn into an admonition (a line of "
                           f"its own, one of {', '.join(k.upper() for k in KINDS)})")
            out.append(line)
            i += 1
            continue
        indent, kind = m.group(1), m.group(2).lower()
        body, i = [], i + 1
        while i < len(lines) and lines[i].startswith(f"{indent}>"):
            rest = lines[i][len(indent) + 1:]
            body.append(rest[1:] if rest.startswith(" ") else rest)
            i += 1
        if i < len(lines) and lines[i].strip():
            # On GitHub a line right after a quote, without its ">", still belongs to it (a lazy continuation).
            raise Stop(f"the line after a > [!{m.group(2)}] alert has no '>': {lines[i].strip()!r}. "
                       f"Give it its '> ', or a blank line before it, where it is written.")
        runs = [len(r) for b in body for r in re.findall(r"^\s*(:{3,})", b)]
        fence = ":" * max([3, *(n + 1 for n in runs)])
        out.append(f"{indent}{fence}{{{kind}}}")
        out += [f"{indent}{b}" if b else "" for b in body]
        out.append(f"{indent}{fence}")
    return "\n".join(out)


def toctree(dest, repo):
    """The hidden toctree the TOCTREES of `repo` gives the page `dest`, as Markdown to append, or nothing."""
    entries = repo.TOCTREES.get(dest)
    if not entries:
        return ""
    lines = "".join(f"{title} <{doc}>\n" for title, doc in entries)
    return f"\n```{{toctree}}\n:hidden:\n\n{lines}```\n"


def slug(heading):
    """The anchor GitHub and MyST both give a heading (lower case, punctuation dropped, spaces to hyphens)."""
    text = re.sub(r"[`*_]", "", heading.strip().lower())
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def link_targets():
    """(repository, source path) -> (destination path, fragments that exist there or None for 'the source's
    own'), over every repository: what a link to a file of any of them can go to here."""
    targets = {}
    for repo in REPOS.values():
        for src, page in repo.pages().items():
            targets[(repo.name, src)] = (page.dest, None)
        for (src, heading), (_, page) in repo.SECTIONS.items():
            targets.setdefault((repo.name, src), (page, set()))[1].add(slug(heading))
        for src, dest in repo.ALSO_HERE.items():
            targets.setdefault((repo.name, src), (dest, set()))
    return targets


def published_dests():
    """Every page some row writes here (it counts as here before it is on disk)."""
    return {d for repo in REPOS.values()
            for d in [*(p.dest for p in repo.pages().values()), *(w.dest for w in repo.WRAPPERS)]}


def in_site(targets, name, path, fragment):
    """The page here a link to `path` of repository `name` goes to, or None."""
    hit = targets.get((name, path))
    if hit:
        dest, fragments = hit
        if not fragment or fragments is None or fragment in fragments:
            return dest
    return None


def rewrite_links(text, src, at, ref, *, repo, own_fragments=None, strict_fragments=False, files=None,
                  titles=None, notes=None):
    """Rewrite the links of the Markdown document src of `repo` so they work from the page `at` here.

    `at` is the page a reader sees the text on: the destination for a page, and for a section or a lead the
    page that includes it (Sphinx resolves the links of an included file from the including page; checked by
    building, 2026-10-05). own_fragments is given for a section: the anchors inside it; a "#fragment" link to
    any other heading of the source goes to the source on GitHub, or, with strict_fragments, stops the sync.
    files is given for a copied FILES file (at is then None): the names copied beside it, which its pictures
    must be; its links inside the site are written from the source root. titles, when given, reads the title
    of what a rewritten link opens, for a link whose text is a file name (see relabel). Fenced code is left
    alone."""
    targets, published, full = link_targets(), published_dests(), REPOS[repo].full

    def github(path, fragment):
        kind = "tree" if path.endswith("/") or "." not in posixpath.basename(path) else "blob"
        url = f"https://github.com/{full}/{kind}/{ref}/{path.rstrip('/')}" + (f"#{fragment}" if fragment else "")
        return url, ("repo", repo, path, ref)

    def here(dest, fragment):
        link = "/" + dest.removeprefix("docs/") if files is not None else posixpath.relpath(dest, posixpath.dirname(at))
        return link + (f"#{fragment}" if fragment else ""), ("page", dest)

    def one(target):
        """(the target rewritten, what it opens: ("page", path here) or ("repo", name, path, ref) or None)."""
        if target.startswith(PUBLISHED):
            # A link to a page of this site, written in the source by its published address: here it is a link
            # inside the site, which the build checks. (By its address it would be checked against what is
            # published, and a page added in the same change is not published yet.)
            page, _, fragment = target[len(PUBLISHED) :].partition("#")
            if page.endswith(".html") and "?" not in page:
                name = page.removesuffix(".html")
                moved = MOVED.get(f"{name}#{fragment}") if fragment else None
                if moved is not None:
                    name, _, fragment = moved.partition("#")
                elif name in MOVED:
                    name = MOVED[name].partition("#")[0]
                page = name + ".html"
            dest = "docs/" + page.removesuffix(".html") + ".md"
            if page.endswith(".html") and "?" not in page and ((DOCS / dest).exists() or dest in published):
                return here(dest, fragment)
            return target, None
        if SCHEME.match(target):
            m = GITHUB_BLOB.match(target)
            if m and m.group(1) in REPOS:
                name, url_ref, path, fragment = m.group(1), m.group(2), m.group(3), m.group(4) or ""
                dest = in_site(targets, name, path, fragment)
                return here(dest, fragment) if dest else (target, ("repo", name, path, url_ref))
            return target, None
        path, _, fragment = target.partition("#")
        if not path:
            if own_fragments is None:
                return target, ("page", at) if at else None
            if fragment in own_fragments:
                return target, ("page", at) if at else ("repo", repo, src, ref)
            if strict_fragments:
                raise Stop(f"{src}: #{fragment} is not a heading of its text nor of what {at} includes")
            return github(src, fragment)
        rooted = path.startswith("/")
        resolved = posixpath.normpath(path.lstrip("/") if rooted else posixpath.join(posixpath.dirname(src), path))
        if resolved.startswith("..") or resolved == ".":
            raise Stop(f"{src} links outside the repository: {target}")
        if path.endswith("/"):
            resolved += "/"
        dest = in_site(targets, repo, resolved, fragment)
        return here(dest, fragment) if dest else github(resolved, fragment)

    def line_fn(line, number):
        where = f"{src}:{number}"
        for what, pattern in UNSUPPORTED.items():
            if files is not None and what == "an image":
                continue
            if pattern.search(line):
                raise Stop(f"{where}: {what}, which rewrite_links does not handle. "
                           f"Teach it to, or write the link inline in {repo}.")
        if files is not None:
            for picture in IMAGE.findall(line):
                if picture not in files:
                    raise Stop(f"{where}: a picture {picture} that is not copied beside it (list it in FILES)")

        def sub(m):
            if m.group(4) is not None:  # the end of a link begun on an earlier line: no label to read
                return "](" + one(m.group(4))[0] + ")"
            bang, label, target = m.group(1), m.group(2), m.group(3)
            if bang:
                return m.group(0)
            new, opens = one(target)
            return f"[{relabel(label, opens, titles, f'{where} [{label}]', notes)}]({new})"

        return LINK_OR_END.sub(sub, line)

    return outside_code(text, line_fn)


def relabel(label, opens, titles, where, notes):
    """The label of a link: when it is a file name ending in .md, the title of what the link opens (`opens`,
    from rewrite_links); otherwise, or when that title cannot be read (reported in notes), the label itself."""
    m = FILE_LABEL.fullmatch(label)
    if not m or titles is None:
        return label
    if opens is None:
        reason = "it does not point at a file of a repository this tool reads, nor at a page here"
    elif not opens[-2 if opens[0] == "repo" else 1].endswith(".md"):
        reason = "it does not point at a Markdown file"
    else:
        title = titles(opens)
        if title and "[" not in title and "]" not in title:
            return title
        reason = f"the title of {' '.join(opens[1:])} could not be read"
    if notes is not None:
        notes.append(f"{where}: label left as it is: {reason}")
    return label


def section(text, heading, src):
    """The "## heading" section of text, up to the next "## " or "# " heading outside fenced code. A heading
    that is there twice stops the sync."""
    lines = text.split("\n")
    code = in_code(lines)
    starts = [i for i, line in enumerate(lines) if not code[i] and line.strip() == f"## {heading}"]
    if not starts:
        raise Missing(f'{src}: no "## {heading}" section')
    if len(starts) > 1:
        raise Stop(f'{src}: "## {heading}" is there {len(starts)} times')
    start = starts[0]
    for i in range(start + 1, len(lines)):
        if not code[i] and re.match(r"#{1,2} ", lines[i]):
            return "\n".join(lines[start:i]).rstrip() + "\n"
    return "\n".join(lines[start:]).rstrip() + "\n"


def headings_twice(text):
    """The "## " headings that text has more than once, outside fenced code."""
    lines = text.split("\n")
    seen = [line.strip() for line, code in zip(lines, in_code(lines)) if not code and line.startswith("## ")]
    return sorted({h for h in seen if seen.count(h) > 1})


def fragments_in(text):
    """The anchors of text: its headings and its MyST targets, outside fenced code."""
    found, lines = set(), text.split("\n")
    for line, code in zip(lines, in_code(lines)):
        if code:
            continue
        m = re.match(r"#{1,6} (.+)", line)
        if m:
            found.add(slug(m.group(1)))
        m = re.match(r"\(([\w-]+)\)=$", line)
        if m:
            found.add(m.group(1))
    return found


def title_of(text):
    """The first "# " heading of a Markdown text, outside fenced code, or None."""
    lines = text.split("\n")
    for line, code in zip(lines, in_code(lines)):
        if not code and line.startswith("# "):
            return line[2:].strip()
    return None


def marker(repo, src, what, ref):
    return (f"% {what} is copied from https://github.com/{repo.full}/blob/{ref}/{src}\n"
            f"% by tools/sync_repos.py. Do not edit it here: change it in {repo.name}.\n\n")


def wrapper_marker(repo):
    return (f"% This page is generated by tools/sync_repos.py from its row in WRAPPERS ({repo.name}), from files\n"
            f"% of https://github.com/{repo.full}. Do not edit it here: change the row, or those files.\n\n")


def wrapper_text(repo, w, lead):
    """The page a WRAPPERS row makes, given its lead's text (already link-rewritten; None for no lead)."""
    blocks = [f"# {w.title}"]
    front = ""
    if w.kind:
        front = (f"---\ntype: {w.kind}\nowner: {repo.name} maintainers\nreader: {w.reader}\n"
                 f"review: {WRAPPER_REVIEW}\n---\n\n")
    if lead:
        blocks.append(lead.strip("\n"))
    for inc in w.includes:
        rel = posixpath.relpath(inc.path, posixpath.dirname(w.dest))
        blocks.append(f"```{{include}} {rel}\n" + (":relative-images:\n" if inc.relative_images else "") + "```")
    if w.toctree:
        t = w.toctree
        if t.heading:
            blocks.append(f"## {t.heading}")
        options = (":hidden:\n" if t.hidden else "") + (f":maxdepth: {t.maxdepth}\n" if t.maxdepth else "")
        entries = "".join((f"{e[0]} <{e[1]}>\n" if isinstance(e, tuple) else f"{e}\n") for e in t.entries)
        blocks.append(f"```{{toctree}}\n{options}\n{entries}```")
    return front + wrapper_marker(repo) + "\n\n".join(blocks) + "\n"


def source_text(repo, ref, commit):
    return (f"These files are copied from https://github.com/{repo.full}\n"
            f"by tools/sync_repos.py. Do not edit them here: change them in {repo.name}.\n\n"
            f"ref: {ref}\ncommit: {commit}\n")


def resolve(full, ref):
    """The commit a branch of `full` points at; exactly that branch, not any ref ending in its name."""
    ref_name = f"refs/heads/{ref}"
    lines = subprocess.run(["git", "ls-remote", f"https://github.com/{full}.git", ref_name],
                           check=True, capture_output=True, text=True).stdout.splitlines()
    matches = [line.split()[0] for line in lines if line.split()[1] == ref_name]
    if len(matches) != 1:
        raise Stop(f"{full} has no branch {ref!r}")
    return matches[0]


def fetch(full, commit, path):
    url = f"https://raw.githubusercontent.com/{full}/{commit}/{path}"
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise Missing(path) from e
        raise


class Titles:
    """Reads the title of what a link opens, for relabel. A page here has its own title (as this run writes
    it, or as it is on disk); a file of a repository its title at the commit its branch points at (the commit
    being synced, when it is that repository and branch)."""

    def __init__(self, commits, page_titles):
        self.commits, self.page_titles, self.cache = dict(commits), page_titles, {}

    def __call__(self, opens):
        if opens[0] == "page":
            dest = opens[1]
            if dest in self.page_titles:
                return self.page_titles[dest]
            return title_of((DOCS / dest).read_text()) if (DOCS / dest).is_file() else None
        _, name, path, ref = opens
        if (name, path, ref) not in self.cache:
            full = REPOS[name].full
            try:
                if (name, ref) not in self.commits:
                    self.commits[(name, ref)] = resolve(full, ref)
                self.cache[(name, path, ref)] = title_of(fetch(full, self.commits[(name, ref)], path).decode("utf-8"))
            except (Missing, Stop):
                self.cache[(name, path, ref)] = None
        return self.cache[(name, path, ref)]


def take(repo, ref, commit, titles_for, notes):
    """{path here: bytes} for everything `repo` publishes, and [what is missing]. titles_for(page_titles)
    gives the title reader once the pages' own titles are known. Raises Stop when a text cannot be synced."""
    wanted, missing = {}, []
    texts = {}
    for src in sorted({*repo.PAGES, *(s for s, _ in repo.SECTIONS), *repo.lead_sources()}):
        try:
            texts[src] = fetch(repo.full, commit, src).decode("utf-8")
        except Missing as e:
            missing.append(str(e))
    for src in repo.lead_sources():
        if src in texts and headings_twice(texts[src]):
            raise Stop(f"{src} has these headings more than once: {', '.join(headings_twice(texts[src]))}")
    pages = {src: p.dest for src, p in repo.pages().items()}
    page_titles = {dest: title_of(texts[src]) for src, dest in pages.items() if src in texts}
    page_titles.update({w.dest: w.title for w in repo.WRAPPERS})
    titles = titles_for(page_titles)
    for dest, (src, names) in repo.FILES.items():
        for name in names:
            try:
                data = fetch(repo.full, commit, f"{src}/{name}")
            except Missing as e:
                missing.append(str(e))
                continue
            if name.endswith(".md"):
                text = data.decode("utf-8")
                data = rewrite_links(text, f"{src}/{name}", None, ref, repo=repo.name,
                                     own_fragments=fragments_in(text), files=set(names), titles=titles,
                                     notes=notes).encode("utf-8")
            wanted[DOCS / dest / name] = data
    seen = collections.Counter(i for src in pages if src in texts for i in anchor_ids(texts[src]))
    shared = {i for i, n in seen.items() if n > 1}
    for src, dest in pages.items():
        if src in texts:
            body = rewrite_links(texts[src], src, dest, ref, repo=repo.name, titles=titles, notes=notes)
            body = anchors_to_targets(alerts_to_admonitions(body), shared)
            wanted[DOCS / dest] = (marker(repo, src, "This page", ref) + body + toctree(dest, repo)).encode("utf-8")
    for (src, heading), (dest, page) in repo.SECTIONS.items():
        if src in texts:
            try:
                part = section(texts[src], heading, src)
            except Missing as e:
                missing.append(str(e))
                continue
            body = alerts_to_admonitions(rewrite_links(part, src, page, ref, repo=repo.name,
                                                       own_fragments=fragments_in(part), titles=titles, notes=notes))
            wanted[DOCS / dest] = (marker(repo, src, f'This section ("{heading}")', ref) + body).encode("utf-8")
    for w in repo.WRAPPERS:
        for inc in w.includes:
            if inc.docs_owned and not (DOCS / inc.path).is_file():
                raise Stop(f"{w.dest} includes {inc.path}, the docs' own file, which does not exist")
        lead = None
        if isinstance(w.lead, Interim):
            lead = w.lead.text
            notes.append(f"{w.dest}: interim lead, not yet in {repo.name}: move it there and give the row a Lead")
        elif isinstance(w.lead, Lead):
            if w.lead.path not in texts:
                continue
            try:
                part = section(texts[w.lead.path], w.lead.heading, w.lead.path)
            except Missing as e:
                missing.append(str(e))
                continue
            body = part.split("\n", 1)[1]
            # An anchor-only link in a lead goes to a heading of the lead or of a file the page includes.
            fragments = fragments_in(body)
            for inc in w.includes:
                path = DOCS / inc.path
                if path in wanted:
                    fragments |= fragments_in(wanted[path].decode("utf-8"))
                elif path.is_file():
                    fragments |= fragments_in(path.read_text())
            lead = alerts_to_admonitions(rewrite_links(body, w.lead.path, w.dest, ref, repo=repo.name,
                                                       own_fragments=fragments, strict_fragments=True,
                                                       titles=titles, notes=notes))
        wanted[DOCS / w.dest] = wrapper_text(repo, w, lead).encode("utf-8")
    return wanted, missing


def changes_for(repo, ref, wanted):
    """[(what, path)] that writing `wanted` makes. Raises Stop when an owned directory holds what cannot be
    removed, before anything is written."""
    changes = []
    for path, data in wanted.items():
        if not path.exists() or path.read_bytes() != data:
            changes.append(("update" if path.exists() else "add", path))
    for dest in repo.owned_dirs():
        d = DOCS / dest
        if d.exists():
            for p in sorted(d.iterdir()):
                if p.name != SOURCE and p not in wanted:
                    if not p.is_file():
                        raise Stop(f"{p.relative_to(DOCS)} is not a file. The directories this tool owns hold "
                                   f"only what it writes; move it out.")
                    changes.append(("remove", p))
    # A new upstream commit alone is not a change (see below), but a different ref is: the files are
    # then vouched for by another branch, and SOURCE has to say so. So is a SOURCE naming another repository.
    for dest in repo.owned_dirs():
        src = DOCS / dest / SOURCE
        if src.exists():
            text = src.read_text()
            if f"\nref: {ref}\n" not in text or f"https://github.com/{repo.full}\n" not in text:
                changes.append(("source", src))
        else:
            changes.append(("source", src))
    return changes


def stale_files(repos=None):
    """{repository name or "?": [paths]}: files in docs/ that carry this tool's comment, and SOURCE files of
    it, that no row of any repository accounts for. A file in an owned directory is accounted for (the sync
    of that directory removes what it does not list)."""
    repos = REPOS if repos is None else repos
    dests = {d for repo in repos.values() for d in repo.dests()}
    owned = {d for repo in repos.values() for d in repo.owned_dirs()}
    found = {}
    for path in sorted((DOCS / "docs").rglob("*")):
        rel = path.relative_to(DOCS).as_posix()
        if rel.startswith("docs/_build/") or not path.is_file() or path.suffix not in ("", ".md", ".inc"):
            continue
        head = path.read_bytes()[:600].decode("utf-8", "replace")
        if not OUR_COMMENT.search(head) or rel in dests or posixpath.dirname(rel) in owned:
            continue
        m = (re.search(r"change it in ([\w-]+)\.", head) or re.search(r"WRAPPERS \(([\w-]+)\)", head)
             or re.search(r"https://github\.com/" + ORG + r"/fpgas\.online-([\w.-]+)\n", head))
        found.setdefault(m.group(1) if m else "?", []).append(rel)
    return found


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", action="append", choices=list(REPOS), metavar="NAME",
                    help=f"a repository to take (default: every one): {', '.join(REPOS)}")
    ap.add_argument("--ref", help="the branch to take (default main); only with exactly one --repo")
    ap.add_argument("--check", action="store_true", help="write nothing; exit 1 if anything would change")
    args = ap.parse_args(argv)
    names = args.repo or list(REPOS)
    if args.ref and len(names) != 1:
        ap.error("--ref needs exactly one --repo")

    def full(name):
        return REPOS[name].full if name in REPOS else f"{ORG}/fpgas.online-{name}"

    try:
        check_tables()
    except Stop as e:
        print(f"sync: FAILED. tools/sync_repos.py: {e.code}", file=sys.stderr)
        return 2

    failures, results, notes = {}, [], []
    for name in names:
        repo = REPOS[name]
        if repo.empty():
            print(f"{repo.full}: nothing listed")
            continue
        ref = args.ref or "main"
        try:
            commit = resolve(repo.full, ref)
            print(f"{repo.full} {ref} = {commit}")
            wanted, missing = take(repo, ref, commit, lambda pt: Titles({(name, ref): commit}, pt), notes)
            if missing:
                failures[name] = [f"{ref} ({commit[:12]}) does not have {m}" for m in missing]
                continue
            results.append((repo, ref, commit, wanted, changes_for(repo, ref, wanted)))
        except Stop as e:
            failures[name] = [str(e.code)]
    for name, paths in stale_files().items():
        failures.setdefault(name, []).extend(
            f"{p} carries the sync's comment, but no row accounts for it: remove it, or give it its row back"
            for p in paths)
    results = [r for r in results if r[0].name not in failures]

    for note in notes:
        print(f"  note   {note}")
    total = 0
    for repo, ref, commit, wanted, changes in results:
        for what, path in changes:
            print(f"  {what:6} {path.relative_to(DOCS)}")
        total += len(changes)
    if not args.check:
        for repo, ref, commit, wanted, changes in results:
            for what, path in changes:
                if what == "remove":
                    path.unlink()
                elif what != "source":  # SOURCE is rewritten below
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(wanted[path])
            if changes:
                # SOURCE moves only with the files or the ref, so a new upstream commit alone changes nothing
                for dest in repo.owned_dirs():
                    (DOCS / dest).mkdir(parents=True, exist_ok=True)
                    (DOCS / dest / SOURCE).write_text(source_text(repo, ref, commit))
    if failures:
        for name, reasons in failures.items():
            for reason in reasons:
                print(f"sync: FAILED. {full(name)}: {reason}", file=sys.stderr)
        print("A file was moved, renamed or removed there (or never added), or its text cannot be synced: update "
              "that repository's tables in tools/sync_repos.py, or fix the text there. The other repositories "
              "were synced.", file=sys.stderr)
        return 2
    if not total:
        print("up to date")
        return 0
    if args.check:
        return 1
    print(f"{total} file(s) changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
