---
type: explanation
owner: documentation maintainers
reader: someone who wants to know what the fpgas.online Acorn design is and how it sits in the flash
review: 2026-11-10
---

# The fpgas.online Acorn design

**You have an Acorn and want to know what the fpgas.online Acorn design is: what is in it, which cards it
is built for, its two images, and how they sit in the card's flash.** To load it into SRAM by hand on
either carrier: [How to check an Acorn's PCIe link by hand on a Raspberry Pi 5](../checks/pcie-by-hand.md). To put it in a card's flash: [How to install the fpgas.online images on an Acorn](../setup/install-images.md). What the boot check tests of it: [Installing the Acorn
packages](../setup/packages.md#installing-the-acorn-packages).

## Images

The fpgas.online Acorn design is
[`designs/acorn-pcie`](https://github.com/fpgas-online/fpgas.online-test-designs/tree/main/designs/acorn-pcie)
in fpgas.online-test-designs: PCIe Gen2 x1 (`10ee:7021`, with the board named in
the PCI subsystem ID, `1e24:021f` for a CLE-215+ and `1e24:0101` for a CLE-101),
a UART bridge on P2, device DNA, XADC, the SPI flash core and ICAP. It builds
with Vivado (the XC7A200T is too large for openXC7) in two images:

| Image | Build | File to write | Flash slot |
|---|---|---|---|
| Golden | `acorn_pcie_soc.py --variant <v> --golden --build` | `sqrl_acorn_fallback.bin` (chain-loads 0x400000) | 0x0 |
| Operational | `acorn_pcie_soc.py --variant <v> --build` | `sqrl_acorn_operational.bin` (with the watchdog) | 0x400000 |

The golden image has no DDR3 and no P2 GPIO, so nothing in it can fail
calibration. The `.bit` of each build is for a JTAG SRAM load.

:::{warning}
**Do not use the `pcie-enumeration_acorn-*` assets of the prebuilt release
[`vivado-bitstreams-v0.0-496-gf162f60`](https://github.com/fpgas-online/fpgas.online-test-designs/releases/tag/vivado-bitstreams-v0.0-496-gf162f60)
as a golden or recovery image.** Their I/O reports put the PCIe lane on package
pins D9/D7 (GTP channel X0Y7, M.2 lane 3) instead of B10/B6 (X0Y6, lane 0): the
Xilinx PCIe IP's own XDC pins a x1 core's transceiver and overrides the port
constraints, so on a x1 host the core never leaves Detect. The fpgas.online
Acorn design's build fails if any port is not on the pin it was constrained to.
The release's `pmod-pin-id` Acorn build configures but never toggles a pin; build
that design from `main` instead. The release's other designs are unaffected; for
a CLE-215+ use the `*_acorn-cle-215p_*` files, whose `.bit` header reads
`7a200tfbg484` (IDCODE `0x3636093`).
:::

## What the flash holds

Which image a card boots shows in its PCI ID (`lspci -nn` on its host). Two images other than the fpgas.online
one are in service:

- **SQRL factory firmware** (`1e24:021f`): a cryptocurrency mining design, not
  LiteX, so neither `spi_flash.py` nor `litepcie_util` can talk to it. Its BAR0
  (128 KB) is a repeating mining parameter pattern. It is itself a multiboot
  pair: its header at `0x0` sets `WBSTAR = 0x680000` and issues `IPROG`, so the
  mining design lives at `0x680000`, clear of the fpgas.online operational slot.
- **The vendor (RHS Research) XDMA sample image** (`10ee:7011`): x4-capable, two
  BARs, also not LiteX.

A board on either needs the fpgas.online Acorn design loaded into SRAM over JTAG
before its flash can be written; a board whose JTAG does not answer cannot be
moved off it.

## SPI flash layout

The Acorn has a Spansion S25FL256S (256 Mbit = 32 MB) quad-SPI NOR flash.

```text
┌──────────────────────────────────────────────────┐
│ 0x00000000  Golden image (fallback)              │  4 MB
│             - Always boots first                 │
│             - Sets NEXT_CONFIG_ADDR = 0x400000   │
│             - PCIe, UART, flash, ICAP            │
│             - PROTECTED: see the safety rules    │
├──────────────────────────────────────────────────┤
│ 0x00400000  Operational image (updatable)        │  4 MB
│             - Chain-loaded by the golden image   │
│             - Has the TIMER_CFG watchdog         │
│             - If broken, watchdog → golden       │
├──────────────────────────────────────────────────┤
│ 0x00800000  Free                                 │  24 MB
└──────────────────────────────────────────────────┘
```

The safety rules are on [How to recover an Acorn with a bad image](../troubleshooting/recovery.md).

## Multiboot

1. **Power-on**: the FPGA loads the golden image from flash address 0x0.
2. **Chain-load**: the golden image's `NEXT_CONFIG_ADDR` (0x400000) makes the
   FPGA load the operational image straight away.
3. **Operational runs**, with PCIe, UART and the rest.
4. **If the operational image fails**, the `TIMER_CFG` watchdog detects the
   configuration failure and falls back to address 0x0.
5. **The golden image boots**, PCIe comes up, and the host can rewrite the
   operational slot.

The operational image carries `CONFIGFALLBACK Enable` and `TIMER_CFG
0x0001fbd0`. If it hangs during configuration, the watchdog fires and the FPGA
ignores `WBSTAR`, rebooting from 0x0.

**ICAPE2 warm boot** reconfigures without a power cycle: write the target flash
address to `WBSTAR`, then `IPROG` to the ICAPE2 command register. The PCIe link
drops and retrains once the new image is loaded. LiteX's `ICAP` core
(`self.icap = ICAP(); self.icap.add_reload()`) exposes it.

To build the two flavours of another design by hand: [generating multiboot bitstreams by hand](../setup/install-images.md#generating-multiboot-bitstreams-by-hand).
