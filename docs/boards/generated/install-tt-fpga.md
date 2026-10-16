% This section ("Installing the TT FPGA Packages") is copied from https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/tt-fpga.md
% by tools/sync_repos.py. Do not edit it here: change it in test-designs.

(installing-the-tt-fpga-packages)=

## What you need

- a Raspberry Pi with the Tiny Tapeout demo board on one of its USB ports
- the fpgas.online apt repository added on the Pi ([fpgas-verify: installing it, step 1](../../../verify/installing.md#installing))
- a network that reaches `mith.ro`, where rpi-hwid's apt repository is, and on bookworm `deb.debian.org`

`grep VERSION_CODENAME /etc/os-release` says which release the Pi runs.

## Steps

**1.** Add [rpi-hwid](https://github.com/mithro/rpi-hwid)'s apt repository and install rpi-hwid. Without it the check cannot ask the board which Tiny Tapeout board it is, and its result is `error`.

The step is safe to run again. The `ls` line lists the key, `rpi-hwid.gpg`, about 1.2 kB (1154 bytes). If it is missing or its size is far from that, run the `curl` line again.

```bash
sudo install -d -m0755 /etc/apt/keyrings
sudo curl -fsSL --remove-on-error -o /etc/apt/keyrings/rpi-hwid.gpg https://mith.ro/rpi-hwid/rpi-hwid.gpg
echo "deb [signed-by=/etc/apt/keyrings/rpi-hwid.gpg] https://mith.ro/rpi-hwid/$(. /etc/os-release; echo $VERSION_CODENAME)/ ./" \
  | sudo tee /etc/apt/sources.list.d/rpi-hwid.list
ls -l /etc/apt/keyrings/rpi-hwid.gpg
sudo apt update
sudo apt install python3-rpi-hwid
```

**2.** Add the fpgas.online-fpga-tools repository, on every release, before step 4: only its openFPGALoader has
the `tt_fpga` board, which loads every design into the demo board's FPGA. Without it step 4 stops with an unmet
dependency on `openfpgaloader-fpgasonline`. On 32-bit Raspberry Pi OS (`ID=raspbian`) the suite is
`raspbian-<release>`. This is [fpgas-verify: installing it](../../../verify/installing.md#installing)'s step 2 again: if
you did that, skip this one.

The step is safe to run again. The `ls` line lists the key, `fpgas.online-fpga-tools.gpg`, about 1.2 kB (1174
bytes). If it is missing or its size is far from that, run the `curl` line again.

```bash
sudo install -d -m0755 /etc/apt/keyrings
sudo curl -fsSL --remove-on-error -o /etc/apt/keyrings/fpgas.online-fpga-tools.gpg \
  https://fpgas.online/fpgas.online-fpga-tools/fpgas.online-fpga-tools.gpg
echo "deb [signed-by=/etc/apt/keyrings/fpgas.online-fpga-tools.gpg] https://fpgas.online/fpgas.online-fpga-tools/$(. /etc/os-release; if [ "$ID" = raspbian ]; then echo "raspbian-$VERSION_CODENAME"; else echo "$VERSION_CODENAME"; fi)/ ./" \
  | sudo tee /etc/apt/sources.list.d/fpgas.online-fpga-tools.list
ls -l /etc/apt/keyrings/fpgas.online-fpga-tools.gpg
sudo apt update
```

**3.** On bookworm only, add bookworm-backports and install `mpremote` from it. On trixie step 4 installs it.
Debian's archive key is not on 32-bit Raspberry Pi OS, so the source names it. Its fingerprint is
`B8B8 0B5B 623E AB6A D877 5C45 B7C5 D7D6 3509 47F8`.

The step is safe to run again. The `ls` line lists the key, `debian-archive-key-12.asc`, about 12 kB (11861 bytes).
If it is missing or its size is far from that, run the `curl` line again.

```bash
sudo install -d -m0755 /etc/apt/keyrings
sudo curl -fsSL --remove-on-error -o /etc/apt/keyrings/debian-archive-key-12.asc \
  https://ftp-master.debian.org/keys/archive-key-12.asc
echo "deb [signed-by=/etc/apt/keyrings/debian-archive-key-12.asc] http://deb.debian.org/debian bookworm-backports main" \
  | sudo tee /etc/apt/sources.list.d/bookworm-backports.list
ls -l /etc/apt/keyrings/debian-archive-key-12.asc
sudo apt update
sudo apt install -t bookworm-backports micropython-mpremote
```

**4.** Install the TT FPGA's packages. This also turns the check at boot on (`fpgas-verify.service`). `fpgas-online-tt` is a different package: the TT site's own.

```bash
sudo apt install fpgas-online-tt-fpga
```

**5.** Check the board. Nothing is sent to the site: `--no-publish` makes sure.

```bash
sudo fpgas-tt-fpga-verify --no-publish
```

## Check

The first line of the output starts with `fpgas-verify: pass`. The board's line (two spaces in, the board's name first) ends in `pass`. So does the line of each test that ran (four spaces in, the test's name first). The `flash none: …` line is a note, not a test.

## If it fails

- The first line names the result, and the output ends with `RESULT:` and `What to do:`. [fpgas-verify: reading the result](../../../verify/reading-the-result.md#reading-the-result) says what each result means.
- [fpgas-verify: common failures](../../../verify/common-failures.md#common-failures) lists the messages and what to do about each.

## Next

- To run one test with its output live: install `fpgas-online-tt-fpga-debug`, then `sudo fpgas-tt-fpga-debug test uart`.
- [The TT FPGA check at boot](../../../verify/tt-fpga.md#the-tt-fpga-check-at-boot): what the check does, test by test.
- [TT FPGA packages](../../../verify/installing.md#tt-fpga-packages): what each package installs.
- [fpgas-verify: reading the result](../../../verify/reading-the-result.md#reading-the-result): the report, `changed` and `--update`.
