---
type: explanation
owner: documentation maintainers
reader: someone who wants to know what fpgas.online plans, beyond one site
review: 2026-11-10
---

# Roadmap

This page says what is planned across fpgas.online, beyond what one site plans. It is for someone deciding
whether to wait for something. It gives no dates. What one site plans is on that site's page, under
[Sites](sites/index.md).

## For someone using a board

Each line is one planned thing and the issue that tracks it. A thing is not listed here once a site offers it.

- A board reached by `ssh` under its own name, with no port number: [infra issue #191](https://github.com/fpgas-online/fpgas.online-infra/issues/191).
- A board reached directly over IPv6: [infra issue #222](https://github.com/fpgas-online/fpgas.online-infra/issues/222).
- Exclusive use of a board for an automated system, through an API: [api issue #1](https://github.com/fpgas-online/fpgas.online-api/issues/1).
- More board types, such as ButterStick and ULX3S: [test-designs issue #225](https://github.com/fpgas-online/fpgas.online-test-designs/issues/225).
- HDMI, HDCP and USB on the NeTV2 boards: [test-designs issue #234](https://github.com/fpgas-online/fpgas.online-test-designs/issues/234).
- Designs to use from a board's page, with nothing to build: [test-designs issue #236](https://github.com/fpgas-online/fpgas.online-test-designs/issues/236).
- One front page for every site: [todo issue #13](https://github.com/fpgas-online/todo/issues/13).

## For someone running a site

Each line is one planned thing and the issue that tracks it. A thing is not listed here once it is in service.

- Debian 13 on the Raspberry Pi hosts: [todo issue #4](https://github.com/fpgas-online/todo/issues/4).
- Pages that show the state of an installation, its switch ports, hosts and use: [site issue #66](https://github.com/fpgas-online/fpgas.online-site/issues/66).
- Every Xilinx design also built with Vivado, on our own runners: [vivado-runners issue #6](https://github.com/fpgas-online/fpgas.online-vivado-runners/issues/6).
- A check for the Tiny Tapeout chip boards: [test-designs issue #235](https://github.com/fpgas-online/fpgas.online-test-designs/issues/235).
- A check of every function of each board type: [test-designs issue #87](https://github.com/fpgas-online/fpgas.online-test-designs/issues/87).
- A guide that takes a site from nothing to running: [docs issue #128](https://github.com/fpgas-online/fpgas.online-docs/issues/128).

Planned items that have no issue are collected in [docs issue #132](https://github.com/fpgas-online/fpgas.online-docs/issues/132) until each has one.
