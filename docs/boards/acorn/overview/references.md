# Acorn resources and links

**You want the documents, repositories and sources behind the Acorn pages: the vendor's and LiteX's
documents, our own repositories, and where the generated wiring comes from.**

## Where the wiring comes from

The wiring has one source: the table `wiring.toml` in
[fpgas.online-test-designs](https://github.com/fpgas-online/fpgas.online-test-designs/tree/main/docs/wiring/acorn).
The wiring sheets, the pin tables and the building guide's pages are generated from it.

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
- Wiring source: [fpgas.online-test-designs `docs/wiring/acorn/`](https://github.com/fpgas-online/fpgas.online-test-designs/tree/main/docs/wiring/acorn)
- NiteFury/LiteFury: [RHSResearchLLC/NiteFury-and-LiteFury](https://github.com/RHSResearchLLC/NiteFury-and-LiteFury)
- Molex Pico-EZmate cable: <https://www.digikey.fr/en/products/detail/molex/0369200601/10233018>
- Compute Blade: <https://computeblade.com/>
- Compute Blade GPIO docs: <https://docs.computeblade.com/blade/guides/gpio>
- Compute Blade GitHub: <https://github.com/uptime-lab/compute-blade>
- Xilinx XAPP1247, MultiBoot with SPI: <https://docs.amd.com/v/u/en-US/xapp1247-multiboot-spi>
- LitePCIe: <https://github.com/enjoy-digital/litepcie>
- LiteX ICAP core: <https://github.com/enjoy-digital/litex/blob/master/litex/soc/cores/icap.py>
- The fpgas.online Acorn design: [`designs/acorn-pcie`](https://github.com/fpgas-online/fpgas.online-test-designs/tree/main/designs/acorn-pcie)
