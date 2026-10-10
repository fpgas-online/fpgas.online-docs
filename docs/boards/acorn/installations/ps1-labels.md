# Labels at ps1

**You want the labels for the blades and cards at ps1: which exist, how to print them, and which wait.**
What each blade still needs is on [Acorns at ps1](ps1.md).

Each host and each card gets a label with what identifies it, made by
`fpgas-verify` from a read of the hardware itself. **Not on pi14 at ps1 or pi18 at ps1:** the label read asks
the firmware (`vcgencmd`), which hung for good on those two Compute Module 4 blades on 7 October 2026. On
pi16 at ps1 or pi20 at ps1, once the packages are installed there
([verifying 1](../checks/compute-blade.md)):

```console
$ sudo fpgas-verify --label --out labels.pdf
```

- **The Compute Module labels of pi16 at ps1 and pi20 at ps1** exist, from reads
  of 5 October 2026. A label names no host: the one with eth MAC
  `2c:cf:67:fb:91:e5` is pi16 at ps1's, the one with `2c:cf:67:fd:1e:be` is pi20
  at ps1's. They are {download}`on plain US Letter paper, at true size with a
  line to cut along <labels/ps1-compute-modules-letter-plain.pdf>`, and
  {download}`laid out for Avery 5163 / 8163 stickers
  <labels/ps1-compute-modules-avery-5163.pdf>`. Print at 100 %, no scaling. The
  sticker layout is not yet tried on a real sheet: print it on plain paper
  first and hold it against the sticker sheet. "HAT none" on these labels means
  the firmware reported no HAT; the header's pins were deliberately not
  scanned, because on a Compute Blade they are JTAG wires.
- **The Acorn labels are not made yet.** Each waits for its card's conversion
  ([Acorns at ps1](ps1.md)).
- **No labels yet for pi14 at ps1 and pi18 at ps1.** Their visitor ports did not answer on 5 October 2026,
  when the other two were read. Both answered on 7 October 2026, but the label read asks the firmware
  (`vcgencmd`), which hung for good on both that day: do not run it there; their labels wait until that is settled.
- **The two labels that exist were checked against the modules on 7 October 2026**: every printed field
  matches what pi16 at ps1 and pi20 at ps1 report.
