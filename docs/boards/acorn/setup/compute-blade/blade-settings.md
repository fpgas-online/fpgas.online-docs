---
type: reference
owner: documentation maintainers
reader: someone looking up a Compute Blade's pins and settings for an Acorn
review: 2026-11-10
---

# A Compute Blade's pins and settings for an Acorn

This page is for someone with an Acorn wired to a Compute Blade with a CM4 or CM5. It lists what each pin of the two headers is and what the blade must have set for the serial pair. It also says where the kernel console must not be.

Why JTAG and the serial pair share a line is on [The line JTAG and the serial port share on a Compute Blade](shared-line.md).

How JTAG is run on a blade is on [How to run JTAG by hand on a Compute Blade](../../checks/compute-blade-jtag-by-hand.md). Which wire goes where is on [Acorn wiring on a Compute Blade](wiring.md).

## The blade's connectors and their GPIOs

Each row of the table is a connector of the blade, the GPIOs it carries and its pins.

| Connector | GPIOs | Pins |
|-----------|-------|------|
| Extension Port (2×5) | GPIO2, GPIO3, GPIO4, GPIO14, GPIO15 | printed 1-10 |
| UART (1×4), beside the Extension Port | GPIO14, GPIO15 | printed 1-4 |
| UART Front (3-pin) | GPIO14, GPIO15 | TX, RX, GND |
| Fan Unit (4-pin) | GPIO12, GPIO13 | PWM0/UART5-TX, PWM1/UART5-RX |
| Not brought out | GPIO8-11 (SPI0) | none |

GPIO14 and GPIO15 are the same lines at every connector that carries them. The vendor's [GPIO table](https://docs.computeblade.com/blade/guides/gpio) lists GPIO14 at "Expansion Module Port, UART Front(3pin), UART Back(4pin)" as "UART0 TX", and GPIO15 at the same three as "UART0 RX". GPIO2 and GPIO3, which carry TDI and TDO here, are also SDA1 and SCL1.

Each row of the next table is one Extension Port pin by printed number: silkscreen, GPIO, matching Pi header pin and wire.

```{include} ../../generated/acorn-blade-ext.md
```

Each row of the next table is one pin of the UART header by printed number. The 5 V pin can be an input or an output (vendor note), so it is live whenever the blade is powered.

```{include} ../../generated/acorn-blade-uart.md
```

## The serial port

```{include} ../../inc/serial-pair.inc
```

Each row of the next table is a setting of the header's serial port and its value.

| Setting | Value |
|---------|-------|
| Device | `/dev/ttyAMA0` |
| Baud rate | 115200 |
| Overlay on a CM5 | none: `enable_uart=1` gives `/dev/ttyAMA0` |
| Pre-test | `systemctl stop serial-getty@ttyAMA0` |

Each row of the next table is a state of the header's serial port and what JTAG and the serial pair do in it.

| Kernel | Header serial port | `/dev/ttyAMA0` | JTAG on GPIO14 |
|--------|--------------------|----------------|----------------|
| 6.18 | on (`enable_uart=1`) | present | cannot run: the kernel's serial driver holds GPIO14 |
| 6.18 | off | absent | ran on the one blade it was tried on ([test-designs issue #213](https://github.com/fpgas-online/fpgas.online-test-designs/issues/213)) |
| 6.12.75 | on | present | ran, and then the serial pair was used in the same boot |

```{include} ../../inc/gpio-contention.inc
```

## Kernel console on the FPGA UART

```{include} ../../inc/kernel-console.inc
```

When a wire does not answer: [Acorn wiring faults on a Compute Blade](../../troubleshooting/compute-blade-wiring.md).
