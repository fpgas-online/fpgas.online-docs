# Tiny Tapeout mechanical: the camera over the mounting plate

**You are fitting the camera that watches a Tiny Tapeout demo board on its mounting plate and want to know
where its lens goes and how it is held.** The drawing is the record; the figures a builder needs are repeated
here in words. How the camera and its holder are put on, step by step, is [fitting, step
6](../building/fitting-2.md#6-the-camera).

## The figures

- **The camera is a Raspberry Pi Camera Module v1.3 with its stock 65 degree lens**, pointing straight down.
- **To see every board revision in focus, the lens face goes 152.4 mm above the mounting plate's face**
  (142.8 mm above the demo board's top face), with the lens axis at X 63.38 mm, Y 44.82 mm in the plate's
  coordinates (frame A on the drawing).
- **To see only the LEDs and the 7-segment displays: 113.3 mm above the plate** (103.7 mm above the board),
  axis at X 67.13 mm, Y 53.12 mm (frame B).
- **The stock lens has to be refocused.** It is sold focused at about 1 m; unscrew it to focus at the
  distance above. **Not done by us as of 7 October 2026.**
- **S**, from the plate's face to the board's top face, is 9.6 ± 0.04 mm (8 mm standoffs and a 1.56 to 1.60 mm
  board). **T**, from the board's top face to its tallest part, is not published: measure it. The clearance
  between the lens face and the tallest part is then 142.8 − T mm (103.7 − T mm for the LEDs-only height).

```{image} /_static/mechanical/over-tt-mounting-plate-views-a-light.svg
:alt: The camera over the Tiny Tapeout mounting plate: end and front elevations with the lens-face heights, the plan with frame A (every board) and frame B (every LED and 7-segment display), the notes, the table of lens-face heights and the table of frames and lens axes
:class: only-light
```

```{image} /_static/mechanical/over-tt-mounting-plate-views-a-dark.svg
:alt: The camera over the Tiny Tapeout mounting plate: end and front elevations with the lens-face heights, the plan with frame A (every board) and frame B (every LED and 7-segment display), the notes, the table of lens-face heights and the table of frames and lens axes
:class: only-dark
```

The drawing's remaining notes and its sources: {download}`light
</_static/mechanical/over-tt-mounting-plate-views-b-light.svg>`, {download}`dark
</_static/mechanical/over-tt-mounting-plate-views-b-dark.svg>`. The whole drawing, RPICAM-OVER-PLATE, with its
title block: {download}`PDF </_static/mechanical/over-tt-mounting-plate.pdf>`; a preview, {download}`light
</_static/mechanical/over-tt-mounting-plate-sheet-light.png>`, {download}`dark
</_static/mechanical/over-tt-mounting-plate-sheet-dark.png>`.

## The holder

The camera hangs from a printed holder, `TT-MP-CAM65`, that bolts onto the plate by the plate's own M4
fixings ([fpgas.online-mechanical](https://github.com/fpgas-online/fpgas.online-mechanical/tree/main/tinytapeout/camera_holder));
it has not yet been built or used by us.

:::{todo}
Open, 7 October 2026: the holder `TT-MP-CAM65` holds the lens face 150.00 mm above the mounting plate, which
was worked out for the lens as sold (focused at about 1 m). With the lens refocused to 142.8 mm, as the camera
drawing now says, seeing every board revision with its 5 mm margin needs the lens face 152.37 mm above the
plate: the holder is 2.37 mm low, more than its 1.00 mm print allowance. The boards are still fully in the
picture, with 3.82 mm of the 5.00 mm margin left along X and 4.11 mm along Y. Whether to raise the holder is
Tim's decision. Source: fpgas.online-mechanical PR #46 (`raspberry_pi_camera/README.md`,
`tinytapeout/camera_holder/README.md`).
:::

Source: the sheet RPICAM-OVER-PLATE in
[fpgas.online-mechanical](https://github.com/fpgas-online/fpgas.online-mechanical/tree/main/raspberry_pi_camera),
copied from commit `4039bfa` (the commit is recorded beside the files in `docs/_static/mechanical/SOURCE`).
