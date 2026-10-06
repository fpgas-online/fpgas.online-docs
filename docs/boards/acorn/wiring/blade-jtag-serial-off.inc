:::{warning}
**JTAG needs the header's serial port off at boot.** TMS is GPIO14, the serial
port's TX pin. With `enable_uart=1` the kernel's serial driver holds GPIO14
whether or not a console or a getty uses the port, and kernel 6.18 does not hand
a held pin to openFPGALoader, which then stops with `gpiod_line_request_set_values_subset:
Assertion 'request' failed` (read on pi16 at ps1, a CM5, on 2026-10-05: [pi16 at ps1 on 5
October 2026](../installations/ps1-reads.md#pi16-at-ps1-on-5-october-2026)). The serial port off
means `enable_uart=0`, no `dtoverlay=uart0…` or `dtparam=uart0` line, and no
`console=serial0` word on the kernel command line, which is expected to free
GPIO14;
in that boot there is no serial pair to test. **Booting a blade that way is not
yet run by us on this hardware**, and nothing has been read on a CM4. pi20 at ps1's
JTAG answered under kernel 6.12.75 with the serial port on.
:::
