---
type: reference
owner: documentation maintainers
reader: someone looking for the documents behind the NeTV2 pages
review: 2026-11-10
---

# NeTV2 references

**You want the outside documents and the LiteX files behind the NeTV2 pages.** Each line names a document and links it.

- LiteX platform file: [`litex_boards/platforms/kosagi_netv2.py`](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_netv2.py), the source of the pin tables on [NeTV2 specifications](specifications.md).
- LiteX target file: [`litex_boards/targets/kosagi_netv2.py`](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/targets/kosagi_netv2.py).
- NeTV2 FPGA reference design: [AlphamaxMedia/netv2-fpga](https://github.com/AlphamaxMedia/netv2-fpga).
- NeTV2 MVP scripts: [alphamaxmedia/netv2mvp-scripts](https://github.com/alphamaxmedia/netv2mvp-scripts), whose [alphamax-rpi OpenOCD configuration](https://github.com/alphamaxmedia/netv2mvp-scripts/blob/master/alphamax-rpi.cfg) is the source of the JTAG pin mapping on [NeTV2 wiring to a Raspberry Pi](../setup/wiring.md).
- The RP1 PIO JTAG support: [mithro/openFPGALoader (feature/rp1-jtag-netv2)](https://github.com/mithro/openFPGALoader/tree/feature/rp1-jtag-netv2) and [mithro/rp1-jtag](https://github.com/mithro/rp1-jtag).
- The designer's blog on the NeTV2 design: [bunnie's blog](https://www.bunniestudios.com/blog/?p=4842).
- The board's campaign page: [Crowd Supply NeTV2](https://www.crowdsupply.com/alphamax/netv2).
