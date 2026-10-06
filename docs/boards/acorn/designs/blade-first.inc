**On a Compute Blade the JTAG steps and the serial step cannot share a boot**
under kernel 6.18 ([JTAG on a blade](../wiring/compute-blade-host.md#jtag-on-a-blade)): the JTAG, pin-ID and PCIe-design loads
go over JTAG and need the header's serial port off; a test of the serial pair
(`fpgas-verify`'s `p2-uart` and `p2-serial`) needs it on, with a design already
running that was loaded from flash. What has been
run on a blade is the detach, load, rescan and re-probe of the JTAG and PCIe pages, on
pi20 at ps1 (a CM5, kernel 6.12.75, its P2 pair on the Extension Port). Everything else
in the blade blocks of these pages is **not yet run by us on this hardware**. The J5 and
H5 part of the pin-ID check does not apply on a blade.

Every blade block uses the card's address from `BDF`; set it once per shell:

On a **CM5** blade (pi16 at ps1, pi20 at ps1):

```console
$ BDF=0001:01:00.0
```

On a **CM4** blade (pi14 at ps1):

```console
$ BDF=0000:01:00.0
```
