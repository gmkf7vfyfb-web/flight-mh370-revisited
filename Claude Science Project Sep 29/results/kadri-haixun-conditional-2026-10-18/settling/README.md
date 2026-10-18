# Kadri / Haixun conditional test — settling leg (pre-registration Q8)

18 Oct 2026. Ocean Settling Module. Prior: **run J** (end of flight `mh370-exchange/end-of-flight/run-j/`, four route strata, 74 seeds; plus `run-j-joined-v2/J0011` (24 seeds) and `J2241` (22 seeds), all seeds with impacts32.npy present at 18 Oct 2026).
**00:19 option: none.** Rows carry the run J `weight` column only (no 00:19 option term, no C1/C2 log-on-cause mixture, no survival factor);
one sensitivity multiplies by exp(`loglik:r600/no-offset`). The headline key `D{d} total q=0.333 (C2 silent)` is **not** applied here:
settling is a transform and its outputs (displacements, inverse region, depth) are conditional on the impact, so the 00:19 option enters only the
prior-mass numbers in section 3, which are labelled. Times: `t_impact_s` is seconds after run.json `T0_unix_s` = 1394236800 (00:00:00 UTC 8 Mar 2014).
Settling physics **PROVISIONAL**: element table is an educated estimate (breakup.toml at hypothesis/settling 9330d4c), plus one recorder class declared here.
Run J convergence: accepted as a pass by project ruling, 16 Oct 2026.

## Answer in brief

1. **Seabed depth.** Haixun 01 first contact **4,589 m** (AusSeabed 150 m; GEBCO_2026 4,583 m, TID 11 multibeam); 4,558-4,619 m within 2 km.
   Second contact 2 / 3 km west: 4,578 / 4,573 m (AusSeabed). Bearing x 7th-arc crossing: **4,466 m** (GEBCO_2026 TID 40, gravity-predicted; the
   AusSeabed survey does not cover that cell). Beyond the arc along the bearing the strip is almost all GEBCO TID 40 (no AusSeabed): depth falls to
   about 3,750-3,900 m 50-100 km beyond the arc, then deepens to 5,400-5,700 m at 150-250 km.
2. **Seabed displacement** (GLORYS12V1 baseline, run J rows in L): a detached recorder rests **0.18 / 0.34 / 0.50 km** (p50/p90/p99) from the impact,
   engines 0.15 / 0.29 / 0.43 km, landing gear 0.15 / 0.30 / 0.44 km. A recorder that stays in its aft fuselage section moves 0.38 / 2.49 / 10.27 km,
   driven by the float phase of intact sections (intact family p99 13.9 km). Kadri branches T and C give the same distances within 0.06 km at p99 for dense classes.
   HYCOM GOFS 3.1 at the Haixun kernel raises the detached-recorder p90 from 0.36 to 0.46 km and the retained-recorder p99 from 11.7 to 12.9 km.
3. **Inverse.** A beacon on the seabed within 2 km of the Haixun contact needs a surface impact within **2.2 km (p99; 2.6 km max)** of the contact for a
   detached recorder, or within **11.6 km (p99)** for a recorder kept in a floating aft section. That region lies entirely inside the wide (1 deg) Kadri strip,
   and about half of it inside the core (0.5 deg) strip, because Haixun is 0.50 deg off the bearing. **It does not reach the Kadri eq. 4 impact locus**:
   the locus is on or beyond the 7th arc, at least 18.9 km away (sea-level arc, central BTO). No Kadri impact draw (0 of 40,000 per branch and class)
   puts a recorder within 2 km of Haixun. Joint H_K and H_H therefore need a BTO / altitude excursion, not a settling excursion (section 3c).
   Run J does reach the region: 1,084 run J rows lie within 2 km of the contact; settling changes the prior mass of 'recorder within 2 km'
   by a factor of 0.98-1.10 relative to the impact-point mass (route strata), so **settling adds no information to H_H**.

## 1. Seabed depth (AusSeabed 150 m inside coverage, GEBCO_2026 outside)

Provenance per cell: `source` = AusSeabed150 (GA ga/100315, MH370 Phase 1 150 m, CC BY 4.0) or GEBCO2026 (15 arc-second, doi 10.5285/4f68d5c7-45eb-f999-e063-7086abc036fa),
with the GEBCO TID code (11 = multibeam, 40 = predicted from satellite-derived gravity). Nearest-cell values. Over a 0.9 deg patch around Haixun the two grids
differ by +2.0 m mean, 10.9 m SD where both exist.

| Site | lat | lon | depth (m) | source | AusSeabed (m) | GEBCO_2026 (m) | within 2 km (m) |
|---|---|---|---|---|---|---|---|
| Haixun first contact (25.975 S 101.461 E) | -25.9750 | 101.4610 | 4589 | AusSeabed150 | 4589 | 4583 (TID 11) | 4558-4619 (median 4589); AusSeabed share 0.84 |
| Haixun second contact, 2 km west | -25.9750 | 101.4410 | 4578 | AusSeabed150 | 4578 | 4567 (TID 11) | 4552-4619 (median 4579); AusSeabed share 0.96 |
| Haixun second contact, 3 km west | -25.9750 | 101.4310 | 4573 | AusSeabed150 | 4573 | 4568 (TID 11) | 4545-4619 (median 4573); AusSeabed share 0.97 |
| Bearing x 7th arc (25.732 S 101.369 E) | -25.7320 | 101.3690 | 4466 | GEBCO2026 |  | 4466 (TID 40) | 4443-4494 (median 4467); AusSeabed share 0.15 |
| Kadri R7=1586 km point | -25.7640 | 101.4080 | 4526 | AusSeabed150 | 4526 | 4525 (TID 11) | 4492-4534 (median 4522); AusSeabed share 1.00 |

Note for the beacon-physics leg: it used 4,577 m (GEBCO 2020 via OpenTopoData). The 150 m AusSeabed value is 4,589 m (12 m deeper; about +0.02 dB spreading).

Along the bearing strip (5 lines at -1, -0.5, 0, +0.5, +1 deg; 1 km spacing; `seabed_depth_bearing_strip.csv`):

| range minus R7 | centre min | centre median | centre max | all lines range | AusSeabed share | TID 40 share of GEBCO cells |
|---|---|---|---|---|---|---|
| -60 to 0 km | 4470 | 4604 | 4805 | 4366-4840 | 0.41 | 0.93 |
| 0 to 50 km | 4127 | 4293 | 4466 | 3463-4606 | 0.14 | 0.98 |
| 50 to 100 km | 3764 | 3856 | 4171 | 2289-4532 | 0.00 | 1.00 |
| 100 to 150 km | 3753 | 4669 | 5733 | 2201-6048 | 0.00 | 0.92 |
| 150 to 200 km | 4544 | 5411 | 5678 | 4544-5827 | 0.00 | 0.74 |
| 200 to 250 km | 5466 | 5640 | 5682 | 5380-5760 | 0.00 | 0.78 |

## 2. Displacement on the seabed

Method: vectorised Python port (`settle_mc.py`) of `hypotheses/settling/physics.rs` (9330d4c): carry along the impact track (horizontal speed x carry time),
float phase for elements that do not sink at once (GLORYS12V1 top-level current + leeway x ERA5 10 m wind + diffusion K log-uniform 10-200 m2/s), descent in
50 m steps at terminal speed with TEOS-10 density from the GLORYS12V1 column (8 Mar 2014, crossing cell), current from the GLORYS12V1 daily column
(trilinear in lat/lon/depth, linear in time), glide as a heading random walk, banded uniform-offset ocean error once per draw
(0.10 m/s x [1.0, 0.5, 0.2, 0.3]), stop at first seabed contact (AusSeabed then GEBCO). Below the model bottom: hold deepest level (module baseline);
median extrapolated depth 180-340 m. Breakup family per row = run J `latent:debris_class`.

Recorder classes:
- **Detached recorder** (new, declared educated estimate): SSFDR/SSCVR chassis or crash-survivable memory unit alone; areal density 65-330 kg/m2 (log-uniform,
  smallest to largest face of a 1/2 ATR short box of 4-8 kg), material density 2,700-5,000 kg/m3, Cd 0.8-1.2, descent factor 1.0-1.3, glide ratio 0-0.3,
  glide memory 1-20 m, carry 0-1 s (0-3 s intact), sinks at once. Source grade C (general knowledge of the unit format), not checked against Honeywell data.
- **Recorder retained in the aft fuselage section**: rests with its host section (breakup.toml `fuselage-section` in that family: intact sections always float
  10 min-6 h first; broken 30 % float 1 min-1 h; fragmented 10 % float 1-30 min).

GLORYS12V1 baseline; distances in km; descent time = median minutes from release to seabed; floated = share with a float phase.

| class | impacts | p50 | p90 | p99 | descent (min) | floated |
|---|---|---|---|---|---|---|
| Recorder, detached (dense compact) | run J rows in L | 0.18 | 0.34 | 0.50 | 46 | 0.00 |
| Recorder, detached (dense compact) | Kadri T, 00:52:03 | 0.20 | 0.37 | 0.56 | 46 | 0.00 |
| Recorder, detached (dense compact) | Kadri C, 00:54:30 | 0.19 | 0.36 | 0.55 | 47 | 0.00 |
| Recorder, detached (dense compact) | planned descents before 00:11 (J0011) in L | 0.19 | 0.35 | 0.51 | 44 | 0.00 |
| Recorder retained in aft fuselage section | run J rows in L | 0.38 | 2.49 | 10.27 | 63 | 0.35 |
| Recorder retained in aft fuselage section | Kadri T, 00:52:03 | 0.42 | 2.59 | 10.12 | 63 | 0.35 |
| Recorder retained in aft fuselage section | Kadri C, 00:54:30 | 0.40 | 2.49 | 9.86 | 65 | 0.35 |
| Recorder retained in aft fuselage section | planned descents before 00:11 (J0011) in L | 0.36 | 1.31 | 8.68 | 66 | 0.25 |
| Engine | run J rows in L | 0.15 | 0.29 | 0.43 | 23 | 0.00 |
| Engine | Kadri T, 00:52:03 | 0.15 | 0.30 | 0.44 | 23 | 0.00 |
| Engine | Kadri C, 00:54:30 | 0.15 | 0.29 | 0.44 | 24 | 0.00 |
| Engine | planned descents before 00:11 (J0011) in L | 0.15 | 0.30 | 0.45 | 22 | 0.00 |
| Landing gear | run J rows in L | 0.15 | 0.30 | 0.44 | 26 | 0.00 |
| Landing gear | Kadri T, 00:52:03 | 0.16 | 0.30 | 0.46 | 26 | 0.00 |
| Landing gear | Kadri C, 00:54:30 | 0.15 | 0.30 | 0.46 | 27 | 0.00 |
| Landing gear | planned descents before 00:11 (J0011) in L | 0.16 | 0.31 | 0.45 | 25 | 0.00 |

By breakup family (run J rows in L):

| class | family | n | p50 | p90 | p99 |
|---|---|---|---|---|---|
| Recorder, detached (dense compact) | intact | 9612 | 0.20 | 0.37 | 0.54 |
| Recorder, detached (dense compact) | broken | 6222 | 0.16 | 0.29 | 0.42 |
| Recorder, detached (dense compact) | fragmented | 24166 | 0.18 | 0.34 | 0.49 |
| Recorder retained in aft fuselage section | intact | 9612 | 1.91 | 7.50 | 13.87 |
| Recorder retained in aft fuselage section | broken | 6222 | 0.29 | 0.82 | 2.22 |
| Recorder retained in aft fuselage section | fragmented | 24166 | 0.31 | 0.61 | 1.08 |

Ocean sensitivity (impacts at the Haixun contact, 20,000 draws, common random numbers; p90 / p99 km). HYCOM GOFS 3.1 expt 53.X, 8 Mar 2014 00Z and 03Z,
24.0-27.0 S, 100.0-102.6 E, all 40 levels, in-situ temperature converted with TEOS-10; times after 03Z are held at 03Z, and the model bottom at Haixun is the
4,000 m level (hold-deepest below). Scalings and rotations of GLORYS12V1 are bounding sensitivities, not ocean products.

| ocean | Recorder, detached (dense compact) | Recorder retained in aft fuselage section | Engine | Landing gear |
|---|---|---|---|---|
| GLORYS12V1 baseline | 0.36 / 0.51 | 3.09 / 11.65 | 0.30 / 0.44 | 0.31 / 0.46 |
| HYCOM GOFS 3.1 (53.X) | 0.46 / 0.62 | 3.46 / 12.90 | 0.33 / 0.48 | 0.34 / 0.50 |
| current x0.5 | 0.28 / 0.42 | 2.19 / 8.51 | 0.27 / 0.42 | 0.28 / 0.43 |
| current x1.5 | 0.46 / 0.63 | 4.09 / 15.07 | 0.33 / 0.47 | 0.34 / 0.49 |
| current x2 | 0.57 / 0.75 | 5.06 / 18.52 | 0.36 / 0.51 | 0.39 / 0.54 |
| current rotated +90 deg | 0.35 / 0.50 | 2.03 / 7.44 | 0.29 / 0.43 | 0.30 / 0.45 |
| current rotated 180 deg | 0.38 / 0.53 | 1.65 / 6.40 | 0.31 / 0.45 | 0.32 / 0.47 |

Term-off check at Haixun (GLORYS12V1; km):

| class | term off | p50 | p90 | p99 |
|---|---|---|---|---|
| Recorder, detached (dense compact) | none (all on) | 0.21 | 0.36 | 0.51 |
| Recorder, detached (dense compact) | carry | 0.19 | 0.30 | 0.41 |
| Recorder, detached (dense compact) | float | 0.21 | 0.36 | 0.51 |
| Recorder, detached (dense compact) | current | 0.12 | 0.26 | 0.37 |
| Recorder, detached (dense compact) | glide | 0.21 | 0.36 | 0.50 |
| Recorder, detached (dense compact) | ocean-error | 0.20 | 0.34 | 0.47 |
| Recorder, detached (dense compact) | diffusion | 0.21 | 0.36 | 0.51 |
| Recorder retained in aft fuselage section | none (all on) | 0.43 | 3.09 | 11.65 |
| Recorder retained in aft fuselage section | carry | 0.42 | 3.09 | 11.60 |
| Recorder retained in aft fuselage section | float | 0.34 | 0.63 | 1.04 |
| Recorder retained in aft fuselage section | current | 0.27 | 1.48 | 5.73 |
| Recorder retained in aft fuselage section | glide | 0.38 | 3.06 | 11.63 |
| Recorder retained in aft fuselage section | ocean-error | 0.41 | 3.09 | 11.15 |
| Recorder retained in aft fuselage section | diffusion | 0.43 | 2.97 | 11.53 |

The detached-recorder distance is set by carry (impact speed x carry time, up to about 0.3 km) and current (about 0.1 km); for the retained recorder the float
phase dominates (p90 3.1 to 0.6 km without it). The mean displacement at Haixun is to the north-west (GLORYS12V1: -0.11 km east, +0.14 km north for the
detached recorder), i.e. toward the arc crossing, but 0.2 km against a 19-22 km gap.

## 3. Inverse: surface impact points for a beacon within 2 km of the Haixun contact

(a) Region. Impact offset = contact - displacement + a point uniform in the 2 km disc, with displacements from the Haixun kernel (40,000 draws, impact conditions
from run J rows in L). Flat local prior over impact position.

| recorder | dist p50 | p90 | p99 | max (km) | in wide strip | in core strip | beyond 7th arc on bearing | min gap to sea-level arc (km) |
|---|---|---|---|---|---|---|---|---|
| Recorder, detached (dense compact) | 1.42 | 1.94 | 2.21 | 2.56 | 1.00 | 0.47 | 0 | 19.8 |
| Recorder retained in aft fuselage section | 1.56 | 3.49 | 11.61 | 19.90 | 1.00 | 0.50 | 0 | 18.9 |

(b) Kadri impacts, forward (eq. 4, sea-level arc 18,400 us m0019a, c = 1.48 km/s, v ~ U(0, 250) m/s, bearing sd 0.5 deg; 40,000 draws per branch):

| branch | recorder / part | impact min dist to Haixun (km) | rest min dist (km) | rest within 2 km | rest depth p05 / p50 / p95 (m) |
|---|---|---|---|---|---|
| T | Recorder, detached (dense compact) | 21.5 | 21.7 | 0 of 40000 | 3148 / 4327 / 5683 |
| T | Recorder retained in aft fuselage section | 21.5 | 21.7 | 0 of 40000 | 3127 / 4323 / 5682 |
| T | Engine | 21.5 | 21.6 | 0 of 40000 | 3149 / 4327 / 5684 |
| T | Landing gear | 21.5 | 21.6 | 0 of 40000 | 3149 / 4326 / 5685 |
| C | Recorder, detached (dense compact) | 21.7 | 21.8 | 0 of 40000 | 3268 / 4455 / 5704 |
| C | Recorder retained in aft fuselage section | 21.7 | 21.6 | 0 of 40000 | 3235 / 4458 / 5705 |
| C | Engine | 21.7 | 21.7 | 0 of 40000 | 3268 / 4456 / 5704 |
| C | Landing gear | 21.7 | 21.6 | 0 of 40000 | 3268 / 4455 / 5704 |

With 0 of 40,000, P(recorder within 2 km of Haixun | H_K, central geometry) < 7.5e-5 (95 % upper bound, 3/n). Rest points of Kadri impacts are 99 % on GEBCO cells
(TID 40 on 91-94 % of all rest points), so the depths there are gravity-predicted.

(c) Sensitivity of the locus to the 00:19:29 geometry (BTO noise N(0, 63 us) and altitude U(0, 40,000 ft) at the arc; linearised R7 shifts from kadri_geom_output.txt):

| branch | recorder | impact min dist (km) | rest min dist (km) | rest within 2 km |
|---|---|---|---|---|
| T | Recorder, detached (dense compact) | 1.39 | 1.42 | 9 of 40000 (2.2e-04) |
| T | Recorder retained in aft fuselage section | 1.39 | 1.19 | 6 of 40000 (1.5e-04) |
| C | Recorder, detached (dense compact) | 0.78 | 0.63 | 3 of 40000 (7.5e-05) |
| C | Recorder retained in aft fuselage section | 0.78 | 0.29 | 1 of 40000 (2.5e-05) |

The joint event 'Kadri impact and Haixun beacon' is reached only in the tail of the arc geometry (about 1e-4 of draws), and settling does not change that
(rest and impact fractions agree within Monte Carlo noise).

(d) Run J prior mass. Per stratum, the mean over seeds of the sum of the `weight` column (normalised by the seed's total weight over all rows) times the
per-row probability that the part rests within 2 km of the contact (50 settling draws per row within 4 km for the detached recorder; 8 per row within 20 km
for the retained recorder). **00:19 option: none (weight column only).**

| stratum | P(impact in L) | P(impact within 2 km) | P(detached recorder rests within 2 km) | P(retained recorder rests within 2 km) | ratio detached / impact | ratio retained / impact |
|---|---|---|---|---|---|---|
| planned descent before 00:11 (J0011) | 0.0039 | 1.3e-06 | 1.3e-06 | 1.4e-06 | 1.00 | 1.12 |
| planned descent set J2241 | 0.0005 | 5e-10 | 4.6e-10 | 2.2e-08 | 0.91 | 44.02 |
| descent-climb | 0.0041 | 3e-06 | 3.1e-06 | 3.1e-06 | 1.02 | 1.03 |
| free flight | 0.0084 | 2.4e-06 | 2.7e-06 | 2.8e-06 | 1.10 | 1.15 |
| radar-reproducing | 0.0070 | 2.7e-06 | 2.7e-06 | 2.7e-06 | 0.99 | 1.01 |
| waypoint routes | 0.0038 | 1.4e-06 | 1.3e-06 | 1.6e-06 | 0.98 | 1.13 |

Conditional on L, with the effective sample size of the contributing rows (w0 = weight column; w2 = w0 x exp(loglik r600/no-offset), L-conditional only):

| stratum | P(rest within 2 km given L), w0 | ESS w0 | distinct parents | same, w2 | ESS w2 |
|---|---|---|---|---|---|
| planned descent before 00:11 (J0011) | 0.00033 | 28.0 | 158 | 9.1e-05 | 2.5 |
| planned descent set J2241 | 9.2e-07 | 5.4 | 16 | 1.1e-25 | 1.0 |
| descent-climb | 0.00076 | 7.6 | 195 | 0.0011 | 3.3 |
| free flight | 0.00032 | 59.9 | 283 | 0.0014 | 2.2 |
| radar-reproducing | 0.00038 | 34.3 | 218 | 0.00042 | 2.5 |
| waypoint routes | 0.00036 | 48.4 | 376 | 0.0019 | 1.8 |

These prior-mass numbers rest on 5-60 effective rows per stratum (w0) and 1-3 (w2): **provisional, not assessed at the depth needed for a firm number**.
The ratio column is the settling contribution, and it is near one in every route stratum. The J2241 retained-recorder ratio (44) rests on 16 parents with
ESS 5 and is not interpretable.

## Likelihood terms

Settling is a transform and adds no likelihood. The only settling-derived factors are:
- **H_H:** P(recorder rests within 2 km | run J) / P(impact within 2 km | run J) = 0.98-1.10 (detached), 1.01-1.15 (retained), route strata; ln ratio -0.02 to +0.10 (detached), +0.01 to +0.14 (retained), i.e. within Monte Carlo noise of 0. Treated as 1.
- **H_K and H_H jointly:** P(recorder rests within 2 km of Haixun | H_K^T or H_K^C, central geometry) < 7.5e-5 per branch; 2.2e-4 (T) and 7.5e-5 (C) for the
  detached recorder with BTO and altitude spread. This is a compatibility ratio, not a Bayes factor; it belongs to the composer's joint-hypothesis row.

## COVERAGE

- (a) Feasible set: any impact in L (strip and discs) with the 777-200ER impact conditions run J produces (weighted p05-p95 per stratum: horizontal speed 65-331 m/s, descent rate 1-313 m/s,
  intact / broken / fragmented); recorders either detached or retained in their section. Sources: run J (end of flight), breakup.toml (educated estimates).
- (b) Model reach: settling reaches every impact in the 94-108 E, 32-19 S box (GLORYS12V1 subgrid); HYCOM case only 24.0-27.0 S, 100.0-102.6 E and 00Z-03Z 8 Mar
  (reach gap for HYCOM: used only for the Haixun kernel). No implosion-at-depth case (declared alternative, off). No sliding after first contact (module rule).
  Recorder detachment is not modelled as a probability: both modes are carried as separate labelled cases (gap G-S1, below).
- (c) Proposal coverage: 40,000 draws per class and case (ESS of the impact resample from L: waypoints 101,106, free 90,788, repro 56,312, descent-climb 32,417,
  J0011 64,673, J2241 2,059; weight column). Near Haixun (section 3d) the ESS is 5-60: the prior mass in the 2 km disc is a thin-tail quantity.
- Parameter bounds and sources: recorder class ranges (declared here, grade C); element table (breakup.toml, educated estimates); ocean-error magnitudes
  (module provisional); K 10-200 m2/s (declared stand-in for the shared provisional diffusivity prior, which was not read); speed of sound 1.48 km/s fixed
  for the Kadri locus (pre-registration).
- Gaps: **G-S1** recorder detachment probability per breakup family not modelled (both modes reported). **G-S2** HYCOM window 00Z-03Z only, small box.
  **G-S3** below-model-bottom extrapolation 180-340 m (hold deepest level). **G-S4** near-Haixun prior mass ESS 5-60.

## Deviations from the brief / pre-registration

- Python port of physics.rs run outside the engine (the Rust module was not rebuilt); same equations, own random numbers.
- 00:19 option weights (option_table_0019.seed_terms) not applied; weight column only, plus one loglik sensitivity. Labelled '00:19 option: none'.
- HYCOM sensitivity limited to the Haixun kernel, 2 times (00Z, 03Z), one box. The NCSS subset service did not respond; OPeNDAP was used.
- Kadri synthetic impacts: impact conditions resampled from run J rows in L, independent of the eq. 4 speed v.
- Density from one GLORYS12V1 column (crossing cell) for every element.

## Files

`settle_mc.py` (transform), `extract_L.py` (run J rows within 400 km of the crossing or Haixun), CSV tables, figures
`fig_settling_haixun_map.png`, `fig_settling_displacement.png`. Depth grids: `~/Downloads/mh370-ocean-data/ausseabed/grid/`, `gebco/grid/`.
GLORYS12V1 column: `glorys12/profile/grid_75-115E_45-10S/` (layout [time][lat][lon][var][depth]). ERA5: `era5/era5_u10_v10_3h_15-120E_50-0S_20140307-20141231`.
HYCOM: tds.hycom.org OPeNDAP `GLBv0.08/expt_53.X/data/2014`, indices time 519-520, lat 1162-1200, lon 3500-3532.
