# Northern supplement to core run J — reports and graphics (order D, 19 Oct 2026)

Status: DONE. These files are the reports for the 16-run northern supplement (seeds 1001–1016, early-flight
family 'waypoints', engine revision 3bf0801, deskstar job b6389957). They do not change run J or its convergence
ruling (PASS, Pete 16 Oct 2026). The Davey et al. (2016) reference is the Fig. 10.3 curve recovered from the PDF
vector paths (`engine/.sources/davey-2016/fig10-3-bto-bfo-latitude-pdf-vector.csv`, from commit 5315fde).

## Files

| File | What it shows |
|---|---|
| `run-j-supplement-0011-report.pdf` | 00:11 supplement report, 7 pages: summary page, Figures 1–3 and Tables 1–3 (the same pages are also given as separate PDF and PNG files) |
| `page0-summary.*` | Summary: purpose, method, results and limits, in short sentences |
| `fig1-latitude-0011.*` | Probability by latitude band at 00:11: run J alone, supplement alone and combined (rule B weights), with 5–95 % seed-bootstrap bands |
| `fig2-distinct-states.*` | Distinct 00:11 states and effective distinct states per latitude band, before and after the supplement |
| `fig3-evidence-noise.*` | Seed standard deviation of ln Z per autopilot mode: measured supplement/run J ratio with 95 % CI against the predicted square-root ratio |
| `table1-prior-recovery.*` | Prior recovery after the northern tilt is removed (all \|z\| < 1.6) |
| `table2-correction-checks.*` | Weight-sum and rule B / rule C checks, with the paired z for P(north of 30 S) |
| `table3-parameters.*` | Run parameters: particles per mode, seeds, revision, runtime, data options |
| `report-numbers.json` | All the numbers in the figures and tables, in machine-readable form |
| `run-j-supplement-north-report.pdf` | Standard run report (`report/build_report.py`, 8 pages) for the 16 supplement runs pooled; PNG pages are in `standard-report-png/` in the exchange copy only (the project .gitignore excludes `*-png/`) |
| `run-j-supplement-north-report-convergence.json` | Split-half overlap: all 6,435 balanced partitions 0.883 (range 0.779–0.963); random 8-run subsets 0.837 (5–95 % 0.805–0.884) |
| `supplement-merged-summary.json` | `mh370 summarise` output for the 16 pooled runs (vector Davey curve) |

Main values. 00:11 band mass (supplement only / combined, 5–95 % seed bootstrap): 35–30 S 0.241 [0.217–0.267] /
0.237 [0.217–0.256]; 30–25 S 0.0184 [0.0165–0.0204] / 0.0194 [0.0164–0.0219]; 25–20 S 0.0023 / 0.0026. The northern
interval does not become narrower in the combined result, because it rests on the 16 supplement runs alone. 00:19
(supplement pooled): median 37.11 S, mode 37.15 S, 95 % 38.02–33.25 S, P(34.5–36.5 S) = 0.140. Davey vector curve:
median 37.43 S, mode 37.75 S, 95 % 39.21–34.82 S, P(34.5–36.5 S) = 0.271.

## Convergence

No convergence ruling is made for the 16 supplement runs: there is no calibrated split-half floor for 16 runs
(floors exist for 4, 6 and 8 runs). The report says "NOT judged". The run J ruling is not affected.

## How these were made

- Standard report: deskstar job 58769f9b (final), script `engine/scripts/job-supplement-report.sh` at revision
  e5804474. It merges the 16 seed directories of job b6389957 read-only (a merged run.json and symbolic links;
  `report/merge_seed_runs.py`), runs `mh370 summarise` from `bin-3bf0801` with the current engine tree, then
  `report/build_report.py`. Earlier builds: e109832e (failed: scipy not installed in the job venv), 5b36e43a,
  68dd3bcd and 0914b976 (layout fixes). Their job folders on deskstar are small and are kept.
- 00:11 supplement report: built on the Mac from the staged files in `mh370-exchange/core/run-j-supplement/`
  (`report/build_supplement_report.py` assembles the pages). The figure and table code is in the session artifact
  lineage; it is not committed as a separate script.

## Deviations from work order D

1. Heavy lock. The work order gives `lockf -k /tmp/.mh370-heavy.lock`. Deskstar has no `lockf`, and
   `/tmp/.mh370-heavy.lock` does not exist there. All deskstar heavy jobs (core runs, drift chain) use
   `flock` on `~/.mh370-heavy.lock`, so the report job used that lock (`flock -w 36000`). The job had no background
   monitor, and the venv/pip steps ran with fd 9 closed (`9>&-`), so the lock leak of 18 Oct cannot occur again.
2. No run J overlay in the standard report: the run J final particle files are not on deskstar. Run J values are
   quoted in the tables of the 00:11 report.
3. Layout changes to shared report code (all generic): Davey label and caption (c3bb9212), map titles use
   `REPORT_RUN_LABEL` and a `REPORT_REPRODUCE` override (67964d87), parameter-page row pitch (098dbf9c), page 1
   caption position (e5804474).
4. The deskstar job folder b6389957 (about 35 GB) is NOT deleted. Pete decides.
