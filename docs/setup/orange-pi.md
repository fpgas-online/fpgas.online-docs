# Orange Pi H3 hosts

Five Orange Pi PC boards (Allwinner H3, ARMv7) sit on the Welland rack and boot
the *same* NFS root as the Raspberry Pis: the Raspbian bookworm armhf userland
runs unchanged on an H3, so only the kernel, initrd and DTB are board-specific.
They have no SD or eMMC, so each one powers up in the Allwinner BROM's USB FEL
mode and is loaded with U-Boot over its OTG cable by a hub host, `pi-sw2-p30`,
which is also where its console lands: the same cable carries a USB serial
gadget once Linux is running.

This page covers how that boot works, how to deploy and re-converge it, how to
read a board's console and verify it, how to recover or add a board, the known
failures, the port/USB/MAC mapping, what is special about the hub host, and the
design behind the shared root.

## How it works

The boards have no SD or eMMC, so on power-up the Allwinner BROM waits in USB
FEL mode (`1f3a:efe8`). Their OTG cables go to the hub host **pi-sw2-p30**; its
`fpgas-online-setup-pi` package ships a udev rule that starts
`fpgas-felboot@<usb-device>.service`, which loads U-Boot with `sunxi-fel`.
U-Boot's distro-boot then DHCPs — the per-port VLAN scheme hands it
`pi-sw2-p<port>` / `10.21.2.<port>` exactly as it would a Pi — and fetches
`pxelinux.cfg/default-arm-sunxi` plus `sunxi/{vmlinuz,initrd.img,dtbs/…}` from
tweed's TFTP root, then boots the [shared Pi NFS
root](netboot.md#the-nfs-root-is-shared-and-read-only) with the Debian `armmp`
kernel that `fixpi/tasks/sunxi.yml` bakes into it.

U-Boot looks for `pxelinux.cfg/01-<mac>` first, then the IP-hex names, then
`default-arm-sunxi`, `default-arm` and `default` — so a different sunxi board
model can be given its own file without disturbing these five. The one
`fixpi` templates is short:

```jinja
default sunxi
timeout 10

label sunxi
  kernel sunxi/vmlinuz
  initrd sunxi/initrd.img
  fdt sunxi/dtbs/{{ sunxi_default_dtb }}
  append root=/dev/nfs nfsroot={{ eth_local_address }}:{{ nfs_root }}/root,nfsvers=3,tcp ro ip=dhcp rootwait consoleblank=0 overlayroot=tmpfs console=ttyS0,115200 systemd.log_level=debug systemd.log_target=kmsg log_buf_len=1M printk.devkmsg=on
```

`sunxi_default_dtb` is `sun8i-h3-orangepi-pc.dtb`. There is no `netconsole=` on
that append line, unlike the Pi [kernel command
line](netboot.md#the-kernel-command-line): `dwmac-sun8i` is an initramfs module,
so built-in netconsole has no interface to bind to on sunxi. `console=ttyS0` is
the H3's UART0 3-pin debug header, which is not wired on the rack, and
`console=ttyGS0` would be inert because `CONFIG_U_SERIAL_CONSOLE` is unset in
both Debian's `armmp` kernel and every Raspbian kernel in the root — which is
why the usable console is fed from userspace instead.

`fixpi/tasks/sunxi.yml` is the whole root-side story, and every task in it is
guarded by `when: sunxi_boards is defined` so no other site is touched. It adds
a Debian bookworm armhf apt source to the root pinned so that only
`linux-image-*-armmp` and `linux-base` may come from it, installs
`linux-image-armmp` into the root through `chroot-mount-pi-fs.bash`, and copies
`vmlinuz-*-armmp`, `initrd.img-*-armmp` and the three
`sun8i-h3-orangepi-{pc,pc-plus,one}.dtb` files into `<tftp_root>/sunxi/`. The
install is safe for the Pi fleet: Raspbian's `z50-raspi-firmware` kernel hook
prints "Unsupported kernel version (6.1.0-50-armmp) - skipping setup" and leaves
`/boot/firmware` untouched (verified 2026-08-28 in the spike).

The boards are declared in `sunxi_boards` in
`ansible/inventory/host_vars/fpgas.online.yml`, one mapping per board with
`switch`, `port`, `host`, `usb`, `model` and `mac` keys — the same five rows as
the mapping table below, all `model: orangepi-pc` and all `host: pi-sw2-p30`.

## Deploying and reconverging

Run from an infra checkout, against the Welland gateway:

```console
$ # main, or the PR worktree
$ cd ~/github/fpgas-online/fpgas.online-infra
$ uv run ansible-playbook -i ansible/inventory ansible/site.yml \
    --limit fpgas.online,pi \
    --tags fixpi,netboot,sunxi,sunxi-kernel,onpi,fpgas-apt
```

- `--limit` must include `pi`, the nspawn provisioning host, or the NFS root is
  not touched at all.
- The first run installs the kernel into the root and takes about 30 minutes
  under qemu, almost all of it `update-initramfs`. Later runs skip it on a
  `creates:` guard, and kernel upgrades afterwards arrive through `onpi`'s apt
  upgrade like every other package — which is why CI can skip the
  `sunxi-kernel` tag.

Check the result on tweed:

```console
$ # the boot payload and the PXE file
$ ls /srv/nfs/rpi/bookworm/boot/sunxi /srv/nfs/rpi/bookworm/boot/pxelinux.cfg
$ # the packages the hub host and the boards need
$ chroot /srv/nfs/rpi/bookworm/root dpkg -l fpgas-online-setup-pi sunxi-tools
```

:::{warning}
Running Pis do not see NFS-root changes until they reboot, and it is worse than
stale: a file the converge replaced becomes `Stale file handle` on a running
host, and udev then drops the felboot rule for hot-plugged boards. **Always
PoE-cycle pi-sw2-p30 (port 30) after a converge**, then the boards.
:::

## Reading a console

Once Linux runs, each board's OTG cable presents a `0525:a4a7 Linux-USB Serial
Gadget` (`fpgas.online usb-console`) to the hub host with two CDC-ACM ports.
`/dev/serial/by-path/platform-xhci-hcd.0-usb-0:<hub port>:2.0` is the kernel log
(`fpgas-usb-console.service` on the board, running `dmesg --follow`) and `…:2.2`
is a login getty. The hub host's `fpgas-usb-console-log@ttyACM*.service` appends
the log port to `/var/log/fpgas-usb-console/<hub port>.log` from the moment the
gadget enumerates. Both units are described under [Pi
services](pi.md#services); here they are the only console the boards have.

```console
$ # the hub host
$ ssh 10.21.2.30
$ # hub port :2.0 is the kernel log, :2.2 the getty
$ ls -l /dev/serial/by-path/ | grep ':2.0'
$ # captured from the first byte -- 1-1.3.1 is pi-sw2-p21
$ tail -f /var/log/fpgas-usb-console/1-1.3.1.log
$ # the login getty on the same cable
$ picocom /dev/serial/by-path/platform-xhci-hcd.0-usb-0:1.3.1:2.2
```

- The board replays its whole ring buffer to every *USB attach*. A second reader
  on an already-attached port sees only new lines; to replay again, restart
  `fpgas-usb-console` on the board.
- Open the port once, in raw mode — `picocom`, `tio` or the logger. An `stty -F`
  before a `cat` opens and closes the port in cooked mode and drops the start of
  the stream.
- A board that crawls on its first boot now leaves its kernel log in
  `/var/log/fpgas-usb-console/<hub port>.log` on the hub host, which is how the
  audio-codec Oops below was finally found.

Verified 2026-08-29 on pi-sw2-p21: `ttyACM0`/`ttyACM1` at `1.3.1`, 1.1 MB of log
replayed in 4 s, and `pi-sw2-p21 login:` on the second port. A cold PoE cycle of
pi-sw2-p20 the same day was captured from `[    0.000000] Booting Linux` — the
gadget enumerated 55 s after power-on and the logger wrote `1-1.2.2.log` from
the first byte. The capture-from-enumeration design exists because the cmdline
carries `systemd.log_level=debug`, under which the 1 MB ring buffer wraps within
minutes and a late reader cannot recover the early boot.

### No USB host attached does not block or delay the boot

Tested 2026-08-29 on pi-sw2-p20 by disabling its hub port in sysfs
(`/sys/bus/usb/devices/1-1.2:1.0/1-1.2-port2/disable`) one second after
`fpgas-felboot` loaded U-Boot, so the OTG link was dead for the whole boot:

| Check | Result |
| --- | --- |
| `systemd-analyze` | `15.693s (kernel) + 48.248s (userspace) = 1min 3.941s`, `graphical.target` after 40.8 s |
| `systemctl is-system-running` | `running`, `systemctl --failed` empty |
| gadget | `/sys/class/udc/musb-hdrc.2.auto`, `/dev/ttyGS0`, `/dev/ttyGS1` present |
| units | `fpgas-usb-console.service` and `serial-getty@ttyGS1.service` both `active` |
| sshd | reachable 96 s after power-on |

Re-enabling the port made the gadget enumerate immediately (`0525:a4a7`,
`ttyACM2`/`ttyACM3` at `1-1.2.2`) and the log resumed streaming. Note that the
board had by then been up for two minutes with `systemd.log_level=debug` and the
ring buffer had already wrapped past `Booting Linux` — exactly why the hub host
captures from enumeration rather than reading on demand.

## Verifying

```console
$ # from the infra checkout, against the boards and the hub host
$ uv run ansible-playbook -i 10.21.2.20,10.21.2.21,10.21.2.23,10.21.2.24,10.21.2.30, \
    ansible/verify-pi.yml -u pi -e verify_pi_hosts=all --skip-tags hw-camera,hw-fpga
```

The `hw-sunxi` group asserts that each Orange Pi runs an `armmp` kernel on
`armv7l`, that the audio codec modules stay unloaded on Orange Pi hardware, and
that the hub host has an `fpgas-felboot@<usb>` instance for every board declared
for it in `sunxi_boards`. Because a netbooted Pi's journal is volatile and
rotates fast, `fpgas-felboot.sh` writes a per-board success marker under
`/run/fpgas-felboot/` and that is what the check reads.

:::{note}
The inventory line above is the runbook's, written when there were four boards;
it does not include `10.21.2.22`, the fifth board resolved on 2026-08-28
evening. Add it when running the check today.

It also predates the hub host's move to an SD card: `verify-pi.yml` no longer
applies to `pi-sw2-p30` at all (no `pi` user, not the NFS root), so the hub-host
half of `hw-sunxi` has to target it as another user or move to the fleet repo.
:::

Deployment result on 2026-08-28: a hub-host reboot fired `fpgas-felboot@` for
all four boards then known within its 19 s boot, and staggered PoE cycles
reached `multi-user` in 49 s (p20), 52 s (p23) and 35 s (p24) — 16 s of kernel
plus 19–37 s of userspace — on the production root with kernel
`6.1.0-50-armmp`. `verify-pi.yml` including `hw-sunxi` was green on the four
boards and the hub host, p21 after its second cycle.

## Recovery

There is no remote power control other than PoE; see [PoE power
control](network.md#poe-power-control) for the scripted paths and the switch
credentials, which are not repeated here.

```console
$ # off, then on -- the board is back in FEL about 3 s later
$ ngsw --config ~/.config/ngsw/inventory.toml --switch s3300-1 poe 20 off -y --force
$ ngsw --config ~/.config/ngsw/inventory.toml --switch s3300-1 poe 20 on -y --force
$ # what the hub host did about it
$ journalctl -u 'fpgas-felboot@*'
```

- **Board unreachable** — PoE-cycle its switch port. It re-enumerates in FEL on
  the hub host within about 3 s and is FEL-booted automatically; the
  `fpgas-felboot@` journal on pi-sw2-p30 shows the attempts (three tries, two
  seconds apart).
- **Hub host unreachable** — PoE-cycle port 30. Every board re-enumerates when
  the hub host comes back and is booted then.
- **No early console** — `netconsole=` is inert on sunxi, and the H3's UART0
  3-pin header at 115200 8N1 is the only way to see U-Boot or early kernel
  output. The PL2303 on the hub host is not wired to any board's header, so in
  practice the earliest thing anyone can see is the gadget console, which starts
  once Linux is up.

## Adding a board

1. Cable it: a PoE port on s3300-1, and the OTG micro-USB to the hub host.
2. On the hub host, `sudo sunxi-fel --list` shows the new device with its SID,
   and `ls -l /sys/bus/usb/devices/ | grep <busnum>-` gives its USB path. The
   felboot service will already have booted it, so read its MAC from the switch
   (`ngsw … --json macs`, VLAN 22xx of its port).
3. Add it to `sunxi_boards` in
   `ansible/inventory/host_vars/fpgas.online.yml` (`switch`, `port`, `host`,
   `usb`, `model`, `mac`) and to the inventory sheet tool
   (`welland-ansible-rpi` `tools/rpi_hardware_sheet.py`: a `FPGAS_PORT_MAC`
   entry plus a `KNOWN_BOARDS` entry) so the RPi Hardware sheet names it.
4. A different sunxi board model needs its own U-Boot build, vendored in
   `fpgas.online-setup-pi/felboot/u-boot/`, and possibly a per-MAC
   `pxelinux.cfg/01-<mac>` naming its DTB — U-Boot looks for that file first.

## Known issues

**Slow first boot after a cold FEL boot.** Any board may crawl on its first boot
after a power cycle and never reach sshd: U-Boot loads, the kernel boots and
mounts the NFS root (the kernel DHCP is visible on tweed), but userspace reads
about 40 MB from NFS in 10 minutes where a healthy sibling reads about 170 MB in
2 minutes, and sshd never starts. Seen twice on p21 and once on p24 on
2026-08-28 — 2 of 3 first boots that day — so it is a general flake of roughly
1 in 4 cold FEL boots, not a bad board. A second PoE cycle boots it normally in
about 87–90 s every time. Treat "board not up after 5 minutes" as "cycle it
again", not as an infrastructure fault.

**Kernel Oops in the sunxi audio codec probe (found 2026-09-02).** The gadget
console captures show the same crash on three boards — pi-sw2-p20, pi-sw2-p21
and the board on hub port 1-1.3.3 — about 25 s into boot:

```text
Internal error: Oops: 80000005 [#1] SMP ARM
Workqueue: events_unbound deferred_probe_work_func
PC is at 0x15669654                     <- garbage pointer (== r3)
LR is at snd_soc_dai_set_fmt+0x34/0x94 [snd_soc_core]
Modules linked in: sun8i_codec_analog sun4i_codec sun8i_adda_pr_regmap ...
```

It is a call through an uninitialised DAI `set_fmt` pointer while the
`sun4i-codec` sound card retries its deferred probe, and it kills the
`events_unbound` kworker running `deferred_probe_work_func` — the strongest lead
so far for the crawling first boot above, which predates the gadget console and
was undiagnosable without it. The boards have no audio use, so
`fixpi/tasks/sunxi.yml` now writes
`/etc/modprobe.d/fpgas-sunxi-no-audio.conf` into the root blacklisting
`sun4i_codec`, `sun8i_codec_analog` and `sun8i_adda_pr_regmap`. A root blacklist
is enough to cover every load path because none of the three are in the sunxi
initramfs — they load only from udev's DT-alias coldplug once the real root is
mounted — and `verify-pi` asserts they stay unloaded on Orange Pi hardware.

:::{note}
The Oops report names a board on hub port `1-1.3.3`, which is not one of the
five ports in the mapping table below (`1-1.2.2`, `1-1.2.3`, `1-1.2.4`,
`1-1.3.1`, `1-1.3.2`) and not in `sunxi_boards`. Either a sixth board was
cabled after the mapping was written, or the port was recorded wrongly.
:::

**Boards dying part-way into uptime (2026-09-02).** On the same day, four of the
five boards (p20 to p23) were found dead 19 to 36 minutes into uptime: the USB
gadget still enumerated, PoE still drew 1.5–2.5 W, but there was no ping or ssh,
and each console log ended mid-normal-operation with `fpgas-cam.service`
crash-looping (`status=255/EXCEPTION`). This may be a separate problem from the
boot-time Oops; the next hang will be on the captured consoles.

**A two-minute `udevadm settle`.** `ifupdown-pre.service` sat through its full
two-minute settle on an H3 while the rest of userspace took about 14 s. It is
masked to `/dev/null` in the root along with `networking.service`, described
under [boot-time configuration](pi.md#boot-time-configuration); the underlying
stuck udev event was never identified.

## Board mapping

Established 2026-08-28, two ways: by switching each candidate PoE port off for
25 s and watching which FEL device vanished from the hub host's USB tree, and by
FEL-booting U-Boot on each board and reading the MAC the switch learned. Both
methods agreed for all four boards then known; `1/g22` was resolved the same
evening when its OTG cable turned up on hub port `1-1.3.2` and felboot picked it
up as `pi-sw2-p22`.

All five are Allwinner H3 (`sunxi-fel ver` reports `soc=0x1680`) and all five
run the `orangepi_pc_plus` U-Boot build with DRAM init OK.

| Hub port (sysfs) | Switch port (s3300-1 = "sw2") | VLAN | IP / hostname (per-port scheme) | MAC (U-Boot, derived from SID) | SID (`sunxi-fel sid`) |
| --- | --- | --- | --- | --- | --- |
| 1-1.2.2 | 1/g20 | 2220 | 10.21.2.20 `pi-sw2-p20` | 02:81:bf:f6:b7:99 | 02c00181:34304620:79058814:541b0614 |
| 1-1.3.1 | 1/g21 | 2221 | 10.21.2.21 `pi-sw2-p21` | 02:81:31:f4:6e:48 | 02c00081:35b04620:79058814:502c0194 |
| 1-1.3.2 | 1/g22 | 2222 | 10.21.2.22 `pi-sw2-p22` | 02:81:2e:b7:a3:4e | 02c00081:35d04620:79058814:401c0a94 |
| 1-1.2.3 | 1/g23 | 2223 | 10.21.2.23 `pi-sw2-p23` | 02:81:1f:e1:45:1d | 02c00181:34504620:79058814:40260714 |
| 1-1.2.4 | 1/g24 | 2224 | 10.21.2.24 `pi-sw2-p24` | 02:81:f5:c0:a6:10 | 02c00081:35e04620:79058814:48230714 |

- Power comes from PoE on s3300-1 through a splitter: 1.1–1.2 W while idle in
  FEL, about 1.5 W with U-Boot running. The micro-USB OTG cable does **not**
  power them — cutting PoE made the USB device disappear within seconds, which
  is why the fleet's ordinary PoE-cycle recovery works unchanged here.
- Link speed once U-Boot is up is 100 Mbit/s, the H3's internal fast-ethernet
  PHY.
- The exact board variant (OPi PC, PC Plus or One) still needs a physical check.
  Both U-Boot's `orangepi_pc_plus` build and the `sun8i-h3-orangepi-pc` DT run;
  the boards report `Memory: 992 MB`, so they are not 512 MB "One" boards, and
  the kernel log — SY8106A regulator present, RAM size — will narrow the rest
  down.

One other device hangs off the hub, and it is worth knowing it is useless:

| Hub port | Device | Notes |
| --- | --- | --- |
| 1-1.1.4 | Prolific PL2303 USB-serial (067b:2303) → `/dev/ttyUSB0` | Received **nothing** at 115200 8N1 while each of the four boards ran U-Boot, so it is not wired to any of their UART0 headers (or is wired TX/RX-swapped). |

:::{todo}
[Welland](../sites/welland.md#hosts-and-boards) does not list these five boards
in any of its host tables. They are on s3300-1 ports 20 to 24 per `sunxi_boards`
and the mapping above; the site page should gain an Orange Pi section for them.
:::

### udev symlinks on the hub host

Recorded 2026-08-28. `/etc/udev/rules.d/70-fpgas-opi-ports.rules` on the hub
host (source of truth: `welland-ansible-rpi`
`inventory/host_vars/rpi5-new-13f59c.yml`, `hw_udev_files`) names each FEL
device by everything known about it. The links exist only while a board sits in
FEL — that is, from power-on until `fpgas-felboot@` loads U-Boot — so they are
the handle for anything that has to talk to a board *before* it boots.

| Hub port | `/dev/fpgas/opi/…` symlinks (all → `/dev/bus/usb/001/NNN`) |
| --- | --- |
| 1-1.2.2 | `sw2-p20`, `usb-1-1.2.2`, `sid-02c00181-34304620-79058814-541b0614`, `mac-02-81-bf-f6-b7-99` |
| 1-1.3.1 | `sw2-p21`, `usb-1-1.3.1`, `sid-02c00081-35b04620-79058814-502c0194`, `mac-02-81-31-f4-6e-48` |
| 1-1.3.2 | `sw2-p22`, `usb-1-1.3.2`, `sid-02c00081-35d04620-79058814-401c0a94`, `mac-02-81-2e-b7-a3-4e` |
| 1-1.2.3 | `sw2-p23`, `usb-1-1.2.3`, `sid-02c00181-34504620-79058814-40260714`, `mac-02-81-1f-e1-45-1d` |
| 1-1.2.4 | `sw2-p24`, `usb-1-1.2.4`, `sid-02c00081-35e04620-79058814-48230714`, `mac-02-81-f5-c0-a6-10` |
| any other | `usb-<port>` (`FPGAS_SWITCH_PORT=unknown`) |
| 1-1.1.4 (PL2303) | `/dev/fpgas/serial/hub-1-1.1.4` → `ttyUSB0` |

`udevadm info` on the device also carries `FPGAS_SWITCH_PORT=sw2-pNN`. Verified
by masking p24's felboot instance, holding it in FEL and reading the links.

## The hub host

`pi-sw2-p30` is a Raspberry Pi 5 Rev 1.1, 1 GB, serial `3c1fc2b41d68ae81`, eth0
`98:fe:54:13:f5:9c`, on s3300-1 port 30. Its USB tree is one Realtek RTS5411 hub
at `1-1` with four RTS5411 sub-hubs `1-1.1` to `1-1.4`, giving 16 downstream
ports; the USB-3 twin at `2-1` (0bda:0411) has nothing attached.

On the evening of 2026-08-28 it stopped being an NFS-root Pi. Its 8 GB microSD
now carries the `welland-ansible-rpi` **fleet-bootstrap-arm64** image
(Raspberry Pi OS trixie, cloud-init accounts `tim` and `ansible`, hostname
`rpi5-new-13f59c`), and the Pi 5 EEPROM is `BOOT_ORDER=0xf21` — SD first,
netboot only if the card fails. That was verified both ways: with the card in,
the bootloader fetches nothing from tweed; with netboot deliberately broken, the
card booted and both accounts logged in. tweed still hands it `10.21.2.30` and
`pi-sw2-p30` on the per-port VLAN, so nothing about the boards' addressing
changes.

:::{note}
The mapping document, written earlier the same day, still describes this host as
netbooting the shared Raspbian bookworm NFS root with `overlayroot=tmpfs`. The
evening addendum supersedes it: it is a fleet host with its own SD image now.
:::

Three things were hand-configured on that OS, to be captured by
`welland-ansible-rpi` when the host is enrolled there:

- the apt source `https://fpgas.online/apt trixie main` (key in
  `/usr/share/keyrings/fpgas-online.gpg`), with `fpgas-online-setup-pi` and
  `sunxi-tools` installed — this is what FEL-boots the Orange Pis, and it is
  proven on this OS: a PoE-cycled board was back in 72 s;
- the NetworkManager profile `netplan-eth0` with `ipv4.never-default yes` and
  `ipv6.never-default yes`, because eth0 (tweed's VLAN) has no internet and
  wlan0 on `ansells-iot` carries the default route;
- the consequence for this page: the hub-host half of the verification above no
  longer runs as the `pi` user.

Changing the EEPROM on a still-*netbooted* Pi 5 has a trap worth recording next
to the [EEPROM write protect](netboot.md#eeprom-write-protect) procedure: the
bootloader looks for `pieeprom.sig` and `pieeprom.upd` at the TFTP **root**, not
in its per-serial directory, so serving an update to exactly one Pi needs a
per-interface `tftp-root=<dir>,v22NN` in dnsmasq. The same trick with an empty
directory is how one Pi's netboot was deliberately broken for the SD-fallback
test above. On the SD-booted OS, `rpi-eeprom-config --apply` flashes directly.

## Design

The 2026-08-28 spike chose a **shared NFS root plus a second kernel** over a
dedicated Orange Pi root, because the Raspbian bookworm armhf userland runs
unchanged on an ARMv7 H3 and only the kernel, initrd and DTB are board-specific,
so the boards get every fleet change for free from one image pipeline, one `pi`
play, one set of packages and one `verify-pi`. The cost is one extra kernel
package in the root (about 250 MB of modules and the one-off 30-minute
qemu-emulated `update-initramfs`), a `sunxi/` TFTP directory and one PXE file —
against a dedicated root, which would have doubled the roughly 100-minute apt
converge and forked every Pi role. An Armbian root and per-MAC `pxelinux.cfg`
files were rejected for the same reason, the latter kept as the escape hatch if
a different sunxi board ever appears.

The FEL mechanism is what makes SD-less boards bootable at all: the H3 BROM
falls into USB FEL mode on every power-up and enumerates as `1f3a:efe8`, so the
hub host's udev rule (`60-fpgas-felboot.rules`, matching that VID/PID and adding
`SYSTEMD_WANTS`) starts `fpgas-felboot@%k.service`, and `fpgas-felboot.sh` reads
`busnum`/`devnum` out of sysfs and runs `sunxi-fel --dev <bus>:<dev> uboot
u-boot-sunxi-with-spl.bin`, retrying three times. About 3 s after a PoE cycle
the board is back in FEL and is re-booted with no operator action. The unit uses
`%i` rather than `%I` deliberately: systemd unescapes `%I` and turns the USB
name `1-1.2.2` into `1/1.2.2`, found on hardware on 2026-08-28.

Raspbian ships no `u-boot-sunxi`, so the image is vendored in
`fpgas.online-setup-pi` under `felboot/u-boot/orangepi_pc_plus/`, copied
unmodified from Debian's `u-boot-sunxi_2025.01-3+deb13u1_armhf.deb`
(GPL-2.0-or-later). The README pins both hashes: sha256
`9f10a3532457b71006053028b013e7c73f86f55788872c8fba40ba1aa45f53cb` for the
559488-byte `.bin` and
`c34a1e756612a10ba3fa2abe4bdc6c0dd685cc472628879b0fe153251073c36a` for the
`.deb`, with a refresh procedure of download, `dpkg-deb -x`, copy, update the
hashes. The `orangepi_pc_plus` build runs on these PC boards because they share
the H3 and the 1 GB DRAM; the extra eMMC and wifi nodes are harmless, and it
only has to reach distro-boot.

Two details of the design drifted before it shipped, and the shipped form is
what this page documents. The spec proposed a separate `fpgas-online-felboot`
package and a `felboot@<bus:dev>.service`; what exists is
`fpgas-online-setup-pi` shipping `fpgas-felboot@<usb kernel device>.service`, so
any Pi with FEL devices on its USB is a boot host. The spec also counted four
boards; there are five, the fifth resolved on the evening the spec was written.

:::{todo}
Confirm the board variant by physical inspection. The spec, the mapping document
and the vendored U-Boot README all record the same open question: these are
1 GB H3 boards running an `orangepi_pc_plus` U-Boot and a
`sun8i-h3-orangepi-pc` device tree, and nobody has yet looked at one to say
whether it is an Orange Pi PC or a PC Plus. `sunxi_boards` records them all as
`model: orangepi-pc`.
:::

## Sources

fpgas.online-infra, `main`:

- [`docs/superpowers/runbooks/2026-08-28-orange-pi-netboot.md`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/docs/superpowers/runbooks/2026-08-28-orange-pi-netboot.md)
  — how the boot works, the converge command and its tags, reading a console on
  the hub host, the verify invocation, PoE recovery, adding a board, the
  1-in-4 cold-boot flake, and the 2026-08-28-evening hub-host addendum.
- [`docs/hardware/2026-08-28-orange-pi-h3-boards.md`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/docs/hardware/2026-08-28-orange-pi-h3-boards.md)
  — the port/USB/MAC/SID mapping and how it was established, the hub host's USB
  tree, the PL2303, the udev symlink scheme, the USB gadget console and the
  no-host-attached measurements, the slow-first-boot flake, the 2026-08-28
  deployment result, and the 2026-09-02 audio codec Oops and mid-uptime deaths.
- [`docs/superpowers/specs/2026-08-28-orange-pi-netboot-design.md`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/docs/superpowers/specs/2026-08-28-orange-pi-netboot-design.md)
  — the shared-root decision and what it was weighed against, the FEL answer,
  the inert `netconsole=` and `console=ttyGS0` findings, the `ifupdown-pre`
  wait, and the open PC-versus-PC-Plus question.
- [`ansible/roles/fixpi/tasks/sunxi.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/fixpi/tasks/sunxi.yml)
  — the pinned Debian armhf source, the `creates`-guarded kernel install, the
  `sunxi/` TFTP publish, the three DTBs, and the audio blacklist file.
- [`ansible/roles/fixpi/templates/boot/default-arm-sunxi.j2`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/fixpi/templates/boot/default-arm-sunxi.j2)
  — the U-Boot distro-boot PXE config, its lookup order and its append line.
- [`ansible/inventory/host_vars/fpgas.online.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/inventory/host_vars/fpgas.online.yml)
  — `sunxi_kernel_package`, `sunxi_default_dtb` and the five `sunxi_boards`
  entries.

fpgas.online-setup-pi, `main`:

- [`felboot/60-fpgas-felboot.rules`](https://github.com/fpgas-online/fpgas.online-setup-pi/blob/main/felboot/60-fpgas-felboot.rules)
  — the `1f3a:efe8` match and the `SYSTEMD_WANTS` instance name.
- [`felboot/fpgas-felboot@.service`](https://github.com/fpgas-online/fpgas.online-setup-pi/blob/main/felboot/fpgas-felboot@.service)
  — `StopWhenUnneeded`, and `%i` rather than `%I`.
- [`felboot/fpgas-felboot.sh`](https://github.com/fpgas-online/fpgas.online-setup-pi/blob/main/felboot/fpgas-felboot.sh)
  — the sysfs `busnum`/`devnum` lookup, the three retries, and the
  `/run/fpgas-felboot` markers.
- [`felboot/u-boot/README.md`](https://github.com/fpgas-online/fpgas.online-setup-pi/blob/main/felboot/u-boot/README.md)
  — the vendored image provenance, both SHA256 pins, and the refresh procedure.
