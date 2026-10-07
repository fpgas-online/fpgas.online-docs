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
| Administrator login | `ssh root@ps1.fpgas.online`, with a key the gateway's administrator has installed; no password |

The Pi network is one flat `/24`. A Pi is recognised by its MAC and handed a reserved address
(`10.21.0.1NN` for the host on port `eNN`, from `/etc/dnsmasq.d/pibs.conf`, which held 12 hosts on
6 October 2026). dnsmasq gives 10.21.0.128 to 10.21.0.254 to anything it does not recognise, on a six-hour
lease. Welland's one-network-per-port scheme is not used here.

### One NFS root

On 6 October 2026 the gateway served ONE root, `/srv/nfs/rpi/trixie/{boot,root}`, exported read-only to
`10.21.0.1/24` (the Pi network); there was no `bookworm` root, though older versions of this page list one for the Arty hosts.
Every Pi's TFTP directory (`/srv/tftp/<serial>`, 12 of them) was a link to the same `boot/`, so a change
there changes every host at once ([Where a blade's boot configuration
is](../boards/acorn/installations/ps1-reads.md#where-a-blades-boot-configuration-is)). Its kernel command line
mounts `nfsroot=10.21.0.1:/srv/nfs/rpi/trixie/root` and asks for a tmpfs overlay (`overlayroot=tmpfs`); the
blades were seen running with that overlay on 2026-09-20 ([Acorns at ps1: what was
read](../boards/acorn/installations/ps1-reads.md)). With it, anything a host writes, `/home/pi` included, is
gone after a reboot or a power cycle ([The NFS root is shared and
read-only](../setup/netboot.md#the-nfs-root-is-shared-and-read-only)).

The root's own files date from 17 June 2026 (a Raspberry Pi OS image); its boot directory was updated on
25 September 2026 to kernel `6.18.50+rpt`. The blades read it as a 32-bit userspace on kernel
`6.18.50+rpt-rpi-v8` (pi16 and pi20 at ps1, 5 October 2026). What packages are inside the root was not read.
How it was built is not recorded. fpgas.online-infra's playbook builds a bookworm root at
`/srv/nfs/rpi/bookworm` (`dist: bookworm` in `inventory/group_vars/all/srv.yml`, main, read 2026-10-07), so
this root did not come from it as it stands.

## PoE switch

One **Netgear FS728TPv2** at 10.21.0.200: 24 Fast Ethernet ports `e1` to `e24` and 4 Gigabit ports `g25` to
`g28` (site notes). The gateway hands that address to the switch's MAC `a0:21:b7:af:4e:05`
(`/etc/dnsmasq.d/switch.conf`, read 6 October 2026), and the `host_vars` give the same MAC with the
FS728TPv2's PoE OID; its comments also name an HP ProCurve 2610 and a Netgear GS728TPP, which nothing has
ruled out on the unit itself. The site notes record the gateway on `g25` by LLDP, and above it a Ubiquiti
US-24-G1 (`PS1-SW-MODEM`). The port is the host's number: `piNN` is on `eNN`.

Which host is on which port, from the site notes' port inventory (undated; not read by fpgas.online):

| Port | Host | Board | Notes (site notes) |
|---|---|---|---|
| e2, e3, e5, e7, e9, e11, e13 | pi2, pi3, pi5, pi7, pi9, pi11, pi13 | Arty A7 | |
| e6, e8, e10, e12 | | | the Artys' own Ethernet test adapters; no PoE needed |
| e14 | pi14 | Acorn CLE-101 | CM4 Compute Blade |
| e16 | pi16 | Acorn CLE-101 | CM5 Lite Compute Blade |
| e17 | pi17 | Arty A7 | |
| e18 | pi18 | (slot empty) | CM4 Compute Blade |
| e19 | pi19 | | dead hardware |
| e20 | pi20 | Acorn CLE-101 | CM5 Lite Compute Blade |
| e21 | pi21 | | Raspberry Pi 5, no FPGA |
| g25 | the gateway | | server uplink |

## Power control

**To power-cycle one host at ps1.** Cutting a host's PoE is the only remote reset, and the host loses what it
held in memory.

```{include} ps1-power-cycle.inc
```
