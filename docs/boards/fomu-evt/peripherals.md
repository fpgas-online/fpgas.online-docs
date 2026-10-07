# Fomu EVT: SPI flash, RGB LED, touch pads, buttons, PMOD, I2C and debug header

**You are building or checking a design that uses one of the Fomu's on-board peripherals or its PMOD pins.**

## SPI Flash

The Fomu stores its bitstream in an external SPI flash on dedicated iCE40 SPI
pins. The iCE40UP5K loads the bitstream from flash automatically on power-up.

| Signal     | iCE40 Pin | I/O Standard |
| ---------- | --------- | ------------ |
| CS_N       | 16        | LVCMOS33     |
| CLK        | 15        | LVCMOS33     |
| MOSI (DQ0) | 14        | LVCMOS33     |
| MISO (DQ1) | 17        | LVCMOS33     |
| WP (DQ2)   | 18        | LVCMOS33     |
| HOLD (DQ3) | 19        | LVCMOS33     |

Quad SPI (4x) mode is supported, via the `spiflash4x` resource in the LiteX
platform file.

Source: [LiteX platform file for the Fomu EVT](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_fomu_evt.py)

## RGB LED

The Fomu has a single RGB LED driven by the iCE40UP5K's internal LED driver IP
(an active-low LED driven through the `SB_RGBA_DRV` primitive).

| Color | FPGA Pin | Active |
| ----- | -------- | ------ |
| Red   | 40       | Low    |
| Green | 39       | Low    |
| Blue  | 41       | Low    |

The `user_led_n` signal (active-low) is on pin 41 (blue).

## Touch Pads

The EVT board has 4 capacitive touch pads that can be used as user inputs.

| Pad     | FPGA Pin |
| ------- | -------- |
| Touch 0 | 48       |
| Touch 1 | 47       |
| Touch 2 | 46       |
| Touch 3 | 45       |

These are directly connected to FPGA I/O pins. Capacitive touch sensing is
implemented in the FPGA fabric.

## Buttons

Two active-low buttons:

| Button | FPGA Pin | I/O Standard |
| ------ | -------- | ------------ |
| BTN0   | 42       | LVCMOS33     |
| BTN1   | 38       | LVCMOS33     |

## PMOD Connectors

The EVT board has two half-PMOD connectors — a standard 6-pin PMOD carrying 4
signals plus GND and VCC, 4 signal pins each. The loopback gateware drives them
against each other; see [PMOD / GPIO loopback](loopback.md#pmod--gpio-loopback).

### PMODA_N

| Index | FPGA Pin |
| ----- | -------- |
| 0     | 28       |
| 1     | 27       |
| 2     | 26       |
| 3     | 23       |

### PMODB_N

| Index | FPGA Pin |
| ----- | -------- |
| 0     | 48       |
| 1     | 47       |
| 2     | 46       |
| 3     | 45       |

Note: PMODB_N shares its pins with the touch pads.

Source: [LiteX platform file for the Fomu EVT](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_fomu_evt.py)

## I2C

| Signal | iCE40 Pin | I/O Standard |
| ------ | --------- | ------------ |
| SCL    | 12        | LVCMOS18     |
| SDA    | 20        | LVCMOS18     |

Note that the I2C interface uses LVCMOS18 (1.8V) rather than the 3.3V used by
every other pin on the board.

## Debug Header

The Fomu EVT has a debug connector with 6 pins:

| Index | iCE40 Pin |
| ----- | --------- |
| dbg:0 | 20        |
| dbg:1 | 12        |
| dbg:2 | 11        |
| dbg:3 | 25        |
| dbg:4 | 10        |
| dbg:5 | 9         |
