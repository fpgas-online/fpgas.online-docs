# Updating the NFS root

**You want to put a new NFS root on welland's gateway and have every Pi run it, and to be able to go back.**
You need a checkout of [fpgas.online-infra](https://github.com/fpgas-online/fpgas.online-infra), its
automation key, the vault password, and IPv6 to reach the gateway. Every Pi reboots during an update, so
anyone using a board loses their session; visitors use the boards at any time, which is expected. ps1's
gateway does not take its root this way ([The ps1 gateway and switch](../sites/ps1-gateway.md)).

Everything here is from fpgas.online-infra, main, read 2026-10-07 (`README.md`, `.github/workflows/vm-test.yml`,
`roles/img`, `roles/nfsroot_generation`) unless a line names another source.

## How the root is built

Nothing is built on the gateway. CI builds the root on an arm64 runner (`ansible/ci-nfsroot.yml`), boots a
virtual Pi from it in the VM test, and publishes it as an image, `ghcr.io/fpgas-online/nfsroot`. The rolling
tag `bookworm-armhf` moves only after a virtual Pi has netbooted that exact image, and never backwards; a
scheduled run keeps it within about six hours of the repositories' packages.

On the gateway the playbook's `img` role pulls the image and copies its `boot/` and `root/` into
`/srv/nfs/rpi/bookworm` with rsync, recording the image's digest in `/srv/nfs/rpi/bookworm/.image-digest`.
The `fixpi` role then adds what belongs to the site and is never in the image: the `pi` password, the
`authorized_keys` files and the SSH host keys. Then `nfsroot_generation` bumps a generation number in the
root if any file changed.

## 1. Choose the image and pin it

Take the digest of the image to deploy, from the packages page of the image
(`https://github.com/orgs/fpgas-online/packages/container/package/nfsroot`) or:

```console
$ gh api "orgs/fpgas-online/packages/container/nfsroot/versions?per_page=6" \
    --jq '.[] | "\(.name) \(.metadata.container.tags | join(","))"'
```

Write down the digest the gateway serves now, so you can go back:

```console
$ ssh <you>@gw.welland.fpgas.online cat /srv/nfs/rpi/bookworm/.image-digest
```

## 2. Run the whole playbook

From the fpgas.online-infra checkout, on a branch that is `origin/main`. The run is the whole playbook,
scoped only with `--limit` and `-e`; never `--tags` or `--skip-tags` (issue #157):

```console
$ export ANSIBLE_VAULT_PASSWORD_FILE=<your copy of the vault password>
$ uv run ansible-playbook ansible/site.yml --limit fpgas.online \
    -e img_nfsroot_image=ghcr.io/fpgas-online/nfsroot@sha256:<digest>
```

Without `-e img_nfsroot_image=…` the run pulls the rolling tag, which may have moved since you looked. At
welland on 6 October 2026 such a run took 32 minutes and ended `failed=0`.

If the run fails part-way, the update lock stays on the root on purpose and no Pi reboots into a half-made
root; `verify-server.yml` fails while the lock exists. Fix the cause and run the playbook again.

## 3. Every Pi reboots

When the root changed, every Pi's `nfsroot-watchdog` sees the new generation and reboots at its own time:
`420 s + slot × 20 s` after the generation, where the slot comes from its port, `(switch − 1) × 48 +
(port − 1)`. At least five minutes before, it warns on its console, on every logged-in terminal (the web
terminal too) and in the journal. A two-switch site is through in about 40 minutes.

To have a board back sooner, power-cycle its port ([Power-cycling a board](network-power-cycle.md)). After
the update of 6 October 2026 at welland, the 12 boards that were power-cycled were all back within 9 minutes,
and the Orange Pis, left to the watchdog, by 08:57, 36 minutes after the 08:21 swap (the deploy record of that day).

To keep one board from rebooting (a JTAG session, say): `sudo nfsroot-watchdog inhibit` on the board, until it
next reboots or `nfsroot-watchdog release`. `nfsroot-watchdog status` on a board says what it plans.

## 4. Check

```console
$ uv run ansible-playbook ansible/verify-server.yml --limit fpgas.online
$ # the Pis by address: the inventory lists none
$ uv run ansible-playbook ansible/verify-pi.yml -i 10.21.2.33,10.21.2.46, -e verify_pi_hosts=all
```

`verify-server.yml` checks the gateway and the root's contents; `verify-pi.yml` checks each running Pi: its
mounts, address, services, packages, JTAG tools, camera and board. A `verify-pi.yml` run that selects no Pi
fails rather than passing. Compare with the results from before the update: a board that failed before
will fail again.

## To go back

Run step 2 again with the digest you wrote down in step 1. The Pis reboot onto it the same way.
