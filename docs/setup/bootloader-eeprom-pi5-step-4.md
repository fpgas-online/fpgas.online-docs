# Bootloader EEPROM on a Raspberry Pi 5: step 4, card in, network cable in, wait 60 seconds

**You are upgrading a locked Raspberry Pi 5, its FLASH WP pads joined
([step 3](bootloader-eeprom-pi5-step-3.md)) or tweezers or a short wire ready
for them, and now let it write its new bootloader from the card.**

:::{warning}
`TP1` carries power when the Pi is on. A bridge that touches anything besides
`TP14` and `TP1` can damage the Pi. If yours does, take it off and make it
again now, while the Pi is off.
:::

```{figure} bootloader-eeprom/pi5-underside-sd-slot.jpg
:alt: Underside of a Raspberry Pi 5 with the microSD slot ringed on the right edge, a card going in, and the bridge still on the FLASH WP pads
:width: 100%
:figclass: only-light

Photo: Suyash Dwivedi, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Raspberry_Pi5_8GB_Bottom_View_(1).jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); annotated, same licence.
```

```{figure} bootloader-eeprom/pi5-underside-sd-slot-dark.jpg
:alt: Underside of a Raspberry Pi 5 with the microSD slot ringed on the right edge, a card going in, and the bridge still on the FLASH WP pads
:width: 100%
:figclass: only-dark

Photo: Suyash Dwivedi, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Raspberry_Pi5_8GB_Bottom_View_(1).jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); annotated, same licence.
```

1. Push the card into the slot.

```{image} bootloader-eeprom/cable-in.svg
:alt: A Raspberry Pi 5, top side up, with its network cable going into the Ethernet socket
:width: 80%
:class: only-light
```

```{image} bootloader-eeprom/cable-in-dark.svg
:alt: A Raspberry Pi 5, top side up, with its network cable going into the Ethernet socket
:width: 80%
:class: only-dark
```

2. Plug the network cable in, on the switch port the Pi was on. (The drawing
   shows the Pi top side up; yours is lying upside down. The Ethernet socket
   is the one beside the two USB blocks.)

   No solder bridge? Do this instead of item 2:

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

   - put one tip of the tweezers (or one end of the wire) on each pad;
   - plug the network cable in with your other hand;
   - keep the tips on both pads until the 60 seconds below are over.
3. Wait 60 seconds by a clock. There is nothing to watch for: the Pi writes
   its new bootloader from the card and stops. Whatever the green light does,
   go on to [step 5](bootloader-eeprom-pi5-step-5.md) when the 60 seconds are over.
