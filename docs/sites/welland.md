---
type: explanation
owner: documentation maintainers
reader: someone choosing a board to use who wants to know what welland offers
review: 2026-11-10
---

# The welland site

This page explains what the welland site offers a visitor, and what it plans to offer. It is for someone
choosing a board to use. It does not list the boards or their hosts. The site's own pages show those as they
are.

## What the site provides

welland is a private test lab in South Australia. Its boards are open to visitors through the public sites named here.
A bare host name in these docs means a host at welland. Its gateway is on [The welland gateway](welland-gateway.md), for someone who runs the site.

[The welland site](https://welland.fpgas.online/fpgas/) lists the FPGA boards a visitor can use. A board is
listed while the check on its host passes, so the list is what works at that moment. The lab holds these kinds of board.

- [Acorn](../boards/acorn/index.md) CLE-215+ cards, each on a Raspberry Pi 5, with PCIe, JTAG and a serial port.
- [NeTV2](../boards/netv2.md) boards, each on a Raspberry Pi, with JTAG and a serial port on the header.
- A [Fomu EVT](../boards/fomu-evt.md), with a USB analyser between the board and its host.
- [Arty A7](../boards/arty-a7.md) boards, each on a Raspberry Pi over USB.

A board's page gives a terminal in the browser, an upload for a bitstream and a camera feed of the board.
Its reset power-cycles the host. The page also shows the command for a visitor's own `ssh` client. Whatever a
visitor writes on a host is gone after its next reset.

[The Tiny Tapeout site](https://tinytapeout.fpgas.online) has the Tiny Tapeout boards. The
[chip boards](../boards/tt-asic.md) carry manufactured Tiny Tapeout chips, and a visitor selects a design on
the chip and drives its pins. The [FPGA demo boards](../boards/tt-fpga.md) run a bundled demo or a visitor's
own bitstream. Each board has a camera feed.

## What the site plans to provide



- Arty A7 boards a visitor can use again: [infra issue #125](https://github.com/fpgas-online/fpgas.online-infra/issues/125).
- NeTV2 boards that pass their memory test: [test-designs issue #86](https://github.com/fpgas-online/fpgas.online-test-designs/issues/86) and [test-designs issue #91](https://github.com/fpgas-online/fpgas.online-test-designs/issues/91).
- The Acorn cards that are installed and not in service: [test-designs issue #209](https://github.com/fpgas-online/fpgas.online-test-designs/issues/209).
- The Tiny Tapeout boards whose hosts are down, back in service: [infra issue #274](https://github.com/fpgas-online/fpgas.online-infra/issues/274).
- The Tiny Tapeout chip boards tt09 and tt10: [tt issue #20](https://github.com/fpgas-online/fpgas.online-tt/issues/20).
- Driving the oldest chip board from the browser, which shows a camera feed only: [tt-commander-app issue #9](https://github.com/fpgas-online/tt-commander-app/issues/9).
