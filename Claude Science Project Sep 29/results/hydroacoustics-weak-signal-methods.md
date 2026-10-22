# Hydroacoustics — weak-signal method trials (work order 2026-10-21, block 8; brief Refresh v2 §7)

**Status: DONE as a method trial; PREDICTIVE, NOT CALIBRATED. No detection is claimed.** Every number below carries
caveat C1 (propagation slope misfit, +10.4/+7.4 dB per octave at H01W/H08S) and C2 (coupling efficiency not
calibrated; η swept over four decades, F-35A upper anchor). The Kadri Fig. 9 traces are DIGITISED plots (PDF vector
polylines, ~14.5 vertices/s, envelope resolution), not recordings. Both Kadri times are carried everywhere: text time
00:52:03 and caption time 00:54:30.

Pre-registration: module branch commit `78c7e88` (`prepare/weak_signal/preregistration.py`), committed before any
statistic on data. Amendment 1 (SNR grid 15–30 dB, `run_injection_ext.py`) is disclosed below. Code:
`engine/hypotheses/hydroacoustics/prepare/weak_signal/` (module branch). Data products:
`/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-weak-signal/` (17 MB, SHA256SUMS). Thread budget 3 processes;
total compute about 12 minutes (templates 33 s, null + injections 269 s, extension 127 s, panels 69 s).

## 1. Summary

1. On real IMOS background (Perth Canyon 3376, 14 days, 5,376 null windows of 60 s), **the two dispersion-aware
   matched filters reach P_D = 0.5 at SNR ≈ 7 dB** (α = 0.01 per 60 s window), against 13–16 dB for the STA/LTA
   baseline and 27–28 dB for the band-energy baseline: a 6–9 dB gain over STA/LTA, about 20 dB over band energy. At
   α = 0.001 only the matched filters reach P_D = 0.5 at all (envelope 16–19 dB, waveform 24–25 dB; STA/LTA P_D ≤ 0.24
   at 30 dB). **This is the model-matched best case**: the injected pulses were made with the same KRAKEN propagation
   model as the templates (declared in the pre-registration). The gain is the shape test: a 50 s dispersed arrival does
   not look like the loud local transients (ships, fish, whales) that fill the null's upper tail.
2. Spectral kurtosis is equivalent to STA/LTA (SNR_50 13–15 dB at α = 0.01). Cepstral fingerprint, time-domain
   kurtosis, synchrosqueezed concentration, Bayesian change-point and stochastic resonance **failed** as implemented
   (P_D ≤ 0.17 at 30 dB): negative results, kept in the code behind the method table (not deleted).
3. Two-station envelope stacking at a known lag (idealised, same SNR at both loggers) reaches only P_D = 0.27 at
   +10 dB (α = 0.01): stacking band-level z-scores from two heavy-tailed backgrounds does not beat one shape test.
4. On the digitised H01W panels, **only the envelope matched filter reaches p = 0.05 inside an author's box**: at the
   text time 00:52:03 (panel c, p = 0.052, label *mark*). The caption time 00:54:30 gives p = 0.16 (screen). The four
   poster panel-(a) boxes stay at p ≥ 0.08 for every method (best: Bayesian change-point in box 1, p = 0.080, *mark*).
   The cepstral statistic marks three unlabelled times in panel b (Kadri's "no signal" panel) at p = 0.002–0.021; with
   nine methods on 50 minutes of trace, chance gives about two such values, and this method had no power in test (a).
   On H08S (panels d, e) the kurtosis statistics fire on the airgun shots throughout (46 *report* rows): the IMOS
   emulated null does not represent a shot-dominated record, so those rows are **null-mismatch artefacts**, listed but
   not candidates.
5. H08S airgun suppression on the digitised panels: shot-template subtraction lowers the residual energy by 5.8 dB (d)
   and 4.7 dB (e); with cadence gating (30 % of time removed) 7.6 and 5.3 dB. It cuts the chance rate of a z ≥ 3 peak
   within ±2 s of a random time from 0.40–0.62 to 0.00–0.20, while an injected deep-channel arrival 4 dB below the median
   shot peak is still found in 0.88 (d) / 0.50 (e) of trials (0 dB: 0.98 / 0.92). Below −8 dB it is not recovered.
   36 residual peaks survive at z ≥ 3; 9 of them fall in the lag windows of the two Kadri H01W times (table below), all
   carried as screen-level rows with labels, none as a claim.
6. Recommendation for the main pipeline (§7): add the dispersion-aware **envelope** matched filter as the primary
   screen statistic beside STA/LTA (it is the only method that keeps power at α = 0.001 and it is robust to phase),
   with the waveform matched filter as a secondary at α = 0.01; calibrate its threshold on the real background of each
   receiver as here; and test it on a non-model-matched ground-truth case before any MH370 statistic (gap G-W1).

## 2. Test set (a): synthetic impact pulses in real IMOS background

**Design (as pre-registered).** Background: IMOS public-bucket days 1–7 and 9–15 March 2014 (8 March excluded; it holds
the MH370 windows). Primary target 3376 (Perth Canyon): all 1,344 files (0 unreadable). Secondary 3274 (Portland) and
3250 (Scott Reef): every 4th file (336 each). Series: module `imos_noise.read_volts/decimate` (500 Hz), 5–40 Hz
4th-order Butterworth zero-phase, decimated to 100 Hz. Null: statistic maxima over non-overlapping 60 s windows from
32 s; thresholds = null (1 − α) quantiles, α ∈ {0.01, 0.001} per window (5376 windows at 3376, so the 0.001
quantile rests on the top ~5 values; 1344 at each secondary target, where 0.001 is at the resolution floor).
Pulse: one-pole source (ESD flat to 1/τ, f⁻² above; the module's `band_fraction` model), τ ∈ {0.1, 1, 10} s, convolved
with a KRAKEN coherent broadband channel (2–48 Hz, step 1/64 Hz, 2945 frequencies, 5–121 modes; WOA23 March profile at the
path midpoint 36.6°S 102.2°E of the run J seed-1 weighted-median impact (37.07°S 89.85°E) → H01W, extended below
4,800 m holding SA and CT; flat bottom at the path's median GEBCO 2026 depth 4,610 m; module 'hard' half-space;
Francois–Garrison; source 10 m, receiver at the channel axis 1,200 m). Of the two time conventions the one whose energy
builds to an abrupt end (the deep-sound-channel crescendo) was taken as physical; 50 s templates with the peak at 35 s.
Injection ranges on a 25 km grid over 1,800–3,000 km; template bank at 1,800, 2,200, 2,600, 3,000 km × 3 τ (12
templates), so a range mismatch of up to 200 km exists. SNR = peak 1 s 5–40 Hz level of the pulse minus the target's
background median 1 s level (3376: -59.3 dB re V²). N_INJ = 120 per (SNR, τ) cell at 3376, 60 at the secondary
targets; seed 20261022. Stochastic-resonance constants set on the first 20 background files (k = 3.0, σ = 0.7; background
switch rate 0.92 per s — the pre-registered target of 1 per s was not reached on the grid, disclosed). Cepstral band Q =
0.06–1.14 s.

**Amendment 1 (disclosed, not pre-registered).** The pre-registered SNR grid (−15 to +10 dB) ended before the baselines
and most trial methods reached P_D = 0.5, so their SNR_50 was unidentified. The same design was re-run at 15, 20, 25,
30 dB (seed 20261023), thresholds unchanged; fits below use the union grid. The pre-registered P_D values stand.

**Null thresholds at 3376** (statistic units; per 60 s window):

| method | α = 0.01 | α = 0.001 |
|---|---|---|
| M0a_stalta | 21.6 | 134 |
| M0b_bandenergy | 21.9 | 32.4 |
| M1a_mf_waveform | 0.15 | 0.338 |
| M1b_mf_envelope | 0.897 | 0.983 |
| M3_cepstral | 4.87 | 6.89 |
| M4a_spectral_kurtosis | 6.38 | 14.7 |
| M4b_kurtosis | 25.2 | 60 |
| M5_synchrosqueezed | 12.2 | 20.4 |
| M6_changepoint | 0.913 | 0.974 |
| M7_stochastic_resonance | 20.2 | 23 |

**SNR_50 (dB) at 3376** from a logistic fit on the union grid; "not reached" = P_D never crossed 0.5 by 30 dB:

| method | α 0.01, τ 0.1 s | α 0.01, τ 1 s | α 0.01, τ 10 s | α 0.001, τ 0.1 s | α 0.001, τ 1 s | α 0.001, τ 10 s |
|---|---|---|---|---|---|---|
| M0a_stalta | 13.4 | 15.3 | 15.7 | not reached (P_D max 0.24) | not reached (P_D max 0.12) | not reached (P_D max 0.18) |
| M0b_bandenergy | 28.3 | 27.5 | 28.0 | not reached (P_D max 0.01) | not reached (P_D max 0.01) | not reached (P_D max 0.02) |
| M1a_mf_waveform | 6.5 | 7.2 | 7.0 | not reached (P_D max 0.39) | 24.4 | 25.2 |
| M1b_mf_envelope | 6.9 | 7.8 | 8.0 | 16.4 | 18.9 | 18.6 |
| M3_cepstral | not reached (P_D max 0.12) | not reached (P_D max 0.17) | not reached (P_D max 0.12) | not reached (P_D max 0.02) | not reached (P_D max 0.00) | not reached (P_D max 0.01) |
| M4a_spectral_kurtosis | 12.8 | 14.7 | 15.0 | not reached (P_D max 0.02) | not reached (P_D max 0.01) | not reached (P_D max 0.01) |
| M4b_kurtosis | not reached (P_D max 0.07) | not reached (P_D max 0.12) | not reached (P_D max 0.08) | not reached (P_D max 0.01) | not reached (P_D max 0.01) | not reached (P_D max 0.01) |
| M5_synchrosqueezed | not reached (P_D max 0.09) | not reached (P_D max 0.10) | not reached (P_D max 0.12) | not reached (P_D max 0.01) | not reached (P_D max 0.02) | not reached (P_D max 0.03) |
| M6_changepoint | not reached (P_D max 0.04) | not reached (P_D max 0.03) | not reached (P_D max 0.03) | not reached (P_D max 0.01) | not reached (P_D max 0.01) | not reached (P_D max 0.01) |
| M7_stochastic_resonance | not reached (P_D max 0.00) | not reached (P_D max 0.01) | not reached (P_D max 0.01) | not reached (P_D max 0.00) | not reached (P_D max 0.00) | not reached (P_D max 0.00) |

**P_D at 3376, τ = 1 s, α = 0.01** (120 trials per cell; −15…+10 dB pre-registered, 15–30 dB amendment 1):

| method | -15 dB | -10 dB | -5 dB | 0 dB | 5 dB | 10 dB | 15 dB | 20 dB | 25 dB | 30 dB |
|---|---|---|---|---|---|---|---|---|---|---|
| M0a_stalta | 0.00 | 0.00 | 0.02 | 0.00 | 0.03 | 0.16 | 0.44 | 0.84 | 0.95 | 1.00 |
| M0b_bandenergy | 0.00 | 0.01 | 0.01 | 0.01 | 0.02 | 0.00 | 0.01 | 0.01 | 0.28 | 0.78 |
| M1a_mf_waveform | 0.01 | 0.00 | 0.03 | 0.07 | 0.36 | 0.72 | 0.89 | 0.98 | 0.99 | 1.00 |
| M1b_mf_envelope | 0.00 | 0.01 | 0.03 | 0.13 | 0.34 | 0.66 | 0.82 | 0.96 | 0.98 | 1.00 |
| M3_cepstral | 0.00 | 0.00 | 0.00 | 0.00 | 0.01 | 0.02 | 0.03 | 0.12 | 0.09 | 0.17 |
| M4a_spectral_kurtosis | 0.02 | 0.01 | 0.01 | 0.00 | 0.05 | 0.26 | 0.50 | 0.82 | 0.91 | 0.99 |
| M4b_kurtosis | 0.02 | 0.00 | 0.02 | 0.00 | 0.01 | 0.04 | 0.04 | 0.08 | 0.12 | 0.03 |
| M5_synchrosqueezed | 0.02 | 0.00 | 0.00 | 0.01 | 0.03 | 0.09 | 0.07 | 0.08 | 0.07 | 0.10 |
| M6_changepoint | 0.00 | 0.01 | 0.01 | 0.00 | 0.03 | 0.02 | 0.03 | 0.01 | 0.03 | 0.01 |
| M7_stochastic_resonance | 0.01 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |

**P_D at 3376, τ = 1 s, α = 0.001:**

| method | -15 dB | -10 dB | -5 dB | 0 dB | 5 dB | 10 dB | 15 dB | 20 dB | 25 dB | 30 dB |
|---|---|---|---|---|---|---|---|---|---|---|
| M0a_stalta | 0.00 | 0.00 | 0.01 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.03 | 0.12 |
| M0b_bandenergy | 0.00 | 0.01 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.01 | 0.00 | 0.00 |
| M1a_mf_waveform | 0.00 | 0.00 | 0.01 | 0.00 | 0.04 | 0.17 | 0.23 | 0.46 | 0.52 | 0.58 |
| M1b_mf_envelope | 0.00 | 0.00 | 0.00 | 0.01 | 0.08 | 0.25 | 0.38 | 0.68 | 0.74 | 0.72 |
| M3_cepstral | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| M4a_spectral_kurtosis | 0.00 | 0.00 | 0.01 | 0.00 | 0.00 | 0.00 | 0.01 | 0.00 | 0.00 | 0.00 |
| M4b_kurtosis | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.01 | 0.00 | 0.00 | 0.01 | 0.00 |
| M5_synchrosqueezed | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.01 | 0.02 | 0.00 | 0.00 | 0.00 |
| M6_changepoint | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.01 | 0.00 | 0.00 | 0.00 |
| M7_stochastic_resonance | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |

**Secondary targets, τ = 1 s (SNR_50, dB):**

| logger | method | α = 0.01 | α = 0.001 |
|---|---|---|---|
| 3274 | M0a_stalta | 11.2 | 22.3 |
| 3274 | M0b_bandenergy | 20.5 | not reached (P_D max 0.00) |
| 3274 | M1a_mf_waveform | 5.2 | 14.5 |
| 3274 | M1b_mf_envelope | 2.3 | 10.3 |
| 3274 | M4a_spectral_kurtosis | 7.5 | not reached (P_D max 0.00) |
| 3250 | M0a_stalta | not reached (P_D max 0.03) | not reached (P_D max 0.02) |
| 3250 | M0b_bandenergy | not reached (P_D max 0.02) | not reached (P_D max 0.02) |
| 3250 | M1a_mf_waveform | 24.2 | not reached (P_D max 0.25) |
| 3250 | M1b_mf_envelope | 25.9 | not reached (P_D max 0.33) |
| 3250 | M4a_spectral_kurtosis | not reached (P_D max 0.02) | not reached (P_D max 0.02) |

Scott Reef 3250 has the heaviest null tail (its STA/LTA 0.01 threshold is 206 in stage A); only the matched filters
reach P_D = 0.5 there, at 24–26 dB. Portland 3274 is the quietest: envelope matched filter SNR_50 = 2.3 dB (α 0.01).

**Two-station envelope stacking (M2), 3376 + 3274 at the same SNR, known lag, ±30 s search, 60 trials per cell:**

| alpha | -15 dB | -10 dB | -5 dB | 0 dB | 5 dB | 10 dB |
|---|---|---|---|---|---|---|
| 0.001 | 0.00 | 0.01 | 0.00 | 0.00 | 0.00 | 0.05 |
| 0.01 | 0.00 | 0.02 | 0.01 | 0.01 | 0.03 | 0.27 |

**Verdicts (pre-registered rule: better = SNR_50 at α 0.01 at least 2 dB below the better baseline with
non-overlapping Wilson intervals at the baseline's SNR_50):**

| method | principle | free parameters (fixed in prereg) | FAR control | verdict at 3376 |
|---|---|---|---|---|
| M0a STA/LTA | energy ratio, 2 s / 30 s | STA, LTA | null quantile | baseline (SNR_50 13–16 dB) |
| M0b band energy | 1 s band level over preceding-60 s median, 3 s mean | bands, memory | null quantile | baseline (28 dB); worst |
| M1a matched filter, waveform | normalised cross-correlation with 12 KRAKEN dispersed templates | bank ranges, τ, template length | null quantile | **better** (−7 to −9 dB vs STA/LTA; α 0.001 reached) |
| M1b matched filter, envelope | as M1a on the 0.5 s squared envelope at 10 Hz | as M1a | null quantile | **better** (−6 to −8 dB; best at α 0.001) |
| M2 two-station stacking | z(band level) summed at predicted lag | lag search ±30 s | pair null | worse than M1 (P_D 0.27 at +10 dB) |
| M3 cepstral fingerprint | cepstral energy fraction in Q, z vs preceding 60 s | segment 8 s, Q | null quantile | **failed** (P_D ≤ 0.17 at 30 dB) |
| M4a spectral kurtosis | Antoni SK, 1 s STFT, 8 s blocks, 5–40 Hz mean | block, hop | null quantile | equivalent to STA/LTA (13–15 dB) |
| M4b time kurtosis | excess kurtosis, 2 s frames | frame | null quantile | failed (≤ 0.12) |
| M5 synchrosqueezed concentration | top-5 % energy fraction of SST, z vs preceding 60 s | block, top fraction | null quantile | failed (≤ 0.12); ssqueezepy 0.6.6 |
| M6 Bayesian change-point | Adams–MacKay on 1 s band level, hazard 1/120 | prior, hazard | null quantile | failed (≤ 0.04) |
| M7 stochastic resonance | bistable well switching rate | k, σ | null quantile | failed (≤ 0.01); exploratory |

Why the failures: M3, M5 and M6 are z-scored against the preceding 60 s and the null's upper tail (loud local
transients) already saturates them; M6's change probability is near 1 at every transient; M7's switching rate is
set by the normalised series and is insensitive to a slow 50 s energy ramp. They are kept in `methods.py` as
negative results.

## 3. Test set (b): the digitised Kadri Fig. 9 traces

**These traces are decimated plots** (panels a, b, c: 8,706 / 8,722 / 8,716 vertices over 600 s; d, e: 8,936 / 8,974),
resampled to 20 Hz and band-passed 1–9 Hz; the matched filter uses the template envelope only (2,200 km for H01W,
3,704 km for H08S). Null: IMOS 3376 background passed through a plot-decimation emulator (per 69 ms bin the min and
max as vertices, 20 Hz), 1344 files × 4 windows of 60 s. p = fraction of null window maxima ≥ the statistic.
Labels: report p < 0.05, mark p < 0.1, screen p < 0.3 (ruling 13 Oct). Chance alone gives about one p < 0.05 value per
20 minutes of trace per method, so with nine methods on 50 minutes a handful of *report* rows is the expectation.

**Counts of candidate rows (local maxima with p < 0.3) by method and station:**

| method | H01W screen / mark / report | H08S screen / mark / report |
|---|---|---|
| M0a_stalta | 0 / 0 / 0 | 22 / 0 / 0 |
| M0b_bandenergy | 0 / 0 / 0 | 20 / 0 / 0 |
| M1b_mf_envelope | 2 / 1 / 0 | 6 / 1 / 0 |
| M3_cepstral | 16 / 1 / 3 | 5 / 1 / 2 |
| M4a_spectral_kurtosis | 0 / 0 / 0 | 51 / 24 / 22 |
| M4b_kurtosis | 1 / 0 / 0 | 33 / 18 / 20 |
| M5_synchrosqueezed | 1 / 0 / 0 | 0 / 0 / 0 |
| M6_changepoint | 9 / 2 / 0 | 4 / 0 / 0 |
| M7_stochastic_resonance | 2 / 0 / 0 | 1 / 0 / 0 |

The H08S counts for spectral and time kurtosis (46 *report* rows) are the airgun shots: the emulated IMOS null has no
10 s shot train, so the null is mismatched for H08S and these rows are not candidates. Full list:
`run-j-weak-signal/kadri/candidates.csv` (268 rows, 230 of them H08S).

**H01W candidate rows ranked by p (top 25 of the screen-level list):**

| panel | method | UTC | statistic | p (null) | label | box / Table 1 |
|---|---|---|---|---|---|---|
| b | M3_cepstral | 00:41:08 | 4.4 | 0.002 | report | unlabelled |
| b | M3_cepstral | 00:42:52 | 3.75 | 0.021 | report | unlabelled |
| b | M3_cepstral | 00:42:38 | 3.73 | 0.021 | report | unlabelled |
| c | M1b_mf_envelope | 00:52:05 | 0.712 | 0.052 | mark | text time 00:52:03 |
| c | M6_changepoint | 00:52:57 | 0.443 | 0.064 | mark | Table 1 00:52:50 (274.84 deg) |
| c | M3_cepstral | 00:53:32 | 3.2 | 0.070 | mark | Table 1 00:53:31 (257.58 deg); Table 1 00:53:38 (315.46 deg) |
| a | M6_changepoint | 00:28:39 | 0.371 | 0.080 | mark | poster (a) box 1 |
| c | M6_changepoint | 00:54:29 | 0.294 | 0.106 | screen | caption time 00:54:30; Table 1 00:54:30 (306.18 deg) |
| b | M3_cepstral | 00:40:56 | 3.03 | 0.107 | screen | unlabelled |
| a | M3_cepstral | 00:27:46 | 3.01 | 0.110 | screen | unlabelled |
| a | M3_cepstral | 00:34:05 | 3.01 | 0.111 | screen | unlabelled |
| c | M3_cepstral | 00:49:01 | 2.97 | 0.120 | screen | Table 1 00:48:55 (291.13 deg) |
| b | M7_stochastic_resonance | 00:39:24 | 9 | 0.123 | screen | unlabelled |
| a | M3_cepstral | 00:33:46 | 2.96 | 0.124 | screen | poster (a) box 3 |
| b | M6_changepoint | 00:43:34 | 0.223 | 0.141 | screen | unlabelled |
| a | M6_changepoint | 00:34:58 | 0.215 | 0.148 | screen | unlabelled |
| b | M3_cepstral | 00:41:23 | 2.86 | 0.148 | screen | unlabelled |
| c | M1b_mf_envelope | 00:54:29 | 0.601 | 0.156 | screen | caption time 00:54:30; Table 1 00:54:30 (306.18 deg) |
| a | M3_cepstral | 00:31:44 | 2.8 | 0.170 | screen | poster (a) box 2 |
| a | M6_changepoint | 00:33:04 | 0.185 | 0.172 | screen | poster (a) box 3 |
| a | M3_cepstral | 00:28:33 | 2.77 | 0.181 | screen | poster (a) box 1 |
| b | M6_changepoint | 00:46:12 | 0.17 | 0.191 | screen | unlabelled |
| c | M3_cepstral | 00:55:48 | 2.72 | 0.196 | screen | unlabelled |
| c | M6_changepoint | 00:48:21 | 0.162 | 0.201 | screen | unlabelled |
| a | M3_cepstral | 00:27:25 | 2.68 | 0.214 | screen | unlabelled |

**Author's boxes: the smallest p inside each box, per method** (the test the work order asked for):

| box | M0a_stalta | M0b_bandenergy | M1b_mf_envelope | M3_cepstral | M4a_spectral_kurtosis | M4b_kurtosis | M5_synchrosqueezed | M6_changepoint | M7_stochastic_resonance |
|---|---|---|---|---|---|---|---|---|---|
| caption time 00:54:30 | 0.62 | 0.83 | 0.16 | 0.30 | 0.80 | 0.91 | 0.85 | 0.11 | 0.67 |
| poster (a) box 1 | 0.95 | 0.94 | 0.89 | 0.18 | 1.00 | 0.99 | 0.57 | 0.08 | 0.67 |
| poster (a) box 2 | 0.83 | 0.83 | 0.84 | 0.17 | 0.97 | 1.00 | 0.55 | 0.34 | 0.46 |
| poster (a) box 3 | 0.78 | 0.91 | 0.57 | 0.12 | 0.92 | 0.99 | 0.75 | 0.17 | 0.87 |
| poster (a) box 4 | 0.52 | 0.71 | 0.52 | 0.29 | 0.82 | 0.96 | 0.33 | 0.56 | 0.46 |
| text time 00:52:03 | 0.44 | 0.60 | 0.05 | 0.30 | 0.87 | 0.99 | 0.76 | 0.38 | 0.87 |

Reading: at the text time 00:52:03 the envelope matched filter gives p = 0.05 (mark) and STA/LTA p = 0.44; at the
caption time 00:54:30 the best is the Bayesian change-point at p = 0.11 and the matched filter at p = 0.16 (screen);
the four panel (a) boxes reach p = 0.08 at best (change-point, box 1) and are otherwise screen-level or below. The
21 Oct review diagnostic (fixed STA/LTA ratio 4.69 at 00:52:03, 2.38 at 00:54:28, panel (a) maxima 1.7–2.7) is
consistent with these p-values on the same traces. A fixed single-station threshold would remove every box; under the
screen-level stance they are all carried as rows with their labels.

**Two-station stacking across the panels (H08S − H01W lag 855.93–1346.50 s, 1 s steps):**

| H01W UTC | lag (s) | H08S UTC | statistic | p (null) | label | box / Table 1 |
|---|---|---|---|---|---|---|
| 00:52:04 | 1016 | 01:09:00 | 9.51 | 0.056 | mark | text time 00:52:03 |
| 00:54:29 | 871 | 01:09:00 | 8.85 | 0.086 | mark | caption time 00:54:30; Table 1 00:54:30 (306.18 deg) |
| 00:52:05 | 1015 | 01:09:00 | 8.25 | 0.129 | screen | text time 00:52:03 |
| 00:52:00 | 1020 | 01:09:00 | 7.86 | 0.172 | screen | text time 00:52:03; Table 1 00:51:50 (320.4 deg) |
| 00:52:57 | 963 | 01:09:00 | 7.76 | 0.186 | screen | Table 1 00:52:50 (274.84 deg) |
| 00:46:50 | 1330 | 01:09:00 | 7.73 | 0.189 | screen | unlabelled |
| 00:48:21 | 1239 | 01:09:00 | 7.72 | 0.190 | screen | unlabelled |
| 00:49:44 | 1156 | 01:09:00 | 7.70 | 0.192 | screen | Table 1 00:49:41 (234.67 deg) |

Every top pair lands on the same H08S second, 01:09:00 (540 s into panel d), which lies 0.9 s from the shot grid
(cadence 9.95 s, phase 1.83 s): a loud on-cadence airgun shot, not an independent second-station event. The pairs are
therefore driven by one H08S feature and carry no coincidence information; they are listed for completeness only.

## 4. Test set (c): H08S airgun suppression

Panels d, e at 40 Hz (as `h08s_shot_outliers.load`); envelope p² smoothed 0.25 s; shots by the `h08s_pulse_energy`
rule (64 and 52 shots). (c1) Local median template of up to 12 neighbouring shots over [−3, +6] s, scaled to the
shot's peak, subtracted. (c2) Cadence = median 9–11 s interval, phase = circular median; ±1.5 s gated (30 % of time).
(c3) Off-cadence flag = phase distance > 2 s.

| panel | shots | cadence (s) | gated fraction | (c1) residual, whole panel (dB) | (c1) shot-free gaps (dB) | (c2) gating alone (dB) | (c1)+(c2) (dB) |
|---|---|---|---|---|---|---|---|
| d | 64 | 9.95 | 0.30 | -5.8 | -4.0 | -3.8 | -7.6 |
| e | 52 | 10.00 | 0.30 | -4.7 | -3.5 | -1.4 | -5.3 |

**Candidate energy surviving (z ≥ 3 against the median/MAD of the raw envelope in shot-free gaps):**

| panel | raw | after (c1) | after (c1)+(c2) |
|---|---|---|---|
| d | 87 | 68 | 23 |
| e | 75 | 43 | 13 |

**Survivors after (c1)+(c2)** (lag-consistent = inside [t₁ + 855.93, t₁ + 1346.50] s for a Kadri H01W time t₁):

| panel | UTC | z | off cadence | lag-consistent with H01W box |
|---|---|---|---|---|
| e | 01:19:47 | 8.8 | no | none |
| e | 01:19:37 | 7.4 | no | none |
| d | 01:01:24 | 7.1 | no | none |
| d | 01:02:34 | 7.1 | yes | none |
| e | 01:11:21 | 6.7 | no | text time 00:52:03; caption time 00:54:30 |
| e | 01:16:00 | 6.3 | no | caption time 00:54:30 |
| e | 01:18:42 | 5.2 | yes | none |
| d | 01:09:57 | 5.0 | yes | text time 00:52:03; caption time 00:54:30 |
| e | 01:19:17 | 4.5 | no | none |
| d | 01:07:03 | 4.5 | no | text time 00:52:03 |
| d | 01:02:05 | 4.4 | yes | none |
| d | 01:01:35 | 4.3 | yes | none |
| e | 01:18:10 | 4.1 | no | none |
| e | 01:19:57 | 4.1 | no | none |
| e | 01:15:21 | 3.9 | yes | caption time 00:54:30 |
| d | 01:01:16 | 3.9 | yes | none |
| d | 01:00:46 | 3.9 | yes | none |
| e | 01:16:21 | 3.8 | no | caption time 00:54:30 |
| e | 01:19:27 | 3.7 | no | none |
| d | 01:01:55 | 3.7 | yes | none |
| d | 01:03:04 | 3.7 | no | none |
| d | 01:04:47 | 3.5 | yes | none |
| d | 01:05:43 | 3.5 | no | none |
| e | 01:16:41 | 3.5 | no | caption time 00:54:30 |
| d | 01:01:10 | 3.4 | yes | none |
| d | 01:03:35 | 3.4 | yes | none |
| d | 01:03:45 | 3.4 | yes | none |
| d | 01:05:33 | 3.4 | no | none |
| d | 01:02:57 | 3.4 | yes | none |
| d | 01:07:43 | 3.3 | yes | text time 00:52:03 |
| d | 01:08:54 | 3.2 | yes | text time 00:52:03; caption time 00:54:30 |
| e | 01:19:01 | 3.2 | no | none |
| d | 01:04:39 | 3.2 | yes | none |
| d | 01:02:20 | 3.1 | yes | none |
| d | 01:05:18 | 3.1 | yes | none |
| d | 01:04:07 | 3.1 | yes | none |

The surviving rows are what a shot-suppressed H08S scan would hand to the coincidence test. Nine lie in the lag
windows of the Kadri times (01:07:03–01:09:57 for the text time, 01:08:54–01:16:41 for the caption time); 4 of those 9
are off-cadence. None is a claim: on a decimated plot the residual misfit of the template itself produces peaks, and the
null for this residual is unknown (gap G-W3). With raw H08S triad data the same procedure applies to full waveforms
and three elements, and the residual null can be measured on adjacent survey hours.

**Recovery of the module's H08S-range template envelope injected into the panels (40 onsets per level):**

| panel | level (dB re median shot peak) | raw: hit / chance | (c1): hit / chance | (c1)+(c2): hit / chance | peak in gate |
|---|---|---|---|---|---|
| d | -20 | 0.50 / 0.50 | 0.33 / 0.33 | 0.15 / 0.15 | 0.17 |
| d | -16 | 0.55 / 0.55 | 0.42 / 0.42 | 0.17 / 0.17 | 0.28 |
| d | -12 | 0.62 / 0.60 | 0.60 / 0.60 | 0.20 / 0.17 | 0.40 |
| d | -8 | 0.82 / 0.47 | 0.50 / 0.25 | 0.40 / 0.10 | 0.20 |
| d | -4 | 0.93 / 0.53 | 0.97 / 0.35 | 0.88 / 0.12 | 0.25 |
| d | +0 | 0.95 / 0.55 | 1.00 / 0.38 | 0.97 / 0.20 | 0.17 |
| e | -20 | 0.57 / 0.57 | 0.20 / 0.20 | 0.10 / 0.10 | 0.35 |
| e | -16 | 0.62 / 0.62 | 0.47 / 0.45 | 0.20 / 0.20 | 0.47 |
| e | -12 | 0.55 / 0.55 | 0.30 / 0.30 | 0.05 / 0.05 | 0.38 |
| e | -8 | 0.70 / 0.62 | 0.30 / 0.28 | 0.07 / 0.03 | 0.30 |
| e | -4 | 0.95 / 0.47 | 0.68 / 0.25 | 0.50 / 0.00 | 0.23 |
| e | +0 | 0.95 / 0.40 | 1.00 / 0.28 | 0.93 / 0.17 | 0.20 |

"Chance" is the same rule at the same time with nothing injected. Suppression lowers the chance rate by 3–5× and keeps
recovery at ≥ −4 dB relative to the median shot peak; at −8 dB recovery is marginal (0.40 vs 0.10 chance at d) and
below that absent. About a quarter of injected peaks fall inside the gate and are lost by construction.

## 5. COVERAGE

- **Feasible set.** Impact source: the module's source model (one-pole ESD, τ 0.05–10 s; brief §"impact source
  interface"), coupling η over four decades (C2). Propagation: deep-sound-channel arrivals over 1,500–3,700 km with
  modal dispersion of 20–40 s; AGW branch (not touched here). Receivers: IMOS 3315/3376/3250/3274/3275 (single
  hydrophones, 307 s records every 15 min), IMS H01W/H08S/H08N triads (raw data not retrieved — ask Pete).
- **Model's reach.** Templates: one range-independent KRAKEN profile (WOA23 March midpoint, flat 4,610 m), receiver at
  the channel axis (1,200 m) while the IMOS loggers sit at 400–500 m; τ ∈ {0.1, 1, 10}; ranges 1,800–3,000 km. Not
  reached: bathymetry-following paths, the H08S path's 3,704 km other than as one envelope, receiver depth of the
  loggers, AGW arrivals, bearing (single hydrophones). The injected pulses share the template model (model-matched).
- **Proposal's coverage.** Null: 3376 full (5,376 windows), 3274 and 3250 at stride 4 (1,344 each); SNR −15…+30 dB in
  5 dB steps; 120/60 trials per cell (Wilson intervals ±0.09 at P_D 0.5, n = 120). Panels: five digitised panels only.
- **Gaps.** G-W1 (open): no non-model-matched ground-truth test — the brief's San Juan / F-35A / Blackman shots need
  digitised waveforms (block 1) or raw records; until then the matched-filter gain is an upper bound. G-W2 (open):
  the panel null is an emulation from one IMOS site; it is mismatched for the shot-dominated H08S panels. G-W3 (open):
  no null for the H08S suppression residual. G-W4 (declared): secondary-target nulls at stride 4 put α = 0.001 at the
  resolution floor. G-W5 (declared): stochastic-resonance background rate 0.92 per s, not the 1 per s target. G-W6
  (declared): the two-station test is idealised (equal SNR, known lag). ESS is not applicable (no weighted samples).
- **Parameter bounds with sources.** τ from the module's `TAU_GRID` 0.05–10 s (brief); ranges from the run J median
  impact to H01W (2,198 km) ± the bank span; band 5–40 Hz (Kadri's chain, Refresh §5); SNR grid chosen to bracket the
  stage A result (SNR_50 12.6 dB at α 0.05 for D1 at 3376).

## 6. Deviations from the work order

- The ground-truth cases named in the brief (San Juan, F-35A, Blackman shots) were not run: their digitised waveforms
  are block 1's deliverable, which was not available to this track overnight. Test set (a) used synthetic pulses as the
  work order specified; the real-transient templates T_C1/T_C2 of stage A were not added (they are Perth-Canyon
  recordings of unknown source and would not carry a known dispersion).
- Secondary targets at file stride 4 (declared in the pre-registration), N_INJ 60 rather than 120.
- The pre-registered stochastic-resonance target rate was not reached on the fixed grid (0.92 per s).
- The SNR grid was extended after the first run (amendment 1).
- All methods run at 100 Hz (STA/LTA is therefore a 100 Hz variant of the module's D1), declared in the pre-registration.

## 7. Recommendations for the main search pipeline

1. Add the dispersion-aware envelope matched filter (M1b) as the primary screen statistic, STA/LTA beside it; set the
   thresholds per receiver on its own real background exactly as here (null of 60 s window maxima).
2. Build the template bank per receiver from the module's bathymetry-following KRAKEN paths (not the flat profile used
   here), at the receiver's depth, over the run J range span, τ from the `tau90` sidecar; keep a 200 km range step.
3. Before any MH370 statistic, close G-W1: run M1a/M1b on a real long-range arrival with a known source (block 1
   digitisations, or the stage A Curtin events once their sources are identified) and report the loss of gain against the
   model-matched case.
4. For H08S, apply (c1)+(c2) before the screen and report the residual null from adjacent survey hours; carry the
   off-cadence flag with every H08S row.
5. Drop M3, M5, M6, M7 from the pipeline; keep them in the code as negative results behind the method table.

## 8. Charts

- `hydroacoustics-weak-signal-pd-vs-snr.png/.pdf` — P_D against SNR per method, 3376, two false-alarm rates, three τ.
- `hydroacoustics-weak-signal-kadri-panels.png/.pdf` — panels (c) and (a) with every method's p-value trace and the boxes.
- `hydroacoustics-weak-signal-h08s-suppression.png/.pdf` — H08S envelopes before/after suppression, detail, recovery.

Signed: Hydroacoustic Module (weak-signal track, unattended), 22 Oct 2026.
