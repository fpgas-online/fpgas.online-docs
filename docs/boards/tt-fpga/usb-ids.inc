The check finds the demo board's microcontroller on USB as `2e8a:0005` or `2e8a:000f` (MicroPython's serial
port, "MicroPython Board in FS mode"); the boards at welland read `2e8a:0005` on 3 September 2026, and
rpi-hwid, which asks the board what it is, looks at `2e8a:0005` only. Source: the check's code
(`boards/tt_fpga.py` in fpgas.online-test-designs) and [Which Tiny Tapeout board it
is](../../../verify/fpgas-verify.md#which-tiny-tapeout-board-it-is).
