# Design: Port repo documentation into docs.fpgas.online

**Date**: 2026-09-03
**Status**: Draft
**Author**: Tim Ansell + Claude

## Summary

Move the operator and hardware documentation that currently lives in the
`fpgas.online-test-designs`, `fpgas.online-infra`, `fpgas.online-site`,
`fpgas.online-tt`, `tinytapeout-fpga-demos` and `fpgas.online-setup-pi`
repositories into the `fpgas.online-docs` Sphinx site published at
<https://docs.fpgas.online>, restructured into three top-level sections:
**Sites**, **Boards** and **Setup**. Developer documentation (how to build a
test design, CI, toolchains) stays in the repository that owns the code.
After each page is ported, the source file is replaced by a stub pointing at
the published page so there is one copy of every fact.

## Background

`fpgas.online-docs` was created on 2026-09-01 with a single commit. It is
Sphinx + MyST (Markdown), Furo theme, `fail_on_warning: true` on Read the Docs
and `sphinx-build -W` in CI. It currently has five pages: a landing page, a
`sites/` section with a Welland and a PS1 page, `packages.md` and
`contributing.md`. The local build with `uv run --no-project
--with-requirements docs/requirements.txt sphinx-build -b html -W docs
docs/_build/html` succeeds.

The existing pages already contain a small amount of wiring knowledge (JTAG
pin orders, the P2 serial crossover, the PS1 CM4/CM5 difference). Everything
else is spread over other repositories. An inventory of every documentation
file in those repositories was taken on 2026-09-03 and is summarised in the
[source inventory](#source-inventory) below.

The `fpgas.online-test-designs` repository holds by far the most: 21
Markdown files under `docs/hardware/` (about 6,000 lines, plus two wiring
images, a Makefile and two data files), of which 12 were edited on
2026-09-03. That directory is the primary source for the Boards and Sites
sections. Its `docs/tests/`, `docs/toolchains/`, `docs/plans/` and
`designs/*/README.md` files are developer documentation and are not ported.

`fpgas.online-infra` holds the netboot and network knowledge: the README,
CLAUDE.md, three runbooks, one hardware document, two design specs that
describe live behaviour (VLAN-per-port addressing, the Tiny Tapeout stack),
and a rebuild log. That is the primary source for the Setup section.

## Goals

1. A reader who has to wire up, fix or extend a board at either site can find
   every fact they need on docs.fpgas.online without opening a repository.
2. Each fact lives in exactly one place. Ported source files become stubs.
3. The three sections the user asked for exist with the content listed under
   [Information architecture](#information-architecture): Sites, Boards (with
   wiring for each device), Setup (nfsroot, web app, what runs on the Pi).
4. The site keeps building with warnings as errors after every commit.
5. Dated measurements keep their dates. Nothing is re-measured as part of
   the port; stale sections are marked, not silently refreshed.

## Non-goals

- Re-probing hardware, resolving open wiring TODOs, or fixing the
  contradictions found in the sources. Those are recorded as `{todo}` items
  on the ported page and tracked separately.
- Porting implementation plans (`docs/plans/`, `docs/superpowers/plans/`),
  the test-reliability `plan.md`, or the test/toolchain developer docs.
- Porting the QEMU CI test-harness design docs from `fpgas.online-infra`.
  They describe a UEFI/GRUB approach that the current harness does not use.
- Building a generator for per-host inventory. The inventory tables are
  ported as hand-maintained tables with a "probed on" date until a generator
  exists.
- Changing the docs toolchain (theme, extensions, RTD configuration). A
  single site stylesheet for wide tables is the one exception.

## Approaches considered

**A. Mirror the test-designs `docs/hardware/` tree as-is.** Copy the 21 files
into `docs/hardware/` on the docs site and add a toctree. Fast, but the
files mix board wiring with per-host inventory (six board pages carry host
tables), the two NeTV2 files repeat most of each other's tables, and the
netboot and web-app content would still be missing. It does not produce the
three sections requested.

**B. Restructure into Sites / Boards / Setup, one fact per page.**
(Recommended.) Port each source file into the section its content belongs
to, split files that mix concerns, merge the duplicated pairs, and add the
Setup pages from the infra sources. More editing work, but each page has a
single purpose and the site matches how people actually look things up:
"which site", "which board", "how does the platform work".

**C. Aggregate at build time.** Keep the Markdown in the source repositories
and pull them into the docs build with git submodules or `{include}`
directives. Keeps docs next to code, but MyST relative links and heading
anchors break across repository boundaries, Read the Docs needs submodule
access on every build, and the restructuring in B is still needed to get the
requested sections. Rejected.

## Information architecture

The toctree after the port. Files are relative to `docs/` in
`fpgas.online-docs`. Existing files are marked *(exists)*.

```
index.md                         (exists, rewritten: three-section overview)
sites/index.md                   (exists: at-a-glance comparison table)
sites/welland.md                 (exists, extended)
sites/ps1.md                     (exists, extended)
boards/index.md                  board table with per-site counts, planned boards
boards/arty-a7.md                spec + PMOD HAT wiring + verified cable routing
boards/acorn/index.md            spec, compatible variants, programming paths
boards/acorn/wiring.md           P1 JTAG / P2 serial wiring, RPi 5 and Compute Blade variants,
                                 assembly, verification, measured per-host results
boards/acorn/pcie-programming.md PCIe detach rule, prebuilt bitstreams, multiboot, recovery
boards/netv2.md                  spec + JTAG/UART/PCIe wiring (netv2.md and netv2-pin-mapping.md merged)
boards/fomu-evt.md               spec + DFU + pin mapping (with the two open TODOs)
boards/tt-fpga.md                Tiny Tapeout FPGA emulation board: spec, RP2350 bridge,
                                 pin mapping, serial ownership, known workarounds
boards/tt-asic.md                Tiny Tapeout ASIC demo boards (TT03p5 to TT09) as deployed
boards/pmod/index.md             PMOD interface standard (types 1 to 6, I2C extension)
boards/pmod/rpi-hat.md           Digilent PMOD HAT: RPi GPIO to PMOD pin tables
boards/pmod/tinytapeout.md       Tiny Tapeout PMOD layouts and RP2040/RP2350 GPIO maps
boards/pin-id.md                 how wiring is verified: the pin-id design and scanner
setup/index.md                   how the platform fits together (architecture diagram)
setup/netboot.md                 DHCP/TFTP/NFS root chain, overlayroot, how the root is built,
                                 updates need a reboot, stale handles, EEPROM write protect
setup/network.md                 VLAN-per-port scheme (Welland), legacy MAC-table scheme (PS1),
                                 addressing formulas, PoE switches, firewall
setup/pi.md                      what runs on a Pi host: packages, services, model quirks
setup/orange-pi.md               Orange Pi H3 hosts: FEL boot, USB console, board mapping
setup/webapp.md                  the Django site: apps, URLs, deployment on the gateway
setup/tinytapeout.md             the Tiny Tapeout stack: fpgas-tt daemon, demos, Commander, catalogue
setup/gateway.md                 the gateway host: Ansible roles, deploy commands, rebuild lessons
setup/verification.md            deployment checklist, verify_hardware.py, test execution flow
packages.md                      (exists)
contributing.md                  (exists)
```

Rationale for the shape:

- **Sites** carry everything that is true of a place: network, gateway,
  switches, which host has which board, known faults per host. Board pages
  link to the site page for inventory rather than repeating it.
- **Boards** carry everything that is true of a board type regardless of
  where it sits: specifications, wiring to a Raspberry Pi, programming
  methods, verification steps, board-level traps. Where the wiring differs
  by carrier (Acorn on a Pi 5 versus on a Compute Blade), both variants are on
  the board's wiring page, because the reader is holding the board.
- **Setup** carries how the platform works independent of any one board or
  site. It is the section a new operator reads first.
- The PMOD material is an interconnect standard shared by several boards, so
  it gets its own sub-section under Boards rather than being duplicated into
  each board page.

## Source to destination mapping

Every ported source file, what happens to it, and where its content lands.
"Stub" means the source file is replaced by its title and a link to the
published page. "Keep" means the file stays because it is developer
documentation; its links are updated to point at docs.fpgas.online.

### fpgas.online-test-designs (`docs/hardware/`)

| Source | Action | Destination |
|---|---|---|
| `README.md` | stub | `boards/index.md` (board table), `sites/index.md` (site list) |
| `site-welland.md` | stub | `sites/welland.md`: network topology, gateway, host inventory tables, programming methods summary, communication interfaces, test execution flow, disconnected hosts, known issues |
| `site-ps1.md` | stub | `sites/ps1.md`: gateway, RPi inventory, PoE switch port inventory, public web interface |
| `site-welland-pibs.conf`, `site-ps1-pibs.conf` | keep in place | Referenced from the site pages as the historical MAC lookup key. Not ported; they are data files. |
| `arty-a7.md`, `arty-a7-pin-mapping.md` | stub both | `boards/arty-a7.md`. The PMOD HAT port tables that duplicate `rpi-hat-pmod.md` become a link to `boards/pmod/rpi-hat.md`. DDR3, MII and SPI-flash tables appear once. |
| `acorn.md` | stub | `boards/acorn/index.md`. The "Host Inventory" section moves to the two site pages. |
| `acorn-pinmap.md`, the two PNGs, `Makefile` | stub the `.md`; copy the PNGs into `docs/boards/acorn/`; keep the Makefile in test-designs and note the Google Drawings edit links on the page | `boards/acorn/wiring.md` |
| `acorn-pcie-programming.md` | stub | `boards/acorn/pcie-programming.md`. "Current Bitstream State" per-host table moves to `sites/welland.md`. |
| `netv2.md`, `netv2-pin-mapping.md` | stub both | `boards/netv2.md`, one copy of each table |
| `fomu-evt.md`, `fomu-pin-mapping.md` | stub both | `boards/fomu-evt.md`. The two TODOs become `{todo}` directives. "Test Infrastructure Hosts" moves to `sites/welland.md`. |
| `tt-fpga.md`, `tt-fpga-pin-mapping.md` | stub both | `boards/tt-fpga.md`. "Deployment" table moves to `sites/welland.md`. |
| `pmod.md` | stub | `boards/pmod/index.md` |
| `rpi-hat-pmod.md` | stub | `boards/pmod/rpi-hat.md` |
| `pmod-tt.md` | stub | `boards/pmod/tinytapeout.md` |
| `gpio-connectivity-analysis.md` | stub | `boards/pin-id.md` |
| `deployment-checklist.md` | stub | `setup/verification.md`. File paths in the checklist are updated to the new docs pages. |
| `butterstick.md`, `ulx3s.md` | stub | "Planned boards" section of `boards/index.md` (specs only, no wiring exists) |

### fpgas.online-test-designs (other)

| Source | Action | Destination |
|---|---|---|
| `README.md` "Documentation" section | keep, relink | links to docs.fpgas.online |
| `docs/verify-hardware.md` | keep | The stale "Network Topology" section is replaced by a link to `sites/welland.md`. The mechanism sections (pre-test commands, programming commands, PoE reset, TT programming flow) are summarised on `setup/verification.md` with a link back. |
| `docs/tests/*.md`, `docs/toolchains/*.md`, `docs/resources.md`, `docs/plans/*.md`, `plan.md`, `designs/**/README.md` | keep | Developer documentation. Relative links into `docs/hardware/` are updated. |

### fpgas.online-infra

| Source | Action | Destination |
|---|---|---|
| `README.md` architecture, PXE boot chain, package table, roles table, deploy commands | keep, trim | `setup/netboot.md`, `setup/gateway.md`. The README keeps a short overview and links. |
| `CLAUDE.md` "Deployment Targets" | keep | Facts cross-checked into `sites/*.md` |
| `docs/superpowers/specs/2026-08-14-vlan-per-port-network-design.md` | keep (design history) | Addressing formulas, topology and failure modes into `setup/network.md` |
| `docs/superpowers/specs/2026-08-22-tinytapeout-fpgas-online-design.md` | keep (design history) | Architecture into `setup/tinytapeout.md` |
| `docs/superpowers/specs/2026-08-14-vlan-per-port-prototype-runbook.md` | keep (design history) | The isolation-matrix and port-identity checks (stages 7 and 8) become the verification section of `setup/network.md`. The tag gotchas (`pibs` not `pxe`, `nftables` not `firewall`) go on `setup/gateway.md`. |
| `docs/superpowers/specs/2026-08-28-orange-pi-netboot-design.md` | keep (design history) | The shared-root decision and the FEL mechanism into `setup/orange-pi.md`. The open "PC vs PC Plus needs a physical check" question becomes a `{todo}` there. |
| `docs/superpowers/runbooks/2026-08-31-eeprom-write-protect.md` | stub | `setup/netboot.md` section |
| `docs/superpowers/runbooks/2026-08-28-orange-pi-netboot.md` | stub | `setup/orange-pi.md` |
| `docs/superpowers/runbooks/2026-08-23-tweed-web-deploy.md` | stub | `setup/webapp.md` deployment section, `setup/gateway.md` |
| `docs/hardware/2026-08-28-orange-pi-h3-boards.md` | stub | `setup/orange-pi.md` (board mapping table, known issues) |
| `docs/rebuilds/2026-08-25-tweed-rebuild.md` | keep | The stable lessons (BIOS settings, console order, vault path, kernel/initramfs match, running Pis do not see lower-fs changes) are extracted into `setup/gateway.md` and `setup/netboot.md`. The log itself stays; it names credentials patterns and is not for a public site. |
| `notes.txt`, `TECHDEBT.md`, `ansible/roles/*/README.md`, `ansible/roles/*/notes.txt` | keep | Two facts are ported: the `core_freq` / PoE / camera tradeoff (to `setup/pi.md`) and the udev interface-naming history (to `setup/network.md`). The rest is stale tribal knowledge. |
| `docs/superpowers/specs/2026-04-04-qemu-vm-testing-design.md`, `docs/superpowers/plans/*` | keep | Not ported. |

### fpgas.online-site, fpgas.online-tt, tinytapeout-fpga-demos, tt-commander-app, fpgas.online-gw

| Source | Action | Destination |
|---|---|---|
| `fpgas.online-site/README.md` | keep, relink | App list, host routing, URL map and deployment into `setup/webapp.md` |
| `fpgas.online-tt/README.md` | keep | Daemon behaviour, `/dev/ttboard`, WebSocket fan-out, FPGA routes into `setup/tinytapeout.md` |
| `tinytapeout-fpga-demos/README.md` | keep | Demo package and bitstream build flow summarised in `setup/tinytapeout.md`; "Adding a demo" stays in the repo |
| `tt-commander-app/README.fpgas-online.md` | keep | Embedding contract and multi-viewer semantics summarised in `setup/tinytapeout.md` |
| `fpgas.online-gw/README.md` | keep | Mentioned on `setup/webapp.md` as planned; endpoint table is not ported until the `impl-api` branch merges |
| `pibfpgas/templates/index.html`, `tt.html`; `fpgas-online.github.io/site/index.html`; `dot-github/profile/README.md` | relink | Links to the old `CarlFK/pici` wiki and the `fpgas-online.github.io` wiki are replaced with links to docs.fpgas.online pages |

### fpgas.online-setup-pi, fpgas.online-cam, fpgas.online-poe, apt, netboot-pi, tools

| Source | Action | Destination |
|---|---|---|
| `fpgas.online-setup-pi/README.md`, `nfpm.yaml`, unit files | keep | Service table on `setup/pi.md`, with a note on which units the current `onpi` role does not enable |
| `fpgas.online-cam/README.md` | keep | Camera pipeline paragraph on `setup/pi.md` and `setup/webapp.md` |
| `fpgas.online-poe/README.md` | keep | PoE control paragraph on `setup/network.md`; the PS1 private OID stays on `sites/ps1.md` |
| `apt/README.md` | keep | Already covered by `packages.md` |
| `fpgas.online-netboot-pi/*`, `fpgas.online-tools/*` | keep | Named on `setup/netboot.md` as the historical hand-run toolkit that the Ansible roles replaced. Their READMEs get a note saying so. |

## Page conventions

These apply to every ported page and extend `contributing.md`.

- Every measurement, pinout, device ID or fault keeps its original date and
  host. A section whose source predates 2026-08-23 at Welland (the
  VLAN-per-port cutover) gets a `{note}` saying the host names and addresses
  are from the 2026-03-17 survey and have not been re-probed.
- Open questions in the sources become `{todo}` directives so they render
  and are collected by `sphinx.ext.todo`. The list of known ones is in
  [Open items carried into the docs](#open-items-carried-into-the-docs).
- Board pages do not list hosts. They link to the site page section. Site
  pages list hosts in a table with a "Probed YYYY-MM-DD." line directly
  under the section heading. The date is not in the heading itself, because
  MyST derives anchors from headings and a re-probe would break inbound
  links.
- Command blocks use `console` fences with a `$` prompt so `sphinx-copybutton`
  strips the prompt.
- Cross-page links are relative Markdown links with `.md` and, where needed,
  a heading anchor (`myst_heading_anchors = 3`).
- Images live next to the page that uses them.
- Tables wider than the Furo content column scroll horizontally via
  `docs/_static/custom.css` (added during Task 3); do not split a table to
  make it fit.
- Site pages lead with the surprises (wiring, host quirks, traps) and put
  the host inventory tables after them, as `sites/ps1.md` already does.
- Pages record which repository a fact came from only when the reader has to
  go there (for example to run a script). Provenance is otherwise in git.

## Stubbing the sources

After a page is published, the source Markdown file in the owning repository
is replaced by:

```markdown
# <original title>

This page has moved to <https://docs.fpgas.online/<path>/>.
```

Reasons to stub rather than delete: existing external links keep resolving,
GitHub search still finds the title, and `git log --follow` on the stub
reaches the history. Reasons not to leave the full copy: the test-designs
hardware docs are edited most days and two copies would diverge within a
week.

Data files (`site-*-pibs.conf`), images used by developer docs, and the
Google Drawings `Makefile` stay in place.

The stubbing commit in each source repository also fixes every relative link
that pointed at the stubbed file. `sphinx-build -b linkcheck` on the docs
site and a `grep` for `docs/hardware/` across each source repository verify
this.

## Open items carried into the docs

These were found during the inventory. They are recorded on the relevant page
as `{todo}` items rather than resolved by the port.

| Item | Page |
|---|---|
| Orange Pi boards: whether they are PC or PC Plus needs a physical check | `setup/orange-pi.md` |
| `acorn.md`'s DDR3 pin table disagrees with `sqrl_acorn.py` on 11 of 14 rows (16-bit `dq`, not 32; four listed DQ pins belong to SD MOSI, LED 1, PCIe reset, UART TX; `ba`, `ras_n`, `we_n`, `cke`, `reset_n` differ; DM/DQS absent). Found in Task 9 review; recorded as a todo on the page and to be fixed upstream in test-designs. | `boards/acorn/index.md` |
| `acorn.md` lists the CLE-101 package as FBG484; `sqrl_acorn.py` uses fgg484 | `boards/acorn/index.md` |
| `acorn-pinmap.md`'s Compute Blade ASCII header diagram shows the P2 serial pair reversed (TX on GPIO14), contradicting its own tables. Corrected on the docs page during Task 10 with a dated note; fix upstream in test-designs. Both Google Drawings also need redrawing (K2/J2 labels, blade TMS pin). | `boards/acorn/wiring.md` |
| The docs site's 2026-09-01 Welland page recorded the P2 serial pair as straight-through (K2 to GPIO14). The 2026-08-31 pin-ID survey and the 2026-09-03 revision of `acorn-pinmap.md` show the null-modem crossover (K2 to GPIO15) is the fleet standard at both sites. Corrected during Task 3; `sites/ps1.md`'s "opposite of Welland" note is removed in Task 4. | `sites/welland.md`, `sites/index.md`, `sites/ps1.md` |
| Fomu EVT: iCE40 pin to RPi GPIO header mapping for UART and for the GPIO27/GPIO9 loopback pair is undocumented | `boards/fomu-evt.md` |
| Arty A7: only 4 of 8 PMOD loopback lanes verified; JC pins 1 and 2 swapped in the cable on pi9 | `boards/arty-a7.md` |
| Acorn wiring diagram PNGs still show the pre-crossover P2 serial wiring | `boards/acorn/wiring.md` |
| `verify_hardware.py` HOSTS table still has pre-2026-08-23 host names | `setup/verification.md` |
| PS1 switch model: host_vars comments name three candidates (ProCurve 2610, GS728TPP, FS728TPv2); the live OID matches FS728TPv2 | `sites/ps1.md` |
| `slf.sytes.net` is in the Ansible inventory but was unreachable on 2026-08-26 | `setup/gateway.md` |
| Welland host_vars timezone is `America/Los_Angeles` | `sites/welland.md` |
| The `pistat` and `arty-*` units shipped by `fpgas-online-setup-pi` are not enabled by the current `onpi` role | `setup/pi.md` |
| The infra README describes the Pi provisioning container as systemd-nspawn with sshd on port 2200; the role implements a chroot behind an SSH login shell on port 22 | `setup/netboot.md` (documents the real mechanism; the README is corrected in the same change) |
| pi14 and pi16 at PS1 do not answer JTAG on any pin order | `sites/ps1.md` (already present) |
| The TT FPGA `pmod-tt.md` RP2350 table is spec-derived while `tt-fpga-pin-mapping.md` is measured; they agree numerically | `boards/tt-fpga.md` links to `boards/pmod/tinytapeout.md` with a note on provenance |

## Ordering

The port is done page by page, one commit per page, with `sphinx-build -W`
passing after each. Order is chosen so the most-edited and most-linked
sources move first, and so no page links to a page that does not exist yet.

1. **Skeleton.** Add the three section index pages and the toctree entries
   with placeholder pages, rewrite `index.md`. Everything builds. This is the
   only commit that adds pages without content, so links can be written
   forward from here.
2. **Sites.** Extend `sites/welland.md` and `sites/ps1.md` with the
   inventory tables and site-level sections from the two `site-*.md` files
   and the host tables pulled out of the board files. Board pages can now
   link to them.
3. **PMOD sub-section.** `boards/pmod/*` first, since Arty and TT FPGA link
   into it.
4. **Boards.** Acorn (three pages), TT FPGA, TT ASIC, Arty A7, NeTV2,
   Fomu EVT, pin-id, then `boards/index.md` with the table and planned
   boards.
5. **Setup.** netboot, network, pi, orange-pi, gateway, webapp, tinytapeout,
   verification, then `setup/index.md`.
6. **Stub and relink.** One commit per source repository replacing the ported
   files with stubs and fixing links. Then the public-facing link fixes
   (landing page, org profile, Django templates).

Each step is independently shippable. If the port stops after step 4 the
site is still coherent.

## Verification

- `uv run --no-project --with-requirements docs/requirements.txt sphinx-build
  -b html -W --keep-going docs docs/_build/html` passes after every commit.
- `sphinx-build -b linkcheck` is run before the stubbing step and again after;
  the second run must show no new broken internal links.
- A word-level diff (`git diff --no-index --word-diff` between the source
  file and the ported page, ignoring the moved sections) is checked for each
  board and site page to confirm no table rows or measured values were lost
  or altered. The check is recorded in the commit message.
- After step 6, `grep -r "docs/hardware/" --include=*.md` in
  `fpgas.online-test-designs` returns only the stubs and the data files, and
  `grep -r "pici/wiki\|github.io/wiki"` across the site, landing page and
  org profile repositories returns nothing.
- Read the Docs builds `main` successfully and docs.fpgas.online shows the
  new toctree.

## Source inventory

Taken 2026-09-03 against `origin/main` of each repository. Line counts are
from `wc -l`.

| Repository | Files | Lines | Ported |
|---|---|---|---|
| `fpgas.online-test-designs/docs/hardware/` | 21 Markdown, 2 images, 1 Makefile, 2 data files | about 6,000 | all 21 Markdown files; images copied; Makefile and data files stay |
| `fpgas.online-test-designs` (README, tests, toolchains, plans, designs READMEs, `verify-hardware.md`, `resources.md`, `plan.md`) | 30 | about 8,900 | none; links updated, one section replaced |
| `fpgas.online-infra` (README, CLAUDE.md, notes, TECHDEBT, role READMEs and notes) | 11 | about 800 | selected facts |
| `fpgas.online-infra/docs/` (specs, runbooks, rebuild log, hardware, plans) | 14 | about 7,400 | 4 files ported, 4 specs summarised, rest kept |
| `fpgas.online-site` | 9 | about 400 | README summarised, 2 stub READMEs left alone |
| `fpgas.online-tt`, `tinytapeout-fpga-demos`, `tt-commander-app`, `fpgas.online-gw` | 8 | about 600 | summarised |
| `fpgas.online-setup-pi`, `fpgas.online-cam`, `fpgas.online-poe`, `apt`, `netboot-pi`, `tools` | 14 | about 700 | service table and two paragraphs |
| `fpgas-online.github.io`, `.github` profile, `website` | 4 | about 470 | links only |

## Decisions made during design

Recorded so they can be revisited.

- **Per-host inventory goes on the site pages.** `contributing.md` says to
  link to a generator instead, but no generator exists and the tables are
  the most-consulted content in the sources. They are ported as dated tables.
- **Stub, do not delete.** See [Stubbing the sources](#stubbing-the-sources).
- **Acorn gets three pages.** The single 601-line `acorn-pinmap.md` mixes
  spec, wiring, Compute Blade variant and PCIe programming; readers land on
  it for different reasons.
- **Tiny Tapeout ASIC boards get a board page** even though no wiring file
  exists for them today. The page collects what the Welland site file, the
  Tiny Tapeout PMOD file and the infra `tt_boards` catalogue say, so the
  Boards section covers every device type that is live.
- **Orange Pi H3 hosts go under Setup, not Boards.** They are hosts, not
  FPGAs.
- **The tests, toolchains and designs documentation stays in
  test-designs.** It is about building the repository's own code.
- **Nothing is re-measured.** Dates are preserved and stale sections marked.
