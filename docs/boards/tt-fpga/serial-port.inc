:::{warning}
**Only if your Pi runs the fpgas.online Tiny Tapeout daemon (the boards at welland do): the `fpgas-tt`
daemon holds the board's serial port.** The daemon has `/dev/ttboard` (`/dev/ttyACM0`) open all the time, so
`mpremote` and the programming script cannot open it while the daemon runs. Stop the daemon first, and start
it again afterwards or the board drops off the public site:

```console
$ sudo systemctl stop fpgas-tt
# ... the command that needs the port ...
$ sudo systemctl start fpgas-tt
```

A Pi without the `fpgas-online-tt` package has no such daemon and needs none of this. The boot check
(`fpgas-verify`, `fpgas-tt-fpga-verify`) stops and starts the daemon itself; whether `fpgas-tt-fpga-debug`
does is not recorded. Why the daemon owns the port is on another page, not in this set: "Serial port
ownership" on [The Tiny Tapeout stack](/setup/tinytapeout.md#serial-port-ownership).
:::
