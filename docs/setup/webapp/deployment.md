# The web application: deployment

**You run a gateway and want to know how the site role puts the web application on it.**

## Deployment

The application is installed on the gateway by the infra `site` role, which runs
in the `pig` play — see
[What runs on the gateway](../gateway.md#what-runs-on-the-gateway) for the
surrounding services and [Deploying](../gateway.md#deploying) for the command
lines. The role installs `fpgas-online-site` and `fpgas-online-poe[cli]` into
`/srv/www/pib/venv` straight from their git repositories with pip, at
`state: forcereinstall`. The role does not say why that flag is there; the
requirement is a git URL with no version in it, so a plain install would find it
already satisfied and not take a new commit. The web tier is installed from git
this way; the Pi side, by contrast, arrives as debs from the
[apt repository](../../packages.md). The same task file then installs the app
servers — gunicorn, uvicorn and daphne — plus `channels-redis`, before the unit
files are written, so that gunicorn's first start with the uvicorn worker class
cannot race the uvicorn install. `channels_redis` is a settings dependency the
site package does not declare.

The wheel ships the `pib` project package as well as the apps, so the role
copies `__init__.py`, `settings.py`, `urls.py` and `asgi.py` back out of the
installed package into `/srv/www/pib/pib/`, which shadows it on `sys.path`. That
directory is where `local_settings.py` lives, and `local_settings.py` is created
once with `force: false` and never overwritten afterwards. Ansible only ever
edits individual lines in it. Those lines turn `DEBUG` off, set the domain name
and the static root, and derive `ALLOWED_HOSTS` from the host's own uplink
address, its `domain_name`, its streaming front-end aliases and — only when the
host defines `tt_boards` — the Tiny Tapeout domain. `CSRF_TRUSTED_ORIGINS` is
the same list with the bare IP and any wildcard entry dropped and `https://`
prefixed. It also carries the host's `SECRET_KEY`, which the role generates once
into `<django_dir>/.secret_key`, keeps out of the inventory, and never rotates;
the wheel's own settings ship Django's insecure development default.

The role then writes a `manage.py` whose shebang is the venv interpreter and
runs, as the service user so the SQLite file and the static root end up owned by
it, `migrate --noinput`, `collectstatic --noinput` and `loaddata` of the site's
board fixture. The fixture ships inside the installed package and is resolved by
bare name (`fpgas.online.json` at Welland, `ps1.fpgas.online.json` at PS1), so
nothing is copied out of the infra repository; `loaddata` upserts by primary key,
so re-running a converge refreshes the seeded boards rather than duplicating
them.

:::{warning}
That indirection has bitten before. The fixtures used to be copied from the
infra repository, and when they moved into the site repository with the monorepo
split the copy silently stopped matching. The 2026-08-26 tweed reinstall seeded
zero boards and `welland.fpgas.online` came up with an empty board list.
:::

Not every task restarts the application. The `restart django services` handler
is notified by the pip install, the copy of the project files out of the wheel,
and the `SECRET_KEY`/`DEBUG`, `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` lines —
but not by the `DOMAIN_NAME`, `PI_PW` or `STATIC_ROOT` lines, nor by the
generated `manage.py`, so a change to any of those is not picked up until
something else restarts the services. What the handler is for, and the
`--tags django` rollback path, are under
[Deploying](../gateway.md#deploying).

nginx routes to the application through per-app location includes rendered by
the same role — one file each for `pibfpgas`, `pistat`, `pibup` and
`snmp_switch`. All of them proxy to gunicorn on `/run/gunicorn.sock`; the
`pistat` include additionally proxies `/ws/` to daphne on port 8085 with the
upgrade headers, and the `pibfpgas` include carries the `301 /fpgas` redirect.
The vhost itself is a `root` pointing at the static directory and an `include`
of that directory, so a path with no include is unreachable no matter what the
urlconf says — which is why `/admin/` and `/static/` do not work on this host.

The Tiny Tapeout host is a separate role, `ttsite`, which runs only where
`tt_boards` is defined. It renders the board catalogue to
`/etc/fpgas-online/tt-boards.yaml` and loads it with:

```console
$ /srv/www/pib/venv/bin/python manage.py ttsite_loadboards /etc/fpgas-online/tt-boards.yaml --prune
```

`--prune` deletes rows whose slug is absent from the file, and refuses to run
against an empty board list unless `--allow-empty` is also given. The role
writes the `TTSITE_HOST` and Commander version lines into `local_settings.py`,
re-runs `collectstatic`, and downloads the Commander embed bundle from the
fork's `embed-v<version>` release, verified against a SHA-256 pinned in the
inventory beside the version, into a per-version directory under the static
root. Version and checksum are pinned together and the role asserts that a set
version has a 64-hex checksum; a board page whose pinned version is empty shows
a "bundle not deployed" notice instead of the embed. There is a second, legacy
bundle for boards with pre-2.x firmware, pinned separately and unpacked under
its own directory. The design gallery calls the embed's `refreshDesigns()` after
a run or an upload, which needs bundle 0.2.0 or newer.

TLS is obtained by the webroot method and the vhost stays Ansible-owned. The
rules that keep certbot away from the nginx configuration, and the IPv6 outage
that taught them, are in
[Web topology at Welland](../gateway.md#web-topology-at-welland); do not run
`certbot --nginx` against this host.
