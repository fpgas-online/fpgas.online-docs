# The welland gateway

**You look after welland and want to know what tweed, its gateway, is and serves, and how to reach a Pi at welland through
it.** Deploying to it is [The gateway host](../setup/gateway.md); who may log in, with which keys, is
[Accounts and logins](../setup/access.md).

## Gateway: tweed

The rows say where each value is from. `host_vars` is `ansible/inventory/host_vars/fpgas.online.yml` in
fpgas.online-infra (main, read 2026-10-07); Ansible names this gateway `fpgas.online`.

| | |
|---|---|
| Name | tweed; reached by Ansible as `gw.welland.fpgas.online` (host_vars) |
| Serves | DHCP, DNS and TFTP (dnsmasq), the NFS root, the web tier of welland.fpgas.online and tinytapeout.fpgas.online |
| Hardware | Intel Core i5-3610ME, QM77 chipset; 2 × Intel 82574L Ethernet (the earlier version of this page; not re-read) |
| System | Debian 13 (trixie), installed 2026-08-30 (the earlier version of this page); the newest kernel package installed was `6.12.105+deb13-amd64` on 2026-10-05 (the gateway's package list of that day) |
| Uplink | `eth-uplink`, 10.99.21.2/30 and 2404:e80:a137:9921::2/126, a point-to-point link to the site's upstream gateway (10.99.21.1), which forwards the web ports to tweed (host_vars) |
| Pi network | `eth-local`, 10.21.0.1/16, a trunk to the switches with one VLAN sub-interface per switch port (host_vars) |
| NFS root | `/srv/nfs/rpi/bookworm/{boot,root}`, from image `ghcr.io/fpgas-online/nfsroot@sha256:f33a8fc8…2f0dd8e8` (the root update of 6 October 2026, below) |

The root of 6 October 2026 carried `fpgas-online-verify` and `fpgas-online-tt-fpga-bitstreams`
0.0.post1189, `fpgas-online-tt` 0.0.post71, `fpgas-online-cam` 0.0.post68, `python3-rpi-hwid` 0.0.post543
and `fpgas-online-acorn-litepcie-*` 0.0.post1079 (read in the root after the update, 08:21 Adelaide time).
The digest the gateway serves is in `/srv/nfs/rpi/bookworm/.image-digest`; a root update changes it
([Netboot and the NFS root](../setup/netboot.md)).

tweed has no FPGA board of its own. Login is by key only. Ansible logs in as `ansible`; people log in to their
own operator accounts, or to the restricted `pi` jump account ([Accounts and
logins](../setup/access.md)).

## Reaching tweed

`tweed.welland.mithis.com` answers differently inside and outside the site (looked up 2026-09-29). Public DNS
gives A `87.121.95.37`, the site's upstream gateway, whose reverse proxy is not tweed, and AAAA
`2404:e80:a137:2100::1` and `2404:e80:a137:9921::2`, which are tweed. Inside the site it gives `10.99.21.2`
and `10.21.0.1`. So from outside, SSH to tweed goes over IPv6, to `2404:e80:a137:2100::1`; port 22 on
`…9921::2` timed out from outside on 2026-09-29.

## Reaching a Pi

Nothing upstream of tweed can reach a Pi: each is in its own VLAN. Jump through tweed, to the Pi's address
(`10.21.<switch>.<port>`):

```console
$ ssh -J <you>@tweed.welland.mithis.com pi@10.21.2.46
$ ssh -J pi@tweed.welland.mithis.com pi@10.21.2.46   # through the jump account
```

The `pi` jump account can only run `ssh` and `ssh-keyscan`. For a jump, your key must be trusted by the jump
account and by the Pi, and the Pis trust only the operators' GitHub keys; anyone else logs in to the jump
account and runs `ssh pi@10.21.2.46` from there, which uses the jump account's own key.

Visitors reach a Pi on a forwarded port instead: tweed forwards port `<s><pp>22` on its uplink to the SSH
port of the Pi on switch `s`, port `pp` (the firewall's port forward, [Network and
power](../setup/network.md#two-addressing-schemes)); which public address and port reach that from the
internet is set on the upstream gateway ([What a site needs from its upstream
network](../setup/upstream-gateway.md)). The Pis' password is public by design; the login banner prints it
(read on the sweep of 6 October 2026).
