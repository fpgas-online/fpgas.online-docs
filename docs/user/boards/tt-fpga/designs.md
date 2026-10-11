---
type: reference
owner: documentation maintainers
reader: a visitor choosing a bundled design for a Tiny Tapeout FPGA demo board
review: 2026-11-10
---

# The bundled designs

**The designs that come with the Tiny Tapeout FPGA demo boards on tinytapeout.fpgas.online, one row each**. Each
row gives the design's name, what it does, the `ui` inputs it uses, its clock and its source. A design that also
reads the bidirectional `uio` pins says so in what it does. The table is made from each
design's `info.yaml` in [tinytapeout-fpga-demos](https://github.com/fpgas-online/tinytapeout-fpga-demos).

```{include} generated/designs.md
```
