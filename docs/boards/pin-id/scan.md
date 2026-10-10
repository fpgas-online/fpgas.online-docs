---
type: how-to
owner: documentation maintainers
reader: someone with an Arty A7 on a Raspberry Pi with a PMOD HAT
review: 2026-11-10
---

# How to scan a board's wiring with the pin-id design

**You have an Arty A7 joined to a Raspberry Pi through a PMOD HAT and want to read which FPGA pin each GPIO reaches**. The commands on this page are for the Arty A7. Other boards need their own build and program targets: [How to add a board to the pin-id design](add-board.md). How the design works is on [The pin-id design](../pin-id.md).

## What you need

- An Arty A7 cabled to the Raspberry Pi's [PMOD HAT](../pmod/rpi-hat.md) with the three ribbon cables.
- A checkout of the [test-designs repository](https://github.com/fpgas-online/fpgas.online-test-designs) with the `designs/pmod-pin-id` directory.
- `uv` on both machines: the design's `make` targets run Python through `uv run`.
- A machine that builds the bitstream and has the Arty's USB cable, for steps 1 and 2. The scanner of step 3 runs on the Raspberry Pi, from the same directory of a checkout there.

## Steps

1. On the machine that builds, in `designs/pmod-pin-id`, build the Arty bitstream, which CI also does automatically.

   ```console
   $ cd designs/pmod-pin-id
   $ make gateware-arty
   ```

2. In the same directory, on the machine with the Arty's USB cable, program the FPGA, which makes every PMOD pin start sending its name.

   ```console
   $ make program-arty
   ```

3. On the Raspberry Pi, in `designs/pmod-pin-id`, run the scanner, which prints one line per GPIO and then a mapping table.

   ```console
   $ make scan-arty
   ```

## Check

The scan ends with a table that gives every scanned GPIO an FPGA pin name. This is the output of a clean scan:

```text
=== FPGA Pin Identification Scanner ===
Baud rate:  1200
GPIO chip:  /dev/gpiochip0
Scanning:   21 GPIO pins

  GPIO 8 (HAT JA pin 01       ) -> G13
  GPIO19 (HAT JA pin 07       ) -> D13
  GPIO21 (HAT JA pin 08       ) -> B18
  GPIO20 (HAT JA pin 09       ) -> A18
  GPIO18 (HAT JA pin 10       ) -> K16
  GPIO 7 (HAT JB pin 01       ) -> E15
  GPIO26 (HAT JB pin 07       ) -> J17
  GPIO13 (HAT JB pin 08       ) -> J18
  ...

=== Pin Mapping Table (21 confirmed, 0 garbled, 0 no signal) ===

| RPi GPIO | HAT Location           | FPGA Pin |
|----------|------------------------|----------|
| GPIO7    | HAT JB pin 01          | E15      |
| GPIO8    | HAT JA pin 01          | G13      |
| ...
```

A line such as `GPIO8 (HAT JA pin 01) -> G13` means FPGA pin G13 is physically connected to Raspberry Pi GPIO8 through the cable. Look G13 up in the FPGA platform file to find which connector and pin position it belongs to.

## If it fails

Each row is a line the scanner prints for one GPIO.

| What you see | Likely cause | Fix |
|---|---|---|
| `GPIO7 (HAT JB pin 07) -> (garbled: '????a????a')` | Python timing jitter missed bit boundaries | Run the scan again |
| `GPIO7 (HAT JB pin 07) -> (garbled: '????a????a')` | Two FPGA outputs drive one GPIO, as on the HAT's shared SPI pins JA2-4 and JB2-4 | None on this page: pins 2-4 of JA cannot be verified independently while JB is also connected |
| `GPIO7 (HAT JB pin 07) -> (garbled: '????a????a')` | A kernel driver (SPI, I2C, UART) is driving the GPIO | Run without `--no-unload`, so the scanner unloads the SPI modules |
| `GPIO0 (HAT JB pin 09) -> (no signal)` | The GPIO routes to no FPGA pin, as GPIO0 and GPIO1 (the HAT's I2C EEPROM) | None: they always show no signal |
| `GPIO0 (HAT JB pin 09) -> (no signal)` | A pull-up overrides the FPGA's drive (not expected with LVCMOS33 at 3.3V) | None known |
| `GPIO0 (HAT JB pin 09) -> (no signal)` | The PMOD cable for this port is not plugged in | Plug the cable into this port |
| `GPIO0 (HAT JB pin 09) -> (no signal)` | A different GPIO chip on a Raspberry Pi 5 (`pinctrl-rp1`, not `pinctrl-bcm2711`) | None: the scanner detects the chip itself |

A garbled line means start bits arrived but the UART frames did not decode cleanly. A "no signal" line means the GPIO stayed high (idle).

## Next

- [Pin-id scanner options](scanner-options.md)
- [How to add a board to the pin-id design](add-board.md)
- [The pin-id design](../pin-id.md)
- [Raspberry Pi PMOD HAT](../pmod/rpi-hat.md)
- [Tiny Tapeout PMOD layouts](../pmod/tinytapeout.md)
