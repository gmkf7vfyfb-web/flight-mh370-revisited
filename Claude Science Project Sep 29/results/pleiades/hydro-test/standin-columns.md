# Hydroacoustic test of the Pléiades hypothesis: Pléiades-side columns and source package on core (b) (stand-in)

10 Oct 2026. **Run by an architecture stand-in on the Pléiades module's behalf; module to review.**
Labels: core (b) not converged (split-half) · two-tank bookkeeping only · Pléiades/COSMO transport errors treated as
independent (correlation pending from ocean transport) · GlobCurrent windage as run (debris-drift audit F1) · PROVISIONAL.
Interface: architecture.md ~20:00 and ~20:10 UTC. Design: `results/pleiades/hydro-conditional-test-design.md`.

## What was built
Location: `/Users/pete/Downloads/mh370-exchange/pleiades/hydro-test/next-run-b/` (README.md there has the full provenance; `READY` written last).
1. `<stratum>/seed-<k>/pleiades-lnL.npy` for all 4 strata × 4 seeds (51.2 M rows; 2.6 GB in total with the sources), row-aligned with end of flight's `impacts.npy` (`row`, `parent` checked equal). Fields: `stratum`, `seed`, `row`, `parent`, `lnL_{pleiades,cosmo,both}_{glorys12,globcurrent,mean}`, `not_computed`; `COLUMNS.txt`, `SHA256SUMS`.
2. `sources.npz` (00:19 R600 BTO Only), `sources-0019-held-out.npz`, `sources-0019-r600-bto-raw-bfo.npz`: 5,000 rows each, defensive mixture ½ flight posterior + ½ posterior under H, full 106-column state, `w_flight`, `w_H` (re-weighted strata) and `w_flight_fixed`, `w_H_fixed` (fixed strata) relative to the mixture, with ESS.
3. Scripts: `standin-scripts/export_surfaces.sh` (runs the module's own export tests), `standin-scripts/build_columns.py` (imports `branch_eof289` and EoF's `displacement_hist` read-only). Tables: `standin-ess-per-seed.csv`, `standin-strata-weights.csv`, `standin-reproduction.csv`, `standin-mixture-before-search.csv`, `standin-summary.json`.

**Likelihood, exactly as the module scores impacts.** The module never evaluates its likelihood at an exact impact position. It exports its hook on a 0.05° grid (85-103 E, 43-25 S) and multiplies each grid cell's impact mass by the cell value (`branch_eof289.histograms` + `build_branch`). The columns give each impact its cell's value with the same bin edges. Hook: `hypothesis/pleiades` 74332d0. The release tables and surfaces were regenerated with the module's own `#[ignore]` export tests, because its gitignored run tree is not reachable (sha256 in the exchange README). Configuration: rating-5 objects in 6 clusters at equal weights (`rho4-0`), all four COSMO-SkyMed contacts (C4, pass-marginal), GLORYS12 + ERA5 and GlobCurrent daily + ERA5 at equal weight, measured transport error (run.toml), debris released at a fixed 00:20 UTC.

**Weights:** the module's own path in `branch_eof289`: for R600 BTO Only, EoF's `option_posteriors` key `r600-bto__other+alive`; for Held Out and R600 BTO + Raw BFO, `weight × exp(loglik) × exp(EoF alive factor)`. Log-on not from fuel exhaustion; transmitting at 00:19:37 (variant (a), as ruling ~19:10 B allows until EoF exposes (b)).

## Reproduction check (passes)
Per stratum, before any search, the 90 % area and the mean under H computed from the columns (weights w_i × exp(lnL_<field>_mean)) equal the module's published `results/pleiades/next-run-b-core/<stratum>/by-0019-option.csv` in **24 of 24 rows** (P and P+C4, all three options), to the published rounding (1 km², 0.001°). The same summary computed through the module's own grid path (`build_branch` × grid histogram) agrees to 0.0 km² and 1e-8°. 00:19 R600 BTO Only, Pléiades + all four COSMO contacts:

| 00:19 option | stratum | field | published 90 % area, km² | from columns | published mean | from columns |
|---|---|---|---|---|---|---|
| 00:19 R600 BTO Only | next-descent-climb | P | 78,282 | 78,282 | -35.956, 91.868 | -35.956, 91.868 |
| 00:19 R600 BTO Only | next-descent-climb | P+C4 | 40,898 | 40,898 | -35.663, 92.184 | -35.663, 92.184 |
| 00:19 Held Out | next-descent-climb | P | 118,079 | 118,079 | -35.523, 91.457 | -35.523, 91.457 |
| 00:19 Held Out | next-descent-climb | P+C4 | 65,927 | 65,927 | -35.364, 91.721 | -35.364, 91.721 |
| 00:19 R600 BTO + Raw BFO | next-descent-climb | P | 66,632 | 66,632 | -35.926, 91.744 | -35.926, 91.744 |
| 00:19 R600 BTO + Raw BFO | next-descent-climb | P+C4 | 35,595 | 35,595 | -35.598, 92.144 | -35.598, 92.144 |
| 00:19 R600 BTO Only | next-free | P | 80,804 | 80,804 | -35.909, 91.972 | -35.909, 91.972 |
| 00:19 R600 BTO Only | next-free | P+C4 | 43,560 | 43,560 | -35.641, 92.226 | -35.641, 92.226 |
| 00:19 Held Out | next-free | P | 122,944 | 122,944 | -35.463, 91.528 | -35.463, 91.528 |
| 00:19 Held Out | next-free | P+C4 | 68,042 | 68,042 | -35.336, 91.740 | -35.336, 91.740 |
| 00:19 R600 BTO + Raw BFO | next-free | P | 68,715 | 68,715 | -35.865, 91.865 | -35.865, 91.865 |
| 00:19 R600 BTO + Raw BFO | next-free | P+C4 | 37,678 | 37,678 | -35.582, 92.182 | -35.582, 92.182 |
| 00:19 R600 BTO Only | next-repro-radar | P | 71,147 | 71,147 | -35.841, 92.100 | -35.841, 92.100 |
| 00:19 R600 BTO Only | next-repro-radar | P+C4 | 41,031 | 41,031 | -35.626, 92.261 | -35.626, 92.261 |
| 00:19 Held Out | next-repro-radar | P | 112,986 | 112,986 | -35.424, 91.678 | -35.424, 91.678 |
| 00:19 Held Out | next-repro-radar | P+C4 | 62,194 | 62,194 | -35.338, 91.818 | -35.338, 91.818 |
| 00:19 R600 BTO + Raw BFO | next-repro-radar | P | 61,616 | 61,616 | -35.780, 92.012 | -35.780, 92.012 |
| 00:19 R600 BTO + Raw BFO | next-repro-radar | P+C4 | 36,139 | 36,139 | -35.565, 92.206 | -35.565, 92.206 |
| 00:19 R600 BTO Only | next-routes | P | 83,186 | 83,186 | -35.886, 92.005 | -35.886, 92.005 |
| 00:19 R600 BTO Only | next-routes | P+C4 | 42,788 | 42,788 | -35.595, 92.337 | -35.595, 92.337 |
| 00:19 Held Out | next-routes | P | 120,217 | 120,217 | -35.599, 91.504 | -35.599, 91.504 |
| 00:19 Held Out | next-routes | P+C4 | 67,161 | 67,161 | -35.393, 91.888 | -35.393, 91.888 |
| 00:19 R600 BTO + Raw BFO | next-routes | P | 68,423 | 68,423 | -35.843, 91.869 | -35.843, 91.869 |
| 00:19 R600 BTO + Raw BFO | next-routes | P+C4 | 35,963 | 35,963 | -35.524, 92.284 | -35.524, 92.284 |

**Not reproduced:** the mixture-level after-search numbers in `next-run-b-core/closeups/closeup-stats.csv` (52,507 / 53,544 km²). They need the searched-areas module's per-impact seabed-search column, which is not in the exchange and which this task does not produce. The per-stratum check covers the same likelihood and weights. The P+C4 mixture under H **before** search, from the columns:

| 00:19 option | strata weights | 90 % area under H, km² | mean under H | 90 % area, flight only, km² |
|---|---|---|---|---|
| 00:19 R600 BTO Only | fixed | 42,782 | 35.639 S 92.231 E | 319,984 |
| 00:19 R600 BTO Only | reweighted | 42,807 | 35.639 S 92.230 E | 318,229 |
| 00:19 Held Out | fixed | 66,847 | 35.340 S 91.756 E | 519,714 |
| 00:19 Held Out | reweighted | 66,847 | 35.340 S 91.756 E | 519,659 |
| 00:19 R600 BTO + Raw BFO | fixed | 38,259 | 35.579 S 92.185 E | 213,976 |
| 00:19 R600 BTO + Raw BFO | reweighted | 38,309 | 35.580 S 92.184 E | 211,210 |

## ESS under H, per stratum and seed (rows; parents in brackets)
Weight under H = w_i × exp(lnL_both_mean), with not-computed rows excluded.

**00:19 R600 BTO Only**
| stratum | seed 1 | seed 2 | seed 3 | seed 4 |
|---|---|---|---|---|
| next-free | 112,544 (13,891) | 93,131 (9,959) | 108,795 (12,970) | 52,519 (6,695) |
| next-repro-radar | 145,381 (16,197) | 127,459 (13,939) | 141,981 (16,058) | 155,883 (17,189) |
| next-descent-climb | 98,381 (11,565) | 70,755 (7,810) | 49,771 (6,467) | 109,375 (12,493) |
| next-routes | 89,811 (9,648) | 100,460 (10,453) | 97,759 (10,157) | 40,880 (4,278) |

ESS without H (rows), range over seeds: next-free 1,588,663-2,073,864, next-repro-radar 1,525,952-1,654,983, next-descent-climb 1,726,980-1,997,331, next-routes 1,815,395-1,913,506.

**00:19 Held Out**
| stratum | seed 1 | seed 2 | seed 3 | seed 4 |
|---|---|---|---|---|
| next-free | 314,021 (34,224) | 250,015 (24,694) | 311,872 (33,673) | 161,418 (17,731) |
| next-repro-radar | 381,014 (39,552) | 379,282 (38,896) | 358,668 (36,992) | 386,044 (37,921) |
| next-descent-climb | 264,328 (27,763) | 201,410 (20,884) | 153,259 (18,689) | 288,860 (28,653) |
| next-routes | 214,445 (20,485) | 223,850 (21,099) | 234,971 (21,587) | 105,857 (10,091) |

**00:19 R600 BTO + Raw BFO**
| stratum | seed 1 | seed 2 | seed 3 | seed 4 |
|---|---|---|---|---|
| next-free | 5,776 (3,320) | 4,957 (2,659) | 5,158 (2,842) | 2,263 (1,475) |
| next-repro-radar | 6,556 (3,600) | 6,255 (3,209) | 6,959 (3,758) | 7,236 (3,936) |
| next-descent-climb | 4,636 (2,600) | 3,849 (1,993) | 2,426 (1,356) | 5,196 (2,832) |
| next-routes | 3,794 (1,999) | 4,220 (2,275) | 4,267 (2,222) | 1,844 (910) |

- R600 BTO Only: 40,900-155,900 rows (4,300-17,200 parents) per seed. The design note's 90,000-145,000 rows (10,000-16,000 parents) was read from seed 1 only. Seeds 3-4 of free, descent-climb and routes are lower (to 40,900 rows). So the per-seed spread is itself part of the Monte Carlo error that hydroacoustics' split-half will show.
- R600 BTO + Raw BFO under H: 1,844-7,236 rows (910-3,936 parents) per seed. These are usable, but an R_hyd split-half on this option will carry larger Monte Carlo noise.
- Not computed: 0.3-2.2 % of rows per seed (mostly outside the grid; 545-4,444 rows per seed lie in cells at the 25 S edge). They hold 0.1-3.1 % of the flight-posterior weight, by seed and option (`standin-ess-per-seed.csv`).

## Source packages (5,000 rows each; ESS of 5,000)
| 00:19 option | rows | unique | ESS w_flight | ESS w_H | ESS w_flight (fixed strata) | ESS w_H (fixed strata) |
|---|---|---|---|---|---|---|
| 00:19 R600 BTO Only | 5,000 | 4,998 | 2,810 | 2,778 | 2,809 | 2,770 |
| 00:19 Held Out | 5,000 | 5,000 | 2,972 | 2,932 | 2,972 | 2,932 |
| 00:19 R600 BTO + Raw BFO | 5,000 | 4,907 | 2,848 | 2,859 | 2,790 | 2,804 |

Importance-weighted means from `sources.npz` (R600 BTO Only): under H 35.651 S 92.224 E. The column-based mixture (re-weighted, in-grid) gives 35.639 S 92.230 E. The difference is within Monte Carlo noise for 2,800 effective rows.

## Strata: 00:19-re-weighted and fixed P(family)
Ẑ_00:19(family, option) = mean over seeds of Σ_i weight_i·exp(ll_i) / Σ_i weight_i, with ll = the option's 00:19 log-likelihood (EoF's stored or derived column) + EoF's alive factor; MC s.e. from the 4 seeds. **Computed by the stand-in from end of flight's columns with EoF's own functions. EoF has not yet published its factors; when it does, they replace these.**

| 00:19 option | stratum | ln Ẑ_00:19 (± MC s.e.) | P(family) fixed | P(family) re-weighted |
|---|---|---|---|---|
| 00:19 R600 BTO Only | next-descent-climb | -5.734 ± 0.041 | 0.1376 | 0.1478 |
| 00:19 R600 BTO Only | next-free | -5.802 ± 0.068 | 0.6948 | 0.6972 |
| 00:19 R600 BTO Only | next-repro-radar | -5.902 ± 0.025 | 0.1527 | 0.1386 |
| 00:19 R600 BTO Only | next-routes | -5.711 ± 0.014 | 0.0149 | 0.0164 |
| 00:19 Held Out | next-descent-climb | -0.100 ± 0.004 | 0.1376 | 0.1383 |
| 00:19 Held Out | next-free | -0.106 ± 0.015 | 0.6948 | 0.6946 |
| 00:19 Held Out | next-repro-radar | -0.109 ± 0.002 | 0.1527 | 0.1523 |
| 00:19 Held Out | next-routes | -0.113 ± 0.003 | 0.0149 | 0.0148 |
| 00:19 R600 BTO + Raw BFO | next-descent-climb | -12.082 ± 0.208 | 0.1376 | 0.2041 |
| 00:19 R600 BTO + Raw BFO | next-free | -12.560 ± 0.024 | 0.6948 | 0.6388 |
| 00:19 R600 BTO + Raw BFO | next-repro-radar | -12.566 ± 0.049 | 0.1527 | 0.1395 |
| 00:19 R600 BTO + Raw BFO | next-routes | -12.313 ± 0.148 | 0.0149 | 0.0176 |

- For R600 BTO Only and Held Out the re-weighting moves P(family) by ≤ 0.014 and the mixture 90 % area under H by < 0.1 %. For R600 BTO + Raw BFO it moves descent-climb from 0.138 to 0.204 (ln Ẑ s.e. 0.21 there, so the shift is provisional).
- **Question for architecture (Held Out):** ruling C says the factor is 1 under Held Out. With `+alive`, the existence fact still enters: ln Ẑ = ln P(transmitting at 00:19:37 | family) = −0.100 to −0.114. That changes P(family) by < 0.001. The sources and mixture use the computed factor; the fixed-strata weights are given beside it.

## Deviations and caveats
1. Surfaces regenerated by the stand-in, not read from the module's run tree. Checked through the 24-row reproduction, not by checksum: the module recorded no checksum for the extended 85-103 E grid.
2. Values are stored as float32 (the surfaces are float32). `lnL_both_<model>` = pleiades + cosmo to 1.5e-5.
3. A row whose cell is not computed in one ocean model is flagged `not_computed` (NaN). The module instead keeps the other model's half-weight there. This affects 545-4,444 rows per seed at the 25 S edge. The 90 % areas and means are unchanged (differences of 0.0 km² and < 1e-8°).
4. All three options were built in one pass, and `READY` was written after all three, not after R600 BTO Only alone.
5. The exchange holds ~80 GB against the 60 GB cap, and the Mac has ~64 GiB free against the 100 GiB floor. Both limits were already exceeded before this run. This run adds 2.6 GB (compact dtypes). Nothing was deleted.
6. The Pléiades likelihood releases debris at a fixed 00:20 UTC; core (b) fuel model uncorrected; Holland H1/H2 not included.

— architecture stand-in (Pléiades side), for the Pléiades module to review
