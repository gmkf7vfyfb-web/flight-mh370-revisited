# Release v0.1 notes

## Milestone outcome

Release v0.1 freezes a coherent, reproducible Bayesian-estimator checkpoint
for the final flight of MH370. It is intentionally a milestone rather than a
claim of scientific finality.

Completed scope:

- deterministic central 00:11 inference across three explicit model families,
  five seeds, and 450,000 total evaluated particles;
- typed posterior handoff to the corrected-R600 BTO contact;
- six separately labelled end-of-flight impact families;
- conditional antenna-gain and Pléiades sensitivities;
- ocean-drift and hydroacoustic diagnostics that are fail-closed at zero
  estimator weight;
- provisional searched-area evidence and planning views;
- publication PDFs, SVGs, PNGs, particle tables, run manifests, and a
  fail-closed release validator;
- truth-separated MH371 known-flight control.

## Central numerical summaries

- BTO-only 00:11 mean: 36.4895 degrees south, 89.3491 degrees east.
- BTO plus medium-BFO mean: 36.4086 degrees south, 89.4961 degrees east.
- BTO plus medium-BFO plus conditional gain mean: 36.4095 degrees south,
  89.4923 degrees east.
- Primary conditional end-of-flight family mean: 38.1596 degrees south,
  89.4088 degrees east.

All values remain conditional on their named models. Families are not assigned
cross-family probabilities and are not pooled.

## Verification at freeze

- Rust formatting passed.
- The full workspace test suite passed; five explicitly ignored tests are
  external-data or manual-performance checks.
- The original validator passed all 70 release artifacts.
- Core and R600 input/output manifests closed with zero mismatches.
- The release directory contained no empty files or symlinks.
- A fresh medium-BFO MH371 control made with the exact v0.1 producer binary
  completed with `numerical_valid=true`.

## Deferred beyond v0.1

- calibrated probabilities for B777 terminal systems/aerodynamic families;
- R1200/startup transient calibration;
- admission-quality ocean-drift likelihoods;
- raw hydrophone channels and transfer-function calibration;
- complete survey swaths, holidays, and probability-of-detection modelling;
- broad runner refactoring and nonblocking style-lint cleanup;
- further particle-lineage experiments.

These items are stated limitations and do not invalidate the bounded v0.1
claims.
