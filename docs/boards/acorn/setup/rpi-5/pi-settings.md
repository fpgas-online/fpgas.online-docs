---
type: reference
owner: documentation maintainers
reader: someone looking up a Raspberry Pi 5's settings for an Acorn
review: 2026-11-10
---

# A Raspberry Pi 5's settings for an Acorn

**You have an Acorn wired to a Raspberry Pi 5 and want to know what the Pi must have set for the card's
serial pair and for JTAG, where the kernel console must not be, and what must never be done on those
wires.** Which wire goes where is on [Acorn wiring on a Raspberry Pi 5](wiring.md).

## The serial port

```{include} ../../inc/serial-pair.inc
```

How firmly the host holds to it:

- **RP1 hosts (Pi 5, CM5):** the hardware UART0 is only offered as GPIO14 =
  `TXD0`, GPIO15 = `RXD0` (`pinctrl funcs 14,15` lists no alternative where they
  swap). The RP1's PIO block (`/dev/pio0`, the `rp1_pio` module) could run a
  UART on any pin, but no driver for that exists in the test scripts, so the
  fleet uses the crossover everywhere and one cable design works on every host.

| Parameter | Value |
|-----------|-------|
| Device    | `/dev/ttyAMA0` |
| Baud rate | 115200 |
| Pre-test  | `systemctl stop serial-getty@ttyAMA0` (inactive on the Welland fleet) |

**A Pi 5 needs an explicit overlay for this UART.** `bcm2712-rpi-5-b.dtb` ships
the RP1 header UART (`serial0`) disabled, and `dtoverlay=disable-bt` only touches
Bluetooth on a Pi 5. Without
`[pi5] dtoverlay=uart0-pi5` in `config.txt` there is no `/dev/ttyAMA0`.
Enabling it also makes `console=serial0` resolve to `ttyAMA0`, which would put
the kernel console on the FPGA's serial pins (see [Kernel console on the FPGA
UART](#kernel-console-on-the-fpga-uart)), so the Pi 5s use
`console=ttyAMA10`, the dedicated debug connector, via `[pi5]
cmdline=cmdline-pi5.txt`. The Welland NFS root sets both, and its
`verify-pi.yml --tags uart` play checks them; see also [Raspberry
Pi 5](../../../../setup/pi.md#raspberry-pi-5).

```{include} ../../inc/gpio-contention.inc
```

## JTAG from the Pi

JTAG uses the Pi's SPI0 pins. On a Pi 5 `pinctrl` shows GPIO8-11 unclaimed even
with the SPI modules loaded, so they do not have to be unloaded.

**On a Pi 5 the 40-pin header is `/dev/gpiochip15`.** The Welland NFS root ships
`openfpgaloader-rp1pio` (openFPGALoader 1.1.1, from
[mithro/rp1-jtag](https://github.com/mithro/rp1-jtag)). Its `libgpiod` cable
always opens `/dev/gpiochip0` and fails with `JTAG init failed with: Unable to
open gpio chip`, so link the chip first (devtmpfs, so the link goes at reboot):

```console
$ sudo ln -sfn /dev/gpiochip15 /dev/gpiochip0
```

Its `rp1pio` cable (RP1 PIO-driven JTAG) needs `/dev/pio0`, which the check's `rp1-pio` test opens. `rp1-pio` passed on the Pi 5 then at sw2 p47 on 2 October 2026 (on 6 October 2026 that port had acorn-holly, device DNA `0x00200c8664b04854`, on the Pi 5 2 GB `285df3f84af242d0`) and on all four welland Pi 5s that carry an Acorn on 6 October 2026 (bootloader 2026/09/25 on the two read that day); on 3 October 2026 it was recorded failing on the two Pi 5s then at sw2 p47 and p48 with bootloader 2024/11/05. Whether the bootloader decides it is not confirmed: [test-designs issue #151](https://github.com/fpgas-online/fpgas.online-test-designs/issues/151). These pages use the `libgpiod` cable. The
build has `--read-dna`, `--read-xadc` and `--read-register`, all read-only.

`--detect` is read-only and safe against a live PCIe endpoint. Loading a
bitstream is not: [detach the PCIe endpoint
first](../../checks/jtag-and-the-pcie-endpoint.md#why-the-endpoint-is-detached-before-a-load).

```{include} ../../inc/kernel-console.inc
```

When a wire does not answer: [Acorn wiring faults on a Raspberry Pi 5](../../troubleshooting/rpi-5-wiring.md).
