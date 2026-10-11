---
type: how-to
owner: documentation maintainers
reader: a visitor whose board or host no longer answers
review: 2026-11-10
---

# How to reset a board

**You have a board's page open, and the board or its host no longer answers. You want it to start again**. A reset
cuts the host's power and restores it, so the host and the board start from scratch.

## What you need

- The board's page on welland.fpgas.online, ps1.fpgas.online or tinytapeout.fpgas.online.

A reset ends the session of anyone else using the board. Everything written on the host is gone after it, uploads
included.

## Steps

1. On welland or ps1, press **Reset**, next to "Turn it off and on again".
2. On tinytapeout.fpgas.online, press **Power-cycle board** instead, and confirm.
3. Wait about two minutes for the host to come back.

## Check

On welland, the status box shows the host's boot messages, and the terminal connects again by itself. On ps1, press
**reconnect** and **reset ssh**: the terminal shows a prompt. On tinytapeout.fpgas.online, the status log shows
`power-cycle: done`, and the status pill shows the board again.

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| `reset failed (429)`, or `power-cycle refused (HTTP 429)` | the board was power-cycled a moment ago | wait, then press it again |
| `power-cycle refused`, with another reason | the reason it gives | press it again later; if it repeats, the site cannot cycle this board |
| On ps1, nothing at all after Reset, and no boot messages | ps1's page shows the answer only in the browser's console | wait two minutes, then press reconnect and reset ssh |
| An upload says the host "did not answer, so nothing was uploaded" | the host is still starting | wait a little longer, then upload again |

## Next

- [The board page on welland and ps1](board-page.md)
- [Using a board](index.md)
