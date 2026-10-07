# Tiny Tapeout FPGA board tests: from a workstation

**You want to run one of the Tiny Tapeout FPGA board's test designs (Pmod pin ID, Pmod loopback, UART) from
your own machine with the older runner, `verify_hardware.py`, rather than on the board's Raspberry Pi.** On
the Pi itself the check's own tools do this: [verifying 1](../building/verifying-1.md).

Tests are orchestrated by the
[hardware verification script](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/verify_hardware.py),
which uploads the wrapper scripts and bitstreams to the RPi, then runs the
appropriate test.

:::{warning}
**The command below names a host that does not exist today.** `verify_hardware.py`'s `HOSTS` table still
carries the pre-2026-08-23 names and `10.21.0.1xx` addresses (`welland-pi27` … `welland-pi33`), which Welland
does not use ([test-designs issue #17](https://github.com/fpgas-online/fpgas.online-test-designs/issues/17)),
so `--host welland-pi33` is the name in that table, not a host. The table itself is tracked on [Verifying a
deployment](../../../setup/verification.md#running-the-hardware-tests). Not run by us in this form since the
hosts were renamed.
:::

The Pis are not routable from outside tweed, so reaching one to stop its daemon
means jumping through the gateway; the form is in
[Gateway: tweed](../../../sites/welland.md#gateway-tweed) on the Welland page.

**`<host-ip>`** is the address of the Pi the board is on. At welland it follows the switch port the Pi is
plugged into, `10.21.<switch>.<port>` ([the per-port scheme](../../../setup/network.md#two-addressing-schemes));
find the port from the board's own page or the site's records at the time, as on [the boards at
welland](../installations/welland.md).

The wrapper opens the serial port on the target host, so the `fpgas-tt` daemon has to be stopped around the
run, and started again after, or the board drops off the public site (why: [Serial port
ownership](../../../setup/tinytapeout.md#serial-port-ownership)):

```console
# -J <you>@tweed.welland.mithis.com uses your own operator login on tweed.
$ ssh -J <you>@tweed.welland.mithis.com pi@<host-ip> sudo systemctl stop fpgas-tt
$ uv run python verify_hardware.py --board tt --host welland-pi33
$ ssh -J <you>@tweed.welland.mithis.com pi@<host-ip> sudo systemctl start fpgas-tt
```

```{include} wrappers.inc
```
