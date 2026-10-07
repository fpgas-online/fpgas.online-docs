# Arty A7: programming and LiteX

**You want to load a bitstream into the Arty from its Raspberry Pi, or the LiteX names for the board.**

## LiteX Integration

| Property | Value |
|----------|-------|
| Platform module | `litex_boards.platforms.digilent_arty` |
| Target module | `litex_boards.targets.digilent_arty` |
| Default clock | `clk100` (100 MHz, pin E3) |
| Programmer | OpenOCD with `openocd_xc7_ft2232.cfg` |
| BSCAN SPI bitstream | `bscan_spi_xc7a35t.bit` or `bscan_spi_xc7a100t.bit` |
| Toolchain | Vivado (proprietary) or openXC7 (open source) |

Source: [digilent_arty.py](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/digilent_arty.py)

## Programming

### Via openFPGALoader (USB-JTAG)

```console
# The first form is a volatile load, lost on the next power cycle. The second
# writes the on-board SPI flash and replaces whatever was there.
$ openFPGALoader -b arty design.bit
$ openFPGALoader -b arty --write-flash design.bit
```

### Via OpenOCD (USB-JTAG)

```console
$ openocd -f openocd_xc7_ft2232.cfg -c "init; pld load 0 design.bit; exit"
```
