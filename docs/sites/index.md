# Sites

**You want to know which fpgas.online sites there are and which page has each.** Two sites, each with one
gateway and its own Raspberry Pi hosts; a bare host name in these pages means welland, and a ps1 host is
always written with its site ("pi20 at ps1").

```{toctree}
:maxdepth: 1

welland
ps1
```

## At a glance

| | welland | ps1 |
|---|---|---|
| Where | South Australia, a private lab | Pumping Station: One, Chicago, run by Carl Karsten |
| Public site | [the welland site](https://welland.fpgas.online) and [the Tiny Tapeout site](https://tinytapeout.fpgas.online) | [the ps1 site](https://ps1.fpgas.online/fpgas/) |
| Hosts and boards | [Hosts and boards at welland](welland-boards.md): NeTV2, Fomu, Acorn, Arty A7, Tiny Tapeout, Orange Pis | [Hosts and boards at ps1](ps1-boards.md): Arty A7 (on Raspberry Pis), Acorn CLE-101 (on Compute Blades) |
| Gateway | [tweed](welland-gateway.md), deployed by fpgas.online-infra | [Carl's own install](ps1-gateway.md), read but not deployed by fpgas.online |
| Addressing | one VLAN per switch port, since late August 2026 ([Network and power](../setup/network.md)) | one flat network, a Pi known by its MAC |

Where an Acorn's wiring differs, it follows the carrier, not the site: a Raspberry Pi 5 with an M.2 HAT, or
a Compute Module on a Compute Blade. Each carrier has its own pages under [Acorn](../boards/acorn/index.md).
