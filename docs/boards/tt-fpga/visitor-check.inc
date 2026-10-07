**First, look whether a visitor is connected, and do not cut a visitor short.** On a board of the public site a
visitor may be using it right now. The daemon's `/health` says how many are connected in `clients`, and the
site's `https://tinytapeout.fpgas.online/board/<board>/status.json` is a summary of it: on the Pi,

```console
$ curl -s http://localhost:8765/health
```

(the daemon listens on port 8765: [The fpgas-tt daemon](/setup/tinytapeout.md#the-fpgas-tt-daemon); this
command is not run by us in this form). If `clients` is more than 0, wait until it is 0.
