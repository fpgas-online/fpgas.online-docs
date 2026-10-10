The loopback and pin-ID designs are in no package. CI builds them and attaches them to the
[releases](https://github.com/fpgas-online/fpgas.online-test-designs/releases) of fpgas.online-test-designs as
`pmod-loopback_acorn-<variant>_vivado-vivado_sqrl_acorn.bit` and
`pmod-pin-id_acorn-<variant>_vivado-vivado_sqrl_acorn.bit`, for example in the release
`vivado-bitstreams-v0.0-496-gf162f60`. Build the pin-ID design from `main`, not from that release. Copy the file
to the host and put its name in `LOOPBACK` or `PINID`.

A card that runs the fpgas.online design needs none of these files for the wiring check:
[on a Compute Blade](/boards/acorn/checks/compute-blade.md), [on a Raspberry Pi 5](/boards/acorn/checks/rpi-5.md).
