# fpgas.online

FPGA hardware you can reach over the internet: Raspberry Pi hosts with FPGA
boards attached, wired up so a design can be built, loaded and driven remotely.

:::{note}
These pages describe live infrastructure, so they track the current state
rather than a released version. Where a page records a measurement, it says
when it was taken.
:::

## I want to use a board from the website

The boards are used from the public sites, not from these pages:

<https://welland.fpgas.online>
: The welland site, in South Australia: Arty A7, NeTV2, Fomu, Acorn and
  Tiny Tapeout boards.

<https://tinytapeout.fpgas.online>
: The Tiny Tapeout boards: the demo boards with their chips, and the FPGA
  demo boards.

<https://ps1.fpgas.online>
: The PS1 site, at Pumping Station: One in Chicago: Arty A7 boards on Raspberry
  Pis, and Acorn cards on Compute Blades.

Each board type's own page under [Boards](boards/index.md) says what is on the
board and how it is wired to its Raspberry Pi.

## I want to set up a Raspberry Pi and a board at my bench

Start at the board's page under [Boards](boards/index.md). For an Acorn, the
[Acorn page](boards/acorn/index.md) gives a step-by-step guide for each
carrier: a Raspberry Pi 5 with an M.2 HAT, or a Compute Blade. When it is
wired, [fpgas-verify](verify/fpgas-verify.md) checks the board from its
Raspberry Pi, and needs no fpgas.online infrastructure.

## I want to know what a repository is for

See [where the code lives](#where-the-code-lives), below.

## I keep the infrastructure running

[Sites](sites/index.md)
: Where the hardware is: Welland (South Australia) and PS1 (Chicago). Network,
  gateway, switches, which host carries which board, and the faults known on
  each host.

[Setup](setup/index.md)
: How the platform works: netboot and the NFS root, the network, what runs on
  the Pi hosts and on the gateway, and the web application.

[Packages](packages.md), [Contributing to these docs](contributing.md) and
[Open items on these pages](open-items.md) are in the contents in the sidebar.

```{toctree}
:hidden:
:maxdepth: 2
:caption: Contents

sites/index
boards/index
setup/index
verify/fpgas-verify
packages
contributing
open-items
```

(where-the-code-lives)=
## Where the code lives

The systems described here have their own repositories under the
[fpgas-online](https://github.com/fpgas-online) organisation. The main ones:

[fpgas.online-infra](https://github.com/fpgas-online/fpgas.online-infra)
: Ansible for the gateway servers and the Raspberry Pi NFS root.

[fpgas.online-test-designs](https://github.com/fpgas-online/fpgas.online-test-designs)
: FPGA designs that verify a board is wired up correctly, and the generated
  wiring and building pages.

[fpgas.online-site](https://github.com/fpgas-online/fpgas.online-site)
: The Django web application, including the Tiny Tapeout catalogue.

[fpgas.online-tt](https://github.com/fpgas-online/fpgas.online-tt), [tinytapeout-fpga-demos](https://github.com/fpgas-online/tinytapeout-fpga-demos), [tt-commander-app](https://github.com/fpgas-online/tt-commander-app)
: The Pi-side Tiny Tapeout bridge daemon, the demo bitstreams, and the
  browser Commander it serves.

[fpgas.online-setup-pi](https://github.com/fpgas-online/fpgas.online-setup-pi), [fpgas.online-cam](https://github.com/fpgas-online/fpgas.online-cam), [fpgas.online-poe](https://github.com/fpgas-online/fpgas.online-poe)
: Packages installed on the Pi hosts, the camera feeds, and the PoE switch
  control library.

[fpgas.online-docs](https://github.com/fpgas-online/fpgas.online-docs)
: These pages. Pages owned by another repository are copied in from it; the
  page says so at its top.

`apt`
: The package repository at <https://apt.fpgas.online>. See [Packages](packages.md).

```{toctree}
:hidden:

verify/identity
verify/goals
```
