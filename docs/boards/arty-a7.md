# Digilent Arty A7

The Digilent Arty A7 is a Xilinx Artix-7 development board and the most numerous
FPGA board in the fleet: five at Welland ([Arty A7-35T](../sites/welland.md#arty-a7-35t))
and eight at PS1 ([Arty A7 hosts](../sites/ps1.md#arty-a7-hosts)). Each board
reaches its Raspberry Pi host over a single USB cable — an on-board FTDI
FT2232HQ gives the host both a JTAG channel and a UART channel — and, on hosts
fitted with a [PMOD HAT](pmod/rpi-hat.md), over three ribbon cables from the
HAT's PMOD ports to the Arty's own.

These pages cover the board itself, its FPGA pin assignments for every on-board
peripheral, how it is programmed, and the measured
[wiring to the Raspberry Pi](#wiring-to-the-raspberry-pi) including the
[PMOD cable routing](#pmod-cable-routing-hat--arty). Which host carries which
Arty is on the two site pages linked above.

```{include} generated/install-arty-a7.md
```

Which do you need?

(key-specifications)=
(fpga-device-variants)=
- **[Device info](arty-a7/device.md):** for you if you want the Arty A7's FPGA, memory and connectors, and which FPGA variant a board carries.
(serial-uart)=
- **[Serial (UART)](arty-a7/serial.md):** for you if you want to talk to a design on the Arty over its USB serial port.
(ddr3-sdram)=
- **[DDR3 SDRAM](arty-a7/ddr3.md):** for you if you are building or checking a design that uses the Arty's DDR3 memory.
(mii-ethernet)=
- **[MII Ethernet](arty-a7/ethernet.md):** for you if you are building or checking a design that uses the Arty's Ethernet port.
(pmod-connectors)=
(pmod-pin-numbering)=
(pmod-fpga-pin-assignments)=
(pmod-usage-in-test-infrastructure)=
- **[PMOD connectors](arty-a7/pmod.md):** for you if you want the Arty's PMOD pin numbering and FPGA pins, and how the test infrastructure uses them.
(spi-flash)=
- **[SPI flash](arty-a7/spi-flash.md):** for you if you are building or checking a design that uses the Arty's SPI flash.
(litex-integration)=
(programming)=
(via-openfpgaloader-usb-jtag)=
(via-openocd-usb-jtag)=
- **[Programming and LiteX](arty-a7/programming.md):** for you if you want to load a bitstream into the Arty from its Raspberry Pi, or the LiteX names for the board.
(wiring-to-the-raspberry-pi)=
(programming-interface)=
(uart-interface)=
(pmod-connectors-fpga-side)=
(pmoda)=
(pmodb)=
(pmodc)=
(pmodd-not-cabled-to-the-hat)=
- **[Wiring to the Raspberry Pi](arty-a7/wiring.md):** for you if you want to know how an Arty is joined to its Raspberry Pi: the USB cable's JTAG and UART, and the Arty's PMOD pins that the HAT's cables reach.
(pmod-cable-routing-hat--arty)=
(pi9-21-of-24-unique-gpios-scanned)=
(pi3)=
(pi5-offline)=
(unproven-lanes)=
(which-site-were-these-hosts-at)=
- **[PMOD cable routing, HAT to Arty](arty-a7/cable-routing.md):** for you if you want to know which Pmod HAT pin reaches which Arty PMOD pin on each host, as measured.
(gpio-loopback-test)=
(pre-test-requirements)=
- **[The GPIO loopback test](arty-a7/loopback.md):** for you if you want to run the GPIO loopback test between an Arty and its Raspberry Pi.
(references)=
- **[References](arty-a7/references.md):** for you if you want the sources behind these pages.

```{toctree}
:hidden:

Device info <arty-a7/device>
Serial (UART) <arty-a7/serial>
DDR3 SDRAM <arty-a7/ddr3>
MII Ethernet <arty-a7/ethernet>
PMOD connectors <arty-a7/pmod>
SPI flash <arty-a7/spi-flash>
Programming, LiteX <arty-a7/programming>
Wiring to the Pi <arty-a7/wiring>
PMOD cable routing <arty-a7/cable-routing>
GPIO loopback test <arty-a7/loopback>
References <arty-a7/references>
```
