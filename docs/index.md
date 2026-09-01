# fpgas.online

FPGA hardware you can reach over the internet: Raspberry Pi hosts with FPGA
boards attached, wired up so a design can be built, loaded and driven remotely.

This site documents how that hardware is put together and how the
infrastructure behind it runs. It is written for whoever has to fix it next.

:::{note}
These pages describe live infrastructure, so they track the current state
rather than a released version. Where a page records a measurement, it says
when it was taken.
:::

## Where things live

The documentation is assembled here, but most of the systems it describes have
their own repositories under the
[fpgas-online](https://github.com/fpgas-online) organisation:

`fpgas.online-infra`
: Ansible for the servers and the Raspberry Pi NFS root.

`fpgas.online-test-designs`
: FPGA designs used to verify that a board is wired up correctly, plus the
  hardware pinout documentation.

`fpgas.online-site`
: The Django web application.

`fpgas.online-cam`
: Camera capture and streaming for the Pi hosts.

`apt`
: The APT package repository served at <https://apt.fpgas.online>.

```{toctree}
:maxdepth: 2
:caption: Contents

sites/index
packages
contributing
```

## Sites

There are two of them, and they are wired differently — which matters more
often than you would expect.

[Welland](sites/welland.md)
: The private test lab in South Australia. Raspberry Pi 5 hosts with SQRL Acorn
  boards on mPCIe adapters.

[PS1](sites/ps1.md)
: The public service at the Pumping Station: One hackerspace in Chicago.
  Compute Blade carriers with CM4 and CM5 modules, and a different JTAG and
  serial pinout from Welland.
