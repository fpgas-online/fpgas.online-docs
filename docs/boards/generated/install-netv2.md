% This section ("Installing the NeTV2 Packages") is copied from https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/netv2.md
% by tools/sync_repos.py. Do not edit it here: change it in test-designs.

(installing-the-netv2-packages)=

## What you need

- a Raspberry Pi 3, 4 or 5 with the NeTV2 on its GPIO header ([NeTV2 wiring to a Raspberry Pi](wiring.md#jtag))
- the fpgas.online apt repository added on the Pi ([fpgas-verify: installing it, step 1](../../../verify/installing.md#installing))
- on a Raspberry Pi 5 (any release), and on bookworm (any Pi): the fpgas.online-fpga-tools apt repository added too ([fpgas-verify: installing it, step 2](../../../verify/installing.md#installing))

Only that repository's openFPGALoader has the `rp1pio` cable a Raspberry Pi 5 needs. Debian bookworm's openFPGALoader cannot read back an XC7A35T board's flash. `grep VERSION_CODENAME /etc/os-release` says which release the Pi runs.

## Steps

**1.** Install the NeTV2's packages. This also turns the check at boot on (`fpgas-verify.service`).

```bash
sudo apt install fpgas-online-netv2
```

**2.** Check the board. Nothing is sent to the site: `--no-publish` makes sure.

```bash
sudo fpgas-netv2-verify --no-publish
```

## Check

The first line of the output starts with `fpgas-verify: pass`. The board's line (two spaces in, the board's name first) ends in `pass`. So does each test line under it (four spaces in, the test's name first).

## If it fails

- The first line names the result, and the output ends with `RESULT:` and `What to do:`. [fpgas-verify: reading the result](../../../verify/reading-the-result.md#reading-the-result) says what each result means.
- [fpgas-verify: common failures](../../../verify/common-failures.md#common-failures) lists the messages and what to do about each.

## Next

- To run one test with its output live: install `fpgas-online-netv2-debug`, then `sudo fpgas-netv2-debug test uart`.
- [The NeTV2 check at boot](../../../verify/tests.md#the-netv2-check-at-boot): what the check does, test by test.
- [NeTV2 packages](../../../verify/installing.md#netv2-packages): what each package installs.
- [fpgas-verify: reading the result](../../../verify/reading-the-result.md#reading-the-result): the report, `changed` and `--update`.
