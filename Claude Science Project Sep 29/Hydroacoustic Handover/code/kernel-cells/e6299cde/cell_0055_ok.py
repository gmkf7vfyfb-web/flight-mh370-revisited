out = {
 "block": "4 (pre-registration) and 5 (searches on data held), run J",
 "status": "done",
 "summary": ("Pre-registration committed at a4cdab0 before any statistic (windows = union over D0'/D2/D3/D4 x p in {0,0.5,1} of the 99 % arrival windows, SOFAR/AGW separately; bands 2-5/5-10/10-20/20-40/5-40 Hz; detectors M1b envelope matched filter, D1 STA/LTA, band energy, H08S suppressed residual; thresholds 0.3/0.1/0.05; backgrounds = same logger other days (6,541-6,720 null windows), emulated-plot null A + block-permutation surrogates null B for the digitised panels; two-site lag rule; candidate format with eta_needed label). "
            "Searches run on IMOS 3315/3376/3274/3275/3250 (8 Mar records in window), digitised Kadri panels a-e (H08S with c1+c2 suppression), Kadri Table 1 at both times, six poster boxes, Royer B/D1/D2, infrasound row; two-site coincidence over 18 pairs. "
            "786 windows scored: 184/60/29 rows at screen/mark/report vs 236/79/39 expected by chance; per receiver one third (Perth Canyon, H01W) to 1.5x (Scott Reef, Portland 3275) the chance rate. No detection; likelihood stays 0.0 (PREDICTIVE, NOT CALIBRATED; C1, C2; H01W/H08S digitised; both Kadri times carried). "
            "Strongest single row: H01W 00:52:04 matched filter p 0.043 (report; text-time box; caption time p 0.123), needing eta ~0.026 for the median impact (100x the F-35A anchor). H08S after suppression: Z_res 01:07:52 p_B 0.094 (mark). Strongest two-site pair: H01W 00:52:04 x H08S 01:12:49 (max p 0.043, lag 1,245 s in [809,1536] s; H08S row typical of its own airgun panel, p_B 0.30); H01W x Perth Canyon 3376 00:52:11 lag-consistent at p 0.167 but needs eta 1.6. 36 pair tests give 2-3 values at p ~0.02-0.03 by chance. "
            "Kadri Table 1 on run J: 5 favoured / 10 uninformative / 5 disfavoured in bearing; the three favoured rows before 00:42 imply impacts at 00:15-00:16 (before 00:19:29); two rows fit both time and bearing (00:49:58 at 260.4 deg, 00:53:31 at 257.6 deg); the 306.18 deg row is UNINFORMATIVE (log10 BF -0.49 at both times), not DISFAVOURED as on the stand-in (northern supplement). Poster (a) boxes 1-3 end 7.2/5.0/2.9 min before the earliest arc arrival (00:36:51; closest approach 1,563 km at 28.0 S): 'source before 00:19:29 or off the arc'; box 4 marginal. Royer B 493 km off the arc with zero D0' mass within 100 km; D1/D2 outside the 99 % impact-time band of every option and 667/502 km off the arc. Infrasound: declared no-information row."),
 "commits": ["a4cdab0 (hypothesis/hydroacoustics) BLOCK 4 pre-registration + geometry sample",
             "7561cc5 (hypothesis/hydroacoustics) BLOCK 5 searches code + tables (prepare/searches_run_j, results-data/searches_run_j)",
             "214f890 (claude-science-sep29) results note, two charts, coordination/architecture.md entry"],
 "results_notes": ["Claude Science Project Sep 29/results/hydroacoustics-searches-run-j.md",
                   "Claude Science Project Sep 29/results/hydroacoustics-searches-run-j-timeline.{png,pdf}",
                   "Claude Science Project Sep 29/results/hydroacoustics-searches-run-j-table1.{png,pdf}"],
 "exchange_paths": ["/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches/ (geometry/, null/, imos/, panels/, named/, coincidence/, counts_vs_chance_*.csv, SHA256SUMS; 293 MB)"],
 "key_numbers": ("Rows screen/mark/report observed vs chance: total 184/60/29 vs 236/79/39. Per receiver (screen obs/exp; report obs/exp): H01W 4/36; 1/6. H08S 47/36; 1/6 (airgun; residual rows 3 screen, 1 mark). 3315 10/31.5; 0/5.3. 3376 6/27.3; 0/4.6. 3274 26/31.5; 5/5.3. 3275 28/31.5; 10/5.3. 3250 63/42; 12/7 (blocked path, no-information row). "
                 "Strongest two-site coincidence: H01W 00:52:04 (M1b p 0.043, text time) x H08S 01:12:49 (M1b p 0.039, p_B 0.30), lag 1,245 s; pair count 19 vs 8.8 expected, p_perm 0.019 (held-span permutation; amendment A1). Table 1: 306.18 deg log10 BF -0.49 (uninformative) at both times; two rows time-and-bearing consistent (00:49:58, 00:53:31). eta_needed H01W text-time row 0.026; Perth Canyon 3376 lag partner 1.6."),
 "gaps": ["G-S1 AGW branch not searchable with the data held (all detectors >= 2 Hz; Kadri's chain removes it)",
          "G-S2 H01W/H08S are digitised plots only (envelope resolution, nothing above ~7 Hz); raw-data request to Kadri stands",
          "G-S3 no bearing on any IMOS logger",
          "G-S4 3315 and 3275 nulls are stand-ins from the paired logger (3376, 3274)",
          "G-S5 eta_needed uses TL grid pass A at one source latitude per receiver and the D0' median total kinetic energy (upper anchor); interim until the TL grid note lands",
          "G-S6 pre-registered time-slide null is schedule-biased on duty-cycled data; replaced by a held-span permutation null (amendment A1, disclosed; both reported)",
          "G-S7 geometry sample = waypoints seeds 1-8 every 6th row + supplement every 4th row; other strata (0.2 % of mixture) omitted; supplement at p = 0.5 only; D3 ESS 403 (thin)",
          "G-S8 IMOS 2-5 Hz band below the 8 Hz hardware corner (labelled)",
          "G-S9 H08S raw-panel rows are airgun null-mismatch artefacts; only residual rows are candidates",
          "make scope H=hydroacoustics not run in the sparse clone (engine Makefile not checked out); commits touch only engine/hypotheses/hydroacoustics/, results/ and coordination/"],
 "next": "Block 11 composition (candidate rows as labels; 95 % upper limits need the block-7 P_D gate); re-run eta_needed when the TL grid note lands; carry the two time-and-bearing-consistent Table 1 rows and the 306 deg re-verdict into the Kadri package (block 12); add Royer timing offsets to the prior-work critique.",
 "blocker": "none for blocks 4-5; block 11 waits on block 7 (P_D)."
}
r = host.submit_output(out,
    completion_bullets=["Pre-registered all block-5 searches (a4cdab0) before computing any statistic",
                        "Ran the searches on 5 IMOS loggers, 5 digitised Kadri panels, Table 1, poster boxes, Royer events and infrasound; 786 windows, rows at chance rate, no detection",
                        "Tested 18 two-site pairs with a schedule-aware permutation null; strongest pair H01W 00:52:04 x H08S 01:12:49 at max p 0.043",
                        "Committed code/tables (7561cc5), note + charts + coordination entry (214f890)"],
    deviations=["Coincidence significance: the pre-registered time-slide null was kept but a held-span permutation null was added after the first run and sets p (amendment A1, disclosed in the note and code)",
                "Geometry sample for lags/bearings/energy: waypoints seeds 1-8 every 6th row + northern supplement every 4th row, not all 74 seeds (0.2 % of the mixture omitted; D3 ESS 403)",
                "eta_needed uses the interim block-2 TL grid pass A (one source latitude per receiver, src depth 10 m) rather than a per-impact TL; Scott Reef labelled blocked",
                "3315 and 3275 backgrounds are stand-ins from 3376 and 3274 (no bucket data), as pre-registered and declared",
                "make scope H=hydroacoustics was not executed (sparse clone without the engine Makefile)"])
print(r)