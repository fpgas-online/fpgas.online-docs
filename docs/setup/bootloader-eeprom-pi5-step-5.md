# Bootloader EEPROM on a Raspberry Pi 5: step 5, cable out, card out, bridge off, cable in

**You are upgrading a locked Raspberry Pi 5, and the 60 seconds of
[step 4](bootloader-eeprom-pi5-step-4.md) are over: now you take the card and
the bridge off and put the Pi back on its port.**

```{image} bootloader-eeprom/cable-out.svg
:alt: A Raspberry Pi 5, top side up, with its network cable pulled out of the Ethernet socket
:width: 80%
:class: only-light
```

```{image} bootloader-eeprom/cable-out-dark.svg
:alt: A Raspberry Pi 5, top side up, with its network cable pulled out of the Ethernet socket
:width: 80%
:class: only-dark
```

1. Pull the network cable.
2. Pull the card out of its slot.

```{figure} bootloader-eeprom/pi5-flash-wp-clear.jpg
:alt: Close-up of TP14 and TP1 as two separate pads again
:width: 100%
:figclass: only-light

Photo: Suyash Dwivedi, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Raspberry_Pi5_8GB_Bottom_View_(1).jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); annotated, same licence.
```

```{figure} bootloader-eeprom/pi5-flash-wp-clear-dark.jpg
:alt: Close-up of TP14 and TP1 as two separate pads again
:width: 100%
:figclass: only-dark

Photo: Suyash Dwivedi, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Raspberry_Pi5_8GB_Bottom_View_(1).jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); annotated, same licence.
```

3. Take the bridge off: wick the solder away (or let go of the wire or
   tweezers). The two pads must be separate again, as in the picture.
4. Put the Pi back where it was.

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

5. Plug the network cable in, on the same switch port: the port this Pi
   normally lives on. (Some sites keep one port aside for bringing up new
   Pis, an EEPROM service port. A Pi plugged in there is never locked: not
   that port.)

:::{warning}
Leave the Pi alone for two minutes now. It starts from the network and locks
its flash again while it starts; do not pull the cable during that time. (The
two Pis we read after an upgrade on 6 October 2026 were already locked when
read, 40 and 100 seconds after they started.)
:::
