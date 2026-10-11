The header's GPIO chip is the one `gpiodetect` lists as `pinctrl-rp1`; its number varies from 11 to 15. Where the
Acorn packages are installed, the boot check makes `gpiochip0` a link to it when `gpiochip0` is missing. The link is
gone at each reboot. Check which chip `gpiochip0` is:

```console
$ sudo gpiodetect
$ ls -l /dev/gpiochip0
```

Skip the link if `ls -l` shows `-> gpiochipN` with N the number of `pinctrl-rp1`, or `gpiodetect` lists `gpiochip0`
itself as `pinctrl-rp1`. If `/dev/gpiochip0` is missing or another chip, link it. The line below is for `gpiochip15`: put your chip's number in
place of 15.

```console
$ sudo ln -sfn /dev/gpiochip15 /dev/gpiochip0
```
