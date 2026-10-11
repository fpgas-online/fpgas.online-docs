---
type: explanation
owner: documentation maintainers
reader: a visitor watching a board through its page
review: 2026-11-10
---

# The camera on a board

This page explains the video on a board's page: the two views, how far behind they are, and what the camera points
at. It is for a visitor watching a design run. It does not cover setting up a camera, which is [Camera](../../setup/pi/camera.md).

## The two views

Where the browser can take it, the page first shows a low-latency view, about 0.3 s behind the camera. A **rewind**
button swaps it for a slower stream with a window you can scroll back through, about 5 s behind. A **live** button
swaps back. If the low-latency view gives no picture, the slower stream stays, and the page keeps trying the fast one.
Both run at 6 frames a second.

When a host sends no picture, a box saying so stands in place of the player. The page asks again every 15 seconds,
and the player comes back when the picture does. **reset video player** asks at once.

## Watching outside the page

The board's page gives the stream's address under "Accessing directly", for a player on your own machine:

```console
$ vlc https://welland.fpgas.online/live/HOST.m3u8
```

`HOST` is the host's name, as the page shows it. The address plays the slower stream.

## What the camera points at

A host with a camera of its own points it at the board's LEDs. Over an Acorn the lens sits 60 mm above the card, over
the LEDs at its end ([The camera over an Acorn](../../boards/acorn/overview/camera.md)). The Tiny Tapeout hosts carry a
camera too.

A host with no camera of its own can send the picture of a USB HDMI grabber instead. On a NeTV2 host that is the
board's HDMI output, not a view of the board. Which NeTV2 hosts have which, and what the Fomu EVT's host shows, are
[docs issue #189](https://github.com/fpgas-online/fpgas.online-docs/issues/189).

:::{admonition} Figure to come
:class: placeholder

The board page's camera in its two views, with the rewind and live buttons. Tracked in [docs issue #188](https://github.com/fpgas-online/fpgas.online-docs/issues/188).
:::
