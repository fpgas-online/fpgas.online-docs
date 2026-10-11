The header's GPIO chip is the one `gpiodetect` lists as `pinctrl-rp1`; its number varies from 11 to 15. Where the
Acorn packages are installed, the boot check makes `gpiochip0` a link to it. Check which chip `gpiochip0` is:

```console
$ sudo gpiodetect
$ ls -l /dev/gpiochip0
```

If `/dev/gpiochip0` is missing or another chip, link it. The line below is for `gpiochip15`: put your chip's number in
place of 15.

```console
$ sudo ln -sfn /dev/gpiochip15 /dev/gpiochip0
```
