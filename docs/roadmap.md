---
type: explanation
owner: documentation maintainers
reader: someone who wants to know what fpgas.online plans, beyond one site
review: 2026-11-10
---

# Roadmap

This page says what is planned across fpgas.online, beyond what one site plans. It is for someone deciding
whether to wait for something. It gives no dates.

Each line is one planned thing and the issue or pull request
that tracks it. A thing leaves this page once it is in service. What one site plans is on that site's page,
under [Sites](sites/index.md).

## Boards and designs

- More board types, such as ButterStick and ULX3S: [test-designs issue #225](https://github.com/fpgas-online/fpgas.online-test-designs/issues/225).
- More Fomu hosts: [infra issue #280](https://github.com/fpgas-online/fpgas.online-infra/issues/280).
- HDMI, HDCP and USB on the NeTV2 boards: [test-designs issue #234](https://github.com/fpgas-online/fpgas.online-test-designs/issues/234).
- Designs to use from a board's page, with nothing to build: [test-designs issue #236](https://github.com/fpgas-online/fpgas.online-test-designs/issues/236).
- A check for other PCIe Xilinx cards: [test-designs issue #238](https://github.com/fpgas-online/fpgas.online-test-designs/issues/238).

## The check of each board

- A full test design for every board type, with every function checked at boot: [test-designs issue #87](https://github.com/fpgas-online/fpgas.online-test-designs/issues/87), with [#89](https://github.com/fpgas-online/fpgas.online-test-designs/issues/89) and [#90](https://github.com/fpgas-online/fpgas.online-test-designs/issues/90).
- Every GPIO pin checked in both directions: [test-designs issue #271](https://github.com/fpgas-online/fpgas.online-test-designs/issues/271).
- Transfer rates measured against expected figures, for DDR, PCIe and Ethernet: [test-designs issue #274](https://github.com/fpgas-online/fpgas.online-test-designs/issues/274).
- On the Arty A7 and the NeTV2, the flash checked against the golden full test design: [test-designs issue #275](https://github.com/fpgas-online/fpgas.online-test-designs/issues/275). Flash a user changed is restored: [test-designs issue #68](https://github.com/fpgas-online/fpgas.online-test-designs/issues/68). A tool writes the golden design to the flash of an Arty A7, NeTV2 or Fomu: [test-designs issue #278](https://github.com/fpgas-online/fpgas.online-test-designs/issues/278).
- The flash's identifiers read on every board, and everything a board can report sent with its labels: [test-designs issue #26](https://github.com/fpgas-online/fpgas.online-test-designs/issues/26) and [test-designs issue #76](https://github.com/fpgas-online/fpgas.online-test-designs/issues/76).
- What a board reports compared with the site's records of it: [test-designs issue #276](https://github.com/fpgas-online/fpgas.online-test-designs/issues/276).
- Candidate bitstreams checked on one board of each setup before they become golden: [test-designs issue #277](https://github.com/fpgas-online/fpgas.online-test-designs/issues/277).

## Reaching a board

- A board reached by `ssh` under its own name, with no port number: [infra issue #191](https://github.com/fpgas-online/fpgas.online-infra/issues/191).
- A board reached directly over IPv6: [infra issue #222](https://github.com/fpgas-online/fpgas.online-infra/issues/222).
- Exclusive use of a board for an automated system, through an API: [api issue #1](https://github.com/fpgas-online/fpgas.online-api/issues/1).
- The Tiny Tapeout FPGA demo boards on the welland site's list as well: [site issue #98](https://github.com/fpgas-online/fpgas.online-site/issues/98).
- One front page for every site: [todo issue #13](https://github.com/fpgas-online/todo/issues/13).

## Running a site

- Debian 13 on the Raspberry Pi hosts: [todo issue #4](https://github.com/fpgas-online/todo/issues/4).
- A bootloader locked after boot and upgraded only from a service port: [infra issue #279](https://github.com/fpgas-online/fpgas.online-infra/issues/279).
- A watchdog that finds a dead host and power-cycles it: [poe pull request #8](https://github.com/fpgas-online/fpgas.online-poe/pull/8) and [infra pull request #88](https://github.com/fpgas-online/fpgas.online-infra/pull/88).
- Pages that show the state of an installation, its switch ports and hosts: [site issue #66](https://github.com/fpgas-online/fpgas.online-site/issues/66).
- Public reports of visitors and use: [site issue #69](https://github.com/fpgas-online/fpgas.online-site/issues/69).
- Every Xilinx design also built with Vivado, on our own runners: [vivado-runners issue #6](https://github.com/fpgas-online/fpgas.online-vivado-runners/issues/6).
- A guide that takes a site from nothing to running: [docs issue #128](https://github.com/fpgas-online/fpgas.online-docs/issues/128).

## These pages

- Drawn wiring sheets for the boards other than the Acorn: [test-designs issue #239](https://github.com/fpgas-online/fpgas.online-test-designs/issues/239).
- Pages kept in step with the repositories they describe: [docs issue #134](https://github.com/fpgas-online/fpgas.online-docs/issues/134).
