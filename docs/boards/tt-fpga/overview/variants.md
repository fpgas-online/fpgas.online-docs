# Tiny Tapeout FPGA board: variants

**You have a Tiny Tapeout demo board and want to know which kind it is: which demo board version, and whether
its chip socket holds the FPGA breakout or a Tiny Tapeout chip.** These pages are for a version 3 demo board
with the FPGA breakout. A demo board with a chip is on [Tiny Tapeout ASIC demo boards](../../tt-asic.md).

## Demo board version 3 against version 2

Every board on these pages is a demo board **version 3 (TTDBv3)** carrying an **RP2350B**, and the
[wiring pages](../wiring/cables.md) give the version 3 mapping. A version 2 demo board carries an **RP2040**.
The two are *not* interchangeable: [Tiny Tapeout PMOD layouts](../../pmod/tinytapeout.md) shows the
clock on GPIO0 for version 2 against GPIO16 for version 3, and a different GPIO block for
every signal group. Our loader and tests are written for version 3 (source:
[fpgas.online-test-designs](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/tt-fpga.md)).

| | Version 3 (TTDBv3) | Version 2 |
|---|---|---|
| Microcontroller | RP2350 | RP2040 |
| Clock to the design | GPIO16 | GPIO0 |
| The 24 signals at the microcontroller | [the same 24 signals at the microcontroller](../wiring/pins-other.md#the-same-24-signals-at-the-microcontroller) | [the RP2040 map](../../pmod/tinytapeout.md#rp2040-gpio-mapping-demo-board-v2-tt06-tt08) |
| Tiny Tapeout SDK | 3.1.x | 2.0.x is the last RP2040 build |

Source: [Tiny Tapeout PMOD layouts](../../pmod/tinytapeout.md), from Tiny Tapeout's specification, and
[the `sdk` test](../../../verify/fpgas-verify.md#the-sdk-test) and [Tiny Tapeout ASIC demo
boards](../../tt-asic.md#firmware) for the SDK row. Not verified by us on a version 2 board.

The Tiny Tapeout PCB specification the [device info](device-info.md#key-specifications) table comes from
describes the RP2040-based version 2 board; two of its facts have not been measured again on a version 3
board (the todo under that table).

## The FPGA breakout against a chip

The same demo PCB carries either the FPGA breakout or a fabricated Tiny Tapeout chip in its socket. A board
with the breakout carries an **iCE40UP5K FPGA** (FabricFox breakout) that emulates Tiny
Tapeout designs. It is **not** an ASIC board.

- **On USB the two look the same.** The demo board's microcontroller reads `2e8a:0005` either way, so the
  boot check asks the board itself, and loads a design only into a board that said it carries the FPGA:
  [Which Tiny Tapeout board it is](../../../verify/fpgas-verify.md#which-tiny-tapeout-board-it-is).
- **A board with a chip**: its shuttles, its firmware and how it is connected are on
  [Tiny Tapeout ASIC demo boards](../../tt-asic.md). No Pmod wiring has been measured for those boards; the
  wiring pages here apply to a version 3 chip board only if its cabling is identical.
