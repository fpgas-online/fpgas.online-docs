# The web application: known gaps

**You want to know what the web application does not do yet, or does wrong.**

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
bundle (see [Deployment](../webapp.md#deployment)). Either the README follows the code or
the code follows the README. The four code faults listed above — the broken
classic upload form, the unauthenticated `csrf_exempt` `/pistat/` views,
`pibfpgas.views.one` looking boards up by port alone, and `fpga.html`'s
hard-coded legacy `vlc .../live/pi<N>.m3u8` URL — are open the same way: fix
them in `fpgas.online-site` or record that the classic site is frozen.
:::
