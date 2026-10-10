---
type: reference
owner: documentation maintainers
reader: someone looking up a figure or a pin of the Acorn card
review: 2026-11-10
---

# Acorn specifications

**You want to look up a figure or a pin of an Acorn: its FPGA, PCIe interface, clock, LEDs, serial pins, flash or memory.** The card as a whole, with its picture, is on [The Acorn card](card.md).

## Key specifications

The table describes the CLE-215+. The CLE-215 has the same FPGA in speed grade -2. A CLE-101 or a LiteFury
has an XC7A100T (speed grade -2) and 512 MB of DDR3, and a NiteFury an XC7A200T with 512 MB: [Acorn
variants](../which-one.md#compatible-boards).

| Parameter        | Value                            |
| ---------------- | -------------------------------- |
| FPGA             | Xilinx Artix-7 XC7A200T-FBG484-3 |
| Package          | FBG484 (484-ball BGA)            |
| Logic cells      | 215,360                          |
| CLB flip-flops   | 269,200                          |
| DSP slices       | 740                              |
| Block RAM        | 13,140 Kib                       |
| GTP transceivers | 4 (up to 6.6 Gb/s each)          |
| DDR3 SDRAM       | 1 GiB (one MT41K512M16, 16-bit)  |
| SPI Flash        | S25FL256S (256 Mbit, quad SPI)   |
| PCIe             | Gen2 x4 (M.2 M-key)              |
| Form factor      | M.2 2280                         |
| Power            | Via M.2 / mPCIe slot (3.3V)      |
| Process          | 28 nm HPL                        |

Source: [LiteX platform file for the SQRL
Acorn](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/sqrl_acorn.py)

## PCIe interface

| Parameter       | Value                                    |
| --------------- | ---------------------------------------- |
| Link            | Gen2 x4 (4-lane GTP transceivers)        |
| Connector       | M.2 M-key                                |
| Reference clock | Differential (FPGA pins F6/E6)           |
| Reset           | LVCMOS33 (FPGA pin J1, internal pull-up) |
| Vendor:Device   | `1e24:021f` Squirrels Research Labs "Acorn CLE-215+" with the factory (mining) firmware in flash; `1e24:0101` for a CLE-101; `10ee:7011` (Xilinx) is the vendor (RHS Research) XDMA sample image, as on pi20 at ps1; a LiteX x1 PCIe design is `10ee:7021` |

On a Raspberry Pi 5 the Acorn connects via an M.2 HAT and appears on PCIe bus
`0001:01:00.0` (the RP1 south bridge is `0002:01:00.0`). Reconfiguring the FPGA
over JTAG while that endpoint is enumerated crashes a Pi 5 host — detach it
first, see [detach the PCIe endpoint before any JTAG
reconfiguration](../checks/pcie-by-hand.md#detach-the-pcie-endpoint-before-any-jtag-reconfiguration).

## Clock

| Signal         | FPGA Pins | Standard    | Frequency |
| -------------- | --------- | ----------- | --------- |
| System clock   | J19 / H19 | DIFF_SSTL15 | 200 MHz   |
| PCIe ref clock | F6 / E6   | —           | 100 MHz   |

## User LEDs

| LED | FPGA Pin |
| --- | -------- |
| 0   | G3       |
| 1   | H3       |
| 2   | G4       |
| 3   | H4       |

## Serial (UART)

On the P2 connector:

| Signal | FPGA Pin |
| ------ | -------- |
| RX     | J2       |
| TX     | K2       |

The board carries no USB serial adapter of its own, so P2 has to be wired to the
host's own GPIO UART with an adapted Pico-EZmate cable; see the wiring [on a Raspberry Pi
5](../setup/rpi-5/wiring.md) or [on a Compute Blade](../setup/compute-blade/wiring.md).

## SPI Flash

| Signal | FPGA Pin |
| ------ | -------- |
| CS_n   | T19      |
| MOSI   | P22      |
| MISO   | R22      |
| WP     | P21      |
| HOLD   | R21      |

Flash part: Spansion S25FL256S (256 Mbit). Supports multiboot with separate
fallback and operational bitstream regions.

## DDR3 SDRAM

1 GiB in one MT41K512M16, an x16 part: 16 bits wide, two byte lanes, driven by
the 7-series DDR PHY (A7DDRPHY). The fpgas.online Acorn design runs it at
800 MT/s. Pins as in the LiteX platform file `sqrl_acorn.py`:

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

The platform file has no CS_N. Everything except RESET_N is SSTL15 (the DQS and
clock pairs DIFF_SSTL15).
