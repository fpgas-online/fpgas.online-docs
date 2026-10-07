# PMOD interface

The PMOD (Peripheral Module) interface is a standard defined by Digilent for connecting peripheral modules to FPGA and microcontroller host boards. These pages cover the standard PMOD connector types, pinouts, and the extended I2C interface.

Source: [Digilent PMOD Interface Specification 1.3.1](https://digilent.com/reference/pmod/pmod-interface-specification), [High Speed PMOD Spreadsheet](https://docs.google.com/spreadsheets/d/1D-GboyrP57VVpejQzEm0P1WEORo1LAIt92hk1bZGEoo/edit?gid=0#gid=0)

Which do you need?

(physical-connectors)=
(single-width-6-pin-16)=
(single-width-6-pin-1-6)=
(double-width-12-pin-26)=
(double-width-12-pin-2-6)=
(electrical-characteristics)=
- **[Physical connectors](interface/connectors.md):** for you if you want the PMOD connector's pin numbering, single and double width, and its electrical limits.
(standard-pmod-interface-types)=
(type-1--gpio-6-pin)=
(type-1-gpio-6-pin)=
(type-1a--expanded-gpio-12-pin)=
(type-1a-expanded-gpio-12-pin)=
(type-2--spi-6-pin)=
(type-2-spi-6-pin)=
(type-2a--expanded-spi-12-pin)=
(type-2a-expanded-spi-12-pin)=
(type-3--uart-6-pin)=
(type-3-uart-6-pin)=
(type-4--uart-6-pin)=
(type-4-uart-6-pin)=
(type-4a--expanded-uart-12-pin)=
(type-4a-expanded-uart-12-pin)=
(type-5--h-bridge-6-pin)=
(type-5-h-bridge-6-pin)=
(type-6--dual-h-bridge-6-pin)=
(type-6-dual-h-bridge-6-pin)=
- **[The standard interface types](interface/types.md):** for you if you want the pinout of a standard PMOD interface type: GPIO, SPI, UART or H-bridge.
(extended-interface-i2c-8-pin)=
(summary-table)=
- **[The 8-pin I2C interface and the summary table](interface/i2c-summary.md):** for you if you want the extended 8-pin I2C interface, or all the interface types in one table.
(references)=
- **[References](interface/references.md):** for you if you want the sources behind these pages.

## Board-specific pinouts

How the PMOD signals map onto the Raspberry Pi HAT and onto Tiny Tapeout demo boards:

```{toctree}
:maxdepth: 1

rpi-hat
tinytapeout
```

```{toctree}
:hidden:

Physical connectors <interface/connectors>
Interface types <interface/types>
I2C, summary table <interface/i2c-summary>
References <interface/references>
```
