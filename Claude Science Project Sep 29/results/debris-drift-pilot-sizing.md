# Drift source grid: pilot sizing from the reference posterior

Ocean drift module, 9 October 2026 (night of 8-9 October). **Provisional**: the extent source is a
stand-in, not an impact posterior.

## What was measured

The node counts of the drift source grid (brief section 5) as built by
`engine/hypotheses/debris-drift/source_grid.rs` on branch `hypothesis/debris-drift` (commit
`00867ef`; unchanged at `bf82159`), from the extent source ruled on 8 October: `no-exhaustion-prior` at 00:19:37
(`results/no-exhaustion-prior-summary.json`, sha256 `394029b4...cacb9c`, `cases[0].map`, 1,022
non-empty 0.25 deg cells pooled from 7,000,000 particles; datasheet
`results/no-exhaustion-prior-datasheet.md`). Embedded in the module as
`data/reference-map-no-exhaustion-prior-m0019b.csv`. Produced by the test
`reference_extent_cell_counts`.

Method: cells are ranked by density per unit area and taken to the coverage level; the selected
cells are grouped by single linkage at 40 NM into the main band and islands; every node within the
margin of a selected cell is a release node of that cell's group. The 100 NM margin is a stand-in
for the descent reach until impact samples exist (Pleiades measured a glide bound of 103.4 NM).

| coverage | spacing NM | margin NM | main-band nodes | island nodes | main mass | main lat span of nodes |
|---|---|---|---|---|---|---|
| 0.50 | 10 | 100 | 582 | - | 0.515 | -39.67 to -35.17 |
| 0.90 | 10 | 100 | 1,115 | - | 0.904 | -40.17 to -33.33 |
| 0.95 | 10 | 100 | 1,388 | - | 0.951 | -40.67 to -32.67 |
| 0.98 | 10 | 100 | 1,681 | 1,166 | 0.967 | -40.67 to -31.67 |
| **0.99** | **10** | **100** | **1,709** | **1,390** | **0.971** | -40.67 to -31.17 |
| 0.99 | 5 | 100 | 6,839 | 5,568 | 0.971 | |
| 0.99 | 20 | 100 | 429 | 347 | 0.971 | |
| 0.99 | 10 | 50 | 920 | 719 | 0.971 | |
| 0.99 | 10 | 0 | 174 | 87 | 0.971 | -39.00 to -32.50 |
| 0.999 | 10 | 100 | 3,576 (merged) | - | 0.999 | -41.17 to -21.33 |

The 99% coverage cells span -38.9 to -24.6 deg; at 40 NM linkage they split into a main band
(-38.9 to -32.6 deg, mass 0.971) and a northern island (-31.9 to -24.6 deg, mass 0.020) across a gap
of about 45 NM. At 60 NM linkage, or at 99.9% coverage, the gap is bridged and there is one
component. **So "the island" is a property of the coverage level and the linkage distance, not of
the posterior alone**; both are declared parameters (`coverage`, `island_link_nm`).

## What it means for the pilot

- **Pilot (99%, 10 NM, main band, 10^4 per node): 1,709 nodes, 17.1 M trajectories** per (ocean
  model, environment realisation, object class) case, against 11 M in the brief's table (which
  assumed a +/-100 NM band about the arc line rather than a margin about the 2-D coverage region).
  With the island as a labelled sensitivity: +1,390 nodes, 31.0 M total.
- The 5 NM refinement is 4.0x the nodes (6,839 main band), as the inverse-square rule predicts.
- **The case multiplicity is the real cost driver**, not the grid: 3 object classes x 3 environment
  realisations x 2 ocean models would be 18 cases, 308 M trajectories at the pilot setting.
- Throughput of the provisional analytic stub, one thread: 1.1-1.9 x 10^7 particle-steps per
  second (two velocity evaluations each; 1.907 x 10^7 in the test run at `611d443`, corrected 9 Oct). This is **an upper bound for closed-form fields** and is
  not the field-evaluation throughput the pilot must measure; that comes from the shared transport
  with gridded fields.

## What the stub showed that the real pilot must watch

On the stub (uniform current, straight coast, nine synthetic finds, 100 particles per node), 1,225 to
1,402 of 1,709 nodes (depending on the random streams) were Monte Carlo unresolved: for at least one find, no simulated particle contributed.
They are flagged, never scored as zero. This is the rare-arrival problem of brief section 9 in its
structural form, and the reason the per-find minimum effective particle count is a reported quality
flag. The stub's dispersal is far narrower than 500 days of real ocean, so the fraction is not a
prediction - but the pilot's particle count must be set by the find with the lowest arrival
probability, not by the average.

**Measured since (9 Oct):** the real-field pilot ran at 1.72 x 10^6 particle-steps/s at 2 threads
(`results/debris-drift-pilot.md`), and the production sizing is in `results/debris-drift-production-sizing.md`.
