---
type: reference
owner: documentation maintainers
reader: someone looking up a Fomu EVT's FPGA, memory or pin assignments
review: 2026-11-10
---

# Fomu EVT specifications

**You want the Fomu EVT's key specifications and the iCE40 pin of each peripheral.**

The pins come from the [LiteX platform file for the Fomu EVT](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_fomu_evt.py) and the [Fomu hardware repository](https://github.com/im-tomu/fomu-hardware). The wires to the Raspberry Pi are on [Fomu EVT wiring to a Raspberry Pi](../setup/wiring.md).

## Key specifications

Each row gives a parameter of the board and its value.

| Parameter            | Value                                     |
| -------------------- | ----------------------------------------- |
| FPGA                 | Lattice iCE40UP5K-SG48                    |
| Package              | SG48 (48-pin QFN)                         |
| Logic cells          | 5,280 LUT4s                               |
| SPRAM                | 128 KB (4 x 32 KB blocks)                 |
| DPRAM (EBR)          | 120 Kbit (30 blocks of 4 Kbit, per the [iCE40 UltraPlus data sheet](https://www.latticesemi.com/view_document?document_id=51968)) |
| DSP blocks           | 8 (16x16 multiply-accumulate)             |
| System clock         | 48 MHz (pin 44, LVCMOS33)                 |
| Internal oscillators | 48 MHz HFOSC, 10 kHz LFOSC                |
| USB                  | Native USB 1.1 Full Speed (ValentyUSB core) |
| SPI Flash            | Quad SPI for bitstream storage            |
| RGB LED              | 1 (active-low, pins R=40, G=39, B=41)     |
| Touch pads           | 4 (pins 48, 47, 46, 45)                   |
| PMOD connectors      | 2 half-PMOD (4 signal pins each)          |
| External SDRAM       | None (SPRAM only)                         |
| Form factor          | Fits inside a USB Type-A port             |

## USB interface

The board implements a full USB 1.1 Full Speed device with the ValentyUSB soft core on the iCE40UP5K, and needs no external USB PHY. Each row gives a USB signal, the iCE40 pin it is on, its I/O standard and its use. All USB pins use the LVCMOS33 I/O standard.

| Signal    | iCE40 Pin | I/O Standard | Description                             |
| --------- | --------- | ------------ | --------------------------------------- |
| D+        | 34        | LVCMOS33     | USB data positive                       |
| D-        | 37        | LVCMOS33     | USB data negative                       |
| Pull-up   | 35        | LVCMOS33     | 1.5K pullup for Full Speed identification |
| Pull-down | 36        | LVCMOS33     | Pulldown resistor control               |

## Serial (UART)

Each row gives a serial signal of the board, its FPGA pin, its I/O standard and a note.

| Signal | FPGA Pin | I/O Standard | Notes       |
| ------ | -------- | ------------ | ----------- |
| RX     | 21       | LVCMOS33     |             |
| TX     | 13       | LVCMOS33     | Has PULLUP  |

## SPI flash

The board stores its bitstream in an external SPI flash on dedicated iCE40 SPI pins. Each row gives a flash signal, its iCE40 pin and its I/O standard. Quad SPI (4x) mode is supported, via the `spiflash4x` resource in the LiteX platform file.

| Signal     | iCE40 Pin | I/O Standard |
| ---------- | --------- | ------------ |
| CS_N       | 16        | LVCMOS33     |
| CLK        | 15        | LVCMOS33     |
| MOSI (DQ0) | 14        | LVCMOS33     |
| MISO (DQ1) | 17        | LVCMOS33     |
| WP (DQ2)   | 18        | LVCMOS33     |
| HOLD (DQ3) | 19        | LVCMOS33     |

## RGB LED

The board has a single RGB LED, driven by the iCE40UP5K's internal LED driver IP through the `SB_RGBA_DRV` primitive. Each row gives a colour, its FPGA pin and the level that lights it. The `user_led_n` signal (active-low) is on pin 41 (blue).

| Color | FPGA Pin | Active |
| ----- | -------- | ------ |
| Red   | 40       | Low    |
| Green | 39       | Low    |
| Blue  | 41       | Low    |

## Touch pads

The board has 4 capacitive touch pads that can be used as user inputs, directly connected to FPGA I/O pins. Each row gives a pad and its FPGA pin. Capacitive touch sensing is implemented in the FPGA fabric.

| Pad     | FPGA Pin |
| ------- | -------- |
| Touch 0 | 48       |
| Touch 1 | 47       |
| Touch 2 | 46       |
| Touch 3 | 45       |

## Buttons

The board has two active-low buttons. Each row gives a button, its FPGA pin and its I/O standard.

| Button | FPGA Pin | I/O Standard |
| ------ | -------- | ------------ |
| BTN0   | 42       | LVCMOS33     |
| BTN1   | 38       | LVCMOS33     |

## PMOD connectors

The board has two half-PMOD connectors, each a standard 6-pin PMOD carrying 4 signals plus GND and VCC. Each row of the next two tables gives a signal index and its FPGA pin. PMODB_N shares its pins with the touch pads.

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

## I2C

Each row gives an I2C signal, its iCE40 pin and its I/O standard. The I2C interface uses LVCMOS18 (1.8V) rather than the 3.3V used by every other pin on the board.

| Signal | iCE40 Pin | I/O Standard |
| ------ | --------- | ------------ |
| SCL    | 12        | LVCMOS18     |
| SDA    | 20        | LVCMOS18     |

## Debug header

The board has a debug connector with 6 pins. Each row gives a header index and its iCE40 pin.

| Index | iCE40 Pin |
| ----- | --------- |
| dbg:0 | 20        |
| dbg:1 | 12        |
| dbg:2 | 11        |
| dbg:3 | 25        |
| dbg:4 | 10        |
| dbg:5 | 9         |

## Clock, LED and button signals

Each row gives a signal name of the platform file, its iCE40 pin, its I/O standard and its function.

| Signal          | iCE40 Pin | IO Standard | Function                 |
| --------------- | --------- | ----------- | ------------------------ |
| clk48           | 44        | LVCMOS33    | 48 MHz oscillator input  |
| user_led_n      | 41        | LVCMOS33    | User LED (active low)    |
| RGB LED R       | 40        | LVCMOS33    | RGB LED red              |
| RGB LED G       | 39        | LVCMOS33    | RGB LED green            |
| RGB LED B       | 41        | LVCMOS33    | RGB LED blue             |
| user_btn_n[0]   | 42        | LVCMOS33    | Capacitive touch button  |
| user_btn_n[1]   | 38        | LVCMOS33    | Capacitive touch button  |

## DFU bootloader

Each row gives a parameter of the DFU interface that loads a design and its value.

| Parameter      | Value                                |
| -------------- | ------------------------------------ |
| Interface      | USB DFU (flash user image)           |
| USB VID:PID    | `1209:5bf0` (DFU bootloader)         |
| Tool           | `openFPGALoader -b fomu <bitstream>` |
| Bitstream type | `.bin` (flash user image, 0x40000)  |
| Bootloader     | DFU Bootloader v2.0.4                |

## LiteX integration

Each row gives a property of the LiteX support for the board and its value. The `Programmer` row is the LiteX platform's default; fpgas.online loads the board over USB DFU with `openFPGALoader`.

| Property        | Value                                             |
| --------------- | ------------------------------------------------- |
| Platform module | `litex_boards.platforms.kosagi_fomu_evt`          |
| Target module   | `litex_boards.targets.kosagi_fomu`                |
| Default clock   | `clk48` (48 MHz, pin 44)                          |
| Programmer      | IceStorm (`iceprog`)                              |
| Toolchain       | Yosys + nextpnr-ice40 (open source, IceStorm flow) |
