---
type: reference
owner: documentation maintainers
reader: someone holding an Acorn-family card who wants to know which one it is
review: 2026-11-10
---

# Acorn variants

This page tells the cards of the Acorn family apart: the Acorn CLE-215+, CLE-215 and CLE-101, the LiteFury and the
NiteFury. It lists what differs between them and what you can read from a card to identify it.

:::{admonition} Figure to come
:class: placeholder

The five variants side by side, in the same orientation and at the same scale, with the difference between them marked. Tracked in [docs issue #123](https://github.com/fpgas-online/fpgas.online-docs/issues/123).
:::

## Compatible boards

All five share one PCB layout and pin assignments. The LiteX platform file `sqrl_acorn.py` works for all of them: change
only the device string. Board names the card, and the other columns are its FPGA, speed grade, DDR3 size and PCIe link.

| Board          | FPGA     | Speed Grade | DDR3   | PCIe    |
| -------------- | -------- | ----------- | ------ | ------- |
| LiteFury       | XC7A100T-FBG484 | -2          | 512 MB | Gen2 x4 |
| NiteFury       | XC7A200T-FBG484 | -2          | 512 MB | Gen2 x4 |
| Acorn CLE-101  | XC7A100T-FBG484 | -2          | 512 MB | Gen2 x4 |
| Acorn CLE-215  | XC7A200T-FBG484 | -2          | 1 GB   | Gen2 x4 |
| Acorn CLE-215+ | XC7A200T-FBG484 | -3          | 1 GB   | Gen2 x4 |

The CLE-215+ is equivalent to the NiteFury but with 1 GB DDR3 (against 512 MB). The file `sqrl_acorn.py` builds the
CLE-101 as `xc7a100t-fgg484-2` and passes `fgg484` to openFPGALoader; only the CLE-215 and CLE-215+ are `fbg484` there.
The LiteFury is the same board as the CLE-101. Sources are the [NiteFury and LiteFury repository](https://github.com/RHSResearchLLC/NiteFury-and-LiteFury) and the
[LiteX Acorn CLE-215 wiki](https://github.com/enjoy-digital/litex/wiki/Use-LiteX-on-the-Acorn-CLE-215).

## Telling the variants apart

Tell names what is read, Reads is the value it shows, and Identifies is the card or cards it points to.

| Tell                                                           | Reads         | Identifies                         |
| -------------------------------------------------------------- | ------------- | ---------------------------------- |
| PCI ID as sold, with SQRL's factory firmware in flash          | `1e24:021f`   | Acorn CLE-215+                     |
| PCI ID as sold, with SQRL's factory firmware in flash          | `1e24:0101`   | Acorn CLE-101                      |
| PCI ID on the fpgas.online design                              | `10ee:7021`   | the same card as its PCI subsystem ID (`1e24:021f` or `1e24:0101`) |
| JTAG IDCODE                                                    | `0x3636093`   | XC7A200T: CLE-215+, CLE-215, NiteFury |
| JTAG IDCODE                                                    | `0x3631093`   | XC7A100T: CLE-101, LiteFury        |

Where to read each tell:

- The PCI ID: the PCIe table of [Acorn specifications](overview/specifications.md#pcie-interface), read as in
  [How to check an Acorn's PCIe link by hand](checks/pcie-by-hand.md).
- The fpgas.online design: [Images](overview/design.md#images).
- The IDCODE: the `--detect` blocks of [How to run JTAG by hand on an Acorn](checks/jtag-by-hand.md).

## Wiring

All variants share the PCB layout and pin assignments, so the wiring applies unchanged to each of them.

- [On a Raspberry Pi 5](setup/rpi-5/wiring.md)
- [On a Compute Blade](setup/compute-blade/wiring.md)
