# The ps1 gateway and switch

**You look after the ps1 gateway and want to know what it serves, which switch port carries which host, and
how to power-cycle one host.** You need root on the gateway. Which board is on which host, and its faults,
are on [Hosts and boards at ps1](ps1-boards.md).

## Gateway: val2

The site notes (`docs/hardware/site-ps1.md` in fpgas.online-test-designs) call the gateway val2; Ansible
calls it `ps1.fpgas.online`. Unless a row says otherwise, the table is the read made on the gateway itself on
6 October 2026 at 08:14 Adelaide time (5 October, 16:45 Chicago time) by the fpgas.online coordinator, with
Tim's permission. It found an install of about 25 September 2026, last booted on 26 September 2026.

| | |
|---|---|
| Name | ps1.fpgas.online; the machine calls itself `kas1` |
| System | Debian 13 (trixie), kernel `6.12.107+deb13-amd64` |
| Uplink | `eth-uplink`, 76.227.131.147/25, on the public internet; no global IPv6 address |
| Pi network | `eth-local`, 10.21.0.1/24 |
| Boot service | dnsmasq: DHCP, DNS and TFTP (TFTP from `/srv/tftp`) |
| Root service | NFS, two read-only exports (below) |
| Web | nginx in front of the board pages, the web SSH terminal and the video feeds |
| Switch | Netgear FS728TPv2 at 10.21.0.200 ([below](#poe-switch)) |
| Time zone | America/Chicago (site notes) |
| Administrator login | `ssh root@ps1.fpgas.online`, by key |

The Pi network is one flat `/24`. A Pi is recognised by its MAC and handed a reserved address
(`10.21.0.1NN` for the host on port `eNN`, from `/etc/dnsmasq.d/pibs.conf`, which held 12 hosts on
6 October 2026). dnsmasq gives 10.21.0.128 to 10.21.0.254 to anything it does not recognise, on a six-hour
lease. Welland's one-network-per-port scheme is not used here.

### One NFS root

On 6 October 2026 the gateway served ONE root, `/srv/nfs/rpi/trixie/{boot,root}`, exported read-only to
10.21.0.0/24; there was no `bookworm` root, though the site notes and older pages list one for the Arty hosts.
Every Pi's TFTP directory (`/srv/tftp/<serial>`, 12 of them) was a link to the same `boot/`, so a change
there changes every host at once ([Where a blade's boot configuration
is](../boards/acorn/installations/ps1-reads.md#where-a-blades-boot-configuration-is)). Its kernel command line
mounts `nfsroot=10.21.0.1:/srv/nfs/rpi/trixie/root` with a tmpfs overlay (`overlayroot=tmpfs`), so anything
a host writes, `/home/pi` included, is gone after a reboot or a power cycle ([The NFS root is shared and
read-only](../setup/netboot.md#the-nfs-root-is-shared-and-read-only)).

The root's own files date from 17 June 2026 (a Raspberry Pi OS image); its boot directory was updated on
25 September 2026 to kernel `6.18.50+rpt`. The blades read it as a 32-bit userspace on kernel
`6.18.50+rpt-rpi-v8` (pi16 and pi20 at ps1, 5 October 2026). What packages are inside the root was not read.
How it was built is not recorded in fpgas.online-infra, whose playbook builds a different layout
(`/srv/nfs/rpi/versions/`).

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

**To power-cycle one host at ps1**, run this on the gateway as root. Cutting a host's PoE is the only remote reset,
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
back (site notes); it netboots again from the gateway.

The FS728TPv2 does not answer the standard PoE MIB. It uses a Netgear-private OID from a draft of the spec,
`1.3.6.1.4.1.4526.11.16.1.1.1.3.1` rather than `1.3.6.1.2.1.105.1.1.1.3`, which is the `oid` in
`host_vars/ps1.fpgas.online.yml` (fpgas.online-infra). The commands above are the site notes'. On 6 October
2026 the gateway's web venv held `snmp_switch` 0.0.17; the read did not open `/etc/environment.export`,
because it holds the switch's credentials, so whether that file came back with the reinstall of 25 September
2026 is not known: if `set -a; . /etc/environment.export` fails, the switch settings are missing. No role in
fpgas.online-infra writes that file name ([PoE power
control](../setup/network.md#poe-power-control)).
