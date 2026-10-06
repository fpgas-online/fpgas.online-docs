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

## Wiring

All variants share the PCB layout and pin assignments, so the wiring applies
unchanged to each of them: [on a Raspberry Pi 5](../wiring/rpi-5.md), [on a Compute
Blade](../wiring/compute-blade.md).
