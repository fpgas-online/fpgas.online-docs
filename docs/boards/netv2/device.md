# NeTV2 device info

**You want to know what is on a NeTV2: its FPGA, memory and connectors, and which of the two FPGA variants a board carries.**

## Key Specifications

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

Source: [LiteX platform file for the NeTV2](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_netv2.py)

## FPGA Device Variants

| Variant  | Device String       |
| -------- | ------------------- |
| `a7-35`  | `xc7a35t-fgg484-2`  |
| `a7-100` | `xc7a100t-fgg484-2` |

Both variants share the same FGG484 package and identical pin assignments, so
everything on the [NeTV2 pages](../netv2.md) applies to either. CI builds variant-specific bitstreams:
`*-netv2-a7-35t` and `*-netv2-a7-100t`.

Source: [LiteX platform file for the NeTV2](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_netv2.py)
