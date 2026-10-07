# Bootloader EEPROM on a Raspberry Pi 5: step 4, card in, network cable in, wait for the green light

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

2. Next the network cable goes in, and that powers the Pi. How you do it depends
   on what joins the pads:

   - **A solder bridge on the pads:** plug the network cable in.
   - **Tweezers or a short wire instead:** do these in this order, and read all three before you start.

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

     1. Put one tip of the tweezers (or one end of the wire) on each pad, first.
     2. Then plug the network cable in with your other hand.
     3. Keep the tips on both pads until you pull the network cable in step 5.

   Where the network cable goes, either way: the switch port the Pi was on, into
   the Ethernet socket, the one beside the two USB blocks. (The drawing shows the
   Pi top side up; yours is lying upside down.)

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

3. Watch the Pi's green activity light. When it flashes rapidly, the new
   bootloader is written and the Pi has stopped: go on to
   [step 5](bootloader-eeprom-pi5-step-5.md). (Raspberry Pi's documentation:
   "On success ... the green activity LED is flashed rapidly", for a card whose
   image is called `pieeprom.bin`, as step 1's is.)

   Give it at least 60 seconds before you decide it is not going to: until it
   flashes rapidly, leave the cable in. If instead it blinks a repeating
   pattern of long and short flashes, Raspberry Pi calls that an error code.
   Write down the pattern and still go on to step 5: on one of our runs a
   pattern of 3 long and 3 short came after a write that had worked, and step 6
   tells which it was. If after five minutes it does neither, go on to step 5
   as well, and let step 6 tell.

   Whether the write worked is checked in
   [step 6](bootloader-eeprom-pi5-step-6.md), after the Pi has started again:
   the new bootloader date there means it was written; the old date means the
   new bootloader was not written, and the chart in step 6 sends you back to
   step 2.
