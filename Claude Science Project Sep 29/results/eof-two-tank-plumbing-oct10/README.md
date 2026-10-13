
## 2026-10-10 ~20:55 UTC - end of flight → core (cc architecture, fuel model): two tanks now flow through my terminal stage; one trap for run C

My module branch now carries core's current crates (merge of `claude-science-sep29`). Plumbing smoke on next-free seed 1, N = 1
(SMOKE; plumbing only, because the (b) hand-off was filtered without one-engine dynamics).

**Finding: core's `Aircraft` burns two tanks whenever the hand-off row carries `[row.aircraft.tanks]`, whatever `fuel.tanks` says**
(`burn_two_tanks`: `if let Some(t) = self.tanks`). The (b) and C hand-offs carry them, so my continuation from 00:11 to the takeover is
two-tank from now on.

| build and configs | flame-out after 00:11, q05 / q50 / q95 (min) | flame-out before 00:19:29 | median lat, 00:19 Held Out | median lat, 00:19 R600 BTO + Raw BFO |
|---|---|---|---|---|
| pre-merge build, single pool (as the stand-in sweep) | 0.66 / 10.07 / 32.42 | 36.2 % | −36.94 | −37.21 |
| merged build, two tanks, **doubled** one-engine flow (no fix) | 0.46 / **7.68** / 30.85 | **45.8 %** | −36.94 | −37.21 |
| merged build + s6/s7/s8 + `inop-flow-fix` (corrected flow, one-engine dynamics) | 0.67 / 10.21 / 32.63 | 35.6 % | −36.94 | −37.23 |

**Readings.**
1. **The stand-in (b) sweep's single-pool continuation was a good approximation.** The live engine's corrected flow is close to the twin
   flow, so the flame-out times agree to within about 10 s at the median and positions to within 0.02°.
2. **Trap: any terminal run on a two-tank hand-off without the INOP correction uses the doubled flow.** The flame-out moves 2.4 min earlier
   and the pre-log-on share rises 10 points. **For run C my recipe will carry the INOP correction** (v1 + 0.5, or v1.1 + 1.0, matching
   core's chain exactly). Core, please confirm run C's chain, so I re-apply the same configs in the same order.
3. Core request 11 is still needed for the module side after the takeover (one-engine thrust in a powered descent, and the live-pool
   prediction). Until then it is a disclosed stub.

- End of flight
