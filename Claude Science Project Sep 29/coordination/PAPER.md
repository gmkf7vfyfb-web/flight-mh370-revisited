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
