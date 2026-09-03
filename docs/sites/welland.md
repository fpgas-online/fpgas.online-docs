# Welland

The private test lab in South Australia, published as
[welland.fpgas.online](https://welland.fpgas.online). Raspberry Pi 5 hosts, each
with a SQRL Acorn board on an mPCIe adapter, plus a camera pointed at the board;
alongside them Arty A7, NeTV2, Fomu and Tiny Tapeout hosts on their own Pis.

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
   (sw2 p38 +…)   (sw1 ×4)      (sw2 ×6)       (sw2 p3–p8)     (sw2 p33–36)
                                            + Fomu EVT on sw1 p17
```

Every Raspberry Pi netboots over PXE/TFTP from tweed. Since **2026-08-23** the
site runs the **VLAN-per-port** scheme
([fpgas.online-infra PR #10](https://github.com/fpgas-online/fpgas.online-infra/pull/10)):
every Pi-facing switch port is an untagged access port in its own VLAN, tweed isolates Pi↔Pi traffic with
nftables, and a Pi's identity comes from the port it is plugged into rather
than from its MAC.

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
| Domain     | fpgas.welland.mithis.com                                                             |
| PCI        | 2× Intel 82574L GbE, Tundra PCI bridge, Matrox G200eW                                |
| NFS roots  | `/srv/nfs/rpi/bookworm/{boot,root}` (armhf + arm64 kernels, `overlayroot=tmpfs`); apt packages `fpgas-online-tt` 0.0.post52, `fpgas-online-tt-demos` 0.0.post21, `fpgas-online-cam` 0.0.post43, `openfpgaloader` 0.10.0 |

Tweed hosts no FPGA boards itself. Reach it as the `ansible` user on the uplink
address 10.99.21.2, from ten64 (verified 2026-09-03).

:::{warning}
The public name `tweed.welland.mithis.com` resolves to ten64's reverse proxy, so
ssh to that name never reached tweed. Use the 10.99.21.2 uplink address.
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
live on 2026-09-03 under the VLAN-per-port scheme. The Arty A7, NeTV2 and Fomu
sections still carry the pre-2026-08-23 names and addresses from the 2026-03-17
survey.

:::{todo}
Re-probe the Arty, NeTV2 and Fomu hosts under the VLAN-per-port scheme and
replace the 2026-03-17 rows below with measured ones.
:::

Programming commands for each board type live on the board pages; see
[Boards](../boards/index.md).

### Infrastructure host (probed 2026-03-17)

| Host | Switch Port | IP          | RPi MAC           | RPi Model   | Role                                         |
| ---- | ----------- | ----------- | ----------------- | ----------- | -------------------------------------------- |
| pi1  | port 1      | 10.21.0.101 | b8:27:eb:ec:c2:c9 | RPi 3B+ 1GB | Always-on NFS maintenance system (RW access) |

:::{note}
The host name and address are from the 2026-03-17 survey and have not been
re-probed since the 2026-08-23 VLAN-per-port cutover.
:::

### Arty A7-35T (probed 2026-03-17)

Five boards, on RPi 4 / 3B+ hosts with PMOD HATs.

| Host | Switch Port | IP          | RPi MAC           | RPi Model   | Arty Serial         | Arty DNA           | USB Ethernet                     | Serial Devices   |
| ---- | ----------- | ----------- | ----------------- | ----------- | ------------------- | ------------------ | -------------------------------- | ---------------- |
| [pi7](https://welland.fpgas.online/fpgas/pi7.html)   | port 7      | 10.21.0.107 | e4:5f:01:96:f8:a5 | RPi 4 2GB   | 210319B301DE        | 0x00628502251ea85c | ASIX AX88179 (f8:e4:3b:0f:c1:e6) | ttyUSB0, ttyUSB1 |
| pi9  | port 9      | 10.21.0.109 | b8:27:eb:86:39:63 | RPi 3B+ 1GB | (FTDI disconnected) | —                  | Apple Eth (48:d7:05:e9:40:52)    | **none**         |
| [pi11](https://welland.fpgas.online/fpgas/pi11.html) | port 11     | 10.21.0.111 | e4:5f:01:8d:f7:17 | RPi 4 8GB   | 210319B3E5C5        | 0x002c8d02251ea854 | DM9601 (00:e0:4c:53:44:58)       | ttyUSB0, ttyUSB1 |
| [pi13](https://welland.fpgas.online/fpgas/pi13.html) | port 13     | 10.21.0.113 | b8:27:eb:6d:27:f6 | RPi 3B+ 1GB | 210319A43ADB        | 0x0002f54832290854 | ASIX (8a:ce:4c:ff:ae:83)         | ttyUSB0, ttyUSB1 |
| [pi26](https://welland.fpgas.online/fpgas/pi26.html) | port 26     | 10.21.0.126 | e4:5f:01:97:1f:7e | RPi 4 2GB   | 210319B0C238        | 0x0144cd2a47442854 | Linksys GbE (60:38:e0:e3:56:4f)  | ttyUSB0, ttyUSB1 |

:::{note}
The host names and addresses here are from the 2026-03-17 survey and have not
been re-probed since the 2026-08-23 VLAN-per-port cutover. The 2026-08-30
hardware inventory sheet places the Arty (`210319B3E5C5`, was pi11) at sw2 p38.
:::

Each RPi also carries a separate USB Ethernet adapter wired to the Arty's
Ethernet port for network testing. See [Arty A7](../boards/arty-a7.md) for the
FTDI interfaces and serial paths.

Source: `lsusb` and `ls /dev/serial/by-id/` on each RPi, dnsmasq pibs.conf.

### NeTV2 (probed 2026-03-17)

Five boards, on RPi 3B+ hosts with GPIO JTAG.

| Host | Switch Port | IP          | RPi MAC           | RPi Model   | FPGA    | FPGA DNA           |
| ---- | ----------- | ----------- | ----------------- | ----------- | ------- | ------------------ |
| pi10 | port 10     | 10.21.0.110 | b8:27:eb:e3:e7:e4 | RPi 3B+ 1GB | XC7A35T | 0x2a11a4c662251c6f |
| pi12 | port 12     | 10.21.0.112 | b8:27:eb:eb:5d:bf | RPi 3B+ 1GB | XC7A35T | 0x3a11a4c662372a6b |
| pi14 | port 14     | 10.21.0.114 | b8:27:eb:e3:7c:3c | RPi 3B+ 1GB | XC7A35T | 0x3a11dcc864222e93 |
| pi16 | port 16     | 10.21.0.116 | b8:27:eb:c6:29:79 | RPi 3B+ 1GB | XC7A35T | 0x2a11a4c662372a53 |
| pi18 | port 18     | 10.21.0.118 | b8:27:eb:2c:e8:de | RPi 3B+ 1GB | XC7A35T | 0x3a11dcc864241c0b |

:::{note}
The host names and addresses here are from the 2026-03-17 survey and have not
been re-probed since the 2026-08-23 VLAN-per-port cutover. The 2026-08-30
hardware inventory sheet places these four NeTV2 Pis at sw1 p10, p12, p14 and
p16, with the same MACs as pi10, pi12, pi14 and pi16.
:::

No USB serial devices: the NeTV2 uses GPIO UART, and JTAG is bit-banged on the
Pi's GPIO header. See [Kosagi NeTV2](../boards/netv2.md).

Source: dnsmasq pibs.conf, `lsusb` on pi10.

### Sqrl Acorn CLE-215+ (probed 2026-09-03)

Six boards deployed, on RPi 5 hosts with an M.2 HAT.

| Host       | Switch Port | IP         | RPi MAC           | RPi Model (rev)          | PCIe Device at `0001:01:00.0`                          | JTAG          | P2 serial            | Old name |
| ---------- | ----------- | ---------- | ----------------- | ------------------------ | ------------------------------------------------------ | ------------- | -------------------- | -------- |
| pi-sw2-p29 | sw2 p29     | 10.21.2.29 | 88:a2:9e:45:dd:be | RPi 5 Rev 1.1 2 GB (b04171) | Squirrels Research Labs Acorn CLE-215+ `1e24:021f` | OK            | OK (J5 wire dead)    | pi4      |
| pi-sw2-p43 | sw2 p43     | 10.21.2.43 | 98:fe:54:13:e0:75 | RPi 5 Rev 1.1 1 GB (a04171) | Squirrels Research Labs Acorn CLE-215+ `1e24:021f` | empty chain   | untestable           | —        |
| pi-sw2-p44 | sw2 p44     | 10.21.2.44 | 98:fe:54:13:e0:f5 | RPi 5 Rev 1.1 1 GB (a04171) | Xilinx 7-Series FPGA Hard PCIe block `10ee:7011`   | empty chain   | untestable           | —        |
| pi-sw2-p46 | sw2 p46     | 10.21.2.46 | 88:a2:9e:45:85:77 | RPi 5 Rev 1.1 2 GB (b04171) | Squirrels Research Labs Acorn CLE-215+ `1e24:021f` | OK            | OK                   | pi6      |
| pi-sw2-p47 | sw2 p47     | 10.21.2.47 | 98:fe:54:13:f5:75 | RPi 5 Rev 1.1 1 GB (a04171) | Squirrels Research Labs Acorn CLE-215+ `1e24:021f` | OK            | reversed (K2↔J2)     | —        |
| pi-sw2-p48 | sw2 p48     | 10.21.2.48 | 88:a2:9e:45:c6:87 | RPi 5 Rev 1.1 2 GB (b04171) | Squirrels Research Labs Acorn CLE-215+ `1e24:021f` | OK            | OK                   | pi2      |

Every one of the six has an ov5647 camera and publishes a feed. All run the
shared bookworm NFS root (kernel 6.12.96, `overlayroot=tmpfs`), have
`/dev/ttyAMA0` enabled by `[pi5] dtoverlay=uart0-pi5` with the kernel console on
`ttyAMA10` and `serial-getty@ttyAMA0` inactive, and carry openFPGALoader 0.10.0.
A wedged Pi 5 draws about 0.4 W on PoE instead of about 8 W and needs a PoE
cycle, taking more than 90 s to come back. An earlier revision of this table
called the first three "RPi 5 8GB"; the revision codes say 2 GB.

What is in each board's SPI flash — that is, what enumerates on PCIe at boot,
`lspci -nn` on each host 2026-09-03:

| Host       | Flash contents (what enumerates at boot)                                   |
|------------|----------------------------------------------------------------------------|
| pi-sw2-p29 | Sqrl factory firmware `1e24:021f`                                          |
| pi-sw2-p43 | Sqrl factory firmware `1e24:021f`                                          |
| pi-sw2-p44 | `10ee:7011` — Xilinx 7-Series Hard PCIe block (a LiteX/Vivado design)      |
| pi-sw2-p46 | Sqrl factory firmware `1e24:021f`                                          |
| pi-sw2-p47 | Sqrl factory firmware `1e24:021f`                                          |
| pi-sw2-p48 | Sqrl factory firmware `1e24:021f`                                          |

Five of the six therefore still boot the factory mining firmware, which is not a
LiteX design, so `litepcie_util` cannot talk to them; see
[PCIe programming](../boards/acorn/pcie-programming.md).

Source: live probe of all six hosts 2026-09-03 (`/proc/device-tree/model`,
`/proc/cpuinfo`, `lspci -nn`, `/proc/cmdline`, `openFPGALoader --Version`);
JTAG and P2 columns from the 2026-08-31 pin-ID survey.

### Fomu EVT (probed 2026-03-17)

Two boards, on RPi 3B+ hosts.

| Host | Switch Port | IP          | RPi MAC           | RPi Model   | Fomu USB VID:PID | DFU Version | USB Analyzer             |
| ---- | ----------- | ----------- | ----------------- | ----------- | ---------------- | ----------- | ------------------------ |
| [pi17](https://welland.fpgas.online/fpgas/pi17.html) | port 17     | 10.21.0.117 | b8:27:eb:47:9f:d1 | RPi 3B+ 1GB | 1209:5bf0        | v2.0.4      | OpenVizsla (1d50:607c)   |
| [pi21](https://welland.fpgas.online/fpgas/pi21.html) | port 21     | 10.21.0.121 | b8:27:eb:fc:4d:f8 | RPi 3B+ 1GB | 1209:5bf0        | v2.0.4      | Cythion/LUNA (16d0:05a5) |

:::{note}
The host names and addresses here are from the 2026-03-17 survey and have not
been re-probed since the 2026-08-23 VLAN-per-port cutover. The 2026-08-30
hardware inventory sheet places the Fomu and its OpenVizsla (was pi17) at
sw1 p17.
:::

Each host has a USB protocol analyzer inline, so the Fomu's native USB traffic
can be captured without changing the design or the host software: an
[OpenVizsla](https://github.com/openvizsla/ov_ftdi) sniffer on pi17 and a
[Cythion](https://greatscottgadgets.com/cythion/) running
[LUNA](https://github.com/greatscottgadgets/luna) on pi21. The Fomu itself has
no serial device — it speaks native USB (ValentyUSB) and appears as "Generic
Fomu EVT running DFU Bootloader v2.0.4".

Source: `lsusb` on pi17, dnsmasq pibs.conf, verified 2026-03-17.

### Tiny Tapeout ASIC boards (probed 2026-09-03)

Six boards on S3300 ports 3–8, on RPi 4 / 3B+ hosts with PMOD HATs. These carry
**real fabricated TT ASIC silicon** on a TT demo board (RP2040, MicroPython TT
SDK) and are the public boards on
[tinytapeout.fpgas.online](https://tinytapeout.fpgas.online) (live since
2026-08-23): S3300 port N carries TTN, the board page is
`https://tinytapeout.fpgas.online/board/<slug>/` and its `status.json` is the
liveness check.

| Host      | Slug     | Switch Port | IP        | RPi MAC           | RPi Model (rev)               | Chip / firmware                          | RP2040 serial      | Old name |
| --------- | -------- | ----------- | --------- | ----------------- | ----------------------------- | ---------------------------------------- | ------------------ | -------- |
| pi-sw2-p3 | [tt03p5](https://tinytapeout.fpgas.online/board/tt03p5/) | sw2 p3 | 10.21.2.3 | 98:fe:54:1b:7f:de | RPi 4 2 GB Rev 1.5 (b03115) | TT03p5 (sky130), demo-board fw **1.2.2** (last release supporting tt03p5) | de636c65c34d6a25 | — |
| pi-sw2-p4 | [tt04](https://tinytapeout.fpgas.online/board/tt04/)     | sw2 p4 | 10.21.2.4 | 98:fe:54:1b:7f:57 | RPi 4 2 GB Rev 1.5 (b03115) | TT04, TT SDK 2.0.4                        | de637061074b1838 | — |
| pi-sw2-p5 | [tt05](https://tinytapeout.fpgas.online/board/tt05/)     | sw2 p5 | 10.21.2.5 | 98:fe:54:1b:80:11 | RPi 4 2 GB Rev 1.5 (b03115) | TT05, TT SDK 2.0.4                        | de637061071e5439 | — |
| pi-sw2-p6 | [tt06](https://tinytapeout.fpgas.online/board/tt06/)     | sw2 p6 | 10.21.2.6 | b8:27:eb:71:78:cc | RPi 3B+ 1 GB Rev 1.3 (a020d3) | TT06, TT SDK 2.0.4                      | de640cb1d3357125 | pi23 |
| pi-sw2-p7 | [tt07](https://tinytapeout.fpgas.online/board/tt07/)     | sw2 p7 | 10.21.2.7 | b8:27:eb:19:43:cd | RPi 3B+ 1 GB Rev 1.3 (a020d3) | TT07, TT SDK 2.0.4                      | de641070db746f27 | pi19 |
| pi-sw2-p8 | [tt08](https://tinytapeout.fpgas.online/board/tt08/)     | sw2 p8 | 10.21.2.8 | b8:27:eb:44:46:e9 | RPi 3B+ 1 GB Rev 1.3 (a020d3) | TT08, TT SDK 2.0.4                      | de641070db5b2d27 | pi25 |

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

### Tiny Tapeout FPGA demo boards (probed 2026-09-03)

Four boards on S3300 ports 33–36, on RPi 4 hosts with PMOD HATs. These carry an
**iCE40UP5K FPGA** (FabricFox breakout) that emulates Tiny Tapeout designs, on a
TT demo board **v3 (RP2350B)** running TT SDK **3.1.0** (reflashed 2026-08-23).
They are **not** ASIC boards. Public as `fpga-1` … `fpga-4` on
tinytapeout.fpgas.online since 2026-08-24, where users can run bundled demos or
upload their own bitstream.

| Host       | Slug   | Switch Port | IP         | RPi MAC           | RPi Model (rev)              | USB VID:PID | RP2350 Serial    | Old name |
| ---------- | ------ | ----------- | ---------- | ----------------- | ---------------------------- | ----------- | ---------------- | -------- |
| pi-sw2-p33 | [fpga-1](https://tinytapeout.fpgas.online/board/fpga-1/) | sw2 p33 | 10.21.2.33 | e4:5f:01:97:0e:77 | RPi 4 2 GB Rev 1.5 (b03115) | 2e8a:0005 | 4df39a7a6856f86f | pi27 |
| pi-sw2-p34 | [fpga-2](https://tinytapeout.fpgas.online/board/fpga-2/) | sw2 p34 | 10.21.2.34 | e4:5f:01:97:27:f2 | RPi 4 2 GB Rev 1.5 (b03115) | 2e8a:0005 | fd1a167bd863a198 | pi29 |
| pi-sw2-p35 | [fpga-3](https://tinytapeout.fpgas.online/board/fpga-3/) | sw2 p35 | 10.21.2.35 | e4:5f:01:97:0c:e3 | RPi 4 2 GB Rev 1.5 (b03115) | 2e8a:0005 | 8c46329b33590ecb | pi31 |
| pi-sw2-p36 | [fpga-4](https://tinytapeout.fpgas.online/board/fpga-4/) | sw2 p36 | 10.21.2.36 | e4:5f:01:8e:02:27 | RPi 4 8 GB Rev 1.5 (d03115) | 2e8a:0005 | a2961e5cac65b25f | pi33 |

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

### NeTV2 development hosts, separate network (probed 2026-03-09)

Two NeTV2 hosts sit outside the tweed network, on `iot.welland.mithis.com`,
reachable over `wg-desktop` rather than through the gateway.

| Host                              | IP (via DNS)    | RPi Model             | Board                  | Connections         | SSH                                                        |
| --------------------------------- | --------------- | --------------------- | ---------------------- | ------------------- | ---------------------------------------------------------- |
| rpi5-netv2.iot.welland.mithis.com | 10.1.90.210/211 | RPi 5 Model B Rev 1.0 | NeTV2 (bare developer) | GPIO + PCIe Gen2 x1 | `tim@rpi5-netv2.iot.welland.mithis.com` (via `wg-desktop`) |
| rpi3-netv2.iot.welland.mithis.com | 10.1.90.212/213 | RPi 3                 | NeTV2 (stock packaged) | GPIO only           | `pi@rpi3-netv2.iot.welland.mithis.com` (via `wg-desktop`)  |

**rpi5-netv2**, verified over SSH 2026-03-09: Debian 13 (Trixie), kernel
6.12.47+rpt-rpi-2712 aarch64; OpenOCD installed but no openFPGALoader and no
LiteX; an ASIX AX88179 Gigabit Ethernet adapter is the only USB device, so
there is no FTDI JTAG adapter and no USB serial device; only the RP1 south
bridge is visible on PCIe, so the NeTV2 FPGA is not enumerating.

### PMOD HAT development hosts, separate network (surveyed 2026-03-17)

| Host                             | RPi Model | Notes             |
| -------------------------------- | --------- | ----------------- |
| rpi5-pmod.iot.welland.mithis.com | RPi 5     | PMOD HAT dev host |
| rpi4-pmod.iot.welland.mithis.com | RPi 4     | PMOD HAT dev host |

## Wiring

JTAG and the serial pair are on separate GPIOs here, which is why a design that
drives the FPGA's TX does not cost you JTAG the way it does at
[PS1](ps1.md#two-traps).

| Signal | GPIO | Header pin |
|---|---|---|
| TCK | 11 | 23 |
| TDI | 10 | 19 |
| TDO | 9 | 21 |
| TMS | 8 | 24 |

```console
$ openFPGALoader --cable libgpiod --pins 10:9:11:8 --detect
```

The P2 serial pair is a **null-modem crossover**, the same as at PS1: the
crossover is the fleet standard, not a Compute Blade special case. Measured on
2026-08-31 with the pin-ID design on pi-sw2-p29, p46 and p48; p47 has both
pairs transposed (see [Known faults](#known-faults)), and p43 and p44 could not
be read because JTAG scans an empty chain there.

| P2 ball | lands on | RPi function |
|---|---|---|
| K2 (FPGA TX) | GPIO15 | RXD0 — the Pi receives |
| J2 (FPGA RX) | GPIO14 | TXD0 — the Pi sends |

:::{note}
Until 2026-09-03 this page recorded the opposite — K2 straight through to
GPIO14 — and called the crossover a PS1 peculiarity. That was a documentation
error, not a difference between the sites: it wired transmitter into
transmitter, which cannot work with the hardware UART (`/dev/ttyAMA0`) every
host and test script uses. Corrected here from the 2026-08-31 pin-ID
measurements.
:::

Both tables are the Acorn on a Pi 5; the connector pinout they are measured
against, and the full per-pin survey behind them, are on
[Acorn wiring](../boards/acorn/wiring.md).

## Raspberry Pi 5 specifics

`gpiochip`
: The 40-pin header GPIOs are on **gpiochip15**, not gpiochip0. Tools that
  hardcode `/dev/gpiochip0` — including openFPGALoader 0.10.0 — fail here.

`dtoverlay=disable-bt`
: A no-op on the Pi 5. The overlay is `compatible="brcm,bcm2835"` and resolves
  to `disable-bt-pi5.dtbo`, which only touches the `bluetooth` node; the header
  UART stays disabled. Use `dtoverlay=uart0-pi5` instead, which is what the NFS
  root now carries
  ([infra PR #32](https://github.com/fpgas-online/fpgas.online-infra/pull/32)).

`/dev/ttyAMA0` vs `/dev/ttyAMA10`
: `ttyAMA0` is the RP1 header UART; `ttyAMA10` is the dedicated debug UART. The
  NFS root boots with `console=ttyAMA10` so that `ttyAMA0` is free for the FPGA.

## PCIe and JTAG interact

Reconfiguring the FPGA over JTAG while its PCIe endpoint is enumerated crashes
the BCM2712 root complex. Detach the endpoint first:

```console
$ echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove
```

Restore it with `/sys/bus/pci/rescan`, or by rebooting.

:::{warning}
The root filesystem is a read-only NFS export with a tmpfs overlay
(`overlayroot=tmpfs`), so anything staged in `/home/pi` is gone after a reboot.
A bitstream that loaded a minute ago will fail with `Open file … FAIL` after a
reboot because the file no longer exists.
:::

## Interfaces

Which physical interface each board type uses at this site. The pin mappings
themselves are board facts and live on the board pages.

USB-UART (FTDI FT2232)
: **Arty A7**. The FT2232 offers two USB interfaces; interface 1
  (`-if01-port0`) is the UART, at 115200 baud, on the FPGA's D10 (TX) and A9
  (RX). See [Arty A7](../boards/arty-a7.md).

GPIO UART
: **NeTV2** (its primary serial) and **Acorn CLE-215+** (the P2 connector). The
  Pi's `/dev/ttyAMA0` or `/dev/serial0` faces the FPGA's serial port. On the
  Pi 5 Acorn hosts `/dev/ttyAMA0` exists only because the NFS root's
  `config.txt` carries `[pi5] dtoverlay=uart0-pi5`, and the kernel console is
  kept off it (`console=ttyAMA10`) so FPGA output cannot trigger SysRq. Pin
  mappings: [Kosagi NeTV2](../boards/netv2.md) and
  [Acorn wiring](../boards/acorn/wiring.md).

Secondary UART on the PCIe "hax" pins
: **NeTV2** on a Pi 5 only. Pin mapping on [Kosagi NeTV2](../boards/netv2.md).

PCIe
: **Acorn CLE-215+** on all six Pi 5 hosts, and **NeTV2** on a Pi 5. The Acorn
  enumerates at `0001:01:00.0`, either as `1e24:021f` (Sqrl factory firmware) or
  as `10ee:7011` (a LiteX design — pi-sw2-p44). Reconfiguring the FPGA over JTAG
  while the endpoint is enumerated is a surprise removal that crashes the Pi 5;
  remove the device from the bus first and rescan afterwards. The NeTV2 supports
  x1/x2/x4 and connects as Gen2 x1 on a Pi 5, appearing as `10ee:7011` — but as
  of 2026-03-09 it is not enumerating at all on rpi5-netv2.

USB (native)
: **Fomu EVT** (ValentyUSB, pi17 and pi21), **Tiny Tapeout ASIC** (RP2040,
  pi-sw2-p3 … p8) and **Tiny Tapeout FPGA demo board** (RP2350,
  pi-sw2-p33 … p36). The USB analyzers on pi17 and pi21 sit inline on the Fomu's
  USB.

PMOD HAT
: **Arty A7** hosts. The HAT breaks Pi GPIOs out to three standard 12-pin PMOD
  ports (JA, JB, JC); see [Raspberry Pi PMOD HAT](../boards/pmod/rpi-hat.md).

## Test execution flow

```
┌──────────────────────────────────────────────────────────────┐
│ 1. BOOT                                                      │
│    RPi PXE-boots from tweed (TFTP)                           │
│                                                              │
│ 2. PROGRAM FPGA                                              │
│    - openFPGALoader (Arty): USB FTDI JTAG                    │
│    - openFPGALoader (NeTV2): RPi GPIO bitbang JTAG           │
│    - openFPGALoader (Acorn): RPi GPIO bitbang JTAG,          │
│      PCIe endpoint detached first                            │
│    - openFPGALoader (Fomu): USB DFU                          │
│    - RP2040/MicroPython (TT ASIC + FPGA Demo): /dev/ttyACM0  │
│                                                              │
│ 3. RUN TEST HARNESS                                          │
│    - Open serial port (ttyUSB1/ttyAMA0/ttyACM0)              │
│    - Send test commands to FPGA                              │
│    - Read responses and validate                             │
│                                                              │
│ 4. COLLECT RESULTS                                           │
│    - Parse UART output for PASS/FAIL                         │
│    - Check PCIe enumeration (NeTV2)                          │
│    - Verify PMOD loopback signals (Arty)                     │
│    - Report results                                          │
└──────────────────────────────────────────────────────────────┘
```

## Disconnected hosts (probed 2026-03-17)

| Host | MAC               | IP          | Notes                                   |
| ---- | ----------------- | ----------- | --------------------------------------- |
| pi44 | dc:a6:32:b4:5e:c9 | 10.21.0.144 | Not connected (old MAC, may be reassigned) |

:::{note}
This entry is from the 2026-03-17 survey and has not been re-probed since the
2026-08-23 VLAN-per-port cutover.
:::

Source: `pibs.conf` on tweed.

## Known faults

- **pi-sw2-p43 and pi-sw2-p44** (Acorn): `openFPGALoader --detect` finds an
  empty JTAG chain although PCIe enumerates — the P1 cable needs a physical
  check. Until then nothing can be loaded on them.
- **pi-sw2-p47** (Acorn): the P2 connector is reversed (K2↔J2 and J5↔H5).
  Transpose both pairs; a 180° re-seat does not fix it.
- **pi-sw2-p29** (Acorn): the J5 (spare GPIO 0) conductor is open. The serial
  pair is fine.
- **All Acorn hosts**: openFPGALoader is 0.10.0, which predates `--read-dna`,
  `--read-xadc` and `--read-register` and needs the `gpiochip15 → gpiochip0`
  symlink on a Pi 5. That is why device DNA cannot be read here while it can at
  PS1. See [Packages](../packages.md) for the replacement, which arrives with
  [infra PR #48](https://github.com/fpgas-online/fpgas.online-infra/pull/48).
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
- **rpi5-netv2**: the NeTV2 FPGA is not visible on the PCIe bus — it needs a
  bitstream loaded first.
- **Legacy entries from the 2026-03-17 survey** (not re-checked):
  - pi9 Arty A7: FTDI disconnected, so no USB serial devices are present and the
    board cannot be programmed or tested until the USB connection is restored.
  - pi18 NeTV2: offline.
  - pi21: Cythion/LUNA and Fomu offline.
  - The former "pi19 TT ASIC (version unconfirmed)" is TT07, now pi-sw2-p7 and
    online.
