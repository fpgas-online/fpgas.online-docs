**First, check who is on the port.** The port is the host's number: the switch names its ports `e1` to `e24`
(site notes), and pi20 at ps1 is on port `e20`. On the ps1 gateway, the address `10.21.0.1NN` must be answered
by that host's MAC (listed on Hosts and boards at ps1):

```console
$ grep ' 10.21.0.120 ' /var/lib/misc/dnsmasq.leases
$ ip -4 neigh show 10.21.0.120
```

A netbooted Pi may hold no lease while it runs (a lease is not renewed; fpgas.online-infra issue #230), so a
missing lease line does not mean the Pi is off. The neighbour entry names the MAC that last answered at the
address; it can stay for a while after the Pi has gone, so it identifies the board but does not prove it is
up. Someone may be using the board: a visitor's session ends with the power. Do not cycle pi19 (dead
hardware, site notes) or pi24 (on no port, site notes).

**From the board's page.** The board pages on ps1.fpgas.online have "Turn it off and on again: Reset" and a
"Check PoE" button (read on `https://ps1.fpgas.online/fpgas/pi3.html` on 7 October 2026). The Compute Blades
have no page there.

**This is Carl's tooling on his gateway, not run by fpgas.online.** The gateway's files date from about
25 September 2026, when it was installed again. The gateway read of 6 October 2026 found `snmp_switch` 0.0.17
in the web venv, `/srv/www/pib/venv`. A read on 7 October 2026 (00:30 Chicago time) found
`/usr/local/bin/poe.sh`: fpgas.online-poe's script, with the same switch notes in its header, sourcing
`/etc/environment.export` and running `snmp_switch/utils.py` from that venv. Neither read opened the settings
file, because it holds credentials, and neither ran a power cycle. No role in fpgas.online-infra writes that name:
its `snmp.yml` writes `/etc/environment.exports`, plural, and only on a gateway it deploys. If the settings
file is not there, the switch settings are missing and the gateway's administrator has to put them back.

**From the gateway, as root.** fpgas.online-poe's `scripts/poe.sh` (main, fcb4a2a) is the tool for this
switch: `poe.sh PORT` reads the port's state, `poe.sh PORT 2` switches it off and `poe.sh PORT 1` on. It reads
the switch's SNMP settings from `/etc/environment.export` and runs `snmp_switch/utils.py` from the web venv.
Check the settings file first, then cycle in one line, so that a dropped connection cannot leave the host off
(port 20 here):

```console
$ test -r /etc/environment.export && echo settings present
$ poe.sh 20                                   # read: 1 is on, 2 is off
$ poe.sh 20 2 && sleep 5 && poe.sh 20 1       # off, a few seconds, on
$ poe.sh 20                                   # read again: expect 1
```

If `poe.sh` is not on the gateway, each `poe.sh 20 N` is these two lines from the script:

```console
$ source /etc/environment.export
$ /srv/www/pib/venv/bin/python3 /srv/www/pib/venv/lib/python3.13/site-packages/snmp_switch/utils.py 20 N
```

The host is back when its SSH port answers: from the gateway, `nc -z -w 3 10.21.0.120 22`; from outside, the
visitor login on port `12022`. How long that takes after a power cycle has not been measured at ps1; the test
automation allows about two minutes from power-on to SSH (`docs/verify-hardware.md` in
fpgas.online-test-designs).

`poe.sh PORT` takes no switch argument: it acts on the one switch its settings name. That ps1 has one PoE
switch, a Netgear FS728TPv2 carrying every host, is the site notes' reading and matches the OID and MAC in
`host_vars/ps1.fpgas.online.yml` (fpgas.online-infra); that file's comments also name an HP ProCurve 2610 and a
Netgear GS728TPP, and nobody from fpgas.online has looked at the rack, so this is not settled. The FS728TPv2 takes PoE commands only on a Netgear-private OID, `1.3.6.1.4.1.4526.11.16.1.1.1.3.1`
(site notes; the `oid` in `host_vars`).
