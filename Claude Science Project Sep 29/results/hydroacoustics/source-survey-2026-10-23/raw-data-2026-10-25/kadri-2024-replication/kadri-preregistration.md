# Pre-registration: replication of Kadri (2024) crash panels on raw IMS data (track 4)

Written 2026-10-25 01:56:40 UTC, BEFORE any waveform for these cases was downloaded or looked at in this track.
(Kadri's published panels and box positions were seen before writing; they are inputs, not our data.)
Status: a pre-registered replication check of a fixed set of case–station windows; it is not a search.

## 1. Data
IM network, channel EDH, all three elements of each triad, EarthScope FDSN dataselect (anonymous), 250 Hz.
Record span per case: impact − 2 h to impact + 4 h (the 'same-day background'). StationXML response from the station service (level=response, event epoch).

## 2. Processing (Kadri's stated processing, 'K')
Kadri Methods: "a high pass Butterworth IIR filter was used (in addition to the CTBTO high pass filter) below 5 Hz. Moreover, a 2–40 [Hz] band-pass filter was applied in general."
Our implementation: demean, linear detrend, 5 % cosine taper; full response removal to Pa (obspy remove_response, pre_filt 0.5/1/100/115 Hz, water level 60 dB);
then Butterworth high-pass 5 Hz (order 4) and Butterworth band-pass 2–40 Hz (order 4), both zero-phase (sosfiltfilt). Net band 5–40 Hz.
Filter order and phase are not stated by Kadri; order 4 zero-phase is our choice (sensitivity: causal order 4, reproduction check only).

## 3. Windows (pre-registered)
Sound channel c = 1.482 ± 0.006 km/s (module standard); windows use c ± 3 sd = 1.464–1.500 km/s, plus the impact-time uncertainty (cases.py), plus 60 s at the end for signal duration.
Shallow-water routes (Java Sea cases): whole route at 1.45–1.53 km/s.
Hybrid (crustal/T-phase) envelope (Java Sea cases): geodesic length shallower than 1,000 m (incl. land) at 3.0–8.0 km/s, remainder at 1.464–1.500 km/s.
Wide hybrid (secondary; defined after seeing Kadri's panel times, before seeing any data): same, but 1.5–8.0 km/s on the shallow part.
Kadri window 'KB': the black box in his pressure panel, digitised from the full-resolution figure (Figs. 4–6).

| case   | station   | impact_utc          |   geodesic_km | route_km   | path_class                                                              | water_window                   | hybrid_window                  |   expected_baz_deg |   geodesic_baz_deg |
|:-------|:----------|:--------------------|--------------:|:-----------|:------------------------------------------------------------------------|:-------------------------------|:-------------------------------|-------------------:|-------------------:|
| F35A   | H11N      | 2019-04-09 10:26:30 |        3248.8 | —          | water (geodesic clear)                                                  | 2019-04-09 11:02:05 - 11:04:59 | —                              |             320.78 |             320.78 |
| F35A   | H11S      | 2019-04-09 10:26:30 |        3341.5 | —          | water (geodesic clear)                                                  | 2019-04-09 11:03:07 - 11:06:02 | —                              |             322.3  |             322.3  |
| SJ182  | H08S      | 2021-01-09 07:40:28 |        3771.9 | 3844.4     | shallow-water route only (bottleneck 44 m; 199 km < 200 m)              | 2021-01-09 08:22:15 - 08:25:54 | 2021-01-09 08:20:08 - 08:23:16 |              90.63 |              89.35 |
| TA810  | H11N      | 2021-07-02 11:45:18 |        3655.4 | —          | water (geodesic clear)                                                  | 2021-07-02 12:24:54 - 12:28:54 | —                              |              81.08 |              81.08 |
| TA810  | H11S      | 2021-07-02 11:45:18 |        3699.5 | —          | water (geodesic clear)                                                  | 2021-07-02 12:25:24 - 12:29:24 | —                              |              79.22 |              79.22 |
| QZ8501 | H01W      | 2014-12-27 23:20:35 |        3492.1 | 3891.6     | shallow-water route only (bottleneck 31 m; 1601 km < 200 m)             | 2014-12-28 00:02:58 - 00:06:28 | 2014-12-27 23:49:27 - 23:55:05 |             351.4  |             351.48 |
| QZ8501 | H08S      | 2014-12-27 23:20:35 |        4146.6 | 4292.5     | shallow-water route only (bottleneck 30 m; 647 km < 200 m)              | 2014-12-28 00:07:20 - 00:11:05 | 2014-12-27 23:58:44 - 00:03:50 |              90.63 |              85.97 |
| AB1103 | H08S      | 2022-02-26 09:30:00 |        3186.6 | 3355.3     | water (geodesic crosses banks/islands; route >= 1000 m exists, +169 km) | 2022-02-26 10:05:24 - 10:19:11 | —                              |             254.56 |             258.47 |
| JT610  | H08S      | 2018-10-28 23:31:54 |        3834   | 3902.9     | shallow-water route only (bottleneck 30 m; 257 km < 200 m)              | 2018-10-29 00:14:24 - 00:18:00 | 2018-10-29 00:11:41 - 00:14:59 |              90.63 |              89.17 |

## 4. Statistics (per case × station × window)
* S = max over the window of the triad-mean 1-s moving RMS (Pa) of the K-filtered pressure (hop 0.5 s). Also per element: instantaneous peak |p| (Pa), 1-s RMS peak (Pa).
* SNR_panel (dB) = 20 log10(S / median triad-mean 1-s RMS in Kadri's 10-min panel outside his box). SNR_day (dB) = same with the median over the 6-h record outside the exclusion zones.
* p-value: S compared with the same statistic on all non-overlapping windows of the same length in the 6-h record, excluding windows that overlap [KB − 5 min, KB + 5 min] or [W − 5 min, W + 5 min] of the pre-registered windows. p = (1 + #null ≥ S)/(n + 1); floor 1/(n + 1) stated per row; rank of S given.
* Thresholds: screen p ≤ 0.3, mark p ≤ 0.1, report p ≤ 0.05.
* D1 STA/LTA (module run-J definition, detectors.py d1_stalta: STA 2 s / LTA 30 s on 5–40 Hz, hop 0.1 s): max ratio in the window and its p-value against the same null windows.
* Likelihood ratio: not defined here (no calibrated per-case signal model); not reported.
* Back-azimuth: 20-s segment centred on the time of S; K-filtered element waveforms cross-correlated pairwise (max lag 2.5 s, parabolic peak); plane-wave slowness by least squares from the three pair delays; report back-azimuth (deg), apparent speed (km/s), closure residual (s). Robustness: the same on 1-s RMS envelopes. Bearing null: the same estimator at the times of the 20 largest null-window maxima.
* Bearing consistency: |measured − expected| ≤ 10° (≈ 3 × the module's 3.3° bearing sd). QZ8501–H01W: expected range 341–4° (Sunda to Bali exits).
* 'Consistent with the crash site' requires: time within the pre-registered water or hybrid window AND bearing consistent AND p ≤ 0.05.

## 5. Reproduction match (our panel vs Kadri's printed panel)
Kadri's orange trace digitised from the full-resolution figure: per pixel column, upper and lower envelope (Pa).
Ours: per same time bin, max and min of the K-filtered trace of each element. Metric: Pearson r between upper envelopes after a lag search of ±90 s, and the median-envelope amplitude ratio (dB).
'Match = yes' if r ≥ 0.5 at |lag| ≤ 5 s with amplitude ratio within ±3 dB; 'partial' if r ≥ 0.3, or the box feature is visible at |lag| ≤ 30 s; else 'no'.

## 6. Standing caveats
(1) The module propagation model failed the frequency-slope check against the 2001 airguns (+10 dB/octave at H01W, +7 at H08S) although levels passed. This replication uses no transmission-loss model, so its results do not change that caveat.
(2) Detection probability is a proxy unless measured on real data; no detection probability is claimed here.
No MH370 quantity is inferred from any result here.
