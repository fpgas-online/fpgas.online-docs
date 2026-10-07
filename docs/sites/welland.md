# Welland

**You look after welland and want to know what is there, how its network is laid out, and which page has the rest.** This page
chooses; the detail is on the two pages it links.

welland is the private test lab in South Australia behind
[welland.fpgas.online](https://welland.fpgas.online) and
[tinytapeout.fpgas.online](https://tinytapeout.fpgas.online). One gateway, tweed, serves Raspberry Pi hosts
on two PoE switches: NeTV2 boards, a Fomu, Acorn cards on Raspberry Pi 5s, Arty A7 boards, Tiny Tapeout
boards, and Orange Pis that carry no FPGA. A bare host name on these pages (`pi-sw2-p46`) is a welland host.

| You want | Page |
|---|---|
| Which board is on which host, what was last seen on each, and what is known wrong | [Hosts and boards at welland](welland-boards.md) |
| tweed: what it is, its addresses, how to reach a Pi through it | [The welland gateway](welland-gateway.md) |
| An Acorn: which card, its state, what it still needs | [Acorns at welland](../boards/acorn/installations/welland.md) |
| How a port becomes an address and a name | [Network and power](../setup/network.md) |

## Network

```
                          ┌────────────────────────────────────┐
Internet ── upstream ─────│  tweed (the welland gateway)       │
            gateway       │  Debian 13 (trixie), x86_64        │
                          │  dnsmasq (DHCP, DNS, TFTP), NFS    │
                          │  root, web tier                    │
              eth-local ──│  10.21.0.1/16, one VLAN per port   │
                          └───────────┬────────────────────────┘
                                      │ trunk
                      ┌───────────────┴───────────────┐
                      │ switch 1, Netgear GSM7252PS   │
                      │ NeTV2 p10-18, Fomu p17, Acorn │
                      │ p38                           │
                      └───────────────┬───────────────┘
                                      │ trunk
                      ┌───────────────┴───────────────┐
                      │ switch 2, Netgear S3300       │
                      │ Tiny Tapeout p3-8 and p33-36, │
                      │ Acorns, Orange Pis and their  │
                      │ hub host p30                  │
                      └───────────────────────────────┘
```

Every Pi netboots from tweed. Since 2026-08-23 the site has run one VLAN per switch port (fpgas.online-infra
PR #10): a Pi's name and address come from the port it is plugged into, `pi-sw<switch>-p<port>` at
`10.21.<switch>.<port>`, and tweed's firewall stops one Pi reaching another. The formulas, and which switch
port is which, are on [Network and power](../setup/network.md). Moving a Pi to another port renames and
re-addresses it.

On switch 2, port N carries Tiny Tapeout board N (ports 1 to 10; Tim's rule), and the Tiny Tapeout FPGA
boards sit on ports 33 to 36. An Acorn is identified by its label, not its port: where each is plugged in is
what its check last reported ([Acorns at welland](../boards/acorn/installations/welland.md)).

## Where each part of the old page went

The sections of this page moved on 7 October 2026. Links to the old sections land here:

(gateway-tweed)=
- [Gateway: tweed](welland-gateway.md).

(hosts-and-boards)=
- [Hosts and boards](welland-boards.md).

(infrastructure-host)=
- Infrastructure host (pi1, the old NFS maintenance host, now unlocated): [Retired and unlocated hosts](welland-boards.md#retired-and-unlocated-hosts).

(arty-a7-35t)=
- [Arty A7-35T](welland-boards.md#arty-a7-35t).

(netv2)=
- [NeTV2](welland-boards.md#netv2).

(sqrl-acorn-cle-215)=
- [SQRL Acorn CLE-215+](welland-boards.md#acorn-cle-215).

(fomu-evt)=
- [Fomu EVT](welland-boards.md#fomu-evt).

(tiny-tapeout-asic-boards)=
- [Tiny Tapeout ASIC boards](welland-boards.md#tiny-tapeout-asic-boards).

(tiny-tapeout-fpga-demo-boards)=
- [Tiny Tapeout FPGA demo boards](welland-boards.md#tiny-tapeout-fpga-demo-boards).

(disconnected-hosts)=
- [Disconnected hosts](welland-boards.md#retired-and-unlocated-hosts).

(known-faults)=
- Known faults: now beside each board kind on [Hosts and boards at welland](welland-boards.md).

```{toctree}
:hidden:

Hosts and boards <welland-boards>
Gateway <welland-gateway>
```
