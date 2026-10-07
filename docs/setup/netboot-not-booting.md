# When a Pi does not boot

**A fleet Pi does not come back after a power cycle or an update, and you want to find where its boot
stops.** You need a login on the site's gateway. A netbooted Pi has no disk to look at; these are the ways to
watch one boot, in the order to try them. The Orange Pis boot the same root by another route: [Orange Pi H3
hosts](orange-pi.md).

## 1. Did it get an address?

dnsmasq logs every DHCP exchange (`log-dhcp`) to the gateway's journal, and its lease file is
`/var/lib/misc/dnsmasq.leases` (`roles/pxe/templates/dnsmasq-base.conf.j2`, fpgas.online-infra main). On the
gateway, for the Pi on welland's switch 2, port 46:

```console
$ sudo journalctl -u dnsmasq --since -15min | grep -i dhcp | grep 10.21.2.46
$ ip -4 neigh show 10.21.2.46
```

No DHCP at all from the port: the Pi has no power or no link (read the port's PoE state, [Power-cycling a
board](network-power-cycle.md)), or the port is not in its VLAN ([Converging the switches](network-switches.md)).

## 2. Did it fetch its files?

The TFTP log is in the same journal: each file sent, and each file not found.

```console
$ sudo journalctl -u dnsmasq --since -15min | grep -i tftp | grep 10.21.2.46
```

A Pi 4 or 5 asks for `<serial>/start4.elf` and then, finding nothing, the same names without the prefix
([Where TFTP serves from](netboot.md#where-tftp-serves-from)); those "not found" lines are normal. A Pi 5 also
asks for `kernel_2712.img` and falls back to `kernel8.img`. The same files fetched again every two minutes or
so means the Pi is rebooting in a loop: the kernel starts and something later fails. That was seen at ps1 on
5 October 2026 ([The ps1 gateway and switch](../sites/ps1-gateway.md)).

## 3. The kernel's own log, over the network

The kernel command line carries `netconsole=@/,@10.21.0.1/`, which sends the kernel log to the gateway over
UDP ([The kernel command line](netboot.md#the-kernel-command-line)). Listen on the gateway (port 6666 is
netconsole's default) while the Pi boots:

```console
$ nc -u -l 6666
```

The gateway's rebuild log of 2026-08-25 records this both failing and working within one night: try it, do
not rely on it.

## 4. A console on the Pi's USB-C port (Pi 4 and Pi 5)

The served `config.txt` puts a Pi 4's or Pi 5's USB-C port in gadget mode (`dtoverlay=dwc2,dr_mode=peripheral`,
`roles/fixpi/tasks/tweeks.yml`), so a laptop plugged into that port gets a serial console from the Pi, as
`/dev/ttyACM0` on the laptop. The fleet Pis take their power over PoE, so that port is free. Not on a Pi 3 or
a Zero: there the gadget controller is the only USB controller.

## 5. Stale files after an update

A Pi that is up but fails new logins or commands with `Stale file handle` booted the root before it was
replaced ([The NFS root is shared and read-only](netboot.md#the-nfs-root-is-shared-and-read-only)). Its
watchdog reboots it on its own; power-cycle it to have it back sooner.
