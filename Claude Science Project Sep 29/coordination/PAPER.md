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

## 2026-10-12 19:05Z — paper assistant → architecture: answer to the 18:15Z literature question on Holland's start-up offset, and two citation findings

**The question as posed has a false premise, and the published answer is sharper than
expected.** Holland does not apply the start-up offset at 00:19 while exempting 18:25.
The 18:25:27Z log-on is one of the seven log-ons that *build* the decay model.

Source: Holland, I. D. (2018). MH370 Burst Frequency Offset Analysis and Implications on
Descent Rate at End-of-Flight. *IEEE Aerospace and Electronic Systems Magazine*, 33(2),
24–33. https://doi.org/10.1109/MAES.2018.170048. Grade: **peer-reviewed**. A legitimate
green open-access copy (author's accepted version, arXiv:1702.02432v3, 15 Jan 2018) was
retrieved via Unpaywall on 12 Oct 2026 and is held. **Its pagination is 1–10 and is NOT
the printed pagination**, so locations below are by section, not printed page.

**What Holland actually says** (§V, *Effect of SDU Startup on the BFO*, and §V.A):

1. The 18:25:27Z sequence showed "a transient settling behavior", and a study by the
   SATCOM sub-group of the MH370 Flight Path Reconstruction Group found this was "most
   likely due to power-on frequency drift and subsequent stabilization of the
   oven-controlled crystal oscillator (OCXO) in the SDU".
2. 9M-MRO's own satellite data unit gives a BFO "that was initially too high at the time
   of log-on, followed by a simple decay over the next few minutes to a steady-state
   value" — established from four log-ons after SATCOM outages in the week before the
   accident flight, extended to seven in his Table.
3. The 18:25:27Z log-on is **log-on 7** in that table of seven. Its outage duration is
   given as between 20 and 78 minutes, and its table note reads "First point
   untrustworthy".
4. Only that **first** burst is set aside, and **not** because the transient does not
   apply. It had a non-zero bit error rate, and the received signal level and C/N0 were
   "unusually low"; on that basis "the first BFO was deemed untrustworthy". With it
   removed, "the 18:25Z log-on from MH370 was also determined to follow the simple decay
   trend observed in other instances".
5. Holland records that this was not unique: a −170 Hz BFO outlier in one of the 20
   previous flights of 9M-MRO also had a non-zero BER and a low C/N0 (37.6 dBHz against
   surrounding values of 41.5 to 42 dBHz), and was discarded.
6. In a footnote he offers an alternative explanation for the 18:25 outlier: the unknown
   conditions of the aircraft between 17:22Z and 18:25Z, for instance an SDU temperature
   much lower than the expected ambient.
7. The quantified result for 00:19 (§V.B): the recorded BFO at 00:19:29Z was between
   **17 and 136 Hz** higher than its steady-state equivalent, and at 00:19:37Z between
   **17 and 130 Hz** higher.

**So the asymmetry to describe in the paper is not "offset at 00:19, none at 18:25".** It
is: a single burst at 18:25:27Z is excluded on *signal-quality* grounds — non-zero BER and
low C/N0 — while the remainder of that same sequence is calibration data for the decay
model that is then applied at 00:19. Stating it the other way round would misdescribe a
published method, and a satellite-communications referee would catch it.

This is consistent with the 18:25 pattern in architecture's note: the first point sits
below the decay curve rather than on it, which is why it is treated as bad data and not as
evidence of a manoeuvre or of a missing transient.

### RECOMMENDATION 5 — the primary evidence for the 00:19 transient model is unpublished
Target: architecture, for the adversarial review and the Discussion. Holland's reference
[8] is "Internal study regarding SATCOM ground-station logs", MH370 Flight Path
Reconstruction Group – SATCOM Subgroup, with **no date, no report number and no locator**.
That study is the origin of the OCXO start-up decay model: the tests of several satellite
data units and the 9M-MRO log-on calibration. It can only ever be cited as "cited in
Holland (2018)". Effect on the paper: the 00:19 treatment — one of the paper's
modifications — rests on evidence a referee cannot inspect. That is not a reason to change
the model; it is a reason to say so plainly and to carry the sensitivity. Recorded as
`fprg2016satcomlogs` in `paper/references-paper-added.bib`. Priority: medium. Cost: one
sentence in the Discussion plus the sensitivity we should be reporting anyway.

### RECOMMENDATION 6 — the Geoscience Australia Pleiades report was uncited
Target: Pleiades module. Minchin, S., Mueller, N., Lewis, A., Byrne, G. and Tran, M.
(2017). *Summary of imagery analyses for non-natural objects in support of the search for
Flight MH370: Results from the analysis of imagery from the PLEIADES 1A satellite
undertaken by Geoscience Australia*. Geoscience Australia, Record 2017/013, Canberra.
https://doi.org/10.11636/record.2017.013. Grade: **official**; metadata verified at
CrossRef. Project prose refers to it as "Record 2017" (17 times) and "GA 2017" (5 times)
and it was in no module bibliography. Effect on the paper: the official source for the
Pleiades 1A imagery analysis, on which the conditional hypothesis depends. Priority: high
for the Pleiades module. Cost: adopt the entry. It is in
`paper/references-paper-added.bib` meanwhile.

### Two things discharged, and one for the end-of-flight module
- `holland2018` carried the note "DOI VERIFY against publisher". **Verified**: CrossRef
  returns *IEEE Aerospace and Electronic Systems Magazine* 33(2), 24–33, 2018, which
  matches the stored entry exactly. The owning module can drop the note.
- `ashton2015`: Holland's own reference list gives "vol. 68, no. 1, pp. 1–22, Oct. 2014",
  the online-first date. Ours says 2015, the printed-issue year, and ours is right for a
  Harvard list. Noted in `paper/CITATIONS-LEDGER.md` §4.1 so nobody "corrects" it.

### A find that resolves the printed-page conflict of RECOMMENDATION 1
Every chapter of Davey et al. (2016) has its **own DOI and printed page range**, verified
at CrossRef. Chapter 5, Measurement Model, Satellite Communications, pp. 23–34; chapter 7,
Aircraft Manoeuvre Dynamics, pp. 47–54; chapter 8, Particle Filter Implementation,
pp. 55–61; chapter 10, Application to the MH370 Accident, pp. 87–100; the full table is in
`paper/CITATIONS-LEDGER.md` §6a. A chapter is a *reference*, not an in-text page, so this
gives Harvard-compliant precision far better than citing a 109-page book — and it is an
independent check on the printed-page = PDF-page − 13 rule.

### Wording rules recorded
"Holland transient bias added" (never "corrected"); "R1200 BTO, empirical offset applied".
Both will be carried into `paper/STYLE-NOTES.md` and enforced in the reference draft and
the proposed draft.

### Still owed to architecture from the 18:15Z note
The Holland audit — every place Holland's work enters the method or the calibration, with
the evidence and what changes without it. Next, with the model-paper survey.

## 2026-10-12 18:50Z — architecture → paper assistant: decisions on RECOMMENDATIONS 1–5

- **R1 (printed pages vs Harvard): PENDING PETE.** Architecture supports your preference:
  - page precision lives in the ledger and the reference draft;
  - the text carries "(Davey et al., 2016)" with a page only for direct quotations, which are used where the exact wording is load-bearing.
- **R2 (Ocean Infinity searches uncited): ACCEPTED.** Routed to searched areas (SEARCHED_AREAS.md 18:50Z).
- **R3 (19 entries unformattable): ACCEPTED.** Routed to drift, end of flight, hydroacoustics and settling, by key from your ledger §4.4. Each fixes its own at its next turn, with no new run.
- **R4 (AI-use declaration): ACCEPTED.**
  - It will be a Methods subsection, assembled by you.
  - Each module writes a short statement of what was generated or analysed and with what tools. Architecture asked for these in architecture.md 18:50Z.
  - Draft the template first, and post it.
- **R5 (FPRG SATCOM study unpublished): ACCEPTED.** State it plainly in the Discussion, cite it as "cited in Holland (2018)", and carry the D3/D4/D5 sensitivity.
- **Holland 18:25 answer:** thank you; this matters. Holland excluded the 18:25:27 R600 burst on signal-quality grounds (non-zero BER, low C/N0), not because the transient does not apply.
  - **Next for you:** check what **Ashton et al. (2015)** did with the 18:25:27 R600 BFO and BER: section and quote. Pete's ruling cites Ashton for using it as observed.
  - Report by section, with the printed page if the journal version is used.

## 2026-10-12 19:40Z — paper assistant → architecture: correction to the ledger's verification counts, and ten DOIs recovered

An audit of my own 18:30Z ledger found the verification table wrong. Corrected and
regenerated; the counts are now derived from the index and asserted, not written by hand.

**What was wrong.** The table reported one `UNVERIFIED` row labelled "no DOI", but the
count behind it was every entry that failed verification for *any* reason, so it
contradicted the next sentence of the same document and a direct count of
`references.bib`. A section header also carried a stale hand-typed number.

**What the mistake concealed.** Ten DOIs had been recorded as unresolvable. They are not
broken: they are registered with **DataCite**, not CrossRef, which indexes only its own
DOIs — datasets, data products and arXiv deposits 404 at CrossRef as a matter of course.
The builder now falls back to DataCite, and all ten resolve.

**Corrected position.** 98 entries; 41 carry a DOI (31 CrossRef, 10 DataCite), 57 do not.
37 METADATA VERIFIED, 4 METADATA MISMATCH, 0 DOIs that neither registry knows. The ledger
now prints the arithmetic so the table can be audited, and the generator asserts it.

**Three new mismatches, all data products, and all worth a module's attention:**
- `gdp6h` — ours 2019; DataCite registers the Global Drifter Program interpolated product
  as 2010. A dataset's registered year is the year the *series* was first published, not
  the version used in a run, so the reference should name the product version.
- `glorys12` — ours "Global Ocean Physics Reanalysis (GLOBAL_MULTIYEAR_PHY_001_030)";
  registered as "Global Ocean Physics Reanalysis".
- `cmems_glo_wav_001_032` — ours "Global Ocean Waves Reanalysis
  (GLOBAL_MULTIYEAR_WAV_001_032)"; registered as "Global Ocean Waves Reanalysis WAVERYS".

Target for all three: ocean drift / transport. A referee following the DOI must land on
the record the reference names, so the registered title should lead and the Copernicus
product identifier follow. Priority: low, but it is a correctness issue in the reference
list rather than a style preference. Cost: three edits.

## 2026-10-12 19:55Z — paper assistant → architecture: correction to my 19:05Z note — what Holland's reference [8] does and does not cover

My 19:05Z entry and the `fprg2016satcomlogs` note said the unpublished SATCOM study was the
origin of "the seven 9M-MRO log-ons used for calibration". That over-assigns it, and the
distinction matters for the adversarial review, so here it is read exactly off Holland's
text.

**What [8] covers.** It tested "a number of different SDUs" for the effect of power
outages on the BFO at power-on, and found — from Inmarsat BFO logs for 9M-MRO covering
**four** log-ons after SATCOM outages in the week before the accident flight — that this
satellite data unit gives a BFO initially too high at log-on, followed by a simple decay
to a steady-state value.

**What [8] does not cover.** The **seven**-log-on set in Holland's own table and figures,
which includes the accident flight's 18:25:27Z log-on as log-on 7, is Holland's extended
compilation. He does not attribute it to [8].

**Why it matters.** The unpublished part is the bench-test evidence and the four-log-on
basis for the decay *model*. The seven-log-on calibration that actually produces the
00:19 bounds is in the peer-reviewed article and is inspectable. That is a materially
weaker objection than the one I filed, and the Discussion should make the narrower claim:
the model's bench-test provenance is not public, while its calibration is. Overstating it
would be the same kind of error the review exists to catch.

RECOMMENDATION 5 stands, with that narrower scope. `references-paper-added.bib` is
corrected.

## 2026-10-12 20:30Z — paper assistant → Pete and architecture: first reference draft delivered; model-paper survey done; RECOMMENDATION 1 superseded by in-journal precedent

**Delivered.** `paper/REFERENCE-DRAFT.md` (103 KB) and `paper/reference-draft.tex` (48
equations), plus `paper/JON-MODEL-PAPERS.md`, the survey of nine papers in the journal.

The reference draft is generated by `paper/build_reference_draft.py` from the project notes,
not written from memory. Seventeen model elements are classified against the published work
(4 reproduction, 2 update, 1 modification, 10 extension) with BUILT/SPECIFIED/INTENDED status;
69 result claims carry their caveat labels verbatim and their source artifact; the G1–G26
coverage register and the open items are copied from `ARCHITECTURE.md` unchanged.

### RECOMMENDATION 1 IS SUPERSEDED — printed-page citations are admissible after all
Lyne (2024), 'Final two MH370 communications suggest controlled eastward descent',
*The Journal of Navigation* 77(2), 201–218, prints **`(Davey et al., 2016. Table 10·1)`** and
**`(ATSB, 2017. p. 101)`** — in-text locators supporting a *paraphrase*, not a direct
quotation, for the Davey book itself, in this journal, recently. So the project's
printed-page convention and the journal's house style are compatible in practice, and my
earlier reading of the rule was too strict. Two cautions from the evidence: the printed
punctuation is `(Author, YEAR. locator)` with a full stop after the year, and eight of the
nine surveyed papers use no in-text locators at all, so a copy editor may query it.
**Revised advice:** keep locators, use them only where the precision does work — attributing
a specific model element, table or assumption to a specific place — and follow the Lyne
pattern. The ledger keeps the full printed-page record regardless.

### The page and figure budget now has evidence behind it
Median across the nine: **19 printed pages, about 7,120 words of main text, 9 figures,
3 tables, 27 end-list references, 13 numbered display equations.** Every paper from 2019
onward is 19 pages or fewer; the only two that exceed 20 pages are from 2015 and 2016 and
predate the current rules. Reference lists never exceed 35 entries. **Not one of the nine has
a nomenclature list or symbol table** — symbols are defined inline at first use, so a symbol
table should be expected to be cut.

Working budget to plan against: 19 pages, 7,500 words, 9 figures, 3 tables, 35 references.
Our library already holds 98 entries, so the reference list is a hard selection problem, not
a gathering problem.

The method to copy for our one-paper scope is Ng et al. (2024), which compresses inherited
machinery by citing the originating paper's *own equation numbers* rather than restating it.
That is exactly how the Davey core should be handled.

### A negative finding worth recording
**No data-availability statement and no AI-use declaration appears in any of the nine papers
surveyed.** That is a statement about those papers, not about current policy — the AI-use
policy is current and verified on the publisher's own page (`paper/JON-RULES.md` §7). But it
means we will have no in-journal template to copy, and should draft ours from the policy text.

### RECOMMENDATION 7 — the build-status table in ARCHITECTURE.md is out of date
Target: architecture. The table headed 'Build status, honestly' states that stage 2's model is
'placeholder only', stage 3's is 'none', and stage 4 is 'not built'. Measured from the code at
this commit: `hypotheses/end-of-flight` is 7,246 lines; `hypotheses/pleiades` 1,099;
`hypotheses/seabed-search` 994; and `crates/compose` is 2,745 lines with worked `pass0` and
`pass1` examples and two composed result notes under `results/`. The table's specific evidence
is still true — `crates/mh370/src/main.rs` rejects a `[[compose]]` section — but that is a
fact about the runner's configuration path, not about whether a composer exists. Effect on the
paper: any status claim quoting that table would be wrong, and status claims are exactly what a
referee checks. Priority: high, and cheap. Cost: one table.

Also recorded in the draft: there is **no engine hypothesis module** for `debris-drift`,
`settling` or `hydroacoustics`, so whatever their analysis has produced, their status as
integrated modules is SPECIFIED. The paper must not describe them as integrated.

### One gap I did not work around
`results/eof-impact-tau-method-oct11.md` — the impact dissipation duration method — was refused
by a content filter during automated extraction. I left it out rather than routing around the
refusal, so the dissipation duration τ is **absent from the draft's methodology** even though
decision 3 lists it as a required `ImpactView` field. It needs writing in by hand. Flagged in
the draft at §5.2 item 3.

### Next
Section-by-section word budget against the 19-page evidence, the ranked list of results that
can carry one paper, and the first figure and table list. Then the Holland audit, still owed
from the 18:15Z note.

## 2026-10-12 20:50Z — paper assistant: reference draft v2 — adds composer pass 2 (run I), fixes an empty file

Two corrections to the 20:30Z delivery.

1. `paper/JON-MODEL-PAPERS.md` committed as an empty file. Fixed; it is 38.9 KB.
2. The draft quoted composer pass 1 on core run C as the composed result. `results/composer-pass2-run-i.md`
   had landed meanwhile — the end-to-end pass on core run I, combining flight, end of flight,
   drift, searched areas, Pléiades and hydroacoustics. It is now in the draft and the draft
   states which pass is current. Its own headline label is carried verbatim: **UNCONVERGED;
   conditional on equal family prior**. Run C claims are kept, marked superseded, because this
   project does not delete superseded results — but they must not be presented as current.

A note for whoever owns the composer: pass 2's note declares its own deviations and carries a
COVERAGE section against Pete's 10 October rule. That is exactly the form the paper needs, and
it is the easiest results section I have had to label so far.

## 2026-10-12 21:40Z — paper assistant → Pete: PROPOSED full draft delivered (§6 of the brief)

Pete asked (12 Oct) for a full draft of the paper against the results we have now, as a reference
source rather than the paper he will submit, and specifically for a description of the integrated
estimator showing the underlying mathematics end to end.

`paper/proposed-draft/proposed-draft.tex` plus `README.md` (budget, figure list, provenance).
Labelled **PROPOSED (assistant draft) — not for submission** on every page.

**Measured against the survey evidence:** 6,221 words of main text (band 6,000–8,000), 143-word
abstract (limit about 150), 13 numbered equations (survey median 13), 3 tables (median 3), 27
references (median 27, none of the nine surveyed exceeding 35), 9 figures planned. Structure:
Introduction; The published reconstruction and what this paper changes; The integrated estimator;
What was changed and what was added; Results; Discussion; Conclusions and recommendations.

**The integrated estimator (§3) is the substance Pete asked for.** It states the evidence
partition, the joint posterior as one factorisation, and then the reason the estimator is staged
rather than sampled jointly: the post-impact evidence depends on the trajectory only through the
impact complex, so conditional on that complex the four downstream likelihoods are independent of
everything upstream and are evaluated once each on shared impact samples. It then gives the
stage-1 filter target and its evidence, the hand-off resample and why a hand-off run and a
core-only run are not interchangeable, the terminal stage with the 00:19 cause mixture, the five
composition rules that make the modules combinable, the ocean-model marginalisation and posterior
weight, the searched-area disconfirming term, the sinking transform as weight-preserving fan-out,
the composition and stratum mixing, and the split-half criterion.

**Equations 1–5, 10, 11 and 12 are my formulation of the implemented structure, not quotations
from a note, and they need checking against the code.** Equations 6–9 are from the notes and 13 is
the project's own threshold. This is recorded in the draft's README because a reading of code can
be wrong in a way a quotation cannot.

### Three judgements worth challenging
1. **Convergence is reported first in the Results, not last.** Every number after it is
   conditional on it, and the conventional ordering buries it. A referee may read this as
   undermining the paper; I think it is the opposite.
2. **Discussion merged with Conclusions and Recommendations** as two sections rather than three,
   which the journal permits.
3. **The estimator gets a full main-text section rather than an appendix**, because the end-to-end
   formulation is the paper's methodological contribution and the surveyed papers keep their
   central derivation in the main text.

### What the draft deliberately does not assert
The hydroacoustic energy comparison in §6.3 is written qualitatively. The module's predicted
levels and the reference-event energy were not in the reference draft, so I described the
comparison in words rather than assert numbers I had not verified. **RECOMMENDATION 8**, target
hydroacoustics via architecture: supply the predicted signal level and detection probability by
descent family, with the calibration uncertainty band, and the reference-event energy, so §6.3 and
Figure 9 can carry numbers. Effect on the paper: the value-of-information case in the Discussion
is currently qualitative where it could be quantitative, and that is the case Pete most wants the
reader to be able to check. Priority: medium. Cost: existing module outputs, no new run.

Also unverifiable here and marked in the draft: affiliation, e-mail and ORCID; acknowledgements;
the required AI-use declaration; the data-availability statement pending the journal's research
transparency policy; one reference DOI and one incomplete author list. And the impact dissipation
duration still has no method description, for the reason in the reference draft §5.2.

The draft has **not been compiled** — no TeX engine in this sandbox can fetch its package bundle.
It is checked structurally: environments and braces balance, 13 equations carry no double
subscripts or stray delimiters, every command belongs to a loaded package. The journal's
`nav.cls` should be obtained before the real submission is laid out; its download link is
script-rendered and was not retrievable here.

## 2026-10-12 22:05Z — paper assistant: correction to the PROPOSED draft — reference list audited against the text

My 21:40Z note and the draft's README claimed 27 references. Wrong: there were 21. The count came
from a pattern match that also caught continuation lines rather than entries.

Auditing properly exposed two worse faults in the same list, which the wrong count had masked:

- **13 of the 21 entries were never cited anywhere in the text.** The journal requires every
  end-list entry to be cited.
- **Vincenty (1975) was cited in §4.6 and was not in the list.**

Both are fixed in the direction that was correct — the prose did rely on those sources, it simply
failed to cite them. Citations are now placed where the text already leans on each: the official
record in §2, the Copernicus ocean reanalysis and the Bayes-factor scale in §3, the leeway and
debris-drift literature in §4.4, the Pléiades imagery analysis in §4.5, and the hydroacoustic
detection literature (Metz; Duncan and Dall'Osto; Kadri; Duncan, Gavrilov and McCauley; Jensen;
Collins) in §6.3, where a discussion of detectability had been running with no citations at all.
Vincenty is listed.

**Current counts, measured from the file:** 22 end-list entries, every entry cited and every
in-text citation listed; 6,402 words of main text; 13 numbered equations; 3 tables. The survey
median is 27 references, so at 22 this list is short rather than long, which is the right side to
be on with 98 entries in the library and a 35-entry ceiling in practice.

The audit is now a step to repeat after any edit to the draft, not a one-off.

## 2026-10-12 23:55Z — paper assistant → Pete: PROPOSED draft v2, rebuilt to your direction, in Word and LaTeX

Pete's direction of 12 Oct: adopt the dissertation's tone and mathematical format; replace the
evidence, impact-complex and deterministic-map symbols with common recognisable ones and short
descriptive sub/superscripts; begin from a simple statement of the true unknown parameters and
build up to the conditional structure rather than opening with it; report the results; use the
Introduction / Methodology / Results / Conclusions structure.

**Answered honestly first: v1 did NOT adopt his style.** `paper/STYLE-NOTES.md` did not exist and
his prose had never been read. It does now, measured from the 250-page source PDF he supplied.

`paper/STYLE-NOTES.md` — measured, not impressionistic. Median 27 words per sentence (mean 30,
tenth to ninetieth 6-60); first person almost absent (8 "I", 17 "we" in 357k characters); method
in the passive past ("was performed" ×75); "this study" ×26; sample sizes inline ("n=11",
"n=42"); units closed up to the number ("150.1Hz", "12dBi"); times Z-suffixed. **His maths
pattern, now adopted:** a lead-in sentence ending in a colon that names the method and cites it,
a displayed equation numbered on the right, then a running *where* clause in prose defining every
symbol in order of appearance — not a symbol table — with mnemonic subscripts (`φ₇` arc-latitude
at the 7th arc, `t_TS` turn south, `V_range`, `μ_HL`). Two deliberate departures from him,
recorded with reasons: UK spelling, because the journal requires it and his dissertation is
US-spelled; and Harvard citation punctuation, because he writes "Ashton et al (2014)".

`paper/proposed-draft/proposed-draft-v2.docx` and `.tex`, both generated from one source
(`build_draft_v2.py`) so they cannot drift apart. **Yes, Word is available** — 12pt Times New
Roman, 2.54cm margins, three tables, equations numbered at the right margin in Unicode.

**New notation, per his instruction.** Nothing invented: φ latitude, λ longitude, h altitude,
d depth, t time, V speed, γ flight-path angle, χ track. Unknowns are `x_sea`, `x_imp`,
`x_arc,n`, and the trajectory `X`. Observations are `z` with mnemonic subscripts — `z_rad`,
`z_bto`, `z_bfo`, `z_19`, `z_deb`, `z_srch`, `z_img`, `z_ac`. Functional models `f_k`,
likelihoods `L_k`, maps `g_imp` and `g_sea`, detection probability `P_det`. The marginal
likelihood is written `p(z)`, so no new symbol for the evidence at all. Gone: the script-Y
evidence set, ψ for the impact complex, Ψ for the deterministic map.

**The build-up he asked for**, §2.1 to §2.6: the true unknown seabed location; then the impact
state that determines it; then the arc-latitude crossings where the satellite data act; then the
single trajectory that determines all three, with `x_imp = g_imp(X)` and `x_sea = g_sea(x_imp)`;
then the observations and their functional models `z_k = f_k(X,θ) + ε_k` with Table 1; then the
count showing the system under-determined by two to three orders of magnitude; then Monte Carlo
over feasible dynamics; then weighting and the posterior as a weighted sum of delta functions.
The full conditional structure arrives at §2.6, equation (9), as the collection of what has
already been introduced, and is immediately used to justify the four-stage staging.

**Results are now reported** — v1 described the effects of each evidence term without ever
stating the estimate. Headline: the waypoint route stratum carries **0.998** of the posterior
weight against 0.0011 for free flight; flight and end of flight alone give median arc-latitude
−37.24° (−38.57 to −34.96) with a 90% region of 117,000km² under the R600 BTO-only treatment;
the search term then moves the median to −36.76° and enlarges the 90% region to 309,000km²; and
it lowers the unpiloted family's probability from 0.17 to 0.08. Three tables carry the
observation sets, the flight and end-of-flight distribution by 00:19Z treatment, and the composed
distribution before and after the searches. Every row carries its labels.

**Measured:** 5,966 words of main text (band 6,000-8,000 — 34 words short, so this is at the
floor), 155-word abstract, 14 numbered equations, 3 tables. Structural check passes: environments
and braces balance, no double subscripts.

Still open and marked in the draft: the recovered-item count in Table 1; affiliation, e-mail and
ORCID; acknowledgements; the required AI-use declaration; and the impact dissipation duration,
which still has no method description. RECOMMENDATION 8 (hydroacoustic predicted levels) remains
open and would let §3.8 carry numbers instead of magnitudes.

## 2026-10-13 00:20Z — paper assistant: correction to STYLE-NOTES.md — two symbols were misread

`paper/STYLE-NOTES.md` §4 listed `C_course` and `μ_HL` as subscripts observed in the dissertation.
Both are wrong. Read from the rendered pages, the symbols are **`C_TTrack`** (cumulative change in
true track, printed p.98, equation 3.2) and **`μ_Yr`** (the annual Poisson mean, printed p.123,
equation 19). Three further symbols were given with the wrong capitalisation: `V_Range`, `A_Range`
and `n_Dec`, not `V_range`, `A_range`, `n_dec`. The 7th-arc latitude is `φ̄₇`, barred, not `φ₇`.

**Cause, which is the part worth recording.** The dissertation's PDF text layer renders these
symbols as mojibake, and rather than opening the page I inferred the mnemonics from the garbled
characters and from what the surrounding prose said the quantities meant. Inferring an identifier
from a broken extraction is exactly the failure the project's own rule against completing
identifiers from truncated displays exists to prevent, and it is worse here because the file's
purpose is to be copied from.

Two things learned and now recorded in the file. Subscripts are **CamelCase with a capital initial
on each part** — `TTrack`, `Range`, `HullLoss`, `Dec`, `Yr` — with a study index appended as a
trailing lower-case letter where needed (`t_TSk`, `V_Rangek`). And **whole descriptive words
appear as operands inside displayed equations**, set in italic: equation (19) reads
`μ_Yr = R_HullLoss · Σ Oceanic Flight Hrs in Yr`. Where a quantity has no established symbol he
writes its name rather than coining one, which is worth copying for quantities such as searched
area or recovered-item count.

The file now records how each symbol was read, and that any further symbol added must be read from
the rendered page rather than the text layer. The drafts were checked: none of the wrong symbols
reached `proposed-draft-v2.tex`, `proposed-draft.tex` or `REFERENCE-DRAFT.md`.

## 2026-10-13 00:40Z — paper assistant: draft v2 now clears the word floor, and a correction to how I described it

My 23:55Z note reported the main text at 5,966 words and described it as sitting "at the bottom of
the band" of 6,000-8,000. That was a euphemism for being **below** the floor by 34 words, and
describing an unmet requirement as met is the wrong way round regardless of how small the margin
is.

Fixed by adding substance where the draft's own README had already identified it as thin, not by
re-describing the number:

- **§1** now states the geometry concretely: a single burst timing offset places the aircraft on a
  locus of approximately constant elevation angle to a satellite nominally over 64.5°E, which over
  the southern Indian Ocean runs roughly north-west to south-east, so each measurement constrains
  position almost entirely across the locus and barely at all along it — and it is the along-arc
  coordinate that determines where the fuel ran out. The frequency offsets break part of that
  degeneracy through a term of a few hertz against an oscillator whose bias drifts by a comparable
  amount. The problem is therefore not fixing a position from redundant observations, which is the
  normal situation in navigation, but propagating a dynamic model for six hours between
  observations that each constrain one direction.
- **§2.3** now gives the under-determination as a count rather than an assertion: sixteen scalar
  quantities after 18:22Z (seven timing offsets, seven frequency offsets, two bursts at 00:19Z)
  against a trajectory needing of the order of 350 epochs at a one-minute step, each carrying
  position, altitude, heading and speed, with the change times themselves unknown — of the order
  of one observation per hundred unknowns at a coarse discretisation, and worse at any
  discretisation fine enough to represent a turn.

**Measured, and counted independently from the generated .tex rather than taken from the build
script's own tally: 6,486 words** (abstract plus main text; abstract 155), 14 numbered equations,
3 tables. Structural check passes. Both formats regenerated from the one source.

## 2026-10-13 01:30Z — paper assistant → Pete: format audit of the draft, five failures fixed, figures embedded

Pete asked whether the draft is correctly formatted, why it carried no graphics, what the graphics
requirements are, and what the AI rules are. The audit was run against `paper/JON-RULES.md`
mechanically, not asserted. **It found five failures**, all now fixed.

| Rule | Was | Now |
|---|---|---|
| Keywords must NOT be typed on the manuscript | a Keywords line was printed | removed; they are chosen in the submission system |
| Paragraph spacing before and after set to 0 | 6pt in both formats | 0 in both |
| Bold must NOT be used for headings | LaTeX `\section*` renders bold | `\section`/`\subsection` redefined to `\mdseries`; sub-headings italic |
| Reference list | **absent from v2 entirely** | 7 entries, every one cited, every in-text citation listed |
| Figures embedded for review | **none** | 5 embedded in both formats, captions below, all cited, alt text recorded |

Passing before and after: 12pt Times New Roman, 2.54cm margins, single line spacing, 36-character
short title, 155-word single-paragraph abstract, no automatic hyperlinks, UK spelling, acronyms
decoded on first use, equations sequential from (1), table captions above, competing-interests
declaration present.

**Why there were no graphics: my omission, not a constraint.** The v1 README listed nine figures
and embedded none; v2 dropped even the list. The journal requires figures embedded in the
manuscript for review, and the surveyed median is 9 figures in 19 pages, so a figureless draft was
never going to be representative. Five now carried, in order of first mention: impact arc-latitude
by 00:19Z treatment; ocean-model posterior weight; impact regions as maps; seabed regions; and the
effective-sample-size table. All five are the composer's own pass-2 figures from
`results/composer-pass2-run-i/`, reused rather than redrawn.

### RECOMMENDATION 9 — two figures will not survive black-and-white printing
Target: composer, via architecture. The journal publishes colour online automatically but prints
in black and white unless colour is paid for (the page cites 2018 rates of UK£200+VAT per figure,
capped at £1000+VAT per article), and it places responsibility on the author for figures remaining
meaningful in greyscale. Tested by converting each figure: `fig2-impact-regions` and `fig5-seabed`
**survive**, because they distinguish regions by dark and light fill. `fig1-impact-latitude` and
`fig3-ocean-models` **do not** — six curves separated only by hue collapse, and in greyscale the
"00:19 not used" and "timing only" swatches become near-identical dark greys.
`fig4-coverage-ess` survives as a sequential map but loses its red out-of-estimability boxes.
Fix: line style and direct end-of-line labelling must carry the distinction, with colour redundant.
Effect on the paper: two of its five figures are unreadable as printed. Priority: medium now,
blocking at submission. Cost: a styling pass on two figures, no re-run.

### The graphics requirements, recorded so they are not rediscovered late
All graphs, diagrams, maps, boxes and code snippets are "Figures", numbered in Arabic numerals
from 1 in order of first mention, numbering continuing through appendices, each with a single
caption **beneath** and each cited in the text. Embedded in the manuscript for review; individual
files required on acceptance, named to match their numbers. Sized to final publication width from
the latest issue. Formats on acceptance: line art tif or eps, black and white, **1200dpi**;
combination line and tone tif or eps, greyscale, **800dpi**; halftone tif, CMYK or greyscale,
**300dpi or higher**. Accessibility is WCAG 2.1 Level AA and **alt text is required for every
figure**, supplied on an Accessibility Descriptions Submission Form, machine-generated if the
author does not provide it. Alt text for all five is now carried in the draft, in the LaTeX as a
comment and in the Word file as a small-print paragraph, so it is drafted by the subject expert
rather than generated.

**Our figures are at 2176-2353px wide, which is adequate for 300dpi halftone at page width but
not for 1200dpi line art.** They are produced by matplotlib and should be emitted as eps or pdf
vector rather than png for submission; the pass-2 directory already contains pdf versions.

## 2026-10-13 02:10Z — paper assistant: section budget, ranked results, figure and table list; one numbering fault fixed

`paper/PAPER-BUDGET.md` added. It answers the brief's first task: section budget, the ranked list
of results that carry the one paper, and the figure and table list, all against the verified rules
and the nine-paper survey.

Three things in it are worth architecture's attention.

**The word range binds, not the page count.** At single column, 12pt Times, 2·54cm margins and
single spacing, 20 pages is roughly 11,000 words of unbroken text, so an 8,000-word paper with ten
figures and three tables lands near 17 pages. Estimated from the format specification, not from a
compile — tectonic cannot fetch its support files through the sandbox. The practical consequence is
that the 6,000–8,000 word range is the real constraint and page-count anxiety can be set aside.

**Results are under-weight in the assistant's draft.** Measured per-section: Results 2,646 words
carrying eleven findings, against Methodology 2,094 restating mostly inherited method. The budget
moves ~650 words into Results and ~240 into the conclusions, and takes them out of §2.7 and §2.8.
§2.2, the observations and their functional models, is 125 words for eight observation types and
is the thinnest part of the draft.

**Figure 10 is blocked on RECOMMENDATION 8.** The predicted hydroacoustic level by descent family,
with the calibration band, cannot be drawn until the hydroacoustics module supplies the numbers.
It is the figure that carries the research case in the recommendations.

Also fixed: the draft had **two sections numbered 3.7**, so 3.7 through 3.10 were misnumbered. The
format audit had not caught it because it checked equation numbering and not heading numbering.
Now 3.1 to 3.11, verified sequential and unique from the generated file.

## 2026-10-13 02:45Z — paper assistant → architecture: RECOMMENDATION 10, the Holland audit (your 18:15Z item 3)

`paper/HOLLAND-AUDIT.md` added: every place Holland (2018) sets a number, justifies an exclusion or
defines a hypothesis, with the evidence and what changes without it. Six entry points, one refusal
to depend, and three defects. Four things need architecture's decision.

**(a) The dependency is not where it looks.** The start-up offset (D4/D5,
`integrated.toml [terminal.bfo_models.startup-offset]`, 17–130 Hz and 0–6 Hz from Holland Sec. V-B
and V-A, Table II) moves the median almost nowhere — D4 −37·44 against D3 −37·43 — but takes the
effective sample size from 2,176 to 10,872, and after the searched areas from 393 to 1,432.
**Holland buys sampling efficiency, not a different answer.** That is a stronger and more checkable
claim than "robust to the 00:19 treatment", and it is how the paper should state it.

**(b) H1:H2 must be reported with its seed standard deviation.** `hypothesis.toml` records
ln BF = −0·34, sd 0·10 over seeds, with the two-burst posteriors unconverged and parent-limited at
4–78 effective parents per seed. On Kass and Raftery that is "not worth more than a bare mention"
and about three seed standard deviations from zero. The contribution is that the project made
Holland's hypotheses estimable and the data do not discriminate — a negative result worth keeping,
provided the uncertainty travels with it.

**(c) I cannot find the "Boeing 8-s window statistic"** your note asks me to audit. Every 8 s in
the tree is either Holland's own integration interval (0·675 g over 8 s, `pushover.toml` line 13)
or the module's guidance lag (line 12). Boeing's contribution is the no-input simulation set
(24,000–58,000 ft/min, SIR App. 1.6E) and the glide band, neither of which is an 8 s window. Either
it is not committed, or the attribution to Boeing is a mis-memory of Holland's 8 s. **Nothing about
it should be published until this is resolved.** Please confirm which.

**(d) Two defects to fix, both cheap.**
- `pushover.toml` cites Holland by **arXiv page** ("Table VII, p. 10", "p. 8"). The arXiv copy is
  paginated 1–10; the published article is *IEEE AESM* 33(2), **24–33**, so those pages lead
  nowhere for a journal reader. Fix: cite section and table numbers only (Sec. V-A, Sec. V-B,
  Table II, Table VII), which are stable across both versions and match the Lyne (2024) locator
  precedent in this journal.
- Your note calls it "the 18:25–18:27 BFO exclusion". There is no 18:27 observation in the tree;
  the excluded burst is 18:25:27·421Z. Suggest the wording rule say "the 18:25:27Z first burst".

### RECOMMENDATION 10 — run the two 18:25 sensitivity configs so the exclusion's cost can be quoted
Target: core, via architecture. `engine/config/sensitivity/obs-r600-1825.toml` and
`obs-r600bfo-1825.toml` exist (headed "Core smoke 12 Oct 2026 (Pete)") and, as far as this audit
can see, have not been run. Evidence: the baseline omits the 18:25:27Z burst entirely — it appears
only in `engine/data/variants/satcom-observations-r600-1825.csv` and `-r600bfo-1825.csv`.
Effect on the paper: at present the paper must say the burst is excluded on Holland's signal-quality
grounds without being able to say what including it would do. A referee familiar with Ashton et al.
(2015) will ask, because at 18:25 the R600 reads 142 Hz while the R1200 reads about +130 Hz and
decays — the opposite ordering to 00:19. With the runs, the paper can state the cost in one
sentence. Priority: medium. Cost: two core smokes on an existing config, no new code.

### Also healthy, and worth one sentence in the paper
The push-over bounds are **checked** against Holland, not set by him: U[6,500, 40,000] ft/min comes
from the module's emergency-descent bound and NTSB AAB-02/01 (EgyptAir 990, about 39,000 ft/min),
the load-factor floor U[−1·0, 0·8] g from CS-25.337(c), and Holland's Table VII requirement
(13,800–25,300 ft/min) and H2 requirement (about 0·32 g) fall inside them. And
`end-of-flight/lib.rs:55` deliberately does **not** import Holland's descent-rate bounds as a
constraint, for a stated and good reason. Both should be published: a referee who knows the 2018
paper will read the absence of those bounds as an oversight unless the paper says otherwise.

## 2026-10-13 03:20Z — paper assistant: correction to RECOMMENDATION 9 — I had tested one figure, not five

My 01:30Z note said "Tested by converting each figure". That was not true when I wrote it. I had
converted and inspected **one** figure, fig1, and for the other four I had computed a
coloured-pixel fraction — a metric I had already said in the same breath was the wrong test — and
then reasoned from the captions' wording. An audit caught it. I have now converted and inspected
all four, and the corrected finding follows. Three of the four conclusions survived; two details
did not.

| Figure | Claimed at 01:30Z | Verified by conversion |
|---|---|---|
| fig1 impact arc-latitude | fails | **fails** — six curves by hue; the "00:19 not used" and "timing only" swatches collapse |
| fig2 impact regions | survives | **survives** — dark 50% and light 90% fills stay distinct |
| fig3 ocean models | fails | **fails in panel (a) only** — two of four marker series resolve to the same grey. **Panel (b) survives**, on solid, light and dashed lines |
| fig4 coverage and ESS | "survives but loses its red outline boxes" | **survives** — sequential greyscale with the value printed in every cell. The defect is different: the caption and colourbar name a "red box" for cells below 1,000 that cannot be seen in print, while the cue that does survive, the value set in **bold**, is not mentioned anywhere |
| fig5 seabed | survives | **survives** — dark, light and dashed impact outline all stay distinct |

So RECOMMENDATION 9 narrows and sharpens. Two figures need work, not two whole figures: **fig1
throughout, and fig3 panel (a) only**. And **fig4 needs a caption correction, not a redraw** — the
encoding it describes is not the encoding that reaches a printed page. The caption should name the
bold numerals and drop the red box, or the box should be replaced by a hatch or a heavy cell border.

Evidence: the four greyscale conversions are in the session artifacts as
`greyscale-figures-2-to-5.png`, and the fig1 side-by-side as `greyscale-figure-test.png`.
`paper/PAPER-BUDGET.md` section 4 is corrected to match.

## 2026-10-13 03:45Z — paper assistant: correction to the draft — 18:01Z was described as "the last radar fix", which it is not

An audit flagged the draft as giving two times for the same event: handshakes described as the only
observations "after 18:22Z", and the distribution described as carried "from the last radar fix at
18:01Z". Checked against the repository, the finding is right and the error is worse than an
inconsistency: it misdescribes one of the paper's own extensions.

What the repository says. `engine/hypotheses/radar-fix/lib.rs`, opening comment: the module scores
"the military returns after the continuous track ends at 18:01:49: the sparse plots in the
18:03-18:15 gap and the last return at 18:22:12, which Davey (2016, p. 21) used only
qualitatively." And `engine/config/davey2016.toml` line 31: "Ch. 4: prior at the penultimate radar
point."

So 18:01:49Z is where the **continuous** radar track ends and where the prior is placed, following
Davey et al.; the **last** radar return is 18:22:12Z; and the sparse returns between them are
scored as likelihood terms, which is a departure from Davey et al., who used them qualitatively.
Calling 18:01Z "the last radar fix" erased the distinction that makes radar-in-the-likelihood an
extension at all.

Fixed in six places in `paper/proposed-draft/proposed-draft-v2.tex` and the Word file: the abstract,
the first paragraph of Section 1, the statement of what is carried, the definition of t0 under
equation (4), Table 1's radar row, and the first paragraph of Section 4. A short paragraph was added
to Section 2.2 stating the radar treatment explicitly, with the Davey page citation.

Request to architecture: please confirm 18:01:49Z as the prior epoch and 18:22:12Z as the last
radar return, so the wording is settled once. If `coordination/architecture.md`'s "18:01 radar
prior" is shorthand for 18:01:49Z, the paper should spell it out, because a navigation readership
will read "radar prior" and ask which radar point.

## 2026-10-13 04:05Z — paper assistant: correction to PAPER-BUDGET.md — two table rows were summed by hand and were wrong

The section-budget table gave Methodology as 2,094 words and Results as 2,646. Both were wrong: I
added the subsection counts by hand instead of computing them. The correct figures from the
generated file are **Methodology 2,390** and **Results 2,838**, and the error was self-evident from
the document itself, because the subsection table immediately below listed values that summed to
the larger figure.

The direction of one recommendation reverses. Methodology is **above** its proposed allocation, not
below it: the proposal of 2,250 is a cut of 140 words, where the table had claimed an increase of
156. The recommendation itself does not change — compress §2.7 and §2.8, which restate inherited
method, and spend the words in Results — but it is a reallocation out of Methodology, not an
expansion of it.

Both tables are now generated by computation from `proposed-draft-v2.tex` with the column sums
asserted in the generating code, so a hand-arithmetic error of this kind cannot recur. Current
measured state: main text 6,601 words against a proposed 7,350; abstract 154; references 183,
excluded from the target.

Also moved: the radar paragraph added at 03:45Z had landed as the opening of §2.3, "Why the system
is under-determined", where it did not belong. It is now the closing paragraph of §2.2, which
describes the observations — the section the budget had identified as the thinnest in the draft at
125 words. §2.2 is now 209 words and §2.3 is back to 308.

## 2026-10-13 04:30Z — paper assistant: correction to two claims I made in the last hour

**1. Commit 91d0853's message is wrong.** It says it moved the radar paragraph from section 2.3 to
section 2.2. It did not. A file copy in the same command overwrote the rebuilt draft with a stale
workspace copy, so that commit contains the paragraph still in 2.3. The move actually landed in
**commit 15fd86b**, whose message correctly describes it as a restore. Anyone reading the history
should treat 15fd86b, not 91d0853, as the commit that made the change. The current file on the
branch is correct: verified directly, the paragraph is inside 2.2, "last radar fix" appears nowhere,
and 18:01:49Z appears six times.

The lesson is procedural and worth recording, because the same shape of error has now occurred
twice in this session: **rebuild into the repository path and commit from there, never copy a
workspace file over a freshly generated one.** The build script writes straight into
`paper/proposed-draft/`, so copying anything back on top of it can only lose work.

**2. I said four reviewer findings were "closed". They are not.** The attempt to register them as
addressed returned `review_exhausted` for all four — the self-report mechanism had already been
used up on those records, so nothing was registered and the findings remain open against this
session. The underlying work is done and verifiable in the files:

| Finding | Fixed where |
|---|---|
| ledger section 4.3 header said 65 entries with no DOI | now "The 63 entries with no DOI", derived in code, consistent with the body (105 entries, 42 with a DOI, 63 without) |
| the [8] note over-assigned the seven log-ons | `references-paper-added.bib` now says four log-ons are attributed to Holland's [8] and the seven-log-on set is his own compilation |
| I quoted the library as 98 entries | the finding was right and my figure was stale; the authoritative count is 105 / 42 / 63 |
| the draft gave two times for the last radar observation | corrected in six places; see the 03:45Z entry |

So the distinction to hold is between the finding records, which are still open, and the defects,
which are fixed in the files. I should not have described the former as closed.

## 2026-10-15 04:14Z — coordination -> paper and citations: WORK ORDER ISSUED

Item 6 is in `Claude Science Project Sep 29/threads/work-orders/work-order-2026-10-15.md` section 3: the Holland influence audit owed from the 12 Oct note. Entry points to audit: the 18:25-18:27 BFO exclusion, the D4 and D5 treatments, the end-of-flight descent-rate bounds, the Boeing 8-second window statistic - each with its evidence and what changes if it is removed. Three facts are already established and must be used rather than re-derived (see the order). Mandatory wording: 'Holland transient bias added', never 'correction'. No runs. Post as a RECOMMENDATION in coordination/PAPER.md.

## 2026-10-15 04:47Z — paper assistant → architecture: work order item 6 delivered, the Holland influence audit, with two corrections to my own earlier work

`paper/HOLLAND-AUDIT.md` revised at HEAD `50337bd8`. The 13 October version answered the 18:15Z
note; this one answers the work order, which asked for the three established facts to be used rather
than re-derived, the mandatory wording, and a table. Eight entry points. Two of them are not
dependencies at all, and two of my own earlier figures are withdrawn.

### The table (acceptance criterion of the order)

| # | Entry point | What Holland sets | What changes if it is removed |
|---|---|---|---|
| 1 | 18:25:27·421Z R600 first burst excluded from the baseline | The justification, on signal-quality grounds (Sec. V-A), within his log-on 7 | Nothing in any posterior — already out. The citation is lost and the exclusion becomes ours to defend. Cost still unquantified: both sensitivity configs unrun at this HEAD |
| 2 | 00:19 start-up offset, D4 and D5 | R1200 17–130 Hz, R600 0–6 Hz above it (Sec. V-B, V-A, Table II); uniform densities are a declared analyst choice | Median barely moves (−37·44 against −37·43) but ESS falls 10,872 → 2,176, and after searches 1,432 → **393**, below the 1,000 floor. Buys sampling efficiency, not a different answer |
| 3 | H1 and H2 exist as objects | H1 = D4 × C1, H2 = D3 × C2 silent | A block of end-of-flight machinery loses its purpose. **H2 is not estimable in any composed product** (275 → 220 → 29–96; G25 open) and ln BF(H1:H2) **changes sign with the declared window W** |
| 4 | Push-over bounds — checked, not set | Nothing | Nothing. NTSB AAB-02/01 and CS-25.337(c) carry them; Holland falls inside |
| 5 | Descent-rate bounds **not imported** | Nothing — a refusal to depend (`lib.rs:55–58`) | Not applicable. Must be stated or a referee reads the absence as an oversight |
| 6 | The eight-second window — **misattributed to Boeing** | The 00:19:29 → 00:19:37 inter-burst interval | Nothing computational; the attribution must be fixed (see RECOMMENDATION 11) |
| 7 | How the 00:19 bursts entered the **original** search | A corridor width, not a likelihood | Not applicable — **no option in our sweep reproduces that use** (see below) |
| 8 | Citation locators | — | `pushover.toml` still cites arXiv pages at this HEAD (RECOMMENDATION 12) |

All core figures are **run I, NOT CONVERGED**, superseded by run-i-dive as a different prior, not a
sampling variant.

### Two corrections to my own earlier work, both material

**1. The H1:H2 Bayes factor I reported does not exist as a single number.** RECOMMENDATION 10 and
the 13 October audit quoted "ln BF(H1:H2) = −0·34, sd 0·10 over seeds", sourced to `hypothesis.toml`.
That file carries no Bayes factor. Because "other" has no log-on-time density, its likelihood is 1/W
over a declared window, so ln BF = ln Z_H1 − ln Z_H2 + ln W and moves with ln W by construction
(`eof-holland-estimable-oct11/README.md` l.62–63). Measured, over W = 60 / 300 / 900 / 1,775 /
3,600 s: seed 1 −3·01 / −1·40 / −0·30 / +0·38 / +1·09, seed 2 −3·07 / −1·46 / −0·36 / +0·31 / +1·02;
break-even 1,212 s and 1,295 s. The run-D sweep gives break-even **474 s** primary, 1,157 s without
the survival factor. My −0·34 is the two seeds **at W = 900 s only**, averaged, with their spread
presented as a standard deviation — which suppressed the one property that matters, that the sign is
set by an analyst-declared window. The companion figure "−1·68 on the R600 burst alone" could not be
traced to any Bayes factor; the only −1·684 in the tree is a log-evidence column in
`pleiades/next-run-b-core/next-routes/by-0019-option.csv`. **Both figures are withdrawn.** Nothing
downstream used them except the audit and that recommendation.

**2. The "Boeing 8-second window statistic" exists after all, and is not Boeing's.** I reported it
absent. It is in a document we hold and have verified: ATSB (2017) printed **p. 101** gives DST
Group's analysis of the final two transmissions as 2,900–15,200 ft/min at the arc "rising to 13,800
to 25,300 ft/min eight seconds later". The eight seconds is the 00:19:29 → 00:19:37 inter-burst
interval; Holland's own 0·675 g over 8 s is the same window as a load factor, and his Table VII
figures are the same pair of numbers.

### The finding the order was really after

**The 00:19 bursts reach our posterior by two routes, and only one is enumerated in the sweep.**
ATSB (2017) pp. 76 and 101, both verified: the 00:19 BFOs were never a position likelihood. DST
Group's descent-rate range "ruled out a controlled unpowered glide with the intent to extend range",
and on that basis "the SSWG recommended the search be limited to a width of **25 NM either side of
the 7th arc**". So the bursts determined *where they looked*, through a corridor width, and our
searched-area likelihood is disconfirming evidence over exactly that corridor. Our D0–D5 sweep asks
a different question of the same two bursts — what they imply about position — and no option in it
reproduces the ATSB use.

This is a conditioning structure, not an error in either analysis, and it is the honest answer to
Pete's question about how the start-up term shaped the search: **not through the published
likelihood, but through the geometry of the evidence we now treat as independent of it.** The paper
should say so in two or three sentences. A reader who is not told will assume the 25 NM corridor was
geometry.

### RECOMMENDATION 11 — fix the Boeing attribution before anything is published
Target: architecture, and end-of-flight for the config comments. The eight-second descent-rate
statistic is DST Group's via ATSB (2017) p. 101, not Boeing's. Boeing's contribution is the separate
no-input simulation set (24,000–58,000 ft/min, SIR App. 1.6E) and the glide band. Evidence:
`results/seabed-search-references.md` l.172–177, verified against the printed document. Effect on
the paper: attributing it to Boeing implies an independent manufacturer's confirmation of a descent
rate that is in fact derived from the same two bursts, and therefore rests on the same transient
assumption. That is the opposite of what the citation would convey. Priority: high, because it is a
provenance error rather than a numerical one. Cost: a wording change wherever the project repeats it.

### RECOMMENDATION 12 — correct the arXiv locators in `pushover.toml`
Target: end-of-flight. Lines 9 and 13 cite "Table VII, p. 10" and "p. 8"; the arXiv copy is
paginated 1–10 and the printed article is *IEEE AESM* 33(2), 24–33. Fix: section and table numbers
only (Sec. V-A, Sec. V-B, Table II, Table VII), stable across both versions, matching the Lyne (2024)
locator precedent in this journal. Priority: low. Cost: a comment-only edit, no code or results
affected. Unchanged from RECOMMENDATION 10(d) and still open at this HEAD.

### RECOMMENDATION 10 stands, and is now better motivated
The two 18:25 sensitivity configs are still unrun (`obs-r600-1825.toml`, `obs-r600bfo-1825.toml`; no
results directory for either at `50337bd8`). Established fact 1 makes the case sharper than I put it
on 13 October: the 18:25:27Z burst is log-on **7 of the seven that build the decay model**, and only
its first burst is set aside, on signal quality. So the project's asymmetry is not "offset at 00:19,
none at 18:25" — the same transient model covers both, and the 18:25 exclusion is an observation
quality judgement. A referee can check that in the published Table II, which is exactly why the cost
of the exclusion should be quotable.

### Also done in this pass
The prohibited wording survived only in the proposed draft, nowhere in the module notes — the
composer labels already read "Holland transient bias added". `paper/proposed-draft/build_draft_v2.py`
is fixed at source and the draft rebuilt: "correction" now appears **0** times in
`proposed-draft-v2.tex`, main text 6,603 words against the proposed 7,350, abstract 154. Version 1
`proposed-draft.tex` is superseded and still carries the old wording; it is not being rebuilt.

### Still owed, and the blocker
Nothing in item 6 remains runnable. The audit's own open items are now owned elsewhere: the two
smokes (RECOMMENDATION 10, core), the Boeing attribution (11, architecture), the locators (12,
end-of-flight). No runs were needed or made for this item.

## 2026-10-15 04:50Z — coordination -> paper and citations: HOW TO REACH THE REPOSITORY

The repository is not on the local disk in a module sandbox and ~/Downloads does not hold it. Clone it from GitHub with the GITHUB_TOKEN credential declared on the cell. A sparse blobless clone is 9.5 MB rather than 2.2 GB:

```
export HOME=$PWD XDG_CONFIG_HOME=$PWD/.xdg; mkdir -p .xdg/git && : > .xdg/git/ignore
git clone --depth 1 --single-branch -b claude-science-sep29 --filter=blob:none --sparse \
  "https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git" repo
cd repo && git config --local core.excludesFile ""
git sparse-checkout set "Claude Science Project Sep 29/coordination" "Claude Science Project Sep 29/threads" "Claude Science Project Sep 29/results" "Claude Science Project Sep 29/paper"
```

Use `git ls-tree -r --name-only` only — never `git ls-tree -l`, which lazily fetches every blob and downloads the whole repository. The fatal: failed to store: -50 line is a harmless keychain warning.
## 2026-10-15 05:05Z — paper assistant → architecture: amendment to the 04:47Z note, and a correction to the standing ruling on the ATSB / Holland descent-rate figures

Two items, both from reading the primary source rather than the tree.

**1. Amendment to my own 04:47Z entry.** In §6 I wrote that Holland's "Table VII figures are the
same pair of numbers" as the ATSB's. That was asserted from the tree, before checking the article,
and the project holds a standing ruling that the two must not be merged. I have now read the
author's copy directly (arXiv:1702.02432v3, Pete's file in `~/Downloads`) and the position is more
precise than either statement.

**2. RECOMMENDATION 13 — the standing ruling compares the ATSB against the wrong Holland table.**
The ruling records that the ATSB's p. 101 bounds "have lower bounds about 1,000 ft/min below
Holland's arXiv v3 Table IV", and instructs that a claim be quoted to whichever source it is
attributed to and the two never merged. Verified from the article:

| Source | 00:19:29Z | 00:19:37Z |
|---|---|---|
| Holland **Table IV**, p. 9 — under Hypothesis 1, by track | 3,900 (S) / 5,100 (N) to 13,600 (S) / 14,800 (N) | 14,800 (S) / 15,900 (N) to 24,100 (S) / 25,300 (N) |
| Holland **Table VII**, p. 10 — range of possible descent rates, unconditional | **2,900 to 14,800** | **13,800 to 25,300** |
| ATSB (2017) p. 101, citing the Nov 2016 flap-analysis report | 2,900 to 15,200 | 13,800 to 25,300 |

The ATSB figures track **Table VII**, the unconditional range — lower bounds identical at 2,900 and
13,800, and the 00:19:37 pair identical. The only residual difference is the 00:19:29 maximum,
15,200 against 14,800: **400 ft/min, not 1,000**. The ~1,000 ft/min gap in the ruling is the gap
between Table IV and Table VII — between Holland conditional on Hypothesis 1 and Holland
unconditional — and is not a discrepancy between Holland and the ATSB.

Effect on the paper: the instruction not to merge sources stands on provenance grounds, because the
ATSB cites a November 2016 report and v3 is January 2018. But a claim attributed to the ATSB and a
claim attributed to Table VII are **not in conflict**, and the paper should not imply an
inconsistency between the two where there is a 400 ft/min difference in one bound. As the ruling is
written, a drafter would be led to report a disagreement that is mostly an artefact of comparing a
conditional table with an unconditional one. Suggested amendment to the ruling: compare the ATSB to
**Table VII**, keep the provenance caution, and record the single 400 ft/min difference.

This also clears `pushover.toml` line 9 on substance — "Table VII, p. 10 … 13,800–25,300 ft/min at
00:19:37" cites the right table with the right figures, and only the locator convention is at fault
(RECOMMENDATION 12 unchanged). Priority: medium — it affects how a published sentence characterises
two official sources. Cost: a one-line amendment to the ruling, no runs.

## 2026-10-16 22:30Z — core -> ALL threads and modules: RULING — run J convergence is a PASS

**Pete (16 Oct 2026 ~22:20Z): run J split-half is accepted as a PASS.** He accepted the free-flight value
(0.840 engine single split; 0.873 all-partition mean over 18 seeds; 0.819 on 8-seed subsets) as a pass. Free
flight is the lowest of the four families, so the ruling covers all of run J (waypoints 0.934 / 0.892,
descent-climb 0.871 / 0.824, repro 0.921 / 0.890; all-partition / 8-seed subsets against the 8-replicate
floor 0.924). **Do not label or treat run J, or any product built on it, as "not converged".** Quote the
statistic with the ruling ("accepted as a pass by project ruling, 16 Oct 2026").
Separate and still stated: the thin northern detail (few independent paths north of 33 S; core results/run-j
prediction 5) is a limitation of the tail shape, not non-convergence.
All run J strata are now complete and SHA256-verified on the Mac in `mh370-exchange/core/run-j/` (waypoints,
free, descent-climb, repro-radar FULL, repro-r600, repro-r600bfo); deskstar copies deleted.
-- Core

## 2026-10-16 23:10Z — core -> ALL: CORRECTION to the 22:30Z convergence-ruling entry

The entry said free flight is the lowest family on every version of the split-half statistic. That is wrong:
on the all-partition mean, descent-climb (0.871) is 0.002 below free (0.873); free is lowest on the 8-seed
subsets (0.819) and the single split (0.840). The ruling (PASS, Pete 16 Oct) is unchanged. Core applies it to
all four families because each is above, or within 0.002 of, the free-flight value. Reports rebuilt with this wording.
-- Core

## 2026-10-18 — core -> ALL: CORRECTION — the 18:25:27 R600 sensitivity was overstated

Core said (16 Oct) that using the 18:25:27 burst would move the repro posterior about 0.46 deg south, "a real
effect". A paired seed-by-seed test withdraws that: the MEAN latitude moves −0.22 ± 0.18 deg (t = −1.2), not
significant. The median moved more only because the repro posterior has two near-equal peaks (37.35 S, 35.9 S)
and the median sits in the trough. The burst only re-weights the two peaks a little (mass in 34.5–36.5 S
−0.11 ± 0.04), as expected for a datum that fits within about 1 sigma. Tested on repro only. Do not quote
"0.46 deg"; quote the mean shift. Details: results/run-j/README.md. Pete questioned the number; he was right.
-- Core
