# HOLLAND-AUDIT.md — every place Holland (2018) enters the method or the calibration

Owed to architecture's 18:15Z note of 12 Oct 2026, item 3. Prepared by the paper and citations
assistant, 13 Oct 2026, by searching the whole tree at the commit then on `claude-science-sep29`.
Source graded **peer-reviewed**: Holland, I. D. (2018). MH370 Burst Frequency Offset Analysis and
Implications on Descent Rate at End-of-Flight. *IEEE Aerospace and Electronic Systems Magazine*,
33(2), 24–33, DOI 10.1109/MAES.2018.170048. The copy the project reads is the author's green
open-access copy, arXiv:1702.02432v3.

Holland is named 149 times in `coordination/architecture.md` and 60 times in
`results/composer-pass2-run-i.md`. What follows is only the places where his work **does
something** — where it sets a number, justifies an exclusion, or defines a hypothesis.

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
Holland's and nobody else's. The measured outcome, from `hypothesis.toml`: ln BF(H1:H2) = **−0·34,
standard deviation 0·10 over seeds**, with cause "other"; −1·68 on the R600 burst alone; and the
two-burst posteriors under H1 and H2 **remain unconverged, parent-limited at 4–78 effective parents
per seed**. On Kass and Raftery's scale −0·34 is "not worth more than a bare mention", and it is
only about three seed standard deviations from zero.

So the paper can say that the project made Holland's hypotheses estimable and found the data do not
discriminate between them. That is a real contribution and a negative result worth keeping. What
the paper must not do is report the ln BF without its seed standard deviation and its
non-convergence, because at that size the uncertainty is the finding.

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

## 6. The "Boeing 8-second window statistic" — I cannot find it

Architecture's 18:15Z note lists "the Boeing 8-s window statistic" as a Holland entry point to
audit. **No such statistic exists in the tree.** Every eight-second quantity found is one of two
unrelated things:

- Holland's own integration interval: "about 0·32 g (0·675 g downward over 8 s, Holland p. 8)" —
  `pushover.toml` line 13;
- the end-of-flight module's guidance lag, "the module's 8 s guidance lag below 6,500 ft/min" —
  `pushover.toml` line 12.

Boeing's contribution in the tree is the no-input simulation set peaking at 24,000–58,000 ft/min
(SIR Appendix 1.6E) and the Boeing-calibrated glide band, neither of which is an eight-second
window. Either architecture means something not committed to the repository, or the attribution to
Boeing is a mis-memory of Holland's 8 s. **Nothing about it should be published until that is
resolved.** Query back to architecture.

## 7. A citation defect, across at least two configs

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
2. The start-up offset as a declared analyst choice with its source, and the honest statement that
   it buys sampling efficiency rather than a different answer.
3. H1 and H2 made estimable, with ln BF −0·34 ± 0·10 over seeds and **unconverged** — a negative
   result, reported as one.
4. That Holland's descent-rate bounds were excluded by decision, with the reason.
5. Section and table locators, never arXiv page numbers.

## Open items this audit creates

- Run `obs-r600-1825.toml` and `obs-r600bfo-1825.toml` so the exclusion's cost can be quoted.
- Resolve the "Boeing 8-s window statistic" attribution.
- Correct the arXiv page citations in `pushover.toml` and anywhere else they appear.
