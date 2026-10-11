% This section ("Installing the Arty Packages") is copied from https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/arty-a7.md
% by tools/sync_repos.py. Do not edit it here: change it in test-designs.

(installing-the-arty-packages)=

## What you need

- a Raspberry Pi with the Arty on one of its USB ports
- the fpgas.online apt repository added on the Pi ([fpgas-verify: installing it, step 1](../../../verify/installing.md#installing))
- on bookworm: the fpgas.online-fpga-tools apt repository added too ([fpgas-verify: installing it, step 2](../../../verify/installing.md#installing)). Debian bookworm's openFPGALoader is too old for the check

`grep VERSION_CODENAME /etc/os-release` says which release the Pi runs.

## Steps

**1.** Install the Arty's packages. This also turns the check at boot on (`fpgas-verify.service`).

```bash
sudo apt install fpgas-online-arty
```

**2.** Check the board now. Nothing is sent to the site: `--no-publish` makes sure.

```bash
sudo fpgas-arty-verify --no-publish
```

## Check

The first line of the output starts with `fpgas-verify: pass`. The board's line under it ends in `pass`, and so does the line of each test.

## If it fails

- The first line names the result, and the output ends with `RESULT:` and `What to do:`. [fpgas-verify: reading the result](../../../verify/reading-the-result.md#reading-the-result) says what each result means.
- [fpgas-verify: common failures](../../../verify/common-failures.md#common-failures) lists the messages and what to do about each.
- To run one test with its output live, install `fpgas-online-arty-debug` and run it:

```bash
sudo fpgas-arty-debug test ddr
```

## Next

- [The Arty A7 check at boot](../../../verify/tests.md#the-arty-a7-check-at-boot): what the check does, test by test.
- [Arty A7 packages](../../../verify/installing.md#arty-a7-packages): what each package installs.
- [fpgas-verify: reading the result](../../../verify/reading-the-result.md#reading-the-result): the report, `changed` and `--update`.
