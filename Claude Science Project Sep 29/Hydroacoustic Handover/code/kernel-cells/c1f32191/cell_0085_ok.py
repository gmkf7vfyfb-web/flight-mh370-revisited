out = {
 "block": "11 — composition (two-site coincidence, 95 % upper limits on coupling, Bayes factors per conditional, coverage table, module likelihood columns)",
 "status": "done",
 "summary": ("Pre-registered (90d7181) and computed the IMOS-gated likelihood L_r = (1-P_D,r) + P_D,r m_r/beta_r (M1b, alpha 0.05, block 7 P_D on own backgrounds, "
             "block 2 arc-grid TL, E = contact KE, tau = tau90, cal. error N(0,10 dB)) on all 313,599,968 run J rows: five float32 columns row-aligned with impacts32 "
             "(eta 1e-3, 2.1e-4, 1e-4, eta-marginal log-uniform [1e-6,1e-2] = proposed default, IMS-proxy sensitivity) in mh370-exchange/hydroacoustics/run-j-gated (READY). "
             "Streamed statistics over all rows + northern supplement give the 95 % upper limits on eta (two ways), the evidence three ways with a non-detection-only control, "
             "Bayes factors for the Kadri 306.18 row (both times), Royer B/D1/D2, the poster boxes and the Holland-type descent, and the two-site coincidence summary. "
             "Headline: the IMOS non-detections are weakly informative (ln Z = -0.066 under D0' p 0.5; median latitude +0.10 deg; mass north of 33 S 0.058 -> 0.072; KL 0.019 nats); "
             "the 95 % posterior upper limit on eta is 4.6e-3 against 6.3e-3 for the prior alone, and classical exclusion is not reached below 1e-2 anywhere. "
             "New gap G11-1: the pre-registered match term is amplitude-blind; two Portland 3275 candidates (eta needed 19-30) drive +1.4-1.5 deg shifts under D3/D4 at p = 1 "
             "that vanish with the non-detection likelihood alone. Ruling requested; composer default lnL_gated = 0.0 unchanged. PREDICTIVE, NOT CALIBRATED; C1, C2."),
 "commits": ["90d7181 (module: pre-registration)", "dddfbd0 (module: code)", "978422d (module: results-data + tables/charts code, amendments A2/A3)",
             "cd001a2 (module: prereg amendments A2/A3 text)", "3a566a0 (work branch: results note, two charts, coordination entry with ruling request)"],
 "results_notes": ["Claude Science Project Sep 29/results/hydroacoustics-composition-run-j.md",
                   "Claude Science Project Sep 29/results/hydroacoustics-composition-run-j-evidence.{png,pdf}",
                   "Claude Science Project Sep 29/results/hydroacoustics-composition-run-j-limits.{png,pdf}"],
 "exchange_paths": ["/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated/ (6.5 GB; columns per <stratum>/seed-N, acc.npz, subsample.npz, supplement/, reduce/, README.txt, SHA256SUMS, READY)"],
 "key_numbers": ("eta 95 % upper limit (posterior quantile, log-uniform prior [1e-6,1e-2], non-detection likelihood, IMOS gated, alpha 0.05): D0' p0.5 4.6e-3 (p0 4.8e-3, p1 4.5e-3); "
                 "D2 4.3e-3, D3 3.7e-3, D4 3.3e-3 (p 0.5); per 5-deg band under D0' p0.5: 41-36 S 4.5e-3, 36-31 S 4.7e-3, 31-26 S 6.0e-3, 26-21 S 6.4e-3, 21-20 S 6.5e-3 (ESS 491); "
                 "prior alone 6.3e-3; classical 95 % exclusion not reached below 1e-2 in any option/p/band; P(no detection | eta) D0' p0.5 = 0.37 at 1e-2, 0.61 at 1e-3, 0.75 at the anchor 2.1e-4. "
                 "IMS-proxy sensitivity: 4.0e-3, P(nd | 1e-2) 0.28. "
                 "Combined with the core (D0' p0.5): median latitude 37.08 -> 36.98 S (+0.10 deg); mass north of 33 S 0.058 -> 0.072; KL 0.019 nats; ln Z_hydro -0.066; "
                 "non-detection only: +0.02 deg, 0.058 -> 0.067, KL 0.002. D3/D4 p = 1 full-likelihood shifts +1.37/+1.49 deg (KL 0.31) are G11-1 artefacts (ND-only <= 0.05 deg). "
                 "ln BF (gated IMOS, vs run J D0' p0.5): Kadri 306.18 row -0.004 at text time 00:52:03 and caption time 00:54:30 (IMS proxy +1.38 / +0.10, circular); "
                 "Royer B -0.14; Royer D1/D2 +0.07 (no information); poster (a) boxes 1-3 before 00:19:29, +0.07 (no information), box 4 -0.02; "
                 "Holland p=1 vs p=0: D0' -0.08, D2 -0.06, D3 -0.15, D4 -0.15 (ND only -0.06/-0.05/-0.35/-0.30). "
                 "Coincidence H01W 00:52:04 x H08S 01:12:49: 19 pairs vs 8.8 chance, p_perm 0.019 over 36 tests (chance-level); arc locus 33.6 S 94.5 E, implied impact 00:31:41 (run J mass within +/-1 deg 0.23); "
                 "eta for P_D(both) = 0.5 is 0.069 (330x anchor); P_D(both) at the anchor 1e-4. ESS streamed D0'/D2/D3/D4 at p 0.5: 1,334,115 / 107,236 / 5,672 / 25,411."),
 "gaps": ["G11-1 (new, matters): amplitude-blind candidate matching in the pre-registered form; fix = amplitude kernel or non-detection-only column, pre-register as an amendment",
          "G11-2: 10 of 18 free-stratum seeds (0.13 % of mixture mass) carry only the marginalised IMOS column (another process held the disk below 20 GiB); top-up recipe in README",
          "G11-3: supplement tau is a log-normal stand-in through run J tau90 quantiles (reduced file has no tau90); supplement enters statistics only",
          "G11-4: IMOS clock drift not corrected (sigma_clock 2 s allowance); G11-5: 55 s vs 60 s window mismatch (<= 0.4 dB)",
          "Carried: G-TL1/G-TL2/G-TL-X (TL), G7-2/3/5/6/7/8/9 (injection), G-S1/2/3/4/7 (searches), G-W1/W4 (windows), G23/G4/G5 (TL recalibration); IMS gate proxy-only; AGW not searchable; H08N blocked",
          "Coverage: D3/D4 bands north of 26 S and the 21-20 S band in every option not estimable better than ~2x; D3 p=1 thin (ESS 2,945); 'outside B' not estimable under D3",
          "Deviations: alpha 0.05 primary (task said screen level 0.3; 0.3 and 0.01 as sensitivities); exchange product 6.5 GB vs 6 GB figure"],
 "next": "Ruling on the composer default (IMOS-gated marginal column, IMS proxy as sensitivity) — module recommends admitting with the G11-1 label or waiting one pre-registered amendment for an amplitude-aware match; then top up the 10 short seeds when >= 22 GiB free; consume run-j-imos-ram-grid for G-TL1; carry the 33.6 S / 00:31:41 locus into the Kadri package (block 12).",
 "blocker": "none for this block; composer change waits on the architecture ruling"
}
r = host.submit_output(out,
    completion_bullets=["Pre-registered and wrote the IMOS-gated likelihood columns for all 313.6 M run J rows (5 columns, 74 seeds, READY)",
                        "Computed 95 % upper limits on coupling, evidence three ways, Bayes factors per conditional and the two-site coincidence summary",
                        "Found and declared G11-1 (amplitude-blind matching drives the D3/D4 p = 1 shifts); ruling request posted to coordination/architecture.md",
                        "Results note with COVERAGE and two footnoted charts committed; code and data on the module branch"],
    deviations=["Primary false-alarm level alpha = 0.05 (report level) instead of the task's screen level 0.3; 0.3 and 0.01 reported as sensitivities on the streamed statistics",
                "10 of 18 free-stratum seeds (0.13 % of mixture mass) carry only the marginalised IMOS column: another process held the disk below the 20 GiB floor during the run; 4 of 14 short seeds were topped up",
                "H08S matched candidates restricted to the suppressed-residual rows (none), per searches gap G-S9; the raw-panel row 01:12:49 appears only in the coincidence table",
                "Northern supplement enters the statistics with a log-normal tau stand-in (reduced file has no tau90) and native weights at every p; it has no column (no row alignment exists)",
                "Attitude sidecar enters no value (the chain's coupling has no attitude dependence)",
                "Exchange product 6.5 GB against the task's 6 GB figure; the merged 1.1 GB subsample was not written",
                "Bayes-factor draws (E, tau) come from the 1-in-125 subsample within +/-1 deg of each hypothesis latitude (20,000 resampled draws), not from all rows"])
print(r)