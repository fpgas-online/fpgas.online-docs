# Fomu EVT: device info

**You want the Fomu EVT's FPGA, memory and connectors.**

## Key Specifications

| Parameter            | Value                                     |
| -------------------- | ----------------------------------------- |
| FPGA                 | Lattice iCE40UP5K-SG48                    |
| Package              | SG48 (48-pin QFN)                         |
| Logic cells          | 5,280 LUT4s                               |
| SPRAM                | 128 KB (4 x 32 KB blocks)                 |
| DPRAM (EBR)          | 120 Kbit (15 x 8 Kbit blocks)             |
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

:::{note}
The two source documents disagree about the block RAM: the row above says 120
Kbit as 15 blocks of 8 Kbit, the pin-mapping document says 30 EBR blocks
totalling 15 KB. The totals agree (120 Kbit is 15 KB); only the block count and
block size differ.
:::

:::{todo}
Confirm the EBR geometry against the Lattice iCE40 UltraPlus family datasheet
(<https://www.latticesemi.com/Products/FPGAandCPLD/iCE40UltraPlus>): it gives 30
EBR blocks of 4 Kbit (120 Kbit), which makes the Key Specifications table's
"15 x 8 Kbit blocks" the suspect figure; correct it once confirmed.
:::

Source: [LiteX platform file for the Fomu EVT](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_fomu_evt.py),
[Fomu hardware repository](https://github.com/im-tomu/fomu-hardware)
