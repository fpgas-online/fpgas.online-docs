# Arty A7: DDR3 SDRAM

**You are building or checking a design that uses the Arty's DDR3 memory.**

## DDR3 SDRAM

- Part: MT41K128M16JT-125 (Micron, 128M x 16-bit = 256 MB)
- Interface: 16-bit data bus (DQ[15:0]), 2 byte lanes (DM/DQS pairs)
- I/O Standard: SSTL135 (1.35V)
- FPGA I/O bank 34 has INTERNAL_VREF set to 0.675V

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

Source: [digilent_arty.py](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/digilent_arty.py)
