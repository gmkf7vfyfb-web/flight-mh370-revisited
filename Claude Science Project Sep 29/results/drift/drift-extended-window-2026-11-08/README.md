# Ocean drift: extended-window run and offline rescoring (8 November 2026)

## Summary
- The drift evidence, with all western Indian Ocean coasts, four detection periods and twelve items, moves the core mean **0.15° south** (−36.72° to −36.87°). The median moves from −37.13° to −37.19°.
- The probability north of 33° S falls from 3.2 % to 0.9 %. The evidence ratio of the core against a uniform prior along the arc is ln R = +0.85.
- The earlier northward shifts (+0.61° on 7 November, +1.17° on 8 November) are **superseded**. Two causes are found:
  1. The level marginalisation used 256 draws. At that count the shift scatters by up to about 0.6° with the draw seed alone (+0.69° to +1.25° over six seeds for the configuration as first scored). At 16,384 draws two seeds agree to 0.05°.
  2. With one detection level for 1 Mar 2016 – 30 Jan 2017, the few qualifying finds after June 2016 count as evidence for fast, northern paths. A fourth period from 1 Jul 2016, or the coasts with no finds, removes this.
- The two independent runs agree when scored the same way (old window, nine finds: −0.31° and −0.38°).
- Mossel Bay alone still moves the estimate north (+1.11°). The Australian non-finds also move it north (ratio 0.25: +0.19°; ratio 1: +0.57°). So does GLORYS12 alone (+0.50°).
- The Monte Carlo uncertainty of the headline mean is about ±0.2° (particle halves +0.07° and −0.30°).

## What was run
- Particle run (deskstar, 7–8 Nov; power cycle at about 01:35 UTC, resumed, no completed work lost): 84 release points on the 7th arc, two ocean models, 16 ocean samples per point (32 south of 33.25° S), 6250 particles per object type per sample, finds window to 30 Jan 2017. Every beaching written to `arrivals.bin` (8.0 GB, kept on deskstar). Binary `bin-arr` (SHA-256 f86b14178c00df8b), branch `hypothesis/debris-drift` e56a39d.
- Offline rescoring: a `rescore` entry in the drift module re-runs the module's own recovery code (`Recovery::coefficients`, `shadow_coefficients`) on the stored arrivals with any segment map, window, periods, finds, freshness marks and bandwidths. It reproduces the module coefficients to 2.2 × 10⁻⁸ (67,200 find kernels and all class totals; f32 storage of the particle weights).
- Scoring: `final_analysis.py` with 16,384 level draws (seed 31); identity-weighted mixture for items with grade below confirmed; same core posterior and interpolation as the 7 November analysis.

## Model ladder (nine finds unless stated; core D0; 16,384 level draws)
| Case | Mean (°) | Median (°) | 5–95 % (°) | Shift of mean (°) | North of 33° S (%) | ln R core vs uniform |
|---|---|---|---|---|---|---|
| Satellite and flight data only (core) | -36.72 | -37.13 | -38.41 to -33.87 | 0 | 3.2 | — |
| As first scored: nine finds, window to 30 Jan 2017, 3 periods, 6 find coasts | -36.05 | -36.99 | -38.09 to -30.13 | +0.66 | 9.0 | -0.71 |
| Window to 30 Jun 2016 (this run) | -37.09 | -37.09 | -38.27 to -35.39 | -0.37 | 0.5 | +1.08 |
| Fourth detection period from 1 Jul 2016 | -36.90 | -37.07 | -38.19 to -34.53 | -0.18 | 1.4 | +0.73 |
| … and Linga Linga | -36.91 | -37.09 | -38.23 to -34.51 | -0.19 | 1.3 | +0.74 |
| All western Indian Ocean coasts (3 periods) | -36.90 | -37.13 | -38.31 to -34.37 | -0.18 | 1.3 | +0.72 |
| … twelve items, identity-weighted | -36.88 | -37.19 | -38.31 to -34.35 | -0.16 | 1.0 | +0.82 |
| All coasts and four periods, nine finds | -36.92 | -37.13 | -38.31 to -34.43 | -0.20 | 1.2 | +0.76 |
| **Headline: all coasts, four periods, twelve items, identity-weighted** | -36.87 | -37.19 | -38.31 to -34.39 | -0.15 | 0.9 | +0.85 |

## Changes to the headline
| Case | Mean (°) | Median (°) | 5–95 % (°) | Shift of mean (°) | North of 33° S (%) | ln R core vs uniform |
|---|---|---|---|---|---|---|
| All identity probabilities set to 1 | -36.86 | -37.17 | -38.31 to -34.39 | -0.15 | 0.9 | +0.86 |
| Add eight items identified partly from drift (sensitivity) | -36.99 | -37.13 | -38.65 to -34.85 | -0.27 | 0.4 | +0.81 |
| Without Nautilus Bay and Mpame | -36.90 | -37.15 | -38.29 to -34.43 | -0.18 | 1.1 | +0.78 |
| Time ashore: fresh marks 10 d, 10 d, 14 d | -36.96 | -37.17 | -38.39 to -34.89 | -0.24 | 0.4 | +1.28 |
| Time ashore: fresh marks 3 d, 3 d, 14 d | -36.86 | -37.03 | -38.61 to -34.73 | -0.15 | 0.4 | +1.26 |
| Mossel Bay at second beaching (21-22 Mar 2016) | -36.95 | -37.27 | -38.31 to -34.57 | -0.23 | 0.7 | +0.87 |
| Three official alternative dates | -36.84 | -37.15 | -38.23 to -34.37 | -0.12 | 0.9 | +0.86 |
| Other coasts at the find-coast level | -36.70 | -37.07 | -38.23 to -34.17 | +0.01 | 1.3 | +0.69 |
| Other coasts at 0.1 of the find-coast level | -36.95 | -37.23 | -38.33 to -34.55 | -0.24 | 0.8 | +0.92 |
| Populated new coasts also at 0.3 | -36.82 | -37.15 | -38.29 to -34.31 | -0.10 | 1.0 | +0.80 |
| Australia ratio 1.0 | -36.14 | -36.57 | -37.85 to -33.49 | +0.57 | 3.1 | +0.30 |
| Australia ratio 0.25 | -36.53 | -36.97 | -38.09 to -33.93 | +0.19 | 1.7 | +0.59 |
| Australia ratio 0.05 | -36.77 | -37.11 | -38.23 to -34.23 | -0.05 | 1.1 | +0.78 |
| All but Mossel Bay | -37.01 | -37.27 | -38.33 to -34.85 | -0.29 | 0.5 | +0.99 |
| All but Mossel Bay and Paindane | -37.10 | -37.25 | -38.37 to -35.17 | -0.38 | 0.3 | +0.98 |
| Only Mossel Bay | -35.60 | -36.83 | -38.15 to -27.91 | +1.11 | 12.3 | -1.14 |
| Only the flaperon | -36.81 | -37.13 | -38.39 to -34.17 | -0.10 | 2.2 | +0.38 |
| Kernel 25 km | -36.86 | -37.21 | -38.43 to -34.21 | -0.15 | 1.0 | +0.72 |
| Kernel 100 km | -36.79 | -37.11 | -38.19 to -34.33 | -0.07 | 1.3 | +0.75 |
| Kernel 200 km | -36.80 | -37.09 | -38.17 to -34.39 | -0.09 | 1.4 | +0.74 |
| Particle half a | -36.64 | -37.03 | -38.11 to -34.19 | +0.07 | 1.0 | +0.84 |
| Particle half b | -37.02 | -37.37 | -38.29 to -34.53 | -0.30 | 0.9 | +1.06 |
| Headline, GlobCurrent only | -36.88 | -37.19 | -38.31 to -34.41 | -0.16 | 0.9 | — |
| Headline, GLORYS12 only | -36.22 | -36.69 | -37.91 to -33.65 | +0.50 | 2.8 | — |

## Other core posteriors (headline)
| Core posterior | Core mean (°) | Headline mean (°) | Shift (°) |
|---|---|---|---|
| H_D1_all | -36.96 | -37.07 | -0.10 |
| H_D2_all | -36.80 | -36.97 | -0.17 |

## Two independent runs, same configuration
| Old window (to 30 Jun 2016), nine finds | Shift (°) | North of 33° S (%) |
|---|---|---|
| 7 Nov run (seeds 101-132) | -0.31 | 1.0 |
| extended run rescored to the old window (seeds 201-232) | -0.37 | 0.5 |
| both runs pooled | -0.37 | 0.6 |

Node-level ln L differences between the two runs: RMS 0.94 (GlobCurrent) and 1.49 (GLORYS12) south of 33.25° S; 1.03 and 0.72 to the north.

## Level-draw convergence (shift of the mean, °)
| Level draws | First scored, seed 21 | First scored, seed 22 | Headline-type, seed 21 | Headline-type, seed 22 |
|---|---|---|---|---|
| 256 | +0.69 | +0.91 | -0.24 | -0.09 |
| 1024 | +0.53 | +0.78 | -0.04 | -0.18 |
| 4096 | +0.69 | +0.76 | -0.14 | -0.18 |
| 16384 | +0.74 | +0.78 | -0.15 | -0.14 |

## Particle and environment convergence (headline, extended window)
| Ocean model | Band | 4-sample groups: RMS ln L difference from the pooled value | Particle halves: RMS difference (ln) | Samples with no Mossel Bay kernel hit |
|---|---|---|---|---|
| globcurrent | south of 33.25 S | 2.73 | 1.26 | 9 % |
| globcurrent | 33.25 S and north | 0.87 | 1.09 | 0 % |
| glorys12 | south of 33.25 S | 3.07 | 2.11 | 21 % |
| glorys12 | 33.25 S and north | 0.99 | 1.08 | 0 % |

## Key assumptions and modelling choices
| Item | Choice | Status |
|---|---|---|
| Core posterior | End-of-flight run J, families pooled, 00:19 data held out (D0); D1 and D2 also reported | Ruling (earlier) |
| Ocean models | GLORYS12V1 (0.494 m) + ERA5 and Copernicus GlobCurrent (0 m) + ERA5, equal weight; GlobCurrent wind factor reduced by U(0.60, 0.75) % | Pete's default (a), 17 Oct |
| Object response | Flaperon as measured by CSIRO (1.2 % wind factor, 0.10 ± 0.03 m/s leeway, 0–30° left of downwind); exterior panels N(1.2 %, 0.3 %) cut to 0.5–2 %; interior panels median 2.5 % | Ruling D-a (flaperon); own choice (others, unmeasured) |
| Stokes drift | Carried by the wind factor; no separate field | Ruling D-b |
| Find window | To 30 Jan 2017 (ocean and wind data end 31 Jan 2017) | Own choice, from Pete's "use all data" |
| Detection periods | Four: before 29 Jul 2015; to 29 Feb 2016; to 30 Jun 2016; to 30 Jan 2017 | Own choice (headline); three periods as sensitivity |
| Coasts | Original six find coasts and ten Australian segments, plus nine new western Indian Ocean segments | Own choice |
| Detection-level priors | Log-normal, σ = 1 per coast and period; find coasts and populated new South African and southern Mozambique coasts at 1; other new coasts at 0.3; Australian coasts carry no information unless stated | Own choice (tiers set by population and search effort, not by finds) |
| Items | Nine finds plus Linga Linga, Nautilus Bay and Mpame; weights confirmed 1, almost certain 0.98, highly likely 0.9, likely 0.7 | Pete: use everything incl. 'likely'; weights own choice |
| Unrelated debris | Same prior-predictive distribution of place and time as MH370 debris | Own choice |
| Excluded | Eight items identified partly from drift (sensitivity only: circular); Sandravinany (date range past the window); Asian coasts (no segment) | Own choice |
| Mossel Bay date | 23 Dec 2015 (first beaching); 21–22 Mar 2016 as sensitivity | Pete, 7 Nov |
| Time ashore | Exponential delay, mean 60 days; fresh-arrival marks as sensitivity | Own choice |
| Find-place tolerance | 50 km Gaussian (25, 100, 200 km as sensitivity) | Earlier default |
| Level draws | 16,384 (module default 256 is not adequate) | Own choice, from the draw study |

## Limits and open items
1. GLORYS12 alone gives +0.50°, GlobCurrent alone −0.16°. The combination follows GlobCurrent, because its likelihood is higher. The disagreement between ocean models is the largest single uncertainty.
2. Mossel Bay alone gives +1.11°. Early arrivals in South Africa are under-predicted (posterior predictive check of 7 November). Exterior-panel windage and transport speed are the candidate causes. The wide-windage sensitivity needs a new particle run.
3. Particle Monte Carlo noise is about ±0.2° in the mean. More ocean samples south of 33° S would reduce it.
4. Sandravinany and later finds need ocean and wind data after 31 Jan 2017 (GLORYS12, WAVERYS, ERA5) and a new run. GlobCurrent is downloaded to 31 Dec 2018.
5. The clean-item model (time ashore without marine life) needs delay-binned coefficients: a rescore extension, with no new particles needed.
6. The evidence-ledger and suspiciousness figures must be recomputed with these surfaces and 16,384 draws.
7. Module default of 256 level draws: raise it in the module, or score offline as here.
