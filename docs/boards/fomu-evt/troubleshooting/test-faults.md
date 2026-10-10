---
type: reference
owner: documentation maintainers
reader: someone whose Fomu EVT does not answer the UART test, or fails the `pmod` or `pin-id` test
review: 2026-11-10
---

# Fomu EVT test faults

**Your Fomu EVT is loaded, but its UART, `pmod` or `pin-id` test fails.**

The Pi's side of the UART test is on [How to stop the serial login console before a Fomu UART test](../checks/stop-serial-console.md).

Each row gives what you see, the likely cause and the fix.

| Problem | Likely cause | Fix |
|---------|--------------|-----|
| `no GPIO UART on this host` | `/dev/serial0` does not exist on this Pi | Run the UART test on a Pi that has the GPIO UART |
| The serial data never reaches the test | `serial-getty` was stopped but not masked, so it came back and consumes the data | Mask the unit, as in the serial console how-to |
| The `pmod` or `pin-id` test never passes | An EVT on the Pi's header has no loopback pair: GPIO27 is CRESET and GPIO9 is the flash's MISO, and no net joins them | None on the board: [test-designs issue #202](https://github.com/fpgas-online/fpgas.online-test-designs/issues/202) |
