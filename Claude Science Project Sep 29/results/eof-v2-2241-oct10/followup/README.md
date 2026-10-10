# V1b and V2 from 22:41: profiles, what the 00:11 data select, R600 as observed, and why V1b is favoured (10 Oct 2026)

**SMOKE, UNCORRECTED FUEL, PROVISIONAL SAMPLER.**
- Runs: `runs/eof-2241-tr-{v1,v2}-s{1,2}`, from core `reference-289` m2241, prior track 289.7 deg; 100,000 parents x 2 children x 4 descents per seed.
- Build `9fdad5fb-dirty`, committed as this commit: module-only additions, namely burst-state latents, a trace recorder and four options.
- All 95 columns shared with `eof-2241-r14-*` are byte-identical, and the dense-trace re-runs reproduce the rows exactly. The additions change nothing sampled.
- Descent burn: core tables x thrust / level drag, with the ICAO EEDB Trent 892 idle floor.

## 1. Vertical profiles (`vertical-profiles-2241.png`)

- **Sample.** 40 descents per panel, drawn in proportion to the prior or the 00:11 posterior from a hash-selected 1-in-25 traced subset
  (about 32,000 per arm; 99.99% joined to their impact rows). The posterior panels rest on a traced-subset ESS of 143 (V1b) and 107 (V2), so they are
  representative but coarse.
- **Cruise segment.** From 22:41 to onset the aircraft is flown by the core's cruise dynamics, which the module does not record. It is drawn flat at the takeover altitude.
- **V1b.** No powered descent; every onset is a flame-out. After 00:11 is scored, every surviving flame-out comes after 00:11, because a flame-out before 00:11
  leaves the SDU unpowered for the 00:11 burst.
- **V2.** Descents begin from 22:41 onward, with level-offs, emergency descents and continuous descents. After 00:11 is scored, survivors begin
  from about 23:30, and the earliest are mostly late.

## 2. What the 00:11 data select (seed means; selection factor = posterior / prior share)

| arm | state | prior | 23:15 BFO | 23:15 + 00:11 BFO | 00:11 BTO | 23:15 BFO + 00:11 BTO/BFO |
|---|---|---|---|---|---|---|
| V1b | down before 00:11 | 0.084 | 0.076 (x0.90) | 0.000 (x0.00) | 0.000 (x0.00) | 0.000 (x0.00) |
| V1b | cruise at 00:11 (onset later) | 0.680 | 0.706 (x1.04) | 1.000 (x1.47) | 1.000 (x1.47) | 1.000 (x1.47) |
| V1b | descending at 00:11 (< -300 ft/min) | 0.212 | 0.196 (x0.92) | 0.000 (x0.00) | 0.000 (x0.00) | 0.000 (x0.00) |
| V1b | steep at 00:11 (< -3,000 ft/min) | 0.046 | 0.043 (x0.93) | 0.000 (x0.00) | 0.000 (x0.00) | 0.000 (x0.00) |
| V1b | level or climbing after onset at 00:11 | 0.024 | 0.022 (x0.94) | 0.000 (x0.00) | 0.000 (x0.00) | 0.000 (x0.00) |
| V1b | onset before 23:15 | 0.000 | - | - | - | - |
| V1b | onset 23:15-00:11 | 0.320 | 0.294 (x0.92) | 0.000 (x0.00) | 0.000 (x0.00) | 0.000 (x0.00) |
| V2 | down before 00:11 | 0.491 | 0.418 (x0.85) | 0.000 (x0.00) | 0.000 (x0.00) | 0.000 (x0.00) |
| V2 | cruise at 00:11 (onset later) | 0.279 | 0.327 (x1.17) | 0.842 (x3.02) | 0.453 (x1.62) | 0.561 (x2.01) |
| V2 | descending at 00:11 (< -300 ft/min) | 0.192 | 0.211 (x1.10) | 0.103 (x0.54) | 0.434 (x2.26) | 0.302 (x1.57) |
| V2 | steep at 00:11 (< -3,000 ft/min) | 0.029 | 0.032 (x1.10) | 0.000 (x0.00) | 0.048 (x1.67) | 0.000 (x0.00) |
| V2 | level or climbing after onset at 00:11 | 0.038 | 0.043 (x1.12) | 0.055 (x1.44) | 0.112 (x2.94) | 0.137 (x3.58) |
| V2 | onset before 23:15 | 0.158 | 0.053 (x0.34) | 0.002 (x0.01) | 0.002 (x0.01) | 0.001 (x0.01) |
| V2 | onset 23:15-00:11 | 0.563 | 0.620 (x1.10) | 0.156 (x0.28) | 0.545 (x0.97) | 0.438 (x0.78) |

- **Descending trajectories are preserved in V2, but only gentle ones.** Under the full 00:11 data the weight on descending at 00:11 rises from 0.19 to
  0.30. Their descent rate at 00:11 is -1,030 ft/min (median; 5-95% -1,630 to -460), their altitude 21,000 ft (3,000-33,000), and their onset about 12 min
  before 00:11. **Everything steeper than -3,000 ft/min is eliminated, by the BFO.** The 00:11 BFO alone keeps descents of -380 to -1,460 ft/min.
  The 00:11 BTO alone favours descending states (x2.3).
- **V1b keeps nothing descending at 00:11.** A V1b descent has flamed out, so the 00:11 burst is impossible (the SDU is unpowered).
- **Early descents die.** Onset before 23:15 is cut to x0.34 by the 23:15 BFO, and to x0.01 by the 00:11 data.

**Where the descending survivors cross the 6th arc** (`arc6-crossing-v2-descending.png`): median 34.1 deg S along the arc (5-95% 35.5-31.7 deg S),
ESS 1,722 over two seeds. That is north of where the descending prior crosses (34.3 deg S median, with a long northern tail to 24.9 deg S), and south of the
BFO-only selection (32.6 deg S).

## 3. R600 only, BFO as observed (`impact-map-r600-observed-*.png`)

- **From 22:41 it is not estimable in either arm**: 37-832 effective impacts. The maps are stamped.
- **From the 00:11 hand-off (reference-289, 4 seeds) it is converged.** With the `other` log-on cause: ESS 197,569, median 37.25 deg S, split-half 0.940. With
  fuel exhaustion: ESS 59,512, median 37.28 deg S, split-half 0.935.
- It is narrower along the arc than held out and sits just inside the 7th arc. Using the BTO alone (panel d) puts much less constraint on the latitude.

## 4. What panel (c) samples (V1b and V2 maps, option `m0011__fuel-exhaustion`)

- **Population:** the 22:41 parents (core's filtering distribution at 22:41 from reference-289, unscored after 22:41), 100,000 per seed.
- **For each parent:**
  - 2 children; each draws its onset (V1b: at flame-out; V2: anticipatory / fuel-cue / flame-out, 1:1:1), and the core flies the cruise from 22:41 to that onset;
  - 4 descents per child; each draws control, profile shape, aero and spiral.
- **Weight per descent:** hand-off weight x L(23:15 BFO) x L(00:11 BTO) x L(00:11 BFO) (in-stage, the filter's own bias sequence, core request 14)
  x the Erlang(8, 14.875 s) density of (00:19:29.416 - realised flame-out).
  - A flame-out after the log-on, or none before impact, gets weight zero. A burst after flame-out cannot be answered.
  - **No 00:19 BTO or BFO is used** in (c).
- **What survives:** descents that are cruising or gently descending at 00:11 and whose single flame-out falls before 00:19:29, weighted by the lag density
  (mean 119 s, sd 42 s), so most weight sits 1-4 min before the log-on.
  - V1b: 69-101 effective parents per seed.
  - V2: 55-69.
  - Hence NOT ESTIMABLE as a posterior shape; the evidence (ln Z) is usable.

(Panel (c) of the four-priority map of 9 Oct is Holland H1: both 00:19 bursts with the start-up offset, fuel-exhaustion log-on, from 00:11; not estimable.)

## 5. Why V1b is favoured, and by how much

**The Bayes factor and its parts.** ln BF = ln Z(V2) - ln Z(V1b) on identical data:

| data | ln Z V1b (s1, s2) | ln Z V2 (s1, s2) | ln BF per seed | pooled | min eff. parents V1b / V2 |
|---|---|---|---|---|---|
| 23:15 BFO | -3.91, -3.93 | -4.02, -4.04 | -0.10, -0.11 | **-0.11** | 84,187 / 80,265 |
| 00:11 BTO | -9.54, -9.51 | -9.67, -9.70 | -0.13, -0.19 | **-0.16** | 1,208 / 1,813 |
| 23:15 + 00:11 BFO | -7.34, -7.45 | -8.04, -8.15 | -0.69, -0.71 | **-0.70** | 49,706 / 34,263 |
| 23:15 BFO + 00:11 BTO/BFO | -16.84, -16.81 | -17.18, -17.19 | -0.34, -0.38 | **-0.36** | 776 / 886 |
| as above + fuel-exhaustion log-on lag | -24.30, -24.11 | -25.02, -25.04 | -0.72, -0.93 | **-0.83** | 69 / 55 |
| R600 BTO/BFO as observed (no 00:11) | -16.30, -16.34 | -17.05, -17.03 | -0.75, -0.70 | **-0.72** | 296 / 158 |

Monte Carlo error: the parent-bootstrap s.e. of each ln Z is 0.034-0.039, and the two seeds agree to <= 0.04 on the main row. So **-0.36 +- about 0.05** is a
property of the model, not of sampling.

**Exact decomposition.** V2 is a prior mixture of its three onset mechanisms, so Z(V2) = sum_k pi_k Z_k, and the Bayes factor is the prior-weighted mean of
the component ratios r_k = Z_k / Z(V1b):

| V2 component | prior pi_k | r_k = Z_k / Z(V1b) | ln r_k |
|---|---|---|---|
| flame-out-associated | 1/3 | 0.98 | -0.02 |
| fuel cue | 1/3 | 0.73 | -0.32 |
| anticipatory | 1/3 | 0.38 | -0.96 |

- r_F is about 1: V2's flame-out component **is** V1b, which is an internal consistency check.
- The whole Bayes factor comes from the other two components predicting the 23:15 and 00:11 data less well.

**Which part of the anticipatory component is penalised** (ln Z_bin / Z(V1b), by lead before the cruise-predicted exhaustion):

| lead | 0-10 min | 10-20 min | 20-40 min | 40-60 min | 60-96 min |
|---|---|---|---|---|---|
| ln ratio | -0.13 | -0.20 | -0.50 | -1.32 | -2.21 |

**The mechanism.**
- A descent begun 40-96 min before exhaustion is descending, or already low, at 23:15 and 00:11.
- The cruise BFOs at those bursts are about 17.5 Hz per 1,000 ft/min sensitive, against a 7 Hz sd, and they say the aircraft was not descending steeply then.
- So an Occam penalty falls on the part of V2's prior that predicts early descents. Late anticipatory descents (lead < 20 min) score almost like V1b.
- By datum: the BFOs carry the penalty (ln BF -0.70 from 23:15 + 00:11 BFO alone). The 00:11 BTO partly offsets it, because it prefers the gently descending
  states V2 can supply (x2.3 on descending at 00:11). The 23:15 BFO and the 00:11 BTO alone are nearly neutral (-0.11, -0.16).

**How much the verdict depends on V2's prior** (the same component ratios, re-weighted):
- equal 1/3 weights: ln BF -0.36;
- no fuel cue (1/2, 0, 1/2): -0.38;
- no anticipatory (0, 1/2, 1/2): -0.16;
- (0.6, 0.2, 0.2): -0.56;
- anticipatory lead restricted to U[0, 20 min]: -0.16.

The Bayes factor is therefore **bounded between about -0.6 and 0 for any reasonable V2 prior**. **The data never favour V2, and never reject it.**

**Statistical reading.**
- |ln BF| < 1 is "not worth more than a bare mention" (Jeffreys; Kass & Raftery 1995). The posterior odds V2:V1b at equal prior odds are 0.70 (main row),
  0.44 (with the fuel-exhaustion log-on, evidence only).
- What the data do say firmly is about **timing within V2**: a deliberate descent begun more than about 40 min before exhaustion is disfavoured by a factor of
  3.7-9 relative to V1b, and descents steeper than 3,000 ft/min at 00:11 are excluded.
- Caveats:
  - uncorrected fuel: exhaustion times shift under request 16, so the lead-bin boundaries may move;
  - provisional sampler (request 17);
  - point-mass descent physics, which the 6-DOF will replace;
  - 2 seeds;
  - the 00:19 BFO rows are not estimable from 22:41 (look-ahead needed).
