# Energy-transfer duration at water entry, `impact_tau_method = 1` (ocean settling, 8 Nov 2026)

**Status: UNCHECKED.** Owner: ocean settling. Run id `energy-transfer-m1-2026-11-08`.
Authority: Pete's ruling of 8 Nov 2026 (settling owns everything after x_Impact, first water contact) and the work order
`threads/work-orders/settling-energy-transfer-duration-2026-11-08.md` (commit 6baa905). This note supersedes, as the owner's
method note, the end-of-flight note `results/eof-impact-tau-method-oct11.md` (11 Oct 2026; registry id
`eof.res.eof-impact-tau-method-oct11_md`). That note is not edited. The formulas below are its formulas, ported without change.

## 1. Summary

1. Method 1 is computed for all 501,102 rows of the Davey-model-with-fuel hand-off and all 500,198 rows of the waypoint hand-off
   (final end-of-flight run, 7 Nov 2026, status UNCHECKED). No row is NaN; no row is reordered.
2. The duration has two clusters. Steep entries (flight-path angle at least 30 deg) give tau90 of 0.093-0.18 s; shallow
   entries (at most 10 deg) give 2.2-12 s (weighted 5-95 %, D10, both route models; largest value 33 s, at the highest shallow
   contact speeds). The no-pilot family is almost all steep under D9 and D10; the piloted family is about
   half shallow.
3. Headline weighted tau90, 5 / 50 / 95 %: D10, Davey model with fuel, 0.0956 / 0.152 / 6.09 s; D10, waypoints, 0.0955 / 0.158 / 6.82 s.
   Tables in section 5.
4. Source check: NACA Report 1347 and NACA RM SL9H05a were retrieved and read. The upper edge (3.0 g) covers every tabulated transport
   average (largest 2.64 g). The lower edge (0.75 g) is above 10 % of the damaged-model averages and 49 % of the undamaged-model
   averages (smallest 0.45 g). The range is not changed (work order); a sensitivity with 0.45 g is reported, and the lower edge is
   put to Pete (section 4). NACA RM SL55K08 (Boeing 707): not retrieved — ask Pete.

## 2. Method (as the 11 Oct note; checked formula by formula)

Inputs per row, from the contact state only (the family label is never read by the physics):
v = sqrt(2 KE / m) from `kinetic_energy_j` and `mass_kg`; theta = |`flight_path_angle_deg_descent_positive`|; m = `mass_kg`.
Two declared random parameters per row: a_bar ~ U[0.75 g, 3.0 g]; L_eff ~ U[0.5, 1.0] x 63.7 m.

| Regime | t05 | t95 | tau90 | Peak rate |
|---|---|---|---|---|
| Shallow, theta <= 10 deg: F(t) = 1 - (1 - t/T)^2, T = v / a_bar | (1 - sqrt 0.95) T = 0.0253 T | (1 - sqrt 0.05) T = 0.776 T | 0.751 v / a_bar | m a_bar v |
| Steep, theta >= 30 deg: linear transfer over L_eff / v | 0.05 L_eff / v | 0.95 L_eff / v | 0.9 L_eff / v | KE v / L_eff |
| Blend, 10 < theta < 30 deg: w = (theta - 10) / 20 | log-linear | log-linear | t95 - t05 (see below) | log-linear |

Log-linear: X = exp((1 - w) ln X_shallow + w ln X_steep). Band-edge sensitivity: the same draws with the band 5-45 deg
(w = (theta - 5) / 40); columns with suffix `_band5_45`.

**One point the 11 Oct note leaves open.** The note defines tau90 = t95 - t05 (its conventions paragraph) and also says the blend is
applied to tau90, t05, t95 and the peak rate. In the blend band the two readings differ, because the blend of a difference is not the
difference of the blends. `energy_transfer_tau90_s` is t95 - t05 (the 8 Oct contract definition, and what the Run C and Run J sidecars
`tau90_v1.npz` did). The literal blend of tau90 is in `energy_transfer_tau90_logblend_s`. The largest relative difference over all
rows is 0.13 %, so the choice has no material effect.

Other columns: `impact_energy_transferred_j` = KE (declared upper bound; energy left in intact floating pieces is not modelled);
`energy_transfer_n_pulses` = 1 (declared single-pulse model; stored as float so that NaN can mark a row not computed);
`kinetic_energy_at_contact_j` = KE (a copy, never an alias); `impact_tau_method` = 1; `w_steep`; `a_bar_mps2`; `l_eff_m`;
`bank_assigned` = 1 where `family_code` is 2 or 3 and `bank_deg` == 0.0; `contact_speed_mps`; `row_index`; `seed`.
NaN means not computed (non-finite or non-positive v or m, non-finite theta). No value is filled.

**Reproducible draws.** A counter-based hash, so that a row's draw depends only on its key, not on chunking or order:
x_k = 0x5E771E0000000001 + route_code x 2^56 + seed x 2^40 + row_index x 4 + k (uint64, wrapping; k = 0 for a_bar, 1 for L_eff;
route_code 1 Davey model + fuel, 2 waypoints); h = splitmix64(x_k); u = ((h >> 11) + 0.5) 2^-53. The same rule can be written in Rust.

**Separation from the sinking sequence** (qualification 3 of 8 Oct): flooding, implosion and seabed contact do not lengthen tau90.
Break-up stays in settling and is not applied here. No parameter is tuned on hydrophone data (ruling of 8 Nov, item 3).

## 3. Inputs and checks

1. `EX:end-of-flight/final-2026-11-07/results/eof-final-handoff-df.npz` (SHA-256 11c4753e...cd7d39) and `...-wp.npz`
   (c7db0bbf...9acb). `READY` present; all six entries of `SHA256SUMS` verified (`shasum -c`: OK) before reading.
2. Unit tests (`code/test_settling_energy_transfer_m1.py`, 11 pass): the note's magnitudes (ditching 70 m/s: 1.79-7.15 s;
   steep 200 m/s: 0.143-0.287 s; 300 m/s: 0.096-0.191 s; they round to the note's 1.8-7, 0.14-0.29 and 0.10-0.19 s); the
   constants 0.0253, 0.776, 0.751; pure-regime formulas; log-linear blend and band edges; NaN rule; draw reproducibility and order
   independence; uniformity of the draws; `bank_assigned`; and, on both full sidecars, row count, `row_index`, `seed`, the copied
   kinetic energy, contact speed, and exact recomputation of 2,000 random rows from the hand-off alone.
3. `bank_assigned` row shares agree with the work order: 67.5 % of piloted rows (Davey + fuel), 66.5 % (waypoints), 72.2 % of
   planned-descent rows; no-pilot rows 0.11 % and 0.15 % zeros (not flagged; bank is computed there).

## 4. Source check of the a_bar range (work order section 2 item 3)

Retrieved from the NASA Technical Reports Server (public, US Government work): NACA Report 1347 (Fisher and Hoffman 1958, NTRS
19930092335), NACA RM SL9H05a (Fisher and Thompson 1949, NTRS 20050071552), NACA RM SL8K18 (Fisher and Morris 1948, NTRS 20050029398)
and NASA TM X-2445 (Thompson 1972, heavy jet transport, NTRS 19720009355). Copies: `EX:settling/energy-transfer-m1-2026-11-08/sources/`.

1. **Report 1347** states that average decelerations "were derived from the landing speeds and lengths of run" (that is
   a = v^2 / 2s, the same quantity as a_bar in method 1), and that scale-model tests indicate decelerations in severe ditchings may
   exceed 10 g (maximum, not average). Tables 26-37 (twelve transports, calm water) were transcribed
   (`naca-ditching-average-deceleration.csv`, 104 rows) and a was recomputed from v and s; the printed values (rounded to 1/2 g) agree
   for 103 of 104 rows (Transport F, damaged model, 12 deg, 91 kt, 500 ft: printed 1 g, recomputed 0.73 g).
   Standard configuration, recomputed average: damaged models (n = 40) 0.45-2.64 g, median 1.13 g, 10 % below 0.75 g;
   undamaged models (n = 55) 0.47-2.30 g, median 0.75 g, 49 % below 0.75 g. Landing speeds 56-164 kt (29-84 m/s).
   Printed maxima: 1-8 g (damaged), 0.5-6 g (undamaged).
2. **RM SL9H05a** (Constellation with Speedpak): maximum longitudinal deceleration about 1 1/2 g at 9 deg and about 2 g at 12 deg,
   against about 4 g without the Speedpak (its reference 1, RM SL8K18, which gives "about 4 g"). The 11 Oct note quotes 1.7 g; the
   report says 1 1/2 g (the PDF text layer renders it as "17 g", the likely source of the 1.7). Recomputed averages from its Table I:
   0.60, 0.66 and 1.00 g.
3. **TM X-2445** (1/30-scale heavy jet transport, calm water): maximum longitudinal accelerations about 3-7 g; landing runs about
   3-6 fuselage lengths at 65-91 m/s. It gives no average deceleration.
4. **RM SL55K08** (Thompson 1955, Boeing 707): not retrieved — ask Pete. Searched: the artifact store (all projects), the repo
   (claude-science-sep29 and main, file names), ~/Downloads and ~/Documents (file names), Google Drive (title and full text) and the
   NTRS API (report number and title words). Recorded in `results/source-access-ledger-2026-10-22.csv`, row S01.
5. **Assessment.** Upper edge 3.0 g: supported (above every tabulated transport average). Lower edge 0.75 g: narrower than the
   tabulated range. Under the sampling-coverage rule (item 5) a bound narrower than the sourced range is a gap unless it has a source.
   The range is kept as the 11 Oct note set it (the work order forbids a change without Pete). Sensitivity, same draws,
   a_bar ~ U[0.45, 3.0] g: tau90 95 % rises from 6.09 to 7.04 s (D10, Davey + fuel) and from 6.82 to 8.12 s (D10, waypoints); medians
   change by less than 0.01 s for D10 (section 5, table 3). **Open for Pete: widen the lower edge to 0.45 g, or keep 0.75 g with a
   reason** (for example, that the MH370 contact was unpowered and probably not in calm water).
6. Limits of the evidence: dynamic models of 1940s-1950s transports, calm water, landing speeds 29-84 m/s, landing attitudes
   0-14 deg nose-up. None is a 777-size airframe; none is at the higher contact speeds of the hand-off.

## 5. Results (weighted; weights exp(log_weight_<treatment>), normalised per route model)

Shares are of the family's weight within the route model. Regimes: shallow theta <= 10 deg, steep theta >= 30 deg.
All nine treatments, all families and both bands are in `settling-energy-transfer-summary.csv`.

Table 1. Headline band 10-30 deg.

| Route model | Treatment | Family | Weight share | ESS | Shallow / blend / steep share | tau90 5 / 50 / 95 % (s) | Peak rate 5-95 % (W) | Peak rate min-max (W) |
|---|---|---|---|---|---|---|---|---|
| Davey + fuel | D7 | all | 1.000 | 151996 | 0.528 / 0.232 / 0.240 | 0.119 / 2.99 / 9.48 | 1.54e+08 - 6.88e+10 | 7.48e+07 - 1.41e+11 |
| Davey + fuel | D7 | no pilot | 0.515 | 85230 | 0.271 / 0.297 / 0.432 | 0.108 / 1.71 / 7.62 | 1.91e+08 - 7.42e+10 | 8.54e+07 - 1.02e+11 |
| Davey + fuel | D7 | piloted | 0.485 | 67840 | 0.801 / 0.162 / 0.036 | 0.198 / 3.87 / 11.2 | 1.34e+08 - 4.61e+10 | 7.48e+07 - 1.41e+11 |
| Davey + fuel | D9 | all | 1.000 | 508 | 0.234 / 0.206 / 0.561 | 0.0982 / 0.165 / 7.2 | 2.17e+08 - 8.73e+10 | 7.84e+07 - 1.41e+11 |
| Davey + fuel | D9 | no pilot | 0.525 | 156 | 0.002 / 0.001 / 0.996 | 0.0943 / 0.127 / 0.173 | 4.19e+10 - 8.89e+10 | 1.52e+08 - 1.01e+11 |
| Davey + fuel | D9 | piloted | 0.475 | 1142 | 0.489 / 0.431 / 0.080 | 0.129 / 2.86 / 9.39 | 1.60e+08 - 7.43e+10 | 7.84e+07 - 1.41e+11 |
| Davey + fuel | D10 | all | 1.000 | 3341 | 0.148 / 0.133 / 0.719 | 0.0956 / 0.152 / 6.09 | 2.68e+08 - 8.78e+10 | 7.84e+07 - 1.41e+11 |
| Davey + fuel | D10 | no pilot | 0.696 | 1672 | 0.002 / 0.002 / 0.996 | 0.0939 / 0.136 / 0.176 | 4.14e+10 - 8.85e+10 | 1.78e+08 - 1.01e+11 |
| Davey + fuel | D10 | piloted | 0.304 | 10049 | 0.482 / 0.433 / 0.085 | 0.125 / 2.29 / 9.64 | 1.63e+08 - 7.71e+10 | 7.84e+07 - 1.41e+11 |
| waypoints | D7 | all | 1.000 | 127717 | 0.544 / 0.239 / 0.217 | 0.126 / 3.08 / 9.6 | 1.52e+08 - 6.47e+10 | 7.60e+07 - 1.44e+11 |
| waypoints | D7 | no pilot | 0.506 | 72451 | 0.291 / 0.311 / 0.398 | 0.114 / 2.02 / 7.72 | 1.85e+08 - 6.97e+10 | 8.07e+07 - 1.01e+11 |
| waypoints | D7 | piloted | 0.446 | 59858 | 0.791 / 0.174 / 0.034 | 0.211 / 4 / 11.6 | 1.39e+08 - 4.52e+10 | 7.60e+07 - 1.44e+11 |
| waypoints | D7 | planned descent | 0.048 | 2382 | 0.912 / 0.074 / 0.014 | 1.63 / 3.38 / 9.39 | 1.13e+08 - 5.79e+09 | 7.63e+07 - 1.33e+11 |
| waypoints | D9 | all | 1.000 | 1129 | 0.269 / 0.248 / 0.484 | 0.0957 / 0.195 / 8 | 2.06e+08 - 8.74e+10 | 7.77e+07 - 1.41e+11 |
| waypoints | D9 | no pilot | 0.447 | 261 | 0.002 / 0.004 / 0.994 | 0.0928 / 0.136 / 0.173 | 4.45e+10 - 8.96e+10 | 1.49e+08 - 1.01e+11 |
| waypoints | D9 | piloted | 0.527 | 2363 | 0.484 / 0.445 / 0.071 | 0.133 / 2.9 / 9.98 | 1.67e+08 - 7.25e+10 | 7.77e+07 - 1.41e+11 |
| waypoints | D9 | planned descent | 0.026 | 497 | 0.487 / 0.436 / 0.077 | 0.134 / 2.78 / 10.1 | 1.67e+08 - 7.14e+10 | 8.08e+07 - 1.33e+11 |
| waypoints | D10 | all | 1.000 | 14678 | 0.193 / 0.173 / 0.634 | 0.0955 / 0.158 / 6.82 | 2.35e+08 - 8.83e+10 | 7.77e+07 - 1.41e+11 |
| waypoints | D10 | no pilot | 0.605 | 5960 | 0.003 / 0.002 / 0.995 | 0.0934 / 0.134 / 0.175 | 4.30e+10 - 8.94e+10 | 1.94e+08 - 1.01e+11 |
| waypoints | D10 | piloted | 0.378 | 21527 | 0.483 / 0.437 / 0.081 | 0.126 / 2.3 / 9.4 | 1.66e+08 - 7.73e+10 | 7.77e+07 - 1.41e+11 |
| waypoints | D10 | planned descent | 0.018 | 1941 | 0.490 / 0.413 / 0.097 | 0.119 / 2.23 / 9.5 | 1.62e+08 - 7.88e+10 | 8.08e+07 - 1.33e+11 |

Table 2. Band-edge sensitivity (5-45 deg), same draws.

| Route model | Treatment | Family | Shallow / blend / steep share, 5-45 deg | tau90 5 / 50 / 95 %, 10-30 deg (s) | tau90 5 / 50 / 95 %, 5-45 deg (s) |
|---|---|---|---|---|---|
| Davey + fuel | D7 | all | 0.363 / 0.489 / 0.148 | 0.119 / 2.99 / 9.48 | 0.13 / 2.86 / 8.63 |
| Davey + fuel | D7 | no pilot | 0.071 / 0.642 / 0.287 | 0.108 / 1.71 / 7.62 | 0.111 / 1.88 / 6.16 |
| Davey + fuel | D7 | piloted | 0.673 / 0.327 / 0.000 | 0.198 / 3.87 / 11.2 | 0.933 / 3.85 / 10.3 |
| Davey + fuel | D9 | all | 0.205 / 0.346 / 0.449 | 0.0982 / 0.165 / 7.2 | 0.0996 / 0.225 / 7.17 |
| Davey + fuel | D9 | no pilot | 0.001 / 0.144 / 0.856 | 0.0943 / 0.127 / 0.173 | 0.0943 / 0.13 / 0.214 |
| Davey + fuel | D9 | piloted | 0.430 / 0.570 / 0.000 | 0.129 / 2.86 / 9.39 | 0.572 / 3.19 / 9.39 |
| Davey + fuel | D10 | all | 0.126 / 0.242 / 0.632 | 0.0956 / 0.152 / 6.09 | 0.0965 / 0.16 / 6.02 |
| Davey + fuel | D10 | no pilot | 0.000 / 0.092 / 0.908 | 0.0939 / 0.136 / 0.176 | 0.0941 / 0.14 / 0.202 |
| Davey + fuel | D10 | piloted | 0.414 / 0.586 / 0.000 | 0.125 / 2.29 / 9.64 | 0.567 / 2.86 / 9.58 |
| waypoints | D7 | all | 0.372 / 0.501 / 0.127 | 0.126 / 3.08 / 9.6 | 0.14 / 2.94 / 8.71 |
| waypoints | D7 | no pilot | 0.078 / 0.671 / 0.251 | 0.114 / 2.02 / 7.72 | 0.117 / 2.08 / 6.25 |
| waypoints | D7 | piloted | 0.662 / 0.338 / 0.000 | 0.211 / 4 / 11.6 | 0.964 / 3.99 / 10.4 |
| waypoints | D7 | planned descent | 0.779 / 0.221 / 0.000 | 1.63 / 3.38 / 9.39 | 1.68 / 3.36 / 8.95 |
| waypoints | D9 | all | 0.231 / 0.371 / 0.399 | 0.0957 / 0.195 / 8 | 0.0981 / 0.893 / 7.86 |
| waypoints | D9 | no pilot | 0.001 / 0.108 / 0.891 | 0.0928 / 0.136 / 0.173 | 0.093 / 0.137 / 0.224 |
| waypoints | D9 | piloted | 0.418 / 0.582 / 0.000 | 0.133 / 2.9 / 9.98 | 0.631 / 3.21 / 9.74 |
| waypoints | D9 | planned descent | 0.399 / 0.601 / 0.000 | 0.134 / 2.78 / 10.1 | 0.61 / 3.02 / 10.1 |
| waypoints | D10 | all | 0.164 / 0.289 / 0.548 | 0.0955 / 0.158 / 6.82 | 0.0969 / 0.168 / 6.71 |
| waypoints | D10 | no pilot | 0.001 / 0.093 / 0.906 | 0.0934 / 0.134 / 0.175 | 0.0936 / 0.137 / 0.218 |
| waypoints | D10 | piloted | 0.412 / 0.588 / 0.000 | 0.126 / 2.3 / 9.4 | 0.587 / 2.91 / 9.32 |
| waypoints | D10 | planned descent | 0.418 / 0.582 / 0.000 | 0.119 / 2.23 / 9.5 | 0.519 / 2.78 / 9.48 |

Table 3. a_bar lower-edge sensitivity (section 4), same draws, band 10-30 deg.

| Route model | Treatment | Family | tau90 5 / 50 / 95 %, a_bar U[0.75, 3.0] g (s) | tau90 5 / 50 / 95 %, a_bar U[0.45, 3.0] g (s) |
|---|---|---|---|---|
| Davey + fuel | D7 | all | 0.119 / 2.99 / 9.48 | 0.119 / 3.13 / 12.8 |
| Davey + fuel | D7 | no pilot | 0.108 / 1.71 / 7.62 | 0.108 / 1.77 / 10.1 |
| Davey + fuel | D7 | piloted | 0.198 / 3.87 / 11.2 | 0.2 / 4.21 / 15.1 |
| Davey + fuel | D9 | all | 0.0982 / 0.165 / 7.2 | 0.0982 / 0.166 / 8.88 |
| Davey + fuel | D9 | no pilot | 0.0943 / 0.127 / 0.173 | 0.0943 / 0.127 / 0.173 |
| Davey + fuel | D9 | piloted | 0.129 / 2.86 / 9.39 | 0.129 / 2.98 / 12.4 |
| Davey + fuel | D10 | all | 0.0956 / 0.152 / 6.09 | 0.0956 / 0.152 / 7.04 |
| Davey + fuel | D10 | no pilot | 0.0939 / 0.136 / 0.176 | 0.0939 / 0.136 / 0.176 |
| Davey + fuel | D10 | piloted | 0.125 / 2.29 / 9.64 | 0.125 / 2.44 / 12.9 |
| waypoints | D7 | all | 0.126 / 3.08 / 9.6 | 0.126 / 3.24 / 13.1 |
| waypoints | D7 | no pilot | 0.114 / 2.02 / 7.72 | 0.114 / 2.11 / 10.3 |
| waypoints | D7 | piloted | 0.211 / 4 / 11.6 | 0.213 / 4.38 / 15.6 |
| waypoints | D7 | planned descent | 1.63 / 3.38 / 9.39 | 1.64 / 3.69 / 12.6 |
| waypoints | D9 | all | 0.0957 / 0.195 / 8 | 0.0957 / 0.199 / 10.2 |
| waypoints | D9 | no pilot | 0.0928 / 0.136 / 0.173 | 0.0928 / 0.136 / 0.173 |
| waypoints | D9 | piloted | 0.133 / 2.9 / 9.98 | 0.134 / 3.03 / 13.4 |
| waypoints | D9 | planned descent | 0.134 / 2.78 / 10.1 | 0.134 / 2.9 / 13.9 |
| waypoints | D10 | all | 0.0955 / 0.158 / 6.82 | 0.0955 / 0.158 / 8.12 |
| waypoints | D10 | no pilot | 0.0934 / 0.134 / 0.175 | 0.0934 / 0.134 / 0.175 |
| waypoints | D10 | piloted | 0.126 / 2.3 / 9.4 | 0.126 / 2.47 / 12.4 |
| waypoints | D10 | planned descent | 0.119 / 2.23 / 9.5 | 0.119 / 2.35 / 13.1 |

## 6. COVERAGE

1. **Feasible set (a).** Water entry of a 777-200ER from a ditching-like contact (flight-path angle a few degrees, about 60-80 m/s)
   to a near-vertical high-speed dive (up to about 380 m/s ground speed in the hand-off). Sources: end-of-flight hand-off ranges
   (contact speed 55-384 m/s; flight-path angle 0.09-89.9 deg); NACA ditching tests (section 4) for the shallow end.
2. **Model's reach (b).** Method 1 gives a value for every v > 0 and every angle 0-90 deg. Reach gaps, declared: (i) the shallow
   regime extrapolates the ditching-test basis (29-84 m/s) to higher speed: weight with theta <= 10 deg and v > 100 m/s is 26 % (D7),
   14-16 % (D9) and 9-11 % (D10) of all weight; at these speeds early break-up is likely and the constant-deceleration run-out is
   not supported by any test; (ii) single pulse, so skipping, porpoising and a dive after a run (the "dived" outcomes of the NACA
   tables) are not resolved; (iii) calm water only; (iv) no pitch attitude, flap or gear configuration in the hand-off; (v) bank is a
   placeholder in the flagged rows (not used by method 1).
3. **Proposal's coverage (c).** Sampling is the end-of-flight sampling; this transform adds no proposal and no weight. ESS (all
   families, 10-30 band): Davey + fuel D7 152,000, D9 508, D10 3,341; waypoints D7 127,700, D9 1,129, D10 14,680. Every one of the
   nine treatments is estimable from the same rows (smallest ESS: D9, Davey + fuel, 508). Provisional cells, carried from end of
   flight: D9 no pilot ESS 156 (Davey + fuel) and 261 (waypoints); D11 no pilot 490 (Davey + fuel; the work order quotes 489). Sub-regime ESS below 100: the
   no-pilot shallow and blend cells under D9 and D10 (weight share at most 0.4 %), and planned descent steep under D7 and D9 (ESS 98
   and 77). These are reported, not dropped.

Table 4. ESS per regime, high-speed shallow share and share of rows with placeholder bank (band 10-30 deg).

| Route model | Treatment | Family | ESS shallow / blend / steep | Weight share, shallow and v > 100 m/s | Weight share bank_assigned |
|---|---|---|---|---|---|
| Davey + fuel | D7 | all | 77787 / 34366 / 40308 | 0.262 | 0.328 |
| Davey + fuel | D7 | no pilot | 21793 / 25707 / 37848 | 0.147 | 0.000 |
| Davey + fuel | D7 | piloted | 56085 / 9507 / 2537 | 0.385 | 0.677 |
| Davey + fuel | D9 | all | 554 / 465 / 177 | 0.141 | 0.305 |
| Davey + fuel | D9 | no pilot | 19 / 13 / 155 | 0.002 | 0.000 |
| Davey + fuel | D9 | piloted | 549 / 462 / 171 | 0.295 | 0.642 |
| Davey + fuel | D10 | all | 4807 / 4225 / 1780 | 0.087 | 0.199 |
| Davey + fuel | D10 | no pilot | 51 / 78 / 1657 | 0.002 | 0.000 |
| Davey + fuel | D10 | piloted | 4756 / 4160 / 1290 | 0.281 | 0.657 |
| waypoints | D7 | all | 63313 / 33780 / 32163 | 0.266 | 0.340 |
| waypoints | D7 | no pilot | 19539 / 23091 / 30004 | 0.150 | 0.000 |
| waypoints | D7 | piloted | 47517 / 10264 / 2080 | 0.399 | 0.677 |
| waypoints | D7 | planned descent | 2045 / 505 / 98 | 0.250 | 0.783 |
| waypoints | D9 | all | 1228 / 1054 / 304 | 0.160 | 0.336 |
| waypoints | D9 | no pilot | 13 / 5 / 258 | 0.002 | 0.000 |
| waypoints | D9 | piloted | 1125 / 965 / 533 | 0.289 | 0.606 |
| waypoints | D9 | planned descent | 194 / 266 / 77 | 0.266 | 0.648 |
| waypoints | D10 | all | 11197 / 9559 / 6516 | 0.113 | 0.256 |
| waypoints | D10 | no pilot | 80 / 34 / 5910 | 0.003 | 0.000 |
| waypoints | D10 | piloted | 10396 / 8948 / 2379 | 0.282 | 0.649 |
| waypoints | D10 | planned descent | 903 / 833 / 212 | 0.270 | 0.641 |

4. **Parameter bounds and sources.** a_bar U[0.75, 3.0] g: 11 Oct note; checked here against Report 1347 (upper edge supported; lower
   edge narrower than the source, open for Pete). L_eff U[0.5, 1.0] x 63.7 m: 11 Oct note (777-200ER length; lower half allows wings,
   engines and tail to separate); no test source, declared. Blend band 10-30 deg: 11 Oct note, declared arbitrary; sensitivity 5-45 deg.

## 7. Defects carried from the input (work order section 5)

1. Bank placeholder: `bank_assigned` = 1 rows; any attitude-dependent method must treat them as not assessed.
2. Pitch, sideslip, flap and gear configuration are not in the hand-off.
3. No-pilot alternate-configuration impact energy at or above the top of the Boeing range (median about 9.2 GJ): it enters the peak
   rate directly (P = KE v / L_eff); a declared sensitivity.
4. Piloted pull-out load factors above 2.5 g in 24-26 % of piloted weight and above 3.75 g in 7-8 % (end of flight, 8 Nov,
   `eof-piloted-load-factor-cap.csv`): relevant to in-flight break-up, which is a settling item and is not applied in this run.
5. Contact speed is ground-relative (wind included, current not subtracted); the surface is ISA sea level.

## 8. Files

In this folder: `manifest.json`; this note; `code/` (the module, the build, summary, sensitivity, transcription and figure scripts, and
the unit tests); `settling-energy-transfer-summary.csv`; `settling-energy-transfer-abar-sensitivity.csv`;
`naca-ditching-average-deceleration.csv`; the sidecar descriptions `settling-energy-transfer-m1-{df,wp}.json`; the figures
`settling-tau90-cdf` and `settling-abar-source-check` (working PNG, Word PNG at 600 dpi, vector PDF, proof with caption, caption text).
On the exchange: `EX:settling/energy-transfer-m1-2026-11-08/settling-energy-transfer-m1-{df,wp}.npz` with `SHA256SUMS` and `READY`,
and `sources/` (the four NACA and NASA PDFs).

Reproduce: `PYTHONPATH=code python code/build_sidecars.py <hand-off dir> <out dir>`, then `summarise.py`, `abar_sensitivity.py`,
`naca_tr1347_transport_runs.py` and `make_figures.py`; tests with `HANDOFF_DIR=... SIDECAR_DIR=... pytest code/`.

-- Ocean Settling Module, 8 Nov 2026
