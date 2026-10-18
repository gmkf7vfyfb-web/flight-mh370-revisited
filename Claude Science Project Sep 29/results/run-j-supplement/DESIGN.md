# Run-J northern supplement: measurement, design, cost and predictions (core, 18 Oct 2026, posted before the run)

Approval: Pete, 18 Oct 2026 00:41Z (architecture.md, item 1), including the run. Requests: END_OF_FLIGHT / architecture.md
2026-10-17 20:41Z (end of flight), CORE_STAGES 2026-10-17 19:50Z (composer). Target: >= 1,000 effective distinct 00:11
parents in every 5 deg band of impact latitude that holds > 1 % of the mass, under D2, D3 and D4, after combination with production.
Run J convergence is a PASS by project ruling (Pete, 16 Oct 2026 ~22:20Z; confirmed for all four families 18 Oct 2026); this work adds northern detail, it does not re-open that ruling.

## 1. Measurement (run J as it is; all 74 seeds; scripts and JSON in `measure/`)

End of flight's band ESS (`band_ess.py`) is reproduced exactly (for example D3, 30-25 S: 84 / 83). Two new views:
(a) parents with IDENTICAL 00:11 states (latitude, longitude, altitude, BFO bias) are merged, because resampled copies are
distinct hand-off rows but not distinct paths; (b) nested subsets of descents per parent and of parents.

**Table 1. Impact band: mass; Kish ESS over rows / parents / distinct 00:11 states.**

| Treatment | 35-30 S | 30-25 S | 25-20 S |
|---|---|---|---|
| D0' | 0.093; 109k / 30k / **17.5k** | 0.013; 15.8k / 3.5k / **1.41k** | 0.0025; 6.5k / 1.5k / **378** |
| D2 | 0.068; 6.0k / 5.2k / 4.4k | 0.011; 1,081 / 906 / **342** | 0.0034; 184 / 167 / 109 |
| D3 | 0.064; 308 / 306 / 305 | 0.010; 84 / 83 / 79 | 0.0020; 22 / 22 / 21 |
| D4 | 0.065; 370 / 365 / 355 | 0.012; 167 / 155 / **120** | 0.0021; 104 / 88 / 57 |

**Table 2. ESS (rows / parents) against the share of the sample used** (D3 and D4; the full sample is 64 rows per parent).

| | 8 rows per parent | 16 | 32 | 64 (all) | 1/8 of parents | 2/8 | 4/8 |
|---|---|---|---|---|---|---|---|
| D3, 35-30 S | 77 | 158 | 139 | 308 | 23 | 53 | 133 |
| D3, 30-25 S | 27 | 55 | 66 | 84 | 33 | 74 | 36 |
| D4, 35-30 S | 144 | 286 | 738 | 370 | 92 | 255 | 611 |
| D4, 30-25 S | 21 | 63 | 84 | 167 | 28 | 39 | 84 |

**Table 3. What the 00:11 populations hold (waypoints, per seed; band of 00:11 latitude 30-25 S).** Coincidence ESS =
C(m,2) / (pairs of hand-off rows with the same state): an estimate of the effective number of distinct states the hand-off
draw can reach.

| Mode | Particles (run J) | Hand-off rows | Distinct states | Coincidence ESS |
|---|---|---|---|---|
| True heading | 1.0M | 241 | 143 | 118 |
| Magnetic heading | 0.5M | 560 | 139 | 53 |
| True track | 2.5M | 53 | 51 | (no pairs) |
| Magnetic track | 0.5M | 1,099 | 202 | 45 |
| Lateral navigation | 2.5M | 116 | 106 | 1,300 |

**Findings.**
1. Under D3 and D4 the band ESS rises about linearly with descents per parent AND with parents (Table 2; heavy-tailed, so
   noisy). Rows ESS is about equal to parents ESS because about one descent per parent fits the two 00:19 BFOs, not because
   the parents are exhausted. So total northern descents set the D3 ESS where few states are used (35-30 S).
2. Distinct states are the limit in 30-25 S and north: D0' has only 1.41k effective distinct 00:11 states in 30-25 S and
   378 in 25-20 S. A Poisson-hit estimate of the number of states that can fit (G = ESS (1 + lambda) / lambda, lambda =
   rows ESS / states ESS - 1) gives D2 about 500 and D4 about 430 in 30-25 S: more descents on the existing states cannot
   reach 1,000 there.
3. The populations themselves are thin in the north for the magnetic modes, which carry the north: per seed only about 45-53
   effective distinct states in 30-25 S (Table 3); all modes together about 174 per seed (about 4.2k over 24 seeds), against
   about 59 per seed in the hand-off rows.

## 2. Design decision

| Option | Can it reach the target? | Cost |
|---|---|---|
| (a) flattened 00:11 hand-off from the EXISTING populations (re-run of run J seeds; the 00:11 population is not stored) | **No** in 30-25 S under D2/D4: at most about 3x the distinct states (about 4.2k D0'), so G about 1.3-1.5k with ALL 24 seeds re-run (about 9 h) | 9 h |
| (b) mode re-allocation alone (new seeds, normal hand-off) | Slowly: about 2.4x distinct northern states per seed, but the normal hand-off uses about 1/3 of them | many seeds |
| (c) evidence-tilted filter (new filter code) | Probably, but about a day to build and gate | > 1 day |
| **(a)+(b) on NEW seeds (chosen)** | **Yes for D2 and D4; D3 needs end of flight's descents (below)** | about 6.5 deskstar h |

**Chosen design.** 16 NEW waypoint seeds (1001-1016; no overlap with any run J random stream), run J configuration
unchanged except:
- **(b) particles re-allocated to the modes that carry the north:** [TH, MH, TT, MT, LN] = [1.2, 1.3, 1.1, 2.2, 1.2]M
  (run J [1.0, 0.5, 2.5, 0.5, 2.5]M; 7.0M in total; largest mode 2.2M, so memory stays below run J). Allocation n_m
  proportional to m_m / sqrt(a_m) (Kish-optimal across modes; m = mode mass in 30-25 S under D0', a = distinct-state ESS per
  million particles per seed). Exact: each mode is its own filter and the mixture is weighted by mode evidence.
- **(a) a second 00:11 hand-off, `handoff-m0011-supplement/` (flag `output.handoff_supplement`, off by default):** 100,000
  rows per seed drawn from the same per-mode look-ahead rows as the normal hand-off with q = P(mode)/N x r(lat),
  r = 0.1 + 0.9 h(bin)/H, flattened part spread over 00:11 latitude -34.5..-29.5 (45 %), -29.5..-25.5 (40 %), -25.5..-21.0 (15 %)
  (by the run J 00:11-to-impact map these feed impact 35-30, 30-25 and 25-20 S). Defensive share 0.1 of the unchanged
  posterior. Each row carries the exact correction in log_correction (standalone use = the normal recipe); mis.npy and
  production-mis.npy carry ln rho for multiple importance sampling. No latitude band changes the target.
- The normal hand-offs (m2241, m0011, 100k rows) and final.npy of the new seeds are written as usual (valid extra replicates).

## 3. Gates and checks (before any supplement seed)

1. Unit tests (new: corrected supplement alone, and combined with the normal rows by the balance heuristic, both reproduce
   the exact hand-off expectation; rho is one function of mode and latitude; config validation; overlay loads).
2. Gates B and C byte-identical to `~/mh370/gates-2026-10-15/`; regress-seed1 equal.
3. FLAG OFF: run J repro seed 1 at the new HEAD byte-identical to run J (final.npy, hand-offs, routes, trace, tanks32).
4. FLAG ON: run J waypoints seed 1 at the new HEAD: every normal output byte-identical to run J seed 1, plus a supplement
   drawn from run J's own population.
5. Prior recovery: corrected supplement means against the uncorrected run (|z| < 3): on seed 1 (same population) and on the
   new seeds against run J's 24 seeds; re-allocation checked on final.npy and the normal hand-off.

## 4. Cost

- deskstar: build, tests, gates about 15 min; flag-off repro seed 1 about 6 min; flag-on waypoints seed 1 about 22 min;
  16 seeds x about 22 min = about 5.9 h. **Total about 6.6 h** (cap 10 h; the job starts no seed that would end after 9.3 h).
  It starts only when the drift arc-latitude chain writes ALL-DONE (that chain takes the heavy lock per leg).
- deskstar disk about 2 GB per seed (about 34 GB; 66 GB free). Mac: hand-offs, sidecars and diagnostics only (about
  0.15 GB per seed, about 3 GB), no final.npy.
- End of flight (its estimate): 10-15 min per 100k parents at 14 threads, about 2.8 GB per 100k parents at 64 rows per parent.
  All 1.6M supplement rows would be about 4-6 h and about 45 GB; a uniform every-k-th-row subset is valid (README).

## 5. Predictions (written before the run)

P1. Gates B/C identical; flag-off repro seed 1 identical; flag-on seed 1 normal outputs identical.
P2. Prior recovery |z| < 3 for every checked mean (latitude, longitude, altitude, Mach, BFO bias, P(north of 33 S), mode
    probabilities).
P3. Supplement rows north of 35 S at 00:11: about 0.92. Impact bands (via the run J map): about 40 % in 35-30 S, 38 % in
    30-25 S, 14 % in 25-20 S.
P4. D0' effective distinct 00:11 states after MIS with production: 30-25 S 4k-10k (now 1.41k); 25-20 S 1k-3k (now 378).
P5. With end of flight's production recipe (64 rows per parent) on all supplement rows, combined by MIS:
    D2 >= 1,000 in all three bands; D4 30-25 S 0.8k-2.5k and 35-30 S 0.6k-1.5k; D3 35-30 S 0.5k-1.2k and 30-25 S
    0.5k-1.5k. **D3 is limited by descents**: where it is short, more descents per northern parent are the exact remedy
    (Table 2: linear), at end of flight's cost, with no new core run.
P6. Side result for the mode-allocation question: magnetic-mode ln Z seed sd lower than run J's by about x0.6 if the
    mode-probability noise is particle-limited; about unchanged if it is structural.
