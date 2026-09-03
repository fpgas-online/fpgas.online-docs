# The web application

One Django project, `pib`, is the whole web tier. On `fpgas.online` and the
per-site names such as `ps1.fpgas.online` and `welland.fpgas.online` it serves
the classic board pages: a grid of boards, one page each, a camera feed and a
terminal. On `tinytapeout.fpgas.online` the same process serves the Tiny Tapeout
catalogue instead, chosen by the `Host` header alone. Nothing on either host
asks anyone to log in and nothing reserves a board. This page covers what a
visitor sees, which Django apps the project is made of, the URL map, and how the
`site` role puts it on the gateway.

## What a user sees

The front page of a site is the board grid. Each board gets a card with its
hostname, the FPGA board fitted to it, a live HLS camera thumbnail playing
through video.js, and a "Use this FPGA" link to the board page. Nothing on the
card is interactive beyond the video controls. Which boards are on it is a site
fact, not a platform one: the public grid is
[PS1's](../sites/ps1.md#public-site), and Welland's boards are listed under
[Hosts and boards](../sites/welland.md#hosts-and-boards).

The board page (`fpga.html`) is one screen with everything on it:

- **Pi controls** — "Reset" power-cycles the board's switch port, "reconnect"
  reopens the status WebSocket, "reset video player" reloads the HLS player,
  "reset ssh" reloads the terminal, and "ping" asks the server to ping the Pi
  and stream the output back.
- **Demos** — "Blink LEDs", "Load MicroPython", "Boot Linux" and "Check Wire".
  These are not server calls: `demos.js` types the demo commands into the
  browser terminal below, so a demo is exactly what an operator would have typed
  (`cd ~/Demos/counter_test && ./run_demo.sh`, and for the wire check
  `openFPGALoader -b arty top.bit` followed by `python3 t1.py`).
- **The camera** — the board's HLS stream, played inline.
- **The terminal** — a WebSSH iframe connected to the Pi as the `pi` user,
  filling most of the page.
- **Upload** — a form that takes a file and drops it into the Pi's `Uploads`
  directory over SFTP, optionally running it.
- **A status log** — a read-only text area fed by the status WebSocket, with a
  box for sending a test message and a "Check PoE" button that reads the switch
  port's power state.
- **Where the board is** — the Pi's location and patch cable colour, so someone
  standing in the room can find it.

Some of that happens without being asked. The page's WebSocket client checks the
PoE state as soon as it connects, reconnects the terminal when the Pi reports
that its ssh server has started, and reloads the video player when the Pi
reports its camera is up — so a board that has just been reset comes back on its
own.

Below that is an "Accessing directly" block with the commands to bypass the page
entirely: an ssh command with the board's own forwarded port, the matching `scp`
into `Uploads`, and the playlist URL for a desktop player.

```console
$ ssh -p <port> pi@<site>
$ scp -P <port> * pi@<site>:Uploads
$ vlc https://<site>/live/pi<N>.m3u8
```

The Tiny Tapeout board page is laid out the same way but built from different
parts — the chip, the RP2040 and the Pi-side daemon behind it are
[The Tiny Tapeout stack](tinytapeout.md). What the page itself shows is the
board's camera beside an embedded Commander app, a status pill polled from
`status.json`, a "Power-cycle board" button (only for boards on the first
switch, because the PoE view drives that switch alone), a "Reset video" button,
an "About this board" panel listing the PCB, the PMODs fitted and where the
board lives, and a status log. On boards of kind `fpga` there is also a
gallery of the designs currently on the board with a "Run" button each, and an
"Upload your own bitstream" form capped at 256 KiB.

None of this is gated. There is no login, no account and no reservation: anyone
who loads the page can reset a board, run a demo, or type into its terminal, and
several people can be doing that to the same board at the same time. The Tiny
Tapeout index says so in as many words — "Anyone can drive these boards — no
login required. Be nice: others may be driving the same board at the same time."
— and the bitstream upload help repeats it: "everyone sees the same board".

## Applications

**`pibfpgas`** owns the board model and the classic pages. It has three views:
the grid, one board by switch port, and a hard-coded Tiny Tapeout variant. The
board record is what supplies the hostname, IP, stream URL, forwarded ssh port,
location and cable colour that the templates render. It also ships the page
JavaScript and the fixtures that seed the boards.

**`pistat`** is the live status channel. A `stat/<name>/<status>` request from
anywhere on the Pi network is turned into a message on the Django Channels group
for that board and pushed to every browser watching it, with a lookup table that
expands terse statuses into sentences ("Arty board detected", "ssh server
started", and a warning that a kernel boot can take two minutes). The `ping`
view runs `ping -c 3` at the board and streams each output line through the same
group. The WebSocket end is `PiStatConsumer`, one group per board name.

**`pibdemos`** is the server-side counterpart of the demo buttons: views that ssh
to a Pi and run `openFPGALoader` or stage a LiteX Linux image. It is in the
repository, but it is not in `INSTALLED_APPS` and no urlconf includes it, so
nothing on the deployed site reaches it — the demo buttons go through the
terminal instead. See [Known gaps](#known-gaps).

**`pibup`** is the upload form. It takes the file and the board's switch port,
looks the board's IP up in the `pibfpgas` model, opens an SFTP session to the Pi
as `pi` and writes the file into `Uploads`, then redirects to a success page.

**`ttsite`** is the Tiny Tapeout catalogue: an index that buckets boards into
ASIC, FPGA-emulation and KianV sections, a board page, a curated documentation
index (a static list of links to Tiny Tapeout's own docs, the Commander fork and
this instance's design spec), a cached `status.json` health probe, and three
thin proxies to the Pi-side daemon for the design gallery and bitstream upload.
The proxies pass the daemon's status code and JSON body through unchanged, cache
successful reads for a few seconds, and answer 404 for a board that is not live
or not an FPGA board and 502 when the Pi cannot be reached.

**`snmp_switch`** is not in this repository at all: it comes from the
`fpgas-online-poe` package, installed as a dependency, and provides the power
views — read a port's state, toggle one port, toggle or turn off all of them.
Every power change is also announced on the board's `pistat` group, so the
status log on the page narrates the power cycle. The switch side of that is
[PoE power control](network.md#poe-power-control).

Routing between the two faces of the site is done by host name. The middleware
`ttsite.middleware.TTSiteHostMiddleware` runs first in the middleware list; it
compares the request's host, minus any port and case-folded, against the
`TTSITE_HOST` setting, and on a match points `request.urlconf` at `ttsite.urls`.
Every other host is left alone and keeps the project urlconf. `TTSITE_HOST`
defaults to `tinytapeout.fpgas.online` in `pib/settings.py` and is written into
`local_settings.py` by the `ttsite` role. One process, one database, two URL
maps.

## URL map

Default hosts (`fpgas.online`, `<site>.fpgas.online`), from `pib/urls.py` and
the apps it includes:

| Path | App | What it serves |
| --- | --- | --- |
| `/` | — | redirect to `/fpgas/` (nginx returns the 301; Django has a `RedirectView` for the same path) |
| `/fpgas/` | `pibfpgas` | the board grid, one card per board |
| `/fpgas/pi<N>.html` | `pibfpgas` | the board page, `<N>` being the switch port the Pi is plugged into |
| `/fpgas/tt.html` | `pibfpgas` | the legacy Tiny Tapeout page, rendered for port 21 |
| `/pistat/stat/<name>/<status>` | `pistat` | accepts a status from a Pi and fans it out to that board's WebSocket group |
| `/pistat/ping/<name>` | `pistat` | pings the board and streams each line to the group |
| `/pibup/upload` | `pibup` | the upload form, and the SFTP write on POST |
| `/pibup/success` | `pibup` | the post-upload confirmation |
| `/snmp/status` | `snmp_switch` | read one port's PoE state |
| `/snmp/toggle` | `snmp_switch` | power-cycle one port |
| `/snmp/toggle_all`, `/snmp/off_all` | `snmp_switch` | the same for every port |
| `/admin/` | Django | the admin site |

Three more paths on the same host are served beside Django rather than by it:
`/ws/pistat/<name>/` is the status WebSocket, routed by `pistat/routing.py` and
proxied to daphne; `/wssh/` is the browser terminal from the `wssh` role; and
`/live/` is the HLS output described under [Camera streams](#camera-streams).

Tiny Tapeout host (`tinytapeout.fpgas.online`), from `ttsite/urls.py`:

| Path | App | What it serves |
| --- | --- | --- |
| `/` | `ttsite` | the catalogue, grouped into ASIC, FPGA emulation and KianV |
| `/board/<slug>/` | `ttsite` | the board page with camera, Commander embed and, on FPGA boards, the design gallery |
| `/board/<slug>/status.json` | `ttsite` | cached health probe of the board's daemon |
| `/docs/` | `ttsite` | the curated documentation index |
| `/api/board/<slug>/designs` | `ttsite` | proxy for the daemon's design list |
| `/api/board/<slug>/designs/<name>/enable` | `ttsite` | proxy that loads one design |
| `/api/board/<slug>/bitstream` | `ttsite` | proxy that uploads a bitstream |
| `/pistat/…`, `/pibup/…`, `/snmp/…`, `/admin/` | as above | re-included so the existing apps keep working on this host |

## Deployment

The application is installed on the gateway by the infra `site` role, which runs
in the `pig` play — see
[What runs on the gateway](gateway.md#what-runs-on-the-gateway) for the
surrounding services and [Deploying](gateway.md#deploying) for the command
lines. The role installs `fpgas-online-site` and `fpgas-online-poe[cli]` into
`/srv/www/pib/venv` straight from their git repositories with pip, at
`state: forcereinstall` — the requirement is a git URL with no version in it, so
this is what makes a re-run take a new commit. The web tier is installed from
git this way; the Pi side, by contrast, arrives as debs from the
[apt repository](../packages.md). The app servers — gunicorn, uvicorn and daphne — plus
`channels-redis` are installed into the same venv first, deliberately, so that
gunicorn's first start with the uvicorn worker class cannot race the uvicorn
install. `channels_redis` is a settings dependency the site package does not
declare.

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
prefixed.

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

Every task that changes code or settings notifies a `restart django services`
handler, because a new wheel means new templates and new code that the running
gunicorn, daphne and uvicorn keep serving the old versions of until they are
restarted. `--tags django` narrows a deploy to the application, and is also the
rollback path: pip an older `fpgas-online-site` reference into the venv and
re-run with that tag. `local_settings.py` survives both directions.

nginx routes to the application through per-app location includes rendered by
the same role — one file each for `pibfpgas`, `pistat`, `pibup` and
`snmp_switch`. All of them proxy to gunicorn on `/run/gunicorn.sock`; the
`pistat` include additionally proxies `/ws/` to daphne on port 8085 with the
upgrade headers, and the `pibfpgas` include carries the `/` to `/fpgas` redirect.
The vhost itself is nothing but an `include` of that directory, so an app that
has no include is unreachable no matter what the urlconf says.

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
[Web topology at Welland](gateway.md#web-topology-at-welland); do not run
`certbot --nginx` against this host.

## Camera streams

Video is not Django's problem. Each Pi with a camera pushes an RTMP stream to
the gateway, which republishes it as HLS under `/live/` — the capture side is
[Camera](pi.md#camera), and the gateway side is the `cam/stream-server` role
listed in [What runs on the gateway](gateway.md#what-runs-on-the-gateway). The
role installs nginx's RTMP and fancyindex modules, pins nginx to a single worker
(the RTMP module needs it), and accepts publishes only from the Pi network.
Fragments land in `/…/hls/source`, which is mounted `tmpfs` from `/etc/fstab` so
the constant rewriting never touches the disk, and are served from `/live` with
`Cache-Control: no-cache` because a live playlist is stale as soon as it is
written. All the templates do is point a video.js `<source>` at the board's
playlist.

## Gateway API

A separate service, `fpgas.online-gw`, is meant to take over everything the web
tier currently does by reaching into the Pi network itself: board inventory with
absolute stream, serial and API URLs, per-board pass-through to the Pi daemon,
PoE control by board slug, and a WebSocket event stream fed by the `pistat`
pings, the DHCP hook and the netconsole listener. The address derivation from a
board slug would live only there, so that a front end — the co-located site or a
remote aggregator — never touches the private network or the switch credentials.
It is planned, not deployed: `main` in that repository is a scaffold, and the
README says the API and its configuration land with the implementation on the
`impl-api` branch. There is nothing to document yet beyond the intent.

## Known gaps

- **`pistat`'s ping view assumes the legacy names.** It derives the address by
  slicing the digits off a `pi<N>` name and building `10.21.0.<100+N>`, so it
  works only for hosts on the flat network under the old numbering. The
  hyphenated per-site hostnames are not supported, and the site README says so.
  The page's own JavaScript makes the same assumption: it builds `pi<N>` from
  the switch port for both the WebSocket group and the ping URL.
- **`pibdemos` is installed but not wired up.** It is absent from
  `INSTALLED_APPS`, no urlconf includes it, and the infra role renders no nginx
  location for it even though the app carries a `/demos/` include of its own.
  Its README is still the brainstorm it started as ("Give the user some push
  button candy", "boot micro python (no idea how they will interact with
  it...)"), and the role file that would deploy it says only that the pip
  install is handled elsewhere. The demo buttons work through the terminal, so
  nothing is visibly broken; the app is just dead code with a README that reads
  like a plan.
- **Two READMEs are still the setuptools example.** `pibfpgas/README.md` and
  `pibup/README.md` both read "This is a simple example package. You can use
  Github-flavored Markdown to write your content."
- **Templates still link to the retired wiki.** The board grid's "Get Started"
  and "Behind the scenes" buttons point at `github.com/CarlFK/pici/wiki`, and
  `tt.html`'s "Edit this page" link and its "Host" section point at the
  monorepo's own paths, which no longer exist after the split.
- **`tt.html` is hard-coded to one board.** The `tt` view is
  `return one(request, 21, 'tt.html')` — port 21, literally. It predates
  `ttsite`, which does the same job from the database.
- **The Arty page has empty links.** Two entries under "Toolchains", for OpenXC7
  and for Vivado, have `href=""` and go nowhere.
- **Two templates pull assets from another project's docs site.** `fpga.html`
  and `tt.html` load jQuery, a stylesheet and a script from
  `f4pga-examples.readthedocs.io`, so the pages depend on an unrelated
  documentation build staying up and serving those exact paths.

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
  — the three views, the port-as-board-id comment, and `tt` calling `one` with a
  literal 21.
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
  — the form, the model lookup by port and the SFTP write into `Uploads`.
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
  — the two pip installs, `state: forcereinstall` with its comment, the app
  servers and `channels-redis`, and the ordering rationale.
- [`ansible/roles/site/tasks/django.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/site/tasks/django.yml)
  — the directories, the copy of the project files out of the wheel and why,
  `local_settings.py` created with `force: false`, the `ALLOWED_HOSTS` and
  `CSRF_TRUSTED_ORIGINS` derivations, the generated `manage.py`, and the
  `migrate` / `collectstatic` / `loaddata` tasks with the fixture history.
- [`ansible/roles/site/tasks/nginx.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/site/tasks/nginx.yml)
  and the [`templates/includes/`](https://github.com/fpgas-online/fpgas.online-infra/tree/main/ansible/roles/site/templates/includes)
  files — the four location includes, the gunicorn socket, the daphne `/ws/`
  proxy and the `/` to `/fpgas` redirect.
- [`ansible/roles/site/tasks/pistat.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/site/tasks/pistat.yml),
  [`pibup.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/site/tasks/pibup.yml),
  [`pibfpgas.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/site/tasks/pibfpgas.yml),
  [`pibdemos.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/site/tasks/pibdemos.yml)
  and [`snmp.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/site/tasks/snmp.yml)
  — that the per-app task files carry no installs of their own.
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
- [`ansible/roles/cam/stream-server/tasks/main.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/cam/stream-server/tasks/main.yml),
  [`base.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/cam/stream-server/tasks/base.yml),
  [`back.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/cam/stream-server/tasks/back.yml)
  and the [`pib.conf.j2`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/cam/stream-server/templates/pib.conf.j2)
  / [`live-hls.conf.j2`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/cam/stream-server/templates/live-hls.conf.j2)
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
  — the capture scripts that feed the RTMP endpoint, and that the gateway side
  is the `cam/stream-server` role.
