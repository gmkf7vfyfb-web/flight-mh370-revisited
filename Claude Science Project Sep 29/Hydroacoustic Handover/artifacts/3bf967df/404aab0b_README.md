# Kadri H01W signal and Haixun 01 contact — FLIGHT leg (pre-registration Q1–Q3, Q4 undersampling)

18 Oct 2026. Leg owner: end-of-flight module session. Pre-registration: `../preregistration.md` (followed; statistics unchanged; deviations listed below).
**Source posterior: end-of-flight run J** (four route strata, 74 seeds, mixed by core P(family) 0.9982 / 0.0013 / 0.0003 / 0.0002) and, as a
separate labelled arm, **run-j-joined-v2** (planned descents with onset before 00:11, arm V2, waypoints only, seeds 1–21, D0–D4).
Every number carries its 00:19 option. Headline cells: `D{d} total q=0.333 (C2 silent)`. Run J is not formally declared final; Pete ruled (18 Oct) that enough is done to proceed.
Physics is PROVISIONAL (interim pitch-down, piloted turns, residual roll P(left) 0.8, round-3 free-flight laws). No search, drift, ocean or hydro-propagation term enters anything here.
**Primary locality: the 306.18 deg H01W bearing and its sea-level 7th-arc crossing X = 25.732 S 101.369 E (R7 = 1,591.3 km).** Haixun 01 (25.975 S 101.461 E) is a
secondary sensitivity line only (Pete, 18 Oct). Time origin: compact `T0_unix_s` = 1394236800 (00:00:00 UTC 8 Mar 2014), read through end of flight's loader; the 1394232081 origin was never used.

## Result in one paragraph

Run J *can* produce the Kadri arrival: 209,210 (00:52:03) and 222,410 (00:54:30) impact rows lie within 6 sigma of both arrival time and bearing, and 56,261 rows from 37,825
production parents end within 50 km of X 13–18 min after 00:19:29. But the satellite-conditioned flight posterior puts little mass there: 0.06–0.11 % in the bearing strip and
0.55–0.79 % within 200 km of X, depending on the 00:19 option. Against the pre-registered chance-transient background (18 transients / 21 min / 140 deg), the Bayes factor is
**below 1 under every 00:19 option and both readings**: ln B = -5.59 (T) / -5.58 (C) with the 00:19 data held out (D0), -5.14 / -5.09 with the R600 BTO+BFO (D2),
and −3.7 to −7.2 over D3–D5 and both bearing sigmas; arm V2 gives −4.5 to −9.6. A one-arrival background (no rate) adds ln 18 = +2.89, which is still below 0 everywhere.
**All of these are UNCONVERGED**: the conditional effective samples are 166 (D0, T) and 278 (D1, T) at best, 14–36 for the caption reading, and 1–27 under D2–D5, against
the end-of-flight thresholds (30 effective parents per seed for a Bayes factor, 1,000 effective impacts for a map). The trajectories selected by the sound are
**unpowered, piloted glides after fuel exhaustion**: final flame-out 00:16:30–00:18:30, 15–20 min aloft after flame-out, mostly families B (deliberate descent before
exhaustion, ~0.7) and A2 (~0.3), A1 ≈ 0. Most have turns (median heading change about 400–900 deg). Under the two-burst options (D3–D5) every selected row is an arrested dive
(−15,000 to −22,000 ft/min at 00:19:37) followed by such a glide. Powered flight after 00:19:29 (log-on cause other than fuel exhaustion) is in reach but carries ≤ 1 % of
the conditional. A targeted re-simulation (Q4) was designed, built and smoke-tested, but **not run**: the Mac had 15–18 GiB free against the 25 GiB floor.

## Q1 — run J posterior mass in the locality L (primary: bearing strip and discs around X)

Strip = 1,531.3–1,841.3 km from H01W, |cross-track| ≤ range × tan 1 deg. Share = posterior mass in the region (pooled, all four strata). ESS = Kish effective sample size of the
impacts in the region; eff. parents = (Σ_p M_p)² / Σ_p M_p². C1 share = fraction of the region's mass from the fuel-exhaustion log-on cause (q = 1/3, p(C1) = 0.75).
Seed SE = standard error of the share over the 24 waypoints seeds.

| 00:19 option | region | mass share | Kish ESS | eff. parents | A1/A2/B in region | C1 share | seed SE of share |
|---|---|---|---|---|---|---|---|
| D0 held out | strip | 0.00085 | 1763 | 657 | 0.16/0.28/0.55 | 0.990 | 0.00010 |
| D0 held out | X50 | 0.00093 | 2014 | 736 | 0.21/0.26/0.53 | 0.991 | 0.00010 |
| D0 held out | X100 | 0.00294 | 5262 | 1650 | 0.15/0.28/0.56 | 0.989 | 0.00029 |
| D0 held out | X200 | 0.00679 | 11661 | 2751 | 0.13/0.30/0.56 | 0.988 | 0.00061 |
| D0 held out | X400 | 0.01193 | 17691 | 3941 | 0.13/0.31/0.55 | 0.987 | 0.00099 |
| D1 R600 BTO | strip | 0.00064 | 1803 | 894 | 0.16/0.30/0.54 | 0.990 | 0.00010 |
| D1 R600 BTO | X50 | 0.00077 | 2227 | 1050 | 0.19/0.27/0.54 | 0.990 | 0.00010 |
| D1 R600 BTO | X100 | 0.00245 | 6242 | 2262 | 0.14/0.30/0.56 | 0.989 | 0.00031 |
| D1 R600 BTO | X200 | 0.00553 | 14891 | 4176 | 0.13/0.31/0.56 | 0.987 | 0.00058 |
| D1 R600 BTO | X400 | 0.00904 | 22615 | 6337 | 0.12/0.32/0.56 | 0.986 | 0.00083 |
| D2 R600 BTO+BFO | strip | 0.00097 | 175 | 168 | 0.06/0.33/0.60 | 0.996 | 0.00021 |
| D2 R600 BTO+BFO | X50 | 0.00111 | 278 | 259 | 0.10/0.28/0.61 | 0.994 | 0.00017 |
| D2 R600 BTO+BFO | X100 | 0.00369 | 336 | 315 | 0.07/0.31/0.62 | 0.996 | 0.00051 |
| D2 R600 BTO+BFO | X200 | 0.00792 | 718 | 618 | 0.07/0.33/0.60 | 0.996 | 0.00082 |
| D2 R600 BTO+BFO | X400 | 0.01249 | 1099 | 925 | 0.07/0.33/0.60 | 0.996 | 0.00102 |
| D3 both BFOs raw (Holland H2 data) | strip | 0.00078 | 22 | 22 | 0.01/0.46/0.53 | 0.993 | 0.00028 |
| D3 both BFOs raw (Holland H2 data) | X50 | 0.00105 | 19 | 19 | 0.02/0.49/0.49 | 0.992 | 0.00032 |
| D3 both BFOs raw (Holland H2 data) | X100 | 0.00290 | 39 | 39 | 0.02/0.37/0.61 | 0.994 | 0.00069 |
| D3 both BFOs raw (Holland H2 data) | X200 | 0.00736 | 50 | 50 | 0.01/0.31/0.68 | 0.995 | 0.00120 |
| D3 both BFOs raw (Holland H2 data) | X400 | 0.01026 | 83 | 83 | 0.01/0.36/0.62 | 0.995 | 0.00127 |
| D4 both BFOs start-up offset (Holland H1 data) | strip | 0.00110 | 13 | 13 | 0.50/0.22/0.27 | 0.993 | 0.00045 |
| D4 both BFOs start-up offset (Holland H1 data) | X50 | 0.00149 | 22 | 21 | 0.48/0.23/0.28 | 0.986 | 0.00050 |
| D4 both BFOs start-up offset (Holland H1 data) | X100 | 0.00416 | 47 | 47 | 0.41/0.23/0.36 | 0.990 | 0.00095 |
| D4 both BFOs start-up offset (Holland H1 data) | X200 | 0.00761 | 123 | 118 | 0.35/0.27/0.38 | 0.991 | 0.00136 |
| D4 both BFOs start-up offset (Holland H1 data) | X400 | 0.01203 | 217 | 195 | 0.38/0.27/0.36 | 0.992 | 0.00187 |
| D5 R600 BFO + R1200 BFO offset | strip | 0.00077 | 46 | 45 | 0.04/0.35/0.60 | 0.994 | 0.00015 |
| D5 R600 BFO + R1200 BFO offset | X50 | 0.00117 | 46 | 45 | 0.03/0.35/0.62 | 0.993 | 0.00029 |
| D5 R600 BFO + R1200 BFO offset | X100 | 0.00345 | 95 | 91 | 0.01/0.39/0.60 | 0.994 | 0.00061 |
| D5 R600 BFO + R1200 BFO offset | X200 | 0.00666 | 221 | 213 | 0.03/0.40/0.56 | 0.995 | 0.00088 |
| D5 R600 BFO + R1200 BFO offset | X400 | 0.00996 | 374 | 362 | 0.03/0.39/0.57 | 0.995 | 0.00093 |

Mass in L is almost the same under every option (0.06–0.11 % in the strip), but the **effective sample in the strip is below 200 for D2–D5** (175, 22, 13, 46): under-sampled (Q4).
By route stratum (conditional on stratum), the strip holds 0.085 % (waypoints), 0.198 % (free), 0.141 % (repro-radar) and 0.116 % (descent-climb) under D0 (`q1-by-route-stratum.csv`).
P(strip | family) under D0 is 0.080 % (A1), 0.071 % (A2), 0.096 % (B).

Impact time, final flame-out and minutes aloft after flame-out for impacts in L (5/50/95 %, minutes after 00:00 UTC; `q1-q4-timing-quantiles.csv`):
D0 strip: impact 20.5/30.5/45.5, flame-out 16.5/17.5/18.5, aloft 2.5/13.5/28.5 min; D2 strip 21.5/31.5/44.5, 16.5/17.5/18.5, 2.5/13.5/27.5; D4 strip 20.5/20.5/30.5,
16.5/17.5/18.5, 2.5/2.5/14.5. The share still powered at impact is 0.3–0.7 %. The final flame-out window 00:16:30–00:18:30 is set by the log-on lag model under C1 (C1 carries ≥ 99 %).

Arm V2 (planned descent before 00:11, joined at 00:11):

| 00:19 option | region | mass share | Kish ESS | eff. parents | A1/A2/B in region | C1 share | seed SE of share |
|---|---|---|---|---|---|---|---|
| D0 joined V2 | strip | 0.00060 | 594 | 195 | 0.35/0.55/0.08 | nan | 0.00012 |
| D0 joined V2 | X50 | 0.00070 | 712 | 239 | 0.42/0.47/0.09 | nan | 0.00012 |
| D0 joined V2 | X200 | 0.00527 | 1556 | 670 | 0.28/0.58/0.13 | nan | 0.00074 |
| D1 joined V2 | strip | 0.00048 | 572 | 256 | 0.31/0.59/0.08 | nan | 0.00014 |
| D1 joined V2 | X50 | 0.00061 | 744 | 298 | 0.39/0.49/0.09 | nan | 0.00014 |
| D1 joined V2 | X200 | 0.00429 | 2813 | 1146 | 0.27/0.61/0.11 | nan | 0.00077 |
| D2 joined V2 | strip | 0.00075 | 30 | 29 | 0.16/0.68/0.14 | nan | 0.00044 |
| D2 joined V2 | X50 | 0.00083 | 42 | 40 | 0.32/0.51/0.14 | nan | 0.00025 |
| D2 joined V2 | X200 | 0.00590 | 199 | 163 | 0.21/0.67/0.11 | nan | 0.00128 |
| D3 joined V2 | strip | 0.00050 | 6 | 6 | 0.05/0.87/0.08 | nan | 0.00021 |
| D3 joined V2 | X50 | 0.00084 | 4 | 4 | 0.03/0.86/0.05 | nan | 0.00077 |
| D3 joined V2 | X200 | 0.00452 | 8 | 8 | 0.02/0.91/0.05 | nan | 0.00171 |
| D4 joined V2 | strip | 0.00113 | 7 | 7 | 0.66/0.30/0.02 | nan | 0.00037 |
| D4 joined V2 | X50 | 0.00178 | 10 | 10 | 0.74/0.22/0.03 | nan | 0.00059 |
| D4 joined V2 | X200 | 0.00891 | 40 | 37 | 0.59/0.33/0.04 | nan | 0.00228 |

## Q2 — per-row acoustic likelihood and Bayes factor (all 470 M run J rows scored, not only rows in L)

L_i = N(t_obs − t_i − d_i/c; 0, s_t) N(306.18 − b_i; 0, s_b), c = 1.48 km/s, s_t² = (d_i 0.015/1.48²)² + 25 s², WGS84 geodesics from H01W (34.8903 S 114.1426 E).
B = Σ w_i L_i / λ, λ = 18 / (1,260 s × 140 deg) (Kadri Table 1 rate, pre-registered). The "one arrival" column uses λ = 1/(1,260 × 140) (sensitivity only).
Per-seed ln B is the same ratio within each waypoints seed.

| 00:19 option | branch, s_b | ln B (rate background) | ln B (one arrival) | conditional ESS | eff. parents | share in strip / X200 | A1/A2/B | C1 share | per-seed ln B min/median/max |
|---|---|---|---|---|---|---|---|---|---|
| D0 held out | T, 0.5 deg | -5.53 | -2.64 | 83 | 81 | 0.80 / 1.00 | 0.00/0.25/0.75 | 0.994 | -6.6 / -5.6 / -4.6 |
| D0 held out | T, 1.0 deg | -5.59 | -2.70 | 166 | 156 | 0.61 / 0.99 | 0.00/0.26/0.74 | 0.993 | -6.5 / -5.7 / -4.8 |
| D0 held out | C, 0.5 deg | -5.73 | -2.84 | 19 | 19 | 0.50 / 0.96 | 0.00/0.21/0.79 | 0.991 | -8.0 / -6.1 / -4.2 |
| D0 held out | C, 1.0 deg | -5.58 | -2.69 | 14 | 14 | 0.32 / 0.95 | 0.00/0.19/0.80 | 0.993 | -7.4 / -6.1 / -3.7 |
| D1 R600 BTO | T, 0.5 deg | -6.04 | -3.15 | 135 | 131 | 0.67 / 1.00 | 0.00/0.33/0.67 | 0.993 | -6.9 / -6.2 / -4.7 |
| D1 R600 BTO | T, 1.0 deg | -6.06 | -3.17 | 278 | 263 | 0.49 / 1.00 | 0.00/0.33/0.66 | 0.992 | -7.0 / -6.2 / -4.8 |
| D1 R600 BTO | C, 0.5 deg | -6.00 | -3.11 | 17 | 17 | 0.51 / 1.00 | 0.00/0.26/0.73 | 0.992 | -8.8 / -6.4 / -4.4 |
| D1 R600 BTO | C, 1.0 deg | -6.05 | -3.16 | 36 | 36 | 0.37 / 1.00 | 0.00/0.31/0.69 | 0.992 | -8.4 / -6.4 / -4.8 |
| D2 R600 BTO+BFO | T, 0.5 deg | -5.04 | -2.15 | 11 | 11 | 0.55 / 1.00 | 0.00/0.08/0.92 | 0.999 | -9.0 / -5.9 / -3.2 |
| D2 R600 BTO+BFO | T, 1.0 deg | -5.14 | -2.25 | 24 | 24 | 0.42 / 1.00 | 0.00/0.12/0.88 | 0.999 | -7.6 / -5.7 / -3.6 |
| D2 R600 BTO+BFO | C, 0.5 deg | -5.05 | -2.16 | 5 | 5 | 0.81 / 1.00 | 0.00/0.45/0.55 | 1.000 | -12.8 / -6.5 / -2.4 |
| D2 R600 BTO+BFO | C, 1.0 deg | -5.09 | -2.19 | 14 | 14 | 0.55 / 1.00 | 0.00/0.32/0.68 | 1.000 | -8.0 / -5.6 / -2.9 |
| D3 both BFOs raw (Holland H2 data) | T, 0.5 deg | -3.68 | -0.79 | 1 | 1 | 0.97 / 1.00 | 0.00/0.03/0.97 | 1.000 | -27.7 / -11.7 / -0.4 |
| D3 both BFOs raw (Holland H2 data) | T, 1.0 deg | -4.21 | -1.32 | 1 | 1 | 0.89 / 1.00 | 0.00/0.09/0.91 | 1.000 | -21.8 / -10.0 / -1.0 |
| D3 both BFOs raw (Holland H2 data) | C, 0.5 deg | -6.98 | -4.09 | 2 | 2 | 0.75 / 1.00 | 0.00/0.27/0.73 | 1.000 | -30.2 / -12.4 / -4.1 |
| D3 both BFOs raw (Holland H2 data) | C, 1.0 deg | -6.53 | -3.64 | 3 | 3 | 0.35 / 1.00 | 0.00/0.62/0.38 | 1.000 | -21.1 / -10.0 / -3.8 |
| D4 both BFOs start-up offset (Holland H1 data) | T, 0.5 deg | -7.23 | -4.34 | 15 | 15 | 0.58 / 1.00 | 0.00/0.51/0.49 | 1.000 | -14.2 / -8.4 / -5.3 |
| D4 both BFOs start-up offset (Holland H1 data) | T, 1.0 deg | -7.12 | -4.23 | 27 | 26 | 0.42 / 1.00 | 0.00/0.50/0.50 | 1.000 | -10.3 / -7.9 / -5.2 |
| D4 both BFOs start-up offset (Holland H1 data) | C, 0.5 deg | -6.92 | -4.03 | 4 | 4 | 0.85 / 1.00 | 0.00/0.08/0.92 | 1.000 | -16.5 / -9.7 / -4.0 |
| D4 both BFOs start-up offset (Holland H1 data) | C, 1.0 deg | -6.80 | -3.91 | 7 | 7 | 0.45 / 1.00 | 0.00/0.09/0.91 | 1.000 | -12.9 / -8.7 / -4.7 |
| D5 R600 BFO + R1200 BFO offset | T, 0.5 deg | -5.46 | -2.57 | 4 | 4 | 0.05 / 1.00 | 0.00/0.23/0.77 | 1.000 | -15.5 / -7.6 / -3.2 |
| D5 R600 BFO + R1200 BFO offset | T, 1.0 deg | -5.56 | -2.67 | 6 | 6 | 0.04 / 1.00 | 0.00/0.24/0.76 | 1.000 | -11.7 / -7.3 / -3.6 |
| D5 R600 BFO + R1200 BFO offset | C, 0.5 deg | -6.18 | -3.29 | 2 | 2 | 1.00 / 1.00 | 0.00/0.99/0.01 | 1.000 | -25.9 / -11.8 / -3.2 |
| D5 R600 BFO + R1200 BFO offset | C, 1.0 deg | -6.58 | -3.68 | 2 | 2 | 0.95 / 1.00 | 0.00/0.95/0.05 | 1.000 | -17.8 / -10.0 / -3.8 |

Arm V2:

| 00:19 option | branch, s_b | ln B (rate background) | ln B (one arrival) | conditional ESS | eff. parents | share in strip / X200 | A1/A2/B | C1 share | per-seed ln B min/median/max |
|---|---|---|---|---|---|---|---|---|---|
| D0 joined V2 | T, 0.5 deg | -6.58 | -3.69 | 7 | 7 | 0.50 / 0.99 | 0.01/0.86/0.13 | nan | -10.3 / -6.7 / -4.1 |
| D0 joined V2 | T, 1.0 deg | -6.59 | -3.70 | 18 | 18 | 0.43 / 0.98 | 0.01/0.83/0.16 | nan | -9.6 / -6.8 / -4.7 |
| D0 joined V2 | C, 0.5 deg | -6.70 | -3.81 | 14 | 14 | 0.59 / 1.00 | 0.00/0.93/0.06 | nan | -10.3 / -7.6 / -4.4 |
| D0 joined V2 | C, 1.0 deg | -6.48 | -3.59 | 13 | 13 | 0.33 / 0.99 | 0.00/0.94/0.05 | nan | -10.2 / -7.5 / -4.7 |
| D1 joined V2 | T, 0.5 deg | -6.74 | -3.85 | 7 | 7 | 0.48 / 1.00 | 0.00/0.87/0.12 | nan | -10.3 / -7.3 / -4.3 |
| D1 joined V2 | T, 1.0 deg | -6.74 | -3.85 | 19 | 19 | 0.40 / 1.00 | 0.00/0.84/0.16 | nan | -9.5 / -6.8 / -4.8 |
| D1 joined V2 | C, 0.5 deg | -6.63 | -3.74 | 10 | 10 | 0.56 / 1.00 | 0.00/0.96/0.04 | nan | -10.0 / -8.0 / -3.9 |
| D1 joined V2 | C, 1.0 deg | -6.42 | -3.53 | 10 | 10 | 0.31 / 1.00 | 0.00/0.96/0.04 | nan | -10.0 / -7.4 / -4.2 |
| D2 joined V2 | T, 0.5 deg | -7.81 | -4.91 | 7 | 7 | 0.76 / 1.00 | 0.00/0.32/0.68 | nan | -17.2 / -9.6 / -5.7 |
| D2 joined V2 | T, 1.0 deg | -7.33 | -4.44 | 6 | 6 | 0.31 / 1.00 | 0.00/0.55/0.45 | nan | -12.2 / -8.5 / -4.9 |
| D2 joined V2 | C, 0.5 deg | -4.53 | -1.64 | 1 | 1 | 0.99 / 1.00 | 0.00/0.98/0.02 | nan | -18.9 / -9.9 / -0.9 |
| D2 joined V2 | C, 1.0 deg | -5.00 | -2.11 | 2 | 2 | 0.86 / 1.00 | 0.00/0.96/0.04 | nan | -13.9 / -7.9 / -1.5 |
| D3 joined V2 | T, 0.5 deg | -9.27 | -6.38 | 1 | 1 | 0.02 / 1.00 | 0.00/1.00/0.00 | nan | -39.5 / -18.5 / -6.1 |
| D3 joined V2 | T, 1.0 deg | -9.63 | -6.74 | 2 | 2 | 0.03 / 1.00 | 0.00/0.96/0.04 | nan | -24.0 / -14.0 / -6.8 |
| D3 joined V2 | C, 0.5 deg | -7.81 | -4.92 | 2 | 2 | 0.37 / 1.00 | 0.00/0.63/0.37 | nan | -51.8 / -20.6 / -5.5 |
| D3 joined V2 | C, 1.0 deg | -7.11 | -4.22 | 1 | 1 | 0.10 / 1.00 | 0.00/0.89/0.11 | nan | -27.7 / -19.5 / -5.1 |
| D4 joined V2 | T, 0.5 deg | -6.99 | -4.10 | 3 | 3 | 0.21 / 1.00 | 0.00/0.44/0.56 | nan | -31.0 / -10.7 / -4.3 |
| D4 joined V2 | T, 1.0 deg | -6.65 | -3.76 | 2 | 2 | 0.10 / 1.00 | 0.00/0.29/0.71 | nan | -15.8 / -8.7 / -3.7 |
| D4 joined V2 | C, 0.5 deg | -8.41 | -5.52 | 2 | 2 | 0.96 / 1.00 | 0.00/1.00/0.00 | nan | -25.6 / -14.3 / -4.9 |
| D4 joined V2 | C, 1.0 deg | -8.19 | -5.30 | 5 | 5 | 0.40 / 1.00 | 0.00/0.96/0.04 | nan | -17.6 / -11.4 / -5.5 |

Within-family Bayes factors (family prior held fixed, `q2-acoustic-bayes-factors.csv` columns ln_B_rate_A1/A2/B): A1 is strongly disfavoured (ln B −10 under D0, below −97 under D2–D5),
because uncontrolled A1 descents end within a few minutes of flame-out. A2 and B are about −5 to −7.

**Status: every Bayes factor above is UNCONVERGED.** The per-seed spread is 2–30 nats under D2–D5, and the conditional effective parents are below the threshold of 30 per seed.
The direction (ln B < 0) holds in all 24 options × readings and in the per-seed medians, but the magnitude is not established.

Conditional impact PDF (greyscale 50/90/99 % HPD) given each branch: `fig-conditional-impact-maps-sb1.0.png` (s_b 1 deg) and `-sb0.5.png`. Every panel is stamped NOT ESTIMABLE (ESS < 1,000).
The conditional is centred on X: the along-bearing offset from X is −3.5 km median (D0, T; 5–95 % −87 to +133 km), the cross-track offset is within about ±45 km, and
99 % of the D0 conditional lies inside 23.3–27.7 S, 99.1–103.6 E.

## Q3 — trajectories that fit the sound (top 1 % of rows by w_i L_i)

"Top 1 %" is applied to the rows that are acoustically compatible with the branch (6-sigma joint gate, s_b 1 deg: 209,210 rows for T, 222,410 for C). Their top 1 % (2,092 / 2,224 rows)
carries 97.3–100 % of Σ w_i L_i in every option. The weighted conditional (w_i L_i over all rows) is reported beside it (`q3-conditional-characterisation-weighted.csv`, `q3-top1pct-rows-summary.csv`).

Weighted conditional, 5/50/95 % (T = 00:52:03, C = 00:54:30; s_b 1 deg):

| option, branch | ESS | impact (min after 00:00) | min after 00:19:29 | final flame-out | min aloft after flame-out | A1/A2/B | powered after 00:19:29 | glide with turns | arrested dive (V/S < −8,000 ft/min at 00:19:37) | inside arc |
|---|---|---|---|---|---|---|---|---|---|---|
| D0 held out, T | 166 | 32.7/34.1/35.2 | 13.2/14.6/15.7 | 16.3/17.6/18.5 | 14.8/16.5/18.2 | 0.00/0.26/0.74 | 0.007 | 0.76 | 0.05 | 0.49 |
| D0 held out, C | 14 | 34.6/37.3/37.9 | 15.1/17.9/18.4 | 16.5/17.8/18.4 | 16.7/19.4/20.8 | 0.00/0.19/0.80 | 0.007 | 0.52 | 0.05 | 0.26 |
| D1 R600 BTO, T | 278 | 33.5/34.5/35.3 | 14.0/15.0/15.8 | 16.3/17.6/18.6 | 15.7/16.9/18.3 | 0.00/0.33/0.66 | 0.008 | 0.66 | 0.05 | 0.23 |
| D1 R600 BTO, C | 36 | 36.0/37.2/38.3 | 16.5/17.8/18.8 | 16.4/17.7/18.4 | 17.9/19.7/20.9 | 0.00/0.31/0.69 | 0.008 | 0.62 | 0.07 | 0.21 |
| D2 R600 BTO+BFO, T | 24 | 33.7/34.7/35.1 | 14.3/15.2/15.6 | 16.2/17.2/18.5 | 15.9/16.9/18.4 | 0.00/0.12/0.88 | 0.001 | 0.63 | 0.01 | 0.14 |
| D2 R600 BTO+BFO, C | 14 | 36.1/36.8/37.7 | 16.6/17.4/18.2 | 16.7/18.1/18.5 | 18.0/18.9/20.3 | 0.00/0.32/0.68 | 0.000 | 0.75 | 0.02 | 0.25 |
| D3 both BFOs raw (Holland H2 data), T | 1 | 34.1/34.1/34.9 | 14.6/14.6/15.5 | 16.9/16.9/18.2 | 16.8/17.2/17.2 | 0.00/0.09/0.91 | 0.000 | 0.90 | 1.00 | 0.89 |
| D3 both BFOs raw (Holland H2 data), C | 3 | 36.6/37.0/37.0 | 17.1/17.5/17.5 | 16.4/17.8/18.7 | 18.0/19.2/20.6 | 0.00/0.62/0.38 | 0.000 | 0.92 | 1.00 | 0.03 |
| D4 both BFOs start-up offset (Holland H1 data), T | 27 | 33.9/34.6/35.3 | 14.5/15.1/15.8 | 15.7/17.5/18.7 | 15.7/17.2/18.8 | 0.00/0.50/0.50 | 0.000 | 0.79 | 1.00 | 0.11 |
| D4 both BFOs start-up offset (Holland H1 data), C | 7 | 36.3/36.6/37.6 | 16.9/17.2/18.1 | 16.4/17.0/18.4 | 18.4/19.7/20.7 | 0.00/0.09/0.91 | 0.000 | 0.81 | 1.00 | 0.30 |
| D5 R600 BFO + R1200 BFO offset, T | 6 | 34.2/34.9/35.3 | 14.7/15.4/15.8 | 16.1/17.9/18.6 | 16.5/17.0/19.0 | 0.00/0.24/0.76 | 0.000 | 0.59 | 1.00 | 0.02 |
| D5 R600 BFO + R1200 BFO offset, C | 2 | 35.9/36.6/36.6 | 16.4/17.1/17.1 | 16.6/17.9/17.9 | 18.8/18.8/19.4 | 0.00/0.95/0.05 | 0.000 | 0.99 | 1.00 | 0.34 |

Residuals (residual/sigma, run J convention: BTO 29 µs at 00:10:59, 63 µs R600 00:19:29, 43 µs 00:19:37; BFO 4.3177 Hz, predictive with the hand-off bias variance), weighted 5/50/95 %:

| option, branch | BTO 00:10:59 | BFO 00:10:59 | BTO 00:19:29 | BFO 00:19:29 | BFO 00:19:37 | V/S 00:19:37 (ft/min) | impact speed (m/s) | flight-path angle (deg) | tau90 (s) | heading change (deg) |
|---|---|---|---|---|---|---|---|---|---|---|
| D0 held out, T | -1.7/-0.0/1.9 | -1.3/-0.7/0.4 | -1.3/1.0/7.4 | -17.3/-7.0/9.9 | -57.7/-47.7/-27.5 | -7739/-2316/-0 | 62/80/181 | 2.4/4.1/15.8 | 1.6/3.6/8.0 | 0/509/1497 |
| D0 held out, C | -2.3/-0.4/1.3 | -1.7/-0.7/0.4 | -2.7/-0.2/11.9 | -43.1/-10.2/10.0 | -78.1/-50.4/-30.4 | -7194/-1581/5566 | 67/101/158 | 2.3/3.4/8.4 | 2.0/3.2/7.8 | 0/682/1260 |
| D1 R600 BTO, T | -1.7/-0.1/1.6 | -1.3/-0.7/0.4 | -1.0/0.1/1.5 | -25.1/-6.7/10.0 | -57.0/-47.2/-26.7 | -8080/-2512/9 | 62/81/182 | 2.1/4.1/15.1 | 1.6/3.5/8.5 | 0/397/1340 |
| D1 R600 BTO, C | -1.6/-0.4/1.3 | -1.2/-0.8/0.1 | -1.0/-0.1/1.2 | -43.1/-8.5/22.6 | -78.1/-48.8/-18.1 | -10099/-2000/5566 | 66/101/164 | 1.7/3.6/9.5 | 2.0/3.2/7.8 | 0/359/1239 |
| D2 R600 BTO+BFO, T | -1.4/0.1/1.5 | -1.2/-0.6/0.2 | -1.2/-0.1/0.9 | -1.7/-0.0/1.8 | -42.6/-40.4/-38.7 | -4677/-4078/-3269 | 61/69/111 | 3.1/4.2/6.7 | 1.6/3.3/6.9 | 0/472/1235 |
| D2 R600 BTO+BFO, C | -1.4/0.1/1.1 | -1.2/-0.6/0.1 | -1.3/-0.0/1.2 | -1.5/0.0/1.6 | -42.6/-41.0/-38.8 | -4639/-3946/-3387 | 69/78/113 | 3.1/4.1/5.5 | 2.0/3.4/6.6 | 0/871/1375 |
| D3 both BFOs raw (Holland H2 data), T | -1.0/-1.0/-0.4 | -1.3/-0.8/-0.8 | -0.2/-0.2/0.5 | 0.0/1.1/1.1 | -0.1/-0.1/0.8 | -15060/-14690/-14690 | 102/102/114 | 1.8/4.2/4.2 | 4.2/4.2/9.6 | 156/794/794 |
| D3 both BFOs raw (Holland H2 data), C | -0.7/-0.4/0.1 | -1.3/-0.5/-0.1 | -0.1/0.1/0.5 | -0.7/0.3/1.7 | -0.7/-0.1/0.5 | -14796/-14758/-14336 | 104/113/115 | 2.6/4.5/5.5 | 3.9/6.3/8.5 | 0/773/1256 |
| D4 both BFOs start-up offset (Holland H1 data), T | -1.4/0.4/1.9 | -1.1/-0.6/0.6 | -1.1/0.6/1.4 | 5.4/13.8/26.5 | 4.0/13.4/28.3 | -22006/-18234/-15607 | 84/106/120 | 2.3/3.6/5.1 | 2.8/3.7/8.1 | 0/496/1200 |
| D4 both BFOs start-up offset (Holland H1 data), C | -0.8/-0.1/1.6 | -1.2/-0.9/0.4 | -0.1/0.6/0.9 | 6.0/21.0/23.9 | 6.7/21.5/24.8 | -20696/-20441/-15907 | 71/110/129 | 2.8/3.5/8.4 | 2.3/5.7/8.5 | 128/360/853 |
| D5 R600 BFO + R1200 BFO offset, T | -2.3/-0.7/0.7 | -1.6/-0.8/-0.5 | -0.7/-0.2/1.6 | -2.4/0.7/2.8 | 3.5/18.8/25.5 | -21257/-19610/-15711 | 70/102/110 | 1.9/3.9/4.4 | 2.2/4.2/9.9 | 0/10/1134 |
| D5 R600 BFO + R1200 BFO offset, C | -0.8/-0.8/0.7 | -1.3/-1.3/-0.7 | 0.0/0.0/1.6 | -0.4/-0.4/2.5 | 3.7/3.7/15.6 | -18774/-15786/-15786 | 98/98/119 | 2.9/2.9/3.0 | 4.0/8.5/10.6 | 499/607/678 |

Residuals at 18:25–23:15 are **not assessed at this depth**: core run J does not store per-parent residuals before the 00:11 hand-off. Every row is conditioned on them through
its hand-off weight. The 00:10:59 values were recomputed from the m0011 hand-off states (engine forward model, `h0011_worker.py`). The matching rows sit near 0 sigma in BTO
and at about −0.7 sigma in BFO at 00:10:59, which is the value for paths ending north of 30 S. Columns that a given option does not use (for example the 00:19:29 BFO under D0) are shown for description only.

**Is a 15–17 min post-00:19 flight ending near 25.7 S in the feasible set, and how is it achieved?** Yes; it is in the model's reach and in the proposal (`q3-feasibility-near-crossing.csv`).
Within 50 km of X, 13–18 min after 00:19:29, there are 56,261 rows from 37,825 parents, carrying posterior mass 1.5e-4 (D0) to 2.9e-4 (D2). By mechanism:
- **Unpowered glide with turns** (flame-out before 00:19:29, ≥ 1 turn): 28,643 rows; 1.2e-4 (D0), 2.4e-4 (D2). This is the dominant route under every option.
- **Unpowered glide without turns**: 7,927 rows; 3.2e-5 (D0).
- **Arrested dive after a steep 00:19:37 descent** (V/S < −8,000 ft/min at 00:19:37, then > 10 min aloft): 6,291 rows; 6.5e-6 (D0), but under D3–D5 it carries all the mass near X (1.8e-4 under D3, 7.0e-5 under D4).
- **Powered after 00:19:29** (final flame-out after 00:19:29, log-on cause other than exhaustion): 19,691 rows, but only 6e-7 (D0) and ≤ 1e-7 (D2–D5). Inside the C2 cell alone
  (`q3-c2-cause-cells.csv`), these rows are powered to a fuel exhaustion at 00:31–00:37 and impact 1–3 min later (ESS 150 for D0 T). The competing-cause total gives this route ≤ 1 % because
  the 00:19:29 log-on is much more probable under C1 (lag density) than under C2 (uniform over 3,898 s).

**Position relative to the arc.** Kadri's eq. 4 places the impact inside the arc only for flight along the bearing after 00:19:29. The run J rows that fit the sound are not
constrained to that track. Their impacts straddle the arc: 49 % inside under D0 T, 26 % under D0 C, 14–25 % under D2, 3–89 % under D3–D5 (very few effective rows there).
Haixun 01 is 28.5 km outside the arc. Its 0.05 deg cell (± 1 cell) lies in the 50 % region for D0 and D1 (00:52:03), in the 90 % region for the caption reading and for D2, in the 99 % region for D4, and outside the 99 % region for D3 and D5 (effective samples 1–6). This is a sensitivity check only; none of these maps is estimable.

Haixun-centred sensitivity line (secondary): posterior mass within 50/100/200/400 km of Haixun under D0 is 0.105 % / 0.308 % / 0.700 % / 1.22 % (around X: 0.093 % / 0.294 % / 0.679 % / 1.19 %). These are close to the
values around X because the two centres are 28.5 km apart (`q1-locality-mass.csv`, regions H50–H400).

## Q4 — under-sampling and the targeted run

ESS in the strip is below 200 for D2–D5, and the acoustic conditional has an effective sample of 1–278. This is a **coverage gap of the proposal (set c)**, not of the model's reach (set b).
Rows that fit the sound exist in every option, but too few children per parent land there.

Designed and built (`targeted_build.py`, `targeted_seed.sh`, `flight_leg_worker.process_targeted`); smoke-tested end to end on 40 parents × 16 children (seed 1, mechanics only;
not evidence). The combined seed's ln Z reproduced production to 5e-5:
- **Proposal**: re-simulate, in each of the 24 run-j-waypoints seeds, every parent with at least one production child that is acoustically compatible (6-sigma gate, either branch)
  or lies in the strip or within 200 km of X (mean 1,860 parents per seed, range 1,176–3,417), with **256 children** (production 16). Use a fresh RNG stream (seed 1000 + k).
- **Weights**: exact. Within-parent weights are unnormalised (row.weight × p/q / (M × children)), so every parent's children estimate its hand-off weight for any N.
  The selected parents' production children are **discarded and replaced** (stratified replacement; unbiased because the fresh draws are independent of the selection).
  Targeted cells get the production seed normaliser (cells_t + ln W_t − ln W_prod). The prior and every option likelihood are unchanged.
- **Expected gain**: about 16× in the conditional ESS where the parent count is not limiting (D0/D1/D2: about 2,600 / 4,400 / 380 for the 00:52:03 reading). D3–D5 stay limited by parent
  diversity (1–27 effective parents); they would need an aimed descent proposal (arrested-dive + glide branch) with the same exact correction.
- **Cost**: about 45.7 M rows; about 1.5 h at production rate behind the heavy lock; about 3.4 GB transient disk per seed (full impacts deleted after reduction).
- **Status: NOT RUN.** The Mac had 15–18 GiB free during this session (other modules' data), below the 25 GiB floor. Run when ≥ 30 GiB is free:
  `for k in 1..24: lockf -k /tmp/.mh370-heavy.lock bash targeted_seed.sh k <TDIR> children-256.toml`.

Fuel-exhaustion time for trajectories ending in L: see Q1. The final flame-out is 00:16:30–00:18:30 in every option and region (C1 share ≥ 0.99). Only the C2 cells reach later exhaustion (00:31–00:37 for the matching rows).

## COVERAGE

1. **(a) Feasible set** (777-200ER): powered flight to fuel exhaustion; at exhaustion either an uncontrolled descent (spiral/phugoid; A1) or a piloted glide, ditching attempt or circuit (A2, B).
   A clean glide from FL350–FL400 lasts roughly 20–30 min (engineering estimate from a lift-to-drag ratio of about 17–20; not a sourced bound: grade C, not re-read in this leg).
   A powered descent or a later flame-out under a non-exhaustion log-on cause is also in the set. Rapid descents (Holland-type, 15,000–22,000 ft/min at 00:19:37) with recovery are in the set.
2. **(b) Model's reach**: all of the above are produced by run J, with these limits: the longest time aloft after final flame-out among the stored rows is 37 min and the latest stored impact is 01:42.7 (stored rows = the locality, acoustically compatible and top-ranked rows, not the whole posterior);
   and piloted rapid descents are capped at 40,000 ft/min (end of flight's holland-estimable overlay: a declared cap, i.e. a reach limit). Stepped profile shapes are not eligible for push-over (declared gap in end of flight's README).
3. **(c) Proposal coverage**: 470 M impact rows; acoustically compatible rows 209,210 (T) / 222,410 (C); ESS per option in the strip 1,763 / 1,803 / 175 / 22 / 13 / 46 (D0–D5);
   conditional ESS 166 / 278 / 24 / 1.4 / 27 / 5.6 (T, s_b 1 deg) and 14 / 36 / 14 / 3.1 / 7.4 / 2.3 (C).
   By family (D0, T): A1 share 0.002 (ESS < 5), A2 0.26, B 0.74; per-family conditional ESS in `q2-acoustic-bayes-factors.csv`.
4. **Gaps**: (G1) proposal thinness near the bearing for D2–D5 and for every option given the caption reading. The fix is the targeted run (Q4); NOT RUN, disk floor.
   (G2) Residuals before 00:11 per parent are not stored, so they are not assessed. (G3) Arm V2 has no D5 and no tau90/attitude sidecar, so those are not assessed for V2.
   (G4) The 40,000 ft/min cap on piloted rapid descents is a reach limit (from end of flight; it does not bind for the matching rows, whose 00:19:37 V/S is −14,000 to −22,000 ft/min).
   (G5) run-j-both-burst (supplementary D3/D4 set) is not used in this leg.
5. **Parameter bounds used here** (all from the pre-registration): c = 1.48 km/s ± 0.015 (sound-speed spread); timing floor 5 s; s_b 0.5 / 1.0 deg; background 18 transients in 00:36–00:57, 200–340 deg (Kadri 2024, Table 1, grade B: cited, not re-read in this leg).

## Deviations from the pre-registration

- "Top 1 %" is applied to the acoustically compatible rows (6-sigma joint gate) rather than to all 470 M rows. In all rows it would be 4.7 M rows, almost all with L_i ≈ 0.
  The chosen set carries ≥ 97 % of Σ w_i L_i, and the weighted conditional is reported as well.
- The Q4 targeted run was designed and smoke-tested but not run (disk floor).
- Residuals at arcs before 00:11 are not assessed (not stored per parent).
- Arm V2 joined estimate uses seeds 1–21 only (22–24 were finishing at the time), and D0–D4 only.

## Reproduction and files

- Weights: `option_table_0019.seed_terms` from branch hypothesis/end-of-flight (5d060f0) exec'd unchanged with only its final reduction replaced, as in `results/drift-runj-2026-10-17`.
  This reproduces `run-j/summary/table-0019-mixture.json` exactly (ln Z and ESS of every D cell, e.g. D0 −7.5251 / 1,946,624). Arm V2 reproduces `joined-s1.txt` ln Z to 1e-6.
- Scripts: `flight_leg_worker.py`, `run_flight_leg.py`, `aggregate_flight_leg.py`, `figures.py`, `targeted_build.py`, `targeted_seed.sh`, `h0011_worker.py` (copy of the run J hand-off residual parser).
- Tables: `q1-locality-mass.csv`, `q1-by-route-stratum.csv`, `q1-q4-timing-quantiles.csv`, `q2-acoustic-bayes-factors.csv`, `q3-conditional-characterisation-weighted.csv`,
  `q3-top1pct-rows-summary.csv`, `q3-feasibility-near-crossing.csv`, `q3-c2-cause-cells.csv`, `q3-joined-v2-characterisation.csv`.
- Figures: `fig-conditional-impact-maps-sb1.0.png/.pdf`, `fig-conditional-impact-maps-sb0.5.png/.pdf`, `fig-bayes-factors.png/.pdf`, `fig-timing-distributions.png/.pdf`.
- Per-row stored subsets (4.5 M rows, 1.6 GB) stay in the session workspace (`kh/out/rows/`); they are not committed.
