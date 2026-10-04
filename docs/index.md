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

## Finding your way

[Sites](sites/index.md)
: Where the hardware is: Welland (South Australia) and PS1 (Chicago). Network,
  gateway, switches, which host carries which board, and the faults known on
  each host.

[Boards](boards/index.md)
: Each FPGA board type: specification, wiring to its Raspberry Pi, how to
  program it, and how to check the wiring.

[Setup](setup/index.md)
: How the platform works: netboot and the NFS root, the network, what runs on
  the Pi hosts and on the gateway, and the web application.

[Repositories](repositories.md)
: What each repository is responsible for, what it publishes and where it
  runs.

```{toctree}
:maxdepth: 2
:caption: Contents

sites/index
boards/index
setup/index
repositories
packages
contributing
```

## Where the code lives

The systems described here have their own repositories under the
[fpgas-online](https://github.com/fpgas-online) organisation.
[Repositories](repositories.md) lists every one, with what it is responsible
for and what it publishes.
