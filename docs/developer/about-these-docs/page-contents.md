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

Every rule carries a number in bold, such as 5.2: the section, then the rule within it. A review finding cites a
rule by that number. Later rules take the next free number in their section, so a cited number keeps its meaning.

## Every page

| Part | Value |
|---|---|
| **1.1** Type | one of tutorial, how-to, reference, explanation; `landing` for an index page |
| **1.2** Opening | one to three sentences: what the page covers, for whom, what it leaves out |
| **1.3** Front matter | type, owner, reader, review date |
| **1.4** Last modified | the date, linked to the commit |
| **1.5** After a move or rename | a redirect from the old address |
| **1.6** Smallest size | more than links alone; more than two sentences |
| **1.7** Feedback | a "was this useful" control, routed to the issue tracker |

## Content with another home

| Content | Home |
|---|---|
| **2.1** A plan | the site's "what this site provides and plans" page, or the roadmap page |
| **2.2** A planned item's anchor | its issue or its milestone |
| **2.3** A dated record of work | no page |
| **2.4** A broken thing | an issue |
| **2.5** Questions and answers | no page: there is no FAQ |

## A how-to

| Part | Value |
|---|---|
| **3.1** Title | "How to" and exactly what the page shows; unique; 65 characters at most |
| **3.2** Headings | What you need · Steps · Check · If it fails · Next; this order; no others |
| **3.3** What you need, bench page | every part with quantity and picture; every tool |
| **3.4** What you need, software page | the non-obvious prerequisites only, as plain text |
| **3.5** Steps | numbered; one bullet to a step; one imperative sentence: the place, the action, then the result in the same paragraph |
| **3.6** Check | what success looks like, pictured or quoted |
| **3.7** If it fails | at the step where it happens: what you see, the likely cause, the fix |
| **3.8** Next | five links at most |

## Other pages

| Page | Type | Title | Body |
|---|---|---|---|
| **4.1** Tutorial | tutorial | the first success it reaches | one path from nothing; each step with a visible result; the success state pictured first |
| **4.2** Explanation | explanation | a noun phrase | prose; one idea to a paragraph; no numbered steps |
| **4.3** Explanation of a board's programming | explanation | the board and "programming" | one page for each board, in three layers: protocol, connection, tool |
| **4.4** Reference | reference | the thing looked up | a table or list, generated from source data where a data file exists; no steps; no prose beyond the scope sentences and the column definitions |
| **4.5** Orientation | explanation | the object | the whole object, then a master picture whose numbered callouts are the sections, each with its own crop |
| **4.6** Identification | reference | the variants | the variants side by side at one orientation and scale; the difference marked; a table of the tells |
| **4.7** Landing | landing | the section | one line for each destination and nothing else |

## Limits

| Item | Limit |
|---|---|
| **5.1** Title | 65 characters |
| **5.2** Sentence | 25 words |
| **5.3** Paragraph | 3 to 5 sentences |
| **5.4** List | 2 to 7 items |
| **5.5** Callouts on a page | 2 |
| **5.6** Steps or prerequisites inside a callout | 0 |
| **5.7** Links on a page | 15 |
| **5.8** Heading levels | 5 |
| **5.9** Entries under one sidebar heading | 7 |
| **5.10** Alt text | 150 characters |

## Words

| Class | Words |
|---|---|
| **6.1** Banned | `just`, `simply`, `easy`, `easily`, `straightforward`, `please note`, `click here`, `currently`, `soon`, `e.g.`, `i.e.`, `etc.`, `in order to`, `as of this writing` |
| **6.2** Watched: allowed when not about time | `new`, `now`, `latest` |
| **6.3** Forbidden phrases | `Future:`, `Sources:`, `unverified`, `TODO`, `not yet`, `as read on` |

## Text

- **7.1** Detail: full where the reader acts; a summary only where the reader orients.
- **7.2** The future, the unproven and the unused: none on a reader page. An unknown becomes an issue.
- **7.3** Names: one name for each thing, as printed on the part, with board markings in bold. "GPIO 4", never "pin 4".
- **7.4** Pin 1 and directions: by a visible marker or feature, never by colour, "left" or "above".
- **7.5** Numbers and dates: no number that drifts, and no date except on a fact that is itself dated.
- **7.6** What changes: anchored by a version or an issue number.
- **7.7** A source: one descriptive link in the sentence that needs it. No sources line, section or footnote.

## Pictures

| Aspect | Value |
|---|---|
| **8.1** First mention | every physical thing named is pictured: the board, then each variant, connector and part |
| **8.2** Text beside a picture | the action and the check; never a description of the picture |
| **8.3** Alt text | what the picture shows for this step |
| **8.4** Render | matched to a photo of the same state before it ships |
| **8.5** No photo of that state | an existing photo, one from the web, or a line drawing; the wanted photo goes on the list |
| **8.6** State shown | the object as it sits in that step |
| **8.7** Viewpoint | one change at most in a sequence, then held |
| **8.8** In frame | pin 1 and the "this way up" cue |
| **8.9** Colour | one for each item across the page set |
| **8.10** Callout numbers | equal to the section numbers |
| **8.11** Wire colours | the real cable's |
| **8.12** Labels | on the pin, not in a numbered key |
| **8.13** Light and dark | one figure that follows the viewer's theme; print gets the light one |
| **8.14** Terminal output | text, never an image |
| **8.15** Information in one diagram | one paragraph's worth |

## Diagrams

| Aspect | Value |
|---|---|
| **9.1** For each step | one action diagram at a fixed viewpoint; never one diagram reused across steps |
| **9.2** Figure that opens a page | its callouts are the page's sections |
| **9.3** Model | one: the board geometry, pin 1, the Pi header, `wiring.toml`, the cable |
| **9.4** A view's id sets | crop, highlight, state, orientation, theme |
| **9.5** A crop | carries a whole-object inset |
| **9.6** Part added in the step | at least half visible |
| **9.7** Earlier parts | at least a tenth visible |
| **9.8** Attachment point | unoccluded |
| **9.9** Motion | arrowed |
| **9.10** Small fasteners | an inset |
| **9.11** Repeated identical attachments | shown twice, then collapsed |
| **9.12** Wires, everything connected | crossing, as they do |
| **9.13** Building diagram | drawn for clarity and for ease of making the cable |
| **9.14** Debugging diagram | drawn as the real layout |
| **9.15** Which of the two | stated on the page |

### The build-guide diagram set

| Slot | Shows |
|---|---|
| **9.16** 1 | the finished cable in place |
| **9.17** 2 | the cable and its internals |
| **9.18** 3 | the connectors and the function of every pin |
| **9.19** 4 | the assembly steps |
| **9.20** 5 | the verification steps |
| **9.21** 6 | the plugging-in steps |
| **9.22** 7 | the result after each major group of steps |
| **9.23** 8 | the wrong configurations: what you see, the cause, the fix |

### The figures every board gets

| Figure | Shows |
|---|---|
| **9.24** Whole board | the top and the bottom |
| **9.25** Connectors | each one, with pin 1 |
| **9.26** Wiring | the cable as the ribbon lies |
| **9.27** Programming | the three layers: protocol, connection, tool |
| **9.28** Variants | the comparison, side by side |

## What the build checks

| Check | Result |
|---|---|
| **10.1** A banned word or a forbidden phrase on a reader page | fails |
| **10.2** A title over 65 characters | fails |
| **10.3** A title that is not unique | fails |
| **10.4** A step sentence over 25 words | fails |
| **10.5** A how-to with a heading missing | fails |
| **10.6** A how-to with an extra heading | fails |
| **10.7** A bench step with no figure | fails |
| **10.8** Missing alt text | fails |
| **10.9** A light and dark pair outside a switched figure | fails |
| **10.10** A sidebar group over seven | fails |
| **10.11** More than five heading levels | fails |
| **10.12** A link-only page | fails |
| **10.13** A rename without a redirect | fails |
| **10.14** Missing front matter | fails |
| **10.15** Generated reference older than its source data | fails |
| **10.16** A broken internal link | fails |
| **10.17** A bench page whose print splits a step | fails |
| **10.18** One figure used twice with the same view | warns |
| **10.19** More than 15 links on a page | warns |
| **10.20** More than two callouts on a page | warns |
| **10.21** An expired review date | warns |
| **10.22** A broken external link | checked on a schedule, not on each change |

