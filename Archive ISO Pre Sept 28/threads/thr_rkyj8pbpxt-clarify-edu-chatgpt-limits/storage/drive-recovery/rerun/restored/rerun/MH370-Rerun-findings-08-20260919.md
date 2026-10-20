# MH370 Rerun checkpoint 8 — exact joint-block kernel and synthetic recovery

Created 2026-09-19T09:53:03Z.

## Outcome

The retained-all two-contact proposal from checkpoint 7 is now implemented and
validated on a solvable synthetic target. The target has two SATCOM-like
observations, a persistent Gaussian BFO bias updated sequentially after the
first contact, discrete flight-path dynamics, and an exactly enumerable
posterior. The guide uses both observations but is divided out; each likelihood
is applied once.

Eight independent probability tests pass. They cover positive support, complete
prior/proposal correction, exact evidence closure for every incoming state,
independent sequential-bias reconstruction, bit-identical `K=1` construction,
per-child weight identity, and a negative control showing that failing to divide
out the guide conditions on the observations twice.

The validation produced 1,408 retained trial rows: 128 seeds for a declared
rare-late-turn stress case and 128 independently generated data sets. The exact
90% HPD coverage over the generative data sets was 91.4%.

## Matched 2,048-path generative comparison

| Method | Median root TV | Median path TV | Median row ESS | Median parent ESS | Median largest parent | 90% HPD coverage |
|---|---:|---:|---:|---:|---:|---:|
| Prior, resample after contact 1 | 0.0367 | 0.0701 | 554 | 355 | 0.870% | 90.6% |
| Prior, defer resampling | 0.0335 | 0.0653 | 411 | 411 | 0.455% | 92.2% |
| Joint guide, `K=1` | **0.0168** | **0.0369** | 1,433 | **1,433** | **0.098%** | 90.6% |
| Joint guide, `K=4` | 0.0291 | 0.0454 | **1,442** | 403 | 0.387% | 92.2% |

The `K=1` joint guide reduced median full-path total-variation error by 43%
relative to deferring the prior proposal and by 47% relative to early
resampling. Its median row ESS was 3.49 times the deferred-prior value. Mean
relative evidence errors were 0.14% for `K=1` and -0.14% for `K=4`; both are
inside their Monte Carlo 95% intervals around zero.

## Important design correction

At the same total path budget, `K=4` kept almost the same row ESS as `K=1` but
used only 512 incoming parents instead of 2,048. Parent ESS fell from 1,433 to
403 and root-marginal error increased. Increasing candidates per ancestor is
therefore not automatically beneficial if it is paid for by shrinking the
incoming population.

For physical implementation, retain the diverse incoming bank and add `K`
candidates to it, or use an explicitly balanced allocation that preserves
initial-state coverage. Matched-budget tests must report row ESS and
parent/root ESS separately; row ESS alone can conceal genealogical loss.

## Archived-failure reconciliation

The exact archived cruise-contact bridge driver and verifier were recovered and
identified. The old five-point, prior-transition, and normalized-guide variants
resampled inside the gap; all three failed reproducibility and were rejected.
The later last-manoeuvre proposal improved two 20,000-candidate trials but failed
the 100,000-candidate comparison and was also rejected.

Checkpoint 8 does not repeat those designs. It defers resampling through both
contacts, retains every candidate, uses a positive guide floor, includes the
complete proposal correction, and carries the bias update across the block.
The detailed distinction is in
`candidate-20260919T0934/ARCHIVED-PROPOSAL-RECONCILIATION.md`.

## Reproduction

```bash
cd candidate-20260919T0934
python3 -m unittest -v test_joint_block_kernel.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 run_synthetic_validation.py
```

The raw trial CSV, aggregate JSON, hashes, seeds, and exact model are retained.

## Boundaries and next step

This control deliberately uses an exactly normalized future-aware guide, which
is stronger than the approximate guide available in the aircraft model. It
does not validate a physical bridge, fuel-exhaustion boundary, evidence value,
posterior probability, or location.

The next step is an opt-in aircraft implementation with `K=1` disabled-mode
replay equality, followed by `K>1` tests that keep the incoming population fixed
and compare matched total evaluations. The Rust 1.98.0 compiler remains absent,
so no uncompiled source change should be adopted as a result. Hydroacoustics
remains excluded.
