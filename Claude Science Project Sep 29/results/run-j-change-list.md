
# Run J change list

Reconstructed 15 October 2026 by the outgoing core thread from the committed coordination record
(its handover, GAP 2) and filed here by the coordination session. Pete's 13 October 00:40Z ruling
cuts the list to core items only. **Run J needs Pete's own explicit GO; no delegated GO applies.**
Before it starts, post a proposal with size, ETA, disk and predictions.

| # | Item | Source | Evidence | State |
|---|---|---|---|---|
| 1 | Waypoint and free-flight convergence. All-partition split-half: waypoints 0.916, free 0.830, against the 8-replicate floor 0.924. | Run I; composer pass 2 §8 | A 23:15 refresh smoke changed nothing (Δln Z −0.01). More particles (estimated 2.2–5×) is the only tested remedy. | Deferred, no date |
| 2 | Aimed proposal for the northern arc, about 34–25 S. Searched-area evidence moves weight north. | Composer pass 2 §8 | No smoke yet | Not designed |
| 3 | 18:25:27 R600 epoch: BFO 142 Hz as observed (sd 7); BTO 12,520 µs (sd 62), included but flagged; only the last two R1200 BFOs (18:28:05 and 18:28:14), which run I already uses. | Pete's ruling, 12 Oct | Smoke f529c67a, `results/run-i-oct12/r600-1825-smoke.csv` | Data file committed: `engine/data/variants/satcom-observations-r600-1825.csv` + `config/sensitivity/obs-r600-1825.toml` (4297f3bc) |
| 3a | For item 3: record the BER and C/N0 of the 18:25:27 burst from the Inmarsat log, if the project holds it. Holland excluded it for signal quality, and arm E's −89 assumes it is trustworthy. | PAPER.md 19:05Z | — | Open |
| 4 | Wording rules for charts and notes (Pete's language rule; "Holland transient bias added"). | Architecture, 12 Oct | — | Applies to reports, not config |
| 5 | **Added 15 Oct:** the 00:19 two-burst hand-off proposal — item 10, `threads/work-orders/item10-order-rev2-2026-10-15.md`. Design first, no run. | Coordination, 15 Oct | Effective hand-off parents 38.8 (both raw) and 170 (both with bias), per seed | Not designed |
| 6 | **Added 15 Oct:** BFO sd 4.32 Hz (Davey Table 5.1, in-flight empirical, the larger value) in the production run; 7 Hz as a declared sensitivity. Also a one-seed check at 7 Hz with the bias-drift term off, to find why our 4 Hz shoulder (0.2931) matches Davey's 7 Hz shoulder (0.2406). | Pete, 15 Oct | 4 Hz sweep: shoulder 0.1739→0.2931, +1.52 nat | Agreed, not run |
| 7 | **Added 15 Oct:** uniform-onset prior for planned descent (B) as a sensitivity | Coordination, 15 Oct (`results/answers-2026-10-15-pm.md` §3) | Reweighting: D0 B 0.108→0.225 | EoF order b, item 4 |
| 8 | **Added 15 Oct:** D0 = 00:19 values held out, transmission imposed (airborne at 00:19:37) | Pete, 15 Oct | 32.8% of D0 weight impacts before 00:19 today | EoF order b, item 2 |

Adding item 3's epoch renumbers every later step and shifts every later random stream, so run J can
never be byte-compared with run I; compare statistically.
