# Overnight work orders, 20 Oct 2026 (Pete approved items 1-4 at about 02:50Z; he is away until morning)

Coordination session ac78e73d. The shared rules of `overnight-2026-10-19.md` apply unchanged, with these values:
- Mac disk pause floor 5 GB df free (pause, never delete). Mac free was 75 GiB at 02:45Z. Total budget tonight 35 GB.
- deskstar heavy lock: `flock ~/.mh370-heavy.lock` (not FIFO; orders C and D may run in either order). deskstar free 27 GB.
- Never delete under /Users/pete. Charts: no project codes in titles/axes/legends, ASD-STE100 for work-specific items,
  two footnotes (STE100 + technical), family codes spelled out, "Holland transient bias added".
- Report counts from partial input as "not assessed at this depth". Each order ends with results note, figures (PNG + PDF),
  inbox + architecture.md entries, commit and push, READY + SHA256SUMS on the exchange.

## A. End of flight completes the northern supplement (END_OF_FLIGHT_MODULE; Mac, 12 threads, cap 30 GB)
Follows `results/eof-run-j-supplement-oct19` (f4fa6cf0).
1. Fly the other half of the supplement rows (the rows not flown at k = 2) with the same recipe, config tree a517deeb and
   binary rj1, own seeds. Combine all rows by rule B (u2 without the x2 factor once both halves are in).
2. Extra descents for D2-D5 on the new half north of 35.5 S, as last night, inside the cap.
3. Second A1 conditional pass: A1 cases outside the branch (other onsets / log-on from another cause), as costed in the
   19 Oct note (about 1.6 h, 3.5 GB); stratified estimator as for the branch pass.
4. Report band ESS (rows / parents / distinct states) per treatment vs 1,000, before and after; the A1 cells; update
   `reduced/impacts-ruleB.npz` for the full set (keep last night's file as `-k2`).

## B. Supplement through the downstream modules (starts when A is READY; coordination dispatches it)
B1 settling (seabed samples on the full rule-B set; cap 3 GB) -> B3 searched areas (impact, settled, per-cell V0-V3; cap 2 GB)
-> C composer v3.2 (supplement in; northern ESS and masses with seed bootstrap; compare v3.1; cap 3 GB). B2 Pléiades under H
runs in parallel with B1 (cap 3 GB). Same rules and recipes as on 19 Oct.

## C. Drift arc-latitude run extended north (OCEAN_DRIFT_MODULE; deskstar, heavy lock, cap 8 GB deskstar)
Follows `results/drift-runj-2026-10-17/arc-latitude-scan/` (15ab7c9; recipe, configs, release points, run_arclat.sh).
1. Add release points at 25, 24, 23, 22, 21 and 20 S on the run J impact track and 50 NM either side, north tier (3e5
   particles), both ocean models, identical settings otherwise. Extend the release-node grid if it stops at 25.5 S; state it.
2. Check that the 26 S points reproduce the existing values within Monte Carlo noise (overlap check).
3. Publish the merged likelihood profile (20-40 S) and node tables; redo panel a/b of the dedicated-run figure for 20-40 S.
4. State the detection settings exactly as before (finds only base; options B, C, populated coast as labelled settings).

## D. Calibration smoke cases 5 and 1 at 3.5M (resumes the order E sub-agent; deskstar, heavy lock, cap 8 GB)
Follows `results/e2e-calibration-smoke-2026-10-19/` (d7c73576).
1. Re-run case 5 at 4 x 3.5M. Report its rank, HPD coverage and posterior weight on its true log-on cause; say whether the
   miss is sample size or model (fault F5).
2. Re-run case 1 at 4 x 3.5M with the corrected 00:19 BFO-model draw (the script bug), all 00:19 options.
3. Do not start the full run; amendments A1-A5 stay proposed.
