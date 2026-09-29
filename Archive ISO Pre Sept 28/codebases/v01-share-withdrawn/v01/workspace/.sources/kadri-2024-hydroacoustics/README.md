# Kadri hydroacoustic publication-trace analysis

Primary paper: Kadri (2024), SHA-256
`b4f8f37ad1577a0f4726e6acdbfeea295b89197c88fac4ab5546d80bd9eb9db4`.
The 2025 reference poster SHA-256 is
`97775dd669262dd97f052bdf30bff3a8b2da31b529d8b5248e8124d215a7d2af`.

This descriptive source bundle contains exact PDF-vector traces extracted from
Figure 9, explicitly conditional station-range geometry, an impact-to-SOFAR
Monte Carlo sensitivity, periodic-airgun controls, and a concise discussion
pack. It does not contain raw CTBTO channels.

Run with an environment providing NumPy, SciPy, Matplotlib and PyMuPDF:

```bash
python code/extract_figure_vectors.py
python code/conditional_geometry_and_filter.py
python code/filter_sensitivity.py
python code/impact_simulation.py
python code/simulated_waveforms.py
python code/event_pair_analysis.py
python code/aligned_detection_analysis.py
python code/oscar_boundary_audit.py
python code/two_station_correlation_scan.py
python code/publication_trace_score_overview.py
python code/candidate_overview.py
python code/candidate_context.py
python code/potential_signal_infographic.py
python code/make_briefing.py
python code/hydro_release_workflow.py
```

## v0.1 forward/reverse diagnostic release

The deterministic release entry point is
`outputs/release-v0.1/index.html`. It expands the common 5 NM seventh-arc grid
from 0–640 NM along arc and ±100 NM cross-arc into 5,289 source boxes. Each box
is evaluated against 32 explicitly unweighted impact/time/coupling templates:
169,248 box–scenario combinations and 338,496 station predictions for H01W and
H08S. It emits arrival envelopes, reduced-order pressure and signal proxies,
the existing complete publication-trace correlation controls, and reverse
geometry for four declared candidate constructions.

All outputs have `likelihood_evaluated=false` and `log_weight_increment=0`.
The release does not alter an estimator posterior. In particular, the
complete-search maxima remain non-significant: unfiltered energy correlation
`r=0.120`, scan-adjusted `p=1.000`; held-out-selected rank-8 correlation
`r=0.109`, scan-adjusted `p=0.964`. The broad two-station time pairs are
compatible with thousands of grid boxes, while the source-reported 57° and
306.18° single-station bearings do not intersect this southern 0–640 NM grid
under the declared 30-minute impact-time control. These are useful geometry
results, not event identities.

The generator writes SVG, PNG, PDF, HTML, CSV and JSON plus a deterministic
manifest and typed hash ledger. Both generation and the ledger fail closed if
the package contains Python caches, test caches, editor backups or temporary
files. Two consecutive regenerations are byte-identical.
Focused source tests run with:

```bash
.venv/bin/python -B .sources/kadri-2024-hydroacoustics/code/test_hydro_release.py
```

### Raw triad handoff for Kadri

`data/raw-triad-input-schema-v1.json` defines a three-channel CSV contract.
Start from the H01W/H08S examples, provide calibrated pascals (or explicit
positive pascal-per-count scalars), verified channel locations, applied
instrument-response identity, and clock-correction identity. Then run:

```bash
.venv/bin/python -B .sources/kadri-2024-hydroacoustics/code/raw_triad_adapter.py \
  metadata-H01W.json prepared-H01W
.venv/bin/python -B .sources/kadri-2024-hydroacoustics/code/raw_triad_adapter.py \
  metadata-H08S.json prepared-H08S
.venv/bin/python -B .sources/kadri-2024-hydroacoustics/code/raw_triad_search.py \
  prepared-H01W prepared-H08S \
  .sources/pleiades-bran2016-forward-inversion/outputs/model-averaged-impact-density.csv \
  raw-search-output
```

The raw baseline filters and robustly standardises each channel, combines
channel energy without phase cancellation, evaluates every unique source-grid
lag, and calibrates the maximum using station time slides. It deliberately
does not claim coherent bearing recovery: that requires verified array
geometry, channel clock corrections and blinded source injections. CTBTO vDEC
access is described at <https://www.ctbto.org/resources/for-researchers-experts/vdec>;
the current conditions are generally organization-based and prohibit raw-data
redistribution, which is why the adapter can be run where the data are held.

## Current results

- A publication-ready summary infographic now consolidates seven distinct
  candidate classes: the two selected Kadri Table 1 entries, both Figure 9
  rectangles, two exploratory CL–DG timing pairs and the 01:03:13 DG-only
  screen. It reports station arrival times, conditional impact times, nearest
  seventh-arc latitude and the HPD percentile of the independent archived
  integrated spatial PDF. Bearing-derived arc intersections and timing-derived
  source representatives are explicitly shown as alternative conditionings,
  not fused event locations.

- The impact experiment uses 1,000,000 deterministic draws per impact family
  and coupling prior (seed `3700054`). The impact draws use 174,369 kg, the
  actual 9M-MRO zero-fuel weight on the final loadsheet, as a fuel-exhaustion
  impact-mass surrogate—not as a measured mass at 00:19 UTC—and four
  vertical-speed families. The F-35 example centres only one surface-to-SOFAR
  coupling sensitivity prior at order `1e-4`; a log-uniform
  `1e-8`–`1e-2` control is reported alongside it. Under the centred prior,
  median peak-pressure proxies span 0.025–0.786 Pa at H01W and 0.014–0.439 Pa
  at H08S. These are not detection probabilities.
- Kadri's Figure 9 rectangle 1 and Table 1 caption identify an approximately
  00:52 UTC, 57° signal. Rectangle 2 and Table 1 identify the preferred
  00:54:30 UTC, 306.18° candidate. The p. 9 sentence appears to conflate the
  second signal's 306° bearing with the first signal's approximately 00:52
  timing. The two signals are now shown separately.
  The separately screened 00:47:01.7 UTC time remains panel-edge affected.
- An amplitude-adjusted Fourier surrogate control preserves each H01W panel's
  observed amplitude distribution and approximately preserves its power
  spectrum. The largest 00:47–00:50 feature is 00:49:41.15 UTC (score 4.83).
  Its maximum is unusual within that visually selected three-minute interval
  (exploratory window-maximum p = 0.035), but not after allowing a search
  anywhere in Figure 9c (panel-maximum p = 0.115). The 00:48:22.05 feature has
  panel-maximum p = 0.281; the smaller requested features and the late features
  have still larger scan-adjusted p-values. These are stationary
  publication-trace surrogate tests, not calibrated receiver false-alarm rates.
- Conditional two-panel alignments now shift H01W and H08S arrivals back to
  implied source time at 1.50 km/s for the independent integrated-PDF density
  mode, the BRAN2016 and OSCAR v2 Final Pléiades transport modes, and a declared
  50:50 BRAN–OSCAR model-average transport mode. Their central H08S-minus-H01W
  lags are respectively 16.37, 19.92, 18.01 and 19.81 minutes. The integrated
  PDF is a separate flight+BTO/BFO+terminal-flight+drift posterior and is not
  the BRAN–OSCAR model average; its shorter differential distance is why it
  shifts H08S later relative to H01W. The 1.43–1.57 km/s control changes the
  shifts by minutes. The transport modes are explicit model alternatives, not
  crash posteriors; horizontal visual coincidence is not an event association.
- Neither the 00:49:58 nor 00:53:31 Table 1 time exceeds the publication-panel
  q99 screen within ±2, ±5 or ±10 seconds. Their broad-bearing conditional H08S
  95% reception windows are 01:04:51–01:11:05 and 01:07:50–01:13:37 UTC.
- A common event catalogue now reports arrival time, source-reported bearing,
  publication-trace score and the 2.5th, median and 97.5th percentiles of implied
  impact time. Those intervals condition on the independent integrated spatial
  PDF and a uniform 1.43–1.57 km/s celerity; they are not event-association
  posteriors. The catalogue includes 00:39:23.7, 00:47:01.7, 00:49:58,
  00:52:00, 00:52:04.35, 00:53:31, 00:54:30, 01:03:13.15 and 01:12:49.5 UTC.
- Across the available H01W Figure 9 vectors, only 00:39:23.7 and 00:52:04.35
  exceed their panel's q99 local-energy screen. The screen is a within-panel
  ranking, not a calibrated false-alarm probability. At H08S, the q99 residual
  peaks after the held-out-control-selected rank-8 filter occur at 01:08:00.75
  and 01:12:49.5; both remain coincident with the periodic airgun train. The top
  residual peaks are generally within 0–0.3 seconds of observed airgun peaks.
- Uniformly resampled, median-centred publication traces have mean-removed RMS
  pressure of 0.211–0.226 Pa for H01W panels and 0.242 Pa for H08S panel d;
  airgun-dominated H08S panel e is 0.390 Pa. Raw plotted vertices give roughly
  0.28–0.31 Pa for panels a–d but are sampling-density dependent. These values
  describe already-filtered plotted traces, not raw CTBTO receiver noise.
- At H08S, the 01:03:13.15 UTC time is 0.174 seconds after a target-excluded
  periodic-shot prediction and 0.050 seconds after the observed envelope peak.
  The control-selected low-rank method moves its empirical residual rank from
  the 97.5th to the 94.1st percentile; defensible settings span approximately
  the 80.5th–99.2nd percentiles.
- At ±100/±150 ms, masks centred on the blind periodic prediction retain the
  screened time, whereas masks centred on observed shot peaks remove it. Both
  widths are below the plotted line's indicative ±0.51-second timing thickness,
  so the publication rendering cannot resolve this distinction.
- A stronger rank-20 H08S sensitivity removes 28.6% of median periodic
  control-pulse RMS in panel d and 26.5% in panel e, compared with 8.8% and
  12.1% at the primary rank-8 setting. In held-out-cycle Gaussian injections,
  median recovered amplitude falls from 96.8% to 84.8% in panel d and from
  94.2% to 76.1% in panel e. A ±1 s observed-centre pressure mask removes 20.2%
  of samples; dilating it to ±3 s so the four-second local-energy window cannot
  see a masked pulse excludes 59.5% of the score timeline. More aggressive
  airgun removal therefore has a large and quantified loss-of-signal cost.
- The visually near-coincident OSCAR source-time features are H01W at
  00:52:04.350 (implied source 00:29:43.911) and H08S at 01:10:00.500 (implied
  source 00:29:39.354), a 4.557-second offset at 1.50 km/s. This is worthy of
  raw-data follow-up, but it is not significant in the strongest test available
  from the publication traces. The H08S point is only 0.5 seconds inside Figure
  9e; the rank-20 residual is identical to the published pressure trace over the
  first four seconds, and a robust fit to 52 interior airgun centres predicts
  the preceding periodic centre at -0.078 seconds (95% bootstrap interval
  -0.213 to +0.055 seconds) relative to the panel boundary. The earlier display
  masked only centres visible inside the panel and therefore made this cropped
  member of the same periodic sequence look uniquely retained. With the cropped
  neighbouring cycles included in the mask and a fully supported one-sided
  1/2/4-second energy statistic, the OSCAR-compatible ten-second window is less
  extreme than 63% of 570 matched interior windows (empirical p = 0.632). A
  random phase of the fitted 9.974-second pulse train lies within the observed
  4.557-second offset 91.4% of the time. This cadence result does not identify
  the cropped waveform as an airgun shot; it establishes that the apparent H08S
  timing match is non-discriminating under the measured periodic-interference
  null. If the H01W peak is Figure 9 rectangle 1, its reported 57 degree bearing
  also differs by 153.45 degrees from the 263.55 degree direction expected from
  the OSCAR mode.
- A GPS-acquisition-style sensitivity now retains the publication-trace energy
  before any additional low-rank airgun suppression or masking. It evaluates
  all 5,289 source cells against 41 propagation offsets from -5 to +5 seconds
  in 0.25-second steps, producing 17,753 unique station-lag hypotheses. The
  highest response is represented by the exact OSCAR mode (34.9167°S,
  92.0472°E) with a -1.25-second correction: H01W 00:54:30.148 is paired with
  H08S 01:12:29.599. Its full-overlap energy correlation is only r = 0.120 and
  the pressure correlation is r = 0.008. All ten independent leading responses
  put H08S inside the fitted periodic mask, while their H01W arrivals cluster at
  the approximately 00:52 and 00:54:30 high-energy features. Every one of 250
  complete panel-wise IAAFT surrogate scans produces a larger maximum
  (scan-adjusted p = 1.000; null-maximum q95 = 0.230). Thus the visually
  attractive OSCAR representative is not an acquisition-significant match.
- Repeating the complete 5,289-cell, 41-offset scan after the control-selected
  rank-8 low-rank subtraction gives a smaller maximum energy correlation,
  r = 0.109. It is not unusual under 250 complete panel-wise IAAFT scans
  (scan-adjusted p = 0.964; null-maximum q95 = 0.160). All ten leading filtered
  alignments still place H08S within the fitted periodic-pulse mask. Filtering
  changes the ranking but does not expose a trials-corrected association.
- The raw H08S periodic population was also tested without subtracting the
  airgun train. Each fitted cycle was scored by its core-minus-local-shoulder
  pressure-squared exposure (Pa² s), which is a trace statistic rather than
  received acoustic energy. Panels d and e each contain 59 complete cycles.
  Only one panel-d cycle exceeds its Tukey upper fence; no panel-e cycle does.
  A full source-grid search pairing upper-tail H08S cycles with H01W local
  energy reaches Fisher score 18.121, but the complete marked-pulse permutation
  p-value is 0.948 and the H01W time-slide p-value is 1.000. Some high-tail
  pulses can therefore be geometrically aligned to H01W and the Pléiades grid,
  but no alignment is rare under the measured periodic-interference null.
- The separately noticed OSCAR-aligned H08S spike has implied source time
  00:34:28.210 and lies 0.156 seconds from a periodic centre. It is the
  third-largest of 59 pulse-centred H08S windows, so additional constructive
  overlap is possible but not identifiable from one publication trace. The
  strongest four-second aligned product occurs at 00:34:28.560, close to the
  H01W panel end. Fully supported trailing-window Pearson correlations ending
  at 00:34:29.510 range from r = 0.125 to 0.422 for 4–20-second choices; 8.0%
  to 46.4% of same-length control endpoints are at least as large. This is
  positive local similarity, but not rare after the post-hoc time/window choice.
- Pearson correlation of panel-wise standardised local-energy scores was
  scanned along the seventh arc at 5 NM spacing and across it to ±100 NM. The
  nominal rank-8 unmasked full-grid maximum is r = 0.109 at 470 NM along and
  +60 NM across the grid (38.17°S, 90.27°E). Changing the filter rank and
  periodic-pulse exclusion moves the central-celerity full-grid maximum between
  235 and 625 NM along the arc and −95 to +60 NM across it.
- The full-grid maximum is driven primarily by aligning H01W 00:54:29.848 with
  H08S 01:13:09.499, followed by H01W 00:49:41.449 with H08S 01:08:21.099.
  Both H08S counterparts remain embedded in residual periodic airgun structure.
  Conditional pairing of the nominal lag with the reported 306.18° bearing
  intersects at 24.55°S, 99.91°E; pairing it with the 234.67° bearing intersects
  at 45.85°S, 84.96°E. Kadri's separately source-reported 1,586 km seventh-arc
  control lies at 25.79°S, 101.38°E and implies a different 23.09-minute lag.
  These are bearing–lag constructions, not detections or unique source
  locations; the correlation field consists of range-difference contours.

For browser viewing, open `VIEWABLE-INDEX.md`; it embeds every plot and all five
briefing pages as PNG images. The optional vector master is
`outputs/kadri-discussion-briefing.pdf`.
Copy-ready paper prose and mathematics are in `paper-section.md` and
`paper-section.tex`. Passage-level support is recorded in
`data/citation-ledger.md` and `data/impact-simulation-citation-ledger.md`.
An accessible account of what the impact model does and does not simulate is in
`impact-simulation-lay-explainer.md`.
The staged design and public-data boundary for a higher-fidelity model are in
`next-generation-impact-model.md`.

Reproducible GeoJSON areas for historical-AIS retrieval are in
`data/spire-aois/`. They include the Huzzas/*Geo Caspian* operational polygon,
the official FL400 seventh-arc corridor at ±100 NM south of 20°S, and a tiled
version that respects Spire/Kpler's documented per-request area limit. Rebuild
them with `python3 code/build_spire_aois.py`.

## Integration status

Predictive only. The canonical hydroacoustic spoke can propagate a typed impact
state to station-specific arrival, coupled-energy, pressure-exposure and RMS
pressure intervals under named source, propagation, bathymetry/path and station
response families. It accepts no observed trace and cannot evaluate a
likelihood. Publication vectors cannot establish event identity, triad bearing,
cross-station coherence, receiver false-alarm statistics or detection
probability. Candidate associations remain clearly labelled source-reproduction
sensitivities. A likelihood requires a named observed-signal model calibrated on
raw channels, with selection and complete-search false-alarm correction.
