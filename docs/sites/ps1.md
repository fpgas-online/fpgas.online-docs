# PS1

The public deployment at [Pumping Station: One](https://pumpingstationone.org/)
in Chicago, published as
[ps1.fpgas.online](https://ps1.fpgas.online/fpgas/) and run by Carl Karsten.
Eight Arty A7 boards on Raspberry Pi 3B/3B+/4B hosts, and four Raspberry Pi
Compute Modules on [Compute Blade](https://computeblade.com/) carriers with SQRL
Acorn boards in the M.2 slot.

Of the four [blades](#compute-blades), **pi14**, **pi16** and **pi20** carry an
Acorn; **pi18**'s M.2 slot is empty.

## Gateway: val2

From the site notes and the infra `host_vars/ps1.fpgas.online.yml`; not
re-probed.

| Property   | Value |
| ---------- | ----- |
| Hostname   | val2 |
| Public DNS | ps1.fpgas.online |
| OS         | Debian 12 (bookworm) |
| Kernel     | 6.1.0-40-amd64 |
| eth-uplink | 76.227.131.147/25 (public internet) |
| eth-local  | 10.21.0.1/24 (RPi network) |
| Web server | nginx (reverse proxy for web SSH + video streams) |
| PoE switch | Netgear FS728TPv2 at 10.21.0.200 |
| Time zone  | America/Chicago |
| SSH access | `ssh root@ps1.fpgas.online` |

Two NFS roots, because the site runs two generations of hardware:

- **bookworm** (armhf): `/srv/nfs/rpi/bookworm/{boot,root}` — RPi 3B/3B+/4B,
  read-only with overlayroot.
- **trixie** (arm64): `/srv/nfs/rpi/trixie/{boot,root}` — the Compute Blades,
  kernel 6.12.75+rpt-rpi-v8.

:::{warning}
Both roots are read-only NFS exports with a tmpfs overlay, so anything staged
under `/home/pi` is gone after a reboot or a PoE cycle — see [The NFS root is
shared and read-only](../setup/netboot.md#the-nfs-root-is-shared-and-read-only)
for the symptom and what to do about it.
:::

val2 is a flat `/24` with the legacy `piNN` / `10.21.0.1NN` naming. Welland's
VLAN-per-port scheme has not been applied here, so a Pi's identity still comes
from its MAC rather than from the port it is plugged into. dnsmasq hands
10.21.0.128–10.21.0.254 to anything it does not recognise, on a six-hour lease;
every documented host is a static reservation below that range.

## Hosts and boards

Probed 2026-08-31. Hosts are in the natural sort order of
`/etc/dnsmasq.d/pibs.conf` on val2, and the switch port for `piNN` is `eNN`.
The Arty A7 rows are the exception — they were not re-probed.

Programming commands for each board type live on the board pages; see
[Boards](../boards/index.md).

### Boards

Counts as of 2026-08-31; the Arty rows are from configuration, not a probe. The
pending counts are allocations, not hardware on site.

| Board Type    | Deployed | Pending | Hosts                     |
|---------------|----------|---------|---------------------------|
| Arty A7-35T   | ×8       | —       | [pi2](https://ps1.fpgas.online/fpgas/pi2.html), [pi3](https://ps1.fpgas.online/fpgas/pi3.html), [pi5](https://ps1.fpgas.online/fpgas/pi5.html), [pi7](https://ps1.fpgas.online/fpgas/pi7.html), [pi9](https://ps1.fpgas.online/fpgas/pi9.html), [pi11](https://ps1.fpgas.online/fpgas/pi11.html), [pi13](https://ps1.fpgas.online/fpgas/pi13.html), pi17 |
| LiteFury / Acorn CLE-101 | ×3 | ×1 | pi14, pi16, pi20 (pending: pi18, M.2 empty) |
| TT FPGA Demo  | —        | ×4      | TBD                       |
| TT ASIC       | —        | ×7      | TBD (one each: TT02-TT09 except TT08) |

Source: the FPGA board summary in `site-ps1.md`.

### Arty A7 hosts

Configuration from `/etc/dnsmasq.d/pibs.conf`. Eight boards, on RPi 3B / 3B+ /
4B hosts. The source gives no provenance or date for the `Status` column.

```{rst-class} nowrap
```

| Host | Switch Port | IP          | RPi MAC           | RPi Model       | Arty Serial  | USB Ethernet                     | Status  |
|------|------|-------------|-------------------|-----------------|--------------|----------------------------------|---------|
| [pi2](https://ps1.fpgas.online/fpgas/pi2.html)   | e2   | 10.21.0.102 | b8:27:eb:2f:5d:08 | RPi 3B Rev 1.2  | 210319B301E0 | Apple A1277 (no MAC recorded)    | Offline |
| [pi3](https://ps1.fpgas.online/fpgas/pi3.html)   | e3   | 10.21.0.103 | dc:a6:32:05:32:45 | RPi 4B Rev 1.1  | 210319A43AD3 | ASIX AX88179 (00:05:1b:b0:47:9d) | Online  |
| [pi5](https://ps1.fpgas.online/fpgas/pi5.html)   | e5   | 10.21.0.105 | b8:27:eb:d4:f1:74 | RPi 3B Rev 1.2  | 210319B58381 | ASIX AX88179 (f8:e4:3b:a6:a8:62) | Online  |
| [pi7](https://ps1.fpgas.online/fpgas/pi7.html)   | e7   | 10.21.0.107 | b8:27:eb:33:51:27 | RPi 3B+ Rev 1.3 | 210319A764F5 | ASIX AX88179 (00:05:1b:b0:46:51) | Online  |
| [pi9](https://ps1.fpgas.online/fpgas/pi9.html)   | e9   | 10.21.0.109 | b8:27:eb:a3:51:b4 | RPi 3B+ Rev 1.3 | 210319B58379 | ASIX AX88179 (f8:e4:3b:a0:55:af) | Online  |
| [pi11](https://ps1.fpgas.online/fpgas/pi11.html) | e11  | 10.21.0.111 | b8:27:eb:51:01:df | RPi 3B Rev 1.2  | 210319B5835B | ASIX AX88179 (f8:e4:3b:a6:c6:a9) | Online  |
| [pi13](https://ps1.fpgas.online/fpgas/pi13.html) | e13  | 10.21.0.113 | b8:27:eb:68:fc:e7 | RPi 3B Rev 1.2  | 210319B3E5C3 | ASIX AX88179 (f8:e4:3b:a6:cf:b1) | Online  |
| pi17 | e17  | 10.21.0.117 | b8:27:eb:5f:de:85 | RPi 3B Rev 1.2  | 210319B58370 | ASIX AX88179 (f8:e4:3b:a6:c6:10) | Online  |

Every Arty connects through an FTDI FT2232C/D/H (`0403:6010`), which gives the
host `/dev/ttyUSB0` for JTAG and `/dev/ttyUSB1` for the 115200-baud console.
Each RPi also carries a separate USB Ethernet adapter wired to the Arty's own
Ethernet port. See [Arty A7](../boards/arty-a7.md).

The Arty boards are the ones with a camera: the public pages carry live feeds of
their LEDs. The source records no per-host camera inventory for PS1, so which
Pi holds which camera is not documented — but no blade has one.

:::{todo}
These rows are configuration, not measurement. Nothing here has been probed
live, and the source does not say where the `Status` column came from or when.
Probe the eight Arty hosts, record the date, and note where a camera is fitted.
:::

Source: `/etc/dnsmasq.d/pibs.conf` on val2, via `site-ps1.md`; `Status` column
provenance unknown.

### Compute blades

Probed 2026-08-31; all four were up, with 37 days of uptime.

```{rst-class} nowrap
```

| Host | Switch Port | IP          | RPi MAC           | RPi Model             | Board (PCIe ID)             | FPGA DNA           | PCIe Bus | JTAG (P1)                | P2 serial             | Status |
|------|------|-------------|-------------------|-----------------------|-----------------------------|--------------------|----------|--------------------------|-----------------------|--------|
| pi14 | e14  | 10.21.0.114 | 2c:cf:67:37:d4:bd | CM4 Rev 1.1 4 GB      | Acorn CLE-101 `1e24:0101`   | unreadable         | 0000:01  | no response (P1 unmated) | untested              | Online |
| pi16 | e16  | 10.21.0.116 | 2c:cf:67:fb:91:e5 | CM5 Lite Rev 1.0 8 GB | Acorn CLE-101 `1e24:0101`   | unreadable         | 0001:01  | no response (P1 unmated) | untested              | Online |
| pi18 | e18  | 10.21.0.118 | 2c:cf:67:37:d5:08 | CM4 Rev 1.1 4 GB      | none — M.2 slot empty       | —                  | —        | n/a                      | n/a                   | Online |
| pi20 | e20  | 10.21.0.120 | 2c:cf:67:fd:1e:be | CM5 Lite Rev 1.0 8 GB | XC7A100T design `10ee:7011` | 0x0028e5c45e304854 | 0001:01  | OK                       | OK, crossover present | Online |

pi20 is the only blade whose JTAG has ever answered, so it is the only one with
a device DNA: `0x0028e5c45e304854`, an XC7A100T.

:::{note}
Earlier revisions of the source table put pi20's DNA in pi14's row (commit
c5322ad wrote it one row up) and listed pi20 as pending. pi14's JTAG has never
answered, so no DNA can have come from it.
:::

These boards have long been called LiteFury. The factory PCI ID that pi14 and
pi16 still present identifies them as SQRL Acorn CLE-101 — the same PCB family,
XC7A100T with 512 MB of DDR3. See [SQRL Acorn](../boards/acorn/index.md).

These four are Compute Blade carriers, so they are wired to the [Compute Blade
variant](../boards/acorn/wiring.md#compute-blade-wiring-variant) of the Acorn
pinout: both connectors on the expansion module port, JTAG on
`--pins 2:3:4:14`, and the FPGA UART on `/dev/ttyAMA0` at GPIO14/15. All four
netboot the trixie arm64 NFS root with overlayroot and run **openFPGALoader
0.13.1** — so `--read-dna` works here, unlike Welland. All four have
`console=tty1` with `serial-getty@ttyAMA0` inactive, so the [kernel console
SysRq
crash](../boards/acorn/wiring.md#known-issue-kernel-console-sysrq-on-the-fpga-uart)
cannot recur. PCIe is through the M.2 slot. The per-pin measurements behind the
JTAG and P2 columns are on [Acorn wiring](../boards/acorn/wiring.md).

The `RPi Model` column matters: a CM4 and a CM5 are not interchangeable, and
what differs — the serial mux, and how many UARTs there are — is under [Compute
Module 4 versus Compute Module
5](../setup/pi.md#compute-module-4-versus-compute-module-5).

:::{warning}
Reconfiguring the FPGA over JTAG while its PCIe endpoint is enumerated is a
surprise removal. Detach the endpoint first, using the host's own bus from the
`PCIe Bus` column above — `0000:01:00.0` on pi14, `0001:01:00.0` on pi16 and
pi20:

```console
$ echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove
```

Restore it with `/sys/bus/pci/rescan`, or by rebooting. `--detect` and the other
read-only queries are safe without this; **loading a bitstream is not**.
:::

:::{note}
This crash was measured at Welland, not here: on 2026-08-31 an undetached load
crashed a Pi 5's BCM2712 root complex outright. No PS1 blade has been recorded
hitting it, and pi20 is the only one where the combination can arise today,
since pi14 and pi16 do not answer JTAG at all.
:::

:::{note}
The blades have no page under `https://ps1.fpgas.online/fpgas/` — pi14, pi16,
pi18 and pi20 all return 404 (checked 2026-09-03). Only the linked hosts above
are published.
:::

Source: live probe 2026-08-31 via `site-ps1.md` and `acorn.md`; JTAG and P2
columns from the 2026-08-31 pin-ID survey; MACs and switch ports cross-checked
against infra `host_vars/ps1.fpgas.online.yml`.

### Other hosts

From `pibs.conf` and the 2026-08-31 switch dump.

```{rst-class} nowrap
```

| Host | Switch Port | IP          | RPi MAC           | RPi Model         | Notes                      | Status  |
|------|------|-------------|-------------------|--------------------|----------------------------|---------|
| pi19 | e19  | 10.21.0.119 | b8:27:eb:0c:f8:43 | RPi 3B             | Dead hardware              | Dead    |
| [pi21](https://ps1.fpgas.online/fpgas/pi21.html) | e21  | 10.21.0.121 | 2c:cf:67:39:18:66 | RPi 5 Rev 1.0 4 GB | No FPGA, development host  | Online  |
| pi24 | —    | 10.21.0.124 | b8:27:eb:85:ab:d9  | (unknown)          | Registered but not on switch | Offline |

`Dead` and `Offline` describe the host, not the cable. The 2026-08-31 switch
dump shows e19 with link up and PoE delivering, yet pi19 does not respond; pi24
is not on the switch at all. Nothing in the sources reconciles the two, so both
readings are recorded as they were taken.

Source: `/etc/dnsmasq.d/pibs.conf` on val2 and the 2026-08-31 switch dump, via
`site-ps1.md`.

### Pending

Probed live 2026-09-03; the PS1 rows were still TBD at that probe. Four Tiny
Tapeout FPGA demo boards are allocated to PS1 and not yet installed. The source
inventory carries four identical rows for them — host, switch port, IP, RPi MAC
and RP2350 serial are all TBD, and there is no board page yet:

```{rst-class} nowrap
```

| Site | Board | Count | Host | Switch Port | IP | RPi MAC | RP2350 Serial | Board page |
|---|---|---|---|---|---|---|---|---|
| PS1 | Tiny Tapeout FPGA demo | ×4 | TBD | TBD | TBD | TBD | TBD | — |

Seven Tiny Tapeout ASIC boards are pending as well (one each for TT02-TT09
except TT08), and pi18's M.2 slot is still waiting for an Acorn. See
[Tiny Tapeout FPGA demo board](../boards/tt-fpga.md) and
[Tiny Tapeout ASIC boards](../boards/tt-asic.md).

Source: the deployment table in `tt-fpga.md` (probed live 2026-09-03) and the
board summary in `site-ps1.md`.

## PoE switch

Read 2026-08-31. One **Netgear FS728TPv2** at 10.21.0.200: 24 Fast Ethernet
ports (`e1`–`e24`) and 4 Gigabit ports (`g25`–`g28`). LLDP puts val2 on `g25`,
and upstream of that is a Ubiquiti US-24-G1 (`PS1-SW-MODEM`).

| Port | Link | PoE        | Host | FPGA Board | Notes                      |
|------|------|------------|------|------------|----------------------------|
| e1   | down | searching  |      |            | Cable present, no device   |
| e2   | UP   | delivering | [pi2](https://ps1.fpgas.online/fpgas/pi2.html)  | Arty A7    | Offline                    |
| e3   | UP   | delivering | [pi3](https://ps1.fpgas.online/fpgas/pi3.html)  | Arty A7    |                            |
| e4   | down | searching  |      |            | Cable present, no device   |
| e5   | UP   | delivering | [pi5](https://ps1.fpgas.online/fpgas/pi5.html)  | Arty A7    |                            |
| e6   | down | disabled   |      |            | Arty Ethernet test port    |
| e7   | UP   | delivering | [pi7](https://ps1.fpgas.online/fpgas/pi7.html)  | Arty A7    |                            |
| e8   | down | disabled   |      |            | Arty Ethernet test port    |
| e9   | UP   | delivering | [pi9](https://ps1.fpgas.online/fpgas/pi9.html)  | Arty A7    |                            |
| e10  | down | disabled   |      |            | Arty Ethernet test port    |
| e11  | UP   | delivering | [pi11](https://ps1.fpgas.online/fpgas/pi11.html) | Arty A7    |                            |
| e12  | down | disabled   |      |            | Arty Ethernet test port    |
| e13  | UP   | delivering | [pi13](https://ps1.fpgas.online/fpgas/pi13.html) | Arty A7    |                            |
| e14  | UP   | delivering | pi14 | LiteFury   | CM4 Compute Blade          |
| e15  | down | delivering |      |            | PoE on, no link            |
| e16  | UP   | delivering | pi16 | LiteFury   | CM5 Lite Compute Blade     |
| e17  | UP   | delivering | pi17 | Arty A7    |                             |
| e18  | UP   | delivering | pi18 | (pending)  | CM4 Compute Blade, M.2 empty |
| e19  | UP   | delivering | pi19 |            | Dead hardware              |
| e20  | UP   | delivering | pi20 | LiteFury   | CM5 Lite Compute Blade (up since 2026-07) |
| e21  | UP   | delivering | [pi21](https://ps1.fpgas.online/fpgas/pi21.html) |            | RPi 5, no FPGA             |
| e22  | down | disabled   |      |            |                            |
| e23  | down | searching  |      |            | Cable present, no device   |
| e24  | down | searching  |      |            | Cable present, no device   |
| g25  | UP   | —          | val2 |            | Server uplink              |
| g26  | down | —          |      |            |                            |
| g27  | down | —          |      |            |                            |
| g28  | down | —          |      |            |                            |

The even-numbered ports between Arty hosts (e6, e8, e10, e12) carry the Artys'
own Ethernet adapters, which is why PoE is disabled on them.

:::{todo}
The infra `host_vars/ps1.fpgas.online.yml` names three switch models in its
comments — HP ProCurve 2610-24-PWR J9087A, Netgear GS728TPP and Netgear
FS728TPv2 — with no note saying which is installed. The live PoE OID and the
recorded management MAC both match the FS728TPv2, which is what this page says.
Confirm it against the physical unit and delete the other two comments.
:::

### Power control

The Netgear FS728TPv2 at `10.21.0.200` does **not** answer the standard PoE
MIB. It uses a Netgear-private OID under a draft of the spec:

```
1.3.6.1.4.1.4526.11.16.1.1.1.3.1     # not 1.3.6.1.2.1.105.1.1.1.3
```

The working path is on the server (`val2`):

```console
$ set -a; . /etc/environment.export; set +a
$ /srv/www/pib/venv/bin/python3 \
    /srv/www/pib/venv/lib/python3.13/site-packages/snmp_switch/utils.py 20 2  # off
$ /srv/www/pib/venv/bin/python3 \
    /srv/www/pib/venv/lib/python3.13/site-packages/snmp_switch/utils.py 20 1  # on
```

`1` is on, `2` is off; omit the value to read the current state. A blade takes
about 60 seconds to come back.

## Public site

PS1 is the public site. `https://ps1.fpgas.online/fpgas/` serves a page per
board — web SSH terminal, reset button, bitstream upload, PoE power cycle, and
an HLS video feed at `/live/piN.m3u8` — all behind nginx on val2. How that is
built and deployed is in [The web application](../setup/webapp.md).

## Known faults

- **pi14 and pi16 do not respond to JTAG on any pin order.** All 24 permutations
  of the four available GPIOs were tried. GPIO4 (TCK) shows a pull-up only on
  pi20; on pi14 and pi16 it floats exactly as it does on pi18, whose M.2 slot is
  empty. TCK is a dedicated JTAG pin that no design can drive, so that pull-up
  is the Acorn's own and should be present whenever the connector is mated.
  Both boards enumerate over PCIe, so the boards are alive — reseating P1 is the
  thing to try. Their P2 serial is untested until JTAG works.
- **pi2** (Arty A7): recorded Offline. Port e2 shows link up and PoE delivering
  in the 2026-08-31 switch dump, so "offline" is the host, not the link. pi2 is
  also the only host with an Apple A1277 USB Ethernet adapter rather than an
  ASIX AX88179, and its adapter MAC was never recorded.
- **pi19**: dead hardware. Port e19 likewise shows link up and PoE delivering,
  so again this is the host and not the cable.
- **pi24**: registered in `pibs.conf` at 10.21.0.124 but on no switch port, and
  offline. Its model is unknown.
- **e15**: PoE is delivering into a port with no link.
- No cameras on any blade. The camera feeds on the public pages are the Arty
  boards'.
