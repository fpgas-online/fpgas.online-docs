# Tiny Tapeout FPGA board: functionality

**You want to know what a design on a Tiny Tapeout FPGA demo board has to work with (its signals and its
serial port) and how a bitstream is loaded into the FPGA from the board's Raspberry Pi.** What is on the
board is on [device info](device-info.md); each wire is on the [wiring pages](../wiring/cables.md).

## TinyTapeout I/O Interface

The FPGA implements a TinyTapeout-compatible interface with the following
signals:

| Signal Group | Width | Direction | Description |
|-------------|-------|-----------|-------------|
| `ui_in[7:0]` | 8 bits | Input | User inputs (from the Raspberry Pi through the Pmod HAT, the DIP switches or the RP2350) |
| `uo_out[7:0]` | 8 bits | Output | User outputs (directly to 7-segment display or RP2350) |
| `uio[7:0]` | 8 bits | Bidirectional | User bidirectional I/O |
| `ena` | 1 bit | Input | Enable signal |
| `clk` | 1 bit | Input | Clock (up to ~66 MHz) |
| `rst_n` | 1 bit | Input | Active-low reset |

Source: [TinyTapeout PCB Specs](https://tinytapeout.com/specs/pcb/); the Raspberry Pi in the `ui_in` row is
ours ([`ui_in` and `uo_out`](../wiring/pins-ui-uo.md)).

**The clock.** "Up to ~66 MHz" is the specification's maximum (Tiny Tapeout PCB specs; not measured by us on
a version 3 board). The clock the board actually gets is 50 MHz on the RP2350's GPIO16, started by our loader
with `--gpio-release` and by the UART test's bridge (`tt_fpga_program.py`, `tt_test_wrapper.py`).

Each group is on its own Pmod header and reaches the Raspberry Pi through the Pmod HAT: `ui_in` on the INPUT
header to port JA, `uio` on BIDIR to JB, `uo_out` on OUTPUT to JC. Wire by wire:
[`ui_in` and `uo_out`](../wiring/pins-ui-uo.md), [`uio`](../wiring/pins-uio-uart.md).

### Who can drive `ui_in`

Three things are on the eight `ui_in` signals, and the pages say each of them drives them:

- **The Raspberry Pi**, through the Pmod HAT's port JA. The cable picture's "the Pi drives" means this: in
  our tests the Pi drives `ui_in` and the FPGA reads it ([`ui_in` and `uo_out`](../wiring/pins-ui-uo.md)).
- **The demo board's microcontroller.** Its GPIO17 to GPIO24 are on the same signals. Our serial bridge
  sends on one of them, `ui_in[3]`, from its GPIO20 ([the UART test](../designs/uart.md)). A load made with
  `--gpio-release` sets all 24 of its signal pins to inputs, so that only the FPGA and the Pi drive them
  (below).
- **The DIP switches**, according to Tiny Tapeout's specification (the table above); not verified by us.
  How the switches must be set while the Pi or the microcontroller drives `ui_in` is not recorded.

Two of them driving one signal at once fight each other.

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
| USB VID:PID    | below the table |
| Tool           | `tt_fpga_program.py --gpio-release /dev/ttyACM0 <bitstream>` (by hand, below) |
| Bitstream type | `.bin` (volatile SRAM load)                           |

The microcontroller pins the loader drives, and the iCE40's configuration pins: [the pins that load the
FPGA](../wiring/pins-other.md#loading-the-fpga-its-configuration-pins).

```{include} ../usb-ids.inc
```

### By hand

Read these three things before the command:

1. **The serial port.** On a host of the public site the `fpgas-tt` daemon holds the board's serial port,
   so it is stopped around the load and started again after (why: [Serial port
   ownership](../../../setup/tinytapeout.md#serial-port-ownership)).
2. **`--gpio-release`, or the Pi and the microcontroller fight.** The microcontroller shares the same
   physical traces as the Pmod headers. Without `--gpio-release` the loader leaves its 24 signal pins as they
   were, and starts no clock. With it, the loader starts the 50 MHz clock on GPIO16 and sets GPIO17 to GPIO40
   (`ui_in`, `uio`, `uo_out`) to inputs (source: `tt_fpga_program.py` on the record branch). Before anything
   on the Pi drives a Pmod pin, load with `--gpio-release`.
3. **What you need.** The loader is `designs/_host/tt_fpga_program.py` in a checkout of
   [fpgas.online-test-designs](https://github.com/fpgas-online/fpgas.online-test-designs); the packages
   carry a copy for the check's own use, at a path these pages do not record. The packaged test bitstreams
   are in `/usr/share/fpgas-online/tt-fpga/bitstreams/` (one directory for each design, each holding
   `tt_fpga_platform.bin`: [verifying 1](../building/verifying-1.md)).

```console
# The fpgas-tt daemon holds the serial port open; stop it before programming
# by hand, and start it again afterwards or the board drops off the public site.
$ sudo systemctl stop fpgas-tt
# From the top of a checkout of fpgas.online-test-designs:
$ python3 designs/_host/tt_fpga_program.py --gpio-release /dev/ttyACM0 \
    /usr/share/fpgas-online/tt-fpga/bitstreams/uart-test-tt-fpga/tt_fpga_platform.bin
$ sudo systemctl start fpgas-tt
```

Not run by us in this form: the old page gave `python3 designs/_host/tt_fpga_program.py /dev/ttyACM0
bitstream.bin`; the flag and the packaged path are from the record (the loader's `--help`, and the check's
`boards/tt_fpga.py`, which names `uart-test-tt-fpga/tt_fpga_platform.bin`).

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
3. Only with `--gpio-release` (the Pmod tests): start the 50 MHz clock on GPIO16, and release all GPIO pins
   to high-Z. All `ui_in`, `uo_out` and `uio` pins are set to `Pin.IN`. This is critical: the
   controller shares the same physical traces as the PMOD headers, so without
   releasing them its output drivers contend with the RPi's GPIO signals coming
   through the PMOD HAT. Without the flag the loader starts no clock; the UART test's bridge
   (`tt_test_wrapper.py`) starts the clock itself.

After step 3 the RPi has clean access to the FPGA through the PMOD HAT, and the Pmod tests run the same way
as on any other board. The UART test does not: its serial port goes through the demo board's microcontroller
and the USB-C cable, not through the Pi's own UART as on the Arty and the Fomu ([the UART
test](../designs/uart.md)).

### From the public site

On a board of the public site the bitstream-loading and design-listing features live in the `fpgas-tt`
daemon, which is what the site uses: [what the public site loads](../designs/demos.md).

### openFPGALoader support (work in progress)

Direct programming of the iCE40 via openFPGALoader (bypassing the MicroPython
REPL) is being developed. This would allow faster, more reliable programming
without needing `mpremote`. The work is in the
[tt-fpga-support branch of mithro/openFPGALoader](https://github.com/mithro/openFPGALoader/tree/tt-fpga-support).
