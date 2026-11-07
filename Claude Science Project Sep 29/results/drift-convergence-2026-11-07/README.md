# Ocean drift: coefficient output, convergence run and exact sensitivities (7 November 2026)

Ocean drift work, run overnight 6–7 November 2026 on Pete's instruction ("overnight run, starting with item 1 then 2 onwards").
Deskstar jobs 91ee26ce (main run) and 272016f7 (southern supplement). Code: branch `hypothesis/debris-drift`, commit c2f3eb4.

## Summary (ASD-STE100)

- The drift module now writes its internal coefficients to a file. With this file, we can calculate exactly any detection ratio, any set of finds and any find-kernel width, without a new transport run.
- We checked the offline calculation against the module. The difference is less than 1.3 × 10⁻⁶ log-likelihood units at all 84 release points, in both ocean models.
- The new run uses 16 ocean-environment realisations per point (32 south of 33.25° S). The earlier run used 4. With 4, the result is biased towards the north.
- With all nine finds and no Australian term, the mean impact latitude moves +0.61° north. The earlier value was +1.00°.
- The flaperon alone moves the mean +0.02° (median about 1 NM). This agrees with Davey et al. (2016).
- One find, the engine cowling found at Mossel Bay, causes almost all of the northward move. Without it, the move is −0.09°.
- The absence of debris on Australian coasts moves the mean further north. At a detection ratio of 0.25, the total move is +1.89°. At a ratio of 1, it is +3.49°.
- The model does not reproduce the early finds in southern Mozambique and South Africa: it expects 0.22 such finds before 1 March 2016, and there were 3. This occurs for every source latitude in the scan. Transport speed, object windage or search effort may be the cause.

## 1. What changed in the code (item 1)

`write_coefficients = true` (default false) writes, for every release point, every ocean environment and every object class:
the find-kernel coefficients `a` (each find's own coast segment, by discovery period) and the recovery mass `A` (all 16 segments × 3 periods),
for the full ensemble and both particle halves, at all four kernel widths. `coefficients-meta.json` holds the block layout, the finds,
the environments and the module's own standard-normal detection-level draws `z`, so that ν = exp(μ + σz) reproduces the module exactly.
The node likelihood is then

  ln L(x) = ln mean over (environment e, level draw d) of Σ_c Σ_{j∈c} [ ln(a_cj(e)·ν_d) − ln(A_c(e)·ν_d) ].

Checks: (i) the node table is byte-identical with the switch off and on, and with the previous binary (smoke test, MD5 equal);
(ii) `drift_coef.py` reproduces the module's primary, finds-only, split-half and three new Australian-ratio columns
to ≤ 1.3 × 10⁻⁶ at all 84 points in both models (`validation-offline-vs-module.csv`).

## 2. The run (item 2)

- Release points: the 84 arc-latitude points of 18 and 20 October (20–40° S, run J median impact track and ±50 NM), on the extended 5 NM grid.
- 6,250 particles per class per environment; environments 101–116 at all points; a supplement adds environments 117–132 at the 42 points south of 33.25° S.
  Seeds are independent of the 18–20 October run (environments 1–4).
- Both ocean models (GLORYS12 and GlobCurrent, product-relative windage), settings otherwise identical to the 20 October configuration.
- All 18 chunks exited 0. Wall time 6 h 47 min (main) plus 2 h 38 min (supplement).
- The 15–160° E forcing had been removed from deskstar on 3 November as a verified duplicate. It was restored from the Mac copy and checked
  against the original SHA-256 list (48 of 48 files match) before the run.

## 3. Results (run J impact samples, 00:19 data held out, two ocean models at equal weight, 50 km kernel)

Core alone: mean −36.72°, median −37.13°, 3.2 % of mass north of 33° S.

| Drift evidence | Mean shift (deg N) | Median (deg) | Mass N of 33° S | ln R, core vs uniform on the arc |
|---|---|---|---|---|
| Nine finds | +0.61 | −36.73 | 6.7 % | −0.39 |
| Flaperon alone | +0.02 | −37.11 | 3.1 % | +0.15 |
| Mossel Bay engine cowling alone | +1.40 | −36.65 | 14.4 % | −1.53 |
| All finds except Mossel Bay | −0.09 | −37.13 | 2.4 % | +0.39 |
| All finds except Mossel Bay and Paindane | −0.25 | −37.19 | 1.5 % | +0.56 |
| Nine finds, Australian ratio 0.05 | +1.06 | −36.31 | 9.4 % | −0.62 |
| Nine finds, Australian ratio 0.1 | +1.33 | −36.01 | 11.4 % | −0.79 |
| Nine finds, Australian ratio 0.25 | +1.89 | −35.47 | 16.3 % | −1.11 |
| Nine finds, Australian ratio 0.5 | +2.55 | −35.07 | 22.9 % | −1.43 |
| Nine finds, Australian ratio 1 | +3.49 | −34.57 | 33.4 % | −1.79 |
| Seven finds (no Mossel Bay, Paindane), ratio 0.25 | +0.46 | −36.89 | 4.7 % | −0.03 |

Australian ratio = detection on Australian city and inner-regional coasts relative to the coasts where debris was found; outer regional
= 0.3 × ratio; remote = 0 (17 October tiers). With populated coasts only (outer regional also 0): ratio 1 +2.46°, 0.5 +1.87°, 0.25 +1.45°, 0.1 +1.08°.

Single finds (mean shift): Mossel Bay +1.40, Paindane +0.64, Vilanculos +0.14, Chidenguele +0.10, flaperon +0.02, Mauritius −0.08,
Antsiraka −0.13, Rodrigues −0.17, Pemba −0.20. Seven of the nine finds, alone, favour the satellite region or are neutral.

Other sensitivities (nine finds): GlobCurrent alone +0.54°, GLORYS12 alone +0.66°; kernel 25 / 100 / 200 km: +0.65 / +0.53 / +0.46°,
kernel averaged over 25–200 km +0.59°. 00:19 BTO only: +0.45° (ratio 0.25: +1.64°); 00:19 BTO and BFO: +0.53° (ratio 0.25: +1.70°).

## 4. Convergence

| Estimate of the nine-find shift | Mean shift (deg N) |
|---|---|
| 4 environments, 18–20 October run | +1.00 |
| 4 environments, this run (four disjoint sets) | three of four have unresolved points; the fourth +1.22 |
| 8 environments, this run (environments 9–16) | +1.28 |
| 16 environments, this run, all points | +0.79 |
| Pooled: 32 environments south of 33.25° S, 16 north | +0.61 (particle halves +0.69 and +0.96) |

1. **The environment average is the dominant convergence problem.** At 38–40° S the nine-find product varies between environments by about
   3.8 ln units (standard deviation), after particle noise is removed. Almost all of this is in two finds: Mossel Bay (about 4 ln units; no particle
   in its kernel in 22–38 % of environments) and Paindane (about 3 ln units). The other seven vary by about 1 ln unit or less.
2. **A small environment sample biases the shift north.** The log of a mean of a few heavy-tailed values is biased low, and more so where the
   spread is larger, which is in the south. Four-environment subsets lie 0.2–3.1 ln units below the pooled value south of 33.25° S. The shift
   falls as environments are added (+1.0 to +1.3 with 4–8, +0.79 with 16, +0.61 with 32 in the south). It is not yet converged; the converged
   value is probably lower still.
3. **Particle noise per point is still large in the south** (split-half RMS 1.4 ln GlobCurrent, 2.2 ln GLORYS12), which gives ±0.14° on the shift.
4. **Kernel width is no longer a first-order lever** (+0.46 to +0.65° from 200 to 25 km). The factor-of-six spread reported on 17 October
   came mostly from Monte Carlo noise on the earlier surfaces.
5. **Results without Mossel Bay and Paindane are converged for practical purposes**: the flaperon-only and seven-find terms vary by about 1 ln unit
   or less between environments.

## 5. Posterior predictive check (nine finds, finds-only posterior)

Expected and observed identified finds by coast (prior detection levels, posterior over impact position):

| Coast | Expected, whole window | Observed | Expected before 1 Mar 2016 | Observed before 1 Mar 2016 |
|---|---|---|---|---|
| Réunion | 1.59 | 1 | 0.70 | 1 |
| Mauritius and Rodrigues | 2.91 | 2 | 1.48 | 0 |
| Southern Mozambique | 0.65 | 3 | 0.16 | 2 |
| South African south coast | 0.23 | 1 | 0.06 | 1 |
| North-east Madagascar | 3.11 | 1 | 1.51 | 0 |
| Pemba | 0.50 | 1 | 0.28 | 0 |

The early south-western finds are the misfit. For exterior panels, the share that reaches southern Mozambique and South Africa
before 1 March 2016 rises with a northern source (GlobCurrent: 0.9 % from 38° S, 2.9 % from 30° S, 4.3 % from 26° S, about 10 % from 20–22° S),
but at every arc latitude in the scan the expected count stays well below the three observed. Candidate causes, not separated here:
transport too slow or too little windage for exterior panels; search effort in southern Mozambique in late 2015 to early 2016
(private searchers) above the period level; or an impact further north. The module's `searcher` option addresses the second in part.

## 6. Equation (21) of the paper equation set against the code

Equation (21) in `MH370-equations-JON-form-v3.docx` is the one-class, fixed-level special case of what the module computes:
L ∝ Γ(n) Π q_i / Q^n. The code differs in four ways that the paper must state:
(a) a separate unknown number of floating pieces per object class, each with p(λ_c) ∝ 1/λ_c, so the denominator is Π_c (A_c·ν)^{n_c};
(b) detection levels ν per coast segment and discovery period are latent, log-normal (σ = 1), and averaged by 256 draws;
(c) the average over ocean environments (diffusivity and ocean-error realisation) is taken outside the product over finds, inside each ocean model;
(d) the remoteness weights in the terms table (1 / 0.3 / 0.05) are the pre-registered option B; the 17 October ruling is 1 / 0.3 / 0 times a ratio.
The finds-only term is the same equation with Australian levels set to zero; it is not a separate formula.

## Key assumptions and modelling choices

| Item | Value | Status |
|---|---|---|
| Impact samples | Run J, end-of-flight families pooled, 2-D impact histogram, 00:19 data held out | Project convention |
| Ocean models | GLORYS12 and GlobCurrent with ERA5 wind, equal weight in likelihood; GlobCurrent windage product-relative | Pete's ruling (9 and 17 Oct) |
| Finds | Nine confirmed or almost-certain items, find episodes by coast and period | Project convention |
| Object response, delay, detection levels | Provisional priors (60-day reporting delay; ln ν ~ N(μ_period, 1)) | Provisional, not ruled |
| Australian tiers | City and inner regional = ratio, outer regional = 0.3 × ratio, remote = 0 | Pete's ruling (17 Oct); the ratio grid is a sensitivity |
| Ratio values 0.05–1 | Sensitivity grid | Own choice; Pete has not chosen a headline ratio |
| Environments | 16 (32 south of 33.25° S), 6,250 particles per class per environment | Own choice; not converged (section 4) |
| Release points | 84 arc-latitude points; posterior by inverse-distance weighting of the six nearest points | As 18–21 October method |
| Evidence ratio | Against a uniform prior along the arc, 1-D evidence-ledger bins | As evidence-ledger method |
| Posterior predictive check | Prior detection levels, not posterior levels | Own choice |

The interim values sent on 7 November (emulator, ratio 0.25: +2.51°) are superseded by the exact values above (+1.89°).
The 18–21 October arc-latitude values (finds only +1.00°, option B +5.44°, populated only +3.36°) are four-environment estimates and are superseded.

## Files

- `validation-offline-vs-module.csv`, `posterior-summaries.csv`, `convergence-finds-only.csv`, `environment-convergence-points.csv`,
  `evidence-ratio-core-vs-uniform.csv`, `posterior-predictive-finds.csv`, `node-values-all-cases.csv`, `node-values-finds-only.csv`, `low-exposure-shares-by-source.csv`
- Figure: `drift-evidence-on-impact-latitude.png/.pdf` (working); `drift-evidence-on-impact-latitude-jon-word.png`, `-jon.pdf`, `-jon-proof.pdf`, `-jon-caption.txt` (journal form)
- Scripts: `conv_analysis.py`, `conv_figures.py`, `drift_coef.py` (also in the module at `prepare/coef/`)
- `drift-coefficients-2026-11-07.tar.gz`: all coefficient files, node tables and summaries of both jobs (56 MB)
- `chain-main.log`, `chain-supplement.log`, `release-points-84.csv`, `ocean-forcing-sha256.txt`
- SST back-of-envelope: `sst-arc-2014.csv`, `sst-18C-line-by-month.csv`, `sst-warm-lines-2015.csv` (NOAA OISST v2 monthly, 1°)
