# Hydroacoustics: arrival windows on run J (block 3, timing half; block 6 timeline charts)

*Hydroacoustic Module (run J windows track), 22 Oct 2026 03:11 UTC. Unattended overnight run of work order 2026-10-21. Pre-registration `prepare/run_j_windows.py` committed at bc99b07 before any run; amendment 1 (plumbing only: subprocess workers instead of a process pool, the sandbox forbids POSIX semaphores) disclosed in the docstring. Data: `results-data/windows_run_j/` on `hypothesis/hydroacoustics` (windows.csv, coverage.csv, request_windows.csv, ess.json, run.json); per-seed histograms in `mh370-exchange/hydroacoustics/run-j-windows/` (153 MB).*

**Status: PREDICTIVE, NOT CALIBRATED.** These are timing windows only. No level, no detection and no likelihood is claimed; caveats C1 (propagation slope misfit, +10.4/+7.4 dB per octave at H01W/H08S) and C2 (coupling efficiency not calibrated; η swept over four decades) apply to any level statement built on them. The level/power-screen half of block 3 waits for the TL grid of the parallel track. Both Kadri times are carried everywhere: "text time 00:52:03" and "caption time 00:54:30".

## Inputs and method

- Impact set: end of flight **run J**, four strata, 74 seeds, 313,599,968 rows (seeds used: {'run-j-waypoints': 24, 'run-j-free': 18, 'run-j-descent-climb': 16, 'run-j-repro-radar': 16}), impacts32 SHA256 recorded in run.json; convergence accepted as a pass by project ruling, 16 Oct 2026. Plus the **northern supplement** `run-j-supplement/reduced/impacts-ruleB.npz` (2,408,038 rows; the 1,277,785 rows with technique ≥ 1 used; technique 0 rows are the production set already covered by the strata).
- 00:19 options and weights: end of flight's two-factor table (`smoke/option_table_0019.py`), "total q = 1/3 (C2 silent)" cells, re-implemented from the stored columns: ln w = ln(weight/Σ) + ln(1 − P_breakup) + loglik_D + ln(0.75·e^{C1} + 0.25·e^{C2}); C1 = Erlang log-on lag density + `unpowered` constraint, C2 = −ln W + `unpowered` + no-later-log-on survival. D0′ holds the 00:19 values out but keeps the log-on-cause and survival factors, exactly as EoF's D0 cell and the supplement's `lnw:comb/D0`. Strata mixed by p_core (0.9982/0.0013/0.0003/0.0002) × Ẑ_D, seeds pooled by evidence (EoF's pooling). Supplement share s_D = its `lnw:comb` mass: D0 0.125, D2 0.111, D3 0.105, D4 0.105.
- Dive probability p ∈ {0, 0.5, 1}: the module's existing push-over re-weighting (×2p where pushover_to_surface = 1, ×2(1−p) where drawn but not to the surface, ×1 where not drawn). Supplement rows keep their native weights at every p (no pushover_to_surface column: **gap**, size s_D).
- Arrival = impact time + WGS84 geodesic / c. SOFAR c ~ N(1.482, 0.006) km/s; AGW c ~ U(1.40, 1.50) km/s (assumed, not modelled). No refraction, blockage or path lengthening. 2 s grid, 23:00 7 Mar to 06:00 8 Mar; mass beyond the grid: 0 in every row. Quantiles 0.5/5/25/50/75/95/99.5 %; request window [q0.5 − 10 min, q99.5 + 20 min] rounded to 5 min; UNCONVERGED flag when the per-seed q0.5 or q99.5 spread over the 24 waypoints seeds exceeds 5 min (then the window is widened to the seed envelope).
- Receivers: H01W, H08S, H08N (triad means), IMOS 3315, 3376, 3274, 3275, 3250 (Scott Reef: declared no-information row), and the six OHASISBIO 2014 sites (chart rows, nothing held).

## Impact time (pooled, p = 0.5)

| Option | q0.5 | q5 | q50 | q95 | q99.5 | 99th-pct northern latitude | Kish ESS |
|---|---|---|---|---|---|---|---|
| 00:19 Held Out (D0′) | 00:20:03 | 00:20:29 | 00:32:07 | 00:46:41 | 00:49:35 | 27.5°S | 1,336,700 |
| 00:19 R600 BTO + BFO (D2) | 00:20:21 | 00:20:31 | 00:31:47 | 00:46:13 | 00:48:51 | 27.0°S | 107,226 |
| 00:19 both BFOs as recorded (D3, Holland H2 data) | 00:20:13 | 00:20:23 | 00:21:31 | 00:36:07 | 00:38:03 | 28.5°S | 5,671 |
| 00:19 both BFOs, shared start-up offset (D4, Holland H1 data) | 00:20:01 | 00:20:09 | 00:21:03 | 00:35:33 | 00:37:41 | 27.5°S | 25,414 |

The 99th-percentile contour sits at 27–28.5°S in every option, so the operating note's rule 7 makes **20°S** the latitude span for every spatial product.

## Arrival windows, SOFAR branch, p = 0.5 (median; 90 % interval = q5–q95; request window)

| Receiver | 00:19 Held Out | 00:19 R600 BTO + BFO | 00:19 both BFOs as recorded | 00:19 both BFOs, shared start-up offset |
|---|---|---|---|---|
| Cape Leeuwin H01W | 00:55:43 (00:44:03–01:11:19); req 00:25–01:35 | 00:55:11 (00:44:21–01:10:25); req 00:25–01:35 | 00:46:25 (00:41:57–01:00:39); req 00:25–01:25 | 00:45:51 (00:41:07–00:59:59); req 00:25–01:25 |
| Diego Garcia South H08S | 01:13:47 (01:02:01–01:29:11); req 00:50–01:55 | 01:13:35 (01:02:07–01:28:21); req 00:50–01:55 | 01:03:27 (01:01:57–01:18:15); req 00:50–01:50 ⚠tail | 01:02:53 (01:01:33–01:17:37); req 00:50–01:45 |
| Diego Garcia North H08N | 01:16:05 (01:04:19–01:31:27); req 00:50–01:55 | 01:15:53 (01:04:23–01:30:37); req 00:50–01:55 | 01:05:43 (01:04:15–01:20:31); req 00:50–01:50 ⚠tail | 01:05:09 (01:03:51–01:19:53); req 00:50–01:45 |
| IMOS 3315 Perth Canyon | 00:57:33 (00:45:33–01:13:23); req 00:25–01:40 | 00:56:59 (00:45:55–01:12:27); req 00:25–01:40 | 00:48:25 (00:43:21–01:02:43); req 00:25–01:30 ⚠tail | 00:47:51 (00:42:27–01:02:03); req 00:25–01:25 |
| IMOS 3376 Perth Canyon | 00:57:35 (00:45:35–01:13:25); req 00:25–01:40 | 00:57:01 (00:45:55–01:12:29); req 00:25–01:40 | 00:48:27 (00:43:21–01:02:45); req 00:25–01:30 ⚠tail | 00:47:53 (00:42:29–01:02:05); req 00:25–01:25 |
| IMOS 3274 Portland | 01:21:31 (01:10:07–01:36:37); req 00:55–02:00 | 01:21:03 (01:10:19–01:35:53); req 00:55–02:00 | 01:11:51 (01:08:29–01:26:01); req 00:55–01:50 | 01:11:17 (01:07:51–01:25:23); req 00:55–01:50 |
| IMOS 3275 Portland | 01:21:29 (01:10:07–01:36:35); req 00:55–02:00 | 01:21:01 (01:10:17–01:35:51); req 00:55–02:00 | 01:11:49 (01:08:29–01:25:59); req 00:55–01:50 | 01:11:17 (01:07:49–01:25:21); req 00:55–01:50 |
| IMOS 3250 Scott Reef | 01:14:31 (01:01:39–01:31:01); req 00:40–01:55 ⚠tail | 01:13:59 (01:01:51–01:29:55); req 00:35–01:55 ⚠tail | 01:05:49 (00:59:31–01:20:11); req 00:35–01:50 ⚠tail | 01:05:15 (00:58:21–01:19:33); req 00:35–01:45 ⚠tail |
| OHASISBIO NEAMS | 00:42:43 (00:30:19–00:57:55); req 00:15–01:25 | 00:42:17 (00:30:19–00:57:07); req 00:20–01:25 | 00:32:33 (00:30:11–00:46:53); req 00:15–01:15 ⚠tail | 00:31:19 (00:29:53–00:46:09); req 00:15–01:15 |
| OHASISBIO SWAMS | 00:50:03 (00:36:57–01:05:17); req 00:25–01:40 ⚠tail | 00:48:53 (00:36:59–01:03:59); req 00:25–01:40 ⚠tail | 00:40:27 (00:36:35–00:54:09); req 00:25–01:30 ⚠tail | 00:38:37 (00:36:19–00:53:33); req 00:20–01:30 ⚠tail |
| OHASISBIO SSEIR | 00:53:17 (00:40:25–01:08:21); req 00:25–01:40 ⚠tail | 00:52:27 (00:40:27–01:07:27); req 00:25–01:40 ⚠tail | 00:43:37 (00:40:11–00:57:11); req 00:25–01:30 ⚠tail | 00:41:59 (00:39:57–00:56:29); req 00:25–01:30 ⚠tail |
| OHASISBIO MAD | 01:09:33 (00:56:51–01:24:33); req 00:45–01:55 | 01:08:51 (00:56:51–01:23:41); req 00:45–01:50 | 00:59:51 (00:56:37–01:13:31); req 00:45–01:45 ⚠tail | 00:58:21 (00:56:21–01:12:47); req 00:45–01:40 |
| OHASISBIO WKER | 01:03:13 (00:50:09–01:18:29); req 00:35–01:55 ⚠tail | 01:02:03 (00:50:09–01:17:09); req 00:35–01:55 ⚠tail | 00:53:39 (00:49:45–01:07:19); req 00:35–01:45 ⚠tail | 00:51:49 (00:49:31–01:06:43); req 00:35–01:40 ⚠tail |
| OHASISBIO NCRO | 01:09:27 (00:56:23–01:24:39); req 00:40–02:00 ⚠tail | 01:08:21 (00:56:23–01:23:25); req 00:40–02:00 ⚠tail | 00:59:53 (00:56:01–01:13:25); req 00:40–01:50 ⚠tail | 00:58:03 (00:55:45–01:12:49); req 00:40–01:45 ⚠tail |

⚠tail = UNCONVERGED upper or lower tail (per-seed spread of q0.5 or q99.5 > 5 min over the 24 waypoints seeds); the request window is widened to the seed envelope. These are the distant receivers (Scott Reef, the OHASISBIO sites) and the low-ESS D3 rows; the H01W/H08S rows under D0′ and D2 are converged.

## Dive probability sensitivity (H01W and H08S, SOFAR, D0′): median and 90 % interval

| p | H01W | H08S | Perth Canyon 3376 |
|---|---|---|---|
| 0 | 00:57:11 (00:44:37–01:11:19) | 01:15:09 (01:02:05–01:29:11) | 00:59:03 (00:46:23–01:13:25) |
| 0.5 | 00:55:43 (00:44:03–01:11:19) | 01:13:47 (01:02:01–01:29:11) | 00:57:35 (00:45:35–01:13:25) |
| 1 | 00:53:13 (00:43:29–01:11:19) | 01:11:39 (01:01:59–01:29:11) | 00:54:55 (00:44:59–01:13:25) |

The AGW branch (c ~ U(1.40, 1.50) km/s, assumed) ends 0–5 min later than SOFAR at every receiver; its rows are in windows.csv (branch = AGW).

## Recommended request windows (union over options with ESS ≥ 1,000, padded −10/+20 min, p = 0.5; ticks for p = 0, 1 on the chart)

| Receiver | SOFAR | AGW |
|---|---|---|
| Cape Leeuwin H01W | 00:25–01:35 | 00:25–01:40 |
| Diego Garcia South H08S | 00:50–01:55 | 00:50–01:55 |
| Diego Garcia North H08N | 00:50–01:55 | 00:50–02:00 |
| IMOS 3315 Perth Canyon | 00:25–01:40 | 00:25–01:40 |
| IMOS 3376 Perth Canyon | 00:25–01:40 | 00:25–01:40 |
| IMOS 3274 Portland | 00:55–02:00 | 00:55–02:05 |
| IMOS 3275 Portland | 00:55–02:00 | 00:55–02:05 |
| IMOS 3250 Scott Reef | 00:35–01:55 | 00:35–02:00 |

All four options clear the ESS ≥ 1,000 gate at p = 0.5 (D3 at 5,671 is the lowest), so the unions include Holland H1/H2 data treatments for the first time on run J. Against the module's earlier raw-data request to Pete (H01W 00:25–02:20, H08S/H08N 00:45–02:50): the run J windows lie inside it; no change to the request is needed.

## Held-data coverage: fraction of the predicted SOFAR arrival mass inside a recording the module holds (p = 0.5)

| Receiver | held | 00:19 Held Out | 00:19 R600 BTO + BFO | 00:19 both BFOs as recorded | 00:19 both BFOs, shared start-up offset |
|---|---|---|---|---|---|
| Cape Leeuwin H01W | Kadri 2024 Fig. 9 panels a-c, digitised (30 min) | 54 % | 58 % | 84 % | 88 % |
| Diego Garcia South H08S | Kadri 2024 Fig. 9 panels d-e, digitised (20 min) | 69 % | 85 % | 99 % | 99 % |
| Diego Garcia North H08N | nothing held (0 min) | 0 % | 0 % | 0 % | 0 % |
| IMOS 3315 Perth Canyon | IMOS 307 s records (data/imos/recordings.csv) (511 min) | 42 % | 53 % | 62 % | 66 % |
| IMOS 3376 Perth Canyon | IMOS 307 s records (data/imos/recordings.csv) (511 min) | 27 % | 20 % | 16 % | 15 % |
| IMOS 3274 Portland | IMOS 307 s records (data/imos/recordings.csv) (736 min) | 28 % | 17 % | 14 % | 13 % |
| IMOS 3275 Portland | IMOS 307 s records (data/imos/recordings.csv) (491 min) | 33 % | 38 % | 27 % | 28 % |
| IMOS 3250 Scott Reef | IMOS 307 s records (data/imos/recordings.csv) (511 min) | 38 % | 48 % | 42 % | 52 % |

- H01W: Kadri's three published 10-min panels (00:27–00:57, digitised) cover 54 % of the predicted arrival under D0′ and 84–88 % under the Holland data treatments, which pull the impact earlier. The whole of the 99 % window is 00:39–01:14, so the published traces do not reach the late half of the held-out window.
- H08S: panels d–e (01:00–01:20) cover 69 % (D0′) to 99 % (D4). H08N: nothing held. OHASISBIO: nothing held; NEAMS, nearest the arc, was lost on recovery.
- IMOS: 307 s records every 15 min give a 34 % duty cycle; the phase of the schedule relative to the arrival matters (3315 at 42 % vs 3376 at 27 % under D0′, loggers 100 m apart with offset start times). Blackman et al. (2004) is 2003 data: n/a.
- Royer's H01W picks (Table 5): event B 00:35:44–00:35:55 falls before the 0.5 % quantile of every option's H01W arrival (00:37:57–00:40:07 over options and p); C2/D1/D2 picks at 01:29–01:35 fall after the 99.5 % quantile (01:14:23 under D0′, earlier in the other options). On timing alone none of the four Royer events is consistent with a run J impact by the deep sound channel (the 16 s H01W clock question in the evidence sweep does not change this).

## Charts (results/, PNG + PDF, two footnotes each)

- `hydroacoustics-run-j-timelines`: per receiver, impact-time bands, arrival intervals per option (SOFAR filled, AGW hollow), recordings held, poster boxes, both Kadri times, Royer picks, held fraction.
- `hydroacoustics-run-j-timelines-ohasisbio`: the six 2014 sites, "no recordings held", Royer picks.
- `hydroacoustics-run-j-request-windows`: panel-(c)-style request windows per receiver.
- `hydroacoustics-run-j-publication-coverage`: impact-time densities per option and the Fig. 9 spans converted to impact time along the arc 38→20°S. The earlier chart of this name could not be located in the repository or the artifact store by title; this one is built from its description in the work order (declared).

## COVERAGE

- **(a) Feasible set:** every impact that end of flight's run J prior reaches, from 00:19:37 to 01:15:56 and north to the supplement's extent; both log-on causes; both existence constraints as EoF's total cell.
- **(b) Model's reach:** straight-line (geodesic) arrival with a single group speed per row; AGW speed assumed. Reach gaps: no refraction or bathymetric path lengthening (G-N2 ridge paths), no blockage (H08N is BLOCKED for arc impacts even in the N×2D corridor, K4; its windows are geometric only), no modal dispersion. These shift arrivals by at most a few minutes on open paths and do not affect the ±10/+20 min padding.
- **(c) Proposal's coverage (Kish ESS, mixture incl. supplement; per family share/ESS):**

| Option / p | ESS | strata-only ESS | supplement ESS | supplement share | A1 share/ESS | A2 | B | outside B |
|---|---|---|---|---|---|---|---|---|
| D0/p0 | 955,255 | 1,105,859 | 44,296 | 0.125 | 0.167 / 440,429 | 0.337 / 345,178 | 0.495 / 374,954 | 0.001 / 3,738 |
| D0/p0.5 | 1,336,700 | 1,946,624 | 44,296 | 0.125 | 0.167 / 441,507 | 0.338 / 496,262 | 0.494 / 537,224 | 0.001 / 3,748 |
| D0/p1 | 934,086 | 1,069,185 | 44,296 | 0.125 | 0.167 / 442,588 | 0.339 / 335,287 | 0.493 / 365,716 | 0.001 / 3,758 |
| D2/p0 | 61,101 | 50,643 | 16,350 | 0.111 | 0.229 / 52,612 | 0.236 / 18,441 | 0.534 / 23,072 | 0.001 / 578 |
| D2/p0.5 | 107,226 | 92,213 | 16,350 | 0.111 | 0.230 / 52,613 | 0.236 / 33,196 | 0.533 / 42,763 | 0.001 / 579 |
| D2/p1 | 69,841 | 58,287 | 16,350 | 0.111 | 0.231 / 52,614 | 0.236 / 19,619 | 0.532 / 27,055 | 0.001 / 579 |
| D3/p0 | 3,184 | 2,600 | 1,762 | 0.105 | 0.090 / 412 | 0.395 / 2,183 | 0.514 / 1,185 | 0.001 / 14 |
| D3/p0.5 | 5,671 | 4,707 | 1,762 | 0.105 | 0.091 / 411 | 0.401 / 4,661 | 0.507 / 2,114 | 0.001 / 14 |
| D3/p1 | 2,944 | 2,401 | 1,762 | 0.105 | 0.093 / 411 | 0.406 / 2,649 | 0.500 / 975 | 0.001 / 14 |
| D4/p0 | 17,908 | 14,763 | 6,895 | 0.105 | 0.250 / 2,289 | 0.343 / 22,492 | 0.405 / 7,034 | 0.002 / 100 |
| D4/p0.5 | 25,414 | 21,215 | 6,895 | 0.105 | 0.249 / 2,290 | 0.344 / 36,733 | 0.405 / 18,126 | 0.002 / 100 |
| D4/p1 | 22,574 | 18,755 | 6,895 | 0.105 | 0.248 / 2,291 | 0.344 / 21,869 | 0.406 / 13,674 | 0.002 / 100 |

- Gaps and status: (G-W1) supplement rows not re-weighted for p ≠ 0.5 (no pushover_to_surface column) — open, size 10.5–12.5 % of the mass; fix = ask end of flight to add the column to the reduced file. (G-W2) D3 at p = 1 has ESS 2,944 and family A1 ESS ≈ 410 under D3 — estimable but thin; report as such. (G-W3) tails UNCONVERGED at the distant receivers and in low-ESS rows (flagged per row). (G-W4) the stratum mixture rests on p_core from core's hand-off (waypoints 0.998): the free/descent-climb/repro strata carry 0.1 % of the mass, so the result is effectively conditional on the waypoints family. (G-W5) AGW speed is an assumption. (G-W6) the IMOS held intervals use the logger clock start times (start_logger) without drift correction. (G-W7) the level/power-screen half of block 3 is not in this note (TL grid pending).
- Parameter bounds with sources: c_SOFAR 1.482 ± 0.006 km/s (module standard, search_windows.py prereg 55eb191); AGW 1.40–1.50 km/s (stated allowance); q = 1/3 and W = 3,898 s (EoF rulings 12 Oct); Erlang lag (shape 8, scale 14.875 s, log-on 1394237969.416) from each seed's run.json.

## done / next / blocker

- done: pre-registered and computed run J arrival windows (4 options × 3 p × 2 branches × 14 receivers), held-data coverage, request windows, four charts, this note.
- next: level/power-screen half of block 3 when the TL grid arrives; then block 4 pre-registration of searches using these windows.
- blocker: TL grid from the parallel track (block 2) for the level half; nothing else.
