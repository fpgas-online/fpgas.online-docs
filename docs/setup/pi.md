# What runs on a Pi host

Every Pi in the fleet boots the same read-only NFS root over the network
([Netboot and the NFS root](netboot.md)), so nothing on a Pi is installed at
boot time. The root is built once on the server, in two phases: `fixpi` shapes
the extracted tree in place — the boot files, the `pi` account, the
hostname-to-`/etc/hosts` unit, the `timesyncd` drop-in and the `ifupdown` masks
— and then `fpgas-apt`, `cam/pi` and `onpi` run against that same tree through
a chroot reached over SSH; see
[The provisioning container](netboot.md#the-provisioning-container). A running
Pi only adds a tmpfs upper layer over the result, which is discarded on the next
power cycle.

This page is the inventory of what that converge leaves behind — the packages,
the systemd units, and the `config.txt` and `cmdline.txt` settings the firmware
reads on the way up. Per-model quirks and per-board wiring live on the site and
board pages and are linked rather than repeated.

## Packages

The `fpgas-apt` role adds the fpgas.online APT repository
(`https://fpgas.online/apt bookworm main`, keyring dearmoured into
`/usr/share/keyrings/fpgas-online.gpg`) before anything else runs. How that
repository is built and what else it serves is on [Packages](../packages.md).

From it:

| Package | Installed by | Purpose |
| --- | --- | --- |
| `fpgas-online-setup-pi` | `onpi/tasks/main.yml` | The pistat and Arty units, the USB gadget console, the FEL-boot host, the `.link` interface names, the `/etc/profile.d` banner scripts, the zsh/tmux skeleton and the sshd drop-in. |
| `fpgas-online-tt` | `onpi/tasks/tt.yml` | The `fpgas-tt` daemon: it owns `/dev/ttboard` and fans it out as a WebSocket on port 8765. See [The Tiny Tapeout stack](tinytapeout.md). |
| `fpgas-online-tt-demos` | `onpi/tasks/tt.yml` | The demo bitstream set under `/usr/share/fpgas-tt/demos` (`index.json` plus one `.bin` per design), which the daemon syncs onto an `fpga` board. |
| `fpgas-online-cam` | `cam/pi` role | `/usr/local/bin/fpgas-gst-libcam.sh` and `fpgas-cam.service`. See [Camera](#camera). |

`fpgas-online-setup-pi` also drags in four packages that `apt.yml` never names,
through `depends:` in its `nfpm.yaml`: `sunxi-tools` for `sunxi-fel`, `expect`
for the Arty detection script, `zsh` for the shell it ships a skeleton for, and
`python3`. `expect` in particular has no other route onto a Pi — the only
explicit `apt install` of it is in the orphaned `arty_here.yml` task file. The
other two `depends:` entries, `tmux` and `vim`, are installed by `apt.yml`
itself and appear in the Debian table below.

Both Tiny Tapeout packages are installed with `state: latest`, deliberately —
they are rolling releases, so re-running the Pi play picks up a newer daemon
and demo set. Their install is gated on
`tt_install | default(tt_boards is defined)`, so a site with TT boards gets them
automatically and a build with none — the CI nfsroot build — can force them in
by setting `tt_install: true`. That is the point of the split: the daemon and
demos are generic fleet content, and a Pi with no `/dev/ttboard` simply waits
for one. The *site catalogue* (`/etc/fpgas-online/tt-boards.yaml`) and the
*enablement* of `fpgas-tt.service` are gated on `tt_boards` alone, because a
service enabled without its catalogue would change behaviour on a non-TT site.

From Debian, by `onpi/tasks/apt.yml`:

| Package | Why it is there |
| --- | --- |
| `overlayroot` | Provides the tmpfs upper layer that makes the read-only NFS root writable at runtime (`overlayroot=tmpfs` on the kernel command line). |
| `lldpd` | Advertises this Pi's hostname on its link, so the switch's LLDP neighbour table names which Pi is on which port — that confirms the assumed cabling instead of trusting it. A running Pi only picks this up after a reboot, because the NFS root is a read-only lower layer. |
| `atftpd`, `atftp` | A TFTP server and client on the Pi itself. `onpi/tasks/tftpd.yml` then rewrites the port in both `atftpd.socket` and `/etc/default/atftpd` from 69 to `tftpd_port` (6069 in the inventory) and makes `/srv/tftp` writable by the `pi` user. |
| `openfpgaloader` | Bitstream loading. This is Debian's 0.10.0 build — see the note below. |
| `openocd` | JTAG for the boards openFPGALoader does not drive, notably the Pi 3 NeTV2 path. |
| `fxload`, `openwince-jtag` | Older USB firmware-loading and JTAG tooling. |
| `uhubctl` | Per-port USB power control. |
| `tio`, `minicom`, `picocom`, `screen` | Serial terminals. |
| `tmux`, `vim`, `git`, `tree`, `ack`, `rsync`, `sshfs` | Interactive shell environment for someone SSHed into a node. |
| `nmap`, `tcpdump` | Network diagnosis from inside a per-port VLAN. |
| `ssh-import-id` | Used by `onpi/tasks/sshkeys.yml` to pull the operators' public keys for the `pi` account from the `ssh_imports` inventory list. |
| `software-properties-common` | `add-apt-repository` and friends. |
| `python3-full`, `python3-venv`, `python3-pip`, `python3-dev`, `pipx` | The Python toolchain the test scripts run on. |
| `python3-serial`, `python3-rpi.gpio`, `python3-numpy`, `python3-tqdm` | The libraries those scripts import: serial ports, GPIO, arrays, progress bars. |
| `build-essential`, `dkms`, `libfreetype6-dev`, `libjpeg-dev` | Compiler and headers, so a `pip install` of something with a C extension works on the node. |

Two of those tasks are corrections rather than installs. `vim-tiny` is removed
explicitly, because `dpkg-divert` refuses to rename
`/usr/share/vim/vim82/doc/help.txt.vim-tiny` over the full `vim`'s copy. And
`mpremote` and `uv` are installed through `pipx` with `PIPX_HOME=/opt/pipx` and
`PIPX_BIN_DIR=/usr/local/bin` pinned in the environment: a bare `pipx install`
puts the venv wherever the invoking environment points it and the binaries on
no user's `PATH`, which made the chroot-built and CI-built roots disagree.

:::{note}
`apt.yml` on `main` installs Debian's `openfpgaloader` (0.10.0), not the
`openfpgaloader-rp1pio` build from
[mithro/rp1-jtag](https://github.com/mithro/rp1-jtag) that
[Packages](../packages.md) describes. Swapping the default in the NFS root is
[fpgas.online-infra PR #48](https://github.com/fpgas-online/fpgas.online-infra/pull/48),
still open. Until it lands, the NFS root has no `rp1pio` cable and no
`--read-dna`, which is why the [Acorn wiring page](../boards/acorn/wiring.md)
carries workarounds for 0.10.0 — the `/dev/gpiochip15` symlink over
`/dev/gpiochip0`, and a hand-rolled `ISC_ENABLE` + `ISC_DNA` OpenOCD sequence
standing in for `--read-dna`.
:::

:::{todo}
Two package-and-firmware decisions are still open in `fpgas.online-infra`. The
`openfpgaloader-rp1pio` swap is only on PR #48, so the roots keep shipping
Debian's 0.10.0 until it lands or is closed. And `core_freq=500` is not set
anywhere: `TECHDEBT.md` records the PoE-versus-camera trade-off undecided — see
[`core_freq` under boot-time configuration](#boot-time-configuration) — so
whichever way it goes, one of the two failure modes stays possible.
:::

The `cam/pi` role adds the streaming stack on top: `gstreamer1.0-tools`, the
`base`, `good`, `bad`, `ugly`, `base-apps` and `libcamera` plugin sets,
`rpicam-apps-lite`, `jq` (the publisher script reads the default route out of
`ip -json route`) and `lm-sensors`.

## Services

One row per unit that ends up in the shared root. "Enabled by `onpi`?" means
the current include chain in `onpi/tasks/main.yml`, which is `apt.yml`,
`nonfs.yml`, `tt.yml`, `tftpd.yml`, `sshkeys.yml`, `tweeks.yml` — and nothing
else.

| Unit | Installed by | Purpose | Enabled by `onpi`? |
| --- | --- | --- | --- |
| `fpgas-tt.service` | `fpgas-online-tt` | Runs `fpgas-tt --device /dev/ttboard --boards /etc/fpgas-online/tt-boards.yaml` as the `pi` user with the `dialout` group, restarting always. | Yes, by `tt.yml`, but only when the site defines `tt_boards`. |
| `fpgas-cam.service` | `fpgas-online-cam` | Runs `/usr/local/bin/fpgas-gst-libcam.sh`, restarting always, after `network-online.target`. | No — the `cam/pi` role enables it, not `onpi`. |
| `fpgas-usb-console.service` | `fpgas-online-setup-pi` | `dmesg --follow` onto `/dev/ttyGS0`, so a laptop on the USB-C port gets the kernel log replayed from the start of boot. | Not enabled; `70-fpgas-usb-console.rules` starts it when `ttyGS0` appears. |
| `serial-getty@ttyGS1.service` | systemd (pulled in by the usb-console udev rule) | The login console on the second gadget port. Separate from `ttyGS0` because `agetty` flushes its tty on start, which would drop queued log data. | Not enabled; udev-started. |
| `fpgas-usb-console-log@.service` | `fpgas-online-setup-pi` | Host side only: captures an attached board's log port to `/var/log/fpgas-usb-console/`, from the first byte, because the board's ring buffer wraps within minutes under debug logging. | Not enabled; `71-fpgas-usb-console-host.rules` starts one instance per matching `ttyACM*`. |
| `fpgas-felboot@.service` | `fpgas-online-setup-pi` | Host side only: runs `sunxi-fel uboot` against an Allwinner board that enumerated in BROM FEL mode on this Pi's USB, so a PoE-cycled Orange Pi netboots without an operator. | Not enabled; `60-fpgas-felboot.rules` starts it on `1f3a:efe8`. |
| `lldpd.service` | Debian `lldpd` | The LLDP advertisement described above. | Package default. |
| `atftpd.socket`, `atftpd.service` | Debian `atftpd` | TFTP on the Pi. `tftpd.yml` rewrites `ListenDatagram=` and `--port` to `tftpd_port`. | Package default; `onpi` only changes the port. |
| `ssh.service` | Debian `openssh-server` | Remote access. `fpgas-online-setup-pi` adds an `/etc/ssh/sshd_config.d/` drop-in. | Image default. |
| `fpgas-hostname-hosts.service` | `fixpi` role | Appends the DHCP-assigned hostname to `/etc/hosts` on boot, so `sudo`'s per-invocation `getaddrinfo()` of the machine name is instant instead of stalling on DNS. | Not `onpi` — `fixpi` enables it by planting the `multi-user.target.wants` symlink directly in the root. |
| `systemd-timesyncd.service` | Debian systemd | NTP, with a `fixpi`-written drop-in pointing it at the gateway. The drop-in is needed because "Pis have no internet and timesyncd does not reliably consume the DHCP ntp-server option under dhcpcd", so without it every Pi's clock sits on the fake-hwclock date. | Image default; `onpi` does not touch it. |
| `fpgas-pistat-ssh.service` | `fpgas-online-setup-pi` | One-shot `curl` to `https://${pistat_host}/pistat/stat/%l/ssh/`, bound to `ssh.service`. | Shipped in the deb, not enabled by any included task. |
| `fpgas-pistat-cam.service` | `fpgas-online-setup-pi` | The same for `/cam/`, but ordered after `cam.target` and bound to `cam.service` — neither exists, the camera unit having been renamed `fpgas-cam.service`. | Shipped in the deb, not enabled by any included task. |
| `fpgas-pistat-info.service` | `fpgas-online-setup-pi` | Reports the device-tree model string, so the server knows which Pi model answered on that port. | Shipped in the deb, not enabled by any included task. |
| `fpgas-pistat-shutdown.service` | `fpgas-online-setup-pi` | `RemainAfterExit` unit whose `ExecStop` reports `/shutdown/` on the way down. | Shipped in the deb, not enabled by any included task. |
| `fpgas-arty-here.service` | `fpgas-online-setup-pi` | Meant to report whether an Arty is attached, but its `ExecStart` is `/usr/local/bin/arty_here.sh` and the deb installs the script as `fpgas-arty-here.sh` — which in turn calls `/usr/local/bin/arty_here.exp`, installed as `fpgas-arty-here.exp`. | Shipped in the deb, not enabled by any included task — and would not run if it were. |
| `fpgas-arty-wire.service` | `fpgas-online-setup-pi` | Meant to check the Pi-to-Arty wiring. `ExecStart` is `/usr/local/bin/arty_wire.sh` against an installed `fpgas-arty-wire.sh`, and it orders `After=arty_here.target`, a target that does not exist. | Shipped in the deb, not enabled by any included task — and would not run if it were. |
| `fpgas-arty-blink.service` | `fpgas-online-setup-pi` | Meant to run the Arty counter demo from `/home/pi/Demos/counter_test`. `ExecStart` is `/usr/local/bin/arty_blink.sh` against an installed `fpgas-arty-blink.sh`, and it orders `After=arty_wire.target`, also nonexistent. | Shipped in the deb, not enabled by any included task — and would not run if it were. |

:::{todo}
The `fpgas-pistat-*` and `fpgas-arty-*` families are shipped in
`fpgas-online-setup-pi` but enabled by nothing. The role files that used to
enable them — `onpi/tasks/pistat.yml`, `arty_here.yml`, `arty_wire.yml`,
`arty_blink.yml` — still exist in the infra repo, still copy or template the
units under their **old** names (`pistat_ssh.service`, `arty_here.service`)
into `/etc/systemd/system/`, and are not in `onpi/tasks/main.yml`'s include
list. So status reporting for the per-port fleet may not be wired up at all on
the current roots: nothing reports SSH-ready, camera-ready, model or shutdown,
and no Arty presence check runs.

Enabling them is not a one-line fix for the Arty three. Their unit bodies were
never updated when the package took over installation, so all three would fail
with **203/EXEC**: each `ExecStart` names the pre-package script path
(`/usr/local/bin/arty_here.sh`) while `nfpm.yaml` installs `fpgas-arty-here.sh`,
and there is no postinstall script or compatibility symlink in the deb to
bridge the two. `arty_here.sh` has the same problem one level down — it calls
`/usr/local/bin/arty_here.exp`, installed as `fpgas-arty-here.exp`. On top of
that, `arty_wire` and `arty_blink` order themselves after `arty_here.target`
and `arty_wire.target`, targets that do not exist anywhere in the package. The
unit bodies need the `fpgas-` names and those two `After=` targets removed
before enabling them would achieve anything.

The four pistat units do **not** share the path problem: their `ExecStart`
lines invoke `/usr/bin/curl` (and `/usr/bin/bash` in the `info` case) directly,
so enabling them is sufficient. `fpgas-pistat-cam.service` would still be inert,
because it is bound to `cam.service`, which was renamed `fpgas-cam.service`.

Decide whether the pistat path is still wanted; if it is, fix the unit bodies
in `fpgas.online-setup-pi`, add an include that enables the `fpgas-`-prefixed
units, and delete the four orphaned task files either way.
:::

Two smaller oddities in the same package. The `pistat-scripts/` Python files
are installed onto the Pi as `/usr/local/bin/fpgas-pistat-*.py`, but they are
server-side code: `send.py` imports `channels.layers`, `send_stat.py` is a
dnsmasq `--dhcp-script` and both it and `send_ncc.py` carry the shebang
`#!/srv/www/pib/venv/bin/python3`, a path that does not exist on a Pi. And the
`.link` files that name the two Ethernet interfaces `eth-uplink` and
`eth-fpga` come from this package too — they are covered under
[interface naming](network.md#interface-naming-on-the-pi).

## Boot-time configuration

The firmware reads `config.txt` and `cmdline.txt` from the TFTP root, which is
served read-only. That is what makes these settings hold: they are re-applied
on every boot, so a user with root can change the running kernel's behaviour
for the life of a session but never across a reboot. The `fixpi` role's
`tasks/tweeks.yml` appends the following to the served `config.txt`:

```text
dtoverlay=disable-wifi
dtoverlay=disable-bt
enable_uart=1
uart_2ndstage=1
eeprom_write_protect=1

# BEGIN ANSIBLE MANAGED BLOCK: pi5 header uart
[pi5]
dtoverlay=uart0-pi5
cmdline=cmdline-pi5.txt
[all]
# END ANSIBLE MANAGED BLOCK: pi5 header uart

# BEGIN ANSIBLE MANAGED BLOCK: usb gadget console
[pi4]
dtoverlay=dwc2,dr_mode=peripheral
[pi5]
dtoverlay=dwc2,dr_mode=peripheral
[all]
# END ANSIBLE MANAGED BLOCK: usb gadget console
```

`eeprom_write_protect=1`
: The bootloader EEPROM is the one piece of per-board state a netbooted Pi does
  *not* revert on reboot, so it is the only place a root user could leave a
  persistent change. How effective the lock is differs by model, and updating
  an EEPROM legitimately has its own procedure — both are on
  [EEPROM write protect](netboot.md#eeprom-write-protect).

`dtoverlay=disable-wifi`, `dtoverlay=disable-bt`
: The onboard radios off, on both Pi 4 and Pi 5 — the per-generation overlay
  remapping is under
  [How the root is built](netboot.md#how-the-root-is-built).

`dtoverlay=uart0-pi5` and the `[pi5]` console
: `disable-bt` frees the 40-pin header UART as a side effect on Pi 0–4 only —
  the Pi 5 variant of the overlay touches the `bluetooth` node and nothing
  else, and `bcm2712-rpi-5-b.dtb` ships the RP1 header UART disabled. So Pi 5
  hosts need `uart0-pi5` explicitly. Enabling it, though, makes the firmware
  resolve `console=serial0` to `ttyAMA0` and put the kernel console straight
  onto the FPGA's UART, where a design driving TX feeds the console garbage the
  kernel reads as SysRq. That is what `cmdline=cmdline-pi5.txt` is for: it
  swaps in a command line with `console=ttyAMA10,115200`, the dedicated debug
  UART, leaving `ttyAMA0` unclaimed. The rest of both command lines is on
  [the kernel command line](netboot.md#the-kernel-command-line); PS1 hit the
  SysRq failure for real, recorded under [Two traps](../sites/ps1.md#two-traps).

`dtoverlay=dwc2,dr_mode=peripheral`
: Pi 4 and Pi 5 only. Their USB-C port is a dwc2 OTG controller the firmware
  otherwise leaves in host mode; in peripheral mode it becomes the gadget
  console described under [Serial consoles](#serial-consoles). It is safe on
  exactly these two models because their USB-A ports hang off separate
  controllers, whereas on a Pi 3 or Zero dwc2 *is* the only USB there is.
  Orange Pi H3 boards need nothing here — musb autoloads.

`core_freq`
: Not set. `config.txt.j2` carries it commented out as `# core_freq=250`, and
  the infra technical-debt notes record why the value is contested: dropping
  the core clock to 250 was an attempt at the intermittent (roughly 1 in 50)
  stuck-boot problem, on the theory that PoE power was marginal, and it may
  have helped a little. But one Pi with a camera fails with a camera error at
  250 or anything below 500, and `core_freq=500` fixed that. The note ends
  undecided: 500 might bring the PoE boot problem back, or the PoE problem
  might never have been real.

`tweeks.yml` also edits the root itself, mostly to stop units failing where
nobody can see them. `console-setup.service` and `profile.d/wifi-check.sh` are
deleted (a failed console-setup, and a "Wi-Fi is blocked by rfkill" warning on
every login); `/etc/hostname` is deleted so the DHCP-supplied name wins; and
`networking.service` and `ifupdown-pre.service` are masked to `/dev/null`,
because `ifupdown` is unused under `ip=dhcp` plus NetworkManager and
`ifupdown-pre` sat through its full two-minute `udevadm settle` on an Orange Pi
before anything else could start. It also writes `pistat_host` into
`/etc/environment`, which is where every pistat and Arty unit reads the server
name from. The `fpgas-hostname-hosts.service` unit and the `timesyncd` drop-in
that pins the Pi's clock at the gateway are `fixpi`'s too, from `netboot.yml`,
and are described under
[How the root is built](netboot.md#how-the-root-is-built).

## Model differences

The fleet runs several Pi models off one root, and the differences that bite
are documented where they were found:

- **Raspberry Pi 5** — header GPIOs on `gpiochip15` not `gpiochip0`,
  `disable-bt` a no-op, `ttyAMA0` versus `ttyAMA10`:
  [Raspberry Pi 5 specifics](../sites/welland.md#raspberry-pi-5-specifics).
- **CM4 versus CM5** — not drop-in replacements for each other:
  [CM4 and CM5 are not interchangeable](../sites/ps1.md#cm4-and-cm5-are-not-interchangeable).
- **Raspberry Pi 3** — the mini UART on the header and what `disable-bt`
  actually does there, per host:
  [Serial device by host](../boards/netv2.md#serial-device-by-host).
- **Raspberry Pi 3B+ USB topology** — why the gadget console is Pi 4 and Pi 5
  only, and what a 3B+ would lose:
  [When a Pi does not boot](netboot.md#when-a-pi-does-not-boot).

## Camera

`fpgas-cam.service` runs `/usr/local/bin/fpgas-gst-libcam.sh` on every host
that has a camera, restarting always. The script builds one GStreamer pipeline:
`libcamerasrc` at 6 fps, a `clockoverlay`, then H.264 — `v4l2h264enc` where the
hardware encoder exists, `x264enc` where it does not, which on the Pi 5 means
software. It publishes to `rtmp://<default gateway>/pib/<short hostname>`,
finding the gateway from `ip -json route show default` rather than from a
configured variable.

The gateway's `cam/stream-server` role runs nginx-rtmp, which repackages the
stream as HLS under `/live`, served with `Cache-Control: no-cache` because a
cached live playlist is stale by definition. The board pages embed that
playlist, and each one also offers the direct URL for a desktop player:

```console
$ vlc https://<site>/live/pi<N>.m3u8
```

Latency is a deliberate trade. nginx-rtmp can only cut an HLS fragment at a
keyframe, so the GOP length is the floor on fragment length, and the player
starts three fragments behind the newest. A 60-frame GOP at 6 fps meant 10-second
fragments and about 40 seconds glass-to-glass, measured 2026-08-30; one keyframe
per second plus a 900 ms server fragment brings that to roughly 5 seconds.

Which hosts have cameras is a site fact, not a platform one. At Welland the
Arty, Fomu and Tiny Tapeout hosts all carry an ov5647 and publish a feed — see
the per-board tables on the [Welland page](../sites/welland.md#hosts-and-boards).
At PS1 the Arty hosts are the ones with cameras and no compute blade has one
([PS1 hosts and boards](../sites/ps1.md#hosts-and-boards)).

## Serial consoles

A Pi host can have up to three separate serial paths, and the recurring problem
is that more than one thing wants the same one.

**The board's own USB serial.** On a Tiny Tapeout host, the demo board's
RP2040/RP2350 CDC port gets a stable `/dev/ttboard` symlink from a udev rule in
`fpgas-online-tt`, matching `2e8a:0005` and `2e8a:000f` with `GROUP="dialout"`.
`fpgas-tt` holds that port open permanently and fans it out over WebSocket, so
`mpremote` and the programming scripts cannot open it while the daemon runs —
the full consequences are under
[Serial port ownership](../boards/tt-fpga.md#serial-port-ownership).

**The 40-pin header UART.** When the FPGA is going to drive this, the login
console has to be out of the way first, and `stop` alone is not enough because
systemd restarts it — it has to be masked. Which unit to mask depends on the
model, so resolve the device rather than hardcoding `ttyAMA0`:

```console
# Stop early if there is no GPIO UART here -- otherwise the lookup below
# resolves to nothing and the mask silently targets the wrong unit.
$ [ -e /dev/serial0 ] || { echo "no GPIO UART on this host"; exit 1; }
$ GETTY="serial-getty@$(basename "$(readlink -f /dev/serial0)").service"
$ sudo systemctl mask "$GETTY"
$ sudo systemctl stop "$GETTY"
```

The same form is spelled out with its permission and `fuser` follow-up under
[the Fomu UART interface](../boards/fomu-evt.md#uart-interface).
Two related pre-test steps come from the same place: `rmmod spidev spi_bcm2835`
frees GPIO 7–11 for a PMOD loopback, since the SPI kernel modules claim them;
and on a Pi 5 only, `pinctrl set 14 a4; pinctrl set 15 a4` puts GPIO14/15 back
into their UART alternate function after `serial-getty` releases them and they
revert to plain GPIO. A Pi 3 does not need that — its mini UART pins do not
change function.

Masking a getty does not survive a reboot: the root is read-only and the mask
lives in the tmpfs layer. Anything that power-cycles a host — a PoE reset
during a Fomu DFU recovery, for instance — has to re-run the pre-test.

**The USB-C gadget console.** On a Pi 4 or Pi 5 with the peripheral-mode
overlay above, a laptop plugged into the USB-C port sees two CDC-ACM ports:
`ttyGS0` carrying the kernel log from the start of boot, and `ttyGS1` a login
getty. Nothing waits for a host — the gadget enumerates only when one is
plugged in, and boot proceeds identically either way; a board with no USB
device controller never even loads the gadget stack. It is one of four ways the
roles provide to watch a boot, listed under
[When a Pi does not boot](netboot.md#when-a-pi-does-not-boot).

:::{warning}
A design that drives the serial TX line while the kernel console is on the same
UART is not merely noisy: at PS1 a 1200-baud FPGA transmitting into a
115200-baud console produced garbage the kernel parsed as SysRq commands and
eventually hit `reboot`. See [Two traps](../sites/ps1.md#two-traps) for how that
was fixed there, and the `[pi5]` console pinning above for how it is avoided on
the Pi 5 hosts.
:::

## Sources

fpgas.online-infra, `main`:

- [`ansible/site.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/site.yml)
  — the `pi` play: `fpgas-apt`, then `cam/pi`, then `onpi`, run against the
  `piroot` chroot the `nspawn-pi` role sets up on the NFS root.
- [`ansible/roles/onpi/tasks/main.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/onpi/tasks/main.yml)
  — the include list (`apt.yml`, `nonfs.yml`, `tt.yml`, `tftpd.yml`,
  `sshkeys.yml`, `tweeks.yml`) and the `fpgas-online-setup-pi` install; the
  absence of `pistat.yml`, `arty_here.yml`, `arty_wire.yml`, `arty_blink.yml`
  and `tmux.yml` from it.
- [`ansible/roles/onpi/tasks/apt.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/onpi/tasks/apt.yml)
  — the Debian package list, the `lldpd` rationale, the `vim-tiny` removal, and
  the pinned `pipx` locations for `mpremote` and `uv`.
- [`ansible/roles/onpi/tasks/tt.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/onpi/tasks/tt.yml)
  — `fpgas-online-tt` and `fpgas-online-tt-demos` at `state: latest` for every
  Pi, and `tt-boards.yaml` plus the `fpgas-tt.service` enable gated on
  `tt_boards`.
- [`ansible/roles/onpi/tasks/tftpd.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/onpi/tasks/tftpd.yml)
  and [`sshkeys.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/onpi/tasks/sshkeys.yml),
  [`nonfs.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/onpi/tasks/nonfs.yml),
  [`tweeks.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/onpi/tasks/tweeks.yml)
  — the atftpd port rewrite and `/srv/tftp` ownership, `ssh-import-id` driven
  by `ssh_imports`, the `nfsvers=4.2` safety net, and the `pi` home directories.
- [`ansible/roles/onpi/tasks/pistat.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/onpi/tasks/pistat.yml),
  [`arty_here.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/onpi/tasks/arty_here.yml),
  [`arty_wire.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/onpi/tasks/arty_wire.yml)
  and [`arty_blink.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/onpi/tasks/arty_blink.yml)
  — the orphaned enablement tasks, still using the pre-package unit names.
- [`ansible/roles/fixpi/tasks/tweeks.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/fixpi/tasks/tweeks.yml)
  — every `config.txt` line quoted above and the reasoning behind each, plus
  the `pistat_host` entry in `/etc/environment`, the deleted
  `console-setup.service`, `wifi-check.sh` and `/etc/hostname`, and the masked
  `networking.service` and `ifupdown-pre.service`.
- [`ansible/roles/fixpi/tasks/netboot.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/fixpi/tasks/netboot.yml)
  — `fpgas-hostname-hosts.service` and its `multi-user.target.wants` symlink,
  and the `timesyncd.conf.d/fpgas.conf` drop-in pointing at the gateway.
- [`ansible/roles/fixpi/files/fpgas-hostname-hosts.service`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/fixpi/files/fpgas-hostname-hosts.service)
  and [`fpgas-hostname-hosts.sh`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/fixpi/files/fpgas-hostname-hosts.sh)
  — the `sudo`/DNS stall this exists to prevent, and why the logic is in a
  script rather than in `ExecStart`.
- [`ansible/roles/fixpi/templates/boot/config.txt.j2`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/fixpi/templates/boot/config.txt.j2)
  — the base file, with `core_freq` commented out.
- [`ansible/roles/fixpi/templates/boot/cmdline.txt.j2`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/fixpi/templates/boot/cmdline.txt.j2)
  and [`cmdline-pi5.txt.j2`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/fixpi/templates/boot/cmdline-pi5.txt.j2)
  — `console=serial0,115200` versus `console=ttyAMA10,115200`.
- [`ansible/roles/cam/pi/tasks/main.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/cam/pi/tasks/main.yml)
  — the GStreamer package set and the `fpgas-cam.service` enable.
- [`ansible/roles/cam/stream-server/templates/live-hls.conf.j2`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/cam/stream-server/templates/live-hls.conf.j2)
  and [`nginx-rtmp.conf.j2`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/cam/stream-server/templates/nginx-rtmp.conf.j2)
  — the `/live` HLS location and its `no-cache` header.
- [`ansible/roles/fpgas-apt/tasks/main.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/fpgas-apt/tasks/main.yml)
  and [`defaults/main.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/fpgas-apt/defaults/main.yml)
  — the repository URL, suite and dearmoured keyring.
- [`ansible/inventory/group_vars/all/ci.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/inventory/group_vars/all/ci.yml)
  — `tftpd_port: 6069`.
- [`TECHDEBT.md`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/TECHDEBT.md)
  — items 2 and 3, the `core_freq` PoE-versus-camera trade.

[fpgas.online-setup-pi](https://github.com/fpgas-online/fpgas.online-setup-pi), `main`:

- [`nfpm.yaml`](https://github.com/fpgas-online/fpgas.online-setup-pi/blob/main/nfpm.yaml)
  — the authoritative list of what the deb installs and where, including the
  `fpgas-`-prefixed script and unit names and the `pistat-scripts` destinations;
  the `depends:` list (`sunxi-tools`, `zsh`, `tmux`, `vim`, `expect`,
  `python3`), which is the only route by which `expect` reaches a Pi; and the
  absence of any `scripts:` block, so there is no postinstall to symlink the
  old script names.
- [`README.md`](https://github.com/fpgas-online/fpgas.online-setup-pi/blob/main/README.md)
  — the summary of what the package provides and the directory layout.
- [`usb-console/70-fpgas-usb-console.rules`](https://github.com/fpgas-online/fpgas.online-setup-pi/blob/main/usb-console/70-fpgas-usb-console.rules),
  [`71-fpgas-usb-console-host.rules`](https://github.com/fpgas-online/fpgas.online-setup-pi/blob/main/usb-console/71-fpgas-usb-console-host.rules),
  [`fpgas-usb-console.service`](https://github.com/fpgas-online/fpgas.online-setup-pi/blob/main/usb-console/fpgas-usb-console.service),
  [`fpgas-usb-console-log@.service`](https://github.com/fpgas-online/fpgas.online-setup-pi/blob/main/usb-console/fpgas-usb-console-log@.service)
  and [`fpgas-usb-console.conf`](https://github.com/fpgas-online/fpgas.online-setup-pi/blob/main/usb-console/fpgas-usb-console.conf)
  — the two gadget ports, why the log and the getty are separate, and the
  host-side capture.
- [`felboot/fpgas-felboot@.service`](https://github.com/fpgas-online/fpgas.online-setup-pi/blob/main/felboot/fpgas-felboot@.service),
  [`60-fpgas-felboot.rules`](https://github.com/fpgas-online/fpgas.online-setup-pi/blob/main/felboot/60-fpgas-felboot.rules)
  and [`fpgas-felboot.sh`](https://github.com/fpgas-online/fpgas.online-setup-pi/blob/main/felboot/fpgas-felboot.sh)
  — the `1f3a:efe8` match, the `%i` escaping note, and the retry and marker
  behaviour.
- The `onpi/` unit files
  ([`pistat_ssh.service`](https://github.com/fpgas-online/fpgas.online-setup-pi/blob/main/onpi/pistat_ssh.service),
  [`pistat_cam.service`](https://github.com/fpgas-online/fpgas.online-setup-pi/blob/main/onpi/pistat_cam.service),
  [`pistat_info.service`](https://github.com/fpgas-online/fpgas.online-setup-pi/blob/main/onpi/pistat_info.service),
  [`pistat_shutdown.service`](https://github.com/fpgas-online/fpgas.online-setup-pi/blob/main/onpi/pistat_shutdown.service),
  [`is_arty/arty_here.service`](https://github.com/fpgas-online/fpgas.online-setup-pi/blob/main/onpi/is_arty/arty_here.service),
  [`is_wire/arty_wire.service`](https://github.com/fpgas-online/fpgas.online-setup-pi/blob/main/onpi/is_wire/arty_wire.service),
  [`arty_blink/arty_blink.service`](https://github.com/fpgas-online/fpgas.online-setup-pi/blob/main/onpi/arty_blink/arty_blink.service))
  — what each reports, the `ExecStart` paths that no longer match what
  `nfpm.yaml` installs, the `curl`-only pistat `ExecStart` lines, the
  `cam.target`/`cam.service` references in `pistat_cam.service`, and the
  `arty_here.target` and `arty_wire.target` orderings.
- [`onpi/is_arty/arty_here.sh`](https://github.com/fpgas-online/fpgas.online-setup-pi/blob/main/onpi/is_arty/arty_here.sh)
  — its call to `/usr/local/bin/arty_here.exp`, installed as
  `fpgas-arty-here.exp`.
- [`pistat-scripts/send.py`](https://github.com/fpgas-online/fpgas.online-setup-pi/blob/main/pistat-scripts/send.py),
  [`send_stat.py`](https://github.com/fpgas-online/fpgas.online-setup-pi/blob/main/pistat-scripts/send_stat.py)
  and [`send_ncc.py`](https://github.com/fpgas-online/fpgas.online-setup-pi/blob/main/pistat-scripts/send_ncc.py)
  — the Django/dnsmasq imports and the `/srv/www/pib/venv` shebang that make
  these server-side code.

[fpgas.online-cam](https://github.com/fpgas-online/fpgas.online-cam), `main`:

- [`README.md`](https://github.com/fpgas-online/fpgas.online-cam/blob/main/README.md)
  — the four scripts and what the deb installs.
- [`cam.service`](https://github.com/fpgas-online/fpgas.online-cam/blob/main/cam.service)
  — `ExecStart=/usr/local/bin/fpgas-gst-libcam.sh`, `Restart=always`.
- [`gst-libcam.sh`](https://github.com/fpgas-online/fpgas.online-cam/blob/main/gst-libcam.sh)
  — the pipeline, the `v4l2h264enc`-versus-`x264enc` choice, the RTMP
  destination derived from the default route, and the latency budget with the
  2026-08-30 measurement.
- [`nfpm.yaml`](https://github.com/fpgas-online/fpgas.online-cam/blob/main/nfpm.yaml)
  — the installed paths and the `fpgas-cam.service` name.

[fpgas.online-tt](https://github.com/fpgas-online/fpgas.online-tt), `main`:

- [`README.md`](https://github.com/fpgas-online/fpgas.online-tt/blob/main/README.md)
  — the daemon, `/dev/ttboard`, the demo directory, and the note that every Pi
  runs it.
- [`debian/fpgas-tt.service`](https://github.com/fpgas-online/fpgas.online-tt/blob/main/debian/fpgas-tt.service)
  and [`debian/60-fpgas-tt.rules`](https://github.com/fpgas-online/fpgas.online-tt/blob/main/debian/60-fpgas-tt.rules)
  — the unit's user, group and arguments, and the `2e8a:0005` / `2e8a:000f`
  symlink rule.

[fpgas.online-site](https://github.com/fpgas-online/fpgas.online-site), `main`:

- [`pibfpgas/src/pibfpgas/templates/fpga.html`](https://github.com/fpgas-online/fpgas.online-site/blob/main/pibfpgas/src/pibfpgas/templates/fpga.html)
  — the `vlc https://<domain>/live/pi<N>.m3u8` line offered on each board page.

[fpgas.online-test-designs](https://github.com/fpgas-online/fpgas.online-test-designs), `main`:

- [`docs/verify-hardware.md`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/verify-hardware.md)
  — "Pre-Test Commands": why `mask` and not `stop`, the `rmmod spidev
  spi_bcm2835` GPIO 7–11 clash, the Pi 5 `pinctrl set 14 a4` restoration, and
  the note that a PoE cycle loses the mask.
