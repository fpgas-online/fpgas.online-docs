# The Tiny Tapeout stack

`https://tinytapeout.fpgas.online/` is the public front end for the Tiny Tapeout
boards in the fleet. Every board page carries a live camera and an embedded
Tiny Tapeout Commander — a fork of the upstream app whose only hardware
dependency is a byte stream, so it drives a board over a WebSocket instead of
WebSerial. The bytes come from `fpgas-tt`, a daemon on that board's Raspberry Pi
which owns the demo board's USB serial port and fans it out to every viewer at
once. This page covers the software: the daemon, the board catalogue the daemon
and the site share, the demo bitstreams, and the Commander fork. The hardware is
on [Tiny Tapeout FPGA demo board](../boards/tt-fpga.md) and
[Tiny Tapeout ASIC demo boards](../boards/tt-asic.md); the Django side of the
site is [The web application](webapp.md).

## Overview

The whole path from browser to chip, redrawn from the design spec with the
Welland host and switch names generalised:

```
browser ──https──▶ gateway (nginx, vhost tinytapeout.fpgas.online)
                    ├─ /, /board/<slug>/, /docs/      Django `ttsite` (gunicorn)
                    ├─ /static/tt-commander/<ver>/    built Commander embed bundle
                    ├─ /live/<pi-hostname>.m3u8       existing HLS camera (unchanged)
                    ├─ /ws/pistat/<pi>/               existing daphne status socket (unchanged)
                    ├─ /ws/board/<slug>/serial  ─ws─▶ 10.21.<s>.<p>:8765/serial   fpgas-tt daemon on the Pi
                    └─ /api/board/<slug>/…     ─http▶ 10.21.<s>.<p>:8765/…            │
                                                                                      ├─ /dev/ttboard → RP2040 (MicroPython SDK) → TT chip / iCE40
                  snmp toggle (existing) ──▶ switch PoE ──▶ Pi power                  └─ (later) PMOD HAT GPIO, Verilog build
```

Four properties of that picture matter more than the boxes:

- **No address is stored anywhere.** A board is identified by `(switch, port)`
  and everything else is derived from it — hostname `pi-sw<s>-p<p>`, address
  `10.21.<s>.<p>`, camera stream `/live/pi-sw<s>-p<p>.m3u8`. That is the
  per-port VLAN scheme in [Two addressing schemes](network.md#two-addressing-schemes);
  the older `10.21.0.100+port` convention is not used on this host.
- **The gateway runs nginx and Django only.** The WebSocket path is a plain
  nginx proxy with no Python in the data path; the HTTP API paths are thin
  Django proxies that do the slug-to-address lookup, apply size limits and
  enforce CSRF. Nothing compiles and nothing opens a serial port there.
- **The Pi runs the daemon.** `fpgas-tt` comes from the `fpgas-online-tt` deb,
  baked into the shared read-only NFS root; nothing is installed or fetched
  after boot.
- **Port 8765 is not public.** The daemon listens on `0.0.0.0:8765` and only the
  gateway can reach it, because each Pi sits alone in its own port VLAN and the
  `firewall` role allows the gateway to those interfaces on tcp/8765 while the
  Pis still cannot reach each other.

## The fpgas-tt daemon

`fpgas-tt` opens `/dev/ttboard` at 115200 baud and keeps retrying every second
until a board appears, so a Pi whose board is unplugged simply waits. The device
node is a udev symlink for the demo board's RP2040/RP2350 USB-CDC port; the rule
that creates it ships in the same package and is quoted under
[Serial consoles](pi.md#serial-consoles). What the daemon holding that port open
means for anything else that wants it — and how to take it back, and why to give
it straight back — is under
[Serial port ownership](../boards/tt-fpga.md#serial-port-ownership) and
[Connection to the Pi](../boards/tt-asic.md#connection-to-the-pi).

One object owns that port. `WS /serial` is the bridge: every connected client
receives the same bytes from the board and may write bytes to it, with no
locking and no arbitration. A client whose send queue falls more than 256 KiB
behind is dropped, so the board reader is never blocked by a slow browser. On
shutdown every open `/serial` socket is closed with code 1001
(`server shutdown`); when the board goes away they are closed with 1011
(`board disconnected`) and the daemon starts re-opening the device once a
second. Internal tasks are clients of the same bridge, never a second owner of
the port — which is why a design load and a human typing in the terminal can
collide, and the task is the one that fails.

`GET /health` answers `{"board": {"present", "device", "vid_pid"}, "kind",
"slug", "switch", "port", "hostname", "clients", "uptime_s", "version",
"config_error"}`. `vid_pid` is the board's USB `idVendor:idProduct` read from
sysfs, `null` when the device is not a USB tty; `config_error` is non-null when
the board map could not be read and the daemon fell back to a plain `asic`
bridge instead of restart-looping. The site's `/board/<slug>/status.json` is a
cached summary of it, with `reachable` added, which is what the status pill on a
board page reflects.

The daemon works out which board it is on its own: it reads its short hostname,
decomposes it into `(switch, port)`, and looks itself up in
`/etc/fpgas-online/tt-boards.yaml` to get its `slug` and `kind`. A hostname that
is not in the catalogue leaves it a plain `asic` bridge. There are no per-Pi
configuration files and no boot-time fetches.

### FPGA-board routes

On a `kind: fpga` board four more routes manage bitstreams over the board's raw
MicroPython REPL, each run through the bridge like any other client:

| Route | Description |
|-------|-------------|
| `GET /designs` | `{"enabled": str\|null, "designs": [{"name", "title", "author", "description", "docs_url", "repo_url", "clock_hz", "pinout", "source": "demo"\|"upload"}, ...]}` — every `.bin` under `/bitstreams`, demo metadata merged in from `index.json` when it matches a name |
| `POST /designs/{name}/enable` | body `{"clock_hz": int}` (optional) → `{"enabled": name, "clock_hz": int\|null}`; bounded to a 25 s overall REPL deadline (below the site proxy's own 30 s/45 s read timeouts, so a stuck SPI load still gets a clean 502 from this daemon instead of the client seeing a raw connection reset) |
| `POST /bitstream` | multipart form (`name`, `file`) → `201 {"name", "size", "evicted": [str, ...]}`; rejects names that collide with a demo, non-`[a-z0-9_]{1,40}` names, oversize (>256 KiB) or non-iCE40 files (400); evicts the oldest non-demo uploads first so at most 16 uploads remain |
| `POST /demos/sync` | (re)writes any demo whose sha1 no longer matches a manifest kept on the board (`/bitstreams/.demos.json`) — a same-size content update is still noticed, unlike a plain size comparison → `{"synced": [str, ...], "skipped": [str, ...]}`; waits up to ~1 s for a running task before answering 409 |

A non-`fpga` board answers `404 {"error": "not an fpga board", "detail": ""}` on
all four. Every other failure has the same `{"error", "detail"}` shape with an
honest status: `503` board not present, `409` another task is running (or a
demo-name collision on upload), `404` no such design — including a name that
could never be valid, rejected before the board is asked — `502` REPL task
failed with the board's traceback in `detail` (non-printable bytes stripped and
truncated), `400` for validation failures and `500` for anything unexpected.
Nothing is swallowed and nothing returns a bare crash page.

`--demos-dir` (default `/usr/share/fpgas-tt/demos`) points at the demo bitstream
set. On an `fpga` board the daemon runs one `/demos/sync` itself in the
background once the board is first present, retrying every 30 s on failure, so a
freshly baked image comes up with the demo set already on the board.

### Installation

The daemon is a deb, and nobody installs it by hand. `onpi/tasks/tt.yml` adds
`fpgas-online-tt` and `fpgas-online-tt-demos` to the shared Pi NFS root and
enables `fpgas-tt.service` there, and it does that in the provisioning chroot on
the gateway rather than on a booted Pi. Installing either package on a running
Pi would write into the tmpfs overlay above that read-only root and be gone at
the next reboot, and enabling the unit by hand would only duplicate what Ansible
already manages. What the two packages contain, how the install is gated, and
how `fpgas-tt.service` is invoked are in the [package](pi.md#packages) and
[service](pi.md#services) tables on [What runs on a Pi host](pi.md).

## The board catalogue

One file describes every board: `/etc/fpgas-online/tt-boards.yaml`. The infra
`ttsite` role renders it onto the gateway for the web tier, and
`onpi/tasks/tt.yml` bakes it into the Pi NFS root from the same template, so the
daemon and the site always agree on what a slug means. It is a list of mappings
with these keys:

| Key | What it carries |
| --- | --- |
| `slug` | The board's identity: its `/board/<slug>/` page, its `/ws/board/<slug>/serial` socket, and its `/api/board/<slug>/` proxy base. |
| `switch`, `port` | Which switch port the Pi is plugged into. Everything on the network side is derived from the pair. A null `port` means the slot has no Pi yet. |
| `kind` | `asic`, `kianv` or `fpga`. It selects the daemon routes that exist, the Commander behaviour, and the extras on the board page. |
| `shuttle` | Which Tiny Tapeout shuttle the chip came from; blank on FPGA emulation boards. |
| `title`, `blurb`, `description`, `pcb` | Display text for the tile and the board info card. |
| `pmods`, `links` | Lists of `{name, url, note}` and `{label, url}` rendered on the board page. |
| `enabled` | False keeps the slot rendered as "coming soon". |
| `sort_order` | Ordering within the board's section on the landing page. |
| `commander` | Selects a non-default Commander embed flavour for a board whose firmware the current bundle cannot drive. |

Note what is **not** in there: no IP address, no port 8765, and no design list.
Addresses are derived from `(switch, port)`, and designs are read live from the
daemon rather than modelled in the database.

On the gateway the file is loaded into the site database by a management
command:

```console
$ uv run python manage.py ttsite_loadboards /etc/fpgas-online/tt-boards.yaml --prune
```

The load is an idempotent upsert by slug. `--prune` additionally deletes rows
whose slug has vanished from the file, and refuses to run against an empty board
list unless `--allow-empty` is given as well — so a template that renders to
nothing cannot silently empty the catalogue. The path the role takes to get
there, and the interpreter to use on the deploy host, are under
[Deployment](webapp.md#deployment).

The mapping runs both ways. The daemon uses hostname → catalogue to learn its
own slug and kind; the site uses catalogue → `(switch, port)` to build the Pi's
address for the WebSocket and API proxies, and to hand the board's switch port
to the PoE views behind the "Power-cycle board" button — the same
`/snmp/toggle` endpoint the classic pages use, described under
[PoE power control](network.md#poe-power-control).

## Demo bitstreams

FPGA emulation boards ship with a curated set of ready-to-load bitstreams so a
visitor can run something without synthesising anything. They live in the
`tinytapeout-fpga-demos` repository, are built in CI, and reach the Pi as the
`fpgas-online-tt-demos` deb, which installs `index.json` and one `.bin` per
design under `/usr/share/fpgas-tt/demos/`. Nothing is fetched at run time; the
daemon syncs the set onto the board itself.

The current set is five designs: `tt_um_factory_test`, `tt_um_counter_7seg`,
`tt_um_pwm_breathe`, `tt_um_uart_hello` and `tt_um_vga_pattern`. Each one is a
normal Tiny Tapeout template project — `info.yaml`, `src/`, `docs/info.md` and
an optional cocotb `test/` — so it is a valid starting point for a real shuttle
submission, built here instead of taped out.

The build turns each project into an iCE40UP5K bitstream. A harness copied from
`TinyTapeout/tt-fpga-compiler` (`tt_fpga_top.v` plus a FabricFox `.pcf`) wraps
the demo's top module so it can be synthesised standalone, and then:

```console
$ yosys -p "synth_ice40 -top tt_fpga_top -json out.json" tt_fpga_top.v <sources>
$ nextpnr-ice40 --up5k --package sg48 --pcf harness/tt_fpga_fabricfox.pcf --pcf-allow-unconstrained --json out.json --asc out.asc
$ icepack out.asc <name>.bin
```

The resulting `.bin` is checked for the iCE40 bitstream preamble
`7E AA 99 7E` before it is accepted. The same tool writes `bundle/index.json` —
the shape the daemon reads back from `/usr/share/fpgas-tt/demos/index.json` —
and `bundle/VERSION`. CI lints, runs the index-derivation unit tests, runs the
cocotb bench of every demo that has one, and builds the full bundle and a trial
deb on every push.

:::{todo}
The design spec lists six demos plus a stretch goal (`tt_um_wokwi_example` and
`tt_um_kianv_fpga` in addition to the five above), and describes the build as
`tt_fpga.py harden` per demo. What shipped is the five designs above, built by
the repository's own `tools/build.py` with the `tt-fpga-compiler` harness.
Reconcile `docs/superpowers/specs/2026-08-22-tinytapeout-fpgas-online-design.md`
§8 with `tinytapeout-fpga-demos/README.md`, or record that the spec is
superseded there.
:::

## The Commander fork

The embedded Commander is `fpgas-online/tt-commander-app`, a fork of
`TinyTapeout/tt-commander-app`. Its `main` branch mirrors upstream untouched;
`fpgas-online` is the default branch and every change lands there, additively,
behind a transport abstraction so it stays offerable upstream.

A host page mounts the widget with `mountCommander(el, opts)`, which returns
`{ unmount, refreshDesigns }`. `unmount()` tears the widget down and clears the
mount point. `refreshDesigns()` re-fetches the daemon's design list into the
running widget, so an upload made elsewhere on the page — the site's own upload
form — shows up in the project dropdown and the pinout tab without a remount; on
non-`fpga` boards it resolves immediately and does nothing. The options:

| option      | meaning |
| ----------- | ------- |
| `transport` | `{ kind: 'websocket', url }` — the daemon's `WS /serial`. **WebSocket-only**: WebSerial needs a user gesture per page load, which an embedded widget cannot promise, so the standalone app keeps that job. `WebSocketImpl` may be set to a `WebSocket` double **in tests only** (see `src/transport/testing/FakeWebSocket.ts`). |
| `board`     | `{ slug, kind, shuttle? }` — board identity (`apiBase` is its own option, not part of this). `kind` is `'asic'` or `'fpga'` (`'kianv'` is phase 3, not yet implemented). |
| `apiBase`   | e.g. `/api/board/<slug>`; required for `kind` `fpga`/`kianv`. |
| `chrome`    | `{ header, footer }`, both default `false` when embedded. |
| `admin`     | shows maintenance controls (Reset to Bootloader); default `false`. |
| `reconnect` | `{ minDelayMs, maxDelayMs }`; defaults 1 s / 30 s. |

The embed deliberately keeps to itself: it injects no global styles and ships no
CSS reset, scoping what it needs to its own root element, and it does not fetch
web fonts — the host page has to provide Roboto.

On an `fpga` board the Config tab is backed by the daemon instead of the Tiny
Tapeout shuttle index. The project list comes from `GET ${apiBase}/designs`,
fetched on mount, again on every connect and reconnect, and on
`refreshDesigns()`; a failure shows a **Retry** button. "Load design" issues
`POST ${apiBase}/designs/<name>/enable` and stays busy until the daemon answers,
so a slow reprogram cannot be fired twice, and a rejection appears as a
dismissible alert. There is no mux index or subtile field, because the daemon
addresses designs by name and the selection is re-derived from the daemon's
`enabled` name after every load. The pinout tab renders from the selected
design's own metadata with no fetch to `index.tinytapeout.com`, and only the
`docs_url` and `repo_url` the daemon supplies are linked — an FPGA design has no
chip page and no feedback form.

The wire protocol on `WS /serial` is small: binary frames are board bytes in
both directions; server-to-client text frames are JSON events such as
`{"event":"board","present":true,"device":"/dev/ttboard"}` and
`{"event":"error","error":"board not present"}`; the close codes are
`1011 board disconnected`, `1008 client too slow` and `1001 server shutdown`. On
a close the embed shows the code and reason, tears the old device down, and
retries with exponential back-off — `minDelayMs * 2 ** (attempt - 1)` capped at
`maxDelayMs`, with ±20 % jitter so a roomful of viewers does not stampede a
daemon that has just come back. The attempt counter only resets after a
connection that stayed up for 10 s, so a board that flaps backs off instead of
hammering. Each new connection re-runs the REPL bootstrap.

Nothing arbitrates who is driving. The fork's README puts it plainly:

> The daemon fans the board's bytes out to everyone connected, so **everyone
> connected sees and can drive the same REPL** — one viewer's `select_design()`
> changes what every other viewer sees. The Commander already tolerates
> unsolicited `tt.*=` lines, so state converges instead of fighting. Nothing
> arbitrates access; the host page should say so, e.g. "other people may be
> driving this board too".

Mount one widget per page. The board, shuttle and design stores are
module-global, so a second `mountCommander(...)` on the same page shares them
with the first and the two fight over the selected design.

Releases are tagged `embed-vX.Y.Z` on the `fpgas-online` branch and publish a
GitHub Release carrying `tt-commander-embed-X.Y.Z.tar.gz` and its `.sha256`,
which the infra `ttsite` role downloads and unpacks under the static root — no
node on the gateway. Two versions exist: **0.1.0**, the initial fork with the
`SerialTransport` seam, the `WebSocketTransport` bridge and the embeddable build
(`asic` boards only), and **0.2.0**, which adds the `fpga` kind, the
`refreshDesigns()` handle, and the reconnect and firmware-version fixes from the
fork's issue #7. Which version a deployment serves is pinned by the
`TTSITE_COMMANDER_VERSION` setting; when it is empty the board pages show a
"bundle not deployed" notice instead of the embed. FPGA boards need 0.2.0 or
newer, because the design gallery calls `refreshDesigns()` after a run or an
upload. The download, the checksum pin and the static layout are under
[Deployment](webapp.md#deployment).

:::{todo}
The fork's README documents only the `embed-vX.Y.Z` release line and does not
mention the second, legacy embed bundle that the `ttsite` role also downloads
and that the catalogue's `commander` key selects — see
[Deployment](webapp.md#deployment). Meanwhile
[Firmware](../boards/tt-asic.md#firmware) still records the pre-2.x board as
camera-only pending that work. Confirm which is current and document the legacy
bundle in `README.fpgas-online.md`, or drop it here.
:::

## Rolling releases

`fpgas-online-tt` and `fpgas-online-tt-demos` are rolling releases with no
manual version bumps: every green CI run on `main` builds the deb, attaches it
to the current series release, and the APT repository picks it up on its next
poll. Series tags are two-component `vX.Y` and are always pushed by a person,
never by CI. The mechanics — the version derivation from `git describe`, the
pull into the repository, and how a Pi installs from it — are on
[Packages](../packages.md). The Commander embed does not go through APT at all:
it is a release tarball fetched by the infra role, pinned by version and SHA-256
in the inventory.

## Not yet implemented

Phases 1 and 2 of the design spec — the ASIC boards end to end, then the
FPGA emulation boards — have shipped. What has not:

- **KianV boot-to-Linux.** The spec's phase 3 is a one-click boot of the KianV
  RISC-V SoC with the Linux console shown in the Commander terminal, bridged
  from the chip's UART by the demo board's controller. It needs a hardware spike
  first — whether the pins land on a hardware UART or need a PIO one, and what
  baud is achievable — before the sequence is encoded as a daemon task. Neither
  `POST /kianv/boot` nor the fork's `kianv` kind exists yet, and both READMEs
  say so.
- **Verilog compiled on the Pi.** The spec reserves `POST /build` as later
  work, taking Verilog instead of a finished bitstream. It needs an arm64 NFS
  root, because oss-cad-suite only ships `linux-arm64`, and the root is still
  built from an armhf image. The spec numbers this step inconsistently: §11
  lists it under phase 4, while §5.3 and §7.3 still label it phase 2. Either
  way it has not shipped.
- **PMOD HAT features.** The spec's topology has each Pi carrying a PMOD HAT
  alongside the USB link, explicitly reserved and unused by everything above.
  Driving pins or capturing logic from the Pi is listed as later work.
- **The gateway API.** A separate service is meant to take over the
  slug-to-address derivation and the per-board pass-through so that no front end
  touches the private network. It is planned, not deployed — see
  [Gateway API](webapp.md#gateway-api).
- **The transport abstraction upstream.** Offering the `SerialTransport` seam
  back to `TinyTapeout/tt-commander-app` is listed as later work in the spec;
  the fork is kept rebaseable on upstream for that reason.

:::{todo}
The design spec's own open items are still open: the KianV UART bridge spike,
recording which demo-board revision and firmware version sits on each port in
the catalogue, the heads-up to the Tiny Tapeout team about hosting a public
Commander instance under their logo, and the armhf-versus-arm64 decision for the
Pi root. Track them where they belong rather than in the spec.
:::

## Sources

fpgas.online-infra, `main`:

- [`docs/superpowers/specs/2026-08-22-tinytapeout-fpgas-online-design.md`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/docs/superpowers/specs/2026-08-22-tinytapeout-fpgas-online-design.md)
  — the component diagram reproduced above, the addressing and camera-name
  derivations, the "nginx and Django only" split of the gateway, the single-owner
  bridge rule, the firewall rule that limits tcp/8765 to the gateway, the board
  model's fields, the `--prune` seeding step, the power-cycle button on the board
  page, the phasing, and the not-yet-implemented list including `POST /build`,
  the PMOD HAT reservation and the open items.
- [`ansible/roles/onpi/tasks/tt.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/roles/onpi/tasks/tt.yml)
  — the two packages installed at `state: latest`, the catalogue baked from the
  `ttsite` role's own template, and `fpgas-tt.service` enabled only where the
  site defines Tiny Tapeout boards.
- [`ansible/inventory/host_vars/fpgas.online.yml`](https://github.com/fpgas-online/fpgas.online-infra/blob/main/ansible/inventory/host_vars/fpgas.online.yml)
  — the shape of the `tt_boards` list only: which keys exist and what each one
  is for. No values from that file are reproduced here; the boards themselves
  are listed on the [Welland](../sites/welland.md) page.

fpgas.online-tt, `main`:

- [`README.md`](https://github.com/fpgas-online/fpgas.online-tt/blob/main/README.md)
  — the device open and retry, the `WS /serial` fan-out with its 256 KiB
  slow-client drop, the 1001 and 1011 close codes, the `/health` payload
  including `vid_pid` and `config_error`, the hostname-to-catalogue discovery
  and the unknown-hostname fallback, the four FPGA routes reproduced verbatim
  above with their error shapes, `--demos-dir` and the automatic demo sync, the
  install commands, and the rolling-release description.

tinytapeout-fpga-demos, `main`:

- [`README.md`](https://github.com/fpgas-online/tinytapeout-fpga-demos/blob/main/README.md)
  — the package and its install path, the current five-demo set, the per-demo
  project layout, the harness and its origin, the yosys/nextpnr-ice40/icepack
  commands, the `7E AA 99 7E` preamble check, `index.json` and `VERSION`, and
  the CI jobs.

tt-commander-app, `fpgas-online`:

- [`README.fpgas-online.md`](https://github.com/fpgas-online/tt-commander-app/blob/fpgas-online/README.fpgas-online.md)
  — the fork's branch layout, `mountCommander` and its handle, the options table
  reproduced verbatim above, what the embed does and does not do to the host
  page, the `fpga` kind's Config and Pinout behaviour, the wire protocol and
  close codes, the reconnect back-off, the multi-viewer paragraph quoted above,
  the one-widget-per-page rule, and the `embed-vX.Y.Z` releases 0.1.0 and 0.2.0.

fpgas.online-site, `main`:

- [`README.md`](https://github.com/fpgas-online/fpgas.online-site/blob/main/README.md)
  — the `ttsite_loadboards` invocation, what `--prune` and `--allow-empty` do,
  the `TTSITE_COMMANDER_VERSION` pin with its "bundle not deployed" notice and
  the 0.2.0 floor for FPGA boards, and the three daemon-proxy endpoints. The
  rest of that README is covered on [The web application](webapp.md).
