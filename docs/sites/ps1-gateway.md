---
type: reference
owner: documentation maintainers
reader: someone who looks after the ps1 site and needs its gateway, switch and power control
review: 2026-11-10
---

# The ps1 gateway and switch

**You look after the ps1 gateway and want to know what it serves, which switch port carries which host, and
how to power-cycle one host**. You need root on the gateway.

## Gateway: val2

The gateway, its switch and its tooling are the site operator's own install. They come from the
[pici](https://github.com/CarlFK/pici) playbooks and the `pib` web application.
None of it is built by fpgas.online-infra.
fpgas.online reads the gateway and does not deploy to it. The site notes, `docs/hardware/site-ps1.md` in
fpgas.online-test-designs, call it val2.

| | |
|---|---|
| Name | ps1.fpgas.online; the machine calls itself `kas1` |
| System | Debian 13 (trixie) |
| Uplink | `eth-uplink`, 76.227.131.147/25, on the public internet; no global IPv6 address |
| Pi network | `eth-local`, 10.21.0.1/24 |
| Boot service | dnsmasq: DHCP, DNS and TFTP (TFTP from `/srv/tftp`) |
| Root service | NFS, read-only ([below](#one-nfs-root)) |
| Web | nginx in front of the board pages, the web SSH terminal and the video feeds |
| Switch | Netgear FS728TPv2 at 10.21.0.200 ([below](#poe-switch)) |
| Administrator login | `ssh root@ps1.fpgas.online`, with a key the gateway's administrator has installed |

The Pi network is one flat `/24`. A Pi is recognised by its MAC and handed a reserved address from `/etc/dnsmasq.d/pibs.conf`.
The host on port `eNN` gets `10.21.0.1NN` as its address. Anything else gets an address from 10.21.0.128 to
10.21.0.254, on a six-hour lease. Welland's one-network-per-port scheme is not used here.

### One NFS root

The gateway serves one root, `/srv/nfs/rpi/trixie/{boot,root}`, exported read-only to the Pi network. Every
Pi's TFTP directory, `/srv/tftp/<serial>`, is a link to the same `boot/`, so a change there changes every host
at once. The kernel command line mounts `nfsroot=10.21.0.1:/srv/nfs/rpi/trixie/root` with a tmpfs overlay
(`overlayroot=tmpfs`). Anything a host writes, `/home/pi` included, is gone after a reboot or a power cycle
([The NFS root is shared and read-only](../setup/netboot.md#the-nfs-root-is-shared-and-read-only)).

The root is a 32-bit Raspberry Pi OS userspace on a `6.18.50+rpt` kernel. It did not come from
fpgas.online-infra, whose playbook builds a bookworm root at `/srv/nfs/rpi/bookworm`
(`dist: bookworm` in `inventory/group_vars/all/srv.yml`).

## PoE switch

One **Netgear FS728TPv2** at 10.21.0.200 has 24 Fast Ethernet ports, `e1` to `e24`, and 4 Gigabit ports,
`g25` to `g28` (site notes). The gateway hands that address to the switch's MAC `a0:21:b7:af:4e:05`
(`/etc/dnsmasq.d/switch.conf`). The site notes record the gateway on `g25`, and above it a Ubiquiti US-24-G1
(`PS1-SW-MODEM`). The port is the host's number: `piNN` is on `eNN`.

Which host is on which port, from the site notes' port inventory:

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

## What is planned

- A record of which hosts the shared boot directory serves, with every host named once: [infra issue #273](https://github.com/fpgas-online/fpgas.online-infra/issues/273).
- Which physical Compute Blade is pi14, pi16, pi18 and pi20 at ps1: [infra issue #269](https://github.com/fpgas-online/fpgas.online-infra/issues/269).
- How the shared boot files set the header serial port for the blades' checks and for JTAG: [infra issue #270](https://github.com/fpgas-online/fpgas.online-infra/issues/270).
- `fpgas-verify` in the shared root, so a blade keeps its packages across a boot: [infra issue #271](https://github.com/fpgas-online/fpgas.online-infra/issues/271).
- A trixie root that fpgas.online-infra builds: [infra issue #72](https://github.com/fpgas-online/fpgas.online-infra/issues/72).
- The switch model settled, among the three that `host_vars` names: [infra issue #73](https://github.com/fpgas-online/fpgas.online-infra/issues/73).
- The Arty A7 hosts that do not answer, back in service: [infra issue #272](https://github.com/fpgas-online/fpgas.online-infra/issues/272).
