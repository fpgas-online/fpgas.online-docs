# What works and what is planned

This page says, area by area, what a visitor can use today, what is being
worked on, and what is planned but not started. Each statement carries the date
it was last checked. For the hardware itself see [Sites](sites/index.md) and
[Boards](boards/index.md).

:::{note}
Last reviewed 2026-10-04. A board appears on a site's board list only once it
has passed `fpgas-verify`, so the live list at
[welland.fpgas.online](https://welland.fpgas.online) is always the authority on
what is usable right now.
:::

## Sites

| Site | State (2026-10-04) |
|---|---|
| [welland.fpgas.online](https://welland.fpgas.online) | Running. The board list is built from what the Pis register and what verify reports; nothing is listed by hand |
| [tinytapeout.fpgas.online](https://tinytapeout.fpgas.online) | Running. Still lists its boards from a fixed table, so it shows boards that are powered off |
| [ps1.fpgas.online](https://ps1.fpgas.online) | A second site, run separately. See [PS1](sites/ps1.md) |

## Boards at Welland

| Board | Works (2026-10-04) | In progress | Planned |
|---|---|---|---|
| [SQRL Acorn CLE-215+](boards/acorn/index.md) on a Raspberry Pi 5 | Boards carrying the fpgas.online image pass every verify test (PCIe link and register access, JTAG through the Pi's RP1, flash, DDR3, the P2 UART and GPIO) and are listed on the site | Converting the remaining boards from the factory image, which can be done over JTAG; bringing every bootloader to one version; camera focus, which is lost at power-off until the lens driver is enabled; labels | A drawn camera position; a bootloader that is locked after boot and upgraded only from a service port |
| [Tiny Tapeout FPGA demo board](boards/tt-fpga.md) | Reachable on tinytapeout.fpgas.online: pick a demo, drive it from the browser | Passing verify, which they fail today. The pin check expects the mirror image of the cabling actually fitted, which is a fault in the test, not the wiring. The SPI flash check fails for a reason not yet known. Cameras are out of focus | Listing on welland.fpgas.online as well |
| [Tiny Tapeout ASIC demo boards](boards/tt-asic.md) | Listed on tinytapeout.fpgas.online, but their hosts are powered off | Getting the hosts powered again, which needs someone at the rack | A verify check for ASIC boards; none exists yet |
| [Arty A7](boards/arty-a7.md) | Not listed: the hosts fail verify | Finding which hosts carry Arty boards and what each fails | Ethernet, the Linux demo, and everything else that worked before |
| [NeTV2](boards/netv2.md) | Not listed: the hosts fail verify | Board verification | HDMI in and out, HDCP, USB |
| [Fomu EVT](boards/fomu-evt.md) | One host passes verify | | More Fomu hosts |
| [ButterStick](boards/butterstick.md), [ULX3S](boards/ulx3s.md), other ECP5 boards and other PCIe Xilinx cards | Not deployed | | New board types, in no fixed order |

## What a visitor can do

| Function | State (2026-10-04) |
|---|---|
| See the boards and watch their cameras | Works |
| Web terminal on a board's page | Works |
| Upload a bitstream from the board's page | Fixed in September 2026; not re-checked since the board list changed to registration |
| Restart a board's Pi by PoE from its page | Fixed in September 2026; not re-checked since the board list changed to registration |
| ssh to a board | Works by jumping through the gateway: see [Accounts and logins](setup/access.md). ssh by board name is designed and not built |
| Reach a board directly over IPv6 | Planned. IPv6 reaches the gateway today |
| Ask for exclusive use of a board from an automated system | Planned. The design is in [fpgas.online-api](https://github.com/fpgas-online/fpgas.online-api); there is no code |

## Platform

| Area | Works (2026-10-04) | Planned |
|---|---|---|
| Netboot | Any Pi plugged into a fleet switch port netboots a shared read-only root and registers itself | Rebooting Pis whose root changed underneath them, automatically |
| Operating system | The Welland gateway runs Debian 13 (trixie); the Pi root is still Debian 12 (bookworm) | Trixie on the Pis |
| Verification | `fpgas-verify` runs at boot and gates the board list. See [Verification](setup/verification.md) | A check for every board type, covering all of each board's functions |
| Test designs | Built by the open toolchains in CI and published as packages | Every Xilinx design also built by Vivado, on self-hosted runners that are designed and not deployed; interactive designs (a Wishbone bridge, LEDs driven from the web page, booting MicroPython, Zephyr and Linux) |
| Operations | | An admin page showing which devices are seen and their state; usage tracking |
| Setting up a new site | Welland and PS1 are documented as built | Step-by-step instructions, including what a site needs from the network it sits behind |

## Where the work is tracked

Each repository's issues and pull requests are the record of work in progress:
see [Repositories](https://github.com/fpgas-online). Issues about these pages
are in [fpgas.online-docs](https://github.com/fpgas-online/fpgas.online-docs/issues).
