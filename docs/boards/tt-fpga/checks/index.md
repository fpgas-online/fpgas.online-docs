---
type: landing
owner: documentation maintainers
reader: someone with a Tiny Tapeout FPGA demo board who wants to know that it works
review: 2026-11-10
---

# Tiny Tapeout FPGA demo board checks

- [fpgas-verify: the Tiny Tapeout demo boards](../../../verify/tt-fpga.md): how the check tells which board it has, and what its tests judge.
- [fpgas-verify: what an Arty, NeTV2, Fomu or TT FPGA check tests](../../../verify/tests.md): what each test of the check does, and when it passes.
- [How to install the Tiny Tapeout FPGA packages](../setup/packages.md): the check on the host, and how to run it by hand.
- [Tiny Tapeout FPGA demo board test designs](test-designs.md): the designs under `designs/` and the scripts that load them. Whether the breakout has a flash for its SPI Flash ID design is [test-designs issue #258](https://github.com/fpgas-online/fpgas.online-test-designs/issues/258).

```{toctree}
:hidden:

test-designs
```
