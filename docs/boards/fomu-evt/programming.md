# Fomu EVT: programming and LiteX

**You want to load a bitstream into a Fomu over USB DFU or iceprog, or the LiteX names for the board.**

## Programming

Three tools appear below and they are not interchangeable. The fleet programs
the board from its Pi host with `openFPGALoader -b fomu design.bin`, which
speaks DFU itself and needs nothing else installed on the Fomu side; that is the
path the test harness takes and the one described under
[Programming interface](wiring.md#programming-interface). `dfu-util -D design.dfu` is the
upstream manual equivalent of the same DFU transfer, but it takes a `.dfu`
container rather than the raw `.bin`. `iceprog` writes the SPI flash directly
and needs external SPI programming hardware, so it cannot be used on these hosts
at all.

### USB DFU (dfu-util)

The Fomu is programmed over USB using the DFU (Device Firmware Upgrade)
protocol. The `dfu-util` tool is used:

```console
# List connected DFU devices.
$ dfu-util -l
# Program a bitstream.
$ dfu-util -D design.dfu
# Program with explicit device selection.
$ dfu-util -d 1209:5bf0 -D design.dfu
```

The DFU bootloader resides in the SPI flash and provides a USB DFU interface
when no valid application is present or when the user triggers DFU mode. The
test infrastructure drives the same interface through `openFPGALoader` instead;
see [Programming interface](wiring.md#programming-interface).

If `dfu-util -l` shows nothing, the bootloader has probably timed out; see
[DFU bootloader timeout](wiring.md#dfu-bootloader-timeout).

### IceStorm Programmer (iceprog)

For direct SPI flash programming (this requires an external SPI programmer, so
it is not something that can be done from the Pi host):

```console
$ iceprog design.bin
```

Source: [Fomu Workshop](https://workshop.fomu.im)

## LiteX Integration

| Property        | Value                                             |
| --------------- | ------------------------------------------------- |
| Platform module | `litex_boards.platforms.kosagi_fomu_evt`          |
| Target module   | `litex_boards.targets.kosagi_fomu`                |
| Default clock   | `clk48` (48 MHz, pin 44)                          |
| Programmer      | IceStorm (`iceprog`)                              |
| Toolchain       | Yosys + nextpnr-ice40 (open source, IceStorm flow) |

The pin-mapping notes give the toolchain as `icestorm` / `nextpnr-ice40`, which
is the same open-source flow.

:::{note}
The `Programmer | IceStorm (iceprog)` row is the LiteX platform default, not the
path this fleet uses. `iceprog` needs external SPI programming hardware; the
hosts program the board over USB DFU with `openFPGALoader`, as described under
[Programming](#programming).
:::

Source: [LiteX platform file for the Fomu EVT](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_fomu_evt.py)
