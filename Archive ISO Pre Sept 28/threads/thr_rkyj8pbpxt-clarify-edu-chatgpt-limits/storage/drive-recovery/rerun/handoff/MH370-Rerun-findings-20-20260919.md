# MH370 Rerun checkpoint 20 — coupled prefix and release recovery

## What advanced

Implemented a stochastic aircraft-path prefix from the conditional 18:22:12
state to the 18:28:05.9 fuel anchor. Each production dynamics step receives the
current gross mass; its actual midpoint weather/Mach/altitude/bank/climb values
drive the feed-resolved fuel step. One event budget is retained throughout.
There is no anchor reset and no silent retry of rejected paths.

Eight seeded synthetic-atmosphere paths exercise random speed, altitude and
lateral renewal events. Their 481 total segments
reconcile backward and forward fuel to within
1.16e-10 kg. A deliberate +100 kg
post-generation anchor replacement fails the new mass-history guard.
These are construction controls, not posterior recovery or real-flight fits.

## Important source reconciliation

Production dynamics use mass-dependent stall, bank and turn limits. Thus the
affine fuel map at fixed path remains valid, but its retained-fraction derivative
is not generally the total derivative when regenerating a path as fuel changes.
For A(m)=r(m)m+c(m), dA/dm=r+m dr/dm+dc/dm. A shooting proposal needs the total
derivative and branch/support accounting, or an explicit joint path-density
derivation. No such weight is emitted by this experimental API.

A new exactly solvable nonlinear bookkeeping control demonstrates the issue:
the correct density integrates to 1.000000000000;
using the frozen-path partial integrates to
0.959946081263. A frozen inverse after
a +100 kg anchor change misses replay by
4.174530 kg.
Those numbers describe a mathematical test, not MH370 error estimates.

## Release checks and repairs

Full Rust workspace: 526 passed, 5 ignored, zero failures after
recovery/repair. New controls: six Rust tests and four independent Python tests.
The ignored tests are not counted as passed. Full-workspace unit tests include
existing acoustic code tests but NO acoustic observations enter the estimator.

The release audit recovered four exact original fixtures missing from the small
checkpoint package, restored the canonical weather/magnetic bytes, and repaired
a stale runner synthetic diagnostic initializer. A NaN-clock guard was also
added to the experimental source contract. All failed intermediate attempts are
retained; the baseline sampler/likelihood logic is unchanged.

## Still unfinished

No complete two-ended aircraft bridge, weighted endpoint proposal, full synthetic
posterior recovery, or new 18:39/19:41 physical bottleneck comparison has run.
The prefix uses a constant synthetic atmosphere and fixed diagnostic radar/fuel
state. It does not apply the broad estimator's thrust/operational screens.
Unit-test stability is not scientific calibration. Hydroacoustics remains queued.

IGOGU original and R600-conditioned artifacts remain separately preserved. They
are not inserted into the baseline or reused as independent evidence. See the
milestone folder's IGOGU START-HERE and exact recovery manifest.

## Reproduce

Restore core-recovery parts for the offline Rust toolchain, dependencies and large
environment inputs. In source, run `cargo test --offline --locked --workspace`.
Run `python3 test_coupled_derivative.py` beside source. The small checkpoint ZIP
contains source, fixtures, raw traces, failed/successful logs, scripts and hashes;
it requires the separately preserved environment/runtime for a full offline run.
Read checkpoint-20-continuation.json for the next commands and scientific gates.
