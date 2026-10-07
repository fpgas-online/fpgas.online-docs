# Tiny Tapeout mechanical: the mounting plate

**You are making or fitting the fpgas.online mounting plate for a Tiny Tapeout demo board and want its
figures.** The drawing governs every dimension; the figures a builder needs are repeated here in words. Which
holes your board's revision uses: [the demo board on its mounting plate](mechanical.md).

## The figures

- **The board stands on M3 × 8 mm standoffs**, from the plate's face to the board's underside.
- **The board's holes and slots are 3.4 mm** (clearance for M3); the plate's own fixings, P1 to P6, are
  **4.3 mm** (clearance for M4).
- **Fit the plate to the chassis before the board**: a board overhangs the plate's fixings.
- **Keep the plate's front (lower) edge clear**: the Pmod connectors' bodies overhang it by 2.78 mm.
- The plate is 135.00 × 101.00 mm with 4.00 mm corner radii.

```{image} /_static/mechanical/tt-generic-mounting-plate-views-light.svg
:alt: The mounting plate in plan, with every demo board revision's holes and slots, the plate fixings P1 to P6, the Pmod host fields and USB-C positions, then the legend, the table of which revision uses each hole, and the notes with their sources
:class: only-light
```

```{image} /_static/mechanical/tt-generic-mounting-plate-views-dark.svg
:alt: The mounting plate in plan, with every demo board revision's holes and slots, the plate fixings P1 to P6, the Pmod host fields and USB-C positions, then the legend, the table of which revision uses each hole, and the notes with their sources
:class: only-dark
```

The whole plate drawing, TT-MP-PLATE, with its title block: {download}`PDF
</_static/mechanical/tt-generic-mounting-plate.pdf>`; a preview,
{download}`light </_static/mechanical/tt-generic-mounting-plate-sheet-light.png>`,
{download}`dark </_static/mechanical/tt-generic-mounting-plate-sheet-dark.png>`.

Source: the sheet TT-MP-PLATE in
[fpgas.online-mechanical](https://github.com/fpgas-online/fpgas.online-mechanical/tree/main/tinytapeout/mounting_plate),
copied from commit `64181e1` (the commit is recorded beside the files in `docs/_static/mechanical/SOURCE`).
