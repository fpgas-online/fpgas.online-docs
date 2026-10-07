# Acorn mechanical: the camera over the card

**You are fitting the camera that watches an Acorn's LEDs (an Acorn CLE-215+ on its host) and want to know
where the camera's lens goes over the card.** The drawing is the record; the figures a builder needs are
repeated here in words.

```{image} /_static/mechanical/over-acorn-cle-215-plus-views-light.svg
:alt: The camera over an Acorn CLE-215+: end and front elevations with the lens-face heights, the plan with the LEDs, the notes and the table of lens-face heights
:class: only-light
:target: ../../../_static/mechanical/over-acorn-cle-215-plus-sheet-light.svg
```

```{image} /_static/mechanical/over-acorn-cle-215-plus-views-dark.svg
:alt: The camera over an Acorn CLE-215+: end and front elevations with the lens-face heights, the plan with the LEDs, the notes and the table of lens-face heights
:class: only-dark
:target: ../../../_static/mechanical/over-acorn-cle-215-plus-sheet-dark.svg
```

The whole drawing sheet, with its title block: {download}`light </_static/mechanical/over-acorn-cle-215-plus-sheet-light.svg>`,
{download}`dark </_static/mechanical/over-acorn-cle-215-plus-sheet-dark.svg>` (an SVG: zoom in to read it).

## The figures

- **The lens face goes 60.0 mm above the Acorn card's top face**, where the LEDs at the card's end are, straight
  over those LEDs.
- **The camera's stock lens has to be refocused.** The Raspberry Pi camera module v1.3 is sold with its lens
  focused at about 1 m; at 60 mm it has to be unscrewed to focus (60 mm is the closest a Raspberry Pi forum user
  reports). **Not yet done by us.**
- **Two heights are not known**: S, from the face of the mounting plate to the card's top face, and T, from the
  card's top face to the highest point of the assembly under the camera. Neither is published, and neither has
  been measured by us. So the lens face above the plate is S + 60.0 mm, and the room left above the highest
  part is 60.0 − T mm; the drawing gives them that way, and draws S and T not to scale.
- What is seen on one Acorn today (Tim, 3 October 2026): an autofocus camera (AF-65) on the reference Acorn
  at welland sits about 10 cm above the LEDs, looks in focus, and needs a digital crop of about four times
  to fill the picture with the LEDs.

Source: the sheet RPICAM-OVER-ACORN in
[fpgas.online-mechanical](https://github.com/fpgas-online/fpgas.online-mechanical/tree/main/raspberry_pi_camera),
copied from commit `fd1c69a` (the commit is recorded beside the files in `docs/_static/mechanical/SOURCE`).
