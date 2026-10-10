---
type: how-to
owner: documentation maintainers
reader: someone with a wired Acorn who wants to test its serial pair and spare wires
review: 2026-11-10
---

# How to run the UART and GPIO loopback on an Acorn

**You have an Acorn wired to a Raspberry Pi 5 and want to see by hand, with the loopback design, that the
serial pair of P2 (J2 and K2) carries in both directions.** On a Compute Blade this cannot be done by hand
today; the last section says why and what checks the pair instead. On a card that runs the fpgas.online
design the boot check tests the same wires without this design (`p2-uart`, `p2-serial`): [Installing the
Acorn packages](../setup/packages.md#installing-the-acorn-packages).

The loopback design (`pmod-loopback`) returns on K2 the inverse of what it sees
on J2, and nothing else: GPIO14 → J2 → inverted → K2 → GPIO15. It does not touch
J5 or H5; on a Raspberry Pi 5 those two wires are tested by `fpgas-verify`
(`p2-gpio`) on a card that runs the fpgas.online design.

## The design this page loads

```{include} ../inc/release-designs.inc
```

Set `LOOPBACK` to the file you downloaded or built. `<variant>` is `cle-215p`, `cle-215` or `cle-101`; for a
CLE-215+ and the release's file:

```console
$ LOOPBACK=pmod-loopback_acorn-cle-215p_vivado-vivado_sqrl_acorn.bit
```

## Before loading: the console and the getty must be off the FPGA's serial port

The loopback design drives serial TX. Check the host's kernel command line (`cat /proc/cmdline`) against
this before the load:

```{include} ../inc/kernel-console.inc
:heading-offset: 1
```

## On a Raspberry Pi 5

```console
$ sudo systemctl stop serial-getty@ttyAMA0
$ sudo systemctl mask serial-getty@ttyAMA0
# Detach the endpoint first, as before every JTAG load, then load the loopback bitstream
$ echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove
# The libgpiod cable opens gpiochip0, the header is gpiochip15
$ sudo ln -sfn /dev/gpiochip15 /dev/gpiochip0
$ openFPGALoader --cable libgpiod --pins 10:9:11:8 $LOOPBACK
# The loopback inverts each bit, so what comes back is not what was sent
$ stty -F /dev/ttyAMA0 115200 raw -echo
$ (sleep 1; echo test > /dev/ttyAMA0) &
$ timeout 3 cat /dev/ttyAMA0 | od -An -tx1
```

Some bytes arriving means J2 and K2 both carry; they are not the bytes sent,
and because the design holds the line inverted while idle the UART may report
framing errors or a break as well. No bytes at all means K2 or GPIO15 is not
connected. These commands are written from the design's source: not yet run by
us in this form.

## On a Compute Blade

Under kernel 6.18 this check cannot be done by hand in one
boot: the
loopback design has to be loaded over JTAG, which needs the header's serial
port off, and the test itself needs the serial port on ([JTAG on a
blade](compute-blade-jtag-by-hand.md#jtag-on-a-blade)). The serial pair of a blade is checked by
`fpgas-verify` (`p2-uart`, `p2-serial`) once the card runs the fpgas.online
design from its flash; whether a ps1 blade card has that is on its installations page (see [What each blade
still needs](../installations/ps1.md#what-each-blade-still-needs)).

## If it goes wrong

The last row sends you to the pin-ID design. Before loading that one:

```{include} ../inc/gpio-contention.inc
```


| Problem | Likely cause | Fix |
|---------|--------------|-----|
| No UART output | serial-getty holding the port, wrong baud, or K2/J2 not crossed over | Mask serial-getty, use 115200, run pin-ID and check GPIO15 reads `K2` |
