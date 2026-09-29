# MH370 Rerun checkpoint 21 — regenerated-path shooting and target-measure audit

Completed 2026-09-19T21:22:00.386196+00:00. Experimental work is separate from frozen checkpoint
20. The baseline sampler and likelihood source files are byte-identical to that
release. This checkpoint does not claim a replacement estimator is validated.

## New implementation and observed result

Implemented a compiled scalar shooting diagnostic that regenerates the entire
radar-to-anchor prefix with the same random tape, including mass-dependent
initialization and dynamics. It checks the anchor residual, deterministic replay,
discrete branch signature, three derivative scales and one-sided slopes. It
refuses unsupported paths, changed branches, singular/unstable derivatives and
out-of-support stencils. No importance weights are emitted.

All 16 declared local fixtures completed: eight ordinary synthetic-atmosphere
prefixes and eight deliberately mass-sensitive stress prefixes. Their largest
absolute anchor residual was 9.12e-08 kg.
Ordinary fixtures agree with the fixed-path derivative to numerical precision.
The active-limit stress cases instead show the fixed-path derivative overstating
the regenerated derivative by 0.00974–0.15452 percent.
Using a frozen inverse after changing the target anchor by +20 kg misses the
regenerated anchor by 0.001947–0.030856 kg.
These are synthetic construction tests, NOT estimates of real MH370 errors.
Stress CLmax=0.85 is deliberately artificial; it is not a calibrated aircraft
parameter. The earlier ineffective stress attempt is retained, not discarded.

## Model distinction that must not be hidden

Source audit confirms the historical broad estimator initializes with its
configured source fuel, then resets both feeds at the fuel anchor with zero
log-likelihood increment. Checkpoint 19 identified that reset. The new conclusion
is its implication for target equivalence: a continuously matched, no-reset
bridge is not automatically the same model with a better proposal. A Jacobian
alone does not establish equality. The complete joint prior and branch law must
be derived or the new model explicitly labelled as a separate sensitivity.

The accompanying derivation distinguishes radar-coordinate and anchor-coordinate
weights, including the absolute total derivative exactly once. It also flags
the additional determinant needed if feed allocation is independently varied.

## New exact multiplicity control

For the solvable map A=m² with two branches, omitting branch probabilities
doubles total density. Using the frozen-path partial instead of the total
derivative halves it. Keeping only the positive branch can reproduce the correct
anchor marginal while giving the wrong radar-state mean: 14/9 rather than 7/9
for the declared unequal-branch fixture. This is why endpoint-only recovery
checks cannot establish early-state recovery.

Seven independent Python controls pass. Twenty-four seeded 10,000-draw runs
compare three correctly weighted proposal designs; evidence, ESS, both marginal
CDF errors and branch masses are retained. These are new mathematical branch
controls, not full-aircraft synthetic posterior recovery or calibration coverage.

## Validation and release status

- Full Rust workspace: 536 passed, five ignored, zero failures.
- Ten new Rust controls (nine numerical tests plus one 16-fixture aircraft test).
- Seven independent exact Python controls; 24 matched-budget mathematical runs.
- Three source files differ from checkpoint20: new diagnostic module, export,
  and integration tests. Production sampler/likelihood files are unchanged.
- All raw evaluations, full root traces, earlier attempts and successful logs
  are included. Five ignored workspace tests remain explicitly unexecuted.

The stable release remains checkpoint20. This experimental API cannot certify
global root count, target equivalence, or valid full-aircraft importance weights.
No new 18:39/19:41 posterior comparison, full endpoint bridge, exhaustion-window
recovery, or calibrated location probability is claimed. Hydroacoustics remains
excluded; IGOGU artifacts remain separate. Build instructions, exact hashes and
next actions are in this bundle. Include it as a delta in the 22:00 milestone;
do not wait for further experiments or overwrite already released archives.
