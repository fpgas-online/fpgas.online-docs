# Kosagi NeTV2

The NeTV2 is a Xilinx Artix-7 video overlay and processing board designed by
bunnie (Andrew Huang) and produced by Alphamax/Kosagi. It stacks on a Raspberry
Pi's 40-pin header, and the fleet runs it in two arrangements: five production
boards on RPi 3B+ hosts driven entirely over GPIO JTAG and GPIO UART
([NeTV2](../sites/welland.md#netv2)), and two development boards on a separate
network that is not part of the fpgas.online fleet, one of which, the RPi 5
host, adds a PCIe Gen2 x1 link ([development hosts](netv2/hosts.md#development-hosts)).
Every NeTV2 in the fleet is at Welland. These pages cover the board itself, its
FPGA pin assignments for each on-board peripheral, how it is wired to its
Raspberry Pi, and how it is programmed and talked to.


Which do you need?

(key-specifications)=
(fpga-device-variants)=
- **[Device info](netv2/device.md):** for anyone who wants the board's FPGA,
  memory and connectors, and its two FPGA variants.
(host-connections)=
(development-hosts)=
- **[Host connections](netv2/hosts.md):** for anyone looking for which
  Raspberry Pi each NeTV2 sits on, and how to reach the two development hosts.
(jtag-via-rpi-gpio)=
(programming-with-openfpgaloader)=
(rpi-3b-gpio-bitbang-current-deployed-hosts)=
(rpi-5-gpio-bitbang-slow)=
(rpi-5-rp1-pio-jtag-not-in-upstream-openfpgaloader)=
(future-netv2-board-definition-in-openfpgaloader)=
(programming-with-openocd)=
- **[JTAG via RPi GPIO](netv2/jtag.md):** for someone loading a bitstream into
  the FPGA, or into its SPI flash, from the Pi with openFPGALoader or OpenOCD.
(serial-uart)=
(primary-uart-via-rpi-gpio)=
(serial-device-by-host)=
(rpi5-netv2-specifics)=
(rpi3-netv2-specifics)=
(uart-test-parameters)=
(secondary-uart-via-pcie-hax-pins)=
- **[Serial / UART](netv2/serial.md):** for someone talking to the FPGA's
  design over serial from the Pi: pins, the device on each Pi, what to stop.
(pmod-gpio-loopback)=
- **[PMOD / GPIO loopback](netv2/loopback.md):** for someone checking the GPIO
  wiring to the Pi with the loopback test.
(ddr3-sdram)=
- **[DDR3 SDRAM](netv2/ddr3.md):** for someone building or checking a design
  that uses the DDR3 memory.
(pcie)=
(lane-assignments)=
(pcie-detection-rpi5-netv2)=
- **[PCIe](netv2/pcie.md):** for someone building or checking a PCIe design,
  or looking for the board on rpi5-netv2's PCIe bus.
(rmii-ethernet)=
- **[RMII Ethernet](netv2/ethernet.md):** for someone building or checking a
  design that uses the board's own Ethernet port.
(hdmi)=
(hdmi-input-0)=
(hdmi-input-1)=
(hdmi-output-0)=
(hdmi-output-1)=
- **[HDMI](netv2/hdmi.md):** for someone building or checking a design that
  uses the two HDMI inputs or the two HDMI outputs.
(spi-flash)=
(sd-card)=
(spi-mode)=
(bit-mode)=
(user-leds)=
- **[SPI flash, SD card and user LEDs](netv2/flash-sd-leds.md):** for someone
  building or checking a design that uses any of these.
(programming)=
(quick-reference)=
(litex-integration)=
- **[Programming and LiteX](netv2/programming.md):** for someone who wants the
  programming commands at a glance, or the LiteX names for the board.
(references)=
- **[References](netv2/references.md):** for anyone looking for the sources
  behind these pages.

```{toctree}
:hidden:

Device info <netv2/device>
Host connections <netv2/hosts>
JTAG from the Pi <netv2/jtag>
Serial / UART <netv2/serial>
GPIO loopback <netv2/loopback>
DDR3 SDRAM <netv2/ddr3>
PCIe <netv2/pcie>
RMII Ethernet <netv2/ethernet>
HDMI <netv2/hdmi>
Flash, SD, LEDs <netv2/flash-sd-leds>
Programming, LiteX <netv2/programming>
References <netv2/references>
```

```{include} generated/install-netv2.md
```
