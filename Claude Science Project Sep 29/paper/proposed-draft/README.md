# PROPOSED full draft — assistant draft, not Pete's paper

**This is not the paper.** It is a complete reference draft written by the paper drafting and
citations module so that Pete has something to compare his own working draft against. It is
never merged into his text except where he chooses. Every page of the PDF is headed
*PROPOSED (assistant draft) — not for submission*.

Files: `proposed-draft.tex` (the draft), this README (budget, figure list, provenance).

## 1. Section budget — my recommendation, and what the draft actually spends

The budget is set from the survey of nine papers in the journal
(`paper/JON-MODEL-PAPERS.md`), not from the stated guidance alone. The evidence there: median
19 printed pages, about 7,120 words of main text, 9 figures, 3 tables, 13 numbered equations,
27 end-list references, and no paper from 2019 onward exceeding 19 pages.

Counts below are measured from `proposed-draft.tex`, excluding display equations, tables,
declarations and references.

| Section | Recommended | This draft | Note |
|---|---:|---:|---|
| Abstract | 150 | 143 | Single paragraph, self-contained, as required |
| 1. Introduction | 850 | 645 | Problem, gap, what the paper does, four results |
| 2. The published reconstruction | 650 | 387 | Cites rather than re-derives; carries Table 1 |
| 3. The integrated estimator | 1,800 | 1,718 | 13 numbered equations; the mathematical core |
| 4. What was changed and added | 1,800 | 1,162 | One subsection per element; includes verification |
| 5. Results | 1,400 | 1,279 | Convergence first, then each factor, then negatives |
| 6. Discussion | 750 | 866 | What integration bought; limits; hydroacoustics |
| 7. Conclusions and recommendations | 450 | 345 | Four ordered lines of work |
| **Main text total** | **~7,700** | **6,402** | Inside the 6,000–8,000 band, at its lower end |

13 numbered equations (survey median 13), 3 tables (median 3), **22 end-list references**
(survey median 27, range 2–35, none exceeding 35).

**Citation audit, run against the file rather than estimated.** 22 entries; every entry is
cited in the text, and every in-text citation has an entry. An earlier version of this README
claimed 27 references, which was wrong — the count came from a pattern match that also caught
continuation lines. That version also had 13 of its 21 entries never cited anywhere in the
text, and cited Vincenty (1975) without listing it. Both are fixed: the uncited entries are now
cited at the places where the prose already relied on them — the official record in §2, the
ocean product and the Bayes-factor scale in §3, the leeway and debris-drift literature in §4.4,
the imagery analysis in §4.5, and the hydroacoustic detection literature in §6.3 — and Vincenty
is in the list. Re-run the audit after any edit; a reference list that drifts from the text is
the defect a copy editor will find first.

**Where the remaining ~1,300 words should go, in priority order.** Section 5, which at 1,279
words is carrying nine figures' worth of argument and is the thinnest part of the draft
relative to its importance; then section 4, where the end-of-flight extension deserves more
than the 300 words it currently has, being the largest extension in the paper; then section 1,
which could state the problem's geometry more concretely. Sections 2 and 7 are deliberately
short — 2 because the journal's own practice is to compress inherited method by citation, and 7
because a conclusions section that restates results wastes the reader.

**Three judgements I made that Pete may want to reverse.** First, I put convergence *first* in
the results rather than last, because every number after it is conditional on it; the
conventional ordering would bury it. Second, I merged Discussion with Conclusions and
Recommendations as one pair of sections rather than three, which the journal permits. Third, I
gave the integrated estimator a full section with its own notation rather than relegating the
mathematics to an appendix, because the end-to-end formulation is the paper's methodological
contribution and the surveyed papers keep their central derivation in the main text.

## 2. Figure list — 9 figures, each tied to the result it carries

| # | Figure | Carries | Source |
|---|---|---|---|
| 1 | The estimator as a chain: four stages, what evidence enters where, where the hand-off sits | §3 — makes equation (2) readable | schematic, to draw |
| 2 | Flight-path posterior at 00:11, by stratum, with the 18:01 prior | §3.3, §5.1 | core run I |
| 3 | Fuel and endurance feasibility against commanded Mach and track | §4.1 | fuel model |
| 4 | Effective sample size per evidence factor, per 00:19 treatment | §5.4, §5.7 — the estimability result | `composer-pass2-run-i/fig4-coverage-ess` |
| 5 | Composed impact latitude distribution, per end-of-flight family, with and without the search term | §5.2 — the headline | `composer-pass2-run-i/fig1-impact-latitude` |
| 6 | Log evidence of each composed product with replicate spread | §5.7 | `composer-pass2-run-i/evidence.csv` |
| 7 | Ocean-model sensitivity: the two products and their posterior weight | §5.3 | `composer-pass2-run-i/fig3-ocean-models` |
| 8 | Seabed distribution beside the impact distribution | §5.6 | `composer-pass2-run-i/fig5-seabed` |
| 9 | Predicted hydroacoustic signal level and detection probability by descent family, with the calibration uncertainty band | §6.3 — the value-of-information case | hydroacoustics module |

Three figures (1, 3, 9) do not yet exist. Figures 4 to 8 exist as PDF and PNG in
`results/composer-pass2-run-i/` and need re-rendering to the journal's requirements, which are
strict and easy to miss: **every figure must remain meaningful in black and white**, because
colour prints only if paid for; line art at 1200 dpi, combination art at 800 dpi, halftone at
300 dpi or higher, as tif or eps; caption **below**; and alt-text is required for every figure
at submission. Colour may carry information online but must be redundant with line style,
marker and direct labelling.

Nine figures and three tables will occupy roughly 5 to 7 of the 19 pages on the surveyed
evidence. If that proves too many, figures 3 and 7 are the first to go: 3 supports an element
the paper can describe in prose, and 7 supports a negative result that one sentence can carry.

## 3. Tables — 3, as in the surveyed median

1. Elements of the integrated estimator, classified and with build status (§2).
2. The six 00:19 data treatments against the two causes (§3.5).
3. Coverage limitations that bound the reported distributions, with direction of effect (§6.2).

## 4. Provenance, and what is not yet verifiable

Factual source: `paper/REFERENCE-DRAFT.md` only, which is itself generated from the project
notes. Result numbers are the composer's second composed pass on core run I, carrying that
note's own labels — **not converged; conditional on an equal family prior; end-of-flight physics
provisional; Western Australia non-recovery not modelled**. Those labels are in the draft text,
not in a footnote, because they change how every number should be read.

**Marked for checking in the draft.** Affiliation, e-mail and ORCID; the acknowledgements; the
AI-use declaration, which is required and must be assembled from what the repository records;
the data-availability statement, pending the journal's research transparency policy; one
reference DOI and one incomplete author list.

**Equations 1 to 5, 10, 11 and 12 are my formulation of the implemented structure, not
quotations from a project note.** Equations 6, 7, 8 and 9 are taken from the notes (the 00:19
cause mixture, the ocean-model average, the ocean-model posterior weight, and the search term).
Equation 13 is the project's own split-half threshold. **The formulation ones need checking
against the code before any of this is used** — they are my reading of what the four stages do,
and a reading can be wrong in a way a quotation cannot.

**The hydroacoustic energy figures are deliberately qualitative** in §6.3. The module's specific
predicted levels and the reference-event energy were not in the reference draft, so I described
the comparison in words rather than assert numbers I had not verified. They should be filled in
from the hydroacoustics module through architecture.

**One element is missing entirely.** The impact dissipation duration method could not be
extracted from its note (a content filter refused it), so the duration over which impact energy
is deposited appears in the notation of §3.1 and in the hydroacoustic discussion but has no
method description. It must be written in by hand.

## 5. Compiling

`pdflatex proposed-draft.tex` twice, or `tectonic proposed-draft.tex`. The draft uses
`mathptmx` for Times, `geometry` at 2.54 cm, `amsmath`, `booktabs` and `fancyhdr`.
**It has not been compiled here** — no TeX engine in this sandbox can fetch its package bundle
— so it is checked structurally only: environments and braces balance, 13 equations are free of
double subscripts and stray delimiters, and every command belongs to a loaded package. Expect to
fix small spacing issues on first compile.

The journal accepts Word or LaTeX, wants figures embedded for review, and requires the LaTeX
source only on provisional acceptance, using its own `nav.cls`. **Obtain `nav.cls` before
laying out the real submission** — its download link is script-rendered on the publisher's page
and was not retrievable here, and a late switch of document class will cost a re-layout.
