---
type: explanation
owner: documentation maintainers
reader: someone who wants to know how a design reaches an Acorn on fpgas.online
review: 2026-11-10
---

# Programming an Acorn

This page explains how a design reaches an Acorn on fpgas.online, in three layers: the protocol, the connection and
the tool. It does not give the commands. They are on [How to run JTAG by hand on an Acorn on a Raspberry Pi 5](../checks/jtag-by-hand.md) and
[How to install the fpgas.online images on an Acorn](../setup/install-images.md). The card's own hardware is on
[Acorn specifications](specifications.md).

:::{admonition} Figure to come
:class: placeholder

The three layers: JTAG as the protocol, the host's GPIO pins to P1 or PCIe as the connection, openFPGALoader, OpenOCD and `spi_flash.py` as the tools. Tracked in [docs issue #122](https://github.com/fpgas-online/fpgas.online-docs/issues/122).
:::

## The protocol: JTAG

The Acorn is configured over JTAG. A load over JTAG lands in the FPGA's SRAM and is gone at the next power cycle.
A JTAG load works whatever the card has loaded.

Anything persistent has to go into the SPI flash. The command `openFPGALoader --write-flash` does not work over the
GPIO JTAG wiring, because its spiOverJtag bridge never toggles CCLK after configuration. Over that wiring JTAG can
only load volatile SRAM.

## The connection: GPIO pins to P1, or PCIe

PCIe comes through the M.2 slot of the host. JTAG, the serial pair and the spare wires are carried on two cables to
GPIO pins of the host. The wiring depends on the carrier the Pi sits in, which sets how many GPIOs it brings out, and
not on the site.

### GPIO pins to P1

On a [Raspberry Pi 5 with an M.2 HAT](../setup/rpi-5/wiring.md) the full 40-pin header is available:

- P2 goes to header pins 5-10 and P1 to header pins 19-26.
- JTAG has its own pins, `10:9:11:8` in the order TDI:TDO:TCK:TMS.
- The serial pair is on GPIO14/15, and both spare balls (J5, H5) are wired.
- libgpiod opens `gpiochip0`, so on a Pi 5 `/dev/gpiochip0` is a link to `/dev/gpiochip15`.

On a [Compute Blade with a CM4 or CM5](../setup/compute-blade/wiring.md) only GPIO2, 3, 4, 14 and 15 are brought out:

- P1 goes to the Extension Port, and JTAG is `2:3:4:14`: the I²C pair, GPIO4 and the UART TX line.
- P2's serial pair goes to the 4-pin UART header, and J5 and H5 are not connected.
- The UART header's TX pin is the same GPIO14 as TMS. The J2 wire has a 470 Ω resistor in it, so that JTAG wins by design; its measurement is [test-designs issue #221](https://github.com/fpgas-online/fpgas.online-test-designs/issues/221).
- The `gpiochip0` link of the Pi 5 is not made, and the PCIe bus address differs per blade.

On both carriers the serial pair lands on the same GPIOs: K2 (FPGA TX) on GPIO15 and J2 (FPGA RX) on GPIO14. One set of
FPGA pin constraints and one set of host scripts therefore serves every host.

The pin order and the Pi 5 link are in [JTAG from the Pi](../setup/rpi-5/pi-settings.md#jtag-from-the-pi). The
`overlayroot=tmpfs` trap is in [How to run JTAG by hand on an Acorn on a Raspberry Pi 5](../checks/jtag-by-hand.md). The blade is in
[JTAG on a blade](../checks/compute-blade-jtag-by-hand.md).

:::{warning}
Detach the PCIe endpoint before loading a bitstream. Reconfiguring the FPGA underneath an enumerated endpoint is a
surprise removal, and the BCM2712 root complex does not survive it: the host crashes. The rule, the per-host bus
address and bringing the endpoint back are in [why the endpoint is detached before a load](../checks/jtag-and-the-pcie-endpoint.md#why-the-endpoint-is-detached-before-a-load).
:::

### PCIe

PCIe programming only works on a board that is running a LiteX design with PCIe. With the fpgas.online Acorn design
running, the flash is written over PCIe BAR0 with `spi_flash.py`. That moves a board onto the golden and operational images, and updates the operational image. The steps are on
[How to install the fpgas.online images on an Acorn](../setup/install-images.md).

A board on the SQRL factory firmware or the vendor XDMA image first needs the design loaded into SRAM over JTAG. Which
bitstreams to use, and which prebuilt ones not to, is under [Images](design.md#images).

## The tools: openFPGALoader, OpenOCD and spi_flash.py

openFPGALoader bit-bangs JTAG through libgpiod; a full XC7A200T bitstream of 1.6 MB takes about 16 s. OpenOCD loads the
2.3 MB fpgas.online SoC over the same wiring in about 24 s. Both load to SRAM only, which is what makes it safe to
experiment with.

`spi_flash.py` is standard-library Python over BAR0 and needs no kernel module. It reads the 32 MiB flash in 58 s and
erases, writes and verifies a 4 MiB slot in about 20 s.

## The paths compared

Method names the path, Speed what it takes, Persistent whether the result survives a power cycle, and Requires what must
be in place first.

| Method                          | Speed                                            | Persistent | Requires                                                     |
|---------------------------------|--------------------------------------------------|------------|--------------------------------------------------------------|
| GPIO JTAG to SRAM               | 16 s (openFPGALoader, 1.6 MB); 24 s (OpenOCD, 2.3 MB) | No    | the P1 JTAG wiring, with the PCIe endpoint detached first    |
| PCIe to SPI flash, `spi_flash.py` | 58 s to read 32 MiB; about 20 s for a 4 MiB slot | Yes      | the fpgas.online Acorn design running, from flash or loaded into SRAM over JTAG |
| PCIe to SPI flash, `litepcie_util` | waits for its run: [test-designs issue #220](https://github.com/fpgas-online/fpgas.online-test-designs/issues/220) | Yes | a LiteX PCIe design and the `litepcie` kernel module |
