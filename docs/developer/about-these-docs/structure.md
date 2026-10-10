---
type: explanation
owner: documentation maintainers
reader: someone about to add or move a docs.fpgas.online page
review: 2026-11-10
---

# The structure of the documentation

This page explains how docs.fpgas.online is organised: its sections, its page types, its sidebar, and where a
page's source lives. It is for someone about to add or move a page. It does not give the rules for a page's
content or its review; those are [What a page contains](page-contents.md) and
[Review and verification of a page](review.md).

## Sections by audience

The top level starts from four sections, one for each kind of reader. The audiences do not overlap, which is why
the sections are named for them. The four are a starting framework that grows as pages need it, not a fixed list
of contents.

| Section | Reader | Holds |
|---|---|---|
| User documentation | a visitor to a site, with no hardware | using a board from the website |
| Admin documentation | someone who runs a site, with a bench | how the system works, its upkeep, setting up sites and devices |
| Developer documentation | someone with a checkout | changing the code and these docs |
| Resources | anyone looking something up | pinouts, pin numbering, other reference |

A section exists only when a real page sits under it. An empty heading tells the reader that something is there
when nothing is. So the structure is built by re-nesting pages that exist, never by adding headings first.

## The parts of Admin documentation

Admin documentation starts from three parts: how the system works, how to maintain it, and how to set up sites
and devices. A guide to building a Raspberry Pi with an FPGA board belongs with the third part. Like the
sections, the parts are a starting point, and others are added when pages need them.

## Page types inside every section

Inside a section, every page is one of four types. Each type serves a different need, so each has a different
shape. A page that tries to serve two needs leaves both readers hunting, so it is split into two pages that
link each other.

| Type | The reader's need | Shape |
|---|---|---|
| Tutorial | a first success | one safe path, each step showing its result |
| How-to | one task done | fixed headings, numbered steps |
| Reference | a fact looked up | a table or list to scan, no steps |
| Explanation | one thing understood | prose under a noun title, no numbered steps |

One more kind of page holds the others together. A landing page is one line for each destination and nothing
else. Its front matter says `landing`, and only an index page uses it.

## The sidebar

The sidebar nests exactly like the headings of the index page above it. A heading with more than seven entries
gets sub-headings, so a reader can scan any one group. Within a group, pages follow the order in which the reader
works: what it is, which one I have, set it up, check it, look it up.

## Where a page lives

A page's source lives in the repository it is about. A page about a board's wiring lives with the wiring
generator, and a page about the gateway lives with the gateway's code. The documentation repository holds only
the pages about the site as a whole, such as this section.

The docs build pulls each page in from its own repository, and nothing is copied by hand. A pulled page names
its source repository in its opening lines, so a reader knows where to change it. A change to that page is made
there, in the same pull request as the code change that made the page wrong.

A moved or renamed page leaves a redirect. Readers arrive from search and from old links, so an address that
once worked keeps working. The build refuses a rename that has no redirect.
