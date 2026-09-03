# Netboot and the NFS root

Every Raspberry Pi in the fleet boots from the network. There is no SD card and
no local storage: the board's ROM asks for DHCP, pulls its bootloader and kernel
over TFTP, and mounts one shared read-only NFS root from the site gateway, with a
tmpfs overlay on top that is thrown away on every reboot.

This page covers the boot chain, what the shared root is and what that costs you,
how the root gets built on the gateway, how to push a change out to a running
fleet, and the bootloader EEPROM lock that keeps the one non-ephemeral piece of
per-board state from drifting.

## The boot chain

1. The Pi powers on and its ROM broadcasts DHCP.
2. dnsmasq on the gateway's internal NIC answers with an address and its own
   TFTP address. It binds with `bind-dynamic` rather than `bind-interfaces`,
   because on a per-port-VLAN site there are roughly 150 per-port interfaces and
   most have no carrier until a Pi is plugged in — `bind-interfaces` would make
   dnsmasq refuse to start.
3. The Pi fetches `bootcode.bin`, the kernel, the DTB and the initramfs over
   TFTP.
4. The kernel mounts the NFS root read-only and layers a tmpfs over it.
5. Everything the Pi needs is already installed in that root. Nothing is
   configured at boot.

dnsmasq also advertises the gateway as the NTP server. The Pis have no route to
the internet (the firewall drops forwarding), and without this their clocks sit
on the `fake-hwclock` date forever — found during the tweed rebuild on
2026-08-25 and fixed in the `pxe` role.

### Where TFTP serves from

`tftp_root` is computed, not fixed:

```jinja
tftp_root: "{{ (nfs_root ~ '/boot') if switches is defined else '/srv/tftp' }}"
```

On a per-port-VLAN site (`switches` is defined) dnsmasq serves the NFS root's
own `boot/` directory directly. The Pi 4 bootloader asks for `<serial>/<file>`
first and, when `start4.elf` is not there, clears the prefix and re-requests
every file from the root — so no Pi has to be registered by serial number.

Legacy MAC-table sites keep `/srv/tftp`, where the `fixpi` role creates one
symlink per Pi serial number pointing at the NFS root's `boot/`, plus a
`bootcode.bin` symlink at the top because, in the role's own words, Pi netboot
is not too smart.

That difference decides what an operator does to add a Pi. On a per-port-VLAN
site: nothing — plug it into the port, and the cleared TFTP prefix means it
gets the shared `boot/` without being registered anywhere. On a legacy
MAC-table site: add a `{port, mac, sn, model, loc, cable_color}` entry to
`switch.nos` in the site's `host_vars`, then re-converge so `netboot.yml`
creates that serial's symlink. See [Network](network.md) for the two addressing
schemes, and [Verification](verification.md) for the checklist afterwards.

### The kernel command line

`cmdline.txt` is templated into the NFS root's `boot/`:

```text
root=/dev/nfs nfsroot=10.21.0.1:{{ nfs_root }}/root,nfsvers=3,tcp ro ip=dhcp rootwait consoleblank=0 netconsole=@/,@10.21.0.1/ overlayroot=tmpfs console=serial0,115200 systemd.log_level=debug systemd.log_target=kmsg log_buf_len=1M printk.devkmsg=on
```

Three parts are load-bearing:

`nfsvers=3,tcp`
: Welland's gateway [tweed](../sites/welland.md#gateway-tweed) runs trixie,
  whose `nfsd` serves v3 over TCP only, while the initramfs `nfsmount` from
  klibc defaults to UDP. Without this the mount hangs in the initramfs. The
  bookworm VM used in CI does not reproduce it, so it was only found on real
  hardware (tweed rebuild, 2026-08-25). PS1's gateway
  [val2](../sites/ps1.md#gateway-val2) is still on bookworm, so the constraint
  is a tweed one, not a fleet-wide one. The flag is in the shared template all
  the same, because there is one template for every site.

`overlayroot=tmpfs`
: The writable layer. See [below](#the-nfs-root-is-shared-and-read-only).

`console=serial0,115200`
: Fine on a Pi 4 and below, wrong on a Pi 5.

This template is what the bookworm root boots. The PS1 Compute Blades boot the
separate trixie root and have `console=tty1` with `serial-getty@ttyAMA0`
inactive, so none of the console reasoning below applies to them — see
[Compute blades](../sites/ps1.md#compute-blades).

On a Pi 5 `dtoverlay=disable-bt` does not free the header UART, so the `fixpi`
role enables it explicitly and points the kernel console somewhere else:

```text
[pi5]
dtoverlay=uart0-pi5
cmdline=cmdline-pi5.txt
[all]
```

`cmdline-pi5.txt` is the same line with `console=ttyAMA10,115200`. That matters
because enabling `uart0` makes the firmware resolve `console=serial0` to
`ttyAMA0` — which on these hosts is wired to the FPGA. A design driving that pin
would then feed the kernel console garbage that SysRq reads as reboot or crash.
Pinning the Pi 5s to their dedicated debug UART keeps the console off the FPGA
and leaves `/dev/ttyAMA0` free. See
[Raspberry Pi 5 specifics](../sites/welland.md#raspberry-pi-5-specifics).

### The export is read-only

Both halves of the root are exported `ro`:

```text
{{ nfs_root }}/boot {{ eth_local_address }}/{{ eth_local_netmask }}(ro,sync,no_subtree_check,no_root_squash)
{{ nfs_root }}/root {{ eth_local_address }}/{{ eth_local_netmask }}(ro,sync,no_subtree_check,no_root_squash)
```

The Pi's own `/etc/fstab` matches: `/` and `/boot/firmware` are both `ro`, and
both are `noauto`. The `noauto` on `/boot/firmware` has consequences all over
the build — see [How the root is built](#how-the-root-is-built).

## The NFS root is shared and read-only

There is one root per distribution for the whole site, at
`/srv/nfs/rpi/<dist>/{boot,root}`. Every Pi mounts the same one. It is built
from a pinned Raspberry Pi OS image — `2024-07-04-raspios-bookworm-armhf-lite`,
downloaded from `downloads.raspberrypi.org` — so a rebuild is reproducible
rather than "whatever is current today".

:::{warning}
The root is read-only and the writable layer is a tmpfs. Everything a user
writes is gone on the next reboot or PoE cycle, including anything staged in
`/home/pi`. A bitstream that loaded a minute ago will fail to open after a
reboot because the file no longer exists — the same warning is recorded under
[PCIe and JTAG interact](../sites/welland.md#pcie-and-jtag-interact) on the
Welland page.
:::

Automation has to account for this. The hardware verification script in
`fpgas.online-test-designs` power-cycles a Pi to recover a Fomu whose DFU
bootloader has timed out, and after the Pi comes back (roughly two minutes) it
re-uploads every file, because the tmpfs is empty again, and re-runs its
pre-test, because the `serial-getty` mask is lost too.

Two roots exist at [PS1](../sites/ps1.md#gateway-val2), because the site runs
two generations of hardware: a bookworm armhf root for the RPi 3B/3B+/4B, and a
separate trixie arm64 root that the Compute Blades boot. Both are read-only with
an overlay.

:::{note}
The Ansible inventory pins one `dist` (`bookworm`) for every host, and no PS1
host variable overrides it, so the trixie arm64 root the blades boot is not
built by the roles described below. How it is maintained is not recorded in the
infra repository.
:::

:::{todo}
Record how the trixie arm64 root is built and maintained. `group_vars/all/srv.yml`
pins `dist: bookworm` for every host and nothing in `fpgas.online-infra` builds a
trixie root, yet the PS1 Compute Blades boot `/srv/nfs/rpi/trixie/`
([Two NFS roots](../sites/ps1.md#gateway-val2)). Either the roles gain a second
`dist`, or the procedure that made that root by hand needs writing down.
:::

## How the root is built

The root is built and configured **on the gateway**, before any Pi boots. No
configuration is applied to a running Pi.

`img`
: Downloads the pinned `.img.xz`, loop-mounts its two partitions and rsyncs them
  into `<nfs_root>/boot` and `<nfs_root>/root`. It installs `xz-utils`
  explicitly — a minimal Debian installer install has no `xz`, which the CI
  cloud image hid.

`fixpi`
: Does everything else to the extracted tree. In rough order:

  - Saves the stock `cmdline.txt`, `user-data` and `fstab` aside as `.org`, then
    templates the netboot versions over them.
  - Appends to `config.txt`: `dtoverlay=disable-wifi` and `dtoverlay=disable-bt`
    to turn the onboard radios off, plus `enable_uart=1` and `uart_2ndstage=1`.
    The two overlay lines cover both generations, because on a Pi 5 (BCM2712)
    the firmware auto-remaps them to `disable-wifi-pi5` and `disable-bt-pi5` via
    `overlay_map.dtb` — on a Pi 4 they disable `&mmc`/`&mmcnr` and `&bt`, on a
    Pi 5 `&sdio2` (so WLAN never enumerates) and `&bluetooth`. Since
    `config.txt` is served read-only over TFTP, these are re-applied on every
    boot: a root user can bring a radio up for the life of a session, but the
    change never survives a reboot.
  - Creates the `pi` user directly, with a `sudoers.d` drop-in granting it
    passwordless sudo. On stock Raspberry Pi OS that comes from the first-boot
    `userconf` mechanism, which this root never runs; without the drop-in,
    Ansible privilege escalation over SSH times out and every Pi reports
    UNREACHABLE.
  - Masks `userconfig.service`, the first-boot setup wizard. Because
    `/boot/firmware` is mounted `noauto`, the wizard never sees its config file,
    finds no answers, and drops into an interactive setup that blocks
    `multi-user.target` forever. This is not a QEMU artefact — a real headless
    Pi hangs on it identically. The same `noauto` is why `ssh.service` is
    enabled directly in the root rather than left to `sshswitch.service`, which
    looks for a flag file it can never see.
  - Runs `apt update` and `apt install -y nfs-common overlayroot` through
    `chroot-mount-pi-fs.bash`, a helper that does the whole bind-mount-and-chroot
    inside a private mount namespace. The private namespace is deliberate: with
    plain binds under systemd's shared `/`, the cleanup unmount propagated back
    and unmounted the *host's* `devpts`, leaving the gateway unable to allocate
    ptys until it was remounted (tweed rebuild, 2026-08-25).
  - Installs a small unit that puts the Pi's own DHCP-assigned hostname into
    `/etc/hosts`, so sudo's per-invocation name lookup is instant instead of
    stalling on DNS and tripping Ansible's escalation timeout.
  - Points the Pi's `timesyncd` at the gateway, matching the DHCP NTP option.
  - Syncs the whole firmware payload from `root/boot/firmware/` into `boot/`,
    excluding the templated `cmdline.txt`, `cmdline-pi5.txt` and `config.txt`.
  - Pre-generates the SSH host keys on the gateway, and disables
    `regenerate_ssh_host_keys.service`, which would otherwise delete and rebuild
    them on first boot — minutes per key under QEMU emulation, with sshd blocked
    the whole time. CI skips the pre-generation so that a published image does
    not ship keys shared by every site that consumes it.
  - `nogrow.yml` diverts and masks the root-resize and swap machinery:
    `rpi-resize.service`, `systemd-growfs@`, `systemd-growfs-root`, the zram
    swap generator, `dphys-swapfile` and `resize2fs_once`. None of them make
    sense on a read-only NFS root.

:::{note}
Sync the *whole* firmware payload, not just the initramfs. Historically `fixpi`
copied only `initramfs8` across, so after a kernel upgrade inside the chroot the
TFTP boot directory served `kernel8.img` 6.6.31 with a 6.12.96 initramfs. The
result was nondeterministic: panic-hangs, boot loops, and half-booted Pis with
sshd never coming up. Found and fixed during the tweed rebuild on 2026-08-25.
:::

Packages come last. `fpgas-apt` adds the fpgas.online APT repository (see
[Packages](../packages.md)), then `cam/pi` and `onpi` install the camera capture
and Pi environment packages — all inside the root, none on a running Pi.

### The provisioning container

Those three roles need to run ARM package scripts on an x86 gateway. What the
`nspawn-pi` role actually sets up is a chroot, reached over SSH:

- `qemu-user-static` is installed and the `qemu-arm` binfmt handler registered,
  so ARM binaries in the root execute transparently.
- `/proc`, `/sys`, `/dev` and `/dev/pts` are bind-mounted into
  `<nfs_root>/root`.
- A `policy-rc.d` stub returning 101 is dropped in, so `apt` does not try to
  start services inside the root.
- A `piroot` Unix user is created on the gateway whose login shell is a wrapper
  script that immediately `chroot`s into the NFS root, with a `sudoers.d` rule
  permitting that one binary, with any arguments.
- The inventory host named `pi` is `ansible_user=piroot` at the gateway's own
  address, with no port override — so Ansible reaches the chroot over the
  gateway's ordinary sshd on port 22, and every command it runs lands inside the
  ARM root.

The teardown role unmounts the four binds and removes the `policy-rc.d` stub.

:::{note}
The infra README, `site.yml` comments and the `nspawn-pi` role name all describe
this as `systemd-nspawn` running its own `sshd` on port 2200, and the role still
carries an unused `nspawn_sshd_port: 2200` default. No task starts a container or
an sshd. The description above is what the tasks do; the discrepancy is
corrected upstream in the stubbing phase of this port (Task 30).
:::

## Updating a running fleet

Re-running the playbook changes the NFS root. It does not change any running Pi.

:::{warning}
A running `overlayroot` Pi does **not** see changes made to the lower filesystem
underneath it. Package and configuration updates to the NFS root only take
effect after the Pi reboots (tweed rebuild, recorded 2026-08-26).
:::

Worse, converging under running Pis is actively harmful: files replaced in the
shared root leave the Pis holding stale NFS handles. On 2026-08-30 an upgrade of
`fpgas-online-cam` took the cameras off air on eleven boards with `ESTALE` on the
replaced files, and days later the Tiny Tapeout hosts still had `dpkg-query`
reporting a stale file handle. Only a reboot clears it. See
[Known faults](../sites/welland.md#known-faults) on the Welland page.

So the update procedure is: converge, then reboot every Pi. On a PoE fleet that
means a PoE cycle per port — see [Network](network.md) for the switch and PoE
control, and [Verification](verification.md) for checking the fleet came back.
Expect roughly two minutes per Pi from power-on to SSH.

## EEPROM write protect

The fleet Pis netboot from a read-only NFS root with a tmpfs overlay: everything
a user changes is reverted on reboot, and root access is deliberately available.
The bootloader EEPROM — the SPI flash holding the second-stage bootloader and its
config, `BOOT_ORDER`, `NET_INSTALL_*` and so on — is the **one piece of per-board
state that does not live in the NFS root and therefore does not revert**. Without
protection, a user with root can run `rpi-eeprom-update`, `rpi-eeprom-config` or
`flashrom` and leave a persistent change to how the board boots. It is the only
persistent-tampering surface on an otherwise ephemeral device, so it is locked.

The `fixpi` role adds `eeprom_write_protect=1` to the served `config.txt`. That
tells the bootloader to configure the SPI flash **Write Status Register** to
protect the entire device. Because `config.txt` comes from the read-only TFTP
root, it is re-applied on every boot.

From the official `config.txt` documentation:

> This option must be used in conjunction with the EEPROM `/WP` pin which
> controls updates to the EEPROM `Write Status Register`. Pulling `/WP` low
> (CM4 `EEPROM_nWP` or on a Raspberry Pi 4 `TP5`) does NOT write-protect the
> EEPROM unless the `Write Status Register` has also been configured.
>
> On Raspberry Pi 5 `/WP` is pulled low by default and consequently
> write-protect is enabled as soon as the `Write Status Register` is configured.
> To clear write-protect pull `/WP` high by connecting `TP14` and `TP1`.

Values: `1` = protect entire EEPROM, `0` = clear protection, `-1` = do nothing
(default).

### Per-model effectiveness

| Model | `/WP` default | Effect of `eeprom_write_protect=1` |
|-------|---------------|-------------------------------------|
| **Pi 5** (BCM2712) | pulled **low** by default | **Hardware-enforced immediately.** Even root cannot clear the Write Status Register or reflash without physically bridging `TP14`↔`TP1`. Tamper-resistant. |
| **Pi 4** (BCM2711) | `TP5`, **not asserted** by default | Blocks the standard tooling (`rpi-eeprom-update`, `rpi-eeprom-config --apply`) and accidental changes, but a determined root user could clear the Write Status Register. **Pull `TP5` low** to make it hardware-enforced. |

So on the Pi 5 the software setting alone is a real lock; on the Pi 4 it raises
the bar and, combined with grounding `TP5`, becomes a real lock too.

### Verify

On a running board, these should show the protected config and refuse to write:

```console
$ vcgencmd bootloader_config
$ sudo rpi-eeprom-update
$ sudo rpi-eeprom-update -a
```

`rpi-eeprom-update` reports the current state; `-a` fails to write the flash on
a protected board. The build is checked in CI too: `verify-server.yml` asserts
the built NFS-root `config.txt` contains `eeprom_write_protect=1`.

### Legitimately updating an EEPROM later

Because protection is re-applied from the read-only image every boot, you cannot
just clear it on the board. To update a board's bootloader EEPROM:

1. On the gateway, temporarily set `eeprom_write_protect=0` (or `-1`) in the
   served `config.txt` — either fleet-wide in `fixpi` or for one board via a
   per-board boot config — and rebuild and deploy.
2. Reboot the target board so it boots with protection cleared. On a Pi 4 with
   `TP5` grounded, or on any Pi 5, you must additionally undo the hardware
   assertion (Pi 5: bridge `TP14` to `TP1`) before the flash will accept writes.
3. Run `sudo rpi-eeprom-update -a` (or `rpi-eeprom-config --apply`), reboot,
   confirm.
4. Restore `eeprom_write_protect=1` in the served `config.txt`, redeploy, reboot.

A change here takes effect when a board next netboots the rebuilt image. Confirm
on one board before relying on it fleet-wide.

## When a Pi does not boot

A netbooted Pi has no console and no disk to inspect, so the roles build four
ways to watch one boot. Full procedures belong on
[Verification](verification.md) and [Pi hosts](pi.md); this is what exists and
where it comes from. The Allwinner hosts take the same DHCP, TFTP root and NFS
root, so the lease check below applies to them unchanged; the netconsole and
gateway-serial methods do not, because their command line carries no
`netconsole=` and no UART of theirs is wired to the gateway. Their console is
the USB gadget log captured on their hub host — see
[Orange Pi H3 hosts](orange-pi.md).

**Did it get a lease?** dnsmasq runs with `log-dhcp`, so every DHCP transaction
is journalled on the gateway, and the lease database is pinned to the absolute
path `/var/lib/misc/dnsmasq.leases`. The absolute path is deliberate: dnsmasq
daemonises and `chdir()`s to `/` before opening a relative lease, pid or log
path, and silently fails if one is given relative.

**Kernel log over the network.** Both command lines carry
`netconsole=@/,@10.21.0.1/`, which points the kernel log at the gateway over
UDP.

:::{note}
The tweed rebuild log records this both ways within one night: entry C1-3 calls
netconsole's dynamic cmdline form "a dead cmdline feature" that never transmits,
and C1-3b then reports netconsole working on the next boot. Treat it as worth
trying, not as a guarantee — the same log's fallback was to plant a unit in the
NFS root that streams the journal early.
:::

**Serial from the gateway.** `tweeks.yml` sets the gateway up as the watching
station: it installs `tio`, adds the operator account to the `dialout` group so
`tio` can open the tty, masks `serial-getty@ttyAMA0` so a getty does not eat the
boot messages, and removes `brltty`, which grabs serial ports greedily and makes
`ftdi_sio` lose the connection ([Debian #667616](https://bugs.debian.org/667616)).
When the gateway is itself a Pi, it also adds `dtoverlay=disable-bt` to the
gateway's own `/boot/firmware/config.txt` to free `/dev/serial0`.

**USB-C gadget console.** `tweeks.yml` puts the Pi 4 and Pi 5 USB-C port into
peripheral mode with `dtoverlay=dwc2,dr_mode=peripheral`, so a laptop plugged
into that port gets the kernel log and a getty. Only those two models: their
USB-A ports hang off separate controllers (VL805 on the Pi 4, RP1 on the Pi 5),
so nothing is lost, whereas on a Pi 3 or a Zero `dwc2` is the only USB
controller there is — on a 3B+ that includes the Ethernet. Fleet nodes are
PoE-powered, so their USB-C port is free.

## Historical tooling

Before the Ansible roles, the netboot root was built and switched by hand from
two repositories:
[fpgas.online-netboot-pi](https://github.com/fpgas-online/fpgas.online-netboot-pi)
(image extraction, NFS root preparation, the QEMU/chroot wrapper, TFTP
serial-number symlinks, and maintenance/production mode switching) and
[fpgas.online-tools](https://github.com/fpgas-online/fpgas.online-tools) (DHCP
log analysis and a netconsole client for capturing Pi boot spew). The infra repo
now vendors netboot-pi's scripts — `img2files.sh` in the `img` role,
`maintenance.sh`, `production.sh` and the chroot helper in `fixpi` — so those
repositories are history, not the running system.

:::{warning}
Do not read `fpgas.online-netboot-pi`'s `pinet/` directory as documentation of
what the fleet boots. Those files are a **trixie** root with `overlayroot=`
empty and both NFS mounts read-write — that is maintenance mode, the state
`maintenance.sh` puts the fleet into so a single Pi can apt-install into the
shared root. The fleet boots a **bookworm** root with `overlayroot=tmpfs` and
both mounts read-only.
:::

## Sources

fpgas.online-infra, `main`:

- [`README.md`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/README.md)
  — architecture overview, PXE boot chain, package table.
- [`ansible/site.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/site.yml)
  — role order, the nspawn start/stop wrapper around the `pi` play.
- [`ansible/inventory/hosts`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/inventory/hosts)
  — the `pi` host as `piroot` at the gateway address, no port override.
- [`ansible/inventory/group_vars/all/srv.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/inventory/group_vars/all/srv.yml)
  — pinned image name and date, `dist`, `nfs_root`, the `tftp_root` expression.
- [`ansible/inventory/host_vars/ps1.fpgas.online.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/inventory/host_vars/ps1.fpgas.online.yml)
  — PS1 does not override `dist`; the `switch.nos` list and the shape of its
  entries.
- [`ansible/roles/pxe/templates/dnsmasq-base.conf.j2`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/pxe/templates/dnsmasq-base.conf.j2)
  — DHCP/TFTP on the internal NIC, `bind-dynamic`, `log-dhcp`, the pinned
  absolute `dhcp-leasefile` path, the NTP option.
- [`ansible/roles/nfs/templates/exports.j2`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/nfs/templates/exports.j2)
  — both exports read-only.
- [`ansible/roles/img/tasks/main.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/img/tasks/main.yml)
  and [`ansible/roles/img/files/img2files.sh`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/img/files/img2files.sh)
  — image download and extraction into `boot/` and `root/`.
- [`ansible/roles/fixpi/tasks/main.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/fixpi/tasks/main.yml)
  — the task-file order within `fixpi`.
- [`ansible/roles/fixpi/tasks/manage.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/fixpi/tasks/manage.yml)
  — `qemu-user-static`, and the vendored `maintenance.sh` / `production.sh` /
  `chroot-mount-pi-fs.bash`.
- [`ansible/roles/fixpi/tasks/netboot.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/fixpi/tasks/netboot.yml)
  — TFTP symlinks, cmdline and fstab templating, the `pi` user and its sudo
  drop-in, `nfs-common` and `overlayroot`, the firmware-payload sync, ssh
  enablement, the masked wizard, pre-generated host keys.
- [`ansible/roles/fixpi/tasks/tweeks.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/fixpi/tasks/tweeks.yml)
  — `config.txt` edits: onboard Wi-Fi and Bluetooth off and the Pi 5 overlay
  remapping (lines 70-86), `eeprom_write_protect=1`, the `[pi5]` header-UART and
  `cmdline=` stanza, the Pi 4 / Pi 5 USB gadget console (lines 145-161), and the
  gateway-side serial watch: `brltty` removed, `tio` installed, operator in
  `dialout`, `serial-getty@ttyAMA0` masked (lines 176-218).
- [`ansible/roles/fixpi/tasks/nogrow.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/fixpi/tasks/nogrow.yml)
  — root-resize and swap machinery disabled.
- [`ansible/roles/fixpi/templates/boot/cmdline.txt.j2`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/fixpi/templates/boot/cmdline.txt.j2)
  and [`cmdline-pi5.txt.j2`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/fixpi/templates/boot/cmdline-pi5.txt.j2)
  — the kernel command lines.
- [`ansible/roles/fixpi/templates/etc/fstab.j2`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/fixpi/templates/etc/fstab.j2)
  — `/` and `/boot/firmware` as `noauto,ro` NFS v3 mounts.
- [`ansible/roles/fixpi/files/scripts/chroot-mount-pi-fs.bash`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/fixpi/files/scripts/chroot-mount-pi-fs.bash)
  — the private-mount-namespace chroot helper.
- [`ansible/roles/nspawn-pi/tasks/start.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/nspawn-pi/tasks/start.yml),
  [`stop.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/nspawn-pi/tasks/stop.yml)
  and [`defaults/main.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/nspawn-pi/defaults/main.yml)
  — the `piroot` chroot-shell provisioning host, and the unused port default.
- [`docs/superpowers/runbooks/2026-08-31-eeprom-write-protect.md`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/docs/superpowers/runbooks/2026-08-31-eeprom-write-protect.md)
  — the EEPROM write-protect section above.
- [`docs/rebuilds/2026-08-25-tweed-rebuild.md`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/docs/rebuilds/2026-08-25-tweed-rebuild.md)
  — kernel/initramfs mismatch (C1-3), `nfsvers=3,tcp` (C1-3c), the host devpts
  unmount (B1-10), Pi clocks with no LAN NTP (C2-2), and the lesson that a
  running overlayroot Pi does not see lower-filesystem changes, and the two
  conflicting readings of netconsole (C1-3 versus C1-3b).

fpgas.online-test-designs, `main`:

- [`docs/verify-hardware.md`](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/verify-hardware.md)
  — PoE reset, the two-minute PXE boot, and re-uploading everything because the
  tmpfs is empty after a reboot.

Other repositories:

- [fpgas.online-netboot-pi](https://github.com/fpgas-online/fpgas.online-netboot-pi)
  — `README.md` for the predecessor scripts, `pinet/cmdline.txt` and
  `pinet/fstab` for the maintenance-mode configuration, `scripts/maintenance.sh`
  and `scripts/production.sh` for the mode switch.
- [fpgas.online-tools](https://github.com/fpgas-online/fpgas.online-tools)
  — `README.md` for the DHCP and netconsole utilities.

Pages on this site: [Welland](../sites/welland.md#gateway-tweed) (tweed on
trixie, Pi 5 console, stale NFS handles),
[PS1](../sites/ps1.md#gateway-val2) (val2 on bookworm, the two roots) and
[Compute blades](../sites/ps1.md#compute-blades) (`console=tty1` on the trixie
root), [Packages](../packages.md).
