# Close-up of "Both, after search", with Ocean Infinity, and comparison with the prior work

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
