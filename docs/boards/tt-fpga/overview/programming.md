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

The iCE40UP5K is configured over its SPI configuration port. The bitstream is a `.bin` file, and a load is volatile: it goes into the FPGA's SRAM. The RP2350 asserts CRESET_B low and then high, which resets the iCE40 into configuration mode. It then streams the bitstream over SPI at 1 MHz and waits for the FPGA's CDONE.

## The connection

The iCE40 is programmed through the RP2350 on the demo PCB, over USB CDC, and not directly from the Raspberry Pi. The Raspberry Pi reaches the RP2350 over USB-C as the serial port `/dev/ttyACM0`, which shows the MicroPython REPL. The RP2350 drives the iCE40 configuration port with SCK on GPIO6, MOSI on GPIO3, SS on GPIO5 and CRESET_B on GPIO1.

After the load, the RP2350 starts the 50 MHz clock on GPIO16. For a PMOD test it then releases all its GPIO pins to high impedance, which the tools do with `--gpio-release`. All `ui_in`, `uo_out` and `uio` pins are set to `Pin.IN`. This is critical, because the controller shares the same physical traces as the PMOD headers. Without the release its output drivers contend with the Raspberry Pi's GPIO signals coming through the PMOD HAT.

## The tools

The RP2350 runs the `fabricfox` MicroPython module, which is PIO-accelerated with a bitbang fallback. A MicroPython script in the raw REPL asserts CRESET (GPIO1) and transfers the bitstream over SPI (SCK=GPIO6, MOSI=GPIO3, SS=GPIO5). It then releases CRESET, waits for CDONE and starts the clock. Those are the v3 values, hardcoded as `TTDBv3` in the programming script.

On the host side, the `fpgas-tt` daemon on the Raspberry Pi loads bitstreams for the public site. The check's tools, `fpgas-tt-fpga-verify` and `fpgas-tt-fpga-debug test ...`, load the test designs: [How to install the Tiny Tapeout FPGA packages](../setup/packages.md). They stream the bitstream to the FPGA through the RP2350, and store nothing on the board. The check's page says it this way: "Like every load it is streamed: nothing is stored on the board" ([fpgas-verify: the Tiny Tapeout demo boards](../../../verify/tt-fpga.md#what-the-tt-fpga-is-left-running)).

Loading a design of your own by hand, and recovering a hung board, without a file write is [fpgas.online-tt issue #21](https://github.com/fpgas-online/fpgas.online-tt/issues/21). The test-designs scripts are listed on [Tiny Tapeout FPGA demo board test designs](../checks/test-designs.md). The UART test wrapper also calls its `reset_rp2350()`, which sends Ctrl-C to break any stuck MicroPython script, and retries after a USB power cycle.

Once the FPGA is programmed, the Raspberry Pi has clean access to it through the PMOD HAT. Tests then run the same way as on any other board. UART and PMOD tests work identically to the Arty and the Fomu. Programming is the only Tiny Tapeout specific step.
