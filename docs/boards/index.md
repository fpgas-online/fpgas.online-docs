# Boards

Every FPGA board type attached to a host at either site, and the interconnects
they share. Each board page covers the board itself, how it is wired to its
Raspberry Pi, how to program it, and how to check the wiring. Which host has
which board is on the [site pages](../sites/index.md).

```{toctree}
:maxdepth: 1

arty-a7
acorn/index
netv2
fomu-evt
tt-fpga
tt-asic
pmod/index
pin-id
```

## Boards at a glance

Counts are the test-designs hardware README as read on 2026-09-03; where a site
page disagrees, the site page is the measured source and wins.

| Board | Docs | [Welland](../sites/welland.md#hosts-and-boards) | [PS1](../sites/ps1.md#hosts-and-boards) | FPGA | Features |
|-------|------|---------|-----|------|----------|
| [Digilent Arty A7-35T](https://digilent.com/shop/arty-a7-artix-7-fpga-development-board/) | [Arty A7](arty-a7.md), [wiring to the Pi](arty-a7.md#wiring-to-the-raspberry-pi) | ×5 | ×8 | Xilinx XC7A35T | DDR3, Ethernet, PMOD, USB&nbsp;JTAG+UART |
| [Kosagi NeTV2](https://www.crowdsupply.com/alphamax/netv2) (GPIO&nbsp;JTAG) | [Kosagi NeTV2](netv2.md), [JTAG via RPi GPIO](netv2.md#jtag-via-rpi-gpio) | ×5 | — | Xilinx XC7A35T | DDR3, Ethernet, PCIe, HDMI, GPIO&nbsp;JTAG+UART |
| [Kosagi NeTV2](https://www.crowdsupply.com/alphamax/netv2) (RPi5&nbsp;PCIe) | [Kosagi NeTV2](netv2.md), [JTAG via RPi GPIO](netv2.md#jtag-via-rpi-gpio) | —&nbsp;(+×4) | — | Xilinx XC7A35T | DDR3, Ethernet, PCIe, HDMI, GPIO&nbsp;JTAG+UART |
| [Sqrl Acorn CLE-215+](https://github.com/enjoy-digital/litex/wiki/Use-LiteX-on-the-Acorn-CLE-215) | [SQRL Acorn](acorn/index.md), [Acorn wiring](acorn/wiring.md), [PCIe programming](acorn/pcie-programming.md) | ×6 | — | Xilinx XC7A200T | DDR3, PCIe, SPI&nbsp;Flash, GPIO&nbsp;JTAG+UART |
| [LiteFury](https://github.com/RHSResearchLLC/NiteFury-and-LiteFury) / Acorn CLE-101 | [SQRL Acorn](acorn/index.md), [Acorn wiring](acorn/wiring.md), [PCIe programming](acorn/pcie-programming.md) | — | ×3&nbsp;(+×1) | Xilinx XC7A100T | DDR3, PCIe, SPI&nbsp;Flash, GPIO&nbsp;JTAG+UART |
| [Fomu EVT](https://www.crowdsupply.com/sutajio-kosagi/fomu) | [Fomu EVT](fomu-evt.md), [wiring to the Pi](fomu-evt.md#wiring-to-the-raspberry-pi) | ×2 | — | Lattice iCE40UP5K | USB&nbsp;1.1, SPI&nbsp;Flash, PMOD, I2C |
| [TT FPGA Demo Board](https://tinytapeout.com/guides/fpga-breakout/) | [TT FPGA demo board](tt-fpga.md), [pin mapping](tt-fpga.md#pin-mapping), [live board page](https://tinytapeout.fpgas.online/board/fpga-1/) | ×4 | —&nbsp;(+×4) | Lattice iCE40UP5K | PMOD, USB&nbsp;(RP2350), SPI&nbsp;Flash |
| [ButterStick](https://github.com/butterstick-fpga) | [ButterStick](butterstick.md) | —&nbsp;(+×4) | — | Lattice ECP5UM5G-85F | DDR3, GbE, USB&nbsp;2.0, SYZYGY |
| [ULX3S](https://radiona.org/ulx3s/) | [ULX3S](ulx3s.md) | —&nbsp;(+×4) | — | Lattice ECP5 (various) | SDRAM, USB, WiFi, PMOD |
| [TT02](https://tinytapeout.com/chips/tt02/) | [TT ASIC boards](tt-asic.md), [connection to the Pi](tt-asic.md#connection-to-the-pi) | —&nbsp;(+×1) | —&nbsp;(+×1) | SKY130 ASIC | PMOD, USB&nbsp;(RP2040) |
| [TT03](https://tinytapeout.com/chips/tt03/) | [TT ASIC boards](tt-asic.md), [connection to the Pi](tt-asic.md#connection-to-the-pi) | —&nbsp;(+×1) | —&nbsp;(+×1) | SKY130 ASIC | PMOD, USB&nbsp;(RP2040) |
| TT03p5 | [TT ASIC boards](tt-asic.md), [connection to the Pi](tt-asic.md#connection-to-the-pi), [live board page](https://tinytapeout.fpgas.online/board/tt03p5/) | ×1 | — | SKY130 ASIC | PMOD, USB&nbsp;(RP2040, fw 1.2.2) |
| [TT04](https://tinytapeout.com/chips/tt04/) | [TT ASIC boards](tt-asic.md), [connection to the Pi](tt-asic.md#connection-to-the-pi), [live board page](https://tinytapeout.fpgas.online/board/tt04/) | ×1 | —&nbsp;(+×1) | SKY130 ASIC | PMOD, USB&nbsp;(RP2040) |
| [TT05](https://tinytapeout.com/chips/tt05/) | [TT ASIC boards](tt-asic.md), [connection to the Pi](tt-asic.md#connection-to-the-pi), [live board page](https://tinytapeout.fpgas.online/board/tt05/) | ×1 | —&nbsp;(+×1) | SKY130 ASIC | PMOD, USB&nbsp;(RP2040) |
| [TT06](https://tinytapeout.com/chips/tt06/) | [TT ASIC boards](tt-asic.md), [connection to the Pi](tt-asic.md#connection-to-the-pi), [live board page](https://tinytapeout.fpgas.online/board/tt06/) | ×1 | —&nbsp;(+×1) | SKY130 ASIC | PMOD, USB&nbsp;(RP2040) |
| [TT07](https://tinytapeout.com/chips/tt07/) | [TT ASIC boards](tt-asic.md), [connection to the Pi](tt-asic.md#connection-to-the-pi), [live board page](https://tinytapeout.fpgas.online/board/tt07/) | ×1 | —&nbsp;(+×1) | SKY130 ASIC | PMOD, USB&nbsp;(RP2040) |
| [TT08](https://tinytapeout.com/chips/tt08/) | [TT ASIC boards](tt-asic.md), [connection to the Pi](tt-asic.md#connection-to-the-pi), [live board page](https://tinytapeout.fpgas.online/board/tt08/) | ×1 | —&nbsp;(+×1) | SKY130 ASIC | PMOD, USB&nbsp;(RP2040) |
| [TT09](https://tinytapeout.com/chips/tt09/) | [TT ASIC boards](tt-asic.md), [connection to the Pi](tt-asic.md#connection-to-the-pi) | —&nbsp;(+×1) | —&nbsp;(+×1) | SKY130 ASIC | PMOD, USB&nbsp;(RP2040)&nbsp;[†](#count-and-controller-disagreements) |

Deployment counts: `×N` = deployed, `(+×N)` = pending deployment, `—` = none.
The Welland TT ASIC and TT FPGA boards are the public boards on
[tinytapeout.fpgas.online](https://tinytapeout.fpgas.online) and sit on S3300
ports 3–8 and 33–36 (`pi-sw2-p<port>`); see
[Welland hosts and boards](../sites/welland.md#hosts-and-boards).

The Docs column links the board pages rather than the litex-boards platform
files the source listed; every board page carries its own platform link in its
LiteX section. Two source links are not reproduced. The source linked
`tinytapeout.com/chips/tt03p5/` from the TT03p5 row; that page returns 404
(checked 2026-09-03), so the row carries plain text here. The source's
ButterStick row linked `butterstick.io`, whose domain no longer resolves at all
(NXDOMAIN, checked 2026-09-03), so that row links the
[ButterStick GitHub organisation](https://github.com/butterstick-fpga) instead;
see [ButterStick](butterstick.md).

:::{note}
The Arty row's vendor link is the source's, and it still answers, but Digilent
now redirects `shop/arty-a7-artix-7-fpga-development-board/` to the **A7-100T**
product page. The deployed boards are A7-35T. The obvious replacement,
`digilent.com/reference/programmable-logic/arty-a7/start`, could not be
substituted: the whole `digilent.com/reference/` tree returns 403 to a
command-line fetch, so no replacement could be confirmed reachable.
:::

(count-and-controller-disagreements)=

:::{note}
Cross-checking the table against the site pages leaves five disagreements. The
README numbers are reproduced unchanged; where a site page disagrees, the site
page is the measured source.

- **TT ASIC at PS1.** The table above has a pending TT08 at PS1, so it totals
  eight pending ASIC boards there. The PS1 board summary counts seven, "one
  each: TT02-TT09 except TT08" — see [PS1 pending](../sites/ps1.md#pending) and
  the same disagreement recorded on
  [Tiny Tapeout ASIC demo boards](tt-asic.md#shuttles-and-boards).
- **TT ASIC at Welland.** The table above has TT02, TT03 and TT09 pending at
  Welland. The Welland page records only that S3300 ports 9 and 10 are reserved
  for `tt09` and `tt10` with no Pi behind them, says nothing about TT02 or TT03,
  and names a `tt10` that has no row here — see
  [Tiny Tapeout ASIC boards](../sites/welland.md#tiny-tapeout-asic-boards).
- **NeTV2 (RPi5 PCIe) at Welland.** Four are pending here. The Welland page has
  no pending PCIe NeTV2 hosts; the only RPi 5 NeTV2 is `rpi5-netv2`, one of the
  two development hosts on the separate `iot.welland.mithis.com` network — see
  [NeTV2 development hosts](../sites/welland.md#netv2-development-hosts-separate-network).
- **ButterStick and ULX3S at Welland.** Four of each are pending here. Neither
  board appears anywhere on the [Welland page](../sites/welland.md), and neither
  has a host, a switch port or an allocation recorded.
- **† TT09's controller.** The TT09 row's Features cell says `USB (RP2040)`,
  following the README. The demo-PCB version rule puts TT09 on demo board v3
  with an **RP2350**, which is what
  [Tiny Tapeout ASIC demo boards](tt-asic.md#shuttles-and-boards) records. No
  TT09 board is deployed, so nothing has been measured either way.
:::

## Guides

The interconnects and the cross-board procedures, in the order they are usually
needed.

PMOD interconnects:

- [PMOD interface](pmod/index.md) — the PMOD interface specification (standard
  Digilent types 1–6 + I2C extension)
- [Raspberry Pi PMOD HAT](pmod/rpi-hat.md) — the Digilent PMOD HAT adapter for
  Raspberry Pi (RPi GPIO ↔ PMOD pinmap, type conformance)
- [Tiny Tapeout PMOD layouts](pmod/tinytapeout.md) — TinyTapeout PMOD connector
  standards (TT-specific layouts, RP2040/RP2350 GPIO mapping, community PMOD
  boards)

Wiring guides:

- [Acorn wiring](acorn/wiring.md) — step-by-step Acorn CLE-215+ setup: M.2 HAT,
  Pico-EZmate cable prep, JTAG/UART/GPIO wiring (serial crossover!), Pi 5 traps,
  measured per-board wiring, PCIe verification
- [Acorn PCIe programming](acorn/pcie-programming.md) — PCIe-detach rule for
  JTAG loads, prebuilt Vivado bitstreams, PCIe-based bitstream programming,
  Xilinx 7-series multiboot, flash layout, recovery procedures

Processes:

- [Verifying a deployment](../setup/verification.md) — files to update when
  deploying a new device of an existing type

Analysis:

- [Verifying wiring with the pin-id design](pin-id.md) — GPIO scan results and
  connectivity verification across boards

## Planned boards

Two boards have been specified but never wired to a Raspberry Pi. Each carries a
pending count of four at Welland in the test-designs hardware README, but
neither appears on the [Welland page](../sites/welland.md) at all: no host, no
switch port, no allocation. Neither has a wiring guide, because neither has been
wired — their pages are what the litex-boards platform files and the vendor
material say, not measured facts.

```{toctree}
:maxdepth: 1
:hidden:

butterstick
ulx3s
```

### ButterStick

:::{note}
**Status: Future / Planned** — this board is not yet deployed in the
fpgas.online infrastructure, and no wiring to a Raspberry Pi exists for it.
:::

Notable differences from other boards:

- **ECP5UM5G with SERDES**: The `5G` variant includes high-speed
  serializer/deserializer blocks, enabling protocols like PCIe Gen1, SATA, or
  custom high-speed links.
- **SYZYGY connector** (not PMOD): The SYZYGY standard provides higher-speed and
  higher-density connectivity than PMOD. PMOD-based tests cannot run on this
  board without an adapter.
- **Gigabit Ethernet**: RGMII PHY supporting 1000Base-T, unlike the 100Base-T on
  the Arty and NeTV2.
- **ULPI USB**: External USB 2.0 PHY, unlike the Fomu's native USB.
- **DDR3**: Full DDR3 with 32-bit bus, similar to NeTV2 but larger capacity.

Specifications, LiteX modules, programming commands and the state of the vendor
site are on the [ButterStick page](butterstick.md).

### ULX3S

:::{note}
**Status: Future / Planned** — this board is not yet deployed in the
fpgas.online infrastructure, and no wiring to a Raspberry Pi exists for it.
:::

Notable differences from other boards:

- **No PMOD connectors**: Uses pin headers instead. PMOD-based tests cannot run
  on this board without an adapter.
- **SDR SDRAM** (not DDR3): 32 MB, 16-bit bus. Simpler memory interface but
  lower bandwidth.
- **ESP32 WiFi**: On-board wireless connectivity, could enable remote test
  reporting without wired Ethernet.
- **GPDI video**: HDMI-compatible output using differential pairs.

Specifications, the ECP5 variant table, LiteX modules and programming commands
are on the [ULX3S page](ulx3s.md).
