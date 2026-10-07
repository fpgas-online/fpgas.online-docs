# NeTV2: DDR3 SDRAM

**You are building or checking a design that uses the NeTV2's DDR3 memory and need its FPGA pins.**

512 MB DDR3 on a 32-bit wide bus, 4 byte lanes, at 1.5V.

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

Source: [LiteX platform file for the NeTV2](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_netv2.py)
