# Acorn functionality

**You want to know what an Acorn on fpgas.online can do today, and how each part of it is reached from its
host.** The card's own hardware is on [Acorn device info](device-info.md).

## How the card is reached

PCIe is through the M.2 slot of the host. JTAG, the serial pair and the spare wires are carried on two cables
to GPIO pins of the host.

The wiring depends on the **carrier the Pi sits in** — how many GPIOs it brings
out — not on the site:

- **[Raspberry Pi 5 with an M.2 HAT](../wiring/rpi-5.md)**: the full 40-pin header
  is available. P2 goes to header pins 5-10 and P1 to header pins 19-26. JTAG
  has its own pins, `--pins 10:9:11:8` (TDI:TDO:TCK:TMS), the serial pair is on
  GPIO14/15, and both spare balls (J5, H5) are wired.
- **[Compute Blade with a CM4 or CM5](../wiring/compute-blade.md)**: the blade brings out
  only GPIO2, 3, 4, 14 and 15. P1 goes to the Extension Port and JTAG is
  `--pins 2:3:4:14`. P2's serial pair goes to the 4-pin UART header, and J5 and
  H5 are not connected. The UART header's TX pin is the same GPIO14 as TMS, so
  the J2 wire has a 470 Ω resistor in it so that JTAG should win (designed so,
  not yet measured). Whether a ps1 blade is wired this way,
  and how each one is wired, is on [Acorns at
  ps1](../installations/ps1.md#the-cards).

On both carriers the serial pair lands on the same GPIOs — K2 (FPGA TX) on
GPIO15, J2 (FPGA RX) on GPIO14 — so one set of FPGA pin constraints and one set
of host scripts serves every host.

## Programming

There are three ways in, and they are not interchangeable. A load over GPIO JTAG
lands in SRAM and is gone at the next power cycle. Anything persistent has to go
into the SPI flash, which the GPIO JTAG path cannot write. And PCIe programming
only works on a board that is running a LiteX design with PCIe.

### GPIO JTAG (openFPGALoader): what the fleet uses

P1 is wired to GPIOs on the Pi's header; openFPGALoader bit-bangs JTAG through
libgpiod (about 16 s for a full XC7A200T bitstream). The load goes to SRAM only
and is lost at power-off, which is what makes it safe to experiment with.

On a **Raspberry Pi 5** (these three commands are for that carrier only):

```console
$ echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove   # detach the endpoint first
$ sudo ln -sfn /dev/gpiochip15 /dev/gpiochip0                  # Pi 5 only: libgpiod opens gpiochip0
$ openFPGALoader --cable libgpiod --pins 10:9:11:8 <bitstream.bit>
```

**On a Compute Blade do not make this `gpiochip0` link and do not use these commands.** There the JTAG pins are
`2:3:4:14` (P1 lands on GPIO2, 3, 4 and 14: the I²C pair, GPIO4 and the UART TX
line), and the PCIe bus address differs per blade; see [JTAG on a
blade](../wiring/compute-blade-jtag.md#jtag-on-a-blade) and [Acorns at ps1](../installations/ps1.md#the-cards).

:::{warning}
Detach the PCIe endpoint before loading a bitstream. Reconfiguring the FPGA
underneath an enumerated endpoint is a surprise removal, and the BCM2712 root
complex does not survive it: the host crashes. The rule, the per-host bus
address and bringing the endpoint back are in [detach the PCIe endpoint before
any JTAG
reconfiguration](../designs/pcie.md#detach-the-pcie-endpoint-before-any-jtag-reconfiguration).
:::

Pin order and the Pi 5 `gpiochip15` link are in [JTAG from the Pi](../wiring/rpi-5-host.md#jtag-from-the-pi), and the
`overlayroot=tmpfs` trap in [JTAG by hand](../designs/jtag.md). Which bitstreams
to use, and which prebuilt ones not to, is under
[Images](../designs/litex-soc.md#images).

### JTAG over an FT232H (OpenOCD)

For a bench setup, an FT232H USB adapter with a BSCAN_SPI proxy bitstream:

```console
$ openocd -f openocd_xc7_ft232.cfg -c "init; pld load 0 <bitstream>; exit"
```

### PCIe (the fpgas.online Acorn design)

With the fpgas.online Acorn design running, the flash is written over PCIe BAR0
with `spi_flash.py`, which is how a board is moved onto the golden and
operational images and how the operational image is updated; see [Acorn PCIe
programming and multiboot](../designs/install-images.md). A board on the SQRL factory
firmware or the vendor XDMA image first needs the design loaded into SRAM over
JTAG. Which image each card boots is on [Acorns at welland](../installations/welland.md) and [Acorns at
ps1](../installations/ps1.md).

## The programming paths compared

| Method | Speed | Persistent? | Requires | Notes |
|--------|-------|-------------|----------|-------|
| GPIO JTAG → SRAM | about 16 s for a 1.6 MB XC7A200T bitstream over libgpiod; 24 s for the 2.3 MB fpgas.online SoC over OpenOCD | No (lost at power-off) | the P1 JTAG wiring | Works whatever is loaded. **[Detach the PCIe endpoint first](../designs/pcie.md#detach-the-pcie-endpoint-before-any-jtag-reconfiguration)** |
| PCIe → SPI flash, `spi_flash.py` | 32 MiB read in 58 s; a 4 MiB slot erased, written and verified in about 20 s | Yes | the fpgas.online Acorn design running (from flash, or loaded into SRAM over JTAG) | Stdlib Python over BAR0, no kernel module. The proven path |
| PCIe → SPI flash, `litepcie_util` | — | Yes | a LiteX PCIe design and the `litepcie` kernel module | Not yet run on fleet hardware |

`openFPGALoader --write-flash` does not work over the GPIO JTAG wiring: its
spiOverJtag bridge never toggles CCLK after configuration, so over that path JTAG
can only load volatile SRAM.

## Future: flash over JTAG

When openFPGALoader's `--write-flash` works over the GPIO JTAG wiring, initial
setup becomes a single JTAG flash write, golden recovery no longer needs the
volatile SRAM step, and the "bricked" row of the [recovery summary](../designs/recovery.md#summary) disappears. Until then the SRAM
bootstrap is the recovery path.

## The check

What the boot check (`fpgas-verify`) tests on an Acorn, test by test, and how to run it, is under [Installing
the Acorn packages](../packages.md#installing-the-acorn-packages).

## Where they are

CLE-215+ cards at Welland on Raspberry Pi 5 hosts: [Acorns at welland](../installations/welland.md). CLE-101 /
LiteFury cards at ps1 on Compute Blades: [Acorns at ps1](../installations/ps1.md). Those pages carry the
per-card tables.
