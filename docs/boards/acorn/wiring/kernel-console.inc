## Kernel console on the FPGA UART

:::{warning}
**The kernel console must not be on the FPGA's UART.** If a host's kernel
command line puts it there (`console=ttyAMA0`, or `console=serial0` on any host whose
header UART is enabled: `uart0-pi5` on a Pi 5, `enable_uart=1` on a blade, as on
pi16 at ps1), loading any design that drives serial TX — the UART
SoC, pin-ID, the GPIO loopback — reboots or crashes the host. A fleet host
is meant to boot with `console=tty1` (Compute Blades) or `console=ttyAMA10` (Pi 5s); check
this on any new host, and on a host that has been reinstalled: pi16 at ps1 had
its console on the FPGA UART when read on 2026-10-05 ([pi16 at ps1 on 5 October
2026](../installations/ps1-reads.md#pi16-at-ps1-on-5-october-2026)).
:::

The FPGA drives K2 at its own baud rate (1200 for pin-ID, 115200 for the UART
SoC), and the kernel console reads the bytes as garbage, some of which are
**SysRq commands** — `reboot(b)`, `crash(c)`, `poweroff(o)`,
`kill-all-tasks(i)`. Apply both:

1. Keep the console off the FPGA UART: `console=tty1` on a Compute Blade;
   `console=ttyAMA10` (the debug connector) on a Pi 5, via `[pi5]
   cmdline=cmdline-pi5.txt`, so the getty systemd derives from the console lands
   there too.
2. Disable SysRq: `kernel.sysrq=0` on the kernel command line or in
   `/etc/sysctl.d/`.

Tracked in [fpgas-online/todo#22](https://github.com/fpgas-online/todo/issues/22)
and [test-designs
issue #3](https://github.com/fpgas-online/fpgas.online-test-designs/issues/3).
