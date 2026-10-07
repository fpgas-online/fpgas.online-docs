# The web application: sources

**You want the sources behind these pages.**

## Sources

fpgas.online-site, `main`:

- [`README.md`](https://github.com/fpgas-online/fpgas.online-site/blob/main/README.md)
  — the app table, the host split and `TTSITE_HOST`, the `ttsite_loadboards`
  invocation and what `--prune` does, the `TTSITE_COMMANDER_VERSION` pin and the
  "bundle not deployed" notice, the three daemon-proxy endpoints with their
  status codes and the 256 KiB cap, the `refreshDesigns()` and 0.2.0 note, the
  `pistat` ping legacy-hostname note, the deployment path `/srv/www/pib/`, and
  the description of what the wheel ships and what `local_settings.py` is.
- [`pib/settings.py`](https://github.com/fpgas-online/fpgas.online-site/blob/main/pib/settings.py)
  — `INSTALLED_APPS` (which does not contain `pibdemos`) and the middleware list
  with `TTSiteHostMiddleware` first.
- [`pib/urls.py`](https://github.com/fpgas-online/fpgas.online-site/blob/main/pib/urls.py),
  [`pibfpgas/src/pibfpgas/urls.py`](https://github.com/fpgas-online/fpgas.online-site/blob/main/pibfpgas/src/pibfpgas/urls.py),
  [`pistat/src/pistat/urls.py`](https://github.com/fpgas-online/fpgas.online-site/blob/main/pistat/src/pistat/urls.py),
  [`pibup/src/pibup/urls.py`](https://github.com/fpgas-online/fpgas.online-site/blob/main/pibup/src/pibup/urls.py),
  [`pibdemos/src/pibdemos/urls.py`](https://github.com/fpgas-online/fpgas.online-site/blob/main/pibdemos/src/pibdemos/urls.py)
  and [`ttsite/src/ttsite/urls.py`](https://github.com/fpgas-online/fpgas.online-site/blob/main/ttsite/src/ttsite/urls.py)
  — the URL map for both hosts, and the fact that nothing includes `pibdemos`.
- [`pibfpgas/src/pibfpgas/views.py`](https://github.com/fpgas-online/fpgas.online-site/blob/main/pibfpgas/src/pibfpgas/views.py)
  — the three views, the lookup by `port` alone, the port-as-board-id comment,
  and `tt` calling `one` with a literal 21.
- [`pibfpgas/src/pibfpgas/pis.py`](https://github.com/fpgas-online/fpgas.online-site/blob/main/pibfpgas/src/pibfpgas/pis.py)
  — the `Pi` record, which has replaced `models.py`: the `(switch, port)`
  identity parsed from a registered hostname, and the derived `hostname`, `ip`,
  `ssh_port` and `stream_url` properties for both the flat and the
  per-port-VLAN schemes.
- [`pibfpgas/src/pibfpgas/templates/index.html`](https://github.com/fpgas-online/fpgas.online-site/blob/main/pibfpgas/src/pibfpgas/templates/index.html)
  and [`fpga.html`](https://github.com/fpgas-online/fpgas.online-site/blob/main/pibfpgas/src/pibfpgas/templates/fpga.html)
  — the card grid and its video element; the control, demo, camera, terminal,
  upload, log and cable-colour blocks; the "Accessing directly" commands; the
  empty toolchain hrefs; the wiki links; and the readthedocs assets.
- [`pibfpgas/src/pibfpgas/static/demos.js`](https://github.com/fpgas-online/fpgas.online-site/blob/main/pibfpgas/src/pibfpgas/static/demos.js)
  — the demo buttons sending commands into the terminal rather than to a view,
  and the exact commands.
- [`pistat/src/pistat/static/dcws.js`](https://github.com/fpgas-online/fpgas.online-site/blob/main/pistat/src/pistat/static/dcws.js)
  — which button calls which endpoint (`/snmp/toggle` for Reset, `/snmp/status`
  for Check PoE, `/pistat/ping/pi<N>` for ping), the status check on connect,
  and the automatic terminal reconnect and video reload.
- [`pistat/src/pistat/views.py`](https://github.com/fpgas-online/fpgas.online-site/blob/main/pistat/src/pistat/views.py),
  [`routing.py`](https://github.com/fpgas-online/fpgas.online-site/blob/main/pistat/src/pistat/routing.py)
  and [`consumers.py`](https://github.com/fpgas-online/fpgas.online-site/blob/main/pistat/src/pistat/consumers.py)
  — the group fan-out, the humanising table, the ping loop with its
  `10.21.0.<100+N>` derivation, and the WebSocket path.
- [`pibup/src/pibup/views.py`](https://github.com/fpgas-online/fpgas.online-site/blob/main/pibup/src/pibup/views.py)
  and [`forms.py`](https://github.com/fpgas-online/fpgas.online-site/blob/main/pibup/src/pibup/forms.py)
  — the intended flow (model lookup by port, SFTP write into `Uploads`) and the
  commented-out `run` field the view still reads, which is what breaks the POST.
- [`pibdemos/src/pibdemos/views.py`](https://github.com/fpgas-online/fpgas.online-site/blob/main/pibdemos/src/pibdemos/views.py),
  [`nginx/pibdemos.conf`](https://github.com/fpgas-online/fpgas.online-site/blob/main/pibdemos/nginx/pibdemos.conf)
  and [`README.md`](https://github.com/fpgas-online/fpgas.online-site/blob/main/pibdemos/README.md)
  — the ssh-based demo views, the unused `/demos/` location, and the brainstorm
  README.
- [`pibfpgas/README.md`](https://github.com/fpgas-online/fpgas.online-site/blob/main/pibfpgas/README.md)
  and [`pibup/README.md`](https://github.com/fpgas-online/fpgas.online-site/blob/main/pibup/README.md)
  — the two unedited example-package READMEs.
- [`ttsite/src/ttsite/middleware.py`](https://github.com/fpgas-online/fpgas.online-site/blob/main/ttsite/src/ttsite/middleware.py)
  — the host comparison and the `request.urlconf` switch.
- [`ttsite/src/ttsite/views.py`](https://github.com/fpgas-online/fpgas.online-site/blob/main/ttsite/src/ttsite/views.py)
  — the three board buckets, the per-board Commander flavour, the
  `can_power_cycle` condition on switch 1, the status cache, and the 404/502
  behaviour of the proxies.
- [`ttsite/src/ttsite/docs_links.py`](https://github.com/fpgas-online/fpgas.online-site/blob/main/ttsite/src/ttsite/docs_links.py)
  and the [`index.html`](https://github.com/fpgas-online/fpgas.online-site/blob/main/ttsite/src/ttsite/templates/ttsite/index.html),
  [`board.html`](https://github.com/fpgas-online/fpgas.online-site/blob/main/ttsite/src/ttsite/templates/ttsite/board.html)
  and [`docs.html`](https://github.com/fpgas-online/fpgas.online-site/blob/main/ttsite/src/ttsite/templates/ttsite/docs.html)
  templates — the curated link sections, the "Be nice" text, the board page
  furniture, the gallery and upload form with its 256 KiB cap, and the
  "everyone sees the same board" note.
- [`CLAUDE.md`](https://github.com/fpgas-online/fpgas.online-site/blob/main/CLAUDE.md)
  — the app summaries and the deployment paragraph.

fpgas.online-poe, `main`:

- [`src/snmp_switch/urls.py`](https://github.com/fpgas-online/fpgas.online-poe/blob/main/src/snmp_switch/urls.py)
  and [`views.py`](https://github.com/fpgas-online/fpgas.online-poe/blob/main/src/snmp_switch/views.py)
  — the four power views and the `pistat` notification on every state change.

fpgas.online-infra, `main`:

- [`ansible/roles/site/tasks/main.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/site/tasks/main.yml)
  — the include order of the role.
- [`ansible/roles/site/tasks/fpgas-online-site.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/site/tasks/fpgas-online-site.yml)
  — the two pip installs with `state: forcereinstall`, the app servers and
  `channels-redis` in the same file, and the ordering rationale. The file's only
  comment explains the restart notification, not the flag; why
  `forcereinstall` is needed for a git requirement is these pages' inference,
  flagged as such on [deployment](deployment.md).
- [`ansible/roles/site/tasks/django.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/site/tasks/django.yml)
  — the directories, the copy of the project files out of the wheel and why,
  `local_settings.py` created with `force: false`, the once-generated
  `.secret_key` that Ansible never rotates, the `ALLOWED_HOSTS` and
  `CSRF_TRUSTED_ORIGINS` derivations, the generated `manage.py`, and the
  `migrate` / `collectstatic` / `loaddata` tasks with the fixture history. Which
  tasks carry `notify: restart django services` and which do not is read off the
  task list directly.
- [`ansible/roles/site/tasks/nginx.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/site/tasks/nginx.yml)
  and the [`templates/includes/`](https://github.com/fpgas-online/fpgas.online-infra/tree/main/ansible/roles/site/templates/includes)
  files — the four location includes, the gunicorn socket, the daphne `/ws/`
  proxy and the `/` to `/fpgas` redirect.
- [`ansible/roles/site/tasks/fpgas-online-site.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/site/tasks/fpgas-online-site.yml)
  and [`snmp.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/site/tasks/snmp.yml)
  — the site and PoE packages installed in one `pip` task, so there are no
  per-app task files any more (`snmp.yml` only populates `/etc/environment`).
  [`pistat.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/site/tasks/pistat.yml)
  installs redis and the dnsmasq `send_stat.conf` hook.
- [`ansible/roles/site/templates/vhost.conf.j2`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/site/templates/vhost.conf.j2)
  and [`roles/ttsite/templates/vhost.conf.j2`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/ttsite/templates/vhost.conf.j2)
  / [`ws-board.conf.j2`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/ttsite/templates/ws-board.conf.j2)
  — the default vhost's bare `root` with no `/static/` location and no
  `location /`, against the Tiny Tapeout vhost's `/static/` alias, `/ws/pistat/`,
  `/api/`, `location /` catch-all and `client_max_body_size 1m`, plus the
  generated per-board `location = /ws/board/<slug>/serial` proxies.
- [`ansible/roles/ttsite/tasks/main.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/ttsite/tasks/main.yml),
  [`boards.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/ttsite/tasks/boards.yml),
  [`django.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/ttsite/tasks/django.yml),
  [`embed.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/ttsite/tasks/embed.yml)
  and [`nginx.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/ttsite/tasks/nginx.yml)
  — the checksum assertion, the catalogue render and load, the `TTSITE_*` lines,
  the bundle download and unpack including the legacy flavour, and the webroot
  certificate flow.
- [`ansible/roles/wssh/tasks/main.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/wssh/tasks/main.yml)
  and its nginx include — webssh in its own venv behind a systemd socket, and
  the `/wssh/` location.
- [`ansible/roles/stream_server/tasks/main.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/stream_server/tasks/main.yml),
  [`base.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/stream_server/tasks/base.yml),
  [`back.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/stream_server/tasks/back.yml)
  and the [`pib.conf.j2`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/stream_server/templates/pib.conf.j2)
  / [`live-hls.conf.j2`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/stream_server/templates/live-hls.conf.j2)
  templates — the RTMP modules, the single worker, the publish restriction, the
  tmpfs `fstab` line, and the `/live` location with `no-cache`.
- [`ansible/inventory/group_vars/all/site.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/inventory/group_vars/all/site.yml),
  [`group_vars/all/ttsite.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/inventory/group_vars/all/ttsite.yml),
  [`host_vars/fpgas.online.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/inventory/host_vars/fpgas.online.yml)
  and [`host_vars/ps1.fpgas.online.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/inventory/host_vars/ps1.fpgas.online.yml)
  — `django_dir`, `static_dir`, `django_project_name`, `ttsite_domain` and the
  two `fixture_path` values.
- [`docs/superpowers/runbooks/2026-08-23-tweed-web-deploy.md`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/docs/superpowers/runbooks/2026-08-23-tweed-web-deploy.md)
  — the catalogue path from inventory to `ttsite_loadboards --prune`, the embed
  version and SHA-256 pin, the Phase 2 rollout with embed 0.2.0, and the
  `--tags django` rollback with `local_settings.py` never overwritten.

fpgas.online-gw, `main`:

- [`README.md`](https://github.com/fpgas-online/fpgas.online-gw/blob/main/README.md)
  — the planned endpoints and event stream, the slug-to-address derivation
  living only in the gateway, the `board-access` deployment sketch, and the
  statement that the full API documentation lands with the `impl-api` branch.

fpgas.online-cam, `main`:

- [`README.md`](https://github.com/fpgas-online/fpgas.online-cam/blob/main/README.md)
  — the capture scripts and the deb that feed the RTMP endpoint. It names the
  `cam/pi` role for installation and lists `cam/stream-server` only among the
  infra roles; the gateway-side behaviour on [camera streams](streams-api.md) is from that role itself.
