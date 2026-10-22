"""PRE-REGISTRATION, work order 2026-10-21 block 7: injection-recovery across the full coupling range at every
unblocked receiver, with real background; P_D against received level -- the gate of contract rule 2.
Committed to the module branch BEFORE any statistic is computed on hydrophone data. Template synthesis (KRAKEN) and
the run J geometry/energy/tau quantiles are not statistics on hydrophone data and may run before or alongside this
commit. Anything changed after the first run is an amendment, committed and disclosed in the results note.

Unattended overnight track (operating note 21/22 Oct 2026). Inputs from finished tracks: run J windows
(results/hydroacoustics-run-j-windows.md, bc99b07/490b6f4/7bb4b08), weak-signal methods
(results/hydroacoustics-weak-signal-methods.md, 78c7e88..59a714b), stage A (item3, eb83b31). Every number carries
caveats C1 (propagation slope misfit, +10.4/+7.4 dB per octave at H01W/H08S) and C2 (coupling efficiency not
calibrated; eta swept over four decades, F-35A upper anchor). Both Kadri times where a time is quoted:
"text time 00:52:03" and "caption time 00:54:30".

RECEIVERS and their BACKGROUNDS (the background DEFINES the false-alarm rate; nothing is tuned on it)
  IMOS 3376 Perth Canyon  -- OWN background: the 14-day set (1-7 and 9-15 March 2014, 1,344 files, MANIFEST.json),
                             all files. PRIMARY logger (N_INJ 120 per cell).
  IMOS 3274 Portland      -- OWN background: the 14-day set, all 1,344 files (N_INJ 60 per cell).
  IMOS 3315 Perth Canyon  -- the 14 GB set does NOT hold 3315 (bucket: PAPCA/3376, PAPOR/3274, PAKIM/3250).
  IMOS 3275 Portland         DEVIATION from the task text, declared. OWN background = the logger's 8 March 2014
                             recordings OUTSIDE its run J request window (SOFAR and AGW union, windows.csv/
                             request_windows.csv): protocol (b) 'same station outside the window'. About 90 files,
                             about 400 null windows, p floor about 0.0025. The co-located logger's 14-day set
                             (3376 for 3315, 3274 for 3275) is the deeper CROSS-CHECK, as stage A did.
  IMOS 3250 Scott Reef    -- declared no-information row (path crosses land; brief Refresh v2 section 4): no P_D.
  IMS H01W Cape Leeuwin   -- PROXY background (raw IMS data not held): IMOS 3376 14-day background spectrally
  IMS H08S Diego Garcia S    shaped so that its median 5-40 Hz PSD equals the Blackman et al. (2004) App. B 2003
                             median PSD of the station (results-data/blackman_noise, DIGITISED), and its absolute
                             median 5-40 Hz band level is the Blackman median. Shaping filter: zero-phase FIR
                             (firwin2, 257 taps at 100 Hz) with gain sqrt(S_Blackman(f) / S_IMOS_median(f)) over
                             5-40 Hz, held constant outside. The temporal statistics (burstiness, 1 s level spread)
                             stay IMOS's: DECLARED PROXY; the spread is reported beside Blackman's q10-q90 and the
                             Kadri (2024) Fig. 9 panel (b) 'no signal' trace (DIGITISED; envelope resolution only,
                             compared through the module's plot-decimation emulator) as the cross-check. 1,344
                             realisations (>= the 400 target of block 10). Single hydrophone: no triad gain in P_D;
                             the +4.8 dB coherent triad gain is applied ONLY in the eta mapping and is labelled.
                             For H08S the airgun suppression (c1)+(c2) of the weak-signal track is a panel-domain
                             tool (digitised shot trains); the 2003 Blackman noise holds no 2014 survey, so no
                             suppression is applied to the proxy; the proxy therefore UNDERSTATES the 8 March 2014
                             H08S noise during the TGS survey. Declared; the H08S P_D is an upper bound on that day.
  IMS H08N                -- BLOCKED for arc impacts (N x 2D corridor, K4): no P_D, row carried as blocked.
  Receiver depth for templates: SOFAR axis 1,200 m (as the weak-signal track; IMOS loggers sit shallower, DECLARED).

SOURCE MODEL
  One-pole source (module band_fraction model): ESD flat to f_r = 1/tau, f^-2 above; realised as the causal
  one-pole low-pass applied to the channel impulse response. tau = end of flight's tau90 (impact_tau_method 1) at its
  run J quantiles 5/50/95 % under 00:19 Held Out (D0'), p = 0.5, computed by inputs.py from a systematic chunk
  subsample of every seed (8 chunks x 50,000 rows per seed, all 74 seeds; declared). Mechanical-to-acoustic factor
  k = 1 (the module's amendment 3 draws k in {0.5, 1, 2}; the 5-95 % tau span already covers that factor; declared).
  Channel: KRAKEN coherent broadband (2-48 Hz, step 1/64 Hz) on the representative profile of the weak-signal track
  (template_profile.npz: WOA23 March at the midpoint of the run J median impact -> H01W path; flat bottom 4,610 m;
  module 'hard' half-space; Francois-Garrison; source 10 m), at the per-receiver ranges below. The bulk delay
  r / 1.482 km/s is removed; the 'h2' time convention (energy builds to an abrupt end) as the weak-signal bank;
  50 s pulse with the energy peak at 35 s. ONE profile for every path: the path-dependent dispersion (Portland shelf,
  Perth Canyon, H08S ridge crossings) is a REACH GAP declared in COVERAGE.
  Ranges: per receiver, injection range r drawn uniformly from the 25 km grid spanning the run J 5-95 % geodesic range
  under D0' p = 0.5 (inputs.py); template bank at the 5/50/95 % ranges x 3 tau = 9 templates per receiver (range
  mismatch up to half the bank spacing exists, as in the weak-signal trial).
  Fallback if KRAKEN fails or exceeds 45 min: the travel-time-spread template (envelope rising linearly over 25 s to an
  abrupt end, band-limited noise fill); the note then says so.

RECEIVED-LEVEL GRID
  Received level is the peak 1 s 5-40 Hz band level of the injected pulse (dB) RELATIVE to the receiver's background
  median 1 s 5-40 Hz band level ('re band noise'), from -20 to +30 dB in 2.5 dB steps (21 levels). It is also
  expressed as an absolute band level: IMOS by the module's calibration chain (dB re 1 uPa^2/Hz = 10 log10(V^2/Hz)
  - G_band - S_h, G from calibration_gain.csv averaged over 5-10/10-20/20-40 Hz, S_h from the logger metadata; the
  band level in dB re 1 uPa over 5-40 Hz and the mean spectral density = band level - 10 log10(35)); IMS by the
  Blackman median. Both numbers are carried in every table.
  The level is set by scaling the unit-energy pulse so that max over 1 s frames of its 5-40 Hz level equals the
  target (no background in that measurement; the stage A / weak-signal definition).

DETECTORS (fixed; nothing tuned on the injections)
  M1b  dispersion-aware ENVELOPE matched filter (PRIMARY): 9 per-receiver templates, 0.5 s squared envelope at 10 Hz,
       local-mean-removed correlation coefficient; statistic = max over the bank. Weak-signal track's recommendation.
  M0a  STA/LTA D1 variant (STA 2 s / LTA 30 s on squared 5-40 Hz pressure at 100 Hz, hop 0.1 s) -- baseline.
  M0b  band energy (1 s level in 5-20 and 10-40 Hz minus the preceding-60 s median, 3 s mean) -- baseline.
  Detection: the statistic's maximum inside [onset - 10 s, onset + 50 s] exceeds the threshold.

FALSE-ALARM LEVELS and the NULL
  Null: every background file, statistic over the whole file, window maxima over non-overlapping 60 s windows from
  32 s (LTA warm-up). Thresholds = (1 - alpha) quantiles of the null maxima at alpha in {0.3, 0.1, 0.05, 0.01} per 60 s
  window (the pre-registered levels of this block) plus alpha = 0.001 as the supplementary level that stands in for a
  family-wise 0.05-0.07 over a 70-window request search (Bonferroni over the H01W 00:25-01:35 request window).
  p floor per receiver = 1 / (number of null windows); alpha below the floor is reported 'not resolvable'.

INJECTIONS
  N_INJ per (level, tau) cell: 120 at 3376; 60 at 3274, 3315, 3275, H01W-proxy, H08S-proxy. Onset uniform inside the
  file with 75 s / 70 s margins; file drawn uniformly from the receiver's background set; seed 20261022 + block 7
  stream (rng = default_rng([20261022, 7, receiver_index])). Thresholds from the null; the P_D of a cell is the share of
  its injections detected, with Wilson 95 % intervals.
  Outputs per receiver, detector, tau, alpha: P_D(level) table; the level at P_D = 0.5 ('L50') and 0.9 from a logistic
  fit in level ('not reached' if no cell crosses 0.5); timing error = time of the statistic maximum minus the pulse
  energy-peak time (onset + 35 s), reported as median, 5-95 % and share within +-5 s, for detected injections;
  amplitude error = (measured peak 1 s band level in [onset, onset + 50 s] minus the background median) minus the
  injected level, median and 5-95 %, for detected injections.

ETA MAPPING (deliverable 6, the detectability statement)
  Per impact row of the run J chunk subsample, per receiver r: received peak 1 s band level
     SPL_r = 10 log10( eta * E * rho c / (2 pi) * sum_b S_b(tau) 10^(-TL_b(lat, r)/10) / T_eff(r, tau) / 1e-12 ),
  E = 0.5 m |v|^2 (contact kinetic energy, the module's convention), rho c = 1025 x 1500, S_b the third-octave band
  fractions 5-40 Hz of the one-pole source normalised over 1-500 Hz (module imos_stageB_map.band_fraction), T_eff(r,
  tau) = template energy / peak 1 s energy measured on this block's own templates, TL_b from (i) the module's RAM-
  corrected table for the IMOS loggers (results-data/ram_check/imos_tl_ramcorr.csv, five quantile paths, linear in
  latitude, clamped) and (ii) the block 2 TL grid pass A for H01W/H08S (mh370-exchange/hydroacoustics/run-j-tl-grid/
  raw/passA/tl_grid.csv, on-arc sources 41-20 S, 0.5 deg; PROVISIONAL until that track's note is published; source
  depth 10 m; 'no_modes'/'land' bands carry no energy); where neither covers a path the row is 'TL pending (grid)'.
  Calibration error: L ~ N(0, 10 dB) per row shared by all receivers (the module's cal_L), reported with and without.
  H01W/H08S add the +4.8 dB triad gain (labelled). SNR_r = SPL_r - median_r; P_D,r from this block's logistic fit
  (M1b, alpha 0.01 primary; 0.05 and 0.001 beside; tau cell nearest the row's tau); P_D(any) = 1 - prod(1 - P_D,r)
  over the unblocked receivers; eta_50 = the eta at which the weighted mean of P_D(any) over the rows equals 0.5,
  by bisection on log10 eta in [1e-8, 1e-2], per 00:19 option (D0', D2, D3, D4) and p in {0, 0.5, 1}, plus P_D(any)
  at the F-35A anchor 2.1e-4 and per eta decade; and eta_50 per 1-degree latitude band (D0', p 0.5).

GATE VERDICT (rule 2): 'yes' for a receiver when P_D(received level) is measured on a declared background by this
  block; 'proxy-only' for H01W/H08S; 'blocked' for H08N; 'no-information' for 3250. The likelihood form is written
  down in the note with the background rate's units; NO likelihood column is written to the exchange by this block.
"""
from __future__ import annotations

FS = 100
BAND = (5.0, 40.0)
LEVELS_DB = [round(-20.0 + 2.5 * i, 1) for i in range(21)]        # re band noise median
ALPHAS = (0.3, 0.1, 0.05, 0.01, 0.001)
ALPHA_PRIMARY = 0.01
TAU_QS = (0.05, 0.50, 0.95)
RANGE_QS = (0.05, 0.50, 0.95)
RANGE_STEP_KM = 25.0
RECEIVERS = ["3376", "3274", "3315", "3275", "H01W", "H08S"]
N_INJ = {"3376": 120, "3274": 60, "3315": 60, "3275": 60, "H01W": 60, "H08S": 60}
BACKGROUND = {"3376": "own-14day", "3274": "own-14day", "3315": "own-8mar-outside-window", "3275": "own-8mar-outside-window",
              "H01W": "proxy-3376-shaped-blackman", "H08S": "proxy-3376-shaped-blackman"}
CROSSCHECK_BG = {"3315": "3376", "3275": "3274"}
PROXY_SOURCE = "3376"
BLOCKED = {"H08N": "blocked (N x 2D corridor K4)", "3250": "no-information row (path crosses land)"}
WINDOW_S = 60.0
WARMUP_S = 32.0
INJ_WIN = (10.0, 50.0)
MARGIN_S = (75.0, 70.0)
SEED = 20261022
BLOCK = 7
TEMPLATE_T = 64.0
TEMPLATE_DF = 1.0 / 64.0
TEMPLATE_FREQS = (2.0, 48.0)
TEMPLATE_DEPTH_M = 4610.0
TEMPLATE_SD_M = 10.0
TEMPLATE_RD_M = 1200.0
BOTTOM = dict(cp=1650.0, rho=1.9, ap=0.5)
FG = dict(T=4.0, S=34.7, pH=8.0, z_bar=1000.0)
C_BULK_KM_S = 1.482
PULSE_LEN_S = 50.0
PULSE_PEAK_S = 35.0
METHODS = ("M1b_mf_envelope", "M0a_stalta", "M0b_bandenergy")
PRIMARY_METHOD = "M1b_mf_envelope"
SHAPING_TAPS = 257
RHO_C = 1025.0 * 1500.0
TRIAD_GAIN_DB = 4.8
CAL_L_SD_DB = 10.0
ETA_ANCHOR = 2.1e-4
ETA_BOUNDS = (1e-8, 1e-2)
OPTIONS = ("D0", "D2", "D3", "D4")
PS = (0.0, 0.5, 1.0)
CHUNKS_PER_SEED = 8
CHUNK_ROWS = 50_000
TL_SRC_DEPTH_M = 10.0
BANDS_HZ = (5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0)
RUN_J = "/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j"
TL_GRID_PASSA = "/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/raw/passA/tl_grid.csv"
EXCHANGE_OUT = "/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-injection"
