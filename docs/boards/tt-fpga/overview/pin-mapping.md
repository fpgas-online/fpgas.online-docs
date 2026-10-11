---
type: reference
owner: documentation maintainers
reader: someone looking up the pins of a Tiny Tapeout signal
review: 2026-11-10
---

# Tiny Tapeout FPGA demo board pin mapping

**You want to look up where a signal of the demo board v3 (TTDBv3) goes, from the iCE40 ball to the Raspberry Pi GPIO.**

This is the mapping as connected in the fpgas.online test infrastructure. The wires between the PMOD HAT and the demo board are on [Tiny Tapeout FPGA demo board wiring to a Raspberry Pi](../setup/wiring.md). The other figures are on [Tiny Tapeout FPGA demo board specifications](specifications.md).

The check expects `ui_in` on HAT JA, `uio` on HAT JB and `uo_out` on HAT JC. The boards measured with the pin-id design and by the check are cabled that way.

The shipped RP2350 firmware loaded `GPIOMapTT04` instead of `GPIOMapTTDBv3`, returning incorrect GPIO numbers. All pin numbers on this page are the correct TTDBv3 values, not the firmware-reported ones.

The spec-derived map ([PMOD layouts](../../pmod/tinytapeout.md#rp2350-gpio-mapping-demo-board-v3-tt09)) agrees. `ui_in[0:7]` is on GPIO17 to GPIO24, `uio[0:7]` on GPIO25 to GPIO32 and `uo_out[0:7]` on GPIO33 to GPIO40. Each PMOD connector is wired straight through, with bit 0 on pin 1 and bit 7 on pin 10.

In the tables, Bit is the Tiny Tapeout signal, and iCE40 Pin the ball number on the iCE40UP5K-SG48. RP2350 GPIO is the controller pin on the same trace. PMOD HAT Pin is the connector pin on the PMOD HAT, and RPi GPIO the Raspberry Pi GPIO behind it.

Read or inferred, in the `ui_in` and `uo_out` tables, is `read` where the pin-id design decoded the signal. It is `inferred` where the position follows from the straight-through wiring.

## ui_in

The 8-bit input bus. The Raspberry Pi drives these through the PMOD HAT, and the FPGA reads them. They are cabled to PMOD HAT port JA.

Six wires were not read back: `ui_in[1:3]` and `uio[1:3]`, which share Raspberry Pi GPIOs. Their positions are inferred from the pattern of bit 0 on pin 1 and bit 7 on pin 10: [test-designs issue #142](https://github.com/fpgas-online/fpgas.online-test-designs/issues/142). The HAT joins the JA wire and the JB wire of the same number (2, 3 or 4) on one Raspberry Pi pin. No test can therefore tell those two wires swapped with each other.

| Bit      | iCE40 Pin | RP2350 GPIO | PMOD HAT Pin | RPi GPIO | Read or inferred |
| -------- | --------- | ----------- | ------------ | -------- | ---------------- |
| ui_in[0] | 13 | 17 | JA1 | 8 | read |
| ui_in[1] | 19 | 18 | JA2 | 10 | inferred |
| ui_in[2] | 18 | 19 | JA3 | 9 | inferred |
| ui_in[3] | 21 | 20 | JA4 | 11 | inferred |
| ui_in[4] | 23 | 21 | JA7 | 19 | read |
| ui_in[5] | 25 | 22 | JA8 | 21 | read |
| ui_in[6] | 26 | 23 | JA9 | 20 | read |
| ui_in[7] | 27 | 24 | JA10 | 18 | read |

## uo_out

The 8-bit output bus. The FPGA drives these, and the Raspberry Pi reads them through the PMOD HAT. They are cabled to PMOD HAT port JC.

| Bit       | iCE40 Pin | RP2350 GPIO | PMOD HAT Pin | RPi GPIO | Read or inferred |
| --------- | --------- | ----------- | ------------ | -------- | ---------------- |
| uo_out[0] | 38 | 33 | JC1 | 16 | read |
| uo_out[1] | 42 | 34 | JC2 | 14 | read |
| uo_out[2] | 43 | 35 | JC3 | 15 | read |
| uo_out[3] | 44 | 36 | JC4 | 17 | read |
| uo_out[4] | 45 | 37 | JC7 | 4 | read |
| uo_out[5] | 46 | 38 | JC8 | 12 | read |
| uo_out[6] | 47 | 39 | JC9 | 5 | read |
| uo_out[7] | 48 | 40 | JC10 | 6 | read |

## uio

The 8-bit bidirectional bus, connected through the third PMOD header of the demo PCB to PMOD HAT port JB.

| Bit    | iCE40 Pin | RP2350 GPIO | PMOD HAT Pin | RPi GPIO |
| ------ | --------- | ----------- | ------------ | -------- |
| uio[0] | 2         | 25          | JB1          | 7        |
| uio[1] | 4         | 26          | JB2          | 10       |
| uio[2] | 3         | 27          | JB3          | 9        |
| uio[3] | 6         | 28          | JB4          | 11       |
| uio[4] | 9         | 29          | JB7          | 26       |
| uio[5] | 10        | 30          | JB8          | 13       |
| uio[6] | 11        | 31          | JB9          | 3        |
| uio[7] | 12        | 32          | JB10         | 2        |

## UART interface

The Tiny Tapeout standard UART uses `ui_in[3]` (RX) and `uo_out[4]` (TX), following the [Tiny Tapeout UART0 convention](../../pmod/tinytapeout.md#uart-via-rp2040rp2350-built-in-usb-bridge-no-pmod-needed).

Signal names the UART signal, and TT Signal the Tiny Tapeout signal that carries it. The other columns are as above.

| Signal | iCE40 Pin | TT Signal | RP2350 GPIO | HAT Pin | RPi GPIO |
| ------ | --------- | --------- | ----------- | ------- | -------- |
| Serial RX (FPGA receives) | 21 | ui_in[3] | GPIO20 | JA4 | 11 |
| Serial TX (FPGA sends) | 45 | uo_out[4] | GPIO37 | JC7 | 4 |

How a test reaches these pins is on [Serial port ownership on a Tiny Tapeout FPGA demo board](serial-port.md#how-a-test-reaches-the-fpga-uart).

## PMOD loopback

Item names the part of the GPIO loopback test, and Value gives it.

| Item | Value |
| ---- | ----- |
| Driven pins | all 8 `ui_in` pins |
| Read pins | all 8 `uo_out` pins |
| FPGA function | `uo_out = ~ui_in` |
| GPIOs contended with SPI0 | GPIO7-11, which carry JB1/`uio[0]` and JA1-4/`ui_in[0:3]` |
| RP2350 GPIOs | released to high impedance after FPGA programming, by the tools that load the design |

The command that frees the SPI pins is on [Tiny Tapeout FPGA demo board faults on the Raspberry Pi](../troubleshooting/pi-faults.md).

## Configuration SPI

These are the iCE40's dedicated SPI pins on the FPGA breakout board, not shared with PMOD. They go only to the demo board's microcontroller, which loads the bitstream over them; the breakout has no SPI flash. Signal names the SPI function and iCE40 Pin the ball that carries it.

| Signal  | iCE40 Pin |
| ------ | --------- |
| SPI_SS  | 16        |
| SPI_SCK | 15        |
| SPI_SI  | 17        |
| SPI_SO  | 14        |

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
