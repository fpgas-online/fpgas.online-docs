---
type: reference
owner: documentation maintainers
reader: someone looking up a Raspberry Pi 5's settings for an Acorn
review: 2026-11-10
---

# A Raspberry Pi 5's settings for an Acorn

This page is for someone with an Acorn wired to a Raspberry Pi 5. It lists what the Pi must have set for the card's serial pair and for JTAG, and where the kernel console must not be. Why each setting is what it is is on [The serial port, the console and JTAG on a Raspberry Pi 5](serial-and-console.md). Which wire goes where is on [Acorn wiring on a Raspberry Pi 5](wiring.md).

## The serial port

```{include} ../../inc/serial-pair.inc
```

Each row of the next table is a setting of the Pi's header serial port and its value.

| Setting | Value |
|---------|-------|
| Device | `/dev/ttyAMA0` |
| Baud rate | 115200 |
| Overlay | `[pi5] dtoverlay=uart0-pi5` in `config.txt` |
| Pre-test | `systemctl stop serial-getty@ttyAMA0` |

```{include} ../../inc/gpio-contention.inc
```

## JTAG from the Pi

Each row of the next table is a setting of JTAG from a Pi 5 and its value. To run JTAG, follow [How to run JTAG by hand on an Acorn on a Raspberry Pi 5](../../checks/jtag-by-hand.md).

| Setting | Value |
|---------|-------|
| Pins | SPI0, GPIO8-11 |
| SPI modules | need not be unloaded: `pinctrl` shows GPIO8-11 unclaimed with them loaded |
| The 40-pin header's GPIO chip | `/dev/gpiochip15` |
| Cable these pages use | `libgpiod`, which always opens `/dev/gpiochip0` |
| Link before the `libgpiod` cable runs | `/dev/gpiochip15` as `/dev/gpiochip0`, made again at each boot |
| Package in the Welland NFS root | `openfpgaloader-rp1pio` (openFPGALoader 1.1.1, from [mithro/rp1-jtag](https://github.com/mithro/rp1-jtag)) |
| Other cable of that package | `rp1pio` (RP1 PIO-driven JTAG), which needs `/dev/pio0` |

Each row of the next table is an action of that openFPGALoader build and what it does to the card.

| Action | Effect |
|--------|--------|
| `--detect` | read-only; safe against a live PCIe endpoint |
| `--read-dna`, `--read-xadc`, `--read-register` | read-only |
| Loading a bitstream | not safe against a live PCIe endpoint: [why the endpoint is detached before a load](../../checks/jtag-and-the-pcie-endpoint.md#why-the-endpoint-is-detached-before-a-load) |

## Kernel console on the FPGA UART

```{include} ../../inc/kernel-console.inc
```

When a wire does not answer: [Acorn wiring faults on a Raspberry Pi 5](../../troubleshooting/rpi-5-wiring.md).
