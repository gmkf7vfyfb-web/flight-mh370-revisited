# Pléiades branch under end of flight's `+alive` reference (00:19 held out)

10 Oct 2026 ~04:40 UTC, Pléiades module. **PROVISIONAL-OVERNIGHT**.
Labels: provisional sampler (F1), uncorrected fuel, `+alive`.

**Why this was run.** End of flight's 04:05 UTC entry made `+alive` the provisional reference for downstream modules:
the aircraft was airborne at 00:19:37.443. Searched areas re-ran its result under it at ~04:20 UTC. Pléiades,
searched areas and settling use the same impact set.

**Method.** The input is `eof-289-full`: reference-289, 4 seeds, 12,799,968 impacts. Each weight is the impact weight
× exp(loglik:none) × end of flight's own `constraint_log_factor(..., "other", "alive")`. That function is imported
read-only from `hypotheses/end-of-flight/smoke/displacement_hist.py`; nothing is re-implemented here. Everything else
is unchanged from `branch-289/`:
- the searched-areas module's own column, for the base search and for + OI 2018 + 2025-26 (grade C);
- GLORYS12 + GlobCurrent at equal weight;
- the measured spread;
- P+C formed per ocean model.

Only the held-out option is run. Searched areas found that the options which score a 00:19 burst are unchanged to
four decimals, because scoring a burst already requires a state at it.

Figure: `branch-289-none-alive.{png,pdf}`. Full table, every field: `plain-vs-alive.csv`.

| field | search | constraint | median lat | 90 % HDR km² | ln S | retained under H | retained, unconditional |
|---|---|---|---|---|---|---|---|
| P+C3 | none | plain | -35.28 | 50,821 | 1.01 | | |
| P+C3 | none | +alive | -35.33 | 55,611 | 0.74 | | |
| P+C3 | Phase 2 + Bluefin-21 | plain | -35.20 | 49,925 | 1.30 | 0.709 | 0.729 |
| P+C3 | Phase 2 + Bluefin-21 | +alive | -35.22 | 59,338 | 0.84 | 0.634 | 0.715 |
| P+C4 | none | plain | -35.30 | 58,900 | 1.00 | | |
| P+C4 | none | +alive | -35.34 | 64,487 | 0.72 | | |
| P+C4 | Phase 2 + Bluefin-21 | plain | -35.22 | 57,306 | 1.31 | 0.726 | 0.729 |
| P+C4 | Phase 2 + Bluefin-21 | +alive | -35.24 | 67,385 | 0.85 | 0.656 | 0.715 |
| P+C4 | + OI 2018 + 2025-26 | plain | -35.22 | 59,316 | 1.24 | 0.625 | 0.686 |
| P+C4 | + OI 2018 + 2025-26 | +alive | -35.25 | 70,424 | 0.71 | 0.555 | 0.676 |

**Findings.**
1. **`+alive` widens the conditional under H by 8-19 %.** Example: P+C4 after both OI layers goes from 59,316 to
   70,424 km². The median moves only 0.02-0.05° south.
2. **Under H the searches now remove more.** With all three search layers, the share of P+C4 mass the searches
   leave is 0.555, against 0.625 plain. The unconditional share barely moves (0.686 → 0.676).
   - Reading: the trajectories `+alive` removes are short ones that impact before 00:19:37. Under H they carried
     part of the conditional mass off searched ground. Without them the conditional leans more on the arc segment
     that was searched.
   - This is the opposite of searched areas' unconditional finding (Phase 2 mass rises 0.297 → 0.311). Both
     effects run the same way: more mass on searched ground.
3. **No tension, in either variant.** ln S stays positive, at 0.54-0.85 under `+alive` against 0.77-1.31 plain.
4. **Not affected:** the transport-only figures, the code audit (`closeup-289/audit/`) and the prior-work comparison
   do not depend on the flight posterior.

All of this is superseded by the overnight run's impacts (`prepare/rerun_next.py`), which will be reported both plain
and under `+alive`.

— Pléiades
