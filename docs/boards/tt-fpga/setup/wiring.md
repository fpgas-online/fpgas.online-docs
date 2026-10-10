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

The check expects this cabling, wire by wire: [fpgas-verify: the Tiny Tapeout demo boards](../../../verify/tt-fpga.md#the-wiring-test).

HAT Port is the connector on the PMOD HAT. TT Bus is the signal group on it, and Driven By the side that drives it.

| HAT Port | TT Bus | Driven By |
|----------|--------|-----------|
| JA | `ui_in` | the Raspberry Pi |
| JB | `uio` | either, through the third PMOD header of the demo PCB |
| JC | `uo_out` | the FPGA |

## Shared GPIOs of JA and JB

HAT JB pins 2-4 and HAT JA pins 2-4 are the [same RPi GPIO lines](../../pmod/rpi-hat.md), the shared SPI0 bus. That sharing is a property of the HAT. RPi GPIO is the shared line. HAT JA Pin and HAT JB Pin are the two connector pins on it, and TT Signal the signal on each.

| RPi GPIO | HAT JA Pin | TT Signal (ui_in) | HAT JB Pin | TT Signal (uio) |
| -------- | ---------- | ----------------- | ---------- | --------------- |
| GPIO10   | JA2        | ui_in[1]          | JB2        | uio[1]          |
| GPIO9    | JA3        | ui_in[2]          | JB3        | uio[2]          |
| GPIO11   | JA4        | ui_in[3]          | JB4        | uio[3]          |

## Effect of the shared GPIOs

Three `ui_in` signals and three `uio` signals are electrically connected at the Raspberry Pi side. In a normal design `ui_in` is an input, so the short does not make two FPGA outputs fight. The pin-id design, which drives everything, is the exception. Case names the situation, and Effect what happens.

| Case | Effect |
|------|--------|
| GPIO loopback test | works: it drives `ui_in` (JA) and reads `uo_out` (JC); driving `ui_in[1:3]` also drives `uio[1:3]`, and the loopback design does not use `uio` |
| Design that drives `uio[1,2,3]` | also drives `ui_in[1,2,3]`, so the Raspberry Pi must leave GPIO10, GPIO9 and GPIO11 as inputs or it fights the FPGA |
| Raspberry Pi that drives `ui_in[1,2,3]` | also drives `uio[1,2,3]`, so those `uio` bits must be inputs in the design |
| Bidirectional I/O test | cannot test `uio[1,2,3]` independently of `ui_in[1,2,3]` |
| SPI kernel modules | `rmmod spidev spi_bcm2835` unloads them, because GPIO7-11 overlap with HAT JA pins 1-4 and JB pins 1-4 |
| Unshared `uio` bits | `uio[0]` and `uio[4:7]` are on JB pins 1 and 7-10, use unique RPi GPIOs and work correctly |
