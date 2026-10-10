---
type: reference
owner: documentation maintainers
reader: someone writing or checking a docs.fpgas.online page
review: 2026-11-10
---

# What a page contains

This page lists what a docs.fpgas.online page must contain, by page type, with the limits and the diagram set.
It is for someone writing a page or checking one against the rules. It does not explain the reasons or the
review. Those are on [References on writing documentation](references.md) and
[Review and verification of a page](review.md). In each table, the first column names the part and the last
column gives what it must be.

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

## Content with another home

| Content | Home |
|---|---|
| A plan | the site's "what this site provides and plans" page, or the roadmap page |
| A planned item's anchor | its issue or its milestone |
| A dated record of work | no page |
| A broken thing | an issue |
| Questions and answers | no page: there is no FAQ |

## A how-to

| Part | Value |
|---|---|
| Title | "How to" and exactly what the page shows; unique; 65 characters at most |
| Headings | What you need · Steps · Check · If it fails · Next; this order; no others |
| What you need, bench page | every part with quantity and picture; every tool |
| What you need, software page | the non-obvious prerequisites only, as plain text |
| Steps | numbered; one bullet to a step; one imperative sentence: the place, the action, then the result in the same paragraph |
| Check | what success looks like, pictured or quoted |
| If it fails | at the step where it happens: what you see, the likely cause, the fix |
| Next | five links at most |

## Other pages

| Page | Type | Title | Body |
|---|---|---|---|
| Tutorial | tutorial | the first success it reaches | one path from nothing; each step with a visible result; the success state pictured first |
| Explanation | explanation | a noun phrase | prose; one idea to a paragraph; no numbered steps |
| Explanation of a board's programming | explanation | the board and "programming" | one page for each board, in three layers: protocol, connection, tool |
| Reference | reference | the thing looked up | a table or list, generated from source data where a data file exists; no steps; no prose beyond the scope sentences and the column definitions |
| Orientation | explanation | the object | the whole object, then a master picture whose numbered callouts are the sections, each with its own crop |
| Identification | reference | the variants | the variants side by side at one orientation and scale; the difference marked; a table of the tells |
| Landing | landing | the section | one line for each destination and nothing else |

## Limits

| Item | Limit |
|---|---|
| Title | 65 characters |
| Sentence | 25 words |
| Paragraph | 3 to 5 sentences |
| List | 2 to 7 items |
| Callouts on a page | 2 |
| Steps or prerequisites inside a callout | 0 |
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
- Names: one name for each thing, as printed on the part, with board markings in bold. "GPIO 4", never "pin 4".
- Pin 1 and directions: by a visible marker or feature, never by colour, "left" or "above".
- Numbers and dates: no number that drifts, and no date except on a fact that is itself dated.
- What changes: anchored by a version or an issue number.
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

## What the build checks

| Check | Result |
|---|---|
| A banned word or a forbidden phrase on a reader page | fails |
| A title over 65 characters | fails |
| A title that is not unique | fails |
| A step sentence over 25 words | fails |
| A how-to with a heading missing | fails |
| A how-to with an extra heading | fails |
| A bench step with no figure | fails |
| Missing alt text | fails |
| A light and dark pair outside a switched figure | fails |
| A sidebar group over seven | fails |
| More than five heading levels | fails |
| A link-only page | fails |
| A rename without a redirect | fails |
| Missing front matter | fails |
| Generated reference older than its source data | fails |
| A broken internal link | fails |
| A bench page whose print splits a step | fails |
| One figure used twice with the same view | warns |
| More than 15 links on a page | warns |
| More than two callouts on a page | warns |
| An expired review date | warns |
| A broken external link | checked on a schedule, not on each change |

