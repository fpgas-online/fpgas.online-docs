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

From `/etc/dnsmasq.d/pibs.conf` on val2, as copied into the site notes; not probed by us. The site notes give
no date or source for the `Status` column. Board pages: `https://ps1.fpgas.online/fpgas/piN.html`.

```{rst-class} nowrap
```

| Host | Port | Address | Pi MAC | Pi model | Arty serial | USB Ethernet | Status |
|---|---|---|---|---|---|---|---|
| [pi2](https://ps1.fpgas.online/fpgas/pi2.html) | e2 | 10.21.0.102 | b8:27:eb:2f:5d:08 | 3B Rev 1.2 | 210319B301E0 | Apple A1277 (MAC not recorded) | Offline |
| [pi3](https://ps1.fpgas.online/fpgas/pi3.html) | e3 | 10.21.0.103 | dc:a6:32:05:32:45 | 4B Rev 1.1 | 210319A43AD3 | ASIX AX88179 (00:05:1b:b0:47:9d) | Online |
| [pi5](https://ps1.fpgas.online/fpgas/pi5.html) | e5 | 10.21.0.105 | b8:27:eb:d4:f1:74 | 3B Rev 1.2 | 210319B58381 | ASIX AX88179 (f8:e4:3b:a6:a8:62) | Online |
| [pi7](https://ps1.fpgas.online/fpgas/pi7.html) | e7 | 10.21.0.107 | b8:27:eb:33:51:27 | 3B+ Rev 1.3 | 210319A764F5 | ASIX AX88179 (00:05:1b:b0:46:51) | Online |
| [pi9](https://ps1.fpgas.online/fpgas/pi9.html) | e9 | 10.21.0.109 | b8:27:eb:a3:51:b4 | 3B+ Rev 1.3 | 210319B58379 | ASIX AX88179 (f8:e4:3b:a0:55:af) | Online |
| [pi11](https://ps1.fpgas.online/fpgas/pi11.html) | e11 | 10.21.0.111 | b8:27:eb:51:01:df | 3B Rev 1.2 | 210319B5835B | ASIX AX88179 (f8:e4:3b:a6:c6:a9) | Online |
| [pi13](https://ps1.fpgas.online/fpgas/pi13.html) | e13 | 10.21.0.113 | b8:27:eb:68:fc:e7 | 3B Rev 1.2 | 210319B3E5C3 | ASIX AX88179 (f8:e4:3b:a6:cf:b1) | Online |
| pi17 | e17 | 10.21.0.117 | b8:27:eb:5f:de:85 | 3B Rev 1.2 | 210319B58370 | ASIX AX88179 (f8:e4:3b:a6:c6:10) | Online |

Every Arty connects through its FTDI FT2232 (`0403:6010`), which gives the host `/dev/ttyUSB0` for JTAG and
`/dev/ttyUSB1` for the 115200-baud console; a second USB Ethernet adapter on each Pi is wired to the Arty's own
Ethernet port ([Arty A7](../boards/arty-a7.md)). The Arty hosts are the ones with cameras: the public pages
carry live feeds of their LEDs. Which Pi holds which camera is not recorded.

**Known wrong with an Arty host:**

- **pi2**: recorded Offline. The switch read of 2026-08-31 shows its port e2 with link up and PoE delivering,
  so "offline" is the host, not the cable. It is the only host with an Apple A1277 adapter, and that
  adapter's MAC was never recorded.

:::{todo}
These rows are configuration, not measurement. Probe the eight Arty hosts, record the date, and note where a
camera is fitted.
:::

## Compute blades

Four [Compute Blades](https://computeblade.com/), each with a Raspberry Pi Compute Module, netbooted from
val2's trixie root. Which Acorn card is in which blade, its state and what each still needs: [Acorns at
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
port `ttyAMA0` (`console=ttyAMA0,115200`), with a login on that port, and with GPIO14 and GPIO15 as that
port's TXD0 and RXD0. A CM4 and a CM5 are not interchangeable: what differs (the serial mux, how many UARTs) is under
[Compute Module 4 versus Compute Module 5](../setup/pi.md#compute-module-4-versus-compute-module-5). No blade
has a camera.

**Known wrong with a blade:**

- **pi14 and pi16 did not answer JTAG on any pin order on 2026-09-20.** All 24 orders of the four GPIOs were
  tried. GPIO4 (TCK) showed a pull-up only on pi20; on pi14 and pi16 it floated as it does on pi18, whose
  slot is empty. TCK is a dedicated JTAG pin that no design drives, so that pull-up is the Acorn's own and
  should be there whenever the connector is mated. Both cards enumerated over PCIe that day, so they were alive:
  reseating the JTAG cable (P1) is the thing to try. Their serial (P2) is untested until JTAG works.
- **With the serial port on, JTAG cannot run on any blade**: the serial driver holds GPIO14, which is also
  JTAG's TMS. That has been the boot configuration of all four since at least 2026-10-07 (above). pi20's
  JTAG test of 7 October 2026 and what it needs are on [Acorns at
  ps1](../boards/acorn/installations/ps1.md).

## Other hosts

From `pibs.conf` and the switch read of 2026-08-31, via the site notes.

| Host | Port | Address | Pi MAC | Pi model | What it is | Status |
|---|---|---|---|---|---|---|
| pi19 | e19 | 10.21.0.119 | b8:27:eb:0c:f8:43 | 3B | no board | Dead |
| [pi21](https://ps1.fpgas.online/fpgas/pi21.html) | e21 | 10.21.0.121 | 2c:cf:67:39:18:66 | 5 Rev 1.0, 4 GB | no FPGA; a development host | Online |
| pi24 | — | 10.21.0.124 | b8:27:eb:85:ab:d9 | not recorded | registered, on no port | Offline |

**Known wrong:**

- **pi19**: dead hardware. Its port e19 shows link up and PoE delivering on 2026-08-31, so it is the host,
  not the cable.
- **pi24**: in `pibs.conf` at 10.21.0.124, on no switch port, offline; its model is not recorded.

## Pending

No Tiny Tapeout board is installed at ps1. Four Tiny Tapeout FPGA demo boards and seven Tiny Tapeout ASIC
boards (one each of TT02 to TT09 except TT08) are allocated; host, port, address and serial are not yet
known (probed live 2026-09-03; the site notes' board summary). The Acorn for pi18's empty slot is pending
too. See [Tiny Tapeout FPGA demo board](../boards/tt-fpga.md) and [Tiny Tapeout ASIC
boards](../boards/tt-asic.md).
