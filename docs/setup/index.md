# Setup

How the platform works, independent of any one board or site: how the hosts
boot, how the network is laid out, what runs on each host, and how the web
application reaches the boards.

Both sites are built the same way. One x86 gateway serves the boot chain and
the web tier, a managed PoE switch carries both the network and the power, and
each FPGA host hangs off one switch port with one FPGA board attached:

```text
                        ┌────────────────────────────────────┐
      browser ──https──▶│ gateway             nginx + Django │
                        │ (one per site)  dnsmasq DHCP/TFTP, │
                        │                 NFS root, ssh hop  │
                        └──────────────────┬─────────────────┘
                                           │ eth-local
                        ┌──────────────────┴─────────────────┐
                        │ PoE switch      one VLAN per port  │
                        │                 PoE off/on by SNMP │
                        └───┬──────────────┬──────────────┬──┘
                            │              │              │
                     ┌──────┴─────┐ ┌──────┴─────┐ ┌──────┴─────┐
                     │ Pi host    │ │ Pi host    │ │ Pi host  … │
                     │ netboots   │ │            │ │            │
                     │ read-only  │ │            │ │            │
                     │ NFS root + │ │            │ │            │
                     │ tmpfs      │ │            │ │            │
                     │ camera,    │ │            │ │            │
                     │ fpgas-tt   │ │            │ │            │
                     └──────┬─────┘ └──────┬─────┘ └──────┬─────┘
                            │              │              │  USB / JTAG / PCIe
                     ┌──────┴─────┐ ┌──────┴─────┐ ┌──────┴─────┐
                     │ FPGA board │ │ FPGA board │ │ FPGA board │
                     └────────────┘ └────────────┘ └────────────┘

boot path: Pi ─DHCP▶ dnsmasq ─TFTP▶ kernel ─NFS▶ shared read-only root
user path: browser ─https▶ gateway ─ssh/proxy▶ Pi ─USB/JTAG/PCIe▶ board
prov path: Ansible ─ssh▶ gateway ─chroot▶ NFS root, baked before any Pi boots
```

One VLAN per port is the Welland scheme, and the gateway link is a VLAN trunk
only there; PS1 is one flat network with a MAC table. `fpgas-tt` runs only on
the Tiny Tapeout hosts, and only some hosts carry a camera. The pages below
take that picture apart:

- [Netboot and the NFS root](netboot.md) — how a Pi with no SD card and no
  local storage gets a kernel and a root filesystem, and what it costs you
  that the root is shared.
- [Network and power](network.md) — how a Pi gets its address and its power,
  and why the two sites lay that out differently.
- [What runs on a Pi host](pi.md) — the packages, systemd units and boot-time
  settings that building the root leaves behind on every host.
- [Orange Pi H3 hosts](orange-pi.md) — how five non-Raspberry boards boot the
  same NFS root after being loaded with U-Boot over USB FEL, and what to do
  when one of them does not come back.
- [The gateway host](gateway.md) — what the one x86 machine per site runs, how
  it is deployed, and what a rebuild from bare metal has to get right.
- [The web application](webapp.md) — what a visitor sees, which Django apps
  serve it, and how the `site` role puts it on the gateway.
- [The Tiny Tapeout stack](tinytapeout.md) — the `fpgas-tt` daemon, the board
  catalogue, the demo bitstreams and the Commander fork behind
  `tinytapeout.fpgas.online`.
- [Verifying a deployment](verification.md) — what to change when adding
  another device of a type the fleet already has, and how to prove it works.

```{toctree}
:maxdepth: 1

netboot
network
pi
orange-pi
gateway
webapp
tinytapeout
verification
```
