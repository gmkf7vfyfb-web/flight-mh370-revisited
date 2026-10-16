# Both-burst 00:19 cells (D3, D4): the descent-sampling fix, smoke on seed 1 — 16 Oct 2026

**Status: SMOKE, one seed, one stratum. Not evidence; do not quote.** Answers core's work request of 15 Oct 23:17Z
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

## 5. COVERAGE
**(a) Feasible set.** The pair at 00:19:29.416 / 00:19:37.443 needs a vertical-speed change of about -9,400 to -9,800 ft/min in 8.0 s.
The 777-200ER can reach this in an uncontrolled spiral or push-over after flame-out (Boeing no-input traces; ATSB).
**(b) Model's reach.** The descent laws produce such pairs from almost any 00:11 parent; the parent ESS ceiling is 30k-122k of 100k
parents' worth (base, seed 1). This fix does not change the reach.
**(c) Proposal's coverage.** D3 and D4 are **estimable only at about 700-850 effective impacts per seed** under either fix (seed 1,
repro stratum; other strata not run). They remain a declared coverage gap at the production setting (D3 228, D4 32). The held-out
and R600 cells are well covered in base and brute force. Under the aimed arm the held-out cell falls to 100k effective impacts and R600
to 4,070. Families: A1, A2 and B controlled carry their shares within 0.001 in all arms; B uncontrolled (0.0011) has fewer than
1,000 effective impacts in the both-burst cells and is not estimable there. Bounds: aimed K = 8 is a sampling choice and the selection
correction is exact. No physical parameter bound is changed.

> The uncontrolled-arm dynamics are not calibrated: the Boeing leave-one-out gate failed in all
> three rounds. Impact energy, attitude, flight-path angle and energy-transfer duration from
> this arm are a labelled sensitivity on uncalibrated dynamics, not a physical prediction.

The both-burst cells depend on the uncontrolled-arm descent laws more than any other cell does.

Data: `both-burst-smoke-seed1.json` (this folder); script `engine/hypotheses/end-of-flight/smoke/both_burst_acceptance.py`.
