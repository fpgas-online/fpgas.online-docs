# Tiny Tapeout mechanical: the demo board on its mounting plate

**You are fitting a Tiny Tapeout demo board to the fpgas.online mounting plate and want to know which holes
your board uses.** This is the fitting guide (each revision of the demo board on the plate); the plate itself is
[its own page](plate.md). The figures a builder needs are repeated here in words. The boards
at welland do not stand on it yet; they move onto it soon, and these pages are written for it (Tim Ansell,
7 October 2026).

## Which board you have, and its holes

```{image} /_static/mechanical/tt-generic-mounting-plate-fitting-guide-views-a-light.svg
:alt: Each Tiny Tapeout demo board revision on the mounting plate, with the holes or slots it uses in red, the holes it does not use and its outline in grey, and its USB-C connector in amber
:class: only-light
```

```{image} /_static/mechanical/tt-generic-mounting-plate-fitting-guide-views-a-dark.svg
:alt: Each Tiny Tapeout demo board revision on the mounting plate, with the holes or slots it uses in red, the holes it does not use and its outline in grey, and its USB-C connector in amber
:class: only-dark
```

- **Find your board by its shuttle or its board revision:**
  - DB mpw: TT02, TT03 (board revisions tt123-v2.2.5, tt123-v2.2.6);
  - DB 4+: TT03p5, TT04, TT05 (v1.2.1 to v1.2.3);
  - DB 06+: TT06, TT07, TT08 (v2.0.1, v2.1.0, v2.1.2);
  - DB ETR v3.2: TT09, TTSKY25a, TTSKY25b, TTGF0p2;
  - DB ETR v3.3: no shuttle shipped on it yet.
- **The holes it uses** (S1 and S2 are slots): DB mpw A1 to A4; DB 4+ B1, B2, S1, S2; DB 06+ C1, C2, S1,
  S2; DB ETR v3.2 A1, D1; DB ETR v3.3 D1, E1.
- **Pmod host positions:** DB mpw uses positions 2 and 3; every other revision uses 1, 2 and 3.
- Revisions in one group share their mounting holes and Pmod positions exactly, but may differ elsewhere:
  v2.1.2's USB-C connector, for one, is 0.9 mm from v2.0.1's.
- The boards on these pages are demo boards **version 3** ([variants](variants.md)). One of them,
  `4df39a7a6856f86f` at welland, reported itself as demo board `TTDBv3 [3.2]` in its boot check of
  5 October 2026 ([the boards at welland](../installations/welland.md)); we take that to be **DB ETR v3.2**
  here (holes A1 and D1), matching the two names, not checked on the board. The other boards' revision has
  not been read.

```{image} /_static/mechanical/tt-generic-mounting-plate-fitting-guide-views-b-light.svg
:alt: Tables of each board's placement on the plate (dX, dY, Pmod positions, holes used) and of its USB-C connector's extent, with the notes
:class: only-light
```

```{image} /_static/mechanical/tt-generic-mounting-plate-fitting-guide-views-b-dark.svg
:alt: Tables of each board's placement on the plate (dX, dY, Pmod positions, holes used) and of its USB-C connector's extent, with the notes
:class: only-dark
```

The whole fitting guide, TT-MP-FIT, with its title block: {download}`PDF
</_static/mechanical/tt-generic-mounting-plate-fitting-guide.pdf>`; a preview,
{download}`light </_static/mechanical/tt-generic-mounting-plate-fitting-guide-sheet-light.png>`,
{download}`dark </_static/mechanical/tt-generic-mounting-plate-fitting-guide-sheet-dark.png>`. It is for
reference: the plate drawing below governs every dimension.

The plate itself, which governs every dimension (standoffs, hole sizes, fitting order, the front edge
kept clear): [the mounting plate](plate.md).

Source: the sheet TT-MP-FIT in
[fpgas.online-mechanical](https://github.com/fpgas-online/fpgas.online-mechanical/tree/main/tinytapeout/mounting_plate),
copied from commit `64181e1` (the commit is recorded beside the files in `docs/_static/mechanical/SOURCE`).
