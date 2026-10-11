% This section ("Installing the Fomu Packages") is copied from https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/fomu-evt.md
% by tools/sync_repos.py. Do not edit it here: change it in test-designs.

(installing-the-fomu-packages)=

## What you need

- a Raspberry Pi with the Fomu EVT on its GPIO header ([Fomu EVT wiring to a Raspberry Pi](wiring.md#connections-to-the-pi))
- the fpgas.online apt repository added on the Pi ([fpgas-verify: installing it, step 1](../../../verify/installing.md#installing))
- on bookworm: the fpgas.online-fpga-tools apt repository added too ([fpgas-verify: installing it, step 2](../../../verify/installing.md#installing)). Debian bookworm's openFPGALoader is too old for the check

`grep VERSION_CODENAME /etc/os-release` says which release the Pi runs.

## Steps

**1.** Install the Fomu's packages. This also turns the check at boot on (`fpgas-verify.service`).

```bash
sudo apt install fpgas-online-fomu
```

**2.** Check the board. Nothing is sent to the site: `--no-publish` makes sure.

```bash
sudo fpgas-fomu-verify --no-publish
```

## Check

The first line of the output starts with `fpgas-verify: pass`. The board's line (two spaces in, the board's name first) ends in `pass`. So does the line of each test that ran (four spaces in, the test's name first). The `flash not read back: …` line is a note, not a test.

## If it fails

- The first line names the result, and the output ends with `RESULT:` and `What to do:`. [fpgas-verify: reading the result](../../../verify/reading-the-result.md#reading-the-result) says what each result means.
- [fpgas-verify: common failures](../../../verify/common-failures.md#common-failures) lists the messages and what to do about each.

## Next

- To run one test with its output live: install `fpgas-online-fomu-debug`, then `sudo fpgas-fomu-debug test spiflash`. Then `sudo fpgas-fomu-debug reset`, which puts foboot back on USB.
- [The Fomu EVT check at boot](../../../verify/tests.md#the-fomu-evt-check-at-boot): what the check does, test by test.
- [Fomu EVT packages](../../../verify/installing.md#fomu-evt-packages): what each package installs.
- [fpgas-verify: reading the result](../../../verify/reading-the-result.md#reading-the-result): the report, `changed` and `--update`.
