# End of flight: the planned-descent arm V2 against V1b, from the 22:41 hand-off, with the 00:11 BFO (10 Oct 2026)

**SMOKE. UNCORRECTED FUEL. PROVISIONAL SAMPLER.**
- SMOKE: 100,000 parents x 2 children x 4 descents per seed, seeds 1-2.
- UNCORRECTED FUEL: the 22:41 fuel state carries audit F1-F4, so absolute exhaustion times are provisional.
- PROVISIONAL SAMPLER: the 22:41 population comes from a tempered epoch, before core request 17.

As architecture says (~23:10 UTC), comparisons between arms are more robust than absolute values.

**Runs.** `runs/eof-2241-r14-{v1,v2}-s{1,2}`:
- terminal stage on core's `reference-289` m2241 hand-off (`runs/snap289-m2241` links to core's `handoff-m2241`); prior track 289.7 deg;
- binary built at `c959e690`, which includes core request 14 (`34ef6bc`): the 23:15 and 00:11 BFOs are scored in-stage by the filter's own bias
  sequence, and the bias is drifted to 00:19;
- configs: davey2016 + no-exhaustion-prior + reference-snapshots + early-families/overnight/reference-289 + `smoke/snapshot-m2241.toml`
  + `smoke/terminal.toml` + `smoke/options-m2241.toml` + `smoke/children-2.toml` + `full/seed-k.toml` + `smoke/arm-v{1,2}.toml`
  + `full/descent-idle-floor.toml`.

**Arms.** Brief section 1:
- **V1b**: flame-out-associated onset only;
- **V2**: anticipatory (lead U[0, 5,760] s before the cruise-predicted exhaustion), fuel cue, and flame-out-associated, weights 1:1:1.

Same hand-off, same data, so per-option evidence gives a direct Bayes factor.

**Descent fuel.** The descent burns at its own thrust (core tables x thrust / level drag). Floor: ICAO EEDB, Trent 892, UID 2RR027 idle 0.30 kg/s per
engine at sea-level static ISA, with altitude scaling drawn between delta sqrt(theta) and Boeing Fuel Flow Method 2 (`results/eof-descent-fuel-oct09/`).
The onset cue uses the cruise prediction by design. The exhaustion time is the descent's own.

## 1. Evidence, V2 against V1b, per option

ln BF = ln Z(V2) - ln Z(V1b) on the same data; pooled = ln of the mean Z over the two seeds. "Estimable" means at least 30 effective parents per seed in both arms.

| option x log-on cause | seed 1 | seed 2 | pooled | eff. parents / seed, V1b / V2 | estimable |
|---|---|---|---|---|---|
| `none__other` | +0.00 | -0.00 | -0.00 | 100,000 / 100,000 | yes |
| `none__fuel-exhaustion` | -0.75 | -0.85 | -0.81 | 6,613 / 4,776 | yes |
| `m0011__other` | -0.34 | -0.38 | -0.36 | 801 / 904 | yes |
| `m0011__fuel-exhaustion` | -0.72 | -0.93 | -0.83 | 85 / 62 | yes |
| `m0011+r600_inflated__other` | -0.69 | -0.76 | -0.73 | 339 / 172 | yes |
| `m0011+r600_inflated__fuel-exhaustion` | -0.82 | -1.05 | -0.94 | 49 / 28 | **no** |
| `m0011+r600_no-offset__other` | -0.56 | -0.49 | -0.53 | 32 / 13 | **no** |
| `m0011+r600_no-offset__fuel-exhaustion` | -0.80 | -0.96 | -0.89 | 22 / 8 | **no** |
| `m0011+r600_startup-offset__other` | -0.67 | -0.97 | -0.85 | 35 / 16 | **no** |
| `m0011+r600_startup-offset__fuel-exhaustion` | -0.53 | -1.11 | -0.90 | 14 / 7 | **no** |
| `m0011+r1200_inflated__other` | -0.38 | -1.18 | -0.69 | 16 / 11 | **no** |
| `m0011+r1200_inflated__fuel-exhaustion` | -0.82 | -1.21 | -1.04 | 7 / 4 | **no** |
| `m0011+r1200_no-offset__other` | -0.98 | -3.38 | -1.24 | 3 / 2 | **no** |
| `m0011+r1200_no-offset__fuel-exhaustion` | -3.33 | -6.21 | -3.99 | 2 / 2 | **no** |
| `m0011+r1200_startup-offset__other` | -0.51 | -1.90 | -1.08 | 10 / 3 | **no** |
| `m0011+r1200_startup-offset__fuel-exhaustion` | -1.58 | -2.86 | -1.95 | 3 / 2 | **no** |
| `m0011+both_inflated__other` | -1.08 | +0.03 | -0.67 | 6 / 3 | **no** |
| `m0011+both_inflated__fuel-exhaustion` | +0.07 | -1.05 | -0.15 | 2 / 3 | **no** |
| `m0011+both_no-offset__other` | -45.22 | -5.80 | -16.77 | 1 / 1 | **no** |
| `m0011+both_no-offset__fuel-exhaustion` | -40.25 | -8.68 | -37.47 | 1 / 1 | **no** |
| `m0011+both_startup-offset__other` | -21.27 | -18.50 | -21.27 | 1 / 1 | **no** |
| `m0011+both_startup-offset__fuel-exhaustion` | -28.38 | -35.38 | -28.39 | 1 / 1 | **no** |
| `r600-bto__other` | -0.55 | -0.58 | -0.56 | 8,593 / 6,758 | yes |
| `r600-bto__fuel-exhaustion` | -0.61 | -0.65 | -0.64 | 301 / 230 | yes |
| `both-bto__other` | -0.55 | -0.56 | -0.55 | 5,353 / 4,073 | yes |
| `both-bto__fuel-exhaustion` | -0.62 | -0.64 | -0.63 | 193 / 139 | yes |

**Reading.**
- **Two different thresholds, stated explicitly (correction, 10 Oct ~03:00 UTC).** A Bayes factor is a ratio of means
  (marginal likelihoods). Here it is accepted at >= 30 effective parents per seed in both arms **and** seed agreement. A posterior shape needs
  >= 1,000 effective impacts, which is the NOT ESTIMABLE stamp on the maps. A row can pass the first test and fail the second.
- Wherever the comparison is estimable as evidence, the data **mildly favour V1b over V2**, and the two seeds agree to <= 0.21:
  - 23:15 + 00:11, cause `other`: ln BF -0.36. Both the evidence and the posterior are estimable (map panel b);
  - 23:15 + 00:11, fuel-exhaustion: -0.83. **Evidence only: the posterior is not estimable** (panel c; effective parents per seed: V1b 69 and 101, V2 55 and 69);
  - adding the R600 BTO/BFO under `inflated`: -0.73 (`other`). **Evidence only in V2** (panel d; 884 effective impacts over two seeds; effective parents per seed: V1b 300 and 377, V2 159 and 185);
  - the 00:19 BTO-only options, which score 00:19 without 23:15 and 00:11: -0.55 to -0.64;
  - the fuel-exhaustion log-on alone: -0.81.
  The R600 rows under Holland's two BFO models (`no-offset`, `startup-offset`) are **not** estimable in V2: 7-16 effective parents.
- On the usual scale, |ln BF| < 1 is weak. This is the planned-descent hypothesis **not being supported, rather than being refuted**.
- **All R1200 and two-burst rows are not estimable**: 1-16 effective parents. Their Bayes factors (down to -45) are noise.

## 2. The 22:41 sample-size wall

Scoring the 23:15 BFO and the 00:11 BTO/BFO in-stage leaves **about 800-900 effective parents per seed of 100,000**. The 00:19 BFO
options then leave 1-35. At 00:11 the filter itself resampled and rejuvenated, which is why the 00:11 hand-off arms did not hit this wall.
**V2 with the 00:19 data needs either many more 22:41 parents or a look-ahead resampling at the 22:41 hand-off** (proposed core request 10, here at
22:41, with g = the 00:11 BTO/BFO likelihood of a cheap cruise propagation). As at 00:11, more children cannot lift it, because the limit is the parents.

## 3. What the 00:11 data do to V2 (seed 1)

| arm / option | onset mechanism, anticipatory / fuel cue / flame-out | powered at onset | median onset - 00:19:29.4, s | median impact - 00:19:29.4, s | flame-out in lag window | endurance ratio (KM median, powered) |
|---|---|---|---|---|---|---|
| v1/none__other | 0.00 / 0.00 / 1.00 | 0.00 | +81 | +1148 | 0.082 | nan |
| v1/m0011__other | 0.00 / 0.00 / 1.00 | 0.00 | +344 | +1517 | 0.145 | nan |
| v1/m0011__fuel-exhaustion | 0.00 / 0.00 / 1.00 | 0.00 | -92 | +1298 | 0.992 | nan |
| v1/r600-bto__other | 0.00 / 0.00 / 1.00 | 0.00 | -482 | +730 | 0.074 | nan |
| v2/none__other | 0.33 / 0.33 / 0.34 | 0.55 | -1664 | -392 | 0.038 | 1.11 |
| v2/m0011__other | 0.17 / 0.36 / 0.47 | 0.51 | -356 | +1087 | 0.098 | 1.59 |
| v2/m0011__fuel-exhaustion | 0.16 / 0.18 / 0.66 | 0.30 | -121 | +946 | 0.991 | 0.88 |
| v2/r600-bto__other | 0.19 / 0.22 / 0.59 | 0.34 | -698 | +675 | 0.068 | 1.31 |

- Scoring 23:15 and 00:11 moves V2's weight **away from early anticipatory descents** (0.33 -> 0.17) towards flame-out-associated onsets
  (0.34 -> 0.47, and 0.66 with the fuel-exhaustion log-on). The cruise BFOs and the 00:11 BTO prefer the aircraft still in cruise at 00:11.
- Without 00:11 data, V2's median impact is 6.5 min **before** 00:19:29. With it, the median impact is 18 min after.
- In V2's powered descents the endurance ratio is 1.1-1.6 (exhaustion pushed out, as Pete expected), and 0.88 under the fuel-exhaustion log-on, which selects the
  faster burners.

## 4. Maps

`impact-map-2241-v1-greyscale.{pdf,png}`, `impact-map-2241-v2-greyscale.{pdf,png}`: project greyscale, HPD 50/90/99, two seeds pooled, run
footnote beneath each (standing rule). Panels with < 1,000 effective impacts are stamped NOT ESTIMABLE.

## 5. Next
- Present to Pete with the caveats. The estimable answer is "V2 mildly disfavoured (ln BF about -0.4 to -0.9); its two-burst arms are not estimable from 22:41".
- Re-run on corrected fuel (request 16 in the next core run) and the fixed sampler (request 17) when the next hand-off exists.
- Core request 10 at 22:41 is the route to the 00:19 BFO rows.
