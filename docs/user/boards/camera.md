---
type: explanation
owner: documentation maintainers
reader: a visitor watching a board through its page
review: 2026-11-10
---

# The camera on a board

This page explains the video on a board's page: the two views, how far behind they are, and what the camera points
at. It is for a visitor watching a design run. It does not cover how a host sends its camera's picture, which is [The camera on a Pi host](../../setup/pi/camera.md), for operators.

## The two views

Where the browser can take it, the page first shows a low-latency view, about 0.3 s behind the camera. A **rewind**
button swaps it for a slower stream with a window you can scroll back through, about 5 s behind. A **live** button
swaps back. If the low-latency view gives no picture, the slower stream stays. The page tries the fast view a few times, then stops; reload the page to try again.

```{figure} screenshots/camera-live.png
:alt: The low-latency view of a Tiny Tapeout FPGA board: the purple board with a green LED lit, above a blue board. A clock is burned into the top left corner, and a rewind button sits at the top right.

The low-latency view, with its **rewind** button. A Tiny Tapeout FPGA board, 11 Oct 2026.
```

```{figure} screenshots/camera-rewind.png
:alt: The same board in the slower view after rewind was pressed, with the clock in the top left corner and a live button at the top right in place of rewind.

The slower view after **rewind**, with its **live** button.
```

Both views run at 6 frames a second.

When a host sends no picture, a box saying so stands in place of the player. The page asks again every 15 seconds,
and the player comes back with the picture. The button reset video player asks at once, and reloads the slower stream.

## Watching outside the page

The board's page gives the stream's address under "Accessing directly", for a player on your own machine:

```console
$ vlc https://welland.fpgas.online/live/HOST.m3u8
```

`HOST` is the host's name, as the page shows it. The address plays the slower stream.

## What the camera points at

On an Acorn host the camera points at the board's LEDs. The lens sits 60 mm above the card, over the LEDs at its end
([The camera over an Acorn](../../boards/acorn/overview/camera.md)).

A host with no camera of its own can send the picture of a USB HDMI grabber instead. On a NeTV2 host that is the
board's HDMI output, not a view of the board. Which NeTV2 hosts have which, and what the other boards' cameras show, are
[docs issue #189](https://github.com/fpgas-online/fpgas.online-docs/issues/189).
