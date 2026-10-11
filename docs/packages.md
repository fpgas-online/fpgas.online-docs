---
type: reference
owner: documentation maintainers
reader: someone installing fpgas.online packages on a host
review: 2026-11-10
---

# Packages

Debian packages for fpgas.online are served from
<https://apt.fpgas.online>, built by CI in the repository that owns each
package.

## Using the repository

The repository's key and the line for apt are step 1 of
[fpgas-verify: installing it](verify/installing.md#installing), which picks the suite for your Debian release.

## Checking a board

Each board's install page adds the repository and installs its package, with
`fpgas-verify`:
[Acorn](boards/acorn/setup/packages.md#installing-the-acorn-packages),
[Arty](boards/arty-a7/setup/packages.md#installing-the-arty-packages),
[NeTV2](boards/netv2/setup/packages.md#installing-the-netv2-packages),
[Fomu](boards/fomu-evt/setup/packages.md#installing-the-fomu-packages),
[Tiny Tapeout FPGA](boards/tt-fpga/setup/packages.md#installing-the-tt-fpga-packages).
[Checking a board: fpgas-verify](verify/fpgas-verify.md) covers running it and
reading the result.

## How packages get there

Each source repository builds its own `.deb` in CI and publishes it; the APT
repository pulls them in. Nothing needs write access to the source repositories
and no source repository needs a token for the APT repository.

1. A push to `main` builds the package and attaches it to a rolling GitHub
   Release in the source repository.
2. The `apt` repository pulls every `.deb` it has not seen across all such releases,
   regenerates the index, signs it, and republishes.

Versions come from `git describe`: `X.Y` exactly at a `vX.Y` tag, `X.Y.postN`
N commits later. Every push therefore produces a higher version that apt upgrades to,
with no manual bump.

## Related repositories elsewhere

Several tools used on the Pi hosts are packaged outside this organisation, each
publishing its own signed APT repository per Debian suite:

`openfpgaloader-rp1pio`, `openocd-rp1pio`
: [mithro/rp1-jtag](https://github.com/mithro/rp1-jtag) — retired. The hosts
  carry `openfpgaloader-fpgasonline-git` and `openocd-fpgasonline-git` from
  [fpgas.online-fpga-tools](https://github.com/fpgas-online/fpgas.online-fpga-tools)
  instead ([What runs on a Pi host](setup/pi.md)).

`python3-netgear-switch-library`
: [mithro/python-netgear-switch-library](https://github.com/mithro/python-netgear-switch-library)
  — the `ngsw` CLI used for switch and PoE control.

`sensors2mqtt`
: [mithro/sensors2mqtt](https://github.com/mithro/sensors2mqtt)

Those repositories are laid out as one flat repository per suite:

```
deb [signed-by=/etc/apt/keyrings/rp1-jtag.gpg] https://mith.ro/rp1-jtag/trixie/ ./
```

Each has its **own** signing key, published at the root of its repository, so
compromising one does not affect the others.
