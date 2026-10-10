---
type: reference
owner: documentation maintainers
reader: someone whose Acorn on a Compute Blade does not answer on its wires
review: 2026-11-10
---

# Acorn wiring faults on a Compute Blade

**Your Acorn on a Compute Blade does not answer on JTAG or on its serial port, and you want the likely cause.** Which wire goes where is on [Acorn wiring on a Compute Blade](../setup/compute-blade/wiring.md); the blade's settings are on [A Compute Blade's pins and settings for an Acorn](../setup/compute-blade/blade-settings.md).

| Problem | Likely cause | Fix |
|---------|--------------|-----|
| GPIO pins don't respond | Cable wired incorrectly | Buzz each wire from its Pico-EZmate position (pin 1 = GND, nearest the M.2 edge) to the pin in [the wiring tables](../setup/compute-blade/wiring.md) |
| Pi reboots when a serial design loads | Kernel console on the FPGA UART; SysRq | Console to `ttyAMA10` (Pi 5) / `tty1` (blade), `kernel.sysrq=0` |
| UART dead after JTAG on a Compute Blade | openFPGALoader left GPIO14 a plain output | Only in a boot with the serial port on (kernel 6.12), and only once the loaded design treats J2 as an input: on a CM4 `pinctrl set 14,15 a0`; on a CM5 `pinctrl set 14,15 a4` (one or the other), then open `/dev/ttyAMA0`. Never with pin-ID loaded |
