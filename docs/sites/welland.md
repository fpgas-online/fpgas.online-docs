# Welland

The private test lab in South Australia. Raspberry Pi 5 hosts, each with a SQRL
Acorn board on an mPCIe adapter, plus a camera pointed at the board.

## Wiring

JTAG and the serial pair are on separate GPIOs here, which is why a design that
drives the FPGA's TX does not cost you JTAG the way it does at
[PS1](ps1.md#two-traps).

| Signal | GPIO | Header pin |
|---|---|---|
| TCK | 11 | 23 |
| TDI | 10 | 19 |
| TDO | 9 | 21 |
| TMS | 8 | 24 |

```console
$ openFPGALoader --cable libgpiod --pins 10:9:11:8 --detect
```

The P2 serial pair is wired straight through, **without** the crossover used at
PS1:

| P2 ball | lands on | RPi function |
|---|---|---|
| K2 | GPIO14 | TXD0 |
| J2 | GPIO15 | RXD0 |

## Raspberry Pi 5 specifics

`gpiochip`
: The 40-pin header GPIOs are on **gpiochip15**, not gpiochip0. Tools that
  hardcode `/dev/gpiochip0` — including openFPGALoader 0.10.0 — fail here.

`dtoverlay=disable-bt`
: A no-op on the Pi 5. The overlay is `compatible="brcm,bcm2835"` and resolves
  to `disable-bt-pi5.dtbo`, which only touches the `bluetooth` node; the header
  UART stays disabled. Use `dtoverlay=uart0-pi5` instead.

`/dev/ttyAMA0` vs `/dev/ttyAMA10`
: `ttyAMA0` is the RP1 header UART; `ttyAMA10` is the dedicated debug UART. The
  NFS root boots with `console=ttyAMA10` so that `ttyAMA0` is free for the FPGA.

## PCIe and JTAG interact

Reconfiguring the FPGA over JTAG while its PCIe endpoint is enumerated crashes
the BCM2712 root complex. Detach the endpoint first:

```console
$ echo 1 | sudo tee /sys/bus/pci/devices/0000:01:00.0/remove
```

Restore it with `/sys/bus/pci/rescan`, or by rebooting.

:::{warning}
The root filesystem is a read-only NFS export with a tmpfs overlay
(`overlayroot=tmpfs`), so anything staged in `/home/pi` is gone after a reboot.
A bitstream that loaded a minute ago will fail with `Open file … FAIL` after a
reboot because the file no longer exists.
:::

## Known faults

- p43 and p44 do not respond to JTAG.
- p29's J5 conductor is dead.
- openFPGALoader is 0.10.0, which predates `--read-dna`, `--read-xadc` and
  `--read-register`. That is why device DNA cannot be read here while it can at
  PS1. See [Packages](../packages.md) for the replacement.
