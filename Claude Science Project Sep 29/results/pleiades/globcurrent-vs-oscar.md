# Copernicus-GlobCurrent against OSCAR v2 Final: what differs, and what it means for the `ocean-model` choice

Pléiades module, 9 Oct 2026, written for Pete's decision on how OSCAR enters. This is a comparison of the products'
documented construction. Neither product has been tested against the other here: OSCAR has not been fetched or replayed.

**Sources.**
- **[QUID-GC]** CMEMS-MOB-QUID-015-003, issue 2.0, 3 May 2024. Fetched from documentation.marine.copernicus.eu,
  sha256 `afa73f97c4d3ab8b1a02f9676a212692e0a6295a5ce174028bac14285a1cefd7`.
- **[OSCAR-UG]** OSCAR v2.0 user guide (ESR; Dohan 2021, doi:10.5067/OSCAR-25F20), the copy in the prior work's
  archive, sha256 `ffc6f6a2e5a0c16e3c9a268e466a32c16eef193e2719ccf689c51984f40d29e2`.
- **[OT-GDP]** Ocean transport's GDP replay.

## Side by side

| | Copernicus-GlobCurrent (MULTIOBS_GLO_PHY_MYNRT_015_003, MY, v202411) | OSCAR v2.0 Final |
|---|---|---|
| Producer | CLS, for the Copernicus Marine Service | Earth & Space Research, distributed by NASA PO.DAAC |
| **Geostrophic part** | Daily absolute geostrophic velocity from CMEMS SEALEVEL_GLO_PHY_L4_REP_OBSERVATIONS_008_047 (DUACS), 0.25°. A 100 km Bessel filter removes small-scale noise [QUID-GC p. 6] | Computed from the SSH gradient of the **same** DUACS delayed-time ADT product, 008_047 [OSCAR-UG pp. 6, 8–9]. The MDT is CNES-CLS18 [OSCAR-UG p. 11] |
| **Wind** | ERA5 hourly wind stress, with a coastal land-contamination correction [QUID-GC p. 7] | ERA5 10 m wind [OSCAR-UG p. 9] |
| **Wind-driven part** | **Empirical.** U_ek = β e^{iθ} τ at 0 m and 15 m. β and θ are fitted by least squares to drogued SVP drifters (1993–2020) and Argo surface displacements, as functions of latitude and mixed-layer depth (weekly ARMOR3D MLD) [QUID-GC pp. 7, 9–10] | **Simplified physical model:** quasi-steady linear flow in a mixed layer, with eddy viscosity a function of wind, H = 125 m. Its two parameters are regressed on a drifter climatology [OSCAR-UG pp. 8–9] |
| Other terms | Barotropic tide from FES2022, 12 constituents, in the hourly product [QUID-GC p. 8] | **Thermal-wind** shear from SST gradients (CMC SST) [OSCAR-UG pp. 8–9]. No tide |
| **Depth represented** | Surface (0 m), and 15 m | **Average over the top 30 m** [OSCAR-UG p. 4] |
| Resolution | 0.25°; hourly, daily and monthly | 0.25°; daily [OSCAR-UG p. 4] |
| Known weak spots | The equator; meridional accuracy is worse than zonal; the Ekman term is defaulted where drifters never sampled that MLD [QUID-GC pp. 5, 10] | The equator; "generally OSCAR currents are inaccurate within 100 km of the coast"; no local acceleration or non-linear terms [OSCAR-UG p. 11] |
| Data assimilation / dynamics | None; a diagnostic sum of components | None; a diagnostic model |

## Answers to the three questions

1. **Same source data? Largely, yes.**
   - Both take their geostrophic current from the same DUACS reprocessed altimetry product (008_047), and both
     take their wind from ERA5.
   - The geostrophic part dominates the eddy-rich open ocean of the search box. So the two products share most of
     their information, and most of their errors: altimeter-mapping smoothing, and gaps in the constellation in
     2014.
   - They differ in how they turn wind into current, in the depth they represent, and in their extras (tide
     against thermal wind). The QUID itself names OSCAR as an example of the same approach [QUID-GC p. 6].
2. **Same resolution? Nominally, yes.** Both are 0.25°, and both inherit the effective resolution of the
   altimetry, about 100 km or more for eddies. GlobCurrent is available hourly; OSCAR only as daily means.
3. **Would one be expected to be better, and why?** For floating debris, GlobCurrent should be the better
   representation, for three reasons:
   - **Depth.** GlobCurrent provides a 0 m current. OSCAR averages over the top 30 m, which damps the near-surface
     wind-driven shear that a floating object feels. In our system the windage coefficient would have to absorb
     the difference, so OSCAR and GlobCurrent would imply different windage posteriors from the same data.
   - **Calibration of the wind-driven part.** GlobCurrent's Ekman transfer is fitted directly to drifters, as a
     function of MLD and latitude. OSCAR's eddy-viscosity model has two global parameters regressed on a
     climatology.
   - **Evidence so far.** On ocean transport's GDP replay (search box, March–May, undrogued), GlobCurrent gave
     14.3 / 14.2 km 2-day RMS against GLORYS12's 21.2 / 19.6 km [OT-GDP]. OSCAR has not been replayed.

   Caveats:
   - That replay is not a fully independent test. GlobCurrent's Ekman parameters were fitted to SVP drifters from
     1993–2020, which overlaps the 2014–2017 GDP segments in the replay. OSCAR's parameters are also tuned to
     drifters.
   - OSCAR has one physical term GlobCurrent lacks (thermal wind). It matters most at strong SST fronts, and the
     subtropical front lies near the search area.

## What this implies for the choice

- **OSCAR is not an independent third model in the sense GLORYS12 is.** It is a second rendering of the same
  altimetry and wind. Giving it a full equal share would let the altimetry-plus-ERA5 family carry two-thirds of
  the weight. Ocean transport made the same point in its recommendation.
- **It is useful for two things:**
  - comparison with the prior work, which used OSCAR v2 Final as its "current-family control";
  - a measure of how much the wind-to-current step alone moves the answer, because geostrophy is held fixed
    between the two.
- **A cheap test would inform the weight before it is set.** Fetch OSCAR (about 0.6 GB for the drift period) and
  replay the same GDP segments through it, as was done for GlobCurrent. Then report:
  - its 2-day and 15-day errors;
  - the correlation between its errors and GlobCurrent's, segment by segment.

  A high correlation supports treating the two as one family: the comparison-arm or family-weight options. A low
  one would support a separate equal share.

— Pléiades module
