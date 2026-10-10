---
type: how-to
owner: documentation maintainers
reader: someone about to run a test over a NeTV2's GPIO UART
review: 2026-11-10
---

# How to free a NeTV2's serial port before a test

**You want to run a test that reads a NeTV2 design's output on the Pi's GPIO UART.**

The login console holds that port open and eats or corrupts the design's output. The device for each Pi model is in [Serial device by Raspberry Pi model](../overview/specifications.md#serial-device-by-raspberry-pi-model).

## What you need

- A NeTV2 wired as on [NeTV2 wiring to a Raspberry Pi](wiring.md#primary-uart).
- `sudo` on the Pi: the `pi` user is not in the `dialout` group, so the port must be opened with `sudo`.

## Steps

1. On the Pi, run `sudo systemctl stop 'serial-getty@*'` to stop the serial login console.
2. On a Raspberry Pi 5, run `pinctrl set 14 a4; pinctrl set 15 a4` to restore the UART function of GPIO14 and GPIO15, which is ALT4 (TXD0/RXD0).
3. On the Pi, open the GPIO UART device for your Pi model with `sudo`, at 115200 baud, and run the test.

## Check

The design's output arrives on the device whole and uncorrupted.

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| The design's output is missing or corrupt | The login console still holds the port | Run step 1 again |
| On a Raspberry Pi 5 the port is silent after step 1 | Stopping the console drops the pin mux, so GPIO14 and GPIO15 are plain GPIO | Run step 2 |
| The test cannot open `/dev/ttyAMA0` on a Raspberry Pi 3 with Bluetooth enabled | The GPIO UART there is the mini UART at `/dev/ttyS0` | Change the test's `--port` to `/dev/ttyS0` |

## Next

- [UART test parameters](../overview/specifications.md#uart-test-parameters)
- [NeTV2 checks](../checks/index.md)
