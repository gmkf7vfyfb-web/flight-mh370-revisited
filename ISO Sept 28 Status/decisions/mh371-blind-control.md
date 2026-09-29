---
name: mh371-blind-control
description: MH371 known-flight control must be run blind — window/config/scoring fixed before truth is read; only the scorer reads ACARS truth
metadata:
  node_type: memory
  type: feedback
  originSessionId: c924a4ee-d933-4d28-bd74-6dd738e4c3d8
  modified: 2026-09-25T23:53:03.872Z
---

Run the MH371 validation (9M-MRO, 7 March 2014, Beijing to Kuala Lumpur) prospectively:
- Fix the time window, config and scoring before looking at the truth track.
- Take the window from Davey et al.'s validation segment (book Fig. 9.7).
- Only the scoring script reads the ACARS truth (/jackbox/home/MH370-inputs/acars/mh370-acars-position-and-wind-reports.xlsx, sheet "ACARS"). Don't browse it while building the observation set or prior.
- SATCOM for MH371 comes from the SITA log, which starts 2014-03-07 00:51 UTC.
- Already seen on 2026-09-25, and disclosed in status.md: ACARS rows 01:33–02:59 UTC (altitude, Mach, gross weight, fuel on board; no positions).

**Why:** the architecture thread (thr_4pbhvf3sxi) reported that in the old work the MH371 window was moved after the truth was inspected, so the control wasn't blind. MH371 was the most informative check there: it exposed a sampler failure and ruled out WSPR.
**How to apply:** when starting MH371 work, write the config and scorer first and commit them, then run; the prior may come from pre-window ACARS only if that is decided before reading. Related: [[fuel-performance-plan]] (ACARS fuel-on-board check).
