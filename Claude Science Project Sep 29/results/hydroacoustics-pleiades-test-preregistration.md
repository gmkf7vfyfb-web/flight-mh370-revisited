# Pre-registration: hydroacoustic test of the Pléiades hypothesis (first pass, core (b))

**Run by an architecture stand-in for the hydroacoustics module; module to review.** Written and committed
**before any R_hyd was computed** (architecture ~20:00 and ~20:10 UTC, 10 Oct 2026). At the time of writing, the
Pléiades stand-in's `READY` flag did not exist; three strata of per-impact columns were on disk, and no value in
them had been read. Changes after the first R_hyd are amendments, committed and disclosed.

**Labels carried by every number:** core (b) not converged (split-half); two-tank bookkeeping only; Pléiades/COSMO
transport errors treated as independent (pair correlation pending from ocean transport); GlobCurrent windage as run
(debris-drift audit F1); end-of-flight sweep run by a stand-in (EoF `3c6319f`); hydroacoustic likelihood is a
stand-in construction from the module's exploratory per-sample model, not the module's gated likelihood (its
`impact_log_likelihood` still returns 0.0).

**Settings (Pete, via architecture ~20:30 UTC):** near-limit, not conservative. Loose per-station false-alarm rate
(0.05 per 50 s), triad gain, joint coincidence across stations, the F-35A-calibrated η with RAM-corrected
transmission loss, the full kinetic energy of every impact (so the dive branch carries its 6-11 GJ), and soft
likelihoods with false alarms and chance coincidence **inside** L_hyd, not handled by raising thresholds.

## 1. Statistic

R_hyd = p(hydro data | flight data, H) / p(hydro data | flight data)
      = [Σ_i w_i L_P,i L_hyd,i / Σ_i w_i L_P,i] ÷ [Σ_i w_i L_hyd,i / Σ_i w_i]

(design: `results/pleiades/hydro-conditional-test-design.md`). It is one factor of the Bayes factor for H, reported
alone, never as P(H | data). The Pléiades factor itself stays uninterpretable (no scene-footprint or background term).

- **i:** end of flight's impact rows, `mh370-exchange/end-of-flight/next-run/<stratum>/seed-<k>/impacts.npy`
  (4 strata × 4 seeds, about 3.2 M rows each), read by memmap and column subset only.
- **w_i:** end of flight's own `option_posteriors(run, seed_dir, constraints=("alive",))` from
  `engine/hypotheses/end-of-flight/smoke/displacement_hist.py` (EoF `3c6319f`, sha256 `f964a9b9…`), loaded read-only
  by path. Keys: `r600-bto__other+alive` (00:19 R600 BTO Only), `none__other+alive` (00:19 Held Out),
  `r600_no-offset__other+alive` (00:19 R600 BTO + Raw BFO). Facts after 00:19: variant (a) `+alive`, as ruled
  (~19:10, B), and said so. Holland H1/H2 are excluded (not yet estimable).
- **L_P,i:** `exp(lnL_both_mean)` from the Pléiades columns `mh370-exchange/pleiades/hydro-test/next-run-b/
  <stratum>/seed-<k>/pleiades-lnL.npy` (row-aligned; key `row` checked against the row index). Rows with
  `not_computed = 1` are **excluded from the H-weighted sums and counted**; they stay in the flight-weighted sums
  (they are part of the flight posterior). Sensitivity: excluded from both.
- **L_hyd,i:** section 3.

## 2. What data enter L_hyd, and what is held

| station | data held now | enters L_hyd (primary, scenario A)? | observation used |
|---|---|---|---|
| IMOS 3315, 3376 (Perth Canyon) | raw, 5 loggers + 14 background days (`mh370-inputs/hydroacoustics/imos`) | **yes** | stage A "or" detector at α = 0.05 per 50 s, inside 2b's pre-registered MH370 windows (00:37:14-01:01:45 UTC). Scored coverage 372.5 s (3315) and 450.5 s (3376). **No events.** |
| IMOS 3274, 3275 (Portland) | raw | **yes** | same detector (3275 borrows 3274's thresholds), window 01:03:51-01:24:58 UTC. Scored coverage 350.5 s / 550.1 s. **3274: no events. 3275: two loose events, 01:07:46.6 and 01:20:34.5 UTC** (r = 1.83, 1.20); none at α = 0.005. |
| IMOS 3250 (Scott Reef) | raw | no | path blocked (module ruling); not in the module's logger set |
| H01W (IMS triad) | **raw NOT held** (EarthScope returns no 2014 waveforms; CTBTO vDEC / national data centre request outstanding). Held: Kadri (2024) Table 1, 19 transients with time and bearing (extracted), and Fig. 9 traces 00:27-00:57 (digitised, single channel, pre-filtered) | **yes, soft** | Kadri Table 1 as the event list over Kadri's analysed record, 00:27:00-00:57:00 UTC; background density from the module's own 2a test: 18 events per (998 s × 108.5°) |
| H08S (IMS triad) | raw NOT held; Kadri Fig. 9d-e trace 01:00-01:20 (digitised) | no (excluded) | the trace is dominated by a 9.98 s airgun-like shot train; triggers are shots, and no P_D exists after shot removal in absolute units. Its trigger times were not saved by the module. |
| H08N | none | no | path blocked by the Great Chagos Bank (module, 9 Oct) |
| H11, other IMS | not relevant / not held | no | |
| AGW branch | | no | not assessable: Kadri's 5 Hz high-pass and IMOS's 8 Hz analogue high-pass remove it |

Event lists and coverage were produced by `standin-scripts/extract_imos_events.py`, which runs the module's
`imos_coincidence.rec_events` unchanged; it reads no impact sample. Its output `imos_events_searched.json`
(sha256 `01ae942f…`) reproduces the module's own covered seconds (372.5 / 450.5 / 350.5 / 550.1 s) exactly.

**Joint coincidence across stations** is inside L_hyd: the station terms of section 3 are multiplied per impact row,
and each row has one impact time, one position and one source draw. A pair of events is rewarded only where the
same impact explains both times (and bearings).

## 3. How L_hyd is computed per impact

Code: `results/hydroacoustics-pleiades-test-standin/standin-scripts/lhyd.py` (sha256 **`5000c56e…`**, full hash in section 8). It imports the module's `prepare/`
scripts read-only and repeats the per-sample arithmetic of `prepare/exploratory/near_limits_eof289.py` (sha256
`da86a5e4…`).

**Inputs per row (end of flight's columns):** `unix_s` (impact time), `latitude_deg`, `longitude_deg`,
`kinetic_energy_j` (total kinetic energy, primary; `vertical_kinetic_energy_j` as a sensitivity).

**Source.** Energy flux density at 1 m: SE₁ = η(τ, z_s) · E · ρc / 2π, with ρc = 1025 × 1500. η is the F-35A
(JASDF 79-8705, 9 Apr 2019, H11 path) calibration, **RAM-corrected** (`results-data/ram_check/eta_cal_ramcorr.csv`,
slope 2, template T_C2, E case "mid", station-mean in log). Spectrum: flat to f_r = 1/τ and f⁻² above, split into the
third-octave bands 5-40 Hz (`imos_stageB_map.band_fraction`).
Nuisance per row (module stage C priors), one draw per row, shared by all stations: τ log-uniform 0.05-10 s;
z_s ∈ {2, 10, 30} m; C_site ~ N(0, 10 dB); C_rcv ~ N(0, 10 dB) for the IMOS seabed loggers; for the IMS
SOFAR-axis receivers C_rcv is replaced by N(0, 3 dB) (as in the near-limits analysis).

**Propagation.** Band TL interpolated in impact latitude between the five impact-quantile paths (38.46-31.64 °S) and
**clamped outside that span** (declared; about 20 % of flight-posterior rows lie outside it). Longitude dependence
is not modelled (declared).
- IMOS: KRAKEN adiabatic TL corrected by RAM (`results-data/ram_check/imos_tl_ramcorr.csv`).
- H01W, H08S: KRAKEN on the same paths minus the RAM Δ of the median path (`results-data/near_limits/`).

**Received SNR and P_D.**
- IMOS: SNR = 10 log₁₀(SE / T_eff / 1 µPa²) − (logger's 2b background median) + C_site + C_rcv. P_D = stage A
  logistic fit at α = 0.05, "or" detector, T_C2 (`results-data/stageA/summary_union.json`; 3315 ← 3376, 3275 ← 3274).
- H01W/H08S: SNR on the **proxy** noise (Perth Canyon 3376 background median; no IMS noise is held) + C_site + N(0,3)
  + **4.8 dB triad gain**; P_D = the 3274 stage A fit at α = 0.05 (proxy).

**Arrival.** t_arr = t_impact + d / 1.482 km/s, d the WGS84 geodesic; timing sd = √(10² + (d · 0.006 / 1.482²)²) s
(10 s pick error plus group-speed spread). Bearing: azimuth from the station to the impact; error Student-t, ν = 3,
sd 3.3° (demonstrated; module's `kadri_table1_test.log_t`).

**Station term (soft, near-limit).** With q = coverage × P_D, coverage = t_arr inside a scored segment (IMOS) or
inside 00:27-00:57 (H01W, Kadri), and background events Poisson with density λ:

  L_s,i = (1 − q_s,i) + q_s,i · Σ_k f_s,i(t_k, b_k) / λ_s

- IMOS: λ = 0.05 / 50 s per logger (the operating point's false-alarm rate); f = timing density.
- H01W (Kadri): λ = 18 / (998 s × 108.5°); f = timing density × bearing density.

**L_hyd,i = Π_s L_s,i.** No hard detect / no-detect cut. False alarms and chance coincidences are inside L through λ.

**Declared numerical changes from the module arithmetic:** band fraction tabulated on 600 log-spaced τ values
(maximum relative error 8.6 × 10⁻⁵, measured); mean group speed with its spread carried as timing sd, as the
module's 2a test does.

## 4. Mixing, errors and effective sample size

- **Per seed:** sums S_HL = Σ w L_P L_hyd, S_H = Σ w L_P, S_0L = Σ w L_hyd, S_0 = Σ w (w normalised per seed;
  computed in log space).
- **Strata:** P(s | flight) = core's P(family) (free 0.6948, Davey dynamics + radar 0.1527, descent-climb 0.1376,
  routes 0.0149) for the **fixed-weight mixture**; for the **00:19-re-weighted mixture** (ruling ~19:10, C) it is
  ∝ P(family) × Ẑ_00:19(s, option), where Ẑ_00:19 = Σ w_handoff exp(ℓ_option) / Σ w_handoff, with ℓ_option the
  option's log-likelihood including the `+alive` factor (EoF's `derived_logliks` and `constraint_log_factor`).
  End of flight has not published Ẑ_00:19; this is the stand-in's computation from its columns. Under Held Out, Ẑ
  contains only the `+alive` factor; the ruling's "factor 1" is shown as the fixed-weight mixture.
  Both mixtures are reported, labelled. Within a stratum, seeds have equal weight.
- **Mixture estimate:** p(hyd | flight, H) = Σ_s π_s mean_k(S_HL/S_0)_s,k ÷ Σ_s π_s mean_k(S_H/S_0)_s,k, and
  p(hyd | flight) = Σ_s π_s mean_k(S_0L/S_0)_s,k. (Strata are re-weighted under H by their mean Pléiades
  likelihood, as Bayes' rule requires.)
- **Split-half Monte Carlo error:** replicate k = seed k of every stratum. For each of the 3 balanced partitions of
  the 4 replicates into two halves, ln R is computed on each half; the error is the **RMS over partitions of
  |ln R_A − ln R_B| / 2**. The largest of the three is also reported.
- **ESS:** Kish ESS of w and of w·L_P per seed, summed over seeds per stratum, and for the mixture.

## 5. Reading of ln R_hyd (fixed now; graded)

Point estimate with its split-half error. Positive favours H, negative favours no H.

| \|ln R_hyd\| | reading |
|---|---|
| < 0.5 | within noise |
| 0.5 - 1 | weak |
| 1 - 2.3 | moderate |
| > 2.3 | strong |

The band of ln R ± 2σ (split-half) is stated beside the point reading. A direction is reported at any band.
If the fixed-weight and re-weighted mixtures fall in different bands, both are stated and the result is labelled
"sensitive to stratum weighting".

## 6. Power check (before the result), on `sources.npz`

On the Pléiades source package (about 5,000 rows, defensive mixture, `w_flight` and `w_H`):
1. **Arrival windows** at H01W, H08S, H08N, Perth Canyon (3376) and Portland (3274), SOFAR branch, under H
   (weights w_H) and without H (w_flight), on one chart; with the 1-99 % windows, the overlap coefficient
   OVL = ∫ min(p_H, p_0) dt (1-min bins), and the scored coverage of each station drawn on the chart.
2. **Expected distribution of ln R_hyd**, from 2,000 synthetic data sets drawn under each hypothesis:
   truth = a source row drawn with w_H (under H) or w_flight (without H), with a fresh nuisance draw; per station,
   the signal event occurs with probability q at a time and bearing drawn from the error model, and background
   events are Poisson(λ × coverage) uniform over the station's coverage (H01W: uniform over the module's Table 1
   time-bearing box). ln R is then computed exactly as in section 1, over the source rows with **the truth row left
   out**, each source row replicated with 8 nuisance draws.
3. Scenarios: **A** (primary: data held and scored, as section 2); **A-IMOS** (IMOS terms only); **B** (planning:
   every recorded IMOS segment of the day scored, data held but not yet scored, assumed event-free outside the
   current windows); **C** (planning: A plus raw H01W and H08S triads over the outstanding request windows,
   H01W 00:25-02:20 and H08S 00:45-02:50 UTC, with bearings at both, α = 0.05, λ = 0.001 s⁻¹ uniform in bearing;
   it replaces the Kadri table).
4. **Stop rule (fixed now):** the test is reported as **"not informative with the data held"** and no R_hyd is
   computed if, for scenario A: (i) OVL ≥ 0.5 at every station, **and** (ii) under both hypotheses |E[ln R]| < 0.1
   and P(|ln R| ≥ 0.5) < 0.05. Otherwise the result (section 7) is computed. Scenarios B and C are reported in
   either case, as the statement of what data would make the test informative.

## 7. Result (only if the power check does not stop the test)

R_hyd in this order: 00:19 R600 BTO Only, then 00:19 Held Out, then 00:19 R600 BTO + Raw BFO; each with its
split-half error, the ESS of both weights, the not-computed count, and both stratum mixtures, labelled.
Sensitivities beside the headline (not replacing it): A-IMOS only; vertical kinetic energy; not-computed rows
excluded from both sums. Nuisance random streams: `numpy.random.default_rng([20261010, stratum_index, seed_k])`,
stratum index in core's order (free 0, Davey dynamics + radar 1, descent-climb 2, routes 3).

## 8. Hashes

- Base: `claude-science-sep29` at `31fe9e3` (this file's commit is given in the commit message and the
  architecture post).
- Hydroacoustics module: `hypothesis/hydroacoustics` at `4735abc`, read-only. `near_limits_eof289.py`
  `da86a5e48d8edd0f70be2672f0f571e568e9abb12311e6485ec2ba7131f18f55`; `f35a_eta_calibration.py` `a8b74716…`;
  `imos_stageB_map.py` `63437dc1…`; `imos_preregistration.py` `cc48e1f3…`; `imos_coincidence.py` `17376781…`;
  `kadri_table1_test.py` `db10bfb6…`; `search_windows.py` `1b05492b…`.
- End of flight: `hypothesis/end-of-flight` at `3c6319f`; `displacement_hist.py`
  `f964a9b9b4a42fe21eb4f34edaf1a014650f4c2ef9339cdb3aa75a6040983169`.
- Pléiades: `hypothesis/pleiades` at `74332d0` (the stand-in's wrapper scripts are its own).
- Stand-in: `lhyd.py` `5000c56ec514924cd4767eb065d3fd592273f7f7712a4aee2a6ee0ec8a01094f`;
  `imos_events_searched.json` `01ae942f8b652f4edd72ca19ddfbaab8664300d7d5ec2afb8dc9aff4c5e24127`;
  Kadri Table 1 CSV `73fb8586153af5ca7ebcbd2552828be8f9f18d55c9bfa59e0366812109cde4f9`.

## 9. Known limitations, declared now

1. L_hyd is not the module's gated likelihood. IMS noise and IMS P_D are proxies; the H01W term assumes Kadri's
   Table 1 is a complete event list at a threshold comparable to the proxy P_D, which is doubtful (17 of 18 distinct
   Table 1 times are not visible in his own published traces, module note 2a).
2. TL depends on latitude only and is clamped outside 38.46-31.64 °S.
3. The IMOS scored coverage (350-550 s per logger) was set by 2b's windows from an earlier stand-in impact time
   (00:24:37 ± 3 min). Core (b) arrivals run to about 02:05 (Perth Canyon) and 02:30 (Portland), so most of the
   predicted arrival mass is unscored. Scoring the rest is scenario B; it needs no new data.
4. Compute: at most 2 threads, no heavy lock.

— Modular Architecture (stand-in for Hydroacoustics), 10 Oct 2026
