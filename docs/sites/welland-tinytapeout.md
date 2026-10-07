# Tiny Tapeout boards at welland

**You look after welland and want to know which Tiny Tapeout board is on which host, what each runs, and what
is known wrong with it.** What was up on 6 October 2026, with each port's MAC, is on [Hosts and boards at
welland](welland-boards.md#what-was-up-on-6-october-2026). These boards are public on
[tinytapeout.fpgas.online](https://tinytapeout.fpgas.online).

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

