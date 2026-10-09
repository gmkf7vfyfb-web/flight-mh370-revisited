# Convergence: the same measurement on eight replicates

Searched-areas module, 9 October 2026. Composition rule 6 asks for Monte Carlo adequacy to be
measured and unconverged results reported as unconverged. `results/seabed-search-eof-smoke/` reported
split-half 0.846 / 0.812 on **two** replicates and said so. This is the same measurement on **eight**,
and it supersedes it.

**It is still the glide class only.** The Boeing engineering-simulator runs were tests of uncontrolled
dives; until the end-of-flight model is calibrated against cases 3, 4, 5, 6 and 10 (Pete, 9 October)
these impacts carry no dive class, and a dive class would land nearer the 7th arc — inside the
searched corridor — so the search evidence here is likely **understated**.

**Run.** `runs/fixture-8` (`config/integrated.toml` + `config/smoke.toml` + `config/fixture.toml` +
`hypotheses/seabed-search/smoke/seeds-1-8.toml`: 20k particles per mode, seeds 1–8, 2,000 hand-off
rows per seed) continued by `mh370 terminal` with the end-of-flight smoke override at `children = 4`,
`target = "none"`, 00:19 option `none`. **265,936 impacts, 8 replicates.** 2 m 26 s + 2 m 4 s at
`RAYON_NUM_THREADS=4`; 183 MB.

## Convergence

| | 2 replicates | 8 replicates |
|---|---|---|
| split-half, before the search | 0.846 | **0.957** |
| split-half, after (`run.toml`) | 0.812 | **0.947** |
| Kish ESS, before | 64,119 | 253,694 |

The split-half agreement of the module's own reported distribution now sits at 0.947–0.957, above the
0.924 floor the project has been using. **The module's aggregate numbers are converged at this
scale**; what is not converged is the underlying end-of-flight model's own sampling, which is theirs,
and the absolute level remains smoke-scale.

## What moved, and what did not

| quantity | 2 replicates | 8 replicates | |
|---|---|---|---|
| prior mass on Phase 2 ground | 0.232 | **0.231** | stable |
| mass removed at ρ = 0, Phase 2 alone | 0.2197 | **0.2180** | stable |
| Z at ρ = 0.05 | 0.7913 | **0.7929** | stable |
| mass on searched ground after | 0.032 | **0.031** | stable |
| median before → after | −38.83 → −39.25 | **−38.61 → −39.00** | shift 0.42° → **0.39°** |
| mass south of 39.5°S, after | 0.439 | **0.409** | moved 0.03 |
| 95% upper bound, after | −33.78 | **−30.08** | **not converged** |
| repeat-search gap (shared − independent) | 0.0013 | **0.0016** | stable |
| OI 2018 alone, mass removed | 0.0051 | **0.0109** | doubled, still small |
| OI 2025–26 variant, change in Z | 0.0004 | **0.0017** | still negligible |

**Every headline the module reports survives**: the search is a ~22% reduction in evidence rather
than the placeholder's 63%, it shifts the distribution south rather than excluding ground, and it
leaves about 3% of the mass on searched seabed.

**Two things were Monte Carlo artefacts of the two-replicate run and are corrected here.**

1. **The northern tail is not determined.** The 97.5th percentile moves from −33.78 to −30.08 between
   the two runs. It is a tail statistic on a long, thin northern shoulder and it should not be quoted
   from either run.
2. **The eq. 11.2 candidate-area ranking was over-concentrated.** On two replicates, P(find) = 25%
   appeared to need the best 8 blocks and 19,092 km²; on eight it needs **19 blocks and 45,502 km²**,
   50% needs **56 blocks, 134,092 km²**, and 75% needs **175 blocks, 423,002 km²**. The leading block
   also changes, from 39.5°S 89.0°E to **40.0°S 87.5°E**, although the leading *cluster* — 39–40.5°S,
   87.5–89.0°E — is the same in both.

   The lesson is specific and worth carrying: **the ranked planning output needs more samples than the
   aggregate evidence does.** A 0.5° block holds about 2% of the mass, so block-level ordering is set
   by differences the two-replicate run could not resolve, while Z and the mass-removed figures were
   already stable to three decimal places. Any search-planning table in the paper must come from a
   full-scale run, with the cumulative curve shown rather than a top-N list.

Figures: `search-evidence.pdf` and a PNG of each page, including the residual view.

---

*Searched areas, 9 October 2026. Supersedes `results/seabed-search-eof-smoke/`, which stays as the
two-replicate record.*
