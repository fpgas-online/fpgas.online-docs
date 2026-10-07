# NeTV2: Host Connections

**You want to know which Raspberry Pi each NeTV2 sits on, what it is connected by, and how to reach the two development hosts.**

The NeTV2 is designed to sit on top of a Raspberry Pi, connecting through the
40-pin GPIO header and optionally through a PCIe link. The two hosts below are
the [development hosts](#development-hosts), personal machines on a separate
network rather than part of the fpgas.online fleet.
Five production boards are installed ([NeTV2](../../sites/welland.md#netv2)), of
which four are the working fleet: pi18 was already offline at the 2026-03-17
survey. All five are RPi 3B+ hosts without PCIe, carrying the same GPIO JTAG and
GPIO UART wiring as rpi3-netv2 — which says nothing about the tool they are
driven with, see [Programming with openFPGALoader](jtag.md#programming-with-openfpgaloader).

Probed 2026-03-09.

| Host       | FPGA Variant      | JTAG IDCODE  | Tool [†](jtag.md#programming-with-openfpgaloader) |
| ---------- | ----------------- | ------------ | ----------------------- |
| rpi5-netv2 | XC7A100T-FGG484-2 | `0x03631093` | openFPGALoader (rp1pio) |
| rpi3-netv2 | XC7A35T-FGG484-2  | `0x0362D093` | OpenOCD (bcm2835gpio)   |

† Which tool rpi5-netv2 actually has is unsettled; see
[Programming with openFPGALoader](jtag.md#programming-with-openfpgaloader).

## Development hosts

Probed 2026-03-09. Neither host is part of the fpgas.online fleet: they sit on
`iot.welland.mithis.com`, reachable over `wg-desktop` rather than through a site
gateway, and no site page lists them.

```{rst-class} nowrap
```

| Host                              | IP (via DNS)    | RPi Model             | Board                  | Connections         | SSH                                                        |
| --------------------------------- | --------------- | --------------------- | ---------------------- | ------------------- | ---------------------------------------------------------- |
| `rpi5-netv2.iot.welland.mithis.com` | 10.1.90.210/211 | RPi 5 Model B Rev 1.0 | NeTV2 (bare developer) | GPIO + PCIe Gen2 x1 | `tim@rpi5-netv2.iot.welland.mithis.com` (via `wg-desktop`) |
| `rpi3-netv2.iot.welland.mithis.com` | 10.1.90.212/213 | RPi 3                 | NeTV2 (stock packaged) | GPIO only           | `pi@rpi3-netv2.iot.welland.mithis.com` (via `wg-desktop`)  |

**rpi5-netv2** is a bare developer NeTV2 (unpackaged), with JTAG (4 signals +
SRST) and UART (TX/RX) over GPIO and a PCIe Gen2 x1 link through the RPi 5 PCIe
connector. A configured board is *expected* to enumerate there as a Xilinx
device, vendor `10ee` device `7011`. Verified over SSH 2026-03-09: Debian 13
(Trixie), kernel 6.12.47+rpt-rpi-2712 aarch64; OpenOCD installed but no
openFPGALoader and no LiteX; an ASIX AX88179 Gigabit Ethernet adapter is the
only USB device, so there is no FTDI JTAG adapter and no USB serial device;
and only the RP1 south bridge was visible on PCIe, so at that survey the NeTV2
FPGA was not enumerating — it needs a bitstream loaded first, as
[PCIe detection](pcie.md#pcie-detection-rpi5-netv2) records.

**rpi3-netv2** is a stock packaged NeTV2 (as shipped by bunnie via Crowd
Supply), with the same GPIO JTAG (4 signals + SRST) and UART (TX/RX). It has no
PCIe connection: the RPi 3 has no PCIe interface.
