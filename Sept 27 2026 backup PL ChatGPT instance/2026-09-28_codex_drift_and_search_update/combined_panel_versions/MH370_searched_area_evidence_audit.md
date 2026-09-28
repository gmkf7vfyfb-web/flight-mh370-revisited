# MH370 searched-area evidence audit

As of 11 August 2026

## Bottom line

The model should not use a single binary `searched = 1` mask. The open record supports a high-fidelity binary *coverage* mask only for the 2014–2017 ATSB-led Phase-2 data footprint, and even there detection probability varies with terrain, sonar quality, and known holidays. Ocean Infinity has not published its AUV swath polygons for either 2018 or 2025–2026, so those footprints must be marginalized.

The official current position is unambiguous on area but not geometry: the renewed contract targets 15,000 km²; about 7,571 km² was completed after signature; 7,428.54 km² remains; the agreement runs to 30 June 2027, with redeployment expected in the November 2026–April 2027 calm-season window. The best public reconstruction places most of that residual in the proposed inboard/northwest band, with some allowance for infill, data holidays, and contract-boundary differences. No official remaining polygon has been released.

## Cross-checks that matter

- **Bathymetry is not aircraft-search evidence.** The 710,000 km² Phase-1 bathymetric survey was collected primarily to map terrain and navigate near-bottom systems. The 2022 Geoscience Australia review states that the >30 m shipborne data cannot identify an aircraft debris field. Its aircraft-detection probability should be zero.
- **ATSB high-resolution footprint.** The official public Phase-2 tile alpha mask sums to **120515 km²**, agreeing with the official “over 120,000 km²” statement. The First Principles Review reported about 97% deep-tow coverage, about 99.9% coverage in the high-priority portion after AUV completion, and >95% overall debris-field detection confidence. It separately identified 606.7 km² of lower-probability-detection terrain and 119.29 km² of shadow/avoidance/equipment gaps in the 36–39.3°S indicative area.
- **The 2022 re-review does not validate OI2018 data.** Within the 17,000 km² review circle around 33.177°S, 95.3°E, GA reviewed 4,900 km² of ATSB high-resolution data. It found 72.79 km² of holidays/LPD (1.5% of reviewed area) and explicitly said it did not have Ocean Infinity's 2018 data.
- **OI2018 area totals are stage-dependent.** Ocean Infinity reported >112,000 km² of high-quality data at the 29 May contract conclusion. It continued for several days beyond the expired agreement in the northern/Haixun area. Its later data-donation release used 120,000 km² for the final campaign. That roughly 8,000 km² difference is not an exact unique-area estimate because both numbers are rounded and may differ in definitions.
- **OI2025 pre-contract work is real but not quantified.** Malaysia's 8 March 2026 release explicitly acknowledges additional survey activity in a broader area before the 25 March 2025 agreement. Community vessel tracks place activity on 23–28 February and 11–24 March, but the ship is only an AUV launch/recovery platform; its track is not the sonar footprint.
- **The cumulative OI number cannot be subtracted mechanically.** OI reported >140,000 km² mapped and 151 sea days cumulatively since 2018. Subtracting its 2018 120,000 km² figure suggests >20,000 km² of later mapping, greater than the 7,571 km² officially credited inside the signed contract. The difference can contain pre-contract work, infill, repeat passes, overlap, and different accounting definitions.

## Likely geography of the remaining OI area

The approximate March-2024 proposal reconstruction consists of two long bands around the 7th arc from roughly 33–36°S. Its outboard/southeast band is about 9768 km² in the traced outline; its inboard/northwest band is about 6072 km². Community tracking indicates that the 2025–2026 campaigns substantially traversed the outboard band, including pre-contract activity. The official residual of 7,428.54 km² is therefore most plausibly concentrated in the inboard/northwest band plus infill and boundary differences. This is an inference, not a published Ocean Infinity polygon.

This matters for the controlled-glide hypothesis: historical ATSB and OI2018 searches are predominantly close to the 7th arc, and the renewed proposal reaches only on the order of 45 NM from it. A controlled terminal displacement of 100 NM or more leaves large cross-arc regions with no high-resolution sonar exclusion. The official ±100 NM planning envelope is included as context and must not be mistaken for searched seabed.

## Recommended likelihood in the integrated estimator

For an impact state `x`, campaign `k`, coverage probability `c_k(x)`, and conditional detection probability `q_k(x)`, use

`P(no detection | x) = product_k [1 - c_k(x) q_k(x)]`.

For genuinely independent repeat passes, combine them as `1 - product_j(1 - q_kj)`. Do not subtract overlapping polygon areas. Recommended implementation:

1. Read the ATSB mask directly. Assign normal-quality cells a hierarchical `q` centred near 0.97 with at least 0.95–0.99 sensitivity; use the report's 0.50–0.90 range in LPD cells and approximately zero in true holidays.
2. Treat OI2018 and OI2025–2026 footprints as latent random fields. Constrain their total unique covered areas by official totals, and constrain their spatial support by official maps plus track-derived envelopes. Draw multiple plausible footprint realizations and marginalize them.
3. Give bathymetry-only cells `q=0` for aircraft-debris detection.
4. Assimilate the March–April 2014 surface search through the drift/debris observation model, not by applying the aircraft's impact coordinate to the daily surface polygons. If the drift likelihood already uses the absence of observed debris, do not add it again.
5. Do not apply the 7,428.54 km² future residual as negative evidence until it has actually been searched.

## Package contents

- `search_campaign_inventory.csv`: source-graded campaign ledger and model treatment.
- `source_register.csv`: primary and reconstruction sources with the claim each supports.
- `search_footprints.geojson`: official ATSB/Bluefin geometry, official arc/context, and clearly labelled approximate OI outlines.
- `atsb_phase2_coverage_mask_z8.png` and georeferencing JSON: model-ready official open footprint.
- `surface_search_2014_official.geojson`: official daily surface-search polygons, kept separate to prevent accidental seabed use.
- `oi_2025_2026_vessel_track_proxies.geojson`: community AIS evidence, expressly not AUV swaths.
- `stage1_search_overlap_diagnostic.csv`: geometry-only overlap with the existing Stage-1 impact sample; not a posterior update.

## Limitations

Exact Ocean Infinity 2018 and 2025–2026 AUV mission polygons, per-cell sonar quality, data holidays and audited probabilities of detection are not public. The 2024 proposal outlines and present remaining-area geography are therefore source-grade C. The evidence package preserves those uncertainties so the integrated estimator can marginalize them instead of turning inference into false precision.
