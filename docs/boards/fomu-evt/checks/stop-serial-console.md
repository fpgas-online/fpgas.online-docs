---
type: how-to
owner: documentation maintainers
reader: someone about to run the Fomu EVT's UART test on its Raspberry Pi
review: 2026-11-10
---

# How to stop the serial login console before a Fomu UART test

**You want the Fomu EVT's UART test to own `/dev/serial0`.**

The Pi's login console holds it; the wires are on [Fomu EVT wiring to a Raspberry Pi](../setup/wiring.md#serial-uart-on-the-gpio-header).

## What you need

- A Raspberry Pi with the Fomu EVT on its GPIO header and a GPIO UART at `/dev/serial0`.
- `sudo` rights on the Pi.

## Steps

1. On the Pi, stop early if there is no GPIO UART here. Otherwise the lookup in step 2 resolves to nothing, and the mask silently targets the wrong unit.

```console
$ [ -e /dev/serial0 ] || { echo "no GPIO UART on this host"; exit 1; }
```

2. In the same shell, resolve `serial0` to the real device; this works whether the GPIO UART is the PL011 (`ttyAMA0`) or the mini UART (`ttyS0`).

```console
$ GETTY="serial-getty@$(basename "$(readlink -f /dev/serial0)").service"
```

3. Mask the unit, which prevents systemd from restarting the serial login console.

```console
$ sudo systemctl mask "$GETTY"
```

4. Stop the instance that is running.

```console
$ sudo systemctl stop "$GETTY"
```

5. Kill any remaining process holding the port.

```console
$ sudo fuser -k /dev/serial0
```

6. Fix the permissions after `serial-getty` releases the device.

```console
$ sudo chmod 666 /dev/serial0
```

7. With the Fomu in its DFU bootloader (`lsusb` lists `1209:5bf0`), run the UART test. It loads the UART echo design, then opens `/dev/serial0` at 115200 baud. It is the check's `uart` test, described on the page under Next.

The UART echo design has no USB core, so after the test the Fomu is off USB. The second command puts foboot back for
the next load: it resets the Fomu through the header and waits for `1209:5bf0` on USB.

```console
$ sudo fpgas-fomu-debug test uart
$ sudo fpgas-fomu-debug reset
```

## Check

- Each command returns without an error.
- The UART test reads its echo from the design on `/dev/serial0`.
- After `fpgas-fomu-debug reset`, `lsusb` lists `1209:5bf0` again.

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| `no GPIO UART on this host` | `/dev/serial0` does not exist on this Pi | Run the test on a Pi that has the GPIO UART |
| The test cannot load the design; `lsusb` does not list `1209:5bf0` | The Fomu is out of its DFU bootloader | [Fomu EVT programming faults](../troubleshooting/programming-faults.md) |
| `fpgas-fomu-debug reset` says foboot did not come back on USB | The reset through the header did not restart foboot | Ask the site operator, then power-cycle the Fomu's host, and check `lsusb` again |
| The test reads nothing, or the output is corrupt | The login console came back and consumes the serial data: `serial-getty` was stopped but not masked | Run the block again; the `mask` line keeps systemd from restarting it |

## Next

- [How to load a design onto a Fomu EVT with openFPGALoader](../setup/load-design.md)
- [Fomu EVT test faults](../troubleshooting/test-faults.md)
- [fpgas-verify: what an Arty, NeTV2, Fomu or TT FPGA check tests](../../../verify/tests.md#what-the-check-tests-on-each-board)
