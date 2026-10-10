---
type: reference
owner: documentation maintainers
reader: someone looking up a figure or a pin of the Digilent Arty A7
review: 2026-11-10
---

# Arty A7 specifications

**You want to look up a figure or an FPGA pin of an Arty A7.**

The page covers the device, serial pins, memory, Ethernet, PMOD connectors and flash. The board as a whole is on [The Arty A7 board](board.md). The wires to the Raspberry Pi are on [Arty A7 wiring to a Raspberry Pi](../setup/wiring.md).

## Key specifications

Parameter names a feature of the board and Value gives it. The values come from the [Digilent Arty A7 Reference Manual](https://digilent.com/reference/programmable-logic/arty-a7/reference-manual).

| Parameter | Value |
|-----------|-------|
| FPGA (A7-35 variant) | Xilinx Artix-7 XC7A35T**I**CSG324-1L |
| FPGA (A7-100 variant) | Xilinx Artix-7 XC7A100TCSG324-1 |
| Package | CSG324 (324-ball BGA) |
| System clock | 100 MHz (pin E3, LVCMOS33) |
| DDR3 SDRAM | 256 MB, MT41K128M16JT-125 (16-bit bus) |
| Ethernet PHY | TI DP83848J, MII interface (100Base-T) |
| USB-UART/JTAG | FTDI FT2232HQ (dual-channel) |
| SPI Flash | Quad SPI (pins L13, L16, K17, K18, L14, M14) |
| User LEDs | 4 green (H5, J5, T9, T10) + 4 RGB |
| User switches | 4 (A8, C11, C10, A10) |
| User buttons | 4 (D9, C9, B9, B8) |
| PMOD connectors | 4x 12-pin (JA, JB, JC, JD) |
| I/O standard | LVCMOS33 (3.3V) for most I/O |
| Power | USB or external 7-15V |

The bold **I** in the A7-35 device string is the temperature grade. The boards in the fleet are the industrial-grade, low-power part, which is the `a7-35` variant below.

## FPGA device variants

Variant is the LiteX name, Device String is the part it selects, and Notes says how the two differ. The [LiteX platform file](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/digilent_arty.py) defines both.

| Variant | Device String | Notes |
|---------|--------------|-------|
| `a7-35` | `xc7a35ticsg324-1L` | Industrial temp, low power |
| `a7-100` | `xc7a100tcsg324-1` | Larger fabric, commercial temp |

## Serial (UART)

The primary serial port uses the FTDI FT2232HQ USB-to-UART bridge. It is not a GPIO connection. It goes through USB, so the FPGA's TX and RX pins face the on-board FTDI chip rather than the Raspberry Pi header. The FTDI chip provides two channels: Channel A for JTAG and Channel B for UART.

Signal names the line and its direction as seen from the Raspberry Pi. FPGA Pin is the ball, Direction is as the FPGA sees it, and IO Standard is its electrical standard.

| Signal | FPGA Pin | Direction | IO Standard |
| --------------- | -------- | --------- | ----------- |
| TX (FPGA → RPi) | D10      | Output    | LVCMOS33    |
| RX (RPi → FPGA) | A9       | Input     | LVCMOS33    |

## DDR3 SDRAM

The memory has these properties, from the [LiteX platform file](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/digilent_arty.py):

- Part: MT41K128M16JT-125 (Micron, 128M x 16-bit = 256 MB)
- Interface: 16-bit data bus (DQ[15:0]), 2 byte lanes (DM/DQS pairs)
- I/O Standard: SSTL135 (1.35V)
- FPGA I/O bank 34 has INTERNAL_VREF set to 0.675V

Signal is a DDR3 line or bus, FPGA Pins lists its balls in bit order, and IO Standard is its electrical standard.

| Signal        | FPGA Pins                                 | IO Standard  |
| ------------- | ----------------------------------------- | ------------ |
| A[13:0]       | R2 M6 N4 T1 N6 R7 V6 U7 R8 V7 R6 U6 T6 T8 | SSTL135      |
| BA[2:0]       | R1 P4 P2                                  | SSTL135      |
| DQ[7:0]       | K5 L3 K3 L6 M3 M1 L4 M2                   | SSTL135      |
| DQ[15:8]      | V4 T5 U4 V5 V1 T3 U3 R3                   | SSTL135      |
| DQS_P[1:0]    | N2 U2                                     | DIFF_SSTL135 |
| DQS_N[1:0]    | N1 V2                                     | DIFF_SSTL135 |
| DM[1:0]       | L1 U1                                     | SSTL135      |
| CLK_P / CLK_N | U9 / V9                                   | DIFF_SSTL135 |
| CKE           | N5                                        | SSTL135      |
| ODT           | R5                                        | SSTL135      |
| CS_N          | U8                                        | SSTL135      |
| RAS_N         | P3                                        | SSTL135      |
| CAS_N         | M4                                        | SSTL135      |
| WE_N          | P5                                        | SSTL135      |
| RESET_N       | K6                                        | SSTL135      |

## MII Ethernet

The Arty uses a TI DP83848J Ethernet PHY with a standard MII (Media Independent Interface), supporting 10/100 Mbps. Every MII signal is LVCMOS33. The pins are from the [LiteX platform file](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/digilent_arty.py) and the [Digilent Arty A7 Reference Manual](https://digilent.com/reference/programmable-logic/arty-a7/reference-manual).

Signal is the MII line, FPGA Pin is its ball, and Direction is as the FPGA sees it.

| Signal | FPGA Pin | Direction |
|--------|----------|-----------|
| ref_clk | G18 | Output (25 MHz) |
| tx_clk | H16 | Input |
| rx_clk | F15 | Input |
| rst_n | C16 | Output |
| mdio | K13 | Bidirectional |
| mdc | F16 | Output |
| rx_dv | G16 | Input |
| rx_er | C17 | Input |
| rx_data[3:0] | D18 E17 E18 G17 | Input |
| tx_en | H15 | Output |
| tx_data[3:0] | H14 J14 J13 H17 | Output |
| col | D17 | Input |
| crs | G14 | Input |

## PMOD connectors

The Arty A7 has four 12-pin PMOD connectors (JA through JD). Each provides 8 signal pins plus power (VCC) and ground (GND). All PMOD I/O use the LVCMOS33 (3.3V) standard.

### PMOD pin numbering

Pins 1-4 are the top row, pins 5-8 are the bottom row. LiteX numbers the eight signals 0-7, where 0-3 are the top row and 4-7 the bottom row. The physical connector numbers the bottom row 7-10, because pins 5 and 6 of each row are GND and VCC. The per-connector tables below use the physical numbering, as does the [PMOD interface specification](../../pmod/index.md).

```text
           ┌─────────────────────────────────────┐
Top row:   │ Pin1  Pin2  Pin3  Pin4  GND   VCC   │
Bottom row:│ Pin5  Pin6  Pin7  Pin8  GND   VCC   │
           └─────────────────────────────────────┘
```

### PMOD FPGA pin assignments

LiteX Index is the signal's number in LiteX, and each other column is the ball on that connector. The balls are from `_connectors` in the [LiteX platform file](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/digilent_arty.py).

| LiteX Index | PMODA (JA) | PMODB (JB) | PMODC (JC) | PMODD (JD) |
|-------------|-----------|-----------|-----------|-----------|
| 0 (top pin 1) | G13 | E15 | U12 | D4 |
| 1 (top pin 2) | B11 | E16 | V12 | D3 |
| 2 (top pin 3) | A11 | D15 | V10 | F4 |
| 3 (top pin 4) | D12 | C15 | V11 | F3 |
| 4 (bottom pin 7) | D13 | J17 | U14 | E2 |
| 5 (bottom pin 8) | B18 | J18 | V14 | D2 |
| 6 (bottom pin 9) | A18 | K15 | T13 | H2 |
| 7 (bottom pin 10) | K16 | J15 | U13 | G2 |

### PMODA

PMOD Pin is the physical pin number and Signal Index is the LiteX resource name. FPGA Pin is the ball, and IO Standard is its electrical standard. The GPIO loopback test uses PMODA (input) and PMODB (output).

| PMOD Pin | Signal Index | FPGA Pin | IO Standard |
| -------- | ------------ | -------- | ----------- |
| 1        | pmoda:0      | G13      | LVCMOS33    |
| 2        | pmoda:1      | B11      | LVCMOS33    |
| 3        | pmoda:2      | A11      | LVCMOS33    |
| 4        | pmoda:3      | D12      | LVCMOS33    |
| 7        | pmoda:4      | D13      | LVCMOS33    |
| 8        | pmoda:5      | B18      | LVCMOS33    |
| 9        | pmoda:6      | A18      | LVCMOS33    |
| 10       | pmoda:7      | K16      | LVCMOS33    |

### PMODB

The columns are as for PMODA.

| PMOD Pin | Signal Index | FPGA Pin | IO Standard |
| -------- | ------------ | -------- | ----------- |
| 1        | pmodb:0      | E15      | LVCMOS33    |
| 2        | pmodb:1      | E16      | LVCMOS33    |
| 3        | pmodb:2      | D15      | LVCMOS33    |
| 4        | pmodb:3      | C15      | LVCMOS33    |
| 7        | pmodb:4      | J17      | LVCMOS33    |
| 8        | pmodb:5      | J18      | LVCMOS33    |
| 9        | pmodb:6      | K15      | LVCMOS33    |
| 10       | pmodb:7      | J15      | LVCMOS33    |

### PMODC

The columns are as for PMODA.

| PMOD Pin | Signal Index | FPGA Pin | IO Standard |
| -------- | ------------ | -------- | ----------- |
| 1        | pmodc:0      | U12      | LVCMOS33    |
| 2        | pmodc:1      | V12      | LVCMOS33    |
| 3        | pmodc:2      | V10      | LVCMOS33    |
| 4        | pmodc:3      | V11      | LVCMOS33    |
| 7        | pmodc:4      | U14      | LVCMOS33    |
| 8        | pmodc:5      | V14      | LVCMOS33    |
| 9        | pmodc:6      | T13      | LVCMOS33    |
| 10       | pmodc:7      | U13      | LVCMOS33    |

### PMODD

The columns are as for PMODA. PMODD is not cabled to the HAT.

| PMOD Pin | Signal Index | FPGA Pin | IO Standard |
| -------- | ------------ | -------- | ----------- |
| 1        | pmodd:0      | D4       | LVCMOS33    |
| 2        | pmodd:1      | D3       | LVCMOS33    |
| 3        | pmodd:2      | F4       | LVCMOS33    |
| 4        | pmodd:3      | F3       | LVCMOS33    |
| 7        | pmodd:4      | E2       | LVCMOS33    |
| 8        | pmodd:5      | D2       | LVCMOS33    |
| 9        | pmodd:6      | H2       | LVCMOS33    |
| 10       | pmodd:7      | G2       | LVCMOS33    |

## SPI flash

The on-board SPI flash holds a bitstream across power cycles. Every line is LVCMOS33. Quad SPI (4x) mode is supported through the `spiflash4x` resource, and the bitstream configuration enables SPI_BUSWIDTH=4.

Signal is the flash line and FPGA Pin is its ball.

| Signal | FPGA Pin |
|--------|----------|
| CS_N | L13 |
| CLK | L16 |
| MOSI (DQ0) | K17 |
| MISO (DQ1) | K18 |
| WP (DQ2) | L14 |
| HOLD (DQ3) | M14 |

### Secondary SPI

There is also a secondary SPI resource on a directly accessible header. The columns are Signal, FPGA Pin and IO Standard.

| Signal | FPGA Pin | IO Standard |
| ------ | -------- | ----------- |
| clk    | F1       | LVCMOS33    |
| cs_n   | C1       | LVCMOS33    |
| mosi   | H1       | LVCMOS33    |
| miso   | G1       | LVCMOS33    |
