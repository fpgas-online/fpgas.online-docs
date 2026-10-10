---
type: landing
owner: documentation maintainers
reader: someone who wants to know what a Tiny Tapeout FPGA demo board is before using one
review: 2026-11-10
---

# Tiny Tapeout FPGA demo board overview

- [The Tiny Tapeout FPGA demo board](board.md): what the board is, what is on it, and how it sits on its Raspberry Pi.
- [Tiny Tapeout FPGA demo board specifications](specifications.md): the FPGA, the Tiny Tapeout interface, the clock, the display and the programming interface.
- [Tiny Tapeout FPGA demo board pin mapping](pin-mapping.md): every signal from iCE40 ball to RP2350 GPIO, PMOD HAT pin and Raspberry Pi GPIO.
- [Programming a Tiny Tapeout FPGA demo board](programming.md): how a design reaches the FPGA.
- [Serial port ownership on a Tiny Tapeout FPGA demo board](serial-port.md): the daemon that holds the port, and what that means for a tool.
- [The firmware on a Tiny Tapeout FPGA demo board](firmware.md): the Tiny Tapeout SDK that the board boots into.
- [Tiny Tapeout FPGA demo board references](references.md): the outside documents and the LiteX support.

```{toctree}
:hidden:

board
specifications
pin-mapping
programming
serial-port
firmware
references
```
