% This section ("Installing the TT FPGA Packages") is copied from https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/tt-fpga.md
% by tools/sync_repos.py. Do not edit it here: change it in test-designs.

(installing-the-tt-fpga-packages)=

## What you need

- a Raspberry Pi with the Tiny Tapeout demo board on one of its USB ports
- the fpgas.online apt repository added on the Pi ([fpgas-verify: installing it](../../../verify/installing.md#installing))
- a network that reaches `mith.ro`, where rpi-hwid's apt repository is, and on bookworm `deb.debian.org`

`grep VERSION_CODENAME /etc/os-release` says which release the Pi runs.

## Steps

**1.** Add [rpi-hwid](https://github.com/mithro/rpi-hwid)'s apt repository and install rpi-hwid. Without it the check cannot ask the board which Tiny Tapeout board it is, and its result is `error`.

```bash
sudo install -d -m0755 /etc/apt/keyrings
curl -fsSL https://mith.ro/rpi-hwid/rpi-hwid.gpg | sudo tee /etc/apt/keyrings/rpi-hwid.gpg > /dev/null
echo "deb [signed-by=/etc/apt/keyrings/rpi-hwid.gpg] https://mith.ro/rpi-hwid/$(. /etc/os-release; echo $VERSION_CODENAME)/ ./" \
  | sudo tee /etc/apt/sources.list.d/rpi-hwid.list
sudo apt update
sudo apt install python3-rpi-hwid
```

**2.** On bookworm only, add bookworm-backports and install `mpremote` from it. On trixie the next step installs it.

```bash
echo "deb http://deb.debian.org/debian bookworm-backports main" | sudo tee /etc/apt/sources.list.d/bookworm-backports.list
sudo apt update
sudo apt install -t bookworm-backports micropython-mpremote
```

**3.** Install the TT FPGA's packages. This also turns the check at boot on (`fpgas-verify.service`). `fpgas-online-tt` is a different package: the TT site's own.

```bash
sudo apt install fpgas-online-tt-fpga
```

**4.** Check the board now. Nothing is sent to the site: `--no-publish` makes sure.

```bash
sudo fpgas-tt-fpga-verify --no-publish
```

## Check

The first line of the output starts with `fpgas-verify: pass`. The board's line under it ends in `pass`, and so does the line of each test.

## If it fails

- The first line names the result, and the output ends with `RESULT:` and `What to do:`. [fpgas-verify: reading the result](../../../verify/reading-the-result.md#reading-the-result) says what each result means.
- [fpgas-verify: common failures](../../../verify/common-failures.md#common-failures) lists the messages and what to do about each.
- To run one test with its output live, install `fpgas-online-tt-fpga-debug` and run it:

```bash
sudo fpgas-tt-fpga-debug test uart
```

## Next

- [The TT FPGA check at boot](../../../verify/tt-fpga.md#the-tt-fpga-check-at-boot): what the check does, test by test.
- [TT FPGA packages](../../../verify/installing.md#tt-fpga-packages): what each package installs.
- [fpgas-verify: reading the result](../../../verify/reading-the-result.md#reading-the-result): the report, `changed` and `--update`.
