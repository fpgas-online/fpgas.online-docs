# Acorn on a Compute Blade: the blade's pins, the shared line and settings

**You have an Acorn wired to a Compute Blade with a CM4 or CM5 and want to know what each pin of the
blade's two headers is, what follows from JTAG and the serial pair sharing one line, and what the blade must
have set for the serial pair and the kernel console.** How JTAG is run on a blade is on [JTAG on a Compute
Blade](compute-blade-jtag.md). Which wire goes where is on [Acorn wiring on a Compute
Blade](compute-blade.md).

## The blade's connectors and their GPIOs

| Connector | GPIOs | Pins |
|-----------|-------|------|
| Extension Port (2×5) | GPIO2, GPIO3, GPIO4, GPIO14, GPIO15 | printed 1-10 |
| UART (1×4), beside the Extension Port | GPIO14, GPIO15 | printed 1-4 |
| UART Front (3-pin) | GPIO14, GPIO15 | TX, RX, GND |
| Fan Unit (4-pin) | GPIO12, GPIO13 | PWM0/UART5-TX, PWM1/UART5-RX |

GPIO14 and GPIO15 are the same lines at every connector that carries them: the
vendor's [GPIO table](https://docs.computeblade.com/blade/guides/gpio) lists
GPIO14 at "Expansion Module Port, UART Front(3pin), UART Back(4pin)" as "UART0
TX", and GPIO15 at the same three as "UART0 RX". The vendor publishes no
schematic, so whether anything sits in series between the connectors is not
known. GPIO8-11 (SPI0) are not brought out. GPIO2 and GPIO3, which carry TDI and
TDO here, are also SDA1 and SCL1; I²C pull-ups on them are expected but have
not been measured on a blade.

The Extension Port (2×5), by printed pin:

```{include} ../generated/acorn-blade-ext.md
```

The UART header (1×4), by printed pin:

```{include} ../generated/acorn-blade-uart.md
```

The UART header's 5 V pin can be an input or an output (vendor note), so it is
live whenever the blade is powered.

## The serial port

```{include} serial-pair.inc
```

How firmly the host holds to it:

- **BCM2711 hosts (a CM4 on a Compute Blade):** the PL011 mux is fixed —
  GPIO14 can only be a UART transmitter and GPIO15 only a receiver — so the
  crossover is the one wiring that works.

- **RP1 hosts (Pi 5, CM5):** the hardware UART0 is only offered as GPIO14 =
  `TXD0`, GPIO15 = `RXD0` (`pinctrl funcs 14,15` lists no alternative where they
  swap). The RP1's PIO block (`/dev/pio0`, the `rp1_pio` module) could run a
  UART on any pin, but no driver for that exists in the test scripts, so the
  fleet uses the crossover everywhere and one cable design works on every host.

| Parameter | Value |
|-----------|-------|
| Device    | `/dev/ttyAMA0` |
| Baud rate | 115200 |
| Pre-test  | `systemctl stop serial-getty@ttyAMA0` (active on pi16 at ps1 on 2026-10-05) |

A CM5 on a Compute Blade needs no `uart0-pi5` overlay: pi16 at ps1 had `/dev/ttyAMA0` with `enable_uart=1` and no
`uart0-pi5`, read 2026-10-05.

```{include} gpio-contention.inc
```

## The shared line and the 470 Ω resistor

UART pin 3 *is* GPIO14, which is also Extension Port pin 9, where P1 puts TMS.
The blade brings out five GPIOs and JTAG needs four, so one JTAG signal has to
share a line with the serial pair: J2 and TMS share GPIO14.

The TMS wire goes straight to its pin. The J2 wire reaches the same line through
a 470 Ω resistor fitted at the housing end of the wire. Whatever a loaded design
does with J2, TMS should still get through: the worst case is an FPGA output
fighting the JTAG driver through 470 Ω, 3.3 V / 470 Ω ≈ 7 mA, which the
Artix-7 I/O and the Pi's GPIO should tolerate, with the direct driver winning
the level (designed so, not measured: see the note below). Without the
resistor the same fight is a short between two outputs, which crashes the host
(see the warning under [P2](#the-serial-port)). K2 needs no
resistor: GPIO15 is not a JTAG pin on this carrier.

The serial port and JTAG cannot both have GPIO14 in one boot of a host on
kernel 6.18: with the header's serial port on (`enable_uart=1`) the kernel's
serial driver holds GPIO14 and JTAG cannot run, and with it off there is no
`/dev/ttyAMA0` for the serial pair (see [JTAG on a blade](compute-blade-jtag.md#jtag-on-a-blade)).
Under kernel 6.12.75 pi20 at ps1 ran JTAG and then used `/dev/ttyAMA0` in the same
boot.

:::{note}
470 Ω is a chosen value, not a measured one: it limits the current to about
7 mA if the FPGA drives J2 against the Pi at 3.3 V. Whether `--detect` answers
while a design drives J2, and whether `/dev/ttyAMA0` still transmits through
the resistor, is **not yet run by us on this hardware**: no blade is wired this
way yet. Check both on the first blade that is.
:::

:::{warning}
**On a cable without the J2 resistor, a design that drives J2 costs you JTAG**
([test-designs issue
#4](https://github.com/fpgas-online/fpgas.online-test-designs/issues/4) item 1):
GPIO14 is TMS, and once the FPGA drives it `openFPGALoader` cannot. The pin-ID
design drives every P2 ball, so it does this every time. The way back is a PoE
cycle of the blade's switch port, which restores everything in about 60 s: the
flash bitstream reloads and `--detect`, the DNA read and the PCIe endpoint all
come back. See [PoE power control](../../../setup/network-power-cycle.md) and,
for the ps1 blades, [Power control](../../../sites/ps1-gateway.md#power-control). Which
blades have the resistor is on [Acorns at ps1](../installations/ps1.md#the-cards).
:::

```{include} kernel-console.inc
```

## Troubleshooting

| Problem | Likely cause | Fix |
|---------|--------------|-----|
| Pi reboots when a serial design loads | Kernel console on the FPGA UART; SysRq | Console to `ttyAMA10` (Pi 5) / `tty1` (blade), `kernel.sysrq=0` |
