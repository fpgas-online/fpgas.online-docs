---
type: explanation
owner: documentation maintainers
reader: someone who wants to know what runs on the demo board's controller
review: 2026-11-10
---

# The firmware on a Tiny Tapeout FPGA demo board

**You want to know what runs on the RP2350 of a Tiny Tapeout FPGA demo board, and why it is left as it is.**

The programming the controller does is on [Programming a Tiny Tapeout FPGA demo board](programming.md). The faults it can show are on [Tiny Tapeout FPGA demo board faults](../troubleshooting/board-faults.md).

The boards run the Tiny Tapeout MicroPython SDK, release 3.1.0. With that release the SDK's `tt` object comes up as `Shuttle FPGA`, and the Tiny Tapeout Commander connects. The `ttdbv3` build the boards shipped with stalled at boot.

The stall is in the stock `main.py` of the RP2350, which calls `DemoBoard()`. That call probes I2C and can hang permanently, which makes the board unrecoverable without a physical reset. SDK 3.1.0 boots cleanly, and the board reports `board present`.

The public site depends on that boot. The site and the `fpgas-tt` daemon's design list need the SDK to boot into `DemoBoard()`. A `main.py` that does nothing therefore takes the board off [the Tiny Tapeout site](https://tinytapeout.fpgas.online), so the board's `main.py` stays the SDK's own.

The check that runs on the host is on [fpgas-verify: the Tiny Tapeout demo boards](../../../verify/tt-fpga.md).
