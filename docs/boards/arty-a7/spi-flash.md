# Arty A7: SPI flash

**You are building or checking a design that uses the Arty's SPI flash.**

## SPI Flash

On-board SPI flash for persistent bitstream storage. Every line is LVCMOS33.

| Signal | FPGA Pin |
|--------|----------|
| CS_N | L13 |
| CLK | L16 |
| MOSI (DQ0) | K17 |
| MISO (DQ1) | K18 |
| WP (DQ2) | L14 |
| HOLD (DQ3) | M14 |

Quad SPI (4x) mode is supported via the `spiflash4x` resource. The bitstream
configuration enables SPI_BUSWIDTH=4.

There is also a secondary SPI resource on a directly accessible header:

| Signal | FPGA Pin | IO Standard |
| ------ | -------- | ----------- |
| clk    | F1       | LVCMOS33    |
| cs_n   | C1       | LVCMOS33    |
| mosi   | H1       | LVCMOS33    |
| miso   | G1       | LVCMOS33    |
