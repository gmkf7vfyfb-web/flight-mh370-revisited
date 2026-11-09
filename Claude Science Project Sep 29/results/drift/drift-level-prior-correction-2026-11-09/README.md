# Ocean drift: correction of the detection-level prior, drift evidence alone, and its agreement with the core (9 Nov 2026)

Branch `claude-science-sep29`, folder `results/drift/drift-level-prior-correction-2026-11-09/`.
This folder **supersedes the headline numbers and both figures** of `results/drift/drift-extended-window-2026-11-08/` (commit 905fb46).
The transport run, the arrivals file and the offline rescore coefficients of 8 Nov are unchanged and remain valid.

## Summary

- The offline rescoring of 8 Nov had a defect. It set the detection level of every coast to the same value in every period.
- The drift module uses a provisional prior that increases with time: 0.1 before 29 Jul 2015 (flaperon find), 0.5 to 1 Mar 2016, then 1.
- The defect penalised fast northern drift paths. It made the drift evidence look as if it agreed with the satellite and flight data at about 36° S.
- We corrected the defect. The offline scorer now reproduces the module log-likelihood exactly at all 84 release points (difference 0 to 1e-6).
- Drift evidence alone (uniform prior along the arc): median 30.3° S, mean 30.6° S, 5–95 % 36.4–25.1° S, 75 % north of 33° S.
- This agrees with the October calculation (median 30.0° S) and with most published drift studies.
- Agreement with the satellite and flight data: suspiciousness ln S = −1.39, tension probability 0.078 (1.8 standard deviations). This is mild tension, not a contradiction.
- Combined with the satellite and flight data, the drift evidence moves the mean impact latitude 0.82° north (36.72° S to 35.90° S), not 0.15° south.
- The satellite fit alone is nearly flat along the arc between 38° S and 24° S (Δχ² at most 2.5). The core concentrates at 36–38° S because of the flight-path prior volume and the fuel limit, not because of the fit.

## 1. The defect

`offline/rescore_cfg.py::meta_for()` sets the period means of ln(detection level) to 0 when no value is passed. The rescore variants R1–R4
(including the headline R3) were built without passing the module ramp [ln 0.1, ln 0.5, ln 1]. The module run R0 kept its own ramp.
So the 8 Nov ladder step "R0 → old window" changed two things at once, and every rescored result used detection constant in time.
New-coast tiers (0.3, populated 1) were also applied as absolute values, not as offsets on the ramp.

Fix (`offline/rescore_analysis.py`, `load()` and `mu_tiers()`): base means = ramp [ln 0.1, ln 0.5, 0, 0] (the fourth period, after 1 Jul 2016,
continues at 1); new-coast tiers are offsets on the ramp; `LEVELS=flat` reproduces the old behaviour as a labelled sensitivity.
Check (`scorer-vs-module-node-check.csv`): with the ramp, the offline log-likelihood equals the module node-table `ln_l_lev_off` at all 84 points,
both ocean models (maximum absolute deviation 1e-6). With the flat prior it is 3.5–4.4 ln units lower in the north than in the south.

## 2. Drift evidence alone (uniform prior along the arc; 16384 level draws)

Table `drift-alone-and-tension.csv`; figure `drift-alone-latitude-density-2026-11-09` (working and JON versions).
Tension: Handley and Lemos (2019) statistics on the evidence-ledger bins, core = run J, 00:19 data held out.

| Case | Mean | Median | 5–95 % | N of 33° S | ln R | ln S | p (σ) |
|---|---|---|---|---|---|---|---|
| Satellite and flight data (core) | −36.70 | −37.07 | −38.35 to −33.80 | 3.4 % | | | |
| October calculation (ledger v32, 4 ocean samples, 256 draws) | −30.06 | −30.02 | −37.21 to −23.61 | 77 % | −0.73 | −1.49 | 0.067 (1.8) |
| Nine finds, as first scored (module run) | −29.42 | −29.75 | −36.87 to −22.61 | 81 % | −0.67 | −1.19 | 0.032 (2.1) |
| Nine finds, old window (to 30 Jun 2016) | −31.67 | −30.95 | −38.54 to −24.50 | 61 % | +0.20 | +0.22 | not defined (d ≤ 0) |
| **Headline: twelve items, all coasts, four periods** | **−30.57** | **−30.29** | **−36.37 to −25.15** | **75 %** | **−0.57** | **−1.39** | **0.078 (1.8)** |
| Headline, GlobCurrent only | −30.64 | −30.42 | −36.45 to −25.15 | 74 % | −0.55 | −1.36 | 0.082 (1.7) |
| Headline, GLORYS12 only | −29.45 | −29.75 | −35.23 to −23.97 | 86 % | −1.17 | −2.14 | 0.024 (2.3) |
| Headline, no finds in Australia (ratio 0.25) | −29.99 | −30.02 | −35.82 to −24.66 | 82 % | −1.06 | −2.20 | 0.045 (2.0) |
| Headline, no finds in Australia (ratio 1) | −29.59 | −30.02 | −35.60 to −24.39 | 88 % | −1.45 | −2.81 | 0.030 (2.2) |
| Headline without Mossel Bay | −32.19 | −32.37 | −38.49 to −25.51 | 53 % | +0.15 | −0.19 | 0.20 (1.3) |
| Mossel Bay only | −25.58 | −24.21 | −34.29 to −20.30 | 93 % | −1.68 | −2.73 | 0.012 (2.5) |

Release points span 40.25–19.92° S; the drift likelihood is not computed outside this span. The two-model curve is an average of likelihoods,
so the ocean model that gives the finds the higher likelihood carries more weight; here the curve lies close to GlobCurrent.
Monte Carlo: in the nine-find, old-window configuration (finds to 30 Jun 2016), disjoint four-ocean-sample subsets give drift-alone medians
from 30.4 to 36.5° S (`diag/drift-alone-four-environment-subsets.csv`). The headline configuration has not been subset-tested; by analogy its
drift-alone median may be uncertain by about ±2°. The peaks at 35.7 and 30.7° S are point-to-point noise.

## 3. Why the core dominates: fit or prior volume?

Table `combination-fit-vs-prior-volume.csv` (0.5° bands, 20–40° S; satellite fit = exp(−Δχ²/2) of the best trajectory per band, run J four route families).

| Combination | Mean | Median | N of 33° S |
|---|---|---|---|
| Core posterior (fit × prior volume) | −36.19 | −36.75 | 3.9 % |
| Satellite fit only (uniform prior along the arc) | −30.41 | −31.25 | 62 % |
| Headline drift alone | −30.57 | −30.25 | 75 % |
| Headline drift × core posterior | −35.47 | −35.75 | 7.6 % |
| Headline drift × satellite fit only | −31.01 | −30.75 | 71 % |

The best χ² in each band lies within 2.5 of the best fit overall (Δχ² 0 to 2.54) between 37.75° S and 23.75° S (10.4 at 39.75° S). Relative to the fit,
the prior volume (the share of flight-path prior samples that reach a band and fit) is on average about 120 times larger at 35.75–37.75° S than at
29.75–31.75° S (36 to 420 times, band by band).
The concentration of the core at 36–38° S is therefore a property of the flight-path prior (route families, speed and altitude schedules, fuel endurance),
not of the satellite measurements. A profile likelihood is not a marginal likelihood; the prior-volume factor is legitimate evidence only to the extent
that the flight-path prior is credible.

## 4. Combined with the core (corrected; 16384 draws; core D0 mean −36.72, median −37.13)

Table `final-posterior-summaries.csv`; `compare-flat.csv` lists each value with the 8 Nov (flat-prior) value beside it.

| Case | Shift of mean (deg N) | 8 Nov value (defect) |
|---|---|---|
| As first scored (module run, nine finds) | +0.66 | +0.66 |
| Old window (to 30 Jun 2016) | +0.06 | −0.37 |
| Four detection periods | +0.71 | −0.18 |
| All western Indian Ocean coasts | +0.82 | −0.18 |
| All coasts and four periods, nine finds | +0.76 | −0.20 |
| **Headline: twelve identity-weighted items** (mean −35.90, median −36.69, 5–95 % −38.13 to −30.47, N33 8.5 %, ln R −0.57) | **+0.82** | −0.15 |
| Headline, detection constant in time (sensitivity) | −0.15 | — |
| GlobCurrent only / GLORYS12 only | +0.78 / +2.35 | −0.16 / +0.50 |
| Fresh-arrival marks 10/10/14 d; 3/3/14 d | +0.22; +0.32 | −0.24; −0.15 |
| All but Mossel Bay; all but Mossel Bay and Paindane | +0.22; −0.07 | −0.30; −0.38 |
| Mossel Bay only; flaperon only | +1.61; 0.00 | +1.11; −0.10 |
| No finds in Australia, ratio 1 / 0.25 / 0.05 | +2.68 / +1.72 / +1.10 | +0.57 / +0.19 / −0.05 |
| Other coasts at the find level / at 0.1 | +1.36 / +0.60 | +0.01 / −0.24 |
| Kernel 25 / 100 / 200 km | +0.94 / +0.96 / +0.89 | −0.15 / −0.07 / −0.09 |
| Particle halves | +1.04 / +0.74 | +0.07 / −0.30 |
| Core D1 / D2 | +0.63 / +0.66 | −0.10 / −0.17 |

The 8 Nov finding that 256 level draws scatter the shift by up to about 0.6° (draw study on the module run, which kept the ramp) stands.
The 8 Nov statement that the earlier northward shifts were mostly that scatter does not stand: they were mostly the detection prior.

## Key assumptions and modelling choices

| Item | Value | Status |
|---|---|---|
| Detection level prior | log-normal, σ 1, period medians 0.1 / 0.5 / 1 (/ 1) | Provisional, pre-registered in the module; not ruled |
| Detection constant in time | Sensitivity only | Own choice |
| Headline drift model | All WIO coasts, four periods, twelve identity-weighted items | Own choice (8 Nov), unchanged |
| Mossel Bay date | 23 Dec 2015 (first beaching); March 2016 as sensitivity | Pete's ruling |
| Australian coasts | Off unless stated | Pending Pete's ruling on the ratio |
| Ocean models | GLORYS12V1 0.494 m + ERA5; GlobCurrent + ERA5; equal prior weight, likelihood average | Project convention |
| Core | Run J, 00:19 data held out (D0) | Project convention |
| Satellite fit profile | Run J four families, best χ² per 0.5° band | Diagnostic only |
| Tension statistics | Handley and Lemos (2019), ledger bins | Evidence-ledger method |
| Physics | Provisional (windage classes, 60-day delay, kernel 50 km) | Provisional |

## 5. Independent review (9 Nov 2026) — corrections that override sections 2–4

Review report: reviewer artifact eb3de6fb (own scorer written from the Rust source; 84 points, both ocean models). Verdicts and corrections:

- **C1 defect** — confirmed with qualification. The ramp 0.1 / 0.5 / 1 is the module's configured prior since 8 Oct 2026 (commit 4993171), but its
  config comment marks it PROVISIONAL pending the architect's values. It is **not** a pre-registered prior; "pre-registered" refers to Australian option B.
- **C2 scorer = module** — confirmed: max |deviation| 4.98e-7 (GlobCurrent), 4.90e-7 (GLORYS12), equal to the node-table rounding.
- **C3 drift alone** — median robust (−30.1 to −30.5 over ten draw seeds); the share north of 33° S (73–86 %) and the tension are not.
  Tension over draw seeds and curve-mapping choices: p 0.049–0.105 (about 1.6–2.0 σ); over disjoint ocean-sample quarters: median −29.1 to −31.6,
  p 0.019–0.23 (about 1.2–2.3 σ). Quote as a range, provisional.
- **C4 combined shift** — the seed-31 value +0.82° lies at the low end. Eight seeds at 16384 draws: +0.75° to +1.09° (mean +0.92°, SD 0.12);
  65536 draws: +0.98°, +0.90°. Best estimate **about +0.9° ± 0.1° (level draws only; ocean-sample error not assessed)**. The 8 Nov statement that
  16384 draws converge to 0.05° is wrong (effective draws per point median about 400, minimum 39). Detection constant in time: −0.13°.
- **C5 satellite fit** — arithmetic confirmed; inference not sound. The posterior-to-profile ratio contains the Occam factor of the satellite likelihood
  (width of the well-fitting region), not prior volume alone, and the fuel limit is physical. The "fit only" curve in section 3 was normalised within each
  family; best χ² per band across families gives median −30.58° S, mean −29.73° S, 66 % north of 33° S. A marginal likelihood per band under an
  alternative prior is needed before attributing the core's peak.
- **C6 October agreement** — wrong as stated. Like-for-like (7 Nov run, same window, nine finds): drift-alone median −30.78 (256 draws) / −31.35
  (16384 draws, one seed) against October −29.97; correlation per point 0.81 / 0.58. Section 2 compared October with a different configuration.
- **C7 interpretation** — not supported as stated: "mild" and "agrees with most published drift studies" are withdrawn; the principal official drift
  work (CSIRO) places the impact at 32.5–36° S, most likely 35.6° S. The result depends on unruled choices (provisional ramp, Australia off,
  Nautilus Bay and Mpame identity basis 'unclear').
- Further defects to fix: Australian ruled tiers are absolute and constant in time (section 1 said all tiers are ramp offsets; Australia rows differ by
  0.4–1.0°); the tension table clips d ≤ 0 and then reports p ≈ 0 (5.35 / 5.47 σ) or p = 1 — such rows are undefined; the 1-D drift curve interpolates
  over node latitude with 14 tied latitudes (on-arc and ±50 NM points), so results depend on tie order; the unrelated-debris background uses the core
  posterior, so drift alone is not fully independent of the core; Nautilus Bay and Mpame each move the mean north (+0.13°, +0.22° singly).

## 6. Wrong core distribution in all drift work to date (found 9 Nov 2026)

Every drift combination and tension statistic so far, from October to section 5 above, used the end-of-flight accumulator
`run-j-maps-accumulators.npz` key `H_D0_all` (17 Oct end of flight). That is the **evidence-combined Run J mixture: 99.87 % waypoint/airway family**
(strata weights 0.99868 / 0.00094 / 0.00023 / 0.00015). Pete ruled on 31 Oct 2026 that Results do not use the evidence-combined families; the main
configuration is the Davey model + fuel model. The ruled input is the final 7 Nov end of flight, `end-of-flight/final-2026-11-07/results/eof-final-handoff-df.npz`.

Eight level-draw seeds of 16384 (`drift-vs-three-cores-eight-seeds.csv`; impact latitudes, treatment D0 = log-on event only, no 00:19 measurement):

| Core | Core mean | Combined mean (range) | Shift (range) | Combined N of 33° S | ln S | p (σ) |
|---|---|---|---|---|---|---|
| **Davey model + fuel, final end of flight** | −35.94 | −34.52 (−34.78 to −34.26) | +1.43 (+1.17 to +1.68) | 23 % | −0.82 | 0.134 (1.5) |
| Waypoint/airway, final end of flight | −36.47 | −35.45 | +1.01 (+0.84 to +1.19) | 14 % | −1.38 | 0.104 (1.6) |
| Evidence-combined Run J (used so far) | −36.72 | −35.81 | +0.91 (+0.75 to +1.08) | 9 % | −1.45 | 0.089 (1.7) |

Drift alone is nearly unchanged (median −30.2 to −30.25 for all three; the core enters only through the unrelated-debris background).
The 1-D drift curve now averages the on-arc and ±50 NM points at each latitude (no tie-order dependence). Ocean-sample error is not included.

## 7. Smoothed drift-alone curves against the ruled core (9 Nov 2026)

Method (scripts `smooth_stage1.py`, `smooth_stage2.py`, `smooth_figures.py`; table folder `tables/`):

1. Stage 1: for each configuration (headline, Australia 0.25, without Mossel Bay) and each of 16 level-draw seeds of 16384 draws (262,144 draws in all),
   the module-equivalent likelihood is reduced to one number per release point, ocean sample and ocean model: lm = ln mean over draws of exp(sum over items).
   The drift log-likelihood at a point is ln mean over ocean samples of exp(lm). Check: equal to `rescore_analysis.score` to 3e-14 (seed 31, headline).
   The unrelated-debris background uses the ruled core (final end of flight, Davey model + fuel, D0).
2. Stage 2: a Gaussian process (Matérn 3/2, constant mean, amplitude, length scale and nugget by restricted marginal likelihood) smooths ln L along the arc.
   Per-point noise is the bootstrap variance over ocean samples. The fitted length scale reaches its 15° limit and the nugget is about 0.3–0.5 ln units;
   fixed length scales of 2, 4 and 8° give the same result (`smoothed-fixed-length-scale-sensitivity.csv`).
3. Ocean-sample uncertainty: 400 bootstrap resamples of the ocean samples, the same samples at every release point and in both ocean models, because the
   ocean-error realisation is common to all points (samples 1–16 at every point, 17–32 south of 33.25° S, resampled as two blocks). Each replicate is smoothed with the fitted hyperparameters.
4. Grid: uniform 0.1° latitude bins, 40.25–19.9° S. The arc prior (uniform per unit arc length) is the derivative of a cubic fit to the ledger's equal-mass bin count against bin latitude.
   A first run on the ledger's own bins gave jagged curves: the ledger bin latitudes are mass-weighted means over sparse core samples and jitter; that run is discarded.
5. Tension statistic as in the ledger; p and σ are undefined (NaN) where the effective dimension d ≤ 0 (not occurring in these cases).

Results (`smoothed-drift-alone-summary.csv`; medians in degrees south; 5–95 % from the bootstrap):

| Case | Median (range) | North of 33° S | ln S | p | σ (range) |
|---|---|---|---|---|---|
| Two ocean models | 30.0 (29.6–30.4) | 74 % | −0.71 | 0.109 | 1.6 (1.5–1.7) |
| GlobCurrent only | 30.0 (29.5–30.5) | 73 % | −0.63 | 0.112 | 1.6 (1.5–1.7) |
| GLORYS12 only | 29.4 (29.1–29.6) | 89 % | −1.86 | 0.061 | 1.9 (1.8–1.9) |
| Australia ratio 0.25 | 29.5 (29.1–29.8) | 80 % | −1.17 | 0.078 | 1.8 (1.7–1.8) |
| Without Mossel Bay | 32.9 (32.1–33.6) | 51 % | +0.16 | 0.407 | 0.8 (0.0–1.2) |

Satellite and flight data (final end of flight, Davey model + fuel, D0): median 36.4° S. Unsmoothed (tie-averaged) values for comparison: median 30.1° S, p 0.129.

Checks of the smoothing: (a) split halves (even and odd ocean samples within each block) give medians 30.1° S and 29.8° S, p 0.104 and 0.113, and
densities within 10–12 % of the peak of the full-data curve (`smoothed-split-halves.csv`); (b) fixed length scales 2/4/8° give median 30.0/29.9/30.0° S and p 0.119/0.116/0.112.

Limits. Smoothing removes scatter, not bias: ln of a mean over few heavy-tailed ocean samples is biased low where the spread is large (south), and 16/32 samples may not remove it.
The bootstrap range is conditional on the smoothness assumption and on the samples drawn. The earlier statement that the tension is 1.5σ (8 seeds, ledger bins) is replaced by 1.6σ here.
The combined (drift × core) shift of section 6 uses the per-point inverse-distance method, not this smoothing, and is unchanged (+1.43°, eight seeds +1.17° to +1.68°).

## 8. Figure set with the requested legend wording and the combined density (9 Nov 2026)

Script `smooth_figures_v2.py`. Combined density = satellite and flight density (final end of flight, Davey model + fuel, D0, 0.1° bins) × smoothed drift likelihood (headline, two ocean models), normalised.
This is the one-dimensional product used in the tension statistic (p_AB = p_core × L_drift). Figures: A drift standalone curves with the satellite and flight data (legend wording as requested);
B = A plus the combined density; C = satellite and flight data, drift standalone (two ocean models) and combined; D = combined with and without the Mossel Bay item; E = two-panel version of A.

| Density | Mean (° S) | Median (° S) | North of 33° S |
|---|---|---|---|
| Satellite and flight data | 35.95 | 36.4 | 8.1 % |
| Combined (two ocean models) | 34.79 | 35.7 | 18 % |
| Combined, excluding Mossel Bay | 35.71 | 36.1 | 7.5 % |

The shift of the mean from this smoothed one-dimensional product is +1.15° (+0.23° without Mossel Bay). The per-point reweighting of the two-dimensional core samples in section 6 gives +1.43° (eight draw seeds +1.17° to +1.68°),
N of 33° S 23 %; the two methods differ by 0.28°, inside the seed range. The jagged outline of the combined curve north of 33° S is sampling noise in the core (few samples there), multiplied by the smooth drift likelihood.

### 8a. Update (9 Nov 2026, later): legend order, dash key, figure F, Mossel Bay mode shift

- Legend order in figures A, B and E: satellite and flight data; GlobCurrent only; GLORYS12 only; two ocean models; two ocean models with no finds on Australian coasts; two ocean models excluding Mossel Bay.
  The long-dash key (excluding Mossel Bay) is now drawn with legend handles of 5.5 font heights so that two full dashes show; the earlier key looked like a dash-dot line.
- The curve excluding Mossel Bay uses no Australian term (Australian coasts off, as in the headline). Only the dotted curve uses the absence of finds on Australian coasts (detection on populated Australian coasts 0.25 of that on the find coasts). Captions now say so.
- New scoring pass (`smooth_stage1.py au025nomb`, 16 seeds × 16384 draws): excluding Mossel Bay together with the Australian term. The five earlier cases reproduce identically after adding it (same bootstrap stream).
- Figure F: drift curves with and without the Mossel Bay item, each with and without the Australian term.

| Drift model (two ocean models) | Median (° S) | 5–95 % | Mean | North of 33° S | Tension σ (5–95 %) |
|---|---|---|---|---|---|
| Standalone | 30.0 | 29.6–30.4 | 30.3 | 74 % | 1.6 (1.5–1.7) |
| No finds on Australian coasts | 29.5 | 29.1–29.8 | 29.7 | 80 % | 1.8 (1.7–1.8) |
| Excluding Mossel Bay | 32.9 | 32.1–33.6 | 32.4 | 51 % | 0.8 (0.0–1.2) |
| Excluding Mossel Bay, no finds on Australian coasts | 31.4 | 30.8–32.0 | 31.3 | 63 % | 1.4 (1.3–1.6) |

Position of the highest point: standalone 29.5° S (0.109 per degree; second maximum 34.0° S, 0.068); excluding Mossel Bay 34.8° S (0.104; the northern part becomes a plateau of 0.068 at 29.7° S);
excluding Mossel Bay with the Australian term 34.3° S (0.101). The highest point therefore moves 5.3° south when the single item is removed, while the median moves 2.9° and the mean 2.1°,
because without that item the distribution is broad (density ratio 35° S : 30° S is 1.52 without it and 0.57 with it). The Australian term moves the median north by 0.5° with the item and 1.5° without it.
