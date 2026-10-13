# The Journal of Navigation — verified author rules

Owner: paper drafting and citations module (`PAPER_CITATIONS_MODULE`).
Status: **VERIFIED against the publisher's own pages, read 12 October 2026.**

This file replaces the provisional figures in the module brief
(`threads/master-prompts/paper-drafting.md` §2, which were architecture's reading of
12 Oct 2026 and were marked for re-verification). Where this file and the brief differ,
**this file is correct** and the brief should be corrected.

## Sources read

All pages fetched 12 October 2026 from Cambridge Core, the publisher's site for the
journal (published on behalf of The Royal Institute of Navigation). Grade: **official**.

| Key | URL | Text retrieved |
|---|---|---|
| JON-AI | `https://www.cambridge.org/core/journals/journal-of-navigation/information/author-instructions` | 12,186 chars |
| JON-PYM | `https://www.cambridge.org/core/journals/journal-of-navigation/information/author-instructions/preparing-your-materials` | 37,937 chars |
| JON-SYM | `https://www.cambridge.org/core/journals/journal-of-navigation/information/author-instructions/submitting-your-materials` | 17,398 chars |
| JON-PA | `https://www.cambridge.org/core/journals/journal-of-navigation/information/author-instructions/publishing-agreement` | 15,293 chars |
| JON-FEE | `https://www.cambridge.org/core/journals/journal-of-navigation/information/author-instructions/fees-and-pricing` | 12,362 chars |

Local copies of the extracted text are not committed (publisher copyright). Re-fetch to
re-verify. Every rule below carries its source key.

---

## 1. Article type, length and page budget

| Rule | Source |
|---|---|
| Article types accepted: Research Articles, Review Articles, Letters to the Editor, Forum, Editorials. | JON-PYM |
| Length: papers are "on average 6,000-8,000 words long". This is **descriptive, not a stated hard cap**. | JON-PYM |
| Pages: "Average submission page length can be up to 20 pages including Figures and Tables". | JON-PYM |
| Layout: "presented single column 12 point Times New Roman with 2·54 cm margins". | JON-PYM |
| Two-part papers: for subjects needing significantly higher page counts, "this must be discussed with the Editor-in-Chief in advance of submission". | JON-PYM |
| Forum section: opinion and ideas not suited to a full paper, "up to 2,500 words". | JON-PYM |
| Figures and Tables "must all be clearly legible". | JON-PYM |

**Not stated anywhere on these pages:** whether the References list counts toward the
20 pages. Treat as counting until the Editorial Office confirms otherwise — that is the
conservative reading and it is the one that binds our figure budget.

**The 40-character short title survives.** The brief's note that this was a 2012/2016
rule and might be obsolete is wrong: it is current (see §3).

## 2. A rule that bears directly on this paper

> Experimentation: real-world experimentation results should be included where
> appropriate; papers "with only simulation as verification of concept will be generally
> judged less favourably than those with extensive experimentation". — JON-PYM

This is a standing referee risk for a paper whose evidence is an estimator run on
historical data. It is **not** fatal — the data are real observations (BTO, BFO, radar,
recovered debris, searched area, hydrophone records), and the paper should say so
plainly and early rather than letting a referee reach for this clause. Recorded as an
open issue in `paper/ADVERSARIAL-REVIEW.md` when that file opens.

## 3. Title block, abstract, keywords

| Rule | Source |
|---|---|
| Short title: "up to 40 characters". Subtitle optional. | JON-PYM |
| Title block also carries authors' names, affiliations, and **only the corresponding author's** e-mail address. Co-author affiliations by superscript numbering. | JON-PYM |
| Abstract: "self-contained", "up to about 150 words", a **single paragraph**, outlining aims, scope and conclusions. | JON-PYM |
| Keywords: **not** typed on the manuscript. Chosen at submission from the system's list, "a maximum of four". | JON-PYM, JON-SYM |
| Corresponding author must supply an **ORCID iD**; this is required, not optional. | JON-PYM |

## 4. Structure, headings and numbering

| Rule | Source |
|---|---|
| Main text in numbered main paragraphs with **headings in capitals**; numbered sub-paragraphs with italic title-case headings are optional but recommended. | JON-PYM |
| Numbering convention: `3.`, `3.1.`, `3.1.1.` | JON-PYM |
| Bold font "should NOT be used for headings". | JON-PYM |
| Automatic numbering of paragraphs, Figures and Tables switched **OFF**; manual Arabic numerals instead. Automatic linking/hyperlinks **not** used. | JON-PYM |
| Spelling: English (United Kingdom). All acronyms decoded on first use, "even those considered to be commonplace". | JON-PYM |
| Single line spacing, paragraph spacing before and after set to 0, no indents, text fully justified. | JON-PYM |
| A concise, self-contained **Conclusions** section is expected: outcome, benefits to the wider community, and intentions for further research. | JON-PYM |
| Acknowledgements at the end, before References and any appendices. The journal itself must **not** be thanked. | JON-PYM |
| Appendices lettered `A.`, `B.`; their Figure/Table/Equation numbering restarts at 1 but is prefixed by the appendix letter (`A1.`). | JON-PYM |
| Footnotes allowed but "their use should be kept to a minimum". | JON-PYM |

The journal's own suggested structure (JON-SYM) is: Abstract; Keywords; Introduction;
Methods; Results; Discussion (may be combined with Results); Conclusions. Pete's planned
structure maps onto this with Discussion/Conclusions/Recommendations combined, which the
journal explicitly permits for Results and Discussion.

## 5. Equations, units, tables, figures

| Rule | Source |
|---|---|
| Equations numbered sequentially from `(1)`; ideally set in a full-width two-cell table with borders suppressed, expression centred, number right-aligned. | JON-PYM |
| Equations must be **editable**, not pasted pictures. | JON-PYM |
| Units, symbols and abbreviations follow the Royal Society, *Quantities, Units and Symbols* (1975). | JON-PYM |
| Tables numbered sequentially in order of mention; **caption above** the table. | JON-PYM |
| All graphs, diagrams and drawings are "Figures", Arabic numerals from 1, one **caption beneath**, each cited in the text; numbering continues through appendices. | JON-PYM |
| Figures embedded in the manuscript for review; individual figure files required on acceptance. | JON-PYM |
| Figures sized to final publication size (page width from the latest issue). | JON-PYM |
| Colour figures publish in colour online automatically but print in black and white unless hard-copy colour is requested and paid for (the page cites a 2018 cost of UK£200 + VAT per figure, capped at UK£1000 + VAT per article). | JON-PYM |
| Authors are reminded it is their responsibility that colour figures remain meaningful in black and white. | JON-PYM |
| Artwork: line art — tif or eps, black and white, **1200 dpi**. Combination line/tone — tif or eps, greyscale, **800 dpi**. Halftone — tif, CMYK or greyscale, **300 dpi or higher**. | JON-PYM |

**Consequence for our figure set.** Every figure must survive greyscale. That rules out
colour-only distinction between posterior families, ocean models and 00:19 treatments.
Line style, marker and direct labelling must carry the distinction, with colour as a
redundant channel. This is a design constraint on `figure-style`/`figure-composer` work,
not a late conversion step.

## 6. Reference style — Harvard, and one conflict with our convention

| Rule | Source |
|---|---|
| The system is the **Harvard** author–date style. References are hyperlinked online, so correct formatting is "essential". | JON-PYM |
| In-text: not numbered; authors' names **without initials** plus date — `(Kemp, 1998)`; two authors `(Steele and White, 1996)`; more than two `(Cole et al., 2007)`; name may move out of the brackets where the context demands. | JON-PYM |
| **"Specific pages should be added only in the case of direct quotations"**, in the form `(Kemp, 1998. P.29)`. | JON-PYM |
| End list: not numbered; alphabetical by first author's family name; full details "even if the list of authors is extensive". | JON-PYM |

Reference formats, from the journal's own examples (JON-PYM):

```
Journal of Navigation   Rosenkrans, W. A. (1978). Aeronautical Charts. The Journal of
                        Navigation, 31, 39-51.
Other journals          Smart, W. M. (1946). On a Problem in Navigation. Monthly Notices
                        of the Royal Astronomical Society, 106, 124-127.
Books                   Skolnik, M. I. (1976). Radar Systems. McGraw-Hill, Inc.
Websites                Open Geospatial Consortium. (2011). OGC Making Location Count.
                        http://www.opengeospatial.org. Accessed 12 January 2018.
Proceedings             Helwig, A. W. S., Offermans, G. W. A. and van Willigen, D. (1996).
                        Implementation and Testing of Eurofix in Standard Loran-C
                        Receiver Technology. Proceedings of the 25th Annual Technical
                        Symposium of the International Loran Association, San Diego, CA.
```

**CONFLICT, and it needs a ruling.** The project convention (brief §1) is to cite
*printed* Davey et al. (2016) pages for every methodological statement. JON's style
permits an in-text page number **only for a direct quotation**. The two cannot both hold
in the submitted manuscript. Three ways out, in my order of preference:

1. **Keep page-precision in the reference list, not in the text.** Cite
   `(Davey et al., 2016)` in text, and give the chapter or section in the end-list entry
   where the journal's book format allows it. Precision is then one lookup away and the
   style is obeyed.
2. **Quote where precision matters.** Where the exact wording of a Davey assumption is
   load-bearing, quote it briefly — which legitimately earns `(Davey et al., 2016. P.41)`
   under the rule as written.
3. **Keep printed pages in the reference draft and the book only.** The internal
   documents carry full page traceability; the paper carries the style-compliant form.

There is no loss of traceability in any of these: `paper/CITATIONS-LEDGER.md` records the
printed pages for every claim regardless of what the manuscript prints. What must not
happen is a manuscript full of `(Davey et al., 2016. P.112)` that a copy-editor strips,
silently detaching claims from their sources.

No reference-list format is given for **datasets, software or theses**. Our library needs
all three (CMEMS/HYCOM products, GEBCO, the engine itself, Pete's 2019 dissertation).
Proposal: follow the website pattern for datasets and software, with a DOI in place of
the URL and an access date, and the book pattern for the thesis with the degree and
institution in place of the publisher. Flag to the Editorial Office at submission rather
than inventing a style silently.

## 7. Policies that change what we must write

| Rule | Source |
|---|---|
| **Prior publication / preprints.** A manuscript must not be under consideration elsewhere, **but** depositing a preprint on a personal website, in an institutional repository, or in a preprint archive "shall not be viewed as prior or duplicate publication". | JON-PYM |
| **Competing interests.** A declaration is **required** in the main manuscript file. If none: "Competing interests: The author(s) declare none". | JON-PYM |
| **Third-party copyright.** The author must obtain permission for any material they do not own — figures, charts, tables, photographs, excerpts of text — pay any fees, and supply each permission statement at acceptance. | JON-PYM |
| **Supplementary materials** are accepted, published online alongside the article, **not** typeset or copy-edited, and form part of the formal academic record (so not retractable except by correction). | JON-PYM |
| **Accessibility.** WCAG 2.1 Level AA. Alt-text/image descriptions required for **all** figures, supplied via an Accessibility Descriptions Submission Form; machine-generated if the author does not supply them. All diagrams, graphs, maps, boxes and code snippets must be labelled and numbered as Figures. | JON-PYM |
| Submission is through **ScholarOne Manuscripts**; account separate from Cambridge Core. | JON-SYM |

### The AI-use policy, in full effect for this paper

JON-PYM requires declaration and description of AI use. The rules that bind us:

- Generative AI tools "should not be listed as authors".
- Declaration is required where a tool was used to generate text or images, **or** "to
  analyse or extract insights from data or other materials".
- Minimal, non-generative use (spell-checking, single words, formatting) needs no
  declaration — but accountability rests with the author either way, and the page
  specifically warns to check the article thoroughly, "particularly in relation to the
  references".
- Where to declare: text generation in the acknowledgements or a footnote; **data
  collection or analysis in the Methods section**; AI-generated or AI-modified visual
  content in the relevant figure captions.
- How to declare: tool name and version; dates of use; how others can access it; a full
  description of how it was used; citations to third-party material in its output; plus,
  as appropriate, proprietary information, any modification of the tool, and any
  competing interest or bias arising from its ownership or development.

**This is a drafting requirement, not a footnote.** The estimator was built and run with
AI assistance throughout, so the declaration belongs in Methods and must be specific. It
should be drafted early and checked against what the repository actually records, not
written from memory at submission. The reproducibility position is strong — the
repository, configs and commits are public — and the declaration should lean on that.

**Three accessibility consequences** that are cheaper to honour while drafting than to
retrofit: alt-text for every figure; every map and diagram labelled as a Figure and cited
in the text; and the greyscale constraint of §5.

## 8. Open access, fees, agreement

JON-FEE and JON-PA were retrieved and are available for the open-access decision, which
is not yet needed. Article types "may be eligible for APC waivers or discounts" under
Cambridge's open-access agreements (JON-PYM). **Not yet extracted in detail** — do this
before submission, and before any decision on the book's release order (brief §6a),
because the preprint position in §7 interacts with it.

## 9. Open items on the rules themselves

1. **The `nav.cls` LaTeX template.** JON-PYM names "LaTeX source files for submission
   (zip file)" and says authors "should use the nav.cls style file", but the download URL
   is not present in the static page HTML (it is script-rendered). The template must be
   obtained before the proposed draft is laid out, or the layout will be re-done.
2. **Do references count toward the 20 pages?** Not stated. Ask the Editorial Office
   (`journal@rin.org.uk`).
3. **Data-availability statement.** Not required on these pages; they defer to the
   journal's Research Transparency policy, which has not yet been read. Check it — the
   project's public repository makes a strong statement easy, and it may be expected.
4. **Current practice versus stated rules.** The model-paper survey (brief §2) is not yet
   done. Recent JON papers will show how much the stated 6,000-8,000 words and 20 pages
   bind in practice, and how mathematics and references actually appear in print.

---

*Verified and written by the paper drafting and citations module, 12 October 2026.
Re-verify before submission; publisher pages change without notice.*
