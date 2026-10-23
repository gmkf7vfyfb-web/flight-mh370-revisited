# Whale calls in the 8 March 2014 hydroacoustic data (track: whale calls, 23 Oct 2026)

EXPLORATORY. Purpose: identify whale calls in every 8 March 2014 source held, so that they can be separated from potential impact signals.
Read `METHODS.md` first (deviations and limits at the top).

| File | Contents |
|---|---|
| `METHODS.md` | Methods, validation, results, limits |
| `DOWNLOADS.md` | Datasets and papers fetched or checked, with links and what each gave |
| `whale_call_catalogue_8mar2014_all_sources.csv` | One table for 8 Mar 2014: IMOS detections (5 loggers), SEANOE published Z-calls (MAD, NCRO, SSEIR, SWAMS, WKER), Royer-panel 26 Hz chorus lines |
| `whale_call_catalogue_imos_8mar2014.csv` | IMOS 8 Mar detections with q-value, false alarms per hour, structure, band level, notes |
| `whale_call_catalogue_imos_backgrounds.csv.gz` | Same for the 14-day backgrounds (3250, 3274, 3376; 1-15 Mar 2014 without 8 Mar) |
| `candidate_crosscheck.csv` | 679 candidate rows (Kadri Table 1, Royer Table 5, ranked singles, potential signals v3 tables 1-2) with whale evidence, verdict and manual review |
| `seanoe_zcalls_8mar2014.csv` | SEANOE 46124 Z-call detections 7 Mar 12:00 - 9 Mar 12:00 UTC |
| `royer_26hz_lines.csv` | 26 Hz line in each of the 34 digitised Royer panels |
| `kadri_trace_periodicity.csv`, `kadri_trace_envelope_events.csv` | Frequency-blind duration and repetition features of the Kadri Fig. 9 traces |
| `validation_*.csv`, `run_summary.json` | Target-decoy counts, confidence counts, manual review, injection-recovery, Royer kernel real vs null, Royer test base rates |
| `fig1_whale_call_types_8mar2014.png` | Example spectrograms per call type and the top single-site candidate |
| `fig2_whale_calls_vs_candidates_0000_0200.png` | Whale calls and candidate signals, 00:00-02:00 UTC, all recorders |
| `fig3_whale_chorus_tests.png` | Blackman 2003 17-27 Hz excess and the 26 Hz line in the Royer panels |
| `downloads/` | SEANOE 46124 and 51007 archives (CC-BY-NC 4.0, Leroy, Royer, Bonnel, Samaran) |
| `code/` | `imos_io.py`, `whale_detectors.py` (reusable detector feature set), `make_event_spectrograms.py`, `process_imos.py`, `build_catalogue.py`, `crosscheck.py` |

Re-run: `process_imos.py jobs.csv k n det/` for k in 0..n-1 (separate processes), then `build_catalogue.py`, then `crosscheck.py` (argument lists in each file header).
Figures were drawn in the session kernel from these tables (not scripted).
