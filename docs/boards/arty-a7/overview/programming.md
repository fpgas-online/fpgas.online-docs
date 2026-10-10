---
type: explanation
owner: documentation maintainers
reader: someone who wants to know how a design reaches an Arty A7 on fpgas.online
review: 2026-11-10
---

# Programming an Arty A7

**You want to know how a design reaches an Arty A7.** Three layers answer it: the protocol, the cable and the tool. The commands are on [How to load a design onto an Arty A7](../setup/load-design.md) and [How to write a design into an Arty A7's flash](../setup/write-flash.md).

:::{admonition} Figure to come
:class: placeholder

The three layers of programming an Arty A7: JTAG, the USB cable to the FTDI chip's channel A, and openFPGALoader. Tracked in [docs issue #138](https://github.com/fpgas-online/fpgas.online-docs/issues/138).
:::

## The protocol

The Arty A7 is configured over JTAG, which reaches it through its on-board FTDI FT2232H.

## The connection

One USB cable joins the Arty to its Raspberry Pi. The FTDI chip carries JTAG on channel A and the UART on channel B. The host sees two `/dev/ttyUSB*` devices: `/dev/ttyUSB0` is the JTAG channel and `/dev/ttyUSB1` is the UART channel.

A board whose FTDI is disconnected has no `/dev/ttyUSB*` devices at all. It cannot be programmed or reached on its console. The pins of each channel are on [Arty A7 wiring to a Raspberry Pi](../setup/wiring.md).

## The tool

fpgas.online loads the Arty with openFPGALoader, selecting the board with `-b arty`. A bitstream is a `.bit` file. A plain load is a volatile load into the FPGA's SRAM, and it is lost at the next power cycle.

The same tool can write the on-board SPI flash with `--write-flash`. That replaces whatever the flash held, and the design then survives power cycles. The flash is the board's persistent bitstream storage.
