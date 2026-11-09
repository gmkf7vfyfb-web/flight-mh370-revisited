# Independent review: drift level-prior correction of 9 November 2026

Reviewer: independent adversarial review (delegated). Date: 9 November 2026.
Object of review: `results/drift/drift-level-prior-correction-2026-11-09/README.md` (branch `claude-science-sep29`, commit 1baf301) and its four tables.
Method: own scorer written from `lib.rs` (`node_ln_likelihood_zeros`) and `recovery.rs` (`LevelDraws`, `dot`) on branch `hypothesis/debris-drift` (6f75971);
own ledger, tension and map code. The other agent's scripts were read only after the reviewer's numbers existed, and only to locate the causes of disagreement.

## Summary

- The defect in the 8 November rescoring is real. The rescore metadata set the detection-level period means to 0 in all periods.
- The offline scorer is correct. My own scorer reproduces the module node table at all 84 points and both ocean models to 5e-7.
- The headline numbers are reproduced exactly, but only with the other agent's level-draw seed (31) and its interpolation.
- With other seeds at 16,384 draws, the shift of the mean is +0.75° to +1.09° (8 seeds; mean +0.92°, SD 0.12°). The reported +0.82° is near the low end.
- The 1-D drift profile uses `np.interp` on node latitude. It mixes points on the arc with points 50 NM inside and outside. 14 latitudes are tied, so the result depends on sort order.
- The tension statistic is not robust. Over seeds and interpolation choices, p is 0.049 to 0.105 (1.6 to 2.0 standard deviations). Over disjoint ocean-sample subsets, p is 0.019 to 0.23.
- The October-versus-November agreement claim (C6) is wrong as stated. The like-for-like November calculation gives a drift-alone median of 31.35° S, not about 30° S.
- The fit-versus-prior-volume arithmetic (C5) is correct. The inference that the 36–38° S peak comes "not from the satellite measurements" is not sound.
- "Agrees with most published drift studies" is not supported. CSIRO (Griffin and Oke 2017) gave 35.6° S as the most likely location.

## Verdicts

| Claim | Verdict | Claimed | Reviewer value |
|---|---|---|---|
| C1 defect; ramp is the module prior | Confirmed with qualification | R1–R4 means 0; module ramp ln 0.1 / ln 0.5 / 0 | R1–R4 metadata: `ln_mean_by_period` all 0, `mu_primary` all 0. Module (7 Nov and extended runs, all production configs since 8 Oct, commit 4993171): ramp [−2.302585, −0.693147, 0]. Ramp is labelled "PROVISIONAL pending the architect's values"; "pre-registered" in the configs refers to Australian option B, not to the ramp |
| C2 scorer reproduces `ln_l_lev_off` | Confirmed | ~1e-6 at 84 points × 2 models | Max abs deviation 4.98e-7 (GlobCurrent), 4.90e-7 (GLORYS12); also `ln_l` (option B) 4.96e-7; extended module run 252 node rows 4.97e-7. Flat-minus-ramp mean −2.842 / −2.695 (identical to claimed) |
| C3 drift alone, headline | Confirmed with qualification | median −30.29, mean −30.57, 5–95 % −36.37 to −25.15, N33 75 %, lnR −0.57, lnS −1.39, d 1.63, p 0.078 | Exact reproduction with seed 31 and their interpolation: mean −30.568, p05 −36.376, N33 74.93 %, lnR −0.573, lnS −1.387, d 1.628, p 0.078. Over 10 draw seeds: median −30.11 to −30.52, N33 72.6–79.4 %, lnS −1.21 to −1.70, p 0.073–0.105. Over interpolation choices: N33 75–86 %, lnS −1.51 to −2.28, p 0.049–0.079. Ocean-sample quarters: median −29.1 to −31.6, p 0.019–0.23 |
| C3 nine finds only | Confirmed | median −30.02 | −30.05 (their method, seed 31); −30.10 / −30.22 (my mappings) |
| C4 combined shift | Confirmed with qualification | +0.82° (−36.72 → −35.90); constant in time −0.15° | Seed 31: +0.825° (mean −35.89, median −36.69, 5–95 % −38.13 to −30.47, N33 8.57 %). 8 seeds at 16,384 draws: +0.75 to +1.09 (mean +0.92, SD 0.12); 65,536 draws: +0.98, +0.90. Constant in time: −0.13° |
| C5 fit nearly flat; prior volume ~120× | Arithmetic confirmed; inference not sound | median −31.25; ~120× (36–420) | Ratio 117× (36–419). Δχ² 0–2.54 confirmed. Fit-only median −31.25 is reproduced only with each family normalised to its own best χ²; with the best χ² per band (as described): median −30.58, mean −29.73, N33 66 % |
| C6 October agrees with November | Wrong as stated | same configuration; October median ~30.0–30.4 agrees | Configuration identity confirmed (only particles, seeds, environment seeds, output switches, node subset differ; code changes in between are output-only). Like-for-like 7 Nov run, same window and finds: median −30.78 (module 256 draws), −31.35 (16,384 draws) vs October −29.97; N33 68 % / 62 % vs 77 %; core shift +0.75 / +0.57 vs +1.01 |
| C7 interpretation | Not supported as stated | mild 1.8σ; agrees with most drift studies; defensible | Tension 1.6–2.0σ (seeds, mappings) and 1.2–2.3σ (ocean-sample quarters); depends on unruled choices. CSIRO most likely 35.6° S (2017); debris-only CSIRO estimate 36–32.5° S (Dec 2016). Not yet defensible: see defects 1–8 |

## C1. The defect and the reference prior

The four rescore metadata files (`rescore/cfg/R1…R4-meta.json`) carry `ln_mean_by_period` = [0, 0, 0] or [0, 0, 0, 0] and every entry of `mu_primary` = 0.
The module metadata of the 7 November run (`conv-*-coefficients-meta.json`) and the extended run (`ext*-coefficients-meta.json`) carry [−2.302585, −0.693147, 0.0], and the module node-table column `ln_l_lev_off` is scored with that ramp plus Australian segments at −30 (alternative `off`). So the defect is confirmed.

The ramp entered the module on 8 October 2026 (commit 4993171, before any production result) and is in every production and run configuration since. Its config comment reads "G1 level prior, PROVISIONAL pending the architect's values". The word "PRE-REGISTERED" in the configs (Pete, 12 October) applies to the Australian option B, which is the module's primary `ln_l`. The ramp is therefore the correct reference for reproducing the module, but it is a provisional default, not a ruling, and the README's "pre-registered in the module" is an overstatement for the ramp. It is also the single largest lever on the result: the same headline with detection constant in time gives −0.13° (reviewer) instead of +0.8° to +1.1°.

Qualification on the README's "new-coast tiers are offsets on the ramp": true for the new western Indian Ocean coasts. The Australian ruled tiers in the other agent's scorer (`ruled_au`) are absolute and constant in time. They are therefore 10 times the find-coast level in the first period at ratio 1. Scored as offsets on the ramp, the Australia sensitivities move the mean +1.13° (ratio 0.25) and +1.46° (ratio 1). Scored as absolute values, they move it +1.57° and +2.42° (reviewer, one seed) against the claimed +1.72° and +2.68°.

## C2. Scorer against the module

The reviewer's scorer computes, for each node, ln mean over (environment, draw) of exp(Σ_c Σ_{j∈c} [ln(a_j·ν_seg(j)) − ln(A_c·ν)]), with ν = exp(μ + σz) and the module's own z from the metadata. Against the 7 November node tables (84 points, 16 environments, 256 draws), the maximum absolute deviation is 4.98e-7 (GlobCurrent) and 4.90e-7 (GLORYS12) for `ln_l_lev_off`, and 4.96e-7 for `ln_l` (option B). This is the six-decimal rounding of the node table. The same scorer matches the extended module run (252 node rows, including the 32-sample southern points) to 4.97e-7. The rescore coefficients of R4 agree with the extended module coefficients after summing periods 3 and 4 (relative deviation ≤ 2.2e-8). With the flat prior, the log-likelihood is lower by 2.842 (GlobCurrent) and 2.695 (GLORYS12) on average, by 4.57 / 4.07 north of 33° S and 1.20 / 1.38 to the south. Table: `rv-c2-node-check-84x2.csv`.

## C3. Drift alone and tension

Exact reproduction requires three of the other agent's choices: level draws from `numpy.default_rng(31)`; a draw-dependent unrelated-debris background b_j(d) (the core-weighted average over points and ocean samples of the item's term at each draw); and the 1-D curve `np.interp(ledger latitude, node latitude, L)` over all 84 points sorted by node latitude. With these, my code returns mean −30.568, N33 74.93 %, lnR −0.573, lnS −1.387, d 1.628, p 0.078, σ 1.761, equal to the claim (`rv-c3-exact-reproduction-seed31.csv`). My tension code reproduces the October ledger values (lnR −0.725, lnS −1.485, p 0.067), so the Handley and Lemos implementation is consistent.

Robustness (`rv-c3c4-level-draw-seed-study.csv`, `rv-c3-drift-alone-by-mapping.csv`, `rv-c3-environment-quarter-subsets.csv`):

| Source of variation | Median (° S) | N of 33° S | ln S | p |
|---|---|---|---|---|
| Level-draw seed (8 × 16,384 and 2 × 65,536 draws; their interpolation) | 30.11–30.52 | 72.6–79.4 % | −1.21 to −1.70 | 0.073–0.105 |
| Tie order in `np.interp` (seed 31) | 30.35 / 30.47 / 30.63 | 74.9 / 73.7 / 71.9 % | −1.39 / −1.29 / −1.36 | 0.078 / 0.097 / 0.088 |
| Interpolation choice (three-point mean, six-point inverse distance, track only) | 30.11–30.28 | 74.9–85.8 % | −1.51 to −2.28 | 0.049–0.079 |
| Disjoint ocean-sample quarters (4 of 16 north, 8 of 32 south) | 29.10–31.64 | 55–93 % | −0.30 to −3.50 | 0.019–0.23 |

The median of about 30.3° S is robust to the scorer choices. The tail measures and the tension statistic are not. "p 0.078 (1.8σ)" should be quoted as a range (about 1.6–2.0σ from the level draws and interpolation alone) with the ocean-sample uncertainty stated, and labelled provisional. The README's remark that "by analogy its drift-alone median may be uncertain by about ±2°" is too pessimistic for the median of the headline (quarter subsets span 2.5°; the full set has roughly half that spread), but is about right for N33 and ln S.

Nine finds only (same variant, no mixture): −30.05 with their method and seed (claimed −30.02, a quantile-convention difference); −30.10 / −30.22 with my mappings.

## C4. Combination with the core

The core map H_D0_all gives mean −36.717 (cell centres), median −37.13. With seed 31 and the draw-dependent background, the headline gives mean −35.89, median −36.69, 5–95 % −38.13 to −30.47, N33 8.57 %, shift +0.825°: exact reproduction. Eight seeds at 16,384 draws give +0.752 to +1.085 (mean +0.917, SD 0.116); two seeds at 65,536 draws give +0.975 and +0.900. The 8 November statement, carried into this correction, that 16,384 draws converge to about 0.05° is false. The draw estimator is dominated by few terms: the Kish effective sample size of the (ocean sample × draw) terms per point has median 416 (GlobCurrent) and 256 (GLORYS12), minimum 39, out of 262,144–524,288 terms (`rv-level-draw-ess-by-node.csv`). The best present estimate of the headline shift is about +0.9° ± 0.1° (level draws only), plus the unassessed ocean-sample error.

Other rows (one seed, constant background; `rv-c4-core-combination-shifts.csv`): module run nine finds +0.64 (claimed +0.66); detection constant in time −0.13 (−0.15); without Mossel Bay +0.24 (+0.22); Mossel Bay only +1.64 (+1.61); other coasts at the find level +1.48 (+1.36), at 0.1 +0.65 (+0.60); GlobCurrent only +0.96 (+0.78); GLORYS12 only +2.54 (+2.35); all four periods and coasts, nine finds +0.67 (+0.76). Differences of 0.1–0.2° are within the level-draw scatter. The Australia rows differ because of the absolute-versus-offset tier definition (C1).

The three extra items each move the mean north: nine finds +0.68; plus Linga Linga +0.72; plus Nautilus Bay +0.81; plus Mpame +0.89. Nautilus Bay and Mpame have `identity_uses_prior_drift = unclear` in the evidence audit, but the headline treats them as non-circular.

## C5. Satellite fit against prior volume

Arithmetic (`rv-c5-fit-profile-bands.csv`): mean ratio of posterior to fit, 35.75–37.75° S against 29.75–31.75° S, 117 (band by band 36–419); claimed about 120 (36–420). Δχ² of the best trajectory per band within the 20–40° S range is 0 to 2.54 between 37.75° and 23.75° S, and 10.38 at 39.75° S. The overall best band of the profile is at 16.75° S, outside the drift span.

The "satellite fit only" curve in the table (median −31.25, N33 61.6 %) is reproduced only by summing exp(−Δχ²_f/2) over families with each family normalised to its own best χ² (`delta_vs_family_best`). That discards the χ² differences between families and is not "the best χ² per band" as the README says. With the best χ² per band across families, the fit-only curve has mean −29.73, median −30.58, N33 66 %.

Inference: the posterior-to-profile ratio is not "prior volume" only. A profile likelihood (the best trajectory per band) omits the width of the well-fitting region in the 4-family, speed, altitude and heading parameter space, which the satellite data determine. The ratio therefore contains both the flight-path prior and the Occam factor of the satellite likelihood. The fuel limit is physical information, not a free prior. The README's own caveat ("a profile likelihood is not a marginal likelihood") contradicts the summary line "not because of the fit". A valid test needs the marginal likelihood per band under an alternative prior (for example, prior samples reweighted to be uniform per band). In addition, each band's minimum χ² comes from about four seeds and is a noisy extreme-value statistic (for example 15.8 against 34.7 between seeds at 39.75° S).

## C6. October against November

The configuration diff (October `arclat-ext-globcurrent-a.toml` against 7 November `conv-globcurrent-1.toml`) shows only particles per class, seed, environment seeds, `write_coefficients`, node subset, output directory and three added level alternatives. Code changes on the module branch between 17 October and 7 November are output switches with byte-identical node-table smoke tests. So "same physics configuration" is confirmed.

Agreement is not confirmed. On the same 84 points (`rv-c6-october-vs-nov7-by-point.csv`), the per-point finds-only log-likelihoods differ by a mean of +0.38 (GlobCurrent) and −0.11 (GLORYS12), with centred RMS 0.83 and 1.23 and correlation 0.81 and 0.58; there is no north–south trend in the difference. The drift-alone results (`rv-c6-drift-alone-october-vs-nov7.csv`, three-point mapping, which reproduces ledger v32 for October):

| Surface | Median | N of 33° S | ln S | p | Core shift |
|---|---|---|---|---|---|
| October (4 ocean samples, 256 draws) | −29.97 | 77.2 % | −1.49 | 0.066 | +1.01 |
| 7 November module table (16 samples, 256 draws) | −30.78 | 68.0 % | −1.05 | 0.109 | +0.75 |
| 7 November, 16,384 draws (one seed) | −31.35 | 61.6 % | −0.76 | 0.143 | +0.57 |

The like-for-like November median is 1.4° south of October. The October value agrees with the corrected November headline only because the headline is a different configuration (window to 30 January 2017, four periods, 25 coasts, twelve items). The other agent's own R1 row (old window, nine finds, extended run) gives median −30.95 and N33 61 %, consistent with the reviewer's 7 November value, not with October. The claim of agreement should be withdrawn; the October surfaces (4 ocean samples) should not be used as corroboration.

## C7. Interpretive claims

- "Mild tension (1.8σ)": the sign and order of magnitude are supported; the stated precision is not. The value depends on the level-draw seed, the tie order and the interpolation (1.6–2.0σ), and on ocean-sample noise (1.2–2.3σ in quarter subsets). It also depends on unruled choices that all move the drift evidence north when relaxed (Australia off rather than option B or the ruled tiers; inclusion of two "unclear" items; the provisional ramp).
- "Agrees with most published drift studies": no study is cited in the README. The official CSIRO work for the ATSB gave 35.6° S, 92.8° E as the most likely location (Griffin and Oke 2017, Part III) and an earlier debris-based range of 36–32.5° S (December 2016). A drift-alone median of 30.3° S does not agree with these. The claim must be replaced by a cited comparison.
- "Defensible": not yet, because of defects 1–8 below.

## Further defects, ranked by severity

1. High. Level-draw Monte Carlo error is understated. The headline shift and the tension statistics are reported from one seed (31) that lies at the low end of the seed distribution (+0.75 to +1.09°; p 0.073–0.105). Effective sample size of the draws is about 40–1000 per point. Report several seeds, or use more draws or an importance-sampling scheme, and quote the spread.
2. High. Ocean-sample (environment) error of the headline is not assessed. Disjoint quarters give medians 29.1–31.6° S and p 0.019–0.23.
3. High (interpretation). The headline depends on a provisional, unruled level ramp that is the largest lever (constant in time: −0.13°; ramp: about +0.9°). This must be stated as the dominant modelling assumption, with both values in the paper.
4. Medium-high. The headline sets Australia "off" (limit of ratio → 0). The module's pre-registered primary is option B, and Australian tiers were ruled on 17 October with the ratio pending. Every Australian setting moves the result north; "off" is the most southern choice, so it is not neutral.
5. Medium. The 1-D drift profile (`drift_alone_ramp.py`) interpolates the likelihood in node latitude over points on the arc and 50 NM inside and outside, with 14 tied latitudes. The result depends on sort order (mean −30.57, −30.66 or −30.77; p 0.078, 0.097 or 0.088). Use the arc latitude of each point and combine the three cross-arc points explicitly.
6. Medium. Tension output (`drift-alone-and-tension.csv`) clips d to 1e-6. Where d ≤ 0 it reports p ≈ 0 and 5.35σ or 5.47σ (rows "R0 nine finds GLORYS12" and "R3 nine finds GLORYS12"), and p = 1 where d − 2 ln S ≤ 0. Undefined cases must be reported as undefined.
7. Medium. Australian ruled tiers are absolute and constant in time (`ruled_au`), while new western Indian Ocean tiers are offsets on the ramp. The README describes all tiers as offsets. The two readings differ by about 0.4–1.0° in the Australia rows.
8. Medium. Nautilus Bay and Mpame (`identity_uses_prior_drift = unclear`) are treated as non-circular in the headline. Each moves the mean north (+0.13° and +0.22° when added singly to the nine). The 8 November "without Nautilus Bay and Mpame" sensitivity was not recomputed with the ramp.
9. Medium (interpretation). C5: profile likelihood treated as if it were the fit's contribution to the posterior; the Occam factor of the satellite likelihood is attributed to the prior.
10. Low-medium. C5: the "satellite fit only" curve is family-self-normalised, not best-per-band as described; median −31.25 against −30.58.
11. Low. C6 compares October with a different November configuration; the like-for-like comparison disagrees by 1.4°.
12. Low. The unrelated-debris background in the "drift alone" curves is averaged under the core posterior, so drift alone is not fully independent of the core (effect small: shift +1.00° with the core average against +0.92° with a uniform average, one seed).
13. Low. Priors differ between tables: the drift-alone curves use a uniform prior per unit arc length (ledger bins); the fit-versus-prior-volume table uses a uniform prior per 0.5° latitude band.
14. Low, latent. In `lib.rs` `node_ln_likelihood_zeros`, an environment whose coefficients for a class are `None` skips that class (factor 1 for its finds) instead of giving zero. Not triggered in R3 (0 of 12,096 class entries), but it would bias a sparse run.

## Key assumptions and modelling choices (this review)

| Item | Choice in this review | Status |
|---|---|---|
| Scorer | Own implementation of `node_ln_likelihood_zeros` (log of mean over ocean samples and draws) | Reviewer's choice, from module source |
| Level prior | Log-normal, σ 1, period medians 0.1 / 0.5 / 1 / 1; Australia −30 (off); populated new coasts (Mozambique south and KwaZulu-Natal north, Eastern Cape, Western Cape) at the ramp, other new coasts at ramp + ln 0.3 | Module default (provisional) and the claim's configuration |
| Australia sensitivities | Ruled tiers city and inner ρ, outer 0.3ρ, remote off; as ramp offsets (reviewer) and as absolute values (their method) | Tiers: ruling of 17 October; ratio not ruled |
| Items and weights | Nine stringent finds plus Linga Linga, Nautilus Bay, Mpame; confirmed 1, almost certain 0.98, highly likely 0.9 | Claim's configuration (Pete: use all items; weights own choice of the other agent) |
| Unrelated-debris background | Constant u_j (core-weighted mean) and draw-dependent b_j(d) | Both tested; b_j(d) is the claim's definition |
| Level draws | Own numpy draws, 16,384 (8 seeds) and 65,536 (2 seeds); seed 31 only for reproduction | Reviewer's choice |
| Mossel Bay date | 23 December 2015 (coefficient file as stored) | Pete's ruling |
| Ocean models | GlobCurrent and GLORYS12, equal weight, average of likelihoods | Project convention |
| 1-D mapping | Three-point mean per arc latitude, linear in arc latitude (reproduces ledger v32); six-point inverse distance; track only; their node-latitude interpolation | Reviewer's choice; sensitivity reported |
| 2-D combination | Run J H_D0_all, cell centres, six nearest release points, inverse distance (power 2, also power 1 and likelihood space) | Claim's method |
| Prior for drift alone | Uniform per unit arc length on the 159 ledger reach bins | Evidence-ledger method |
| Tension | Handley and Lemos (2019) R, I, S, d, p on ledger bins | Evidence-ledger method |
| Satellite fit | Run J four families; best χ² per 0.5° band across families | Reviewer's reading of the README |

## What was not done

- No new particle runs. The ocean-sample uncertainty is estimated only from disjoint quarters of the stored samples.
- The 8 November ladder rows R1, R2 and R4 were not re-scored in full; R4 was used only for the coefficient consistency check.
- The published-study comparison in C7 rests on the CSIRO reports only; other published drift studies were not reviewed.

## Files

Scripts: `rv_scorer.py` (scorer), `rv_ledger.py` (summaries and tension), `rv_score_r3.py` (variant passes), `rv_review_driver.py` (condensed driver).
Tables: `rv-c2-node-check-84x2.csv`, `rv-c3-exact-reproduction-seed31.csv`, `rv-c3c4-level-draw-seed-study.csv`, `rv-c3-drift-alone-by-mapping.csv`,
`rv-c3-drift-alone-variants-idw2.csv`, `rv-c3-environment-quarter-subsets.csv`, `rv-c4-core-combination-shifts.csv`, `rv-c5-fit-profile-bands.csv`,
`rv-c6-october-vs-nov7-by-point.csv`, `rv-c6-drift-alone-october-vs-nov7.csv`, `rv-level-draw-ess-by-node.csv`.
