# Sites

Two deployments, with different carrier hardware, and therefore different
wiring. Nothing ties a carrier to a room — a Compute Blade could be racked at
Welland and a Pi 5 with an M.2 HAT installed at PS1 — so what a host is plugged
into is inventory, and what that implies for wiring is on the board pages. The
sites also differ in how hosts are addressed: Welland gives each port its own
VLAN, while PS1 still runs a flat, MAC-based network.

```{toctree}
:maxdepth: 2

welland
ps1
```

## At a glance

| | Welland | PS1 |
|---|---|---|
| Location | South Australia (private lab) | Pumping Station: One, Chicago (public) |
| Carrier | Raspberry Pi 5 + M.2 HAT | Compute Blade (CM4 / CM5) |
| Boards | Arty A7, NeTV2, Fomu EVT, TT ASIC, TT FPGA demo, Acorn CLE-215+ | Arty A7, LiteFury / Acorn CLE-101 (Compute Blades) |
| Addressing | [VLAN-per-port (since 2026-08-23)](../setup/network.md) | [MAC-based (legacy)](../setup/network.md) |
| Acorn wiring variant, which follows the carrier | [Raspberry Pi 5](../boards/acorn/wiring.md) — JTAG on `10:9:11:8` | [Compute Blade](../boards/acorn/wiring.md#compute-blade-wiring-variant) — JTAG on `2:3:4:14` |
| Cameras | Arty, Fomu, Tiny Tapeout and Acorn hosts | Arty hosts only; no blade has one |

The P2 serial crossover — K2 (FPGA TX) to GPIO15, J2 (FPGA RX) to GPIO14 — is
the same on both carriers, so one cable design works everywhere.

:::{warning}
The two JTAG pin orders are not interchangeable, and on a Compute Blade GPIO14
is TMS *and* half of the serial pair, so loading a design that drives it leaves
the FPGA holding a line JTAG needs, recoverable only with a power cycle. That
follows from the carrier rather than from the site, and both variants are on
[Acorn wiring](../boards/acorn/wiring.md).
:::
