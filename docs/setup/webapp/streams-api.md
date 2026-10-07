# The web application: camera streams and the gateway API

**You want to know how the board pages' camera streams and the gateway API are served.**

## Camera streams

Video never passes through Django. Each Pi with a camera pushes RTMP to the
gateway and the gateway republishes it as HLS under `/live/`: the capture side
is [Camera](../pi.md#camera), and the `cam/stream-server` role that does the
republishing is listed under
[What runs on the gateway](../gateway.md#what-runs-on-the-gateway). Fragments are
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
