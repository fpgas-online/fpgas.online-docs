# Bootloader EEPROM on a Raspberry Pi 5: step 3, join the two FLASH WP pads

**You are upgrading a locked Raspberry Pi 5 and now join the two FLASH WP pads
on its underside, so that its flash can be written.**

The Pi is off ([step 2](bootloader-eeprom-pi5-step-2.md)). This is its underside, USB-A sockets on the left, GPIO
header along the top:

```{figure} bootloader-eeprom/pi5-underside-flash-wp.jpg
:alt: Underside of a Raspberry Pi 5 with the two FLASH WP pads ringed, right of the CE mark and above the micro-HDMI sockets
:width: 100%
:figclass: only-light

Photo: Suyash Dwivedi, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Raspberry_Pi5_8GB_Bottom_View_(1).jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); annotated, same licence.
```

```{figure} bootloader-eeprom/pi5-underside-flash-wp-dark.jpg
:alt: Underside of a Raspberry Pi 5 with the two FLASH WP pads ringed, right of the CE mark and above the micro-HDMI sockets
:width: 100%
:figclass: only-dark

Photo: Suyash Dwivedi, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Raspberry_Pi5_8GB_Bottom_View_(1).jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); annotated, same licence.
```

```{figure} bootloader-eeprom/pi5-flash-wp-closeup.jpg
:alt: Close-up of the pads: TP14 on the left, TP1 on the right, FLASH WP printed below
:width: 100%
:figclass: only-light

Photo: Suyash Dwivedi, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Raspberry_Pi5_8GB_Bottom_View_(1).jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); annotated, same licence.
```

```{figure} bootloader-eeprom/pi5-flash-wp-closeup-dark.jpg
:alt: Close-up of the pads: TP14 on the left, TP1 on the right, FLASH WP printed below
:width: 100%
:figclass: only-dark

Photo: Suyash Dwivedi, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Raspberry_Pi5_8GB_Bottom_View_(1).jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); annotated, same licence.
```

```{figure} bootloader-eeprom/pi5-flash-wp-bridged.jpg
:alt: The same close-up with a blob of solder drawn across TP14 and TP1 only
:width: 100%
:figclass: only-light

Photo: Suyash Dwivedi, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Raspberry_Pi5_8GB_Bottom_View_(1).jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); annotated, same licence.
```

```{figure} bootloader-eeprom/pi5-flash-wp-bridged-dark.jpg
:alt: The same close-up with a blob of solder drawn across TP14 and TP1 only
:width: 100%
:figclass: only-dark

Photo: Suyash Dwivedi, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Raspberry_Pi5_8GB_Bottom_View_(1).jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); annotated, same licence.
```

```{figure} bootloader-eeprom/pi5-flash-wp-wrong.jpg
:alt: The same close-up with a blob of solder drawn that also reaches TP17, marked wrong
:width: 100%
:figclass: only-light

Photo: Suyash Dwivedi, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Raspberry_Pi5_8GB_Bottom_View_(1).jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); annotated, same licence.
```

```{figure} bootloader-eeprom/pi5-flash-wp-wrong-dark.jpg
:alt: The same close-up with a blob of solder drawn that also reaches TP17, marked wrong
:width: 100%
:figclass: only-dark

Photo: Suyash Dwivedi, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Raspberry_Pi5_8GB_Bottom_View_(1).jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); annotated, same licence.
```

:::{warning}
`TP1` carries power when the Pi is on. A bridge that touches anything besides
`TP14` and `TP1` can damage the Pi. If yours does, take it off and make it
again now, while the Pi is off.
:::

1. Find the two pads.
2. Join `TP14` to `TP1` with a small blob of solder across both, as in the
   RIGHT picture.
3. Look at it against the RIGHT and WRONG pictures: one blob, on those two
   pads, touching nothing else. With a multimeter: `TP14` to `TP1` reads a
   short circuit.

No soldering iron? Skip items 2 and 3 of this step. In [step 4](bootloader-eeprom-pi5-step-4.md) you hold tweezers (or a short wire)
on the two pads instead:

```{figure} bootloader-eeprom/pi5-flash-wp-tweezers.jpg
:alt: The same close-up with the two tips of a pair of tweezers drawn, one on TP14 and one on TP1
:width: 100%
:figclass: only-light

Photo: Suyash Dwivedi, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Raspberry_Pi5_8GB_Bottom_View_(1).jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); annotated, same licence.
```

```{figure} bootloader-eeprom/pi5-flash-wp-tweezers-dark.jpg
:alt: The same close-up with the two tips of a pair of tweezers drawn, one on TP14 and one on TP1
:width: 100%
:figclass: only-dark

Photo: Suyash Dwivedi, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Raspberry_Pi5_8GB_Bottom_View_(1).jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); annotated, same licence.
```
