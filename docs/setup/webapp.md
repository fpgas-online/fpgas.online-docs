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
  These are not server calls: `demos.js` pushes the demo into the browser
  terminal below with `wssh.send()`, one call per line, so a demo is exactly
  what an operator would have typed. Each of the first three sends two lines, a
  `cd` into a directory under `~/Demos` and `./run_demo.sh`; "Check Wire" sends
  four, ending in `python3 t1.py` and `echo $?`.
- **The camera** — the board's HLS stream, played inline.
- **The terminal** — a WebSSH iframe connected to the Pi as the `pi` user,
  filling most of the page.
- **Upload** — a form that is meant to take a file and drop it into the Pi's
  `Uploads` directory over SFTP. It does not work; see
  [Known gaps](#known-gaps).
- **A status log** — a read-only text area fed by the status WebSocket, with a
  box for sending a test message and a "Check PoE" button that reads the switch
  port's power state.
- **Where the board is** — the Pi's location and patch cable colour, so someone
  standing in the room can find it.

Some of that happens without being asked. `dcws.js`, the WebSocket client that
ships with `pistat` but drives this `pibfpgas` page, checks the PoE state as
soon as it connects, reconnects the terminal when the Pi reports that its ssh
server has started, and reloads the video player when the Pi reports its camera
is up — so a board that has just been reset comes back on its own.

Below that is an "Accessing directly" block with the commands to bypass the page
entirely: an ssh command with the board's own forwarded port, the matching `scp`
into `Uploads`, and a playlist URL for a desktop player.

```console
$ ssh -p <port> pi@<site>
$ scp -P <port> * pi@<site>:Uploads
$ vlc https://<site>/live/pi<N>.m3u8
```

The `vlc` line is legacy-only. The template hard-codes `pi<port>` into it, which
is the hostname a board has only on a site still using the flat numbering; on a
per-port-VLAN site the playlist is `pi-sw<switch>-p<port>.m3u8`, which is what
the page's own video element uses. See [Known gaps](#known-gaps).

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
location and cable colour that the templates render. It also ships `demos.js`
and the page CSS, and the fixtures that seed the boards.

**`pistat`** is the live status channel. A `stat/<name>/<status>` request is
turned into a message on the Django Channels group for that board and pushed to
every browser watching it, with a lookup table that expands terse statuses into
sentences ("Arty board detected", "ssh server started", and a warning that a
kernel boot can take two minutes). The `ping` view runs `ping -c 3` at the board
and streams each output line through the same group. The WebSocket end is
`PiStatConsumer`, one group per board name. Neither view is authenticated:
nginx proxies `/pistat/` unconditionally and both views are `@csrf_exempt`, so
anyone who can reach the site can post a status line into a board's log or make
the server ping a board.

**`pibdemos`** is the server-side counterpart of the demo buttons: views that ssh
to a Pi and run `openFPGALoader` or stage a LiteX Linux image. It is in the
repository, but it is not in `INSTALLED_APPS` and no urlconf includes it, so
nothing on the deployed site reaches it — the demo buttons go through the
terminal instead. See [Known gaps](#known-gaps).

**`pibup`** is the upload form. It is meant to take the file and the board's
switch port, look the board's IP up in the `pibfpgas` model, open an SFTP
session to the Pi as `pi`, write the file into `Uploads` and redirect to a
success page. As shipped it cannot: the view reads a form field the form no
longer declares, so the POST raises before the transfer starts. See
[Known gaps](#known-gaps).

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
| `/` | — | a redirect to the board grid. nginx answers first with `301 /fpgas`, no trailing slash; Django's own `RedirectView` on the same path targets `/fpgas/` and is never reached |
| `/fpgas/` | `pibfpgas` | the board grid, one card per board |
| `/fpgas/pi<N>.html` | `pibfpgas` | the board page, `<N>` being the switch port the Pi is plugged into |
| `/fpgas/tt.html` | `pibfpgas` | the legacy Tiny Tapeout page, rendered for port 21 |
| `/pistat/stat/<name>/<status>` | `pistat` | accepts a status from a Pi and fans it out to that board's WebSocket group |
| `/pistat/ping/<name>` | `pistat` | pings the board and streams each line to the group |
| `/pibup/upload` | `pibup` | the upload form; the SFTP write on POST does not work |
| `/pibup/success` | `pibup` | the post-upload confirmation |
| `/snmp/status` | `snmp_switch` | read one port's PoE state |
| `/snmp/toggle` | `snmp_switch` | power-cycle one port |
| `/snmp/toggle_all`, `/snmp/off_all` | `snmp_switch` | the same for every port |
| `/admin/` | Django | the admin site — in the urlconf only. There is no nginx location for it on this host, so it is unreachable here; it is reachable on the Tiny Tapeout host through that vhost's `location /` catch-all |

Three more paths on this host do not come from the urlconf.
`/ws/pistat/<name>/` is the Django Channels WebSocket: nginx proxies `/ws/` to
daphne, which routes it with `pistat/routing.py` rather than `pib/urls.py`.
`/wssh/` is the browser terminal, proxied to the `wssh` role's own service.
`/live/` is the HLS output, served straight from disk — see
[Camera streams](#camera-streams).

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

This host has its own vhost, so the paths beside Django differ. `/static/` is
served from the static root by an `alias` (the default vhost has no such
location); `/ws/pistat/` goes to daphne as on the other host; the shared
`live-hls` include supplies `/live/`; and a generated
`<domain>-ws-boards.conf` adds one `location = /ws/board/<slug>/serial` per
live board, each proxied straight to that board's Pi daemon — which is what the
Commander embed talks to, and is covered in
[The Tiny Tapeout stack](tinytapeout.md). The vhost also caps request bodies at
`client_max_body_size 1m`, comfortably above the 256 KiB the bitstream proxy
accepts.

## Deployment

The application is installed on the gateway by the infra `site` role, which runs
in the `pig` play — see
[What runs on the gateway](gateway.md#what-runs-on-the-gateway) for the
surrounding services and [Deploying](gateway.md#deploying) for the command
lines. The role installs `fpgas-online-site` and `fpgas-online-poe[cli]` into
`/srv/www/pib/venv` straight from their git repositories with pip, at
`state: forcereinstall`. The role does not say why that flag is there; the
requirement is a git URL with no version in it, so a plain install would find it
already satisfied and not take a new commit. The web tier is installed from git
this way; the Pi side, by contrast, arrives as debs from the
[apt repository](../packages.md). The same task file then installs the app
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
[Deploying](gateway.md#deploying).

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
[Web topology at Welland](gateway.md#web-topology-at-welland); do not run
`certbot --nginx` against this host.

## Camera streams

Video never passes through Django. Each Pi with a camera pushes RTMP to the
gateway and the gateway republishes it as HLS under `/live/`: the capture side
is [Camera](pi.md#camera), and the `cam/stream-server` role that does the
republishing is listed under
[What runs on the gateway](gateway.md#what-runs-on-the-gateway). Fragments are
written to a `tmpfs` mount and served with `Cache-Control: no-cache`, and the
same nginx include supplies `/live/` on both vhosts.

All the application contributes is the URL. The board model derives
`stream_url` as `/live/<hostname>.m3u8` — `pi<port>` on a flat-numbered site,
`pi-sw<switch>-p<port>` on a per-port-VLAN one — and the templates drop that
into a video.js `<source>`. Nothing else in the request path is Django's.

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

- **The classic upload form is broken end to end.** `UploadFileForm` declares
  only `file`; its `run` field is commented out. `pibup.pibup` still does
  `run = form.cleaned_data['run']` on a valid POST, so every upload raises
  `KeyError` before the SFTP session is opened. The form renders on the board
  page and the button works — nothing arrives on the Pi. The Tiny Tapeout
  bitstream upload is a different code path and is unaffected.
- **`pibfpgas` looks boards up by port alone.** The `one` view is
  `get_object_or_404(Pi, port=pino)`, and the model has no unique constraint on
  `port`. On a flat-numbered site the port is unique and this is fine; on a
  per-port-VLAN site the identity is `(switch, port)`, so two boards on the same
  port number of different switches are indistinguishable to the URL, and the
  page returns 500 for both: `get_object_or_404` catches only `DoesNotExist`, so
  the `MultipleObjectsReturned` that `QuerySet.get()` raises propagates. The
  URLs are `pi<N>.html` with no switch in them at all.
- **The direct-access `vlc` command is legacy-only.** `fpga.html` hard-codes
  `/live/pi{{pi.port}}.m3u8` in the click-to-copy block while the page's own
  video element uses `pi.stream_url`, which is `/live/pi-sw<s>-p<p>.m3u8` on a
  per-port-VLAN site. Copying the command from a Welland board page gives a
  playlist that does not exist.
- **`/static/` is dead on the default vhost.** That vhost sets
  `root <static_dir>` and has no `location /static/`, so a request for
  `/static/x` resolves to `<static_dir>/static/x` and 404s. The classic
  templates work around it by loading their JavaScript and CSS from the site
  root (`/dcws.js`, `/demos.js`, `/pib.css`) rather than from `STATIC_URL`. The
  Tiny Tapeout vhost has the `alias` the default one is missing, which is why
  the Commander embed and `board.js` load there.
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
- **The board page has empty links.** Two entries under "Toolchains", for
  OpenXC7 and for Vivado, have `href=""` and go nowhere.
- **Two templates pull assets from another project's docs site.** `fpga.html`
  and `tt.html` load jQuery, a stylesheet and a script from
  `f4pga-examples.readthedocs.io`, so the pages depend on an unrelated
  documentation build staying up and serving those exact paths.

:::{todo}
`fpgas.online-site`'s README is out of date on two points and nobody has
decided which way to fix them (read 2026-09-03): it lists `pibdemos` as a live
app, although it is in no `INSTALLED_APPS`, routed by neither `urls.py`, and
given no nginx include by infra — the demo buttons work by typing into the
WebSSH iframe (`demos.js`); and it names only `TTSITE_COMMANDER_VERSION`, while
the code and the `ttsite` role carry a second `TTSITE_COMMANDER_LEGACY_VERSION`
bundle (see [Deployment](#deployment)). Either the README follows the code or
the code follows the README. The four code faults listed above — the broken
classic upload form, the unauthenticated `csrf_exempt` `/pistat/` views,
`pibfpgas.views.one` looking boards up by port alone, and `fpga.html`'s
hard-coded legacy `vlc .../live/pi<N>.m3u8` URL — are open the same way: fix
them in `fpgas.online-site` or record that the classic site is frozen.
:::

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
- [`pibfpgas/src/pibfpgas/models.py`](https://github.com/fpgas-online/fpgas.online-site/blob/main/pibfpgas/src/pibfpgas/models.py)
  — the `(switch, port)` identity, the absence of a unique constraint on `port`,
  and the derived `hostname`, `ip`, `ssh_port` and `stream_url` properties for
  both the flat and the per-port-VLAN schemes.
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
  `forcereinstall` is needed for a git requirement is this page's inference,
  flagged as such above.
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
- [`ansible/roles/site/tasks/pibup.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/site/tasks/pibup.yml),
  [`pibfpgas.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/site/tasks/pibfpgas.yml),
  [`pibdemos.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/site/tasks/pibdemos.yml)
  and [`snmp.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/site/tasks/snmp.yml)
  — that these per-app task files install nothing themselves, the pip install
  being handled in `fpgas-online-site.yml`.
  [`pistat.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/site/tasks/pistat.yml)
  is the exception: it installs redis and the dnsmasq `send_stat.conf` hook.
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
  — the capture scripts and the deb that feed the RTMP endpoint. It names the
  `cam/pi` role for installation and lists `cam/stream-server` only among the
  infra roles; the gateway-side behaviour above is from that role itself.
