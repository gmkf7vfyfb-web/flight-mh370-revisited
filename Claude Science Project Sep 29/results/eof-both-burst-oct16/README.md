# Both-burst 00:19 cells (D3, D4): the descent-sampling fix, smoke on seed 1 — 16 Oct 2026

**Status: SMOKE (sections 1-4: run I repro seed 1; section 4b: run J waypoints seed 1). Not evidence; do not quote.** Answers core's work request of 15 Oct 23:17Z
(`coordination/END_OF_FLIGHT.md`; core note `results/item10-phase1/smoke-2026-10-15.md`). The seed-2 repeat could not run:
core's run-I hand-offs were removed from `mh370-exchange/core/run-i/` at 02:00:45Z on 16 Oct (folder time stamp), so the repeat is
**not assessed**, not failed.

## 1. Arms
All three arms: repro-radar stratum, seed 1, 100,000 m0011 parents, run-I dive recipe (`full/c2-silent-aim.toml` +
`full/dive-branch.toml`), binary `/tmp/mh370-eof-ob1` (sha256 dc1f52f8b4345712...; reproduces the item-8 seed bit for bit with the new options off).
- **Base.** 8 x 4 = 32 descents per parent (production).
- **Aimed selection (K = 8).** `smoke/score-select-0019.toml`: per parent, 8 times more candidate descents are simulated and kept
  by an aimed draw on the 00:19:29.416 / 00:19:37.443 pair score ("both" target), with the exact selection correction carried in the
  weight (request 9, approved). 32 descents kept per parent. Run time 21 min against about 4 min for base (5.3x).
- **Brute force (children 64).** 256 descents per parent, no aiming. Run time about 39 min (about 10x).

## 2. Acceptance (a) and (c): effective parents / effective impacts, ln Z change against base

| 00:19 cell | base | aimed K = 8 | children 64 | ln Z change, aimed | ln Z change, children 64 | split halves A/B: base; aimed; ch64 | parent ESS ceiling (base) |
|---|---|---|---|---|---|---|---|
| held out (D0 raw) | 35,783 / 399,896 | 28,339 / 100,048 | 38,502 / 3,164,112 | +0.000 | +0.000 | 33,246/32,783; 22,211/21,946; 38,121/38,039 | 39,061 |
| R600 BFO | 8,364 / 11,424 | 3,544 / 4,070 | 24,116 / 76,589 | -0.007 | +0.017 | 4,861/4,629; 2,122/1,736; 18,307/18,071 | 35,381 |
| D3 both raw | 227 / 228 | 751 / 758 | 833 / 845 | +0.053 | +0.089 | 99/134; 612/295; 679/319 | 45,728 |
| D4 both, start-up offset | 32 / 32 | 676 / 683 | 775 / 790 | -0.127 | -0.136 | 11/53; 230/778; 297/568 | 121,898 |
| both, inflated sd | 564 / 570 | 5,009 / 5,765 | 6,352 / 7,653 | -0.036 | -0.043 | 181/764; 2,119/3,585; 3,960/3,198 | 59,301 |

**Reading.**
1. **(a) not met.** Neither fix reaches 1,000 effective impacts in D3 or D4 on this seed: aimed 758 / 683, brute force 845 / 790.
   Both raise D3 by 3.3-3.7x and D4 by 21-25x. The D4 base figure (32) rests on a few heavy parents (halves 11 / 53) and is far below
   core's 651-741 on the same stratum (core used the run-I recipe; this smoke uses the run-I dive recipe). That difference is **not
   resolved** here.
2. **Scaling is sub-linear in D3.** Eight times the descents gave 3.7x the effective parents (228 to 833), not the 8x that core
   predicted. All arms remain far below the parent-level ceiling (30k-122k). So the descent supply is still the limit, but each extra
   descent pays less than predicted.
3. **(c) met within seed noise.** The two improved arms agree with each other on ln Z to 0.04 nat in every cell (D3 +0.053 / +0.089;
   D4 -0.127 / -0.136). The D4 shift against base is what one expects when the base estimate rests on 32 effective impacts.
4. **Cost of aiming to the other cells.** The aimed arm lowers held-out effective impacts from 399,896 to 100,048 and R600 from
   11,424 to 4,070. So aiming is **not** suitable for the production arm. It is suitable only as a separate arm that scores D3-D5.
   Brute force helps every cell (held-out 3.16 M, R600 76,589).
5. **(d) split halves.** Halves stay uncorrelated in the both-burst cells in every arm (|corr| <= 0.003), as before the fix. The
   observed effective parents are nearer the ceiling, but still at about 1-2 per cent of it.

## 3. Acceptance (b): prior recovery, aimed arm against base, 00:19 likelihood off (held-out cell)

Weight ratio aimed / base 0.9992; children 64 / base 1.0005. Family shares within 0.001 (A1 0.1477 / 0.1467; A2 0.3289 / 0.3297; B controlled 0.5223 / 0.5226).

| quantity | max CDF difference, aimed vs base | max CDF difference, children 64 vs base |
|---|---|---|
| latitude_deg | 0.0025 | 0.0014 |
| unix_s | 0.0024 | 0.0010 |
| latent:onset_unix_s | 0.0016 | 0.0015 |
| latent:pushover_rate_fpm | 0.0105 | 0.0031 |
| latent:pushover_hold_s | 0.0071 | 0.0043 |
| latent:max_descent_rate_fpm | 0.0050 | 0.0008 |
| flight_path_angle_deg | 0.0032 | 0.0018 |

**Reading.** The aimed arm misses the 0.0030 standard on two latents: push-over rate 0.0105 and push-over hold 0.0071. The
children-64 arm, which has no aiming and is exact by construction, differs from base by up to 0.0043. That value is a measure of the
Monte Carlo noise in base itself. So about 0.004-0.005 of the aimed arm's 0.0105 is base noise, and the rest is either noise in the
aimed arm (its held-out ESS is 4x lower) or a defect in the selection correction. One seed cannot separate these. The seed-2 repeat
was meant to separate them; it is not assessed (see the status line). **Until it is repeated, the aimed arm is marginal on (b).**

## 4. Proposal for run J's end-of-flight pass (needs Pete's GO; nothing started)
- **Option 1 (recommended): brute force on the production arm,** children 64 (256 descents per parent). It is exact with no new
  correction, it passes (b) at the noise level, and it improves every cell. Cost: about 10x the terminal stage per seed, and 8x the
  impact rows. It needs compaction to the D-cell columns only, or keeping only a weighted subsample of the held-out cell. Disk per
  seed must be planned with core before run J's copies land.
- **Option 2: a separate aimed arm (K = 8) for D3-D5 only,** with production unchanged. Cost: about 5.3x per seed for that arm.
  Before it is used, prior recovery (b) must be repeated on at least two more seeds.
- **Either way the 1,000 target is not reached per seed on this stratum. It is reached only by pooling seeds:** run J has 16 repro
  seeds, which gives about 12,000-13,000 pooled D3 or D4 effective impacts at children 64, if the seeds are independent. The per-seed
  target needs about 2-3x more descents again (sub-linear), which is about 25-30x base cost. I do not recommend that.
- The verification still needed is run J seed 1 of the repro stratum, base against children 64 against aimed, as soon as its
  hand-offs land (about 1 h).


## 4b. Check on run J (16 Oct 2026, 03:32-04:28Z): waypoints stratum, seed 1, all three arms

**Status: SMOKE, one seed. Not evidence.** Hand-off: core `run-j/run-j-smoke-waypoints/bto-bfo/seed-1/handoff-m0011` (sha256 of the
uncompressed hand-off verified against core's COMPACT.txt; 99,998 parents). Config chain = core's run.json `config_paths` without
`config/sensitivity/run-j/smoke.toml`, which is not in the repository (it sizes core's smoke filter, not the terminal stage). Binary built
from 16f2eb1 in target-r3, sha256 19031f41748ecb0c (a second build after the run gave the same hash). Recipe as section 1. Times at 14 threads:
base 3.0 min, children 64 31.1 min (10.4x), aimed 20.8 min (6.9x). This is the stratum that carries 0.9982 of the core prior.

| 00:19 cell | base: eff parents / eff impacts | aimed K = 8 | children 64 | ln Z change, aimed | ln Z change, children 64 | parent ESS ceiling (base) |
|---|---|---|---|---|---|---|
| held out | 57,283 / 637,257 | 45,159 / 159,759 | 61,613 / 5,201,849 | +0.000 | +0.000 | 62,381 |
| R600 BFO | 5,781 / 6,703 | 1,290 / 1,319 | 26,367 / 53,193 | +0.006 | -0.023 | 55,770 |
| D3 both raw | 219 / 219 | 66 / 66 | 488 / 494 | +0.325 | +0.150 | 119,499 |
| D4 both, start-up offset | 251 / 252 | 1,291 / 1,322 | 2,576 / 2,666 | -0.033 | -0.062 | 33,710 |
| both, inflated sd | 3,299 / 3,479 | 9,816 / 11,696 | 19,620 / 27,637 | -0.022 | -0.020 | 76,326 |

Prior recovery with the 00:19 likelihood off (held-out cell), max CDF difference against base (standard 0.0030):

| quantity | aimed | children 64 |
|---|---|---|
| latitude_deg | 0.0018 | 0.0009 |
| unix_s | 0.0015 | 0.0013 |
| latent:onset_unix_s | 0.0036 | 0.0011 |
| latent:pushover_rate_fpm | 0.0033 | 0.0016 |
| latent:pushover_hold_s | 0.0051 | 0.0022 |
| latent:max_descent_rate_fpm | 0.0021 | 0.0011 |
| flight_path_angle_deg | 0.0047 | 0.0007 |

**Reading.**
1. **Children 64 passes (b) here:** the largest difference is 0.0022, which is inside the 0.0030 standard. **The aimed arm fails (b)** on
   four quantities, the largest 0.0051 (push-over hold). This repeats the repro-stratum result on a second, independent hand-off. The
   aimed arm is now **not recommended** at all.
2. **The aimed arm makes D3 worse** (219 to 66 effective impacts), and its D3 ln Z moves by +0.33 nat. Its "both" target favours the
   start-up-offset pair. So one aimed proposal cannot serve D3 and D4 together.
3. **Children 64 meets (a) for D4 on this seed: 2,666 effective impacts** (base 252, 10.6x for 8x the descents). D3 rises only from 219
   to 494 (2.3x) and does not meet (a) per seed. Pooled over 8 waypoints seeds, it would be about 4,000, if the seeds are independent.
4. **(c):** children 64 moves D4 ln Z by −0.06 and D3 by +0.15 against a base of 219 effective impacts. That is consistent with base noise.
5. **Production recipe on run J:** D4 base is 252 here, against 32 on run-I repro. The run-I repro base was therefore not typical of
   the dominant stratum.

**Plan (approved by Pete about 03:40Z on 16 Oct, to run after run J finishes): the supplementary pass.**
- 224 extra descents per parent, scored for the both-burst cells (D3, D4, D5, plus the inflated-sd companion).
- Production 32-descent pass unchanged.
- Storage: a weighted resample per both-burst cell (systematic resampling to a fixed row count), not the full rows. A full children-64
  compact file is 11 GB per waypoints seed (measured), so full storage is not possible inside core's 35 GiB budget.
- Proposed size: 8 waypoints seeds (about 4.2 h at 14 threads) plus 4 seeds in each other stratum (about 2-3 h, estimated from
  the run-I repro timings). Final size to be posted with the run-J hand-off landing times, under the heavy lock.

**Storage, built and tested (16 Oct 04:50Z): `engine/hypotheses/end-of-flight/smoke/both_burst_thin.py`.** It applies Poisson
(Horvitz-Thompson) thinning with inclusion probability pi = min(1, c x max over cells of the row's normalised cell weight), over r600/no-offset
(which covers D5), both/no-offset, both/startup-offset and both/inflated. Kept rows carry weight w/pi, every column is kept, and the
output is in the same compact layout. Tests on run J waypoints seed 1 (base arm, 3.2 M rows):
- At 300k rows kept, 263k rows have pi = 1 and every cell's ln Z, median latitude and A1 share are reproduced exactly.
- At an extreme 3,000 rows kept (40 thinning seeds), the means agree with the full values within 1.2 standard errors: D4 ln Z
  −21.9582 ± 0.0039 against −21.9629, and A1 0.0637 ± 0.0011 against 0.0638.
- **Normalisation (corrected 16 Oct 22:00Z):** ln Z from a thinned file must be normalised by `thinning.weight_sum_in` (the unthinned weight total), not by the sum of the stored weights, because rows with pi = 0 are dropped. The first version of the script's own `after` summary made this error (+2.157 nat on run-J waypoints seed 1; ESS and shares were unaffected). It is fixed, and seed 1's metadata is corrected.
- Planned target: 1 M rows per supplementary seed. Measured: 129 MB for 299,958 kept rows (about 450 bytes per row), so about 0.43 GB per seed and about 14 GB for 32 seeds. That is inside core's 35 GiB budget. [Corrected 16 Oct: first posted as 0.24 GB and 8 GB, from a column-count estimate rather than the measured file size.]

**Correction (17 Oct about 12:20Z).** The prior-recovery 'failures' of the aimed arm in sections 3 and 4b are within the ESS-scaled two-sample 95 % band (see `results/eof-run-j-waypoints-oct16/README.md` section 3c, item 3). They are Monte Carlo noise against a fixed 0.0030 standard that does not scale with ESS, not evidence of a biased correction. The choice of the unaimed pass stands on its other grounds.

## 5. COVERAGE
**(a) Feasible set.** The pair at 00:19:29.416 / 00:19:37.443 needs a vertical-speed change of about -9,400 to -9,800 ft/min in 8.0 s.
The 777-200ER can reach this in an uncontrolled spiral or push-over after flame-out (Boeing no-input traces; ATSB).
**(b) Model's reach.** The descent laws produce such pairs from almost any 00:11 parent; the parent ESS ceiling is 30k-122k of 100k
parents' worth (base, seed 1). This fix does not change the reach.
**(c) Proposal's coverage.** D3 and D4 are **estimable only at about 700-850 effective impacts per seed** under either fix (seed 1,
repro stratum). On run J waypoints seed 1, children 64 gives D4 2,666 and D3 494 (section 4b); D3 stays a per-seed gap. They remain a declared coverage gap at the production setting (D3 228, D4 32). The held-out
and R600 cells are well covered in base and brute force. Under the aimed arm the held-out cell falls to 100k effective impacts and R600
to 4,070. Families: A1, A2 and B controlled carry their shares within 0.001 in all arms; B uncontrolled (0.0011) has fewer than
1,000 effective impacts in the both-burst cells and is not estimable there. Bounds: aimed K = 8 is a sampling choice and the selection
correction is exact. No physical parameter bound is changed.

> The uncontrolled-arm dynamics are not calibrated: the Boeing leave-one-out gate failed in all
> three rounds. Impact energy, attitude, flight-path angle and energy-transfer duration from
> this arm are a labelled sensitivity on uncalibrated dynamics, not a physical prediction.

The both-burst cells depend on the uncontrolled-arm descent laws more than any other cell does.

Data: `both-burst-smoke-seed1.json` (this folder); script `engine/hypotheses/end-of-flight/smoke/both_burst_acceptance.py`.
