# Pléiades hypothesis against the found debris and the Australian non-recovery, core run J (waypoints stratum)

17 Oct 2026. General-profile session working to the Pléiades brief. No new transport: all inputs were already on the Mac.

**Labels (carry them):** conditional hypothesis H (the Pléiades / COSMO-SkyMed objects came from 9M-MRO); Australian
non-recovery term RECONSTRUCTED (post hoc), sensitivity, not headline, until Pete rules on the detection level; end-of-flight
physics provisional (run J label list applies); core run J split-half accepted as a pass by project ruling, 16 Oct 2026; drift bandwidth
50 km only; test 1 releases at the field position on 8 March (the drift nodes), not from the field on 23 March.

## What is measured

Both quantities are log likelihood ratios of the **drift data** (the identified finds and, where stated, the absence of finds on
Australian coasts) under H against the flight posterior without H. They are not Bayes factors for H on all data, and they give no
P(H | data); the prior on H is still swept. Positive values favour H.

- **Test 1, field hypothesis.** H_F: the field imaged on 23 March also held the smaller items that were found later.
  ln R = ln L_drift(field) - ln E_flight[L_drift]. L_drift(field) is the mean over the six rating-5 clusters (equal weights) of the
  drift likelihood, interpolated bilinearly in L from the run A rebuilt node surfaces (nodes 7-31 km from every cluster).
- **Test 2, shared impact point.** The imaged objects and the finds came from one impact point, and are independent given it.
  ln R = ln E[L_P L_D] + ln E[1] - ln E[L_P] - ln E[L_D] over the run J flight posterior, with the ocean model shared between the
  Pléiades and drift factors and marginalised once (equal prior). L_P: Pléiades headline surface (rho 0.25, Pléiades + all four
  COSMO-SkyMed contacts, GlobCurrent product-relative). This replaces composer pass 1 on run C (+0.31 / +0.17 with drift-only carry).

Flight posterior: end of flight's run J waypoints stratum, 24 seeds, two-factor cells "total q = 1/3 (C2 silent)", weights from
`option_table_0019.seed_terms` unchanged. Unscored drift rows carried at the seed's weighted mean (ruling of 15 Oct).
Uncertainty (± values): root sum of squares of a seed bootstrap (500 draws) and 200 transport-noise replicates (node ln L perturbed
per 1-degree band from the committed split-half columns, Australian adjustments perturbed by their split-half SD 0.50 nat at the
pilot nodes; numerator and denominator perturbed together). Transport noise dominates; the seed bootstrap SD is at most 0.08 for D0-D2 and reaches 0.24 for D4 (per-model rows), where the effective sample is small.

## Results, both ocean models (equal prior, marginalised jointly)

| 00:19 option | evidence | ln R, field (test 1) | ln R, shared impact point (test 2) |
|---|---|---|---|
| D0 Held Out | finds only | +0.78 ± 0.40 | +0.49 ± 0.32 |
| D0 Held Out | + Australia, option B (pre-registered) | +1.66 ± 0.27 | +0.86 ± 0.21 |
| D0 Held Out | + Australia, populated coasts only (reconstructed) | +1.52 ± 0.28 | +0.81 ± 0.23 |
| D1 R600 BTO Only | finds only | +0.85 ± 0.49 | +0.59 ± 0.45 |
| D1 R600 BTO Only | + Australia, option B (pre-registered) | +2.09 ± 0.33 | +1.24 ± 0.24 |
| D1 R600 BTO Only | + Australia, populated coasts only (reconstructed) | +1.96 ± 0.31 | +1.20 ± 0.24 |
| D2 R600 BTO + R600 BFO | finds only | +0.85 ± 0.47 | +0.59 ± 0.35 |
| D2 R600 BTO + R600 BFO | + Australia, option B (pre-registered) | +1.94 ± 0.34 | +1.10 ± 0.27 |
| D2 R600 BTO + R600 BFO | + Australia, populated coasts only (reconstructed) | +1.83 ± 0.29 | +1.07 ± 0.27 |
| D3 R600 BTO + both BFOs (Holland H2 data) | finds only | +0.85 ± 0.57 | +0.62 ± 0.55 |
| D3 R600 BTO + both BFOs (Holland H2 data) | + Australia, option B (pre-registered) | +2.09 ± 0.35 | +1.31 ± 0.29 |
| D3 R600 BTO + both BFOs (Holland H2 data) | + Australia, populated coasts only (reconstructed) | +1.95 ± 0.31 | +1.24 ± 0.27 |
| D4 both BFOs, Holland transient bias added (H1 data) | finds only | +0.86 ± 0.48 | +0.58 ± 0.45 |
| D4 both BFOs, Holland transient bias added (H1 data) | + Australia, option B (pre-registered) | +1.83 ± 0.38 | +1.00 ± 0.37 |
| D4 both BFOs, Holland transient bias added (H1 data) | + Australia, populated coasts only (reconstructed) | +1.76 ± 0.34 | +1.00 ± 0.32 |
| D5 R600 BTO + R600 BFO + R1200 BFO with offset | finds only | +0.86 ± 0.46 | +0.61 ± 0.47 |
| D5 R600 BTO + R600 BFO + R1200 BFO with offset | + Australia, option B (pre-registered) | +2.07 ± 0.34 | +1.27 ± 0.27 |
| D5 R600 BTO + R600 BFO + R1200 BFO with offset | + Australia, populated coasts only (reconstructed) | +1.96 ± 0.31 | +1.22 ± 0.28 |

Per ocean model, 00:19 Held Out:

| evidence | field, GLORYS12 | field, GlobCurrent | shared, GLORYS12 | shared, GlobCurrent |
|---|---|---|---|---|
| finds only | +0.88 ± 0.68 | +0.67 ± 0.34 | +0.51 ± 0.50 | +0.48 ± 0.31 |
| + Australia, option B (pre-registered) | +0.10 ± 0.53 | +2.10 ± 0.29 | +0.24 ± 0.38 | +1.21 ± 0.24 |
| + Australia, populated coasts only (reconstructed) | +0.53 ± 0.52 | +1.91 ± 0.30 | +0.32 ± 0.39 | +1.14 ± 0.26 |

Mean latitude, Held Out: flight posterior -36.72; with drift (finds only) -36.02; with drift + populated-coast term -32.27;
under H -35.44; under H with drift -35.41 (finds only) and -35.23 (populated-coast term).
Ocean model under the Pléiades evidence: P(GlobCurrent) = 0.45 (D0), 0.445 (D1).
Cluster weights by object count instead of equal: test 1, D0 = +0.90 / +1.68 / +1.63 (finds only / B / populated).

## Reading

1. **Finds alone are uninformative about H.** ln R is +0.78 (field) and +0.49 (shared point) for Held Out, with a transport-noise
   95 % interval that includes 0 in both. On the usual ln BF scale, below 1 is not worth more than a bare mention.
2. **With the Australian non-recovery term, both tests favour H modestly:** +1.5 to +2.1 (field) and +0.8 to +1.3 (shared point)
   across the six 00:19 options, 2.7 to 6.4 total standard deviations from zero. The Australian term carries the effect.
   The sign is the opposite of a first reading of the coast shares. A 35 S source does send debris to Western Australia, but the
   flight posterior, centred further south, sends more, so the absence of Australian finds penalises the flight posterior more than H.
3. **The support is for the latitude band, not for the field.** Among the 68 drift nodes at 34-36 S, 87-97 E, the field is at the 65th
   (finds only) and 72nd (populated coasts) percentile of drift likelihood. With the populated-coast term, drift alone moves the
   flight posterior to a mean of -32.27, north of the field. The drift data do not identify the Pléiades objects; they penalise the
   southern part of the flight posterior.
4. **GlobCurrent carries most of the Australian effect** (test 1 D0: +0.10 GLORYS12 against +2.10 GlobCurrent with option B), as on the
   drift side, where the two models differ by a factor of about 1.7.
5. **The 00:19 option changes little:** D1-D5 are 0.07-0.12 above D0 for finds only and 0.14-0.46 above it with the Australian term.

## Validation

- The linear node reduction reproduces the direct per-impact drift export: ln E[L_drift] within 0.0003 nat (D0, both models).
- It reproduces the published run J values (`aus160-both.json`, stand-in 17 Oct) within 0.005 nat for D0, D1 and D3, both models,
  options none / B / populated; the refitted law constants are equal (GLORYS12 k 5.475, c 0.388; GlobCurrent k 4.597, c 0.366).
- 0.1 % of rows (7,497 and 5,302 of 6.4 M, seed 1) differ in scored state from the export; the effect on the sums is below 0.001 nat.

## COVERAGE

- **(a) Feasible set:** H spans any impact point whose transport reaches the imaged positions; H_F asserts co-location on 23 March.
- **(b) Model's reach:** drift run A nodes, 30 NM grid, 40.7-22.2 S; three object classes and windage priors as run A (provisional);
  Australian term from 178 pilot nodes (every fourth), 15-160 E, carried to all nodes by inverse-distance weighting.
- **(c) Proposal coverage:** run J waypoints stratum only (24 seeds, 153.6 M rows); free, descent-climb and repro-radar NOT assessed at this
  depth. Pléiades surface outside-grid rows: 0. D3 and D4 use the waypoints stratum, not the both-burst supplementary set, so
  their effective sample size is low and these rows are indicative only; ESS per option not computed here.
- **Gaps:** test 1 uses 8 March releases at the field positions, not 23 March releases from the field (the drift snapshot run from
  the clusters gave coast shares within 1-2 points of a 35 S impact); test 2 omits the shared ocean realisation between the Pléiades
  and drift factors (the deferred correlated likelihood); the populated-coast term is reconstructed, not run.

## Files

`finds-test-runj.csv` (every option, Australian level and ocean model, with seed and noise SDs); `reduce_seed.py` (per-seed
reduction); this note (README.md). The aggregation (node-level Australian adjustments, bootstrap, noise replicates) ran in the session kernel and is not yet a committed script. Inputs: `mh370-exchange/end-of-flight/run-j/run-j-waypoints`, `core/run-j/run-j-waypoints/bto-bfo`,
`debris-drift/run-j/run-j-waypoints`, `debris-drift/runA-rebuilt`, `pleiades/run-i/surfaces/joint-surface-rho0.25-gcrel`; repo
`results/drift-runj-2026-10-17/australia-160E/` and `aus160-both.json`; end-of-flight scorer `smoke/option_table_0019.py` (branch
hypothesis/end-of-flight).
