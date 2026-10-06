From any machine with `ssh`, as the visitor. The port is `1NN22`, where `NN` is the number in the blade's name: `11422` for pi14 at ps1, `11622` for pi16 at ps1, `11822` for pi18 at ps1, `12022` for pi20 at ps1.

```console
$ ssh -p 11622 pi@ps1.fpgas.online
```

The password is not printed here. Each board page of <https://ps1.fpgas.online/fpgas/> shows it under "Use
your own ssh client" (`pi3.html`, for example); it is the same for every board at ps1, and `sudo` asks for
the same one. (Read on that site on 6 October 2026: pi3 at ps1 is on port `10322`. The blades have no board
page of their own there.)
