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

7. Start the UART test with the arguments `--port /dev/serial0 --board fomu --skip-banner`; the test opens `/dev/serial0` at 115200 baud. The test is the check's `uart` test, described on the page under Next.

## Check

- Each command returns without an error.
- The UART test reads its echo from the design on `/dev/serial0`.

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| `no GPIO UART on this host` | `/dev/serial0` does not exist on this Pi | Run the test on a Pi that has the GPIO UART |
| The test reads nothing, or the output is corrupt | The login console came back and consumes the serial data: `serial-getty` was stopped but not masked | Run the block again; the `mask` line keeps systemd from restarting it |

## Next

- [How to load a design onto a Fomu EVT with openFPGALoader](../setup/load-design.md)
- [Fomu EVT test faults](../troubleshooting/test-faults.md)
- [fpgas-verify: what an Arty, NeTV2, Fomu or TT FPGA check tests](../../../verify/tests.md#what-each-boards-check-tests)
