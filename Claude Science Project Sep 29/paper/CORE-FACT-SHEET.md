# Core estimator fact sheet — Run J (checked against source)

Purpose: a check list for the Methodology "core" text. It is not paper text.
Source: git tag `run-j` (1244b7c) on branch `claude-science-sep29`, read 31 Oct 2026 (branch head bc4a900).
Files read: `engine/scripts/job-run-j.sh` (config chains), `engine/config/davey2016.toml`, `davey2016-inmarsat.toml`,
`config/sensitivity/{no-exhaustion-prior, reference-snapshots, handoff-lookahead-d}.toml`, `fuel-fixes/s1–s8, inop-flow-fix`,
`early-families/{radar-full, route-sampler, free, descent-climb, speed-envelope-throughout}.toml`, `run-j/*.toml`,
`engine/data/variants/satcom-observations-bfo432.csv`, `crates/{flight,satcom,mh370}` doc comments, `results/run-j/README.md`.

Labels use the architecture definitions (still proposed): **R** reproduced = as Davey et al. (2016);
**U** updated = same element, better data; **M** modified = Davey element, changed method or assumption;
**E** extended = element Davey did not have. "Davey" = Davey et al. (2016), key `davey2016`.

## A. What the core estimator does (18:01:49 to 00:19:37 UTC)

| # | Element | What Run J does | Davey | Label |
|---|---|---|---|---|
| 1 | Estimator | Particle filter. Sequential importance weighting; systematic resampling when ESS < 0.5 N. | ch. 8–10 | R |
| 2 | Prior, 18:01:49 | 5.624829 N, 99.048157 E, σ 0.5 NM; track 289.7° true, σ 1.0° (Fig. 4.2 digitised). Runs before 9 Oct used 295.66°. | ch. 4 (not tabulated) | R (reconstructed) |
| 3 | Cruise dynamics | Ornstein–Uhlenbeck processes on Mach, control angle and wind error; TAS from local temperature; five autopilot modes (true/magnetic heading, true/magnetic track, LNAV). Turns, Mach and altitude changes at exponential gaps of common mean τ, Jeffreys prior on 0.1–10 h. Table 8.2 values. Bank 15°. LNAV reverts to heading hold, mean 8.66 h (6/ln 2 h). Steps 10 s cruise, 5 s manoeuvre. | ch. 6–8, Table 8.2 | R |
| 4 | Speed and level priors | Repro family: Mach 0.73–0.84, FL250–430 (Davey). Other families: Mach 0.45–0.87 to 18:40, then 0.70–0.87; 210–330 KCAS clip throughout. | Assumption 4 (Mach floor 0.73) | M |
| 5 | Wind and temperature | ERA5. Sensitivities: NCEP FNL (closest public analogue of ACCESS-G), MERRA-2. | ACCESS-G analysis | U |
| 6 | Magnetic declination | IGRF-14. Sensitivity: IGRF-11 (what Davey's NOAA source served in 2014). | NOAA IGRF grid | U |
| 7 | Satellite states | Inmarsat published states (Ashton et al. 2015, Table 4), the set the BTO bias and satellite+EAFC terms were derived with. | — | U (check wording) |
| 8 | BTO model | Round trip GES–satellite–aircraft minus fixed offset; Gaussian. σ 29 µs (R1200), 43 µs (anomalous R1200 log-on acknowledge), 63 µs (R600 log-on request). | ch. 5 | R |
| 9 | BFO model | Uplink and downlink Doppler, aircraft pre-compensation to nominal satellite at 64.5° E, satellite+EAFC term, constant bias N(150, 25²) Hz marginalised per particle by a scalar Kalman filter (Rao–Blackwellised). | §5.3, §8.1 | R |
| 10 | BFO vertical rate | Modelled vertical speed enters the BFO (17.5 Hz per 1,000 ft/min at 00:11). | omitted (§7.2) | M |
| 11 | BFO noise | σ 4.3177 Hz on every BFO (Davey Table 5.1, in-flight value). 7 Hz is a declared sensitivity. | 7 Hz in filter | M |
| 12 | SATCOM data used | **10 BTOs**: 18:25:34 (R1200, empirical offset applied), 18:28:05, 18:28:14, 19:41, 20:41, 21:41, 22:41, 00:10:59, 00:19:29 (R600), 00:19:37 (R1200, empirical offset −4 × 7,820 µs applied). **9 BFOs**: 18:28:05, 18:28:14, 18:39:55 (mean of 51 C-channel), 19:41, 20:41, 21:41, 22:41, 23:15:02 (mean of 29 C-channel), 00:10:59. **Not used**: 00:19 BFOs; 18:25:27 R600 burst (held out, predictive check: 0.9σ BFO, 1.2σ BTO). | ch. 5 | R (00:19 both BTOs = Davey treatment) |
| 13 | Radar after 18:01:49 | 5 position fixes: 18:04:14, 18:05:15 (σ 5 NM), 18:07:16 (σ 3 NM), 18:13:36, 18:22:12 (σ 5 NM), Gaussian with 10 % outlier component (σ 50 NM). 4 across-track fixes on the VAMPI–MEKAR band at 18:15, 18:17, 18:19, 18:21 (σ 1.5 NM). 18:07:06 plot excluded (physically impossible). | prior only; 18:22 used qualitatively | E |
| 14 | Fuel flow | internal-v1 grid; temperature term 1 + 0.003 ΔISA (1 + 0.2 M²); per-path factor κ ~ N(1.0004, 0.0196²); fuel at 18:01:49 = 43,800 − κ × 7,228 kg; ZFW 174,196 kg; levels capped at weight-dependent ceiling; extrapolated-step factor κₓ ~ N(1.0, 0.046²) (PROVISIONAL). | not modelled (Assumption 4) | E |
| 15 | Two tanks | L − R ~ N(221, 120²) kg at 18:01:49; R:L flow ~ N(1.021, 0.008²); engines exhaust separately; live engine on one-engine flow (internal-v1 INOP flow × 0.5 fix). | — | E (PROVISIONAL) |
| 16 | One-engine flight | After first flame-out: hold altitude, KCAS decays U(7, 11) kt/min to drift-down KCAS U(207, 227), tapering descent to about 1,000 ft above one-engine ceiling; lateral autopilot mode unchanged (stated assumption). | — | E (PROVISIONAL) |
| 17 | Powered flight at 00:11 | Weight zero (hard reject) if no engine runs at 00:10:59. Endurance proposal drops paths that cannot reach 00:10:59 and draws Mach from a mixture (0.15 prior), weight corrected exactly. **No exhaustion-time prior**: the 00:19 log-on is not used as fuel-exhaustion evidence; 40–52 % of paths run dry 00:11–00:19:29 unprompted. Results are "conditional on engine power at 00:11". | — | E |
| 18 | Early-flight hypotheses | Four families: repro (Davey dynamics from 18:01:49); free (50 % turn at 18:22:12 to 270–340°); descent-climb (excursion starting 18:01:49–18:05 to 2,000–10,000 ft, ending 18:13–18:18, plus the turn); waypoints (VAMPI–MEKAR to 18:21, then 1–8 legs, mean 3, through named fixes; break-off at 20/40/60/80 %; fly-by or fly-over; turn-backs; no fixes south of 4.5° S; change to an autopilot mode at the last fix or mid-leg west of 96° E). Combined by evidence at equal family prior: waypoints 0.9982, free 0.0013, repro 0.0003, descent-climb 0.0002. | — | E |
| 19 | Static parameters | One filter per autopilot mode (stratified); P(mode \| data) ∝ prior × Z_mode. τ Gibbs-refreshed from its path conditional after each resampling (resample–move). | variable-rate branching, §10.4 | M |
| 20 | Tempering | At 18:39, 19:41, 20:41, 21:41, 22:41 and 00:11 the likelihood is applied in 16 equal stages (exponents multiply to one; target unchanged). | — | M (sampler only) |
| 21 | Hand-offs | Full-state draws at 22:41 and 00:11 (100,000 rows per seed), look-ahead to the next epoch (oversample 50, defensive 0.2). Final state at 00:19:37. | — | E |
| 22 | Scale | 74 seeds, 406 M particles: waypoints 24 × 7 M, free 18 × 7 M, descent-climb 16 × 3.5 M, repro 16 × 3.5 M. Per-mode split [1.0, 0.5, 2.5, 0.5, 2.5] M at 7 M. Plus companions 16 × 3.5 M. | — | E (scale and replication) |
| 23 | Convergence | Split-half over all balanced seed partitions: waypoints 0.934, free 0.873, descent-climb 0.871, repro 0.921. PASS by Pete's ruling, 16 Oct 2026. North of 33° S remains Monte-Carlo limited. | no published floor | E |

## B. Points to decide or correct

1. **00:19 data in core (row 12).** Run J used both 00:19 BTOs and no 00:19 BFOs. This is Davey's treatment, not "R600 BTO only".
   The 00:11 hand-off has not seen 00:19, so the End of Flight D1 (R600 BTO only) results are not affected. The core 00:19 latitude PDF (final.npy) is.
   Your wording rule applies: "R1200 BTO, empirical offset applied", not "bias correction".
2. **Draft p. 7, "7 million candidates across 8 runs, 56 million in total".** Run J is 74 seeds and 406 M particles (row 22). 7 M per seed applies to waypoints and free only.
3. **The Run J "repro" family is not a pure Davey reproduction.** It carries rows 10–17 (fuel, tanks, one engine, power at 00:11, radar, 4.32 Hz, BFO vertical rate). The best Davey match on the charts is the 25 Sep run "complex-manoeuvres" (τ 0.1–1 h, 7 Hz, track 295.66°). The R/U/M/E table must say which run each label rests on.
4. **Waypoint family dominance (row 18).** At equal family prior it carries 99.82 % of the mass, so the combined posterior is in practice the waypoint posterior. A reviewer will ask why the family prior is equal.
5. **Fuel at 18:01:49 (draft p. 7, "fuel state … can be estimated").** It is not independent: it is 43,800 − κ × 7,228 kg, tied to the same flow factor κ (row 14).
6. **Row 7 label.** Check whether Davey used the same Inmarsat satellite states; if yes, row 7 is R, not U.

## C. Citation keys (ledger `paper/references.bib` + `references-paper-added.bib`)

Present: `davey2016`, `ashton2015`, `holland2018`, `era5` (Hersbach et al. 2020), `sir2018`, `stone2014`.
Added 31 Oct 2026 (CrossRef-verified): `gordon1993` (bootstrap filter), `kitagawa1996` (systematic resampling),
`gilks2001` (resample–move), `neal2001` (annealed importance sampling), `delmoral2006` (SMC samplers).
Still needed: IGRF-14 generation paper (not yet found in CrossRef; special-issue record only); internal-v1 fuel model source (fuel session).
