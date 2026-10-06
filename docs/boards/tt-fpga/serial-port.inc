:::{warning}
**The `fpgas-tt` daemon holds the board's serial port.** On a host that serves the public site the daemon has
`/dev/ttboard` (`/dev/ttyACM0`) open all the time, so `mpremote` and the programming script cannot open it
while the daemon runs. Stop the daemon first, and start it again afterwards or the board drops off the public
site:

```console
$ sudo systemctl stop fpgas-tt
# ... the command that needs the port ...
$ sudo systemctl start fpgas-tt
```

The boot check (`fpgas-verify`, `fpgas-tt-fpga-verify`) does this itself: it stops `fpgas-tt.service` for its
tests and starts it again. Whether `fpgas-tt-fpga-debug` does is not recorded. Why the daemon owns the port:
[Serial port ownership](/setup/tinytapeout.md#serial-port-ownership).
:::
