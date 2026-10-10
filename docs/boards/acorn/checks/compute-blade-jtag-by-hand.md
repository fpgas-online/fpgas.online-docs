---
type: how-to
owner: documentation maintainers
reader: someone with an Acorn wired to a Compute Blade who wants to run JTAG on it
review: 2026-11-10
---

# How to run JTAG by hand on a Compute Blade

**You have an Acorn wired to a Compute Blade with a CM4 or CM5 and want to run JTAG on it: what the blade
must have set at boot, the commands, and how the pins are put back afterwards.** Which wire goes where is on
[Acorn wiring on a Compute Blade](../setup/compute-blade/wiring.md); the line JTAG shares with the serial pair is on [The line JTAG and the serial port share on a Compute Blade](../setup/compute-blade/shared-line.md).

## JTAG on a blade

```{include} ../inc/blade-jtag-serial-off.inc
```

```{include} ../inc/blade-detach.inc
```

The pin order is TDI(GPIO2):TDO(GPIO3):TCK(GPIO4):TMS(GPIO14).

```{include} ../inc/blade-jtag-commands.inc
```

`$SOC` is the design's `.bit`; which file that is, and where it comes from, is under [The design
these steps load](jtag-by-hand.md#the-design-these-steps-load).

The `libgpiod` cable opens `/dev/gpiochip0`. On pi16 at ps1 and pi20 at ps1 (CM5s, kernel
6.18.50, 2026-10-05) `gpiodetect` listed the header's chip, `pinctrl-rp1`, as
`gpiochip0` already, so no link was needed; do not copy the Pi 5's
`gpiochip15` link. On any other blade run `gpiodetect` first: the header's chip
is the one labelled `pinctrl-rp1` on a CM5 and `pinctrl-bcm2711` on a CM4 (not
read by us on a CM4).

openFPGALoader 0.13.1 left GPIO2 and GPIO4 as **outputs** driving low when it
exited on pi16 at ps1 (2026-10-05); it drives TMS on GPIO14 too, so treat that as left
an output as well (not observed: the run on pi16 at ps1 stopped before it had GPIO14).
Put them back before anything else uses the lines. On pi16 at ps1 `pinctrl set 2,4 no
pu` restored GPIO2 and GPIO4 to what they were before.

Give GPIO14 and GPIO15 back to the serial port only when the loaded design
treats J2 as an input (the fpgas.online Acorn design does; pin-ID does not: see
the warning under [P2](../setup/compute-blade/blade-settings.md#the-serial-port)). The UART function is
a different alternate on each module, so run only the line for yours;
`pinctrl funcs 14,15` lists them. This applies only to a boot in which the
serial port is on (kernel 6.12.75, as on pi20 at ps1). In a kernel 6.18 boot with the
serial port off there is no `/dev/ttyAMA0` and nothing to give back.

On a **CM4** (BCM2711):

```console
$ pinctrl set 14,15 a0       # GPIO14 = TXD0, GPIO15 = RXD0
```

On a **CM5** (RP1):

```console
$ pinctrl set 14,15 a4       # GPIO14 = TXD0, GPIO15 = RXD0
```

The ps1 blades ran openFPGALoader 0.13.1 when probed on 2026-09-20, and pi16 at ps1 again on 2026-10-05; it has `--read-dna`, `--read-xadc` and `--read-register`, all read-only.

When a wire does not answer: [Acorn wiring faults on a Compute Blade](../troubleshooting/compute-blade-wiring.md).
