---
type: reference
owner: documentation maintainers
reader: someone whose Fomu EVT is missing from USB or has lost its design
review: 2026-11-10
---

# Fomu EVT programming faults

**Your Fomu EVT has left `lsusb`, or its design is gone.**

Loading is on [How to load a design onto a Fomu EVT with openFPGALoader](../setup/load-design.md); the reasons are on [Programming a Fomu EVT](../overview/programming.md#the-bootloaders-window).

Each row gives what you see, the likely cause and the fix.

| Problem | Likely cause | Fix |
|---------|--------------|-----|
| The Fomu is not in `lsusb` | It timed out of DFU after about 3 minutes, or it runs a test bitstream with no USB core | Power cycle the Pi's PoE port, which resets the Fomu and restarts the DFU bootloader; do not look for a dead board first |
| The Fomu disappears from USB after programming | The custom test bitstreams (UART echo, GPIO loopback) include no USB | Nothing: this is expected; talk to the design on `/dev/serial0` |
| The design loaded before a power cycle is not running | The power cycle starts the bootloader again, and the roughly three-minute window starts over; the user image stays in the flash until the next DFU load | Load the design again inside the window |
