---
type: explanation
owner: documentation maintainers
reader: someone choosing a board to use who wants to know what ps1 offers
review: 2026-11-10
---

# The ps1 site

This page explains what the ps1 site offers a visitor, and what it plans to offer. It is for someone choosing
a board to use. It does not list the boards or their hosts. The site's own pages show those as they are.

## What the site provides

ps1 is at [Pumping Station: One](https://pumpingstationone.org/), a hackerspace in Chicago. Its gateway and
switch belong to the site's own operator, and fpgas.online does not deploy to them. A host at ps1 is always
written with its site in these docs, as in "pi20 at ps1".

[The ps1 site](https://ps1.fpgas.online/fpgas/) lists the boards a visitor can use. They are
[Arty A7](../boards/arty-a7.md) boards, each on a Raspberry Pi over USB. A board's page gives a terminal in the
browser, an upload for a bitstream and a camera feed of the board. Its reset power-cycles the host.

ps1 also has Compute Blades, each with a Raspberry Pi Compute Module and an M.2 slot for an
[Acorn](../boards/acorn/index.md) card. A visitor reaches a blade with `ssh`:
[How to log in to a host at ps1](../setup/ps1-login.md). Whatever is installed on a blade is gone after its
next boot.

## What the site plans to provide

Each item names the issue that tracks it.

- Acorn CLE-101 cards on the Compute Blades, wired by the cable guide: [test-designs issue #216](https://github.com/fpgas-online/fpgas.online-test-designs/issues/216).
- Those cards running the fpgas.online design, so that each has a board page: [test-designs issue #213](https://github.com/fpgas-online/fpgas.online-test-designs/issues/213).
- A card for the blade that has none: [test-designs issue #217](https://github.com/fpgas-online/fpgas.online-test-designs/issues/217).
- Tiny Tapeout chip boards and FPGA demo boards: [tt issue #19](https://github.com/fpgas-online/fpgas.online-tt/issues/19).
- A page for each host that stays when its board changes: [site issue #65](https://github.com/fpgas-online/fpgas.online-site/issues/65).

```{toctree}
:hidden:

Gateway and switch <ps1-gateway>
```
