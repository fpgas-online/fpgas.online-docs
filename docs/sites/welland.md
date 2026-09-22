# Welland

The private test lab in South Australia, published as
[welland.fpgas.online](https://welland.fpgas.online). Raspberry Pi 5 hosts, each
with a SQRL Acorn board on an M.2 HAT (older notes say mPCIe HAT), plus a camera
pointed at the board; alongside them Arty A7, NeTV2, Fomu and Tiny Tapeout hosts
on their own Pis.

## Network

```
                          ┌────────────────────────────────────┐
                          │  tweed.welland.mithis.com          │
Internet ─── eth-uplink ──│  Debian 13 (trixie)                │
 (10.99.21.2, via ten64)  │  x86_64, kernel 6.12.105           │
                          │  Intel Core i5-3610ME              │
                          │                                    │
                          │  dnsmasq (DHCP/DNS/TFTP/PXE)       │
              eth-local ──│  10.21.0.1/16, one VLAN per port   │
        (GSM7252PS "sw1"  │  domain: fpgas.welland.mithis.com  │
         + S3300 "sw2")   └───────────┬────────────────────────┘
                                      │
        ┌──────────────┬──────────────┼──────────────┬──────────────┐
        │              │              │              │              │
  ┌─────┴─────┐  ┌─────┴─────┐  ┌─────┴─────┐  ┌─────┴─────┐  ┌─────┴─────┐
  │ RPi 4/3B+ │  │ RPi 3B+   │  │ RPi 5     │  │ RPi 4/3B+ │  │ RPi 4     │
  │ +Arty A7  │  │ +NeTV2    │  │ +M.2 HAT  │  │ +TT ASIC  │  │ +TT FPGA  │
  │ +PMOD HAT │  │ (GPIO     │  │ +Acorn    │  │ demo board│  │ Demo Board│
  │ +USB Eth  │  │  JTAG)    │  │  CLE-215+ │  │ +PMOD HAT │  │ +PMOD HAT │
  └───────────┘  └───────────┘  └───────────┘  └───────────┘  └───────────┘
   (sw2 p38 +…)   (sw1 ×5)      (sw2 ×6)       (sw2 p3–p8)     (sw2 p33–36)
                                            + Fomu EVT on sw1 p17
```

Every Raspberry Pi netboots over PXE/TFTP from tweed. Since **2026-08-23** the
site runs the **VLAN-per-port** scheme
([fpgas.online-infra PR #10](https://github.com/fpgas-online/fpgas.online-infra/pull/10)):
every Pi-facing switch port is an untagged access port in its own VLAN, tweed
isolates Pi↔Pi traffic with nftables, and a Pi's identity comes from the port it
is plugged into rather than from its MAC.

| Switch (index)                    | Mgmt IP    | Role                                                       |
|-----------------------------------|------------|------------------------------------------------------------|
| Netgear GSM7252PS-s2 (**sw1**)    | 10.1.5.23  | Head switch: tweed eth-local on 1/0/47, eth-uplink on 1/0/48 |
| Netgear S3300-52X-PoE+ (**sw2**)  | 10.1.5.11  | Downstream via GSM 1/0/50 ↔ S3300 1/xg51; carries the TT and Acorn boards |

The formulas that turn a switch index and port number into a VLAN, an address
and a hostname are in [Network and power](../setup/network.md); the gateway is
10.21.0.1. Moving a Pi to another port renames and re-addresses it. The old flat
`piNN` / `10.21.0.1NN` names are retired; the "Old name" columns below map them.
On the S3300, Tim's rule is **port N carries Tiny Tapeout N** (ports 1–10), the
TT FPGA emulation boards sit on 33–36, and the Acorn Pi 5s on 29 and 43–48.

Source: the `switches:` block and the `tt_boards` catalogue in
`ansible/inventory/host_vars/fpgas.online.yml` (fpgas.online-infra), the
switches' LLDP tables, and live probes of the hosts below on 2026-09-03.

## Gateway: tweed

| Property   | Value                                                                                |
| ---------- | ------------------------------------------------------------------------------------ |
| Role       | Network gateway, DHCP/DNS/TFTP/PXE server, NFS root server, web tier (welland.fpgas.online + tinytapeout.fpgas.online) |
| Hardware   | Intel Core i5-3610ME (3rd Gen, QM77 chipset)                                         |
| OS         | Debian 13 (trixie) — fresh install 2026-08-30                                        |
| Kernel     | 6.12.105+deb13-amd64                                                                 |
| eth-uplink | 10.99.21.2/30 + 2404:e80:a137:9921::2/126, point-to-point to ten64 (10.99.21.1), which publishes tweed's web names |
| eth-local  | 10.21.0.1/16 trunk to the switches (per-port VLAN sub-interfaces)                    |
| Domain     | `fpgas.welland.mithis.com`                                                             |
| PCI        | 2× Intel 82574L GbE, Tundra PCI bridge, Matrox G200eW                                |
| NFS roots  | `/srv/nfs/rpi/bookworm/{boot,root}` (armhf + arm64 kernels, `overlayroot=tmpfs`); apt packages `fpgas-online-setup-pi` 0.0.post62, `fpgas-online-tt` 0.0.post52, `fpgas-online-tt-demos` 0.0.post21, `fpgas-online-cam` 0.0.post45, `openfpgaloader-rp1pio` and `openocd-rp1pio` 0.0.post76 |

Tweed hosts no FPGA boards itself. Reach it as the `ansible` user on the uplink
address 10.99.21.2, from ten64 (verified 2026-09-03).

:::{note}
The public name `tweed.welland.mithis.com` resolves to ten64's reverse proxy, so
ssh to that name does not reach tweed. Use the 10.99.21.2 uplink address.
:::

The Pis are not routable from outside tweed — with per-port VLANs they do not
even answer pings from ten64 — so jump through it:

```console
$ ssh -o ProxyCommand='ssh -W %h:%p ansible@10.99.21.2' pi@10.21.2.29
```

The old restricted `pi@tweed.welland.mithis.com` jump account (rbash) did not
survive the 2026-08-30 reinstall: `getent passwd pi` is empty there, and only
`ansible`, `carl`, `piroot`, `tim` and `videoteam` remain.

**Public access** for end users: `ssh pi@fpgas.mithis.com -p 13422` is
port-forwarded to individual Pis.

:::{todo}
The infra `host_vars/fpgas.online.yml` sets `time_zone: America/Los_Angeles`
for a gateway that stands in South Australia. Every timestamp tweed writes is
therefore in Californian local time. Nobody has recorded whether that is
deliberate (the fleet is administered from Chicago) or a copy-paste from the
PS1 host_vars.
:::

## Hosts and boards

The Acorn, Tiny Tapeout ASIC and Tiny Tapeout FPGA sections were re-verified
live on 2026-09-03 under the VLAN-per-port scheme, and the NeTV2 section on
2026-09-06. The Arty A7 and Fomu sections still carry the pre-cutover names and
addresses from the 2026-03-17 survey; their `Switch Port` values are the old
flat port numbers, which did not carry a switch index, so they are written `p7`
rather than `sw1 p7` — and `p7` in the stale Arty table is not the `sw2 p7` that
now carries TT07.

:::{todo}
Re-probe the Arty and Fomu hosts under the VLAN-per-port scheme and replace the
2026-03-17 rows below with measured ones. The NeTV2 section was re-probed
2026-09-06.
:::

:::{todo}
`https://welland.fpgas.online/fpgas/pi37.html` and `/fpgas/pi42.html` both serve
pages, but no table here has a host on sw2 p37 or p42 (checked 2026-09-03).
`/fpgas/pi16.html` also answers, although pi16 appears here only as a retired
NeTV2 name. Either these are hosts nobody has documented, or they are stale
pages the site should stop serving.
:::

Programming commands for each board type live on the board pages; see
[Boards](../boards/index.md).

### Infrastructure host

Surveyed 2026-03-17.

```{rst-class} nowrap
```

| Host | Switch Port | IP (retired) | RPi MAC           | RPi Model   | Role                                         |
| ---- | ----------- | ------------ | ----------------- | --------------- | -------------------------------------------- |
| pi1  | p1          | 10.21.0.101  | b8:27:eb:ec:c2:c9 | RPi 3B+ 1 GB     | Always-on NFS maintenance system (RW access) |

:::{note}
This address no longer resolves. This host has not been located on the new
scheme.
:::

### Arty A7-35T

Surveyed 2026-03-17. Five boards, on RPi 4 / 3B+ hosts with PMOD HATs.

```{rst-class} nowrap
```

| Host | Switch Port | IP (retired) | RPi MAC           | RPi Model   | Arty Serial         | Arty DNA           | USB Ethernet                     | Serial Devices   |
| ---- | ----------- | ------------ | ----------------- | --------------- | ------------------- | ------------------ | -------------------------------- | ---------------- |
| pi7  | p7          | 10.21.0.107  | e4:5f:01:96:f8:a5 | RPi 4 2 GB       | 210319B301DE        | 0x00628502251ea85c | ASIX AX88179 (f8:e4:3b:0f:c1:e6) | ttyUSB0, ttyUSB1 |
| pi9  | p9          | 10.21.0.109  | b8:27:eb:86:39:63 | RPi 3B+ 1 GB     | (FTDI disconnected) | —                  | Apple Eth (48:d7:05:e9:40:52)    | **none**         |
| pi11 | p11         | 10.21.0.111  | e4:5f:01:8d:f7:17 | RPi 4 8 GB       | 210319B3E5C5        | 0x002c8d02251ea854 | DM9601 (00:e0:4c:53:44:58)       | ttyUSB0, ttyUSB1 |
| pi13 | p13         | 10.21.0.113  | b8:27:eb:6d:27:f6 | RPi 3B+ 1 GB     | 210319A43ADB        | 0x0002f54832290854 | ASIX (8a:ce:4c:ff:ae:83)         | ttyUSB0, ttyUSB1 |
| pi26 | p26         | 10.21.0.126  | e4:5f:01:97:1f:7e | RPi 4 2 GB       | 210319B0C238        | 0x0144cd2a47442854 | Linksys GbE (60:38:e0:e3:56:4f)  | ttyUSB0, ttyUSB1 |

:::{note}
The 2026-08-30 hardware inventory sheet places the Arty `210319B3E5C5` (was
pi11) at sw2 p38. These addresses no longer resolve; derive the current name and
address from the switch port using [Network and power](../setup/network.md).
:::

Each RPi also carries a separate USB Ethernet adapter wired to the Arty's
Ethernet port for network testing. See [Arty A7](../boards/arty-a7.md) for the
FTDI interfaces and serial paths.

Source: `lsusb` and `ls /dev/serial/by-id/` on each RPi, dnsmasq pibs.conf.

### NeTV2

Re-verified live 2026-09-06 under the VLAN-per-port scheme. **Five** boards on
RPi 3B+ hosts with GPIO JTAG, all five online — including **pi-sw1-p18**, which
earlier surveys had as offline. Each is on switch 1 at the port in its name,
`10.21.1.<port>`, and all five netboot the shared bookworm NFS root reliably.

```{rst-class} nowrap
```

| Host | Switch Port | IP | RPi MAC | FPGA | FPGA DNA | JTAG detect | Old name |
| ---- | ----------- | -- | ------- | ---- | -------- | ----------- | -------- |
| pi-sw1-p10 | sw1 p10 | 10.21.1.10 | b8:27:eb:e3:e7:e4 | XC7A35T | 0x2a11a4c662251c6f | `0x0362d093` OK | pi10 |
| pi-sw1-p12 | sw1 p12 | 10.21.1.12 | b8:27:eb:eb:5d:bf | XC7A35T | 0x3a11a4c662372a6b | `0x0362d093` OK | pi12 |
| pi-sw1-p14 | sw1 p14 | 10.21.1.14 | b8:27:eb:e3:7c:3c | XC7A35T | 0x3a11dcc864222e93 | `0x0362d093` OK | pi14 |
| pi-sw1-p16 | sw1 p16 | 10.21.1.16 | b8:27:eb:c6:29:79 | XC7A35T | 0x2a11a4c662372a53 | `0x0362d093` OK | pi16 |
| pi-sw1-p18 | sw1 p18 | 10.21.1.18 | b8:27:eb:2c:e8:de | XC7A35T | 0x3a11dcc864241c0b | `0x0362d093` OK | pi18 |

The RPi models and DNAs are carried forward from the 2026-03-17 survey; the
MACs, addresses, reachability and the **JTAG detect** column are the 2026-09-06
re-probe. Every node enumerated its NeTV2's Artix-7 XC7A35T (`idcode
0x0362d093`, IR length 6) over GPIO bit-bang JTAG with
`sudo openFPGALoader --cable libgpiod --pins 27:22:4:17 --detect`. The FPGA DNA
(a different identifier from the JTAG IDCODE) was not re-read.

No USB serial devices: the NeTV2 uses GPIO UART on `/dev/serial0` (which is
`ttyAMA0` on these netboot images), and JTAG is bit-banged on the Pi's GPIO
header. See [Kosagi NeTV2](../boards/netv2.md).

:::{warning}
**The kernel must not act on bytes from the FPGA's UART.** On a Pi 3B+ the
serial console pin is the one the NeTV2's FPGA drives, and a design that
transmits on it feeds the kernel bytes it reads as SysRq `reboot`, `crash` or
`poweroff`. The netboot `cmdline.txt.j2` sets no serial console, and a sysctl
drop-in sets `kernel.sysrq = 0`; with both, a node loaded with a serial-driving
bitstream stays up (checked on all five). Leaving `console=serial0` off alone is
not enough, because the device tree's `stdout-path` still registers `ttyAMA0`:
`kernel.sysrq = 0` is the protection that matters.
:::

Access is over GPIO JTAG and GPIO UART only; there is no per-Pi web page for
these hosts yet, and they are not listed on
[welland.fpgas.online](https://welland.fpgas.online) (see the Web application
todo). Reach one through the gateway, e.g. from this workstation over the
`wg-desktop` route: `ssh -J tim@tweed.welland.mithis.com pi@10.21.1.14` (the
`pi` user has passwordless sudo; `root` is not authorised). From ten64 use the
`ansible@10.99.21.2` jump described under [Gateway: tweed](#gateway-tweed).

Source: live re-probe of all five hosts 2026-09-06 (ping/ARP/NFS from tweed,
`openFPGALoader --detect`, `/proc/cmdline`, `kernel.sysrq`); models and DNAs
from the 2026-03-17 survey.

### SQRL Acorn CLE-215+

Six boards, each on a Raspberry Pi 5 with an M.2 HAT: the [Raspberry Pi
5](../boards/acorn/wiring.md#raspberry-pi-5) wiring, with JTAG on its own GPIOs
(`--pins 10:9:11:8`) and both spare balls wired.

All six were unplugged and are being put back one at a time, and not into the
ports they had before. A hostname follows the switch port (`pi-sw2-p<port>`),
so each board is listed by its RPi MAC. A board without a switch port is
unplugged and waiting to go back in; its columns are its last measurement.

```{rst-class} nowrap
```

| RPi MAC | Now | RPi Model (rev) | FPGA Device DNA | In flash | JTAG | P2 (K2/J2/J5/H5) | Camera | Last checked |
| ------- | --- | --------------- | --------------- | -------- | ---- | ---------------- | ------ | ------------ |
| 88:a2:9e:45:85:77 | [pi-sw2-p48](https://welland.fpgas.online/fpgas/pi48.html) | RPi 5 Rev 1.1 2 GB (b04171) | `0x0054b48664b04854` | **fpgas.online golden + operational** (`10ee:7021`, subsystem `1e24:021f`), cold boot proven ([how](../boards/acorn/pcie-programming.md#installing-the-fpgasonline-images)) | OK | OK, all four | **out of focus, not aimed at the board** | 2026-09-21 |
| 88:a2:9e:45:dd:be | unplugged | RPi 5 Rev 1.1 2 GB (b04171) | not read | SQRL factory firmware (`1e24:021f`) | OK | serial pair OK; **J5 wire open** | ov5647 | 2026-09-03 |
| 98:fe:54:13:e0:75 | unplugged | RPi 5 Rev 1.1 1 GB (a04171) | not read | SQRL factory firmware (`1e24:021f`) | **empty chain** | untestable | ov5647 | 2026-09-03 |
| 98:fe:54:13:e0:f5 | unplugged | RPi 5 Rev 1.1 1 GB (a04171) | not read | `10ee:7011`, most likely the vendor XDMA sample image | **empty chain** | untestable | ov5647 | 2026-09-03 |
| 98:fe:54:13:f5:75 | unplugged | RPi 5 Rev 1.1 1 GB (a04171) | not read | SQRL factory firmware (`1e24:021f`) | OK | **reversed** (K2↔J2 and J5↔H5) | ov5647 | 2026-09-03 |
| 88:a2:9e:45:c6:87 | unplugged | RPi 5 Rev 1.1 2 GB (b04171) | not read | SQRL factory firmware (`1e24:021f`) | OK | OK, all four | ov5647 | 2026-09-03 |

The SQRL factory firmware is a mining design, not LiteX, so `litepcie_util`
cannot talk to a board that boots it; `10ee:7011` is the vendor's XDMA sample
image, also not LiteX. See [PCIe programming](../boards/acorn/pcie-programming.md).
The JTAG and P2 columns come from the [pin-ID
check](../boards/acorn/wiring.md#step-4-pin-id): GPIO15 decoded through
`/dev/ttyAMA0`, the other three lines from `gpiomon` edge timestamps.

All six run the shared bookworm NFS root (`overlayroot=tmpfs`), with
`/dev/ttyAMA0` enabled by `[pi5] dtoverlay=uart0-pi5`, the kernel console on
`ttyAMA10` and `serial-getty@ttyAMA0` inactive. The root carries
`openfpgaloader-rp1pio` and `openocd-rp1pio` 0.0.post76 (openFPGALoader 1.1.1,
OpenOCD 0.12). openFPGALoader's `libgpiod` cable works once `/dev/gpiochip0` is
linked to `gpiochip15` ([how](../boards/acorn/wiring.md#p1-jtag)); its `rp1pio`
cable needs `/dev/pio0`, which these hosts do not have (`rp1-pio: failed to
contact RP1 firmware`, bootloader `3c4fc886`). OpenOCD with `adapter driver
linuxgpiod` on `gpiochip15` works too, and loads the 2.3 MB fpgas.online SoC
bitstream in 24 s. A wedged Pi 5 draws about 0.4 W on PoE instead of about 8 W
and needs a PoE cycle, taking more than 90 s to come back.

Source: live probes (`/proc/device-tree/model`, `lspci -nn`, `/proc/cmdline`,
`openFPGALoader --detect`, the pin-ID check), the NFS root's package list on
tweed, and pi-sw2-p48's install record.

### Fomu EVT

Surveyed 2026-03-17. Two boards, on RPi 3B+ hosts.

```{rst-class} nowrap
```

| Host | Switch Port | IP (retired) | RPi MAC           | RPi Model   | Fomu USB VID:PID | DFU Version | USB Analyzer             |
| ---- | ----------- | ------------ | ----------------- | --------------- | ---------------- | ----------- | ------------------------ |
| pi17 | p17         | 10.21.0.117  | b8:27:eb:47:9f:d1 | RPi 3B+ 1 GB     | 1209:5bf0        | v2.0.4      | OpenVizsla (1d50:607c)   |
| pi21 | p21         | 10.21.0.121  | b8:27:eb:fc:4d:f8 | RPi 3B+ 1 GB     | 1209:5bf0        | v2.0.4      | Cythion/LUNA (16d0:05a5) |

:::{note}
The 2026-08-30 hardware inventory sheet places the Fomu and its OpenVizsla (was
pi17) at sw1 p17. These addresses no longer resolve; derive the current name and
address from the switch port using [Network and power](../setup/network.md).
:::

Each host has a USB protocol analyzer inline, so the Fomu's native USB traffic
can be captured without changing the design or the host software: an
[OpenVizsla](https://github.com/openvizsla/ov_ftdi) sniffer on pi17 and a
[Cythion](https://greatscottgadgets.com/cythion/) running
[LUNA](https://github.com/greatscottgadgets/luna) on pi21. The Fomu itself has
no USB serial device — it speaks native USB (ValentyUSB) and appears as "Generic
Fomu EVT running DFU Bootloader v2.0.4". Its UART is on the Pi's GPIO header
instead, not over USB; see the [board page](../boards/fomu-evt.md).

Source: `lsusb` on pi17, dnsmasq pibs.conf, verified 2026-03-17.

### Tiny Tapeout ASIC boards

Probed 2026-09-03. Six boards on S3300 ports 3–8, on RPi 4 / 3B+ hosts with
PMOD HATs. These carry **real fabricated TT ASIC silicon** on a TT demo board
(RP2040, MicroPython TT SDK) and are the public boards on
[tinytapeout.fpgas.online](https://tinytapeout.fpgas.online) (live since
2026-08-23): S3300 port N carries TTN, the board page is
`https://tinytapeout.fpgas.online/board/<slug>/` and its `status.json` is the
liveness check.

```{rst-class} nowrap
```

| Host      | Slug     | Switch Port | IP        | RPi MAC           | RPi Model (rev)               | Chip / firmware                          | RP2040 serial      | Old name |
| --------- | -------- | ----------- | --------- | ----------------- | ----------------------------- | ---------------------------------------- | ------------------ | -------- |
| pi-sw2-p3 | [tt03p5](https://tinytapeout.fpgas.online/board/tt03p5/) | sw2 p3 | 10.21.2.3 | 98:fe:54:1b:7f:de | RPi 4 2 GB Rev 1.5 (b03115) | TT03p5 (sky130), demo-board fw **1.2.2** (last release supporting tt03p5) | de636c65c34d6a25 | — |
| pi-sw2-p4 | [tt04](https://tinytapeout.fpgas.online/board/tt04/)     | sw2 p4 | 10.21.2.4 | 98:fe:54:1b:7f:57 | RPi 4 2 GB Rev 1.5 (b03115) | TT04, TT SDK 2.0.4                        | de637061074b1838 | — |
| pi-sw2-p5 | [tt05](https://tinytapeout.fpgas.online/board/tt05/)     | sw2 p5 | 10.21.2.5 | 98:fe:54:1b:80:11 | RPi 4 2 GB Rev 1.5 (b03115) | TT05, TT SDK 2.0.4                        | de637061071e5439 | — |
| pi-sw2-p6 | [tt06](https://tinytapeout.fpgas.online/board/tt06/)     | sw2 p6 | 10.21.2.6 | b8:27:eb:71:78:cc | RPi 3B+ 1 GB Rev 1.3 (a020d3) | TT06, TT SDK 2.0.4                      | de640cb1d3357125 | pi23 |
| pi-sw2-p7 | [tt07](https://tinytapeout.fpgas.online/board/tt07/)     | sw2 p7 | 10.21.2.7 | b8:27:eb:19:43:cd | RPi 3B+ 1 GB Rev 1.3 (a020d3) | TT07, TT SDK 2.0.4                      | de641070db746f27 | pi19 |
| pi-sw2-p8 | [tt08](https://tinytapeout.fpgas.online/board/tt08/)     | sw2 p8 | 10.21.2.8 | b8:27:eb:44:46:e9 | RPi 3B+ 1 GB Rev 1.3 (a020d3) | TT08, TT SDK 2.0.4                      | de641070db5b2d27 | pi25 |

:::{note}
These hosts have no page under `https://welland.fpgas.online/fpgas/`: the
pi3.html … pi8.html names all return 404 (checked 2026-09-03). Their public
pages are the `tinytapeout.fpgas.online` board pages linked above.
:::

Ports 9 and 10 (tt09, tt10) are reserved in the catalogue but have no Pi yet.
Every host also has a Digilent Pmod HAT and an ov5647 camera. The boards appear
as "MicroPython Board in FS mode" (RP2040, `2e8a:0005`) with a udev symlink
`/dev/ttboard`, and the `fpgas-tt` daemon owns that port; see
[Tiny Tapeout ASIC boards](../boards/tt-asic.md).

Firmware notes (2026-08-23/24): tt04, tt05 and tt07 were reflashed to TT SDK
2.0.4, tt06 and tt08 already had it. The tt03p5 chip is not supported by SDK
2.0 or later, so that board runs demo-board firmware 1.2.2 with a hand-pushed
`/shuttles/tt03p5.json` and `rom_fallback.txt`, and its page is camera-first for
now.

Source: live probe 2026-09-03 (`lsusb`, `/dev/serial/by-id`, `fuser
/dev/ttyACM0`, daemon `/health`); firmware versions from the 2026-08-23 reflash
session; catalogue = `tt_boards` in infra `host_vars/fpgas.online.yml`.

### Tiny Tapeout FPGA demo boards

Probed 2026-09-03. Four boards on S3300 ports 33–36, on RPi 4 hosts with PMOD
HATs. These carry an **iCE40UP5K FPGA** (FabricFox breakout) that emulates Tiny
Tapeout designs, on a TT demo board **v3 (RP2350B)** running TT SDK **3.1.0**
(reflashed 2026-08-23). They are **not** ASIC boards. Public as `fpga-1` …
`fpga-4` on tinytapeout.fpgas.online since 2026-08-24, where users can run
bundled demos or upload their own bitstream.

```{rst-class} nowrap
```

| Host       | Slug   | Switch Port | IP         | RPi MAC           | RPi Model (rev)              | USB VID:PID | RP2350 Serial    | Old name |
| ---------- | ------ | ----------- | ---------- | ----------------- | ---------------------------- | ----------- | ---------------- | -------- |
| [pi-sw2-p33](https://welland.fpgas.online/fpgas/pi33.html) | [fpga-1](https://tinytapeout.fpgas.online/board/fpga-1/) | sw2 p33 | 10.21.2.33 | e4:5f:01:97:0e:77 | RPi 4 2 GB Rev 1.5 (b03115) | 2e8a:0005 | 4df39a7a6856f86f | pi27 |
| [pi-sw2-p34](https://welland.fpgas.online/fpgas/pi34.html) | [fpga-2](https://tinytapeout.fpgas.online/board/fpga-2/) | sw2 p34 | 10.21.2.34 | e4:5f:01:97:27:f2 | RPi 4 2 GB Rev 1.5 (b03115) | 2e8a:0005 | fd1a167bd863a198 | pi29 |
| [pi-sw2-p35](https://welland.fpgas.online/fpgas/pi35.html) | [fpga-3](https://tinytapeout.fpgas.online/board/fpga-3/) | sw2 p35 | 10.21.2.35 | e4:5f:01:97:0c:e3 | RPi 4 2 GB Rev 1.5 (b03115) | 2e8a:0005 | 8c46329b33590ecb | pi31 |
| [pi-sw2-p36](https://welland.fpgas.online/fpgas/pi36.html) | [fpga-4](https://tinytapeout.fpgas.online/board/fpga-4/) | sw2 p36 | 10.21.2.36 | e4:5f:01:8e:02:27 | RPi 4 8 GB Rev 1.5 (d03115) | 2e8a:0005 | a2961e5cac65b25f | pi33 |

Each RPi connects to its board over USB-C, has a Digilent Pmod HAT for
GPIO-level control of the TT I/O pins, and an ov5647 camera publishing a live
feed. Like the ASIC boards they appear as "MicroPython Board in FS mode" with
the `/dev/ttboard` symlink, and the `fpgas-tt` daemon owns the port. Each
board's `status.json` (for example
`https://tinytapeout.fpgas.online/board/fpga-1/status.json`) reports the daemon's
`/health` plus `reachable`, and is the quickest liveness check. The custom
bitstreams that were on the boards before the reflash were backed up to tweed
under `/root/fpgas-tt-setup/fpga-backup/<host>/` and pushed back. See
[Tiny Tapeout FPGA demo board](../boards/tt-fpga.md) for the firmware history.

Source: live probe 2026-09-03 (`lsusb`, `/dev/serial/by-id`, daemon `/health`).

## Disconnected hosts

Surveyed 2026-03-17.

| Host | MAC               | IP (retired) | Notes                                      |
| ---- | ----------------- | ------------ | ------------------------------------------ |
| pi44 | dc:a6:32:b4:5e:c9 | 10.21.0.144  | Not connected (old MAC, may be reassigned) |

:::{note}
This address no longer resolves. This host has not been located on the new
scheme.
:::

Source: `pibs.conf` on tweed.

## Known faults

- **Acorn 98:fe:54:13:e0:75 and 98:fe:54:13:e0:f5**: `openFPGALoader --detect`
  finds an empty JTAG chain although PCIe enumerates. The P1 cable needs a
  physical check; until then nothing can be loaded on them.
- **Acorn 98:fe:54:13:f5:75**: the P2 cable is reversed (K2↔J2 and J5↔H5).
  Transpose both pairs; turning the 2×3 housing round does not fix it, because
  that maps pin 5↔10 and 7↔8.
- **Acorn 88:a2:9e:45:dd:be**: the J5 (spare GPIO) conductor is open. The serial
  pair is fine.
- **All Acorn hosts**: openFPGALoader's `rp1pio` cable cannot run (no
  `/dev/pio0`), and its `libgpiod` cable needs the `gpiochip15 → gpiochip0`
  link on a Pi 5. See [P1: JTAG](../boards/acorn/wiring.md#p1-jtag).
- **pi-sw2-p3** (tt03p5): the web Commander does not support demo-board
  firmware 1.2.x yet, so that board is camera-only. It needs the upstream
  `legacy` branch port —
  [tt-commander-app #9](https://github.com/fpgas-online/tt-commander-app/pull/9)
  and [#10](https://github.com/fpgas-online/tt-commander-app/pull/10).
- **Stale NFS handles after package upgrades in the shared NFS root**: on
  2026-08-30, upgrading `fpgas-online-cam` under running Pis left them with
  `ESTALE` on the replaced files — cameras off air on 11 boards; on 2026-09-03
  the TT hosts still showed `dpkg-query … Stale file handle`. Only a reboot
  fixes it. Expect it after any NFS-root package update.
- **Legacy entries from the 2026-03-17 survey** (not re-checked):
  - pi9 Arty A7: FTDI disconnected, so no USB serial devices are present and the
    board cannot be programmed or tested until the USB connection is restored.
  - pi21: Cythion/LUNA and Fomu offline.
