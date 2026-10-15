# Run J: coordination recommendations, 15 October 2026 (evening)

Inputs: `results/run-j-proposal.md` (draft), the core thread's run-J summary and its answers to Pete (seeds B″: free 18, waypoints 12, descent-climb 18, repro 18, about 12 h), `results/bfo-sd-check-2026-10-15/`, `results/fuel-feasibility-2026-10-15/`, `results/gates-bc-2026-10-15.md`, run I `README.md`.
Pete's three aims: (a) publication-ready, (b) include missed and previously noted items, (c) still able to find a breakthrough.
Family codes: A1 = cruise to FE then uncontrolled descent; A2 = cruise to FE then controlled or arrested descent; B = planned descent with ditching approach begun before FE.

## 0. Bottom line
Run J can start tonight. Five pre-flight checks come first (about 2 h, section 1); start it only if all five pass. Use size B″ as core recommends. Total time is about 12 h of filter plus staging, so the run ends late morning, not at dawn. The changes below cost almost no extra filter time. Most of them are extra **outputs**: they let the downstream modules ask the breakthrough questions without another filter run.

## 1. Pre-flight checks tonight (blocking)
1. **F3 time step** (job set up, f9efbe3; 40–50 min). If the 1 s and default steps differ outside seed noise, run J must use the corrected step. This must be known before 12 h are spent.
2. **Request 20 verdict** (split-half test, running). If it confirms "descent-limited, not parent-limited", take the pilots out of run J (saves about 9 h of pilot time) but keep 1.4 (below).
3. **Reproduction shoulder diagnostic** (BTO-only reproduction against Davey Fig 10.3 BTO-only; about 12 min). Our pure reproduction gives 0.078 against Davey's 0.2406 at his own 7 Hz. If the cause is a model difference on the BTO side, it changes the northern mass, and the fix belongs in run J. If it is not found tonight, run J goes ahead and the deficit is declared.
4. **Final-configuration smoke**: 1 seed per stratum at production particle count. Measure peak memory (cap 36 GiB) and wall time. Re-check gates B and C byte-identical at the frozen HEAD.
5. **Disk plan.** B″ output is about 69 GB (run I per-seed sizes: free 1.3 GB, waypoints 2.1, descent-climb 0.7, repro 0.5). deskstar has 38 GB free; the Mac has about 92 GB. Strata must be staged to `~/Downloads/mh370-exchange/core/run-j/` and deleted on deskstar between strata. Order: waypoints, repro, then free, descent-climb. The chain job must stop cleanly when free space is below the next stratum's size plus 5 GB.

## 2. Publication-ready (a)
1. **Freeze**: one tagged commit (`run-j`); the binary sha256, every config and data-file sha256, and the gate B/C and regress-seed1 values (−97.51251428262529) in `run-j/MANIFEST.md`. The paper cites the tag.
2. **Data and noise**: BFO sd 4.3177 Hz on all cruise BFOs (+0.56 nat against 7 Hz in the pure reproduction); 7 Hz as the declared sensitivity. 18:25:27 R600 burst included as ruled, 4.32 Hz, flagged as weak (C/N0 30.28 dB-Hz, BER 5); sensitivity at 6 Hz on that burst only.
3. **Convergence report per family** at its own seed count: canonical split-half (mean over all balanced partitions) against the floor recomputed for that count; per-seed ln Z and seed sd; mode shares; per-epoch effective sample size. Seeds can be added later, family by family, if a family is still below its floor.
4. **The out-of-sample 00:19 BTO check** in every family (posterior fitted to 00:11, residual at 00:19 in km of slant range, against the model's own spread). This is the strongest validation claim for the paper; run J should produce it directly, not in a later script.
5. **Pre-registered predictions** posted before submission (section 5).

## 3. Missed or previously noted items (b)
1. **Hand-offs** at m2241 and m0011 as in run I, so that end of flight can apply, without a new filter run:
   - D0 with the transmission imposed (airborne at 00:19:37);
   - request 9 (unbiased child weights), approved;
   - the uniform-onset prior for B;
   - the sampled bank limit;
   - surface pressure from ERA5 mean-sea-level pressure at impact (today `terminal.rs` hard-codes sea level 0 ft; a small but systematic bias).
2. **Fuel**: keep the per-particle FE time and the time in table extrapolation (85–95% of the mass touches it) as outputs, so that the paper can state how much of the FE timing rests on extrapolation.
3. **F4 bias drift**: off, as ruled. It is a terminal-stage sensitivity in end of flight.
4. **Waypoints carries 99.8% of the posterior**, so the headline PDF is the waypoint PDF. Free flight must converge too, because the paper shows the two side by side (the 6.78 nat preference is mostly prior volume).

## 4. Breakthrough capacity (c): cheap outputs that keep the open questions answerable
1. **A large distinct-parent hand-off at m0011** (for example 500k distinct candidates per seed in waypoints and free, as in the request 20 pass 1). Request 20 suggests the two-burst 00:19 readings (D3, D4) are limited by the descents per parent. The remedy is then in end of flight: many more descents, aimed at the 9,400–9,800 ft/min change in 8 s, for each candidate. That needs the candidates to exist. It costs disk, not filter time. This is the route to making Holland's readings estimable, which is the largest unresolved lever on the impact PDF.
2. **Path states for the whole-path received-power test.** Today only 2,000 routes per seed are stored, with latitude and longitude every 600 s. Raise this to about 20,000 per seed, and store at every BTO/BFO epoch the true heading, track, altitude, vertical rate, Mach and mode. This allows the no-precompensation received-power hypothesis to be tested over the whole path (the 6th arc alone does not separate 26 S from 37 S: median +0.19 dB). It is also the data for the paper's path figures. A few MB per seed.
3. **Per-epoch log-likelihood on the stored routes and hand-off rows.** Then the BFO-sd and 18:25 sensitivities can be checked by importance reweighting, with an ESS check, and need no second run. Where the ESS is too low, run the sensitivity on the cheap reproduction stratum only.
4. **Northern sampling.** The composer's searched-area evidence moves weight north (about 34–25 S), where the drift and Pléiades tensions also sit. Do not add a latitude-aimed proposal (not designed, and it would put a latitude choice into the sampler). Instead, tonight on the Mac (15 min, no deskstar), measure the composer's ESS north of the searched areas on run I. If it is below about 1,000, give free flight its seeds first, because free flight carries 2.5× the waypoint mass north of 30 S (0.023 against 0.009). The evidence-aimed look-ahead that core describes is the right design for run K.

## 5. Predictions to post before the GO (proposed; core to confirm or change)
1. The waypoints-vs-free preference stays within 6.78 ± 1.5 nat once free flight converges. If it falls below 3 nat, the waypoint headline becomes one hypothesis of two.
2. 4.3177 Hz raises the shoulder (34.5–36.5 S) by 0.05–0.12 in every family, and P(north of 30 S) by less than 0.02.
3. The 18:25 burst moves the 00:19 median by less than 0.3°.
4. The out-of-sample 00:19 BTO residual stays within the run I value ±20%.
5. All families reach their recomputed split-half floors except, possibly, descent-climb.

## 6. Not in run J
- The northern latitude-aimed proposal (item 2 of the change list): undesigned. Run K, as an evidence-aimed look-ahead.
- Request 20 pilots, if the split-half test confirms the descent-limited reading.
- Size C (5×): add seeds later instead.
- F4 drift in the filter.

## 7. Overnight supervision
Staging between strata needs a session to act during the night. Per Pete's rule (no overnight work on long threads), use a **fresh short thread** on the core profile whose only work is the run-J chain: watch, stage each stratum with SHA-256 checks, delete on deskstar, start the next. The long core thread (now about 400 messages) does the pre-flight checks and writes the order for that thread.
