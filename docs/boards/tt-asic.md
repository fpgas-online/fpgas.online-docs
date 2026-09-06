# Tiny Tapeout ASIC demo boards

A Tiny Tapeout ASIC demo board is a fabricated Tiny Tapeout shuttle chip — real
sky130 silicon — on a Tiny Tapeout demo PCB. The PCB carries an RP2
microcontroller running the Tiny Tapeout MicroPython SDK, which selects the
project inside the chip, drives its clock and reset, and bridges the whole thing
to USB: an **RP2040** on demo board **v2** (TT06 to TT08) and an **RP2350** on
**v3** (TT09 and later). The chip's three 8-bit signal groups — `ui_in`,
`uo_out` and `uio` — come out on three 12-pin PMOD connectors along the bottom
edge, one group per connector; the connectors, the standard PMOD layouts built
on them and the controller GPIO maps behind them are on
[Tiny Tapeout PMOD layouts](pmod/tinytapeout.md).

Six of these boards are deployed, all at Welland, on S3300 ports 3–8: one each
for **TT03p5, TT04, TT05, TT06, TT07 and TT08**. Five of the six run TT SDK
**2.0.4**; the TT03p5 board runs demo-board firmware **1.2.2**, the last release
that supports that shuttle. They are the public ASIC boards on
[tinytapeout.fpgas.online](https://tinytapeout.fpgas.online), live since
2026-08-23. [PS1](../sites/ps1.md#pending) has none deployed — its TT ASIC
boards are still pending.

The same demo PCB with a Lattice iCE40UP5K breakout in place of the ASIC is the
[Tiny Tapeout FPGA demo board](tt-fpga.md); everything below about the USB
bridge and the MicroPython SDK is shared between the two, and the FPGA page
carries the deeper detail.

This page covers which shuttles are deployed and pending, how a board is
connected to its Raspberry Pi, and the firmware each board runs. The hosts,
addresses and serial numbers are on the Welland page, not here.

## Shuttles and boards

| Shuttle | Chip page | Demo PCB controller | Welland | PS1 | Live board page |
| ------- | --------- | ------------------- | ------- | --- | --------------- |
| TT02   | [tt02](https://tinytapeout.com/chips/tt02/) | RP2040 | pending ×1 | pending ×1 | — |
| TT03   | [tt03](https://tinytapeout.com/chips/tt03/) | RP2040 | pending ×1 | pending ×1 | — |
| TT03p5 | — | RP2040 | **deployed ×1** | — | [tt03p5](https://tinytapeout.fpgas.online/board/tt03p5/) |
| TT04   | [tt04](https://tinytapeout.com/chips/tt04/) | RP2040 | **deployed ×1** | pending ×1 | [tt04](https://tinytapeout.fpgas.online/board/tt04/) |
| TT05   | [tt05](https://tinytapeout.com/chips/tt05/) | RP2040 | **deployed ×1** | pending ×1 | [tt05](https://tinytapeout.fpgas.online/board/tt05/) |
| TT06   | [tt06](https://tinytapeout.com/chips/tt06/) | RP2040 (v2) | **deployed ×1** | pending ×1 | [tt06](https://tinytapeout.fpgas.online/board/tt06/) |
| TT07   | [tt07](https://tinytapeout.com/chips/tt07/) | RP2040 (v2) | **deployed ×1** | pending ×1 | [tt07](https://tinytapeout.fpgas.online/board/tt07/) |
| TT08   | [tt08](https://tinytapeout.com/chips/tt08/) | RP2040 (v2) | **deployed ×1** | pending ×1 | [tt08](https://tinytapeout.fpgas.online/board/tt08/) |
| TT09   | [tt09](https://tinytapeout.com/chips/tt09/) | RP2350 (v3) | pending ×1 | pending ×1 | [tt09](https://tinytapeout.fpgas.online/board/tt09/) (placeholder) |

Counts as of 2026-09-03 from the test-designs hardware README and the Welland
host table.

The demo PCB version is fixed by the shuttle: v2 (RP2040) carries TT06 to TT08
and v3 (RP2350) carries TT09 onwards, so the six deployed boards are all RP2040
boards. The catalogue behind tinytapeout.fpgas.online reserves S3300 ports 9 and
10 for `tt09` and `tt10`, and serves a board page for each, but neither has a Pi
or a board behind it yet.

:::{note}
Two disagreements between the sources, neither resolved:

- The hardware README lists TT09 as `USB (RP2040)`, while the demo PCB version
  rule on [Tiny Tapeout PMOD layouts](pmod/tinytapeout.md) puts TT09 on demo
  board v3 with an RP2350. The table above follows the version rule. No TT09
  board is deployed, so nothing has been measured either way.
- The README's PS1 column has a pending TT08, while the PS1 board summary counts
  seven pending ASIC boards, "one each: TT02-TT09 except TT08" — which is what
  [PS1 pending](../sites/ps1.md#pending) repeats. The PS1 column above follows
  the README, so it totals **eight** pending boards where
  [PS1 pending](../sites/ps1.md#pending) says seven.
:::

:::{todo}
Fix the test-designs hardware README on the three points in the note above:
TT09's controller, the pending TT08 that [PS1 pending](../sites/ps1.md#pending)
excludes, and its link to `tinytapeout.com/chips/tt03p5/`, which is a 404 —
which is why the TT03p5 row has no shuttle link.
:::

## Connection to the Pi

Each board is wired to its Raspberry Pi two ways.

**USB, to the demo board's controller.** The RP2 presents a USB CDC serial
console — the MicroPython REPL — and enumerates as "MicroPython Board in FS
mode", VID:PID `2e8a:0005`, at
`/dev/serial/by-id/usb-MicroPython_Board_in_FS_mode_<serial>-if00`, with a udev
symlink **`/dev/ttboard`** to `/dev/ttyACM0`. That port has a permanent owner:
every TT host runs the `fpgas-tt` daemon, which holds it open and republishes it
as a WebSocket on port 8765 for the web Commander (all probed 2026-09-03), so
`mpremote` and anything else that wants the port has to stop the daemon first —
and start it again afterwards, or the board drops off the public site:

```console
# Stopping the daemon takes the board off tinytapeout.fpgas.online until it is
# started again -- do not leave it stopped.
$ sudo systemctl stop fpgas-tt
$ sudo systemctl start fpgas-tt
```

The mechanics are the same as for the FPGA boards; see
[Serial port ownership](tt-fpga.md#serial-port-ownership) for the endpoints and
the stop/start rule, and [The Tiny Tapeout stack](../setup/tinytapeout.md) for
how the daemon is installed. Each board's
`https://tinytapeout.fpgas.online/board/<slug>/status.json` reports the daemon's
`/health` plus `reachable`, and is the quickest liveness check.

**A Digilent Pmod HAT ribbon, for GPIO-level access.** Every ASIC host also
carries a [Raspberry Pi PMOD HAT](pmod/rpi-hat.md), which can bring the demo
board's PMOD connectors onto the Pi's GPIO header; how they are cabled on these
hosts has not been recorded. Where the ribbons are in place, the TT I/O pins can
be driven and sampled from Linux rather than through the MicroPython REPL. Every
host has an ov5647 camera pointed at the board as well.

**No GPIO wiring table has been measured for the ASIC boards.** The measured
iCE40-ball-to-PMOD-HAT-to-Pi-GPIO map on
[Tiny Tapeout FPGA demo board](tt-fpga.md#pin-mapping) was taken on a demo board
**v3** (TTDBv3) host; it applies to a v3 ASIC board only if the cabling is
identical, and it says nothing about the v2 boards that are actually deployed
here. Nothing on this page should be read as a verified ASIC pin map.

:::{todo}
Measure the PMOD HAT to Raspberry Pi GPIO wiring on the deployed TT ASIC hosts
with the [pin-ID design](pin-id.md), the way the Acorn wiring was measured, and
record a per-signal table here.
:::

## Firmware

The demo board's firmware is the Tiny Tapeout MicroPython SDK, flashed to the
RP2 controller. Which build a board can run depends on both the controller and
the shuttle:

- **TT SDK 2.0.4** is the last RP2040 build; the 3.x series is RP2350-only.
  That is why the six deployed ASIC boards stop at 2.0.4 while the
  [FPGA boards](tt-fpga.md#board-firmware), which are RP2350 v3 boards, run
  3.1.0.
- On **2026-08-23/24** the tt04, tt05 and tt07 boards were reflashed to
  2.0.4; tt06 and tt08 already had it.
- The **TT03p5** chip is not supported by SDK 2.0 or later, so that board stays
  on demo-board firmware **1.2.2**, the last release that supports the shuttle,
  with a hand-pushed `/shuttles/tt03p5.json` and a `rom_fallback.txt` (TT03p5
  has no chip ROM to identify itself from).

:::{warning}
The web Commander does not support demo-board firmware 1.2.x, so the tt03p5
board is camera-only on the public site until the upstream `legacy` branch is
ported —
[tt-commander-app #9](https://github.com/fpgas-online/tt-commander-app/pull/9)
and [#10](https://github.com/fpgas-online/tt-commander-app/pull/10). This is
tracked under [Known faults](../sites/welland.md#known-faults) on the Welland
page.
:::

Reflashing is awkward on the Raspberry Pi 3B+ hosts (tt06, tt07 and tt08): the
RP2 bootloader's mass-storage path stalls there because `dwc_otg` resets about
every 35 s, so flash those boards over PICOBOOT instead of MSC and run the flash
detached (`setsid nohup … &`). The reflash history and the SDK-level workarounds
— the `DemoBoard()` boot hang, and the rule against leaving a no-op `main.py` on
a board that is on the public site — are written up for the FPGA boards under
[Board firmware](tt-fpga.md#board-firmware) and
[Known Workarounds](tt-fpga.md#known-workarounds); the sources describe both as
properties of the shared MicroPython SDK rather than of the FPGA breakout, but
neither has been re-verified on an ASIC board.

## Where they are

All six deployed boards are at Welland, on S3300 ports 3–8, on Raspberry Pi 4
and 3B+ hosts with Pmod HATs — the switch port number is the shuttle number, so
port N carries TTN. The hosts, their addresses, MACs, RP2040 serial numbers,
per-board firmware versions and old `piNN` names are in
[Tiny Tapeout ASIC boards](../sites/welland.md#tiny-tapeout-asic-boards) on the
Welland page, which also carries the per-port VLAN scheme those addresses come
from. These hosts have no page under `welland.fpgas.online/fpgas/`; their public
pages are the `tinytapeout.fpgas.online` board pages linked above.

## References

- TinyTapeout pinout recommendations: <https://tinytapeout.com/specs/pinouts/>
- TinyTapeout PCB specifications: <https://tinytapeout.com/specs/pcb/>
- TinyTapeout demo PCB design: <https://github.com/TinyTapeout/tt-demo-pcb>
- TinyTapeout MicroPython SDK (demo board firmware):
  <https://github.com/TinyTapeout/tt-micropython-firmware>
- `fpgas-tt`, the Pi-side bridge daemon:
  <https://github.com/fpgas-online/fpgas.online-tt>
- Public boards: <https://tinytapeout.fpgas.online>
- PMOD layouts on the demo board:
  [Tiny Tapeout PMOD layouts](pmod/tinytapeout.md), with the
  [RP2040 map (v2, TT06 to TT08)](pmod/tinytapeout.md#rp2040-gpio-mapping-demo-board-v2-tt06-tt08)
  and the
  [RP2350 map (v3, TT09+)](pmod/tinytapeout.md#rp2350-gpio-mapping-demo-board-v3-tt09)
- PMOD HAT adapter: [Raspberry Pi PMOD HAT](pmod/rpi-hat.md)
- The FPGA sibling: [Tiny Tapeout FPGA demo board](tt-fpga.md)
