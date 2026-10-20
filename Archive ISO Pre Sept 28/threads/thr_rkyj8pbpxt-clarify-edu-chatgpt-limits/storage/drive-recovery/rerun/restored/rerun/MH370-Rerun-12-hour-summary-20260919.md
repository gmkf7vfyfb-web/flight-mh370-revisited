# MH370 Rerun — 12-hour core-estimator summary

Frozen for publication at 2026-09-19 14:35 UTC. This is an estimator audit and development checkpoint, not a location estimate.

## Bottom line

The original runs reproduce, but their scientific output is not yet adequately calibrated for a location probability claim. The extreme 96–98% ancestry concentration belongs to the two difficult synthetic runs, not the six production runs (whose largest-root weights are 2.99–17.51%). The audit now identifies three interacting causes:

1. The 18:39 and 19:41 SATCOM observations are genuinely selective.
2. The historical forward proposal has poor overlap with the high-likelihood region and too few distinct candidate paths there.
3. Later resampling turns that finite-coverage problem into genealogical loss.

This is not explained by hard physical rejection at those contacts: none of 200 independently generated full-aircraft diagnostic histories lost support at 18:39 or 19:41. In 20-history batches the median 19:41 ESS was 1.16 and 8/10 batches gave one history over 90% of the weight. Pooling all 200 distinct histories reduced the maximum weight to 33.5% and raised ESS to 4.31, demonstrating material budget/proposal sensitivity.

## Better estimator developed so far

- A retained-parent joint 18:39–19:41 proposal is implemented in isolated Rust source. It keeps every incoming parent and generates K complete block continuations with exact `W_parent/K × P/Q × L18:39 × L19:41` weights. Synthetic exact controls show that the guided proposal at a 2,048-path budget materially improves CDF accuracy and parent ESS. K must augment, not replace, initial-parent diversity.
- The 18:22:12 radar boundary and 18:28:05.9 fuel anchor are now separated correctly. Fuel at radar is obtained by the path-dependent affine preimage of the anchor fuel; an exhaustion-time proposal uses the exact `|dF_anchor/dT|` Jacobian. The 00:15–00:17 window is an explicit conditional hypothesis and 00:15–00:19 is retained as sensitivity support.
- A continuous-state backward/endpoint recovery suite validates the endpoint/time bridge measure. Across 64 generated flights at matched 2,048-path budgets, median ESS increased from 7.2 (forward bootstrap) to 320 (uniform corrected endpoint) and 1,672 (support-preserving Gaussian guide). Median terminal-position CDF error fell from 0.312 to 0.0446 and 0.0187 respectively. Corrected bridge coverage was 89.1%, close to the exact 89–91% reference.

The endpoint is always a proposal, never a measured location. The exact prior/proposal ratio is retained, SATCOM observations are applied once, and the through-00:11 target does not import the 00:19 BTO/BFO.

## Reproducibility and dependencies

The portable checkpoint contains source snapshots, configs, seeds, raw and derived results, retained failures, environment records, manifests, hashes, and continuation instructions. Begin with `MH370-Rerun-START-HERE-12.md`.

Checkpoint-12 controls require Python 3.12, NumPy 2.3.5 and SciPy 1.17.0; plotting also requires Matplotlib. Deterministic seeds are 37012000–37012031 and 37013000–37013031. The three reproduction commands are recorded in `candidate-20260919T1331/environment.json`.

Full-aircraft execution requires the exact Rust 1.98.0 toolchain (commit `88d9e12ae178fab0fb5cc050a94da85685d449ea`), which remains unavailable in the current environment. The exact recovered aircraft inputs are:

- ERA5: 337,328,648 bytes, SHA-256 `73a14bf…89f4` (complete value recorded in the checkpoint manifest);
- MH370 IGRF grid: 12,497,900 bytes, SHA-256 `ad71fa…6ac1` (complete value recorded in the checkpoint manifest).

The smaller `fbedb8…33f` grid is an MH371 control and must not be substituted. The exact primary provenance of the configured 6.578 N, 96.340 E radar locus and its 2 NM / 2° uncertainty scales remains unresolved; these must remain explicit assumptions.

## Limits and next gate

No full-aircraft backward bridge has yet been executed, the new Rust estimator has not been compiled, and no calibrated posterior probability or solved location is claimed. Hydroacoustics remains excluded.

The next gate is: restore Rust 1.98.0; prove ordinary/K=1 equality; run retained-parent K=4 with the full incoming parent bank over multiple seeds and matched budgets; then integrate the validated endpoint mixture into a separate full-aircraft bridge and test synthetic recovery under both time windows before interpreting MH370 results.

## Published artifacts

- `MH370-Rerun-START-HERE-12.md` — entry point and reproduction commands.
- `MH370-Rerun-findings-12-20260919.md` — detailed checkpoint-12 result.
- `continuous-bridge-recovery.pdf` — supporting diagnostic figure.
- `continuous-bridge-recovery.json` — all 64 trial records.
- `environment.json` and `failed-attempt.json` — exact environment and retained failure.
- `CHECKPOINT-12-MANIFEST.json` — complete file inventory and hashes.
- `MH370-Rerun-checkpoint-12-20260919T133957Z.zip` — portable continuation bundle; 70,447,732 bytes; SHA-256 `2d72f0e7224cdcba5788056890fe533ef3c561d302ba7786a82aa4b94bf160bf`.
