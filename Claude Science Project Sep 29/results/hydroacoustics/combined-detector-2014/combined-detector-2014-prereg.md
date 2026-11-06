# Combined weak-signal detector on the 8 March 2014 data held: critical review and pre-registration

Version 1.0, 6 Nov 2026. Written and committed before any 8 March 2014 arrival window is scored with this detector.

## A. Critical review of the method so far (errors found and how each is fixed)

| # | Problem found | Effect | Fix in this run |
|---|---|---|---|
| A1 | The Kadri check applied the dive impact window (00:19:38-00:29:44) as if it were general. | Overstated "timing rules out". | Two hypothesis families, each with its own impact window (B1). The search runs over the union; each result carries its impact time and family tag. |
| A2 | The synthetic dive used a corner frequency log-uniform 1-20 Hz and slope 2-4. That came from the loose acceptance class, not from physics. | Dive and ditching detection probabilities from the 5-6 Nov tests are not physics-based. | Injections use the project source model (26 Oct 2026): R1 corner 0.92-2.66 Hz, R2 0.35-2.11 Hz, R3 0.21-0.68 Hz (90 %), slope 2.65-3.5. Secondary sub-events (the main missing term for R3) are a declared sensitivity. The detector templates stay loose (they set what can be found; the physics sets P_D). |
| A3 | Synthetic range was drawn 1,500-4,500 km for every station. | No station-specific path. | Range from the real arc-station distance of each grid point. Path filter: deep-channel low cut 1-4 Hz (uniform), Thorp absorption, path tilt f^(+-0.5) (uniform). Real recorded earthquake waveforms remain the empirical anchor. |
| A4 | The combined detector needs 10 min around each window; IMOS records are 307 s. | Cannot run unchanged on IMOS. | IMOS version: noise spectrum and whitening from the rest of the same record (window +-15 s excluded), order-60 prediction filter, persistence reference from the rest of the record, band 8-60 Hz (8 Hz hardware high-pass), IMOS gain and sensitivity applied. Recalibrated (B4). |
| A5 | Detection levels were fixed false-alarm levels (5 %, 20 %). | Arbitrary cut-offs. | No station-level threshold. Every look gets a calibrated background probability. Hypotheses are ranked by a network statistic; significance comes from a time-slide null (B6). Weak candidates are reported with their probabilities. |
| A6 | Tail probabilities beyond the background data used a fitted Pareto tail. | Strict levels rest on extrapolation. | Primary: Pareto tail (as before). Sensitivity: floor at 1/(n+1). The network p-value from time slides does not need the tail. |
| A7 | The statement that single-station transients are common added nothing to the plan. | None. | Dropped. Single-station transients are the seeds of the confirmation test (B7). |
| A8 | The cross-arc range was +-50 NM. A piloted glide can end about 125 NM from the 00:19 position. | Non-dive impacts beyond 50 NM not covered. | Grid extended to +-150 NM where the bathymetry path screen can run; otherwise flagged (B3). |

## B. Pre-registered design

B1. Hypothesis families and impact windows. H1 high-energy dive: impact 00:19:38-00:29:44 (Boeing alternate-run fits, ruling 4 Nov 2026); cross-arc +-25 NM. H2 non-dive (shallow entry or ditching): impact from 00:19:38 to 00:55:00. The upper bound is set wide: the latest Boeing normal-configuration sea arrival is 00:43:07, and a piloted best glide from about 36,800 ft at 0.0034 NM/ft covers about 125 NM, which takes about 28-34 min at 220-270 kt after the 00:19:29 log-on. Cross-arc +-150 NM. Every result carries impact time, position and family, so a later ruling on the windows filters results and does not require a new run.

B2. Data and detector components per station.
- IMOS 3250, 3274, 3275, 3315, 3376 (raw, 307 s in every 15 min): all components (band energy, spectral shape change, impact spectral templates, successive-sample correlation with the impact pattern, envelope persistence) and the Fisher combination.
- Cape Leeuwin and Diego Garcia South (Kadri Fig. 9 envelopes): band energy and envelope persistence only (no spectrum, no waveform). Null: form-matched block bootstrap of the off-window trace (as validated 4 Nov 2026).
- Royer spectrogram readings and OHASISBIO picks: context only, not in the statistic (timing-only ruling; picks need six stations).

B3. Grid. Arc 20-41 S every 1 deg; cross-arc offsets -150 to +150 NM every 25 NM. Path class per station from the project path screen (clear / large attenuation / ridge partial / blocked). Blocked paths contribute no term. Impact time every 15 s within each family window.

B4. Calibration (step 1). IMOS null: background days 1-15 Mar 2014 for 3250, 3274, 3376 (14 days x 96 records each); 3315 and 3275 from their own 8 March records outside 00:15-02:00 (about 22 h), cross-checked with the site partner. Look = 2 min. Background probability per detector from the empirical distribution with Pareto tail; Fisher combination calibrated on the same looks. Injection: physics families R1, R2, R3 (A2) and real earthquake waveforms, at -20 to +30 dB; P_D reported per family and logger. Null check: exceedance at -20 dB must match nominal.

B5. Travel time. Speed 1.465-1.520 km/s (Royer-implied on 8 March 2014 at these stations, well-timed events), detour 0-2 %. Sensitivity: physics bounds 1.40-1.56 km/s, detour 0-5 %. Each station's look is the predicted arrival span for the hypothesis; the per-station statistic is the window maximum, with its probability calibrated for that window length.

B6. Network statistic and significance. For each hypothesis: F = -2 sum ln p_s over stations with data and an open path. Global significance: 1,000 time slides (each station shifted by an independent random offset of 20-120 min, wrapped within its own data) to give the null distribution of the maximum F over all hypotheses. Report the full ranked list with global p; no cut-off.

B7. Seeded confirmation tests. Seeds: all 19 Kadri Table 1 transients (bearing +-3 deg, both families), the reverse-screening candidates, the Portland 3275 burst at 01:07:39-43, and the best network cells of 3 Nov and 5 Nov. For each seed, the predicted look at every OTHER station is scored (independent data). Per-seed result: probabilities at each other station and their Fisher combination; Benjamini-Hochberg across seeds. No station is scored with the data that produced its seed.

B8. Known events. Pre-registered catalogue association (commit 264a9a4). Label every candidate; remove only at association probability >= 0.95 (airgun shots at Diego Garcia South: label only).

B9. Outputs. Per-station look tables with all detector probabilities; ranked hypothesis table (impact time, position, family, per-station p, F, global p); seeded test table; P_D curves per family and logger; charts with footnotes.

## C. What could still require a re-run, and what does not

Does not: a new ruling on impact windows or cross-arc width (results are tagged; filter only); a new source model (changes P_D and upper limits only; candidate probabilities are data-driven).
Could: an error in code or data handling (an independent review of code and results before reporting); a change of the speed model beyond the declared sensitivity; new data.
