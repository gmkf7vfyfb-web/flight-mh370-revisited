# Pléiades module review: run C headline redrawn to the 11 Oct rulings (stand-in note `headline-rho025-standin.md`)

11 Oct 2026, Pléiades module. Labels as in the note: **core run C NOT CONVERGED**; EoF physics PROVISIONAL (G13); conditional on H.

**Verdict: adopted, with the split-half now run and one label to change (point 3).**

## 1. Independent reproduction (passes)
- **Recomputation.** I recomputed all nine ρ ≠ 0 / both-model rows myself: my own mixture loader, the published `joint-surface-rho*.f32`,
  and `closeup_figure.stats`; no stand-in code. The 90 % area, the mean and the share outside past searches equal the stand-in's
  `headline-rho025-stats.csv` at every printed digit.
- **Arithmetic in the findings checked:**
  - ρ 0.25 against ρ 0: +8.5 / +8.9 / +14.0 %; ρ 0.5 against ρ 0: +17.6 / +17.9 / +25.8 %;
  - both models against GLORYS12 at ρ 0.25: +34 / +42 / +19 %;
  - new headline against the old one: −18 / −23 / −6 %;
  - mean south shift ρ 0 → 0.5: 0.09 / 0.10 / 0.11°.
- **The ρ = 0 surface check.** The stand-in reports an ln-ratio sd of 0.006 / 0.010 over the whole grid. My 1e-5 was over cells within
  30 nat of the maximum. Both are right; the difference lies in far-field cells with no conditional mass, and the conditional is
  identical (28,478.18 km²).
- **Scripts reviewed:** `headline_rho_standin.py`, `headline_rho_figure_standin.py` and `headline_rho_splithalf_standin.py`.
  - `rho_L` follows `build_branch`: a not-computed cell has zero likelihood, and the two-model mean is taken in likelihood.
  - The split-half script is `mixture_splithalf.main` with the likelihood set replaced; the seeds and partitions are the same.
  - No issue found. The figure's footnote and labels follow the house style.

## 2. Split-half σ for the three settings that were missing
Run under `lockf -k /tmp/.mh370-heavy.lock` (it waited 25 min for the lock; the run took 5 min; `headline-rho025-standin/splithalf-rho.csv`).
± = rms over the three 4 + 4 seed partitions of (half A − half B)/2. After all searches, P + all four COSMO, `unpowered`, strata re-weighted.

| 00:19 option | setting | 90 % km² ± σ | 50 % km² ± σ | mean under H ± σ | share left by searches, under H | ln S ± σ | mean shift NM ± σ |
|---|---|---|---|---|---|---|---|
| 00:19 R600 BTO + Raw BFO | **ρ 0.25, GLORYS12 only (headline)** | 30,998 ± 227 (0.7 %) | 5,817 ± 25 | 36.008 ± 0.002 S, 92.378 ± 0.009 E | 0.412 ± 0.002 | +0.13 ± 0.07 | 36 ± 5.1 |
| 00:19 R600 BTO + Raw BFO | ρ 0, GLORYS12 only | 28,478 ± 214 (0.8 %) | 5,470 ± 20 | 35.961 ± 0.002 S, 92.380 ± 0.009 E | 0.395 ± 0.003 | -0.01 ± 0.07 | 38 ± 5.1 |
| 00:19 R600 BTO + Raw BFO | ρ 0.5, GLORYS12 only | 33,493 ± 248 (0.7 %) | 6,138 ± 27 | 36.047 ± 0.003 S, 92.373 ± 0.009 E | 0.421 ± 0.002 | +0.24 ± 0.07 | 34 ± 5.1 |
| 00:19 R600 BTO + Raw BFO | ρ 0.25, both models | 41,597 ± 226 (0.5 %) | 7,582 ± 36 | 35.953 ± 0.002 S, 92.363 ± 0.011 E | 0.366 ± 0.002 | -0.32 ± 0.07 | 38 ± 5.1 |
| 00:19 R600 BTO Only | **ρ 0.25, GLORYS12 only (headline)** | 34,997 ± 324 (0.9 %) | 6,980 ± 88 | 36.061 ± 0.004 S, 92.398 ± 0.006 E | 0.450 ± 0.001 | -0.67 ± 0.08 | 95 ± 5.2 |
| 00:19 R600 BTO Only | ρ 0, GLORYS12 only | 32,252 ± 247 (0.8 %) | 6,608 ± 91 | 36.006 ± 0.004 S, 92.391 ± 0.006 E | 0.428 ± 0.001 | -0.83 ± 0.08 | 97 ± 5.2 |
| 00:19 R600 BTO Only | ρ 0.5, GLORYS12 only | 38,016 ± 440 (1.2 %) | 7,326 ± 98 | 36.106 ± 0.004 S, 92.402 ± 0.007 E | 0.464 ± 0.001 | -0.54 ± 0.08 | 93 ± 5.2 |
| 00:19 R600 BTO Only | ρ 0.25, both models | 49,540 ± 341 (0.7 %) | 9,792 ± 167 | 35.994 ± 0.004 S, 92.421 ± 0.009 E | 0.408 ± 0.001 | -1.17 ± 0.08 | 99 ± 5.1 |
| 00:19 Held Out | **ρ 0.25, GLORYS12 only (headline)** | 77,420 ± 351 (0.5 %) | 13,325 ± 119 | 35.572 ± 0.011 S, 91.778 ± 0.016 E | 0.506 ± 0.004 | -0.29 ± 0.07 | 69 ± 3.9 |
| 00:19 Held Out | ρ 0, GLORYS12 only | 67,914 ± 275 (0.4 %) | 12,034 ± 67 | 35.517 ± 0.011 S, 91.758 ± 0.016 E | 0.495 ± 0.004 | -0.35 ± 0.07 | 72 ± 3.8 |
| 00:19 Held Out | ρ 0.5, GLORYS12 only | 85,461 ± 459 (0.5 %) | 14,241 ± 169 | 35.628 ± 0.011 S, 91.804 ± 0.016 E | 0.510 ± 0.003 | -0.24 ± 0.07 | 66 ± 3.9 |
| 00:19 Held Out | ρ 0.25, both models | 92,331 ± 365 (0.4 %) | 17,843 ± 148 | 35.435 ± 0.012 S, 91.659 ± 0.017 E | 0.501 ± 0.004 | -0.52 ± 0.08 | 77 ± 3.5 |

**Reproduction inside the same run:** the hook rows reproduce the module's `splithalf.csv` exactly.

| 00:19 option | hook both models, this run | module splithalf.csv | ρ 0 GLORYS12 surface, this run | module GLORYS12 only |
|---|---|---|---|---|
| 00:19 R600 BTO + Raw BFO | 37,887.3 ± 222.2 | 37,887.3 ± 222.2 | 28,478.2 ± 213.6 | 28,478.2 ± 213.6 |
| 00:19 R600 BTO Only | 45,709.4 ± 269.9 | 45,709.4 ± 269.9 | 32,252.4 ± 247.1 | 32,252.4 ± 247.1 |
| 00:19 Held Out | 82,613.8 ± 315.3 | 82,613.8 ± 315.3 | 67,913.8 ± 274.6 | 67,913.8 ± 273.7 |

The ρ 0 GLORYS12 σ differs from the hook's by ≤ 0.9 km² (Held Out), which comes from far-field cells (point 1).

**Reading:**
- σ is 0.4-1.2 % of the 90 % area in every setting. The largest is R600 BTO Only at ρ 0.5, 1.2 %.
- ρ = 0.25 against ρ = 0 is +2,520 / +2,745 / +9,506 km² (R600 BTO + Raw BFO / BTO Only / Held Out), that is 11 / 8 / 27 σ of one
  setting. The ρ effect is resolved; σ of the difference is smaller still, because both settings use the same seeds.
- From ρ = 0 to ρ = 0.5, ln S rises by +0.25 / +0.29 / +0.11, which is 3.6 / 3.6 / 1.6 σ (σ ≈ 0.07-0.08).
- **The module's Monte Carlo noise is not the limit. Core run C's non-convergence is.**

## 3. One label to change: "GlobCurrent windage double-counted"
The note and figure label the two-model column "GlobCurrent windage double-counted (drift audit F1)". That reads as though the 19-42 % extra
width were an artefact of F1. **The module's own F1 measurement says otherwise** (`results/pleiades/windage-relative/README.md`, on
reference-289):
- lowering GlobCurrent's windage by 0.60-0.75 % U10 shrinks the two-model 90 % region by only **1.4-2.0 %** and moves the mean < 1 km;
- the reason is that the 15-day drift is dominated by the ~100 km transport error, against about 60 km from the windage mismatch.

So nearly all of the between-model width is genuine disagreement between GLORYS12 and GlobCurrent, and leaving it out of the headline
narrows the region by 19-42 %, not by 2 %. Proposed label: "both models; GlobCurrent windage not yet product-relative (drift audit F1;
measured effect about −2 % in area)".

**The ruling itself (GLORYS12-only headline until the GlobCurrent arm is product-relative) is architecture's and Pete's.** I do not change it.
I have put the measurement in front of architecture, and the module's next item, a product-relative GlobCurrent arm at ρ 0.25 on run C,
closes the question either way.

## 4. Not changed
- The seabed (GEBCO) close-up was not redrawn for the ρ 0.25 headline (stand-in deviation 2). It is to follow with the product-relative
  item, so it is drawn once.
- `~v212` and `silent` were not redrawn at ρ 0.25 (coverage note). They are declared, and their effect at ρ 0 is in the module's README.
