# Netboot and the NFS root

**You want to know how a fleet Pi gets its kernel and its root filesystem from the gateway, so that you can
reason about a boot problem or a change to the root.** To put a new root on a gateway, or to find out why a Pi
does not boot, go to the pages listed under [The tasks](#the-tasks).

A fleet Pi has no SD card and no local storage. Its boot ROM asks for DHCP, fetches its firmware and kernel
over TFTP, and mounts one shared, read-only NFS root from the site's gateway, with a tmpfs on top that is
thrown away at every reboot. This page describes what fpgas.online-infra builds (main, read 2026-10-07). ps1's
gateway was not built by it as it stands: [The ps1 gateway and switch](../sites/ps1-gateway.md) has what was
read there.

## The tasks

(updating-a-running-fleet)=
- [Updating the NFS root](netboot-update-root.md): a new root on a gateway, and every Pi on it.

(how-the-root-is-built)=
- [How the root is built](netboot-update-root.md#how-the-root-is-built): CI builds it, the gateway pulls it.

(the-provisioning-container)=
- [The provisioning container](netboot-update-root.md#how-the-root-is-built): the same.

(when-a-pi-does-not-boot)=
- [When a Pi does not boot](netboot-not-booting.md).

(eeprom-write-protect)=
- The bootloader EEPROM lock that `config.txt` sets: [on a Raspberry Pi 5](bootloader-eeprom-pi5.md), [on a
  Compute Module](bootloader-eeprom-compute-module.md), [what was measured](bootloader-eeprom.md).

```{toctree}
:hidden:

Updating the NFS root <netboot-update-root>
When a Pi does not boot <netboot-not-booting>
```

## The boot chain

1. The Pi powers on and its boot ROM broadcasts DHCP.
2. dnsmasq on the gateway answers with an address and the gateway as TFTP server. It binds with
   `bind-dynamic`, because at welland there are about 150 per-port interfaces and most have no carrier until
   a Pi is plugged in (`roles/pxe/templates/dnsmasq-base.conf.j2`).
3. The Pi fetches its firmware, `config.txt`, `cmdline.txt`, the kernel, the device tree and the initramfs over
   TFTP.
4. The kernel mounts the NFS root read-only and puts a tmpfs over it (`overlayroot=tmpfs`).
5. Everything the Pi runs is already in that root; nothing is installed at boot.

dnsmasq also names the gateway as the NTP server: the Pis have no route to the internet, and without it their
clocks stay on the `fake-hwclock` date (found at the welland gateway's rebuild of 2026-08-25).

## Where TFTP serves from

`tftp_root` in `inventory/group_vars/all/srv.yml`:

```jinja
tftp_root: "{{ (nfs_root ~ '/boot') if switches is defined else '/srv/tftp' }}"
```

At welland (`switches` defined) dnsmasq serves the root's own `boot/` directly. A Pi 4 or 5 asks for
`<serial>/<file>` first and, when that is not there, asks again without the prefix, so no Pi is registered by
serial number: plug it into its port and it boots.

On a MAC-table gateway, `/srv/tftp` holds one link per Pi serial number pointing at the root's `boot/`
(`roles/fixpi/tasks/netboot.yml`); adding a Pi means adding its entry to `switch.nos` in the gateway's
`host_vars` and converging, so its link is made.

## The kernel command line

`roles/fixpi/templates/boot/cmdline.txt.j2`, as served to every Pi but a Pi 5:

```text
root=/dev/nfs nfsroot=10.21.0.1:{{ nfs_root }}/root,nfsvers=3,tcp ro ip=dhcp rootwait consoleblank=0 netconsole=@/,@10.21.0.1/ overlayroot=tmpfs console=tty1 systemd.log_level=debug systemd.log_target=kmsg log_buf_len=1M printk.devkmsg=on
```

`nfsvers=3,tcp`
: welland's gateway runs Debian 13, whose NFS server serves version 3 over TCP only, while the initramfs's
  mount tool defaults to UDP; without it the mount hangs in the initramfs (found on real hardware at the
  rebuild of 2026-08-25; the CI VM did not show it).

`overlayroot=tmpfs`
: the writable layer ([below](#the-nfs-root-is-shared-and-read-only)).

`console=tty1`
: the kernel console is on the screen, not on a serial port. On a Pi 3B+ the serial pins are the ones a NeTV2's
  FPGA drives, and bytes from it must not reach a console; the root also sets `kernel.sysrq = 0`
  (`roles/fixpi/tasks/netboot.yml`).

A Pi 5 boots `cmdline-pi5.txt` instead: the same line with `console=ttyAMA10,115200`, the Pi 5's own debug UART.
`roles/fixpi/tasks/tweeks.yml` adds to the served `config.txt`:

```text
[pi5]
dtoverlay=uart0-pi5
cmdline=cmdline-pi5.txt
```

so the 40-pin header UART (`/dev/ttyAMA0`, wired to the FPGA on an Acorn host) is enabled and free of the
console. The same file adds `dtoverlay=disable-wifi`, `dtoverlay=disable-bt`, `enable_uart=1`,
`uart_2ndstage=1` and `eeprom_write_protect=1`, and puts the Pi 4's and Pi 5's USB-C port in gadget mode
([When a Pi does not boot](netboot-not-booting.md)). `config.txt` is served read-only, so these apply at every
boot.

## The NFS root is shared and read-only

There is one root per site, at `/srv/nfs/rpi/<dist>/{boot,root}` (`nfs_root`; `dist: bookworm`). Both halves
are exported read-only to the Pi network, and the Pi's own `/etc/fstab` mounts `/` and `/boot/firmware`
read-only and `noauto`. Every Pi mounts the same root.

:::{warning}
The writable layer is a tmpfs. Everything written on a Pi is gone at the next reboot or power cycle,
including anything copied to `/home/pi`. A bitstream that loaded a minute ago fails to open after a reboot
because the file is not there any more: openFPGALoader prints `Open file … FAIL`. Copy it again.
:::

Test automation that power-cycles a Pi (fpgas.online-test-designs' hardware tests) uploads its files again
afterwards for the same reason.

A Pi that booted before the root was replaced keeps file handles into the old files: every replaced file
answers `Stale file handle` (`ESTALE`). That broke `dpkg-query`, and, since `authorized_keys` was among the
replaced files, key-based SSH, on every board at once (measured on `pi-sw2-p33` at welland on 2026-09-24;
`roles/nfsroot_generation/README.md`). A Pi has to reboot to use a new root: [Updating the NFS
root](netboot-update-root.md) is how that happens.
