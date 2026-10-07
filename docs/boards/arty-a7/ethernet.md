# Arty A7: MII Ethernet

**You are building or checking a design that uses the Arty's Ethernet port.**

## MII Ethernet

The Arty uses a TI DP83848J Ethernet PHY with a standard MII (Media Independent
Interface), supporting 10/100 Mbps. Every MII signal is LVCMOS33.

| Signal | FPGA Pin | Direction |
|--------|----------|-----------|
| ref_clk | G18 | Output (25 MHz) |
| tx_clk | H16 | Input |
| rx_clk | F15 | Input |
| rst_n | C16 | Output |
| mdio | K13 | Bidirectional |
| mdc | F16 | Output |
| rx_dv | G16 | Input |
| rx_er | C17 | Input |
| rx_data[3:0] | D18 E17 E18 G17 | Input |
| tx_en | H15 | Output |
| tx_data[3:0] | H14 J14 J13 H17 | Output |
| col | D17 | Input |
| crs | G14 | Input |

The Ethernet test uses a USB Ethernet adapter on the RPi connected to the Arty's
RJ45 jack, independent of the PMOD HAT and of the RPi's own Ethernet. Both site
pages record which adapter is fitted to each host.

Source: [digilent_arty.py](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/digilent_arty.py), [Digilent Arty A7 Reference Manual](https://digilent.com/reference/programmable-logic/arty-a7/reference-manual)
