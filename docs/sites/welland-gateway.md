---
type: reference
owner: documentation maintainers
reader: someone who looks after the welland site and needs its gateway
review: 2026-11-10
---

# The welland gateway

**You look after welland and want to know what its gateway, tweed, serves, and how to reach a Pi through it**.
Deploying to it is [The gateway host](../setup/gateway.md). Who may log in, with which keys, is [Accounts and
logins](../setup/access.md).

## What the gateway provides

Each row names a part of tweed and gives its value. The addresses are from `host_vars`:
`ansible/inventory/host_vars/fpgas.online.yml` in fpgas.online-infra.

| | |
|---|---|
| Name | tweed. Ansible names it `fpgas.online` and reaches it as `gw.welland.fpgas.online` |
| Serves | DHCP, DNS and TFTP (dnsmasq), the NFS root, and the web tier of welland.fpgas.online and tinytapeout.fpgas.online |
| System | Debian 13 (trixie) |
| Uplink | `eth-uplink`, 10.99.21.2/30 and 2404:e80:a137:9921::2/126: a point-to-point link to the site's upstream gateway, 10.99.21.1, which forwards the web ports to tweed |
| Pi network | `eth-local`, 10.21.0.1/24 on the trunk to the switches, with one VLAN sub-interface per switch port; the Pis' addresses are in 10.21.0.0/16 |
| NFS root | `/srv/nfs/rpi/bookworm/{boot,root}`. The image it serves is named in `/srv/nfs/rpi/bookworm/.image-digest` ([Netboot and the NFS root](../setup/netboot.md)) |

Which package versions the served root holds is read in the root itself, on tweed:

```console
$ dpkg-query --admindir=/srv/nfs/rpi/bookworm/root/var/lib/dpkg -W 'fpgas-online-*' python3-rpi-hwid
```

tweed has no FPGA board of its own. Login is by key only. Ansible logs in as `ansible`. People log in to their
own operator accounts, or to the restricted `pi` jump account ([Accounts and logins](../setup/access.md)).

## Reaching tweed

From outside the site, `ssh` reaches tweed over IPv6, at `2404:e80:a137:2100::1`. The name
`tweed.welland.mithis.com` also has an IPv4 address, 87.121.95.37. That is the site's upstream gateway, which
does not pass `ssh` to tweed (`host_vars`). The name's other IPv6 address, `2404:e80:a137:9921::2`,
does not answer `ssh` from outside the site. Inside the site the name gives `10.99.21.2` and `10.21.0.1`.

## Reaching a Pi

Nothing upstream of tweed can reach a Pi, because each Pi is in its own VLAN. Jump through tweed to the Pi's
address, `10.21.<switch>.<port>`:

```console
$ ssh -J <you>@tweed.welland.mithis.com pi@10.21.2.46
$ ssh -J pi@tweed.welland.mithis.com pi@10.21.2.46   # through the jump account
```

The `pi` jump account can only run `ssh` and `ssh-keyscan`. A jump needs your key trusted by the jump account
and by the Pi, and the Pis trust only the operators' GitHub keys. Anyone else logs in to the jump account and
runs `ssh pi@10.21.2.46` from there, which uses the jump account's own key.

Visitors reach a Pi on a forwarded port instead. On its uplink, tweed forwards port `<s><pp>22` to the Pi on
switch `s`, port `pp` ([Network and power](../setup/network.md#two-addressing-schemes)). The
upstream gateway sets which public address and port reach that ([What a site needs from its upstream
network](../setup/upstream-gateway.md)). The Pis' password is public by design, and the login banner prints it.

## What is planned

- Logins routed to a board by its own name: [infra issue #187](https://github.com/fpgas-online/fpgas.online-infra/issues/187), tracked in [infra issue #191](https://github.com/fpgas-online/fpgas.online-infra/issues/191).
- Per-board ports that answer on the gateway's second global IPv6 address: [infra issue #264](https://github.com/fpgas-online/fpgas.online-infra/issues/264).
- A jump account mode in which a restricted key can only hop: [infra issue #283](https://github.com/fpgas-online/fpgas.online-infra/issues/283).
- Netbooted Pis that renew their DHCP lease: [infra issue #230](https://github.com/fpgas-online/fpgas.online-infra/issues/230).
- Booting a Pi into another NFS root for a special job: [infra issue #176](https://github.com/fpgas-online/fpgas.online-infra/issues/176).
- Sensor data from every Pi and the gateway, stored and graphed: [infra issue #263](https://github.com/fpgas-online/fpgas.online-infra/issues/263).
