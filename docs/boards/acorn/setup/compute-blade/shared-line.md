---
type: explanation
owner: documentation maintainers
reader: someone asking why JTAG and the serial pair share a line on a Compute Blade
review: 2026-11-10
---

# The line JTAG and the serial port share on a Compute Blade

This page explains why the Acorn's JTAG and serial pair share one line on a Compute Blade. It also says what the 470 Ω resistor and the full-length housings are for. It is for someone building or debugging the blade's cables. It gives no pin tables, which are on [the blade's pins and settings](blade-settings.md). It gives no commands, which are on [How to run JTAG by hand on an Acorn on a Compute Blade](../../checks/compute-blade-jtag-by-hand.md).

## Why one line is shared

UART pin 3 *is* GPIO14, which is also Extension Port pin 9, where P1 puts TMS. The blade brings out five GPIOs, and JTAG needs four. So one JTAG signal has to share a line with the serial pair: J2 and TMS share GPIO14. K2 needs no resistor, because GPIO15 is not a JTAG pin on this carrier.

The five GPIOs are JTAG's four plus the serial pair's second line, so none is left for J5 and H5. Their wires are cut back and insulated like VCC. The fpgas.online Acorn design resets J5 and H5 to inputs, so the open ends do no harm.

## The 470 Ω resistor

The TMS wire goes straight to its pin. The J2 wire reaches the same line through a 470 Ω resistor at its housing end, which the [UART wires page](uart-wires.md) fits. The resistor is there so that TMS still gets through, by design, whatever a loaded design does with J2. Its measurement is [test-designs issue #221](https://github.com/fpgas-online/fpgas.online-test-designs/issues/221).

If the FPGA drives J2 against the Pi at 3.3 V, the resistor limits the current to about 7 mA (3.3 V / 470 Ω). Without the resistor, the same fight is a short between two outputs, which crashes the host.

## A cable without the resistor

On a cable without the J2 resistor, a design that drives J2 costs you JTAG ([test-designs issue #4](https://github.com/fpgas-online/fpgas.online-test-designs/issues/4) item 1). GPIO14 is TMS, and once the FPGA drives it `openFPGALoader` cannot. The pin-ID design drives every P2 ball, so it does this every time.

The way back is a PoE cycle of the blade's switch port, which restores everything in about 60 s. The flash bitstream reloads, and `--detect`, the DNA read and the PCIe endpoint all come back. See [PoE power control](../../../../setup/network.md#poe-power-control) and, for the ps1 blades, [Power control](../../../../sites/ps1-gateway.md#power-control).

## The serial port and JTAG in one boot

The serial port and JTAG cannot both have GPIO14 in one boot of a host on kernel 6.18. With the header's serial port on (`enable_uart=1`), the kernel's serial driver holds GPIO14 and JTAG cannot run. With it off, there is no `/dev/ttyAMA0` for the serial pair (see [JTAG on a blade](../../checks/compute-blade-jtag-by-hand.md)). Under kernel 6.12.75, JTAG ran and then the serial pair was used in the same boot.

## What the host offers as a UART

The serial pair is a null-modem crossover, the Raspberry Pi header convention that `/dev/ttyAMA0` uses. It is also the one the NeTV2 boards use ([NeTV2 primary UART](/boards/netv2.md#primary-uart-via-rpi-gpio)).

On a BCM2711 host (a CM4) the PL011 mux is fixed: GPIO14 can only be a UART transmitter and GPIO15 only a receiver. So the crossover is the one wiring that works. On an RP1 host (a CM5) the hardware UART0 is offered only as GPIO14 = `TXD0` and GPIO15 = `RXD0`; `pinctrl funcs 14,15` lists no alternative where they swap.

The RP1's PIO block (`/dev/pio0`, the `rp1_pio` module) could run a UART on any pin, but no driver for that exists in the test scripts. So the fleet uses the crossover everywhere, and one cable design works on every host. A CM5 on a Compute Blade needs no `uart0-pi5` overlay: `enable_uart=1` gives it `/dev/ttyAMA0`.

## The housings and the 5 V pins

A 2×3 housing on Extension Port rows 2-4 also fits one row toward pin 1. That puts the GND wire on pin 7 (5 V). A 1×3 on UART pins 2-4 also fits one pin toward pin 1, which puts GND on UART pin 1 (5 V). Either shorts the blade's 5 V rail, because the Acorn's ground is the blade's ground through the M.2 slot.

A full-length housing has only one position, but it can still go on turned round. The 2×5 then puts TCK on pin 7, and the 1×4 puts K2 on pin 1, both 5 V. So each housing covers its whole header, and pin 1 is marked on it.
