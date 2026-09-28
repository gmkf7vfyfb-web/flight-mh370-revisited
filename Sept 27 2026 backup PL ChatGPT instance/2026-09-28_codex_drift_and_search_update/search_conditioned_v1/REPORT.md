# Search-conditioned residual imagery-origin PDF

Prepared 28 September 2026. This is an explicitly conditional sensitivity calculation, not a calibrated complete MH370 impact posterior. It updates the combined all-four possible-COSMO, 21 March scenario from the previous analysis. Pléiades is fixed at 23 March.

## Findings

The union of the published ATSB footprint and approximate past OI envelopes overlaps 57.8% of the original mass. It overlaps 86.9% of the mass in the original approximately 50% highest-density region. Overlap with the ATSB published mask alone is 42.0%; OI 2018 envelope 47.0%; recent southeast band 3.1%. These overlap, so do not add these percentages. OI envelope overlap is not verified sonar coverage.

The reference uncertainty-marginalized calculations shift the mean northwest from 35.13 S, 91.78 E to about 34.94 S, 91.05 E (dependent misses) or 34.93 S, 91.01 E (independent misses). The grid-cell mode moves from 35.27 S, 92.17 E to about 34.91 S, 91.91 E. The western and northern lobes become more important; a smaller southeastern lobe survives. Boundary peaks depend on the approximate footprints and should not be interpreted at fine positional precision.

| Scenario | P(no detection) within hypothesis | Mean S, E | 90% area km² | Mass outside past envelopes | Mass in possible next NW band |
|---|---:|---|---:|---:|---:|
| original | 1.000 | 35.13, 91.78 | 57,708 | 42.2% | 3.3% |
| ATSB_only | 0.603 | 34.98, 91.32 | 64,568 | 69.9% | 5.4% |
| marginal_dependent | 0.491 | 34.94, 91.05 | 67,140 | 85.8% | 6.7% |
| marginal_independent | 0.478 | 34.93, 91.01 | 63,282 | 88.2% | 6.8% |
| weak_dependent | 0.544 | 34.97, 91.19 | 67,483 | 77.6% | 6.0% |
| strong_dependent | 0.435 | 34.89, 90.87 | 58,308 | 96.9% | 7.5% |

The original density at its peak is reduced to approximately 11% of its former normalized value in the dependent reference treatment, or 3% in the independent treatment. These are point-density ratios after normalization, not probabilities of an aircraft being at one point. A reference residual places about half its mass west of 91 E, compared with about a quarter before conditioning. The possible northwest OI band contains only about 6.7-6.8% of reference residual mass; most surviving mass is not confined to that proposal.

## Likelihood and uncertainty model

For an origin x, let d_k(x)=c_k(x) q_k(x), where c is probability of actual search coverage and q is probability of detecting and recognizing relevant wreckage given coverage. The update is p_res(x) = p_base(x) E_theta[L(no detection | x,theta)] / Z. The likelihood is averaged BEFORE spatial normalization; it is not an equal average of already-normalized scenario posteriors. The fixed equal-model mixture is the pre-search density; this step conditions that pooled density.

- Dependent misses: L = 1 - max_k d_k. This corresponds to nested detection events and is the maximum joint miss probability compatible with the campaign marginals. Overlap gives no extra detection credit beyond the best campaign. It is a conservative dependence sensitivity, not a fitted correlation model.
- Independent misses: L = product_k(1-d_k). This assumes campaign detection events are conditionally independent given location and parameters. Shared terrain or recognizability can violate it.
- ATSB-only control: L = 1 - 0.945 times the published coverage mask.
- Future northwest band: contributes NO negative evidence. Its mass is only a geographic summary.
- Shipborne bathymetry: contributes NO negative evidence.

Uniform sensitivity distributions (chosen, not inferred from operational QA):

| Campaign | Coverage inside mapped envelope | Detection given coverage |
|---|---|---|
| ATSB Phase 2 | Published raster footprint; 0 outside | Uniform 0.90-0.99 |
| OI 2018 | Uniform 0.60-0.95; 0 outside approximate envelope | Uniform 0.85-0.99 |
| OI 2025-2026 southeast band | Uniform 0.50-0.95; 0 outside approximate band | Uniform 0.85-0.99 |

The weak and strong sensitivities use the lower and upper endpoints respectively, with dependent misses. OI pointwise coverage ranges allow incomplete coverage within an envelope; they do not enforce a known exact total, model geometrical errors outside the envelope, or reconstruct actual AUV swaths. The 2018 ratio of reported mapped area to reconstructed envelope is about 0.8, which motivates but does not calibrate the coverage range. ATSB q is a broad sensitivity around published high detection confidence; it is not a measured local q map. Additional low-detection patches could leave more central residual mass than these scenarios.

The raw survival normalizer Z is about 0.49 or 0.48 in the reference cases. It is a predictive non-detection probability WITHIN this transport/imagery/search model. It is not the probability that MH370 lies in the displayed region, nor a Bayes factor against background objects. The missing imagery false-detection denominator remains missing. The source support, kernel assumptions, selected detections, and unvalidated possible-COSMO attribution remain as before.

## Geometry and numerical verification

The ATSB footprint uses the recovered public Phase-2 tile-alpha mask, zoom 8: approximately 500 m pixels at these latitudes. The layer name contains 5 m, but the downloaded footprint at zoom 8 is much coarser and carries no per-cell sonar-quality classification. Known small holidays and low-quality areas are not individually resolved. The prior 5 NM grid is integrated using 20 x 20 subpoints per source cell, respecting half-cell boundaries; local coordinates are interpolated on the original curvilinear grid. Polygon holes are retained through the ATSB raster. OI bands use their recovered reconstructed polygons.

Parameter marginalization uses 8,192 scrambled Sobol samples, seed 3702026. Every output grid sums to one. Changing 10 x 10 to 20 x 20 subcell integration changes total variation by 0.0021 (dependent) and 0.0023 (independent). Doubling parameter samples from 4,096 changes TV by less than 3e-7. These numerical checks do not validate the observational assumptions.

Within-cell density is treated as uniform before applying search likelihood. The posterior is re-aggregated to the original 5 NM cells for plots and HPD areas. Reported masses for polygons use the joint subcell likelihood/membership calculation, not posterior cell mass times an unrelated area fraction. Origin is used as a proxy for seabed wreckage position; descent displacement and seabed redistribution are not separately modelled. No aircraft flight-range or fuel feasibility likelihood is applied to the western lobes.

## Public high-resolution data

Yes, the ATSB-led 2014-2017 Phase 2 raw and processed sonar collection is publicly catalogued. The geographical overlap computed above means about 42% of the starting conditional mass falls within its published data footprint, but this does not imply data exist for the whole map.

- [GA Phase 2 raw and processed data catalogue](https://ecat.ga.gov.au/geonetwork/srv/api/records/11759ecd-b6ea-4e98-95fd-b966cd5735b3?language=eng), DOI 10.4225/25/5b0cd2b84a2dc. Raw and processed data from the 2014-2017 towed/AUV surveys, under CC BY 4.0. Attribution: Governments of Australia, Malaysia and the People’s Republic of China, 2018.
- [AusSeabed Marine Data Portal](https://portal.ga.gov.au/persona/marine). Use MH370 Phase 2 layers and the database search tool to select data intersecting the area.
- [Official download guide](https://asbdatamanagement.atlassian.net/wiki/spaces/AMDPUG/pages/956268789/How%2Bto%2Bdownload%2Bdata). It documents spatial querying/downloading of the full Phase 2 collection held at NCI; some raster clipping jobs require email.
- [GA release explanation](https://www.ga.gov.au/scientific-topics/marine-and-coastal/showcase/mh370-data-release). Distinguishes bathymetric preparation from the underwater sonar search.
- [2022 high-resolution data re-review](https://www.atsb.gov.au/sites/default/files/2024-02/mh370-data-review-2022-final-report-v2.pdf). Describes 10 cm-1 m native search datasets and explains why >30 m shipborne bathymetry cannot identify an aircraft debris field. Its reviewed area was a different, limited circle, not this whole map.
- [OI 2018 data donation announcement](https://oceaninfinity.com/news/ocean-infinity-donates-120000-square-kilometres-of-data-for-missing-malaysian-airliner-to-gebco-seabed-2030-project/). Donation to GEBCO does not by itself establish public access to native-resolution target-search imagery. No equivalent public raw-sonar/quality-footprint download for OI 2018 or 2025-2026 was located in this check. The 2022 GA review explicitly did not have OI data.

Catalogue and documentation access were verified; individual bulk survey downloads and a new visual re-review of sonar were not performed. For the central lobe, start with about 34.5-36 S, 91-93.5 E; for the full figure use 32-38 S, 87.5-96 E. Actual downloadable coverage must be checked against the survey index.

## Reuse

Run `python analyze.py` with numpy, pandas, scipy, Pillow and matplotlib. All inputs needed for this residual calculation are bundled. `base_input.npz` contains the previously computed combined drift PDF; this script does not rerun transport. `cell_probabilities.csv.gz` includes coordinates, areas, all scenarios and footprint fractions. `residual_pdfs.npz` stores normalized cell masses. `coverage_pattern_fractions.npz` contains joint subcell membership fractions. `validation.json` records settings and checks. `summary.csv` and this report provide numerical interpretation. Divide cell masses by cell area to get densities.