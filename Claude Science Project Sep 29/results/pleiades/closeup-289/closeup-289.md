# Close-up of "Both, after search", with Ocean Infinity, and comparison with the prior work

Revised ~22:45 UTC: figures restyled (light greyscale 50/90/99 % HDR with black contours of decreasing weight; heavier
search outlines); audit added at the end (Pete: why does the 50 % region reach so far NW, and is it bug-free?).

9 Oct 2026, Pléiades module. Script: `engine/hypotheses/pleiades/prepare/closeup_figure.py`. Numbers: `closeup-stats.csv`.
Conditional on H throughout. There is no Bayes factor and no P(H | data). Shape is not evidence for H.

## What changed since `branch-289/`

The earlier "after search" panels used only Phase 2 (q 0.945) and Bluefin-21 (q 0.9). Ocean Infinity was not applied
and no outlines were drawn. The searched-areas module was now re-run with its own grade-C OI layers. Two variants were run:
OI 2018 (q 0.9, coverage fraction 0.889) and OI 2018 plus the OI 2025-26 south-east band (q 0.9, coverage fraction 0.7808).
Each variant was run on all 12,799,968 reference-289 impacts and on every 0.05 deg grid centre. The evaluate roots are in
the gitignored `runs/pleiades/eval-oi/`. Point target, rho = 0.05, shared miss dependence (the module's default).
The north-west band is drawn but never used as negative evidence.

## Flight-conditioned (reference-289, 00:19 `none`, cause `other`)

| field | search | 90 % HDR km² | mean | NW band | outside past envelopes |
|---|---|---|---|---|---|
| P+C3 | Phase 2 + Bluefin-21 | 49,925 | 35.18 S 91.66 E | 5.2 % | 74.6 % |
| P+C4 | Phase 2 + Bluefin-21 | 57,306 | 35.20 S 91.54 E | 4.5 % | 76.4 % |
| P+C4 | + OI 2018 | 60,264 | 35.22 S 91.45 E | 5.1 % | 87.2 % |
| P+C4 | + OI 2018 + 2025-26 SE | 59,316 | 35.22 S 91.43 E | 5.2 % | 88.3 % |

- The grid-cell mode is 35.125 S, 91.325 E in every arm, 49 NM inside (NW of) the 7th arc. It sits on a broad plateau:
  L_P and L_C4 are within 5 % of their local maximum over about 0.15 deg. Read the HDR, not the star.
- The posterior mean is 38-42 NM inside the arc.
- Adding OI barely moves the 50 % core, which lies inboard of the OI 2018 outline. OI 2018 mainly removes the
  arc-hugging mass (outside past envelopes goes from 76 % to 87 %).
- Only about 5 % of the conditional PDF falls in the inferred remaining NW band. Under H the residual sits further
  inboard than that band.

## Like-for-like with the prior work (transport only, flat prior)

| quantity | prior work | this work (P+C4 product) | this work (P\|C4 50:50 pool) |
|---|---|---|---|
| 90 % area before search | 57,708 km² | 109,060 km² | 216,334 km² |
| 90 % area after search | 67,140 (dependent) / 63,282 (independent) | 111,730 (P2+B21) / 114,424 (+OI) | 202,821 / 201,119 |
| outside past envelopes, before | 42.2 % | 61.9 % | 69.8 % |
| outside past envelopes, after | 85.8 % / 88.2 % | 80.0 % / 91.0 % | 84.2 % / 93.2 % |
| mode, before | ~35.3 S 92.2 E (17 NM from arc) | 35.125 S 91.325 E (49 NM) | same cell |
| mode, after | ~34.9 S 91.9 E (41 NM) | 35.125 S 91.325 E (49 NM) | same cell |

Differences, in order of likely size:
1. **Transport spread.** Ours is the measured GDP-replay OU spread: σ ≈ 0.10-0.12 m/s, with T of 4-16 d. This roughly
   doubles the 90 % area relative to the prior work.
2. **Ocean models.** Ours are GLORYS12 + ERA5 and GlobCurrent daily + ERA5, at equal weight (the GlobCurrent label is P4,
   provisional). The prior work used BRAN2016, OSCAR v2 and GLORYS12 + WAVERYS. The OSCAR comparison is pending ocean
   transport.
3. **Sensor combination.** Ours is the joint product, so both sets of sightings must come from the same debris field.
   The prior work's 50:50 pool is also computed here: its area is about twice the product's.
4. **COSMO pass.** Ours weights dawn-20 and dusk-21 Mar equally. The prior work used 21 March.
5. **Search treatment.** Ours uses shared undetectability (rho 0.05) with the searched-areas module's own layers. The
   prior work bracketed dependent and independent misses.
6. **Flight conditioning.** The close-up figure is weighted by the reference-289 posterior, which the prior work's
   residual-origin map was not. The flight posterior halves the 90 % area and pulls the mean about 35 NM toward the arc.

Both analyses agree on the main point: after the searches, most of the residual mass under H lies outside every
past envelope. Ours puts the mode about 50 NM inboard, west of 92 E. The prior work's mode moved from 17 NM to 41 NM
inboard after the search.

Provisional: the end-of-flight dive class (b) and the Boeing-calibrated glide; the OI layers (grade C); the
GlobCurrent label (P4). The 00:19 option dominates the after-search result: under R600 raw, the search keeps only
0.35-0.39 of the conditional mass (`branch-289/branch-by-0019-option.csv`). These figures are for option `none`.

## Audit (9 Oct ~22:45 UTC; `prepare/audit_closeup.py`, outputs in `audit/`)

**Which contour reaches NW.** In the flight-conditioned close-up the 50 % region is small: 4,698 km² (P+C4 +
OI), one ellipse around the grid-cell mode at 35.1 S 91.3 E. The line reaching 90 E / 34 S is the 90 % contour. In the
transport-only figure the 50 % region (29,086 km²) does extend NW to about 33 S 89.5 E.

**Did the debris "hardly move"?** No. Inside the flight-conditioned 50 % region the model drift to 23 March is
q10-q90 52-114 km (median 63 km); none of it moves less than 30 km. The model tracks end a median 31 km (q90 42 km) from a
rating-5 cluster. The core starts a median 61 km from the nearest rating-5 cluster, and the tracks carry it north toward the
  clusters. Example, GLORYS12 at zero windage: 91.3 E 35.1 S drifts to 91.17 E 34.45 S, next to the PHR_4 clusters.
Transport-only 50 % region: drift median 97 km; 0.9 % of the mass moves less than 30 km (`audit-drift.csv`).

**Why it differs from the prior work: the transport-error spread, not the ocean models.**
- The GDP replay (808 undrogued segments, 60 drifters, box 80-110 E 45-20 S, March-May starts, current + 1 % ERA5)
  gives 95-120 km rms per component at 15 d. The bootstrap 95 % range is 81-137 km. The OU kernel in `likelihood.rs`
  matches the replay to within about 5 % from 1 d to 15 d (and runs about 20 % low at 6-12 h) (`audit-spread-vs-gdp.csv`).
- The prior work's 5 NM/day random walk plus its 10 km kernel gives 27-37 km at 15 d. That is 3-4 times too narrow
  for this box and season.
- Put the prior work's spread (30 km), windages (0 / 1.25 / 3 %), 50:50 pool and 21 March pass onto **our** GLORYS12 +
  GlobCurrent tables. The result is a 90 % area of 57,436 km² (52,823-69,465 across 27-37 km) with mode 35.38 S
  92.38 E. The prior work published 57,708 km² and about 35.3 S 92.2 E. With the measured spread and nothing else
  changed: 233,802 km², mode 35.08 S 91.38 E (`audit-spread-swap.csv`, `spread-diagnostic.png`).
- So the compact SE core in the prior work comes from its narrow spread. When the error is about 105 km per
  component and the drift about 60-120 km, origins NW of the objects stay compatible.

**Independent code checks (not the Rust path):**
1. A python RK4 on the raw daily fields + c·ERA5 reproduces the release tables: 60 random origin / windage / time
   cases per model, median 0.007 km, max 0.073 km (GLORYS12) and 0.019 km (GlobCurrent) (`audit-integrator.csv`).
2. A python evaluation of the likelihood formula reproduces `likelihood-surface.f32` and `cosmo-surface.f32` at 300
   random grid points each: max |Δ ln L| 8e-5 and 1e-4.
3. The joint P × C4 recomputed from the tables equals the branch map `L_P+C4` to a constant (sd of ln ratio 2e-5).
4. Rust unit tests (unchanged): normalisation, seed-freedom, the closed-form variance, exact interpolation.

**Limits on defensibility (open):**
1. **P / C error correlation.** The joint assumes the Pléiades and COSMO transport errors are independent. At
   ρ = 0.5 / 0.8 the flight-conditioned 90 % area grows from 59,316 to 75,821 / 82,106 km². The mean moves by
   ≤ 12 km, and the share outside past searches changes by ≤ 1 point (`audit-correlation.csv`). ρ has not been
   measured; it has been requested from ocean transport (`OCEAN_TRANSPORT.md` ~22:40).
2. **Replay sample.** The spread comes from 60 drifters with overlapping segments, from one box and one season.
3. **Proxy.** Undrogued drifters stand in for the debris. The replay error already contains a 1 % windage mismatch,
   so marginalising 0-5 % windage counts some of it twice. Fixing windage at 1 % shrinks the area by ≤ 13 %
   (21 March variant).
4. **Upstream sampler defect (new, ~22:20 UTC).** The independent filter audit
   (`results/filter-audit-architecture.md`, F1, High) found that tempered epochs re-simulate moves from another
   particle's pre-epoch history. reference-289 and eof-289-full are tempered (`temper_epochs` m1839-m0011, 16 stages,
   from no-exhaustion-prior), so every **flight-conditioned** panel here is provisional until core re-runs.
   The transport-only figure and the audit checks above do not depend on the sampler.
5. **Inputs.** OSCAR comparison pending. The flight posterior physics is provisional, and the 00:19 option dominates
   the after-search result. OI layers are grade C.
