---
type: landing
owner: documentation maintainers
reader: someone about to put a NeTV2 on a Raspberry Pi
review: 2026-11-10
---

# Setting up a NeTV2

- [NeTV2 wiring to a Raspberry Pi](wiring.md): which board signal goes to which Raspberry Pi pin.
- [How to install the NeTV2 packages](packages.md): the fpgas.online packages for the board, and the check.
- [How to load a design into a NeTV2 on a Raspberry Pi 3B+](load-pi-3b-plus.md): over GPIO JTAG with openFPGALoader.
- [How to load a design into a NeTV2 on a Raspberry Pi 5](load-pi-5.md): detach the PCIe endpoint, then load.
- [How to write a design into a NeTV2's flash](write-flash.md): so the design survives a power cycle.
- [How to free a NeTV2's serial port before a test](free-serial-port.md): stop what holds the port.

```{toctree}
:hidden:

wiring
packages
load-pi-3b-plus
load-pi-5
write-flash
free-serial-port
```
