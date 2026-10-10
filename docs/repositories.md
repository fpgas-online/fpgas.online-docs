---
type: reference
owner: documentation maintainers
reader: someone who wants to know which repository holds what
review: 2026-11-10
---

# Repositories

This page says what each fpgas.online repository is responsible for, what it publishes, and where it runs. It is for
someone looking for the repository that holds a thing. How to build and test a repository is in its own README.
The repositories are in the [fpgas-online](https://github.com/fpgas-online) organisation unless the name says
otherwise.

In each table, Repository links the repository and Responsible for says what it holds. Publishes is what its CI
makes, and Runs on is where that ends up. How the packages reach a host is on [Packages](packages.md).

## The site: gateway and web tier

| Repository | Responsible for | Publishes | Runs on |
|---|---|---|---|
| [fpgas.online-infra](https://github.com/fpgas-online/fpgas.online-infra) | Ansible playbooks, inventory and roles for a whole site: the gateway (DHCP, TFTP, NFS, nginx, the web application, camera relay, web terminal) and the Pi NFS root, which is built on the gateway rather than configured on running Pis. Its CI boots an emulated fleet against a real gateway build. See [The gateway host](setup/gateway.md) and [Netboot](setup/netboot.md) | nothing; it deploys | the operator's machine, against the gateway |
| [fpgas.online-site](https://github.com/fpgas-online/fpgas.online-site) | The Django web application: the board list, each board's page, bitstream upload, the web terminal, power buttons, and the Tiny Tapeout site. See [The web application](setup/webapp.md) | no package; `fpgas.online-infra` deploys it from the repository | the gateway |
| [fpgas.online-poe](https://github.com/fpgas-online/fpgas.online-poe) | Switching PoE ports off and on over SNMP: a Python library, the Django views behind the power buttons, and command-line tools | no package; `fpgas.online-infra` deploys it from the repository | the gateway |
| [fpgas.online-gw](https://github.com/fpgas-online/fpgas.online-gw) | The gateway's board-access service: board inventory, status, power, serial and events over HTTP, so a web front end never touches the Pi network, the switch credentials or redis | no package yet | written to run on the gateway |
| [fpgas.online-e2e-tests](https://github.com/fpgas-online/fpgas.online-e2e-tests) | Browser tests that use the live sites as a visitor does: open board pages, press the buttons, type in the web terminal, watch the camera, upload a bitstream. Needs no secrets | nothing | CI, or any machine with a browser |
| [nfsroot-watchdog](https://github.com/fpgas-online/nfsroot-watchdog) | Rebooting NFS-root machines whose root changed underneath them, one at a time and only once the update is finished | Debian packages `nfsroot-watchdog` (client) and `nfsroot-watchdog-server`, in its own signed apt repository | the gateway (server) and the Pis (client) |
| [fpgas-online.github.io](https://github.com/fpgas-online/fpgas-online.github.io) | The landing page at <https://fpgas.online>. Static HTML, no build step | GitHub Pages | GitHub |
| [sshpiper](https://github.com/fpgas-online/sshpiper) | A fork of sshpiper, an ssh reverse proxy, kept for reaching a board by its own name ([infra issue #191](https://github.com/fpgas-online/fpgas.online-infra/issues/191)) | nothing | not deployed |
| [fpgas.online-api](https://github.com/fpgas-online/fpgas.online-api) | A public HTTPS API for leasing a board, uploading, running commands and reading the camera. **Design only: there is no code yet** | nothing yet | not deployed |

## On the Pi hosts

| Repository | Responsible for | Publishes | Runs on |
|---|---|---|---|
| [fpgas.online-setup-pi](https://github.com/fpgas-online/fpgas.online-setup-pi) | What makes a bare Pi an fpgas.online host: shell environment, board detection, status reporting, network interface naming. See [The Pi hosts](setup/pi.md) | Debian package `fpgas-online-setup-pi` | every Pi |
| [fpgas.online-cam](https://github.com/fpgas-online/fpgas.online-cam) | Capturing the Pi's camera and streaming it to the gateway, so a visitor can watch the board | Debian package `fpgas-online-cam` | every Pi with a camera |
| [fpgas.online-fpga-tools](https://github.com/fpgas-online/fpgas.online-fpga-tools) | A maintained patch series on openFPGALoader and OpenOCD for what is not upstream yet (JTAG through the Pi 5's RP1, NeTV2, the Tiny Tapeout FPGA board), built as packages and static binaries | its own signed apt repository, separate from `apt.fpgas.online`, and static binaries on GitHub Releases | Pis that program an FPGA board |
| [mithro/rp1-jtag](https://github.com/mithro/rp1-jtag) | The library and drivers for fast JTAG through the Raspberry Pi 5's RP1 chip. Development only: installable builds come from `fpgas.online-fpga-tools` | nothing | Pi 5 hosts, through the tools above |
| [mithro/rpi-hwid](https://github.com/mithro/rpi-hwid) | Identifying a Pi and what is attached to it (model, serial, MAC addresses, HAT, power source), and printing the labels that go on the hardware | PyPI and Debian packages | a Pi, or an operator's machine over ssh |

## FPGA designs and verification

| Repository | Responsible for | Publishes | Runs on |
|---|---|---|---|
| [fpgas.online-test-designs](https://github.com/fpgas-online/fpgas.online-test-designs) | The test designs for every board and `fpgas-verify`, the check that proves a board is wired and working. Also the source of the wiring sheets on the board pages here. See [Verification](setup/verification.md) | Debian packages (the check and its bitstreams) | CI builds; the Pis run the check |
| [fpgas.online-vivado-runners](https://github.com/fpgas-online/fpgas.online-vivado-runners) | Sandboxed, one-job-each GitHub Actions runners with Vivado, for the designs the open toolchains cannot build. **Designed, not deployed** | nothing yet | a KVM host |
| [migen](https://github.com/fpgas-online/migen) | A mirror of migen that builds it as the Debian package `python3-migen` | signed apt repository at <https://fpgas.online/migen/> | CI |

## Tiny Tapeout

| Repository | Responsible for | Publishes | Runs on |
|---|---|---|---|
| [fpgas.online-tt](https://github.com/fpgas-online/fpgas.online-tt) | The daemon on the Pi that owns a Tiny Tapeout demo board's USB serial port and shares it with browsers over a WebSocket. See [Tiny Tapeout](setup/tinytapeout.md) | Debian package `fpgas-online-tt` | Pis with a Tiny Tapeout board |
| [tt-commander-app](https://github.com/fpgas-online/tt-commander-app) | A fork of the Tiny Tapeout Commander that adds a WebSocket transport and an embeddable build. Its default branch is `fpgas-online` | the bundle the site embeds | visitors' browsers |
| [tinytapeout-fpga-demos](https://github.com/fpgas-online/tinytapeout-fpga-demos) | The curated demo designs for the FPGA emulation boards, built in CI, with the index the board page's picker reads | Debian package `fpgas-online-tt-demos` | Pis with a Tiny Tapeout FPGA board |
| [tinytapeout-demoboard-to-raspi](https://github.com/fpgas-online/tinytapeout-demoboard-to-raspi) | The adapter board that brings a demo board's I/O to the Pi's ribbon cable while leaving the Pmods usable | board design files | hardware |

## Shared infrastructure

| Repository | Responsible for | Publishes | Runs on |
|---|---|---|---|
| [apt](https://github.com/fpgas-online/apt) | The package repository. It pulls each source repository's published packages on a schedule; no source repository holds a token for it. See [Packages](packages.md) | <https://apt.fpgas.online> | GitHub Pages |
| [rpi-qemu](https://github.com/fpgas-online/rpi-qemu) | A patched QEMU whose Raspberry Pi 4B has working Ethernet, so a Pi can netboot in emulation. It is what lets `fpgas.online-infra` test a site in CI without hardware | packages for CI | CI |
| [fpgas.online-mechanical](https://github.com/fpgas-online/fpgas.online-mechanical) | Dimensioned drawings of the boards, adapters and accessories, and the plates and drill templates that mount them, including camera mounts | drawings | not deployed |
| [fpgas.online-docs](https://github.com/fpgas-online/fpgas.online-docs) | This site. See [Contributing](contributing.md) | <https://docs.fpgas.online> | Read the Docs |
| [.github](https://github.com/fpgas-online/.github) | The organisation's profile page on GitHub | the profile | GitHub |
| [todo](https://github.com/fpgas-online/todo) | An issue tracker for work that belongs to no single repository | issues | GitHub |

## Older repositories

These predate the Ansible-built NFS root and are kept for reference.

| Repository | What it was for |
|---|---|
| [fpgas.online-netboot-pi](https://github.com/fpgas-online/fpgas.online-netboot-pi) | Scripts that turned a Raspberry Pi OS card image into an NFS root by hand. `fpgas.online-infra` builds the root now |
| [fpgas.online-tools](https://github.com/fpgas-online/fpgas.online-tools) | Stand-alone diagnostic scripts, mostly for reading DHCP traffic and logs |
