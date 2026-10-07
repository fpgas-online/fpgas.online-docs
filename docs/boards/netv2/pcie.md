# NeTV2: PCIe

**You are building or checking a PCIe design on a NeTV2, or want to see it enumerate on rpi5-netv2, and need its pins and what it looks like on the bus.**

The NeTV2 supports PCIe x1, x2 and x4 configurations. All share the same clock
and reset pins. Only rpi5-netv2 has a PCIe connection; the RPi 3 has no PCIe.

| Signal        | FPGA Pin(s) | Notes           |
| ------------- | ----------- | --------------- |
| RST_N         | E18         | LVCMOS33        |
| CLK_P / CLK_N | F10 / E10   | Reference clock |

## Lane assignments

| Config    | RX_P | RX_N | TX_P | TX_N |
| --------- | ---- | ---- | ---- | ---- |
| x1 lane 0 | D11  | C11  | D5   | C5   |
| x2 lane 1 | B10  | A10  | B6   | A6   |
| x4 lane 2 | D9   | C9   | D7   | C7   |
| x4 lane 3 | B8   | A8   | B4   | A4   |

## PCIe Detection (rpi5-netv2)

When a bitstream is loaded and the board is connected to the RPi 5 over PCIe
Gen2 x1, the FPGA enumerates as a Xilinx device:

| Parameter | Value                 |
| --------- | --------------------- |
| Vendor ID | `10ee` (Xilinx)       |
| Device ID | `7011`                |
| Link      | Gen2 x1               |
| Command   | `lspci -d 10ee:7011`  |

:::{warning}
As of 2026-03-09, the NeTV2 FPGA is not currently enumerating on the RPi5's PCIe
bus: only the RP1 south bridge is visible in `lspci`. It needs a bitstream
loaded first. Until it enumerates, the
[detach step](jtag.md#programming-with-openfpgaloader) finds nothing to detach — and the moment
it does enumerate, that step becomes mandatory.
:::

Source: [LiteX platform file for the NeTV2](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_netv2.py)
