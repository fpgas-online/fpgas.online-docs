---
orphan: true
---

# Tiny Tapeout FPGA demo board (the old single page)

This page has been split, by task. Each part of it is now on the page named here; the whole tree is on
[Tiny Tapeout FPGA demo board](tt-fpga/index.md).

(installing-the-tt-fpga-packages)=
**Installing the TT FPGA packages and running the check**: [verifying 1](tt-fpga/building/verifying-1.md#installing-the-tt-fpga-packages).

(where-they-are)=
**Where they are**: [the boards at welland](tt-fpga/installations/welland.md), [the boards at ps1](tt-fpga/installations/ps1.md).

(key-specifications)=
(architecture)=
(fpga-device)=
(pmod-headers)=
(clock)=
(7-segment-display)=
(dip-switches)=
**Key specifications, architecture, the FPGA device, the Pmod headers, the clock, the seven-segment display and the DIP switches**: [device info](tt-fpga/overview/device-info.md). Demo board version 3 against version 2, and the FPGA breakout against a chip: [variants](tt-fpga/overview/variants.md).

(tinytapeout-io-interface)=
(serial-interface)=
(option-1-default-tt-uart)=
(option-2-alternate)=
**The Tiny Tapeout I/O interface and the two serial options**: [functionality](tt-fpga/overview/functionality.md).

(programming)=
(programming-interface)=
(programming-flow)=
(openfpgaloader-support-work-in-progress)=
**Programming: how a bitstream is loaded** (by streaming only): [functionality](tt-fpga/overview/functionality.md#programming).

(litex-integration)=
(references)=
**LiteX integration and references**: [resources and links](tt-fpga/overview/resources.md).

(board-firmware)=
(known-workarounds)=
(gpiomap-firmware-mismatch)=
(demoboard-hang-on-boot)=
(rp2350-pwm-first-call-bug)=
(spi-kernel-module-conflict)=
(rp2350-considerations)=
**Board firmware and the known workarounds**: [firmware and known workarounds](tt-fpga/designs/firmware.md).

(serial-port-ownership)=
**Serial port ownership** (the `fpgas-tt` daemon holds the board's serial port): [The Tiny Tapeout stack](../setup/tinytapeout.md#serial-port-ownership).

(test-infrastructure)=
(available-tests)=
(test-execution)=
**Test infrastructure**: one page for each test: [Pmod pin ID](tt-fpga/designs/pmod-pin-id.md), [Pmod loopback](tt-fpga/designs/pmod-loopback.md), [UART](tt-fpga/designs/uart.md); the breakout has [no SPI flash](tt-fpga/overview/device-info.md#no-spi-flash), so no SPI flash ID test. Running them from a workstation with `verify_hardware.py`: [Verifying a deployment](../setup/verification.md#running-the-hardware-tests). What the public site loads: [demos](tt-fpga/designs/demos.md).

(pin-mapping)=
(ui_in)=
(uo_out)=
(uio)=
(rp2350-spi-programming-pins)=
(7-segment-display-pins)=
(other-signals)=
**Pin mapping**: the hand-written tables are gone; the wiring is generated from one source: [which cable goes where](tt-fpga/wiring/cables.md), [`ui_in` and `uo_out`](tt-fpga/wiring/pins-ui-uo.md), [`uio` and the serial port](tt-fpga/wiring/pins-uio-uart.md), [the loading pins, display, clock, reset and LED](tt-fpga/wiring/pins-other.md), [sources](tt-fpga/wiring/sources.md). The old tables had `ui_in` on HAT JC and `uo_out` on HAT JA; the measured cabling is `ui_in` on JA and `uo_out` on JC.

(uart-interface)=
(access-via-the-rp2350-usb-bridge-recommended)=
(access-via-rpi-gpio-not-currently-feasible)=
**UART interface**: [the UART test](tt-fpga/designs/uart.md) and [the serial port's pins](tt-fpga/wiring/pins-uio-uart.md#the-serial-port-uart).

(pmod-loopback)=
**PMOD loopback**: [the Pmod loopback test](tt-fpga/designs/pmod-loopback.md).

(spi-flash)=
**SPI flash**: the breakout has none: [no SPI flash](tt-fpga/overview/device-info.md#no-spi-flash).
