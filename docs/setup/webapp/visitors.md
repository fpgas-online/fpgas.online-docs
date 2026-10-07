# The web application: what a user sees

**You want to know what a visitor to fpgas.online or tinytapeout.fpgas.online sees and can do.**

## What a user sees

The front page of a site is the board grid. Each board gets a card with its
hostname, the FPGA board fitted to it, a live HLS camera thumbnail playing
through video.js, and a "Use this FPGA" link to the board page. Nothing on the
card is interactive beyond the video controls. Which boards are on it is a site
fact, not a platform one: the public grid is
[PS1's](../../sites/ps1.md#public-site), and Welland's boards are listed under
[Hosts and boards](../../sites/welland.md#hosts-and-boards).

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
  [Known gaps](known-gaps.md#known-gaps).
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
the page's own video element uses. See [Known gaps](known-gaps.md#known-gaps).

The Tiny Tapeout board page is laid out the same way but built from different
parts — the chip, the RP2040 and the Pi-side daemon behind it are
[The Tiny Tapeout stack](../tinytapeout.md). What the page itself shows is the
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
