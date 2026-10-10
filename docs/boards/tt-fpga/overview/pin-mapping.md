---
type: reference
owner: documentation maintainers
reader: someone looking up the pins of a Tiny Tapeout signal
review: 2026-11-10
---

# Tiny Tapeout FPGA demo board pin mapping

**You want to look up where a signal of the demo board v3 (TTDBv3) goes, from the iCE40 ball to the Raspberry Pi GPIO.**

This is the mapping as connected in the fpgas.online test infrastructure, measured on the board. The wires between the PMOD HAT and the demo board are on [Tiny Tapeout FPGA demo board wiring to a Raspberry Pi](../setup/wiring.md). The other figures are on [Tiny Tapeout FPGA demo board specifications](specifications.md).

The spec-derived RP2350 map on [Tiny Tapeout PMOD layouts](../../pmod/tinytapeout.md#rp2350-gpio-mapping-demo-board-v3-tt09) agrees with the measured mapping below.

In it, `ui_in[0:7]` is on GPIO17 to GPIO24, `uio[0:7]` on GPIO25 to GPIO32 and `uo_out[0:7]` on GPIO33 to GPIO40. Each PMOD connector is wired straight through, with bit 0 on pin 1 and bit 7 on pin 10.

In the tables, Bit is the Tiny Tapeout signal, and iCE40 Pin the ball number on the iCE40UP5K-SG48. RP2350 GPIO is the controller pin on the same trace. PMOD HAT Pin is the connector pin on the PMOD HAT, and RPi GPIO the Raspberry Pi GPIO behind it.

## ui_in

The 8-bit input bus. The Raspberry Pi drives these through the PMOD HAT, and the FPGA reads them.

| Bit      | iCE40 Pin | RP2350 GPIO | PMOD HAT Pin | RPi GPIO |
| -------- | --------- | ----------- | ------------ | -------- |
| ui_in[0] | 13        | 17          | JC1          | 16       |
| ui_in[1] | 19        | 18          | JC2          | 14       |
| ui_in[2] | 18        | 19          | JC3          | 15       |
| ui_in[3] | 21        | 20          | JC4          | 17       |
| ui_in[4] | 23        | 21          | JC7          | 4        |
| ui_in[5] | 25        | 22          | JC8          | 12       |
| ui_in[6] | 26        | 23          | JC9          | 5        |
| ui_in[7] | 27        | 24          | JC10         | 6        |

## uo_out

The 8-bit output bus. The FPGA drives these, and the Raspberry Pi reads them through the PMOD HAT.

| Bit       | iCE40 Pin | RP2350 GPIO | PMOD HAT Pin | RPi GPIO |
| --------- | --------- | ----------- | ------------ | -------- |
| uo_out[0] | 38        | 33          | JA1          | 8        |
| uo_out[1] | 42        | 34          | JA2          | 10       |
| uo_out[2] | 43        | 35          | JA3          | 9        |
| uo_out[3] | 44        | 36          | JA4          | 11       |
| uo_out[4] | 45        | 37          | JA7          | 19       |
| uo_out[5] | 46        | 38          | JA8          | 21       |
| uo_out[6] | 47        | 39          | JA9          | 20       |
| uo_out[7] | 48        | 40          | JA10         | 18       |

`uo_out[1:3]` are on JA pins 2-4, which share Raspberry Pi GPIOs with JB pins 2-4: [Shared GPIOs of JA and JB](../setup/wiring.md#shared-gpios-of-ja-and-jb).

## uio

The 8-bit bidirectional bus. It is connected through the third PMOD header of the demo PCB to PMOD HAT port JB. The RP2350 GPIO numbers follow the sequential pattern (`ui_in` 17-24, `uio` 25-32, `uo_out` 33-40).

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

The five `uio` bits that are not shared (`uio[0]`, `uio[4:7]`) are on JB pins 1 and 7-10. They use unique Raspberry Pi GPIOs and work correctly.

## UART interface

The Tiny Tapeout standard UART uses `ui_in[3]` (RX) and `uo_out[4]` (TX), following the [Tiny Tapeout UART0 convention](../../pmod/tinytapeout.md#uart-via-rp2040rp2350-built-in-usb-bridge-no-pmod-needed). The PMOD HAT Pin and RPi GPIO columns follow the mapping in `verify-hardware.md` and `test_pmod_loopback.py`.

| Signal                    | iCE40 Pin | TT Signal | RP2350 GPIO | PMOD HAT Pin | RPi GPIO |
| ------------------------- | --------- | --------- | ----------- | ------------ | -------- |
| Serial RX (FPGA receives) | 21        | ui_in[3]  | GPIO20      | JC9          | 5        |
| Serial TX (FPGA sends)    | 45        | uo_out[4] | GPIO37      | JA4          | 11       |

Under the `ui_in` and `uo_out` tables above the same two signals land on JC4/GPIO17 and JA7/GPIO19 instead. The iCE40 pins (21, 45), the Tiny Tapeout signals and the RP2350 GPIOs (20, 37) are the same either way. Only the PMOD HAT pin and the Raspberry Pi GPIO move.

How a test reaches these pins is on [Serial port ownership on a Tiny Tapeout FPGA demo board](serial-port.md#how-a-test-reaches-the-fpga-uart).

## PMOD loopback

The GPIO loopback test uses all 8 `ui_in` pins (drive) and all 8 `uo_out` pins (read). The FPGA computes `uo_out = ~ui_in`. The `ui_in` and `uo_out` tables above give the full mapping.

GPIO7-11 are contended with the SPI0 bus whichever mapping applies. Under the `ui_in` and `uo_out` tables above they carry JB1/`uio[0]` and JA1-4/`uo_out[0:3]`. The RP2350 GPIOs must be released to high impedance after FPGA programming, which the programming wrapper does by itself. The step that frees the SPI pins is on [How to free the Raspberry Pi's SPI pins before a PMOD test](../checks/free-spi-pins.md).

## SPI flash

The SPI flash is on the FPGA breakout board, for persistent bitstream storage, and the SPI Flash ID test uses it. Its pins are dedicated iCE40 SPI pins, not shared with PMOD. Signal names the flash signal and iCE40 Pin the ball that carries it.

| Signal | iCE40 Pin |
| ------ | --------- |
| CS_N   | 16        |
| CLK    | 15        |
| MISO   | 17        |
| MOSI   | 14        |

## 7-segment display pins

The 7-segment LED display is connected to `uo_out[0:6]`. The display shares the same PMOD traces, so it reflects the test patterns while the Raspberry Pi drives GPIO tests. Segment names the segment, TT Signal the output that drives it, and iCE40 Pin the ball behind that output.

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
