mkdir -p "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/weak_signal"
cat > "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/weak_signal/preregistration.py" <<'EOF'
"""PRE-REGISTRATION, work order 2026-10-21 block 8 (brief Refresh v2 section 7): weak-signal method trials.
Committed to the module branch BEFORE any statistic is computed on hydrophone data (IMOS background, IMOS 8 March
recordings, or the digitised Kadri Fig. 9 traces). Geometry and propagation modelling (template build) are not
statistics on data and may precede this commit. Changes after the first run are amendments, committed and disclosed.

STANCE (Pete, 21 Oct). We detect at the limit. Each method below is a DETECTOR whose false-alarm rate is measured on
REAL background before any MH370 statistic. The known structure that replaces the GPS PRN is the propagation model:
the modal arrival structure (dispersion) of a long-range deep-sound-channel arrival.

SAMPLE RATE. All methods run on the 5-40 Hz band-passed series decimated to FS = 100 Hz (from the module's 500 Hz
decimated volts, imos_noise.read_volts/decimate; 4th-order Butterworth 5-40 Hz zero-phase, then scipy decimate by 5).
The baseline D1 is therefore a 100 Hz variant of imos_detectors D1 (same STA 2 s / LTA 30 s), DISCLOSED.

TEST SET (a): synthetic impact pulses in real IMOS background.
  Background: IMOS public bucket days 20140301-20140307, 20140309-20140315 (8 March excluded; it holds the MH370
  windows), as held under mh370-inputs/hydroacoustics/imos/background (MANIFEST.json, fetched eb83b31).
    PRIMARY target 3376 (Perth Canyon): all 1,344 files.
    SECONDARY targets 3274 (Portland) and 3250 (Scott Reef): every 4th file in sorted order (336 each), for thread
    budget (3 processes). 3315 and 3275 are not in the bucket (as stage A: 3376 stands in for 3315, 3274 for 3275).
  Null: every background file, statistic computed over the whole file, window maxima over non-overlapping 60 s
    windows starting at 32 s (LTA warm-up). Thresholds at per-window false-alarm rates alpha = 0.01 and 0.001 are the
    (1 - alpha) quantiles of the null maxima. With ~5,500 windows at 3376 the 0.001 quantile rests on the top ~6
    values and is reported with that caveat; at the secondary targets (~1,400 windows) alpha = 0.001 is at the
    resolution floor and is reported as such.
  Source pulse: the module's source energy-spectral-density model (imos_stageB_map.band_fraction): flat to
    f_r = 1/tau and f^-2 above, realised as the minimum-phase one-pole response s(t) = exp(-2 pi t / tau) u(t),
    tau in {0.1, 1, 10} s.
  Channel: KRAKEN broadband (coherent FIELD, range-independent) on the representative path from the run J seed-1
    weighted-median impact (37.07 S 89.85 E) towards H01W: WOA23 March (95A4 m03) profile at the path midpoint
    (36.6 S 102.2 E), extended below 4,800 m holding SA and CT; flat bottom at the path's median GEBCO 2026 depth
    (4,610 m), module 'hard' half-space (cp 1650, rho 1.9, 0.5 dB/lambda), Francois-Garrison; source 10 m, receiver
    at the sound-channel axis (1,200 m, where the profile minimum lies) - the IMOS loggers sit shallower (3376 at
    ~410 m), so this is the SOFAR-axis arrival shape, DECLARED. Frequencies 2-48 Hz step 1/64 Hz; ranges 1,800,
    2,200, 2,600, 3,000 km (template bank) and the IMOS/IMS ranges 2,376 (Perth Canyon), 3,700 (H08S) km. The
    bulk delay r/1.482 km/s is removed; the template is the 64 s window that holds the dispersed arrival.
    If the KRAKEN run fails or exceeds 45 min, the fallback is the travel-time-spread template: envelope rising
    linearly over 25 s to an abrupt end (SOFAR crescendo), filled with band-limited noise; the note then says so.
  Injection: range r ~ U(1,800, 3,000) km (continuous; the bank is discrete, so a model mismatch exists), tau
    uniform over the three values, onset uniform inside the file with 70 s margins; the pulse (source * channel at r,
    5-40 Hz) is scaled so that SNR = max over 1 s frames of the pulse's 5-40 Hz level (dB) minus the target's
    background median 1 s 5-40 Hz level (the stage A definition, in decimated-volts units of the target logger) is
    in {-15, -10, -5, 0, 5, 10} dB. N_INJ = 120 per (SNR, tau) cell at 3376; 60 at the secondary targets.
    Detection: the method's statistic maximum over [onset - 10, onset + 50] s exceeds the threshold.
  Scoring: P_D with Wilson 95 % intervals at alpha 0.01 and 0.001 per method, tau and target; SNR_50 from a logistic
    fit in SNR (reported 'not reached' if P_D never crosses 0.5 on the grid); ranking by SNR_50 at alpha 0.01.
  Cross-station stacking (M2) idealisation: the same pulse is injected at the SAME SNR into 3376 and 3274 backgrounds
    at the predicted lag; the null pairs random 3376 and 3274 windows at random lags. DECLARED optimistic (a real
    second station is farther and quieter).

TEST SET (b): digitised Kadri (2024) Fig. 9 traces, H01W panels a (00:27-00:37), b (00:37-00:47), c (00:47-00:57) and
  H08S panels d (01:00-01:10), e (01:10-01:20); vertex polylines from the PDF, ~14.5 vertices/s, resampled by linear
  interpolation to 20 Hz. These are DECIMATED PLOTS of Kadri's 5-40 Hz-filtered waveform, at envelope resolution;
  no waveform phase and no content above ~7 Hz is trusted. Methods run with band 1-9 Hz on the 20 Hz series; the
  matched filter uses the template ENVELOPE only. Null for the panels: IMOS 3376 background passed through a
  plot-decimation emulator (5-40 Hz band-pass, 500 Hz; per 69 ms bin keep the min and max as two vertices;
  linear interpolation to 20 Hz), same window rule. Candidates: every local maximum of each method's statistic
  with p < 0.3 against that null (screen), labelled mark (p < 0.1), report (p < 0.05) [ruling 13 Oct], ranked by p;
  each carries its box label: text time 00:52:03, caption time 00:54:30, poster panel-(a) boxes 00:28:12-00:29:42,
  00:30:24-00:31:54, 00:32:30-00:34:00, 00:35:24-00:36:54, Kadri Table 1 times (+-10 s), or 'unlabelled'.
  Cross-station (M2) on the panels: H08S - H01W lag in [855.93, 1346.50] s (h08s_shot_outliers coincidence rule),
  1 s steps; statistic = max over lag of z(H01W, t) + z(H08S, t + lag).

TEST SET (c): H08S airgun suppression on panels d, e (40 Hz, as h08s_shot_outliers.load).
  Shots: h08s_pulse_energy.pulses rule (envelope maxima, prominence >= 2 x panel median, >= 3 s apart).
  (c1) Shot-train template subtraction: per shot, the local median template (13 neighbours, as h08s_shot_template)
       of the 0.25 s boxcar envelope over [-3, +6] s, scaled to the shot's peak, subtracted; residual envelope.
  (c2) Cyclostationary gating: cadence T = median of 9-11 s intervals, phase = circular median of shot times mod T;
       samples within +-1.5 s of the predicted shot times are excluded.
  (c3) Off-cadence residual: exploratory/off_cadence rule (phase distance > 2 s), on the (c1) residual.
  Metrics: residual RMS envelope reduction in dB against the raw panel (whole panel and shot-free gaps); candidate
  energy surviving: residual envelope maxima with z >= 3 (MAD) listed with times and labels; recovery of the H08S
  template-envelope injected at 6 levels (peak/median shot peak = -20..0 dB, 4 dB steps, 40 onsets each) before and
  after (c1)+(c2).

METHODS (M0a, M0b are the baselines). Each returns a statistic series; a window's score is its maximum.
  M0a STA/LTA (D1 variant): STA 2 s / LTA 30 s preceding, on squared band-passed pressure, every 0.1 s.
  M0b band energy (D2-local variant): 1 s Hann periodogram level in 5-20 and 10-40 Hz minus the median level of the
      preceding 60 s, 3 s running mean, max of the two bands (dB).
  M1a Dispersion-aware matched filter, waveform: normalised cross-correlation of the band-passed data with each of
      the 12 bank templates (4 ranges x 3 tau), max over the bank of |rho|.
  M1b Dispersion-aware matched filter, envelope: as M1a on the 0.5 s-smoothed squared envelope (mean removed over the
      template length), robust to phase mismatch.
  M2  Cross-station envelope stacking at predicted lags (see above).
  M3  Cepstral modal-dispersion fingerprint: real cepstrum of 8 s segments (hop 1 s), energy in the quefrency band Q
      that holds 80 % of the KRAKEN template's own cepstral energy above 0.05 s, as a fraction of the segment's
      cepstral energy above 0.05 s; z-scored against the preceding 60 s.
  M4a Spectral kurtosis (Antoni): STFT 1 s Hann, hop 0.25 s; over 8 s blocks SK(f) = <|X|^4>/<|X|^2>^2 - 2; statistic
      = mean SK over 5-40 Hz.   M4b Time-domain excess kurtosis of the band-passed series in 2 s frames.
  M5  Synchrosqueezed STFT (ssqueezepy if installable, version recorded; else STFT reassignment implemented here):
      over 8 s blocks the fraction of time-frequency energy in the top 5 % of bins, 5-40 Hz; z-scored against the
      preceding 60 s. A dispersed arrival concentrates on modal ridges; broadband local noise does not.
  M6  Bayesian online change-point (Adams & MacKay 2007) on the 1 s band level (dB, 5-40 Hz), Normal-Gamma prior,
      hazard 1/120 s; statistic = probability of a change in the last 3 s, counted only when the level rises.
  M7  Stochastic resonance (EXPLORATORY): bistable x' = x - x^3 + k s(t) + sigma xi on the normalised band-passed
      series; statistic = well-switch rate per 1 s minus its preceding-60 s median; k, sigma fixed so the background
      switch rate is ~1 per s (set on the first 20 background files of 3376, before any injection; disclosed).
  Free parameters are fixed here; nothing is tuned on the injections.

VERDICT RULES (fixed now). A method is 'better than baseline' if its SNR_50 at alpha 0.01 is at least 2 dB below the
  better baseline at the same target and tau, with non-overlapping Wilson intervals at the baseline's SNR_50;
  'equivalent' within +-2 dB; 'worse' otherwise. Recommendations for the main pipeline follow the ranking at 3376
  (the receiver that stands in for Perth Canyon, the loudest predicted IMOS receiver).

CAVEATS carried on every number: C1 (propagation slope misfit, +10.4/+7.4 dB per octave at H01W/H08S), C2 (coupling
  efficiency not calibrated; eta swept over four decades, F-35A upper anchor); digitised data are digitised; the
  synthetic pulse is model-matched to the matched filter's own template family (an upper bound on M1).
"""
from __future__ import annotations

FS = 100
BAND = (5.0, 40.0)
TAUS = (0.1, 1.0, 10.0)
SNRS = (-15, -10, -5, 0, 5, 10)
ALPHAS = (0.01, 0.001)
BANK_RANGES_KM = (1800.0, 2200.0, 2600.0, 3000.0)
EXTRA_RANGES_KM = {"PC3376": 2376.1, "H08S": 3703.5}
INJ_RANGE_KM = (1800.0, 3000.0)
N_INJ = {3376: 120, 3274: 60, 3250: 60}
FILE_STRIDE = {3376: 1, 3274: 4, 3250: 4}
WINDOW_S = 60.0
WARMUP_S = 32.0
INJ_WIN = (10.0, 50.0)
SEED = 20261022
TEMPLATE_T = 64.0
TEMPLATE_DF = 1.0 / 64.0
TEMPLATE_FREQS = (2.0, 48.0)
TEMPLATE_DEPTH_M = 4610.0
TEMPLATE_SD_M = 10.0
TEMPLATE_RD_M = 1200.0
BOTTOM = dict(cp=1650.0, rho=1.9, ap=0.5)
FG = dict(T=4.0, S=34.7, pH=8.0, z_bar=1000.0)
C_BULK_KM_S = 1.482
H08S_LAG_S = (855.93, 1346.50)
PANEL_FS = 20
PANEL_BAND = (1.0, 9.0)
BOCPD_HAZARD = 1.0 / 120.0
P_LABELS = ((0.05, "report"), (0.1, "mark"), (0.3, "screen"))
BOXES = {
    "text time 00:52:03": ("00:51:10", "00:52:50"),
    "caption time 00:54:30": ("00:53:50", "00:55:20"),
    "poster (a) box 1": ("00:28:12", "00:29:42"),
    "poster (a) box 2": ("00:30:24", "00:31:54"),
    "poster (a) box 3": ("00:32:30", "00:34:00"),
    "poster (a) box 4": ("00:35:24", "00:36:54"),
}
EOF
echo written