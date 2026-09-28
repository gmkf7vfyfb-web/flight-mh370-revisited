# MH370 conditional imagery-origin study

Prepared 28 September 2026. New calculations use recovered arrays and code. This is a conditional transport-compatibility analysis, not an unconditional aircraft impact posterior.

## What was recovered

The decisive source was the local download `/Users/pete/Downloads/MH370-review-research-03.zip`, under `project/.sources/pleiades-bran2016-forward-inversion/`. Its 74 members (92,661,130 uncompressed bytes) were copied into `recovered/` without altering the originals. `recovered/recovery_manifest.json` maps each recovered file to its archive member. The recovered input manifest is dated 27 August 2026; that is a manifest timestamp, not proof of when every earlier calculation was first performed.

The bundle includes:

- Five decoded binary forcing subsets and their grid/time metadata: BRAN2016 currents, OSCAR v2 Final currents, GLORYS12 currents, WAVERYS Stokes drift, and NCEP-NCAR Reanalysis 1 winds. All five binary SHA-256 hashes match the recovered manifest.
- The twelve GA rating-5 object coordinates, source-grid configuration, FL400 reference arc, and land geometry.
- Forward integration, random-walk dispersion, source-grid, kernel, worker, aggregation and plotting code, plus tests.
- Three-seed primary scores, diffusion controls, normalized model-specific densities, the equal-model mixture, numerical summaries, maps in PDF/PNG/SVG, and a downstream relative-likelihood handoff.
- An RNZAF image-metadata context workbook and separate context plots. These are not used here as detections or non-detections.

The bundle references three PDFs that were not included in this archive: the CSIRO Part III report, GA Record 2017/13, and the OSCAR v2 guide. The scientific source ledger and metadata survive. Attempts to download the two official ATSB reports in this session timed out; their absence does not prevent the numerical rerun, because every required forcing array and observation coordinate table was recovered. The original data-invariant test suite therefore initially gave 14 passes and one failure caused by an absent reference PDF, not a mismatched ocean array. The separate transport-core tests pass. The extension records its own input and output validation.

## Distinguishing earlier project work

1. **Older reconstruction/diagnostic:** the August 14 project snapshot contains `run_pleiades_bran_diagnostic.py`, integrated method notes, CSV summaries and plots. That lineage used published CSIRO source anchors and assumed spatial kernels, together with reconstructed flight/terminal distributions. The older integrated note explicitly gives centers at 35.6 S/92.8 E, 34.7 S/92.6 E and 35.3 S/91.8 E, weights 0.50/0.25/0.25, and 25 km along/10 km across Gaussian widths. Those weights were project choices, not CSIRO probabilities. This was not the requested gridded three-model transport rerun. A later expanded-script import is missing from that older snapshot.
2. **Recovered forward inversion:** the August 2026 bundle is a real forward-particle computation using historical arrays for three transport families. It uses 5,289 source cells, three seeds and 192 trajectories per cell/seed/family. It evaluates endpoint kernels against the 12 GA locations. This is the appropriate computational provenance for the present extension.
3. **Downstream conditional flight analyses:** downloaded review archives also contain family-specific spatial-conditioning outputs and an exported likelihood surface. These are downstream applications, not independent drift observations. This task does not combine the imagery result with flight, acoustic, recovered-debris or seabed-search evidence.
4. **Independent prior audit:** `evidence/prior_independent_audit.md` reports numerical reproduction of the three-model study and a daily-wind knot sensitivity. Its reported total-variation changes were 0.051-0.077, with an OSCAR mode shift of 29.2 km. Those are inherited audit findings, not newly rerun sensitivities in this task.

The complete original `recovered/README.md`, `paper-section.md`, `outputs/summary.json`, and `likelihood-handoff.md` preserve the full prior method and findings. Recovered original results are kept separate from new outputs in `results/`.

## Iannello's date and the briefing slide

**Verified published finding:** [Victor Iannello's 23 July 2021 article](https://mh370.radiantphysics.com/2021/07/23/italian-satellite-may-have-detected-mh370-floating-debris/) explicitly uses **21 March 2014** for the three COSMO-SkyMed contacts and **23 March** for Pléiades. He matched detections to two tracks from CSIRO's BRAN2015 ensemble of 86,400 virtual drifters. The selected origins were within 3.5 NM of each other near 35.4 S, 92.8 E. That result is a published track-matching analysis, not this three-family PDF.

**User-supplied documentary evidence:** `evidence/french_briefing_slide.png` was recovered from the referenced conversation and visually checked. It explicitly labels the four coordinates as French satellite images sighted on 23 March 2014. It does not identify a spacecraft, SAR mode, acquisition clock time, or which date is acquisition versus reporting. The first three coordinates agree with Iannello's values to his four-decimal-place rounding. This supports a coordinate association, but does not establish that his values were derived from this slide or authenticate the underlying satellite product. The fourth point's sensor association remains hypothetical.

| ID | Latitude | Longitude | Original DMS (S, E) |
|---|---:|---:|---|
| F1 | -34.5741666667 | 91.8688888889 | 34 34 27; 91 52 08 |
| F2 | -34.9519444444 | 91.6833333333 | 34 57 07; 91 41 00 |
| F3 | -34.7469444444 | 92.1725000000 | 34 44 49; 92 10 21 |
| F4 | -35.3852777778 | 89.9538888889 | 35 23 07; 89 57 14 |

The eastern subset is F1-F3. The fourth location is about 191 km from its centroid. Pléiades inputs remain the 12 rating-5 objects in the recovered GA table, not all 70 candidate objects and not just the five-object morphology shortlist. [ATSB's GA report page](https://www.atsb.gov.au/summary-imagery-analyses-non-natural-objects-support-search-flight-mh370) confirms acquisition on 23 March 2014 and describes the coordinate tables. No image-object identity has been verified.

## Reproduction and extension

The scientific inverse question is solved by **forward transport from candidate origins**, not by reversing random-walk trajectories. For cell x and transport family m, the compatibility score for sensor set S is

`L(m,S,x) = mean_windage mean_seed mean_particle [ (1/N_S) sum_j K_sigma(endpoint, y_j) ]`.

`K_sigma` is an isotropic 10 km Gaussian kernel evaluated with great-circle distance. The recovered implementation omits the common Gaussian normalization constant; it cancels within each fixed-sigma normalized spatial PDF. This is an equal latent one-of-N association. It does not impose that all N detections came from a common debris field. Taking an average of subset averages under uniform subset selection has the same expectation; taking a product is a different scientific model.

The cell mass is `p_i = L_i A_i / sum_j(L_j A_j)`, using the recovered grid quadrature area A. The source prior is uniform per represented area. The FL400 arc defines coordinates and finite support only; it is not a new likelihood forcing the impact onto the arc.

### Preserved settings

- Surface-release epoch: 8 March 2014, 00:19 UTC. This is an assumed common epoch, not a conclusion about the true end-of-flight or impact time.
- Pléiades endpoint epoch: 23 March, 04:00 UTC. Possible COSMO-SkyMed Radar endpoints: either 21 or 23 March, each at **assumed** 04:00 UTC. The clock time is unverified for the Possible COSMO-SkyMed Radar contacts and is not marginalized over the day.
- Midpoint advection; three-hour steps, final partial step; bilinear spatial and linear temporal interpolation.
- BRAN2016 daily 0.1-degree currents at 2.5 m; OSCAR daily 0.25-degree upper-30-m current control; GLORYS12 daily 1/12-degree currents at approximately 0.494 m plus three-hourly 0.2-degree WAVERYS surface Stokes vectors.
- NCEP-NCAR Reanalysis 1 daily 10 m winds; response factors 0, 0.012, 0.03 with fixed equal weights. In GLORYS12/WAVERYS, windage is additional to explicit wave drift. This is a response envelope, not a calibrated model of the unknown objects.
- Independent isotropic random walk: two-dimensional RMS 5 NM over one day, increments scaled with square root of elapsed time.
- 64 trajectories per windage case per source cell; 192 per seed; seeds 37003801, 37003802, 37003803. Three-seed score averaging occurs before spatial normalization.
- Kernel controls: 5 and 20 km, and each windage response separately, saved without extra trajectory runs. Original zero/10 NM diffusion controls are retained in the recovered results; no new Possible COSMO-SkyMed Radar diffusion sweep is claimed.

### Source-support correction

The original support followed arc latitudes 32-39 S at 5 NM spacing, with offsets -100 to +100 NM at 5 NM spacing (5,289 cells). Pilot scores showed the fourth point's inferred origins crossed the western boundary. The extension therefore adds offsets down to -250 NM, preserving +100 NM eastward and the same along-arc support. The expanded grid has **9,159 cells**.

Original cells keep their original random-number cell index. Added cells use indices starting at 5,289. The old -100 NM edge becomes an interior quadrature cell and its half-width area is doubled; -250 and +100 NM are half-width boundary cells. This is essential when normalizing a merged grid. Original-support Pléiades scores are checked directly against the saved primary seed CSV before interpreting any expanded result. Expanded-support Pléiades results can differ from the original PDF even though their overlapping likelihood values reproduce.

Finite-support sensitivity remains a modelling choice. The report measures outer-band mass and probability outside the old strip; negligible new-edge mass is a numerical truncation diagnostic, not evidence excluding origins outside the computational domain. No flight-performance feasibility mask has been applied to the expanded western region.

### Model and sensor mixtures

Within each transport family, first normalize each sensor's conditional PDF over the same expanded support. The primary combined scenario is

`p_combined,m = 0.5 p_Pleiades,m + 0.5 p_possible_COSMO,m`.

The model mixture is `p_equal_models = (p_BRAN + p_OSCAR + p_GLORYS_WAVERYS)/3`. These are fixed pooling weights, not posterior model probabilities inferred from a marginal likelihood. The component models share oceanographic information and are not independent observations.

The alternative equal-object scenario pools **unnormalized** sensor scores: `(12 L_Pleiades + N_possible_COSMO L_possible_COSMO)/(12+N_possible_COSMO)`, then spatially normalizes within each model. This exposes both candidate-count weighting and normalization effects. It is not generally identical to a 12:N mixture of already normalized PDFs.

No product of Pléiades and Possible COSMO-SkyMed Radar likelihoods is presented as a calibrated common-source posterior. Such a joint model would need explicit assumptions about selected debris identities, detection dependence, shared transport errors and selection. A pooled density alone cannot establish that both sensors saw the same debris field.

## Inherited numerical limits

The exact recovered wind time-knot convention is retained for reproducibility. Its daily wind vectors are anchored at 00:00, while BRAN/OSCAR current means are anchored at 12:00. The field reader clamps times outside the supplied knot range: BRAN/OSCAR use their first field during the first 11 h 41 min; the 23 March wind endpoint has four hours after its last knot. The independently recovered audit found this convention has measurable effects. This extension does not silently fix or recalibrate it. The 21 versus 23 March comparison includes the inherited endpoint convention as part of the specified model.

Grid-cell modes are sensitive to Monte Carlo noise and multiple lobes. Report their precision as roughly the 5 NM grid scale and assess per-seed mode/mean differences, total variation, and broad HPD areas. Kernel width, response mixture, diffusion scale, finite support and sensor weighting are assumptions, not known properties of the detections.

Most importantly, without full acquisition footprints, negative imagery, target-selection rules and background contact rates, none of these outputs supplies `P(MH370 debris | detections)`, a Bayes factor for debris identity, or the probability that MH370 crashed inside a particular unconditional region.

## Reuse

Run `node code/run.mjs` and `node code/run_outer.mjs`; these use only local recovered arrays and resume completed task files. Then run `python code/summarize.py`, `python code/plot.py`, and `python code/report.py`. Node workers are numerical workers, not delegated AI agents. Plotting requires numpy, pandas, matplotlib, reportlab and pypdf.

`results/source_grid.csv` contains cell IDs, signed coordinates and quadrature areas. `conditional_pdfs.npz` and `probability_masses.csv.gz` contain normalized cell masses, not densities. Divide mass by cell area for density. `relative_likelihoods.csv.gz` contains unnormalized transport scores, suitable only as explicitly conditional proxies. Join by cell ID and do not extrapolate outside support. `runs/` retains per-cell, per-seed, per-model scores and all kernel/windage alternatives. The scripts, seed configuration, forcing arrays and checksums make the new calculation rerunnable without external data access.


## Sensor nationality and reported delivery chain — label revision

All new display labels use **Possible COSMO-SkyMed Radar**. This changes no coordinates, probabilities or weights. Historical wording and existing `french4`, `french_coordinates.json` and F1-F4 identifiers remain intact for traceability; recovered files are unchanged.

**COSMO-SkyMed is Italian.** [CNES](https://cnes.fr/en/projects/pleiades) describes it as the Italian radar component of the Franco-Italian ORFEO programme, alongside optical Pléiades. The [French Senate report on the bilateral agreement](https://www.senat.fr/rap/l02-443/l02-4430.html) explicitly describes French access to Italian radar imagery. France could therefore supply imagery originating from an Italian satellite. That is a supported possibility, not proof of the specific upstream delivery of these contacts.

The [Malaysian minister’s 24 March 2014 briefing, reproduced by Yahoo Newsroom](https://malaysia.news.yahoo.com/mh370-press-briefing-by-hishammuddin-hussein--24-march-2014--530pm-101214741.html), reports radar acquisition on **21 March**, receipt by Malaysia on the **evening of 22 March**, and relay to **RCC Australia on the morning of 23 March**. It separately reports camera acquisition on **23 March**, receipt on **24 March**, and relay to Australia. The statement calls the satellites French and does not name COSMO-SkyMed. Thus French supply followed by Malaysian relay to Australia is reported; the exact Italian-to-French agency chain and the connection of all four coordinates to that radar product remain unverified.

“French” on the slide may refer to the supplier rather than spacecraft nationality. This inference does not require confusion with Pléiades, but neither confusion nor acquisition/reporting-date ambiguity can be excluded. Synthetic-aperture radar does produce images from processed radar returns; these are not optical photographs. A list of interpreted target coordinates is a derived product. The briefing graphic alone does not establish whether the recipients received full radar imagery, extracts, coordinates, or a combination.
