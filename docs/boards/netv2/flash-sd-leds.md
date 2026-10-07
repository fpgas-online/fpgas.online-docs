# NeTV2: SPI flash, SD card and user LEDs

**You are building or checking a design that uses the NeTV2's SPI flash, SD card slot or user LEDs and need their FPGA pins.**

## SPI Flash

On-board quad SPI flash for persistent bitstream storage, used by
`--write-flash` on [JTAG via RPi GPIO](jtag.md#rpi-3b-gpio-bitbang-current-deployed-hosts). Quad SPI mode is available through the `spiflash4x` pad
group.

| Signal     | FPGA Pin | I/O Standard |
| ---------- | -------- | ------------ |
| CS_N       | T19      | LVCMOS33     |
| MOSI (DQ0) | P22      | LVCMOS33     |
| MISO (DQ1) | R22      | LVCMOS33     |
| VPP (DQ2)  | P21      | LVCMOS33     |
| HOLD (DQ3) | R21      | LVCMOS33     |

## SD Card

A full-size SD slot, usable in either SPI or 4-bit mode. The two modes share the
clock pin and reuse the same data pins differently.

### SPI Mode

| Signal | FPGA Pin       |
| ------ | -------------- |
| CLK    | K18            |
| CS_N   | M13            |
| MOSI   | L13 (PULLUP)   |
| MISO   | L15 (PULLUP)   |

### 4-bit Mode

| Signal    | FPGA Pin                     |
| --------- | ---------------------------- |
| CLK       | K18                          |
| CMD       | L13 (PULLUP)                 |
| DATA[3:0] | L15 L16 K14 M13 (PULLUP)     |

## User LEDs

| LED | FPGA Pin | I/O Standard |
| --- | -------- | ------------ |
| 0   | M21      | LVCMOS33     |
| 1   | N20      | LVCMOS33     |
| 2   | L21      | LVCMOS33     |
| 3   | AA21     | LVCMOS33     |
| 4   | R19      | LVCMOS33     |
| 5   | M16      | LVCMOS33     |
