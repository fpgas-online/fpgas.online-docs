Tests are orchestrated by the
[hardware verification script](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/verify_hardware.py),
which uploads the wrapper scripts and bitstreams to the RPi, then runs the
appropriate test.

The Pis are not routable from outside tweed, so reaching one to stop its daemon
means jumping through the gateway; the form is in
[Gateway: tweed](/sites/welland.md#gateway-tweed) on the Welland page.

```console
# <host-ip> is the present address of the Pi the board is on, from its page on the site.
# The wrapper opens the serial port on the target host, so fpgas-tt has to be
# stopped -- and started again after, or the board drops off the public site.
# -J <you>@tweed.welland.mithis.com uses your own operator login on tweed.
$ ssh -J <you>@tweed.welland.mithis.com pi@<host-ip> sudo systemctl stop fpgas-tt
$ uv run python verify_hardware.py --board tt --host welland-pi33
$ ssh -J <you>@tweed.welland.mithis.com pi@<host-ip> sudo systemctl start fpgas-tt
```

:::{todo}
`verify_hardware.py`'s `HOSTS` table still carries the pre-2026-08-23 names and
`10.21.0.1xx` addresses (`welland-pi27` … `welland-pi33`), which Welland does not use
([test-designs issue #17](https://github.com/fpgas-online/fpgas.online-test-designs/issues/17)), so the
`--host welland-pi33` above is the name in that table, not a host that exists today.
The table itself is tracked on [Verifying a deployment](/setup/verification.md#running-the-hardware-tests);
what is specific to this board is that the wrapper also needs the `fpgas-tt` daemon stopped and
started again around a run
(see [Serial port ownership](/setup/tinytapeout.md#serial-port-ownership)).
Not run by us in this form since the hosts were renamed.
:::
