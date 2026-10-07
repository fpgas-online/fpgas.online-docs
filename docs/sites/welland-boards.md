# Hosts and boards at welland

**You look after welland and want to know which board is on which host, what was last seen on each, and what is known
wrong with it.** Each section says when its table was read and from where. Logging in through the gateway is
on [The welland gateway](welland-gateway.md); the name and address rules are on [Network and
power](../setup/network.md).

## What was up on 6 October 2026

After the NFS root update of 6 October 2026, every Pi that came back was swept (the MAC is the gateway's
neighbour entry for the port's address), and `verify-pi.yml`
(fpgas.online-infra) checked each, including its board's own check, `fpgas-verify`. From the record of that
update (08:21 to 08:57 Adelaide time):

| Host | MAC seen at the port | Board, as its check reported it | Check |
|---|---|---|---|
| pi-sw1-p10 | b8:27:eb:e3:e7:e4 | NeTV2 (Artix-7 XC7A35T) | fail: the `ddr` test failed, the other two passed |
| pi-sw1-p12 | b8:27:eb:eb:5d:bf | NeTV2 | the same |
| pi-sw1-p14 | b8:27:eb:e3:7c:3c | NeTV2 | the same |
| pi-sw1-p16 | b8:27:eb:c6:29:79 | NeTV2 | the same |
| pi-sw1-p18 | b8:27:eb:2c:e8:de | NeTV2 | the same |
| pi-sw1-p17 | b8:27:eb:47:9f:d1 | Fomu host | pass |
| pi-sw1-p38 | 88:a2:9e:45:dd:81 | Acorn carrying a PCIe Screamer (PCILeech) image | fail: fpgas.online has no test design for that image |
| pi-sw2-p19, -p21, -p22, -p24 | 02:81:e1:ce:7d:46, 02:81:31:f4:6e:48, 02:81:2e:b7:a3:4e, 02:81:f5:c0:a6:10 | Orange Pi, no FPGA | back by themselves by 08:57; `verify-pi.yml` failed on each: no HAT ID EEPROM read over the kernel's TWI1 bus |
| pi-sw2-p30 | 98:fe:54:13:f5:9c | the Orange Pis' USB hub host ([Orange Pi H3 hosts](../setup/orange-pi.md)) | answered the gateway's ping; not checked |
| pi-sw2-p33 | e4:5f:01:97:0e:77 | Tiny Tapeout FPGA demo board | pass |
| pi-sw2-p35 | e4:5f:01:8e:02:27 | Tiny Tapeout FPGA demo board | pass |
| pi-sw2-p36 | e4:5f:01:97:0c:e3 | Tiny Tapeout FPGA demo board | pass |
| pi-sw2-p46 | 88:a2:9e:45:85:77 | Acorn CLE-215+ | pass |
| pi-sw2-p47 | 88:a2:9e:45:c6:87 | Acorn CLE-215+ | pass |

Not among the boards up that morning (the gateway's neighbour table): the Tiny Tapeout ASIC hosts (switch 2, ports 3 to 8), pi-sw2-p34 (Tiny Tapeout FPGA
board 2), and the Arty hosts. Boards are moved and visitors use them; this table is that morning's, not
today's.

## NeTV2

Re-verified live 2026-09-06 under the VLAN-per-port scheme. **Five** boards on
RPi 3B+ hosts with GPIO JTAG, all five online. Each is on switch 1 at the port in its name,
`10.21.1.<port>`, and all five netbooted the shared NFS root.

| Host | Switch Port | IP | RPi MAC | FPGA | FPGA DNA | JTAG detect | Old name |
| ---- | ----------- | -- | ------- | ---- | -------- | ----------- | -------- |
| pi-sw1-p10 | sw1 p10 | 10.21.1.10 | b8:27:eb:e3:e7:e4 | XC7A35T | 0x2a11a4c662251c6f | `0x0362d093` OK | pi10 |
| pi-sw1-p12 | sw1 p12 | 10.21.1.12 | b8:27:eb:eb:5d:bf | XC7A35T | 0x3a11a4c662372a6b | `0x0362d093` OK | pi12 |
| pi-sw1-p14 | sw1 p14 | 10.21.1.14 | b8:27:eb:e3:7c:3c | XC7A35T | 0x3a11dcc864222e93 | `0x0362d093` OK | pi14 |
| pi-sw1-p16 | sw1 p16 | 10.21.1.16 | b8:27:eb:c6:29:79 | XC7A35T | 0x2a11a4c662372a53 | `0x0362d093` OK | pi16 |
| pi-sw1-p18 | sw1 p18 | 10.21.1.18 | b8:27:eb:2c:e8:de | XC7A35T | 0x3a11dcc864241c0b | `0x0362d093` OK | pi18 |

The Pi models and FPGA DNAs are carried forward from the survey of 2026-03-17; the MACs, addresses, and the
**JTAG detect** column are the re-probe of 2026-09-06, with
`sudo openFPGALoader --cable libgpiod --pins 27:22:4:17 --detect` (`idcode 0x0362d093`, IR length 6). The
NeTV2 has no USB serial device: its UART is the Pi's `/dev/serial0` (`ttyAMA0` on these hosts), and JTAG is
bit-banged on the Pi's header ([Kosagi NeTV2](../boards/netv2.md)). These hosts have no page on
welland.fpgas.online.

**Known wrong with a NeTV2 host:**

- Their check fails one of its three tests on all five (6 October 2026, above).
- The FPGA must not be able to make the kernel act on its UART bytes: on a Pi 3B+ the serial pins are the ones
  the NeTV2's FPGA drives, and bytes it sends could reach SysRq as `reboot`, `crash` or `poweroff`. The served
  command line puts the console on `tty1` and the root sets `kernel.sysrq = 0`
  ([The kernel command line](../setup/netboot.md#the-kernel-command-line)); a node loaded with a design that
  drives the pin stayed up on all five (2026-09-06).

## Fomu EVT

Surveyed 2026-03-17. Two boards, on RPi 3B+ hosts.

| Host | Switch Port | IP (retired) | RPi MAC           | RPi Model   | Fomu USB VID:PID | DFU Version | USB Analyzer             |
| ---- | ----------- | ------------ | ----------------- | --------------- | ---------------- | ----------- | ------------------------ |
| pi17 | p17         | 10.21.0.117  | b8:27:eb:47:9f:d1 | RPi 3B+ 1 GB     | 1209:5bf0        | v2.0.4      | OpenVizsla (1d50:607c)   |
| pi21 | p21         | 10.21.0.121  | b8:27:eb:fc:4d:f8 | RPi 3B+ 1 GB     | 1209:5bf0        | v2.0.4      | Cythion/LUNA (16d0:05a5) |

The survey's names and addresses are retired (before the one-VLAN-per-port scheme). The 2026-08-30 hardware
inventory sheet places the Fomu and its OpenVizsla (was pi17) at switch 1 port 17, and on 6 October 2026
`pi-sw1-p17` passed its check. Each host has a USB protocol analyser inline, so the Fomu's own USB traffic can
be captured: an [OpenVizsla](https://github.com/openvizsla/ov_ftdi) on pi17 and a
[Cythion](https://greatscottgadgets.com/cythion/) running [LUNA](https://github.com/greatscottgadgets/luna)
on pi21. The Fomu has no USB serial device; its UART is on the Pi's header ([Fomu EVT](../boards/fomu-evt.md)).

**Known wrong:** pi21 (the Cythion host) and its Fomu were offline at the survey of 2026-03-17 and have not
been read since.

## Acorn CLE-215+

Acorn cards on Raspberry Pi 5 hosts with M.2 HATs (pi-sw1-p38's host model was not recorded). On 6 October 2026 the Acorn hosts up were
pi-sw2-p46 and pi-sw2-p47 (both passed their check) and pi-sw1-p38 (a card with a PCILeech image, which the
check cannot test) (above). An Acorn is known by its label, not its port: which labelled card is on which
host, its state, what it still needs and its cable faults are on [Acorns at
welland](../boards/acorn/installations/welland.md), the one place that list is kept.

## Arty A7-35T

Surveyed 2026-03-17. Five boards, on RPi 4 / 3B+ hosts with PMOD HATs.

| Host | Switch Port | RPi MAC           | RPi Model   | Arty Serial         | Arty DNA           | USB Ethernet                     | Serial Devices   |
| ---- | ----------- | ----------------- | --------------- | ------------------- | ------------------ | -------------------------------- | ---------------- |
| pi7  | p7          | e4:5f:01:96:f8:a5 | RPi 4 2 GB       | 210319B301DE        | 0x00628502251ea85c | ASIX AX88179 (f8:e4:3b:0f:c1:e6) | ttyUSB0, ttyUSB1 |
| pi9  | p9          | b8:27:eb:86:39:63 | RPi 3B+ 1 GB     | (FTDI disconnected) | —                  | Apple Eth (48:d7:05:e9:40:52)    | **none**         |
| pi11 | p11         | e4:5f:01:8d:f7:17 | RPi 4 8 GB       | 210319B3E5C5        | 0x002c8d02251ea854 | DM9601 (00:e0:4c:53:44:58)       | ttyUSB0, ttyUSB1 |
| pi13 | p13         | b8:27:eb:6d:27:f6 | RPi 3B+ 1 GB     | 210319A43ADB        | 0x0002f54832290854 | ASIX (8a:ce:4c:ff:ae:83)         | ttyUSB0, ttyUSB1 |
| pi26 | p26         | e4:5f:01:97:1f:7e | RPi 4 2 GB       | 210319B0C238        | 0x0144cd2a47442854 | Linksys GbE (60:38:e0:e3:56:4f)  | ttyUSB0, ttyUSB1 |

These names, and their addresses `10.21.0.1NN` for `piNN`, are retired: the switch ports are flat numbers from before the one-VLAN-per-port
scheme (`p7` here is not switch 2 port 7, which carries TT07). The 2026-08-30 hardware inventory sheet places
the Arty `210319B3E5C5` (was pi11) at switch 2 port 38. Each Pi also carries a USB Ethernet adapter wired to
the Arty's Ethernet port ([Arty A7](../boards/arty-a7.md)). Source: `lsusb` and `/dev/serial/by-id/` on each
Pi, and dnsmasq's `pibs.conf`, 2026-03-17.

**Known wrong:** no Arty host was up on 6 October 2026, and none has been probed under the current scheme.
pi9's FTDI was disconnected at the survey, so it had no serial device and could not be programmed.

## Tiny Tapeout ASIC boards

Probed 2026-09-03. Six boards on S3300 ports 3–8, on RPi 4 / 3B+ hosts with
PMOD HATs. These carry **real fabricated TT ASIC silicon** on a TT demo board
(RP2040, MicroPython TT SDK) and are the public boards on
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

Firmware: tt04 to tt08 run TT SDK 2.0.4. The tt03p5 chip is not supported by
SDK 2.0 or later, so that board runs demo-board firmware 1.2.2 with a
hand-pushed `/shuttles/tt03p5.json` and `rom_fallback.txt`, and its page is
camera-first.

Source: live probe 2026-09-03 (`lsusb`, `/dev/serial/by-id`, `fuser
/dev/ttyACM0`, daemon `/health`); firmware versions from the 2026-08-23 reflash
session; catalogue = `tt_boards` in infra `host_vars/fpgas.online.yml`.

**Known wrong:**

- None of these hosts was up on 6 October 2026.
- pi-sw2-p3 (tt03p5): the web Commander does not support demo-board firmware 1.2.x, so that board is
  camera-only until the Commander's `legacy` branch is ported (fpgas-online/tt-commander-app
  [#9](https://github.com/fpgas-online/tt-commander-app/pull/9) and
  [#10](https://github.com/fpgas-online/tt-commander-app/pull/10)).

## Tiny Tapeout FPGA demo boards

Probed 2026-09-03. Four boards on S3300 ports 33–36, on RPi 4 hosts with PMOD
HATs. These carry an **iCE40UP5K FPGA** (FabricFox breakout) that emulates Tiny
Tapeout designs, on a TT demo board **v3 (RP2350B)** running TT SDK **3.1.0**
(reflashed 2026-08-23). They are **not** ASIC boards. Public as `fpga-1` …
`fpga-4` on tinytapeout.fpgas.online since 2026-08-24, where users can run
bundled demos or upload their own bitstream.

| Host       | Slug   | Switch Port | IP         | RPi MAC           | RPi Model (rev)              | USB VID:PID | RP2350 Serial    | Old name |
| ---------- | ------ | ----------- | ---------- | ----------------- | ---------------------------- | ----------- | ---------------- | -------- |
| [pi-sw2-p33](https://welland.fpgas.online/fpgas/pi-sw2-p33.html) | [fpga-1](https://tinytapeout.fpgas.online/board/fpga-1/) | sw2 p33 | 10.21.2.33 | e4:5f:01:97:0e:77 | RPi 4 2 GB Rev 1.5 (b03115) | 2e8a:0005 | 4df39a7a6856f86f | pi27 |
| [pi-sw2-p34](https://welland.fpgas.online/fpgas/pi-sw2-p34.html) | [fpga-2](https://tinytapeout.fpgas.online/board/fpga-2/) | sw2 p34 | 10.21.2.34 | e4:5f:01:97:27:f2 | RPi 4 2 GB Rev 1.5 (b03115) | 2e8a:0005 | fd1a167bd863a198 | pi29 |
| [pi-sw2-p35](https://welland.fpgas.online/fpgas/pi-sw2-p35.html) | [fpga-3](https://tinytapeout.fpgas.online/board/fpga-3/) | sw2 p35 | 10.21.2.35 | e4:5f:01:97:0c:e3 | RPi 4 2 GB Rev 1.5 (b03115) | 2e8a:0005 | 8c46329b33590ecb | pi31 |
| [pi-sw2-p36](https://welland.fpgas.online/fpgas/pi-sw2-p36.html) | [fpga-4](https://tinytapeout.fpgas.online/board/fpga-4/) | sw2 p36 | 10.21.2.36 | e4:5f:01:8e:02:27 | RPi 4 8 GB Rev 1.5 (d03115) | 2e8a:0005 | a2961e5cac65b25f | pi33 |

Each RPi connects to its board over USB-C, has a Digilent Pmod HAT for
GPIO-level control of the TT I/O pins, and an ov5647 camera publishing a live
feed. Like the ASIC boards they appear as "MicroPython Board in FS mode" with
the `/dev/ttboard` symlink, and the `fpgas-tt` daemon owns the port. Each
board's `status.json` (for example
`https://tinytapeout.fpgas.online/board/fpga-1/status.json`) reports the daemon's
`/health` plus `reachable`, and is the quickest liveness check. See
[Tiny Tapeout FPGA demo board](../boards/tt-fpga.md) for the firmware.

Source: live probe 2026-09-03 (`lsusb`, `/dev/serial/by-id`, daemon `/health`). On 6 October 2026 the gateway saw
port 35 answer from `e4:5f:01:8e:02:27` and port 36 from `e4:5f:01:97:0c:e3`, the other way round from this
table: the two Pis have changed ports since, or the table had them swapped. Not resolved.

**Known wrong:** pi-sw2-p34 (fpga-2) was not up on 6 October 2026.

## Orange Pis

Orange Pi PC boards on switch 2, booted over USB from a hub host; they carry no FPGA. On 6 October 2026
four of them, pi-sw2-p19, -p21, -p22 and -p24, came back after the root update. How they boot, which is
where, and what to do when one does not come back: [Orange Pi H3 hosts](../setup/orange-pi.md).

## Retired and unlocated hosts

Hosts in the 2026-03-17 survey that have not been found under the current scheme; their addresses no longer
resolve.

| Host | MAC | Old address | Notes |
|---|---|---|---|
| pi1 | b8:27:eb:ec:c2:c9 | 10.21.0.101 | Pi 3B+ 1 GB; was the always-on NFS maintenance host (read-write) |
| pi44 | dc:a6:32:b4:5e:c9 | 10.21.0.144 | not connected at the survey |

`https://welland.fpgas.online/fpgas/pi37.html`, `pi42.html` and `pi16.html` answered on 2026-09-03 although
no host here is on switch 2 port 37 or 42, and pi16 is a retired NeTV2 name: either hosts nobody has
documented or pages the site should stop serving.
