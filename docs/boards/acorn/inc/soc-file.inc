## The design these steps load

Only one design is installed by a package: the fpgas.online Acorn design (the
SoC that `fpgas-verify` checks). `fpgas-online-acorn-bitstreams` puts it in
`/usr/share/fpgas-online/acorn-pcie/images/`, for each variant (`cle-215p`,
`cle-215`, `cle-101`) as `acorn-<variant>-sqrl_acorn.bit` for a JTAG load,
beside the two flash images. The JTAG and PCIe pages load that file; put its name in
`SOC` once per shell. The ps1 cards are CLE-101 ([Acorns at ps1](/boards/acorn/installations/ps1.md#the-cards)); for another card put its
variant in place of `cle-101`, here and in the release file names of the loopback and
pin-ID designs:

```console
$ SOC=/usr/share/fpgas-online/acorn-pcie/images/acorn-cle-101-sqrl_acorn.bit
```
