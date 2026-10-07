# The ps1 gateway and switch

**You look after val2, the gateway at ps1, and want to know what it serves, which switch port carries which
host, and how to power-cycle one host.** You need root on val2. Which board is on which host, and its faults,
are on [Hosts and boards at ps1](ps1-boards.md).

## Gateway: val2

From the site notes (`docs/hardware/site-ps1.md` in fpgas.online-test-designs) and
`ansible/inventory/host_vars/ps1.fpgas.online.yml` in fpgas.online-infra (main, read 2026-10-07); not read on
val2 by us.

| | |
|---|---|
| Hostname | val2 (Ansible inventory host `ps1.fpgas.online`) |
| Public name | ps1.fpgas.online |
| System | Debian 12 (bookworm), kernel 6.1.0-40-amd64 (site notes) |
| Uplink | `eth-uplink`, 76.227.131.147/25, on the public internet (host_vars) |
| Pi network | `eth-local`, 10.21.0.1/24 (host_vars) |
| Web | nginx: the board pages, the web SSH terminal, the video feeds |
| Switch | Netgear FS728TPv2 at 10.21.0.200 ([below](#poe-switch)) |
| Time zone | America/Chicago (site notes) |
| Administrator login | `ssh root@ps1.fpgas.online` (site notes) |

The Pi network is one flat `/24`. A Pi is recognised by its MAC and handed a reserved address
(`10.21.0.1NN` for the host on port `eNN`); dnsmasq gives 10.21.0.128 to 10.21.0.254 to anything it does not
recognise, on a six-hour lease (`dhcp_range` in the host_vars). Every host on [Hosts and boards at
ps1](ps1-boards.md) has a reservation below that range. Welland's one-network-per-port scheme is not used
here.

### Two NFS roots

val2 serves two roots, because the site runs two generations of hardware. Both are read-only NFS exports with
a tmpfs overlay, so anything a host writes, `/home/pi` included, is gone after a reboot or a power cycle
([The NFS root is shared and read-only](../setup/netboot.md#the-nfs-root-is-shared-and-read-only)).

- **bookworm** (32-bit, armhf): `/srv/nfs/rpi/bookworm/{boot,root}`, for the Pi 3B, 3B+ and 4B Arty hosts
  (site notes).
- **trixie**: `/srv/nfs/rpi/trixie/{boot,root}`, for the Compute Blades. Its kernel command line names
  `nfsroot=10.21.0.1:/srv/nfs/rpi/trixie/root`, and the blades share one boot directory, so a change to it
  changes all four ([Where a blade's boot configuration
  is](../boards/acorn/installations/ps1-reads.md#where-a-blades-boot-configuration-is)). On 2026-09-20 it read
  as arm64 with kernel `6.12.75+rpt-rpi-v8`; on 2026-10-05 pi16 and pi20 at ps1 read as a 32-bit userspace on
  kernel `6.18.50+rpt-rpi-v8`. How that root is built is not recorded in fpgas.online-infra, whose playbook
  builds bookworm only.

## PoE switch

Read on 2026-08-31 (switch dump in the site notes). One **Netgear FS728TPv2** at 10.21.0.200: 24 Fast
Ethernet ports `e1` to `e24` and 4 Gigabit ports `g25` to `g28`. LLDP puts val2 on `g25`; above that is a
Ubiquiti US-24-G1 (`PS1-SW-MODEM`). The port is the host's number: `piNN` is on `eNN`.

| Port | Link | PoE | Host | Board | Notes |
|---|---|---|---|---|---|
| e1 | down | searching | | | cable, no device |
| e2 | up | delivering | pi2 | Arty A7 | host offline |
| e3 | up | delivering | pi3 | Arty A7 | |
| e4 | down | searching | | | cable, no device |
| e5 | up | delivering | pi5 | Arty A7 | |
| e6 | down | disabled | | | Arty Ethernet test port |
| e7 | up | delivering | pi7 | Arty A7 | |
| e8 | down | disabled | | | Arty Ethernet test port |
| e9 | up | delivering | pi9 | Arty A7 | |
| e10 | down | disabled | | | Arty Ethernet test port |
| e11 | up | delivering | pi11 | Arty A7 | |
| e12 | down | disabled | | | Arty Ethernet test port |
| e13 | up | delivering | pi13 | Arty A7 | |
| e14 | up | delivering | pi14 | Acorn CLE-101 | CM4 blade |
| e15 | down | delivering | | | PoE on, no link |
| e16 | up | delivering | pi16 | Acorn CLE-101 | CM5 Lite blade |
| e17 | up | delivering | pi17 | Arty A7 | |
| e18 | up | delivering | pi18 | (slot empty) | CM4 blade |
| e19 | up | delivering | pi19 | | dead hardware |
| e20 | up | delivering | pi20 | Acorn CLE-101 | CM5 Lite blade |
| e21 | up | delivering | pi21 | | Pi 5, no FPGA |
| e22 | down | disabled | | | |
| e23 | down | searching | | | cable, no device |
| e24 | down | searching | | | cable, no device |
| g25 | up | — | val2 | | gateway |
| g26 to g28 | down | — | | | |

The even ports between Arty hosts (e6, e8, e10, e12) carry the Artys' own Ethernet adapters, which is why
their PoE is disabled.

:::{todo}
`host_vars/ps1.fpgas.online.yml` names three switch models in its comments: HP ProCurve 2610-24-PWR J9087A,
Netgear GS728TPP and Netgear FS728TPv2. The live PoE OID and the recorded management MAC (`A0:21:B7:AF:4E:05`)
both match the FS728TPv2, which is what this page says. Confirm it on the unit and delete the other two
comments.
:::

## Power control

**To power-cycle one host at ps1**, run this on val2 as root. Cutting a host's PoE is the only remote reset,
and a host loses what it held in memory. The argument is the port number, which is the host's number (20 for
pi20):

```console
$ set -a; . /etc/environment.export; set +a
$ /srv/www/pib/venv/bin/python3 \
    /srv/www/pib/venv/lib/python3.13/site-packages/snmp_switch/utils.py 20 2  # off
$ /srv/www/pib/venv/bin/python3 \
    /srv/www/pib/venv/lib/python3.13/site-packages/snmp_switch/utils.py 20 1  # on
```

`1` is on and `2` is off; with no value it reads the port's state. A blade takes about 60 seconds to come
back (site notes); it netboots again from val2.

The FS728TPv2 does not answer the standard PoE MIB. It uses a Netgear-private OID from a draft of the spec,
`1.3.6.1.4.1.4526.11.16.1.1.1.3.1` rather than `1.3.6.1.2.1.105.1.1.1.3`, which is the `oid` in the
host_vars. `/etc/environment.export` holds the switch's SNMP settings; no role in fpgas.online-infra writes
that name (see [PoE power control](../setup/network.md#poe-power-control)), so it is there from an earlier
install, and a rebuilt val2 would not have it.
