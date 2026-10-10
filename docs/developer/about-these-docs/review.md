---
type: explanation
owner: documentation maintainers
reader: someone whose docs.fpgas.online page is about to be reviewed, or who reviews one
review: 2026-11-10
---

# Review and verification of a page

This page explains what happens to a docs.fpgas.online page between "written" and "merged". It covers the
review, the bench run, the build checks and the merge gate. It is for an author who wants to know what will be
asked of a page, and for a reviewer. It does not list the rules a page is checked against. Those are on
[What a page contains](page-contents.md).

## What the reviewer is given

The reviewer is never the author. The author hands over four things, so that the review judges the page a
reader will see. Markup alone is not enough, because a wrong highlight cannot be seen in markup.

- The pull request. Its body names the reader and type of each page, the views used and missing, and the photos wanted.
- Every fact left out of the page, each with its issue, also in that body.
- The rendered page as screenshots of each step, at desktop and phone width, in light and dark, with the image files.
- The hardware fact sheet for the board on the page.

## A review in two passes

The first pass uses the page. The reviewer follows it as the reader named in its front matter and returns one
row for each step. Each row answers three questions. Could I do it from the picture and one line? What did I
guess, and what did I look for and not find?

The second pass audits the page. Before judging a figure, the reviewer says what it shows. The reviewer then
marks each hardware statement as measured, as taken from the vendor's document, or as without a source. A review
that returns only the audit is sent back, because truth without use is half a review.

The review covers the change, as rendered. A problem outside the change is filed as an issue, not fixed in the
same pull request. Every finding ends in one of two places: fixed in the pull request, or filed as an issue
that the pull request names.

The review record holds the table of steps, the audit, and every stop of the bench run. None of it goes onto
the page. Generator or tooling code in the same change gets a code review as well.

## The shortcuts a reviewer hunts for

Every reviewer is given one sentence in so many words: "Hunt for places where a shortcut was taken and the work
was not completed". A shortcut passes a fact check, which is why a fact check alone never finds one. The list
names the shortcuts a reviewer hunts for.

- The overview figure reused as a step view; the same figure repeated.
- A figure narrated in words; the wrong item highlighted; a part shown without the whole; no before and after.
- A `Sources:` line; `Future:` or `not yet` content; parts or tools we do not use; protocol, connection and tool confused.
- Light and dark offered as links; "What you need" as a block of text; a building diagram drawn as laid.
- Variants without pictures; a step that cannot be done from its picture and one line; a page that mixes types.

## The bench run

A procedure is executed before it merges, by someone other than the author. A bench page is run on the real
hardware, and a software page in a clean environment. Every stop and every question is written down.

A stop means the step is unfinished. The page does not merge until the stop is answered on the page. This is the
difference between a page that is true and a page that can be followed.

## The build checks

The build fails a pull request on anything a machine can decide, so that reviewers spend their time on what it
cannot. A warning does not stop a merge, but the author explains it or removes its cause. Each check is listed
under [what the build checks](page-contents.md#what-the-build-checks).

## The merge gate

Four things must hold before a page merges. The independent review is clean. The build is green on the head
that will merge. That head contains the main branch, checked in the merge command itself. And a documentation
maintainer has followed one procedure on the page from start to finish.

A pull request holds one page, or one coherent set of pages such as a board's tree. A change that makes a page
wrong carries the page's fix in the same pull request. Unrelated pages never share one.

## Staying true after the merge

A merged page is kept true by machinery, not by better prose. Reference generated from source data fails the
build when the data changed and the page did not. An expired review date opens an issue to the page's owner.

What is no longer true is removed, not marked. Deprecated content is deleted. A procedure that nobody has
executed is removed. Content that appears twice becomes one source and a link to it.
