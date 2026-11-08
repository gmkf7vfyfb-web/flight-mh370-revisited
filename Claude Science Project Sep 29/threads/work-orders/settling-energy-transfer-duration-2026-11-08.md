# Work order: energy-transfer duration at impact moves to ocean settling (8 Nov 2026)

From: End of Flight Module (session a7d0bbfc), for Pete. To: Ocean Settling Module.
Status: Pete's ruling of 8 Nov 2026. Read this whole order before you start.

## 1. The ruling

1. Settling owns everything that happens after x_Impact. x_Impact is the state at the moment impact begins (first water contact).
2. This includes the mechanical energy-transfer duration and its companion columns (section 4). Before this ruling, end of flight owned them (architecture ruling of 8 Oct 2026, `coordination/END_OF_FLIGHT.md`). That allocation is superseded. The column definitions and the five qualifications of 8 Oct stay in force.
3. Hydroacoustics still owns the acoustic source duration and the received-signal duration. It must not infer a duration from received signals and return it to an earlier stage (ruling of 8 Oct). The same rule now applies to settling: no settling parameter may be tuned on hydrophone data.
4. End of flight now ends at the contact state. It hands off the contact state and the weights. It computes no water-entry quantity.

## 2. What to build (first pass)

1. Port the existing first-order water-entry model, `impact_tau_method = 1`, into settling. It is in `results/eof-impact-tau-method-oct11.md` (end of flight, 11 Oct 2026). It was used for the Run C and Run J sidecars (`tau90_v1.npz`). It uses only the contact speed v, the flight-path angle gamma and the mass m, plus declared random parameters. It never reads the family label. Keep that property.
2. Summary of method 1 (the note is the authority; check every formula against it):
   - Shallow entry, theta = |gamma| <= 10 deg: constant mean longitudinal deceleration a_bar ~ U[0.75 g, 3.0 g] per row. T = v / a_bar. F(t) = 1 - (1 - t/T)^2. t05 = 0.0253 T, t95 = 0.776 T, tau90 = 0.751 v / a_bar. Peak rate = m a_bar v.
   - Steep entry, theta >= 30 deg: progressive crushing (Riera 1968 picture on a water target). L_eff ~ U[0.5, 1.0] x 63.7 m. tau90 = 0.9 L_eff / v, t05 = 0.05 L_eff / v. Peak rate about KE v / L_eff.
   - Blend, 10 < theta < 30 deg: log-linear in theta with w = (theta - 10)/20 for tau90, t05, t95 and peak rate. Sensitivity: band edges 5 and 45 deg.
   - impact_energy_transferred_j = contact kinetic energy (declared upper bound). energy_transfer_n_pulses = 1 (declared single-pulse model). Method id 1.
   - Expected magnitudes (from the note): ditching at 70 m/s, tau90 about 1.8-7 s; steep entry at 200 m/s, 0.14-0.29 s; at 300 m/s, 0.10-0.19 s. Reproduce these as a unit test.
3. Open source check carried over from the method note (do it before the result is called CURRENT): the a_bar range came from search-engine summaries of NACA reports. Check it against the original tables: NACA RM SL9H05a, NACA Report 1347 (Fisher and Hoffman), NACA RM SL55K08 (Boeing 707). If a report is not found, write "not retrieved — ask Pete" and record the search (labels rule of 22 Oct).
4. The end-of-flight assistant had suggested tau = L / V with a wide spread for shallow impacts (8 Nov). Method 1 already covers this and more. Use method 1. Do not add a second rule.
5. Keep energy-transfer duration separate from your sinking event sequence (qualification 3 of 8 Oct): flooding, implosion and seabed contact do not lengthen it. Break-up stays in settling, as before. If you later compute tau per fragment class, that is a method 2 with its own note.

## 3. Inputs: the final end-of-flight hand-off (7 Nov 2026, status UNCHECKED)

1. Files (exchange): `EX:end-of-flight/final-2026-11-07/results/eof-final-handoff-df.npz` (Davey model + fuel, main configuration, 501,102 rows, 16 seeds) and `eof-final-handoff-wp.npz` (waypoints, 500,198 rows, 24 seeds). Each has a `.json` description. Check `SHA256SUMS` and `READY` in the same folder before use. Repo result folder: `results/end-of-flight/eof-publication-run-2026-11-07/`.
2. Platform copies: handoff-df.npz 4d45eed1-578b-46d8-90d9-0d5d87fbbd04 (json 62bbd6f4-362f-4a84-b2c2-738809eb42fb); handoff-wp.npz b919b696-b0da-4041-9364-accf33a71f6f (json 1bc6f4cf-10c0-4874-9b2a-bfabfd5878c3). The exchange file is the source; check the SHA-256.
3. Columns per row: latitude_deg, longitude_deg, arc_distance_nm_signed, impact_s_after_001929, kinetic_energy_j, vertical_kinetic_energy_j, mass_kg, flight_path_angle_deg_descent_positive, bank_deg, ground_track_deg, ground_speed_mps, reached_sea, max_mach, max_eas_kt, max_load_factor_g, min_load_factor_g, vertical_speed_001929_fpm, vertical_speed_001937_fpm, family_code (1 no pilot after fuel exhaustion, 2 piloted after fuel exhaustion, 3 planned descent), electrical_configuration_code (0 mixture, 1 normal, 2 alternate), first_flameout_s_after_001929, final_flameout_s_after_001929, seed, arrested_dive, late_steep_ending, and log_weight_<treatment> for D13, D0, D7, D8, D9, D10, D14, D11, D12.
4. Contact state conventions:
   - kinetic_energy_j = 0.5 m (V_h^2 + V_z^2). V_h is the ground speed (wind included); V_z the vertical speed. Ocean current is not subtracted (declared, order 0.5 m/s).
   - Contact speed for method 1: v = sqrt(2 KE / m). gamma = flight_path_angle_deg_descent_positive (ground-relative, positive in descent, from the kinetic energies).
   - mass_kg = zero-fuel mass 174,196 kg plus fuel left (1-99 % range 174,193-174,969 kg).
   - The surface is ISA sea level, not the local sea surface (core request 5; small common bias).
5. Weights: w = exp(log_weight_<treatment>), normalised. Every downstream module scores these same rows (composition rule 3). Variants need re-weighting from the run folder; the hand-off carries headline weights only.

## 4. Columns to emit (contract of 8 Oct, unchanged)

Row-aligned sidecar per route model, one row per hand-off row, no reordering:
`impact_energy_transferred_j`, `energy_transfer_t05_s`, `energy_transfer_t95_s`, `energy_transfer_tau90_s`, `energy_transfer_peak_rate_w`, `energy_transfer_n_pulses`, plus `kinetic_energy_at_contact_j` (copied, never aliased to energy transferred), `impact_tau_method`, the regime weight `w_steep`, the drawn `a_bar_mps2` and `l_eff_m`, and a flag `bank_assigned` (section 5). Seed the draws by route model, seed and row index, so the sidecar is reproducible. NaN means "not computed" and is a result; never fill with a guess.

## 5. Known defects in the inputs that you must carry, not hide

1. Bank is a placeholder for engine-flown rows. bank_deg is exactly 0.0 in 67.5 % of piloted rows (Davey model + fuel), 66.5 % (waypoints) and 72.2 % of planned-descent rows. No-pilot rows have computed bank (0.1 % zeros). Method 1 does not use bank. Any later attitude-dependent method must treat these rows as "not assessed". Set bank_assigned = 1 where family_code is 2 or 3 and bank_deg == 0.0.
2. Pitch attitude, sideslip, flap and gear configuration are not in the hand-off. Method 1 does not need them.
3. Impact energy of no-pilot alternate-configuration dives is at or above the top of the Boeing range (median about 9.2 GJ against 6.4-9.0 GJ for Boeing alternate runs 3, 4, 6, 10). Use it as a declared sensitivity. Peak Mach is NaN for engine-flown rows (not stored in Run J).
4. Piloted pull-out load factors: the Run J piloted ceiling was U[1.5, 5.0] g; under both frequencies 24-26 % of piloted weight exceeds 2.5 g and 7-8 % exceeds 3.75 g (end of flight, 8 Nov, `eof-piloted-load-factor-cap.csv` e237bf0a). This matters for in-flight break-up, which is yours. Report it; do not change end-of-flight weights.
5. Provisional cells (fewer than 500 effective no-pilot paths): Davey model + fuel D9 (ESS 156) and D11 (ESS 489); waypoints D9 (ESS 261).

## 6. The current end-of-flight model (final run, 7 Nov 2026), for context

1. Start: the core filtering distribution at 00:10:59 (22:41 for the planned descent), equally weighted, with per-tank fuel. Power from at least one engine at 00:10:59.
2. Powered flight to the power loss: the engine's flight model (autopilot mode, ERA5 wind and temperature, per-tank fuel burn). Right engine flames out first. Normal configuration: one-engine drift-down under the autopilot until the second flame-out.
3. Draws: family H_E from the onset model (equal weight over permitted onset and control combinations); electrical configuration K with P(alternate) = 0.5. Power loss at the second flame-out (normal) or the first (alternate); this starts the log-on clock.
4. No pilot, normal configuration: one of the six Boeing normal-configuration runs replayed from the path's own state with the pre-registered spread (phugoid glide); a diverging phugoid ends in a steep descent flown by the dive model.
5. No pilot, alternate configuration: case-informed three-degree-of-freedom dive model (build-up prior fitted to 12 accident cases and the four Boeing alternate runs; Lock drag rise; CS-25.337 limits; arrest probability Beta(5,2); left engine thrust until its flame-out). Pre-registered tests A and B passed.
6. Piloted after fuel exhaustion and planned descent: Run J engine trajectories (point-mass, pilot laws), re-weighted, not re-flown. Piloted paths that later lose control are excluded from the headline. Planned descent exists only in the waypoint model.
7. 00:19 treatments: 9 headline, 6 sensitivities; no prior on treatments; evidence compared only within the same data group. Log-on cause prior 0.75 fuel exhaustion / 0.25 other.
8. Impact geometry under both frequencies: no-pilot weight 99.6 % at gamma >= 30 deg; piloted weight about 48 % at gamma <= 10 deg and about 8-10 % at gamma >= 30 deg (D10). So both regimes of method 1 carry weight.
9. Known code inconsistency, small: the other-cause survival factor in the log-on term uses the final flame-out in the alternate configuration (`eof-logon-cause-posterior.csv` 2b361daf). It changes shares by at most 0.02. Fixed in the next end-of-flight run.

## 7. Deliverables

1. Code in the settling module directory; unit tests for section 2 item 2 magnitudes and for row alignment.
2. Results in `results/ocean-settling/<run id>/` with `manifest.json` (status UNCHECKED), sidecars for both route models (or on the exchange with SHA256SUMS and READY if large), and a method note under the settling name that supersedes the end-of-flight note as the owner's method (keep a pointer to the 11 Oct note; do not edit it).
3. Weighted summaries for D7, D9 and D10 (both route models): tau90 5/50/95 %, regime shares, peak-rate range, and the band-edge sensitivity. Figures in working and JON forms (no titles or notes on the image; letter-only panel labels; caption beneath; greyscale; 127 mm).
4. Inbox entries: `coordination/HYDROACOUSTICS.md` (the new source of the duration columns and the sidecar path) and `coordination/architecture.md` (ownership change done). Commit at each step; `make check` in registry; `git pull --rebase` before push.
5. Compute: Python on about one million rows; minutes. No heavy lock needed. Ask Pete before anything over 1.5 h.

## 8. Rules that bind this order

Labels rule (22 Oct); repository rule (26 Oct); JON graphics rules (7 Nov); closing-answer rules (ASD-STE100 summary, technical paragraphs, Key assumptions and modelling choices, every artifact linked by version id); check every number against its file; look at every figure.

-- End of Flight Module (session a7d0bbfc), 8 Nov 2026
