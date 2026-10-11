---
type: reference
owner: documentation maintainers
reader: someone who wants the source of a documentation rule
review: 2026-11-10
---

# References on writing documentation

This page lists the published work the docs.fpgas.online rules are built on, with what each one gives us. It is
for someone who wants to read a rule's source before following or changing the rule. It does not restate the
rules. Each row gives a source, what the rules take from it, and one line in the source's own words.

## Page types and structure

| Source | What it gives us | In its words |
|---|---|---|
| [Diátaxis](https://diataxis.fr/start-here/) | the four page types; one reader need to a page | "Crossing or blurring the boundaries described in the map is at the heart of a vast number of problems in documentation" |
| [What nobody tells you about documentation, a PyCon AU talk](https://pyvideo.org/pycon-au-2017/what-nobody-tells-you-about-documentation.html) | the problem the four types solve | "Often, it's not for want of effort ... It simply turns out to be not very good" |
| [Every Page is Page One](https://everypageispageone.com/the-book/) | a page that stands alone; the scope sentences | "Because a reader can arrive at an Every Page is Page One topic from anywhere, the topic must establish its context" |
| [Red Hat modular documentation](https://redhat-documentation.github.io/modular-docs/) | fixed headings on a procedure page | "Do not change or embellish these subheadings. Do not create additional subheadings" |
| [The DITA task topic](https://docs.oasis-open.org/dita/dita/v1.3/os/part3-all-inclusive/archSpec/technicalContent/dita-task-topic.html) | the fixed order of a task's parts | "these optional elements in the following order:" |
| [Carroll and van der Meij on minimalism](https://ris.utwente.nl/ws/files/249663536/Caroll1996ten.pdf) | brevity that serves the task, not brevity for itself | "Brevity is a key element of minimalism, but only because it can facilitate task-oriented activity and learner-initiated reasoning, not as a self-sufficient end in itself" |

## Style and limits

| Source | What it gives us | In its words |
|---|---|---|
| [Google developer documentation style guide: tables](https://developers.google.com/style/tables) | sources as links, not footnotes | "Avoid using footnotes when possible" |
| [Google technical writing course: documents](https://developers.google.com/tech-writing/one/documents) | scope and audience in the opening lines | "A better document additionally defines its non-scope" |
| [GOV.UK: use clear language](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-language/) | the 25-word sentence | "Try to split up sentences that are over 25 words long" |
| [Microsoft Learn Markdown reference](https://learn.microsoft.com/en-us/contribute/content/markdown-reference) | the limit of two callouts | "Readers tend to skip over them" |

## Pictures and assembly instructions

| Source | What it gives us | In its words |
|---|---|---|
| [Mayer's multimedia principles](https://ugc.futurelearn.com/uploads/files/7d/d6/7dd6188d-c343-4311-b064-ac98d2c95abc/Multimedia_Principles._R._E._Mayer__2020.pdf) | each picture beside its step | "People learn better when corresponding words and pictures are presented near rather than far from each other on the page or screen" |
| [The Stanford assembly-instruction study, by Heiser and others](https://www.tc.columbia.edu/faculty/bt2158/faculty-profile/files/esforautomatedgenerationofassemblyinstructions.pdf) | one action diagram to a step, at a fixed viewpoint | "significantly reduce assembly time an average of 35% and error by 50%" |
| [Wordless Instructions, on IKEA's manuals](https://justinzhuang.com/posts/wordless-instructions/) | the finished product first; a test by assembly without text | "a test person manages to assemble the product without any written text in the manual" |

## Review and upkeep

| Source | What it gives us | In its words |
|---|---|---|
| [Write the Docs: documentation principles](https://www.writethedocs.org/guide/writing/docs-principles/) | staleness as a defect; one source for each fact | "Consider incorrect documentation to be worse than missing documentation" |
| [iFixit on content quality](https://www.ifixit.com/Info/content-quality) | a review by someone other than the author | "at least one other team member gives the guide a close look" |

## Which rule comes from which source

The rule numbers are those of [What a page contains](page-contents.md). A source in a table above is named as it is there. Each of the other sources is named by its guide and page.

| Rule | Limit | Source |
|---|---|---|
| 5.1 | a title of 65 characters | GOV.UK, write clear titles |
| 5.2 | a sentence of 25 words | GOV.UK: use clear language |
| 5.3 | a paragraph of 3 to 5 sentences | Google technical writing course, paragraphs: three to five; GOV.UK: use clear language: five at most |
| 5.4 | a list of 2 to 7 items | Microsoft style guide, lists |
| 5.5 | 2 callouts | Microsoft Learn Markdown reference |
| 5.6 | no step or prerequisite in a callout | Google developer documentation style guide, notices |
| 5.7 | 15 links | GitLab documentation style guide |
| 5.8 | 5 heading levels | GitLab documentation style guide |
| 5.9 | 7 entries under a sidebar heading | Mintlify navigation guide |
| 5.10 | alt text of 150 characters | Microsoft style guide, alternative text |
