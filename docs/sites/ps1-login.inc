From any machine with `ssh`, as the visitor. The port is `1NN22`, where `NN` is the number in the blade's name: `11422` for pi14 at ps1, `11622` for pi16 at ps1, `11822` for pi18 at ps1, `12022` for pi20 at ps1.

```console
$ ssh -p 11622 pi@ps1.fpgas.online
```

The password is in the banner that `ssh` prints when you connect, before it asks for one: the board pages of
<https://ps1.fpgas.online/fpgas/> say so under "Use your own ssh client" (read on 6 October 2026 on
`pi3.html`, the page of pi3 at ps1, port `10322`). `sudo` asks for the same one. The blades have no board page
of their own there, and the banner on a blade's port is not verified by us.
