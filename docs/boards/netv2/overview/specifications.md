---
type: reference
owner: documentation maintainers
reader: someone looking up a figure or a pin of the NeTV2
review: 2026-11-10
---

# NeTV2 specifications

**You want to look up a figure or a pin of a NeTV2.**

The board as a whole is on [The NeTV2 board](board.md). The pins that go to the Raspberry Pi are on [NeTV2 wiring to a Raspberry Pi](../setup/wiring.md). Every FPGA pin here is a ball of the FGG484 package.

## Key specifications

Parameter names a property of the board, and Value gives it.

| Parameter            | Value                                             |
| -------------------- | ------------------------------------------------- |
| FPGA (default)       | Xilinx Artix-7 XC7A35T-FGG484-2                   |
| FPGA (large variant) | Xilinx Artix-7 XC7A100T-FGG484-2                  |
| Package              | FGG484 (484-ball BGA)                             |
| System clock         | 50 MHz (pin J19, LVCMOS33)                        |
| DDR3 SDRAM           | 512 MB (32-bit wide, 4 byte lanes)                |
| Ethernet             | RMII PHY, 100Base-T (independent of host network) |
| HDMI                 | 2x HDMI In + 2x HDMI Out (TMDS_33)                |
| PCIe                 | x1 / x2 / x4                                      |
| SD Card              | Full-size SD slot (SPI and 4-bit modes)           |
| SPI Flash            | Quad SPI                                          |
| User LEDs            | 6 (M21, N20, L21, AA21, R19, M16)                 |

## FPGA device variants

Variant is the name the pages and CI use, Device string is the Vivado part, and JTAG IDCODE is what the JTAG scan reads. Both variants share the FGG484 package and identical pin assignments, so every table on this page applies to either. CI builds the bitstreams `*-netv2-a7-35t` and `*-netv2-a7-100t`.

| Variant  | Device string       | JTAG IDCODE  |
| -------- | ------------------- | ------------ |
| `a7-35`  | `xc7a35t-fgg484-2`  | `0x0362D093` |
| `a7-100` | `xc7a100t-fgg484-2` | `0x03631093` |

## Serial device by Raspberry Pi model

Raspberry Pi is the model and its configuration. GPIO UART device is the kernel device that GPIO14 and GPIO15 appear as. Symlink is its stable name, and Reason says why.

| Raspberry Pi                      | GPIO UART device | Symlink        | Reason                                     |
| --------------------------------- | ---------------- | -------------- | ------------------------------------------ |
| Raspberry Pi 5                    | `/dev/ttyAMA0`   | none           | RP1 PL011 UART on GPIO14/15                |
| Raspberry Pi 3, Bluetooth enabled | `/dev/ttyS0`     | `/dev/serial0` | Mini UART (Bluetooth claims the PL011)     |
| Raspberry Pi 3B+, Bluetooth disabled | `/dev/ttyAMA0` | `/dev/serial0` | PL011 on GPIO14/15, free because Bluetooth is disabled |

## UART test parameters

Parameter is an option or setting of the UART test, and Value is what the NeTV2 uses. `/dev/ttyAMA0` is the Raspberry Pi 5 device. Change `--port` to match the host, for example `/dev/ttyS0` on a Raspberry Pi 3 with Bluetooth enabled.

| Parameter        | Value                                                                                |
| ---------------- | ------------------------------------------------------------------------------------ |
| Baud rate        | 115200                                                                               |
| Test args        | `--port /dev/ttyAMA0 --board netv2 --skip-banner`                                    |
| `--skip-banner`  | Required when programming takes about 10 s, because the BIOS banner is missed        |

## DDR3 SDRAM

512 MB DDR3 on a 32-bit wide bus, 4 byte lanes, at 1.5V. Signal names the DDR3 signal, FPGA pins lists its balls in bit order, and I/O standard is the Vivado standard.

| Signal        | FPGA Pins                                      | I/O Standard  |
| ------------- | ---------------------------------------------- | ------------- |
| A[13:0]       | U6 V4 W5 V5 AA1 Y2 AB1 AB3 AB2 Y3 W6 Y1 V2 AA3 | SSTL15_R      |
| BA[2:0]       | U5 W4 V7                                       | SSTL15_R      |
| DQ[7:0]       | C2 F1 B1 F3 A1 D2 B2 E2                        | SSTL15_R      |
| DQ[15:8]      | J5 H3 K1 H2 J1 G2 H5 G3                        | SSTL15_R      |
| DQ[23:16]     | N2 M6 P1 N5 P2 N4 R1 P6                        | SSTL15_R      |
| DQ[31:24]     | K3 M2 K4 M3 J6 L5 J4 K6                        | SSTL15_R      |
| DQS_P[3:0]    | E1 K2 P5 M1                                    | DIFF_SSTL15_R |
| DQS_N[3:0]    | D1 J2 P4 L1                                    | DIFF_SSTL15_R |
| DM[3:0]       | G1 H4 M5 L3                                    | SSTL15_R      |
| CLK_P / CLK_N | R3 / R2                                        | DIFF_SSTL15_R |
| CKE           | Y8                                             | SSTL15_R      |
| ODT           | W9                                             | SSTL15_R      |
| CS_N          | V9                                             | SSTL15_R      |
| RAS_N         | Y9                                             | SSTL15_R      |
| CAS_N         | Y7                                             | SSTL15_R      |
| WE_N          | V8                                             | SSTL15_R      |
| RESET_N       | AB5                                            | LVCMOS15      |

## PCIe

The NeTV2 supports PCIe x1, x2 and x4 configurations, which share the same clock and reset pins. Signal names the pin, FPGA pin(s) gives its balls, and Notes gives its standard or role.

| Signal        | FPGA Pin(s) | Notes           |
| ------------- | ----------- | --------------- |
| RST_N         | E18         | LVCMOS33        |
| CLK_P / CLK_N | F10 / E10   | Reference clock |

## PCIe lane assignments

Config is the link width and lane, and the four columns are the balls of that lane's receive and transmit pairs.

| Config    | RX_P | RX_N | TX_P | TX_N |
| --------- | ---- | ---- | ---- | ---- |
| x1 lane 0 | D11  | C11  | D5   | C5   |
| x2 lane 1 | B10  | A10  | B6   | A6   |
| x4 lane 2 | D9   | C9   | D7   | C7   |
| x4 lane 3 | B8   | A8   | B4   | A4   |

## PCIe detection on a Raspberry Pi 5

Parameter names what the Raspberry Pi 5 reads, and Value gives it. Only a Raspberry Pi 5 has a PCIe connection to the NeTV2: a Raspberry Pi 3B+ has no PCIe interface. The FPGA enumerates only after a bitstream with a PCIe endpoint is loaded.

| Parameter | Value                 |
| --------- | --------------------- |
| Vendor ID | `10ee` (Xilinx)       |
| Device ID | `7011`                |
| Link      | Gen2 x1               |
| Command   | `lspci -d 10ee:7011`  |

## RMII Ethernet

The board has its own Ethernet PHY with an RMII interface, a 100Base-T connection independent of the Raspberry Pi's network. The RMII reference clock runs at 50 MHz on pin D17. Signal is the RMII signal, FPGA pin its ball, and I/O standard its Vivado standard.

| Signal       | FPGA Pin | I/O Standard |
| ------------ | -------- | ------------ |
| ref_clk      | D17      | LVCMOS33     |
| rst_n        | F16      | LVCMOS33     |
| rx_data[1:0] | A20 B18  | LVCMOS33     |
| crs_dv       | C20      | LVCMOS33     |
| tx_en        | A19      | LVCMOS33     |
| tx_data[1:0] | C18 C19  | LVCMOS33     |
| mdc          | F14      | LVCMOS33     |
| mdio         | F13      | LVCMOS33     |
| rx_er        | B20      | LVCMOS33     |
| int_n        | D21      | LVCMOS33     |

## HDMI input 0

The board has two HDMI inputs and two HDMI outputs, all with the TMDS_33 I/O standard. Signal is the HDMI signal pair, FPGA pins its positive and negative balls, and Notes says whether the pair is inverted.

| Signal            | FPGA Pins | Notes      |
| ----------------- | --------- | ---------- |
| CLK_P / CLK_N     | L19 / L20 | Inverted   |
| DATA0_P / DATA0_N | K21 / K22 | Inverted   |
| DATA1_P / DATA1_N | J20 / J21 | Inverted   |
| DATA2_P / DATA2_N | J22 / H22 | Inverted   |
| SCL / SDA         | T18 / V18 | I2C (EDID) |

## HDMI input 1

Signal is the HDMI signal pair, FPGA pins its balls, and Notes says whether the pair is inverted.

| Signal            | FPGA Pins   | Notes        |
| ----------------- | ----------- | ------------ |
| CLK_P / CLK_N     | Y18 / Y19   | Inverted     |
| DATA0_P / DATA0_N | AA18 / AB18 | Not inverted |
| DATA1_P / DATA1_N | AA19 / AB20 | Inverted     |
| DATA2_P / DATA2_N | AB21 / AB22 | Inverted     |
| SCL / SDA         | W17 / R17   | SCL inverted |

## HDMI output 0

Signal is the HDMI signal pair, FPGA pins its balls, and Notes says whether the pair is inverted.

| Signal            | FPGA Pins | Notes    |
| ----------------- | --------- | -------- |
| CLK_P / CLK_N     | W19 / W20 | Inverted |
| DATA0_P / DATA0_N | W21 / W22 |          |
| DATA1_P / DATA1_N | U20 / V20 |          |
| DATA2_P / DATA2_N | T21 / U21 |          |

## HDMI output 1

Signal is the HDMI signal pair, FPGA pins its balls, and Notes says whether the pair is inverted.

| Signal            | FPGA Pins | Notes    |
| ----------------- | --------- | -------- |
| CLK_P / CLK_N     | G21 / G22 | Inverted |
| DATA0_P / DATA0_N | E22 / D22 | Inverted |
| DATA1_P / DATA1_N | C22 / B22 | Inverted |
| DATA2_P / DATA2_N | B21 / A21 | Inverted |

## SPI flash

The on-board quad SPI flash holds a bitstream across power cycles, and the `spiflash4x` pad group gives quad SPI mode. Signal is the flash signal, FPGA pin its ball, and I/O standard its Vivado standard.

| Signal     | FPGA Pin | I/O Standard |
| ---------- | -------- | ------------ |
| CS_N       | T19      | LVCMOS33     |
| MOSI (DQ0) | P22      | LVCMOS33     |
| MISO (DQ1) | R22      | LVCMOS33     |
| VPP (DQ2)  | P21      | LVCMOS33     |
| HOLD (DQ3) | R21      | LVCMOS33     |

## SD card in SPI mode

The full-size SD slot works in SPI mode or in 4-bit mode. The two modes share the clock pin and use the data pins differently. Signal is the SD signal and FPGA pin its ball.

| Signal | FPGA Pin       |
| ------ | -------------- |
| CLK    | K18            |
| CS_N   | M13            |
| MOSI   | L13 (PULLUP)   |
| MISO   | L15 (PULLUP)   |

## SD card in 4-bit mode

Signal is the SD signal and FPGA pin its ball or balls.

| Signal    | FPGA Pin                     |
| --------- | ---------------------------- |
| CLK       | K18                          |
| CMD       | L13 (PULLUP)                 |
| DATA[3:0] | L15 L16 K14 M13 (PULLUP)     |

## User LEDs

LED is the LED's number, FPGA pin its ball, and I/O standard its Vivado standard.

| LED | FPGA Pin | I/O Standard |
| --- | -------- | ------------ |
| 0   | M21      | LVCMOS33     |
| 1   | N20      | LVCMOS33     |
| 2   | L21      | LVCMOS33     |
| 3   | AA21     | LVCMOS33     |
| 4   | R19      | LVCMOS33     |
| 5   | M16      | LVCMOS33     |

## LiteX integration

Property names a LiteX setting of the board, and Value gives it.

| Property        | Value                                                  |
| --------------- | ------------------------------------------------------ |
| Platform module | `litex_boards.platforms.kosagi_netv2`                  |
| Target module   | `litex_boards.targets.kosagi_netv2`                    |
| Default clock   | `clk50` (50 MHz, pin J19)                              |
| Programmer      | openFPGALoader (`libgpiod`, pins 27:22:4:17)           |
| Toolchain       | Vivado (proprietary) or openXC7 (open source)          |
