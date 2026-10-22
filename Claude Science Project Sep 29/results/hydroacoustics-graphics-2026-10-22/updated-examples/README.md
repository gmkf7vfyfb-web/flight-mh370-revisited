# Updated example charts 1–10 (graphics track "updated-examples", 22 Oct 2026)

Hydroacoustic Module, graphics track. PREDICTIVE, NOT CALIBRATED: caveats C1 (propagation slope misfit +10.4 / +7.4 dB per
octave at H01W / H08S; after EW0112 a source-term caveat; air9 verdict NOT EXPLAINED, gap G23) and C2 (coupling efficiency
not calibrated; F-35A anchor η = 2.1e-4 **provisional — from Brown 2026's quote of Metz 2023; re-derivation from Metz
pending**). No detection is claimed. Smoke runs are not used. Digitised data are labelled as digitised.

| # | file | what changed against the 21 Oct example |
|---|---|---|
| 1 | chart01-noise-vs-levels-H01W | full weighted distribution (violin, 2 M run J draws, D0′ p 0.5) per third octave at η 1e-3 / 2.1e-4 / 1e-5, noise median + 10–90 %, matched-filter and baseline detectable shares in the panel (23.0 % / 2.0 %, 8.4 % / 0 %, 0 / 0); 2014 Kadri-noise line 40.4 % / 19.1 % |
| 2 | chart02-noise-vs-levels-H08S | same; 12.5 % / 0, < 0.1 % / 0, 0 / 0 |
| 1–2 companions | chart01-02-companion-noise-vs-levels-{H08N,3315,3376,3274,3275,3250,overview} | IMOS loggers on the corrected IMOS TL table (imos_tl_ram_arc.csv): matched-filter share at η 1e-3: 3315 29.9 → 2.4 %, 3376 15.4 → 8.6 %, 3275 25.4 → 5.8 %, 3274 < 0.1 % both |
| 3 | chart03-loudness-maps | four options (D0′, D2, D3, D4), SNR at the best station on the corrected table, before/after detectable shares, best-station shares; dots weight-proportional |
| 4 | chart04-kadri-poster-boxes-companion | OUR companion (not Kadri's poster): six poster boxes on digitised Fig. 9a–c with M1b/D1/BE min p per box, arrival share, timing verdict |
| 5 | chart05-arrivals-vs-published-traces | run J arrivals at H01W/H08S vs Fig. 9 panel spans, six poster boxes, both Kadri times, strongest pair, request windows (panel c) |
| 6 | chart06-publication-coverage | impact-time density + 50/90/99 % bars; trace spans as impact time by latitude; both Kadri times; pair locus |
| 7 | chart07-hypothesis-table (+ .csv) | rows A–F recomputed, row G = H01W 00:52:04 × H08S 01:12:49, with bearing caveat |
| 8 | chart08-descents-not-redrawn | NOT REDRAWN: run J saved no descent time series (gap) |
| 9 | chart09-illustrative-traces (+ values .csv) | real 3376 background, pulse at median / 90th pct for η 1e-3, 2.1e-4 at 3376 and H01W/H08S stand-ins, corrected table |
| 10 | chart10-air9-predicted-vs-measured | EW0112-source version; title and footnote carry NOT EXPLAINED (G23) and the slope numbers |
| — | contact-sheet-charts-01-10.png | all ten in order |

## Correctness checks done
- Corrected-IMOS levels recomputed with `run_j_levels.py` (chain unchanged, `IMOS_TL_FILE = imos_tl_ram_arc.csv`, amendment 2) for D0/D2/D3/D4 at p 0.5 on the existing 2 M-draw subsamples (`compute_levels.py`). Check against the official rerun `run-j-imos-ram-grid/levels-rerun-v2` (D0′ p 0.5, IMOS loggers): max |Δ detectable share| 1.1e-4, max |Δ median level| 0.009 dB. IMS receivers identical to the overnight table (Δ = 0).
- Every number in the panel boxes and footnotes read from the tables at render time (detectable_corrected.csv, best_receiver_corrected.csv, windows.csv/coverage.csv/request_windows.csv, poster_boxes.csv, panel_windows.csv, table1_verdicts.csv, coincidence_summary.csv, route1_grades.csv/route1_verdict.json); text overlap checked by bounding boxes (figure-style §9.1).
- ESS: earlier draft quoted geometry/lags.csv ESS (an 8-seed waypoints-only sample, 110 k for D0′); corrected to the full run J mixture Kish ESS from run-j-windows/ess.json (D0′ 1.34 M, D2 107 k, D3 5.7 k, D4 25 k).
- Pair geometry recomputed: locus 33.56 S 94.51 E, implied impact 00:31:41 (00:31:31–00:31:51 for c ± 2 sd), bearing 269.0° from H01W, 144.8° from H08S (parent: 268.9° / 144.8°). Second lag root at 20.5 S (grid edge, prior mass < 0.1 %) disclosed.
- Rows E and F recomputed on tonight's arc and c = 1.482 km/s: E 36.14 S 91.13 E, 00:28:36; F 35.79 S 91.64 E, 00:31:28 (21 Oct: 34.92 S / 35.21 S; the old values are kept in column old_21oct of the CSV). H08S 01:10:00.5 (row E) falls between scored panel windows and was not scored.
- Kadri bearing for the 00:52 signal: text p. 9 says 57°, Table 1 caption 306.18°; both stated wherever the pair appears.

## Gaps
- G-GFX1: chart 8 not redrawn — no run J altitude-time traces exist (end-of-flight saves one row per impact).
- G-GFX2: options D1 and D5 and the log-on-cause arms of the 21 Oct chart 5 are not in the run J windows/levels design.
- G-GFX3: chart 9 background recording (3376 role B, 101.5 dB 1 s median) is louder than the 14-day median used for the detectable shares (96.2 dB); disclosed in the footnote.
- Charts 1–3, 9 use p = 0.5 only (as the pre-registered chart design); other p values are in the tables.

Scripts: `scripts/` (common.py, compute_levels.py, charts_*.py); run from a workspace with both clones.
