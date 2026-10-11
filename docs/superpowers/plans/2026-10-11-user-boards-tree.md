# The User boards tree: implementation plan

> **For agentic workers:** this plan is carried out by the docs lane, one pull request per task, each through the
> gate (independent Sonnet review hunting shortcuts, CI on a head that contains main, the coordinator's word). Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** a boards tree under User documentation for a visitor who uses a board from the website. The admin board
trees keep set-up, wiring and checks. The two trees link each other. (Tim, 11 Oct 2026, coord-53: "The user pages
probably need their own boards tree which is focused about using the boards, not admin tasks related to the boards.
The two trees can be cross linked.")

**Architecture:** the welland and ps1 board pages are one template for every board type (fpgas.online-site
`pibfpgas/src/pibfpgas/templates/fpga.html`), so the parts of that page get shared pages, written once. Each board
then gets a short page on what it offers and a how-to for loading a design and seeing it run. The Tiny Tapeout site
is a different page (the Commander, the bundled designs, the upload), so its two board kinds get their own pages.
Every fact comes from the site repository, the live pages, the Tiny Tapeout repositories or the existing board trees,
with the source named in the pull request. Nothing is invented. Where no source states a fact, the page leaves it out,
and an issue says what would settle it.

**Sources:** a Sonnet researcher's report of 11 Oct 2026 (in this session). It read fpgas.online-site (templates,
`pibup`, `pistat`, `ttsite`, `static`), fpgas.online-tt, tt-commander-app (branch `fpgas-online`),
tinytapeout-fpga-demos, fpgas.online-cam, the infra roles, and the live pages of welland, ps1 and Tiny Tapeout. Each
page's pull request quotes its sources again, read at that time.

---

## The tree

```
User documentation
├── Sites                                   (exists)
├── Roadmap                                 (exists)
├── How to reach a board with your own ssh client   (exists, docs #167)
├── How to log in to a host at ps1          (exists)
└── Boards                                  user/boards/index.md        landing
    ├── The board page on welland and ps1   user/boards/board-page.md   reference
    ├── How to reset a board                user/boards/reset.md        how-to
    ├── The camera on a board               user/boards/camera.md       explanation
    ├── Acorn                               user/boards/acorn/index.md  landing
    │   ├── An Acorn on fpgas.online        user/boards/acorn/about.md  explanation
    │   └── How to load a design onto an Acorn from its board page      user/boards/acorn/load.md  how-to
    ├── Tiny Tapeout FPGA demo board        user/boards/tt-fpga/index.md
    │   ├── A Tiny Tapeout FPGA demo board on fpgas.online   about.md   explanation
    │   ├── How to run a bundled design     run-design.md               how-to
    │   ├── How to load your own bitstream  own-bitstream.md            how-to
    │   └── The bundled designs             designs.md                  reference (title, inputs, clock, source path)
    ├── NeTV2                               user/boards/netv2/          about.md, load.md
    ├── Fomu EVT                            user/boards/fomu-evt/       about.md, load.md
    ├── Arty A7                             user/boards/arty-a7/        about.md, load.md (not in service: the issue on the page)
    └── Tiny Tapeout chip demo boards       user/boards/tt-asic/        about.md, select-design.md (how-to)
```

The landing `user/boards/index.md` gives one line per board in this order: Acorn, Tiny Tapeout FPGA, NeTV2, Fomu,
then Arty A7 and the Tiny Tapeout chip boards. Each line says where the board is used (welland.fpgas.online,
tinytapeout.fpgas.online). The order is the coordinator's: the boards a visitor can use today first. Which boards can be
used at a given moment is not typed into any page: the landing points at the live lists (welland's `/fpgas/`, the Tiny
Tapeout index), because the boot check is the authority on what is connected and a typed list would drift. (For this
plan only: the welland list of 11 Oct 2026 showed Acorn, NeTV2, Fomu EVT and TT FPGA; Arty A7 is not in service, infra
#125 and #272.)

## What each page holds, and its source

**The board page on welland and ps1** (reference; a table, one row per part, three columns: part, what it does,
what to know). Rows: the list page and how a board gets onto it (listed only while its check passes); the terminal
(wssh, logged in as `pi`, a shared tmux session group, so another visitor may be typing); "reset ssh", "ping",
"reconnect", "reset video player"; the status box; "Check PoE"; Upload (into `/home/pi/Uploads/<name>`, an existing
file overwritten, 64 MB on welland, the failure messages); "Accessing directly" (links the ssh how-to); the Demo
buttons; "Useful links". Sources: `fpga.html`, `dcws.js`, `pibup/views.py`, `pibup/templates/*`, infra
`roles/site/defaults/main.yml`. The ps1 differences (older code: no low-latency view, no `-4`) go in a column or a
second short table. Whatever a visitor writes is gone at the next reset (`sites/welland.md`, the NFS root).

**How to reset a board** (how-to): the Reset button, what it does (PoE off and on, the host reboots, everything
written is gone, anyone's session ends), how long (about two minutes, more than 90 s on a Pi 5), "Check PoE" and the
status box as the check, the rate limit (HTTP 429 with `Retry-After`; the deployed value is not stated, so no number).
The Tiny Tapeout site's "Power-cycle board" button with its confirm dialog. Sources: `dcws.js`, `pibfpgas/poe.py`,
fpgas.online-poe README, `pibup/views.py`, `ttsite/.../board.js`.

**The camera on a board** (explanation): the live view and the HLS fallback, "rewind" and "live", "no picture", 6 fps,
the `vlc https://<site>/live/<host>.m3u8` line for a player outside the page; what the camera points at (the LEDs over
an Acorn; the NeTV2 hosts with an HDMI grabber show the board's HDMI picture, not a camera). Fomu: no source found, so
the page says nothing about it, and an issue asks. Sources: `whep-live.js`, `no-picture.js`, fpgas.online-cam
`docs/camera.md` and `gst-libcam.sh`, `boards/acorn/overview/camera.md`.

**An <board> on fpgas.online** (explanation, per board): what the board is (one paragraph from its admin overview),
which site has it, what the page offers it (the shared page), which test bitstreams are on the host
(`/usr/share/fpgas-online/<board>/bitstreams/`, test-designs `docs/verify/installing.md`), what is planned with
issues (from the site page), and the line "Setting one up: <admin tree landing>".

**How to load a design onto an <board> from its board page** (how-to, per welland board): choose the board on the list
by its label; upload the file; in the terminal, the board's load command from its admin how-to:
- Acorn: detach the endpoint, link `gpiochip0`, `openFPGALoader --cable libgpiod --pins 10:9:11:8 Uploads/<file>.bit`,
  the `done 1` line (docs #187), the rescan. The detach step is on the page itself, with the commands of the admin
  how-to, and so is what happens without it: reconfiguring the FPGA while its endpoint is enumerated crashes the Pi 5's
  root complex, and the host needs a Reset (`acorn/checks/jtag-by-hand.md`, `acorn/checks/jtag-and-the-pcie-endpoint.md`).
  Neither is left to a link.
- NeTV2: the Pi 3B+ and Pi 5 commands, with the slot gate (docs #186). The host's Pi model is shown how? Not found: the
  page says how to tell (`cat /proc/device-tree/model`), an observation the reader makes.
- Fomu: `openFPGALoader -b fomu Uploads/<file>.bin` inside the bootloader's window; Reset restarts the window
  (`fomu-evt/setup/load-design.md`).
- Arty A7: `openFPGALoader -b arty Uploads/<file>.bit` (`arty-a7/setup/load-design.md`).
Then see it run: the camera, or the serial port where the board has one. Never a flash write from a visitor page. Each
step and check is taken from the admin how-to it names, and every step is on the page itself: the detach, the
`gpiochip0` link, the load line, the `done 1` check, the rescan. Only the failure tables may be a link to the admin
how-to (Tim, 5 Oct 2026: steps complete in place; the reader never leaves the page mid-procedure).

**Tiny Tapeout FPGA** (on tinytapeout.fpgas.online):
- *about*: the board (iCE40UP5K on the demo board v3, RP2350), the page (status pill, camera, status log, Commander,
  "Designs on this board", upload, "About this board"); everyone drives the same board; nothing is written to the board,
  a design is streamed.
- *run-design* (how-to): pick "Run" on a bundled design, see "Loading …" then "… is running", then drive it from the
  Commander's Interact tab. The 25 s load deadline, the `409` and `503` messages (fpgas.online-tt README).
- *own-bitstream* (how-to): build with the FabricFox flow (yosys, `nextpnr-ice40 --up5k --package sg48`, `icepack`, top
  `tt_fpga_top`), name `[a-z0-9_]{1,40}`, a `.bin` of at most 256 KiB, "Upload & load"; 16 uploads kept; lost at the
  Pi's reboot. Sources: `ttsite` `board.html`, `board.js`, `daemon.py`, `views.py`; fpgas.online-tt README.
- *designs* (reference, generated where the data allows): the five bundled designs, with title, inputs, default
  clock and source path in fpgas-online/tinytapeout-fpga-demos (`demos/<name>/info.yaml`, `docs/info.md`). If the data
  is in `info.yaml`, the table is generated by `tools/sync_repos.py` from that repository (rule: a reference page is not
  typed by hand when the data exists). The generator is a separate task (below).

**Tiny Tapeout chip boards**: *about* (the shuttles, the RP2040/RP2350 controller, the Commander, the safe idle state)
and *select-design* (how-to: Config tab, project, clock, "Select", then Interact). Sources: tt-commander-app
`BoardConfigPanel.tsx`, `InteractPanel.tsx`, `README.fpgas-online.md`; fpgas.online-tt README. Only connected boards
can be used; the page says "the index shows which are connected", not a list.

## Cross-links

- Each user board landing links its admin landing: "Setting one up: [<board>](../../boards/<board>/index.md)".
- Each admin landing (`docs/boards/<board>/index.md`) gets one line: "Using this board on fpgas.online:
  [<board> on fpgas.online](../../user/boards/<board>/index.md)". The Acorn and TT FPGA admin landings are
  docs-owned; any admin page copied from test-designs gets its line through test-designs, not here.
- `docs/index.md` "I want to" gains "Use a board from a website: [Boards](user/boards/index.md)". User documentation's
  landing gains the Boards line.

## Issues to file before writing (fpgas-online repositories only)

1. fpgas.online-site #104 (filed): the four Demo buttons are on every board page but run `openFPGALoader -b arty`. On an Acorn,
   NeTV2 or Fomu they can only fail, and whether `~/Demos` and `~/ci/t1` exist on a welland host is not found. Proposed fix (the
   coordinator's): shown only where the host's boot-check report says Arty, else hidden. Site work for later. The user page describes them as the Arty's, with the issue.
2. fpgas.online-site #105 (filed): "Useful links" on every board page are Arty and F4PGA only, two of them with empty `href`s, and
   the list page says "Arty FPGA access system" and "~10 FPGAs boards". Proposed fix (the coordinator's): per board type,
   the links point at the user boards pages on docs.fpgas.online, and the list page's text stops saying Arty and "~10
   FPGAs boards". Site work for later.
3. fpgas.online-docs #188 (filed): screenshots of the welland board page, the Tiny Tapeout board page and the Commander tabs. Each
   page that needs one carries a placeholder naming this issue.
4. fpgas.online-docs #189 (filed): what the Fomu's camera shows, and which NeTV2 hosts have a camera and which a grabber.
5. Settled before the NeTV2 load page: is a visitor told the host's Pi model, or do they read it
   (`/proc/device-tree/model`)? The page uses the reading unless a source says otherwise.

## Tasks, one pull request each

### Task 1: the landing, the three shared pages and the cross-links
- [ ] Files: `docs/user/boards/index.md`, `board-page.md`, `reset.md`, `camera.md`; `docs/user/index.md` (the Boards
      line and toctree); `docs/index.md` (the "I want to" line).
- [ ] Each fact from its source, read at the time, quoted in the pull request's table.
- [ ] Build `-W -j auto`, tests, linter on each page; review (Sonnet, briefed as the visitor, hunting shortcuts);
      CI; the coordinator's word.

### Task 2: Acorn (about, load) and the Acorn admin landing's line
### Task 3: Tiny Tapeout FPGA (about, run-design, own-bitstream, designs) and its admin landing's line
- [ ] The designs table is generated from tinytapeout-fpga-demos' `demos/*/info.yaml` by `tools/sync_repos.py`, with a
      test (the coordinator's decision, 11 Oct 2026: typed copies of data that exists are what rule 14 forbids). The
      generator is part of this task's pull request.
### Task 4: NeTV2 and Fomu EVT (about, load each) and their admin landings' lines
### Task 5: Arty A7 and the Tiny Tapeout chip boards, and their admin landings' lines

Each task: the review brief names the visitor as the reader, lists the sources, and asks the reviewer to compare every
command with the admin how-to it comes from. A command that differs from its source is a finding.

## Not in this plan

- This plan file is not published: `docs/conf.py` excludes `superpowers` from the build, and no toctree names it.

- Screenshots and photos (issue 3): pages carry placeholders naming the issue.
- Changes to the site itself (issues 1 and 2): the docs describe the site as it is.
- The admin trees' own content.
