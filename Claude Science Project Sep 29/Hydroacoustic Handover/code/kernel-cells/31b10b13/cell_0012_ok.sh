cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
mkdir -p prepare/ranked_candidates
cat > prepare/ranked_candidates/prereg.py <<'EOF'
"""EXPLORATORY ranking of the run J search candidates (graphics track, 22 Oct 2026) -- PRE-REGISTRATION.

Committed to the module branch BEFORE any score is computed. EXPLORATORY: not part of the frozen searches
(prepare/searches_run_j, block 5) or of the composition (block 11); no detection is claimed; the ranking orders the
candidates "in order of likelihood" under an approximate likelihood ratio, it does not test anything.
PREDICTIVE, NOT CALIBRATED; caveats C1 (propagation slope misfit +10.4/+7.4 dB/octave at H01W/H08S) and C2 (coupling
efficiency not calibrated; eta swept over four decades, F-35A upper anchor 2.1e-4). Both Kadri times: text time 00:52:03,
caption time 00:54:30. H01W/H08S candidates are from DIGITISED Kadri (2024) Fig. 9 panels.

Inputs (read-only): exchange run-j-searches/{imos/imos_candidates.csv, panels/panel_candidates.csv, coincidence/pairs.csv,
coincidence/coincidence_summary.csv, named/table1_verdicts.csv, geometry/sample.npz}; block 7 P_D fits
(results-data/injection_run_j/fits.json); block 11 machinery prepare/composition_run_j/common.py Machinery(imos_ramgrid=True)
(corrected IMOS TL table run-j-tl-grid/tables/imos_tl_ram_arc.csv; IMS TL = grid KRAKEN - RAM delta; +4.8 dB triad gain).

Score per candidate set C (one, two or three candidates at distinct receivers), source posterior = run J geometry sample
(weights w_D0 = 00:19 Held Out (D0'), p = 0.5; D2/D3/D4 weights give sensitivity columns):

  ln LR(C) = ln N(C) - ln B(C)
  N(C) = sum_i w_i * mean_k prod_{c in C} [ P_D,r(c)(snr_i,r(eta_k); alpha = p_c) * K_t(tp_i,r - t_c; sigma_i,r) * A(snr_i,r(eta_k), snr_obs,c) * G_c(i) ]
  B(C) = prod_{c in C} (p_c / 55 s)          (rate density of background candidates at least as extreme, per second)

  - eta_k: the block 11 grid, 41 points log-uniform on [1e-6, 1e-2], equal weights (prior log-uniform).
  - snr_i,r(eta) = Machinery.level_base(lat_i, E_i, tau_i)[r] + 10 log10 eta + Lcal_i, Lcal_i ~ N(0, 10 dB), one draw per row
    (seed SEED). Scott Reef 3250 is not in the machinery (blocked path, no P_D fit): any set containing a 3250 candidate
    gets N = 0, ln LR = -inf, label 'blocked path'.
  - P_D: block 7 logistic fit for the candidate's detector (M1b, M1b_res -> M1b_mf_envelope; D1 -> M0a_stalta;
    BE, Z_res -> M0b_bandenergy), at the tau cell nearest tau90, with L50 and slope interpolated linearly in log10(alpha)
    between the fitted alphas {0.001, 0.01, 0.05, 0.1, 0.3}; alpha = p_c clipped to [0.001, 0.3].
  - K_t: Gaussian timing kernel as block 11 (sigma^2 = (d c_sd / c^2)^2 + 3^2 + 2^2 s^2, truncated at 4 sigma); tp = t_i + d / 1.482 km/s.
    For two or three candidates the joint kernel on the same rows is the lag-consistency density (it replaces two
    independent time terms).
  - A: amplitude-consistency weight of block 11 amendment A4(c): exp(-0.5 ((snr - snr_obs) / 10 dB)^2) (sigma = 1 decade;
    down-weighting only). snr_obs: IMOS from excess_5_40_pa2s (log_se convention of common.match_amp, per row T_eff);
    panels (no 5-40 Hz band on the plot) from eta_needed: snr_obs = base_ref,r + 10 log10 eta_needed, base_ref at the
    searches' reference impact (arc point nearest 37.1 S, E = 1.13 GJ, tau90 = 3.3 s). Disclosed approximation.
  - G (bearing): H01W candidates only, where Kadri Table 1 (named/table1_verdicts.csv, incl. the text-time row) gives a
    bearing within 30 s of t_c: G = mean over those bearings of t3(delta; scale 3.3 deg) / (1/360), delta = observed minus
    the row's back-azimuth at H01W (WGS84). Otherwise G = 1. Sensitivity column for the 00:52:04 candidate with each of
    Kadri's published bearings for the 00:52 signal (306.18 deg, 57 deg) on its own.
  - H08S raw-panel rows (M1b/D1/BE) carry the G-S9 caveat (airgun survey); sensitivity column ln LR_pB uses p_B
    (block-permutation null) instead of p in B for panel rows.

Decomposition reported per row: ln f_time = ln sum_i w_i prod K_t (time / lag density, 1/s^n); ln f_amp_given_time =
ln N - ln f_time (detectability x amplitude x bearing conditional on the time match); ln B.
Also reported: the plain p ranking (min p for singles; max p for pairs, as the searches), eta needed and its multiple of
the F-35A anchor (singles: level match at the reference impact; pairs/triples: eta for prod P_D = 0.5 at alpha 0.05 at the
arc locus of the lag (block 11 coincidence convention), plus the level-match eta of the louder member), the arc locus and
implied impact time (arc crossing of the lag, block 11 method; for IMOS-only pairs too), the posterior-kernel-weighted
source (weighted mean lat/lon/t over the rows in N), bearing consistency, label (searches: screen/mark/report at
p < 0.3 / 0.1 / 0.05 on max p), caveats. Rank = descending ln LR (D0', p 0.5); ties by plain p.

Sets: singles = every row of imos_candidates.csv and panel_candidates.csv; pairs = every distinct row of pairs.csv
(3,494 rows, 3,315 distinct candidate pairs; the family column kept); triples = every set of three candidates at three
distinct receivers whose three pairwise combinations are all rows of pairs.csv (H01W x H08S x IMOS, IMOS x IMOS x IMOS,
H08S x IMOS x IMOS ...).
"""
SEED = 20261022
ETA_LO, ETA_HI, N_ETA = 1e-6, 1e-2, 41
ALPHA_CLIP = (0.001, 0.3)
BEARING_WINDOW_S = 30.0
BEARING_T3_SCALE_DEG = 3.3
SIGMA_A_DB = 10.0
REF_LAT, REF_E_J, REF_TAU_S = -37.1, 1.13e9, 3.3
KADRI_0052_BEARINGS = (306.18, 57.0)
DETECTOR_METHOD = {"M1b": "M1b_mf_envelope", "M1b_res": "M1b_mf_envelope", "D1": "M0a_stalta", "BE": "M0b_bandenergy", "Z_res": "M0b_bandenergy"}
LABELS = ((0.05, "report"), (0.1, "mark"), (0.3, "screen"))
EOF
python -c "import ast,sys;ast.parse(open('prepare/ranked_candidates/prereg.py').read())" && echo ok