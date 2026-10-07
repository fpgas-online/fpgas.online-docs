# Accounts and logins

Who can log in to a gateway and to the netbooted Pis, and with what. This page
describes Welland (the gateway tweed and its fleet). It summarises the
reference in the infra repository,
[`docs/access.md`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/docs/access.md),
which names the role and variable behind every row and says how to add or
remove a person. It describes what the infra `main` branch configures, which
was deployed to tweed and checked live on 2026-09-29: a password-only login is
refused with `Permission denied (publickey)`, and every account login described
below works.

The `pi` password is public on purpose. The board pages publish it, it is what
the web terminal logs in with, and the boards are ephemeral and isolated one
VLAN per port. Its source is the vaulted `pi_pw` variable. Nothing else
here is a secret: the one private key involved, the `fpgas.online-ansible`
automation key, is vaulted and never appears in the docs.

## The gateway: tweed

Login to tweed is **public-key only**. The infra `sshd` role writes
`/etc/ssh/sshd_config.d/00-pubkey-only.conf`, which sets
`PasswordAuthentication no`, `KbdInteractiveAuthentication no`,
`AuthenticationMethods publickey` and `PermitRootLogin prohibit-password`.
Before writing it, the role refuses to converge while the account Ansible
connects as, any operator, or the jump account has no usable key
(`sshd_pubkey_only_key_users`). It does not check `admin` or `root`.

| Account | What it is for | sudo | Keys it trusts | Role |
|---|---|---|---|---|
| `ansible` (uid 1000) | Ansible's own login | passwordless | only the `fpgas.online-ansible` automation key (ED25519, `SHA256:D/6/i3vPET3EeQKtO0kv0y0YfukEVg7/ZIF7oW3U6yA`) | `automation_user` |
| `admin` (uid 1001) | runs the web tier (gunicorn, daphne, uvicorn, the fleet consumer); its keypair is the "server user" key every Pi trusts | passwordless | exactly the keys published at `github.com/mithro.keys` and `github.com/CarlFK.keys` | `server_user` (renamed in place from `videoteam`) |
| `tim`, `carl` | operators | passwordless | their GitHub keys | `operators` |
| `pi` | restricted jump account for reaching the boards | none | the shared static keys plus the GitHub keys of the `ssh_imports` ids | `jump` |
| `root` | | | key login only, password locked; no role manages its keys | `sshd` |

The `pi` jump account's login shell is `rbash`, and an sshd `ForceCommand`
wrapper lets it run only `ssh` and `ssh-keyscan`. TCP forwarding is allowed,
so `ssh -J` works through it. It has its own ed25519 key, which the Pis
authorize, so a board is one `ssh pi@10.21.<switch>.<port>` away from inside
the jump shell.

`piroot`, the old login whose shell dropped into a chroot of the NFS root, has
been deleted: the Pi root is now built in CI and pulled, and nothing logs in to
a chroot any more. `videoteam` is now `admin`.

## The Pis

Every netbooted board, `pi-sw<S>-p<P>` at `10.21.<S>.<P>`, boots the same NFS
root, so the accounts, keys and SSH host key are the same on every board. The
host key is ED25519 `SHA256:tL3Mm5hn0pSKtUhZxl9CuJTMh5fFpAYxPdFq5tGlRhI`. It
belongs to the site and survives new images.

| Account | sudo | Password | Keys it trusts |
|---|---|---|---|
| `pi` (uid 1000) | passwordless | the shared `pi` password (`pi_pw`) | the gateway's server-user key, the automation key, the operators' GitHub keys, the jump account's key |
| `root` | | | the gateway's server-user key, the automation key, the operators' GitHub keys |
| `ansible` (uid 1001) | passwordless | locked | only the automation key |

The Pis keep `PasswordAuthentication yes` on purpose, because the web terminal
logs in as `pi` with the password. Only the gateway is key-only.

The image carries no `authorized_keys`. The gateway writes them into the root
from the complete list, and only when the list changes. A change replaces the
files, and the running boards cannot see replaced files in their NFS root (see
[Updating a running fleet](netboot-update-root.md)). The change
therefore also bumps the NFS root generation, and every board reboots itself
within its stagger slot. **Adding or removing a key on the Pis reboots the
whole fleet.** So does changing the `pi` password.

## Where the keys come from, and when GitHub is down

The gateway downloads every GitHub key from `https://github.com/<user>.keys`
(never the rate-limited GitHub API). That covers the operators, the jump
account, `admin` and the Pi root. Each download is retried three times, five
seconds apart. If it still gets no keys, **the converge stops there** with a
message naming the account and the URL. Nothing is written empty. For the Pi
root the download is the first step of the NFS root update, so it stops before
the update lock is taken and before the root is touched, and the fleet keeps
running as it was. Re-run once GitHub answers again.

## Logging in

| To reach | Command |
|---|---|
| tweed | `ssh <you>@tweed.welland.mithis.com` |
| a board, with your key | `ssh -J <you>@tweed.welland.mithis.com pi@10.21.2.29`, or `-J pi@tweed.welland.mithis.com` through the jump account |
| a board, from the jump shell | `ssh pi@tweed.welland.mithis.com`, then `ssh pi@10.21.2.29` |
| a board, as the automation account | `ssh -i ~/.ssh/fpgas.online-ansible -o IdentitiesOnly=yes -J <you>@tweed.welland.mithis.com ansible@10.21.S.P` |
| a board, in a browser | the terminal on the board's page at [welland.fpgas.online](https://welland.fpgas.online) |

`tweed.welland.mithis.com` is split-horizon DNS (looked up 2026-09-29). Public
DNS gives A `87.121.95.37`, which is the site's **upstream gateway**, not
tweed, and the AAAAs
`2404:e80:a137:2100::1` and `2404:e80:a137:9921::2`, which are tweed. Inside the
site the name resolves to `10.99.21.2` and `10.21.0.1`, plus the same AAAAs.
Checked on 2026-09-29:

- inside the site or over the wg route, the name reaches tweed directly;
- from outside over IPv6, use `2404:e80:a137:2100::1`. Port 22 on
  `2404:e80:a137:9921::2` times out from outside, so use the address rather than
  the name;
- from outside over IPv4 only, the name reaches the upstream gateway, which
  proxies the web ports (80 and 443) but does not carry SSH to tweed. SSH to
  tweed from outside is over IPv6.

With `-J` your key has to be trusted at both hops. The boards trust only the
operators' GitHub keys. A person who can use the jump account but is not an
operator hops on from the jump shell, or uses the password.

## Changing who has access

The lists are in the infra repository's
`ansible/inventory/group_vars/all/ssh_keys.yml`: `operators_accounts` for
operators (their tweed account, the `admin` account and the Pis), `ssh_imports`
and `ssh_public_keys` for the jump account, and the `*_revoked` lists for keys
that must be removed. The operator and jump accounts only ever gain keys, so
removing one takes a revoked-list entry. The step-by-step, the converge
command and the checks that prove the result (`verify-server.yml`,
`verify-pi.yml`) are in the infra
[`docs/access.md`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/docs/access.md).
