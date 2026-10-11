# Run G — six waypoint routes, full scale (11 Oct 2026)

Config `next-run/server-g-routes.toml` on the run C stack (s7 + s8 PROVISIONAL, inop-flow-fix), routes family
`early-families/waypoints.toml` with `turn_backs` (overshoot rule), routes 10, 11, 3, 2, 19, 43 at equal prior 1/6;
8 seeds × 3M particles; run C sampler (16 equal stages); binary 28f46c7; deskstar job 425aa841.
00:19 data: m0019a and m0019b BTO, no 00:19 BFO (Davey's treatment); log-on cause not modelled.

## Result against the posted prediction

| Quantity | Predicted | Result |
|---|---|---|
| ln Z route 10 / 11 | within ±0.3 of pilot (−128.4 to −128.6) | −128.60 ± 0.04 / −128.49 ± 0.05 |
| ISBIX fraction of the ANOKO routes | 0.50 ± 0.10 | 0.529 ± 0.012 |
| Route 3 below route 11 | 1.5–2 nats | 1.93 nats |
| Family median at 00:19 | −36.75 ± 0.10 | −36.71 |
| Split-half (all 35 balanced partitions) | ≥ 0.924 | 0.980 (0.971–0.987) |

Family ln Z −129.55 (seed sd 0.03). Per-route ln Z = family ln Z + ln(6 × share), per seed, then mean ± sd.

## Per route (`run-g-per-route.csv`; quantiles are medians over seeds of per-seed weighted quantiles)

| Route | Share | ln Z | 00:19 lat median (5–95 %) | Mach initial | Mach 00:19 | Alt 00:19 ft |
|---|---|---|---|---|---|---|
| 10 NILAM–ANOKO–BULVA | 0.432 | −128.60 | −36.81 (−37.12 to −34.53) | 0.796 | 0.693 | 35,000 |
| 11 NILAM–ANOKO–ISBIX | 0.486 | −128.49 | −36.70 (−36.97 to −33.67) | 0.791 | 0.694 | 34,197 |
| 3 NILAM–IGOGU–ISBIX | 0.071 | −130.41 | −36.28 (−36.60 to −27.01) | 0.796 | 0.694 | 33,117 |
| 2 NILAM–IGOGU–BULVA | 0.010 | −132.34 | −34.75 (−36.47 to −25.80) | 0.803 | 0.687 | 33,500 |
| 19 NILAM–SAMAK–ISBIX | 0.000 | −135.7 | −35.39 | 0.795 | 0.696 | 32,825 |
| 43 MEKAR–SAMAK–ISBIX | 0.001 | −135.1 | −35.91 | 0.810 | 0.668 | 30,000 |

## Timing and ground speed (`run-g-timing-by-turn-fix.csv`; medians, 5–95 % in the CSV)

Route samples (2,000 per seed) grouped by turn fix by nearest-polyline fit (cut 15 NM; the engine's track capture after
a fly-by turn gives ~12 NM transient cross-track, so the 4 NM cut used for free paths rejects nearly all route samples).
BULVA and ISBIX share the path to the end fix, so they are not separated here.

| Group | n | MEKAR | NILAM | Turn fix | GS MEKAR–NILAM | GS NILAM–fix | GS after turn | 00:11 lat median |
|---|---|---|---|---|---|---|---|---|
| Turn at ANOKO | 14,547 | 18:21:59 | 18:26:17 | 18:39:03 | 476 | 450 | 459 | −35.76 |
| Turn at IGOGU | 1,439 | 18:21:31 | 18:25:41 | 18:39:21 | 492 | 454 | 464 | −35.26 |

## 00:11 arc-crossing latitude (`arc-0011-latitude-comparison.csv`)

Route vertex interpolated to 00:10:59 (unix 1394237459).

| Group | n | median | 2.5–97.5 % |
|---|---|---|---|
| Run G, turn at ANOKO | 14,547 | −35.76 | −36.14 to −30.75 |
| Run G, turn at IGOGU | 1,439 | −35.26 | −35.68 to −27.28 |
| Run D free, all | 8,000 | −36.05 | −37.12 to −27.18 |
| Run D free, ≤ 4 NM of NILAM–ANOKO line to 19:11:49 | 1,081 | −36.67 | −36.82 to −33.32 |
| Run D free, ≤ 4 NM of NILAM–IGOGU line | 925 | −36.21 | −36.56 to −26.64 |
| Run D routes family (old rule, route 27) | 8,000 | −36.26 | −36.57 to −30.31 |

**Flag.** Route-following ANOKO paths cross 00:11 0.9° north of free paths that fly the same line to 19:11. First
diagnosis (medians): at 19:41:49 the free on-line paths are at −1.20 vs −0.75 (≈ 27 NM further south), and from 19:41
to 00:01 they average 477 vs 471 kt on track 186° vs 184°. Head start plus speed ≈ 53 NM ≈ 0.9° along the arc. The
head start accrues between the turn and 19:41, where route mode's fly-by turn and track capture add path length.
This is a description, not yet a cause; the 00:19 medians differ less (run G −36.71, run D free family about −37.0).

## Files

`run-g-routes-map.png/.pdf` (map with plain and technical footnotes), `make_run_g_map.py`, `run.json`, `summary.json`,
`route-shares.json` (per seed, per route: share, rows, quantiles of 00:19 lat, initial Mach, 00:19 Mach, 00:19 altitude).
Raw outputs stay on deskstar (J15 `runs-g/next-g-routes`) per ruling.
