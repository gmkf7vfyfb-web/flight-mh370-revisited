# Ocean drift: status (updated 17 Oct 2026)

Read after `threads/master-prompts/ocean-drift.md`. Replace entries when they change; do not append history here
(history is in git and in `coordination/OCEAN_DRIFT.md`).

## Current base run
Core run J; end of flight run J, four families (waypoints 24 seeds, free 18, descent-climb 16, radar reproduction 16),
00:19 treatments D0'-D5, headline cell `D<d> total q=0.333 (C2 silent)`.

## Drift surfaces in use
- Run A node surfaces, both models, 710-713 nodes, bandwidths 25/50/100/200 km: `results/debris-drift-runA-rebuilt/`
  (rebuilt 16 Oct from per-impact columns; not a transport run) and `mh370-exchange/debris-drift/runA-rebuilt/`.
- Australian 15-160 E pilot, 178 nodes, both models: `results/drift-runj-2026-10-17/australia-160E/`.
- Refinement of the 94 nodes carrying 95 % of the run J core mass (independent seeds, 17 Oct): node tables
  `results/drift-items-2026-10-17/refine-core94/`. Use the pooled values (mean in likelihood of stored and refined) at those nodes.

## Headline numbers (run J, D0', two models equal weight, 50 km)
| Quantity | Value | Source |
|---|---|---|
| Shift of mean latitude, finds only | +0.81 deg pooled (stored +0.70, independent re-run +0.93), ln BF -0.76 | `refine-core94.json` |
| Same, other families | free +0.68, descent-climb +0.62, radar reproduction +0.74 | `results/drift-items-2026-10-17/drift-by-flight-family.csv` |
| With Australian term, headline scheme (tiers 1/0.3/0, level 0.5) | +3.82 deg pooled (stored +3.83) (range 0.3-0.65: +2.84..+4.42), ln BF -2.12 | `australia-three-tier.csv` |
| Same, GlobCurrent alone / GLORYS12 alone | +2.86 / +5.17 deg | same |
| Populated-only, level 1 (earlier sensitivity) | +4.44 deg, ln BF -2.30 (95 % incl. law misfit +3.64..+5.22) | `aus-noise.json` |
| Sinking, e-folding 1/2/3 yr (level 1) | +6.4 / +5.5 / +5.1 deg | `sinking-effect.csv` |
| Refloat 1/200 and 1/69 per day (headline scheme) | about +3.5..+3.7 and +3.1..+3.7 deg | `refloat-*.csv` |
| Find-timing check (share of arrivals before find date, three earliest finds) | core 0.15-0.23, 30 S 0.37-0.55 | `find-timing-check.csv` |
| Pleiades Australian factor vs core (level 1) | ln LR +0.75 | `pleiades-australia.json` |
| Debris fate from the core (by 30 Jun 2016) | Western Australia 20.8 %, Madagascar 11.5 %, total ashore 49.4 % | `results/drift-runj-2026-10-17/debris-maps/core-pdf/` |

## Open questions
- Dedicated drift run with the headline Australian tiers (would remove the post hoc reconstruction); combine with
  the arc-latitude scan (26-36 S, denser south of 33 S) proposed by the arc-latitude thread.
- Drift run with refloat on for the likelihood itself (configs `australia-refloat-r069/r200.toml` exist).
- Family pooling of drift results is the composer's step.
- 5-year forcing extension deferred (Pete, 17 Oct); GlobCurrent multi-year product retires 24 Nov 2026.
