---
type: explanation
owner: documentation maintainers
reader: someone who wants to know how a design reaches the FPGA
review: 2026-11-10
---

# Programming a Tiny Tapeout FPGA demo board

**You want to know how a bitstream gets from a Raspberry Pi into the iCE40UP5K of a Tiny Tapeout FPGA demo board.**

This page keeps the protocol, the connection and the tools apart. The pins are on [Tiny Tapeout FPGA demo board specifications](specifications.md#programming-interface). The port a tool must own is explained on [Serial port ownership on a Tiny Tapeout FPGA demo board](serial-port.md).

:::{admonition} Figure to come
:class: placeholder

The three layers: iCE40 SPI configuration as the protocol, USB-C and RP2350 GPIO as the connection, host scripts and daemon as the tools. Tracked in [test-designs issue #256](https://github.com/fpgas-online/fpgas.online-test-designs/issues/256).
:::

## The protocol

The iCE40UP5K is configured over its SPI configuration port. The bitstream is a `.bin` file, and a load is volatile: it goes into the FPGA's SRAM. The RP2350 asserts CRESET_B low and then high, which resets the iCE40 into configuration mode. It then streams the bitstream over SPI. Nothing reads the FPGA's CDONE afterwards (the tools, below).

## The connection

The iCE40 is programmed through the RP2350 on the demo PCB, over USB CDC, and not directly from the Raspberry Pi. The Raspberry Pi reaches the RP2350 over USB-C as the serial port `/dev/ttyACM0`, which shows the MicroPython REPL. The RP2350 drives the iCE40 configuration port with SCK on GPIO6, MOSI on GPIO3, SS on GPIO5 and CRESET_B on GPIO1.

After every load, the RP2350 starts the 50 MHz clock on GPIO16 and then releases its GPIO pins to high impedance: the SPI pins and all `ui_in`, `uo_out` and `uio` pins (GPIO17 to GPIO40) become inputs with no pull. This is critical, because the controller shares the same physical traces as the PMOD headers. Without the release its output drivers contend with the Raspberry Pi's GPIO signals coming through the PMOD HAT.

## The tools

The check loads every design with `openFPGALoader -b tt_fpga -d /dev/ttyACM0 <bitstream>`, from the [fpgas.online-fpga-tools](https://github.com/fpgas-online/fpgas.online-fpga-tools) build (`openfpgaloader-fpgasonline` or `-git`, build 0.0.post105 or later; Debian's own openFPGALoader has no `tt_fpga` board). It enters the RP2350's MicroPython raw REPL, asserts CRESET (GPIO1) and streams the bitstream over SPI (SCK=GPIO6, MOSI=GPIO3, SS=GPIO5). It then releases CRESET with a pull-up, starts the clock and releases the pins. CDONE is not read ([fpga-tools issue #17](https://github.com/fpgas-online/fpgas.online-fpga-tools/issues/17)): the tests that follow are what show the design runs. It exits non-zero when the stream, the clock or the release fails, and prints `SRAM programming complete` when all of it worked. A load takes about 20 s ([fpga-tools issue #16](https://github.com/fpgas-online/fpgas.online-fpga-tools/issues/16)). Those are the v3 pin values, hardcoded for `TTDBv3`.

On the host side, the `fpgas-tt` daemon on the Raspberry Pi loads bitstreams for the public site. The check's tools, `fpgas-tt-fpga-verify` and `fpgas-tt-fpga-debug test ...`, load the test designs: [How to install the Tiny Tapeout FPGA packages](../setup/packages.md). Their package needs the fpgas.online-fpga-tools repository added first, on every release, for its openFPGALoader ([installing fpgas-verify, step 2](../../../verify/installing.md#installing)). They stream the bitstream to the FPGA through the RP2350, and store nothing on the board. The check's page says it this way: "Like every load it is streamed: nothing is stored on the board" ([fpgas-verify: the Tiny Tapeout demo boards](../../../verify/tt-fpga.md#what-the-tt-fpga-is-left-running)).

Loading a design of your own by hand, and recovering a hung board, without a file write is [fpgas.online-tt issue #21](https://github.com/fpgas-online/fpgas.online-tt/issues/21). What the daemon's own loading does to the board is in the same issue. The test-designs scripts are listed on [Tiny Tapeout FPGA demo board test designs](../checks/test-designs.md). The UART test wrapper first calls its `reset_rp2350()`, which sends Ctrl-C to break any stuck MicroPython script, and retries after a USB power cycle.

Once the FPGA is programmed, the Raspberry Pi has clean access to it through the PMOD HAT. Programming is the only Tiny Tapeout specific step.
