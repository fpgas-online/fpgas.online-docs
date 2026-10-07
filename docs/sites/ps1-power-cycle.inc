**First, check who is on the port.** The port is the host's number (pi20 at ps1 is on port `e20`). On the
ps1 gateway, the address `10.21.0.1NN` must be answered by that host's MAC (listed on Hosts and boards at ps1):

```console
$ grep ' 10.21.0.120 ' /var/lib/misc/dnsmasq.leases
$ ip -4 neigh show 10.21.0.120
```

A netbooted Pi does not renew its lease, so an empty lease file line does not mean the Pi is off; the
neighbour entry is the better sign. Someone may be using the board: a visitor's session ends with the power.

**From the board's page.** Each Arty host's page on ps1.fpgas.online has "Turn it off and on again: Reset" and
a "Check PoE" button (read on `https://ps1.fpgas.online/fpgas/pi3.html` on 7 October 2026). The Compute
Blades have no page there.

**Not yet run by fpgas.online since the gateway was reinstalled** (about 25 September 2026). The gateway read
of 6 October 2026 found `snmp_switch` 0.0.17 in that venv. It did not open `/etc/environment.export`, because
the file holds credentials, and no role in fpgas.online-infra writes that file name. So whether the file came
back with the reinstall is not known. If the settings file is not there, the switch settings are missing and the gateway's
administrator has to put them back.

**From the gateway, as root.** fpgas.online-poe's `scripts/poe.sh` (main, fcb4a2a) is the tool written for
this switch: `poe.sh PORT` reads the port's state, `poe.sh PORT 2` switches it off and `poe.sh PORT 1` on. It
reads the switch's SNMP settings from `/etc/environment.export` and runs `snmp_switch/utils.py` from the web
venv, `/srv/www/pib/venv`. Check the settings file first, then cycle in one line, so that a dropped
connection cannot leave the host off (port 20 here):

```console
$ test -r /etc/environment.export && echo settings present
$ poe.sh 20                                   # read: 1 is on, 2 is off
$ poe.sh 20 2 && sleep 6 && poe.sh 20 1       # off, wait, on
$ poe.sh 20                                   # read again: expect 1
```

If `poe.sh` is not on the gateway, each `poe.sh 20 N` is these two lines from the script:

```console
$ source /etc/environment.export
$ /srv/www/pib/venv/bin/python3 /srv/www/pib/venv/lib/python3.13/site-packages/snmp_switch/utils.py 20 N
```

The host is back when the gateway's neighbour entry for its address answers again
(`ip -4 neigh show 10.21.0.120`) and its SSH port answers. Do not cycle pi19 (dead hardware, site notes) or
pi24 (on no port).

The switch, a Netgear FS728TPv2, takes PoE commands only on a Netgear-private OID (site notes)
`1.3.6.1.4.1.4526.11.16.1.1.1.3.1`, which is the `oid` in `host_vars/ps1.fpgas.online.yml` (fpgas.online-infra). How long a host takes to come back after a power cycle has not been measured at ps1;
the test automation allows about two minutes from power-on to SSH (`docs/verify-hardware.md` in
fpgas.online-test-designs).
