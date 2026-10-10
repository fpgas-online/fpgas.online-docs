---
type: explanation
owner: documentation maintainers
reader: someone who wants to know how a design reaches a Fomu EVT on fpgas.online
review: 2026-11-10
---

# Programming a Fomu EVT

**You want to know how a design reaches a Fomu EVT.** After a test design loads, the board leaves USB. The commands are on [How to load a design onto a Fomu EVT with openFPGALoader](../setup/load-design.md); the pins are on [Fomu EVT specifications](specifications.md).

:::{admonition} Figure to come
:class: placeholder

The three layers of programming a Fomu EVT side by side. They are the protocol (USB DFU), the connection (the USB-A plug, then two GPIO header pins) and the tool (openFPGALoader). Tracked in ISSUE-03.
:::

## The protocol: USB DFU

The Fomu boots from its SPI flash into a DFU bootloader (DFU Bootloader v2.0.4). The DFU (Device Firmware Upgrade) protocol then loads a replacement bitstream into the iCE40's volatile SRAM over USB. The bootloader resides in the SPI flash. It provides the USB DFU interface when no valid application is present or when the user triggers DFU mode. The iCE40UP5K otherwise loads its bitstream from the flash automatically on power-up.

The Fomu is programmed over USB DFU rather than over JTAG. The same USB interface can act as a CDC-ACM serial port or a custom USB device, depending on the loaded design.

## The connection: USB, then two header pins

A design is loaded through the Fomu's USB-A connector, which plugs into a USB port of the Raspberry Pi. An inline [USB analyser](usb-analysers.md) sits between them when one is fitted. The Fomu enumerates as `1209:5bf0` while its bootloader runs.

The test bitstreams contain no USB core, so the Fomu leaves USB the moment one is loaded. The harness then talks to the design over two pins on the GPIO header. Those pins are wired to the Pi's own GPIO UART, which the Pi opens as `/dev/serial0`. This is a direct connection, not through USB. The pins and the Pi's side are on [Fomu EVT wiring to a Raspberry Pi](../setup/wiring.md).

## The tool: openFPGALoader

fpgas.online loads the board from its Raspberry Pi with `openFPGALoader -b fomu`, which speaks DFU itself and needs nothing else installed on the Fomu side. That is the path the test harness takes. It loads a `.bin` bitstream, which is a volatile SRAM load, so a power cycle of the Fomu discards it.

## The bootloader's window

The bootloader waits only for a limited window. If no DFU activity occurs within it, the bootloader warm-boots the iCE40 to load the user bitstream from the SPI flash. The user bitstream typically has no USB, so the Fomu then disappears from USB. The window is about 3 minutes.

A PoE power cycle of the Pi resets the Fomu and restarts the DFU bootloader. It also discards the volatile SRAM load, so whatever was programmed is gone and the window starts over. A Fomu missing from USB is therefore usually not broken: the fixes are on [Fomu EVT programming faults](../troubleshooting/programming-faults.md).
