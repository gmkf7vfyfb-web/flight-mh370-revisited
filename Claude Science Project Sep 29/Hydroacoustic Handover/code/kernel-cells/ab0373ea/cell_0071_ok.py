out = {
 "block": "G-TL1 closure: RAM (coupled modes) along the arc grid at the five IMOS loggers (work order 2026-10-21, overnight 21/22 Oct 2026)",
 "status": "partial",
 "summary": ("RAM (pyram, settings of the 8-path subset, each logger on its own bathymetry, 10 m source) at 10/20/40 Hz on 212 of 253 planned paths: "
             "ALL 85 open offset-0 paths complete (the line every current consumer uses), 66/86 at -30 NM, 61/82 at +30 NM (41 paths incomplete at the 03:35 soft deadline; mask issued). "
             "Acceptance check exact (<0.001 dB on 6 pairs vs the subset). Drop-in imos_tl_ram_arc.csv (same schema + coverage/mode flags), RAM-KRAKEN delta table and coverage mask written beside the old files; "
             "old files untouched. Levels rerun (D0' p0.5, five loggers): the Perth Canyon 40:1 artefact is gone (3315 MF share at the anchor 13.6 -> 0.5 %, 3376 0.2 -> 1.9 %; at eta 1e-3 29.9 -> 9.8 % and 15.4 -> 17.2 %); "
             "3275 11.3 -> 0.8 % / 25.4 -> 16.6 %; 3274 and 3250 stay 0; power-screen verdicts unchanged. IMOS numbers of the levels note and of block 11 (composition) are superseded once reloaded. "
             "PREDICTIVE, NOT CALIBRATED; C1/C2 on every number; no likelihood written."),
 "commits": ["4920cc2 (hypothesis/hydroacoustics: pre-registration imos_ram_grid.py + run_j_levels amendment 2 + tl_grid_table imos_file)",
             "cc943df (hypothesis/hydroacoustics: run/build code, chart script, results-data tables, levels rerun tables)",
             "880ae5f (claude-science-sep29: results/hydroacoustics-imos-ram-grid.md, old-vs-new chart PNG+PDF, coordination/architecture.md entry)"],
 "results_notes": ["Claude Science Project Sep 29/results/hydroacoustics-imos-ram-grid.md",
                   "Claude Science Project Sep 29/results/hydroacoustics-imos-ram-grid-old-vs-new.png (+ .pdf)"],
 "exchange_paths": ["/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables/imos_tl_ram_arc.csv",
                    "/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables/imos_ram_minus_kraken_arc.csv",
                    "/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables/imos_tl_ram_coverage.csv",
                    "/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid/ (raw rows, per-path environments, levels-rerun/, levels-rerun-sens-lowband-old/, logs, SHA256SUMS; 551 MB)"],
 "key_numbers": ("Coverage: offset 0 100 % of open paths (85/85), -30 NM 66/86, +30 NM 61/82; 647 path x band jobs, 0 failed, ~23 CPU-h, 6 processes. "
                 "RAM - KRAKEN_noabs (dB; offset 0; 10/20/40 Hz; q10/median/q90): 3315 -18/-12/-9, -35/-24/-13, -82/-60/-29; 3376 -16/-13/-5, -42/-30/-17, -81/-70/-53; "
                 "3274 -26/-19/-11, -59/-54/-44, -135/-133/-123; 3275 -26/-19/-11, -58/-55/-46, -126/-117/-113; 3250 -6/-3/-1, -39/-31/-16, -129/-117/-89. "
                 "Detectable share (D0' p0.5, matched filter 7 dB / baseline 15 dB), old -> new: 3315 at eta 2.1e-4 13.6/0.0 -> 0.5/0.0 %, at 1e-3 29.9/12.4 -> 9.8/0.3 %; "
                 "3376 at 2.1e-4 0.2/0.0 -> 1.9/0.0 %, at 1e-3 15.4/0.0 -> 17.2/0.8 %; 3275 11.3/0.0 -> 0.8/0.0 % and 25.4/2.2 -> 16.6/0.1 %; 3274 0 -> 0; 3250 0 -> 0. "
                 "eta_50 MF: 3315 4.0e-3 -> 1.4e-2, 3376 1.3e-2 -> 1.0e-2, 3275 6.0e-3 -> 1.2e-2. Median SNR at the anchor: 3315 -5.8 -> -11.2 dB, 3376 -10.9 -> -9.9, 3275 -7.5 -> -10.6. "
                 "Low-band sensitivity (old 5-8 Hz rows kept): 3315 at 1e-3 9.8 -> 2.8 %, 3376 17.2 -> 12.7 %, 3275 16.6 -> 15.5 %."),
 "gaps": ["G-TL1a: 41 of 168 +-30 NM paths incomplete (deadline); rows keep the old rule-2 value with ram_grid_covered=False",
          "G-TL1b: RAM not run at 5-8 Hz (rows take the clamped 10 Hz delta); the largest residual - 3315 share at eta 1e-3 between 2.8 and 9.8 % depending on the low-band treatment",
          "G-TL1c: 31.5 Hz, 2 m and 30 m sources not run (log-f interpolation and the 10 m delta stand in)",
          "G-TL1d: 0.5-degree rows rest on delta interpolated between 1.0-degree nodes; amendment-1 donor rule (10 % of covered rows) is a heuristic; 12 rows at -30 NM / 28.5 S flagged below_physical_floor",
          "G-TL2 (3376 terminal profile), G-TL-X (offset unused by the levels consumer), G-N2/K5 (ridge-source coupling) unchanged",
          "Consumers (levels note IMOS rows, block 11 IMOS component, Kadri package predictions.csv) still carry the old table until reloaded"],
 "next": "RAM at 5 and 8 Hz on the 85 offset-0 paths plus the 41 incomplete +-30 NM paths (~6 CPU-h); consumers reload with imos_file='imos_tl_ram_arc.csv' and re-issue the IMOS rows / block-11 IMOS component; then the 0.5-degree nodes and G-TL2 with RAM.",
 "blocker": "none for this block; the consumers' reload is theirs to run"
}
r = host.submit_output(out,
    completion_bullets=["Pre-registered and ran RAM along the arc at the five IMOS loggers: offset-0 line complete, +-30 NM 76 %; acceptance check exact",
                        "Issued drop-in imos_tl_ram_arc.csv, RAM-KRAKEN delta table and coverage mask beside the old files; committed code and data (cc943df)",
                        "Re-ran the levels for the five loggers: Perth Canyon 40:1 artefact gone (0.5 % vs 1.9 % at the anchor); IMOS numbers of levels note and block 11 superseded",
                        "Wrote results note + comparison chart (880ae5f) and the coordination entry"],
    deviations=["Coverage: 212 of 253 planned paths complete (41 at +-30 NM not reached at a 03:35 soft deadline instead of 03:50); offset 0 complete",
                "31.5 Hz band not run (timing rule); 5-8 Hz bands take the clamped 10 Hz delta; 2 m / 30 m sources take the 10 m delta",
                "Amendment 1 after an interim build: donor-node rule where neighbouring node deltas differ by > 20 dB (600 rows, 10 % of covered), disclosed in the note",
                "Process count 6 (load 5.9 at launch; 80.6 at the first check); a 40-minute duplicate-run incident (12 processes, byte-identical rows dropped)",
                "Disk fell below the operating note's 20 GiB floor (min 11.9 GiB, Time Machine snapshots); the parent's 9 GiB floor was never reached; our writes 551 MB",
                "Low-band sensitivity run added after the result (labelled, not pre-registered)"])
print(r)