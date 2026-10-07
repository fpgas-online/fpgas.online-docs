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

FILES      copied byte for byte (the Acorn wiring sheets and pin tables), per destination directory.
PAGES      whole Markdown documents, published as pages here.
SECTIONS   one "## heading" section of a Markdown document, written as a fragment that a page here
           includes (each board's "Installing the ... Packages").
ALSO_HERE  documents not taken whole that have a page here on the same subject (a link to one goes there).
TOCTREES   the hidden toctree appended to a pulled landing page.
WRAPPERS   pages here that are only a title, a lead and includes of synced files. A wrapper may exist only
           as a row here: this tool writes it, and nothing in it is written by hand in these docs. Its lead
           is a "## " section of a file in the home repository, taken verbatim (Lead), or, until that file
           exists there, the text itself (Interim, listed on every run so it does not stay).

Ownership: a destination directory belongs to exactly one repository (the directories of its FILES,
PAGES, SECTIONS and WRAPPERS; a wrapper with own_dir=False claims only its own path). Everything in an
owned directory is written by this tool or removed. Two repositories claiming one directory, or two rows
one destination path, is an error.

Text that is synced (PAGES, SECTIONS, leads, and the Markdown among FILES) was written to be read on
GitHub, so its links are rewritten (rewrite_links, own_links):
- a link to a file that this tool publishes here, from ANY repository, becomes a link inside the site: a
  relative link to a file in the same repository, or an absolute
  https://github.com/fpgas-online/fpgas.online-<repo>/blob/<ref>/<path> URL to another;
- a link to this site's published address (https://docs.fpgas.online/en/latest/...html) becomes a link
  inside the site when that page is here;
- any other relative link becomes the file's GitHub URL in its own repository.
Fragments are kept. A GitHub alert (a blockquote opening `> [!NOTE]`, TIP, IMPORTANT, WARNING or CAUTION)
becomes the MyST admonition of its kind (alerts_to_admonitions). A link whose text is a file name or path
ending in .md gets as its text the title (the first "# " heading) of the page it points at; when that cannot
be read, the text is left and the output says so. Each synced page starts with a comment saying where to edit it.

If a repository does not have a listed file or section, this stops with exit status 2 and names the
repository and the file. That means it moved or was renamed there: update the tables below to match, never
paper over it. Only what is listed is copied; a new file there is not picked up until it is added here. The
scheduled workflow (.github/workflows/sync-repos.yml) runs this daily for every repository and opens a pull
request with the result.

fpgas.online-mechanical: its PAGES go here; its drawings are copied by tools/sync_mechanical.py, which
pins one commit for them.
"""

import argparse
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
class Wrapper:
    dest: str
    title: str
    lead: object = None  # Lead, Interim or None
    includes: tuple = ()
    toctree: Toctree = None
    own_dir: bool = True  # False: the page sits among pages of these docs and claims only its own path


@dataclass
class Repo:
    name: str
    FILES: dict = field(default_factory=dict)      # destination directory: (source directory, [file names])
    PAGES: dict = field(default_factory=dict)      # source document: the page it becomes here
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

    def dests(self):
        """Every path this repository's rows write here."""
        out = [f"{d}/{n}" for d, (_, names) in self.FILES.items() for n in names]
        out += [*self.PAGES.values(), *(d for d, _ in self.SECTIONS.values()), *(w.dest for w in self.WRAPPERS)]
        return out

    def owned_dirs(self):
        return sorted({*self.FILES, *(posixpath.dirname(d) for d in self.PAGES.values()),
                       *(posixpath.dirname(d) for d, _ in self.SECTIONS.values()),
                       *(posixpath.dirname(w.dest) for w in self.WRAPPERS if w.own_dir)})

    def lead_sources(self):
        return {w.lead.path for w in self.WRAPPERS if isinstance(w.lead, Lead)}


_GUIDE = ("bom", "jtag-connector-1", "jtag-connector-2", "uart-connector-1", "uart-connector-2", "bench-check",
          "fitting", "verifying-1", "verifying-2", "verifying-2b")


def _guide_pages(*more):
    """The visible toctree that ends an index page of the Acorn building guide."""
    return Toctree((*_GUIDE, *more), heading="The pages of this guide", maxdepth=1, hidden=False)


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
                "acorn-cable-blade-fit.png",
                "acorn-cable-blade-fit-dark.png",
                "acorn-cable-pi5-fit.png",
                "acorn-cable-pi5-fit-dark.png",
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
                "acorn-check-blade-1.md",
                "acorn-check-blade-2.md",
                "acorn-check-blade-2b.md",
                "acorn-check-blade-3.md",
                "acorn-check-blade-wires.png",
                "acorn-check-blade-wires-dark.png",
                "acorn-check-pi5-1.md",
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
            ("docs/boards/generated/install-acorn.md", "docs/boards/acorn/packages.md"),
        ("docs/hardware/arty-a7.md", "Installing the Arty Packages"):
            ("docs/boards/generated/install-arty-a7.md", "docs/boards/arty-a7.md"),
        ("docs/hardware/netv2.md", "Installing the NeTV2 Packages"):
            ("docs/boards/generated/install-netv2.md", "docs/boards/netv2.md"),
        ("docs/hardware/fomu-evt.md", "Installing the Fomu Packages"):
            ("docs/boards/generated/install-fomu-evt.md", "docs/boards/fomu-evt.md"),
        ("docs/hardware/tt-fpga.md", "Installing the TT FPGA Packages"):
            ("docs/boards/generated/install-tt-fpga.md", "docs/boards/tt-fpga.md"),
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
            'docs/boards/acorn/building/compute-blade/bench-check.md',
            'Compute Blade cables: bench check',
            Interim('**You have built both cables for an Acorn on a Compute Blade. Before anything is '
                    'powered, a check on the host with a meter that ground reaches the plugs and that the 3.3 '
                    'V wire reaches nothing.**'),
            (Include('docs/boards/acorn/generated/acorn-build-blade-bench.md', relative_images=True),),
        ),
        Wrapper(
            'docs/boards/acorn/building/compute-blade/bom.md',
            'Compute Blade cables: parts and tools',
            Interim('**You are about to build the two cables for an Acorn on a Compute Blade: tick off every '
                    'line before you start.**'),
            (Include('docs/boards/acorn/generated/acorn-blade-bom.md'),),
        ),
        Wrapper(
            'docs/boards/acorn/building/compute-blade/fitting.md',
            'Compute Blade cables: fitting',
            Interim('**Your two cables for an Acorn on a Compute Blade have passed the bench check, and you '
                    'are fitting them and the card.**'),
            (Include('docs/boards/acorn/generated/acorn-build-blade-fit.md', relative_images=True),),
        ),
        Wrapper(
            'docs/boards/acorn/building/compute-blade/index.md',
            'Compute Blade cables: overview',
            Interim('**You have an Acorn and a Compute Blade, and want to build the two cables between them, '
                    'fit them and check them.** An Acorn on a Raspberry Pi 5 has [its own '
                    'guide](../rpi-5/index.md); nothing there is for a Compute Blade.'),
            (Include('docs/boards/acorn/generated/acorn-build-blade-overview.md', relative_images=True),),
            _guide_pages("verifying-3"),
        ),
        Wrapper(
            'docs/boards/acorn/building/compute-blade/jtag-connector-1.md',
            'Compute Blade cables: JTAG connector 1, prepare the wires',
            Interim('**You have the parts for an Acorn on a Compute Blade and are making the first of its two '
                    "cables, from the Acorn's P1 socket (JTAG). On this page: cut the bought cable in half, "
                    'find wire 1, check it with a meter, cut back the wires that are not used, crimp the '
                    'rest.**'),
            (Include('docs/boards/acorn/generated/acorn-build-blade-jtag-1.md', relative_images=True),),
        ),
        Wrapper(
            'docs/boards/acorn/building/compute-blade/jtag-connector-2.md',
            'Compute Blade cables: JTAG connector 2, fill and check the housing',
            Interim('**You have the P1 cable for an Acorn on a Compute Blade with its wires flagged and '
                    'crimped, and are putting them into their housing. On this page: which wire goes in which '
                    'cavity, and a meter check of every wire.**'),
            (Include('docs/boards/acorn/generated/acorn-build-blade-jtag-2.md', relative_images=True),),
        ),
        Wrapper(
            'docs/boards/acorn/building/compute-blade/uart-connector-1.md',
            'Compute Blade cables: UART connector 1, prepare the wires',
            Interim('**You have the parts for an Acorn on a Compute Blade and are making the second of its '
                    "two cables, from the Acorn's P2 socket (the serial port). On this page: find wire 1, "
                    'check it with a meter, cut back the wires that are not used, solder the resistor into '
                    'the J2 wire, crimp the rest.**'),
            (Include('docs/boards/acorn/generated/acorn-build-blade-uart-1.md', relative_images=True),),
        ),
        Wrapper(
            'docs/boards/acorn/building/compute-blade/uart-connector-2.md',
            'Compute Blade cables: UART connector 2, fill and check the housing',
            Interim('**You have the P2 cable for an Acorn on a Compute Blade with its wires flagged and '
                    'crimped, and are putting them into their housing. On this page: which wire goes in which '
                    'cavity, and a meter check of every wire.**'),
            (Include('docs/boards/acorn/generated/acorn-build-blade-uart-2.md', relative_images=True),),
        ),
        Wrapper(
            'docs/boards/acorn/building/compute-blade/verifying-1.md',
            'Compute Blade cables: verifying 1, run the check and read the result',
            Interim('**You have an Acorn on a Compute Blade, its two cables built and fitted, and want to '
                    'know what the check on the blade says about the wiring. On a Compute Blade today it '
                    'cannot yet prove the cables: the paragraph "What to expect on a Compute Blade today" '
                    'below says why.**\n\nLog in to the blade first. At ps1:'),
            (_PS1_LOGIN, Include('docs/boards/acorn/generated/acorn-check-blade-1.md', relative_images=True)),
        ),
        Wrapper(
            'docs/boards/acorn/building/compute-blade/verifying-2.md',
            'Compute Blade cables: verifying 2, when a test fails',
            Interim('**The check of your Acorn on a Compute Blade printed a failing line, and you want to '
                    'know which wire it means.**'),
            (Include('docs/boards/acorn/generated/acorn-check-blade-2.md', relative_images=True),),
        ),
        Wrapper(
            'docs/boards/acorn/building/compute-blade/verifying-2b.md',
            'Compute Blade cables: verifying 2b, when the failure is not a wire',
            Interim('**The check of your Acorn on a Compute Blade printed a line that is not about one of the '
                    "cables' wires (the card's image, its memory, the tool itself), and you want to know what "
                    'it means.**'),
            (Include('docs/boards/acorn/generated/acorn-check-blade-2b.md', relative_images=True),),
        ),
        Wrapper(
            'docs/boards/acorn/building/compute-blade/verifying-3.md',
            'Compute Blade cables: verifying 3, what has been run on a Compute Blade',
            Interim("**Your Compute Blade's check fails at `jtag` although the wiring is right, or you want "
                    'to know what to expect before you start: what has and has not been run on a blade, and '
                    'the pin JTAG shares with the serial port.**'),
            (Include('docs/boards/acorn/generated/acorn-check-blade-3.md', relative_images=True),),
        ),
        Wrapper(
            'docs/boards/acorn/building/rpi-5/bench-check.md',
            'Raspberry Pi 5 cables: bench check',
            Interim('**You have built both cables for an Acorn on a Raspberry Pi 5. Before anything is '
                    'powered, a check on the host with a meter that ground reaches the plugs and that the 3.3 '
                    'V wire reaches nothing.**'),
            (Include('docs/boards/acorn/generated/acorn-build-pi5-bench.md', relative_images=True),),
        ),
        Wrapper(
            'docs/boards/acorn/building/rpi-5/bom.md',
            'Raspberry Pi 5 cables: parts and tools',
            Interim('**You are about to build the two cables for an Acorn on a Raspberry Pi 5: tick off every '
                    'line before you start.**'),
            (Include('docs/boards/acorn/generated/acorn-pi5-bom.md'),),
        ),
        Wrapper(
            'docs/boards/acorn/building/rpi-5/fitting.md',
            'Raspberry Pi 5 cables: fitting',
            Interim('**Your two cables for an Acorn on a Raspberry Pi 5 have passed the bench check, and you '
                    'are fitting them and the card.**'),
            (Include('docs/boards/acorn/generated/acorn-build-pi5-fit.md', relative_images=True),),
        ),
        Wrapper(
            'docs/boards/acorn/building/rpi-5/index.md',
            'Raspberry Pi 5 cables: overview',
            Interim('**You have an Acorn and a Raspberry Pi 5, and want to build the two cables between them, '
                    'fit them and check them.** An Acorn on a Compute Blade has [its own '
                    'guide](../compute-blade/index.md); nothing there is for a Raspberry Pi 5.'),
            (Include('docs/boards/acorn/generated/acorn-build-pi5-overview.md', relative_images=True),),
            _guide_pages(),
        ),
        Wrapper(
            'docs/boards/acorn/building/rpi-5/jtag-connector-1.md',
            'Raspberry Pi 5 cables: JTAG connector 1, prepare the wires',
            Interim('**You have the parts for an Acorn on a Raspberry Pi 5 and are making the first of its '
                    "two cables, from the Acorn's P1 socket (JTAG). On this page: cut the bought cable in "
                    'half, find wire 1, check it with a meter, cut back the wires that are not used, crimp '
                    'the rest.**'),
            (Include('docs/boards/acorn/generated/acorn-build-pi5-jtag-1.md', relative_images=True),),
        ),
        Wrapper(
            'docs/boards/acorn/building/rpi-5/jtag-connector-2.md',
            'Raspberry Pi 5 cables: JTAG connector 2, fill and check the housing',
            Interim('**You have the P1 cable for an Acorn on a Raspberry Pi 5 with its wires flagged and '
                    'crimped, and are putting them into their housing. On this page: which wire goes in which '
                    'cavity, and a meter check of every wire.**'),
            (Include('docs/boards/acorn/generated/acorn-build-pi5-jtag-2.md', relative_images=True),),
        ),
        Wrapper(
            'docs/boards/acorn/building/rpi-5/uart-connector-1.md',
            'Raspberry Pi 5 cables: UART connector 1, prepare the wires',
            Interim('**You have the parts for an Acorn on a Raspberry Pi 5 and are making the second of its '
                    "two cables, from the Acorn's P2 socket (the serial port). On this page: find wire 1, "
                    'check it with a meter, cut back the wires that are not used, crimp the rest.**'),
            (Include('docs/boards/acorn/generated/acorn-build-pi5-uart-1.md', relative_images=True),),
        ),
        Wrapper(
            'docs/boards/acorn/building/rpi-5/uart-connector-2.md',
            'Raspberry Pi 5 cables: UART connector 2, fill and check the housing',
            Interim('**You have the P2 cable for an Acorn on a Raspberry Pi 5 with its wires flagged and '
                    'crimped, and are putting them into their housing. On this page: which wire goes in which '
                    'cavity, and a meter check of every wire.**'),
            (Include('docs/boards/acorn/generated/acorn-build-pi5-uart-2.md', relative_images=True),),
        ),
        Wrapper(
            'docs/boards/acorn/building/rpi-5/verifying-1.md',
            'Raspberry Pi 5 cables: verifying 1, run the check and read the result',
            Interim('**You have an Acorn on a Raspberry Pi 5, its two cables built and fitted, and want to '
                    "know whether the wiring is right.**\n\nLog in to the Pi 5 first. At welland, the board's "
                    'page on <https://welland.fpgas.online/fpgas/> shows its ssh command under "Use your own '
                    'ssh client".'),
            (Include('docs/boards/acorn/generated/acorn-check-pi5-1.md', relative_images=True),),
        ),
        Wrapper(
            'docs/boards/acorn/building/rpi-5/verifying-2.md',
            'Raspberry Pi 5 cables: verifying 2, when a test fails',
            Interim('**The check of your Acorn on a Raspberry Pi 5 printed a failing line, and you want to '
                    'know which wire it means.**'),
            (Include('docs/boards/acorn/generated/acorn-check-pi5-2.md', relative_images=True),),
        ),
        Wrapper(
            'docs/boards/acorn/building/rpi-5/verifying-2b.md',
            'Raspberry Pi 5 cables: verifying 2b, when the failure is not a wire',
            Interim('**The check of your Acorn on a Raspberry Pi 5 printed a line that is not about one of '
                    "the cables' wires (the card's image, its memory, the tool itself), and you want to know "
                    'what it means.**'),
            (Include('docs/boards/acorn/generated/acorn-check-pi5-2b.md', relative_images=True),),
        ),
        Wrapper(
            'docs/boards/acorn/packages.md',
            'Acorn packages and the boot check',
            Interim('**You have an Acorn on its host (a Raspberry Pi 5 with an M.2 HAT, or a CM4 or CM5 on a '
                    'Compute Blade) and\nwant to install the fpgas.online packages for it, run the check, and '
                    'identify or verify its flash with the\nflash tool (`id` and `verify`; writing the flash '
                    'is on [Installing and updating the\nimages](designs/install-images.md)).**\n\nOn a '
                    'Raspberry Pi 5, before the check is run: its `p2-uart` and `p2-serial` tests need the '
                    "header's serial\nport on (`/dev/ttyAMA0`) and the kernel console off it: [the Pi's "
                    'settings](wiring/rpi-5-host.md#the-serial-port).'),
            (Include('docs/boards/generated/install-acorn.md'),),
            own_dir=False,
        ),
    ],
)

REPOS = {repo.name: repo for repo in (
    TEST_DESIGNS,
    Repo("infra"),
    Repo("site"),
    Repo("tt"),
    Repo("setup-pi"),
    Repo("poe"),
    Repo("cam"),
    Repo("mechanical"),
)}

LINK = re.compile(r"(?<=\]\()([^)\s]+)(?=\))")
# A link whose text is a file name or path ending in .md, in backticks or not.
FILE_LABEL = re.compile(r"\[(`?)([\w./-]+\.md)\1\]\(([^)\s]+)\)")
FENCE = re.compile(r"^(```|~~~)")
GITHUB_BLOB = re.compile(r"https://github\.com/" + ORG + r"/fpgas\.online-([\w.-]+)/blob/([^/#?]+)/([^#?]+)(?:#(.*))?$")
# Link forms LINK does not match. None is in the documents taken today; one appearing stops the sync, because
# a relative link left as written would be wrong on this site.
UNSUPPORTED = {
    "a reference-style link definition": re.compile(r"^\s{0,3}\[[^\]]+\]:\s+\S"),
    "an image": re.compile(r"!\[[^\]]*\]\("),
    "an angle-bracket link target": re.compile(r"\]\(<"),
    "a link with a title": re.compile(r"\]\([^)\s]+\s+[\"'(]"),
    # an <a id="..."></a> anchor carries no link, so it passes: it keeps an old heading's id on a landing page
    "a raw HTML link or image": re.compile(r"<(a\s[^>]*\bhref|img\s)", re.I),
}


class Missing(Exception):
    pass


def check_tables(repos=None):
    """Stop if two rows write one destination path, or two repositories claim one directory, or a destination
    of one repository lies in a directory another owns, or a wrapper includes what nobody writes."""
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
    if errors:
        raise SystemExit("sync: the tables disagree:\n  " + "\n  ".join(errors))


def anchors_to_targets(text):
    """A line that is only an id anchor, <a id="x"></a>, becomes the MyST target (x)=: on GitHub the anchor
    keeps an old heading's id on a landing page without showing anything; here the target does the same and
    lets this site's links to page.md#x resolve, which a raw HTML id does not. Fenced code is left alone."""
    out, fenced = [], False
    for line in text.split("\n"):
        if FENCE.match(line.lstrip()):
            fenced = not fenced
        m = None if fenced else ANCHOR.match(line)
        if not fenced and not m and re.search(r"<a\s", line, re.IGNORECASE):
            sys.exit(f"sync: a raw <a> that is not a line of its own reading exactly <a id=\"lower-case-id\"></a>: "
                     f"{line.strip()!r}. Only that form keeps an anchor here; write it so.")
        out.append(f"({m.group(1)})=" if m else line)
    return "\n".join(out)


ANCHOR = re.compile(r'^<a id="([a-z0-9-]+)"></a>$')
ALERT = re.compile(r"^(\s*)> \[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]$")


def alerts_to_admonitions(text):
    """A GitHub alert, a blockquote whose first line is exactly `> [!NOTE]` (or TIP, IMPORTANT, WARNING,
    CAUTION), becomes the MyST admonition of the same kind: `:::{note}`, the quoted lines without their `> `,
    then `:::`. A line right after the quote without its `> ` stops the sync. The fence is longer than any
    run of colons the body starts a line with. An indented alert (in a list item) keeps its indentation on
    every line. A plain blockquote stays one. Fenced code is left alone."""
    lines, out, fenced, i = text.split("\n"), [], False, 0
    while i < len(lines):
        line = lines[i]
        if FENCE.match(line.lstrip()):
            fenced = not fenced
        m = None if fenced else ALERT.match(line)
        if not m:
            out.append(line)
            i += 1
            continue
        indent, kind = m.group(1), m.group(2).lower()
        body, i = [], i + 1
        while i < len(lines) and (lines[i] == f"{indent}>" or lines[i].startswith(f"{indent}> ")):
            body.append(lines[i][len(indent) + 2:])
            i += 1
        if i < len(lines) and lines[i].strip():
            # On GitHub a line right after a quote, without its "> ", still belongs to it (a lazy continuation).
            raise SystemExit(f"sync: the line after a > [!{m.group(2)}] alert has no '> ': {lines[i].strip()!r}. "
                             f"Give it its '> ', or a blank line before it, where it is written.")
        runs = [len(r) for b in body for r in re.findall(r"^\s*(:{3,})", b)]
        fence = ":" * max([3, *(n + 1 for n in runs)])
        out.append(f"{indent}{fence}{{{kind}}}")
        out += [f"{indent}{b}" if b else "" for b in body]
        out.append(f"{indent}{fence}")
    return "\n".join(out)


def toctree(dest, repo=None):
    """The hidden toctree TOCTREES gives the page `dest`, as Markdown to append, or nothing."""
    entries = (repo or TEST_DESIGNS).TOCTREES.get(dest)
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
        for src, dest in repo.PAGES.items():
            targets[(repo.name, src)] = (dest, None)
        for (src, heading), (_, page) in repo.SECTIONS.items():
            targets.setdefault((repo.name, src), (page, set()))[1].add(slug(heading))
        for src, dest in repo.ALSO_HERE.items():
            targets.setdefault((repo.name, src), (dest, set()))
    return targets


def published_dests():
    """Every page some row writes here (it counts as here before it is on disk)."""
    return {d for repo in REPOS.values() for d in [*repo.PAGES.values(), *(w.dest for w in repo.WRAPPERS)]}


def in_site(name, path, fragment):
    """The page here a link to `path` of repository `name` goes to, or None."""
    hit = link_targets().get((name, path))
    if hit:
        dest, fragments = hit
        if not fragment or fragments is None or fragment in fragments:
            return dest
    return None


def github_target(target):
    """(repository name, path, fragment) of a GitHub blob URL into a repository in REPOS, or None."""
    m = GITHUB_BLOB.match(target)
    if m and m.group(1) in REPOS:
        return m.group(1), m.group(3), m.group(4) or ""
    return None


OWN_LINK = re.compile(r"(?<=\]\()" + re.escape(PUBLISHED) + r"([^)\s#?]+)\.html(#[^)\s]*)?(?=\))")
ABS_LINK = re.compile(r"(?<=\]\()(https://github\.com/[^)\s]+)(?=\))")


def lines_outside_code(text, fn):
    out, fenced = [], False
    for number, line in enumerate(text.split("\n"), 1):
        if FENCE.match(line.lstrip()):
            fenced = not fenced
        out.append(line if fenced else fn(line, number))
    return "\n".join(out)


def own_links(text, titles=None, where="", notes=None):
    """A copied Markdown file's links to pages of this site, as links inside the site.

    Such a file is included by pages at any depth, so the link is written from the source root
    (`/verify/fpgas-verify.md#heading`), which MyST resolves wherever the including page is. The build then
    checks the page and the heading; by its published address the link check would test it against what is
    published, where a heading's address is not the one MyST knows it by and a new page is not there yet.
    A page this run writes counts as here, though it is not on disk yet (FILES are written before PAGES).
    A GitHub URL to a file another row publishes here goes to that page the same way. A link to a page that
    is not in this repository is left as it is. Fenced code is left alone."""

    def one(match):
        page, fragment = match.group(1), match.group(2) or ""
        here = (DOCS / "docs" / f"{page}.md").exists() or f"docs/{page}.md" in published_dests()
        return f"/{page}.md{fragment}" if here else match.group(0)

    def github(match):
        hit = github_target(match.group(1))
        dest = hit and in_site(*hit)
        if not dest:
            return match.group(0)
        return "/" + dest.removeprefix("docs/") + (f"#{hit[2]}" if hit[2] else "")

    def line_fn(line, number):
        if titles:
            line = relabel(line, lambda t: absolute_file(t), titles, f"{where}:{number}", notes)
        return ABS_LINK.sub(github, OWN_LINK.sub(one, line))

    return lines_outside_code(text, line_fn)


def absolute_file(target):
    """(repository, path) a link target names by its GitHub URL, or None."""
    hit = github_target(target)
    return hit and hit[:2]


def relabel(line, locate, titles, where, notes):
    """Give each link whose text is a file name the title of the page it points at. locate(target) says which
    (repository, path) the target is, or None; titles(repository, path) reads its title, or None."""

    def one(match):
        tick, label, target = match.groups()
        found = locate(target)
        if not found:
            reason = "it does not point at a file of a repository this tool reads"
        elif not found[1].endswith(".md"):
            reason = "it does not point at a Markdown file"
        else:
            title = titles(*found)
            if title and "[" not in title and "]" not in title:
                return f"[{title}]({target})"
            reason = f"the title of {found[0]} {found[1]} could not be read"
        if notes is not None:
            notes.append(f"{where}: label [{tick}{label}{tick}] left as it is: {reason}")
        return match.group(0)

    return FILE_LABEL.sub(one, line)


def rewrite_links(text, src, at, ref, own_fragments=None, repo="test-designs", titles=None, notes=None):
    """Rewrite the relative links of the Markdown document src of `repo` so they work from the page `at` here.

    `at` is the page a reader sees the text on: the destination for a page, and for a section the page
    that includes it (Sphinx resolves the links of an included file from the including page; checked by
    building, 2026-10-05). own_fragments is given for a section: the anchors inside it; a "#fragment"
    link to any other heading of the source goes to the source on GitHub. titles, when given, reads the title
    of a page for a link whose text is a file name (relabel). Fenced code is left alone."""
    full = REPOS[repo].full if repo in REPOS else f"{ORG}/fpgas.online-{repo}"

    def github(path, fragment):
        kind = "tree" if path.endswith("/") or "." not in posixpath.basename(path) else "blob"
        return f"https://github.com/{full}/{kind}/{ref}/{path.rstrip('/')}" + (f"#{fragment}" if fragment else "")

    def here(dest, fragment):
        return posixpath.relpath(dest, posixpath.dirname(at)) + (f"#{fragment}" if fragment else "")

    def resolve(path):
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(src), path))
        if resolved.startswith(".."):
            raise SystemExit(f"sync: {repo} {src} links outside the repository: {path}")
        return resolved

    def locate(target):
        if target.startswith(PUBLISHED) or target.startswith("#"):
            return None
        if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target):
            return absolute_file(target)
        return repo, resolve(target.partition("#")[0])

    def one(match):
        target = match.group(1)
        if target.startswith(PUBLISHED):
            # A link to a page of this site, written in the source by its published address: here it is a link
            # inside the site, which the build checks. (By its address it would be checked against what is
            # published, and a page added in the same change is not published yet.)
            page, _, fragment = target[len(PUBLISHED) :].partition("#")
            dest = "docs/" + page.removesuffix(".html") + ".md"
            if page.endswith(".html") and ((DOCS / dest).exists() or dest in published_dests()):
                return here(dest, fragment)
            return target
        if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target):
            hit = github_target(target)
            dest = hit and in_site(*hit)
            return here(dest, hit[2]) if dest else target
        path, _, fragment = target.partition("#")
        if not path:
            if own_fragments is None or fragment in own_fragments:
                return target
            return github(src, fragment)
        resolved = resolve(path)
        if path.endswith("/"):
            resolved += "/"
        dest = in_site(repo, resolved, fragment)
        return here(dest, fragment) if dest else github(resolved, fragment)

    def line_fn(line, number):
        for what, pattern in UNSUPPORTED.items():
            if pattern.search(line):
                raise SystemExit(f"sync: {repo} {src}:{number}: {what}, which rewrite_links does not handle. "
                                 f"Teach it to, or write the link inline in {repo}.")
        if titles:
            line = relabel(line, locate, titles, f"{at} ({repo} {src}:{number})", notes)
        return LINK.sub(one, line)

    return lines_outside_code(text, line_fn)


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


def title_of(text):
    """The first "# " heading of a Markdown text, outside fenced code, or None."""
    fenced = False
    for line in text.split("\n"):
        if FENCE.match(line.lstrip()):
            fenced = not fenced
        elif not fenced and line.startswith("# "):
            return line[2:].strip()
    return None


def marker(repo, src, what):
    return (f"% {what} is copied from https://github.com/{repo.full}/blob/main/{src}\n"
            f"% by tools/sync_repos.py. Do not edit it here: change it in {repo.name}.\n\n")


def wrapper_marker(repo):
    return (f"% This page is generated by tools/sync_repos.py from its row in WRAPPERS ({repo.name}), from files\n"
            f"% of https://github.com/{repo.full}. Do not edit it here: change the row, or those files.\n\n")


def wrapper_text(repo, w, lead):
    """The page a WRAPPERS row makes, given its lead's text (already link-rewritten), or None."""
    blocks = [f"# {w.title}"]
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
    return wrapper_marker(repo) + "\n\n".join(blocks) + "\n"


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
        raise SystemExit(f"sync: {full} has no branch {ref!r}")
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
    """Reads the title of a file for relabel: a page this tool publishes has its own title (as this run
    writes it, or as it is on disk); any other Markdown file its title at the commit its repository is
    synced from in this run, or at that repository's main."""

    def __init__(self, commits, page_titles):
        self.commits, self.page_titles, self.cache = dict(commits), page_titles, {}

    def __call__(self, name, path):
        dest = in_site(name, path, "")
        if dest:
            if dest in self.page_titles:
                return self.page_titles[dest]
            return title_of((DOCS / dest).read_text()) if (DOCS / dest).exists() else None
        if (name, path) not in self.cache:
            full = REPOS[name].full
            if name not in self.commits:
                self.commits[name] = resolve(full, "main")
            try:
                self.cache[(name, path)] = title_of(fetch(full, self.commits[name], path).decode("utf-8"))
            except Missing:
                self.cache[(name, path)] = None
        return self.cache[(name, path)]


def take(repo, ref, commit, titles_for, notes):
    """{path here: bytes} for everything `repo` publishes, and [what is missing]. titles_for(page_titles)
    gives the title reader once the pages' own titles are known."""
    wanted, missing = {}, []
    texts = {}
    for src in sorted({*repo.PAGES, *(s for s, _ in repo.SECTIONS), *repo.lead_sources()}):
        try:
            texts[src] = fetch(repo.full, commit, src).decode("utf-8")
        except Missing as e:
            missing.append(str(e))
    page_titles = {dest: title_of(texts[src]) for src, dest in repo.PAGES.items() if src in texts}
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
                data = own_links(data.decode("utf-8"), titles, f"{dest}/{name}", notes).encode("utf-8")
            wanted[DOCS / dest / name] = data
    for src, dest in repo.PAGES.items():
        if src in texts:
            body = rewrite_links(texts[src], src, dest, ref, repo=repo.name, titles=titles, notes=notes)
            body = anchors_to_targets(alerts_to_admonitions(body))
            wanted[DOCS / dest] = (marker(repo, src, "This page") + body + toctree(dest, repo)).encode("utf-8")
    for (src, heading), (dest, page) in repo.SECTIONS.items():
        if src in texts:
            try:
                part = section(texts[src], heading, src)
            except Missing as e:
                missing.append(str(e))
                continue
            body = alerts_to_admonitions(rewrite_links(part, src, page, ref, own_fragments=fragments_in(part),
                                                       repo=repo.name, titles=titles, notes=notes))
            wanted[DOCS / dest] = (marker(repo, src, f'This section ("{heading}")') + body).encode("utf-8")
    for w in repo.WRAPPERS:
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
            lead = alerts_to_admonitions(rewrite_links(body, w.lead.path, w.dest, ref,
                                                       own_fragments=fragments_in(body), repo=repo.name,
                                                       titles=titles, notes=notes))
        for inc in w.includes:
            if inc.docs_owned and not (DOCS / inc.path).is_file():
                raise SystemExit(f"sync: {w.dest} includes {inc.path}, the docs' own file, which does not exist")
        wanted[DOCS / w.dest] = wrapper_text(repo, w, lead).encode("utf-8")
    return wanted, missing


def changes_for(repo, ref, wanted):
    changes = []
    for path, data in wanted.items():
        if not path.exists() or path.read_bytes() != data:
            changes.append(("update" if path.exists() else "add", path))
    for dest in repo.owned_dirs():
        d = DOCS / dest
        if d.exists():
            for p in sorted(d.iterdir()):
                if p.name != SOURCE and p not in wanted:
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
    check_tables()

    plan, commits = [], {}
    for name in names:
        repo = REPOS[name]
        if repo.empty():
            print(f"{repo.full}: nothing listed")
            continue
        ref = args.ref or "main"
        commits[name] = resolve(repo.full, ref)
        print(f"{repo.full} {ref} = {commits[name]}")
        plan.append((repo, ref))

    notes, failed, all_changes = [], False, []
    for repo, ref in plan:
        commit = commits[repo.name]
        wanted, missing = take(repo, ref, commit, lambda pt: Titles(commits, pt), notes)
        if missing:
            failed = True
            print(f"\nsync: FAILED. {repo.full} at {commit[:12]} ({ref}) does not have:", file=sys.stderr)
            for m in missing:
                print(f"  {m}", file=sys.stderr)
            print(f"It was moved, renamed or removed there (or never added). Update the {repo.name} tables in "
                  "tools/sync_repos.py to match what it has.", file=sys.stderr)
            continue
        all_changes.append((repo, ref, commit, wanted, changes_for(repo, ref, wanted)))
    for note in notes:
        print(f"  note   {note}")
    if failed:
        return 2

    total = 0
    for repo, ref, commit, wanted, changes in all_changes:
        for what, path in changes:
            print(f"  {what:6} {path.relative_to(DOCS)}")
        total += len(changes)
    if not total:
        print("up to date")
        return 0
    if args.check:
        return 1
    for repo, ref, commit, wanted, changes in all_changes:
        for what, path in changes:
            if what == "remove":
                if not path.is_file():
                    raise SystemExit(f"sync: {path.relative_to(DOCS)} is not a file. The directories this tool "
                                     f"owns hold only what it writes; move it out.")
                path.unlink()
            elif what != "source":  # SOURCE is rewritten below
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(wanted[path])
        if changes:
            # SOURCE moves only with the files or the ref, so a new upstream commit alone changes nothing
            for dest in repo.owned_dirs():
                (DOCS / dest).mkdir(parents=True, exist_ok=True)
                (DOCS / dest / SOURCE).write_text(source_text(repo, ref, commit))
    print(f"{total} file(s) changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
