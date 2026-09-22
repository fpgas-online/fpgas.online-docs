# SQRL Acorn and LiteFury

The SQRL Acorn CLE-215+ is an M.2 form factor PCIe FPGA accelerator card,
pin-compatible with the [NiteFury and
LiteFury](https://github.com/RHSResearchLLC/NiteFury-and-LiteFury) boards. In
the fpgas.online fleet it sits either in an M.2 HAT on a Raspberry Pi 5 or in
a Compute Blade's own M.2 slot, with JTAG and UART carried on adapted
Pico-EZmate cables to the host's GPIO header (a Pi 5) or to a Compute Blade's
Extension Port (P1) and 4-pin UART header (P2).

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
| DDR3 SDRAM       | 1 GiB (one MT41K512M16, 16-bit)  |
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

:::{todo}
The CLE-101 package is listed as FBG484 here, but `sqrl_acorn.py` builds it as
`xc7a100t-fgg484-2` and passes `fgg484` to openFPGALoader — only the CLE-215 and
CLE-215+ are `fbg484` there (checked 2026-09-03). The LiteFury row carries the
same FBG484 claim and is the same board. Confirm the package marking against a
CLE-101 in hand before trusting either value.
:::

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
| Vendor:Device   | `1e24:021f` Squirrels Research Labs "Acorn CLE-215+" with the factory (mining) firmware in flash; `1e24:0101` for a CLE-101; `10ee:7011` (Xilinx) is the vendor (RHS Research) XDMA sample image, as on pi20; a LiteX x1 PCIe design is `10ee:7021` |

On a Raspberry Pi 5 the Acorn connects via an M.2 HAT and appears on PCIe bus
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

On the P2 connector:

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

1 GiB in one MT41K512M16, an x16 part: 16 bits wide, two byte lanes, driven by
the 7-series DDR PHY (A7DDRPHY). The fpgas.online Acorn design runs it at
800 MT/s. Pins as in the LiteX platform file `sqrl_acorn.py`:

| Signal       | FPGA pins |
| ------------ | --------- |
| A[15:0]      | M15 L21 M16 L18 K21 M18 M21 N20 M20 N19 J21 M22 K22 N18 N22 J22 |
| BA[2:0]      | L19 J20 L20 |
| DQ[7:0]      | D19 B20 E19 A20 F19 C19 F20 C18 |
| DQ[15:8]     | E22 G21 D20 E21 C22 D21 B22 D22 |
| DM[1:0]      | A19 G22 |
| DQS_P[1:0]   | F18 B21 |
| DQS_N[1:0]   | E18 A21 |
| CLK_P / CLK_N | K17 / J17 |
| CKE          | H22 |
| ODT          | K19 |
| RAS_N        | H20 |
| CAS_N        | K18 |
| WE_N         | L16 |
| RESET_N      | K16 (LVCMOS15) |

The platform file has no CS_N. Everything except RESET_N is SSTL15 (the DQS and
clock pairs DIFF_SSTL15).

## Programming

There are three ways in, and they are not interchangeable. A load over GPIO JTAG
lands in SRAM and is gone at the next power cycle. Anything persistent has to go
into the SPI flash, which the GPIO JTAG path cannot write. And PCIe programming
only works on a board that is running a LiteX design with PCIe.

### GPIO JTAG (openFPGALoader): what the fleet uses

P1 is wired to GPIOs on the Pi's header; openFPGALoader bit-bangs JTAG through
libgpiod (about 16 s for a full XC7A200T bitstream). The load goes to SRAM only
and is lost at power-off, which is what makes it safe to experiment with.

```console
$ echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove   # detach the endpoint first
$ sudo ln -sfn /dev/gpiochip15 /dev/gpiochip0                  # Pi 5 only: libgpiod opens gpiochip0
$ openFPGALoader --cable libgpiod --pins 10:9:11:8 <bitstream.bit>
```

These are for the Raspberry Pi 5 carrier. On a Compute Blade the JTAG pins are
`2:3:4:14` (P1 lands on GPIO2, 3, 4 and 14: the I²C pair, GPIO4 and the UART TX
line), and the PCIe bus address differs per blade; see [Compute
Blade](wiring.md#compute-blade) and the [PS1 Compute
blades](../../sites/ps1.md#compute-blades) inventory.

:::{warning}
Detach the PCIe endpoint before loading a bitstream. Reconfiguring the FPGA
underneath an enumerated endpoint is a surprise removal, and the BCM2712 root
complex does not survive it: the host crashes. The rule, the per-host bus
address and bringing the endpoint back are in [detach the PCIe endpoint before
any JTAG
reconfiguration](pcie-programming.md#detach-the-pcie-endpoint-before-any-jtag-reconfiguration).
:::

Pin order, the Pi 5 `gpiochip15` link, the PCIe detach rule and the
`overlayroot=tmpfs` trap are all in [Acorn wiring](wiring.md). Which bitstreams
to use, and which prebuilt ones not to, is under
[Images](pcie-programming.md#images).

### JTAG over an FT232H (OpenOCD)

For a bench setup, an FT232H USB adapter with a BSCAN_SPI proxy bitstream:

```console
$ openocd -f openocd_xc7_ft232.cfg -c "init; pld load 0 <bitstream>; exit"
```

### PCIe (the fpgas.online Acorn design)

With the fpgas.online Acorn design running, the flash is written over PCIe BAR0
with `spi_flash.py`, which is how a board is moved onto the golden and
operational images and how the operational image is updated; see [Acorn PCIe
programming and multiboot](pcie-programming.md). A board on the SQRL factory
firmware or the vendor XDMA image first needs the design loaded into SRAM over
JTAG. Which image each board boots is on the site pages.

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
