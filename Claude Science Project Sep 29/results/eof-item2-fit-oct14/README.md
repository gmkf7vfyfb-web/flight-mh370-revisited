# Item 2 — Boeing-trace calibration of the free-flight parameters: leave-one-out result (14 Oct 2026)

**Result: the §8 gate FAILS.** No case passes out of sample; 13 of 62 case-targets are inside tolerance. The fit converged (Nelder–Mead stopped on tolerance in 192–319 evaluations per fit, no parameter at a search bound, leave-one-out parameters stable). The failure is structural: the main misfits are ones these seven parameters cannot remove (below). **Consequence:** the uncontrolled arm stays labelled *not calibrated*; no impact energy, attitude, flight-path angle or energy-transfer duration from it may be quoted as a physical prediction; run.toml bands are NOT changed.

## Design (approved by Pete 14 Oct, `results/eof-calibration-tolerances-oct13/README.md`)

One value per case per target; Gaussian residual with σ = tolerance/2; 7 shared parameters, no per-case nuisance; initial conditions from each trace at its loss of control (sim/boeing_events.py); the module's own free dynamics (integrator.rs `boeing_fit_batch`, production steps, Boeing's fitted wind) flown from there and joined to Boeing's trace before the loss; both traces measured by the same code (sim/eof_point_fit.py `features`). Prediction = the module's predictive mixture over its latent draws (bank magnitude, direction, divergent or neutral spiral) and over the unfitted aerodynamic bands (4 Sobol draws). **Effective observation count: 62 case-targets** (the plan estimated about 45), not the ~17,000 trace points; 7 parameters against 62. Declared choices made inside the module: end reference 1,500 ft (Boeing's records stop at 473–1,131 ft); mass 174 t (Boeing's not released); a missing feature scores at 3σ; a wrong dive class or turn direction scores zero; fit bounds wider than run.toml for the trim offset and doubling time.

## Fitted parameters (all data; range over the 10 leave-one-out fits)

| parameter | run.toml prior | fitted, all data | LOO range | free-cap sensitivity, all data |
|---|---|---|---|---|
| spiral_doubling_s | [60, 120] | 107.9 | 73.45 – 115.5 | 23.44 |
| trim_cl_offset | [-0.08, 0.08] | -0.1533 | -0.1603 – -0.1304 | -0.1461 |
| windmilling_per_engine | [0, 0.0015] | 0.0003439 | 0.0001961 – 0.0006397 | 0.0004707 |
| rat_increment | [0.0001, 0.0006] | 0.0004126 | 0.0003524 – 0.0005036 | 0.0004305 |
| residual_bank_deg | upper bound 35 | 18.59 | 13.35 – 18.7 | 6.982 |
| residual_bank_left_probability | 0.8 | 0.586 | 0.5131 – 0.7398 | 0.6239 |
| spiral_divergent_weight | 0.5 | 0.5001 | 0.4444 – 0.5556 | 0.5007 |
| spiral_bank_cap_deg | 90 (fixed) | not fitted | — | 62.02 |

The trim offset (−0.153) lies outside its run.toml band [−0.08, 0.08]: a **reach gap** in the band, not adopted.

## Out-of-sample result per case (each predicted by the fit that did not see it)

| case | dive case | passed | P(right dive class) | P(right direction) | targets outside tolerance (Boeing → model median, tolerance 2σ) |
|---|---|---|---|---|---|
| Case 01 | no | FAIL | 0.44 | 0.46 | phugoid period, s: 86 → 64 (±8.6); phugoid damping ratio: -0.01238 → 0.04982 (±0.02); bank 20 s after roll-off, deg: 6.575 → 11.46 (±2.02); peak descent rate, ft/min: 4800 → 7066 (±300) |
| Case 02 | no | FAIL | 0.44 | 0.44 | phugoid period, s: 83.5 → 64.5 (±8.35); phugoid damping ratio: -0.01333 → 0.04954 (±0.02); bank 20 s after roll-off, deg: 7.131 → 11.33 (±2.11); peak descent rate, ft/min: 6300 → 7017 (±315) |
| Case 03 | yes | FAIL | 0.42 | 0.46 | peak descent rate, ft/min: 5.346e+04 → 3.716e+04 (±6.84e+03); chord after 15,000 ft/min, NM: 4.707 → 2.455 (±0.5); distance first flame-out to 1,500 ft, NM: 20.35 → 16.93 (±2.03); time first flame-out to 1,500 ft, s: 434 → 356 (±43.4) |
| Case 04 | yes | FAIL | 0.44 | 0.24 | bank 20 s after roll-off, deg: 16.3 → 8.12 (±2.05); time to 15,000 ft/min from first flame-out, s: 169 → 320 (±16.9); peak descent rate, ft/min: 3.36e+04 → 4.453e+04 (±3.37e+03); chord after 15,000 ft/min, NM: 6.13 → 2.194 (±0.613); distance first flame-out to 1,500 ft, NM: 10.56 → 11.65 (±1.06); time first flame-out to 1,500 ft, s: 308 → 360 (±30.8) |
| Case 05 | yes | FAIL | 0.44 | 0.44 | phugoid period, s: 87 → 74 (±8.7); phugoid damping ratio: -0.0216 → 0.07024 (±0.02); bank 20 s after roll-off, deg: 6.645 → 11.07 (±2.03); time to 15,000 ft/min from first flame-out, s: 1719 → 1022 (±172); peak descent rate, ft/min: 2.418e+04 → 5.309e+04 (±2.73e+03); chord after 15,000 ft/min, NM: 4.936 → 1.028 (±0.5); distance first flame-out to 1,500 ft, NM: 96.87 → 82.51 (±9.69); time first flame-out to 1,500 ft, s: 1798 → 1058 (±180) |
| Case 06 | yes | FAIL | 0.38 | 0.30 | time to 15,000 ft/min from first flame-out, s: 158 → 320 (±15.8); peak descent rate, ft/min: 4.338e+04 → 2.59e+04 (±4.35e+03); chord after 15,000 ft/min, NM: 8.036 → 2.595 (±0.804); distance first flame-out to 1,500 ft, NM: 12.3 → 9.449 (±1.23); time first flame-out to 1,500 ft, s: 245 → 349 (±24.5) |
| Case 07 | no | FAIL | 0.44 | 0.45 | phugoid period, s: 85 → 64 (±8.5); phugoid damping ratio: -0.01361 → 0.04966 (±0.02); bank 20 s after roll-off, deg: 6.592 → 11.41 (±2.02); peak descent rate, ft/min: 4920 → 7025 (±300) |
| Case 08 | no | FAIL | 0.44 | 0.57 | phugoid period, s: 82 → 64 (±8.2); phugoid damping ratio: -0.008213 → 0.05049 (±0.02); bank 20 s after roll-off, deg: 7.655 → 13.89 (±2.02); distance first flame-out to 1,500 ft, NM: 60.4 → 74.8 (±6.04); time first flame-out to 1,500 ft, s: 2066 → 2325 (±207) |
| Case 09 | no | FAIL | 0.44 | 0.45 | phugoid period, s: 83 → 66 (±8.3); phugoid damping ratio: -0.009017 → 0.04891 (±0.02); bank 20 s after roll-off, deg: 7.847 → 11.09 (±2.02); time first flame-out to 1,500 ft, s: 2074 → 2320 (±207) |
| Case 10 | yes | FAIL | 0.44 | 0.29 | bank 20 s after roll-off, deg: 15.78 → 8.273 (±2.28); time to 15,000 ft/min from first flame-out, s: 172 → 308 (±17.2); peak descent rate, ft/min: 5.802e+04 → 4.401e+04 (±6.05e+03); chord after 15,000 ft/min, NM: 7.322 → 2.485 (±0.732); distance first flame-out to 1,500 ft, NM: 9.036 → 12.32 (±1) |

Full per-target table: `primary/loo-table.csv` (Boeing value, tolerance, out-of-sample median, residual, P(within tolerance), all-data median).

## Why it fails — reach gaps, each outside what these 7 parameters can move

1. **Glide phugoid (cases 1, 2, 5, 7, 8, 9).** Model period 64–74 s and damping ratio +0.05 to +0.07, against Boeing's 82–87 s and −0.01 to −0.02 (neutral to slightly divergent). A fixed-lift point mass gives Lanchester's period π√2·V/g at the speed it flies; Boeing's longer, undamped oscillation is what a speed-holding flight-control law produces. The point mass has no such term.
2. **Dive onset and shape (cases 3, 4, 6, 10).** The short cases pass 15,000 ft/min 158–172 s after the first flame-out; the model takes 308–320 s at the fitted 108 s doubling. Boeing's dives in cases 3, 4, 6 and 10 last 87–157 s after the crossing and cover 4.7–8.0 NM; the model's last 29–40 s in cases 4 and 6 and cover 2.2–2.6 NM in cases 3, 4 and 6, with the bank cap at 90°. Freeing the cap (sensitivity) moves it to 62° and the doubling to 23 s but makes the out-of-sample total worse (−1,527 against −1,282 nat) and passes fewer targets (6 against 13).
3. **Dive class is not predictable.** The divergent-spiral draw is independent of the state at the loss, so every case gets the same dive probability (0.38–0.44 in the primary fit). The approved criterion asks for the right yes/no in all ten cases; a model with no state-dependent dive trigger cannot meet it by construction.
4. **Case 5** (a glide that becomes a dive about 850 s after the loss) is the worst case in both fits (−390 and −745 nat): one doubling time cannot serve both its long glide and the short cases' early dives.

## Declared limitation (unchanged)

All ten Boeing cases are uncontrolled; the piloted and deliberate families have no trace data, so even a pass here would validate the uncontrolled arm only.

## Files

`primary/` (the approved fit) and `sensitivity-free-cap/` (POST-HOC, declared, not the gate): `summary.json`, `loo-table.csv`, `summary.txt`, `fit-all.json`, `fit-loo-caseNN.json` (Boeing summary features only; the traces are not redistributed). Code: `hypotheses/end-of-flight/sim/eof_point_fit.py`, `sim/eof_point_fit_summary.py`, `full/run_item2_fit.sh`, `full/run_item2_sens.sh`; test binary `mh370-eof-test-o14` (sha256 9f8e3282…).


## Round 2 — reach extension (Pete 14 Oct; design fixed before fitting in `PREREG-v2.md`): the gate STILL FAILS

11 shared parameters; converged (354 evaluations for the all-data fit; leave-one-out parameters stable). Out-of-sample total -904.2 nat against -1282.0 in round 1; case-targets inside tolerance 18 of 62 against 13. No case passes. One parameter sits at a search bound: the dive-trigger scale at 2 kt (a step between the long and short cases' EAS at the loss). Files: `round2/`.

| parameter | round 2, all data | LOO range |
|---|---|---|
| spiral_doubling_s | 26.24 | 22.99 – 34.25 |
| trim_cl_offset | -0.0939 | -0.103 – -0.08019 |
| windmilling_per_engine | 0.0005146 | 0.0001495 – 0.0007522 |
| rat_increment | 0.0003248 | 0.0003024 – 0.0004836 |
| spiral_bank_cap_deg | 63.46 | 55.48 – 63.99 |
| free_lift_speed_exponent | 0.8736 | 0.5788 – 1.236 |
| free_path_damping | -0.07652 | -0.1266 – 0.246 |
| residual_bank_deg | 10.07 | 6.93 – 10.73 |
| residual_bank_left_probability | 0.7207 | 0.6321 – 0.98 |
| dive_trigger_eas_mid_kt | 182.5 | 181.7 – 201.6 |
| dive_trigger_eas_scale_kt | 2 | 2 – 2 |

| case | passed (round 1 → 2) | P(right dive class) | P(right direction) | targets still outside tolerance (Boeing → model median) |
|---|---|---|---|---|
| Case 01 | 2/6 → 3/6 | 0.99 | 0.26 | phugoid period, s: 86 → 68.5; phugoid damping ratio: -0.01238 → 0.02679; peak descent, ft/min: 4800 → 6525 |
| Case 02 | 2/6 → 3/6 | 0.94 | 0.41 | phugoid period, s: 83.5 → 72; phugoid damping ratio: -0.01333 → 0.02893; time to 1,500 ft, s: 2286 → 2535 |
| Case 03 | 2/6 → 1/6 | 0.55 | 0.92 | time to 15,000 ft/min, s: 305 → 114; peak descent, ft/min: 5.346e+04 → 2.529e+04; chord after 15,000 ft/min, NM: 4.707 → 7.731; distance to 1,500 ft, NM: 20.35 → 13.53; time to 1,500 ft, s: 434 → 626 |
| Case 04 | 0/6 → 1/6 | 0.70 | 0.07 | bank 20 s after roll-off, deg: 16.3 → 8.402; time to 15,000 ft/min, s: 169 → 144; peak descent, ft/min: 3.36e+04 → 2.806e+04; chord after 15,000 ft/min, NM: 6.13 → 4.878; time to 1,500 ft, s: 308 → 495 |
| Case 05 | 0/8 → 0/8 | 0.00 | 0.40 | phugoid period, s: not produced; phugoid damping ratio: not produced; bank 20 s after roll-off, deg: 6.645 → 14.31; time to 15,000 ft/min, s: 1719 → 871.8; peak descent, ft/min: 2.418e+04 → 1.805e+04; chord after 15,000 ft/min, NM: 4.936 → 2.835; distance to 1,500 ft, NM: 96.87 → 79.82; time to 1,500 ft, s: 1798 → 1273 |
| Case 06 | 1/6 → 1/6 | 0.61 | 0.31 | time to 15,000 ft/min, s: 158 → 122; peak descent, ft/min: 4.338e+04 → 3.069e+04; chord after 15,000 ft/min, NM: 8.036 → 5.557; distance to 1,500 ft, NM: 12.3 → 9.593; time to 1,500 ft, s: 245 → 189 |
| Case 07 | 2/6 → 3/6 | 0.98 | 0.38 | phugoid period, s: 85 → 76; phugoid damping ratio: -0.01361 → 0.03247; peak descent, ft/min: 4920 → 6516 |
| Case 08 | 1/6 → 2/6 | 1.00 | 0.31 | phugoid damping ratio: -0.008213 → 0.03972; peak descent, ft/min: 7140 → 6268; distance to 1,500 ft, NM: 60.4 → 82.99; time to 1,500 ft, s: 2066 → 2407 |
| Case 09 | 2/6 → 2/6 | 0.99 | 0.56 | phugoid period, s: 83 → 70; phugoid damping ratio: -0.009017 → 0.02589; peak descent, ft/min: 6900 → 5791; time to 1,500 ft, s: 2074 → 2374 |
| Case 10 | 1/6 → 2/6 | 0.81 | 0.20 | bank 20 s after roll-off, deg: 15.78 → 9.66; time to 15,000 ft/min, s: 172 → 126; peak descent, ft/min: 5.802e+04 → 2.938e+04; chord after 15,000 ft/min, NM: 7.322 → 5.584 |

**What round 2 fixed and what it did not.** The dive trigger now gets the dive class right in the glide cases (P 0.94–1.00) and in
cases 3, 4, 6, 10 (0.55–0.81). Glide bank 20 s after roll-off now fits. In cases 4, 6 and 10 the dives now pass 15,000 ft/min 122–144 s after the
first flame-out (Boeing 158–172 s; round 1 308–320 s), and their chords are 4.9–5.6 NM (Boeing 6.1–8.0; round 1 2.2–2.6). Case 3 is now
early and long instead (114 s against 305 s; chord 7.7 NM against 4.7). Not fixed:
(1) the **glide phugoid**: period 68.5–76 s and damping ratio +0.026 to +0.040 against 82–86 s and about −0.01; a diagnostic at the all-data
optimum (not part of the fit) gives the right period at n = 1.3 but a worse total (749.5 against 668.8 nat), and any negative damping k
both shortens the period and drives the glides into dives (total → ∞ at k = −0.2), so a speed-exponent and a path-angle term cannot
produce Boeing's long, neutral phugoid together with its other targets; (2) **case 5** (a glide that dives about 850 s after the loss) is
classified as a glide (P(dive) 0.00): a trigger on the state at the loss cannot see a late dive; (3) **turn direction** in the right-turning
dives (cases 4, 6, 10: P 0.07–0.31), because one left-turn probability serves all cases; (4) dive **peak descent rate** and **time to
1,500 ft** remain outside tolerance in most dive cases.

**Status.** Gate failed in round 2 as in round 1. Per `PREREG-v2.md`, run.toml is not changed and the uncontrolled arm stays labelled
*not calibrated*. Round 2 is better out of sample (−904 against −1,282 nat), so its laws are a candidate improvement, not a calibration.
The round-2 production code is in the module, off by default and bit-identical without its configuration.

