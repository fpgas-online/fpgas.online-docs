# Tiny Tapeout FPGA board on a Raspberry Pi: what is known about the parts

**You are about to put a Tiny Tapeout FPGA demo board on a Raspberry Pi with a Pmod HAT and want to know what
is known and what is not known about the parts it takes. This is not a list to buy from.**

**No bill of materials has been written.** No document of ours holds part numbers, suppliers or quantities
for this build. The list below is the parts the records name, each with what is and is not recorded about it.

| Part | What is recorded | What is not recorded |
|---|---|---|
| Tiny Tapeout demo board, version 3 (TTDBv3), with the FabricFox iCE40UP5K FPGA breakout in its chip socket | [device info](../overview/device-info.md), [variants](../overview/variants.md) | where it was bought; how the breakout is seated in the socket |
| Raspberry Pi | on 3 September 2026 each board at welland was on a Raspberry Pi 4 Rev 1.5 (2 GB or 8 GB): [the boards at welland](../installations/welland.md) | which other models work. A Pi 3B+ is recorded as unable to reflash the demo board's microcontroller by its mass-storage path: [firmware](../designs/firmware.md#demoboard-hang-on-boot) |
| Digilent Pmod HAT Adapter | its ports and GPIOs: [Raspberry Pi PMOD HAT](../../pmod/rpi-hat.md) | part number and supplier |
| Ribbon cables, female to female, one for each of the three headers, each joined to the 12-pin sockets through a strip of pin header | the 3.3 V pins (6 and 12) are expected not to be connected (Tim Ansell, 7 October 2026); they join pin 1 to pin 1; the sockets on both boards are female (from the makers' documents, not checked by us): [the cables](index.md#the-cables-33-v-not-connected), [which cable goes where](../wiring/cables.md) | whether they have 10 or 12 wires; the supplier (Tim believes whiteeeen, Amazon product B094RGMBS9; not checked by us) |
| USB-C cable | from the demo board's USB-C socket to a USB port of the Raspberry Pi | length; which USB port |

**Only at welland.** These belong to how the fleet runs the boards, not to the board: a Pi of your own needs
neither the camera nor PoE.

| Part | What is recorded | What is not recorded |
|---|---|---|
| ov5647 camera | each host has one, publishing a live feed of the board: [Camera](../../../setup/pi.md#camera) | its mount, its cable and how it is aimed |
| Power and network for the Raspberry Pi | the Pis are powered and networked through PoE switches | what takes the power off the Ethernet cable on a Pi whose 40-pin header carries a Pmod HAT |

The software is not a part to buy: the packages are installed in [verifying 1](verifying-1.md).
