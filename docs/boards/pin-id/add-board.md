---
type: how-to
owner: documentation maintainers
reader: someone who wants the pin-id design built for an FPGA board that has no build target yet
review: 2026-11-10
---

# How to add a board to the pin-id design

**You have an FPGA board with a LiteX platform and want the pin-id design to build for it**. This page adds the board's build script, scanner GPIO list and Makefile targets. The scan itself is on [How to scan a board's wiring with the pin-id design](scan.md).

This procedure is waiting for its run: [test-designs issue #262](https://github.com/fpgas-online/fpgas.online-test-designs/issues/262).

## What you need

- A checkout of the [test-designs repository](https://github.com/fpgas-online/fpgas.online-test-designs) with the `designs/pmod-pin-id` directory.
- The board's LiteX platform, importable as `litex_boards.platforms.your_board`.
- The board's PMOD connector names, clock frequency and I/O standard.

## Steps

1. In `designs/pmod-pin-id/gateware`, copy `pmod_pin_id_arty.py` to `pmod_pin_id_<board>.py` and change the platform import, the connector list, the clock frequency and the I/O standard. The `build_pin_list()` function works unchanged, because it reads connector pin names from any LiteX platform.

   ```python
   # Change the platform import
   from litex_boards.platforms.your_board import Platform

   # Change the connector list to match your board's connectors
   CONNECTORS = ["pmoda", "pmodb"]  # whatever your board has

   # Change the clock frequency
   SYS_CLK_FREQ = 48e6  # your board's clock

   # Change the I/O standard if needed (in build_io_extensions)
   IOStandard("LVCMOS33")  # or LVCMOS18, or another standard
   ```

2. In `host/identify_pmod_pins.py`, update `PMOD_HAT_PORTS` if your host uses a different GPIO-to-connector mapping than the Digilent PMOD HAT, or pass `--gpios` explicitly when you scan.

3. In the `designs/pmod-pin-id` Makefile, add the build, program and scan targets for the board.

   ```makefile
   gateware-yourboard:
   	$(PYTHON) gateware/pmod_pin_id_yourboard.py --build

   program-yourboard:
   	openFPGALoader -b yourboard build/yourboard/gateware/your_board.bit

   scan-yourboard:
   	$(PYTHON) host/identify_pmod_pins.py --gpios 2 3 4 5 6 7
   ```

## Check

Run `make gateware-yourboard`, `make program-yourboard` and `make scan-yourboard`. The scan prints a mapping table like the one quoted under [Check on the scan page](scan.md#check). It gives an FPGA pin name for each GPIO you passed.

## If it fails

A garbled or "no signal" line in the scan has its cause and fix in the table under [If it fails on the scan page](scan.md#if-it-fails).

## Next

- [How to scan a board's wiring with the pin-id design](scan.md)
- [Pin-id scanner options](scanner-options.md)
- [The pin-id design](../pin-id.md)
