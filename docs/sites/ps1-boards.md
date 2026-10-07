# Hosts and boards at ps1

**You want to know which board is on which host at ps1, what state each host was last seen in, and what is
known wrong with it.** Each table says when it was read and from where. A host at ps1 is named with its site
("pi20 at ps1"); a bare `piNN` on this page always means the ps1 host. Logging in and the gateway are on
[PS1](ps1.md) and [The ps1 gateway and switch](ps1-gateway.md).

The hosts are named after the switch port they are cabled to: `piNN` is on port `eNN`, at `10.21.0.1NN`.
ps1 still recognises a Pi by its MAC (its legacy scheme; [Network and power](../setup/network.md)), so a Pi
moved to another port keeps its name.

## Boards

Counts as of 2026-08-31, from the board summary in the site notes (`docs/hardware/site-ps1.md` in
fpgas.online-test-designs). The Arty rows are configuration, not a probe. Pending counts are allocations, not
hardware on site.

| Board | Installed | Pending | Hosts |
|---|---|---|---|
| Arty A7-35T | 8 | — | pi2, pi3, pi5, pi7, pi9, pi11, pi13, pi17 |
| Acorn CLE-101 (the site notes say LiteFury) | 3 | 1 | pi14, pi16, pi20; pi18's M.2 slot is empty |
| Tiny Tapeout FPGA demo board | — | 4 | none yet |
| Tiny Tapeout ASIC board | — | 7 | none yet (one each of TT02 to TT09 except TT08) |

## Arty A7 hosts

The hosts, MACs, models, serials and adapters are the site notes' (their copy of the gateway's `pibs.conf`,
undated); fpgas.online has not probed these hosts. The last column is the gateway read of 6 October 2026 ([The
ps1 gateway and switch](ps1-gateway.md#gateway-val2)): a lease, or an answer to the gateway's ARP (pi3's
neighbour entry was stale). On
7 October 2026 ps1.fpgas.online listed board pages for pi2, pi3, pi5, pi7, pi9, pi11, pi13, pi21 and pi23
(`https://ps1.fpgas.online/fpgas/`); pi23 is on no table here, and pi17 has no page.

| Host | Port | Address | Pi MAC | Pi model | Arty serial | USB Ethernet | Seen 2026-10-06 |
|---|---|---|---|---|---|---|---|
| [pi2](https://ps1.fpgas.online/fpgas/pi2.html) | e2 | 10.21.0.102 | b8:27:eb:2f:5d:08 | 3B Rev 1.2 | 210319B301E0 | Apple A1277 (MAC not recorded) | no |
| [pi3](https://ps1.fpgas.online/fpgas/pi3.html) | e3 | 10.21.0.103 | dc:a6:32:05:32:45 | 4B Rev 1.1 | 210319A43AD3 | ASIX AX88179 (00:05:1b:b0:47:9d) | lease only |
| [pi5](https://ps1.fpgas.online/fpgas/pi5.html) | e5 | 10.21.0.105 | b8:27:eb:d4:f1:74 | 3B Rev 1.2 | 210319B58381 | ASIX AX88179 (f8:e4:3b:a6:a8:62) | no |
| [pi7](https://ps1.fpgas.online/fpgas/pi7.html) | e7 | 10.21.0.107 | b8:27:eb:33:51:27 | 3B+ Rev 1.3 | 210319A764F5 | ASIX AX88179 (00:05:1b:b0:46:51) | no |
| [pi9](https://ps1.fpgas.online/fpgas/pi9.html) | e9 | 10.21.0.109 | b8:27:eb:a3:51:b4 | 3B+ Rev 1.3 | 210319B58379 | ASIX AX88179 (f8:e4:3b:a0:55:af) | no |
| [pi11](https://ps1.fpgas.online/fpgas/pi11.html) | e11 | 10.21.0.111 | b8:27:eb:51:01:df | 3B Rev 1.2 | 210319B5835B | ASIX AX88179 (f8:e4:3b:a6:c6:a9) | no |
| [pi13](https://ps1.fpgas.online/fpgas/pi13.html) | e13 | 10.21.0.113 | b8:27:eb:68:fc:e7 | 3B Rev 1.2 | 210319B3E5C3 | ASIX AX88179 (f8:e4:3b:a6:cf:b1) | no |
| pi17 | e17 | 10.21.0.117 | b8:27:eb:5f:de:85 | 3B Rev 1.2 | 210319B58370 | ASIX AX88179 (f8:e4:3b:a6:c6:10) | no; not in `pibs.conf` |

Every Arty connects through its FTDI FT2232 (`0403:6010`): `/dev/ttyUSB0` for JTAG and `/dev/ttyUSB1` for the
115200-baud console; a second USB Ethernet adapter on each Pi is wired to the Arty's own Ethernet port
([Arty A7](../boards/arty-a7.md)). The public pages carry live camera feeds of the Arty boards' LEDs (site
notes; `pi3.html` has its feed, read 7 October 2026). Which Pi holds which camera is not recorded. The earlier docs page
said the Arty hosts are the ones with cameras and that no Compute Blade has one (not re-checked); on a Pi,
`systemctl status fpgas-cam` says whether it streams.

**Known wrong with an Arty host:**

- **On 6 October 2026 the gateway saw only pi3.** pi2, pi5, pi7, pi9, pi11 and pi13 did not answer its ARP,
  and pi17 was not in its `pibs.conf`. Whether they were off, unplugged or failing to boot from the one trixie
  root was not read. The gateway was reinstalled about 25 September 2026.
- **pi2** is recorded Offline in the site notes. It is the only host with an Apple A1277 adapter, whose MAC
  was never recorded.
- **Not probed by fpgas.online.** The rows above are configuration. Probing the eight hosts, with the date,
  and noting where a camera is fitted, is still to do.

## Compute blades

Four [Compute Blades](https://computeblade.com/), each with a Raspberry Pi Compute Module, netbooted from
the gateway's trixie root. Which Acorn card is in which blade, its state and what each still needs: [Acorns at
ps1](../boards/acorn/installations/ps1.md). Every read on each blade, with its date: [Acorns at ps1: what
was read on each blade](../boards/acorn/installations/ps1-reads.md).

```{rst-class} nowrap
```

| Host | Port | Address | Pi MAC | Compute Module | M.2 slot |
|---|---|---|---|---|---|
| pi14 | e14 | 10.21.0.114 | 2c:cf:67:37:d4:bd | CM4 Rev 1.1, 4 GB | Acorn CLE-101 |
| pi16 | e16 | 10.21.0.116 | 2c:cf:67:fb:91:e5 | CM5 Lite Rev 1.0, 8 GB | Acorn CLE-101 |
| pi18 | e18 | 10.21.0.118 | 2c:cf:67:37:d5:08 | CM4 Rev 1.1, 4 GB | empty |
| pi20 | e20 | 10.21.0.120 | 2c:cf:67:fd:1e:be | CM5 Lite Rev 1.0, 8 GB | Acorn CLE-101 |

The table is the probe of 2026-09-20, when all four were online. On 2026-10-07 all four answered the visitor
login and were read again ([Acorns at ps1: what was read on each
blade](../boards/acorn/installations/ps1-reads.md)): every one boots with the kernel console on the serial
port `ttyAMA0` (`console=ttyAMA0,115200`), with a login on that port, and `pinctrl` showed GPIO14 and GPIO15
as that port's TXD0 and RXD0. What differs between a CM4 and a CM5 is under [Compute Module 4 versus Compute Module
5](../setup/pi.md#compute-module-4-versus-compute-module-5).

**Known wrong with a blade:**

- **pi14 and pi16: JTAG has never answered.** On 2026-09-20 neither responded and TCK floated, as it does on
  the empty pi18; on 2026-10-07 pi14's and pi16's TCK again followed the host's pull. The JTAG cable (P1) is
  not mated, or its TCK wire is open: reseat it, or build a new one ([Acorns at
  ps1](../boards/acorn/installations/ps1.md), which has what each blade needs).
- **With the serial port on, JTAG cannot run on any blade**: the serial driver holds GPIO14, which is also
  JTAG's TMS. That has been the boot configuration of all four since at least 2026-10-07 (above). pi20's
  JTAG test of 7 October 2026 and what it needs are on [Acorns at
  ps1](../boards/acorn/installations/ps1.md).

## Other hosts

From the site notes (undated), with the gateway read of 6 October 2026.

| Host | Port | Address | Pi MAC | Pi model | What it is | Seen by the gateway, 2026-10-06 |
|---|---|---|---|---|---|---|
| pi19 | e19 | 10.21.0.119 | b8:27:eb:0c:f8:43 | 3B | dead hardware (site notes) | no; not in `pibs.conf` |
| [pi21](https://ps1.fpgas.online/fpgas/pi21.html) | e21 | 10.21.0.121 | 2c:cf:67:39:18:66 | 5 Rev 1.0, 4 GB (site notes) | no FPGA; a development host | no (in `pibs.conf`) |
| pi24 | none | 10.21.0.124 | b8:27:eb:85:ab:d9 | not recorded | registered, on no port (site notes) | no; not in `pibs.conf` |

**Known wrong:** pi21's model disagrees between sources: the site notes say a Raspberry Pi 5, while the
`switch.nos` entry for port 21 in `host_vars/ps1.fpgas.online.yml` (fpgas.online-infra) says `pi4 tt06`. Nobody
from fpgas.online has looked at the board.

## Pending

No Tiny Tapeout board is installed at ps1. Four Tiny Tapeout FPGA demo boards and seven Tiny Tapeout ASIC
boards (one each of TT02 to TT09 except TT08) are allocated; host, port, address and serial are not yet
known (the site notes' board summary). The Acorn for pi18's empty slot is pending
too. See [Tiny Tapeout FPGA demo board](../boards/tt-fpga.md) and [Tiny Tapeout ASIC
boards](../boards/tt-asic.md).
