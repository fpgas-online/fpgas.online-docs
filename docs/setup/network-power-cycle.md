# Power-cycling a board

**You want to power-cycle one board's Pi, at welland or at ps1: it has hung, or it must boot a new NFS root.**
Cutting the Pi's PoE on its switch port is the only remote reset; there is no other power control. The Pi
loses everything it held (its root is read-only with a tmpfs on top, [Netboot and the NFS root](netboot.md)),
and anyone using the board loses their session. Visitors use the boards at any time; that is expected, so cut
a port only when it is needed.

## Before you cut a port

A port is a place, not a board. Make sure the board you mean is the one on the port:

1. Find the port. At welland the port is in the Pi's name (`pi-sw2-p46` is switch 2, port 46); at ps1 it is
   the Pi's number (`pi20` is port `e20`).
2. Check who is on it, on the gateway. A netbooted Pi never renews its DHCP lease, so 12 hours after it boots
   its lease is gone while it runs on (fpgas.online-infra issue #230). Look at the gateway's neighbour table
   as well as the leases:

   ```console
   $ grep ' 10.21.2.46 ' /var/lib/misc/dnsmasq.leases
   $ ip -4 neigh show 10.21.2.46
   ```

   The MAC in either must be the MAC of the Pi you mean (the board pages and the site pages,
   [Welland](../sites/welland.md) and [Hosts and boards at ps1](../sites/ps1-boards.md), list them). If
   another MAC answers, stop: something was moved.

## At welland

**From the board's page.** A board page on welland.fpgas.online that has a Reset button power-cycles its
port: off, half a second, on (`src/snmp_switch/views.py` in fpgas.online-poe, main fcb4a2a). It refuses a port
that is not a board the site offers, and a second cycle of the same port within 60 seconds by default
(fpgas.online-poe `README.md`). It was deployed to the welland gateway on 2026-09-14 (fpgas.online-infra PR
#84) and checked then on one board. The NeTV2 hosts have no board page.

**From the gateway**, as root, with the switch's SNMP write community. Both welland switches answer the
standard PoE MIB (`pethPsePortAdminEnable`, `1.3.6.1.2.1.105.1.1.1.3.1.<port>`) over SNMP v2c. The
communities are in the vault of fpgas.online-infra and are rendered, root-only, into
`/etc/systemd/system/gunicorn.service.d/poe.conf` as `FPGAS_SWITCH_COMMUNITY_<switch>` (the `site` role,
`templates/gunicorn-poe.conf.j2`). Never copy one into a file, a commit or a page.

| Switch | Management address | Carries |
|---|---|---|
| 1, Netgear GSM7252PS | 10.1.5.23 | the NeTV2 hosts and the Fomu host |
| 2, Netgear S3300-52X-PoE+ | 10.1.5.11 | the Tiny Tapeout and Acorn hosts |

```console
$ # the switch, its write community (read it from poe.conf; it is not printed here), and the port
$ export SW=10.1.5.23 COMMUNITY='<switch-write-community>' PORT=14
$ OID=1.3.6.1.2.1.105.1.1.1.3.1.$PORT
$ # read: admin state (1 on, 2 off) and delivery (3 = delivering power)
$ snmpget -v2c -c "$COMMUNITY" -Ovq $SW $OID 1.3.6.1.2.1.105.1.1.1.6.1.$PORT
$ # power-cycle: off, wait, on
$ snmpset -v2c -c "$COMMUNITY" $SW $OID i 2 && sleep 6 && snmpset -v2c -c "$COMMUNITY" $SW $OID i 1
```

The port number is the switch port (`p` in the Pi's name), not a VLAN or an address. This command was checked
on 2026-09-06 by cycling the five NeTV2 ports on switch 1; all five came back within about 48 seconds. The
same MIB is what the fpgas.online coordinator used through fpgas.online-poe's `netgear_switch` library to
cycle 12 welland boards after the NFS root updates of 5 and 6 October 2026.

`poe.sh` and `allpoe.sh` from fpgas.online-poe do not work at welland: the `snmp.yml` task that writes their
settings is skipped on a per-port gateway, by design (its comment in fpgas.online-infra, main).

## At ps1

```{include} ../sites/ps1-power-cycle.inc
```

## How long the board is gone

The Pi netboots again: a kernel and a root over the network, not a resume from disk.

| Pi | Back after | Measured |
|---|---|---|
| Pi 3B+ (NeTV2 hosts, welland) | about 48 s | 2026-09-06, five ports |
| Pi 5 (Acorn hosts, welland) | more than 90 s | [Acorns at welland](../boards/acorn/installations/welland.md#reads-of-september-2026) |
| Compute Blade (ps1) | about 60 s | the ps1 site notes |

About two minutes from power-on to SSH is the figure the test automation uses (`docs/verify-hardware.md` in
fpgas.online-test-designs). At welland a hung Pi 5 shows on its port as about 0.4 W instead of about 8 W
([Acorns at welland](../boards/acorn/installations/welland.md#reads-of-september-2026)).

## After an NFS root update

A Pi that booted before the root was replaced fails to open the new files (`ESTALE`); [Netboot and the NFS
root](netboot.md) says why. Each Pi's watchdog reboots it on its own once it sees a newer root: after the
updates of 5 and 6 October 2026 at welland, the Orange Pis, which were left to it, were back 31 to 33 minutes
after the swap. To have a board back sooner, power-cycle its port as above; on 6 October 2026 twelve
power-cycled boards were all back within 9 minutes.
