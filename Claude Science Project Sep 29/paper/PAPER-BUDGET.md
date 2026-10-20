# PAPER-BUDGET.md — section budget, ranked results, figure and table list

Target: one paper, The Journal of Navigation. Prepared by the paper and citations assistant.
Status: PROPOSED. Pete decides. Written 13 Oct 2026 against `paper/JON-RULES.md` (rules verified
12 Oct 2026) and `paper/JON-MODEL-PAPERS.md` (nine papers read in full).

## 1. The envelope, and which limit actually binds

Verified: average length 6,000–8,000 words; up to 20 pages including figures and tables; single
column, 12 point Times New Roman, 2·54cm margins, single line spacing, no paragraph spacing.

**The word range binds; the page count does not.** In that page format a full page carries roughly
46 lines at about 12 words, so ~550 words, and 20 pages is therefore ~11,000 words of unbroken
text. A paper of 8,000 words with ten figures and three tables still lands near 17 pages. *This is
an estimate from the format specification, not a measured compile — tectonic cannot fetch its
support files through the sandbox, so no page proof has been produced. Treat ±2 pages as the
uncertainty and confirm with a real compile before submission.*

Not yet established: **whether the reference list counts toward the 20 pages.** Not stated on any
of the five Cambridge Core pages read. Worth one email to journal@rin.org.uk; at 27 references,
the surveyed median, it is under a page either way and cannot change a decision.

Survey medians, nine papers: 19 printed pages, ~7,120 words of main text, 9 figures, 3 tables,
13 numbered equations, 27 references. No paper exceeded 35 references. Every paper from 2019 on is
19 pages or fewer; only the 2015 and 2016 MH370 papers exceed 20. **None of the nine carries a
nomenclature or symbol table** — symbols are defined in running prose, which is also Pete's own
practice in the dissertation.

## 2. Proposed section budget

7,350 words of main text, which is inside the stated range with ~650 words of headroom,
against the surveyed median of 7,120. The middle column is measured from the generated
`paper/proposed-draft/proposed-draft-v2.tex`, computed rather than summed by hand, with the
column sums asserted in the generating code.

| Section | Draft now | Proposed | Change | Why |
|---|---:|---:|---:|---|
| Abstract | 154 | 150 | -4 | at the stated limit |
| 1. Introduction | 810 | 850 | +40 | needs the two-paragraph literature position the draft lacks |
| 2. Methodology | 2,390 | 2,250 | -140 | a net cut; see the split below |
| 3. Results | 2,838 | 3,400 | +562 | the paper's contribution, and currently the thinnest part relative to what it carries |
| 4. Conclusions and recommendations | 459 | 700 | +241 | carries the research case; 459 words cannot |
| Declarations, acknowledgements | 104 | 150 | +46 | the AI declaration must be specific |
| References | 183 | — | — | excluded from the word target |
| **Main text total** (excluding abstract and references) | **6,601** | **7,350** | **+749** | |

Within the methodology, the proposed split. The principle is that **every word spent restating
Davey et al. is a word taken from the extensions**, so the inherited particle filter gets a
summary and a printed-page citation, following Ng et al. (2024), which compresses its inherited
method by citing the originating paper's own equation numbers.

| 2.x | Draft now | Proposed | Note |
|---|---:|---:|---|
| 2.1 The parameters to be estimated | 456 | 400 | tighten; the four parameter blocks are clear |
| 2.2 The observations, and the functional models that relate them to the trajectory | 209 | 300 | now carries the radar statement; needs what each observation constrains |
| 2.3 Why the system is under-determined | 308 | 300 | keep; the explicit count is the paper's clearest single argument |
| 2.4 Monte Carlo simulation constrained by feasible dynamics | 258 | 300 | add the proposal and the coverage statement |
| 2.5 Weighting by the evidence | 131 | 200 | add tempering and the effective-sample-size criterion |
| 2.6 The conditional structure, and why the estimator is staged | 248 | 250 | keep |
| 2.7 The impact-level likelihoods | 507 | 350 | compress: five modules at about 70 words each, each citing its own source |
| 2.8 Composition, mixing and convergence | 273 | 150 | move the detail into 3.1 where the numbers are |
| **total** | **2,390** | **2,250** | |

## 3. Ranked results: what carries the paper

Ranked by importance to the argument **and** by how firmly the evidence supports the claim. Every
entry inherits the labels of its source artifact. All pass-2 run I results are **NOT CONVERGED**,
**conditional on an equal descent-family prior**, with **provisional end-of-flight physics** and
**Western Australia non-recovery not modelled**. Those labels travel with every number below and
must appear in the paper, not only in a limitations paragraph.

### Tier 1 — the paper does not exist without these (target ~1,900 words of Results)

1. **The reproduction, and that the estimate is not yet converged.** `config/davey2016.toml`
   reproduces the book byte for byte; the extended estimator does not converge. Split-half
   agreement against a 0·924 floor: waypoints 0·916, Davey reproduction 0·891, free flight 0·830,
   descent-climb 0·794; composed partitions differ 11–57% in 90% area and up to 0·98° in median;
   per-seed ln Z standard deviation 0·20–0·36 nat. **Reported first, before any posterior.** This
   is the honest frame for everything else and, on the journal's own warning that papers verified
   only by simulation are judged less favourably, the paper's credibility rests on reporting it
   rather than burying it.
2. **The unsuccessful searches are the strongest single piece of evidence in the problem.** They
   remove 54–71% of probability (Δln Z −0·78 to −1·23), move the median 0·3–1·2° north, and
   *enlarge* the 90% region by 60–96%. P(A1) falls 0·17→0·08. Counter-intuitive, quantified, and
   the clearest demonstration that disconfirming evidence is informative.
3. **The waypoint family carries essentially all the weight.** Route stratum weights: waypoints
   0·998, free flight 0·0011, Davey reproduction 0·00033, descent-climb 0·00015. The single
   largest departure from the 2016 result and the one a navigation readership will care about most.
   **Must be reported with the sampling-coverage caveat**: this is a weight over the strata that
   were sampled, not a proof that no unsampled route competes.
4. **The 00:19Z data treatment is a second-order effect, not a first-order one.** Across D0–D5 the
   median moves less than 0·5° (−37·07 to −37·44) while the 90% area halves (152k→63k km²), and
   ESS collapses from 823,551 to 2,176. Settles a question the literature has argued over, and the
   ESS collapse is itself the finding: the sharpest treatments are the least reliable.

### Tier 2 — carries the paper's claim to be integrated (~1,100 words)

5. **Drift widens rather than narrows.** 117k→165k km², shifted north-east; Δln Z −128·06 to
   −128·16 across ocean models, a spread of 0·10 nat.
6. **The ocean models are not distinguished by the data.** P(GLORYS12|data) 0·46–0·51 with drift,
   0·47–0·51 after searches, 0·54–0·63 with the imagery hypothesis; |ln BF| ≤ 0·53 throughout. A
   clean negative result and an honest statement of what debris cannot resolve.
7. **The seabed distribution is not the impact distribution, but close.** Within 2·5% of the
   impact regions; halves differ 22–43% in 90% area. The settling stage is a small correction,
   which is worth stating because it is not obvious a priori.
8. **Evidence accounting.** The per-stage ln Z table is the integrated estimator's audit trail and
   the thing no previous MH370 analysis publishes.

### Tier 3 — short mention, one or two sentences each (~300 words total)

9. The imagery hypothesis, **reported conditionally only** — P(GLORYS12|data) rises to 0·54–0·63
   under it. Never as a result.
10. Hydroacoustics, **predictive only, not evidence**, with the transmission loss uncalibrated.
    Its substance belongs in the recommendations, not the results.
11. G13 open: 11–21% of composed weight sits above 1·25 V_MO. A stated limitation.
12. G10 closed on run I: drift not computed for ≤0·11% of base weight.

### Out of the paper

- The fuel model's internal construction — cite the repository, state what it constrains.
- Antenna gain (parked), arc-kernel (placeholder), radar-fix internals.
- The τ impact-dissipation method — not yet written up; cannot be cited until it is.
- Every SPECIFIED-but-not-run element. Name them in one sentence as further work, with no numbers.

## 4. Figure list

Ten proposed, against a surveyed median of nine. The five already embedded in the assistant's
draft are marked EMBEDDED; the rest are proposed and not yet drawn.

| # | Figure | Source | Carries | Status |
|---|---|---|---|---|
| 1 | The estimator as a staged flow, 18:01Z to seabed | to be drawn | §2.6; orients the reader | proposed |
| 2 | Impact arc-latitude density by 00:19Z treatment | `composer-pass2-run-i/fig1` | result 4 | EMBEDDED |
| 3 | Ocean-model posterior weight | `composer-pass2-run-i/fig3` | result 6 | EMBEDDED |
| 4 | Impact regions, map | `composer-pass2-run-i/fig2` | results 2, 3 | EMBEDDED |
| 5 | Seabed regions, map | `composer-pass2-run-i/fig5` | result 7 | EMBEDDED |
| 6 | Coverage and effective sample size | `composer-pass2-run-i/fig4` | results 1, 4 | EMBEDDED |
| 7 | Split-half agreement by route stratum against the 0·924 floor | pass-2 artifacts | result 1 | proposed |
| 8 | Searched areas with the posterior before and after | seabed-search + composer | result 2 | proposed |
| 9 | Evidence accounting, ln Z by stage | pass-2 artifacts | result 8 | proposed |
| 10 | Predicted hydroacoustic level by descent family, with the calibration band | hydroacoustics | §4 recommendations | **blocked on RECOMMENDATION 8** |

**Greyscale survival, tested by converting every one of the five embedded figures and inspecting
each.** Figure 2 (impact arc-latitude by 00:19Z treatment) **fails**: six curves separated only by
hue, and the legend swatches for "00:19 not used" and "timing only" become near-identical greys.
Figure 3 (ocean models) **fails in panel (a)**, where two of the four marker series resolve to the
same grey; its panel (b) survives, because it uses solid, light and dashed lines. Figures 4, 5 and 6
**survive**: the two maps separate their regions by dark and light fill with a dashed outline, and
the effective-sample-size panel is a sequential greyscale map with the value printed in every cell.
Figure 6 carries a separate defect: its caption and colourbar label refer to a "red box" marking
cells below 1,000, which is invisible in print, while the cue that does survive — the value set in
bold — is not mentioned. RECOMMENDATION 9 refers; the journal makes greyscale legibility the
author's responsibility. All ten need alt text on an
Accessibility Descriptions Submission Form, and should be supplied as vector eps or pdf, not the
current png, to meet 1200dpi line art.

## 5. Table list

Three, matching the surveyed median.

| # | Table | Carries |
|---|---|---|
| 1 | Observations, their functional models, and what each constrains | §2.2 |
| 2 | Impact and seabed summary by 00:19Z treatment: median, 50% and 90% area, ESS | results 1, 4 |
| 3 | Evidence accounting by stage: Δln Z, weight removed, family probabilities | results 2, 8 |

Table captions go **above** the table. Figure captions go **below** the figure.

## 6. What this budget does not resolve

- The reference list's page status (one email).
- The AI declaration's final wording, which must name tool, version, dates, access route and a
  full description of use, and which belongs in the Methods section because the tools analysed
  data. None of the nine surveyed papers carries one, so there is no in-journal template.
- A data-availability statement: the journal's Research Transparency policy has not yet been read.
- Whether run I is the run the paper reports. Everything above is conditional on that choice; if a
  converged run supersedes it, the ranking survives but every number changes.
