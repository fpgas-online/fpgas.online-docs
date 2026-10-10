# PS1

**You want to know what is at ps1, how to log in to a host there, and which page has the rest.** This page
chooses; the detail is on the two pages it links.

ps1 is the public site at [Pumping Station: One](https://pumpingstationone.org/) in Chicago, published as
[ps1.fpgas.online](https://ps1.fpgas.online/fpgas/) and run by Carl Karsten (the site notes,
`docs/hardware/site-ps1.md` in fpgas.online-test-designs). One gateway, val2, serves eight Arty A7 boards on
Raspberry Pi 3B, 3B+ and 4B hosts, and four Compute Blades, each with a Raspberry Pi Compute Module. Three of
the blades, pi14, pi16 and pi20 at ps1, carry an Acorn CLE-101 in their M.2 slot; pi18 at ps1's slot is
empty (the reads of 2026-09-20 on [Acorns at ps1](../boards/acorn/installations/ps1.md)).

| You want | Page |
|---|---|
| Which board is on which host, its state, and what is known wrong with it | [Hosts and boards at ps1](ps1-boards.md) |
| What val2 serves, its switch, and how to power-cycle one host | [The ps1 gateway and switch](ps1-gateway.md) |
| An Acorn on a Compute Blade: which card, its state, what it still needs | [Acorns at ps1](../boards/acorn/installations/ps1.md) |
| How a page on the public site is built | [The web application](../setup/webapp.md) |

## Logging in to a host at ps1

```{include} ps1-login.inc
```

## Checking a board here

A host at ps1 is checked as any machine outside the fleet is: install the Acorn packages on the host and run
`fpgas-verify` ([Installing the Acorn
packages](../boards/acorn/setup/packages.md#installing-the-acorn-packages), then [Checking a board:
fpgas-verify](../verify/fpgas-verify.md)). For an Acorn on a Compute Blade, [Compute Blade cables:
verifying](../boards/acorn/checks/compute-blade.md) goes from logging in after a fresh boot to
which wire a failing line points at.

## Public site

`https://ps1.fpgas.online/fpgas/` lists a page per Arty host. Each has a web terminal, a bitstream upload,
"Turn it off and on again: Reset", a "Check PoE" button and a video feed at `/live/piN.m3u8` (read on
`pi3.html` on 7 October 2026). The Compute Blades have no page there.

## Where each part of the old page went

The sections of this page moved to the two pages above on 7 October 2026. Links to the old sections land
here:

(gateway-val2)=
- [Gateway: val2](ps1-gateway.md#gateway-val2): its system, its NFS root, its addresses.

(poe-switch)=
- [PoE switch](ps1-gateway.md#poe-switch): the port table.

(power-control)=
- [Power control](ps1-gateway.md#power-control): power-cycling one host.

(hosts-and-boards)=
- [Hosts and boards](ps1-boards.md): every host.

(boards)=
- [Boards](ps1-boards.md#boards): the count by board kind.

(arty-a7-hosts)=
- [Arty A7 hosts](ps1-boards.md#arty-a7-hosts).

(compute-blades)=
- [Compute blades](ps1-boards.md#compute-blades).

(other-hosts)=
- [Other hosts](ps1-boards.md#other-hosts).

(pending)=
- [Pending](ps1-boards.md#pending): boards allocated and not installed.

(known-faults)=
- Known faults: now beside each host on [Hosts and boards at ps1](ps1-boards.md).

- [Public site](#public-site), above.

```{toctree}
:hidden:

Hosts and boards <ps1-boards>
Gateway and switch <ps1-gateway>
```
