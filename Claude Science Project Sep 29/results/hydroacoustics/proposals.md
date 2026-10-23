# Hydroacoustics: agent proposals waiting for Pete

*Built 23 Oct 2026 in the hydro clean-up run. A proposal is not a rule. When Pete rules, move his words to `decisions.md` and mark the row here.*

| id | proposal | origin | status |
|---|---|---|---|
| X01 | Energy feasibility ladder: coupling at q99 energy vs the F-35A value; <=10x feasible, 10-100x strained, >100x not feasible, >1 impossible | Take 2 review (a35831fe), 22 Oct | agent recommendation 23 Oct (Pete asked 'what do you recommend?'): ladder dropped. Tables give the physics limit (coupling > 1 = impossible) and p_prior_eta_ge_needed = P(coupling >= needed) under the prior, plus the multiple of 2.26e-3. Applied in potential-signals-2026-10-23-v3; not an explicit ruling. |
| X02 | Adopt the Metz-derived F-35A value 2.26e-3 (z_s 10 m, tau >= 1.1 s, with its spread) as one point of the coupling prior | metz-f35a track, coordination/architecture.md 22 Oct | agent recommendation 23 Oct (Pete asked why he was asked; literature check: Metz 2023 gives the arrival, not a coupling; Brown 2026 ~1e-4 is a different quantity that bundles channel coupling): 2.26e-3 applied to labels and the fixed column (run-j-gated-v3, tables v3). Registry eta_F35A_metz stays PENDING_RULING until Pete confirms. |
| X03 | Coupling prior bounds (currently log-uniform 1e-6 to 1e-2, 41 points) | composition track 22 Oct (agent choice) | Pete 23 Oct: 'yes, rebuild'; coupling prior log-uniform on [1e-6, 1] (1 = physical limit). DONE: run-j-gated-v3 (74 seeds), reductions results-data/composition_run_j/v3 (bounds 1, 1e-1, 1e-2); bound 1e-2 reproduces v2; verified (V9). |
| X04 | H08S airgun coincidence window 1.5 s (chance 3/10 for a 10 s shot cadence) | Take 2 review | Pete 23 Oct: estimate from the data. DONE: maximum-likelihood mixture fit, window +/-1.22 s about -0.11 s (sigma 0.38 s, 44/46 in window); results-data/tolerances_x04_x05; verified. |
| X05 | Royer known-event tolerance: cross-ID tolerance; H01W arrows +/-20 s; pick bars +/-2 s | clean-up run 23 Oct | Pete 23 Oct: ditto (estimate from the data). DONE: sigma from data (travel residual 0.46 %, pick 3.48 s, origin-time and epicentre errors); H01W Table 5 +/-7.0 s; Fig. 4 marks bias-corrected 13.1 s (offset not explained; question for Royer); verified. |
| X06 | Validate detector and timing on real same-ocean arrivals (Royer events, CMST 01:34) before any MH370 claim (gap G-W1, defect D05) | Take 2 review item 3; proposal v6 | DONE (first test): M1b detected 6 of 37 real arrivals vs 19.8 predicted by injection; missed CMST 01:33:44 (D1, D2 detect). Limits: amendment 2 post-hoc, one duplicate window, one land path; pre-registered timing not independently verifiable. Detector NOT validated (D05 stays). |
| X07 | Search all held IMOS records, not only the pre-registered windows (defect D24) | Take 2 review finding 14 | open |
| X08 | San Juan real-arrival test of the matched filter | 22 Oct module thread | open; Pete chose to wait for it before the downstream re-run |
| X09 | Amplitude-aware match term in the likelihood (gap G11-1) | composition track 22 Oct | open |
| X10 | Pre-registered crash-panel timing test with bathymetry paths, T-phase paths, primary-report inputs, IMS station positions, digitised boxes for every panel (defect D13) | clean-up session 23 Oct | open; before any question goes to Kadri |
| X11 | Replace the predicted-loudness chart per candidate with: implied coupling from each member, and what the other stations should have recorded | Take 2 review 22 Oct | open |
| X12 | Rewrite the Kadri package text (REQUESTS E1/E4, cover note) after the register: H01W 00:52:04 is time-consistent with Royer icequake A; H08S 01:12:49 coincides with an airgun shot | clean-up run 23 Oct | open; v3 predictions table built, text not rewritten |
| X13 | Independent verifier agent on every result before it goes to Pete | proposal v3-v6 | approved as part of the clean-up plan (Pete, 23 Oct: "OK, do the overnight run as proposed") |
| X14 | Parallel tracks only for mechanical compute with fixed registry inputs and a coded acceptance test | proposal v3-v6 | open |
| X15 | "One track in sequence" for re-runs | agent offer, thread 676a6e64 msg 429; repeated in a35831fe | NOT a rule. Pete, 23 Oct: "I didn't make a rule about one sequential track". |
| X16 | Source-depth and pulse-duration sensitivity in the MH370 level chain (defect D25) | Take 2 review item 7 | open |
| X17 | Ask Pete for the IMOS 3315 and 3275 March 2014 background (Curtin) to replace the paired-logger stand-in (defect D06) | Take 2 review item 12 | open |
