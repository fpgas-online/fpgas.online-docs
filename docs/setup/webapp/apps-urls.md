# The web application: its Django apps and URL map

**You are working on the code and want the Django apps the project is made of and which URL goes where.**

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
terminal instead. See [Known gaps](known-gaps.md#known-gaps).

**`pibup`** is the upload form. It is meant to take the file and the board's
switch port, look the board's IP up in the `pibfpgas` model, open an SFTP
session to the Pi as `pi`, write the file into `Uploads` and redirect to a
success page. As shipped it cannot: the view reads a form field the form no
longer declares, so the POST raises before the transfer starts. See
[Known gaps](known-gaps.md#known-gaps).

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
[PoE power control](../network.md#poe-power-control).

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
[Camera streams](streams-api.md#camera-streams).

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
[The Tiny Tapeout stack](../tinytapeout.md). The vhost also caps request bodies at
`client_max_body_size 1m`, comfortably above the 256 KiB the bitstream proxy
accepts.
