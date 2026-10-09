# End of flight: the two 00:19 bursts - evidence, survivors, and the stopgap proposal (9 Oct 2026)

End of Flight Module. Inputs: the **reference-289 full sweep** (`runs/eof-289-full-s1..s4`, core hand-off
`reference-289`, 100,000 parents per seed, N = 8 children x 4 descents, 4 seeds, 12.8 M descents; impacts
sha256 in `results/eof-289-sweep-oct09/README.md`) for sections 1-3, and **smoke runs** (seed 1,
N = 1 child x 4 descents) for section 4. Section 4 is not evidence and must not be quoted as such.

## Summary

1. **Holland H1 against H2 is estimable as evidence even where neither posterior is.** Scoring both
   00:19 bursts with log-on cause `other`, ln BF(H1:H2) = **-0.34**, sd 0.10 over four independent seeds
   (BF 0.71), although `both/no-offset` has only about 20 effective parents per seed. With the R600 burst alone
   the data favour H2 at ln BF = -1.68 (BF about 1:5.4), sd 0.06. With fuel-exhaustion as the log-on cause the
   two-burst comparison is **not converged** (per seed -0.76 to +0.69).
2. **The parents that carry Holland's arms are interior to the descent prior.** Loss of control 0-160 s
   before 00:19:29, descent rates 19-57 kft/min against a 65 kft/min maximum, and interior Mach, spiral
   doubling time and L/D. Two edges are enriched and disclosed: the core's 25,000 ft hand-off altitude floor
   (5-9% of posterior weight against 1.1% of prior) and the module's 90 deg point-mass spiral bank cap
   (16-32%). The 6-DOF simulator removes the second. The concentration is mostly a real inference about the
   00:19 pair given the 00:11 sample, not clipping.
3. **The stopgap proposal is implemented, exact, and off by default (byte-identical), but it should not be
   used.** (a) Holland's arms are parent-limited (effective impacts = effective parents), so no
   terminal-stage proposal can lift them. This agrees with Searched Areas (~22:35 entry) and with
   `results/eof-ess-limit-oct09/` addendum 2. (b) Core self-normalises each parent's weights over its
   own descents. Under a varying proposal correction that ratio estimator is biased: on the smoke it raised ln Z
   by 0.28 on R1200 and 0.56 on `both/inflated`. Core request 15 asks for an unnormalised option.
4. **The remedy for the Holland arms is upstream**: a look-ahead resampling of the 00:11 hand-off
   (Searched Areas' item iii), filed as core request 16.

## 0. Pete's H1 and H2 differ in log-on cause too (added after architecture ~19:50)

Pete's priorities define H1 = `startup-offset` x fuel-exhaustion and H2 = `no-offset` x other. `other` has no
log-on-time likelihood, so their Bayes factor needs a declared density of the log-on time under `other`. With a uniform density over W s:
ln BF(H1:H2) = ln Z(H1) - ln Z(H2) + ln W. ln Z(H1) - ln Z(H2) is -7.48 for both bursts (sd 0.23 over seeds), -7.63 for R600 (sd 0.15) and
-6.75 for R1200 (sd 0.03). Break-even W is 1,775 s, 2,062 s and 852 s respectively; for both bursts ln BF is -2.69 at W = 120 s,
-1.08 at 600 s and +0.71 at 3,600 s. The sign of the Pete-defined comparison is set by W, which is a modelling choice
(`holland-h1-fuel-vs-h2-other.json`). The within-cause Bayes factors in section 1 do not depend on W.

## 1. Evidence per option (architecture fix 2: effective parents / impacts / top-100 share per option)

ln Z = ln sum_i w_i L_i over the seed. w is the hand-off posterior through 00:11 times the within-parent proposal correction, normalised
over the seed. L is the 00:19 likelihood of the option, times the section 6 lag density for fuel-exhaustion. Z is the predictive probability of the 00:19 data
given the cruise data. **Only options scoring the same data are comparable.** Different burst sets are not,
and neither are the two log-on causes, because `other` has no log-on likelihood (absolute_scale false). Pooled
= ln of the mean of Z over seeds. sd = across the four seeds. boot s.e. = mean parent-bootstrap s.e.
within a seed; it understates the error when the top-10 parent share is near 1. Per-seed values are in
`option-evidence-reference-289.json`. `r600-bto` and `both-bto` are derived from the run's own BTO residual columns
(architecture fix 3; definition in `smoke/displacement_hist.py`; exact decomposition checked, max
residual 7e-10).

| option x cause | ln Z pooled | sd seeds | boot s.e. | eff. parents / seed | eff. impacts / seed | top-100 share | top-10 share |
|---|---|---|---|---|---|---|---|
| `none__other` | 0.00 | 0.00 | 0.00 | 100,000 | 3,089,700 | 0.00 | 0.00 |
| `none__fuel-exhaustion` | -7.40 | 0.05 | 0.01 | 20,738 | 267,294 | 0.01 | 0.00 |
| `r600_inflated__other` | -11.79 | 0.03 | 0.00 | 62,675 | 763,833 | 0.01 | 0.00 |
| `r600_inflated__fuel-exhaustion` | -18.52 | 0.06 | 0.01 | 13,190 | 100,663 | 0.03 | 0.00 |
| `r600_no-offset__other` | -12.71 | 0.03 | 0.01 | 18,616 | 49,392 | 0.02 | 0.00 |
| `r600_no-offset__fuel-exhaustion` | -18.87 | 0.05 | 0.01 | 6,082 | 14,878 | 0.05 | 0.01 |
| `r600_startup-offset__other` | -14.38 | 0.06 | 0.01 | 12,218 | 43,392 | 0.03 | 0.00 |
| `r600_startup-offset__fuel-exhaustion` | -20.34 | 0.16 | 0.01 | 4,214 | 16,899 | 0.07 | 0.01 |
| `r1200_inflated__other` | -10.02 | 0.03 | 0.01 | 10,884 | 17,270 | 0.04 | 0.01 |
| `r1200_inflated__fuel-exhaustion` | -16.22 | 0.06 | 0.02 | 2,752 | 4,876 | 0.10 | 0.02 |
| `r1200_no-offset__other` | -10.09 | 0.04 | 0.02 | 2,901 | 3,379 | 0.08 | 0.01 |
| `r1200_no-offset__fuel-exhaustion` | -16.31 | 0.06 | 0.04 | 773 | 920 | 0.23 | 0.04 |
| `r1200_startup-offset__other` | -10.61 | 0.03 | 0.01 | 7,385 | 9,457 | 0.04 | 0.01 |
| `r1200_startup-offset__fuel-exhaustion` | -16.84 | 0.06 | 0.02 | 1,983 | 2,516 | 0.11 | 0.02 |
| `both_inflated__other` | -23.14 | 0.08 | 0.04 | 678 | 1,196 | 0.28 | 0.07 |
| `both_inflated__fuel-exhaustion` | -29.34 | 0.12 | 0.06 | 237 | 511 | 0.49 | 0.14 |
| `both_no-offset__other` | -23.93 | 0.16 | 0.21 | 20 | 21 | 1.00 | 0.62 |
| `both_no-offset__fuel-exhaustion` | -30.99 | 1.08 | 0.63 | 4 | 5 | 1.00 | 0.96 |
| `both_startup-offset__other` | -24.27 | 0.09 | 0.12 | 78 | 80 | 0.92 | 0.23 |
| `both_startup-offset__fuel-exhaustion` | -31.41 | 0.33 | 0.38 | 8 | 9 | 1.00 | 0.87 |
| `r600-bto__other` | -5.89 | 0.02 | 0.00 | 71,480 | 1,617,760 | 0.00 | 0.00 |
| `r600-bto__fuel-exhaustion` | -13.11 | 0.06 | 0.01 | 14,299 | 167,589 | 0.02 | 0.00 |
| `both-bto__other` | -11.06 | 0.03 | 0.00 | 57,251 | 1,158,619 | 0.00 | 0.00 |
| `both-bto__fuel-exhaustion` | -18.28 | 0.06 | 0.01 | 12,119 | 119,296 | 0.03 | 0.00 |

### Holland H1 (startup-offset) against H2 (no-offset), same data

| bursts | log-on cause | ln BF H1:H2 | BF | per seed | sd |
|---|---|---|---|---|---|
| r600 | other | -1.68 | 0.19 | -1.68, -1.61, -1.66, -1.76 | 0.06 |
| r600 | fuel-exhaustion | -1.47 | 0.23 | -1.54, -1.29, -1.51, -1.57 | 0.13 |
| r1200 | other | -0.52 | 0.60 | -0.51, -0.52, -0.53, -0.50 | 0.01 |
| r1200 | fuel-exhaustion | -0.53 | 0.59 | -0.58, -0.51, -0.53, -0.49 | 0.04 |
| both | other | -0.34 | 0.71 | -0.46, -0.34, -0.34, -0.21 | 0.10 |
| both | fuel-exhaustion | -0.42 | 0.66 | -0.72, +0.51, -0.76, +0.69 | 0.78 |

Reading: |ln BF| < 1 is weak on the usual scale, so the data do not separate H1 from H2 once both bursts or the
R1200 burst are used. R600 alone favours H2 moderately. The H1 evidence integrates over Holland's offset
densities (uniform 17-130 Hz and 0-6 Hz, an analyst choice per `config/integrated.toml`), so it carries an
Occam factor set by those widths, and the Bayes factor moves if they do. The fuel-exhaustion two-burst line
is unconverged and is reported as such.

## 2. Survivor diagnosis (Searched Areas' item ii)

`survivor-diagnosis-reference-289.json`: posterior 5/50/95% of each latent over the top 400 rows per seed,
against the prior (hand-off-weighted) 1/50/99% and range. Two-burst arms, cause `other`:

| quantity | prior min / q50 / max | H2 (no-offset) 5/50/95 | H1 (startup-offset) 5/50/95 |
|---|---|---|---|
| loss of control - 00:19:29.416, s | -510 / +7 / +5,965 | -162 / -40 / +3 | -154 / -42 / -3 |
| max descent rate, ft/min | 1,066 / 6,934 / 64,729 | 18,889 / 22,851 / 51,401 | 20,591 / 28,042 / 56,763 |
| max Mach | 0.7 / 0.8 / 1.1 | 0.8 / 0.8 / 1.0 | 0.8 / 0.9 / 1.0 |
| spiral doubling, s | 60 / 90 / 120 | 63 / 89 / 118 | 62 / 84 / 117 |
| impact bank, deg (cap 90) | 0 / 3.6 / 90 | 0 / 24 / 90 | 3 / 79 / 90 |
| hand-off altitude, ft | 25,000 / 37,000 / 43,000 | 25,000 / 37,000 / 43,000 | 25,000 / 38,000 / 43,000 |

Edge shares (posterior weight): hand-off altitude at the 25,000 ft floor 0.086 (H2), 0.053 (H1), 0.102
(`both/inflated`), against 0.011 under the prior. Bank at the 90 deg cap: 0.16, 0.32 and 0.17. Mach >= 1.05: at most 0.02.

## 3. What the 00:19 pair is saying

The surviving descents lose control about 40 s before the R600 log-on and are in a 20-30 kft/min descent at
00:19:37. That is the same picture as the R1200 BFO alone, now with the R600 BTO/BFO consistent with it from a
handful of 00:11 states. Holland's hypotheses differ mainly in bank at impact (H1 median 79 deg, H2 24 deg),
which is a point-mass-spiral output and will be re-read on the 6-DOF fast model.

## 4. Stopgap two-burst proposal (smoke, not evidence)

Implemented in `lib.rs` (`ProposalParams`, `pick_control`) and `profile.rs` (`LossWindow`,
`draw_loss_after`), with the overlay at `hypotheses/end-of-flight/full/two-burst-proposal.toml`. The design:
- the control draw q = (1 - a) p + a 1{maintained-then-lost}, a = 0.4;
- a defensive mixture on the loss delay, weight 0.75 uniform on the absolute window
  [00:19:29.416 - 260 s, + 5 s] and 0.25 on the prior U[30, 1800] s;
- each draw corrected exactly by ln(prior/proposal) in `Descent::log_q_correction`.

Checks:
- Defaults are **byte-identical** to the reference-289 build (impacts sha256 68ee1469...).
- Two unit tests: E[exp lq] = 1 for both components, the boost-0 draw equals `pick`, and an out-of-support window falls back to the prior. The suite now has 94 tests.
- Core's proposal_self_check on the smoke: mean correction **1.0005 +- 0.0013**.

| arm (cause) | ESS prior | ESS proposal | gain | eff. parents prior | eff. parents proposal |
|---|---|---|---|---|---|
| `r1200_inflated__other` | 2,166 | 2,215 | 1.0 | 1,966 | 2,039 |
| `r1200_inflated__fuel-exhaustion` | 565 | 386 | 0.7 | 460 | 340 |
| `r1200_no-offset__other` | 430 | 406 | 0.9 | 412 | 402 |
| `r1200_no-offset__fuel-exhaustion` | 103 | 69 | 0.7 | 89 | 68 |
| `r1200_startup-offset__other` | 1,185 | 1,265 | 1.1 | 1,130 | 1,182 |
| `r1200_startup-offset__fuel-exhaustion` | 317 | 220 | 0.7 | 298 | 213 |
| `both_inflated__other` | 144 | 327 | 2.3 | 126 | 296 |
| `both_inflated__fuel-exhaustion` | 40 | 70 | 1.7 | 30 | 59 |
| `both_no-offset__other` | 3 | 29 | 9.3 | 3 | 29 |
| `both_no-offset__fuel-exhaustion` | 2 | 3 | 2.1 | 2 | 3 |
| `both_startup-offset__other` | 10 | 35 | 3.4 | 10 | 35 |
| `both_startup-offset__fuel-exhaustion` | 2 | 3 | 1.5 | 2 | 3 |

The gains (x2-9 on the two-burst `other` arms) come with the self-normalisation bias described in Summary 3(b).
Recomputing the smoke's weights unnormalised (W_parent exp(q)/n) recovers the prior-sampled ln Z to 0.01-0.03 on every
converged arm: R1200 inflated -10.055 against -10.047, `both/inflated` -23.209 against -23.198.
On the existing reference-289 runs the bias is negligible (<= 0.01 in ln Z): the takeover correction is mild
(sd 0.19), so no published number changes.

**Not run at full scale.** It would cost about 18 GB and 2 h, the estimator is biased under core's present
normalisation, and the arms it was meant for are parent-limited. Redo after core request 15, and on the
6-DOF fast model as Pete ruled ("Stopgap now, then redo").

## Reproduce

    PYTHONPATH=hypotheses/end-of-flight/smoke python3 hypotheses/end-of-flight/smoke/option_evidence.py OUT.json runs/eof-289-full-s1 runs/eof-289-full-s2 runs/eof-289-full-s3 runs/eof-289-full-s4

Survivor diagnosis: `PYTHONPATH=hypotheses/end-of-flight/smoke python3 hypotheses/end-of-flight/smoke/survivor_diagnosis.py` from `engine/` (writes /tmp/survivors.json). The smoke uses
`full/reference-289.toml full/seed-1.toml` plus a `[terminal] children = 1` overlay, with and without
`full/two-burst-proposal.toml`.
