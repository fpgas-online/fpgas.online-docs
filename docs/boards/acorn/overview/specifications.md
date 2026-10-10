---
type: reference
owner: documentation maintainers
reader: someone looking up a figure or a pin of the Acorn card
review: 2026-11-10
---

# Acorn specifications

This page lists the figures and FPGA pins of the Acorn: FPGA, PCIe interface, clock, LEDs, serial pins, flash and
memory. It does not describe the card as a whole: that is [The Acorn card](card.md).

## Key specifications

Parameter names a property and Value is its figure for the CLE-215+. The figures come from the [LiteX platform file](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/sqrl_acorn.py).
The other cards are in [Acorn variants](../which-one.md#compatible-boards).

| Parameter        | Value                                                              |
| ---------------- | ------------------------------------------------------------------ |
| FPGA             | Xilinx Artix-7 XC7A200T-FBG484-3                                   |
| Package          | FBG484 (484-ball BGA)                                              |
| Logic cells      | 215,360                                                            |
| CLB flip-flops   | 269,200                                                            |
| DSP slices       | 740                                                                |
| Block RAM        | 13,140 Kib                                                         |
| GTP transceivers | 4 (up to 6.6 Gb/s each)                                            |
| DDR3 SDRAM       | 1 GiB (one MT41K512M16, 16-bit)                                    |
| SPI Flash        | S25FL256S (256 Mbit, quad SPI, multiboot with fallback and operational regions) |
| PCIe             | Gen2 x4 (M.2 M-key)                                                |
| Form factor      | M.2 2280                                                           |
| Power            | Via M.2 / mPCIe slot (3.3V)                                        |
| Process          | 28 nm HPL                                                          |

## PCIe interface

Parameter names a property and Value is what the card or the host shows for it.

| Parameter                                  | Value                                    |
| ------------------------------------------ | ---------------------------------------- |
| Link                                       | Gen2 x4 (4-lane GTP transceivers)        |
| Connector                                  | M.2 M-key                                |
| Reference clock                            | Differential (FPGA pins F6/E6)           |
| Reset                                      | LVCMOS33 (FPGA pin J1, internal pull-up) |
| Vendor:Device, CLE-215+ factory (mining) firmware | `1e24:021f` (Squirrels Research Labs "Acorn CLE-215+") |
| Vendor:Device, CLE-101 factory firmware    | `1e24:0101`                              |
| Vendor:Device, vendor (RHS Research) XDMA sample image | `10ee:7011` (Xilinx)         |
| Vendor:Device, LiteX x1 PCIe design        | `10ee:7021`                              |
| PCIe bus address on a Raspberry Pi 5       | `0001:01:00.0`                           |
| PCIe bus address of the RP1 south bridge on a Raspberry Pi 5 | `0002:01:00.0`         |

## Clock

Signal names the clock, FPGA Pins are its balls, Standard is its I/O standard, Frequency its rate.

| Signal         | FPGA Pins | Standard    | Frequency |
| -------------- | --------- | ----------- | --------- |
| System clock   | J19 / H19 | DIFF_SSTL15 | 200 MHz   |
| PCIe ref clock | F6 / E6   | —           | 100 MHz   |

## User LEDs

LED is the LED's number and FPGA Pin the ball that drives it.

| LED | FPGA Pin |
| --- | -------- |
| 0   | G3       |
| 1   | H3       |
| 2   | G4       |
| 3   | H4       |

## Serial (UART)

Signal is the line on the P2 connector and FPGA Pin the ball behind it.

| Signal | FPGA Pin |
| ------ | -------- |
| RX     | J2       |
| TX     | K2       |

## SPI Flash

Signal is the flash line and FPGA Pin the ball behind it.

| Signal | FPGA Pin |
| ------ | -------- |
| CS_n   | T19      |
| MOSI   | P22      |
| MISO   | R22      |
| WP     | P21      |
| HOLD   | R21      |

## DDR3 SDRAM

Parameter names a property of the memory and Value is its figure.

| Parameter                          | Value                         |
| ---------------------------------- | ----------------------------- |
| Part                               | MT41K512M16 (x16)             |
| Capacity                           | 1 GiB                         |
| Data width                         | 16 bits, two byte lanes       |
| PHY                                | 7-series DDR PHY (A7DDRPHY)   |
| Rate in the fpgas.online Acorn design | 800 MT/s                   |

Signal is the DDR3 line and FPGA pins are the balls behind it, as in the LiteX platform file `sqrl_acorn.py`.

| Signal       | FPGA pins |
| ------------ | --------- |
| A[15:0]      | M15 L21 M16 L18 K21 M18 M21 N20 M20 N19 J21 M22 K22 N18 N22 J22 |
| BA[2:0]      | L19 J20 L20 |
| DQ[7:0]      | D19 B20 E19 A20 F19 C19 F20 C18 |
| DQ[15:8]     | E22 G21 D20 E21 C22 D21 B22 D22 |
| DM[1:0]      | A19 G22 |
| DQS_P[1:0]   | F18 B21 |
| DQS_N[1:0]   | E18 A21 |
| CLK_P / CLK_N | K17 / J17 |
| CKE          | H22 |
| ODT          | K19 |
| RAS_N        | H20 |
| CAS_N        | K18 |
| WE_N         | L16 |
| RESET_N      | K16 (LVCMOS15) |
| CS_N         | none in the platform file |

Lines is the group of DDR3 lines and I/O standard the standard they use.

| Lines                              | I/O standard |
| ---------------------------------- | ------------ |
| Every line except RESET_N, DQS and the clock pairs | SSTL15 |
| DQS and clock pairs                | DIFF_SSTL15  |
| RESET_N                            | LVCMOS15     |
