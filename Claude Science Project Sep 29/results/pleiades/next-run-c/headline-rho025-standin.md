# Pléiades conditional on core run C: headline redrawn to the 11 Oct rulings (ρ = 0.25, GLORYS12 only), STAND-IN

11 Oct 2026, ~09:40 UTC. Architecture stand-in for the Pléiades module (Pete pre-approved recipe runs). **Module review requested.**
The module's README in this folder is unchanged; this note sits beside it.

**Labels (every number):**
- **core run C NOT CONVERGED** (split-half floor 0.924: free 0.918, Davey dynamics + radar 0.910, descent-climb 0.892, routes 0.850).
- End-of-flight physics PROVISIONAL: descents above 6,500 ft/min and unloading not reachable; no structural limit (G13).
- **Single ocean model (GLORYS12 + ERA5); between-model spread not included** in the headline (architecture ruling 2, 11 Oct 02:15 -0600).
  The both-models column is labelled "GlobCurrent windage double-counted (drift audit F1)".
- Transport-error correlation ρ = 0.25 headline (architecture ruling 1, 11 Oct 02:15 -0600); ρ = 0 and 0.5 beside.
- Conditional on H (the imaged objects are debris from 9M-MRO); no identity likelihood, no Bayes factor or P(H | D). Holland H1/H2 not estimable.

## What was run (no method change)
- **Inputs changed only:** the module's own run C mixture maps (`runs/pleiades/next-run-c/<stratum>/branch-<option>-<search>/branch-maps.npz`
  from `branch_eof289.py`, read from the module's working tree) with `L_P+C4` replaced by the module's published correlated-error surfaces
  (`surfaces/joint-surface-rho{0,0.25,0.5}.f32`, `prepare/rho_surface.py`; identical SHA-256 in `runs/pleiades/wide/` and
  `mh370-exchange/pleiades/hydro-test/next-run-c/surfaces/`). This is the module's own stated route ("re-scoring the same impacts is all
  that is needed", 02:21 UTC) and the same substitution `rho_sensitivity.py` made on core (b).
- Strata re-weighted by end of flight's `family-evidence-run-c.json` (ruling C, `closeup_styles.reweighted_pfam`, exact keys
  `00:19 … +unpowered`). Existence constraint `unpowered` (reference). After Phase 2 + Bluefin-21 + OI 2018 + OI 2025-26 SE band (OI grade C).
  P + all four COSMO-SkyMed contacts, one debris field.
- Statistics from the module's functions: `closeup_figure.stats`, `branch_figure.hdr_level`, `rerun_reference.tension`,
  `closeup_styles.panel_mass / mix_tension / flight_background`. The model mean for "both models" follows `build_branch` (equal-weight
  mean of likelihoods; a not-computed model counts as zero).
- New stand-in scripts, for the module to review (none of the module's files was edited):
  `engine/hypotheses/pleiades/prepare/headline_rho_standin.py` (table), `headline_rho_figure_standin.py` (close-ups, colour house style
  with faint points), `headline_rho_splithalf_standin.py` (split-half; written, **not run**, see Deviations).

**Reproduction checks** (`headline-rho025-standin/headline-rho025-checks.csv`):
- The hook maps reproduce the module's README exactly: both models 37,887 / 45,709 / 82,614 km²; GLORYS12 only 28,478 / 32,252 / 67,914 km².
- The ρ = 0 GLORYS12 surface gives the same conditional as the hook: 28,478.18 km² against 28,478.18 km², same mean.
  Conditional mass in cells where the ρ = 0 surface is not computed: 0.0. Over the whole grid the ln-ratio sd is 0.006 (both) and
  0.010 (GLORYS12). The module quoted 1e-5 on its own check cells. The larger value comes from far-field cells that carry no conditional mass.

## Result: after all searches, P + all four COSMO, `unpowered`, strata re-weighted

± is the split-half σ (rms over three 4 + 4 seed partitions). It is measured only for ρ = 0 GLORYS12, which is the module's own
`splithalf.csv` row (`GLORYS12 only`). Here the variant is identical. For the other three settings σ was not run.
"Tension" = ln S (suspiciousness) and the Handley-Lemos p; mean shift = distance from the mean of the impact PDF without H.

| 00:19 option | setting | 50 % km² | 90 % km² | mean under H | outside past searches | share left by the searches, under H | mean shift NM | ln S | p | PDF without H inside 90 % under H |
|---|---|---|---|---|---|---|---|---|---|---|
| 00:19 R600 BTO + Raw BFO | **ρ 0.25, GLORYS12 only (headline)** | 5,817 | 30,998 (σ not run) | 36.01 S 92.38 E | 74.3 % | 0.412 | 36 | +0.13 | 0.43 | 15 % |
| 00:19 R600 BTO + Raw BFO | ρ 0, GLORYS12 only | 5,470 | 28,478 ± 214 | 35.96 S 92.38 E | 73.0 % | 0.395 | 38 | -0.01 | 0.38 | 14 % |
| 00:19 R600 BTO + Raw BFO | ρ 0.5, GLORYS12 only | 6,138 | 33,493 (σ not run) | 36.05 S 92.37 E | 75.0 % | 0.421 | 34 | +0.24 | 0.47 | 15 % |
| 00:19 R600 BTO + Raw BFO | ρ 0.25, both models — GlobCurrent windage double-counted (drift audit F1) | 7,582 | 41,597 (σ not run) | 35.95 S 92.36 E | 69.9 % | 0.366 | 38 | -0.32 | 0.30 | 16 % |
| 00:19 R600 BTO Only | **ρ 0.25, GLORYS12 only (headline)** | 6,980 | 34,997 (σ not run) | 36.06 S 92.40 E | 78.1 % | 0.450 | 95 | -0.67 | 0.23 | 7 % |
| 00:19 R600 BTO Only | ρ 0, GLORYS12 only | 6,608 | 32,252 ± 247 | 36.01 S 92.39 E | 76.5 % | 0.428 | 97 | -0.83 | 0.21 | 6 % |
| 00:19 R600 BTO Only | ρ 0.5, GLORYS12 only | 7,326 | 38,016 (σ not run) | 36.11 S 92.40 E | 79.1 % | 0.464 | 93 | -0.54 | 0.25 | 8 % |
| 00:19 R600 BTO Only | ρ 0.25, both models — GlobCurrent windage double-counted (drift audit F1) | 9,792 | 49,540 (σ not run) | 35.99 S 92.42 E | 74.8 % | 0.408 | 99 | -1.17 | 0.16 | 8 % |
| 00:19 Held Out | **ρ 0.25, GLORYS12 only (headline)** | 13,325 | 77,420 (σ not run) | 35.57 S 91.78 E | 81.8 % | 0.506 | 69 | -0.29 | 0.33 | 11 % |
| 00:19 Held Out | ρ 0, GLORYS12 only | 12,034 | 67,914 ± 274 | 35.52 S 91.76 E | 81.2 % | 0.495 | 72 | -0.35 | 0.32 | 10 % |
| 00:19 Held Out | ρ 0.5, GLORYS12 only | 14,241 | 85,461 (σ not run) | 35.63 S 91.80 E | 82.1 % | 0.510 | 66 | -0.24 | 0.34 | 12 % |
| 00:19 Held Out | ρ 0.25, both models — GlobCurrent windage double-counted (drift audit F1) | 17,843 | 92,331 (σ not run) | 35.43 S 91.66 E | 81.6 % | 0.501 | 77 | -0.52 | 0.29 | 12 % |

Full columns (incl. share in the OI north-west band, d_shared, ln R): `headline-rho025-standin/headline-rho025-stats.csv`.

## Findings (UNCONVERGED; to be read with the labels)
1. **New headline (ρ 0.25, GLORYS12 only), R600 BTO + Raw BFO: 90 % region 30,998 km², mean 36.01 S 92.38 E.** It is 18 % smaller than
   the module's previous headline (both models, ρ 0: 37,887 km²). For R600 BTO Only it is 23 % smaller (34,997 against 45,709 km²), and for Held Out
   6 % smaller (77,420 against 82,614 km²). The two rulings act in opposite directions: ρ widens the region, and dropping GlobCurrent narrows it more.
2. **ρ widens the GLORYS12-only region by +8.5 to +14 % at ρ = 0.25 and by +18 to +26 % at ρ = 0.5** (Held Out widens most). The effect
   on core (b), both models, was +11 to +14 % and +21 to +25 %. The mean moves south by 0.09-0.11° from ρ 0 to 0.5. The longitude changes
   by ≤ 0.05°.
3. **The tension eases as ρ rises.** For R600 BTO + Raw BFO, ln S goes from −0.01 to +0.13 to +0.24. For R600 BTO Only, from −0.83 to −0.67 to −0.54. The mean
   shift falls by 3-6 NM. Every p is ≥ 0.16. The lowest is the double-counted two-model R600 BTO Only (ln S −1.17, p 0.16).
4. **The searches leave more of the conditional under H with ρ** (0.395 → 0.412 → 0.421 for BTO + Raw BFO). The share outside past searches is
   73-75 % (BTO + Raw BFO) and 76-79 % (BTO Only).
5. **Both models at ρ 0.25 are 19-42 % wider than GLORYS12 alone.** This is the between-model spread that the headline now leaves out.
   As long as the GlobCurrent arm double-counts windage (F1), this spread is not a clean measure of ocean-model uncertainty.
6. Monte Carlo noise, where measured (ρ 0, GLORYS12): σ is 0.4-0.8 % of the 90 % area. The binding limit is still core run C's non-convergence.

Figures (colour house style, faint points for the impact PDF without H; 90 % outlines of the three other settings overlaid; two-part
footnote STE100 + technical in the bottom 25 %; titled "core run C NOT CONVERGED"):
`headline-rho025-standin/closeup-r600-no-offset+unpowered-rho025-glorys12.{png,pdf}`,
`closeup-r600-bto+unpowered-rho025-glorys12.{png,pdf}`, `closeup-none+unpowered-rho025-glorys12.{png,pdf}`.

## COVERAGE
- **(a) Feasible set:** the full 777-200ER end-of-flight space from the 7th arc: controlled glides and ditchings, uncontrolled spirals,
  and rapid descents (incl. Holland-type, above 6,500 ft/min) up to structural limits. Families A1, A2 and B. Source: architecture
  coverage register and end of flight's notes. This stand-in adds nothing to (a).
- **(b) Model reach:** run C end-of-flight physics cannot produce descents above 6,500 ft/min or unloading (**reach gap, declared**). It has
  no structural limit, so it produces infeasible-speed entries (G13). The module's `~v212` version handles these (≤ 0.4 % effect on the conditional). That version was not redrawn here.
  Pléiades side: the wide grid (78-115 E, 45-5 S) leaves ≤ 1e-4 of the weight not computed. ρ surfaces: 0.0 of the conditional mass lies in
  not-computed cells (measured here).
- **(c) Proposal coverage:** core run C, 4 strata × 8 seeds, **split-half not converged in every stratum** (gap, declared). This note
  re-weights the same impacts on the 0.05° grid. ESS per option, per family and per declared region **was not computed by this stand-in**
  (histogram re-weighting). The module's source packages give ESS 2,730-2,930 of 5,000 per option. Under H about twice the flight-PDF
  share of weight comes from infeasible-speed impacts (module 03:25 UTC). **Holland H1/H2 not estimable** (gap, end of flight's targeted
  sampler pending).
- **Every standard 00:19 option:** Held Out, R600 BTO Only and R600 BTO + Raw BFO are estimable from this sample set and are reported.
  The other options (`r600/inflated`, `startup-offset`, `r1200`) were not requested and not run here. The `silent` constraint was not redrawn.
- **Parameter bounds with sources:** ρ ∈ {0, 0.25, 0.5}: ocean transport `results/ocean-transport-error-pairs.md` (central 0.07-0.41
  GLORYS12 and −0.16-0.31 GlobCurrent at 40-80 km; 0.5 upper sensitivity; 0.8 not supported). Windage 0-5 % and the OU transport variances
  are the hook's `run.toml` (drifter replay, about 100-110 km per component at 15 d). **The headline is conditional on a single ocean model**
  (between-model spread excluded; gap declared in the label until GlobCurrent carries product-relative windage).

## Deviations (stand-in, declared)
1. **Split-half σ for ρ 0.25 / 0.5 (GLORYS12) and ρ 0.25 (both models) was not run.** The heavy lock was held by other work for 45 min
   (08:47-09:32 UTC; a third job was queued). I stopped waiting rather than run a ~90 GB read outside the lock. The timing smoke was 2.4 s per seed
   histogram and 1.7 GB RSS, so the full run is about 10 min under the lock. Command (writes one CSV, < 50 KB):
   `python headline_rho_splithalf_standin.py <mh370-exchange>/end-of-flight/next-run-c <module runs>/pleiades/next-run-c <module runs>/pleiades/wide <…>/summary/family-evidence-run-c.json <out>/splithalf-rho.csv r600/no-offset+unpowered r600-bto+unpowered none+unpowered`.
   It also re-derives the module's `both models` row as a reproduction check. The ± quoted for ρ 0 GLORYS12 is the module's own measurement.
2. Only the colour close-up was drawn. The seabed (GEBCO) style was not redrawn.
3. The inputs were read from the module's working tree (`workspaces/4faea3b7…/engine/…/runs/pleiades/`, gitignored). Nothing was written there.
4. **Not changed (next module item):** the GlobCurrent windage. The module's GlobCurrent arm must apply the product-relative offset (drift audit F1;
   drift's run A draws 0.60-0.75 % U10). That can follow drift's run A. After that, the headline becomes both models under the same alternative
   name and set as drift (ruling 2).

— architecture (stand-in for Pléiades)
