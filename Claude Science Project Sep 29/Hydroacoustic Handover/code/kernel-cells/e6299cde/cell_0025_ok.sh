cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/searches_run_j"
cat > preregistration.py <<'EOF'
"""PRE-REGISTRATION, work order 2026-10-21 BLOCK 4 (brief Refresh v2 sections 2, 5, 6; detection-control protocol
section 6 a-f). Committed to the module branch BEFORE any statistic is computed on hydrophone data for block 5.
Everything below is fixed now; changes after the first run are amendments, committed and disclosed in the note.
Model computations that precede this commit and are not statistics on data: geometry.py (weighted run J sample,
lag distributions, back-azimuth distribution, energy/tau summaries) and the windows track's windows.csv.

STANCE (Pete, 21 Oct). Candidates are GENERATED at the screen level and REPORTED with labels; no receiver is dropped.
The power screen is a label column ('eta_needed'), not a gate. Every row carries caveats C1 (propagation slope
misfit, +10.4/+7.4 dB per octave at H01W/H08S) and C2 (coupling efficiency not calibrated; eta swept over four
decades, F-35A upper anchor). Digitised data are labelled digitised. Both Kadri times are carried everywhere:
text time 00:52:03 and caption time 00:54:30. PREDICTIVE, NOT CALIBRATED: no likelihood is produced by block 5.

1. SEARCH WINDOWS (per receiver, from results-data/windows_run_j/windows.csv, commit 490b6f4)
   The 99 % window of an option is [q0.5, q99.5] of its arrival distribution. The SEARCH WINDOW of a receiver and
   branch is the UNION over options {D0', D2, D3, D4} and dive probability p in {0, 0.5, 1} of the 99 % windows,
   SOFAR and AGW branches kept separate (SOFAR primary; AGW rows labelled). Per-option 99 % windows (p = 0.5) are
   kept for the 'in_window' label of each candidate. Windows are written by build_tables() to
   results-data/searches_run_j/prereg_windows.csv in the pre-registration commit.
   Data searched: every IMOS .DAT record (data/imos/recordings.csv, time base convention A as fixed at item 1d)
   that overlaps the SOFAR-or-AGW search window of its logger: 3315, 3376, 3274, 3275 and 3250 (3250 Scott Reef is
   the declared no-information row and is still run). H01W: digitised Kadri (2024) Fig. 9 panels a, b, c
   (00:27-00:57); H08S: panels d, e (01:00-01:20). Decimated plots: envelope resolution, nothing above ~7 Hz trusted.

2. BANDS. 2-5, 5-10, 10-20, 20-40 Hz, and Kadri's 5-40 Hz chain as the comparison condition (Refresh v2 s5).
   IMOS: all five bands on the 500 Hz decimated volts. The analogue high-pass corner of every IMOS logger is 8 Hz
   (LF=008), so the 2-5 Hz band is below the hardware corner: computed, reported, labelled 'below hardware corner'.
   Panels (20 Hz, Nyquist 10 Hz): 2-5 and 5-9 Hz only; 10-20 and 20-40 Hz are NaN ('not computable on the plot').

3. DETECTORS (each returns a statistic series; a window's score is its maximum, timed at the maximum).
   M1b  envelope matched filter (primary screen statistic; weak-signal note, P_D 0.5 at ~7 dB SNR): squared 5-40 Hz
        series smoothed 0.5 s, decimated to 10 Hz; correlation coefficient (local mean removed) with each
        zero-mean unit-energy template ENVELOPE of the weak-signal KRAKEN bank (run-j-weak-signal/templates/
        templates_raw.npz, 'h2' convention, peak at 35 s, 50 s length), max over the bank.
        IMOS bank: ranges {1800, 2200, 2376.1, 2600, 3000, 3703.5} km x tau {0.1, 1, 10} s (18 envelopes).
        Panels: H01W 2200 km, H08S 3703.5 km, x 3 tau (as weak_signal/run_kadri.panel_ctx).
   D1   STA/LTA energy ratio (module detector D1, 100 Hz variant as in the weak-signal trials, DISCLOSED):
        STA 2 s / LTA 30 s preceding, on the squared 5-40 Hz band-passed series (panels: 1-9 Hz), every 0.1 s.
   BE   band energy per band: 1 s Hann periodogram level in the band minus the median level of the preceding
        60 s, 3 s running mean (dB). One statistic per band of section 2.
   H08S suppressed residual (applied BEFORE any H08S screen; weak-signal test set c): shots by the
        h08s_pulse_energy rule (0.25 s boxcar envelope maxima, prominence >= 2 x panel median, >= 3 s apart);
        (c1) local-median shot template (13 neighbours, [-3, +6] s) scaled to each shot's peak and subtracted;
        (c2) cadence gate: samples within +-1.5 s of the predicted shot times excluded (T = median of 9-11 s
        intervals, phase = circular median). Detectors on the residual envelope (10 Hz): M1b_res (bank envelopes
        against the residual envelope) and Z_res (robust z of the 3 s mean residual against the panel's
        shot-free median/MAD). The raw-panel detectors are run too and reported beside them.

4. WINDOWS OF THE STATISTIC. Non-overlapping 55 s windows starting at 32 s (LTA warm-up) in every record or
   panel (an IMOS 307 s record gives 5 windows with no lost coverage after the warm-up; a 600 s panel gives 10).
   The same window rule is used for data and null.

5. BACKGROUNDS (real data; protocol s6 b) and p-values. p = (k + 1)/(n + 1), k = number of null window maxima
   >= the window's score, n = number of null windows. The floor is 1/(n + 1): enlarge the set, never lower the
   threshold.
   IMOS: the same logger on other days from the 14 GB background set (public bucket, 1-7 and 9-15 March 2014,
   8 March excluded): 3376, 3274 and 3250 ALL files; 3315 <- 3376 and 3275 <- 3274 stand-ins (not in the bucket;
   DECLARED). If the three full sets exceed 40 min wall at 3 processes, every 2nd file is used and disclosed.
   Panels: null A (primary; label-setting) = IMOS 3376 background passed through the plot-decimation emulator
   (weak_signal/common.emulate_plot: 5-40 Hz, per 69 ms bin keep min and max, linear interpolation to 20 Hz),
   all files, same window rule, same detectors. Null B (secondary; burst-preserving surrogate of the panel itself)
   = 200 block-permutation surrogates per panel: the 20 Hz series cut into 20 s blocks, blocks permuted
   (numpy default_rng(SEED + panel index)), detectors recomputed, window maxima pooled. p_B is reported beside p_A
   for every panel row; for Z_res (no null-A analogue) p_B sets the label.
   Time slides between receivers: section 8.

6. THRESHOLDS AND LABELS (ruling 13 Oct): screen p < 0.3; mark p < 0.1; report p < 0.05. A candidate ROW is every
   (receiver, detector, band, window) with p < 0.3, timed at the statistic's maximum. Rows with p >= 0.3 are
   counted (n_windows) but not listed. Expected-by-chance counts per level = n_windows x {0.3, 0.1, 0.05} per
   (receiver, detector, band), and summed. The 'strongest' row is the smallest p; ties by statistic.

7. CANDIDATE ROW FORMAT. time_utc; receiver; detector; band_hz; statistic; p (p_A) [and p_B for panels];
   label (report/mark/screen); in_window_sofar and in_window_agw (the options whose 99 % window at p = 0.5
   contains the time; 'union only' if only the p = 0 or 1 windows do; 'outside' otherwise); kadri_label (text time
   00:52:03 box 00:51:10-00:52:50; caption time 00:54:30 box 00:53:50-00:55:20; poster (a) boxes 1-4; Table 1
   time within +-10 s; else 'unlabelled'); eta_needed = the coupling efficiency at which the run J median impact
   would produce the row's observed 5-40 Hz excess energy at the receiver: observed excess band energy in the
   55 s window (Pa^2 s; IMOS volts -> Pa through results-data/imos1d/calibration_gain.csv; panels already in Pa)
   divided by E_med x rho c/(2 pi) x S_5-40(tau_med) x 10^(-TL/10), E_med and tau_med = the D0' weighted medians
   (geometry/energy.json; E is the 'energy transferred' = total kinetic energy, an upper anchor), S_b from
   imos_stageB_map.band_fraction (ESD flat to 1/tau, f^-2 above, normalised 1-500 Hz), TL = the power-mean over
   the 5-40 Hz third-octave bands of the block-2 TL grid pass A (run-j-tl-grid/raw/passA/tl_grid.csv, src depth
   10 m) at the arc source nearest the D0' median impact latitude; where the grid has no finite entry for the
   receiver the column reads 'TL pending (grid)'. caveats = 'C1;C2'; provenance = 'IMOS raw' or 'digitised plot';
   receivers_silent = the other receivers whose search window covers the implied impact and that show no row
   at the same level within the predicted lag interval.

8. TWO-SITE COINCIDENCE (protocol s6 f). Pairs of candidate rows at receivers (i, j), both M1b rows at the screen
   level or better (primary) and any-detector rows (secondary), with t_j - t_i inside the predicted lag interval
   [q0.5 - 30 s, q99.5 + 30 s], the lag quantiles taken as the UNION over options D0', D2, D3, D4 of the D0'/D2/D3/D4
   weighted lag distributions (geometry/lags.csv, c = 1.482 km/s). Pairs tested: H01W x H08S (panels); IMOS x IMOS
   (3315/3376 x 3274/3275, 3315/3376 x 3250, 3274/3275 x 3250; the co-located 3315 x 3376 and 3274 x 3275 record in
   alternating slots and cannot pair); IMOS x H01W and IMOS x H08S. Statistic: N_pairs, and the strongest pair =
   the pair with the smallest max(p_i, p_j). Significance by TIME SLIDES: the receiver-j candidate times are shifted
   by k x 300 s, k = -24..24, k != 0 (48 slides, +-2 h; slides are not independent when the lag interval exceeds
   300 s and the floor is 1/49: DECLARED), N_pairs recounted; p_slide = (#slides with N >= N_obs + 1)/(49);
   expected-by-chance pairs = the mean over slides.

9. NAMED TEST SETS (Refresh v2 s6; all 'windows' are the run J windows of section 1).
   (a) Kadri Table 1, 19 rows, both times for the 306.18 deg row (text 00:52:03 / caption 00:54:30 = 20 tests):
       (i) time inside the H01W 99 % SOFAR window per option (p = 0.5) and the union; (ii) implied source: the
       row's bearing line from H01W intersected with the 7th arc (results-data/windows_run_j/arc_lat_lon.json),
       range r, implied impact time = t - r/1.482 km/s, inside the impact-time 50/90/99 % band per option?;
       (iii) bearing test as kadri_table1_test: log10 BF = log10[ sum_k m_k f(bearing - baz_k) / (1/360) ] with m_k
       the D0' back-azimuth mass in 0.5 deg bins (geometry/bearing_h01w.csv) and f the DEMONSTRATED error model,
       Student-t (3 dof) scaled to sd 3.3 deg; the CLAIMED Gaussian 0.4 deg beside it; verdict 'disfavoured' at
       BF <= 0.1, 'favoured' at BF >= 10, else 'uninformative' (thresholds as kadri_table1_test). (iv) the panel
       rows of section 7 within +-10 s.
   (b) The six poster boxes: per box, the fraction of the H01W SOFAR arrival mass inside the box per option
       (windows track pooled.npz, p = 0.5); the Refresh s6 arithmetic: d_min = closest approach of the arc to H01W,
       earliest arrival from an arc impact after 00:19:29 = 00:19:29 + d_min/1.500 km/s (fastest credible), boxes
       that end before it are carried as 'source before 00:19:29 or off the arc'; the smallest p per detector
       inside each box (section 7 rows and the full statistic series).
   (c) Royer (2016) events B (35.224 S 99.922 E, 00:21:30.6), D1 (25.404 S 93.567 E, 01:04:39.1), D2 (27.856 S
       93.460 E, 01:06:05.4) (research-radar-infrasound-ohasisbio.md, Table 2): distance to the arc; D0' posterior
       mass within 100 and 200 km of the point; latitude against the 99 % band; origin time inside the impact-time
       50/90/99 % bands per option; predicted arrival at every receiver (t + d/1.482, +-3 sd with sd_c 0.006 km/s)
       and whether any section-7 row lies within +-30 s of it (and at the predicted H01W-H08S lag); Royer's own
       H01W picks (Table 5 rows 4; 14, 15) against the arrival predicted from his origin.
   (d) Infrasound: a declared 'carries no information' row with the numbers of research-radar-infrasound-
       ohasisbio.md Q3 (0.85-6.25 GJ = 0.20-1.49 t TNT against a 500 t network threshold, 50 t-1 kt seasonal,
       x4 near the equinox; 33-2,500 times below; IS06 data for March 2014 not public). No statistic.

10. CHARTS (chart rule of 10 Oct; PNG + PDF; two footnotes). (i) Candidate timeline per receiver over the search
    windows, rows at the three levels, both Kadri times and the six poster boxes, records held; (ii) the Table 1
    rows on the H01W window chart with the bearing verdict.

Constants below are the single source of truth for the scripts in this folder.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent.parent
RD = MODULE / "results-data"
EXCH = Path("/Users/pete/Downloads/mh370-exchange/hydroacoustics")
GEOM = EXCH / "run-j-searches" / "geometry"
OUT = EXCH / "run-j-searches"
TEMPLATES = EXCH / "run-j-weak-signal" / "templates" / "templates_raw.npz"
TL_GRID = EXCH / "run-j-tl-grid" / "raw" / "passA" / "tl_grid.csv"
BG_ROOT = Path("/Users/pete/Downloads/mh370-inputs/hydroacoustics/imos/background")
IMOS_ROOT = Path("/Users/pete/Downloads/mh370-inputs/hydroacoustics/imos")
T0 = 1394236800.0

SEED = 20261022
OPTIONS = ["D0", "D2", "D3", "D4"]
OPTION_NAMES = {"D0": "00:19 Held Out (D0')", "D2": "00:19 R600 BTO + BFO (D2)", "D3": "00:19 both BFOs as recorded (D3)", "D4": "00:19 both BFOs, shared start-up offset (D4)"}
PS = [0.0, 0.5, 1.0]
BRANCHES = ["SOFAR", "AGW"]
IMOS = ["3315", "3376", "3274", "3275", "3250"]
IMS = {"H01W": ["a", "b", "c"], "H08S": ["d", "e"]}
PANEL_T0 = {"a": "00:27:00", "b": "00:37:00", "c": "00:47:00", "d": "01:00:00", "e": "01:10:00"}
NULL_STANDIN = {"3315": "3376", "3275": "3274", "3376": "3376", "3274": "3274", "3250": "3250"}
BANDS = [(2.0, 5.0), (5.0, 10.0), (10.0, 20.0), (20.0, 40.0), (5.0, 40.0)]
PANEL_BANDS = [(2.0, 5.0), (5.0, 9.0)]
BAND_LABEL = lambda b: f"{b[0]:g}-{b[1]:g}"
HW_CORNER_HZ = 8.0
FS_D = 500          # imos_noise.decimate output
FS = 100            # band-passed series for M1b / D1
PANEL_FS = 20
PANEL_BAND = (1.0, 9.0)
BAND_MAIN = (5.0, 40.0)
STA_S, LTA_S, HOP_S = 2.0, 30.0, 0.1
ENV_SMOOTH_S, ENV_FS = 0.5, 10
BE_MED_S, BE_MEAN_S = 60, 3
WINDOW_S = 55.0
WARMUP_S = 32.0
IMOS_BANK_RANGES = (1800.0, 2200.0, 2376.1, 2600.0, 3000.0, 3703.5)
PANEL_BANK_RANGE = {"H01W": 2200.0, "H08S": 3703.5}
TAUS = (0.1, 1.0, 10.0)
N_SURROGATE, SURR_BLOCK_S = 200, 20.0
LEVELS = ((0.05, "report"), (0.1, "mark"), (0.3, "screen"))
SCREEN_P = 0.3
C_KM_S, C_SD_KM_S, C_FAST = 1.482, 0.006, 1.500
LAG_PAD_S = 30.0
SLIDE_STEP_S, SLIDE_K = 300.0, 24
PAIRS = [("H01W", "H08S"), ("3376", "3274"), ("3315", "3274"), ("3376", "3275"), ("3315", "3275"), ("3376", "3250"),
         ("3315", "3250"), ("3274", "3250"), ("3275", "3250"), ("H01W", "3376"), ("H01W", "3315"), ("H01W", "3274"),
         ("H01W", "3275"), ("H01W", "3250"), ("H08S", "3376"), ("H08S", "3315"), ("H08S", "3274"), ("H08S", "3250")]
BOXES = {
    "text time 00:52:03": ("00:51:10", "00:52:50"),
    "caption time 00:54:30": ("00:53:50", "00:55:20"),
    "poster (a) box 1": ("00:28:12", "00:29:42"),
    "poster (a) box 2": ("00:30:24", "00:31:54"),
    "poster (a) box 3": ("00:32:30", "00:34:00"),
    "poster (a) box 4": ("00:35:24", "00:36:54"),
}
KADRI_TIMES = {"text": "00:52:03", "caption": "00:54:30"}
TABLE1_TOL_S = 10.0
BEARING_MODELS = {"demonstrated_t3_3.3": ("t", 3, 3.3), "claimed_gauss_0.4": ("gauss", None, 0.4)}
BF_DISFAVOURED, BF_FAVOURED = 0.1, 10.0
ROYER = {"B": (-35.224, 99.922, "00:21:30.6"), "D1": (-25.404, 93.567, "01:04:39.1"), "D2": (-27.856, 93.460, "01:06:05.4")}
ROYER_H01W_PICKS = {"B": ["00:35:54.76", "00:35:44.00", "00:35:54.71"], "D1/D2": ["01:29:42.47", "01:29:40.42", "01:29:40.42", "01:29:42.37", "01:29:42.37", "01:29:40.37"]}
INFRASOUND = dict(impact_energy_gj=(0.85, 6.25), tnt_t=(0.20, 1.49), network_threshold_t=500, seasonal_range_t=(50, 1000),
                  equinox_factor=4, times_below=(33, 2500), is06_range_km_to_royer_points={"D2": 1774, "D1": 1507, "B": 2575},
                  data_status="IMS infrasound for March 2014 not public (EarthScope IM.I06H1 returns no data before 3 Apr 2014)",
                  source="results/evidence-sweep-2026-10-17/research-radar-infrasound-ohasisbio.md Q2-Q3")
RHO_C = 1025.0 * 1500.0
CAVEATS = "C1;C2"


def hms_to_unix(s):
    h, m, sec = s.split(":"); return T0 + 3600 * int(h) + 60 * int(m) + float(sec)


def unix_to_hms(u, dec=0):
    s = u - T0; h = int(s // 3600); m = int((s % 3600) // 60); x = s % 60
    return f"{h:02d}:{m:02d}:{x:0{3 + dec if dec else 2}.{dec}f}" if dec else f"{h:02d}:{m:02d}:{int(x):02d}"


def label_for_p(p):
    for thr, name in LEVELS:
        if p < thr: return name
    return "none"


def build_tables():
    """Section 1 windows and section 8 lag intervals, written into results-data/searches_run_j/ (pre-registration commit)."""
    out = RD / "searches_run_j"; out.mkdir(parents=True, exist_ok=True)
    w = pd.read_csv(RD / "windows_run_j" / "windows.csv")
    w = w[w.receiver != "impact"]
    rows = []
    for rx, g in w.groupby("receiver"):
        for br, gb in g.groupby("branch"):
            lo, hi = gb["q0.5_unix"].min(), gb["q99.5_unix"].max()
            rows.append(dict(receiver=rx, branch=br, kind="union", option="all", p="all", start_unix=lo, end_unix=hi,
                             start=unix_to_hms(lo), end=unix_to_hms(hi), unconverged=int(gb.unconverged.max())))
            for o in OPTIONS:
                r = gb[(gb.option == o) & (gb.p == 0.5)].iloc[0]
                rows.append(dict(receiver=rx, branch=br, kind="option99", option=o, p=0.5, start_unix=r["q0.5_unix"], end_unix=r["q99.5_unix"],
                                 start=r["q0.5"], end=r["q99.5"], unconverged=int(r.unconverged)))
    W = pd.DataFrame(rows); W.to_csv(out / "prereg_windows.csv", index=False)
    L = pd.read_csv(GEOM / "lags.csv")
    lr = []
    for (a, b), g in L.groupby(["rx_a", "rx_b"]):
        lr.append(dict(rx_a=a, rx_b=b, lag_lo_s=g["q0.5"].min() - LAG_PAD_S, lag_hi_s=g["q99.5"].max() + LAG_PAD_S, lag_median_D0_s=float(g[g.option == "D0"]["q50"].iloc[0])))
    pd.DataFrame(lr).to_csv(out / "prereg_lag_intervals.csv", index=False)
    imp = pd.read_csv(RD / "windows_run_j" / "windows.csv"); imp = imp[(imp.receiver == "impact") & (imp.p == 0.5)]
    imp.to_csv(out / "prereg_impact_time_bands.csv", index=False)
    return W


if __name__ == "__main__":
    W = build_tables()
    print(W[W.kind == "union"][["receiver", "branch", "start", "end"]].to_string(index=False))
EOF
python preregistration.py
ls ../../results-data/searches_run_j/; cat ../../results-data/searches_run_j/prereg_lag_intervals.csv | head -5