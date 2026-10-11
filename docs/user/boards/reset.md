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

1. On welland or ps1, press **Reset**, next to "Turn it off and on again". On tinytapeout.fpgas.online, press
   **Power-cycle board** and confirm.
2. Wait about two minutes for the host to come back. A Raspberry Pi 5 host can take more than 90 s.

## Check

On welland or ps1, the status box shows the host's boot messages, and **Check PoE** writes a line that starts
`status: PoE`. The terminal connects again by itself. On tinytapeout.fpgas.online, the status log shows
`power-cycle: done`, and the status pill shows the board again.

## If it fails

| What you see | Likely cause | Fix |
|---|---|---|
| The status log shows `power-cycle refused`, with a reason | the board was power-cycled a moment ago, or the switch did not answer | wait, then press it again |
| An upload says the board is not answering | the host is still starting | wait a little longer, then upload again |

## Next

- [The board page on welland and ps1](board-page.md)
- [Boards](index.md)
