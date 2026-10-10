---
type: reference
owner: documentation maintainers
reader: someone whose Acorn on a Raspberry Pi 5 does not answer on its wires
review: 2026-11-10
---

# Acorn wiring faults on a Raspberry Pi 5

**Your Acorn on a Raspberry Pi 5 does not answer on JTAG or on its serial port, and you want the likely cause.** Which wire goes where is on [Acorn wiring on a Raspberry Pi 5](../setup/rpi-5/wiring.md); the Pi's settings are on [How to set up a Raspberry Pi 5 for an Acorn](../setup/rpi-5/pi-settings.md).

| Problem | Likely cause | Fix |
|---------|--------------|-----|
| GPIO pins don't respond | Cable wired incorrectly | Buzz each wire from its Pico-EZmate position (pin 1 = GND, nearest the M.2 edge) to the pin in [the wiring tables](../setup/rpi-5/wiring.md) |
| `JTAG init failed with: Unable to open gpio chip` (Pi 5) | The `libgpiod` cable opens `/dev/gpiochip0`; the header is `gpiochip15` | `ln -sfn /dev/gpiochip15 /dev/gpiochip0` |
| No `/dev/ttyAMA0` on a Pi 5 | RP1 uart0 disabled; `disable-bt` does not enable it on bcm2712 | `[pi5] dtoverlay=uart0-pi5` |
| Board hung, ~0.4 W on PoE instead of ~8 W | Wedged Pi 5 | PoE cycle the switch port; a Pi 5 needs over 90 s to come back |
| Pi reboots when a serial design loads | Kernel console on the FPGA UART; SysRq | Console to `ttyAMA10` (Pi 5) / `tty1` (blade), `kernel.sysrq=0` |
