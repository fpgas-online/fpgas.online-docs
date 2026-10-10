---
type: landing
owner: documentation maintainers
reader: someone about to put an Acorn on a host
review: 2026-11-10
---

# Setting up an Acorn

- [An Acorn on a Raspberry Pi 5](rpi-5/index.md): the wiring, the Pi's settings, the cables and the fitting.
- [An Acorn on a Compute Blade](compute-blade/index.md): the wiring, the blade's settings, the cables and the fitting.
- [How to install the Acorn packages](packages.md): the fpgas.online packages for the card, on either host.
- [How to install the fpgas.online images on an Acorn](install-images.md): the two images, into the card's flash.
- [How to update the operational image of an Acorn](update-operational-image.md): a different operational image, into the flash.
- [How to generate multiboot bitstreams by hand](multiboot-bitstreams.md): the golden and operational flavours of another design.
- [Reaching an Acorn's flash through PCIe](flash-access.md): how the flash tool works, and what it checks.

```{toctree}
:hidden:

On a Raspberry Pi 5 <rpi-5/index>
On a Compute Blade <compute-blade/index>
packages
install-images
update-operational-image
multiboot-bitstreams
flash-access
```
