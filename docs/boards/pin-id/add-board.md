---
type: how-to
owner: documentation maintainers
reader: someone who wants the pin-id design built for an FPGA board that has no build target yet
review: 2026-11-10
---

# How to add a board to the pin-id design

**You have an FPGA board with a LiteX platform and want the pin-id design to build for it**. This page adds the board's build script, scanner GPIO list and Makefile targets. The scan itself is on [How to scan an Arty A7's wiring with the pin-id design](scan.md).

This procedure is waiting for its run: [test-designs issue #262](https://github.com/fpgas-online/fpgas.online-test-designs/issues/262).

## What you need

- A checkout of the [test-designs repository](https://github.com/fpgas-online/fpgas.online-test-designs) with the `designs/pmod-pin-id` directory.
- The board's LiteX platform, importable as `litex_boards.platforms.your_board`.
- The board's PMOD connector names, clock frequency and I/O standard.

## Steps

1. In `designs/pmod-pin-id/gateware`, copy `pmod_pin_id_arty.py` to `pmod_pin_id_<board>.py`. The `build_pin_list()`
   function works unchanged, because it reads connector pin names from any LiteX platform.
2. In the copy, change every line that names the Arty, the docstring and comments included:

   ```python
   from litex_boards.platforms.your_board import Platform   # the platform import
   CONNECTORS = ["pmoda", "pmodb"]                          # your board's connectors
   SYS_CLK_FREQ = 48e6                                      # your board's clock
   IOStandard("LVCMOS33")                                   # in build_io_extensions, if your board differs
   parser = argparse.ArgumentParser(description="PMOD Pin Identification for your board")
   parser.add_argument("--variant", default="v1", choices=["v1"])  # your board's variants
   platform = Platform(variant=args.variant, toolchain=args.toolchain)   # drop variant= if the platform has none
   f"{board_dir('yourboard', args.variant)}{flow_suffix(args.toolchain, args.synth_mode)}"  # in the build path
   ```

3. If your board's device string has a dash between the part and the package, such as `xc7a35t-fgg484-2`, add the
   two openXC7 fixups. Import them with the script's other fixup, as `pmod_pin_id_acorn.py` and
   `pmod_pin_id_netv2.py` do, and call them after the platform is made. `print(platform.device)` shows the string.

   ```python
   from designs._shared.platform_fixups import ensure_chipdb_symlink, fix_openxc7_device_name, require_timing

   if args.toolchain == "openxc7":
       fix_openxc7_device_name(platform)
       ensure_chipdb_symlink(platform)
   ```

4. In `host/identify_pmod_pins.py`, update `PMOD_HAT_PORTS` if your host uses a different GPIO-to-connector mapping
   than the Digilent PMOD HAT, or pass `--gpios` explicitly when you scan.
5. In the `designs/pmod-pin-id` Makefile, add your board's variants and its build rules beside the Arty's, NeTV2's and
   Acorn's. Copy `program-arty` and `scan-arty` for the board too: the bitstream is at
   `build/<board>-<variant>-<flow>/gateware/<platform name>.bit`. Build with the flow target, not `make gateware`.

   ```makefile
   YOURBOARD_VARIANTS := v1
   $(eval $(call flow_rules,yourboard,pmod_pin_id_yourboard.py,$(YOURBOARD_VARIANTS)))

   program-yourboard:
   	openFPGALoader -b yourboard build/yourboard-$(VARIANT)-$(PROGRAM_FLOW)/gateware/your_board.bit

   scan-yourboard:
   	$(PYTHON) host/identify_pmod_pins.py
   ```

6. Build, load and scan the board.

   ```console
   $ make gateware-yourboard-v1-yosys-nextpnr
   $ make program-yourboard VARIANT=v1
   $ make scan-yourboard
   ```

This page does not cover registering a board elsewhere in test-designs: the CI job, the scanner's board list, the
check's board module and the packages.

## Check

The scan prints a mapping table like the one quoted under [Check on the scan page](scan.md#check). It gives an FPGA pin name for each GPIO it scanned.

## If it fails

A garbled or "no signal" line in the scan has its cause and fix in the table under [If it fails on the scan page](scan.md#if-it-fails).

## Next

- [How to scan an Arty A7's wiring with the pin-id design](scan.md)
- [Pin-id scanner options](scanner-options.md)
- [The pin-id design](../pin-id.md)
