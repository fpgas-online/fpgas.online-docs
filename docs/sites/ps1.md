# PS1

The public deployment at [Pumping Station: One](https://pumpingstationone.org/)
in Chicago. Raspberry Pi Compute Modules on
[Compute Blade](https://computeblade.com/) carriers, with SQRL Acorn boards in
the M.2 slot.

## Compute blades

| Host | IP | Module | RAM | FPGA on PCIe |
|---|---|---|---|---|
| pi14 | 10.21.0.114 | CM4 Rev 1.1 | 4 GB | Acorn CLE-101 `1e24:0101` |
| pi16 | 10.21.0.116 | CM5 Lite Rev 1.0 | 8 GB | Acorn CLE-101 `1e24:0101` |
| pi18 | 10.21.0.118 | CM4 Rev 1.1 | 4 GB | none — M.2 slot empty |
| pi20 | 10.21.0.120 | CM5 Lite Rev 1.0 | 8 GB | Xilinx 7-series `10ee:7011` |

pi20 is an XC7A100T (LiteFury), device DNA `0x0028e5c45e304854`.

## CM4 and CM5 are not interchangeable

This is the single most useful thing to know about the site.

CM4 (pi14, pi18)
: `GPIO14 = TXD0` and `GPIO15 = RXD0` at **alt0**, on BCM2711 serial blocks.
  Only `/dev/ttyAMA0` exists. There is no mux option that makes GPIO15 a
  transmitter, so the FPGA's TX **must** land on GPIO15. One correct wiring, no
  software escape.

CM5 Lite (pi16, pi20)
: `GPIO14/15` at **alt4** on the RP1, with `/dev/ttyAMA0` and `/dev/ttyAMA10`.
  Like the Pi 5, the RP1 offers several UART instances plus PIO, so pins can be
  reassigned in software.

## Wiring

Only GPIO2, 3, 4, 14 and 15 are exposed on the Compute Blade expansion port, so
JTAG and serial share pins:

| Signal | GPIO | Notes |
|---|---|---|
| TDI | 2 | also SDA1 — has an onboard I²C pull-up |
| TDO | 3 | also SCL1 — has an onboard I²C pull-up |
| TCK | 4 | |
| TMS | 14 | **shared** with the serial pair |
| serial | 15 | |

```console
$ openFPGALoader --cable libgpiod --pins 2:3:4:14 --detect
```

The P2 serial pair is wired as a **null modem crossover**, measured with the
pin-ID design on pi20:

| P2 ball | lands on | RPi function |
|---|---|---|
| K2 (FPGA TX) | GPIO15 | RXD0 — the Pi receives |
| J2 (FPGA RX) | GPIO14 | TXD0 — the Pi sends |

:::{note}
This is the opposite of Welland, and also the opposite of what
`fpgas.online-test-designs` issue #4 originally recorded — the cable was
evidently swapped after that issue was filed.
:::

## Two traps

**Loading a design that drives the serial TX costs you JTAG.** GPIO14 is TMS.
Once the FPGA drives it, `openFPGALoader` cannot use it, and the only way back
is a PoE cycle of the blade's switch port.

**The kernel console used to make this fatal.** With `console=ttyAMA0`, a
1200-baud FPGA transmitting into a 115200-baud console produced garbage that
the kernel read as SysRq commands, eventually hitting `reboot` or `poweroff`.
All four blades now boot with `console=tty1`, so this no longer happens.

## Power control

The Netgear FS728TPv2 at `10.21.0.200` does **not** answer the standard PoE
MIB. It uses a Netgear-private OID under a draft of the spec:

```
1.3.6.1.4.1.4526.11.16.1.1.1.3.1     # not 1.3.6.1.2.1.105.1.1.1.3
```

The working path is on the server (`val2`):

```console
$ set -a; . /etc/environment.export; set +a
$ /srv/www/pib/venv/bin/python3 \
    /srv/www/pib/venv/lib/python3.13/site-packages/snmp_switch/utils.py 20 2  # off
$ /srv/www/pib/venv/bin/python3 \
    /srv/www/pib/venv/lib/python3.13/site-packages/snmp_switch/utils.py 20 1  # on
```

`1` is on, `2` is off; omit the value to read the current state. A blade takes
about 60 seconds to come back.

## Known faults

- **pi14 and pi16 do not respond to JTAG on any pin order.** All 24 permutations
  of the four available GPIOs were tried. GPIO4 (TCK) shows a pull-up only on
  pi20; on pi14 and pi16 it floats exactly as it does on pi18, whose M.2 slot is
  empty. TCK is a dedicated JTAG pin that no design can drive, so that pull-up
  is the Acorn's own and should be present whenever the connector is mated.
  Both boards enumerate over PCIe, so the boards are alive — reseating P1 is the
  thing to try.
- No cameras on any blade.
