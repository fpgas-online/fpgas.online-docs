---
type: landing
owner: documentation maintainers
reader: someone with an Acorn on its host who wants to know that it works
review: 2026-11-10
---

# Acorn checks

- [How to run the Acorn check on a Raspberry Pi 5](rpi-5.md): the check on the host, and how to read its result.
- [How to run the Acorn check on a Compute Blade](compute-blade.md): the check on the blade, and how to read its result.
- [How to make a Compute Blade boot ready for JTAG](compute-blade-jtag.md): the blade's boot settings that let JTAG run.
- [Acorn tests by hand](by-hand.md): each test run by hand, one page for each carrier.
- [The Acorn DDR memory test](ddr-memory.md): how the check tests the card's memory.
- [The Acorn Wishbone bridges test](wishbone-bridges.md): how the check reaches the design's registers.
- [JTAG loads and the PCIe endpoint](jtag-and-the-pcie-endpoint.md): why the endpoint is detached, and why a blade needs its serial port off.

```{toctree}
:hidden:

rpi-5
compute-blade
Tests by hand <by-hand>
ddr-memory
wishbone-bridges
jtag-and-the-pcie-endpoint
```
