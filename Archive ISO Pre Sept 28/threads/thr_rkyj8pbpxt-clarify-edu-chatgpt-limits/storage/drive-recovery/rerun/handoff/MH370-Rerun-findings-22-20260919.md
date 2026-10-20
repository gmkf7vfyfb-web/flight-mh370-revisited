# MH370 Rerun checkpoint 22 — joint target measure and full determinant

Completed 2026-09-19 UTC. This is an experimental delta from checkpoint 21.
The frozen stable release remains checkpoint 20; no baseline sampler or
likelihood source was changed.

## What was implemented

The no-reset radar-start bridge now has an explicit joint change-of-variables
audit for anchor fuel, feed allocation, and any continuously transformed
controls. It evaluates the full square Jacobian determinant rather than a
scalar fuel partial, includes normalized target and proposal branch
probabilities exactly once, and requires uniquely named, normalized branch
partitions with explicit enumeration and support provenance.

The boundary fails closed for non-square, nonfinite, singular, incomplete, or
duplicate branch specifications. It also rejects attempts to describe the
historical 18:28:05.9 anchor-reset model as a continuously propagated no-reset
coordinate transform. Row equilibration prevents unlike units (seconds,
kilograms, and fractions) from creating a false numerical-singularity result.

The output deliberately leaves `global_physical_multiplicity_certified` and
`physical_importance_weight_ready` false. Supplying a mathematically normalized
list is not evidence that every physical aircraft branch has been found.

## Validation

- Seven focused Rust controls passed, including an exact 2-D determinant,
  determinant sign, branch factors, reset/no-reset mismatch, incomplete and
  duplicate partitions, singular/non-square/nonfinite matrices, provenance,
  and a unit-imbalance regression.
- Full Rust workspace: 543 passed, five ignored, zero failed.
- Eight independent 50,000-draw exact-solvable 2-D importance-recovery runs
  passed. Maximum absolute evidence error was 0.00471644, maximum branch-mass
  error 0.00374279, and maximum marginal-CDF error 0.00731334.
- Those controls are mathematical fixtures only. They contain no MH370
  observation, aircraft parameter, or location inference.

## Scientific consequence

Checkpoint 21 showed that a regenerated derivative differs from a frozen-path
partial and that the historical estimator resets fuel at the anchor. This
checkpoint closes the arithmetic/API gap for a declared multidimensional
no-reset target, but it does not resolve target equivalence. The production
bridge must still specify the actual joint radar-fuel/feed/control prior,
enumerate physical branches and support, add uncertain radar/nuisance state and
production atmosphere, and complete same-target synthetic recovery before any
18:39/19:41 posterior comparison.

No full-aircraft bridge was executed. No replacement estimator, calibrated
probability, or location result is claimed. Hydroacoustics remains excluded;
IGOGU remains a separate optional conditional hypothesis and was not reused as
independent evidence.

