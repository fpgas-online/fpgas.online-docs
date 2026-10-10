:::{warning}
**Detach the PCIe endpoint before loading a bitstream**, as on a Pi 5. The bus
address differs per blade: `0000:01:00.0` on the CM4 blade pi14 at ps1, `0001:01:00.0`
on the CM5 blades pi16 at ps1 and pi20 at ps1. Take it from `lspci` or from [Acorns at
ps1](/boards/acorn/installations/ps1.md#the-cards), and put it in `BDF` for the
commands on this page:

```console
$ BDF=0001:01:00.0           # a CM5 blade; 0000:01:00.0 on a CM4 blade
$ echo 1 | sudo tee /sys/bus/pci/devices/$BDF/remove
```
:::
