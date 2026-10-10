---
type: explanation
owner: documentation maintainers
reader: someone who wants to know how pin-id reads a cable's wiring
review: 2026-11-10
---

# The pin-id design

**The pin-id design makes each FPGA pin send its own name over a slow UART**. A host scanner then reads a cable's pin mapping off the wire. This page explains how the design works and why. The commands to scan are on [How to scan a board's wiring with the pin-id design](pin-id/scan.md). Adding a board is on [How to add a board to the pin-id design](pin-id/add-board.md).

Several board pages defer their open wiring questions to this method. They include the Arty A7's [PMOD cable routing](arty-a7/setup/wiring.md#pmod-cables), the Acorn's [P2 wiring check](acorn/checks/pin-id.md) and the TT FPGA's [pin mapping](tt-fpga/overview/pin-mapping.md).

```{toctree}
:hidden:

pin-id/scan
pin-id/scanner-options
pin-id/add-board
```

## How it works

Each FPGA output pin continuously transmits its own name as slow UART data. A host GPIO connected to any FPGA pin decodes the name and so identifies the connection.

```text
FPGA Pin G13 ──── transmits "G13\r\n" at 1200 baud ────> RPi GPIO8
FPGA Pin B18 ──── transmits "B18\r\n" at 1200 baud ────> RPi GPIO21
FPGA Pin E15 ──── transmits "E15\r\n" at 1200 baud ────> RPi GPIO7
  ...every pin simultaneously...
```

## Why 1200 baud

Three properties of 1200 baud decide it.

- **Reliable with software bit-banging**: at 1200 baud each bit is about 833 us, which Python on a Raspberry Pi samples without real-time scheduling.
- **Trivial FPGA divider**: a 100 MHz clock divides to 1200 baud with 83,333 cycles per bit (0.0004% error). A 12 MHz iCE40 clock gives 10,000 cycles per bit.
- **No hardware UART needed on the host**: the Raspberry Pi scanner reads GPIO values directly with `gpiod`. It needs no serial port, no kernel driver and no device tree overlay.

## Why FPGA pin names

The design transmits the FPGA package ball name (`G13`, `V14`, `K16`) rather than a connector label (`JA01`). The ball name is the canonical, unambiguous identifier.

- It does not depend on which connector naming convention the board uses.
- It matches what constraint files (XDC, PCF) and schematics show.
- The pin can be looked up in the FPGA datasheet directly.
- The connector label can be derived by cross-referencing the platform file.

## Components

The design has two parts: the gateware that runs in the FPGA and the scanner that runs on the host.

### FPGA gateware

Two files make up the [pin-id gateware directory](https://github.com/fpgas-online/fpgas.online-test-designs/tree/main/designs/pmod-pin-id/gateware/).

**`pmod_pin_id.py`** holds the reusable `UARTTxIdentifier` Migen module. Each instance is a tiny state machine. It has a baud rate counter, a character index into the label string and a 10-bit shift register (start, 8 data, stop). The pin idles high and continuously cycles through the label characters. The module is board-agnostic and works with any LiteX platform.

**`pmod_pin_id_<board>.py`** is the board-specific build script. It extracts FPGA pin names from the LiteX platform's connector table and instantiates one `UARTTxIdentifier` per pin. It is pure gateware, with no CPU and no firmware.

This is the Arty A7 build script (`pmod_pin_id_arty.py`):

```python
CONNECTORS = ["pmoda", "pmodb", "pmodc", "pmodd"]

def build_pin_list(platform):
    pins = []
    for connector_name in CONNECTORS:
        connector_pins = platform.constraint_manager.connector_manager.connector_table[connector_name]
        for idx in range(len(connector_pins)):
            resource_pin = f"{connector_name}:{idx}"
            fpga_pin = connector_pins[idx]
            label = f"{fpga_pin}\r\n"
            pins.append((resource_pin, label))
    return pins
```

The pin names come directly from the platform definition, with no hardcoding and no manual lookup tables.

### Host scanner

The [pin-id host scanner](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/designs/pmod-pin-id/host/identify_pmod_pins.py) is a Python script that runs on the Raspberry Pi. For each GPIO pin it sets the line as input using `gpiod` (v1.6+ or v2.x). It waits for the line to go HIGH (idle). It detects the HIGH-to-LOW transition, which is the UART start bit. It then samples 8 data bits at the centre of each bit period and repeats for multiple frames to build a label string.

The scanner tries 10 frames per GPIO and uses majority voting. It validates the decoded label against the expected format and reports the mapping. A label is accepted only if it matches `^[A-Z][A-Za-z0-9]{1,3}$`, which FPGA pin names such as `G13` and `V14` do.

## Cross-validation

Two independent scans give high confidence in a mapping.

- **PMOD name scan**: the gateware transmits connector pin names (`JA01`) instead of FPGA ball names. This tests the firmware's index-to-physical-pin mapping.
- **FPGA pin name scan**: the default mode, which reads pin names directly from the LiteX platform connector table.

If both scans agree, with each GPIO mapping to the expected FPGA pin for its connector position, the mapping is verified. Any disagreement points to a bug in the connector table, a cable swap or a documentation error. This is how the [Arty A7 mapping](arty-a7/setup/wiring.md#pmod-cables) was verified. Of 21 unique GPIOs, 17 decoded correctly in both scans, and the 4 that garbled in one scan were confirmed via the other.

A loopback test cannot arbitrate bit order, because driving and reading use the same permutation and any consistent swap between the two still passes. The pin-id design can, as recorded in [test-designs issue #19](https://github.com/fpgas-online/fpgas.online-test-designs/issues/19).

## Limitations

- **Shared GPIOs**: the PMOD HAT shares GPIO9, GPIO10 and GPIO11 between ports JA and JB (the SPI bus). With cables on both Arty JA and JB, these GPIOs see bus contention and read the stronger driver's signal, typically JB. Pins 2-4 of JA cannot be independently verified while JB is also connected.
- **I2C EEPROM GPIOs**: GPIO0 and GPIO1 on the Raspberry Pi serve the HAT's I2C EEPROM and are not routed to any PMOD port. They always show "no signal".
- **Baud rate and label length**: shorter labels (2-3 characters for FPGA names like `G13`) repeat faster than longer ones (4 characters like `JA01`). They give more decode attempts and slightly different timing, and both work reliably.
- **32 simultaneous UART TX modules**: the design uses a few hundred LUTs on Artix-7 for 32 instances. It cannot be combined with other gateware, because it is a dedicated diagnostic bitstream and not a test overlay.
