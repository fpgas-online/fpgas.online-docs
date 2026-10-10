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
| GPIO7-11 cannot be driven by the PMOD test | Raspberry Pi GPIO7-11 overlap with the SPI0 bus and conflict with PMOD HAT pins (JA/JB pins 2-4) | `sudo rmmod spidev spi_bcm2835` before a PMOD test run by hand. The check's own wiring test unloads the SPI drivers and loads them again itself: [The wiring test](../../../verify/tt-fpga.md#the-wiring-test) |
| `uio[1,2,3]` read wrongly while `uo_out[1,2,3]` are driven | HAT JB pins 2-4 and HAT JA pins 2-4 are the same Raspberry Pi GPIO lines (GPIO10, GPIO9, GPIO11), so the two FPGA outputs fight each other. Which signals sit on those pins is contested: [test-designs issue #58](https://github.com/fpgas-online/fpgas.online-test-designs/issues/58) | Do not drive `uo_out[1:3]` and `uio[1:3]` at the same time; the GPIO loopback test drives only `ui_in` and reads only `uo_out` |
