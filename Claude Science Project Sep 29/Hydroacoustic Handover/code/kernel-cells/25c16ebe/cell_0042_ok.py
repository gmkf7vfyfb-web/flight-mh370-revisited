gaps = r"""# End-of-flight master prompt — what needs modifying

Against `threads/master-prompts/end-of-flight.md` version 4 (36,550 bytes, 7 October 2026), which is
the current version. Every ruling that shaped run I and run-i-dive post-dates it: the Boeing
calibration decisions of 9 October, the spiral-regime mixing ruling, the 6-DOF physics-prior ruling,
the three approved diagnostic smoke tests, the C2-silent aim, the dive branch, and the sea-level
static thrust correction. A fresh module session reading the contract today would be told the model
does not exist.

Grouped by what each change buys. Items A–C change what the module is obliged to produce; D–H close
the places where a prose requirement in the prompt was silently not honoured; I–L are additions from
the audit and the benchmark pass.

---

## A. §3 Build status is wrong and actively misleading

It states "The EoF **model** — **does not exist**", "Stage-4 composer — **not built**", and that the
fuel burn fix is "re-run pending". The model has since run at full scale twice, the burn fix is in
and run I is the declared seed. The section's purpose was to stop a session rebuilding the
interface; it now has the opposite effect.

**Change:** replace the table with the current state and a pointer to the run notes, and add a rule
that the section is updated at the end of every full sweep rather than at the next revision.

## B. The three-arm experiment is instructed but not gated

§1 defines V1a, V1b and V2 and correctly forbids hard-coding a checkpoint, and both of those were
honoured — empty onset support is a legal setting. But the prompt never says which hand-off epoch a
*full sweep* must use, and it describes V1a as "nearly free, because the hand-off is built anyway".
Every full sweep since has accordingly been V1a on an m0011 hand-off, and V1b and V2 exist only as
the 11 October stand-in on a superseded core run and superseded physics.

**Change:** make deliverable 4 an acceptance condition rather than an instruction. No result may be
reported as the headline comparison unless all three arms ran on the same binary, the same core run
and the same evidence columns. State explicitly what a V1a-only sweep is permitted to claim, which
§1 already almost does and should say as a rule.

## C. The boundary diagnostic has no threshold and no consequence

§4 requires it twice — "if supported trajectories accumulate against the checkpoint boundary, the
boundary is influencing the answer and the run must be repeated from 21:41" and "Report where the
supported onset mass sits relative to the boundary, every time". Neither run note reports it. The
measured value is 21.6 per cent of the deliberate family's weight within 30 s of the hand-off, with
the earliest onset in the file at the hand-off epoch itself.

**Change:** give it a number and a consequence. Define the statistic (weight fraction with onset
within a stated window of the earliest permitted onset, per family), require it in the run note's
coverage section, and set the trigger above which the sweep must be repeated from an earlier
checkpoint. The word "gate" appears nowhere in the prompt; this is the first place it should.

## D. Two prose requirements in §4 were not honoured, and cannot be checked as written

- "level-offs and changes of descent rate within the envelope, **including 10,000 ft and 4,000 ft**"
  — the configured level-off support is 11,000 to 30,000 ft, which excludes both.
- "substantial lower-altitude flight as a possibility: **an hour between onset and impact need not
  mean an hour descending**" — measured, 1.75 per cent of weight has more than 600 s of
  non-descending flight; the median is 53 s.

Both failed quietly because they are prose inside a bullet list with no corresponding reported
quantity.

**Change:** convert each into a declared support bound plus a coverage statistic reported per run —
the level-off support as an interval that must contain the two named altitudes, and the realised
distribution of non-descending time with a stated minimum mass beyond a named duration.

## E. The four control outcomes are required but two are configured to zero weight

§4 requires all four — control through an attempted ditching, control then lost, no effective
intervention, upset then demonstrated recovery — "within either initiation branch". The realised
weights are 1,1,1,1 for the fuel-exhaustion families and 0.5,0.5,0,0 for the deliberate family, so
the two outcomes are absent from the family where the distinction between an attempted and an
achieved ditching matters most. The prompt already makes that distinction a named requirement in
the same section.

**Change:** require the control weights to be stated per family in every run note, and a zero weight
to carry a written justification rather than being set in configuration.

## F. Nothing separates a change of proposal from a change of support — the most important gap

§8 handles importance weighting properly: exact weights, weight splitting across descendants,
correction for oversampled families, retention of family evidence before normalising. That is why
the aimed proposals are demonstrably harmless — under the sampling weight alone every aimed latent
is recovered uniform on its full support.

But the prompt has **no rule at all** for changing what the model can reach. The dive branch was a
support change, it was triggered by a fit failure in the cells that use the contested 00:19 data,
and nothing in the contract required it to be recorded as such or re-validated against the held-out
column. On the evidence it was a sound change — the data move the dive share down from its prior,
and the held-out impact median moved 0.01 degrees — but the contract did not require that check and
it was not the reason the change was accepted.

**Change:** add a numbered rule to §2. Every change to the model's reach is logged with its physical
justification, whether it was prompted by a fit failure, and the held-out log-evidence and impact
median before and after. Plus a standing silent-exclusion review before each sweep: list every
bound, zero weight and configured range, and for each state whether its justification is independent
of how well anything fits 00:19. Items C, D and E above are the current answers to that review, and
none of them was found by the sampler's own diagnostics, because none of them can be.

## G. §11's test list omits the test that settles the forcing question

It lists ballistic energy conservation, level-flight equilibrium, the BFO finite-difference,
synthetic recovery and hand-computed fixtures. The module built and passed a stronger test than any
of them — recovery of the uniform prior on every aimed latent under the sampling weight alone,
measured here at a maximum CDF deviation of 0.0030, with a stored mean importance correction of
1.000178 ± 0.000693 — and the prompt neither asks for it nor says it must be reported.

**Change:** add it as a required test with its statistic named, and require the figures in every run
note that uses an aimed proposal. This is what makes the aim defensible in the paper.

## H. ESS alone is not a sufficient convergence report

§2 rule 6 requires ESS and split-half agreement. Under both 00:19 bursts on the raw model the
effective sample size is 38.8 over 100,000 parents **and** the largest single trajectory carries
12.3 per cent with the top ten carrying 33.5 per cent. The second fact is the one that tells you the
shape is not estimated, and the first does not imply it.

**Change:** add the top-weight share and the top-ten share to rule 6, and require the per-seed
figure beside the pooled one, since the published tables pool eight seeds and four strata.

## I. Three interface items do not behave as the contract intends

§2 rules in attitude, the dissipation duration τ and a debris class, and says "Emit them anyway".
As built: the six energy-transfer columns are entirely non-finite in the impact file and τ lives in
a per-seed sidecar joined by row order; the transferred-energy field equals total kinetic energy to
float32 precision, so all of it reaches the water; and 52 per cent of weight carries exactly zero
bank, assigned rather than computed, which a consumer cannot distinguish from a computed zero.

**Change:** three sentences. The fields are emitted in the impact sample, not a sidecar. A quantity
not computed for a family is NaN for that family — the prompt already says NaN means "not computed",
and a placeholder value breaks that rule. And the energy delivered to the water is either a declared
alternative with a sampled fraction or is labelled an upper anchor wherever it is quoted.

## J. The calibration requirement has no gate

§8 names the right targets — the ten Boeing traces, phugoid period, bank growth, time to 15,000
ft/min, distance. The runs carry "6-DOF gate not passed" as a self-declared label and proceed. The
6-DOF fit on the 747 base did not converge, its joint misfit fell 4 per cent, and the phugoid agrees
only when the module's own trim at loss of control is used.

**Change:** name the gate in the contract and attach a consequence — which results may and may not
be quoted while it is unpassed. The benchmark pass makes this heavier than it looks: no retrievable
source publishes an impact speed, flight-path angle, impact energy or energy-transfer duration for
this accident, so the trace fit is not one validation among several, it is the only aircraft-specific
validation available for the uncontrolled arm.

## K. Two additions to §12 pitfalls from the benchmark pass

- **None of the ten Boeing cases is in a steep descent as the 7th arc is crossed.** So Boeing's own
  simulations of uncontrolled flight after dual fuel exhaustion and the descent rate derived from the
  00:19 offsets do not agree with each other. This is the single most important framing fact for the
  paper and it bears directly on whether the steep arm is over-trusted. Report it; do not reconcile
  it.
- **Holland's bounds are published by hypothesis and the separation is usually lost in quotation** —
  3,900 to 14,800 ft/min under the satellite-data-unit-restart hypothesis against 2,900 to 6,800
  ft/min under the no-warm-up hypothesis at 00:19:29. §7's declared-alternative structure is already
  the right one; the prompt should require the comparison to be made against the matching hypothesis
  rather than the merged range.

## L. The mission statement should lead with the ordering

§1 says the module exists "to produce an honest posterior, not to decide what happened", and
"Simulations are for learning physics, not for settling the question". Both are right and neither
states the ordering that the push-over question turned on: **simulate what the aircraft is likely to
have actually done, then test those simulations against the evidence; never shape the simulation to
match the evidence.** Because the 00:19 measurements are questioned, the point of scoring subsets is
to see which fit and which do not, as evidence about which data to use.

**Change:** put that ordering at the head of §1 as the mission's first sentence, and make §2's new
support-change rule the mechanism that enforces it. The two belong together: the ordering is the
intent, and the support-change log is the only thing that can demonstrate it was followed.

---

## What does not need changing

§2's ten contract rules, §5's fuel-coupling argument and its case against conditioning on
flame-out, §6's treatment of the log-on as one observation with the cause as a declared alternative,
§7's two orthogonal sweep axes, §9's source-provenance discipline, and §11's two corrected tests —
the frozen-atmosphere phugoid and the energy-height glide — are all sound and were honoured. §7's
disputed 17.50 against 17.81 Hz per 1,000 ft/min attribution is still open and should stay flagged
until the core session settles it.
"""
open("eof-master-prompt-revision-notes.md","w").write(gaps)
print(len(gaps))
