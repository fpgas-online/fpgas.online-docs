# The gateway host

Each site has exactly one x86 gateway, and it is everything at the site that is
not a Pi: [tweed](../sites/welland.md#gateway-tweed) at Welland, which sits
behind the ten64 reverse proxy on a private link, and
[val2](../sites/ps1.md#gateway-val2) at PS1, which faces the public internet
directly. The gateway serves the boot chain, exports the NFS root, is the
network edge and firewall for the Pi network, and runs the web tier that end
users see. This page covers which hosts those are, what runs on them, how they
are deployed, and what a rebuild from bare metal has to get right.

## Hosts

Ansible names the two gateways after their public DNS, not their hostnames:
inventory host `fpgas.online` is tweed, and `ps1.fpgas.online` is val2. Their
hardware, interfaces and boards are on the site pages; what follows is only
their place in the inventory.

| Group | Members | What the group means |
| --- | --- | --- |
| `nbp` | `fpgas.online`, `ps1.fpgas.online`, `slf.sytes.net` | "netboot Pi" — the server play in `site.yml`: `netif`, `operators`, `lldp`, `firewall`, `vlan-ports`, `switch-vlans`, `nfs`, `img`, `fixpi`, `pxe`, plus the tasks that start and stop the provisioning chroot |
| `pig` | `fpgas.online`, `ps1.fpgas.online` | the web tier play, `web.yml`: `site`, `wssh`, `cam/stream-server`, `ttsite` |
| `uhubctl` | `slf.sytes.net` | the `uhubctl` play — USB hub power control |
| `pxe` | `fpgas.online`, `ps1.fpgas.online`, `slf.sytes.net` | declared in the inventory, but no playbook targets it |

Two of those need reading carefully. The `uhubctl` group holds only
`slf.sytes.net`, so on the inventory as it stands the `uhubctl` role never runs
on tweed or val2 — even though the infra README's roles table describes
`uhubctl` as a server role and `CLAUDE.md` describes `site.yml` as running
`nbp`/`uhubctl`/`pig` plays against "the server". The group membership is what
Ansible acts on. And the `pxe` group is a leftover: the dnsmasq work lives in
the `pxe` *role*, which runs from the `nbp` play, while the `pxe` *group* is
matched by nothing in the repo.

:::{todo}
Three inventory-versus-README mismatches are unresolved upstream: the
`[uhubctl]` group contains only `slf.sytes.net`, so the `uhubctl` role never
runs on tweed or val2 despite the infra README calling it a server role; the
`[pxe]` group is declared but no playbook targets it; and the README calls the
chroot group `pi` while the inventory group is `onpi` with a *host* named `pi`.
Either fix the groups or fix the README, in `fpgas.online-infra`.
:::

:::{todo}
`slf.sytes.net` is in both `nbp` and `uhubctl`, so a full-scope `site.yml` run
tries to reach it. The 2026-08-25 tweed rebuild log records, in its rebuild #2
entry P2-9 of 2026-08-26, that it no longer resolves — dead dynamic DNS — and
left it failing as out of scope. Nobody has decided whether the host is retired,
has a new address, or should come out of the inventory.
:::

The inventory's fourth entry is not a machine. Group `onpi` contains a single
host named `pi`, at the gateway's own address as user `piroot`: the login shell
of that account is a wrapper that immediately `chroot`s into the NFS root, so
Ansible talks to it over the gateway's ordinary sshd and every command lands
inside the ARM root. It is how Pi configuration is baked into the image on the
server rather than applied to running Pis — see
[The provisioning container](netboot.md#the-provisioning-container). The plays
that use it are written `hosts: pi`, which matches the host, not the group.

## What runs on the gateway

One line per service, with the role that installs it.

**Boot and storage** — the `nbp` play:

- **dnsmasq** (`pxe`, `dnsmasq.service`) provides DHCP, TFTP and DNS on the Pi
  network. It runs
  `no-resolv` with an explicit upstream, so it is the network's resolver; it
  binds with `bind-dynamic` rather than `bind-interfaces` so it survives the
  ~150 per-port VLAN interfaces that mostly have no carrier; and its lease
  database is pinned to an absolute path. See
  [The boot chain](netboot.md#the-boot-chain).
- **nfs-kernel-server and rpcbind** (`nfs`, `nfs-kernel-server.service` and
  `rpcbind.service`) export the read-only NFS roots, with `host=` in
  `/etc/default/nfs-kernel-server` set to the local NIC so the export is not
  offered on the uplink.
- **chrony** (`pxe`, `chrony.service`) serves NTP to the Pi LAN, allowed for
  `10.21.0.0/16`, and
  dnsmasq advertises the gateway as the time source with
  `dhcp-option ntp-server`. The Pis have no route to the internet, so without a
  LAN time source their clocks never leave the `fake-hwclock` date.
- **The image pipeline** (`img`) downloads and extracts the Raspberry Pi OS
  image into the NFS root, and (`fixpi`) writes the boot configuration, users
  and command line into it — [How the root is built](netboot.md#how-the-root-is-built).

**Network** — also the `nbp` play:

- **netif** (`systemd-networkd.service`) gives the two NICs their `eth-local` /
  `eth-uplink` names via MAC-matched systemd `.link` files, moves the uplink
  from `ifupdown` to systemd-networkd, and reboots once if a NIC still carries
  its installer-era name.
- **nftables** (`firewall`, `nftables.service`) carries the whole isolation
  policy; the role also installs `nmap` for probing it. See
  [Verifying isolation](network.md#verifying-isolation).
- **lldpd** (`lldp`, `lldpd.service`) advertises the gateway on every attached
  link and records what the switches advertise back, so the cabling can be
  confirmed rather than assumed.
- **The per-port VLAN interfaces** (`vlan-ports`) are systemd-networkd `.netdev`
  and `.network` files, one pair per switch port, on the `eth-local` trunk;
  stale `40-v*` files for ports no longer in the plan are removed. The role runs
  only on hosts that define `switches:`.
- **switch-vlans** installs the `fpgas-switch-setup` CLI into its own venv,
  renders `/etc/fpgas/switches.yml` and converges each switch — see
  [Switches](network.md#switches).
- **operators** creates the human operator accounts with passwordless sudo,
  keyed from their GitHub accounts with `ssh-import-id`, and asserts that every
  one of them ended up with at least one key.

**Web tier** — the `pig` play, all of `web.yml`:

- **nginx** (`site`, from `nginx-extras`, `nginx.service`) is installed first in
  the play, because the later web roles write into `/etc/nginx`. The role owns
  the port-80 catch-all vhost that serves ACME challenges and redirects
  everything else to HTTPS, plus the location includes that route each Django
  app.
- **gunicorn** with the uvicorn worker class behind `/run/gunicorn.sock`
  (`gunicorn.socket` and `gunicorn.service`), **daphne** for the status
  WebSocket (`daphne.socket` and `daphne.service`), and **uvicorn**
  (`uvicorn.service`), all pip-installed into the Django venv and run as
  systemd units (`site`).
- **redis** (`site`, `redis-server.service` — the role installs the Debian
  `redis` package without naming a unit, and its own verify tasks assert
  `redis-server.service`) backs the `channels_redis` layer the live Pi status
  page uses.
- **certbot** (`site`; the role writes no unit of its own — renewal is whatever
  the installed certbot ships, and on tweed that is the snap build) obtains the
  TLS certificate — see
  [Web topology at Welland](#web-topology-at-welland).
- **webssh** (`wssh`, `wssh.socket` and `wssh.service`) runs in its own venv
  behind a systemd socket, with an nginx include that publishes the browser
  terminal.
- **nginx-rtmp and fancyindex** (`cam/stream-server`, modules inside
  `nginx.service`) take the RTMP feeds the Pis push and republish them as HLS
  from a tmpfs, with the front-end nginx include beside it.
- **The Tiny Tapeout site** (`ttsite`, only where `tt_boards` is defined) loads
  the board catalogue into Django, pins the Commander embed bundle by version
  and SHA-256, and renders the `tinytapeout.fpgas.online` vhost with one
  WebSocket proxy per live board.

The Django application itself is [The web application](webapp.md); the Tiny
Tapeout catalogue and daemon are [The Tiny Tapeout stack](tinytapeout.md).

**USB** — the `uhubctl` play:

- **uhubctl** plus a udev rule for the D-Link DUB-H7 (USB ID `2001:f103`), which
  sets the hub's device node to mode 0666 and chmods its per-port `disable`
  attributes so an unprivileged user can cut power to one port. This is the
  USB-side counterpart to
  [PoE power control](network.md#poe-power-control), and on the current
  inventory it applies to `slf.sytes.net` only.

## Deploying

`ansible.cfg` supplies the inventory and `become`, so the only thing a run has
to add is the vault password, for the hosts whose variables carry encrypted
values — at Welland, the switches' SNMP write communities.

```console
$ # full deployment of the Welland gateway plus its Pi NFS root
$ uv run ansible-playbook ansible/site.yml --limit fpgas.online,pi
```

```console
$ # server roles on every gateway, no NFS root provisioning
$ uv run ansible-playbook ansible/site.yml --limit nbp,uhubctl,pig
```

```console
$ # the web tier alone: Django site, web SSH, camera front end, tinytapeout
$ uv run ansible-playbook ansible/web.yml --limit fpgas.online
```

Re-running `web.yml` reinstalls the `fpgas-online-site` wheel with
`state: forcereinstall`, and a new wheel means new code and templates that the
running `gunicorn`, `daphne` and `uvicorn` keep serving the old versions of
until they are restarted — so the install task notifies a `restart django
services` handler that restarts all three. `--tags django` narrows a run to the
application itself, which is also the way back: pip an older
`fpgas-online-site` reference into the Django venv and re-run with that tag.
The host's `local_settings.py`, which carries the production settings, is
created once and never overwritten, so it survives both directions.

A second inventory exists for CI. The `ansible/ci-nfsroot.yml` playbook, run
against `ansible/inventory-ci-nfsroot`, runs the same `img`, `fixpi`,
`fpgas-apt`, `cam/pi` and `onpi` roles on a GitHub arm64 runner to build the
NFS root alone, reaching the root through the `community.general.chroot`
connection plugin instead of the `piroot` SSH wrapper — only the inventory
differs.

### The tags do not match the role names

A tag-restricted run is the usual way to touch one part of the gateway, and the
tags are not named after the roles that carry them. The prototype runbook
verified the first three of these traps; the fourth was found against `main`:

- The `pxe` role's per-port work — writing `/etc/dnsmasq.d/ports.conf`, and the
  `pibs.conf` it replaces — is tagged **`pibs`**, a name carried over from the
  MAC-table scheme, not `pxe`. The neighbouring task that writes the legacy
  `switch.conf` carries **no tag at all** on `main`.
- The `firewall` role's ruleset write and service enable are tagged
  **`nftables`**, not `firewall`. The role's converge tasks carry no `firewall`
  tag at all; the one place that name is a tag is `verify-server.yml`, whose
  firewall verify include is tagged `verify, firewall` — so `--tags firewall`
  checks the ruleset without ever writing it.
- The task that removes the legacy `pibs.conf`, `switch.conf` and hand-written
  `local.conf` from a per-port host is recorded in the runbook as carrying **no
  tag at all**, so a tag-restricted run skips it and the stale files keep
  coexisting with `ports.conf` — and `local.conf`'s `bind-interfaces` conflicts
  with `base.conf`'s `bind-dynamic` badly enough that dnsmasq refuses to start
  with both. On `main` today that task is tagged `pxe` and `pibs`. Either way,
  check the directory afterwards.
- Two more consequential tasks carry no tag on `main` and so run only in a
  fully untagged play: the `firewall` role's `Install nftables` (which also
  pulls in `nmap`), and the `pxe` role's `enable Raspberry Pi Boot`, which drops
  `rpi.conf` into `/etc/dnsmasq.d/`. On a host that already has both, a tagged
  run is fine; on a fresh one it writes rules for a package that is not there
  and serves DHCP without the Raspberry Pi boot options.

So the tag list that actually deploys the per-port network is the following.
Preview it first:

```console
$ # check mode: changes nothing, prints the diff
$ uv run ansible-playbook ansible/site.yml --limit fpgas.online \
    --tags vlan-ports,pxe,pibs,switch-vlans,nftables --check --diff
```

Then apply it:

```console
$ # writes the config and reloads dnsmasq, networkd and nftables
$ uv run ansible-playbook ansible/site.yml --limit fpgas.online \
    --tags vlan-ports,pxe,pibs,switch-vlans,nftables
```

`fpgas.online` is in both `nbp` and `pig`, but none of the web roles' tasks
carry any of those tags, so the web tier is left alone.

:::{warning}
A bad `/etc/nftables.conf` leaves the gateway with **no ruleset at all**, not
with the previous one. The two paths differ. The role's notify handler reloads
(`state: reloaded` → `ExecReload=nft -f /etc/nftables.conf`), and that load is
atomic: a parse error fails and the running ruleset stays up. But the role's
`Enable nftables service` task **restarts** the unit (`state: restarted`),
unconditionally and under the same `nftables` tag, and Debian's
`nftables.service` has `ExecStop=/usr/sbin/nft flush ruleset` — so a restart
flushes the ruleset first and then fails to load the replacement. What is left
is an empty ruleset: no `forward` chain, no `policy drop`, no Pi isolation, and
the failure is fail-open rather than fail-closed. SSH surviving is not
reassurance here; it survives either way, because both templates accept it
unconditionally on the input chain and an empty ruleset accepts everything.

The `--check --diff` preview above is the real safeguard — run it and read the
rendered file before applying.
:::

:::{todo}
Fix the fail-open converge upstream in `fpgas.online-infra`: the `firewall`
role's `Enable nftables service` task is `state: restarted` under the
`nftables` tag, and Debian's `nftables.service` has
`ExecStop=nft flush ruleset`, so a converge with a bad rendered ruleset flushes
the old rules and loads nothing. The notify handler's `state: reloaded` is the
safe form. Nobody has decided whether the task should become `state: started`,
gain a validation step, or both.
:::

### Checking and reconnecting

`verify-server.yml` has three plays, one per group. The `nbp` play runs each
server role's own `verify/` tasks — `operators`, `lldp`, `firewall`, `nfs`,
`img`, `fixpi`, `pxe` — then asserts the per-port state on hosts with
`switches:` (a `v*` interface in `networkctl list`, `dnsmasq --test` clean, the
`forward` chain at `policy drop`, `ports.conf` present) and finally that the NFS
root really contains what the Pis need. The `uhubctl` play runs that role's
verify tasks. The `pig` play verifies the web tier: `site`, then `ttsite` where
`tt_boards` is defined, then `wssh` and `cam/stream-server`.

Three roles have no verify tasks at all — `netif`, `vlan-ports` and
`switch-vlans` ship no `tasks/verify/` directory. The per-port network is
covered only by the inline assertions in the `nbp` play, tagged
`switch-vlans`, and nothing checks the NIC naming or the switch converge
directly.

After a web deploy, the narrower check is worth running on its own:

```console
$ # read-only: asserts the deployed web tier, changes nothing
$ uv run ansible-playbook ansible/verify-server.yml --limit fpgas.online \
    --tags site,ttsite,wssh
```

`verify-pi.yml` checks a running Pi instead, and takes the same inventory or an
ad hoc address. Both are [Verifying a deployment](verification.md).

`ansible/ssh.cfg` gives the automation its own `known_hosts` file, separate from
the operator's and from the host-wide one the site's network tooling generates,
with `StrictHostKeyChecking accept-new` and `IdentityAgent none` — a hung
forwarded ssh-agent otherwise stalls every connection at the session-bind query
and looks exactly like a dead server. `accept-new` can add a key but cannot
replace a changed one, so after any deliberate reinstall run
`refresh-known-hosts.yml` before the next `site.yml`: it removes the stale
entries, re-scans with retries while the host finishes booting (plain
`ssh-keyscan`, never `-H`, because hashed names break the `known_hosts` module)
and pins the new key. It runs with `become: false` on purpose — it manages the
control node's own files, and a root-owned `known_hosts` stops the user's ssh
appending anything later. It keyscans from the control node, so hosts on the Pi
network, which are only reachable by jumping through the gateway, cannot be
rekeyed by it.

## Web topology at Welland

Tweed does not face the internet. `ten64` is the public edge: its nginx
reverse-proxies port 80 to tweed and passes port 443 through by SNI, so **tweed
terminates TLS itself** with its own Let's Encrypt certificates, obtained by the
webroot method — the HTTP-01 challenges arrive through ten64's `/.well-known/`
passthrough. The names ten64 routes to tweed come from tweed's alias entry in
the site's network sheet: `welland.fpgas.online`, `*.welland.fpgas.online` and
`welland.fpgas.mithis.com`. `tinytapeout.fpgas.online` is a CNAME to
`welland.fpgas.online` and had to be added to that alias list, and ten64's nginx
redeployed, before its certificate could be issued at all. Ansible reaches tweed
over the private ten64-to-tweed link, so the playbooks are run from inside the
Welland network.

:::{warning}
Three rules keep certbot away from the nginx configuration:

- Obtain certificates with `certbot certonly --webroot` only. Never
  `certbot --nginx`.
- Never install `python3-certbot-nginx`. The plugin is the thing that rewrites
  nginx config, and nothing on the host should be able to.
- Repoint any certificate lineage that was created by the old `--nginx` path at
  the webroot authenticator. Renewal otherwise runs the nginx installer again
  and undoes the Ansible-owned vhost.
:::

The reason is a two-stage failure. `certbot --nginx` does not merely fetch a
certificate: it rewrites the nginx server blocks, copying the `listen`
directives it finds in the port-80 block into the HTTPS block it generates. The
port-80 template had its IPv6 line commented out, so certbot emitted an
IPv4-only `listen 443 ssl` for `welland.fpgas.online`. That was invisible while
nothing else listened on `[::]:443` — IPv6 clients were refused and fell back to
IPv4. When the `ttsite` role added the first `listen [::]:443 ssl` on the box on
2026-08-23, its vhost became the only, and therefore default, server on that
socket, and every IPv6 client asking for `welland.fpgas.online` was handed the
`tinytapeout.fpgas.online` certificate and dropped the connection. It was fixed
on 2026-08-30 by moving to the webroot method with the vhost rendered and owned
by Ansible.

Tweed runs the snap build of certbot, whose renewal configurations an older
Debian package cannot read, so the role installs Debian's `certbot` only when no
`/usr/bin/certbot` already exists.

## Rebuilding from scratch

Tweed was rebuilt from bare metal three times between 2026-08-25 and
2026-08-26. The operating-system install itself — the pxelinux menus, the
preseed and the boot overrides, all of which live on ten64 rather than in the
infra repo — is out of scope for this page; what follows are the lessons that
bear on the gateway coming back correctly. As a checklist for the next one:

- **Enable the PXE option ROM on the uplink NIC in the BIOS, and disable it on
  the others.** The first attempt never reached the installer because the only
  enabled option ROM was on the local NIC, which has no DHCP server on it while
  the gateway is down. This is a hardware-only property; no amount of CI catches
  it.
- **Get the console order right, and name only UARTs that exist.** The serial
  console must come *last* on the installer command line to be the primary one,
  or the installer's UI goes to VGA and a remote operator sees nothing after
  early boot. Naming dead UARTs is worse than useless: two different kernel
  series hung identically about nine seconds into boot until the extra
  `console=` arguments for non-existent ports were removed.
- **Pin the installer's network interface by MAC.** The installer's automatic
  interface selection picks the first NIC with carrier and does not fall back,
  which is the same failure as the option ROM one a layer higher up.
- **Keep the vault password location the deployment documents in step with the
  one that actually decrypts the inventory.** A converge run was lost to three
  different candidate locations coexisting in the ecosystem, only one of which
  worked. CI cannot catch this class at all — the test inventory has no
  encrypted variables, so password and path drift only ever bites a production
  run.
- **The kernel and the initramfs served over TFTP must be the matching pair.**
  A regenerated initramfs beside a two-year-old `kernel8.img` gives
  nondeterministic Pi boots — sometimes fine, sometimes a panic loop. Sync the
  whole firmware payload; see
  [How the root is built](netboot.md#how-the-root-is-built).
- **Run `refresh-known-hosts.yml` after the reinstall and before the next
  `site.yml`.** A reinstalled host has new keys, and the pinned old ones make it
  unreachable to automation — see
  [Checking and reconnecting](#checking-and-reconnecting). Only then converge,
  with the commands in [Deploying](#deploying).

Rebuild #3, on the evening of 2026-08-26 and run from merged `main`, was a full
pass with **zero manual interventions**: 7m41s from power cycle to login, a cold
converge of 2h57m with no failures on either the server or the NFS root play,
`verify-server.yml` at `ok=104 failed=0`, `verify-pi.yml` at `ok=21 failed=0`
including the camera and FPGA assertions. That is the bar a rebuild is expected
to clear.

## Testing without hardware

The whole gateway can be exercised without touching a site. `tests/vm/`
boots a Debian server VM, applies the same `site.yml` production uses, then
PXE-boots a virtual Raspberry Pi from the result using patched QEMU from
[fpgas-online/rpi-qemu](https://github.com/fpgas-online/rpi-qemu), which adds
BCM2838 GENET ethernet emulation to the `raspi4b` machine, and runs both verify
playbooks against them — only the inventory differs from production. A full run
takes roughly two hours under TCG, less when `/dev/kvm` is available, and CI
runs it on every push to `main` and every pull request, uploading the serial
logs as an artifact whether it passed or failed.

:::{note}
The 2026-04-04 QEMU testing design and plan in the infra repo describe a
different arrangement: a generic `qemu-system-aarch64 -machine virt` guest
booting through EDK2 UEFI firmware to `grubaa64.efi` and a TFTP `grub.cfg`,
with the `pxe` role serving an architecture-tagged `dhcp-boot` beside the real
Pi path. That is not what runs. The harness emulates a real Pi and drives the
real `bootcode.bin` chain, so the test exercises the production boot path
rather than a parallel one.
:::

## Sources

fpgas.online-infra, `main`:

- [`README.md`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/README.md)
  — the host-groups and roles tables, the deploy and verify command lines, the
  vault-password note, and the QEMU test harness description including the
  rpi-qemu GENET emulation, the TCG runtime and the CI workflow.
- [`CLAUDE.md`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/CLAUDE.md)
  — the "Deployment Targets" entries for `welland.fpgas.online` (tweed) and
  `ps1.fpgas.online` (val2), and the key-files list naming `site.yml`,
  `web.yml`, `verify-server.yml` and `verify-pi.yml`.
- [`ansible/inventory/hosts`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/inventory/hosts)
  — the `pxe`, `nbp`, `uhubctl` and `onpi` groups and their exact membership,
  and the `pi` pseudo-host with its `piroot` user and comment.
- [`ansible/site.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/site.yml)
  — the role order in the `nbp` play, the `uhubctl` play, the `web.yml` import,
  and the chroot start/stop tasks around the `pi` play.
- [`ansible/web.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/web.yml)
  — the `pig` play's four roles and the `tt_boards` condition on `ttsite`.
- [`ansible/verify-server.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/verify-server.yml)
  — the three plays, the per-role verify includes and the `verify, firewall`
  tag on one of them, the per-port assertions gated on `switches is defined`,
  the NFS-root package and configuration checks, and the `pig` play's `site`,
  `ttsite`, `wssh` and `cam/stream-server` order. The absence of
  `tasks/verify/` under `netif`, `vlan-ports` and `switch-vlans` is from the
  role trees themselves.
- [`ansible/verify-pi.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/verify-pi.yml)
  — the host pattern and the documented ad hoc invocation.
- [`ansible/refresh-known-hosts.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/refresh-known-hosts.yml)
  — when to run it, the remove/rescan/pin sequence, the "never `-H`" rule and
  the `become: false` reasoning.
- [`ansible/ssh.cfg`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/ssh.cfg)
  — the private `known_hosts`, `accept-new`, and `IdentityAgent none` with the
  hung-agent rationale.
- [`ansible/ci-nfsroot.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/ci-nfsroot.yml)
  and [`ansible/inventory-ci-nfsroot/hosts`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/inventory-ci-nfsroot/hosts)
  — the CI NFS-root build and its `community.general.chroot` connection.
- `ansible/roles/*/tasks/main.yml` for the server-side roles — what each one
  installs and configures:
  [`netif`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/netif/tasks/main.yml),
  [`operators`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/operators/tasks/main.yml),
  [`lldp`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/lldp/tasks/main.yml),
  [`firewall`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/firewall/tasks/main.yml)
  (the `nftables` tag, the untagged install, and the `state: restarted` on
  `Enable nftables service`),
  [`vlan-ports`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/vlan-ports/tasks/main.yml),
  [`switch-vlans`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/switch-vlans/tasks/main.yml),
  [`nfs`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/nfs/tasks/main.yml),
  [`img`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/img/tasks/main.yml),
  [`fixpi`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/fixpi/tasks/main.yml),
  [`pxe`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/pxe/tasks/main.yml)
  (dnsmasq, chrony, and the `pibs` tag),
  [`uhubctl`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/uhubctl/tasks/main.yml),
  [`site`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/site/tasks/main.yml),
  [`wssh`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/wssh/tasks/main.yml),
  [`cam/stream-server`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/cam/stream-server/tasks/main.yml)
  and [`ttsite`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/ttsite/tasks/main.yml).
- [`ansible/roles/site/tasks/nginx.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/site/tasks/nginx.yml),
  [`certbot.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/site/tasks/certbot.yml),
  [`fpgas-online-site.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/site/tasks/fpgas-online-site.yml)
  [`pistat.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/site/tasks/pistat.yml),
  [`django.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/site/tasks/django.yml),
  [`handlers/main.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/site/handlers/main.yml)
  and [`tasks/verify/main.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/site/tasks/verify/main.yml)
  — `nginx-extras`, the port-80 ACME vhost, the certbot history and the
  deliberate omission of the nginx plugin, the gunicorn/uvicorn/daphne and
  channels-redis installs, redis, the `local_settings.py` that is created once
  and never overwritten, the `restart django services` handler and the three
  units it restarts, and the verify loop that names `redis-server.service`.
- [`ansible/roles/firewall/handlers/main.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/firewall/handlers/main.yml)
  — the `state: reloaded` notify handler, against the role's `state: restarted`
  converge task. Debian's `nftables.service` supplies the rest: `ExecReload` is
  a plain `nft -f`, while `ExecStop` is `nft flush ruleset`.
- [`ansible/roles/cam/stream-server/tasks/base.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/cam/stream-server/tasks/base.yml)
  and [`back.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/cam/stream-server/tasks/back.yml)
  — the rtmp and fancyindex modules and the tmpfs HLS directory.
- [`ansible/roles/uhubctl/templates/udev/52-uhubctl.rules.j2`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/uhubctl/templates/udev/52-uhubctl.rules.j2)
  — the DUB-H7 USB ID and what the rule relaxes.
- [`ansible/roles/pxe/templates/dnsmasq-base.conf.j2`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/pxe/templates/dnsmasq-base.conf.j2)
  — `bind-dynamic`, the pinned lease path, `no-resolv`, and the NTP DHCP option.
- [`docs/superpowers/runbooks/2026-08-23-tweed-web-deploy.md`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/docs/superpowers/runbooks/2026-08-23-tweed-web-deploy.md)
  — the ten64 edge, the SNI passthrough, the webroot challenge path, the alias
  list and the `tinytapeout.fpgas.online` CNAME, the deploy commands and the
  narrowed `--tags site,ttsite,wssh` verify command, and the rollback note that
  `local_settings.py` is never overwritten.
- [`docs/superpowers/specs/2026-08-14-vlan-per-port-prototype-runbook.md`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/docs/superpowers/specs/2026-08-14-vlan-per-port-prototype-runbook.md)
  — stage 4's verified tag caveats, the working tag list and the check-mode
  preview. The current tagging of each task named there was re-checked against
  `main`. Its "firewall reload safety" note describes the handler's reload
  only; the converge task restarts the unit, so the fail-open case above is not
  covered there.
- [`docs/rebuilds/2026-08-25-tweed-rebuild.md`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/docs/rebuilds/2026-08-25-tweed-rebuild.md)
  — the option ROM (A1-1), console order and dead UARTs (A1-2, A1-3), the
  interface pin (A1-4), the vault-location drift (B1-2), the kernel and
  initramfs mismatch (C1-3), the unreachable `slf.sytes.net` (P2-9), the
  known-hosts lifecycle (P2-2) and rebuild #3's zero-intervention result.
- [`docs/superpowers/specs/2026-04-04-qemu-vm-testing-design.md`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/docs/superpowers/specs/2026-04-04-qemu-vm-testing-design.md)
  and [`docs/superpowers/plans/2026-04-04-qemu-vm-testing.md`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/docs/superpowers/plans/2026-04-04-qemu-vm-testing.md)
  — the superseded EDK2 UEFI and `grubaa64.efi` boot chain for the test guest.
