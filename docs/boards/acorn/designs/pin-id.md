# Acorn test: pin ID

**You have an Acorn wired to a Raspberry Pi 5 or to a Compute Blade and want to read off by hand, with the
pin-ID design, which FPGA ball each P2 wire is connected to.** On a card that runs the fpgas.online design
the boot check names a wrong wire without this design: [on a Raspberry Pi
5](../building/rpi-5/verifying-1.md), [on a Compute Blade](../building/compute-blade/verifying-1.md).

```{include} ../wiring/gpio-contention.inc
```

## The design this page loads

```{include} release-designs.inc
```

## On a Raspberry Pi 5

```console
$ echo 1 | sudo tee /sys/bus/pci/devices/0001:01:00.0/remove   # detach first, as before every JTAG load
# The libgpiod cable opens gpiochip0, the header is gpiochip15
$ sudo ln -sfn /dev/gpiochip15 /dev/gpiochip0
$ openFPGALoader --cable libgpiod --pins 10:9:11:8 $PINID
# Each ball transmits its own name at 1200 baud. Correctly wired:
# GPIO15 → "K2" (serial TX, on the Pi's RXD0)
# GPIO14 → "J2" (serial RX, on the Pi's TXD0)
# GPIO3  → "J5" (spare GPIO)
# GPIO4  → "H5" (spare GPIO)
```

## On a Compute Blade

```{include} blade-first.inc
```

```{include} ../wiring/blade-jtag-serial-off.inc
```

Not yet run by us on a blade wired as on [Acorn wiring on a Compute Blade](../wiring/compute-blade.md).

:::{warning}
**Not on a blade whose J2 wire has no 470 Ω resistor**, which is pi20 at ps1 as it is
wired today ([Acorns at ps1](../installations/ps1.md#the-cards)). The moment
the load finishes, the pin-ID design drives J2, and J2 is on GPIO14, which
openFPGALoader has just left an output. With the resistor that is about 7 mA
for a moment; without it, it is two outputs shorted together, which costs JTAG
until a power cycle and can crash the host.
:::

Like every JTAG load on a blade it needs a boot with the header's serial port
off. The load and the command that makes
GPIO14 an input again are **one command line**, so that nothing is typed
between them, and the pins are put back even if the load fails:

```console
$ echo 1 | sudo tee /sys/bus/pci/devices/$BDF/remove   # detach first, as before every JTAG load
$ openFPGALoader --cable libgpiod --pins 2:3:4:14 $PINID; pinctrl set 14 ip pn; pinctrl set 2,4 no pu
# GPIO14 is now an input with no pull: do NOT set it to a0 or a4 while pin-ID runs.
# Only GPIO15 → "K2" and GPIO14 → "J2" answer: J5 and H5 are not connected.
# The design drives J2, which shares GPIO14 with TMS. The 470 Ω resistor in the
# J2 wire is there so that JTAG still works afterwards; without it JTAG is lost
# until a power cycle (see "The shared line and the 470 Ω resistor").
```

## Reading the pins

Only GPIO15 can be a hardware UART receiver on a Pi 5, so the other three are
decoded from edge timestamps: [the repository's pin-ID host
scanner](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/pmod-pin-id/host/identify_pmod_pins.py)
requests both-edge events through gpiod (v1 or v2), rebuilds the 1200-baud
frames from the kernel timestamps (833 µs per bit against nanosecond stamps),
and finds the header chip by label, so it works on a Pi 5. `gpiomon` edge
timestamps decoded by hand work the same way. Do not sample the pins by polling
from Python: polling mis-frames the bytes even on a clean signal. Keep GPIO14 an
input throughout (the warning at the top of this page).
Check the method on a positive control before trusting a negative: drive a
spare Pi GPIO and confirm the monitor sees it. The design is described under
[Verifying wiring with the pin-id design](../../pin-id.md). Which of these readers
works on a blade under kernel 6.18 is not known.

## A passive check, without a bitstream

A passive check needs no bitstream: toggle the Pi's internal pull-up, then
pull-down, on each line and see whether the line follows. A ~50 kΩ internal pull
loses to any real driver, so a line that follows is floating (the far end is an
FPGA input: J2) and one that stays put is driven (an FPGA output: K2). It cannot
read GPIO2 or GPIO3 where they carry I²C pull-ups. The same test shows whether
P1 is mated: the Acorn pulls TCK up, so a TCK line that the Pi's pull-down
cannot move has the card on the end of it, and one that follows has nothing.

## If it goes wrong

| Problem | Likely cause | Fix |
|---------|--------------|-----|
| Pi crashes the instant a GPIO is set to output | Contention with an FPGA output on the same wire (pin-ID drives all four P2 balls) | Keep GPIO14 an input (`pinctrl set 14 ip pn`) while pin-ID runs |
