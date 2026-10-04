# What works and what is planned

This page says, area by area, what a visitor can use today, what is being
worked on, and what is planned but not started. Each statement carries the date
it was last checked. For the hardware itself see [Sites](sites/index.md) and
[Boards](boards/index.md).

:::{note}
Last reviewed 2026-10-04. A board appears on
[welland.fpgas.online](https://welland.fpgas.online) only once it has passed
`fpgas-verify`, so that live list is the authority on what is usable there
right now. tinytapeout.fpgas.online does not work that way yet: see below.
:::

## Sites

| Site | State (2026-10-04) |
|---|---|
| [welland.fpgas.online](https://welland.fpgas.online) | Running. The board list is built from what each Pi reports about itself and from its verify result; nothing is listed by hand |
| [tinytapeout.fpgas.online](https://tinytapeout.fpgas.online) | Running. Still lists its boards from a hand-written list, so it shows boards whose hosts are powered off |
| [ps1.fpgas.online](https://ps1.fpgas.online) | A second site, run separately. See [PS1](sites/ps1.md) |

## Boards at Welland

| Board | Works (2026-10-04) | In progress | Planned |
|---|---|---|---|
| [SQRL Acorn CLE-215+](boards/acorn/index.md) on a Raspberry Pi 5 | Some boards pass every verify test (PCIe link and register access, JTAG through RP1, the Pi 5's I/O chip, flash, DDR3, and the UART and GPIO on the Acorn's P2 connector) and are listed on the site. Others run the same image but fail verify on a cable fault, so they are hidden | Fixing those cable faults, which needs someone at the rack. Some positions deliver no power, and a board has not been located. Bringing every bootloader to one version. Camera focus, which is lost at power-off until the lens driver is enabled. Labels. A drawn camera position, under review | A bootloader that is locked after boot and upgraded only from a service port |
| [Tiny Tapeout FPGA demo board](boards/tt-fpga.md) | The powered hosts answer on tinytapeout.fpgas.online; a host is unpowered. Whether a demo runs end to end was not checked on this date | Passing verify, which they fail today. The pin check expects the mirror image of the cabling actually fitted, which is a fault in the test, not the wiring. The SPI flash check fails because the FPGA breakout has no SPI flash, which the test and its documentation assumed it had ([fpgas.online-test-designs PR #114](https://github.com/fpgas-online/fpgas.online-test-designs/pull/114) removes the test). The cameras are out of focus | Listing on welland.fpgas.online as well |
| [Tiny Tapeout ASIC demo boards](boards/tt-asic.md) | Nothing: the hosts are powered off. tinytapeout.fpgas.online still lists them, and their status requests time out | Needs someone at the rack to restore power | A verify check for ASIC boards; none exists yet |
| [Arty A7](boards/arty-a7.md) | Not listed: every host fails verify. UART, DDR3 and SPI flash pass; Ethernet passes on some hosts | The cabling between the Pi's HAT and the Arty's Pmod expansion connectors is not what the documented wiring says, and a host differs from the rest; which cabling is intended has to be settled before the pin check can pass. Where Ethernet fails, in one case the test gives up before the link comes up ([fpgas.online-test-designs PR #115](https://github.com/fpgas-online/fpgas.online-test-designs/pull/115) fixes the test); another is not yet explained | The Linux demo, which verify does not check yet, and everything else that worked before |
| [NeTV2](boards/netv2.md) | Not listed. Verify stops with an error on every Raspberry Pi 3 host because of a bug in `fpgas-verify`, so what the board tests would report is not yet known. The Raspberry Pi 5 hosts with a NeTV2 do not netboot and need work at the rack | Fixing that bug ([fpgas.online-test-designs PR #112](https://github.com/fpgas-online/fpgas.online-test-designs/pull/112)) | HDMI in and out, HDCP, USB |
| [Fomu EVT](boards/fomu-evt.md) | Passed verify and was listed until the morning of 2026-10-04; not listed now | The same Raspberry Pi 3 bug stops verify. Separately, the Fomu did not show on the host's USB; why is being looked at | More Fomu hosts |
| Other PCIe Xilinx cards | Not listed. Hosts carrying a PCIe Screamer and a card running an XDMA design are powered, and fail verify because there is no test design for them | | A test design for each |
| [ButterStick](boards/butterstick.md), [ULX3S](boards/ulx3s.md) and other ECP5 boards | Not deployed | | New board types, in no fixed order |
| [Orange Pi PC](setup/orange-pi.md) hosts | They boot unattended; several stop responding after some time up | Finding out why | |

## What a visitor can do

| Function | State (2026-10-04) |
|---|---|
| See the boards and watch their cameras | Works. Most cameras are not yet in focus (see the board table) |
| Web terminal on a board's page | Worked in September 2026; not re-checked since the board list changed |
| Upload a bitstream from the board's page | Fixed in September 2026; not re-checked since the board list changed |
| Restart a board's Pi by PoE from its page | Fixed in September 2026; not re-checked since the board list changed |
| ssh to a board | Works with the gateway as a jump host (used on this date): see [Accounts and logins](setup/access.md). ssh by board name is designed and not built |
| Reach a board directly over IPv6 | Planned. IPv6 reaches the gateway today |
| Ask for exclusive use of a board from an automated system | Planned. Only a design exists, in [fpgas.online-api](https://github.com/fpgas-online/fpgas.online-api) |

## Platform

| Area | Works (2026-10-04) | In progress or planned |
|---|---|---|
| Netboot | A Pi on a powered fleet switch port netboots a shared root that resets on every boot, and reports itself to the site. Some ports are unpowered or hold a host that does not boot | A watchdog that finds dead hosts and power-cycles them, under review |
| Operating system | The Welland gateway runs Debian 13 (trixie); the Pi root is still Debian 12 (bookworm) | Trixie on the Pis |
| Verification | `fpgas-verify` runs at boot and decides what welland.fpgas.online lists. See [Verification](setup/verification.md) | A check for every board type, covering all of each board's functions |
| Test designs | Built by the open toolchains in CI and published as packages | Every Xilinx design also built by Vivado, on self-hosted runners that are designed and not deployed; interactive designs (a Wishbone bridge, LEDs driven from the web page, booting MicroPython, Zephyr and Linux) |
| Operations | | An admin page showing which devices are seen and their state; usage tracking |
| Setting up a new site | Welland and PS1 are documented as built | Step-by-step instructions, including what a site needs from the network it sits behind |
| Documentation | These pages; drawn wiring sheets for the Acorn | Drawn wiring sheets for the other boards; pages kept in step with the repositories they describe |

## Where the work is tracked

Each repository's issues and pull requests are the record of work in progress:
see [Repositories](https://github.com/fpgas-online). Issues about these pages
are in [fpgas.online-docs](https://github.com/fpgas-online/fpgas.online-docs/issues).
