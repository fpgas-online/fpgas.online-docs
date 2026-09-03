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

```{toctree}
:maxdepth: 2
:caption: Contents

sites/index
boards/index
setup/index
packages
contributing
```

## Where the code lives

The systems described here have their own repositories under the
[fpgas-online](https://github.com/fpgas-online) organisation. The main ones:

`fpgas.online-infra`
: Ansible for the gateway servers and the Raspberry Pi NFS root.

`fpgas.online-test-designs`
: FPGA designs that verify a board is wired up correctly.

`fpgas.online-site`
: The Django web application, including the Tiny Tapeout catalogue.

`fpgas.online-tt`, `tinytapeout-fpga-demos`, `tt-commander-app`
: The Pi-side Tiny Tapeout bridge daemon, the demo bitstreams, and the
  browser Commander it serves.

`fpgas.online-setup-pi`, `fpgas.online-cam`, `fpgas.online-poe`
: Packages installed on the Pi hosts and the PoE switch control library.

`apt`
: The package repository at <https://apt.fpgas.online>. See [Packages](packages.md).
