# SQRL Acorn and LiteFury

The SQRL Acorn CLE-215+ is an M.2 form factor PCIe FPGA accelerator card,
pin-compatible with the [NiteFury and
LiteFury](https://github.com/RHSResearchLLC/NiteFury-and-LiteFury) boards. In
the fpgas.online fleet it sits either in an mPCIe HAT on a Raspberry Pi 5 or in
a Compute Blade's own M.2 slot, with JTAG and UART carried on adapted
Pico-EZmate cables to the host GPIO header.

See [Acorn wiring](wiring.md) for the full RPi GPIO pinmap.

## Key specifications

| Parameter        | Value                            |
| ---------------- | -------------------------------- |
| FPGA             | Xilinx Artix-7 XC7A200T-FBG484-3 |
| Package          | FBG484 (484-ball BGA)            |
| Logic cells      | 215,360                          |
| CLB flip-flops   | 269,200                          |
| DSP slices       | 740                              |
| Block RAM        | 13,140 Kib                       |
| GTP transceivers | 4 (up to 6.6 Gb/s each)          |
| DDR3 SDRAM       | 1 GiB (MT41K512M16, 32-bit)      |
| SPI Flash        | S25FL256S (256 Mbit, quad SPI)   |
| PCIe             | Gen2 x4 (M.2 M-key)              |
| Form factor      | M.2 2280                         |
| Power            | Via M.2 / mPCIe slot (3.3V)      |
| Process          | 28 nm HPL                        |

Source: [LiteX platform file for the SQRL
Acorn](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/sqrl_acorn.py)

## Compatible boards

All boards share the same PCB layout and pin assignments. The LiteX platform
file `sqrl_acorn.py` works for all variants — change only the device string.

| Board          | FPGA            | Speed Grade | DDR3   | PCIe    |
| -------------- | --------------- | ----------- | ------ | ------- |
| LiteFury       | XC7A100T-FBG484 | -2          | 512 MB | Gen2 x4 |
| NiteFury       | XC7A200T-FBG484 | -2          | 512 MB | Gen2 x4 |
| Acorn CLE-101  | XC7A100T-FBG484 | -2          | 512 MB | Gen2 x4 |
| Acorn CLE-215  | XC7A200T-FBG484 | -2          | 1 GB   | Gen2 x4 |
| Acorn CLE-215+ | XC7A200T-FBG484 | -3          | 1 GB   | Gen2 x4 |

The CLE-215+ is equivalent to the RHSResearchLLC NiteFury board but with 1 GB
DDR3 (vs 512 MB).

Source: [NiteFury and
LiteFury](https://github.com/RHSResearchLLC/NiteFury-and-LiteFury), [LiteX Acorn
CLE-215
wiki](https://github.com/enjoy-digital/litex/wiki/Use-LiteX-on-the-Acorn-CLE-215)

## PCIe interface

| Parameter       | Value                                    |
| --------------- | ---------------------------------------- |
| Link            | Gen2 x4 (4-lane GTP transceivers)        |
| Connector       | M.2 M-key                                |
| Reference clock | Differential (FPGA pins F6/E6)           |
| Reset           | LVCMOS33 (FPGA pin J1, internal pull-up) |
| Vendor:Device   | `1e24:021f` Squirrels Research Labs "Acorn CLE-215+" with the factory (mining) firmware in flash; `1e24:0101` for a CLE-101; `10ee:7011` (Xilinx) once a LiteX/Vivado design is in flash |

On a Raspberry Pi 5 the Acorn connects via an mPCIe HAT and appears on PCIe bus
`0001:01:00.0` (the RP1 south bridge is `0002:01:00.0`). Reconfiguring the FPGA
over JTAG while that endpoint is enumerated crashes a Pi 5 host — detach it
first, see [detach the PCIe endpoint before any JTAG
reconfiguration](pcie-programming.md#detach-the-pcie-endpoint-before-any-jtag-reconfiguration).

## Clock

| Signal         | FPGA Pins | Standard    | Frequency |
| -------------- | --------- | ----------- | --------- |
| System clock   | J19 / H19 | DIFF_SSTL15 | 200 MHz   |
| PCIe ref clock | F6 / E6   | —           | 100 MHz   |

## User LEDs

| LED | FPGA Pin |
| --- | -------- |
| 0   | G3       |
| 1   | H3       |
| 2   | G4       |
| 3   | H4       |

## Serial (UART)

Available on the P2 connector (active low accent LEDs double as serial adapter
pins):

| Signal | FPGA Pin |
| ------ | -------- |
| RX     | J2       |
| TX     | K2       |

The board carries no USB serial adapter of its own, so P2 has to be wired to the
host's own GPIO UART with an adapted Pico-EZmate cable; see [Acorn
wiring](wiring.md).

## SPI Flash

| Signal | FPGA Pin |
| ------ | -------- |
| CS_n   | T19      |
| MOSI   | P22      |
| MISO   | R22      |
| WP     | P21      |
| HOLD   | R21      |

Flash part: Spansion S25FL256S (256 Mbit). Supports multiboot with separate
fallback and operational bitstream regions.

## DDR3 SDRAM

1 GiB MT41K512M16, 32-bit wide with 4 byte lanes. Uses 7-series native DDR PHY
(A7DDRPHY).

| Signal Group | FPGA Pins                                               |
| ------------ | ------------------------------------------------------- |
| Address      | M15/L21/M16/L18/K21/M18/M21/N20/M20/N19/J21/M22/K22/N18 |
| Bank         | N22/M21/N19                                             |
| DQ[7:0]      | C2/F1/B1/F3/A1/D2/B2/E2                                 |
| DQ[15:8]     | J5/H3/K1/H2/J1/K2/H1/J3                                 |
| DQ[23:16]    | N2/M6/P1/N5/P2/N4/R1/P6                                 |
| DQ[31:24]    | K3/M2/K4/M3/J6/L3/J4/K6                                 |
| CLK_P/N      | K17/J17                                                 |
| CKE          | J18                                                     |
| ODT          | K19                                                     |
| CS_N         | L19                                                     |
| RAS_N        | L20                                                     |
| CAS_N        | K18                                                     |
| WE_N         | L22                                                     |
| RESET_N      | G17                                                     |

## Programming

### Via GPIO JTAG (openFPGALoader) — what the fleet uses

P1 is wired to the Pi's SPI0 pins; openFPGALoader bit-bangs JTAG through
libgpiod (about 16 s for a full XC7A200T bitstream). The load goes to SRAM only
and is lost at power cycle, which is what makes it safe to experiment with.

```console
$ echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove   # MUST detach the endpoint first on a Pi 5
$ sudo ln -sfn /dev/gpiochip15 /dev/gpiochip0                  # openFPGALoader 0.10.0 on a Pi 5 only
$ openFPGALoader --cable libgpiod --pins 10:9:11:8 <bitstream.bit>
```

:::{warning}
Detach the PCIe endpoint before loading a bitstream. On 2026-08-31 a JTAG load
on pi-sw2-p47 with the endpoint still enumerated killed the host. The rule, the
per-host bus address and the recovery are in [detach the PCIe endpoint before
any JTAG
reconfiguration](pcie-programming.md#detach-the-pcie-endpoint-before-any-jtag-reconfiguration)
and [PCIe and JTAG interact](../../sites/welland.md#pcie-and-jtag-interact).
:::

Pin order, the Pi 5 `gpiochip15` trap, the PCIe detach rule and the
`overlayroot=tmpfs` gotcha are all in [Acorn wiring](wiring.md). Prebuilt Vivado
bitstreams for every test design and Acorn variant are on the
`vivado-bitstreams-v0.0-496-gf162f60` release — see [prebuilt Vivado
bitstreams](pcie-programming.md#prebuilt-vivado-bitstreams).

### Via JTAG (OpenOCD + FT232H)

Alternative for a bench setup — uses an FT232H USB adapter with a BSCAN_SPI
proxy bitstream:

```console
$ openocd -f openocd_xc7_ft232.cfg -c "init; pld load 0 <bitstream>; exit"
```

### Via SPI Flash

Flash a persistent bitstream using OpenOCD or openFPGALoader. The S25FL256S
supports multiboot with fallback. `openFPGALoader --write-flash` does **not**
currently work over the GPIO JTAG wiring (the open-source spiOverJtag bridge
never toggles CCLK after configuration); see [Acorn PCIe programming and
multiboot](pcie-programming.md).

### Via PCIe (LiteX)

LiteX provides PCIe-based programming via `litepcie_util` when a LiteX bitstream
with PCIe support is already loaded. Only pi-sw2-p44 currently boots such a
design; the other Welland boards still carry the SQRL factory firmware.

## Where they are

Six CLE-215+ at [Welland](../../sites/welland.md#sqrl-acorn-cle-215) on
Raspberry Pi 5 hosts, and three CLE-101 / LiteFury at
[PS1](../../sites/ps1.md#compute-blades) on Compute Blades. The site pages
carry the per-host tables.

## LiteX support

The LiteX target (`litex_boards/targets/sqrl_acorn.py`) provides:

- PCIe Gen2 x4 endpoint with DMA
- DDR3 SDRAM controller (LiteDRAM)
- SPI Flash access (LiteSPI)
- ICAP for warm-boot / multiboot
- Optional Ethernet via PCIe bridge

Build example:

```console
$ python3 -m litex_boards.targets.sqrl_acorn --build
```

## References

- LiteX platform definition: [`litex_boards/platforms/sqrl_acorn.py`](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/sqrl_acorn.py)
- LiteX target definition: [`litex_boards/targets/sqrl_acorn.py`](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/targets/sqrl_acorn.py)
- LiteX wiki: [Use LiteX on the Acorn CLE-215](https://github.com/enjoy-digital/litex/wiki/Use-LiteX-on-the-Acorn-CLE-215)
- OpenOCD flashing: [NiteFury/Acorn flashing guide](https://github.com/Gbps/nitefury-openocd-flashing-guide)
- Running Linux: [Acorn CLE-215+ blog post](https://spoolqueue.com/new-design/fpga/migen/litex/2020/08/11/acorn-cle-215.html)

## Wiring and programming guides

How the Acorn is wired to its host, and how to put a bitstream in flash:

```{toctree}
:maxdepth: 1

wiring
pcie-programming
```
