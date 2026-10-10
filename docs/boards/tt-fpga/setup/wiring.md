---
type: reference
owner: documentation maintainers
reader: someone wiring or checking the cables to a Raspberry Pi
review: 2026-11-10
---

# Tiny Tapeout FPGA demo board wiring to a Raspberry Pi

**You want to know which signal of the board goes to which port or pin of its Raspberry Pi.**

The pin of every signal is on [Tiny Tapeout FPGA demo board pin mapping](../overview/pin-mapping.md). The PMOD HAT itself is on [Raspberry Pi PMOD HAT](../../pmod/rpi-hat.md).

## USB

Connection names the link and Value gives it.

| Connection | Value |
|------------|-------|
| Cable | USB-C from the demo PCB to the Raspberry Pi |
| Device | `/dev/ttyACM0` (VID:PID `2e8a:0005`, MicroPython Board in FS mode) |
| Symlink | `/dev/ttboard`, which the Pi daemon opens |

## PMOD HAT cabling

The cabling is from the [loopback test's board config](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/pmod-loopback/host/test_pmod_loopback.py). The table is the old page's. The check expects `ui_in` on HAT JA and `uo_out` on HAT JC. Which is right is [test-designs issue #58](https://github.com/fpgas-online/fpgas.online-test-designs/issues/58), and the order within a port is [test-designs issue #19](https://github.com/fpgas-online/fpgas.online-test-designs/issues/19).

HAT Port is the connector on the PMOD HAT. TT Bus is the signal group on it, and Driven By the side that drives it.

| HAT Port | TT Bus | Driven By |
|----------|--------|-----------|
| JC | `ui_in` | the Raspberry Pi |
| JA | `uo_out` | the FPGA |
| JB | `uio` | either, through the third PMOD header of the demo PCB |

## Shared GPIOs of JA and JB

HAT JB pins 2-4 and HAT JA pins 2-4 are the [same RPi GPIO lines](../../pmod/rpi-hat.md), the shared SPI0 bus. That sharing is a property of the HAT. Which Tiny Tapeout signals sit on those pins follows the cabling table of the section before, which [test-designs issue #58](https://github.com/fpgas-online/fpgas.online-test-designs/issues/58) contests. RPi GPIO is the shared line. HAT JA Pin and HAT JB Pin are the two connector pins on it, and TT Signal the signal on each.

| RPi GPIO | HAT JA Pin | TT Signal (uo_out) | HAT JB Pin | TT Signal (uio) | Conflict |
| -------- | ---------- | ------------------ | ---------- | --------------- | -------- |
| GPIO10   | JA2        | uo_out[1]          | JB2        | uio[1]          | Shorted  |
| GPIO9    | JA3        | uo_out[2]          | JB3        | uio[2]          | Shorted  |
| GPIO11   | JA4        | uo_out[3]          | JB4        | uio[3]          | Shorted  |

## Effect of the shared GPIOs

Three `uo_out` signals and three `uio` signals are electrically connected at the Raspberry Pi side. When the FPGA drives `uo_out[1,2,3]` and `uio[1,2,3]` with different values, the outputs fight each other. The ports named in this table follow the same contested cabling ([test-designs issue #58](https://github.com/fpgas-online/fpgas.online-test-designs/issues/58)). Test names what runs, and Effect what happens.

| Test | Effect |
|------|--------|
| GPIO loopback test | works: it drives only `ui_in` (JC) and reads `uo_out` (JA), and the `uio` pins (JB) are not driven, so no conflict occurs |
| Bidirectional I/O test | cannot test `uio[1,2,3]` independently, because they are shorted to `uo_out[1,2,3]` respectively; if the FPGA drives both buses, the outputs may cause contention or incorrect readings |
| SPI kernel modules | `rmmod spidev spi_bcm2835` unloads them, because GPIO7-11 overlap with HAT JA pins 1-4 and JB pins 1-4 |
| Unshared `uio` bits | `uio[0]` and `uio[4:7]` are on JB pins 1 and 7-10, use unique RPi GPIOs and work correctly |
