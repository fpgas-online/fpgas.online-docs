---
type: reference
owner: documentation maintainers
reader: someone wiring or checking the cables to a Raspberry Pi
review: 2026-11-10
---

# Tiny Tapeout FPGA demo board wiring to a Raspberry Pi

**You want to know which signal of the board goes to which port or pin of its Raspberry Pi.**

The pin of every signal is on [Tiny Tapeout FPGA demo board pin mapping](../overview/pin-mapping.md), and the PMOD HAT itself is on [Raspberry Pi PMOD HAT](../../pmod/rpi-hat.md).

## USB

The board connects to the Raspberry Pi by one USB-C cable. Connection names the link and Value gives it.

| Connection | Value |
|------------|-------|
| Cable | USB-C from the demo PCB to the Raspberry Pi |
| Device | `/dev/ttyACM0` (VID:PID `2e8a:0005`, MicroPython Board in FS mode) |
| Symlink | `/dev/ttboard`, which the Pi daemon opens |

## PMOD HAT cabling

Each Tiny Tapeout bus has its own HAT port, from the [loopback test's board config](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/pmod-loopback/host/test_pmod_loopback.py). HAT Port is the connector on the PMOD HAT. TT Bus is the signal group on it, and Driven By the side that drives it.

| HAT Port | TT Bus | Driven By |
|----------|--------|-----------|
| JC | `ui_in` | the Raspberry Pi |
| JA | `uo_out` | the FPGA |
| JB | `uio` | either, through the third PMOD header of the demo PCB |

## Shared GPIOs of JA and JB

HAT JB pins 2-4 and HAT JA pins 2-4 are the [same RPi GPIO lines](../../pmod/rpi-hat.md), GPIO10, GPIO9 and GPIO11, the shared SPI0 bus. Three `uo_out` signals and three `uio` signals are therefore electrically connected at the Raspberry Pi side. RPi GPIO is the shared line. HAT JA Pin and HAT JB Pin are the two connector pins on it, and TT Signal the signal on each.

| RPi GPIO | HAT JA Pin | TT Signal (uo_out) | HAT JB Pin | TT Signal (uio) | Conflict |
| -------- | ---------- | ------------------ | ---------- | --------------- | -------- |
| GPIO10   | JA2        | uo_out[1]          | JB2        | uio[1]          | Shorted  |
| GPIO9    | JA3        | uo_out[2]          | JB3        | uio[2]          | Shorted  |
| GPIO11   | JA4        | uo_out[3]          | JB4        | uio[3]          | Shorted  |

When the FPGA drives `uo_out[1,2,3]` and `uio[1,2,3]` with different values, the outputs fight each other through the shared RPi GPIO. The consequences:

- **GPIO loopback test**: it works, because it drives only `ui_in` (JC) and reads `uo_out` (JA). The `uio` pins (JB) are not driven during this test, so no conflict occurs.
- **Bidirectional I/O test**: it cannot test `uio[1,2,3]` independently, because they are shorted to `uo_out[1,2,3]` respectively. If the FPGA drives both buses, the conflicting outputs may cause contention or incorrect readings.
- **SPI kernel modules**: `rmmod spidev spi_bcm2835` unloads them, because GPIO7-11 overlap with HAT JA pins 1-4 and JB pins 1-4. The step is on [How to free the Raspberry Pi's SPI pins before a PMOD test](../checks/free-spi-pins.md).
