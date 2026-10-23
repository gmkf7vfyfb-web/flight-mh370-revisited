
STL['run-j-joined-v2/J2241']='planned descent set J2241'
massrows=[f"| {STL[st]} | {r['P(impact in L)']:.4f} | {e2(r['P(impact point <=2 km, no settling)'])} | {e2(r['P(recorder detached rests <=2 km)'])} | {e2(r['P(recorder in aft fuselage rests <=2 km)'])} | {r.ratio_rec_to_impact:.2f} | {r.ratio_fus_to_impact:.2f} |" for st,r in mabs.iterrows()]
condrows=[f"| {STL[st]} | {e2(c0.loc[st,'P_rec_given_L'])} | {c0.loc[st,'ESS_rec_rows']:.1f} | {int(c0.loc[st,'distinct_parents_rec'])} | {e2(c2.loc[st,'P_rec_given_L'])} | {c2.loc[st,'ESS_rec_rows']:.1f} |" for st in c0.index]
NL='\n'
md=f"""# Kadri / Haixun conditional test — settling leg (pre-registration Q8)

18 Oct 2026. Ocean Settling Module. Prior: **run J** (end of flight `mh370-exchange/end-of-flight/run-j/`, four route strata, 74 seeds; plus `run-j-joined-v2/J0011` and `J2241`, 21 seeds each).
**00:19 option: none.** Rows carry the run J `weight` column only (no 00:19 option term, no C1/C2 log-on-cause mixture, no survival factor);
one sensitivity multiplies by exp(`loglik:r600/no-offset`). The headline key `D{{d}} total q=0.333 (C2 silent)` is **not** applied here:
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
{NL.join(siterows)}

Note for the beacon-physics leg: it used 4,577 m (GEBCO 2020 via OpenTopoData). The 150 m AusSeabed value is 4,589 m (12 m deeper; about +0.02 dB spreading).

Along the bearing strip (5 lines at -1, -0.5, 0, +0.5, +1 deg; 1 km spacing; `seabed_depth_bearing_strip.csv`):

| range minus R7 | centre min | centre median | centre max | all lines range | AusSeabed share | TID 40 share of GEBCO cells |
|---|---|---|---|---|---|---|
{NL.join(segrows)}

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
{NL.join(rowsD)}

By breakup family (run J rows in L):

| class | family | n | p50 | p90 | p99 |
|---|---|---|---|---|---|
{NL.join(famrows)}

Ocean sensitivity (impacts at the Haixun contact, 20,000 draws, common random numbers; p90 / p99 km). HYCOM GOFS 3.1 expt 53.X, 8 Mar 2014 00Z and 03Z,
24.0-27.0 S, 100.0-102.6 E, all 40 levels, in-situ temperature converted with TEOS-10; times after 03Z are held at 03Z, and the model bottom at Haixun is the
4,000 m level (hold-deepest below). Scalings and rotations of GLORYS12V1 are bounding sensitivities, not ocean products.

| ocean | {' | '.join(CLS_LABEL[c] for c in CLASSES)} |
|---|---|---|---|---|
{NL.join(ocrows)}

Term-off check at Haixun (GLORYS12V1; km):

| class | term off | p50 | p90 | p99 |
|---|---|---|---|---|
{NL.join(ttrows)}

The detached-recorder distance is set by carry (impact speed x carry time, up to about 0.3 km) and current (about 0.1 km); for the retained recorder the float
phase dominates (p90 3.1 to 0.6 km without it). The mean displacement at Haixun is to the north-west (GLORYS12V1: -0.11 km east, +0.14 km north for the
detached recorder), i.e. toward the arc crossing, but 0.2 km against a 19-22 km gap.

## 3. Inverse: surface impact points for a beacon within 2 km of the Haixun contact

(a) Region. Impact offset = contact - displacement + a point uniform in the 2 km disc, with displacements from the Haixun kernel (40,000 draws, impact conditions
from run J rows in L). Flat local prior over impact position.

| recorder | dist p50 | p90 | p99 | max (km) | in wide strip | in core strip | beyond 7th arc on bearing | min gap to sea-level arc (km) |
|---|---|---|---|---|---|---|---|---|
{NL.join(invrows)}

(b) Kadri impacts, forward (eq. 4, sea-level arc 18,400 us m0019a, c = 1.48 km/s, v ~ U(0, 250) m/s, bearing sd 0.5 deg; 40,000 draws per branch):

| branch | recorder / part | impact min dist to Haixun (km) | rest min dist (km) | rest within 2 km | rest depth p05 / p50 / p95 (m) |
|---|---|---|---|---|---|
{NL.join(kfrows)}

With 0 of 40,000, P(recorder within 2 km of Haixun | H_K, central geometry) < 7.5e-5 (95 % upper bound, 3/n). Rest points of Kadri impacts are 99 % on GEBCO cells
(TID 40 94-95 %), so the depths there are gravity-predicted.

(c) Sensitivity of the locus to the 00:19:29 geometry (BTO noise N(0, 63 us) and altitude U(0, 40,000 ft) at the arc; linearised R7 shifts from kadri_geom_output.txt):

| branch | recorder | impact min dist (km) | rest min dist (km) | rest within 2 km |
|---|---|---|---|---|
{NL.join(snrows)}

The joint event 'Kadri impact and Haixun beacon' is reached only in the tail of the arc geometry (about 1e-4 of draws), and settling does not change that
(rest and impact fractions agree within Monte Carlo noise).

(d) Run J prior mass. Per stratum, the mean over seeds of the sum of the `weight` column (normalised by the seed's total weight over all rows) times the
per-row probability that the part rests within 2 km of the contact (50 settling draws per row within 4 km for the detached recorder; 8 per row within 20 km
for the retained recorder). **00:19 option: none (weight column only).**

| stratum | P(impact in L) | P(impact within 2 km) | P(detached recorder rests within 2 km) | P(retained recorder rests within 2 km) | ratio detached / impact | ratio retained / impact |
|---|---|---|---|---|---|---|
{NL.join(massrows)}

Conditional on L, with the effective sample size of the contributing rows (w0 = weight column; w2 = w0 x exp(loglik r600/no-offset), L-conditional only):

| stratum | P(rest within 2 km given L), w0 | ESS w0 | distinct parents | same, w2 | ESS w2 |
|---|---|---|---|---|---|
{NL.join(condrows)}

These prior-mass numbers rest on 5-60 effective rows per stratum (w0) and 1-3 (w2): **provisional, not assessed at the depth needed for a firm number**.
The ratio column is the settling contribution, and it is near one in every route stratum. The J2241 retained-recorder ratio (44) rests on 16 parents with
ESS 5 and is not interpretable.

## Likelihood terms

Settling is a transform and adds no likelihood. The only settling-derived factors are:
- **H_H:** P(recorder rests within 2 km | run J) / P(impact within 2 km | run J) = 0.98-1.10 (detached), 1.01-1.15 (retained), route strata; ln ratio 0.0 to +0.1. Treated as 1.
- **H_K and H_H jointly:** P(recorder rests within 2 km of Haixun | H_K^T or H_K^C, central geometry) < 7.5e-5 per branch; 2.2e-4 (T) and 7.5e-5 (C) for the
  detached recorder with BTO and altitude spread. This is a compatibility ratio, not a Bayes factor; it belongs to the composer's joint-hypothesis row.

## COVERAGE

- (a) Feasible set: any impact in L (strip and discs) with the 777-200ER impact conditions run J produces (horizontal speed 65-330 m/s, descent rate 1-310 m/s,
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
"""
os.makedirs('out',exist_ok=True); open('out/README.md','w').write(md); print(len(md))
