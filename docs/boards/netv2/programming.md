# NeTV2: programming and LiteX

**You want the commands to program a NeTV2 at a glance, or the LiteX names to build a design for it.**

## Programming

See [JTAG via RPi GPIO](jtag.md) for the full openFPGALoader
and OpenOCD commands, and for which host uses which.

### Quick Reference

On rpi5-netv2, detach the PCIe endpoint first — see [the warning](jtag.md#rpi-5-gpio-bitbang-slow).

Volatile load on an RPi 3B+ or RPi 5, GPIO bitbang:

```console
$ sudo openFPGALoader --cable libgpiod --pins 27:22:4:17 design.bit
```

Persistent SPI flash on an RPi 3B+ or RPi 5, GPIO bitbang. This overwrites
whatever bitstream the flash already holds, so keep a copy first:

```console
$ sudo openFPGALoader --cable libgpiod --pins 27:22:4:17 --write-flash design.bit
```

Volatile load on rpi3-netv2, which is driven with OpenOCD instead:

```console
$ sudo openocd -f ~/netv2/alphamax-rpi.cfg -c 'init; pld load 0 <bitstream>; exit'
```

Once the NeTV2 board definition is upstream:

```console
$ sudo openFPGALoader -b netv2 design.bit
```

## LiteX Integration

| Property        | Value                                                  |
| --------------- | ------------------------------------------------------ |
| Platform module | `litex_boards.platforms.kosagi_netv2`                  |
| Target module   | `litex_boards.targets.kosagi_netv2`                    |
| Default clock   | `clk50` (50 MHz, pin J19)                              |
| Programmer      | openFPGALoader (`libgpiod`, pins 27:22:4:17) |
| Toolchain       | Vivado (proprietary) or openXC7 (open source)          |

Source: [LiteX platform file for the NeTV2](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/kosagi_netv2.py)
