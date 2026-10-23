out = {
 "block": "11 — composition (two-site coincidence, 95 % upper limits on coupling, Bayes factors per conditional, coverage table, module likelihood columns); amendment A4 follow-up (corrected IMOS TL, statistics only)",
 "status": "partial",
 "summary": ("Original block 11 (prereg 90d7181): IMOS-gated likelihood columns for all 313.6 M run J rows written to run-j-gated (READY), with streamed statistics, upper limits, "
             "evidence three ways, Bayes factors and the coincidence summary. A4 follow-up (prereg e13a32e, committed before the re-run): the IMOS TL was switched to the "
             "RAM-along-grid drop-in imos_tl_ram_arc.csv (offset-0 line, uncovered rows keep the old value inside the file) and ONLY the statistics were re-run on all rows + "
             "supplement (100 min at 4 processes), with an amplitude-consistency-weighted match (sigma 10 dB, down-weighting only) added as the labelled G11-1 sensitivity. "
             "The per-row EXCHANGE COLUMNS in run-j-gated were NOT rewritten (disk) and are ON THE OLD IMOS TABLE: README warning + rewrite recipe added, READY kept; they must "
             "be rewritten before any composer use (new gap G11-6). Corrected headline (D0' p 0.5): ln Z −0.037 (was −0.066); median latitude +0.06° (was +0.10°); mass north of "
             "33 S 0.058 → 0.064 (was 0.072); KL 0.011 nats; 95 % upper limit on eta from the non-detection 5.2e-3 (was 4.6e-3; prior alone 6.3e-3); P(no detection | eta) 0.48 / 0.72 / 0.85 "
             "at 1e-2 / 1e-3 / anchor (were 0.37 / 0.61 / 0.75); classical exclusion still not reached below 1e-2. D3/D4 p = 1 shifts fall from +1.4–1.5° to +0.3° (amplitude-weighted +0.13°, "
             "non-detection only −0.02 to −0.03°). Status 'partial' because the exchange columns await the rewrite. PREDICTIVE, NOT CALIBRATED; C1, C2; no detection claimed."),
 "commits": ["90d7181 (module: pre-registration)", "dddfbd0 (module: code)", "978422d (module: results-data + tables/charts code, A2/A3)", "cd001a2 (module: A2/A3 text)",
             "3a566a0 (work branch: note, charts, coordination entry)", "e13a32e (module: PRE-REGISTERED amendment A4)",
             "8093d97 (module: A4 code + results-data/composition_run_j/ramgrid)", "e79bba2 (work branch: note addendum A4 + coordination entry)"],
 "results_notes": ["Claude Science Project Sep 29/results/hydroacoustics-composition-run-j.md (with Addendum A4: old vs new tables A1–A6)",
                   "Claude Science Project Sep 29/results/hydroacoustics-composition-run-j-evidence.{png,pdf} (OLD table; not re-rendered)",
                   "Claude Science Project Sep 29/results/hydroacoustics-composition-run-j-limits.{png,pdf} (OLD table; not re-rendered)"],
 "exchange_paths": ["/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated/ (6.5 GB; per-row columns ON THE OLD IMOS TABLE — README warning; READY kept)",
                    "/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated/stats-ramgrid/ (1.2 GB; corrected-table statistics: per-seed acc.npz + subsample.npz, reduce/, DONE)"],
 "key_numbers": ("CORRECTED (imos_tl_ram_arc.csv), alpha 0.05, eta marginal log-uniform [1e-6,1e-2], IMOS gated. eta 95 % upper limit from the non-detection (posterior quantile): D0' p0.5 5.2e-3 "
                 "(p0 5.3e-3, p1 5.0e-3); D2 5.0e-3, D3 4.6e-3, D4 4.2e-3 (p 0.5); per 5-deg band under D0' p0.5: 41-36 S 5.2e-3, 36-31 S 4.8e-3, 31-26 S 5.7e-3, 26-21 S 6.3e-3, 21-20 S 6.6e-3 (ESS 491); "
                 "prior alone 6.3e-3; classical exclusion not reached below 1e-2 anywhere; P(no detection | eta) D0' p0.5 = 0.48 at 1e-2, 0.72 at 1e-3, 0.85 at the anchor. "
                 "Evidence (D0' p0.5): ln Z −0.037; median latitude 37.10 → 37.04 S (+0.06°); mass north of 33 S 0.058 → 0.064; KL 0.011 nats; amplitude-weighted variant −0.084 / +0.04° / 0.006; "
                 "non-detection only −0.185 / −0.03° / 0.001. D3/D4 p = 1: shift +0.29 / +0.34° (was +1.37 / +1.49), KL 0.23 / 0.22. "
                 "ln BF (gated IMOS vs run J D0' p0.5): Kadri 306.18 row −0.034 at text time 00:52:03 and caption time 00:54:30 (IMS proxy +1.35 / +0.08, circular); Royer B −0.18; "
                 "Royer D1/D2 and poster boxes 1–3 +0.04 (no information); box 4 −0.12; Holland p=1 vs p=0: D0' −0.04, D2 −0.03, D3 −0.01, D4 −0.03 (ND only −0.04 / −0.03 / −0.20 / −0.17). "
                 "Coincidence H01W 00:52:04 x H08S 01:12:49 unchanged: 19 pairs vs 8.8, p_perm 0.019 over 36 tests; arc locus 33.6 S 94.5 E, implied impact 00:31:41; eta for P_D(both)=0.5 0.069 (330x anchor). "
                 "OLD-table values for comparison: limit 4.6e-3; ln Z −0.066; shift +0.10°; P(nd | 1e-2) 0.37. ESS unchanged (D0'/D2/D3/D4 p 0.5: 1,334,115 / 107,236 / 5,672 / 25,411)."),
 "gaps": ["G11-6 (new): exchange columns in run-j-gated are on the OLD IMOS TL table; must be rewritten (B11_IMOS_RAMGRID=1 python driver.py, >= 28 GiB free) before composer use",
          "G11-1: amplitude-blind matching — narrowed by the amplitude-consistency-weighted sensitivity (down-weighting only), not closed; a calibrated amplitude likelihood ratio needs the background level density of screen-level candidates",
          "G11-2: 10 of 18 free-stratum seeds (0.13 % of mass) carry only the marginalised IMOS column (disk floor during the first run)",
          "G11-3: supplement tau is a log-normal stand-in; G11-4: IMOS clock drift not corrected (2 s allowance); G11-5: 55 s vs 60 s window mismatch (<= 0.4 dB)",
          "Carried: G-TL1a/b (±30 NM paths, 5/8 Hz bands interpolated), G-TL2, G-TL-X; G7-2/3/5/6/7/8/9; G-S1/2/3/4/7; G-W1/W4; G23/G4/G5; IMS gate proxy-only; AGW not searchable; H08N blocked",
          "Coverage: D3/D4 bands north of 26 S and the 21-20 S band not estimable better than ~2x; D3 p=1 thin (ESS 2,945); 'outside B' not estimable under D3",
          "Charts not re-rendered on the corrected table (they carry the old-table footnote); the addendum tables are the corrected record"],
 "next": "Column rewrite on imos_tl_ram_arc.csv when >= 28 GiB are free (one driver run, ~6.3 GB), then re-render the two charts; architecture ruling on the composer default (recommend: after the rewrite, admit hydro-lnL-imos-margeta with the G11-1 label, or the amplitude-weighted variant as a conservative default; IMS proxy as sensitivity); RAM at 5/8 Hz on the offset-0 paths (G-TL1b).",
 "blocker": "disk for the column rewrite (needs >= 28 GiB free; ~13–30 GiB available and fluctuating); the architecture ruling"
}
r = host.submit_output(out,
    completion_bullets=["Pre-registered amendment A4 and re-ran the block 11 statistics on all 313.6 M rows with the corrected RAM-grid IMOS TL table (no columns rewritten)",
                        "Added the amplitude-consistency-weighted match as the labelled G11-1 sensitivity alongside the non-detection-only control",
                        "Appended the old-vs-new addendum (tables A1–A6) to the results note; flagged the exchange columns as OLD-table in README (READY kept)",
                        "Posted the coordination entry with the updated ruling request"],
    deviations=["Per-row exchange columns NOT rewritten (disk ~13 GiB when asked; rewrite needs >= 28 GiB): they remain on the old IMOS TL table and are labelled so; statistics only were re-run",
                "Charts not re-rendered on the corrected table; the addendum tables carry the corrected numbers",
                "Amplitude-aware match implemented as a down-weighting kernel (sigma 10 dB) without dividing out a background level density — a labelled sensitivity, not a calibrated likelihood ratio; IMS receivers stay amplitude-blind (digitised panels have no comparable band energy)",
                "Primary false-alarm level alpha = 0.05 (report level) rather than the task's screen level 0.3; 0.3 and 0.01 as sensitivities",
                "10 of 18 free-stratum seeds (0.13 % of mixture mass) carry only the marginalised IMOS column (first run, disk floor)",
                "Northern supplement enters the statistics with a log-normal tau stand-in and native weights at every p; no column for it",
                "Bayes-factor draws (E, tau) from the 1-in-125 subsample within +/-1 deg of each hypothesis latitude (20,000 resampled draws)",
                "Per-logger level changes quoted in the addendum (3315 −6.4 dB etc.) rest on a 20,000-row sample of one seed"])
print(r["status"], r.get("message", "")[:120])