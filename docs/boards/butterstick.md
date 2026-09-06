# ButterStick

:::{note}
**Status: Future / Planned** — this board is not yet deployed in the
fpgas.online infrastructure, and no wiring to a Raspberry Pi exists for it.
Everything below comes from the LiteX platform file and the vendor material,
not from a board on a bench.
:::

The ButterStick is a high-performance ECP5 development board designed by Greg
Davill (Great Scott Gadgets / gsg). It features a Lattice ECP5 with SERDES
capabilities, DDR3 memory, Gigabit Ethernet, and a SYZYGY high-speed connector.

:::{warning}
The vendor site `https://butterstick.io` is offline: the domain has no DNS
record at all (NXDOMAIN, checked 2026-09-03). The links the source cited to it
are kept below as plain text so the provenance survives, but they cannot be
followed. The
[ButterStick GitHub organisation](https://github.com/butterstick-fpga) is still
up and is the best remaining primary source.
:::

## Key specifications

| Parameter | Value |
|-----------|-------|
| FPGA | Lattice ECP5UM5G-85F-8BG381C |
| Package | BG381 |
| SERDES | Up to 5 Gbps (ECP5UM5G variant) |
| Logic cells | 84,000 |
| DDR3 SDRAM | 1 GB (32-bit bus) |
| Ethernet | RGMII Gigabit Ethernet (1000Base-T) |
| USB | ULPI USB 2.0 PHY |
| Expansion | SYZYGY connector (high-speed, not PMOD) |
| LEDs | User LEDs |
| JTAG | On-board USB-JTAG |
| Power | USB-C powered |

Source: the
[gsd_butterstick platform file](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/gsd_butterstick.py)
and the ButterStick website at `https://butterstick.io` (offline, see above).

## Notable differences from other boards

- **ECP5UM5G with SERDES**: The `5G` variant includes high-speed
  serializer/deserializer blocks, enabling protocols like PCIe Gen1, SATA, or
  custom high-speed links.
- **SYZYGY connector** (not PMOD): The SYZYGY standard provides higher-speed and
  higher-density connectivity than PMOD. PMOD-based tests cannot run on this
  board without an adapter.
- **Gigabit Ethernet**: RGMII PHY supporting 1000Base-T, unlike the 100Base-T on
  the Arty and NeTV2.
- **ULPI USB**: External USB 2.0 PHY, unlike the Fomu's native USB.
- **DDR3**: Full DDR3 with 32-bit bus, similar to NeTV2 but larger capacity.

## LiteX integration

| Property | Value |
|----------|-------|
| Platform module | `litex_boards.platforms.gsd_butterstick` |
| Target module | `litex_boards.targets.gsd_butterstick` |
| Toolchain | Yosys + nextpnr-ecp5 (open source, Project Trellis) |

## Programming

Untried here — no ButterStick has been connected to a host at either site.

```console
# Via openFPGALoader
$ openFPGALoader -b butterstick design.bit

# Via DFU (ButterStick has a DFU bootloader)
$ dfu-util -D design.bit
```

## References

- LiteX platform file:
  <https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/gsd_butterstick.py>
- ButterStick website: `https://butterstick.io` — offline, no DNS record as of
  2026-09-03
- ButterStick GitHub: <https://github.com/butterstick-fpga>
