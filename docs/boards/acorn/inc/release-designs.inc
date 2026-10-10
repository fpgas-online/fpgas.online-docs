The loopback and pin-ID designs are **not in any package**.
They are built by CI and attached to the
[releases](https://github.com/fpgas-online/fpgas.online-test-designs/releases)
of fpgas.online-test-designs, named
`pmod-loopback_acorn-<variant>_vivado-vivado_sqrl_acorn.bit` and
`pmod-pin-id_acorn-<variant>_vivado-vivado_sqrl_acorn.bit` in the release
`vivado-bitstreams-v0.0-496-gf162f60`. That release's pin-ID build for the Acorn
configures but never toggles a pin ([Images](/boards/acorn/overview/design.md#images)), so
pin-ID has to be built from `main`. Download or build the file, copy it to the
host, and put its name in `LOOPBACK` or `PINID`.

This is the check by hand. To check the wiring of a card that runs
the fpgas.online design, `fpgas-acorn-verify` needs none of these files:
[verifying on a Compute Blade](/boards/acorn/checks/compute-blade.md), [verifying on a Raspberry Pi
5](/boards/acorn/checks/rpi-5.md).
