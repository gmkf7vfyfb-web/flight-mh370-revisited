"""PRE-REGISTRATION — hydroacoustics block 11 (composition), work order 2026-10-21. Run J. Committed before any
likelihood value, upper limit, evidence or Bayes factor is computed. Hydroacoustic Module (composition track), 22 Oct 2026.

STATUS OF EVERYTHING THIS BLOCK WRITES: PREDICTIVE, NOT CALIBRATED. Caveats C1 (propagation slope misfit, +10.4/+7.4 dB per
octave at H01W/H08S; after the TL-recalibration track, a source-term caveat) and C2 (coupling efficiency eta not calibrated;
swept over four decades, F-35A upper anchor 2.1e-4). Both Kadri times are carried: "text time 00:52:03" and "caption time
00:54:30". The composer default (lnL_gated = 0.0 in run-j/primary-tau-eof) does NOT change until architecture rules.

1. RECEIVERS AND GATE (block 7 verdict, hydroacoustics-injection-recovery-run-j.md section 6)
   Gate passed (own real background, P_D(level) measured): IMOS 3376, 3315 (Perth Canyon), 3274, 3275 (Portland).
   Proxy only (IMOS 3376 shaped to Blackman 2003 medians; digitised): H01W, H08S -> SENSITIVITY column only.
   No factor (log-likelihood 0): H08N (blocked), IMOS 3250 (no-information row), AGW branch (not searchable, G-S1),
   OHASISBIO sites and infrasound (nothing held / carries no information).

2. LIKELIHOOD FORM (contract rule 2; block 7 section 6), per impact row i and receiver r:
     L_r(i, eta) = (1 - P_D,r(S_r(i, eta))) + P_D,r(S_r(i, eta)) * m_r(i) / beta_r
   with P_D,r = 0 (so L_r = 1, no information) where the predicted SOFAR arrival at r falls outside a window that the
   searches actually scored (results-data/searches_run_j/imos/imos_windows.csv; panel_windows.csv for H01W/H08S; each
   window [window_start, window_start + 55 s]). The module's log-likelihood per row is
     lnL(i, eta) = sum over gated receivers of ln L_r(i, eta);   lnL_ims_proxy adds the H01W and H08S factors.
   Independence of receiver backgrounds is assumed (declared).

3. DETECTOR, THRESHOLD, BACKGROUND RATE
   Detector M1b (envelope matched filter), the primary of blocks 5 and 7. Primary false-alarm level ALPHA = 0.05 per 55 s
   window: the REPORT level of the 13 Oct ruling (a detection in the likelihood sense is a report-level candidate), resolvable
   at every gated receiver (3315/3275 p floors 2.6e-3/2.8e-3), and the level at which block 7 tabulated eta_50 beside its primary.
   Sensitivities, on the streamed statistics only (not written as columns): ALPHA = 0.3 (screen; the task text's level) and
   0.01 (block 7's primary). DEVIATION from the task text, declared: the screen level is a sensitivity, not the primary,
   because at alpha = 0.3 a third of background windows are candidates and the match term is chance-dominated, and the
   injection's timing recovery is not within +/-0.3 s at the sub-noise levels where P_D(alpha = 0.3) rises (tails to -9 s).
   beta_r = ALPHA / 55 s (per second), by construction of the searches' p = (k+1)/(n+1) on null window maxima
   (block 7 used 60 s windows: a <= 0.4 dB threshold difference, declared).

4. MATCHED CANDIDATES m_r(i)
   Candidate list per receiver = the pre-registered candidate tables of block 5, detector M1b, p <= ALPHA:
     IMOS: imos_candidates.csv (detector == "M1b"); H01W: panel_candidates.csv (detector M1b, p = null A);
     H08S: the suppressed-residual M1b rows only (M1b_res; the raw-panel M1b rows are airgun-survey null-mismatch artefacts,
     searches gap G-S9) -- the raw-panel row 01:12:49 appears in the coincidence table as a labelled variant, not in m_r.
   m_r(i) = sum over candidates c of N(t_c - t_pred,r(i); 0, sigma_t,r(i)) [per second], Gaussian kernel truncated at 4 sigma,
     t_pred,r(i) = t_impact(i) + d_r(i) / c, c = 1.482 km/s (WGS84 geodesic; no refraction or path lengthening),
     sigma_t,r(i)^2 = (d_r c_sd / c^2)^2 + SIGMA_INJ^2 + SIGMA_CLOCK^2, c_sd = 0.006 km/s (module standard),
     SIGMA_INJ = 3 s (block 7 errors.csv: 5-95 % within +/-0.3 s at >= +5 dB, pooled tails to -2.5 s at the H08S proxy),
     SIGMA_CLOCK = 2 s (IMOS logger clock without drift correction, windows gap G-W6; digitised-panel time resolution for
     H01W/H08S). Matching is amplitude-blind (the block 7 form): a candidate louder than any impact could be still matches
     on time -- declared gap G11-1; the candidate's eta_needed is reported beside every matched row.

5. RECEIVED LEVEL S_r(i, eta) (block 7 eta_map chain, second implementation of lhyd._se; TL from the block 2 arc grid)
   S_r = 10 log10(eta F_r / 1e-12) + L_cal(i) + G_r - B_r, with
     F_r = E_i rho c / (2 pi) * sum_b S_b(tau_i) 10^(-TL_b,r(lat_i) / 10) / T_eff,r(tau_i)
     E_i = latent:impact_energy_transferred_j (contact kinetic energy = total KE, an upper anchor; fallback 0.5 m v^2 where NaN,
       counted), tau_i = tau90 from end of flight's tau90_v1.npz (method 1 asserted), clipped to [0.02, 30] s (k = 1; the
       k in {0.5, 1, 2} mapping of per_impact_lnl amendment 3 is not drawn, so the P_D fits' tau cells apply as fitted; declared),
     S_b = third-octave energy fraction for an ESD flat to 1/tau and f^-2 above (imos_stageB_map.band_fraction),
     TL_b,r = results-data/tl_grid_run_j tables via tl_grid_table.load_table (offset 0 arc line, source depth 10 m,
       ridge_policy 'keep', linear in latitude, clamped at 41 S and 20 S, blocked band NaN -> zero energy; IMOS RAM-corrected
       table; IMS raw KRAKEN minus the imp500 RAM delta interpolated in log f, as tl_grid_table.apply_to_model),
     T_eff,r = block 7 summary.json t_eff_s at the nearest tau cell,
     L_cal(i) ~ N(0, 10 dB), one draw per row shared by all receivers (module amendment 2 level term),
       rng = default_rng([20261022, 11, stratum_index, seed]) (supplement: [20261022, 11, 9, 0]),
     G_r = +4.8 dB triad gain at H01W/H08S (labelled), 0 at IMOS; B_r = block 7 background median 1 s 5-40 Hz band level
       (bg_median_level_db + abs_offset_db, dB re 1 uPa). rho c = 1025 * 1500.
   The arc-grid TL is latitude-only (the cross-arc offset is not used: G-TL-X). Attitude (attitude_v1.npz) enters no value:
   the chain's coupling has no attitude dependence (per_impact_lnl amendment 8c); declared.

6. P_D,r(S) = logistic fit of block 7 (results-data/injection_run_j/fits.json, key "<rx>|M1b_mf_envelope|<alpha>|<tau cell>",
   tau cell nearest in log tau): P_D = 1 / (1 + exp(-(S - L50) / slope)). A missing fit gives P_D = 0 (counted). Single
   hydrophone statistics; model-matched templates (block 7 G7-8: an upper bound on real performance).

7. COUPLING EFFICIENCY eta: three fixed values 1e-3, 2.1e-4 (F-35A anchor), 1e-4, and the marginal
     lnL_marg(i) = ln sum_k omega_k exp(lnL(i, eta_k)) over a log-uniform prior on [1e-6, 1e-2] (four decades; the task's
     prior), 41 grid points at 0.1 decade with equal weights omega_k = 1/41. (Fubini: for a single true impact the per-row
     marginal over eta composes exactly with the row weights.)

8. OUTPUT COLUMNS (exchange run-j-gated/<stratum>/seed-N/, float32, row i = row i of impacts32.npy, 74 seeds):
     hydro-lnL-imos-eta1e-3.npy, hydro-lnL-imos-eta2.1e-4.npy, hydro-lnL-imos-eta1e-4.npy, hydro-lnL-imos-margeta.npy,
     hydro-lnL-ims-proxy-margeta.npy (SENSITIVITY: IMOS gated + H01W/H08S proxy factors).
   NaN = not computed (impact time, latitude, longitude, energy or tau not finite), never a default. 0.0 = computed, no
   information (every receiver's predicted arrival outside the scored windows). Rows south of 41 S carry clamped TL (labelled).
   Per seed: COLUMNS.txt, SHA256SUMS; top level README.txt (labels, ruling request, per-seed checks), READY written last.
   Disk rule: df before each seed; below 20 GiB free only the marginalised IMOS column is written and the shortfall declared.

9. STREAMED STATISTICS (full 313.6 M rows, no subsample, plus the northern supplement impacts-ruleB.npz technique >= 1 rows
   with its native lnw:comb weights at every p, mixed by share s_D as the windows note), per 00:19 option D0', D2, D3, D4 and
   p in {0, 0.5, 1} with run_j_windows.ln_weights and p_factor, strata mixed by p_core / K, seeds pooled by evidence:
   (a) per 1-degree latitude band 41-20 S (+ south / north overflow) and eta grid point: sum w, sum w^2, sum w * Pnd(eta)
       with Pnd = product over gated receivers of (1 - P_D) [probability of no detection], sum w * L(eta); IMS-proxy versions.
       -> 95 % UPPER LIMIT on eta two ways: (i) Bayesian: 95 % quantile of the eta posterior under the log-uniform prior,
          posterior proportional to prior * sum_i w_i L(i, eta); (ii) classical exclusion: the eta at which the weighted
          probability of no detection falls to 0.05 ("not reached below 1e-2" when it does not). Per option, p and 5-degree band.
   (b) per 0.5-degree latitude bin: sum w, sum w * exp(lnL_marg) (IMOS and IMS versions) -> evidence three ways
       (ARCHITECTURE rule 5): hydroacoustics alone on a prior uniform along the arc (bin mean of exp(lnL_marg)), combined with
       the core (w * exp(lnL_marg)), and the disagreement: KL(core || combined), shift of the median latitude, shift of the
       mass north of 33 S.
   (c) Kish ESS per option / p / band / family (family4_code) from sum w and sum w^2.
   (d) Z(p) = sum w_p exp(lnL_marg) for the Holland-type unarrested descent Bayes factor p = 1 against p = 0, per option.

10. BAYES FACTORS PER CONDITIONAL (prior stated beside each), likelihood = the gated IMOS term marginalised over eta
    (IMS-proxy version beside it, labelled; for the Kadri row the H01W factor is CIRCULAR because the hypothesis was built
    from that candidate, and is labelled so). For a fixed-source hypothesis H = (lat, lon, t_impact): E and tau are drawn from
    the run J rows within +/-1 degree of lat_H (D0' p 0.5 weights; from the streamed 1-in-125 subsample), L_cal drawn as above,
    n = 20,000 draws; BF = mean_H[L] / Z_runJ with Z_runJ = sum_i w_i exp(lnL_marg(i)) under D0' p 0.5 (and per option).
    Priors stated: run J D0' mass within 100 km of the locus, the implied impact time against the run J impact-time bands.
    (i) Kadri 306.18 degrees row: locus 25.8 S 101.4 E (bearing line x arc), t_impact = t_H01W - d_H01W / c at the text time
        00:52:03 and the caption time 00:54:30.  (ii) Royer B (35.224 S 99.922 E, 00:21:30.6), D1 (25.404 S 93.567 E, 01:04:39.1),
    D2 (27.856 S 93.460 E, 01:06:05.4) as source hypotheses at their own origins and times. (iii) Poster panel (a) boxes 1-4:
    carried as the declared row "source before 00:19:29 or off the arc": the nearest arc locus is the closest approach to H01W
    (28.0 S, 1,563 km); t_impact = box centre - 1,563 km / c; boxes whose implied time precedes 00:19:29 have prior 0 under the
    00:19 log-on and are scored as a what-if only. (iv) Holland-type unarrested descent: BF(p = 1 : p = 0) = Z(1) / Z(0).

11. TWO-SITE COINCIDENCE SUMMARY: the H01W 00:52:04 (M1b p 0.043, text time) x H08S 01:12:49 (M1b p 0.039, p_B 0.30) pair,
    lag 1,245 s, pair count 19 against 8.8 by chance (p_perm 0.019; 36 pair tests), from block 5; the arc locus whose lag
    (d_H08S - d_H01W) / c equals 1,245 s and its implied impact time; the eta at which P_D(H01W) * P_D(H08S) (proxy fits, alpha
    0.05, median E and tau at that latitude, with the +4.8 dB triad gain) reaches 0.5 and 0.05, against the anchor 2.1e-4 and
    the searches' eta_needed (0.026 / 1.5).

12. CHARTS (PNG + PDF, two footnotes): latitude distributions core / combined / hydroacoustics-alone per option (one chart);
    upper limits per band (second chart). No project jargon in titles, axes or legends.

13. COMPUTE AND DISK: 4 single-threaded processes (OMP/OPENBLAS threads 1), one seed per task, chunks of 1 M rows;
    5 columns x 313.6 M x 4 B = 6.27 GB (5 % over the task's 6 GB figure, declared), staged then renamed; READY last.
    No smoke run is quoted as a result.

AMENDMENTS (disclosed below this line as they occur; none at commit).
A1 (22 Oct, before any seed was run): the impacts32 column latent:impact_energy_transferred_j is NaN in every run J row, so E is
   read from the tau90 sidecar's energy_transferred_j, then that column, then 0.5 m v^2 (counted). VALUE CHECK: on three seeds
   (waypoints 1, free 1, descent-climb 1) the sidecar equals 0.5 m v^2 on every row to within 6e-8 relative (float32 rounding),
   as the brief states (energy transferred = total kinetic energy, an upper anchor), so the E values are the same as the
   section 5 definition would have produced through its fallback; the source order changed, the numbers did not.
   CHUNK_ROWS 1 M -> 500 k (memory; no value change).
A2 (22 Oct, after the run): another process held the disk below the 20 GiB floor for part of the run, so 14 seeds were written with the
   marginalised IMOS column only (section 8 rule). B11_TOPUP=1 re-runs such a seed writing all five columns; 4 were topped up (waypoints
   21-24), 10 free-stratum seeds (0.13 % of the mixture mass) remain short (gap G11-2). Values unchanged (deterministic re-run).
A3 (22 Oct, after the run): reduce.py does not write the merged subsample to the exchange (1.1 GB duplicate of the per-seed files).
   Deviation from the task text, declared before the run: alpha 0.05 primary (report level), screen level 0.3 as a sensitivity.
A4 (23 Oct 2026, PRE-REGISTERED before the re-run; parent follow-up after the RAM-along-grid track closed G-TL1 on the offset-0 line):
   (a) IMOS TL for the four gated loggers is read from the corrected drop-in table
       /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables/imos_tl_ram_arc.csv (RAM - KRAKEN_noabs delta along the
       grid; offset-0 line, 10 m source, same loader rule: linear in latitude, clamped 41-20 S, blocked NaN -> zero energy). Rows the RAM
       grid does not cover keep the old rule-2 value inside that file (ram_grid_covered = False; on the offset-0 line only land / shallow
       rows) and their share is reported. The IMS tables are unchanged.
   (b) ONLY the streamed and subsample statistics are re-run (section 9-11): upper limits two ways, P(no detection | eta), evidence three
       ways, families, Holland and conditional Bayes factors, coincidence. The per-row COLUMNS in run-j-gated are NOT rewritten (disk);
       they stay on the OLD IMOS table and are labelled so in the README; they must be rewritten before any composer use.
       New statistics files go to run-j-gated/stats-ramgrid/ (acc.npz, subsample.npz per seed; < 200 MB each).
   (c) Amplitude-aware match, a labelled SENSITIVITY for gap G11-1 (IMOS receivers only; the digitised panels have no comparable
       band energy): m_r^A(i, eta) = sum_c k_t(c) * exp(-0.5 ((log10 E_c - log10 SE_r(i, eta)) / SIGMA_A)^2), where E_c is the candidate's
       observed excess 5-40 Hz band energy (excess_5_40_pa2s, block 5 table), SE_r(i, eta) = eta F_r T_eff,r 10^(L_cal/10) the predicted
       received band energy (same chain), SIGMA_A = 1.0 decade (10 dB: the block 7 level-recovery error, the +/-3 dB IMOS absolute level
       and the calibration-error spread, generous). The kernel only down-weights a match (it is not a calibrated likelihood ratio: no
       background level density is divided out), so the variant is conservative for matches and lies between the full and the
       non-detection-only likelihoods; labelled "amplitude-consistency-weighted (down-weighting only)". Written as additional streamed
       sums (wL_A per band x eta, half-degree wL_A, Holland and conditional BFs); no column.
   Values from the old table are kept in results-data/composition_run_j/ (old/) beside the new ones; the note's addendum tabulates both.
"""
from __future__ import annotations
import pathlib
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
PREPARE = HERE.parent
MODULE = PREPARE.parent
RD = MODULE / "results-data"

BLOCK = 11
SEED = 20261022
RECEIVERS_GATED = ["3376", "3315", "3274", "3275"]
RECEIVERS_PROXY = ["H01W", "H08S"]
RECEIVERS = RECEIVERS_GATED + RECEIVERS_PROXY
METHOD = "M1b_mf_envelope"
ALPHA_PRIMARY = 0.05
ALPHA_SENS = (0.3, 0.01)
ALPHAS = (0.05, 0.3, 0.01)
WINDOW_S = 55.0
SIGMA_INJ_S = 3.0
SIGMA_CLOCK_S = 2.0
KERNEL_TRUNC_SIGMA = 4.0
C_SOFAR, C_SOFAR_SD = 1.482, 0.006          # km/s
RHO_C = 1025.0 * 1500.0
TRIAD_GAIN_DB = 4.8
CAL_L_SD_DB = 10.0
TAU_CLIP = (0.02, 30.0)
TL_SRC_DEPTH_M = 10.0
BANDS_HZ = (5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0)
ETA_FIXED = {"eta1e-3": 1e-3, "eta2.1e-4": 2.1e-4, "eta1e-4": 1e-4}
ETA_ANCHOR = 2.1e-4
ETA_PRIOR = (1e-6, 1e-2)
ETA_GRID = 10 ** np.arange(-6.0, -2.0 + 1e-9, 0.1)       # 41 points, equal weights
OPTIONS = ("D0", "D2", "D3", "D4")
PS = (0.0, 0.5, 1.0)
LAT_BAND_EDGES_1DEG = np.arange(-41.0, -19.99, 1.0)      # 22 edges -> 21 bands; +2 overflow bins (south, north)
LAT_BIN_EDGES_HALF = np.arange(-45.0, -14.99, 0.5)
SUBSAMPLE_EVERY = 125
CHUNK_ROWS = 500_000
N_PROC = 4
DISK_FLOOR_GIB = 20.0
RUN_J = pathlib.Path("/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j")
SUPPLEMENT = pathlib.Path("/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j-supplement/reduced/impacts-ruleB.npz")
EXCHANGE_OUT = pathlib.Path("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated")
STRATA = ["run-j-waypoints", "run-j-free", "run-j-descent-climb", "run-j-repro-radar"]
COLUMNS = ["hydro-lnL-imos-eta1e-3", "hydro-lnL-imos-eta2.1e-4", "hydro-lnL-imos-eta1e-4", "hydro-lnL-imos-margeta",
           "hydro-lnL-ims-proxy-margeta"]
# conditional hypotheses (section 10)
T0 = 1394236800.0
T_0019_LOGON = T0 + 19 * 60 + 29.0
KADRI_LOCUS = (-25.8, 101.4)
KADRI_TIMES = {"text time 00:52:03": T0 + 52 * 60 + 3, "caption time 00:54:30": T0 + 54 * 60 + 30}
ROYER = {"B": (-35.224, 99.922, T0 + 21 * 60 + 30.6), "D1": (-25.404, 93.567, T0 + 64 * 60 + 39.1), "D2": (-27.856, 93.460, T0 + 66 * 60 + 5.4)}
POSTER_BOXES = {"poster (a) box 1": (T0 + 28 * 60 + 12, T0 + 29 * 60 + 42), "poster (a) box 2": (T0 + 30 * 60 + 24, T0 + 31 * 60 + 54),
                "poster (a) box 3": (T0 + 32 * 60 + 30, T0 + 34 * 60), "poster (a) box 4": (T0 + 35 * 60 + 24, T0 + 36 * 60 + 54)}
H01W_CLOSEST_ARC = (-28.0, 1563.0)      # latitude of closest approach of the arc to H01W, distance km (block 2 arc fit)
PAIR = {"H01W": T0 + 52 * 60 + 4, "H08S": T0 + 72 * 60 + 49, "lag_s": 1245.0, "n_obs": 19, "expected": 8.79, "p_perm": 0.0195, "n_pair_tests": 36}
N_DRAWS_BF = 20_000
# amendment A4
TL_TABLE_DIR_RAMGRID = pathlib.Path("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables")
IMOS_TL_FILE_RAMGRID = "imos_tl_ram_arc.csv"
SIGMA_A_DECADES = 1.0
STATS_DIR_RAMGRID = EXCHANGE_OUT / "stats-ramgrid"
