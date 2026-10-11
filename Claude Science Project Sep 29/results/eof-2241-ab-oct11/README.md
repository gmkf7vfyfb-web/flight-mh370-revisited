# 22:41 A-vs-B on core run C: SMOKE only so far (end of flight, 11 Oct 2026, ~00:30 UTC)

**SMOKE. NOT CONVERGED. NOT TO BE QUOTED AS EVIDENCE.** Core run C `next-c-free` seed 1, m2241 hand-off (sha256 verified against core's
COMPACT.txt), N = 1 child x 4 descents, 2 threads. Binary `/tmp/mh370-eof-runc4` (097a5d77). Module recipe as run C (idle floor,
v2-broad, family-b-ditching, residual-bank-boeing P(left) = 0.8 PROVISIONAL). Reach-gap label: rapid descents above 6,500 ft/min and
unloading not reachable by the model.

Arms (same data, so ln Z(A) - ln Z(B) is a Bayes factor):
- **A**: onset only at fuel exhaustion (`smoke/arm-v1.toml`): families A1 / A2 (incl. 'lost').
- **B**: deliberate onset only, anticipatory (up to 96 min before exhaustion) or fuel cue, with family B's control
  (`full/arm-b-deliberate.toml` + `full/family-b-ditching.toml`).

| data option scored in-stage | ln BF A:B | eff. parents A / B | median impact latitude A / B |
|---|---|---|---|
| 00:11 (23:15 BFO, 00:11 BTO + BFO) | +0.62 | 228 / 358 | -37.36 / -35.49 |
| 00:11 BTO only | +0.34 | 307 / 580 | -37.00 / -35.36 |
| 23:15 BFO + 00:11 BFO | +1.76 | 16,455 / 4,889 | -37.00 / -36.28 |
| 00:11 + R600 (inflated BFO noise) | +0.67 | 93 / 63 | -37.68 / -35.96 |
| options with both 00:19 bursts | not estimable (1-3 eff. parents) | | |

Reading (smoke): the data through 00:11 mildly favour A over B (about +0.6 nat), mostly through the 00:11 BFO (+1.8 nat). B puts
impacts about 2 deg further north. The ESS (a few hundred parents) is far from converged. Full run queued: `full/sweep_2241_ab.sh`,
4 strata x seeds 1-4, N = 4 x 4, under the heavy lock after the run C sweep; per-seed JSON `runs/C2241-<stratum>-s<k>-ab.json`.

## COVERAGE
(a) Feasible set: both families from 22:41. (b) Reach: A cannot descend before exhaustion; B cannot have a flame-out-associated
onset; outside-B (deliberate onset, then no intervention) excluded by ruling. (c) Proposal: one seed, N = 1; 00:19 two-burst options
not covered (open; targeted sampler). Bounds: anticipatory lead U[0, 96 min] (module), deliberate control [ditching 0.5,
maintained-then-lost 0.5] (family-b-ditching, ruled 15:45 -0600).

- End of flight
