---
type: reference
owner: documentation maintainers
reader: someone whose Acorn on a Compute Blade does not answer on its wires
review: 2026-11-10
---

# Acorn wiring faults on a Compute Blade

**Your Acorn on a Compute Blade does not answer on JTAG or on its serial port, and you want the likely cause.**

Which wire goes where is on [Acorn wiring on a Compute Blade](../setup/compute-blade/wiring.md). The blade's settings are on [A Compute Blade's pins and settings for an Acorn](../setup/compute-blade/blade-settings.md).

Each row gives what you see, the likely cause, and the fix. The dead-UART fix applies only in a boot with the serial port on (kernel 6.12). It also needs a loaded design that treats J2 as an input, and is never run with pin ID loaded.

| Problem | Likely cause | Fix |
|---------|--------------|-----|
| GPIO pins don't respond | Cable wired incorrectly | Buzz each wire from its Pico-EZmate position (pin 1 = GND, nearest the M.2 edge) to its pin in [the wiring tables](../setup/compute-blade/wiring.md) |
| Blade reboots when a serial design loads | Kernel console on the FPGA UART; SysRq | `console=tty1` and `kernel.sysrq=0` |
| UART dead after JTAG on a CM4 | openFPGALoader left GPIO14 a plain output | `pinctrl set 14,15 a0`, then open `/dev/ttyAMA0` |
| UART dead after JTAG on a CM5 | openFPGALoader left GPIO14 a plain output | `pinctrl set 14,15 a4`, then open `/dev/ttyAMA0` |
