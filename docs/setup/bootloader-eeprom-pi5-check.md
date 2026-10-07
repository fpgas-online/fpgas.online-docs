# Bootloader EEPROM on a Raspberry Pi 5: check it (nothing is changed)

**You have a Raspberry Pi 5 of the fleet and want to know whether its
bootloader is the fleet's and locked.** This check only reads: nothing on the
Pi is changed.

Three reads.

```{image} bootloader-eeprom/check-card.svg
:alt: Three reads: the bootloader date should be 2026/09/25, the boot order BOOT_ORDER=0xf2, and the flash lock SR1 0xbc
:width: 100%
:class: only-light
```

```{image} bootloader-eeprom/check-card-dark.svg
:alt: Three reads: the bootloader date should be 2026/09/25, the boot order BOOT_ORDER=0xf2, and the flash lock SR1 0xbc
:width: 100%
:class: only-dark
```

```{include} bootloader-eeprom-read-state.inc
```

```{image} bootloader-eeprom/boot-order.svg
:alt: BOOT_ORDER is read from its last digit: 0xf2 is network only; 0xf12 and 0xf2461 also boot local media
:width: 100%
:class: only-light
```

```{image} bootloader-eeprom/boot-order-dark.svg
:alt: BOOT_ORDER is read from its last digit: 0xf2 is network only; 0xf12 and 0xf2461 also boot local media
:width: 100%
:class: only-dark
```

Date or boot order NOT DONE: the upgrade is the next part, [Upgrade a locked
Raspberry Pi 5](bootloader-eeprom-pi5-upgrade.md).
