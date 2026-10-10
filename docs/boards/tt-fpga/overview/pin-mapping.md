---
type: reference
owner: documentation maintainers
reader: someone looking up the pins of a Tiny Tapeout signal
review: 2026-11-10
---

# Tiny Tapeout FPGA demo board pin mapping

**You want to look up where a signal of the demo board v3 (TTDBv3) goes, from the iCE40 ball to the Raspberry Pi GPIO.**

This is the mapping as connected in the fpgas.online test infrastructure. The wires between the PMOD HAT and the demo board are on [Tiny Tapeout FPGA demo board wiring to a Raspberry Pi](../setup/wiring.md). The other figures are on [Tiny Tapeout FPGA demo board specifications](specifications.md).

The map on this page is the old page's. The check expects it the other way round, with `ui_in` on HAT JA and `uo_out` on HAT JC. Which is right is [test-designs issue #58](https://github.com/fpgas-online/fpgas.online-test-designs/issues/58), and the order within a port is [test-designs issue #19](https://github.com/fpgas-online/fpgas.online-test-designs/issues/19).

The shipped RP2350 firmware loaded `GPIOMapTT04` instead of `GPIOMapTTDBv3`, returning incorrect GPIO numbers. All pin numbers on this page are the correct TTDBv3 values, not the firmware-reported ones.

The spec-derived map ([PMOD layouts](../../pmod/tinytapeout.md#rp2350-gpio-mapping-demo-board-v3-tt09)) agrees. `ui_in[0:7]` is on GPIO17 to GPIO24, `uio[0:7]` on GPIO25 to GPIO32 and `uo_out[0:7]` on GPIO33 to GPIO40. Each PMOD connector is wired straight through, with bit 0 on pin 1 and bit 7 on pin 10.

In the tables, Bit is the Tiny Tapeout signal, and iCE40 Pin the ball number on the iCE40UP5K-SG48. RP2350 GPIO is the controller pin on the same trace. PMOD HAT Pin is the connector pin on the PMOD HAT, and RPi GPIO the Raspberry Pi GPIO behind it.

Read or inferred is `read` where the pin-id design decoded the signal. It is `inferred` where the position follows from the straight-through wiring. The `inferred` rows are [test-designs issue #257](https://github.com/fpgas-online/fpgas.online-test-designs/issues/257).

## ui_in

The 8-bit input bus. The Raspberry Pi drives these through the PMOD HAT, and the FPGA reads them.

| Bit      | iCE40 Pin | RP2350 GPIO | PMOD HAT Pin | RPi GPIO | Read or inferred |
| -------- | --------- | ----------- | ------------ | -------- | ---------------- |
| ui_in[0] | 13        | 17          | JC1          | 16       | read             |
| ui_in[1] | 19        | 18          | JC2          | 14       | read             |
| ui_in[2] | 18        | 19          | JC3          | 15       | read             |
| ui_in[3] | 21        | 20          | JC4          | 17       | read             |
| ui_in[4] | 23        | 21          | JC7          | 4        | read             |
| ui_in[5] | 25        | 22          | JC8          | 12       | inferred         |
| ui_in[6] | 26        | 23          | JC9          | 5        | inferred         |
| ui_in[7] | 27        | 24          | JC10         | 6        | read             |

## uo_out

The 8-bit output bus. The FPGA drives these, and the Raspberry Pi reads them through the PMOD HAT.

| Bit       | iCE40 Pin | RP2350 GPIO | PMOD HAT Pin | RPi GPIO | Read or inferred |
| --------- | --------- | ----------- | ------------ | -------- | ---------------- |
| uo_out[0] | 38        | 33          | JA1          | 8        | read             |
| uo_out[1] | 42        | 34          | JA2          | 10       | inferred         |
| uo_out[2] | 43        | 35          | JA3          | 9        | inferred         |
| uo_out[3] | 44        | 36          | JA4          | 11       | inferred         |
| uo_out[4] | 45        | 37          | JA7          | 19       | read             |
| uo_out[5] | 46        | 38          | JA8          | 21       | read             |
| uo_out[6] | 47        | 39          | JA9          | 20       | read             |
| uo_out[7] | 48        | 40          | JA10         | 18       | read             |

## uio

The 8-bit bidirectional bus, connected through the third PMOD header of the demo PCB to PMOD HAT port JB.

| Bit    | iCE40 Pin | RP2350 GPIO | PMOD HAT Pin | RPi GPIO | Read or inferred |
| ------ | --------- | ----------- | ------------ | -------- | ---------------- |
| uio[0] | 2         | 25          | JB1          | 7        | inferred         |
| uio[1] | 4         | 26          | JB2          | 10       | inferred         |
| uio[2] | 3         | 27          | JB3          | 9        | inferred         |
| uio[3] | 6         | 28          | JB4          | 11       | inferred         |
| uio[4] | 9         | 29          | JB7          | 26       | inferred         |
| uio[5] | 10        | 30          | JB8          | 13       | inferred         |
| uio[6] | 11        | 31          | JB9          | 3        | inferred         |
| uio[7] | 12        | 32          | JB10         | 2        | inferred         |

## UART interface

The Tiny Tapeout standard UART uses `ui_in[3]` (RX) and `uo_out[4]` (TX), following the [Tiny Tapeout UART0 convention](../../pmod/tinytapeout.md#uart-via-rp2040rp2350-built-in-usb-bridge-no-pmod-needed).

Two records disagree about where the UART signals land on the HAT and the Pi: the pin map above and the [loopback test's board config](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/pmod-loopback/host/test_pmod_loopback.py). [Test-designs issue #58](https://github.com/fpgas-online/fpgas.online-test-designs/issues/58) and [test-designs issue #19](https://github.com/fpgas-online/fpgas.online-test-designs/issues/19) hold it.

The first HAT Pin and RPi GPIO pair is from the pin map above, and the second pair from the loopback test's board config.

| Signal                    | iCE40 Pin | TT Signal | RP2350 GPIO | HAT Pin (pin map) | RPi GPIO (pin map) | HAT Pin (loopback config) | RPi GPIO (loopback config) |
| ------------------------- | --------- | --------- | ----------- | ----------------- | ------------------ | ------------------------- | -------------------------- |
| Serial RX (FPGA receives) | 21        | ui_in[3]  | GPIO20      | JC4               | 17                 | JC9                       | 5                          |
| Serial TX (FPGA sends)    | 45        | uo_out[4] | GPIO37      | JA7               | 19                 | JA4                       | 11                         |

How a test reaches these pins is on [Serial port ownership on a Tiny Tapeout FPGA demo board](serial-port.md#how-a-test-reaches-the-fpga-uart).

## PMOD loopback

Item names the part of the GPIO loopback test, and Value gives it.

| Item | Value |
| ---- | ----- |
| Driven pins | all 8 `ui_in` pins |
| Read pins | all 8 `uo_out` pins |
| FPGA function | `uo_out = ~ui_in` |
| GPIOs contended with SPI0 | GPIO7-11, which carry JB1/`uio[0]` and JA1-4/`uo_out[0:3]` |
| RP2350 GPIOs | released to high impedance after FPGA programming, by the tools that load the design |

The step that frees the SPI pins is [How to free the Raspberry Pi's SPI pins before a PMOD test](../checks/free-spi-pins.md).

## SPI flash

These are dedicated iCE40 SPI pins on the FPGA breakout board, not shared with PMOD. Whether the breakout has a flash is [test-designs issue #258](https://github.com/fpgas-online/fpgas.online-test-designs/issues/258). Signal names the flash signal and iCE40 Pin the ball that carries it.

| Signal | iCE40 Pin |
| ------ | --------- |
| CS_N   | 16        |
| CLK    | 15        |
| MISO   | 17        |
| MOSI   | 14        |

## 7-segment display pins

The 7-segment LED display is connected to `uo_out[0:6]`. Segment names the segment, TT Signal the output that drives it, and iCE40 Pin the ball behind that output.

| Segment | TT Signal | iCE40 Pin |
| ------- | --------- | --------- |
| a       | uo_out[0] | 38        |
| b       | uo_out[1] | 42        |
| c       | uo_out[2] | 43        |
| d       | uo_out[3] | 44        |
| e       | uo_out[4] | 45        |
| f       | uo_out[5] | 46        |
| g       | uo_out[6] | 47        |

## Other signals

Signal names the signal, iCE40 Pin the ball that carries it, and Function what it does.

| Signal     | iCE40 Pin | Function                            |
| ---------- | --------- | ----------------------------------- |
| clk_rp2040 | 20        | 50 MHz clock from RP2350 PWM GPIO16 |
| rst_n      | 37        | Reset (active low)                  |
| RGB LED R  | 39        | Accent LED (active low)             |
| RGB LED G  | 40        | Accent LED (active low)             |
| RGB LED B  | 41        | Accent LED (active low)             |
