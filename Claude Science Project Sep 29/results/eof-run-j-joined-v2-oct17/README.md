# End of flight on core run J: joined V2 with the 22:41 onset proposal window — 17 Oct 2026

**Status:** run J waypoints, both arms (J0011 and J2241): seeds 1-8 complete at 06:56Z, seeds 9-12 at 11:22Z seeds 13-16 at 13:28Z (section 2c gives the 16-seed headline).
- Core run J's split-half convergence is accepted as a pass by project ruling (16 Oct 2026).
- The precision statements below are about end of flight's own sampling.
- This run is the direct 22:41-arm run that Pete deferred to run J's end-of-flight pass (ruling of 16 Oct 02:08Z).

## 1. What was run
- **Driver:** `full/run_j_joined_v2.sh`, which is `run_joined_v2.sh` on run J with three changes:
  - the run-J production laws (round-3 laws, bank limit U[52, 90] deg);
  - in J2241, the clock-time onset proposal window [22:41:21, 00:10:59] (`smoke/onset-window-2241.toml`), with the exact
    ln(prior/proposal) correction, so that the stored weights still target the fuel-tied prior;
  - binary sha256 19031f41748ecb0c.
- **Summary:** `full/summarise_joined_v2_run_j.sh`. The per-seed U1 sensitivity is in `onset-uniform/seed-*.json`, by the same method
  and convention as `results/eof-order-b-oct15/onset-uniform/` (two-factor totals, q = 1/3, C2 silent, transmission imposed).
- **Proposal check:** in seed 1 of J2241, the unweighted deliberate onsets are spread over the window (398k-655k rows in each sixth;
  517k in the last, 00:00-00:11). The weighted shares keep the fuel-tied decline (0.305 in the first sixth, 0.049 in the last).
- **Prior recovery of U1:** 0.997-1.002 on all 8 seeds.

## 2. Result: the planned-descent (B) share, fuel-tied against U1 (median over 8 seeds, range in brackets)

| 00:19 treatment | B share, fuel-tied, run J | B share, U1, run J | B share, fuel-tied, run I | pre-00:11 share, fuel-tied → U1, run J | pre-00:11 ESS per seed, run J | A1 / A2, run J |
|---|---|---|---|---|---|---|
| D0' | **0.194** (0.111-0.316) | 0.168 (0.094-0.262) | 0.108 (0.062-0.254) | 0.140 → 0.112 | 112-157 | 0.26 / 0.51 |
| D2 | 0.104 (0.048-0.149) | 0.104 (0.048-0.149) | 0.077 (0.021-0.119) | 0.0004 → 0.0002 | 1-7 | 0.49 / 0.39 |
| D4 | 0.051 (0.019-0.098) | 0.051 (0.019-0.098) | 0.044 (0.020-0.089) | 0.0000 → 0.0000 | 1-2 | 0.37 / 0.56 |

**Reading.**
1. **Under D0', the B share is higher on run J than on run I** (0.194 against 0.108), almost entirely through pre-00:11 onsets
   (0.140 against 0.068 on run I seed 1). The seed range is wide (0.111-0.316). The two runs differ in their core inputs (24 seeds,
   BFO noise 4.32 Hz, fuel factor kx) **and** in the descent laws, so this change cannot be attributed to either.
2. **U1 lowers B slightly on run J too** (0.194 → 0.168), in the same direction as on run I. The fuel-tied headline and the U1
   sensitivity bracket B under D0' at 0.17-0.19.
3. **With 00:19 data (D2, D4), pre-00:11 descents carry no weight**, as on run I. The B share there comes from onsets after 00:11.
4. **"00:11 selects cruise" still holds:** under D0', A1 + A2 is 0.77 against B 0.19 (seed 1-8 medians). It is weaker than on run I
   (0.88 against 0.11). The paper should quote the run-J figure with its seed range.

## 2b. Extension to 12 seeds (seeds 9-12 added 17 Oct, 09:57-11:22Z; remedy (a) in part, limited by disk)

| 00:19 treatment | B share, fuel-tied, median of 12 (range) | B share, U1, median of 12 | seeds 1-8 / seeds 9-12, fuel-tied | pre-00:11 share, fuel-tied → U1 | pre-00:11 ESS, summed over 12 seeds |
|---|---|---|---|---|---|
| D0' | **0.179** (0.104-0.316) | 0.151 (0.089-0.262) | 0.194 / 0.170 | 0.125 → 0.096 | 1,551 |
| D2 | 0.091 (0.044-0.149) | 0.091 | 0.104 / 0.075 | 0.0003 → 0.0002 | 44 |
| D4 | 0.049 (0.019-0.098) | 0.049 | 0.051 / 0.043 | 0.0000 | 18 |

- Prior recovery of U1 is 0.997-1.002 on all 12 seeds.
- **The four new seeds agree with the first eight within their seed spread.** The 12-seed headline under D0' is B 0.18 (fuel-tied)
  and 0.15 (U1), against run I's 0.11 and 0.10.
- **This supersedes the 8-seed figures in section 2 as the headline.** The remaining 12 waypoints seeds would raise the pooled
  pre-00:11 ESS from about 1,550 to about 3,100, but need about 36 GB more disk.

## 2c. 16 seeds — HEADLINE (seeds 13-16 added 12:05-13:28Z, 17 Oct)

| 00:19 treatment | B share, fuel-tied, median of 16 (range) | B share, U1 | A1 / A2, fuel-tied | pre-00:11 share, fuel-tied → U1 | pre-00:11 ESS, summed over 16 seeds |
|---|---|---|---|---|---|
| D0' | **0.196** (0.098-0.316) | **0.168** (0.080-0.262) | 0.27 / 0.51 | 0.143 → 0.109 | 2,091 |
| D2 | 0.091 (0.044-0.149) | 0.091 | 0.50 / 0.39 | 0.0004 → 0.0002 | 49 |
| D4 | 0.048 (0.019-0.098) | 0.048 | 0.38 / 0.56 | 0.0000 | 25 |

- Prior recovery of U1 is 0.997-1.002 on all 16 seeds.
- **The headline is stable as seeds are added:** the D0' median B is 0.194 at 8 seeds, 0.179 at 12 and 0.196 at 16.
- **Run J gives B 0.17-0.20 under D0'** (U1 to fuel-tied), against run I's 0.10-0.11.
- The remaining 8 waypoints seeds (17-24) need about 24 GB more disk.
- This section supersedes sections 2 and 2b as the headline.

## 3. Why the window proposal did not raise the pre-00:11 ESS (diagnosed on seed 1, D0')
- The pre-00:11 B population has an ESS of 122 rows and **121 effective parents** out of 100,000 22:41 parents. It is
  **parent-limited**.
- The stored weights alone (prior x proposal correction) have an ESS of 192,679, so the window correction is not the cause.
- The 00:11-and-later likelihood alone has an ESS of 3,750. Combined with the 22:41 parents, it collapses onto about 120 of them:
  only a few 22:41 states can start a planned descent and still meet the 00:11 arc.
- 73 % of the mass starts 23:41-00:11 (ESS 104), 27 % starts 23:11-23:41 (ESS 24), and the first half hour carries none.
- **So more onset draws per parent cannot help.** The remedies are more 22:41 parents:
  - (a) J2241 on all 24 run-J waypoints seeds, which would give about 3 times the pooled ESS (about 3,000 over 24 seeds). Cost: about
    7.5 h and about 48 GB in the current slim format. This needs disk.
  - (b) A core request for a larger or aimed 22:41 hand-off (more rows at m2241, or a look-ahead tilt towards states that can descend
    and still meet 00:11).
- I recommend (a) first: it needs no core change, it fits overnight once disk allows, and it tests whether the 0.19 is stable.

## 4. COVERAGE
**(a) Feasible set.** A planned descent may begin at any time from 22:41 to exhaustion.

**(b) Model's reach.** Every onset time from 22:41 is reachable for both deliberate mechanisms. The window adds no reach.

**(c) Proposal's coverage.**
- Pre-00:11 B under D0': **112-157 effective impacts per seed (about 1,000 pooled over 8 seeds)**. This is parent-limited. The share
  is estimable at this precision, but its seed spread is wide. It is a declared end-of-flight coverage gap until remedy (a) or (b).
- Under D2 and D4, pre-00:11 B is not estimable (1-8 per seed). This is reported as "not assessed at this depth", not as absent.
- The J0011 arm uses 32 descents per parent, so its D3 and D4 cells are thin (minimum ESS 40 and 208). Use the waypoints production
  and supplementary sets for D3/D4, not this arm.

**Bounds and sources.**
- Onset window: the joined-V2 split epochs.
- Fuel-tied prior (headline) and U1 (declared sensitivity): Pete's ruling.
- Bank limit U[52, 90] deg (Pete); dive probability p = 0.5 (Decision 4).

> The uncontrolled-arm dynamics are not calibrated: the Boeing leave-one-out gate failed in all
> three rounds. Impact energy, attitude, flight-path angle and energy-transfer duration from
> this arm are a labelled sensitivity on uncalibrated dynamics, not a physical prediction.
