---
type: how-to
owner: documentation maintainers
reader: someone with a NeTV2 on a Raspberry Pi 3B+ loading a design
review: 2026-11-10
---

# How to load a design into a NeTV2 on a Raspberry Pi 3B+

**You want to load a bitstream into a NeTV2's FPGA on a Raspberry Pi 3B+, over GPIO JTAG with openFPGALoader.**

The load goes to the FPGA's SRAM and is lost at power-off; [How to write a design into a NeTV2's flash](write-flash.md) keeps it. A NeTV2 on a Raspberry Pi 5 is on [its own page](load-pi-5.md).

:::{warning}
On these hosts the FPGA's serial TX pin is the Pi's kernel console UART. A bitstream that drives that line crashes a netbooted Pi through SysRq. A host is safe when `kernel.sysrq` reads 0 and the kernel command line has no `console=serial0`.
:::

## What you need

- A NeTV2 wired as on [NeTV2 wiring to a Raspberry Pi](wiring.md#jtag).
- openFPGALoader on the Pi, which [the NeTV2 packages](packages.md) install.
- A bitstream, here `design.bit`.

## Steps

1. On the Pi, run `sysctl kernel.sysrq` and `cat /proc/cmdline`, and confirm that `kernel.sysrq` reads 0 and the command line has no `console=serial0`.
2. On the Pi, run `sudo openFPGALoader --cable libgpiod --pins 27:22:4:17 --detect` to see the FPGA answer on JTAG.
3. On the Pi, run `sudo openFPGALoader --cable libgpiod --pins 27:22:4:17 design.bit` to load the bitstream; the effective JTAG clock is about 5 MHz, so a load is slow.

The pin order is `TDI:TDO:TCK:TMS`.

## Check

Step 2 lists the FPGA of an XC7A35T board as `idcode 0x0362d093` with IR length 6. The part and its IDCODE are in [FPGA device variants](../overview/specifications.md#fpga-device-variants).

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| The Pi crashes or drops off when the design starts | The design drives the serial TX line while the Pi's kernel console and SysRq are on | Run `sudo sysctl -w kernel.sysrq=0` before loading |

## Next

- [How to write a design into a NeTV2's flash](write-flash.md)
- [How to free a NeTV2's serial port before a test](free-serial-port.md)
- [Programming a NeTV2](../overview/programming.md)
