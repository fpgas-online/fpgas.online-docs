# NeTV2: JTAG via RPi GPIO

**You have a NeTV2 on a Raspberry Pi and want to load a bitstream into its FPGA, or write one to its SPI flash, over the Pi's GPIO JTAG.**

The NeTV2 JTAG interface is directly wired to specific Raspberry Pi GPIO pins.
The GPIO-to-JTAG pin mapping originates from the
[alphamax-rpi OpenOCD configuration](https://github.com/alphamaxmedia/netv2mvp-scripts/blob/master/alphamax-rpi.cfg)
in the NeTV2 MVP scripts.

| JTAG Signal | RPi GPIO | RPi Header Pin | Direction (from RPi) |
| ----------- | -------- | -------------- | -------------------- |
| TCK         | GPIO4    | Pin 7          | Output               |
| TMS         | GPIO17   | Pin 11         | Output               |
| TDI         | GPIO27   | Pin 13         | Output               |
| TDO         | GPIO22   | Pin 15         | Input                |
| SRST        | GPIO24   | Pin 18         | Output               |

## Programming with openFPGALoader

openFPGALoader is the primary tool for programming the NeTV2. It supports
multiple JTAG transports over the same GPIO wiring.

### RPi 3B+ (GPIO bitbang, current deployed hosts)

On the five production RPi 3B+ hosts (pi-sw1-p10, p12, p14, p16 and p18 — all
online and JTAG-verified 2026-09-06; see [NeTV2](../../sites/welland.md#netv2)),
openFPGALoader uses `libgpiod` to drive the JTAG signals through the Linux GPIO
subsystem:

```console
$ sudo openFPGALoader --cable libgpiod --pins 27:22:4:17 design.bit
```

To write the bitstream to the on-board SPI flash so it survives a power cycle:

```console
$ sudo openFPGALoader --cable libgpiod --pins 27:22:4:17 --write-flash design.bit
```

Pin order: `TDI:TDO:TCK:TMS`.

This works but is slow (~5 MHz effective JTAG clock) due to GPIO bitbang
overhead.

:::{warning}
On these hosts the FPGA's serial-TX pin is the Pi's kernel-console UART. Until
[infra PR #75](https://github.com/fpgas-online/fpgas.online-infra/pull/75)
(deployed 2026-09-06) a bitstream that drove that line crashed the netbooted Pi
via SysRq. Boards that netbooted after that fix are safe (`kernel.sysrq` reads
0 and the cmdline has no `console=serial0`); if you meet one that has not been
re-cycled, set `sudo sysctl -w kernel.sysrq=0` before programming. See the
[NeTV2 site notes](../../sites/welland.md#netv2).
:::

:::{note}
**Confirmed 2026-09-06**: the production RPi 3B+ hosts program with
openFPGALoader `libgpiod`, exactly the command above. All five (pi-sw1-p10, p12,
p14, p16, p18) ran
`sudo openFPGALoader --cable libgpiod --pins 27:22:4:17 --detect` and enumerated
their Artix-7 XC7A35T (`idcode 0x0362d093`, IR length 6); p14 and p16 were also
loaded with a real bitstream this way. The netboot image ships openFPGALoader
and has no `~/netv2/` OpenOCD config, so the "programmed via OpenOCD" line in the
2026-03-17 inventory was the stale one — the GPIO-to-JTAG wiring is identical
either way. See [NeTV2](../../sites/welland.md#netv2).
:::

### RPi 5 (GPIO bitbang, slow)

:::{warning}
Reconfiguring the FPGA over JTAG while its PCIe endpoint is enumerated is a
surprise removal, and it crashes the BCM2712 root complex. On rpi5-netv2 detach
the endpoint before any of the JTAG commands in this section or the next one
([detach the PCIe endpoint before any JTAG
reconfiguration](../acorn/designs/pcie.md#detach-the-pcie-endpoint-before-any-jtag-reconfiguration)):

```console
$ lspci -d 10ee:7011
$ echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove
```

Take the address from the first command; on a Pi 5 the endpoint enumerates at
`0001:01:00.0`, the slot the Acorn hosts use. Bring it back afterwards with
`echo 1 | sudo tee /sys/bus/pci/rescan`, or by rebooting.
:::

On RPi 5 hosts, the same `libgpiod` cable works but is even slower because the
RPi 5's RP1 I/O controller adds latency to sysfs GPIO access:

```console
$ sudo openFPGALoader --cable libgpiod --pins 27:22:4:17 design.bit
```

### RPi 5 (RP1 PIO JTAG, not in upstream openFPGALoader)

The `rp1pio` cable drives JTAG through the RP1's PIO peripheral instead of
bit-banging it, which is much faster than the `libgpiod` cable above. It is not
in upstream openFPGALoader; it is installed from the `openfpgaloader-rp1pio`
package, which brings the `librp1jtag0` shared library with it (see
[Packages](../../packages.md)). The same PCIe detach applies before this command.

```console
$ sudo openFPGALoader --cable rp1pio --pins 27:22:4:17 design.bit
```

The sources behind the package:

- openFPGALoader with RP1 PIO JTAG support, pending upstream:
  [mithro/openFPGALoader (feature/rp1-jtag-netv2)](https://github.com/mithro/openFPGALoader/tree/feature/rp1-jtag-netv2)
- The RP1 JTAG shared library: [mithro/rp1-jtag](https://github.com/mithro/rp1-jtag)

:::{todo}
† Four artefacts disagree about how rpi5-netv2 is programmed, and none of them
settles it:

- The pin-mapping notes name `openFPGALoader (rp1pio)` as its tool.
- The board specification calls RP1 PIO JTAG a capability still pending
  upstream, not something running here.
- The 2026-03-09 SSH survey found OpenOCD installed on rpi5-netv2 and no
  openFPGALoader at all ([Development hosts](hosts.md#development-hosts)).
- [`alphamax-rpi5-sysfsgpio.cfg`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/pcie-enumeration/openocd/alphamax-rpi5-sysfsgpio.cfg)
  in test-designs is a checked-in OpenOCD Pi 5 configuration for this board —
  `sysfsgpio jtag_nums 575 588 598 593` and `sysfsgpio srst_num 595`, which is
  the Pi 5 RP1 gpiochip base 571 plus GPIO 4, 17, 27, 22 and 24, the same
  wiring as the JTAG table above. It corroborates the survey: an OpenOCD path
  for the Pi 5 exists and is checked in.

To settle it today: if the `openfpgaloader-rp1pio` package is installed on the
host, run `sudo openFPGALoader --cable rp1pio --pins 27:22:4:17 --detect`; if it
is not, use OpenOCD with that configuration. Keep the winner, delete the losers
and record the date.
:::

### Future: NeTV2 board definition in openFPGALoader

Once the NeTV2 board definition is landed upstream in openFPGALoader, the pin
mapping will be built in and the command simplifies to:

```console
$ sudo openFPGALoader -b netv2 design.bit
```

This is tracked in the openFPGALoader fork:
[mithro/openFPGALoader (feature/rp1-jtag-netv2)](https://github.com/mithro/openFPGALoader/tree/feature/rp1-jtag-netv2)

## Programming with OpenOCD

rpi3-netv2 uses OpenOCD 0.10.x with the `bcm2835gpio` interface instead:

```console
$ sudo openocd -f ~/netv2/alphamax-rpi.cfg -c 'init; pld load 0 <bitstream>; exit'
```

The configuration sets `bcm2835gpio_jtag_nums 4 17 27 22`,
`bcm2835gpio_srst_num 24` and peripheral base `0x3F000000`, which is the same
wiring as the table above. The Pi 5 equivalent, using the `sysfsgpio` adapter
because the RP1 has no BCM2835 peripheral window, is
[`alphamax-rpi5-sysfsgpio.cfg`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/pcie-enumeration/openocd/alphamax-rpi5-sysfsgpio.cfg)
in test-designs.

:::{note}
`pld load 0` takes a device index, not a device name: that is the OpenOCD 0.10.x
syntax.
:::
