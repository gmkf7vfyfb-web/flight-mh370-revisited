# Review of the 22:41 A-against-B stand-in on core run D (end of flight, 11 Oct 2026)

Reviewed: `results/eof-a-vs-b-2241-run-d-standin.md` (architecture stand-in, 07:45-10:56 UTC), its scripts and per-seed JSON.

## Verdict: ADOPTED as the module's run D A-vs-B result, with one correction to its reading (section 2)
- Recipe faithful to `full/sweep_2241_ab.sh`; only the input changed; the run C reproduction is exact (+0.72 on descent-climb seed 1).
- Deviations accepted: (1) no rebuild, physics identical to run C; (2) R600 BTO Only derived with `derived_logliks` - the right
  construction (the in-stage `m0011` option plus the Gaussian 00:19:29 BTO term); (3) `mini.npz` instead of `slim.npz` and no impact
  positions - acceptable for Bayes factors; maps need a re-run; (4) the 4-seed agreement rule s.e. <= 0.25 nat - accepted; (5) `~v212`
  as Pleiades - consistent with the module's own `~v212` keys; (6), (7) noted.
- Labels carried: UNCONVERGED (core run D); EoF physics provisional (G13; no push-over, no system sequence); reach gap.

## 2. Correction to the reading: the A:B Bayes factor is conditional on B's onset-time prior
B's onset is anticipatory (lead U[0, 96 min] before the predicted exhaustion) or a fuel cue (30-70 min before it). So in arm B
**67 % of the prior begins the descent before 23:15, 32 % between 23:15 and 00:11, and 1 % after 00:11** (review smoke below). The 23:15
and 00:11 data (mostly the BFOs) rule out the early descents, and the Bayes factor A:B is then largely the prior mass B puts on them.

Review smoke (run D `next-d-free` seed 1, m2241 look-ahead hand-off, sha256 verified; the stand-in's recipe at N = 1 child x 4 descents;
`review-run-d-b-onset-split-free-s1-n1.json` in `results/eof-items-3-4-smoke-oct11/`). SMOKE, not evidence:

| data (scored in-stage) | ln BF A:B, whole B | A against B, onset before 23:15 | A against B, onset 23:15-00:11 | A against B, onset after 00:11 (eff. parents) |
|---|---|---|---|---|
| 23:15 BFO + 00:11 BTO + BFO (Held Out) | +0.29 | +4.49 | **-0.74** | **-1.77** (3) |
| + R600, inflated BFO noise | +0.76 | +7.80 | -0.23 | -1.75 (267) |
| 23:15 BFO only | +0.46 | +1.40 | -0.33 | -0.44 (185) |

So **"weak evidence for A" is evidence against descents begun before 23:15**; deliberate descents begun after 23:15 are not
disfavoured (and those after 00:11 are mildly favoured over A, on few parents). The headline should be stated per onset window.
**Coverage gap G-k (new, proposal):** B onsets after 00:11 have 1 % of B's prior and a few effective parents; fix: a B proposal
stratified uniformly in onset time between the hand-off and the predicted exhaustion, with the proposal correction in the weights.
The onset-time prior itself (lead U[0, 96 min]) is a module choice without a source: declared as a conditional (G-d, extended).

## 3. For core: why the look-ahead did not raise the effective parents
The run D look-ahead weights m2241 rows by the m0011 BTO. In this stage the evidence is driven by the 23:15 and 00:11 BFOs, which
depend on whether and when the module's descent begins (23:15 + 00:11 BFO alone: +1.57 nat), not on the cruise state alone. A
look-ahead on the BTO cannot anticipate that, so the corrected-weight ESS (20 %) buys no effective parents after in-stage scoring.

- End of flight
