---
type: reference
owner: documentation maintainers
reader: someone holding an Acorn-family card who wants to know which one it is
review: 2026-11-10
---

# Acorn variants

**You have a card of the Acorn family (an Acorn CLE-215+, CLE-215 or CLE-101, a LiteFury or a NiteFury) and
want to know which it is and what differs between them.**

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

The CLE-101 package is listed as FBG484 here, but `sqrl_acorn.py` builds it as
`xc7a100t-fgg484-2` and passes `fgg484` to openFPGALoader — only the CLE-215 and
CLE-215+ are `fbg484` there (checked 2026-09-03). The LiteFury row carries the
same FBG484 claim and is the same board. The package marking has not been confirmed against a
CLE-101 in hand.

Source: [NiteFury and
LiteFury](https://github.com/RHSResearchLLC/NiteFury-and-LiteFury), [LiteX Acorn
CLE-215
wiki](https://github.com/enjoy-digital/litex/wiki/Use-LiteX-on-the-Acorn-CLE-215)

## Telling the variants apart

- **By the PCI ID as sold** (SQRL's factory firmware in flash): `1e24:021f` is an Acorn CLE-215+ and
  `1e24:0101` a CLE-101 (the PCIe table of [The Acorn card](overview/specifications.md#pcie-interface); `lspci -nn`
  on [PCIe by hand](checks/pcie-by-hand.md)). A card on the fpgas.online design shows `10ee:7021` and carries
  the same pair as its PCI subsystem ID ([the fpgas.online LiteX SoC](overview/design.md#images)).
- **By the JTAG IDCODE**: `0x3636093` is an XC7A200T (CLE-215+, CLE-215, NiteFury) and `0x3631093` an
  XC7A100T (CLE-101, LiteFury) (the `--detect` blocks of [JTAG by hand](checks/jtag-by-hand.md); `0x3631093`
  was read on pi20 at ps1 on 2026-09-20, [Acorns at ps1](installations/ps1.md#the-cards)).

Neither tells a CLE-215+ from a CLE-215 or a NiteFury: not on these pages.

## Wiring

All variants share the PCB layout and pin assignments, so the wiring applies
unchanged to each of them: [on a Raspberry Pi 5](setup/rpi-5/wiring.md), [on a Compute
Blade](setup/compute-blade/wiring.md).
