# Exterior-class windage: what the drift data prefer (ocean drift, 10 Nov 2026)

## Summary (ASD-STE100)

- I inferred the windage distribution of the exterior items from the stored particles. No new drift run was needed.
- Each grid point is a truncated log-normal windage prior with median m and log-sd σ. Every particle of the wide run and of the higher-windage run was reweighted by its windage and rescored.
- The reweighting reproduces the independent runs. Production prior: ln Z −182.87 (reweighted) against −182.82 (run). Higher prior: −177.74 against −177.65. The identity weights reproduce the rescoring exactly.
- The data prefer median windages of 2.4 to 3.6 %. The maximum of ln Z is at m = 3.0–3.6 % with σ = 0.25–0.35 (ln Z −177.0). It falls again at 4.5 % for σ = 0.25.
- The production prior (median 1.2 %, σ about 0.25) has ln Z −182.5. The data disfavour it by about 5.5 ln units.
- The posterior of the median depends on the upper bound of the hyperprior. The posterior geometric mean is 2.45 % (bound 3.0 %), 2.87 % (bound 3.6 %) and 3.15 % (bound 4.5 %). The probability of a median at or below 1.5 % is 0.026 to 0.075.
- The data do not constrain σ. Posterior weights are 0.31–0.39 (σ 0.25), 0.28–0.35 (0.35), 0.23–0.31 (0.5).
- With the windage hyperparameters marginalised over the hyperprior, drift and core agree. Tension p = 0.645 to 0.747. Drift alone: median 34.5–35.1° S.
- Combined with the core: median 36.1–36.2° S, mean 35.99–36.14° S, 2.6–3.6 % north of 33° S (core alone: 36.4° S, 35.95° S, 8.1 %).
- The inferred value is an effective windage. It also absorbs any transport that the model lacks. It is not a measurement of the physical windage of the panels. The replica trial of the cowling gives about 1.2 %.
- Run 3 (extra ocean samples, 48 in the south) is complete. It changes the wide-prior result very little (section 5).

## 1. Method

- Sampling densities: wide run, log-normal median 1.2 %, σ 0.5, truncated 0.3–5 %. Higher-windage run, log-normal median 2.4 %, σ 0.35, truncated 0.8–6 %.
- The windage of a particle is the same in both ocean models and in every leg of a particle set (same seed). GlobCurrent adds a product offset of −0.75 to −0.60 % and floors at zero. I read the windage from the GLORYS12 response table of the set.
- A target prior g(c) gives each particle the weight g(c)/f(c) (normalised to a mean of 1 per set). The coefficients are linear in the weights. The offline rescorer therefore gives the coefficients of the target prior (importance sampling).
- Rescoring: bandwidth 50 km only, 24 wide legs (wide, wide2, wide3) and 18 higher-run legs. The weights were streamed to the rescorer through a named pipe. Nothing was written to the disk of deskstar apart from the coefficient files (about 250 MB).
- Scoring: headline configuration (twelve identity-weighted items, ramp detection prior, 60-day delay), seeds 1–4 (65,536 draws per point), 48 ocean samples at the southern points for the wide-run targets and 32 for the higher-run targets.
- Z(θ) is the core-weighted mean likelihood at the 84 release points. Two ocean models have equal weight. This is the definition of the earlier ln Z of the three priors.
- Effective sample size of the windage draws (6,250 per set): above 1,300 for m up to 2.4 %, 590–1,000 at m = 3.0 % (wide run). The higher-run particles give 900–6,200 for m = 2.4–4.5 %. For m = 2.4 and 3.0 % both estimates are averaged. They agree within 0.1–0.45 ln units.

## 2. ln Z on the grid (two ocean models, 32-sample basis; both particle sets averaged where they overlap)

| log-sd of windage | 0.8 % | 1.0 % | 1.2 % | 1.5 % | 1.9 % | 2.4 % | 3.0 % | 3.6 % | 4.5 % |
|---|---|---|---|---|---|---|---|---|---|
| 0.25 | -186.04 | -184.48 | -182.46 | -180.14 | -178.52 | -177.50 | -177.04 | -177.09 | -178.07 |
| 0.35 | -185.24 | -183.21 | -181.53 | -179.85 | -178.56 | -177.69 | -177.22 | -177.05 | -177.40 |
| 0.5 | -183.38 | -181.77 | -180.66 | -179.55 | -178.66 | -177.99 | -177.57 | -177.28 | -177.20 |

Wide-run cells with σ = 0.7 (48 samples): m = 0.8 … 3.0 % give -181.75 | -180.78 | -180.11 | -179.41 | -178.81 | -178.36 | -178.05.

## 3. Posterior of the hyperparameters

Uniform hyperprior over the cells (log-uniform in m, uniform in σ). The hyperprior bound is my choice. The literature gives single best values of 0.8–3.3 % for flaperon-type items.

| Hyperprior | Cells | Prior-averaged ln Z | Posterior geometric mean of m (%) | 5 % to 95 % cell of m (%) | P(m ≤ 1.5 %) | P(m ≥ 2.4 %) |
|---|---|---|---|---|---|---|
| m 0.8–3.0 %, σ 0.25–0.7 (48 samples) | 28 | -178.66 | 2.45 | 1.5 to 3.0 | 0.075 | 0.774 |
| m 0.8–3.0 %, σ 0.25–0.5 | 21 | -178.51 | 2.53 | 1.5 to 3.0 | 0.050 | 0.817 |
| m 0.8–3.6 %, σ 0.25–0.5 | 24 | -178.19 | 2.87 | 1.9 to 3.6 | 0.032 | 0.883 |
| m 0.8–4.5 %, σ 0.25–0.5 | 27 | -178.09 | 3.15 | 1.9 to 4.5 | 0.026 | 0.907 |

The prior-averaged ln Z (−178.1 to −178.7) is the marginal likelihood of the hierarchical model. It is 4.1 to 4.7 above the fixed production prior (−182.8) and 1.9 to 2.5 above the fixed wide prior (−180.6). It includes the Occam penalty of the broader hyperprior.

## 4. Latitude and tension with the windage hyperparameters marginalised

At each release point and ocean sample the likelihood is the prior-weighted mean of the likelihoods of all cells. The data enter only through the likelihood. The smoothing and the bootstrap are as for the headline.

| Hyperprior | Drift alone: median (° S) | North of 33° S (%) | ln S | Tension p (5–95 % bootstrap) | Combined with the core: median / mean (° S), north of 33° S (%) |
|---|---|---|---|---|---|
| A | 34.5 | 31.0 | 0.43 | 0.645 (0.53–0.74) | 36.1 / 35.99, 3.6 |
| B30 | 34.7 | 28.9 | 0.44 | 0.678 (0.58–0.76) | 36.1 / 36.02, 3.4 |
| B36 | 35.0 | 25.1 | 0.49 | 0.731 (0.65–0.79) | 36.2 / 36.10, 2.8 |
| B45 | 35.1 | 23.7 | 0.51 | 0.747 (0.68–0.81) | 36.2 / 36.14, 2.6 |

For comparison (fixed priors, 3 to 16 seeds): production p 0.109, median 30.0° S, 74 % north of 33° S. Wide p 0.320 (0.342 with 48 samples). Higher p 0.566.
The tension is weak by construction here. The hyperprior was wide enough to include the values that the drift data prefer. Do not read p = 0.65–0.75 as independent confirmation. The agreement of the drift latitude with the core is obtained by letting the windage float.

## 5. Run 3 (48 ocean samples in the south), wide prior, headline

| Case | 32 samples: median (° S), north of 33° S (%), p | 48 samples: median (° S), north of 33° S (%), p |
|---|---|---|
| Two ocean models | 33.2, 48.4, 0.320 | 33.2, 47.9, 0.342 |
| GLORYS12 only | 31.1, 69.2, 0.122 | 31.2, 68.6, 0.131 |
| Without Mossel Bay | 34.2, 36.7, 0.601 | 34.3, 36.0, 0.638 |
| Mossel Bay at the ATSB find date | 33.6, 44.1, 0.400 | 33.5, 45.3, 0.388 |

The core-weighted ln Z is −180.58 (32 samples) and −180.59 (48 samples). Table `wide-48-vs-32-samples.csv` has all ten cases.

## 6. Limits

- The windage of the flaperon class (fixed 1.2 %) and of the interior class were not varied. Only the exterior class has a hyperprior.
- Every exterior object is assumed to draw its windage independently from the same distribution.
- The inferred windage is effective. It absorbs Stokes drift (treated implicitly, ruling D-b), submesoscale dispersion that the ocean models lack, and other model error. The upper cells (3–4.5 %) are above most direct measurements.
- The hyperprior bound changes the posterior mean of m from 2.5 to 3.1 %. The likelihood is data-limited, not bound-limited, up to 3.6 %. At 4.5 % the likelihood falls for σ = 0.25.
- Four seeds. The seed noise of ln Z is about 0.1–0.2. Cells at m = 3.0 % from the wide run have a larger importance-sampling noise (ESS 590–1,000). The higher-run estimates are used there.
- The wide-run targets are truncated to 0.3–5 % and the higher-run targets to 0.8–5 %. The hyperprior family is therefore bounded at 5 %.
- Detection prior, 60-day delay, identity weights and the Mossel Bay date are provisional, as in the headline.

## 7. Recommendation (technical judgement; the headline prior is Pete's decision)

- Use the hierarchical model for the paper: a log-normal windage distribution for the exterior items with the hyperparameters marginalised over a stated hyperprior. This replaces the choice of one fixed windage prior.
- State the hyperprior from the literature and the physics (median 0.8 to about 3.6 %, σ 0.25 to 0.5), and report the posterior of m next to it.
- Report the three fixed priors (production, wide, higher) as sensitivity cases.
- Present the inferred windage as an effective windage, not as a physical measurement.

## Key assumptions and modelling choices

| Item | Value | Status |
|---|---|---|
| Windage family | truncated log-normal (median m, log-sd σ), one distribution for all exterior items | my choice |
| Hyperprior | uniform on the cells: log-uniform in m (0.8 to 3.0, 3.6 or 4.5 %), uniform in σ (0.25 to 0.5; 0.7 on the wide grid) | provisional (my choice, from the literature range) |
| Truncation of the windage | 0.3 or 0.8 % to 5 % | my choice (the wide design of 9 Nov was approved by Pete) |
| Method | importance reweighting of stored particles; offline rescoring (50 km) | my choice; validated against two independent runs |
| Particle sets | wide run (48 samples in the south), higher run (32 samples) | as run |
| Seeds | 1–4 (65,536 draws) | my choice |
| Z definition | core-weighted mean likelihood, two ocean models at equal weight | as for the earlier ln Z |
| Flaperon and interior windage | not varied | my choice |
| Detection prior, 60-day delay, identity weights, Mossel Bay date | headline settings | provisional or not ruled |
| Core | final 7 Nov end-of-flight model, D0 | Pete's ruling |

## Files

`windage-hyperparameter-grid.csv`, `windage-hyperparameter-posterior.csv`, `wide-48-vs-32-samples.csv`, scripts `reweight_rescore.py`, `build_hybrid_grid.py`, `grid_one.py`, `grid_stage1.py`, `windage_posterior.py`, `smooth_stage1_w48.py`, `smooth_stage2_w48.py`, `smooth_stage2_mixA.py`, `smooth_stage2_mixB.py`, runners.
