# Kadri 306.18 deg arrival and Haixun 01: hydroacoustic signals leg (pre-registration Q2 support and Q4)

Written 18 Oct 2026 by the hydroacoustic leg of the Kadri-Haixun conditional test. Pre-registration:
`../preregistration.md` (committed before any statistic; its statistics are unchanged here). Geometry: `../kadri_geom.py`.

**Labels.** PREDICTIVE, NOT CALIBRATED. Source posterior: run J (four route families, 74 seeds, end-of-flight branch
5d060f0 scorer), headline key `D{d} total q=0.333 (C2 silent)`. Run J is not formally declared final; Pete ruled that
enough is done to proceed. Every run J number names its 00:19 option (D0-D5). The primary locality is the 306.18 deg bearing
and its sea-level 7th-arc crossing, **25.732 S 101.369 E**, with the run J rows along it. **Haixun 01 (25.975 S 101.461 E)
is a sensitivity line only** (Pete, 18 Oct).

**Standing hydroacoustic caveats (C1, C2), attached to every level, SNR, detection probability and likelihood ratio below.**
- **C1 propagation:** the propagation model passes a level check against the 2001 airguns but fails a frequency-slope check
  by +10 dB per octave at Cape Leeuwin and +7 at Diego Garcia South. In this leg the transmission loss (TL) is also
  **borrowed**: no committed TL exists on any path from L, so the nearest committed path (impact quantile 975, 31.6 S
  96.8 E) is range-adjusted by 10 log10(r/r_ref), sd 7.9 dB. OHASISBIO TL and noise are H08S proxies, and ridge-grazing
  loss is not included.
- **C2 coupling:** peak radiated mechanical power is not an acoustic source level. Coupling efficiency eta is a declared
  alternative with a prior (swept 1e-4 to 1e-1, three decades; the F-35A RAM-corrected median 2.7e-3 is the airframe anchor),
  not a constant.

Impact-time origin: run J `impacts32` times are seconds after **00:00 UTC 8 Mar 2014** (`compact_impacts.T0 = 1394236800`),
not after 1394232081 as the task brief stated. Checked: restored flame-out median 00:18:00 and impact median about 00:31.
The run J weights reproduce the end-of-flight normalisers `ln Z` of `table-0019-mixture.json` exactly for D0-D5.

---

## 1. Recomputed arrival windows, and what the 13-14 Oct searches covered

The source time is inferred from the H01W reception, so t_X = t_H01W + (d_X - d_H01W)/c. Here c = 1.48 +/- 0.015 km/s on the
range difference, the pick allowance is 5 s, and the window is 1.96 sigma. Bearing (+/-0.5 deg core, +/-1 deg wide) and BTO
(+/-63 us) re-solve the source point. Each window is the union over its source set. Full table: `out/arrival_windows.csv`.
The superseded 26.2 S 101.9 E values are in `out/arrival_windows_superseded_26p2S.csv`.

| Station | Branch T (00:52:03), crossing | Branch C (00:54:30), crossing | Whole strip T / C (R7-60 to R7+250 km, +/-1 deg) | Searched 13-14 Oct | Covered? |
|---|---|---|---|---|---|
| Perth Canyon 3376 | 00:50:44.3-00:51:08.6 | 00:53:11.3-00:53:35.6 | 00:50:39.0-00:51:11.4 / 00:53:06.0-00:53:38.4 | 00:50:44-00:51:10 / 00:53:11-00:53:37 (26 s); 2b windows 00:50:09-00:53:15 / 00:52:36-00:55:42 | **Yes**: crossing windows 100 % inside the 26 s windows; strip windows inside the 2b windows |
| Perth Canyon 3315 | same +/-0.1 s | same | same | none | **No recording covers any window** (confirmed again) |
| H08S (Diego Garcia S.) | **01:14:32.6-01:16:07.5** | **01:16:59.6-01:18:34.5** | 01:09:19.0-01:17:15.1 / 01:11:46.0-01:19:42.1 | 01:16:19-01:17:33 / 01:18:46-01:20:00 | **No**: 0 % overlap at the crossing; strip 11.8 % |
| H01W-H08S time difference | 1,379-1,415 s (crossing); 1,059-1,481 s (strip) | same | | pair-count test 856-1,347 s (stand-in prior); span 1,346-1,710 s declared 13 Oct, but statistics were computed only in the 74 s windows above | crossing **not covered**; strip covered only at 1,059-1,346 s, by the pair-count test |
| OHASISBIO S-SEIR / SW-AMS / MAD / W-KER / N-CRO | 01:07:59-01:09:18 / 01:08:19-01:09:35 / 01:21:46-01:23:36 / 01:21:21-01:23:08 / 01:26:28-01:28:28 | 01:10:26-01:11:45 / 01:10:46-01:12:02 / 01:24:13-01:26:03 / 01:23:48-01:25:35 / 01:28:55-01:30:55 | in `arrival_windows.csv` | never searched by this project (no data in hand) | n/a: compared against Royer's picks (sect. 2) |

Haixun sensitivity: H08S 01:15:20.7-01:16:20.7 (T) and 01:17:47.7-01:18:47.7 (C) (2.8 % overlap with the old windows).
Perth Canyon 00:50:49.0-00:51:08.7 / 00:53:16.0-00:53:35.7 (covered).

**The pre-registered statistics on the uncovered windows** (code unchanged: `kadri_northern_conditional.py`, prereg 6ecbb0a;
only the windows were replaced; `run_window_stats.py`; levels screen 0.3, mark 0.1, report 0.05; primary null = block/window
null of the same panel or recording; results `out/window_statistics.csv`). These are counts of 16 rows per source set and
branch, with 4.8 expected at 0.3 and 0.8 at 0.05:

| Source set | Branch | at 0.3 | at 0.1 | at 0.05 | smallest p |
|---|---|---|---|---|---|
| crossing (core) | T | 5 | 0 | 0 | 0.214 |
| crossing (core) | C | 6 | 2 | 1 | 0.019 (Perth 3376 band power D2, 9.88 dB at 00:53:27.85, the same excursion found 13 Oct) |
| Kadri eq.-4 strip (v 0-250 m/s) | T / C | 2 / 1 | 0 / 1 | 0 / 1 | 0.286 / 0.021 (same Perth excursion) |
| Haixun (sensitivity) | T / C | 5 / 6 | 0 / 3 | 0 / 1 | 0.133 / 0.017 (same Perth excursion) |

**H08S has no new candidate at 0.05 in any corrected window.** In the corrected caption window, H08S now falls INSIDE the airgun
shot train (shots to 01:18:29), so all seven cycle statistics are computable there (7-8 shots). The smallest H08S p is 0.068
(tail residual, caption). The whole-strip H08S windows (476 s, 40-46 shots) hold fewer than one independent block in the
panel, so the block null cannot resolve them. The p = 0 rows in `window_statistics.csv` for `locality_strip_wide`/text are
an artefact of a cross-panel window (panel d null, panel e shots). They are **not testable** with this null and are not
counted. Caveats C1 and C2 do not enter these p-values: these are detection statistics, not levels.

## 2. Royer (2016, LDO-201608): moorings, paths, events, and the 16 s question

Source grade A (primary read, report pp. 2-3, 5-6, 14-15). Machine-readable Table 5: artifact `royer_table5.json`.

- **Recording on 8 Mar 2014 (p. 2):** every OHASISBIO instrument recorded except **NE-AMS (lost on recovery)**: N-CRO, W-KER,
  SW-AMS 1-3, S-SEIR and MAD. The clock drift of MAD and SW-AMS 1 could not be determined (power failure before recovery).
  Synchronisation at deployment in Jan-Feb 2014 bounds that error to well under a second on 8 Mar (drift order 1e-7, my
  inference). Royer notes that records west of 90 E are obscured by seismic-survey shots on 8 Mar.
- **Paths from L (GEBCO_2026 at 15 arc-sec, geodesic; rule declared in `blockage.py`; `out/path_blockage.csv`):**
  H01W, Perth Canyon 3376/3315 and H08S are OPEN. The H08S minimum depth is 1,505 m at 18.4 S 88.1 E, so the path just clears
  the 1,500 m threshold. Every OHASISBIO path is **PARTIAL**: it grazes the Ninety East Ridge or Broken Ridge, with minimum
  depths of 490 m (MAD, at 27.3 S 88.0 E), 927-977 m (SW-AMS), 1,055 m (W-KER), 1,188 m (S-SEIR) and 1,272 m (N-CRO).
  The loss is not computed. H08N (Chagos Bank, 3 m), Portland (land) and Scott Reef (North West Shelf) are BLOCKED. The
  Scott Reef classification uses a long-shelf clause added after the first pass so that it agrees with the module's 9 Oct
  GEBCO result (disclosed).
- **Do any of Royer's 20 events or 6 candidates fit L?** **None.** No event lies in the strip or within 400 km of the crossing;
  the nearest are D1 (785 km) and D2 (821 km) (`out/royer_events_vs_L.csv`). Royer's H01W picks for events 2 and 3 (00:51:38,
  00:51:42) and event 5 (00:54:10) sit 20.7 s and 19.6 s before Kadri's two times. He associated them with sources at
  64.5 S 127.0 E, 57.3 S 89.0 E (icequake) and 49.8 S 133.1 E (bearings from H01W of 169, 209 and 143 deg, not 306 deg).
  Their OHASISBIO picks do not fall in any L window.
- **Picks in the L windows** (`out/royer_picks_in_L_windows.csv`). Under **C**, S-SEIR has one arrival cluster
  (01:11:10.16-01:11:20.83, which Royer used in events 7, 8, 11 and 12) and MAD has 01:25:20.44 (event 9). Both sit inside
  the crossing windows, at +5 to +16 s and +13 s from the window centres. Under **T**, only N-CRO 01:26:24.17 falls inside
  the wide and strip windows. **Exploratory, not pre-registered** (`royer_recombination.py`): a free fit of H01W 00:54:30 +
  bearing 306.18 + S-SEIR + MAD gives **25.80 S 101.46 E** at origin 00:36:42.6, with residuals under 1 s. That point is
  11.8 km from the crossing, and the 95 % box is 26.24-25.34 S, 101.08-101.84 E. The same fit predicts Perth Canyon 3376
  at 00:53:23.3, 4.5 s before the D2 excursion at 00:53:27.85. From Royer's own pick density, the chance that at least two
  of the five recording sites have a pick inside the C crossing windows is **p = 0.113**; it is 0.056 for the Haixun windows
  (sensitivity). Over two branches and two centres the look-elsewhere-corrected value is about 0.2. Royer's picks were made
  to fit his own associations and are not a complete catalogue, so this Poisson rate is approximate. This is **not
  significant** and is not converted into a likelihood term. Under C the same source also predicts SW-AMS 01:11:32,
  W-KER 01:24:50 and N-CRO 01:30:05; Royer lists no picks there. That is **not assessed** (no data, not a non-detection).
- **The possible 16 s GPS-UTC misapplication to H01W:** it **does not change any window**, because the windows use Kadri's IMS
  H01W times (UTC). It **does matter for identification.** With 16 s added back, Royer's H01W picks become 00:51:58.3
  (4.7 s from T) and 00:54:26.4 (3.6 s from C). So Royer very probably picked both of Kadri's arrivals, and his own
  associations (bearing-free) put them far to the south. In the exploratory C fit, using Royer's H01W pick instead
  (with or without the 16 s) puts the point 15-31 km from the crossing, inside L either way. Still unconfirmed; ask Royer before any re-inversion.

## 3. Predicted received level at each station (run J rows in L; caveats C1 and C2)

Source model as `kadri_predictions.py`: SE = eta E rho c/(2 pi) sum_b S_b(1/tau90) 10^(-TL_b/10), 5-40 Hz third octaves,
source depth 10 m. E = energy transferred and tau90 come from the end-of-flight sidecar. SNR is the 1 s 5-40 Hz SPL against
the detector's own background median (Perth 3376 96.2 dB; H01W 101.65; H08S 95.56 dB re 1 uPa^2; OHASISBIO uses the H08S
proxy). P_D comes from the stage-A union curves (alpha 0.05), with IMS = the 3274 curve + 4.8 dB. H08S also uses the
airgun-shot criterion. Strip rows, D2 headline (ESS 172), median SNR in dB at coupling 1e-4 / 1e-3 / 1e-2 / 1e-1
(`out/levels.json`):

| Station | 1e-4 | 1e-3 | 1e-2 | 1e-1 | Detectability statement (T and C) |
|---|---|---|---|---|---|
| H01W | 0.0 | 0.1 | 0.7 | 4.4 | not detectable at eta <= 1e-2; marginal at 1e-1 (C1, C2) |
| Perth Canyon 3376 | 0.1 | 1.0 | 5.4 | 14.1 | not detectable at <= 1e-3; P_D (strip mean) 0.20 at 1e-2, 0.53 at 1e-1 |
| Perth Canyon 3315 | 0.2 | 1.8 | 7.8 | 17.1 | no recording covers the windows, so not assessed |
| H08S | 0.0 | 0.2 | 1.5 | 7.0 | in the shot train: shot-relative level -37.7 / -27.7 / -17.7 / -7.7 dB, P_D 0.007 / 0.008 / 0.075 / 0.29, so not detectable at <= 1e-2 |
| OHASISBIO (S-SEIR ... N-CRO) | 0.0 | 0.1-0.2 | 1.2-1.7 | 6.2-7.7 | not detectable at <= 1e-2; marginal at 1e-1 before ridge loss (proxy noise and TL) |

The rows whose impact time fits Kadri's H01W time (timed subsets, ESS 11 for T and 5 for C, provisional) are quieter than
the strip as a whole. Their median SNR at 1e-1 is 3.2 dB (H01W), 12.0 dB (3376, T) and 14.7 dB (3376, C), because they are
low-energy, shallow arrivals (sect. 5). **Per branch:** for an impact in L, no station is predicted to detect at
eta <= 1e-2 under either T or C, so the corrected-window non-detections carry LR = 1.000 at those couplings (module
convention).

## 4. Is Kadri's arrival level consistent with the predicted H01W level? (Q4; caveats C1 and C2)

Measured on the digitised Fig. 9c (2-20 Hz). The maximum 1 s mean-square excess over the panel median is **0.128 Pa^2 (T,
7.3 dB)** and **0.069 Pa^2 (C, 5.2 dB)**. The peak envelope excess is 1.02 / 0.67 Pa. The panel noise (104.7 dB re 1 uPa^2,
1 s, 2-20 Hz) agrees with Blackman's 2003 H01W level, which supports the Pa scale of the figure.

| Rows (D2) | Coupling needed (energy anchor), 5 / 50 / 95 % | Same with TL 2 sd favourable |
|---|---|---|
| strip, T | 0.0027 / 0.49 / 1.48 | 7e-5 / 0.013 / 0.039 |
| timed T (ESS 11) | 0.43 / 0.91 / 1.48 | 0.011 / 0.024 / 0.039 |
| strip, C | 0.0014 / 0.26 / 0.80 | 4e-5 / 0.007 / 0.021 |
| timed C (ESS 5) | 0.23 / 0.24 / 0.90 | 0.006 / 0.006 / 0.024 |

**Not consistent at the airframe anchor.** The rows that produce Kadri's arrival at the right time need a median coupling of
0.91 (T) and 0.24 (C). That is about 340 and 90 times the F-35A anchor (25 and 20 dB). Even with the TL 2 sd favourable,
they need 9 and 2 times the anchor. Only the most energetic
strip rows, which do NOT fit the timing, reach the level at the anchor. D5 and D0 give the same picture
(`out/conditional_on_h01w_level.json`).

**Implied levels elsewhere, with eta cancelled** (sect. 6 likelihood term). If the arrival is the impact, scaling to the
measured H01W energy predicts Perth Canyon 3376 at **20.8 dB (T)** and **18.2 dB (C)** SNR. The largest values measured in
those 25 s windows were **4.8 dB (T)** and **8.7 dB (C)**. H08S is predicted at a shot-relative level of -1.4 dB (T) and
-4.1 dB (C) (median).

## 5. What kinds of trajectories are selected (Q2 support; provisional, low ESS)

The run J rows weighted by the pre-registered H01W arrival term (`out/timing_consistent_rows.json`; D2 headline):
- **T:** impact 00:33:44-00:34:54 at 26.27-25.60 S. They are 92 % family B (deliberate onset, approach to ditching) and 8 %
  A2. Energy transferred is 0.33-0.92 GJ, tau90 1.6-6.9 s, flight-path angle 3.8-5.8 deg, sink rate 4-8 m/s, ground speed
  61-102 m/s, and impact comes 16-19 min after flame-out. ESS is 11.
- **C:** impact 00:36:26-00:37:42 at 26.29-25.55 S; 55 % B and 45 % A2; 0.42-0.94 GJ; flight-path angle 3.6-5.8 deg; impact
  18-20 min after flame-out. ESS is 5.
- These are long, shallow glides to the surface, not high-speed dives. D0 gives ESS 83 (T) and 19 (C) with the same character.
  With D5, ESS 3.6 (T) and 1.6 (C) is **not assessed at this depth**.
- Q2 cross-check only (the flight leg's number governs): B = sum w_i L_i / L_bg, with log10 B for T of -0.93 (D2), -1.12
  (D5) and -1.15 (D0), and for C of -0.94 (D2), -1.43 (D5) and -1.23 (D0) (core 0.5 deg). These are **lower bounds**,
  because rows beyond +/-1.5 deg or 1,400-1,950 km were not scanned. ESS is 1-135.

## 6. Likelihood terms (provisional; caveats C1 and C2 on every line)

| Hypothesis | Term | Ratio (log10) | Note |
|---|---|---|---|
| H_K^T | corrected-window non-detection, coupling <= 1e-2 | 1.000 (0) | P_D at the false-alarm floor |
| H_K^C | same | 1.000 (0) | the Perth D2 9.9 dB candidate is at chance yield (1 at 0.05 against 0.8 expected) |
| H_K^T | Perth 3376 amplitude given the H01W level, LR = P(arrival SNR <= 4.8 dB) | **0.012 (-1.92)**; 0.056 (-1.25) at TL sd 11.2 | energy anchor primary; peak anchor 0.0025 |
| H_K^C | same, <= 8.7 dB | **0.10 (-0.99)**; 0.19 (-0.73) at sd 11.2 | peak anchor 0.046; if the 00:53:27.85 excursion IS the arrival, it is 9.5 dB weaker than predicted |
| H_K^T | H08S non-detection given the H01W level (shot criterion) | 0.53-0.55 (-0.27) | module construction (1 - P_D)/(1 - 0.0067) |
| H_K^C | same | 0.62-0.64 (-0.20) | |
| H_K^C | Royer S-SEIR + MAD recombination | not converted | exploratory; chance p 0.113 (crossing), 0.056 (Haixun sensitivity) |

The H01W-conditional product (Perth x H08S) is about 0.0065 (log10 -2.2) for T and 0.064 (log10 -1.2) for C. Both terms
rest on the borrowed TL and on Kadri's digitised amplitude. The anchor (energy rather than peak) was chosen after the
peak-anchor run, because the Perth SNR metric is a 1 s energy. Both are shown.

## 7. COVERAGE

- **(a) Feasible set:** any 777-200ER impact that could produce the 306.18 deg arrival: the whole bearing strip from R7-60 to
  R7+250 km, +/-1 deg, with any descent type (dive, spiral, glide, ditching), energy and duration, under every 00:19 option
  and family.
- **(b) Model's reach:** run J, all four strata (waypoints, free, repro-radar, descent-climb). **GAP, declared:** the planned
  descents starting before 00:11 (`run-j-joined-v2` J0011/J2241) were not included, because they have no tau90 sidecar and
  no ruled weight against run J. Their levels are not assessed. Coupling has no dependence on angle, speed or breakup (C2).
  TL is not computed for any L path (C1).
- **(c) Proposal coverage** (ESS within the strip; `out/L_regions.json`): D0 1,750; D1 1,808; D2 172; D3 22; D4 13; D5 45.5.
  The timed subsets: T 83 / 11 / 3.6 and C 19 / 5.4 / 1.6 (D0 / D2 / D5). D3, D4 and D5 timed subsets are too thin and
  are **not assessed at this depth**. Disc ESS (D2): 50 km 278, 400 km 1,099 at the crossing; 50 km 90, 400 km 1,128 at Haixun.
- Family share in the strip (D2): A1 0.06, A2 0.33, B 0.60. The strip mass is 9.6e-4 of run J (the flight leg's number governs).
- Parameter bounds and sources: c = 1.48 +/- 0.015 km/s (module budget, 13 Oct); bearing sigma 0.5 / 1.0 deg (pre-registration);
  BTO +/-63 us (`kadri_geom_output.txt`); eta 1e-4 to 1e-1 (module convention; F-35A anchor `hydroacoustics-ram-tl-check.md`);
  TL sd 7.9 dB (Blackman air9 residual).

## 8. Footnotes carried by every figure and table of this leg

**Short form (ASD-STE100).** The sound data come from a printed figure and from Perth Canyon recordings. The impacts come from
run J. The sound loss on these paths was not calculated: we used the nearest path that has a calculation. The coupling is not
known; we show a range. A test that we did after we saw the data is marked.

**Technical form.** Source posterior run J (74 seeds; headline 'D{d} total q=0.333 (C2 silent)', D2 primary, D0 and D5 beside
it); 00:19 option as named per row; sea-level 7th arc R600 BTO 18,400 us (m0019a). Physics PREDICTIVE, NOT CALIBRATED; TL
borrowed (quantile-975 path), sd 7.9 dB; slope misfit +10/+7 dB per octave (H01W/H08S); coupling 1e-4 to 1e-1. Search case and
ocean model: n/a. Excluded: NE-AMS (lost), H08N, Portland, Scott Reef (blocked), Perth 3315 (no coverage), J0011/J2241 (not in reach).

## Files

Scripts: `geometry_windows.py`, `run_window_stats.py`, `blockage.py`, `gebco.py`, `royer_fit.py`, `royer_recombination.py`,
`scan_runj_L.py` (run under the heavy lock, 00:58-01:24Z), `levels.py`, `analyse_L.py`, `cond_pred.py`, `fig_*.py`.
Outputs in `out/`. Figures in `fig/`: `arrival-windows-corrected.png`, `locality-paths-map.png`, `received-level-detectability.png` (PDF beside each).
The per-row scan files (711 MB) are not committed. They can be regenerated with `scan_runj_L.py`.
