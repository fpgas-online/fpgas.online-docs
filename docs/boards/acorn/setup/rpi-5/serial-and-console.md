---
type: explanation
owner: documentation maintainers
reader: someone asking why a Pi 5 with an Acorn is set up this way
review: 2026-11-10
---

# The serial port, the console and JTAG on a Raspberry Pi 5

This page explains why a Raspberry Pi 5 that carries an Acorn is set up as [the Pi's settings](pi-settings.md) say. It covers the serial pair, the kernel console and JTAG. The values to set are on the settings page. It gives no commands, which are in [How to run JTAG by hand on an Acorn on a Raspberry Pi 5](../../checks/jtag-by-hand.md).

## The serial pair is a crossover

The serial pair is a null-modem crossover. The FPGA's transmitter (K2) lands on the Pi's receiver (GPIO15 / RXD0), and the FPGA's receiver (J2) lands on the Pi's transmitter (GPIO14 / TXD0). This is the Raspberry Pi header convention that `/dev/ttyAMA0` uses, and the one the NeTV2 boards use ([NeTV2 primary UART](/boards/netv2.md#primary-uart-via-rpi-gpio)).

The RP1 chip of a Pi 5 offers its hardware UART0 only as GPIO14 = `TXD0` and GPIO15 = `RXD0`. `pinctrl funcs 14,15` lists no alternative where they swap. The RP1's PIO block (`/dev/pio0`, the `rp1_pio` module) could run a UART on any pin, but no driver for that exists in the test scripts. So the fleet uses the crossover everywhere, and one cable design works on every host.

## The overlay

A Pi 5 needs an explicit overlay for this UART. The file `bcm2712-rpi-5-b.dtb` ships the RP1 header UART (`serial0`) disabled. The `dtoverlay=disable-bt` line only touches Bluetooth on a Pi 5. Without `[pi5] dtoverlay=uart0-pi5` in `config.txt` there is no `/dev/ttyAMA0`. The Welland NFS root ([Raspberry Pi 5](../../../../setup/pi.md#raspberry-pi-5)) sets this and the console setting below, and its `verify-pi.yml --tags uart` play checks both.

## The kernel console

Enabling the overlay also makes `console=serial0` resolve to `ttyAMA0`, which would put the kernel console on the FPGA's serial pins. So the Pi 5s use `console=ttyAMA10`, the dedicated debug connector, through `[pi5] cmdline=cmdline-pi5.txt`. The getty that systemd derives from the console lands there too.

The FPGA drives K2 at its own baud rate, 1200 for pin-ID and 115200 for the UART SoC. A console on that UART reads the bytes as garbage, and some of them are SysRq commands such as `reboot(b)` and `crash(c)`. That is why SysRq is switched off with `kernel.sysrq=0` as well.

## JTAG

JTAG uses the Pi's SPI0 pins. On a Pi 5 `pinctrl` shows GPIO8-11 unclaimed even with the SPI modules loaded, so they do not have to be unloaded.

The 40-pin header is `/dev/gpiochip15`, but the `libgpiod` cable always opens `/dev/gpiochip0`. Without a link between the two, openFPGALoader fails with `JTAG init failed with: Unable to open gpio chip`. The link is made in devtmpfs, so it goes in again at each reboot. The `rp1pio` cable drives JTAG from the RP1's PIO block instead and needs `/dev/pio0`, which the check's `rp1-pio` test opens.
