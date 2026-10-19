# Overnight work orders, 19 Oct 2026 (Pete approved; architecture / coordination session ac78e73d)

Pete, 19 Oct about 03:45Z: candidates 1-4 approved to run tonight after he freed Mac disk (df free 75 GiB at 03:50Z).
Item 5 (end-to-end calibration) is NOT approved yet and does not run.

## Shared rules (all four orders)

- Work only in `Claude Science Project Sep 29/` on branch `claude-science-sep29`; the Sep 28 ISO tree is frozen.
- Never delete anything under `/Users/pete`. Move superseded outputs aside; Pete removes them.
- **Mac disk:** total budget tonight 48 GB across all orders. Per-order caps are below. Every writer checks `df` free on
  `/System/Volumes/Data` before each large write and **pauses (does not delete) if free < 5 GB** (Pete, 19 Oct about 04:15Z: floor lowered from 25 GiB to 5 GB), then reports.
- **Mac CPU:** order A may use 12 threads; orders B, C, D at most 4 threads each.
- **deskstar:** only order D uses it, under the heavy lock (`lockf -k /tmp/.mh370-heavy.lock`); note the 18 Oct fd-9 leak fix
  (25fe59a8) for background monitors.
- Davey Fig. 10.3 reference: the vector-recovered curve
  (`engine/.sources/davey-2016/fig10-3-bto-bfo-latitude-pdf-vector.csv`, 5315fde), labelled "Davey et al. (2016), Fig. 10.3".
- Charts: titles, axes and legends with no project codes; work-specific items in ASD-STE100; standard statistical terms as-is;
  every chart has two footnotes (STE100 and technical) stating source posterior, prior track, 00:19 data option, provisional
  physics, search case, ocean models, exclusions. Family codes are spelled out: A1 = cruise to fuel exhaustion then no
  control; A2 = cruise to fuel exhaustion then controlled descent; B = planned descent with ditching approach begun before
  fuel exhaustion. Say "Holland transient bias added", never "correction".
- Report every count from partial or thinned input as "not assessed at this depth", not as an absence.
- Each order ends with: results note under `results/`, figures (PNG + PDF), an entry in its module inbox and in
  `coordination/architecture.md`, commit and push, and a READY file plus SHA256SUMS on the exchange folder.

## A. End of flight flies the run J northern supplement (END_OF_FLIGHT_MODULE)

Inputs: `mh370-exchange/core/run-j-supplement/` (README.md §5 has the exact combination rules; DESIGN.md has predictions
P5; `r_hat.csv`). Rows: `north/seed-1001..1016/handoff-m0011-supplement`. Repo note: `results/run-j-supplement/README.md`.

1. Fly the production recipe exactly as run J waypoints (`results/eof-run-j-waypoints-oct16`, binary `mh370-eof-rj1`, sha256
   19031f41748ecb0c, round-3 laws, the same children and scored selection). Standalone weights w x exp(log_correction).
2. Disk cap 40 GB (19 Oct 04:15Z; was 35, then 30 at the 25 GiB floor). Fly all rows if the projected size fits; otherwise a fixed every-k-th-row subset (k declared; rule B
   multiplies u2 by k). Measure the rate on one seed before committing to k.
3. Combine with run J production by rule B (`r_hat.csv`, r = 0.1 outside its range). Report per 00:11 and impact latitude band
   (35-30, 30-25, 25-20 S) and per treatment D0', D1-D5: ESS as rows / parents / distinct states against 1,000; test P5
   prediction by prediction; D0' band masses under rule B against production alone; northern mass with a seed-bootstrap
   interval over both techniques; latitude PDF (production alone vs combined, with Davey Fig. 10.3).
4. Where D3 or D4 is short of 1,000 in a band, fly more descents per supplement parent (exact; linear in descents) within the
   disk cap, and state the remaining shortfall.
5. Optional, if time and disk remain: fly the 16 new 22:41 hand-offs (`north/seed-*/handoff-m2241`) to raise the parent count
   for planned descent before 00:11 under D2/D4 (backlog item 2, 18 Oct 04:00Z); report whether it becomes estimable.
6. Output: `mh370-exchange/end-of-flight/run-j-supplement/`, plus a reduced impact table for downstream modules.

## B. Downstream modules score the A1-branch conditional pass

Input: `mh370-exchange/end-of-flight/run-j-a1branch/` and `results/eof-a1-branch-oct18/README.md` (stratified estimator,
P_D0'(branch) = 0.0935). Purpose: close the D3 x A1 ESS gap (402-409 against the 500 gate) flagged by searched areas
(impact and settled) and Pléiades.

- **B1 settling (OCEAN_SETTLING_MODULE):** seabed samples for the A1-branch rows by the run J settling recipe
  (`results/settling-run-j`). Cap 4 GB. Output `mh370-exchange/settling/run-j-a1branch/`.
- **B2 Pléiades (PLEIADES_MODULE):** columns under H for the A1-branch rows by the run J recipe (`results/pleiades/run-j`).
  Cap 2 GB. Runs in parallel with B1.
- **B3 searched areas (SEARCHED_AREAS_MODULE), after B1 is READY:** impact and settled scoring with the OI base, plus the
  per-cell field (`results/searched-areas-spatial-detection`, V0-V3). Cap 2 GB.
- Each reports D3 x A1 (and D4/D5 x A1) by the stratified estimator against production, and states whether the gate is met.

## C. Composer pass v3 on run J (composer brief, `threads/master-prompts/composer.md`)

Inputs (all committed): searched areas per-cell field on settled positions (237090ab; V1 central as base, V0/V2/V3 as labelled
variants); settling run J (75fcad7b); drift dedicated arc-latitude run (15ab7c9, option B primary as pre-registered, C and
populated-coast as labelled settings, both ocean models); Pléiades run J columns (conditional, reported as P(H|D) and both
ways); hydroacoustics zero weight by ruling; Australian non-recovery as labelled sensitivity. Next OI area: map layer only.
Cap 5 GB.

1. Views per 00:19 treatment and waypoints vs free flight, on settled seabed positions after the searches, Pete's grey
   50/90/99 % band style with arcs, no text over graphics.
2. Sensitivity: ρ(y) field scale 0x, 1x, 5x, 10x; q level V1-V3; OI coverage fractions as a labelled sensitivity row only.
3. Report median latitude, 50/90/95 % HPD areas, mass north of 33 S with ESS, mass on searched ground, influence (KL) by
   factor, all with seed-bootstrap intervals; compare with views v2.
4. When B3 is READY, add the A1-branch stratum for D3 x A1; until then mark that cell below the gate.
5. Do not use the supplement yet (order A lands it); state that the north is still the production sample.

## D. Supplement reports (core; resumes the core sub-agent that ran the supplement)

1. 00:11-level report from the staged files (Mac): 00:11 latitude distribution run J alone vs combined (rule B); effective
   distinct states by band and by mode; ln Z by mode and seed vs run J and the noise-vs-particles test; prior recovery table;
   correction checks; parameter table against run J and Davey.
2. The standard run report (`report/build_report.py`, fix or work around the known page-3 layout defect) for the 16
   supplement seeds, built on deskstar from the job folder's final files, under the heavy lock.
3. Save the PDFs and figures to the repo (`results/run-j-supplement/reports/`) and to the exchange; do not delete the
   deskstar job folder (Pete decides after the reports exist).

## E. End-to-end calibration: protocol and 5-case smoke (Pete approved 19 Oct about 04:00Z)

Source proposal: the composer/architecture thread's three-tier design (tier 1a strict SBC, 1b coverage by latitude band, tier 2
wrong-model stress tests, tier 3 real known-truth links), answering `results/project-assessment-2026-10-18.md` §6 item 2.

1. Write and commit the pre-registered protocol `threads/work-orders/e2e-calibration-protocol-2026-10-19.md` BEFORE any case
   runs: truths from the engine prior (18:01 radar prior, route family, mode, speed/altitude, fuel, end-of-flight family and
   latents, ocean model, windage); synthetic BTO/BFO at every handshake with the model noise and bias drift, 00:19 per data
   option; synthetic finds from drift forward transport; Bernoulli search outcome from q and ρ (detected cases kept);
   statistics (rank of truth for along-arc position at 00:19, impact latitude and time, cross-arc distance; 50/90/95 % HPD
   coverage; reliability of family, end-of-flight family, 00:19 cause), per factor stack (core; core+drift; core+searches;
   all evidence); sample sizes (100 for 1a, about 10 per 5 deg band for 1b); pass criteria; what a failure triggers.
2. Run a 5-case smoke at reduced scale: deskstar under the heavy lock (queue behind order D's report build if it holds the
   lock), at most 40 threads, deskstar disk cap 10 GB; Mac use light only. Record per-case Monte Carlo noise and wall time;
   give the cost estimate for 100 + 40 cases at the scale the ESS floor needs.
3. Do not start the full run; it waits for Pete's review of the smoke.
