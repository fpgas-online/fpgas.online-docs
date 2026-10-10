---
type: explanation
owner: documentation maintainers
reader: someone with a Tiny Tapeout chip demo board
review: 2026-11-10
---

# The Tiny Tapeout chip demo boards

You have a Tiny Tapeout demo board with a manufactured chip on it and want to know what the board is.
The shuttles are on [Tiny Tapeout shuttles and their demo boards](shuttles.md).
The wires are on [Tiny Tapeout chip demo board wiring to a Raspberry Pi](../setup/wiring.md).
This page does not cover loading a design.

## The board

A Tiny Tapeout chip demo board is a fabricated Tiny Tapeout shuttle chip, real sky130 silicon, on a Tiny Tapeout demo PCB.
The PCB carries an RP2 microcontroller running the Tiny Tapeout MicroPython SDK.
The SDK selects the project inside the chip, drives its clock and reset, and bridges the board to USB.
The controller is an **RP2040** on demo board **v2** (TT06 to TT08) and an **RP2350** on **v3** (TT09 and later).

:::{admonition} Figure to come
:class: placeholder

The whole demo board with its chip and each part numbered, top and bottom. Tracked in [test-designs issue #261](https://github.com/fpgas-online/fpgas.online-test-designs/issues/261).
:::

## The chip's connectors

The chip has three 8-bit signal groups: `ui_in`, `uo_out` and `uio`.
They come out on three 12-pin PMOD connectors along the bottom edge of the demo board, one group per connector.
The connectors, the standard PMOD layouts built on them and the controller GPIO maps behind them are on [Tiny Tapeout PMOD layouts](../../pmod/tinytapeout.md).

## How the board reaches its Raspberry Pi

Each board is wired to its Raspberry Pi two ways: USB to the controller, and a Digilent Pmod HAT ribbon for GPIO-level access.
The USB link carries the controller's serial console, the MicroPython REPL.
A daemon on the Raspberry Pi, `fpgas-tt`, holds that serial port open and republishes it as a WebSocket for the web Commander.
Anything else that needs the port must stop the daemon first.
It must start it again, or the board drops off the public site: [How to free a Tiny Tapeout board's serial port from fpgas-tt](../setup/free-the-serial-port.md).

The daemon is installed as described in [The Tiny Tapeout stack](../../../setup/tinytapeout.md).

Every chip board's host also carries a [Raspberry Pi PMOD HAT](../../pmod/rpi-hat.md) and an ov5647 camera pointed at the board.
Where the ribbons are in place, the chip's I/O pins can be driven and sampled from Linux rather than through the MicroPython REPL.

## Beside the FPGA board

The same demo PCB with a Lattice iCE40UP5K breakout in place of the chip is the [Tiny Tapeout FPGA demo board](../../tt-fpga.md).
The USB bridge and the MicroPython SDK are shared between the two boards, and the FPGA page carries the deeper detail.
The public site for these boards is <https://tinytapeout.fpgas.online>.

## Checks

The check that runs on the host for the Tiny Tapeout demo boards is [fpgas-verify: the Tiny Tapeout demo boards](../../../verify/tt-fpga.md). On a chip board it runs the `sdk` test and then the `wiring` test of the three Pmod ribbons, and it loads nothing.
