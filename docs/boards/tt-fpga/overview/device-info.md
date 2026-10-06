# Tiny Tapeout FPGA board: device info

**You have a Tiny Tapeout demo board (version 3) with the FabricFox iCE40UP5K FPGA breakout in its chip
socket and want to know what is on it: the FPGA, the microcontroller, the clock, the display, the switches
and the Pmod headers.** What differs between demo board versions, and between the FPGA breakout and a chip, is
on [variants](variants.md); every wire to the Raspberry Pi is on the [wiring pages](../wiring/cables.md).

## The board

**No picture yet.** We hold no photograph or drawing of the demo board itself. The one picture we have is the
diagram of its three Pmod headers and their cables on [which cable goes where](../wiring/cables.md). Tiny
Tapeout's own photographs and drawings of the board are in its
[demo board design](https://github.com/TinyTapeout/tt-demo-pcb).

The TT FPGA demo board consists of two PCBs:

1. **TinyTapeout Demo PCB** (bottom): Contains the RP2350 microcontroller,
   USB-C connector, 7-segment display, DIP switches, and PMOD headers. This PCB
   is designed to interface with TinyTapeout ASICs but also accepts the FPGA
   breakout board.

2. **FPGA Breakout Board** (top): Contains the iCE40UP5K FPGA; it has no SPI flash. It
   plugs into the demo PCB's chip socket, presenting the same interface as a
   TinyTapeout ASIC.

```text
┌──────────────────────────────┐
│    FPGA Breakout Board       │
│    (iCE40UP5K)               │
│                              │
│    ┌────────────────────┐    │
│    │  Pin headers down  │    │
│    └────────────────────┘    │
└──────────────┬───────────────┘
               │ (plugs into)
┌──────────────┴───────────────┐
│    TinyTapeout Demo PCB      │
│                              │
│  [USB-C] [RP2350] [7-seg]   │
│  [DIP SW] [3 x PMOD header] │
└──────────────────────────────┘
```

The microcontroller programs the iCE40 over SPI and provides its 50 MHz clock.
After programming it releases its GPIO pins to high impedance so the Raspberry
Pi can talk to the FPGA directly through the PMOD HAT — the controller and the
PMOD headers share the same physical traces.

## Key Specifications

| Parameter | Value |
|-----------|-------|
| FPGA | Lattice iCE40UP5K (on FPGA breakout board) |
| Logic cells | 5,280 LUT4s |
| SPRAM | 128 KB (4 x 32 KB blocks) |
| DPRAM (EBR) | 120 Kbit (15 x 8 Kbit blocks) |
| Controller | RP2350 (on the version 3 demo PCB; RP2040 on version 2) |
| USB | USB-C (via RP2350) |
| Display | 7-segment LED display |
| DIP switches | Configuration switches |
| PMOD headers | 3x standard PMOD (following Digilent spec): input, bidirectional, output |
| Max clock | ~66 MHz |
| I/O voltage | 3.3V |

Source: [TinyTapeout PCB Specs](https://tinytapeout.com/specs/pcb/),
[TinyTapeout FPGA Breakout Guide](https://tinytapeout.com/guides/fpga-breakout/); the controller and Pmod
header rows as corrected in
[fpgas.online-test-designs](https://github.com/fpgas-online/fpgas.online-test-designs/pull/153). Not verified
by us against a board.

:::{todo}
The RP2040-specific facts inherited from the version 2 specification have not been
re-verified on a version 3 board: the ~66 MHz maximum clock in the table above, and
the PWM first-call bug the source calls an RP2040 bug while the deployed
workaround calls it an RP2350 bug (see [RP2350 PWM first-call
bug](../designs/firmware.md#rp2350-pwm-first-call-bug)). Measure both on a TTDBv3 in the fleet and
record the date.
:::

## FPGA device

| Parameter | Value                                  |
| --------- | -------------------------------------- |
| FPGA      | Lattice iCE40UP5K-SG48                 |
| Package   | SG48 (48-pin QFN)                      |
| Clock     | 50 MHz from RP2350 PWM (GPIO16)        |
| Block RAM | 30 EBR blocks (15 KB total)            |
| SPRAM     | 128 KB (4 × 32 KB)                     |
| Toolchain | icestorm / nextpnr-ice40 (open source) |

Source: the
[TT FPGA LiteX platform definition](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_shared/tt_fpga_platform.py)

:::{todo}
The two sources disagree on how the iCE40UP5K's block RAM is divided. The table
under Key Specifications says 15 × 8 Kbit EBR blocks; the table above
says 30 EBR blocks. The totals agree (120 Kbit ≈ 15 KB), so one of the
block counts is wrong. Check against the Lattice datasheet and fix the loser.
:::

## No SPI flash

The FPGA breakout has no SPI flash, so the FPGA is empty at every power-up until a design is loaded into it.
The four pins an earlier version of this page listed as flash pins are the iCE40's configuration pins, which
go only to the demo board's microcontroller: [the pins that load the
FPGA](../wiring/pins-other.md#loading-the-fpga-its-configuration-pins). How a design is loaded:
[functionality](functionality.md#programming).

## PMOD Headers

The demo PCB has 3 standard PMOD headers following the
[Digilent specification](../../pmod/index.md), one for each signal group. They are printed INPUT (`ui_in`),
BIDIR (`uio`) and OUTPUT (`uo_out`) (source: Tiny Tapeout's demo board design; not verified by us on a
board):

- Each header is a 12-pin connector (8 signal + 2 GND + 2 VCC)
- Signal voltage: 3.3V

These PMOD headers can be used for loopback testing in the fpgas.online
infrastructure. The layouts Tiny Tapeout recommends for them are on
[Tiny Tapeout PMOD layouts](../../pmod/tinytapeout.md). Which header is cabled to which port of the Pmod HAT,
with the picture: [which cable goes where](../wiring/cables.md).

Source: [TinyTapeout PCB Specs](https://tinytapeout.com/specs/pcb/)

## Clock

The RP2350 (RP2040 on version 2 boards) generates a 50 MHz clock via PWM on GPIO16
(`RP_PROJCLK`) — GPIO16 is the version 3 pin. The
iCE40UP5K's internal PLL divides this down to a 12 MHz system clock for
LiteX SoC designs (see the
[clock and reset generator](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_shared/tt_fpga_crg.py)).
The FPGA pin the clock arrives on: [the clock, the reset and the
LED](../wiring/pins-other.md#the-clock-the-reset-and-the-led).

## 7-Segment Display

The demo PCB includes a 7-segment LED display connected to the `uo_out` pins.
This provides immediate visual feedback from the FPGA design. These
share the same PMOD traces — when the RPi is driving GPIO tests, the display
reflects the test patterns. Which segment each `uo_out` signal lights, with its FPGA pin: [the seven-segment
display](../wiring/pins-other.md#the-seven-segment-display).

Source: [TinyTapeout PCB Specs](https://tinytapeout.com/specs/pcb/)

## DIP Switches

The demo PCB has DIP switches connected to the `ui_in` pins, allowing manual
input to the FPGA design during development and testing (no source is recorded for this; not verified by us).
How the switches must be set while the Raspberry Pi drives `ui_in` through the Pmod HAT is not recorded.
