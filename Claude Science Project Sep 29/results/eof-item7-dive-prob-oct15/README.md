# Item 7 — the dive probability: what is implemented, and the exact sweep over p (15 Oct 2026)

**Work order:** section 1, Task A of `threads/work-orders/work-order-2026-10-15.md`. No run: every number here is an exact re-weighting of the stored run-i-dive sample (`latent:pushover_to_surface`), 127,999,840 impacts, 4 strata x 8 seeds.

> The uncontrolled-arm dynamics are not calibrated: the Boeing leave-one-out gate failed in all
> three rounds. Impact energy, attitude, flight-path angle and energy-transfer duration from
> this arm are a labelled sensitivity on uncalibrated dynamics, not a physical prediction.

## 1. What the code does

`profile.rs::draw_pushover_phase` draws the branch once per descent, `uniform() < pushover_to_surface_probability` (configured 0.5 in `full/dive-branch.toml`), and contributes **no** term to the stored importance weight; the branch is recorded in `latent:pushover_to_surface`. So the stored sample is a proposal at 0.5 and any fixed dive probability p is recovered exactly by the row factor 2p (continued to the sea), 2(1-p) (levelled off at the transition altitude), 1 (no push-over drawn). At p = 0.5 the factor is identically 1, so the p = 0.5 column below **is** the stored run-i-dive result; that is the prior-recovery check for this re-weighting, and it holds by construction.

Measured over the full sample: 73,994,278 of 127,999,840 descents are push-over eligible, 40,384,997 drew a push-over, and 20,185,882 of those continued to the sea (0.4998 of draws).

## 2. The three readings of the prior are numerically the same, and that is a theorem, not a coincidence

The run note records a U[0,1] hyper-prior with marginal 0.5; the configuration holds a fixed 0.5. These are not two different answers for anything this stage reports:

- each descent draws the branch **once**, so the branch enters that row's weight **linearly** in p;
- integral over [0,1] of 2p dp = integral over [0,1] of 2(1-p) dp = 1, so averaging a per-parent hyper-prior over its own U[0,1] returns the p = 0.5 weights exactly, row by row;
- for a single global p with prior U[0,1] both the numerator and the marginal likelihood are affine in p, Z(p) = Z(0) + p[Z(1) - Z(0)], so the posterior-marginalised expectation is [N(0)+N(1)]/[Z(0)+Z(1)] = N(0.5)/Z(0.5) — again the p = 0.5 column.

**Consequence.** Fixed coin at 0.5, per-parent hyper-prior U[0,1], and one global p with prior U[0,1] marginalised over its posterior all give identical impact distributions, identical evidence and identical consumer inputs. No code change makes the reported numbers more correct, and the understated dispersion is not an error in any reported quantity.

What the fixed coin does understate is the **within-parent** dispersion of the dive share, which no product uses. Measured over all 3,199,938 parents that drew at least one push-over (mean 12.62 draws per parent): across-parent standard deviation of the dive share **0.1539**, against **0.1539** predicted for an independent coin at 0.5 and **0.3148** for a per-parent p ~ U[0,1] — a factor 2.05 at this number of draws per parent. This reproduces the work order's diagnostic (0.1140 / 0.1108 / 0.3025 at 20.4 draws per parent on its subsample) and confirms the implementation is the independent coin. It is a correct statement about the implementation and an immaterial one about the results.

## 3. The sweep over the dive probability (exact re-weighting, no new simulation)

Within-stratum normalised weights mixed with the core family prior 0.9982 / 0.0011 / 0.0004 / 0.0002 (`smoke/run_i_maps.py` convention). The loud decile is the share of weight above the 90th percentile of peak radiated power, the threshold fixed at 6.531e+10 W from the held-out baseline at p = 0.5, so the share moves with p. Flight-path angle is the magnitude at water contact; impact energy and peak radiated power come from the per-seed sidecar `tau90_v1.npz`, joined by row order. The 00:19 columns here are **data treatments only**: no survival factor and no competing-cause mixture, matching the hydroacoustic loud-tail convention (`loud_tail_ess.py`), so they are not the D-cell totals of the run note.

| 00:19 data | p | FPA < 10 deg | FPA 10-45 deg | FPA > 45 deg | loud decile | energy q05 (GJ) | energy q50 (GJ) | energy q95 (GJ) | effective impacts |
|---|---|---|---|---|---|---|---|---|---|
| held out (D0 data) | 0.00 | 0.8646 | **0.0354** | 0.1000 | 0.0799 | 0.35 | 1.05 | 10.70 | 6,661,470 |
| held out (D0 data) | 0.25 | 0.8010 | **0.0991** | 0.0999 | 0.0900 | 0.35 | 1.13 | 10.87 | 9,380,273 |
| held out (D0 data) | 0.50 | 0.7374 | **0.1628** | 0.0998 | 0.1000 | 0.35 | 1.23 | 10.98 | 10,835,961 |
| held out (D0 data) | 0.75 | 0.6739 | **0.2265** | 0.0997 | 0.1100 | 0.35 | 1.54 | 11.06 | 9,332,031 |
| held out (D0 data) | 1.00 | 0.6103 | **0.2902** | 0.0995 | 0.1201 | 0.35 | 2.27 | 11.13 | 6,612,480 |
| D2 R600 BTO + R600 BFO | 0.00 | 0.8455 | **0.0407** | 0.1138 | 0.0917 | 0.34 | 1.07 | 10.74 | 143,391 |
| D2 R600 BTO + R600 BFO | 0.25 | 0.8222 | **0.0613** | 0.1165 | 0.0978 | 0.34 | 1.10 | 10.83 | 198,660 |
| D2 R600 BTO + R600 BFO | 0.50 | 0.7978 | **0.0829** | 0.1193 | 0.1042 | 0.34 | 1.12 | 10.91 | 240,105 |
| D2 R600 BTO + R600 BFO | 0.75 | 0.7721 | **0.1056** | 0.1223 | 0.1110 | 0.34 | 1.16 | 10.97 | 220,161 |
| D2 R600 BTO + R600 BFO | 1.00 | 0.7450 | **0.1295** | 0.1254 | 0.1181 | 0.34 | 1.20 | 11.03 | 157,016 |
| D4 R600 BTO + both BFOs, Holland transient bias added | 0.00 | 0.9312 | **0.0393** | 0.0295 | 0.0201 | 0.45 | 1.01 | 5.19 | 2,922 |
| D4 R600 BTO + both BFOs, Holland transient bias added | 0.25 | 0.8222 | **0.1448** | 0.0331 | 0.0378 | 0.48 | 1.08 | 10.58 | 3,833 |
| D4 R600 BTO + both BFOs, Holland transient bias added | 0.50 | 0.6712 | **0.2907** | 0.0381 | 0.0622 | 0.54 | 1.18 | 10.94 | 5,942 |
| D4 R600 BTO + both BFOs, Holland transient bias added | 0.75 | 0.4485 | **0.5060** | 0.0454 | 0.0982 | 0.77 | 6.25 | 11.16 | 13,477 |
| D4 R600 BTO + both BFOs, Holland transient bias added | 1.00 | 0.0868 | **0.8558** | 0.0574 | 0.1567 | 1.19 | 10.18 | 11.35 | 34,218 |

**Read the D4 row block first.** Under the data treatment that drives the headline — R600 BTO with both 00:19 bursts, Holland transient bias added — the acoustically decisive 10-45 degree band share runs **0.0393 at p = 0 to 0.8558 at p = 1**, a factor of 21.8, and the median impact energy runs 1.01 to 10.18 GJ. With the 00:19 bursts held out the same band share runs 0.0354 to 0.2902 (factor 8.2), which is the figure the work order quotes. Every detectability and non-detection statement under D4 is therefore governed by this one number, far more strongly than the prior-side figure suggested.

Effective impacts rise with p under D4 (2,922 to 34,218) because a dive puts the aircraft in the water close to 00:19:37, where the R1200 geometry concentrates the likelihood, so the weights become less uneven.

## 4. Family shares and effective impacts against p (same weighting, data treatments only)

| 00:19 data | p | A1 | A2 | B controlled | B uncontrolled |
|---|---|---|---|---|---|
| held out (D0 data) | 0.00 | 0.1522 | 0.3157 | 0.5311 | 0.0009 |
| held out (D0 data) | 0.25 | 0.1522 | 0.3157 | 0.5312 | 0.0009 |
| held out (D0 data) | 0.50 | 0.1522 | 0.3157 | 0.5312 | 0.0009 |
| held out (D0 data) | 0.75 | 0.1522 | 0.3156 | 0.5313 | 0.0009 |
| held out (D0 data) | 1.00 | 0.1522 | 0.3156 | 0.5313 | 0.0009 |
| D2 R600 BTO + R600 BFO | 0.00 | 0.1595 | 0.2790 | 0.5606 | 0.0009 |
| D2 R600 BTO + R600 BFO | 0.25 | 0.1634 | 0.2769 | 0.5587 | 0.0009 |
| D2 R600 BTO + R600 BFO | 0.50 | 0.1675 | 0.2748 | 0.5567 | 0.0009 |
| D2 R600 BTO + R600 BFO | 0.75 | 0.1718 | 0.2726 | 0.5547 | 0.0009 |
| D2 R600 BTO + R600 BFO | 1.00 | 0.1763 | 0.2703 | 0.5524 | 0.0010 |
| D4 R600 BTO + both BFOs, Holland transient bias added | 0.00 | 0.0593 | 0.3198 | 0.6205 | 0.0004 |
| D4 R600 BTO + both BFOs, Holland transient bias added | 0.25 | 0.0689 | 0.3253 | 0.6054 | 0.0005 |
| D4 R600 BTO + both BFOs, Holland transient bias added | 0.50 | 0.0821 | 0.3329 | 0.5844 | 0.0005 |
| D4 R600 BTO + both BFOs, Holland transient bias added | 0.75 | 0.1017 | 0.3441 | 0.5536 | 0.0007 |
| D4 R600 BTO + both BFOs, Holland transient bias added | 1.00 | 0.1334 | 0.3623 | 0.5034 | 0.0009 |

Family shares are far less sensitive than the acoustic quantities: A1 moves 0.0593 to 0.1334 under D4 across the whole range of p, and not at all with the bursts held out.

### Effective impacts by family

| 00:19 data | p | A1 | A2 | B controlled | B uncontrolled |
|---|---|---|---|---|---|
| held out (D0 data) | 0.00 | 2,704,332 | 2,433,462 | 2,805,097 | 51,054 |
| held out (D0 data) | 0.25 | 2,704,332 | 3,536,822 | 4,039,588 | 51,054 |
| held out (D0 data) | 0.50 | 2,704,333 | 4,182,821 | 4,712,423 | 51,054 |
| held out (D0 data) | 0.75 | 2,704,333 | 3,571,069 | 3,993,040 | 51,054 |
| held out (D0 data) | 1.00 | 2,704,333 | 2,464,900 | 2,760,762 | 51,054 |
| D2 R600 BTO + R600 BFO | 0.00 | 77,133 | 43,125 | 64,957 | 1,251 |
| D2 R600 BTO + R600 BFO | 0.25 | 77,133 | 62,437 | 90,270 | 1,251 |
| D2 R600 BTO + R600 BFO | 0.50 | 77,134 | 83,360 | 107,095 | 1,251 |
| D2 R600 BTO + R600 BFO | 0.75 | 77,134 | 84,506 | 93,810 | 1,251 |
| D2 R600 BTO + R600 BFO | 1.00 | 77,134 | 61,020 | 64,010 | 1,251 |
| D4 R600 BTO + both BFOs, Holland transient bias added | 0.00 | 2,317 | 2,120 | 1,317 | 57 |
| D4 R600 BTO + both BFOs, Holland transient bias added | 0.25 | 2,317 | 2,883 | 1,650 | 57 |
| D4 R600 BTO + both BFOs, Holland transient bias added | 0.50 | 2,317 | 4,668 | 2,411 | 57 |
| D4 R600 BTO + both BFOs, Holland transient bias added | 0.75 | 2,317 | 10,741 | 5,220 | 57 |
| D4 R600 BTO + both BFOs, Holland transient bias added | 1.00 | 2,318 | 19,809 | 16,999 | 57 |

**The dive branch acts only on the piloted families.** A push-over is a piloted manoeuvre, so A1 (fuel exhaustion with no intervention) and B uncontrolled have zero push-over eligibility and identical effective impacts at every p; 65.1 per cent of A2 and 70.1 per cent of B-controlled descents are eligible and 34.0 and 39.2 per cent drew one. The family shares move with p only because the mass of A2 and B controlled moves. Every family cell stays above the 1,000-impact gate except B uncontrolled under D4 (57 effective impacts at every p), which is a standing gap of run-i-dive and is not made better or worse by this task.

## 5. How well the data identify p

| 00:19 data | ln Z(p=0) | ln Z(p=1) | range, nat | posterior mean of p, prior U[0,1] |
|---|---|---|---|---|
| held out (D0 data) | -0.0000 | -0.0002 | -0.0001 | 0.500 |
| D2 R600 BTO + R600 BFO | -12.5277 | -12.6279 | -0.1002 | 0.492 |
| D4 R600 BTO + both BFOs, Holland transient bias added | -21.7540 | -22.5640 | -0.8100 | 0.436 |

Z(p) is affine in p, so these two end points determine the whole curve and the posterior over a global p is a linear density on [0,1]. The data **mildly disfavour** the dive: the whole range of p is worth 0.81 nat under D4 and 0.10 nat under D2, which is weak evidence by any convention, while the band share it controls moves by a factor of 21.8. **p is close to unidentified and the acoustic statements are prior-dominated.** That, and not the implementation, is the finding of item 7.

## 6. Prior-recovery check

Test 6 is the aimed-proposal check (`results/eof-gates-oct13`, mean stored correction 1.0004 +/- 0.0013, maximum weighted-CDF deviation <= 0.0070). Nothing in this task changes the proposal, the sampler or any binary, so test 6 is untouched and still passes as recorded. The re-weighting's own recovery check is the identity above: the factor is 1 at p = 0.5 for every row, and the p = 0.5 column reproduces the stored sample exactly.

## 7. COVERAGE

**(a) Feasible set.** A piloted emergency descent in a 777-200ER may be levelled off at a breathable altitude or continued to the water; both are inside the flight envelope and both are in the feasible set. The dive probability is a statement about intent, not about the aircraft, so the feasible set does not bound it: the whole of [0,1] is feasible.
**(b) Model's reach.** Both branches are reachable: 20,185,882 impacts continue the push-over to the sea and 20,199,115 level off. Declared reach limits are unchanged from run-i-dive (stepped shapes not push-over eligible; INTERIM parametric pitch-down; no transonic drag rise; turn model PROVISIONAL).
**(c) Proposal's coverage.** The proposal is the coin at 0.5, which covers both branches with half the sample each, so every p in [0,1] is estimable from the same sample set by exact re-weighting. The effective impacts in the table are the coverage statistic: the worst cell is D4 at p = 0 with 2,922 effective impacts, above the 1,000 gate. The weight bound is 2, at p = 0 and p = 1, which is why no cell collapses.
**Gaps.** None introduced here. The standing gaps of run-i-dive carry over unchanged.

## 8. For Pete to rule

The work order asks whether the intended model is a per-parent hyper-prior or a fixed coin, and says to flag it rather than choose. The measured answer is that **the choice does not change any reported number** (section 2), so the ruling that matters is a different one:

1. **Report at p = 0.5 and carry the table above as the declared sensitivity** (recommended). This is what all three readings of the prior give, and it keeps one headline rather than five.
2. **Report at a different p**, for example a lower dive probability on the grounds that a pilot who descends to a breathable altitude has a reason to stop there. This is a prior change and needs a source or a stated argument.
3. **Report the acoustic quantities as a function of p only**, with no headline value, because the evidence moves p by 0.81 nat at most while the band share moves by a factor of 21.8.

The module's recommendation is 1 with the table attached to every acoustic product, and the sentence "the dive probability is prior-dominated" in the paper's limitations.

---

Footnote (ASD-STE100). The numbers come from the stored run-i-dive sample. We changed no code and we did no new run. We gave each impact a new weight for each value of the dive probability p: 2p if the aircraft continued the push-over to the water, 2(1-p) if it levelled off, 1 if it made no push-over. The descent physics is not calibrated, so you must not use the energy, the angle or the duration as a prediction.

Footnote (technical). Source posterior and prior track: core run I m0011 hand-offs, end of flight run-i-dive (binary mh370-eof-ri3, sha256 2e60b0e2...), 4 strata x 8 seeds, 127,999,840 impacts, strata mixed at the core family prior 0.9982 / 0.0011 / 0.0004 / 0.0002. 00:19 data options D0 / D2 / D4 as loglik columns only, no survival factor and no competing-cause mixture (q = 1/3, W = 3,898 s not applied here), so these are not the run note's D-cell totals. Dive branch re-weighted exactly from `latent:pushover_to_surface`; proposal 0.5; weight bound 2. Impact energy, peak radiated power and tau90 from the `tau90_v1.npz` sidecar, joined by row order; the impact table's own energy columns are non-finite. Loud-decile threshold 6.531e+10 W, fixed at the held-out p = 0.5 baseline. Core run I is NOT CONVERGED (all-partition split-half 0.916 waypoints, 0.830 free flight, against the 8-replicate floor 0.924); run-i-dive supersedes run I and the two are different priors, never pooled. Uncontrolled-arm dynamics NOT CALIBRATED (Boeing leave-one-out gate failed in all three rounds).
