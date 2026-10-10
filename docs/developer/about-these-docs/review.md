---
type: explanation
owner: documentation maintainers
reader: someone whose docs.fpgas.online page is about to be reviewed, or who reviews one
review: 2026-11-10
---

# Review and verification of a page

This page explains what a docs.fpgas.online page goes through between "written" and "merged": the review, the
bench run, the build checks and the merge gate. It is for an author who wants to know what will be asked of a
page, and for a reviewer. It does not list the rules a page is checked against; those are in
[What a page contains](page-contents.md).

## A review in two passes

The reviewer is never the author. The reviewer works from the rendered page and its image files, not from the
markup alone, because a wrong highlight cannot be seen in markup. Before judging a figure, the reviewer says
what it shows.

The first pass uses the page. The reviewer follows it as the reader named in its front matter and returns one
row for each step. Each row answers three questions: could I do it from the picture and one line, what did I
guess, and what did I look for and not find.

The second pass audits the page. The reviewer marks each hardware statement as measured, as taken from the
vendor's document, or as without a source. That audit goes into the review record, not onto the page. A review
that returns only the audit is sent back, because truth without use was the old failure.

The review covers the change, as rendered. A problem outside the change is filed as an issue, not fixed in the
same pull request. Every finding ends in one of two places: fixed in the pull request, or filed as an issue
that the pull request names.

## The shortcuts a reviewer hunts for

Every reviewer is told, in so many words, to hunt for places where a shortcut was taken and the work was left
unfinished. A shortcut passes a fact check, which is why a fact check alone never found one. The table names the
shortcuts found on these pages before the rules existed.

| Where | Shortcut |
|---|---|
| Figures | the overview reused as a step view; one figure repeated |
| Figures | a figure narrated in words; the wrong item highlighted; a part shown without the whole; no before and after |
| Content | a sources line; plans; parts or tools nobody uses; protocol, connection and tool confused |
| Layout | light and dark offered as links; "What you need" as a block of text; a building diagram drawn as laid |
| Coverage | variants without pictures; a step its picture and one line cannot carry; a page that mixes types |

## The bench run

A procedure is executed before it merges, by someone other than the author. A bench page is run on the real
hardware, and a software page in a clean environment. Every stop and every question is written down.

A stop means the step is unfinished. The page does not merge until the stop is answered on the page. This is the
difference between a page that is true and a page that can be followed.

## What the build checks

The build fails a pull request on anything a machine can decide, so that reviewers spend their time on what it
cannot. A warning does not stop a merge, but the author explains it or removes its cause. External links are
checked on a schedule, not on every change, because they break for reasons outside the change.

| Result | Cause |
|---|---|
| Fails | a banned word or forbidden phrase on a reader page |
| Fails | a title over 65 characters, or not unique |
| Fails | a step sentence over 25 words |
| Fails | a how-to with a missing or an extra heading |
| Fails | a bench step with no figure; missing alt text |
| Fails | a light and dark pair outside a switched figure |
| Fails | a sidebar group over seven; more than five heading levels |
| Fails | a link-only page; missing front matter |
| Fails | a rename without a redirect; a broken internal link |
| Fails | generated reference that is older than its source data |
| Fails | a bench page whose print splits a step from its picture |
| Warns | one figure used twice with the same view |
| Warns | more than 15 links, or more than two callouts |
| Warns | an expired review date |

## The merge gate

Four things must hold before a page merges. The independent review is clean. The build is green on the head
that will merge. That head contains the main branch, checked in the merge command itself. And the coordinator
has followed one procedure on the page from start to finish.

A pull request holds one page, or one coherent set of pages such as a board's tree. A change that makes a page
wrong carries the page's fix in the same pull request. Unrelated pages never share one.

## Staying true after the merge

A merged page is kept true by machinery, not by better prose. Reference generated from source data fails the
build when the data changed and the page did not. An expired review date opens an issue to the page's owner.

What is no longer true is removed, not marked. Deprecated content is deleted. A procedure that nobody has
executed is removed. Content that appears twice becomes one source and a link to it.
