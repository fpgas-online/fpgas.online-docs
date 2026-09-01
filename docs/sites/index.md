# Sites

Two deployments, with different carrier hardware and different wiring. The
difference is not cosmetic: it changes which GPIOs carry JTAG and serial, and
therefore every command you would paste from one site into the other.

```{toctree}
:maxdepth: 2

welland
ps1
```

## At a glance

| | Welland | PS1 |
|---|---|---|
| Location | South Australia (private lab) | Pumping Station: One, Chicago (public) |
| Carrier | Raspberry Pi 5 + mPCIe adapter | Compute Blade (CM4 / CM5) |
| JTAG pin order | `10:9:11:8` | `2:3:4:14` |
| P2 serial wiring | K2 → GPIO14, J2 → GPIO15 | crossover: K2 → GPIO15, J2 → GPIO14 |
| Cameras | one per FPGA host | none |

:::{warning}
The JTAG pin orders are not interchangeable. On a Compute Blade, GPIO14 is TMS
*and* half of the serial pair. Loading a design that drives it leaves the FPGA
holding a line JTAG needs, which is recoverable only with a power cycle.
:::
