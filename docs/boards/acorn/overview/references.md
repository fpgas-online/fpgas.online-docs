---
type: reference
owner: documentation maintainers
reader: someone looking for the documents behind the Acorn pages
review: 2026-11-10
---

# Acorn references

This page lists the vendor's and LiteX's documents, our own repositories, and the source of the generated wiring.
Each list gives one link per document, with a description of what it holds.

## Our repositories

The wiring has one source, the table `wiring.toml`. The wiring sheets, the pin tables and the building guide's pages are
generated from it.

- Wiring source: [fpgas.online-test-designs `docs/wiring/acorn/`](https://github.com/fpgas-online/fpgas.online-test-designs/tree/main/docs/wiring/acorn)
- The fpgas.online Acorn design: [`designs/acorn-pcie`](https://github.com/fpgas-online/fpgas.online-test-designs/tree/main/designs/acorn-pcie)

## LiteX

The LiteX target `litex_boards/targets/sqrl_acorn.py` provides a PCIe Gen2 x4 endpoint with DMA and a DDR3 SDRAM
controller (LiteDRAM). It also provides SPI flash access (LiteSPI), ICAP for warm-boot and multiboot, and optional
Ethernet via a PCIe bridge.

- Platform definition: [`litex_boards/platforms/sqrl_acorn.py`](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/sqrl_acorn.py)
- Target definition: [`litex_boards/targets/sqrl_acorn.py`](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/targets/sqrl_acorn.py)
- Wiki: [Use LiteX on the Acorn CLE-215](https://github.com/enjoy-digital/litex/wiki/Use-LiteX-on-the-Acorn-CLE-215)
- PCIe core: [LitePCIe](https://github.com/enjoy-digital/litepcie)
- ICAP core: [LiteX `icap.py`](https://github.com/enjoy-digital/litex/blob/master/litex/soc/cores/icap.py)

## The card and its documents

- Running Linux: [Acorn CLE-215+ blog post](https://spoolqueue.com/new-design/fpga/migen/litex/2020/08/11/acorn-cle-215.html)
- Flashing with OpenOCD: [NiteFury/Acorn flashing guide](https://github.com/Gbps/nitefury-openocd-flashing-guide)
- NiteFury and LiteFury: [RHSResearchLLC/NiteFury-and-LiteFury](https://github.com/RHSResearchLLC/NiteFury-and-LiteFury)
- MultiBoot with SPI: [Xilinx XAPP1247](https://docs.amd.com/v/u/en-US/xapp1247-multiboot-spi)

## Parts and carriers

- Molex Pico-EZmate cable: [Molex 0369200601 at DigiKey](https://www.digikey.fr/en/products/detail/molex/0369200601/10233018)
- Compute Blade: [computeblade.com](https://computeblade.com/)
- Compute Blade GPIO: [GPIO guide](https://docs.computeblade.com/blade/guides/gpio)
- Compute Blade source: [uptime-lab/compute-blade](https://github.com/uptime-lab/compute-blade)
