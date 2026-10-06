# Tiny Tapeout FPGA board: functionality

**You want to know what a design on a Tiny Tapeout FPGA demo board has to work with (its signals and its
serial port) and how a bitstream is loaded into the FPGA from the board's Raspberry Pi.** What is on the
board is on [device info](device-info.md); each wire is on the [wiring pages](../wiring/cables.md).

## TinyTapeout I/O Interface

The FPGA implements a TinyTapeout-compatible interface with the following
signals:

| Signal Group | Width | Direction | Description |
|-------------|-------|-----------|-------------|
| `ui_in[7:0]` | 8 bits | Input | User inputs (directly from DIP switches or RP2350) |
| `uo_out[7:0]` | 8 bits | Output | User outputs (directly to 7-segment display or RP2350) |
| `uio[7:0]` | 8 bits | Bidirectional | User bidirectional I/O |
| `ena` | 1 bit | Input | Enable signal |
| `clk` | 1 bit | Input | Clock (up to ~66 MHz) |
| `rst_n` | 1 bit | Input | Active-low reset |

Source: [TinyTapeout PCB Specs](https://tinytapeout.com/specs/pcb/)

Each group is on its own Pmod header and reaches the Raspberry Pi through the Pmod HAT: `ui_in` on the INPUT
header to port JA, `uio` on BIDIR to JB, `uo_out` on OUTPUT to JC. Wire by wire:
[`ui_in` and `uo_out`](../wiring/pins-ui-uo.md), [`uio`](../wiring/pins-uio-uart.md).

## Serial Interface

The TT FPGA board supports UART communication through the TinyTapeout I/O pins.
Two serial pin configurations are available:

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

The RP2350 on the demo PCB can act as a USB-to-UART bridge, forwarding serial
data between the USB-C port and the FPGA's UART pins.

Source: [TinyTapeout PCB Specs](https://tinytapeout.com/specs/pcb/)

Our test design and its serial bridge use option 1; option 2 has not been used by us. The pins and how the
port is reached: [the serial port](../wiring/pins-uio-uart.md#the-serial-port-uart) and [the UART
test](../designs/uart.md).

## Programming

```{include} ../generated/tt-fpga-pins-other.md
:start-after: "### Loading the FPGA: its configuration pins"
:end-before: "The FPGA breakout has no SPI flash"
```

The RP2350 (RP2040 on version 2 boards) programs the iCE40UP5K over SPI using the
`fabricfox` MicroPython module (PIO-accelerated or bitbang fallback).
The iCE40 is programmed via the RP2350 over USB CDC, not directly from the RPi.

| Parameter      | Value                                                 |
| -------------- | ----------------------------------------------------- |
| Interface      | RP2350 PIO SPI → iCE40 SPI configuration port         |
| USB device     | `/dev/ttyACM0` (MicroPython REPL)                     |
| USB VID:PID    | `2e8a:0005` (MicroPython Board in FS mode)            |
| Tool           | `python3 tt_fpga_program.py /dev/ttyACM0 <bitstream>` |
| Bitstream type | `.bin` (volatile SRAM load)                           |

The microcontroller pins the loader drives, and the iCE40's configuration pins: [the pins that load the
FPGA](../wiring/pins-other.md#loading-the-fpga-its-configuration-pins).

### By hand

On a host of the public site the `fpgas-tt` daemon holds the board's serial port, so it is stopped around
the load (why: [Serial port ownership](../../../setup/tinytapeout.md#serial-port-ownership)):

```console
# The fpgas-tt daemon holds the serial port open; stop it before programming
# by hand, and start it again afterwards or the board drops off the public site.
$ sudo systemctl stop fpgas-tt
$ python3 designs/_host/tt_fpga_program.py /dev/ttyACM0 bitstream.bin
$ sudo systemctl start fpgas-tt
```

### Programming flow

1. The loader shows the RP2350 a copy of the bitstream that stays on the Pi, served over the serial link
   (`mpremote mount`). **Nothing is written to the demo board's filesystem**: no file is copied to it and no
   directory is made on it (source: the
   [Programming section of the board's page in fpgas.online-test-designs](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/tt-fpga.md#programming)).
   The
   [UART test wrapper](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/_host/tt_test_wrapper.py) additionally calls
   its `reset_rp2350()` (Ctrl-C to break any stuck MicroPython script) and
   retries after a USB power cycle.
2. Enter raw REPL and execute a MicroPython script that:
   - Asserts `CRESET` (GPIO1) to reset the FPGA
   - Transfers the bitstream over SPI (SCK=GPIO6, MOSI=GPIO3, SS=GPIO5 — the
     version 3 values, hardcoded as `TTDBv3` in the programming script), streamed via PIO SPI at 1 MHz
   - Releases `CRESET` (`CDONE` is not read: the tests that follow are what show the design is running)
   - Starts the 50 MHz clock on GPIO16
3. For PMOD tests: release all GPIO pins to high-Z (`--gpio-release`). All
   `ui_in`, `uo_out` and `uio` pins are set to `Pin.IN`. This is critical: the
   controller shares the same physical traces as the PMOD headers, so without
   releasing them its output drivers contend with the RPi's GPIO signals coming
   through the PMOD HAT.

After step 3 the RPi has clean access to the FPGA through the PMOD HAT, and
tests run the same way as on any other board — UART and PMOD tests work
identically to Arty and Fomu once the FPGA is programmed. Programming is the
only TT-specific step.

### From the public site

On a board of the public site the bitstream-loading and design-listing features live in the `fpgas-tt`
daemon, which is what the site uses: [what the public site loads](../designs/demos.md).

### openFPGALoader support (work in progress)

Direct programming of the iCE40 via openFPGALoader (bypassing the MicroPython
REPL) is being developed. This would allow faster, more reliable programming
without needing `mpremote`. The work is in the
[tt-fpga-support branch of mithro/openFPGALoader](https://github.com/mithro/openFPGALoader/tree/tt-fpga-support).
