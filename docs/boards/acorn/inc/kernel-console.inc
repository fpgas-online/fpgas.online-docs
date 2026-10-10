:::{warning}
**The kernel console must not be on the FPGA's UART.** If a host's kernel command line puts it there (`console=ttyAMA0`, or `console=serial0` on a host whose header UART is enabled), loading any design that drives serial TX reboots or crashes the host. Those designs are the UART SoC, pin-ID and the GPIO loopback. The console reads the FPGA's bytes as garbage, and some are SysRq commands: `reboot(b)`, `crash(c)`, `poweroff(o)`, `kill-all-tasks(i)`. The FPGA drives K2 at its own baud rate, 1200 for pin-ID and 115200 for the UART SoC. The console reads those bytes as garbage, and some of them are **SysRq commands**: `reboot(b)`, `crash(c)`, `poweroff(o)`, `kill-all-tasks(i)`.
:::

Each row of the table is a kernel setting that keeps the console off the FPGA's UART, and where it is set. Check them on every host you set up and on a host that has been reinstalled.

| Host | Setting | Set in |
|------|---------|--------|
| Compute Blade | `console=tty1` | the kernel command line |
| Raspberry Pi 5 | `console=ttyAMA10` (the debug connector); the getty that systemd derives from the console lands there too | `[pi5] cmdline=cmdline-pi5.txt` |
| Either | `kernel.sysrq=0` | the kernel command line or `/etc/sysctl.d/` |
