# Fomu EVT

The Fomu is a tiny FPGA board that fits inside a USB Type-A port, designed by
Sean Cross (xobs) and Tim Ansell; the EVT (Engineering Validation Test) revision
is the one used in the fpgas.online test infrastructure. It is built around a
Lattice iCE40UP5K with native USB: the FPGA has dedicated USB I/O pins, so there
is no external PHY and no FTDI. The board therefore enumerates as a USB device
by itself, and it is programmed over USB DFU rather than over JTAG. Two boards
are installed, both at Welland, on Raspberry Pi 3B+ hosts with a USB protocol
analyser inline; their addresses, MACs and analysers are in the
[Fomu EVT host table](../sites/welland.md#fomu-evt). These pages cover the board
itself, its iCE40 pin assignments for each on-board peripheral, how it is
programmed and monitored, and how it is wired to its Raspberry Pi.

Which do you need?

(key-specifications)=
- **[Device info](fomu-evt/device.md):** for you if you want the Fomu EVT's FPGA, memory and connectors.
(usb-interface)=
(serial-uart)=
- **[USB and serial (UART)](fomu-evt/usb-serial.md):** for you if you want the Fomu's native USB pins and how a design talks over its serial port.
(spi-flash)=
(rgb-led)=
(touch-pads)=
(buttons)=
(pmod-connectors)=
(pmoda_n)=
(pmodb_n)=
(i2c)=
(debug-header)=
- **[SPI flash, RGB LED, touch pads, buttons, PMOD, I2C and debug header](fomu-evt/peripherals.md):** for you if you are building or checking a design that uses one of the Fomu's on-board peripherals or its PMOD pins.
(programming)=
(usb-dfu-dfu-util)=
(icestorm-programmer-iceprog)=
(litex-integration)=
- **[Programming and LiteX](fomu-evt/programming.md):** for you if you want to load a bitstream into a Fomu over USB DFU or iceprog, or the LiteX names for the board.
(usb-monitoring)=
(openvizsla-pi17)=
(cythionluna-pi21)=
(cythion-luna-pi21)=
- **[USB monitoring](fomu-evt/usb-monitoring.md):** for you if you want to watch a Fomu's USB traffic with the analyser inline on its host.
(wiring-to-the-raspberry-pi)=
(physical-form-factor)=
(programming-interface)=
(dfu-bootloader-timeout)=
(usb-connection-to-the-pi)=
(uart-interface)=
(uart-pre-test-requirements)=
(other-signals)=
- **[Wiring to the Raspberry Pi](fomu-evt/wiring.md):** for you if you want to know how a Fomu is joined to its Raspberry Pi: the USB port, the DFU bootloader, the UART and the other signals.
(pmod--gpio-loopback)=
(pmoda_n-loopback-input)=
(pmodb_n-loopback-output)=
(confirmed-loopback-pair)=
(loopback-pre-test-requirements)=
- **[The PMOD / GPIO loopback test](fomu-evt/loopback.md):** for you if you want to run the PMOD / GPIO loopback test between a Fomu and its Raspberry Pi.
(references)=
- **[References](fomu-evt/references.md):** for you if you want the sources behind these pages.

```{include} generated/install-fomu-evt.md
```

```{toctree}
:hidden:

Device info <fomu-evt/device>
USB and serial <fomu-evt/usb-serial>
Flash, LED, pads, PMOD <fomu-evt/peripherals>
Programming, LiteX <fomu-evt/programming>
USB monitoring <fomu-evt/usb-monitoring>
Wiring to the Pi <fomu-evt/wiring>
PMOD / GPIO loopback <fomu-evt/loopback>
References <fomu-evt/references>
```
