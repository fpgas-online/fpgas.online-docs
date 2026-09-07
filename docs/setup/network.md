# Network and power

Every Raspberry Pi in the fleet sits behind its site's gateway on a private
`10.21.x.x` network, but the two sites lay that network out differently: PS1 is
one flat `/24` with every Pi on it, while Welland spreads a `/16` across one
VLAN per switch port, so each Pi has a segment to itself with the gateway as
the only thing on the local network it can reach. Which scheme a host uses is
decided by a single inventory variable. Power is PoE from the same managed
switches that carry the network, so "reboot the board" and "cut its Ethernet
power" are the same operation.

## Two addressing schemes

Welland has run **VLAN-per-port** since **2026-08-23**. PS1 still runs the
**legacy MAC table**: a Pi is recognised by its MAC and handed a reserved
address, and its identity travels with the board rather than with the socket.

The switch is a single inventory variable. A host that defines `switches:` in
its `host_vars` gets the per-port scheme; a host that does not falls through to
the legacy path. That one `is defined` test decides the `tftp_root` expression
in `group_vars/all/srv.yml`, picks which half of the `firewall` role's nftables
template is rendered, and gates the `vlan-ports` and `switch-vlans` roles in
`site.yml` — without it neither role runs at all.

The only production host that defines `switches:` is `fpgas.online`, the
Welland gateway [tweed](../sites/welland.md#gateway-tweed); `ps1.fpgas.online`
and `slf.sytes.net` do not. The QEMU CI VM defines one switch of a single
access port with `switches_manage: false`, so every role runs and the address
derivation is exercised against an emulated switch, with only the SNMP converge
step skipped for want of real hardware.

:::{note}
dnsmasq's own coupling to this is indirect. `dnsmasq-base.conf.j2` tests
`dhcp_range is defined`, not `switches` — it emits a flat pool if the host has
one and nothing if it does not. The two line up only because a per-port host's
`host_vars` deliberately omits `dhcp_range`, with a comment saying why, so that
every port gets its own range from `ports.conf.j2` instead.
:::

For switch index `s` and port `p`, and for legacy port `N`:

| Item | Per-port (Welland) | Legacy MAC table (PS1) |
|---|---|---|
| Selected by | the switch port the cable is in | the Pi MAC, listed against a port in `switch.nos` |
| VLAN ID | `2000 + 100*s + p` | none — one flat network |
| IPv4 | `10.21.s.p` | `10.21.0.<100+N>` |
| IPv6 | `2404:e80:a137:210s::p` | none |
| Hostname | `pi-sw<s>-p<p>` | `pi<N>` |
| Gateway interface | `v<VLAN>` | `eth-local` |
| SSH DNAT port | `<s><pp>22` | `<100+N>22` |
| Aux DNAT port (to 4444) | `<s><pp>44` | `<100+N>44` |
| Example | sw1 p7 → VLAN 2107, 10.21.1.7, `2404:e80:a137:2101::7`, `pi-sw1-p7`, `v2107`, 10722 | port 7 → `pi7`, 10.21.0.107, 10722 |

Read a VLAN ID straight: the hundreds digit is the switch number, which is also
the IPv4 third octet and the IPv6 subnet digit; the last two digits are the port
number, which is also the IPv4 last octet and the IPv6 interface ID. The gateway
stays `10.21.0.1` under both schemes, and the subnet stays `10.21.0.0/16`, so
NFS root paths, the `nfsroot=` kernel command line and the firewall's notion of
"internal" did not move at the cutover.

:::{note}
The DNAT formulas agree numerically for switch 1: legacy port 7 and sw1 p7 both
produce 10722, because `<100+N>` and `<s><pp>` are the same five digits when
`s` is 1. The two sites are separate hosts with separate uplink addresses, so
nothing collides — it is arithmetic, not a design guarantee, and it stops
holding at switch 2.
:::

The per-port formulas live in exactly one place on the Ansible side, the
`port_vlan_map` filter, and every VLAN interface, dnsmasq stanza, DNAT rule and
hostname is derived from the `switches:` list by running it. There is no other
per-device state — no MAC tables, and `ports.conf.j2` says so in its own header
comment: *no MAC addresses appear anywhere in this file by design*. The address
derivation is duplicated deliberately in one other component, the gateway
service in
[fpgas.online-gw](https://github.com/fpgas-online/fpgas.online-gw), which owns
the slug → address mapping for both schemes so the web tier never has to know
either.

:::{warning}
The design spec and the deployed inventory disagree about which switch is which
index, and the prototype runbook follows the spec.

- **The spec** (2026-08-14) numbers the S3300 as switch 1 at 10.1.5.11 and the
  GSM7252PS as switch 2 at 10.1.5.23, and calls the GSM7252PS the prototype
  unit.
- **The deployed `host_vars` and the [Welland page](../sites/welland.md#network)**
  number the GSM7252PS as switch 1 at 10.1.5.23 — it is the head switch,
  because tweed's `eth-local` trunks into it — and the S3300 as switch 2 at
  10.1.5.11.

The deployed numbering is the one that is live and the one every hostname and
address on this site is built from. Read the runbook's "switch 1 / 10.1.5.11"
as the S3300 and translate.

The trunk ports differ the same way. The spec reserves ports 49–52 for trunks
and sketches `gateway_trunk_port: 49`; the real cabling, confirmed from the
switches' own LLDP on 2026-08-22, is tweed `eth-local` into GSM 1/0/47 and GSM
1/0/50 into S3300 1/xg51. The spec's `access_ports: 48` on both switches is
also not what shipped: switch 1 carries 40 access ports, switch 2 carries 48.
:::

:::{todo}
Nobody has corrected the losing copy. The VLAN-per-port design spec
(2026-08-14) still numbers the S3300 as switch 1 and the GSM7252PS as switch 2,
still says trunk 49 with `access_ports: 48` on both, and the prototype runbook
still follows it — while the deployed `host_vars`, the LLDP survey of
2026-08-22 and the [Welland page](../sites/welland.md#network) say the
opposite. Update the spec and the runbook in `fpgas.online-infra`, or mark them
superseded.
:::

## Why per-port

The isolation goal is stated first in the design spec and everything else
follows from it: *a device on one switch port can exchange traffic only with the
gateway; devices on different ports cannot talk to each other directly through
the switch*. A Pi-facing port is an untagged access port whose PVID is its own
VLAN, and it is a member of that VLAN **only** — explicitly removed from VLAN 1,
so VLAN-1 membership cleanly means "unconfigured". Every per-port VLAN reaches
tweed tagged over the trunk, and there it meets nftables, where the `forward`
chain's policy is `drop` and `v*` to `v*` is deliberately left to fall through
to it. IPv4 hairpins through the gateway because tweed answers proxy ARP for the
whole `/16`; IPv6 hairpins because the RAs advertise a router with no on-link
prefix, so no NDP proxy is needed.

The second goal is that identity follows the socket, not the board. Swapping a
Pi swaps its identity automatically and no MAC table is maintained anywhere.
The third is containment: the per-port VLANs exist only on the local switches
and on tweed's `eth-local`, never on the house network or `eth-uplink`, and
switch management stays on the house net's VLAN 5 where the provisioning tool
will not touch it.

The spec's failure modes are worth knowing before you debug one:

Unconfigured port
: The device lands in the VLAN-1 quarantine pool — visible in the leases file,
  isolated from everything.

Trunk misconfiguration
: No DHCP at all for that switch. Loud, not subtle.

Provisioning tool crash mid-run
: Convergence is diff-based, so re-running finishes the job. The house VLANs
  were never in the write set.

Pi swapped between ports
: It becomes the new port's identity. The old lease expires.

:::{note}
The public site promises users "isolated networks — each Pi is on its own
network, so users can't interfere with each other". That claim is about the
network and nothing else. It means a user with a shell on one Pi cannot reach
another Pi, at either address family; combined with the read-only NFS root it
means the damage a user can do is bounded and reverts on the next power cycle.
It does **not** mean exclusive access to a board: nothing in the network design
arbitrates who is driving which FPGA. Nothing in the sources reviewed here
describes a lock or a booking mechanism either, so read "two users could be on
one Pi at the same time" as an inference from their absence rather than a
documented behaviour.
:::

## Switches

Welland has two Netgear units, both 52-port. The **GSM7252PS** is the head
switch at 10.1.5.23; tweed's `eth-local` trunk lands on it, which is why it is
switch index 1, and it provisions 40 access ports. The **S3300-52X-PoE+** hangs
off it and is switch index 2 at 10.1.5.11, with 48 access ports; it carries the
Tiny Tapeout and Acorn hosts. Both are managed over the house network's VLAN 5,
which is a separate path from the fpgas trunk — nothing management-related rides
the trunk, and the provisioning tool never touches the house-facing port. Which
board is on which port is on the [Welland page](../sites/welland.md#network).

Ansible drives all of this from the gateway, and a tag-restricted converge is
the usual way to touch just the network — but the tags are not named after the
roles, so read
[The tags do not match the role names](gateway.md#the-tags-do-not-match-the-role-names)
before running one.

Provisioning is `fpgas-switch-setup`, the CLI in
[fpgas.online-poe](https://github.com/fpgas-online/fpgas.online-poe). It reads
the same `switches:` schema the inventory uses, connects over SNMP, reads the
switch's current state and applies the difference: create the VLANs, set trunk
memberships, set access-port PVIDs, remove access ports from VLAN 1. Two things
bound the blast radius. It only ever writes VLANs **2101–2348** and the
membership of the ports it owns, so VLAN 5 and the house uplink cannot be
touched even by a run that dies halfway. And trunk memberships are written
before access-port PVIDs, so a Pi port is never PVID'd into a VLAN that cannot
yet reach the gateway.

Check mode is the default and writes nothing; `--apply` executes. The exit codes
are the interface to Ansible: `0` means in sync or applied cleanly, `2` means
check mode found drift, `1` means error.

```console
$ # set this interactively - it is a write credential, never in a file or a commit
$ export FPGAS_SWITCH_COMMUNITY='<switch-write-community>'
$ # check mode - prints the pending actions, writes nothing
$ fpgas-switch-setup --config /etc/fpgas/switches.yml --switch 1
$ fpgas-switch-setup --config /etc/fpgas/switches.yml --switch 1 --apply
$ # re-check - expect no output and exit 0
$ fpgas-switch-setup --config /etc/fpgas/switches.yml --switch 1
```

The `switch-vlans` role installs the CLI into its own venv at
`/opt/fpgas-switch/venv`, renders `/etc/fpgas/switches.yml` from the
`switches:` list, and runs the converge once per switch, passing that same
variable per switch. The two switches use different write communities, held as
vaulted variables and looked up out of band. Do not copy either value into
documentation or a commit.

:::{note}
Two operational quirks are recorded as verified, not as bugs. The switches'
net-snmp transport intermittently returns `Error in packet` or `commitFailed`
on a VLAN write that in fact applied — re-run, and the diff engine only issues
what is still missing. And each SNMP operation takes roughly two seconds, so a
full 48-port converge runs for several minutes. That is not a hang.
:::

PS1 has no per-port provisioning at all. Its single switch is a **Netgear
FS728TPv2** — the live PoE OID and the recorded management MAC both identify
it, although stale comments in its `host_vars` name two other models as well,
which the [PoE switch](../sites/ps1.md#poe-switch) section notes. It is a
Plus-series unit that the design spec put explicitly out of scope, and it does
not answer the standard PoE MIB: it uses a Netgear-private OID from a draft of
the spec. The OID and the working command are on the PS1 page under
[Power control](../sites/ps1.md#power-control).

## PoE power control

There is no remote power control other than PoE. Cutting power on the switch
port is the reset, and it is also the only way to recover a wedged board — at
Welland a hung Pi 5 shows up as
[drawing about 0.4 W instead of about 8 W](../sites/welland.md#sqrl-acorn-cle-215).

The scripted path ships in `fpgas.online-poe` and runs **on the gateway**, which
is where the SNMP credentials live and the only host with a route to the switch:

```console
$ # read the current PoE state of port 20
$ poe.sh 20
$ # 1 is on, 2 is off
$ poe.sh 20 2
$ poe.sh 20 1
$ # every port in pi_ports, one second apart
$ allpoe.sh 1 1
```

The three scripts do not share a mechanism, and the differences matter:

`poe.sh <port> [1|2]`
: Reads the port, or sets it when given a value, with `1` on and `2` off. It
  sources `/etc/environment.export` (line 39), but its live path is line 57: it
  shells out to `snmp_switch/utils.py` inside the Django venv at
  `/srv/www/pib/venv`, which is what actually reads `SNMP_SWITCH_*` from the
  environment. Everything below the script's `exit` — the hand-written
  `snmpget.py` / `snmpset.py` invocations with the credentials spelled out as
  flags — is dead code kept as a reference.

`allpoe.sh <1|2> [sleep]`
: Sources the same file (line 8) purely for `pi_ports`, then loops `poe.sh $p
  $1` over it with a sleep between calls, defaulting to one second.

`allpoeoff.sh [sleep]`
: Does **not** source anything. It hardcodes `pi_ports=$(seq 1 48)` (line 7)
  and the legacy `ip_base=10.21.0` / `o_base=100` (lines 8–9), then powers every
  one of those 48 ports off. Its single argument is the sleep time, not an
  on/off value, and the active loop never uses it; the loop that would have
  issued a clean shutdown first is commented out, on the grounds that an
  overlayrooted Pi has nothing to flush.

:::{warning}
`SNMP_SWITCH_*` and `pi_ports` are written by the `site` role's `snmp.yml`, and
that task is guarded by `when: switch.mpi_port is defined` — a field the
per-port scheme removed. The whole task is therefore skipped on tweed, and
`pi_ports` is built from `switch.nos`, which tweed does not have either. These
scripts are a working path at PS1 and a non-working one at Welland: **`poe.sh`
does not work on tweed until `snmp.yml` is fixed.** The `switch:` block still in
Welland's `host_vars` points at `10.21.0.200`, an address the per-port firewall
no longer DNATs to, since switch management moved to the house network.
:::

So a PoE cycle at Welland today is a manual one. The
[test-designs troubleshooting table](https://github.com/fpgas-online/fpgas.online-test-designs/blob/main/docs/hardware/acorn-pinmap.md)
records the remedy for a wedged board: an SNMP set against the S3300, using that
switch's write community, looked up out of band with `gdoc2netcfg`. Run it from
[tweed](../sites/welland.md#gateway-tweed) or from any other host that can reach
the switch management VLAN, the same reachability `fpgas-switch-setup` needs.

That row is about the Acorn hosts, and every Acorn at Welland is on switch 2,
the S3300 — so it covers switch 2 only. Switch 1, the GSM7252PS, carries Pis of
its own (the NeTV2 hosts and the Fomu), and fleet Pis are PoE-powered, so it
supplies PoE too and has its own separate write community. A board on switch 1
needs that one, not the S3300's.

### Runnable Welland PoE cycle

Both Welland switches answer the **standard** `POWER-ETHERNET-MIB`
(`pethPsePortAdminEnable`, OID `1.3.6.1.2.1.105.1.1.1.3.1.<port>`) over SNMPv2c,
so a manual PoE cycle is a plain `snmpset`. Run it **from
[tweed](../sites/welland.md#gateway-tweed)**, which reaches the switch
management network (10.1.5.0/24) over its default route through ten64 — the
same reachability `fpgas-switch-setup` needs. The port number is the switch
port the Pi is plugged into (`p` in the [derivation table](#two-addressing-schemes)),
not a VLAN or an address.

| Switch | Mgmt IP | Carries |
|---|---|---|
| GSM7252PS (**sw1**) | 10.1.5.23 | NeTV2 hosts (ports 10, 12, 14, 16, 18) and the Fomu (17) |
| S3300-52X-PoE+ (**sw2**) | 10.1.5.11 | Tiny Tapeout and Acorn hosts |

```console
$ # set this out of band; it is the switch's SNMPv2c write community, never in a
$ # commit. Netgear's factory defaults are public (read) / private (write); the
$ # fleet's switches also answer to pib. Use the write community for that switch.
$ export SW=10.1.5.23 COMMUNITY='<switch-write-community>' PORT=14
$ OID=1.3.6.1.2.1.105.1.1.1.3.1.$PORT
$ # read admin state (1 = on, 2 = off) and delivery (.6.1.<port>: 3 = deliveringPower)
$ snmpget -v2c -c "$COMMUNITY" -Ovq $SW $OID 1.3.6.1.2.1.105.1.1.1.6.1.$PORT
$ # power-cycle: off, wait, on
$ snmpset -v2c -c "$COMMUNITY" $SW $OID i 2 && sleep 6 && snmpset -v2c -c "$COMMUNITY" $SW $OID i 1
```

The board is gone for the netboot time below (roughly a minute for a Pi 3B+,
more than 90 s for a Pi 5). Verified 2026-09-06 by cycling all five NeTV2 ports
on sw1 and watching them netboot back within ~48 s.

This is the same standard PoE MIB the [test-designs `verify_hardware.py`
harness](https://github.com/fpgas-online/fpgas.online-test-designs) `poe_reset`
uses; it differs from the [PS1 switch](../sites/ps1.md#power-control), which
answers only a Netgear-private OID.

:::{note}
This manual `snmpset` path is the working Welland PoE control today. The scripted
`poe.sh` / `allpoe.sh` above are still the PS1 path and remain broken on tweed
until `snmp.yml` and the `/etc/environment.export` filename split are fixed (the
warning and todo below). The `switch:` block in Welland's `host_vars` still points
`poe.sh` at 10.21.0.200, an address the per-port firewall no longer routes.
:::

:::{note}
The two halves also disagree about the filename. `snmp.yml` writes
`/etc/environment` and `/etc/environment.exports`, plural; `poe.sh` sources
`/etc/environment.export`, singular, and nothing in the infra repository creates
that name. The [PS1 procedure](../sites/ps1.md#power-control) sources the
singular name and works, so the file exists on val2 — but it is not one the
roles put there, and a rebuilt gateway would not have it.
:::

:::{todo}
`poe.sh` cannot be converged at Welland until two things are fixed in
`fpgas.online-infra`: `snmp.yml`'s `switch.mpi_port is defined` guard, and the
`/etc/environment.export` versus `.exports` filename split — the warning and
note above. PS1 works by history rather than by converge, so a rebuilt val2
would lose the file too. Fix both and converge each gateway.
:::

Expect the board to be gone for a while. A Compute Blade at PS1 takes about
[60 seconds](../sites/ps1.md#power-control) to come back; a Pi 5 at Welland
takes [more than 90](../sites/welland.md#sqrl-acorn-cle-215) — it is netbooting
a kernel and an NFS root over the network, not resuming from disk. Roughly two
minutes from power-on to SSH is the figure the automation uses.

The replacement for all of this is the gateway service in
[fpgas.online-gw](https://github.com/fpgas-online/fpgas.online-gw), which is to
expose PoE control per board slug over its HTTP API, with SNMP staying on the
gateway so the web tier never holds a credential or a route to the Pi network.
Its `main` branch describes that much and says the full API documentation lands
with the implementation on a separate branch, so treat the whole interface as
planned rather than deployed, and take the request shape from the repository
rather than from here.

:::{note}
A PoE cycle is not optional after a converge. Re-running the playbook changes
the shared NFS root but changes nothing on a running Pi, and files replaced
underneath a live `overlayroot` leave it holding stale NFS handles. The
procedure is converge, then cycle every port — see
[Netboot and the NFS root](netboot.md) for why, and
[Verification](verification.md) for checking the fleet came back.
:::

## Interface naming on the Pi

Some Pis have two Ethernet interfaces: the onboard NIC and a USB dongle wired to
the FPGA board's own Ethernet for testing it. The kernel's enumeration order
between them is not stable, and when it flipped once, the onboard NIC ended up
with both a DHCP lease and the dongle's static address. The fix recorded in the
infra repo's technical-debt notes was udev rules naming the interfaces by USB
port number rather than by enumeration order: `eth-uplink` for the Pi's own
link, `eth-fpga` for the dongle.

Those rules are now two systemd `.link` files,
`11-eth-uplink.link` and `12-eth-fpga.link`, shipped in
[fpgas.online-setup-pi](https://github.com/fpgas-online/fpgas.online-setup-pi)
and installed into `/etc/systemd/network/` by the `fpgas-online-setup-pi`
package.

:::{note}
They match on `Path=`, not on MAC — `platform-3f980000.usb-usb-0:1.1.1:1.0` and
`platform-3f980000.usb-usb-0:1.2:1.0`. That is the point of the scheme (the name
follows the socket, exactly as the network addressing does), but it also means
the files only rename anything on a host whose USB controller and hub topology
match those literal paths.
:::

The gateway does the same job the other way round. Its `netif` role writes
MAC-matched `.link` files for the two NICs, so a fresh Debian install's
`enpXsY` names become `eth-local` and `eth-uplink`, which every downstream
template refers to by variable rather than by literal name. The `.link` match
carries `Type=ether` specifically to stop the VLAN children — which inherit the
parent's MAC — from matching the rule and being renamed too. Renames only apply
when a device is added, so the role reboots once on a host whose NICs still
carry their old names.

## Verifying isolation

These are the hardware checks from the prototype runbook: stage 6 proves the
isolation matrix, stage 7 proves that identity follows the port, and stage 8
proves an unconfigured port lands in quarantine. Run them after any change to
the switch config or the firewall. Mind the index mismatch flagged
[above](#two-addressing-schemes) as you read the runbook: the switch it calls
"switch 1" is the S3300, which in the deployed inventory — and in the addresses
below — is switch 2.

**1. The isolation matrix.** From a Pi on switch 1 port 1, try to reach a Pi on
switch 2 port 1 and then reach the gateway and the internet. Every reachability
claim has to be checked on both address families, because they take different
paths to the same nftables policy.

```console
$ # these two must FAIL - Pi to Pi is dropped in the gateway forward chain
$ ping -c3 10.21.2.1
$ ping6 -c3 2404:e80:a137:2102::1
$ # these must SUCCEED
$ ping -c3 10.21.0.1
$ ping6 -c3 2404:e80:a137:2101::ffff
$ ping -c3 8.8.8.8
```

Then run the mirror image from the switch-2 Pi, and from tweed confirm it can
reach both Pis.

:::{warning}
The gateway's IPv6 address is **per VLAN**, not one flat address: each per-port
interface carries `2404:e80:a137:210<s>::ffff/64`, so a Pi on switch 1 reaches
tweed at `…2101::ffff` and a Pi on switch 2 at `…2102::ffff`. The old flat
`2404:e80:a137:2100::1` was retired with `eth-fpgas` and does not exist in this
design. Pinging it and getting nothing is not an isolation failure.
:::

A pass is a **silent** drop: no reply and no port-unreachable, because the
packet dies against the `forward` chain's `policy drop` rather than being
rejected. Confirm that it never left the gateway at all by watching the target:

```console
$ # run on the TARGET Pi while the ping above is running
$ tcpdump -ni any icmp
```

No ICMP from the other Pi should appear. If any does, stop — the firewall did
not converge, and nothing below is worth running until it has.

**2. Port identity.** Move a Pi to a different port on the same switch — port 1
to port 3 — and reboot it. A reboot rather than a DHCP renew, because the DHCPv6
and RA state has to be picked up cleanly.

A pass is the Pi coming back as `pi-sw1-p3` at `10.21.1.3` and
`2404:e80:a137:2101::3`, with nothing changed anywhere but the cable. The old
lease ages out on its own. Move it back and it reverts.

**3. Quarantine.** Plug a laptop into a port that is not one of the provisioned
access ports, and watch the leases:

```console
$ # do not use a trunk port for this
$ tail -f /var/lib/misc/dnsmasq.leases
```

A pass is a lease from the quarantine pool, `10.21.0.128`–`10.21.0.150`, with no
hostname — the pool has no `host-record`, so the entry is visibly unnamed and
visibly not a `pi-sw<s>-p<p>`. Its lease is one hour against the twelve hours a
provisioned port gets, so it clears fast. It should reach tweed and no Pi.

## Sources

fpgas.online-infra, `main`:

- [`docs/superpowers/specs/2026-08-14-vlan-per-port-network-design.md`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/docs/superpowers/specs/2026-08-14-vlan-per-port-network-design.md)
  — the goals and non-goals, the addressing and VLAN formulas and their reading
  rule, the trunk/access/management port model, the failure-modes list, the
  `fpgas-switch-setup` behaviour and ordering rule, and the host_vars schema.
- [`docs/superpowers/specs/2026-08-14-vlan-per-port-prototype-runbook.md`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/docs/superpowers/specs/2026-08-14-vlan-per-port-prototype-runbook.md)
  — stages 6, 7 and 8 (isolation matrix, port identity, quarantine), the
  per-VLAN gateway IPv6 address, the CLI exit codes, and the `commitFailed` and
  two-seconds-per-operation quirks.
- [`ansible/site.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/site.yml)
  — `vlan-ports` and `switch-vlans` both gated on `when: switches is defined`.
- [`ansible/inventory/hosts`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/inventory/hosts)
  — the hosts that exist, including `slf.sytes.net`.
- [`ansible/inventory/group_vars/all/srv.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/inventory/group_vars/all/srv.yml)
  — the `tftp_root` expression, the other place `switches is defined` decides
  behaviour.
- [`ansible/inventory/host_vars/fpgas.online.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/inventory/host_vars/fpgas.online.yml)
  — the `switches:` list, the confirmed 2026-08-22 cabling and access-port
  counts, `pib_network`, `pib_network6_base`, the `/16` `eth_local_netmask` and
  why it is not `/24`, the note that `dhcp_range` is deliberately absent, and
  the vaulted per-switch write communities.
- [`ansible/inventory/host_vars/ps1.fpgas.online.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/inventory/host_vars/ps1.fpgas.online.yml)
  — the legacy `pib_network: 10.21.0`, the flat `/24` `eth_local_netmask` and
  `dhcp_range`, `switch.nos` and the `100+port` address expression.
- [`tests/inventory/host_vars/test-vm.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/tests/inventory/host_vars/test-vm.yml)
  — the CI VM's single-access-port `switches:` entry and `switches_manage:
  false`.
- [`ansible/filter_plugins/port_vlans.py`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/filter_plugins/port_vlans.py)
  — the single implementation of the per-port formulas.
- [`ansible/roles/vlan-ports/tasks/main.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/vlan-ports/tasks/main.yml)
  and its [`templates/`](https://github.com/fpgas-online/fpgas.online-infra/tree/main/ansible/roles/vlan-ports/templates)
  — the per-port netdev/network files, the `/32` gateway IPv4 and the `/64`
  per-switch gateway IPv6, proxy ARP, and the trunk's 1504-byte MTU.
- [`ansible/roles/switch-vlans/tasks/main.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/switch-vlans/tasks/main.yml)
  — the CLI venv, `/etc/fpgas/switches.yml`, and the per-switch converge with
  `FPGAS_SWITCH_COMMUNITY` from a vaulted variable.
- [`ansible/roles/firewall/templates/nftables.conf.j2`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/firewall/templates/nftables.conf.j2)
  — the `switches is defined` split, the `forward` chain's `policy drop` with
  `v*` to `v*` falling through to it, and both DNAT port formulas.
- [`ansible/roles/pxe/templates/ports.conf.j2`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/pxe/templates/ports.conf.j2)
  and [`dnsmasq-base.conf.j2`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/pxe/templates/dnsmasq-base.conf.j2)
  — one `dhcp-range` per interface tag, the `host-record` names, the
  quarantine pool and its one-hour lease, and the deliberate absence of MAC
  addresses.
- [`ansible/roles/netif/tasks/main.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/netif/tasks/main.yml)
  and [`templates/link.j2`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/netif/templates/link.j2)
  — the gateway's MAC-matched `.link` files, the `Type=ether` guard against
  matching VLAN children, and the one-time reboot.
- [`ansible/roles/site/tasks/snmp.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/site/tasks/snmp.yml)
  — the `/etc/environment.exports` variables `poe.sh` needs, `pi_ports` built
  from `switch.nos`, and the `switch.mpi_port is defined` guard.
- [`TECHDEBT.md`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/TECHDEBT.md)
  — the onboard-versus-dongle enumeration incident and the `eth-uplink` /
  `eth-fpga` naming that followed.

Other repositories:

- [fpgas.online-poe](https://github.com/fpgas-online/fpgas.online-poe) —
  `README.md` for the `fpgas-switch-setup` invocation, its owned VLAN range and
  exit codes, and the SNMP environment variables; `scripts/poe.sh` (lines 37–88:
  the sourced env file, the `utils.py` call, and the dead `snmpget.py` /
  `snmpset.py` block at 67–88, after the `exit` on line 65),
  `scripts/allpoe.sh` (lines 6–14) and `scripts/allpoeoff.sh`
  (lines 5–30: the hardcoded `seq 1 48` and legacy `10.21.0` / `100` bases, and
  the commented-out shutdown loop).
- [fpgas.online-test-designs](https://github.com/fpgas-online/fpgas.online-test-designs)
  — `docs/hardware/acorn-pinmap.md`, the troubleshooting table, for the
  0.4 W wedged-Pi symptom and the manual S3300 PoE cycle with the write
  community from `gdoc2netcfg`; `docs/verify-hardware.md` for the two-minute
  power-on-to-SSH figure.
- [fpgas.online-setup-pi](https://github.com/fpgas-online/fpgas.online-setup-pi)
  — `README.md` for the package contents, `nfpm.yaml` for where the `.link`
  files are installed, and
  `fixpi/etc/systemd/network/{11-eth-uplink,12-eth-fpga}.link` for the `Path=`
  matches themselves.
- [fpgas.online-gw](https://github.com/fpgas-online/fpgas.online-gw) —
  `README.md` for the slug-to-address derivation, PoE control by board slug,
  and the note that the API documentation lands with the implementation on an
  unmerged branch.
- [fpgas-online.github.io](https://github.com/fpgas-online/fpgas-online.github.io)
  — `site/index.html`, "How It Works", for the user-facing "isolated networks"
  claim.

Pages on this site: [Welland](../sites/welland.md#network) (the switches, their
management addresses and the board-to-port map),
[PS1](../sites/ps1.md#poe-switch) (the FS728TPv2 and its port table) and
[Power control](../sites/ps1.md#power-control) (the private OID and the
60-second blade recovery), [Sites](../sites/index.md),
[Netboot and the NFS root](netboot.md), [Verification](verification.md).
