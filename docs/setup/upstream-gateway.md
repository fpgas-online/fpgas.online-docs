# What a site needs from its upstream network

A site is one gateway host, `gw.<site>.fpgas.online`, with the fleet behind
it. The gateway is the fleet's only path to anything else. This page lists
what the network **above** the gateway must provide, so that a site can be
set up without knowing how any other site's upstream is built.

fpgas.online does not manage the upstream network, and nothing in the
fpgas.online repositories may depend on a particular upstream device or name
one. The upstream is only required to meet this page.

A gateway can sit in either of two places:

Behind a NAT gateway
: The gateway's uplink has a private IPv4 address. A separately managed
  router holds the site's public IPv4 address and forwards to the gateway.
  Welland is built this way.

Directly on a public IPv4 address
: The gateway's uplink holds the public IPv4 address itself. Nothing is
  forwarded. PS1 is built this way.

The gateway's own firewall is the same in both cases: it accepts the ports
below on its uplink and does the per-board forwarding itself. The difference
is only whether something upstream has to pass the traffic on.

Each requirement below says whether it is **built** (the deployed gateway
relies on it now) or **designed** (a merged design needs it and no code uses
it yet).

## The uplink

| Requirement | State | Notes |
|---|---|---|
| One Ethernet link from the gateway's uplink interface to the upstream network | built | The fleet's VLANs never appear on this link. |
| An IPv4 address, a default route and a DNS resolver for the gateway, static or by DHCP | built | Inventory: `eth_uplink_static` and the `eth_uplink_static_*` variables, or DHCP when `eth_uplink_static` is false. |
| Outbound IPv4 from that address to the internet | built | The gateway masquerades the whole fleet behind its uplink address, so the upstream sees one source address. Behind a NAT gateway, the upstream NATs it once more. |
| The address must not change | built | The gateway's firewall forwards per-board ports addressed to `eth_uplink_static_address`, and the web application lists it among its allowed host names. |

## Inbound IPv4

"Reaches the gateway" means: on a public address, the port is simply open to
the internet; behind a NAT gateway, the upstream forwards the port on the
public IPv4 address to the gateway's uplink address, same port number.

| Port | Must reach the gateway for | State |
|---|---|---|
| tcp 80 | The web site, and Let's Encrypt `http-01` challenges (`/.well-known/acme-challenge/`) for every public name of the site | built |
| tcp 443 | The web site, the web terminal and the camera players. **TLS ends on the gateway**: an upstream that proxies must pass TLS through untouched (route on the SNI name), not terminate it | built |
| udp and tcp `webrtc_media_port` (8189) | WebRTC camera media. Signalling rides on 443; the media does not, and cannot go through an HTTP or TLS proxy | built |
| tcp `<s><pp>22` and `<s><pp>44` for switch `s`, port `pp` | Per-board ssh and the per-board auxiliary port. The gateway forwards each to its board. See [Network and power](network.md) for the formula | built |
| tcp 22 | Operators' ssh to the gateway, and deploys | built on a public address. Behind a NAT gateway it is not required while the gateway's ssh is reachable over IPv6: Welland's public IPv4 port 22 is not forwarded, and operators and deploys use IPv6 |
| tcp 22, as the entry to the per-board ssh proxy | Logging in to a board by name (`ssh pi-sw2-p47@…`) without a port number | designed; whether public port 22 goes to the proxy is an open decision |

If the upstream is an HTTP reverse proxy for port 80 rather than a plain port
forward, it must pass the `Host` header and the client address
(`X-Forwarded-For`) on, and must not cache.

### Clients inside the site

A client on the upstream's own LAN usually cannot reach the public address
and be forwarded back in ("hairpin"). Such clients need a route to the
gateway's uplink address, and the site's names must resolve to it for them.
The gateway offers its uplink address as a WebRTC candidate for the same
reason (`webrtc_additional_hosts`).

## IPv6

| Requirement | State | Notes |
|---|---|---|
| A global IPv6 address for the gateway's uplink | built | IPv6 clients reach the web site and the WebRTC media port on it directly, with no forwarding. |
| A prefix routed to the gateway's uplink address, large enough for one /64 per fleet switch (a /56 at Welland) | built | Each board gets one address inside its switch's /64. The gateway is the router for the prefix; the upstream only needs a route to it. Either a static route or DHCPv6 prefix delegation will do, provided the prefix does not change. |
| The upstream does not filter that prefix, or filters it to the same ports the gateway allows | designed | The gateway's forward chain decides what reaches a board. An upstream filter in front of it must allow at least ICMPv6, and tcp 22, 80 and 443 to the prefix, or direct IPv6 access to boards cannot work. Both filters have to agree, and both have to be checked. |
| Reverse DNS for the prefix delegated to the gateway | designed | Needed for per-board names to have matching reverse records. |

## DNS

| Requirement | State | Notes |
|---|---|---|
| `A` records for every public name of the site pointing at the public IPv4 address, and `AAAA` records pointing at the gateway's global IPv6 address | built | At Welland: the site name, the Tiny Tapeout site (a `CNAME` to it) and the package cache name. The names live in the public `fpgas.online` zone, which is not served by the site. |
| A resolver the gateway can use | built | `eth_uplink_dns_server`. The gateway runs its own resolver for the fleet and forwards to this one. |
| Optional: an internal zone for the fleet delegated to the gateway | built, optional | The upstream's resolver delegates a zone (`dnsmasq_auth_zone`) to the gateway with an `NS` record and glue. Its queries arrive on the gateway's uplink, so their source address must be listed in `firewall_dns_query_sources`. A site that does not want this leaves the three `dnsmasq_auth_*` variables unset. |
| A public zone for per-board names, `<site>.fpgas.online`, with `SSHFP` records | designed | Which zone, who serves it and whether it is signed are open decisions. |

## Outbound, from the gateway

| The gateway must be able to reach | For |
|---|---|
| Debian and Raspberry Pi package mirrors, and `fpgas.online` package repositories, over http and https | Its own packages and the package cache it runs for the fleet |
| `ghcr.io` over https | The prebuilt fleet root file system |
| `github.com` over https | Operators' public ssh keys |
| Let's Encrypt over https | Certificates |
| An NTP server | Its clock, which the fleet takes from it |

An upstream package cache is **not** required. A site may point the gateway
at one (`apt_client_proxy`), as an optimisation only.

## What the upstream is never asked for

- The fleet's VLANs, DHCP, TFTP or NFS. They exist only between the gateway
  and the fleet switches.
- Access to the fleet switches' management or PoE control. The gateway does
  that.
- Running any fpgas.online software, or holding any fpgas.online
  credential.

## Deploying from outside the site

Ansible must be able to reach the gateway's ssh as the `ansible` account
from wherever the operator runs it: by the gateway's public name, over IPv6
or, where it is forwarded, IPv4 port 22. A site must not need an operator to be on the
upstream network to deploy.

:::{todo}
The infra inventory still reaches the Welland gateway on its private uplink
address, which only works from the upstream network. It has to move to a
public name.
:::

## Checking a site against this page

From a host outside the site, for each public name: `http` and `https`
answer with the gateway's own certificate; a board's ssh port answers with
the fleet's host key; a camera page plays over an IPv4-only connection (the
media port) and over an IPv6-only one. From the gateway: package updates,
the root file system pull and certificate renewal succeed. From inside the
site: the site name resolves and loads.
