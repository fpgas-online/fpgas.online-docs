---
type: explanation
owner: documentation maintainers
reader: someone mounting a camera over an Acorn
review: 2026-11-10
---

# The camera over an Acorn

This page says where the lens of the camera that watches an Acorn CLE-215+ sits over the card. It is for someone
fitting that camera. The drawing is the sheet RPICAM-OVER-ACORN in
[fpgas.online-mechanical](https://github.com/fpgas-online/fpgas.online-mechanical/tree/main/raspberry_pi_camera);
this page repeats the figures a builder needs in words.

```{image} /_static/mechanical/over-acorn-cle-215-plus-views-light.svg
:alt: The camera over an Acorn CLE-215+: end and front elevations with the lens-face heights, the plan with the LEDs, and the notes
:class: only-light
```

```{image} /_static/mechanical/over-acorn-cle-215-plus-views-dark.svg
:alt: The camera over an Acorn CLE-215+: end and front elevations with the lens-face heights, the plan with the LEDs, and the notes
:class: only-dark
```

## The lens position

The lens face goes 60.0 mm from the Acorn card's top face, straight over the LEDs at the card's end.

## The lens focus

The Raspberry Pi camera module v1.3 is sold with its lens set far, "approx 1 m to infinity" in Raspberry Pi's words.
At 60 mm the stock lens has to be refocused by unscrewing it.
A Raspberry Pi forum user reports 60 mm as the closest focus with the lens still held in its thread.

## The two unknown heights

Two heights are not published. S runs from the face of the mounting plate to the card's top face. T runs from the card's
top face to the highest point of the assembly under the camera. The lens face above the plate is then S + 60.0 mm, and the
room left above the highest part is 60.0 − T mm. The drawing gives them that way and draws S and T not to scale.
