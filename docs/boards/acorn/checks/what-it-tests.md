---
type: landing
owner: documentation maintainers
reader: someone who wants to know what the Acorn check tests and how
review: 2026-11-10
---

# What the Acorn check tests

- [The Acorn check](about.md): what the check is, what it does to the card, and what it can show.
- [Acorn tests and their wires on a Raspberry Pi 5](rpi-5-tests.md): the wires each test uses on a Pi 5.
- [Acorn tests and their wires on a Compute Blade](compute-blade-tests.md): the wires each test uses on a blade.
- [The Acorn DDR memory test](ddr-memory.md): how the check tests the card's memory.
- [The Acorn Wishbone bridges test](wishbone-bridges.md): how the check reaches the design's registers.
- [JTAG loads and the PCIe endpoint](jtag-and-the-pcie-endpoint.md): why the endpoint is detached, and why a blade needs its serial port off.

```{toctree}
:hidden:

about
rpi-5-tests
compute-blade-tests
ddr-memory
wishbone-bridges
jtag-and-the-pcie-endpoint
```
