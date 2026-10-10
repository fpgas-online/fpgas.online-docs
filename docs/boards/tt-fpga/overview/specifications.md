---
type: reference
owner: documentation maintainers
reader: someone looking up a figure of the board
review: 2026-11-10
---

# Tiny Tapeout FPGA demo board specifications

**You want to look up a figure of the board: its FPGA, interface, clock, display, switches or programming interface.**

The board as a whole is on [The Tiny Tapeout FPGA demo board](board.md). Its signal-by-signal pins are on [Tiny Tapeout FPGA demo board pin mapping](pin-mapping.md). The figures follow the Tiny Tapeout [PCB specifications](https://tinytapeout.com/specs/pcb/) and [FPGA breakout guide](https://tinytapeout.com/guides/fpga-breakout/).

## Key specifications

Parameter names the figure, and Value gives it.

| Parameter | Value |
|-----------|-------|
| FPGA | Lattice iCE40UP5K-SG48 (on FPGA breakout board) |
| Package | SG48 (48-pin QFN) |
| Logic cells | 5,280 LUT4s |
| SPRAM | 128 KB (4 x 32 KB blocks) |
| Block RAM (EBR) | 120 Kbit (15 KB total) |
| Clock | 50 MHz from RP2350 PWM (GPIO16) |
| Toolchain | icestorm / nextpnr-ice40 (open source); Yosys + nextpnr-ice40, IceStorm flow |
| Controller | RP2350B (on demo PCB) |
| USB | USB-C (via the controller) |
| Display | 7-segment LED display |
| DIP switches | Configuration switches |
| PMOD headers | 3 (2x standard PMOD following the Digilent spec, and the bidirectional `uio` one) |
| I/O voltage | 3.3V |

## Tiny Tapeout I/O interface

The FPGA implements a Tiny Tapeout compatible interface. Signal Group names the signals, Width their count, Direction the direction seen from the FPGA, and Description what they carry.

| Signal Group | Width | Direction | Description |
|-------------|-------|-----------|-------------|
| `ui_in[7:0]` | 8 bits | Input | User inputs (directly from DIP switches or RP2350) |
| `uo_out[7:0]` | 8 bits | Output | User outputs (directly to 7-segment display or RP2350) |
| `uio[7:0]` | 8 bits | Bidirectional | User bidirectional I/O |
| `ena` | 1 bit | Input | Enable signal |
| `clk` | 1 bit | Input | Clock |
| `rst_n` | 1 bit | Input | Active-low reset |

## Serial interface

The board supports UART communication through the Tiny Tapeout I/O pins, in two pin configurations. Signal is the UART signal, TT Pin the Tiny Tapeout pin that carries it, and Direction the direction from the FPGA's perspective.

### Option 1 (Default TT UART)

| Signal | TT Pin | Direction (FPGA perspective) |
|--------|--------|------------------------------|
| RX | ui_in[3] | Input |
| TX | uo_out[4] | Output |

### Option 2 (Alternate)

| Signal | TT Pin | Direction (FPGA perspective) |
|--------|--------|------------------------------|
| RX | ui_in[7] | Input |
| TX | uo_out[0] | Output |

The RP2350 on the demo PCB can act as a USB-to-UART bridge, forwarding serial data between the USB-C port and the FPGA's UART pins.

## PMOD headers

The demo PCB has three PMOD headers, one per signal group. Two follow the [Digilent specification](../../pmod/index.md), which the Tiny Tapeout PCB specification calls standard, and the third is the bidirectional (`uio`) one.

- Each header is a 12-pin connector (8 signal + 2 GND + 2 VCC).
- Signal voltage is 3.3V.
- The PMOD signals are routed through the Tiny Tapeout bidirectional I/O (`uio`) or directly to the FPGA breakout board.
- The layouts Tiny Tapeout recommends for the headers are on [Tiny Tapeout PMOD layouts](../../pmod/tinytapeout.md).

## Clock

The RP2350 generates a 50 MHz clock via PWM on GPIO16 (`RP_PROJCLK`). The iCE40UP5K's internal PLL divides it down to a 12 MHz system clock for LiteX SoC designs, as the [clock and reset generator](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_shared/tt_fpga_crg.py) shows.

## 7-segment display

The demo PCB has a 7-segment LED display connected to the `uo_out` pins. Segment names the display segment, and TT Output Pin the output that drives it.

| Segment | TT Output Pin |
|---------|--------------|
| a | uo_out[0] |
| b | uo_out[1] |
| c | uo_out[2] |
| d | uo_out[3] |
| e | uo_out[4] |
| f | uo_out[5] |
| g | uo_out[6] |
| dp | uo_out[7] |

The iCE40 ball behind each segment is on [Tiny Tapeout FPGA demo board pin mapping](pin-mapping.md#7-segment-display-pins).

## DIP switches

The demo PCB has DIP switches connected to the `ui_in` pins, which allow manual input to the FPGA design during development and testing.

## Programming interface

The iCE40 is programmed through the RP2350 over USB CDC, not directly from the Raspberry Pi. Parameter names the interface item, and Value gives it. How the steps run is on [Programming a Tiny Tapeout FPGA demo board](programming.md).

| Parameter | Value |
|-----------|-------|
| Interface | RP2350 PIO SPI → iCE40 SPI configuration port |
| USB device | `/dev/ttyACM0` (MicroPython REPL) |
| USB VID:PID | `2e8a:0005` (MicroPython Board in FS mode) |
| Bitstream type | `.bin` (volatile SRAM load) |
| SPI clock | 1 MHz |

### RP2350 SPI programming pins

Signal names the SPI signal, RP2350 GPIO the controller pin that drives it, and Function what the signal does.

| Signal | RP2350 GPIO | Function |
|--------|-------------|----------|
| SCK | GPIO6 | SPI clock |
| MOSI | GPIO3 | SPI data out |
| SS | GPIO5 | SPI chip select |
| CRESET_B | GPIO1 | iCE40 configuration reset |
