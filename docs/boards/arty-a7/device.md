# Arty A7: device info

**You want the Arty A7's FPGA, memory and connectors, and which FPGA variant a board carries.**

## Key Specifications

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

:::{todo}
The two sources disagree on the package of the A7-35 boards in the fleet. The
table above (from the board specification) says CSG324; the pin-mapping notes
recorded a different device and package for the three hosts they were measured
on:

| Parameter | Value |
| --------- | ----- |
| FPGA | Xilinx Artix-7 XC7A35T-CPG236-1 |
| Package | CPG236 |

Every FPGA pin name on these pages comes from the LiteX `digilent_arty`
platform, whose two device strings are both CSG324 parts (see
[FPGA Device Variants](/boards/arty-a7/device.md#fpga-device-variants)), so CPG236 looks like a
transcription error in the pin-mapping notes rather than a second board type.
Confirm against a board and delete the loser.
:::

The bold **I** in the A7-35 device string is the temperature grade: the boards
in the fleet are the industrial-grade, low-power part, which is the `a7-35`
variant below.

Source: [Digilent Arty A7 Reference Manual](https://digilent.com/reference/programmable-logic/arty-a7/reference-manual)

## FPGA Device Variants

The LiteX platform file defines two variants:

| Variant | Device String | Notes |
|---------|--------------|-------|
| `a7-35` | `xc7a35ticsg324-1L` | Industrial temp, low power |
| `a7-100` | `xc7a100tcsg324-1` | Larger fabric, commercial temp |

Source: [digilent_arty.py](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/digilent_arty.py)
