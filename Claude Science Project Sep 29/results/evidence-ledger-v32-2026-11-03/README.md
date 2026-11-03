# Evidence ledger on composer views v3.2 (run J) — 3 November 2026

**Question (Pete, 3 Nov 2026).** No single type of evidence can fix the position on the 7th arc. Can we show, with numbers, how
much each type narrows the arc alone and in combination, and whether the types agree? This is the value-of-information idea of the
hydroacoustic synthetic test, applied to all the evidence that the composer uses.

**Status:** exploratory analysis for review. Not yet ruled. Not a headline product. No label in this folder has been approved.

## Short answer (STE100)

1. With the present evidence, the types of evidence **do not converge**. Only the satellite data and the flight model (core) narrow
   the arc. Debris drift and the searched areas, alone, put more probability north of 33 S. When we add them to core, the arc that holds
   90 % becomes longer: 330 NM for core alone, 680 NM for all evidence (00:19 data held out).
2. The satellite result and the other evidence **disagree at about 2 sigma** (p 0.02–0.04 over the six 00:19 treatments). This is a
   moderate disagreement. It is not proof that any type of evidence is wrong.
3. The test cannot say **which** type is wrong. The teaching example (folder `demo/`) shows this: a wrong direction is flagged, but
   so are two correct types.
4. Bayesian search theory still allocates effort by probability. But the best single 15,000 km² block holds 0.45 of the probability
   with core alone and 0.16 with all evidence.

## Method

- The composer v3.2 machinery is reused **unchanged** (`compose_v3.py`, `V32=1 DEXT=1`). The ledger weights reproduce the composer products
  core, D, S, DS, ApopS, DSP and the uniform-arc views with maximum relative difference 0; medians and 90 % areas agree exactly.
- Types: core (satellite data, flight models, end of flight and settling; they cannot be separated in this sample); debris drift (finds
  only); searched areas (per-cell model V1 central, Ocean Infinity coverage inferred, grade C, included as best estimate); no debris on
  populated Australian coasts (measured, labelled sensitivity); Pleiades objects (conditional on being aircraft debris). Hydroacoustics
  has zero weight by ruling.
- The ocean model is shared by drift, the Australian term and Pleiades. These terms are multiplied **inside** the two-model average,
  0.5 Σ_m Π_k L_k|m, as in the composer, so the shared model is not counted twice. The Australian term alone is d|pop|m / d|off|m.
- **Primary measure:** information along the arc. Entropy on 10 NM bins of the impact arc position, against a uniform base on the arc
  where every module is computed (40.25–19.9 S). Views without core are u × E[L | bin] over the core outcomes. One bit halves the arc length.
  2-D measures (90 % seabed area, best 15,000 km² block) are given only for combinations with core, where the effective sample is large.
- Attribution: Shapley values over all subsets of each set. Agreement: suspiciousness ln S = ln R − ln I with Bayesian model
  dimensionality (Handley and Lemos 2019), one type against the product of the others; Gaussian calibration, approximate.
- Uncertainty: 400 seed-bootstrap draws with the composer's resampling groups; views without core are recomputed in each draw.

## Results

### How much each combination narrows the arc

| evidence used | bits along the arc, D0 (95 % interval) | range D0–D5 | 90 % arc length, NM, D0 | range D0–D5 | best 15,000 km², D0 | 90 % seabed area, k km², D0 |
|---|---|---|---|---|---|---|
| uniform along the arc (reference) | 0.00 (0.00–0.00) | 0.00–0.00 | 1440 | 1410–1450 | — | — |
| core alone | 2.32 (2.16–2.44) | 2.32–2.87 | 330 | 270–330 | 0.45 | 165 |
| debris drift alone | 0.35 (0.33–0.36) | 0.35–0.38 | 1050 | 1020–1050 | — | — |
| searched areas alone | 0.11 (0.11–0.12) | 0.11–0.43 | 1270 | 1070–1270 | — | — |
| drift + searched areas (no core) | 0.36 (0.35–0.38) | 0.36–0.52 | 1050 | 950–1050 | — | — |
| core + drift | 1.57 (1.43–1.70) | 1.57–1.97 | 510 | 410–510 | 0.31 | 287 |
| core + searched areas | 1.78 (1.64–1.89) | 1.78–2.25 | 410 | 350–410 | 0.27 | 288 |
| **all evidence (headline)** | 1.13 (1.02–1.22) | 1.13–1.37 | 680 | 620–700 | 0.16 | 435 |
| all + Australian non-finds (sensitivity) | 0.68 (0.63–0.72) | 0.68–0.82 | 890 | 780–890 | 0.11 | 515 |
| all + Pleiades objects (conditional) | 3.16 (3.08–3.21) | 3.16–3.62 | 160 | 100–160 | 0.47 | 72 |

### Fair share of each type (Shapley values, bits along the arc)

| set | evidence | Shapley bits, D0 (95 % interval) | range D0–D5 |
|---|---|---|---|
| headline | satellite data and flight (core) | +1.51 (+1.37 to +1.62) | +1.51 to +1.82 |
| headline | debris drift (finds) | -0.18 (-0.20 to -0.16) | -0.32 to -0.18 |
| headline | searched areas (no find) | -0.20 (-0.22 to -0.17) | -0.22 to -0.15 |
| with Australian non-finds | satellite data and flight (core) | +0.97 (+0.87 to +1.05) | +0.97 to +1.18 |
| with Australian non-finds | debris drift (finds) | -0.06 (-0.08 to -0.03) | -0.14 to -0.06 |
| with Australian non-finds | searched areas (no find) | -0.12 (-0.14 to -0.10) | -0.13 to -0.01 |
| with Australian non-finds | no debris on populated Australian coasts | -0.11 (-0.14 to -0.07) | -0.20 to -0.11 |
| with Pleiades (conditional) | satellite data and flight (core) | +0.88 (+0.82 to +0.94) | +0.88 to +1.11 |
| with Pleiades (conditional) | debris drift (finds) | +0.07 (+0.06 to +0.07) | +0.03 to +0.08 |
| with Pleiades (conditional) | searched areas (no find) | -0.11 (-0.13 to -0.10) | -0.11 to +0.06 |
| with Pleiades (conditional) | Pleiades objects (if debris) | +2.32 (+2.24 to +2.39) | +2.32 to +2.45 |

### Agreement of each type with the rest

| set | test | ln S, D0 | p, D0 | p range D0–D5 | about |
|---|---|---|---|---|---|
| headline | satellite data and flight (core) vs the rest | -2.28 | 0.043 | 0.023–0.043 | 2.0 σ |
| headline | debris drift (finds) vs the rest | -1.28 | 0.094 | 0.067–0.094 | 1.7 σ |
| headline | searched areas (no find) vs the rest | -0.96 | 0.093 | 0.074–0.093 | 1.7 σ |
| with Australian non-finds | satellite data and flight (core) vs the rest | -3.79 | 0.016 | 0.009–0.016 | 2.4 σ |
| with Australian non-finds | debris drift (finds) vs the rest | -0.39 | 0.215 | 0.184–0.215 | 1.2 σ |
| with Australian non-finds | searched areas (no find) vs the rest | -0.54 | 0.114 | 0.101–0.123 | 1.6 σ |
| with Australian non-finds | no debris on populated Australian coasts vs the rest | -1.37 | 0.075 | 0.063–0.109 | 1.8 σ |
| with Pleiades (conditional) | satellite data and flight (core) vs the rest | -1.27 | 0.150 | 0.103–0.150 | 1.4 σ |
| with Pleiades (conditional) | debris drift (finds) vs the rest | -0.21 | 0.177 | 0.177–0.221 | 1.3 σ |
| with Pleiades (conditional) | searched areas (no find) vs the rest (d = 0.13: p not reliable) | -0.76 | 0.020 | 0.020–0.088 | 2.3 σ |
| with Pleiades (conditional) | Pleiades objects (if debris) vs the rest | 0.19 | 0.436 | 0.357–0.511 | 0.8 σ |

p is from chi-squared with d degrees of freedom, d = Bayesian model dimensionality of the pair; when d is below about 0.5 the p-value is not reliable.

## Two corrections found during this work

1. **Synergy.** For two independent constraints, the bits add and the area factors multiply. So a clean crossing gives synergy near
   zero, not a large positive value. Negative synergy = redundancy (both types constrain the same thing). Positive synergy = one type
   makes another relevant. See `demo/`.
2. **Sampling.** On the 769 km² seabed grid, the uniform-arc views have a Kish effective sample of only about 1,000, so their map entropy
   carries a counting bias of 1.3–3.2 bits. The along-arc measure avoids this. Also, north of 19.9 S the drift likelihood is not computed and
   the composer carries it at the mean. This put about 10 % of the no-core mass in seven bins. The ledger domain therefore stops at 19.9 S.

## Limitations

- Core cannot be split into satellite data, fuel and end of flight in this sample. The endurance runs (`results/endurance_*`) could do this.
- 28 % of the nominal 40.6–11.8 S span is outside the ledger domain; core mass there is 0.015 % or less.
- The bootstrap 95 % intervals of non-linear measures (bits, arc length) do not always contain the point value; read them as Monte Carlo
  spread, not as exact confidence intervals.
- Suspiciousness p-values use a Gaussian calibration. The likelihoods here are not Gaussian (the searched areas are a step function).
- The searched-areas information alone depends on the 00:19 treatment (0.11–0.43 bits), because the end-of-flight model sets the across-arc
  position of the wreck in each arc bin.

## Files

- `ledger_v32.py` — the ledger (reads `mh370-exchange/composer/run-j-views-v3/work`, the same inputs as views v3.2).
- `ledger-subsets-v32.csv` (192 rows: 32 subsets × 6 treatments), `ledger-shapley-v32.csv`, `ledger-tension-v32.csv`, `ledger-pairs-v32.csv`,
  `ledger-arc-masses-v32.npz` (bin masses and bin latitudes), `ledger-meta-v32.json`.
- `evidence-ledger-v32-fig1.png/.pdf` — the figure.
- `demo/` — the teaching example with invented numbers (`ledger_demo.py`, two figures, two tables).
