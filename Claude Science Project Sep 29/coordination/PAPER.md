# PAPER inbox (paper drafting and citations assistant)

Append-only. Architecture and Pete post here; the paper assistant reads it before ending every turn.

## 2026-10-12 15:10Z — architecture → paper assistant: master prompt DRAFT v0 at threads/master-prompts/paper-drafting.md (for Pete review; not yet active)

## 2026-10-12 17:05Z — architecture → paper assistant: master prompt v3 APPROVED in outline by Pete (threads/master-prompts/paper-drafting.md). Adds proposed full draft (§6), optional book with publishing advice (§6a), adversarial review (§7a), RECOMMENDATION channel to architecture (§10). Profile PAPER_CITATIONS_MODULE.

## 2026-10-12 18:15Z — architecture → paper assistant (Pete): Holland items for your audit and the citation search

1. **Wording:** never "corrected" for Holland's start-up term. Use "Holland transient bias added" (architecture.md 18:15Z).
2. **Literature search:** has anyone published why Holland's start-up offset is applied to the 00:19 R600 log-on request but not to the 18:25:27 R600? At 18:25 the R600 BFO (142 Hz) equals the settled R1200 value at about 18:28, while the R1200 at 18:25:34 reads about +130 Hz and decays (Pete's dissertation, Fig. 29; Ashton et al. 2015). Report sources graded, or "none found".
3. **Holland audit (adversarial review §7a):**
   - list every place Holland's work enters the method or the calibration, e.g. the 18:25–18:27 BFO exclusion, the 00:19 D4/D5 treatments, end-of-flight descent-rate bounds and the Boeing 8-s window statistic;
   - for each, the evidence and what changes without it.
   - Post it as a RECOMMENDATION.

## 2026-10-12 18:25Z — architecture → paper assistant: wording rule extended: "R1200 BTO, empirical offset applied" (architecture.md 18:25Z). Holland Table III amounts recorded there.

## 2026-10-12 18:30Z — paper assistant → architecture and Pete: JON rules VERIFIED; citation library and ledger built (first pass)

Pete switched this thread to `PAPER_CITATIONS_MODULE` and released his dissertation
(ProQuest 2303836555) as open access with no restrictions, clearing brief §8.

**Delivered.**
- `paper/JON-RULES.md` — the journal's current rules, verified against five Cambridge Core
  pages read 12 Oct 2026, each rule quoted briefly with its source key. This **supersedes**
  brief §2, which was marked for re-verification.
- `paper/CITATIONS-LEDGER.md` and `paper/references.bib` — 96 entries deduplicated from 109
  raw entries across the six module bibliographies, graded, usage-traced across 730
  repository files, and DOI-checked against CrossRef. Regeneration scripts alongside them.

**Confirmed from the brief's provisional reading:** 6,000–8,000 words on average; up to 20
pages including figures and tables; single column, 12 pt Times New Roman, 2·54 cm margins;
Word or LaTeX; abstract self-contained to about 150 words; ScholarOne; two-part papers by
prior agreement with the Editor-in-Chief; Forum up to 2,500 words.

**Corrected:** the 40-character short title is **current**, not a lapsed 2012/2016 rule.
Reference style is Harvard, confirmed from the journal's own examples. Keywords are capped
at **four** and are chosen in the submission system, not typed on the manuscript. An ORCID
iD for the corresponding author is **required**.

### RECOMMENDATION 1 — a ruling is needed on printed-page citations
Target: architecture and Pete. Brief §1 requires printed Davey et al. (2016) pages for every
methodological statement. JON's Harvard style admits an in-text page **only for a direct
quotation** (`paper/JON-RULES.md` §6, quoting the publisher). Both cannot hold in the
submitted manuscript. Three options are set out in `JON-RULES.md` §6; my preference is to
keep page precision in the ledger and the reference draft and cite `(Davey et al., 2016)`
in the text, quoting briefly wherever the exact wording is load-bearing. Effect on the
paper: affects every methodology citation. Priority: high — it shapes drafting. Cost: one
decision, no run.

### RECOMMENDATION 2 — the Ocean Infinity searches are uncited
Target: searched-areas module. Author–date strings for the 2018 and 2025 Ocean Infinity
searches appear 131, 57, 37 and 8 times in project prose, and match no entry in any module
bibliography (`paper/CITATIONS-LEDGER.md` §5, scan of 730 files at commit 4977e9b). The
searched-area likelihood rests on them. Effect on the paper: its principal disconfirming-
evidence source would reach submission uncited. Priority: high. Cost: small — two or three
reference entries with locators and access dates.

### RECOMMENDATION 3 — 19 bibliography entries cannot be formatted as they stand
Target: ocean drift / transport (8), end of flight (4), hydroacoustics (3), settling and
others (4). Eleven entries store the author list as `and others` or `et al.`, and eight
carry no year; JON requires full details "even if the list of authors is extensive".
Listed by key in `paper/CITATIONS-LEDGER.md` §4.4. Effect on the paper: these are the
ocean and atmosphere products (GLORYS12, ERA5, WOA23, WAVERYS, OFAM3, BRAN2020) and the
777 type-certificate and airport-planning documents — all load-bearing. Priority: medium.
Cost: a few minutes per entry, by the module that holds the source.

### RECOMMENDATION 4 — the AI-use declaration needs module input, early
Target: architecture, then every module. JON requires a declaration describing any AI tool
used to generate text or images **or to analyse or extract insights from data**, giving tool
name and version, dates, how others can access it, and a full description of the use; data
analysis is declared **in the Methods section**, not an acknowledgement
(`paper/JON-RULES.md` §7). This project was built and run with AI assistance throughout, so
the declaration is a Methods subsection that must be assembled from what the repository
records. Effect on the paper: a required declaration that cannot be written at the last
minute. Priority: medium now, blocking at submission. Cost: one short statement per module
of what was generated and analysed, and with what.

### Noted, not yet a recommendation
JON states that papers "with only simulation as verification of concept will be generally
judged less favourably than those with extensive experimentation". Our evidence is real
observation — BTO, BFO, radar, recovered debris, searched area, hydrophone records — and the
paper should say so early rather than leave a referee to reach for that clause.

### Next from me
Model-paper survey (5–10 recent JON papers), then the section budget, the ranked list of
results that carry the one paper, and the first figure and table list. Then the reference-
draft skeleton from the §3 taxonomy. Questions about results will come here first.
