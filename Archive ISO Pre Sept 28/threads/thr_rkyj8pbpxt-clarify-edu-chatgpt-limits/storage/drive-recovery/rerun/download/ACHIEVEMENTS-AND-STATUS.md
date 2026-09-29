# Achievements, improvements and current status

## Bottom line

The work now has a reproducible and tested software core, an offline toolchain, preserved inputs and results, and a clear failure-analysis trail. The frozen release is checkpoint 20. The estimator is not yet scientifically calibrated enough to make a wreckage-location probability claim, and no such claim is made here.

## What was achieved

1. Reproduced and audited the historical particle-filter workflow, with exact configurations, deterministic seeds, raw and derived results, plots, logs, and retained failed trials.
2. Localized the main estimator weakness. The selective 18:39 and 19:41 likelihoods expose poor proposal overlap and too few distinct candidate paths; later resampling converts that finite-coverage problem into genealogical collapse. Hard physical rejection was not the primary explanation in the tested diagnostics.
3. Built exact solvable and synthetic recovery controls. Corrected endpoint proposals greatly improved ESS and marginal-CDF recovery at matched budgets, while preserving proposal/prior ratios and avoiding duplicate likelihood use.
4. Tested and rejected two tempting replacements: a single-block K=4 descendant sampler and a fixed root-defensive resampling mixture. Both retained more labels or improved row ESS without solving effective posterior diversity; the evidence is preserved rather than hidden.
5. Corrected provenance and boundary handling. The 18:01:49 historical source, conditional 18:22:12 radar state, and 18:28:05.9 fuel anchor are typed distinctly. False raw-radar provenance, 4 Hz calibration, jettison, clock mismatch, duplicate fuel correction, and accidental reset behavior fail closed.
6. Implemented feed-resolved powered-fuel propagation from 18:22:12 to the fuel anchor. The affine fuel map is derived from actual powered segments, and propagated left/right feeds and total fuel must reproduce the anchor within `1e-7 kg`.
7. Implemented a mass-coupled stochastic aircraft prefix and found that a fixed-path fuel derivative can be wrong when mass changes the regenerated trajectory. Checkpoint 20 therefore exposes the prefix only as an experimental diagnostic API and leaves the production sampler unchanged.
8. Added regenerated-path shooting checks, a full multidimensional Jacobian determinant, explicit target/proposal branch probabilities, normalized-partition checks, and reset/no-reset target separation in experimental checkpoints 21–22.
9. Recovered and froze the exact Rust 1.98.0 toolchain, Cargo dependency cache, lockfile, weather and magnetic inputs, optimized binary, source, tests, and recovery scripts for offline Linux x86_64 continuation.
10. Preserved IGOGU as an optional conditional hypothesis with its own complete multipart recovery archives, reports, code, proposals, seeds, 1,710,701 recovered positive-weight trajectories, R600 sensitivity, FIR/waypoint follow-up, and evidence-scope warnings.

## Validation at the freeze

- Checkpoint 20 stable release: 526 full-workspace Rust tests passed, five ignored, zero failed; six new Rust controls and four independent Python controls passed. Eight mass-coupled prefix draws reconciled forward/backward fuel with maximum error `1.1641532182693481e-10 kg`.
- Checkpoint 21 experimental delta: 536 Rust tests and seven independent Python controls passed; all 16 regenerated aircraft-prefix cases converged.
- Checkpoint 22 experimental delta: 543 Rust tests passed, five ignored, zero failed. Eight independent 50,000-draw solvable recovery runs passed; maximum absolute evidence error was 0.00471644. These are mathematical fixtures, not MH370 location calibration.
- Core recovery archive: ZIP CRC passed; every blob hash passed; all 32 Drive parts were downloaded and matched against SHA-256.
- Stable checkpoint, experimental checkpoints, and publication supplement were independently read back from Drive and hash checked.

## Important improvements in interpretation

- Row ESS can rebound after resampling while root ancestry has already collapsed; root ESS and maximum-root weight are now first-class diagnostics.
- The 18:22:12 configured point lies essentially on the MEKAR–NILAM airway and is best described as constructed airway interpolation unless primary coordinates/covariance are produced.
- Fuel at radar cannot be an independent draw if canonical fuel is defined at 18:28:05.9; it must be the path-induced preimage, with the correct full transformation measure.
- A mathematically normalized declared branch list is not proof that all physical branches have been enumerated.
- The endpoint and exhaustion time are proposal devices, never measured positions or extra observations.
- Software test success is separated explicitly from posterior calibration and scientific adequacy.

## IGOGU status

IGOGU remains conditional and separate. The original position likelihood ends at 00:11; its original 00:19 use was fuel timing only. A separately declared R600 sensitivity uses only the 00:19:29.416 R600 BTO with its stated gate and Gaussian reweighting, not 00:19 BFO or the last R1200 BTO. The posterior is not reliably converged and the terminal extensions are kinematic, not a validated impact model. It must not be multiplied into the baseline as if it were new independent evidence.

## Pending, in order

1. Define the complete continuous target and proposal law for radar state, fuel/feed allocation, controls, nuisance variables, branch multiplicity, and production atmosphere.
2. Prove or reject equivalence to the historical anchor-reset target; do not silently mix targets.
3. Enumerate or conservatively bound every physical shooting branch and unsupported region.
4. Run same-target exact and synthetic recovery under both exhaustion supports.
5. Compare matched seeds and budgets at the 18:39/19:41 bottleneck using evidence dispersion, row/root ESS, marginal CDFs, coverage, and branch diagnostics.
6. Integrate IGOGU only as an optional model after its prior, proposal density, normalizations, and evidence ledger are reconciled.
7. Address hydroacoustics only after the core estimator passes the preceding adequacy gates. Hydroacoustic A/E/F attribution and CL/DG predictions remain unfinished.
