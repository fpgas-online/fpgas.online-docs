# NeTV2: RMII Ethernet

**You are building or checking a design that uses the NeTV2's own Ethernet port and need its FPGA pins.**

The NeTV2 has its own Ethernet PHY with an RMII interface, providing a 100Base-T
network connection independent of the Raspberry Pi's network.

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

The RMII reference clock runs at 50 MHz (pin D17).

Source: [LiteX platform file for the NeTV2](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_netv2.py)
