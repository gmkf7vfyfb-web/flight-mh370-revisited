# HOLLAND-AUDIT.md — every place Holland (2018) enters the method or the calibration

Owed to architecture's 18:15Z note of 12 Oct 2026, item 3. First written by the paper and citations
assistant on 13 Oct 2026; **revised 15 Oct 2026 at HEAD `50337bd8`** under work order item 6
(`threads/work-orders/work-order-2026-10-15.md` §3), which adds the three established facts, the
mandatory wording rule, and the summary table below.

Source graded **peer-reviewed**: Holland, I. D. (2018). MH370 Burst Frequency Offset Analysis and
Implications on Descent Rate at End-of-Flight. *IEEE Aerospace and Electronic Systems Magazine*,
33(2), 24–33, DOI 10.1109/MAES.2018.170048 (`holland2018`). The copy the project reads is the
author's green open-access copy, arXiv:1702.02432v3 (`holland2018oacopy`).

**Wording rule, mandatory and applied throughout this file.** The 00:19 term is written
"Holland transient bias added", never "correction"; and "R1200 BTO, empirical offset applied",
never "corrected". The composer notes already use the first phrase as the treatment label, so the
paper is the only place where the prohibited wording survived; see the open items.

Holland is named 149 times in `coordination/architecture.md` and 60 times in
`results/composer-pass2-run-i.md`. What follows is only the places where his work **does
something** — where it sets a number, justifies an exclusion, or defines a hypothesis.

## Summary table — entry points, evidence, and what changes if removed

Eight entries, of which only **1, 2 and 3 are live dependencies** — the exclusion's justification,
the start-up offset ranges, and the two hypotheses as defined objects. The rest are not: entry 4 is
a check that Holland passes against bounds set from other sources; entry 5 is a deliberate refusal
to depend; entry 7 is a use of the 00:19 bursts that this project does not reproduce at all; and
entries 6 and 8 are provenance and locator defects rather than methodological dependencies. Every
figure in the
"consequence" column is carried with its labels from the note it comes from; all core numbers are
**run I, NOT CONVERGED**, and run I is superseded by run-i-dive as a different prior over the
end-of-flight trajectory, not a sampling variant.

| # | Entry point | What Holland sets | Evidence | What changes if it is removed |
|---|---|---|---|---|
| 1 | 18:25:27·421Z R600 first burst excluded from the baseline observation set | The exclusion's justification, on signal-quality grounds | Holland Sec. V-A: non-zero bit error rate, low signal level, low C/N0, within his log-on 7 | Nothing in any posterior — the burst is already out. The *citation* is lost and the exclusion becomes the project's own judgement to defend. Cost still unquantified: `obs-r600-1825.toml` and `obs-r600bfo-1825.toml` remain unrun at this HEAD |
| 2 | 00:19 start-up offset ranges, treatments D4 and D5 | R1200 acknowledge 17–130 Hz above a steady oscillator; R600 log-on request 0–6 Hz above that | Holland Sec. V-B, Sec. V-A, Table II (seven log-ons after long outages); the **uniform densities over those ranges are an analyst choice**, declared as such in the config | D4 and D5 cease to exist. The median barely moves (arc latitude −37·44 with the bias added against −37·43 as recorded) but effective sample size falls from **10,872 to 2,176**, and after the searched areas from **1,432 to 393**, below the project's 1,000 floor. Holland buys sampling efficiency, not a different answer |
| 3 | Hypotheses H1 and H2 exist as defined objects | H1 = D4 × C1 (both BFOs, bias added, fuel exhaustion); H2 = D3 × C2 (both BFOs as recorded, some other cause) | Holland's own framing; implemented in `holland-estimable.toml` with a targeted proposal, an aimed pitch-down arm and a raised child count | A block of end-of-flight machinery loses its reason to exist. The measured outcome is a negative result: **H2 is not estimable in any composed product** (ESS 275 flight + end of flight, 220 with drift, 29–96 beyond, G25 OPEN), and ln BF(H1:H2) **changes sign with the declared log-on window W** — break-even between 474 s and about 1,300 s depending on version and seed |
| 4 | Push-over bounds — **checked against, not set by** | Nothing | Band U[6,500, 40,000] ft/min from the module's emergency-descent bound and NTSB AAB-02/01 (EgyptAir 990, about 39,000 ft/min); load factor U[−1·0, 0·8] g from CS-25.337(c). Holland's Table VII (13,800–25,300 ft/min) and H2 (about 0·32 g) fall inside bands set elsewhere | Nothing. The bounds stand on their own citations. Worth one sentence in the paper precisely because it shows they were not reverse-engineered to admit Holland's hypotheses |
| 5 | Descent-rate bounds **deliberately not imported** | Nothing — this is a refusal to depend | `engine/hypotheses/end-of-flight/lib.rs:55–58`: they are "conditional on a transient assumption this project declines to treat as established", and importing them "would kill the deliberate-descent branch by assumption rather than by evidence" | Not applicable. The risk is the opposite one: a referee who knows the 2018 paper will read their absence as an oversight unless the paper states the decision and the reason |
| 6 | The eight-second window — **misattributed to Boeing** | The interval between the two 00:19 bursts, not a Boeing statistic | ATSB (2017), printed p. 101: DST Group's analysis gives 2,900–15,200 ft/min at the 7th arc "rising to 13,800 to 25,300 ft/min eight seconds later" (00:19:29 → 00:19:37). Holland's own 0·675 g over 8 s is the same window | Nothing computational. The attribution must be fixed before publication: the 8 s is the inter-burst interval from DST Group via ATSB, while Boeing's contribution is the separate no-input simulation set (24,000–58,000 ft/min, SIR App. 1.6E) |
| 7 | How the 00:19 BFOs entered the **original** search design | Not a position likelihood at all | ATSB (2017), printed pp. 76 and 101 (`atsb2017operational`, both **verified**): the SSWG recommended the search "be limited to a width of 25 NM either side of the 7th arc" | Not applicable — **no option in this project's sweep reproduces this use**. This is the channel through which 00:19 analysis of Holland's kind shaped where the search actually went, and the project's nearest analogue is the held-out position likelihood combined with the module's own dynamic reach constraint |
| 8 | Citation locators | — | `pushover.toml` lines 9 and 13 cite "Table VII, p. 10" and "p. 8" — arXiv pagination 1–10, not the printed 24–33 | Nothing computational; a journal reader cannot follow the locators. Still present at this HEAD |

## 1. The 18:25:27Z R600 first burst is excluded from the baseline

**Where.** The baseline observation set omits it. It exists only as variants:
`engine/data/variants/satcom-observations-r600-1825.csv` (BTO and BFO) and
`satcom-observations-r600bfo-1825.csv` (BFO only), driven by
`engine/config/sensitivity/obs-r600-1825.toml` and `obs-r600bfo-1825.toml`, both headed "Core smoke
12 Oct 2026 (Pete)".

**The evidence.** Holland sets aside the first burst of his log-on 7 — the 18:25:27Z R600 log-on
request — on **signal-quality** grounds: a non-zero bit error rate, an unusually low signal level
and an unusually low C/N0. He does **not** set it aside as a warm-up transient; log-on 7 is one of
the seven log-ons that *build* his oscillator decay model, and only that one burst within it is
excluded. A footnote offers unknown aircraft conditions between 17:22Z and 18:25Z, for instance an
SDU temperature far below ambient, as a possible explanation.

**What changes without it.** Nothing in the posterior — the burst is already out. What is lost is
the *justification*. Without Holland the exclusion rests on the project's own judgement of the
signal quality, which is defensible but is then the project's claim to defend, not a citation. The
two sensitivity configs exist precisely so the cost of the exclusion can be quoted rather than
assumed; **as far as this audit can see they have not yet been run**, so the paper currently cannot
say what including that burst would do. That is a gap worth closing: it is cheap, and a referee who
knows Ashton et al. will ask.

**Note on architecture's wording.** The 18:15Z note calls this "the 18:25–18:27 BFO exclusion".
There is no 18:27 observation anywhere in the tree. The excluded burst is 18:25:27·421Z; the
"18:27" appears to be the seconds field read as a time.

## 2. The 00:19Z start-up offset — treatments D4 and D5

**Where.** `engine/config/integrated.toml`, `[terminal.bfo_models.startup-offset]`:
`second_hz = [17.0, 130.0]`, `first_minus_second_hz = [0.0, 6.0]`, `points = [64, 16]`. The same
block is repeated in `engine/hypotheses/end-of-flight/smoke/terminal.toml`.

**The evidence**, quoted from the config's own comment: the R1200 acknowledge lies 17–130 Hz above
a steady oscillator (Holland Sec. V-B), the R600 log-on request 0–6 Hz above that (Sec. V-A),
extrapolated from seven log-ons after long outages (Table II), with footnote 13 noting *less* after
an outage of about a minute. **The uniform densities over those ranges are an analyst choice**, and
the config says so. This is the single most load-bearing Holland dependency in the project.

**Two kinds of evidence, and only one of them is inspectable.** The physical mechanism behind the
transient — the oscillator warm-up behaviour itself — rests on Holland's reference **[8]**, an
internal bench study with no date, number or locator, which no reader can obtain or check. The
**calibration that actually produces the 17–130 Hz and 0–6 Hz bounds** is the seven-log-on fit in
Table II, which is in the peer-reviewed article and can be inspected and recomputed. The paper
should therefore make the narrow claim, which is the defensible one: the bounds are an empirical
fit to seven observed log-ons, cited to Table II. It should not rest any weight on [8], and should
say that the bench evidence is unpublished when it characterises the mechanism. This distinction
is what makes Pete's reservation about the start-up term precise rather than general: the number
is checkable, the physical story behind it is not.

**What changes without it.** D4 and D5 cease to exist and the estimate rests on D0–D3. The measured
consequence, from `results/composer-pass2-run-i.md`, is not what one would guess:

- D4 moves the median almost nowhere relative to D3 — arc-latitude −37·44 against −37·43 — so
  Holland's offset is **not** what positions the answer.
- D4's effective sample size is 10,872 against D3's 2,176, and after the searched areas are applied
  D4 holds 1,432 while D3 falls to 393. **Holland's offset is what makes the sharpest treatment
  usable at all.** Without it, the sharpest admissible treatment is one whose Monte Carlo error
  the project's own 1,000-effective-sample criterion rejects.

That is the honest way to state the dependency: Holland buys sampling efficiency, not a different
answer. It is a stronger claim than "the result is robust to the 00:19 treatment", and it is
checkable.

## 3. Hypotheses 1 and 2 exist only because Holland defined them

**Where.** `engine/hypotheses/end-of-flight/full/holland-estimable.toml` (headed "Architecture
10:50 -0600 11 Oct (TOP PRIORITY, Pete confirmed 11:00): make 00:19 Holland H1 and H2 estimable.
PROVISIONAL"), with `two-burst-proposal.toml`, `a1-aimed-pitchdown.toml` and `children-64.toml`
built to serve them, and results in `results/eof-two-burst-oct09/`,
`results/eof-holland-estimable-oct11/`, `results/eof-holland-sweep-run-d-oct11/`,
`results/settling-run-d-holland/`, `results/seabed-search-d-he.md` and
`results/pleiades/next-run-d-he/`.

**The evidence.** Holland's Hypothesis 1 is the project's D4 × C1 (both BFOs with the start-up
offset, fuel exhaustion); Hypothesis 2 is D3 × C2 (both BFOs at face value, some other cause).

**What changes without it.** A substantial block of the end-of-flight module — a targeted proposal,
an aimed pitch-down arm, a raised child count — exists to make two hypotheses estimable that are
Holland's and nobody else's. The measured outcome is a negative result in two separate ways.

**First, H2 is not estimable in any composed product.** From `results/composer-pass2-run-i.md`:
Holland's Hypothesis 2 (D3 × C2 silent) holds an effective sample size of **275** for flight plus
end of flight, **220** with drift, and **29–96** beyond, against the project's floor of 1,000;
coverage item **G25 is OPEN** on exactly these cells. Hypothesis 1 (D4 × C1) is estimable at
**10,845**, **7,077** with drift and **1,428** after the searches. So the comparison the hypotheses
were built to support is one-sided: the arm that carries the transient bias samples, and the arm
that does not, does not.

**Second, the Bayes factor's sign is set by an analyst-declared window, not by the data.** Because
"other" carries no log-on-time density, its likelihood is 1/W over a declared log-on window W, so
ln BF(H1:H2) = ln Z_H1 − ln Z_H2 + ln W and moves with ln W by construction
(`results/eof-holland-estimable-oct11/README.md`, lines 62–63). Measured, over W = 60 / 300 / 900 /
1,775 / 3,600 s: **seed 1 −3·01 / −1·40 / −0·30 / +0·38 / +1·09** (break-even 1,212 s) and **seed 2
−3·07 / −1·46 / −0·36 / +0·31 / +1·02** (break-even 1,295 s). The run-D sweep gives a primary
break-even of **474 s**, with ln BF −0·46 at W = 300 s and +1·32 at W = 1,775 s, and 1,157 s without
the survival factor. The hypothesis comparison therefore favours H1 or H2 according to how wide a
log-on window the analyst declares, and the crossing point itself moves by a factor of nearly three
between versions.

**Correction to this audit's own earlier statement, and to RECOMMENDATION 10.** The 13 October
version of this file reported "ln BF(H1:H2) = −0·34, standard deviation 0·10 over seeds" sourced to
`hypothesis.toml`, and "−1·68 on the R600 burst alone". Neither figure is in the tree at this HEAD.
`hypothesis.toml` carries no Bayes factor. The −0·34 is reconstructible as the mean of the two
seed values **at W = 900 s only** (−0·30 and −0·36), with the 0·10 standing in for their spread, and
quoting it as a single number suppressed the one property that matters — that the sign depends on W.
The −1·68 could not be traced to any Bayes factor; the only −1·684 in the tree is a log-evidence
column in `results/pleiades/next-run-b-core/next-routes/by-0019-option.csv`, which is a different
quantity. Both figures are withdrawn and replaced by the window-indexed values above.

So the paper can say that the project made Holland's hypotheses estimable and found that the data do
not discriminate between them. That is a real contribution and a negative result worth keeping. But
it must be stated as window-conditional and one-sided in estimability, not as a single Bayes factor
near zero — at this size, the conditioning *is* the finding.

## 4. The push-over bounds are *checked* against Holland, not set by him

**Where.** `engine/hypotheses/end-of-flight/full/pushover.toml`, lines 6–13.

**The evidence.** The commanded-rate band U[6,500, 40,000] ft/min is sourced to the module's own
emergency-descent bound and, at the top, to NTSB AAB-02/01 (EgyptAir 990, 31 Oct 1999, about
39,000 ft/min). The load-factor floor U[−1·0, 0·8] g is sourced to CS-25.337(c). Holland then
appears as a **check**: his Table VII needs 13,800–25,300 ft/min at 00:19:37, and his H2 needs
about 0·32 g, and both are inside bands that were set from other sources.

**What changes without it.** Nothing. The bounds stand on their own citations. This is the
healthiest dependency in the audit and is worth one sentence in the paper, because it demonstrates
the bounds were not reverse-engineered to admit Holland's hypotheses.

## 5. Holland's descent-rate bounds are deliberately NOT imported

**Where.** `engine/hypotheses/end-of-flight/lib.rs`, lines 55–58, verbatim: "**Holland's 00:19
descent-rate bounds are deliberately not imported** as a constraint: they are conditional on a
transient assumption this project declines to treat as established, and importing them would kill
the deliberate-descent branch by assumption rather than by evidence."

**What changes without it.** This is a refusal to depend, not a dependency, and it is the most
important Holland item for the paper to state explicitly. A referee who knows the 2018 paper will
expect the 00:19 descent rates to appear as a hard constraint, and will read their absence as an
oversight unless the paper says, in one sentence, that they were excluded by decision and why. The
reason given in the code is a good one and should be published in roughly those words.

## 6. The "Boeing 8-second window statistic" — resolved: it is the inter-burst interval, and it is not Boeing's

Architecture's 18:15Z note lists "the Boeing 8-s window statistic" as a Holland entry point. The 13
October version of this file reported that no such statistic existed. That was half right, and the
missing half is now found, in a document the project already holds and has verified.

**What the eight seconds actually is.** ATSB (2017), printed p. 101, records DST Group's analysis of
the final two satellite transmissions as giving **2,900 to 15,200 ft/min at the 7th arc, rising to
13,800 to 25,300 ft/min eight seconds later**. The eight seconds is the interval between the two
00:19 bursts — the 00:19:29Z R1200 acknowledge and the 00:19:37Z R600 log-on request — and the
statistic is the rate of increase of descent rate across it. Holland's own "0·675 g downward over
8 s" (`pushover.toml` line 13) is the same window expressed as a load factor.

**Which Holland table the ATSB figures correspond to — verified against the source, and a
correction to a standing project ruling.** The project holds that the ATSB's p. 101 bounds "have
lower bounds about 1,000 ft/min below Holland's arXiv v3 Table IV", with the instruction never to
merge the two. The caution is right and stands; the table comparison was against the wrong table.
Read directly from the author's copy (arXiv:1702.02432v3, Pete's file in `~/Downloads`):

| Source | 00:19:29Z | 00:19:37Z |
|---|---|---|
| Holland **Table IV**, p. 9 — "under Hypothesis 1", by track | 3,900 (S) / 5,100 (N) to 13,600 (S) / 14,800 (N) | 14,800 (S) / 15,900 (N) to 24,100 (S) / 25,300 (N) |
| Holland **Table VII**, p. 10 — "range of possible descent rates", unconditional | **2,900 to 14,800** | **13,800 to 25,300** |
| ATSB (2017) p. 101, citing the Nov 2016 flap-analysis report | 2,900 to 15,200 | 13,800 to 25,300 |

So the ATSB figures track **Table VII, the unconditional range**, not the Hypothesis 1 table: the
lower bounds agree exactly (2,900 and 13,800) and the 00:19:37 pair is identical. The only residual
difference is the 00:19:29 maximum, ATSB 15,200 against Table VII 14,800 — 400 ft/min, not 1,000.
The ~1,000 ft/min gap in the standing ruling is the gap between Table IV and Table VII — that is,
between Holland conditional on Hypothesis 1 and Holland unconditional — and not between Holland and
the ATSB at all. The instruction not to merge sources still holds, because the ATSB cites a November
2016 report and the arXiv v3 is January 2018; but a claim attributed to the ATSB and a claim
attributed to Table VII are not in conflict, and the paper should not present them as if they were.

This also clears `pushover.toml` line 9 on substance: its "Table VII, p. 10 … 13,800–25,300 ft/min
at 00:19:37" is the correct table and the correct figures. Only the locator convention is at fault
(entry 8).

**So the attribution to Boeing is the error, and it matters.** The eight-second statistic is DST
Group's, reported by the ATSB, and consistent with Holland's own treatment of the same two bursts.
Boeing's separate contribution is the no-input simulation set peaking at 24,000–58,000 ft/min (SIR
Appendix 1.6E) and the Boeing-calibrated glide band — neither of which is an eight-second window.
Attributing the figure to Boeing would imply an independent manufacturer's confirmation of a descent
rate that is in fact derived from the same two bursts, and therefore from the same transient
assumption. Nothing is independent here that looks independent, which is precisely the kind of thing
Pete's reservation about the start-up term is aimed at.

The two earlier readings remain correct as far as they went. Every other eight-second quantity in
the tree is one of two unrelated things:

- Holland's own integration interval: "about 0·32 g (0·675 g downward over 8 s, Holland p. 8)" —
  `pushover.toml` line 13;
- the end-of-flight module's guidance lag, "the module's 8 s guidance lag below 6,500 ft/min" —
  `pushover.toml` line 12.

## 7. What the ATSB actually did with the 00:19 bursts — the use this project does not reproduce

This is the entry point that bears most directly on Pete's concern that the start-up term "shaped
the original search", and it was missing from the 13 October version.

**The ATSB did not use the 00:19 BFOs as a position likelihood.** There was no reweighting of
positions along the 7th arc by the two final bursts. They entered the search design through two
other channels, both recorded in ATSB (2017) and both **verified** against the printed document:

- **Printed p. 101** — the flap-analysis report carried a summary of the work "performed by DST
  Group scientists on the final two satellite transmissions", which "quantified the range of
  possible rates of descent" (2,900–15,200 ft/min at the arc, 13,800–25,300 ft/min eight seconds
  later) and "ruled out a controlled unpowered glide with the intent to extend range".
- **Printed p. 76** — the consequence for the search: with the flap examination and "the completion
  of DST Group's BFO analysis indicating that the aircraft was probably in a high and increasing
  rate of descent the SSWG recommended the search be limited to a width of **25 NM either side of
  the 7th arc**".

So the causal path from the 00:19 bursts to the seabed that was actually searched runs through a
**corridor width**, via an inference that a rapid descent excluded a long glide. It does not run
through a likelihood at all.

**What changes if it is removed.** Nothing in this project's estimate, because **no option in this
project's sweep reproduces that use**. That is the point worth publishing. The project's D0–D5 sweep
asks what the 00:19 bursts imply about *position*, which is a different question from the one the
ATSB's use answered, and the project's nearest analogue to the ATSB treatment is the held-out
position likelihood combined with the end-of-flight module's own dynamic reach constraint. The
searched-area likelihood then enters as disconfirming evidence over a region whose width was itself
chosen on the strength of the descent inference — so the 00:19 bursts reach the project's posterior
twice, by two different routes, and only one of them is enumerated in the sweep. The paper should
state this plainly: it is a structural feature of the evidence, not a defect in either analysis, and
a reader who is not told will assume the corridor was geometry.

## 8. A citation defect, across at least two configs

Holland is cited by **arXiv page number**: "Holland (arXiv:1702.02432v3, Table VII, p. 10)" and
"Holland p. 8" in `pushover.toml`. The arXiv copy is paginated 1–10. The published article is
*IEEE AESM* 33(2), **24–33**. So "p. 8" and "p. 10" are not the printed pages and no reader of the
journal version can follow them.

The fix, and it is the project's own convention elsewhere: cite **section and table numbers**, not
pages — Sec. V-A, Sec. V-B, Table II, Table VII — which are stable across both versions. That also
matches the in-journal precedent set by Lyne (2024) in this journal, which prints locators of the
form `(Davey et al., 2016. Table 10·1)`. The ledger entry for Holland should carry both the printed
page range and a note that the project's internal citations are to the arXiv copy.

## Summary: what the paper must say about Holland

1. One sentence that the 18:25:27Z first burst is excluded on Holland's signal-quality grounds, not
   as a warm-up transient — and ideally the measured cost of the exclusion, which requires running
   the two sensitivity configs.
2. The start-up offset as a declared analyst choice with its source, the distinction between the
   inspectable seven-log-on calibration (Table II) and the unpublished bench study behind the
   mechanism (reference [8]), and the honest statement that the term buys sampling efficiency rather
   than a different answer.
3. H1 and H2 made estimable, reported as **window-conditional and one-sided**: H2 is not estimable
   in any composed product (ESS 275 → 29–220, G25 open), and ln BF(H1:H2) changes sign with the
   declared log-on window W (break-even 474 s to about 1,300 s). Not a single Bayes factor.
4. That Holland's descent-rate bounds were excluded by decision, with the reason.
5. That the eight-second descent-rate statistic is DST Group's, via ATSB (2017) p. 101, **not
   Boeing's** — Boeing's contribution is the separate no-input simulation set.
6. That the ATSB used the 00:19 bursts as a **corridor width** (25 NM either side of the 7th arc,
   ATSB 2017 pp. 76, 101), not as a position likelihood, and that no option in this project's sweep
   reproduces that use.
7. Section and table locators, never arXiv page numbers.

## Open items this audit creates

Status as at HEAD `50337bd8`, 15 Oct 2026.

| Item | Status | Owner |
|---|---|---|
| Run `obs-r600-1825.toml` and `obs-r600bfo-1825.toml` so the exclusion's cost can be quoted | **OPEN** — no results directory for either config at this HEAD | core, via architecture (RECOMMENDATION 10) |
| Resolve the "Boeing 8-s window statistic" attribution | **RESOLVED** in §6 — it is the 00:19:29→00:19:37 inter-burst interval, DST Group's via ATSB (2017) p. 101; the attribution to Boeing is wrong | closed by this audit |
| Correct the arXiv page locators in `pushover.toml` | **OPEN** — lines 9 and 13 still cite "p. 10" and "p. 8" | end-of-flight, as a comment-only edit |
| Remove the prohibited wording from the proposed draft | **FIXED 15 Oct** in `build_draft_v2.py`; v1 `proposed-draft.tex` is superseded and still carries it | paper assistant |
| Withdraw ln BF −0·34 ± 0·10 and −1·68 wherever they were repeated | **DONE** in this file and amended in `coordination/PAPER.md`; neither figure is in the tree | paper assistant |
