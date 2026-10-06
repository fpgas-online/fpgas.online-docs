# Acorn on a Raspberry Pi 5: the Pi's settings

**You have an Acorn wired to a Raspberry Pi 5 and want to know what the Pi must have set for the card's
serial pair and for JTAG, where the kernel console must not be, and what must never be done on those
wires.** Which wire goes where is on [Acorn wiring on a Raspberry Pi 5](rpi-5.md).

## The serial port

```{include} serial-pair.inc
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
Pi 5](../../../setup/pi.md#raspberry-pi-5).

```{include} gpio-contention.inc
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

Its `rp1pio` cable (RP1 PIO-driven JTAG) needs `/dev/pio0`. The Welland Pi 5s did not have it when read in
September 2026 (`rp1-pio: failed to contact RP1 firmware`). On 2 October 2026 it was present, and the check's `rp1-pio` test passed, on the Acorn and
Raspberry Pi 5 seen at welland's sw2 p47 that day.
The `libgpiod` cable does not need it, and is the one these pages use. The
build has `--read-dna`, `--read-xadc` and `--read-register`, all read-only.

`--detect` is read-only and safe against a live PCIe endpoint. Loading a
bitstream is not: [detach the PCIe endpoint
first](../designs/pcie.md#detach-the-pcie-endpoint-before-any-jtag-reconfiguration).

```{include} kernel-console.inc
```

## Troubleshooting

| Problem | Likely cause | Fix |
|---------|--------------|-----|
| `JTAG init failed with: Unable to open gpio chip` (Pi 5) | The `libgpiod` cable opens `/dev/gpiochip0`; the header is `gpiochip15` | `ln -sfn /dev/gpiochip15 /dev/gpiochip0` |
| No `/dev/ttyAMA0` on a Pi 5 | RP1 uart0 disabled; `disable-bt` does not enable it on bcm2712 | `[pi5] dtoverlay=uart0-pi5` |
| Board hung, ~0.4 W on PoE instead of ~8 W | Wedged Pi 5 | PoE cycle the switch port; a Pi 5 needs over 90 s to come back |
| Pi reboots when a serial design loads | Kernel console on the FPGA UART; SysRq | Console to `ttyAMA10` (Pi 5) / `tty1` (blade), `kernel.sysrq=0` |
