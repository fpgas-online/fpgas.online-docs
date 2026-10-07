# Bootloader EEPROM on a Raspberry Pi 5: step 6, read it back

**You are upgrading a locked Raspberry Pi 5, and the two minutes at the end of
[step 5](bootloader-eeprom-pi5-step-5.md) are over: now you read it back and
find your result.**

Do the three reads again, then find your result in the chart at the end of
this step.

```{image} bootloader-eeprom/check-card-after.svg
:alt: Three reads: the bootloader date should be 2026/09/25, the boot order BOOT_ORDER=0xf2, and the flash lock SR1 0xbc
:width: 100%
:class: only-light
```

```{image} bootloader-eeprom/check-card-after-dark.svg
:alt: Three reads: the bootloader date should be 2026/09/25, the boot order BOOT_ORDER=0xf2, and the flash lock SR1 0xbc
:width: 100%
:class: only-dark
```
```{include} bootloader-eeprom-read-state.inc
```

Your result:

```{image} bootloader-eeprom/outcomes.svg
:alt: What step 6 can read and what to do: all three as wanted, done; the old date, nothing was written, go back to step 2; the new date but another boot order, make the card again; the new date and boot order but SR1 0x0, power the Pi off and on and read again; no answer after five minutes, go back to step 2 with a checked card
:width: 100%
:class: only-light
```

```{image} bootloader-eeprom/outcomes-dark.svg
:alt: What step 6 can read and what to do: all three as wanted, done; the old date, nothing was written, go back to step 2; the new date but another boot order, make the card again; the new date and boot order but SR1 0x0, power the Pi off and on and read again; no answer after five minutes, go back to step 2 with a checked card
:width: 100%
:class: only-dark
```

The steps the chart sends you back to: [step 1, make the
card](bootloader-eeprom-pi5-step-1.md), and [step 2, network cable
out](bootloader-eeprom-pi5-step-2.md).
