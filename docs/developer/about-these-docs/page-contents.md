---
type: reference
owner: documentation maintainers
reader: someone writing or checking a docs.fpgas.online page
review: 2026-11-10
---

# What a page contains

This page lists what a docs.fpgas.online page must contain, by page type, with the limits and the diagram set.
It is for someone writing a page or checking one against the rules. It does not explain the reasons or the
review; the sources are in [References on writing documentation](references.md), and the review is in
[Review and verification of a page](review.md).

## Every page

| Part | Value |
|---|---|
| Type | one of tutorial, how-to, reference, explanation; `landing` for an index page |
| Opening | one to three sentences: what the page covers, for whom, what it leaves out |
| Front matter | type, owner, reader, review date |
| Last modified | the date, linked to the commit |
| After a move or rename | a redirect from the old address |
| Smallest size | more than links alone; more than two sentences |
| Feedback | a "was this useful" control, routed to the issue tracker |

Three kinds of content are not on a reader page:

- Plans. They sit on a site's "what this site provides and plans" page and on one roadmap page, each item naming its issue or milestone.
- Dated records of work. They are not pages.
- Broken things. They are issues.

## A how-to

| Part | Value |
|---|---|
| Title | "How to" and exactly what the page shows; unique; 65 characters at most |
| Headings | What you need · Steps · Check · If it fails · Next; this order; no others |
| What you need, bench page | every part with quantity and picture; every tool |
| What you need, software page | the non-obvious prerequisites only, as plain text |
| Steps | numbered; one imperative sentence each: the place, the action, the result |
| Check | what success looks like, pictured or quoted |
| If it fails | at the step where it happens: what you see, the likely cause, the fix |
| Next | five links at most |

## The other page types

| Type | Title | Body |
|---|---|---|
| Tutorial | the first success it reaches | one path from nothing; each step with a visible result; the success state pictured first |
| Explanation | a noun phrase | prose; one idea to a paragraph; no numbered steps |
| Explanation of a board's programming | the board and "programming" | one page for each board, in three layers: protocol, connection, tool |
| Reference | the thing looked up | a table or list, generated from source data where a data file exists; no steps |
| Orientation | the object | the whole object, then a master picture whose numbered callouts are the sections, each with its own crop |
| Identification | the variants | the variants side by side at one orientation and scale; the difference marked; a table of the tells |
| Landing | the section | one line for each destination |
| FAQ | none | none: there is no FAQ page |

## Limits

| Item | Limit |
|---|---|
| Title | 65 characters |
| Sentence | 25 words |
| Paragraph | 3 to 5 sentences |
| List | 2 to 7 items |
| Callouts on a page | 2; none carrying a step or a prerequisite |
| Links on a page | 15 |
| Heading levels | 5 |
| Entries under one sidebar heading | 7 |
| Alt text | 150 characters |

## Words

| Class | Words |
|---|---|
| Banned | `just`, `simply`, `easy`, `easily`, `straightforward`, `please note`, `click here`, `currently`, `soon`, `e.g.`, `i.e.`, `etc.`, `in order to`, `as of this writing` |
| Watched: allowed when not about time | `new`, `now`, `latest` |
| Forbidden phrases | `Future:`, `Sources:`, `unverified`, `TODO`, `not yet`, `as read on` |

## Text

- Detail: full where the reader acts; a summary only where the reader orients.
- The future, the unproven and the unused: none on a reader page. An unknown becomes an issue.
- Names: one name for each thing, as printed on the part. "GPIO 4", never "pin 4".
- Board markings: in bold, as printed.
- Pin 1 and directions: by a visible marker or feature, never by colour, "left" or "above".
- Numbers and dates: none that drift. A version or an issue number anchors what changes.
- A source: one descriptive link in the sentence that needs it. No sources line, section or footnote.

## Pictures

| Aspect | Value |
|---|---|
| First mention | every physical thing named is pictured: the board, then each variant, connector and part |
| Text beside a picture | the action and the check; never a description of the picture |
| Alt text | what the picture shows for this step |
| Render | matched to a photo of the same state before it ships |
| No photo of that state | an existing photo, one from the web, or a line drawing; the wanted photo goes on the list |
| State shown | the object as it sits in that step |
| Viewpoint | one change at most in a sequence, then held |
| In frame | pin 1 and the "this way up" cue |
| Colour | one for each item across the page set |
| Callout numbers | equal to the section numbers |
| Wire colours | the real cable's |
| Labels | on the pin, not in a numbered key |
| Light and dark | one figure that follows the viewer's theme; print gets the light one |
| Terminal output | text, never an image |
| Information in one diagram | one paragraph's worth |

## Diagrams

| Aspect | Value |
|---|---|
| For each step | one action diagram at a fixed viewpoint; never one diagram reused across steps |
| Figure that opens a page | its callouts are the page's sections |
| Model | one: the board geometry, pin 1, the Pi header, `wiring.toml`, the cable |
| A view's id sets | crop, highlight, state, orientation, theme |
| A crop | carries a whole-object inset |
| Part added in the step | at least half visible |
| Earlier parts | at least a tenth visible |
| Attachment point | unoccluded |
| Motion | arrowed |
| Small fasteners | an inset |
| Repeated identical attachments | shown twice, then collapsed |
| Wires, everything connected | crossing, as they do |
| Building diagram | drawn for clarity and for ease of making the cable |
| Debugging diagram | drawn as the real layout |
| Which of the two | stated on the page |

### The build-guide diagram set

| Slot | Shows |
|---|---|
| 1 | the finished cable in place |
| 2 | the cable and its internals |
| 3 | the connectors and the function of every pin |
| 4 | the assembly steps |
| 5 | the verification steps |
| 6 | the plugging-in steps |
| 7 | the result after each major group of steps |
| 8 | the wrong configurations: what you see, the cause, the fix |

### The figures every board gets

| Figure | Shows |
|---|---|
| Whole board | the top and the bottom |
| Connectors | each one, with pin 1 |
| Wiring | the cable as the ribbon lies |
| Programming | the three layers: protocol, connection, tool |
| Variants | the comparison, side by side |
