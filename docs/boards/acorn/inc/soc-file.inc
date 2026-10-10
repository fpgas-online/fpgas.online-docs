The design these steps load is the fpgas.online Acorn design, the only design a package installs.
`fpgas-online-acorn-bitstreams` puts it in `/usr/share/fpgas-online/acorn-pcie/images/`, for each variant
(`cle-215p`, `cle-215`, `cle-101`) as `acorn-<variant>-sqrl_acorn.bit` for a JTAG load, beside the two flash
images. Put its name in `SOC` once per shell; the example is a CLE-101, so put another card's variant in place of
`cle-101`, here and in the release file names of the loopback and pin-ID designs:

```console
$ SOC=/usr/share/fpgas-online/acorn-pcie/images/acorn-cle-101-sqrl_acorn.bit
```
