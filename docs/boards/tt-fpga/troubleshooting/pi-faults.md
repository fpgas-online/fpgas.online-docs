---
type: reference
owner: documentation maintainers
reader: someone whose PMOD test of a Tiny Tapeout FPGA demo board reads wrong values
review: 2026-11-10
---

# Tiny Tapeout FPGA demo board faults on the Raspberry Pi

**A PMOD test of your demo board reads wrong values or cannot drive a pin, and you want the likely cause.**

Which pins are shared is on [Tiny Tapeout FPGA demo board wiring to a Raspberry Pi](../setup/wiring.md#shared-gpios-of-ja-and-jb). The faults of the board itself are on [Tiny Tapeout FPGA demo board faults](board-faults.md).

What you see is the symptom, Likely cause the reason, and Fix what to do.

| What you see | Likely cause | Fix |
|---|---|---|
| GPIO7-11 cannot be driven by the PMOD test | Raspberry Pi GPIO7-11 overlap with the SPI0 bus and conflict with PMOD HAT pins (JA/JB pins 2-4) | `sudo rmmod spidev spi_bcm2835` before a PMOD test run by hand. Nothing else on the Pi may be using SPI0: this takes the bus away from it |
| `uio[1,2,3]` read wrongly while the Raspberry Pi drives `ui_in[1,2,3]` | HAT JB pins 2-4 and HAT JA pins 2-4 are the same Raspberry Pi GPIO lines (GPIO10, GPIO9, GPIO11), so a drive on `ui_in[1:3]` also reaches `uio[1:3]` | Make `uio[1:3]` inputs in the design while the Raspberry Pi drives `ui_in[1:3]`; leave GPIO10, GPIO9 and GPIO11 as inputs while the design drives `uio[1:3]` |
