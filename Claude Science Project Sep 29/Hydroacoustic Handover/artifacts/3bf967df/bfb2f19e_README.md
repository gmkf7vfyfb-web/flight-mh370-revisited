# Searched areas for the Kadri bearing locality and Haixun 01 (pre-registration Q6)

18 Oct 2026, searched-areas leg of the Kadri / Haixun conditional test. Prior: **run J** (four strata, mixed by core P(family);
headline cells `D{d} total q=0.333 (C2 silent)`; run J split-half accepted as a pass by project ruling, 16 Oct 2026).
Every number below carries its 00:19 option (D0 to D5). The headline option is **D0 (00:19 data held out)**.
Pete's steer (18 Oct) applies: the **primary locality is the 306.18 deg bearing at its sea-level 7th-arc crossing (25.732 S 101.369 E) and the
run J rows that the pre-registered acoustic likelihood selects there**. Haixun 01 is a **sensitivity line only**.

## 1. Answers in brief

1. **Was the locality searched on the seabed by high-resolution sonar?** Partly. Only by **Ocean Infinity 2018**. Its inferred (grade C) footprint crosses the
   bearing from 47 km outside to 42 km inside the 7th arc. ATSB Phase 2 sonar ends at 32.7 S. Bluefin-21 covered about 21 S. Ocean Infinity 2025-26 is at 34-36 S.
   No high-resolution search reached the bearing more than about 42 km inside the arc. Kadri's impact geometry puts the impact 0-188 km (T) or 0-219 km (C)
   inside the arc. The 2018 swath covers that geometry only for a mean post-00:19:29 speed of at most about 49 m/s (T) or 42 m/s (C).
2. **Pete's "narrow +/-25 NM strip".** This was the 2018 Ocean Infinity northern extension, not Fugro. On 17 Apr 2018, Malaysia's 12th weekly
   Operational Search Update added a supplementary area to 26 S (grade B: official, cited but not read; reported by Wise 2018, grade C). Independent
   reports state that the arc was searched "as far north as 25S and at a width of at least +/-22 NM" (Iannello, June and Aug 2018, grade C). The
   community tracing ends at 24.73 S (grade C). **It did reach 25.7-26 S**, but only on grade-C evidence. No official Ocean Infinity polygon exists.
3. **Haixun 01 point (sensitivity).** It is inside the inferred 2018 footprint (coverage 1.0 over the 2 km disc; 28.5 km = 15.4 NM outside the arc, inside +/-22 NM).
   It was inside one 2014 surface-search box (13 Apr, D37). It is in the 2014-17 bathymetry (150 m) grid. It is not in the 30 m backscatter coverage.
4. **Bathymetry 2014-17 (Fugro Equator, GA-4421; Zhu Kezhen contribution not separately identified).** The 150 m grid edge is 0.4 km from the crossing.
   Along the bearing it covers only -73 to -64 km and -8.6 to -0.5 km from the arc. A single multibeam line about 7-9 km wide runs along the arc to 24.73 S.
   **Bathymetry excludes nothing.** It enters no likelihood.
5. **Is the data online?** GA/AusSeabed: Phase 1 bathymetry 150 m (pid ga/100315, CC BY 4.0) and 30 m backscatter (ga/83922); Phase 2 5 m sonar (2018 release, south of 32.7 S only).
   Ocean Infinity 2018: sonar imagery is not public. Ocean Infinity states that it donated 120,000 km2 of data to GEBCO Seabed 2030 (22 Jun 2018). A check of the
   **GEBCO_2026 type-identifier grid** (WMS `GEBCO_LATEST_TID`) shows **no measured cells** in the Ocean Infinity-only part of the tracing: black fraction
   0.137, the same as the transit-line background. The Phase 1 area gives 0.998. The crossing cell is TID 40 (predicted from gravity). So GEBCO **cannot**
   confirm or refute the northern tracing. The check is uninformative, not a negative finding.
6. **Surface search 2014.** No daily box (387 GA/AMSA polygons) contains the crossing or the bearing strip on any day. The nearest boxes are 2 Apr (12 % of the
   200 km disc) and 21-26 Apr. But floating debris from the crossing drifts west-south-west. The 28-30 Mar boxes (fair weather) and the 21-26 Apr boxes
   (poor weather) **would have held 14-44 % of it** (Fig. 2b). With the CSIRO POD treatment, the probability that no debris was seen is **0.44** for an impact at the
   crossing cell. It is 0.84 for the rest of run J.

## 2. Likelihood terms (reference cases), locality vs the rest of run J

The seabed reference is rho 0.05 with the BASE = ATSB Phase 2 (q 0.945) + Bluefin-21 (0.9) + Ocean Infinity 2018 (0.9 x 0.889) + Ocean Infinity 2025-26 (0.9 x 0.7808),
with **Ocean Infinity coverage inferred (grade C), included as best estimate**. It is scored at the impact point; run J has no settling resample yet.
The surface reference is the CSIRO POD (1.0 per box-day, 0.15 on poor days), windage 0.5 % on GlobCurrent 0 m (product-relative, as the drift module), and floor 0.
Complement = run J outside the bearing strip. +/- = one seed-bootstrap standard error (within strata, 300 draws); ranges = all sensitivity cases.
The surface range covers windage 0.5/1.2/2.5 %, POD csiro/field (0.5/0.1)/item (0.15/0.05) and floor 0/0.05/0.2. The seabed range covers rho 0-0.5 and the ATSB-only case.

| option | locality | ESS | P(no seabed find) H / rest | seabed ln ratio | seabed range | P(no surface sighting) H / rest | surface ln ratio | surface range | both searches |
|---|---|---|---|---|---|---|---|---|---|
| D0 | 00:52:03 (T) | 83 | 0.652 / 0.310 | +0.74 ± 0.04 | +0.25 to +1.05 | 0.435 / 0.838 | -0.66 ± 0.04 | -0.95 to -0.09 | +0.09 |
| D0 | 00:54:30 (C) | 19 (not converged) | 0.743 / 0.310 | +0.87 ± 0.10 | +0.31 to +1.05 | 0.478 / 0.838 | -0.56 ± 0.03 | -0.75 to -0.11 | +0.31 |
| D0 | bearing strip, prior only | 1749 | 0.448 / 0.310 | +0.37 ± 0.03 | +0.11 to +1.05 | 0.434 / 0.838 | -0.66 ± 0.01 | -1.06 to -0.09 | -0.29 |
| D1 | 00:52:03 (T) | 135 | 0.585 / 0.274 | +0.76 ± 0.06 | +0.23 to +1.19 | 0.465 / 0.835 | -0.59 ± 0.02 | -0.76 to -0.11 | +0.17 |
| D1 | 00:54:30 (C) | 17 (not converged) | 0.694 / 0.274 | +0.93 ± 0.11 | +0.31 to +1.19 | 0.481 / 0.835 | -0.55 ± 0.03 | -0.89 to -0.12 | +0.38 |
| D1 | bearing strip, prior only | 1806 | 0.395 / 0.274 | +0.37 ± 0.02 | +0.10 to +1.19 | 0.455 / 0.835 | -0.61 ± 0.01 | -1.01 to -0.09 | -0.24 |
| D2 | 00:52:03 (T) | 11 (not converged) | 0.624 / 0.211 | +1.09 ± 0.25 | +0.32 to +1.40 | 0.468 / 0.874 | -0.62 ± 0.05 | -0.90 to -0.13 | +0.46 |
| D2 | 00:54:30 (C) | 5 (not converged) | 0.414 / 0.211 | +0.68 ± 0.24 | +0.17 to +1.40 | 0.436 / 0.874 | -0.69 ± 0.07 | -0.98 to -0.11 | -0.02 |
| D2 | bearing strip, prior only | 172 | 0.410 / 0.211 | +0.67 ± 0.06 | +0.17 to +1.40 | 0.453 / 0.874 | -0.66 ± 0.02 | -1.03 to -0.10 | +0.01 |
| D3 | 00:52:03 (T) | 1 (not converged) | 0.257 / 0.150 | +0.54 ± 0.37 | +0.10 to +1.72 | 0.447 / 0.897 | -0.70 ± 0.12 | -0.84 to -0.05 | -0.16 |
| D3 | 00:54:30 (C) | 2 (not converged) | 0.274 / 0.150 | +0.60 ± 0.31 | +0.11 to +1.72 | 0.432 / 0.897 | -0.73 ± 0.09 | -1.46 to -0.11 | -0.13 |
| D3 | bearing strip, prior only | 22 (not converged) | 0.311 / 0.150 | +0.73 ± 0.07 | +0.14 to +1.72 | 0.430 / 0.897 | -0.74 ± 0.08 | -0.97 to -0.10 | -0.01 |
| D4 | 00:52:03 (T) | 15 (not converged) | 0.597 / 0.138 | +1.46 ± 0.22 | +0.37 to +1.83 | 0.482 / 0.902 | -0.63 ± 0.05 | -0.93 to -0.13 | +0.84 |
| D4 | 00:54:30 (C) | 4 (not converged) | 0.375 / 0.138 | +1.00 ± 0.26 | +0.21 to +1.79 | 0.498 / 0.902 | -0.59 ± 0.05 | -0.82 to -0.10 | +0.41 |
| D4 | bearing strip, prior only | 13 (not converged) | 0.282 / 0.138 | +0.71 ± 0.08 | +0.13 to +1.79 | 0.421 / 0.902 | -0.76 ± 0.05 | -1.11 to -0.09 | -0.05 |
| D5 | 00:52:03 (T) | 4 (not converged) | 0.937 / 0.144 | +1.88 ± 0.07 | +0.57 to +2.25 | 0.521 / 0.904 | -0.55 ± 0.02 | -1.27 to -0.11 | +1.33 |
| D5 | 00:54:30 (C) | 2 (not converged) | 0.314 / 0.144 | +0.78 ± 0.43 | +0.15 to +1.76 | 0.505 / 0.904 | -0.58 ± 0.10 | -0.97 to -0.10 | +0.20 |
| D5 | bearing strip, prior only | 46 | 0.302 / 0.144 | +0.75 ± 0.09 | +0.14 to +1.76 | 0.482 / 0.904 | -0.63 ± 0.02 | -1.01 to -0.11 | +0.12 |

**Haixun point (sensitivity only, beacon within 2 km of 25.975 S 101.461 E, seabed point; complement = all run J):**
seabed ln ratio D0 -0.26 (rho 0: -0.31; rho 0.5: -0.06; ATSB only: +1.05); surface ln ratio D0 -0.73 (range -1.53 to -0.10). D1 to D5 seabed: -0.13, +0.13, +0.47, +0.55, +0.51.
The sign of the seabed term changes with the 00:19 option because the complement's P(no find) falls from 0.31 (D0) to 0.14 (D4/D5).

Reading: the **seabed term favours the locality** (ln ratio about +0.7 to +0.9 at D0). The reason is that most of the run J mass lies on searched ground and
nothing was found, while much of the Kadri bearing inside the arc was never searched. The **surface term opposes it by a similar amount** (about -0.6).
Their sum for the acoustically selected rows at D0 is **+0.09 (T)** and **+0.31 (C, not converged)**. **The two searches together give no material
evidence for or against H_K.** The sign of that sum is not robust to the POD case or the windage.

## 3. What trajectories the evidence selects here (D0, acoustically weighted rows)

| | rows in strip (prior) | 00:52:03 (T) | 00:54:30 (C) |
|---|---|---|---|
| effective sample size | 1749 | 83 | 19 (not converged) |
| impact time, UTC min after 00:00 (5/50/95 %) | 20.5 / 30.9 / 45.6 | 32.6 / 34.1 / 35.1 | 34.6 / 37.2 / 37.9 |
| flame-out to impact, min | 2.7 / 13.5 / 28.3 | 14.8 / 16.5 / 18.2 | 16.8 / 19.4 / 20.9 |
| impact speed, m/s | 64 / 119 / 369 | 62 / 80 / 176 | 67 / 101 / 160 |
| flight-path angle at impact, deg | 2.5 / 4.8 / 49.7 | 2.6 / 4.1 / 17.0 | 1.6 / 3.5 / 8.9 |
| distance beyond the arc along the bearing, km (+ = inside) | -53 / -3 / +100 | -79 / +4 / +124 | -109 / -50 / +160 |
| family share A1 / A2 / B | 0.16 / 0.29 / 0.55 | 0.00 / 0.25 / 0.75 | 0.00 / 0.21 / 0.79 |
| mean inferred Ocean Infinity 2018 coverage | 0.73 | 0.46 | 0.34 |

The acoustic timing selects long, shallow glides of 15-20 min after flame-out. These are mostly family B; A1 is absent. Half of the selected impacts are
outside the 2018 swath. Kadri's own model puts the impact on the arc side of the bearing (inside). In run J, about half of the selected rows end outside the arc.

## 4. COVERAGE (three sets, gaps)

- **(a) Feasible set:** any 777-200ER end of flight from the 00:19 state, including glides of up to about 20 min after flame-out and rapid descents (Holland-type).
- **(b) Model's reach:** run J strata waypoints / free / repro-radar / descent-climb. They reach the strip in every family (A1, A2, B have mass in the strip; table above).
  Planned descents starting before 00:11 (run-j-joined-v2 J0011, J2241) were **not** included here: **GAP, declared** (not assessed at this depth).
- **(c) Proposal coverage:** strip ESS 1749 (D0), 1806 (D1), 172 (D2), 22 (D3), 13 (D4), 46 (D5). Acoustically weighted ESS: T 83 / 135 / 11 / 1 / 15 / 4; C 19 / 17 / 5 / 2 / 4 / 2.
  **Every acoustically weighted term other than D0/D1 T is unconverged** and is labelled so. D3/D4 use the production waypoints stratum, not the both-burst supplementary
  pass that the composer uses for its D3/D4 headline (8 seeds): **GAP** for D3/D4. Run J prior mass in the strip is 0.06-0.11 % of the total. Few independent paths reach
  north of 33 S (core run J prediction 5).
- **Parameter bounds:** seabed q from GA/ATSB (Phase 2 0.945), Bluefin 0.9, Ocean Infinity q 0.9 with coverage fractions 0.889 (112,000 / 126,009 km2) and 0.7808. Rho swept 0-0.5.
  Surface POD: AMSA daily values unpublished; CSIRO treatment (1.0 / 0.15), with 0.5 / 0.1 and 0.15 / 0.05 as bounds. Windage 0.5-2.5 %; K = 100 m2/s (not sourced; stated assumption).
- **Validation of the surface treatment:** the core-weighted L_surface by latitude (1.2 % windage) is 0.96 at 36-38 S, 0.27 at 32-34 S and 0.33 at 26-28 S. This agrees in
  shape with CSIRO Part I p.23 (north of 32 S "strongly contra-indicates", 34-38 S "highly likely to have escaped detection").

## 5. Caveats and composition rules

- **Do not multiply these terms onto the composer's "all evidence" products.** Those already contain the searched-areas factor. Under pre-registration section 4 they go with the
  run J **core** mass in L. The surface search enters once, here; the drift module's finds term does not contain it.
- The seabed term is scored at the impact point. There is no run J settling resample, and the ruling asks for settled positions. Settling displacements of a few km are small against the 89 km
  swath width along the bearing, but this is an open item.
- The Ocean Infinity 2018 northern footprint is grade C. If the 2018 search did not in fact reach 25.7 S, the seabed term for the locality rises to the ATSB-only value (+1.05 at D0).
- The drift is this leg's own (stated assumption), not the drift module's surfaces. GlobCurrent 0 m drift near 26 S is about 0.35 m/s westward in 8-18 Mar 2014 (wind 8.3 m/s from
  the south-east). Debris from the crossing is at about 26.9-27.0 S 95.4-95.8 E on 28 Mar and about 27.9 S 100.1 E on 13 Apr (median). The drift Monte Carlo SE per cell is 0.02 (256 parcels).
- The acoustic weights are this leg's evaluation of the pre-registered Q2 formula, to condition the search terms. The Bayes factor of the hydro evidence itself belongs to the Q2 leg.
- End-of-flight physics is not calibrated. Search geometry for the 2014 surface search is grade A, but it carries no POD, sweep width or tracks.

## 6. Sources (grade)

- GA/AMSA ArcGIS `Search_And_Rescue_Search_Area2014` FeatureServer/0, 387 polygons D11-D52 (A, geometry; no POD).
- Griffin, Oke & Jones 2016, CSIRO EP167888 Part I, p.23 (A); Griffin & Oke 2017, Part IV EP177204, pp.1-3 (A): POD treatment. ATSB 2017 *Operational Search* pp.23-35 (A, text extraction).
- GA coverage polygons: Phase 1 bathymetry 150 m (ga/100315) and 30 m backscatter (ga/83922), Fugro Equator, 2014-06-05 to 2017-02-07 (A); Phase 2 sonar 2018 releases (A).
- Ocean Infinity, 29 May 2018 (over 112,000 km2) and 22 Jun 2018 (120,000 km2 donated) (A, company statements; ledger A-9, A-10).
- Malaysia MOT *MH370 Operational Search Update* no. 12, 17 Apr 2018: supplementary area to 26 S (B: cited, not read; the MOT site returns 502 and the Internet Archive was offline).
- Wise J. 2018-04-18 jeffwise.net (C); Iannello V. 2018-02-16, 2018-06 and 2018-08-19 mh370.radiantphysics.com: planned +/-25 NM to 29 S; searched to 25 S at >= +/-22 NM (C).
- MH370-CAPTION search-areas tracing (C). GEBCO_2026 TID grid via wms.gebco.net, 18 Oct 2026 (A for what GEBCO contains).
- CMEMS GlobCurrent `cmems_obs-mob_glo_phy-cur_my_0.25deg_P1D-m` (v202411) and wind `cmems_obs-wind_glo_phy_my_l4_0.125deg_PT1H` (A, data products).
- The point-target non-detection likelihood follows Stone et al. 2014 (AF447) and Davey et al. 2016 ch. 11; it is not new (see the module ledger `results/seabed-search-references.md`).

## 7. Files

`reduce_kh.py` (per-seed reducer; 74 seeds, about 40-70 s each), `surface_drift.py` (drift + POD), and `pool_terms.py` (pooling; reproduces the tables) are in this folder. The
tables are `search-likelihood-terms-summary.csv`, `search-likelihood-terms-all-cases.csv`, `surface-search-days-locality.csv` and `locality-search-summary.json`. The figures
are fig1-3 (png, pdf). The per-seed reductions and drift cell files are on the exchange, not in git: `mh370-exchange/searched-areas/kadri-haixun-2026-10-18/` (SHA256SUMS).
