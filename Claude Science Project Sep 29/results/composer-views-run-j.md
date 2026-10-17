# Composer §0 views on run J — evidence alone, core + E, leave-one-out, all; disagreement; influence; whole-arc outputs

17 October 2026. Composer sub-agent of the coordinating session. Brief: `threads/master-prompts/composer.md` §0 (commit 5c5c8e9).
Implementation: **numpy** (as passes 2/2b), scripts in `results/composer-views-run-j/`. Data outputs:
`mh370-exchange/composer/run-j-views/`. Labels that apply to every number: core run J (tag run-j 1244b7c), split-half **accepted as a
PASS by project ruling, 16 Oct 2026**, thin northern detail is a stated tail-shape limitation; end of flight run J (run-i-dive recipe,
round-3 laws, bank limit U[52, 90]); uncontrolled-arm physics not calibrated; cause model **competing causes, q = 1/3, other cause
silent** (cells `D<d> total q=0.333 (C2 silent)`), the end-of-flight headline; searched areas at the **impact point** (no run J
settling resample); hydroacoustics contributes nothing (0 by ruling, no P_D); Pléiades results are **conditional on H** and carry
no Bayes factor for H; the Australian non-recovery term is a **labelled sensitivity**, never headline.

## Lead

1. **Reproduced before anything new.** From my own per-seed reduction: run J waypoints D0' ln Z −7.5246, ESS 1,941,487, latitude
   5/50/95 % −38.40/−37.12/−33.87 (end of flight's table, exact); with drift −38.20/−36.86/−30.78, ESS 941.1k, mean shift +0.70°,
   not computed 0.03 % (drift stand-in `drift-runj-2026-10-17`, exact, all six options). Pléiades shared-impact-point test on waypoints:
   +0.495 (published +0.49) finds only, +0.811 (+0.81) with the populated-coast term; D1, D2, D5 also match.
2. **Every evidence type alone points north of the satcom peak, except the Pléiades conditional.** With the 7th arc uniform at
   00:19:29 over the span the run J flight paths reach (40.6 S 82.8 E to 11.8 S 107.3 E, 2,200 NM), and the same end-of-flight model,
   D0': drift alone has median **28.2 S** (sampling-free surface version 28.5 S), searched areas alone **25.9 S** (26.0 S), the
   Australian sensitivity **26.5 S** (26.7 S), Pléiades alone **35.3 S** (35.4 S). The core median is 37.1 S. The two versions of
   view (a) agree within 0.35° in the median and 0.01–0.04 nat in the ln evidence ratio in every case.
3. **Disagreement is a result.** ln evidence ratio (E on the core against E on the arc-uniform prior): drift **−0.54**, searched
   areas **−0.88**, Australian sensitivity **−2.09** (each evidence type disfavours the core region against the whole arc), Pléiades
   **+0.68**. Bhattacharyya coefficient core vs E alone 0.24–0.44. Only 7–13 % of the drift-alone or searches-alone mass is inside the
   core's 90 % HPD. The sign is the same in all six 00:19 options (fig. 2b).
4. **All evidence (core × drift × searched areas), D0', four-stratum mixture:** median **35.66 S** (seed SE 0.07°); 50/90/95 % HPD
   **87k / 437k / 581k km²** (core: 19k / 162k / 262k); mass north of 33 S **0.190 ± 0.009** (core 0.032); probability on searched
   ground **0.148** (core 0.724). Nine modes; the largest hold 0.31 (35.7 S), 0.28 (37.2 S), 0.19 (34.3 S). **Label: north of 33 S
   under-sampled (effective sample 345; core 121)**.
5. **Influence.** In all: searches carry 0.48 of the KL from the core, drift 0.28; neither exceeds half. Removing drift moves the
   median 145 NM south and shrinks the 90 % area by 118k km²; removing searches 142 NM and 168k km². **Flags:** the Pléiades factor
   carries 0.53 of the KL of "all given H"; the Australian term 0.57 of its sensitivity product; **model dominance**: the waypoints
   stratum carries 0.996–0.999 of every product (> 0.95); the core and "all given H" are each one mode with 0.984 and 0.998.
6. **Conditional and sensitivity products.** All given H: median 35.40 S, 90 % HPD 70k km², north of 33 S 0.004. P(H | D) is **not
   estimable** (no identity likelihood p(imagery | not H)); the factor by which the non-imagery evidence changes the odds of H is
   **+0.53 nat** (drift + searches, D0'; 0.53–0.82 over the six options). All with the Australian term: median 31.63 S, 90 % HPD 529k km²,
   north of 33 S 0.587, on searched ground 0.033.
7. **Not converged in sampling north of 33 S** for the "alone" views: effective sample north of 33 S is 456 (drift), 97 (searches),
   10 (Pléiades), 1,837 (Australian); per 5° band it is 3–212 for drift alone — far below the §0.4 target of 1,000. The arc-wide
   sample set (§0.4, requested of core and end of flight) is still needed; until then these views carry the label.

## Deviations (also in the submission)

- Searched areas applied through the composer's pass-1 transcription `seabed_loglik.py` (lib.rs; rho 0.05, Phase 2 q 0.945,
  Bluefin-21 q 0.9) at the impact point. Validated in pass 1 against `mh370 evaluate` (max |Δ| 0.0); **not re-validated on run J**:
  the module's run I columns are aligned with end-of-flight run I impacts that are no longer on the exchange. Ocean Infinity layers excluded.
- No settling: no run J resample; all products are impact-point products.
- Drift factor for all four strata from my transcription of the export's lookup (bilinear in L over scored corners, run A rebuilt
  surfaces); on the waypoints stratum it agrees with drift's own `drift-lnL.npy` to 7.6e-6 in ln L, with 2,338–18,950 rows per seed
  (≈0.1 %) differing in scored state (as `pleiades/finds-test/reduce_seed.py` found). Free, repro-radar, descent-climb and the
  both-burst set have no drift columns of drift's own.
- D3/D4 headline: waypoints stratum from end of flight's both-burst supplementary pass (8 seeds, thinned), as the EoF note directs;
  production-only (24 seeds) reported as a check.
- View (a)(ii) uses only rows with a 00:19:29 crossing: rows without one (0.47 % of D0'/D1 core weight, ~0 for D2–D5) get weight 0.
- Arc span = the reach of the run J 00:19:29 crossings (10 NM bins with ≥ 10 crossings), not an analytic flight-prior span.
- The 7th arc is a small circle fitted to 00:19:29 positions with |BTO residual| < 20 µs (8 seeds; centre 0.570 N 64.252 E, radius
  44.501°, RMS 1.3 km).
- View (a)(i) uses one displacement distribution (impact minus crossing, D0' core, pooled) for every option; drift and the
  Australian term abstain on 30 % of its points (outside the drift grid, 41.2–21.2 S), carried at the arc-uniform mean.
- 349 rows fall outside the 2-D map grid (≤ 1.7e-6 of one repro-radar seed's weight; stratum weight 3e-4): absent from maps only.
- Family B = family4 codes 3 and 6 (code 6 holds 0.06 % of the weight), as pass 2; end of flight's tables count codes 1–3.
- Pléiades not-computed surface cells carried at the mean (composition ruling) rather than as zero (module convention); share ≤ 5.3e-6.
- Model-error-doubled sensitivities only where a module supplies the means (drift kernel 50 → 100 km; searches rho 0.05 → 0.10);
  none for Pléiades or the core; no heavy-tailed variant from any module. NaN-drop sensitivity not run (shares ≤ 1.8e-4).
- MC error = seed bootstrap within strata (400 draws); split-half not recomputed.
- My "ln evidence ratio against uniform" uses the arc-uniform prior; the drift stand-in's −0.76 uses uniform per area on the drift grid.
  They are different references and are not comparable.

## 1. Method

- **Row mass** per 00:19 option: end of flight's `option_table_0019.seed_terms` unchanged. Seeds pooled by evidence within a stratum
  (ln(P_s/K_s) + seed scale); strata mixed by core run J P(family) at equal prior (waypoints 0.9982, free 0.0013, repro-radar 0.0003,
  descent-climb 0.0002).
- **Factors per row** (position-only): drift (two ocean models, 50 km kernel); Pléiades (`joint-surface-rho0.25-gcrel`, P + COSMO
  F1–F4); searched areas; Australian populated-coast term (drift stand-in's law refitted: GLORYS12 k 5.4747, c 0.3881; GlobCurrent
  k 4.5971, c 0.3663, identical to `aus160-both.json`). **Ocean model marginalised jointly** per row: Λ = ½(D_G P_G + D_C P_C).
- **Not computed**: carried at the (seed, option) mean of the computed rows **under the base of the product** — core weights for
  views (b), (c) and all; arc-uniform weights for view (a)(ii) (ruling of 15 Oct applied per product base; test 8d).
- **View (a)(ii)**: each row reweighted by r = u/q, q = pooled core proposal mass in the 10 NM bin of the row's 00:19:29 arc position,
  u uniform per NM over the span; the end-of-flight model then carries the crossing to the impact (exact importance correction; the
  prior over arc position becomes uniform, the end-of-flight conditional is unchanged). **View (a)(i)**: the module's own surface at
  every 10 NM arc bin, convolved with one fixed displacement distribution (8,396 points; SD 41 km east, 60 km north), no sampling.
- **Equal-area grid** of the proposed `summary.rs` extension (0.25° × authalic q step, 769.31 km² cells; extent 50–6 S, 78–116 E).
  HPD = smallest set of cells. Medians along the arc: from 10 NM arc-position histograms (NM from the arc's southern tip at 43.9 S).
- **Disagreement**: ln ER = ln E_core[L_E] − ln E_U[L_E] (conditional on the impact model and the arc-uniform reference);
  (c) vs all: ln E_(all−E)[L_E] = ln Z_all − ln Z_(all−E), and the same minus ln E_U[L_E]. **Influence**: KL(P ‖ B) =
  E_P[ln Λ_P/Λ_B] − ln(Z_P/Z_B) on the pooled sample.
- **Effective sample label** = min(Kish ESS in the region, seed-scatter implied n × region mass). For core-weighted products the
  seed-scatter value is the smaller (shared SMC ancestry; core D0' 121 north of 33 S matches core's pooled northern lineages, 119.8);
  for arc-uniform views Kish is the smaller.

## 2. Views, disagreement and influence — D0' (00:19 data held out), four-stratum mixture

![fig1](composer-views-run-j/fig1-evidence-alone-along-arc.png)

![fig2](composer-views-run-j/fig2-disagreement-influence.png)

![fig3](composer-views-run-j/fig3-hpd-map-core-vs-all.png)

The full tables for all six options, per family, per stratum, modes, sensitivities, not-computed shares and coverage are in
**Appendix A** (generated by `report_note_tables.py`); every row of every product is in `products.csv`, `bands-1deg-mixture.csv`
(mass per 1° band with seed-bootstrap SE and mass on searched ground), `disagreement-influence.csv`, `modes.csv`, `coverage-ess.csv`,
`not-computed.csv`, `pleiades-odds-factors.csv`.

Readings:
1. **Triangulation.** Drift and searched areas each say "not 37–39 S" on their own: drift because its likelihood falls steeply south
   of 36 S, the searches because that is where the seabed was searched. Neither has a peak of its own; both are broad from 34 S to
   the north end of the span. Together with the core they move the median 1.5° north (158 NM along the arc: core 1,239 NM, all 1,397 NM
   from the southern tip) and spread the 90 % region by a factor 2.7. The core's narrow peak is **not** confirmed by any other evidence
   type; the Pléiades conditional is the only one that favours the core region (+0.68), and it does so by pulling to 35.4 S.
2. **The drift-and-searches agreement is real but not independent of the 37 S exclusion**: their two alone-views overlap
   (both medians 26–28 S), but the core region is excluded by different physics in each.
3. **Synergy.** KL(all ‖ core) = 0.995 nat exceeds drift (0.28) + searches (0.48): each factor's effect is larger in the presence of the other.

## 3. Whole-arc outputs (§0.7)

Mass per 1° band with seed-bootstrap Monte Carlo error: `bands-1deg-mixture.csv` (every option, every product, view (a) included).
Every mode with its mass: `modes.csv` and Appendix A. HPD 50/90/95 % areas: `products.csv`. Inside vs outside the searched areas:
per product (`p_on_searched_ground`) and per 1° band (`mass_on_searched_ground`). D0': core 0.724 on searched ground; all 0.148;
all given H 0.149; with the Australian term 0.033.

## 4. Model error declared per module (§0.5) and sensitivities

| module | declared model error (source) | doubled / heavy-tailed sensitivity here |
|---|---|---|
| satcom + flight core | BTO / BFO noise and BFO bias-drift inside the filter (R600 BTO sd 63 µs, BFO sd 7 Hz at 00:19, run J BFO sd 4.32 Hz; core run J config) | **not available**: core sensitivity runs are requested of the core session, not run here |
| end of flight | uncalibrated uncontrolled arm (Boeing leave-one-out gate failed) — declared as a labelled limitation, no error scale | none supplied |
| drift | transport Monte Carlo noise per node (split halves), ocean-model spread (two products), ocean-error OU (GlobCurrent σ 0.0869 m/s, T 10 d), windage priors, recovery kernel 50 km (drift run A README, stand-in README) | kernel doubled 50 → 100 km: D0' all median 35.90 S, 90 % 414k km², N of 33 S 0.159; single ocean model: GLORYS12 35.42 S / 475k / 0.246, GlobCurrent 35.88 S / 369k / 0.132 |
| searched areas | rho = 0.05 chance the wreck is not detectable where searched (no published value; module sweeps 0–0.5), q 0.945 / 0.9 | rho doubled 0.10: median 35.76 S, 90 % 425k km², N of 33 S 0.178 |
| Pléiades | object-position OU variances of run.toml, rho 0.25, two ocean models | none supplied (rho 0 / 0.5 surfaces exist but rho is not a model-error scale) |
| hydroacoustics | not applicable (0 by ruling) | — |
| Australian term | fitted-law residual 0.19 / 0.14 nat, SD 0.62 / 0.49; split-half SD 0.50 nat per node; post hoc restriction | it is itself a sensitivity |

**How far the headline moves** under the supplied doublings (D0'): median ≤ 0.24° (drift kernel), 90 % area −5 % to −3 %, north of
33 S 0.190 → 0.159–0.178. The single-ocean-model spread (0.132–0.246 north of 33 S) is larger than either doubling.

## 5. Shared inputs (§0.6)

| input | modules | treatment here | status |
|---|---|---|---|
| ocean model | drift, Pléiades | named alternative, marginalised jointly per row | declared |
| ocean realisation / transport noise | drift, Pléiades | each factor uses its own realisations | **dependence gap** (the deferred correlated likelihood; Pléiades finds-test notes it) |
| windage | drift, Pléiades | each integrates its own prior (Pléiades GlobCurrent windage re-weighted to drift's 0.60–0.75 % convention) | **dependence gap** (not a joint alternative) |
| end-of-flight family | all | `family4_code` column; results per family first | declared |
| 00:19 option and cause | core/EoF weights only | all factors position-only | declared |
| impact vs seabed position | searched areas, settling | searches at the impact point; settling not applied | **gap** (no run J settling resample) |
| impact energy / angle | hydroacoustics, settling, drift breakup | none active (hydro 0; drift breakup at the intact-entry approximation) | not exercised |
| drift surfaces | drift, Australian term, Pléiades finds test | Australian term replaces the drift factor, never multiplied with it | declared |

## 6. COVERAGE

**(a) Feasible set.** Impacts anywhere the 777-200ER can reach after crossing the 7th arc at 00:19:29, with end of flight's feasible
set (uncontrolled spiral to 90° bank, dive or level-off, planned descents before exhaustion; EoF run J note §4).
**(b) Model's reach.** The arc span the run J crossings reach: 40.6 S 82.8 E to 11.8 S 107.3 E (2,200 NM); impacts 46.6–10.4 S,
82.9–111.5 E. Overbank > 90° is an end-of-flight reach gap; pre-00:11 planned descents only via joined V2 (not used here). Drift grid
41.2–21.2 S, 84.0–105.6 E (abstains elsewhere); Pléiades surface 45–5 S, 78–115 E.
**(c) Proposal's coverage.** Kish ESS of all, D0': 309k; all given H 65k. Effective sample north of 33 S (label): core 121, all 345,
all given H 219, Australian sensitivity 1,737; view (a): drift 456, searches 97, Pléiades 10, Australian 1,837. Per 5° band
(Appendix A): core 1,183 / 145 / 149 in 40–35 / 35–30 / 30–25 S; all 668 / 414 / 479; drift alone 3–212. **No 5° band of the drift, searches or
Australian view (a) reaches the §0.4 target of 1,000**; the Pléiades view (a) does in 40–30 S (4,389 and 2,340) but has an effective
sample of 10 north of 33 S; all-given-H does in its bands. Under D3/D4, 7.7 % / 6.8 % of the arc span has no proposal
mass at all (unreachable for view (a)); D3's A1 sub-population stays at end of flight's ~400 effective impacts.
**ESS per option, family, region**: `coverage-ess.csv`, `products.csv` (Kish ESS per product × option × family × stratum).
**Gaps and status.** G-views-1 arc-wide sample set (§0.4): open, requested of core and end of flight. G12 settling on run J: open.
G26 Australian non-recovery: modelled, sensitivity, awaits Pete's detection-level ruling. Ocean-realisation and windage dependence
between drift and Pléiades: open. Searched-areas columns on run J from the module itself: not published (transcription used).
**Bounds and sources.** q = 1/3, C2 silent (12 Oct rulings); bank limit U[52, 90] (Pete, 16 Oct); drift kernel 50 km (drift
primary); rho 0.05 (searched-areas run.toml); Pléiades rho 0.25 gcrel (module headline); strata by core P(family) (core run J README).

**Not-computed share per module per 00:19 option** (share of core weight): drift ≤ 1.8e-4 in every option; Pléiades ≤ 5.3e-6;
searched areas 0; hydroacoustics 0 (no column). No factor abstains on more than 10 %: every factor is eligible for the headline
under the 15 Oct ruling (the Australian term is a sensitivity by Pete's separate ruling).

## 7. Tests 8 and 9 (synthetic fixtures, `test_views.py`): all pass

- 8a defensive mixture with exact weights recovers the uniform arc prior (max |z| 1.8 over 24 bands); 8b factor composed on the
  mixed proposal equals a direct sample from the target (Δ mean −0.001°, tolerance 0.015°) and the closed form; 8c the row-estimated
  reweighting used here recovers the uniform masses exactly and the posterior mean to 0.001°; 8d an abstaining factor under the
  arc-uniform base: carried value within 0.7 % of closed form, abstaining mass 0.2455 vs 0.25.
- 9 Gaussian core and two disagreeing factors: views (a)–(c) medians within 0.003°, ln evidence ratios within 0.002 nat, 90 % HPD
  shares within 0.0003, Bhattacharyya exact to 3 d.p., KL influences within 0.0003 nat of the closed forms.

## 8. Open questions for Pete

1. The Australian detection level (assumption (i) of the drift stand-in): until ruled, the term stays a sensitivity. It is the
   largest single disagreement with the core (ln ER −2.09) and carries 0.57 of the KL of its product.
2. P(H | D) for the Pléiades hypothesis needs either a prior on H with an identity likelihood (p(imagery | not H)) or a ruling that only
   the odds factor (+0.53 nat from drift and searches, D0') is reported.
3. The arc span for "uniform along the arc": I used the reach of the run J crossings (40.6–11.8 S). A span from the core prior itself
   (before the satcom update) needs the core session; it would also define where the §0.4 arc-wide sample set must reach.
4. 0.47 % of the D0'/D1 core weight has no 00:19:29 crossing (impact before or without the log-on). End of flight should say what these
   rows are; they are excluded from the arc-uniform views only.
5. Should the composer publish an "all" headline at all while every view (a) is under-sampled north of 33 S (effective sample 10–456)?
   My reading of §0 is yes, with the label; the arc-wide set would remove the label.

## Files

`results/composer-views-run-j/`: `prep_nodes.py`, `views_common.py`, `views_lib.py`, `arc_line.py`, `arc_q.py`, `arc_r.py`,
`reduce_seed_views.py`, `compose_views.py`, `report_tables.py`, `report_note_tables.py`, `report_figures.py`, `test_views.py`,
`run_all.sh`, `run_pass.sh`, `run_u.sh`; figures (png/pdf); CSV tables; `tests-8-9.json`. Run order: prep_nodes → arc_line →
run_pass.sh arc_q.py → arc_r → run_all.sh (reduce_seed_views; the U-only mode `run_u.sh` recomputes only the arc-uniform products)
→ compose_views → report_tables / report_note_tables / report_figures. Exchange: `mh370-exchange/composer/run-j-views/`
(`views-run-j.json`, maps, 0.01° PDFs, per-seed work files 2 GB).

-- Composer

## Appendix A — generated tables (all options)

#### D0' 00:19 data held out — four-stratum mixture, cause model q = 1/3 (other cause silent)

| evidence E | view | median lat | median along arc (NM from S tip) | 50 % / 90 % HPD km² | mass N of 33 S | effective sample N of 33 S | Kish ESS | on searched ground |
|---|---|---|---|---|---|---|---|---|
| core (satcom + flight + EoF) | = view (a) for the core | -37.13 | 1239 | 19k / 162k | 0.032 | 121 | 1.95e+06 | 0.72 |
| debris drift (finds) | (a)(i) module surface on the arc | -28.52 | 1961 | – | 0.765 | (no sampling) | – | – |
| | (a)(ii) alone, reweighted run J | -28.18 | 1953 | 191k / 720k | 0.786 | 456 | 2.07e+03 | 0.11 |
| | (b) core + E | -36.86 | 1255 | 38k / 269k | 0.085 | 229 | 9.42e+05 | 0.62 |
| | (c) all except E | -36.71 | 1252 | 57k / 319k | 0.091 | 180 | 7.91e+05 | 0.22 |
| | all | -35.66 | 1397 | 87k / 437k | 0.190 | 345 | 3.09e+05 | 0.15 |
| searched areas | (a)(i) module surface on the arc | -25.98 | 2146 | – | 0.787 | (no sampling) | – | – |
| | (a)(ii) alone, reweighted run J | -25.88 | 2121 | 188k / 793k | 0.776 | 97 | 1.17e+03 | 0.02 |
| | (b) core + E | -36.71 | 1252 | 57k / 319k | 0.091 | 180 | 7.91e+05 | 0.22 |
| | (c) all except E | -36.86 | 1255 | 38k / 269k | 0.085 | 229 | 9.42e+05 | 0.62 |
| | all | -35.66 | 1397 | 87k / 437k | 0.190 | 345 | 3.09e+05 | 0.15 |
| Pléiades (conditional on H) | (a)(i) module surface on the arc | -35.41 | 1407 | – | 0.003 | (no sampling) | – | – |
| | (a)(ii) alone, reweighted run J | -35.35 | 1405 | 13k / 60k | 0.016 | 10 | 6.16e+04 | 0.61 |
| | (b) core + E | -35.39 | 1405 | 13k / 67k | 0.002 | 211 | 1.41e+05 | 0.63 |
| | (c) all except E | -35.66 | 1397 | 87k / 437k | 0.190 | 345 | 3.09e+05 | 0.15 |
| | all | H | -35.40 | 1410 | 15k / 70k | 0.004 | 219 | 6.53e+04 | 0.15 |
| drift + Australian non-recovery (SENSITIVITY) | (a)(i) module surface on the arc | -26.67 | 2093 | – | 0.931 | (no sampling) | – | – |
| | (a)(ii) alone, reweighted run J | -26.50 | 2071 | 135k / 562k | 0.959 | 1837 | 2e+03 | 0.02 |
| | (b) core + E | -33.47 | 1530 | 140k / 515k | 0.469 | 1130 | 9.61e+04 | 0.23 |
| | (c) all except E | -36.71 | 1252 | 57k / 319k | 0.091 | 180 | 7.91e+05 | 0.22 |
| | all (with Australian term) | -31.63 | 1681 | 151k / 529k | 0.587 | 1737 | 6.24e+04 | 0.03 |
| hydroacoustics | all views | contributes nothing (0 by ruling, no P_D) | | | | | | |

| E | ln ER (a) vs core, (ii) / (i) | 90 % HPD: core mass in (a) / (a) mass in core | Bhattacharyya (a) vs core | median shift (a) − core, NM | ln E[L_E given all others] (c→all) | Bhattacharyya (c) vs all | KL(all ‖ all−E) nats / share of KL(all ‖ core) | Δ median, Δ 90 % area on removal |
|---|---|---|---|---|---|---|---|---|
| debris drift (finds) | -0.54 / -0.57 | 0.71 / 0.13 | 0.44 | 713 | -2.76 (-0.30 vs uniform) | 0.94 | 0.28 / 0.28 | -145 NM, -118k km² |
| searched areas | -0.88 / -0.85 | 0.40 / 0.07 | 0.35 | 881 | -0.81 (-0.64 vs uniform) | 0.89 | 0.48 / 0.48 | -142 NM, -168k km² |
| Pléiades (conditional on H) | +0.68 / +0.67 | 0.12 / 0.89 | 0.44 | 166 | -2.40 (+1.21 vs uniform) | 0.62 | 1.30 / 0.53 **>0.5** | -14 NM, +367k km² |
| drift + Australian non-recovery (SENSITIVITY) | -2.09 / -2.13 | 0.08 / 0.02 | 0.24 | 832 | -4.30 (-1.27 vs uniform) | 0.66 | 1.29 / 0.57 **>0.5** | -429 NM, -210k km² |

#### D1 00:19:29 BTO — four-stratum mixture, cause model q = 1/3 (other cause silent)

| evidence E | view | median lat | median along arc (NM from S tip) | 50 % / 90 % HPD km² | mass N of 33 S | effective sample N of 33 S | Kish ESS | on searched ground |
|---|---|---|---|---|---|---|---|---|
| core (satcom + flight + EoF) | = view (a) for the core | -37.21 | 1238 | 15k / 116k | 0.018 | 81 | 2.15e+06 | 0.77 |
| debris drift (finds) | (a)(i) module surface on the arc | -28.52 | 1961 | – | 0.765 | (no sampling) | – | – |
| | (a)(ii) alone, reweighted run J | -28.34 | 1946 | 145k / 552k | 0.771 | 342 | 2.17e+03 | 0.13 |
| | (b) core + E | -37.07 | 1243 | 27k / 158k | 0.049 | 139 | 1.31e+06 | 0.70 |
| | (c) all except E | -37.22 | 1240 | 38k / 225k | 0.059 | 106 | 1.09e+06 | 0.27 |
| | all | -36.35 | 1337 | 52k / 306k | 0.130 | 170 | 4.74e+05 | 0.20 |
| searched areas | (a)(i) module surface on the arc | -25.98 | 2146 | – | 0.787 | (no sampling) | – | – |
| | (a)(ii) alone, reweighted run J | -25.70 | 2136 | 152k / 612k | 0.779 | 93 | 1.14e+03 | 0.03 |
| | (b) core + E | -37.22 | 1240 | 38k / 225k | 0.059 | 106 | 1.09e+06 | 0.27 |
| | (c) all except E | -37.07 | 1243 | 27k / 158k | 0.049 | 139 | 1.31e+06 | 0.70 |
| | all | -36.35 | 1337 | 52k / 306k | 0.130 | 170 | 4.74e+05 | 0.20 |
| Pléiades (conditional on H) | (a)(i) module surface on the arc | -35.41 | 1407 | – | 0.003 | (no sampling) | – | – |
| | (a)(ii) alone, reweighted run J | -35.43 | 1406 | 10k / 44k | 0.005 | 2 | 1.01e+05 | 0.71 |
| | (b) core + E | -35.46 | 1406 | 10k / 53k | 0.000 | 40 | 1.91e+05 | 0.72 |
| | (c) all except E | -36.35 | 1337 | 52k / 306k | 0.130 | 170 | 4.74e+05 | 0.20 |
| | all | H | -35.56 | 1415 | 9k / 49k | 0.001 | 32 | 7.14e+04 | 0.20 |
| drift + Australian non-recovery (SENSITIVITY) | (a)(i) module surface on the arc | -26.67 | 2093 | – | 0.931 | (no sampling) | – | – |
| | (a)(ii) alone, reweighted run J | -26.55 | 2073 | 100k / 409k | 0.961 | 1920 | 2.08e+03 | 0.02 |
| | (b) core + E | -34.47 | 1486 | 88k / 354k | 0.402 | 549 | 1.74e+05 | 0.34 |
| | (c) all except E | -37.22 | 1240 | 38k / 225k | 0.059 | 106 | 1.09e+06 | 0.27 |
| | all (with Australian term) | -31.48 | 1719 | 104k / 392k | 0.576 | 941 | 8.99e+04 | 0.06 |
| hydroacoustics | all views | contributes nothing (0 by ruling, no P_D) | | | | | | |

| E | ln ER (a) vs core, (ii) / (i) | 90 % HPD: core mass in (a) / (a) mass in core | Bhattacharyya (a) vs core | median shift (a) − core, NM | ln E[L_E given all others] (c→all) | Bhattacharyya (c) vs all | KL(all ‖ all−E) nats / share of KL(all ‖ core) | Δ median, Δ 90 % area on removal |
|---|---|---|---|---|---|---|---|---|
| debris drift (finds) | -0.57 / -0.65 | 0.72 / 0.12 | 0.40 | 709 | -2.88 (-0.37 vs uniform) | 0.93 | 0.30 / 0.29 | -97 NM, -81k km² |
| searched areas | -1.00 / -0.99 | 0.32 / 0.05 | 0.31 | 899 | -0.99 (-0.80 vs uniform) | 0.88 | 0.54 / 0.52 **>0.5** | -94 NM, -148k km² |
| Pléiades (conditional on H) | +0.52 / +0.47 | 0.09 / 0.84 | 0.40 | 169 | -2.48 (+1.16 vs uniform) | 0.59 | 1.36 / 0.49 | -78 NM, +257k km² |
| drift + Australian non-recovery (SENSITIVITY) | -2.46 / -2.57 | 0.06 / 0.02 | 0.20 | 836 | -4.75 (-1.64 vs uniform) | 0.62 | 1.52 / 0.59 **>0.5** | -479 NM, -167k km² |

#### D2 00:19:29 BTO + BFO — four-stratum mixture, cause model q = 1/3 (other cause silent)

| evidence E | view | median lat | median along arc (NM from S tip) | 50 % / 90 % HPD km² | mass N of 33 S | effective sample N of 33 S | Kish ESS | on searched ground |
|---|---|---|---|---|---|---|---|---|
| core (satcom + flight + EoF) | = view (a) for the core | -37.13 | 1238 | 12k / 103k | 0.024 | 90 | 9.22e+04 | 0.84 |
| debris drift (finds) | (a)(i) module surface on the arc | -28.52 | 1961 | – | 0.765 | (no sampling) | – | – |
| | (a)(ii) alone, reweighted run J | -28.31 | 1954 | 108k / 399k | 0.776 | 277 | 1.06e+03 | 0.14 |
| | (b) core + E | -36.99 | 1245 | 24k / 149k | 0.061 | 132 | 5.91e+04 | 0.75 |
| | (c) all except E | -36.87 | 1249 | 45k / 250k | 0.093 | 126 | 3.46e+04 | 0.36 |
| | all | -35.82 | 1400 | 59k / 300k | 0.182 | 186 | 1.86e+04 | 0.24 |
| searched areas | (a)(i) module surface on the arc | -25.98 | 2146 | – | 0.787 | (no sampling) | – | – |
| | (a)(ii) alone, reweighted run J | -25.49 | 2158 | 93k / 399k | 0.799 | 86 | 576 | 0.03 |
| | (b) core + E | -36.87 | 1249 | 45k / 250k | 0.093 | 126 | 3.46e+04 | 0.36 |
| | (c) all except E | -36.99 | 1245 | 24k / 149k | 0.061 | 132 | 5.91e+04 | 0.75 |
| | all | -35.82 | 1400 | 59k / 300k | 0.182 | 186 | 1.86e+04 | 0.24 |
| Pléiades (conditional on H) | (a)(i) module surface on the arc | -35.41 | 1407 | – | 0.003 | (no sampling) | – | – |
| | (a)(ii) alone, reweighted run J | -35.42 | 1405 | 9k / 38k | 0.003 | 2 | 9.31e+03 | 0.73 |
| | (b) core + E | -35.45 | 1405 | 10k / 45k | 0.000 | 19 | 9.95e+03 | 0.74 |
| | (c) all except E | -35.82 | 1400 | 59k / 300k | 0.182 | 186 | 1.86e+04 | 0.24 |
| | all | H | -35.54 | 1415 | 8k / 42k | 0.000 | 19 | 3.91e+03 | 0.22 |
| drift + Australian non-recovery (SENSITIVITY) | (a)(i) module surface on the arc | -26.67 | 2093 | – | 0.931 | (no sampling) | – | – |
| | (a)(ii) alone, reweighted run J | -26.51 | 2080 | 79k / 298k | 0.961 | 890 | 963 | 0.02 |
| | (b) core + E | -34.11 | 1509 | 75k / 302k | 0.443 | 479 | 8.68e+03 | 0.34 |
| | (c) all except E | -36.87 | 1249 | 45k / 250k | 0.093 | 126 | 3.46e+04 | 0.36 |
| | all (with Australian term) | -30.59 | 1806 | 83k / 325k | 0.635 | 806 | 4.51e+03 | 0.06 |
| hydroacoustics | all views | contributes nothing (0 by ruling, no P_D) | | | | | | |

| E | ln ER (a) vs core, (ii) / (i) | 90 % HPD: core mass in (a) / (a) mass in core | Bhattacharyya (a) vs core | median shift (a) − core, NM | ln E[L_E given all others] (c→all) | Bhattacharyya (c) vs all | KL(all ‖ all−E) nats / share of KL(all ‖ core) | Δ median, Δ 90 % area on removal |
|---|---|---|---|---|---|---|---|---|
| debris drift (finds) | -0.58 / -0.64 | 0.68 / 0.12 | 0.41 | 717 | -2.79 (-0.30 vs uniform) | 0.94 | 0.26 / 0.23 | -151 NM, -50k km² |
| searched areas | -1.18 / -1.20 | 0.27 / 0.05 | 0.31 | 920 | -1.11 (-0.90 vs uniform) | 0.88 | 0.57 / 0.51 **>0.5** | -155 NM, -151k km² |
| Pléiades (conditional on H) | +0.59 / +0.60 | 0.10 / 0.87 | 0.42 | 168 | -2.29 (+1.30 vs uniform) | 0.62 | 1.25 / 0.46 | -15 NM, +258k km² |
| drift + Australian non-recovery (SENSITIVITY) | -2.35 / -2.44 | 0.06 / 0.02 | 0.22 | 842 | -4.40 (-1.32 vs uniform) | 0.66 | 1.31 / 0.51 **>0.5** | -557 NM, -75k km² |

#### D3 both BFOs as recorded — four-stratum mixture, cause model q = 1/3 (other cause silent)

| evidence E | view | median lat | median along arc (NM from S tip) | 50 % / 90 % HPD km² | mass N of 33 S | effective sample N of 33 S | Kish ESS | on searched ground |
|---|---|---|---|---|---|---|---|---|
| core (satcom + flight + EoF) | = view (a) for the core | -37.31 | 1236 | 6k / 57k | 0.015 | 36 | 6.35e+03 | 0.92 |
| debris drift (finds) | (a)(i) module surface on the arc | -28.52 | 1961 | – | 0.765 | (no sampling) | – | – |
| | (a)(ii) alone, reweighted run J | -28.94 | 1905 | 65k / 221k | 0.755 | 289 | 489 | 0.18 |
| | (b) core + E | -37.24 | 1238 | 11k / 77k | 0.040 | 58 | 4.35e+03 | 0.85 |
| | (c) all except E | -37.04 | 1244 | 21k / 122k | 0.082 | 46 | 1.4e+03 | 0.54 |
| | all | -36.06 | 1394 | 25k / 150k | 0.165 | 87 | 627 | 0.38 |
| searched areas | (a)(i) module surface on the arc | -25.98 | 2146 | – | 0.787 | (no sampling) | – | – |
| | (a)(ii) alone, reweighted run J | -25.75 | 2138 | 56k / 187k | 0.814 | 158 | 323 | 0.03 |
| | (b) core + E | -37.04 | 1244 | 21k / 122k | 0.082 | 46 | 1.4e+03 | 0.54 |
| | (c) all except E | -37.24 | 1238 | 11k / 77k | 0.040 | 58 | 4.35e+03 | 0.85 |
| | all | -36.06 | 1394 | 25k / 150k | 0.165 | 87 | 627 | 0.38 |
| Pléiades (conditional on H) | (a)(i) module surface on the arc | -35.41 | 1407 | – | 0.003 | (no sampling) | – | – |
| | (a)(ii) alone, reweighted run J | -35.43 | 1412 | 7k / 27k | 0.000 | 16 | 633 | 0.82 |
| | (b) core + E | -35.45 | 1413 | 6k / 28k | 0.000 | 18 | 621 | 0.83 |
| | (c) all except E | -36.06 | 1394 | 25k / 150k | 0.165 | 87 | 627 | 0.38 |
| | all | H | -35.56 | 1421 | 6k / 26k | 0.000 | 29 | 168 | 0.30 |
| drift + Australian non-recovery (SENSITIVITY) | (a)(i) module surface on the arc | -26.67 | 2093 | – | 0.931 | (no sampling) | – | – |
| | (a)(ii) alone, reweighted run J | -27.14 | 2040 | 43k / 143k | 0.959 | 294 | 319 | 0.03 |
| | (b) core + E | -34.77 | 1470 | 32k / 155k | 0.393 | 144 | 706 | 0.44 |
| | (c) all except E | -37.04 | 1244 | 21k / 122k | 0.082 | 46 | 1.4e+03 | 0.54 |
| | all (with Australian term) | -29.97 | 1837 | 34k / 153k | 0.647 | 142 | 289 | 0.08 |
| hydroacoustics | all views | contributes nothing (0 by ruling, no P_D) | | | | | | |

| E | ln ER (a) vs core, (ii) / (i) | 90 % HPD: core mass in (a) / (a) mass in core | Bhattacharyya (a) vs core | median shift (a) − core, NM | ln E[L_E given all others] (c→all) | Bhattacharyya (c) vs all | KL(all ‖ all−E) nats / share of KL(all ‖ core) | Δ median, Δ 90 % area on removal |
|---|---|---|---|---|---|---|---|---|
| debris drift (finds) | -0.53 / -0.64 | 0.53 / 0.11 | 0.40 | 670 | -2.78 (-0.24 vs uniform) | 0.94 | 0.24 / 0.21 | -149 NM, -28k km² |
| searched areas | -1.48 / -1.53 | 0.05 / 0.03 | 0.26 | 903 | -1.44 (-1.19 vs uniform) | 0.88 | 0.59 / 0.53 **>0.5** | -156 NM, -73k km² |
| Pléiades (conditional on H) | +0.49 / +0.62 | 0.10 / 0.78 | 0.40 | 176 | -2.16 (+1.32 vs uniform) | 0.63 | 1.16 / 0.41 | -27 NM, +124k km² |
| drift + Australian non-recovery (SENSITIVITY) | -2.53 / -2.65 | 0.03 / 0.02 | 0.19 | 805 | -4.42 (-1.30 vs uniform) | 0.66 | 1.37 / 0.47 | -593 NM, -32k km² |

#### D4 both BFOs, shared start-up offset — four-stratum mixture, cause model q = 1/3 (other cause silent)

| evidence E | view | median lat | median along arc (NM from S tip) | 50 % / 90 % HPD km² | mass N of 33 S | effective sample N of 33 S | Kish ESS | on searched ground |
|---|---|---|---|---|---|---|---|---|
| core (satcom + flight + EoF) | = view (a) for the core | -37.24 | 1236 | 5k / 51k | 0.019 | 17 | 4.44e+04 | 0.93 |
| debris drift (finds) | (a)(i) module surface on the arc | -28.52 | 1961 | – | 0.765 | (no sampling) | – | – |
| | (a)(ii) alone, reweighted run J | -28.81 | 1918 | 69k / 246k | 0.766 | 465 | 769 | 0.18 |
| | (b) core + E | -37.16 | 1238 | 8k / 78k | 0.053 | 28 | 2.91e+04 | 0.87 |
| | (c) all except E | -37.05 | 1243 | 18k / 136k | 0.115 | 27 | 1.15e+04 | 0.60 |
| | all | -35.79 | 1411 | 30k / 176k | 0.240 | 57 | 3.4e+03 | 0.42 |
| searched areas | (a)(i) module surface on the arc | -25.98 | 2146 | – | 0.787 | (no sampling) | – | – |
| | (a)(ii) alone, reweighted run J | -25.58 | 2151 | 56k / 225k | 0.839 | 127 | 403 | 0.04 |
| | (b) core + E | -37.05 | 1243 | 18k / 136k | 0.115 | 27 | 1.15e+04 | 0.60 |
| | (c) all except E | -37.16 | 1238 | 8k / 78k | 0.053 | 28 | 2.91e+04 | 0.87 |
| | all | -35.79 | 1411 | 30k / 176k | 0.240 | 57 | 3.4e+03 | 0.42 |
| Pléiades (conditional on H) | (a)(i) module surface on the arc | -35.41 | 1407 | – | 0.003 | (no sampling) | – | – |
| | (a)(ii) alone, reweighted run J | -35.43 | 1408 | 6k / 26k | 0.000 | 87 | 4.05e+03 | 0.86 |
| | (b) core + E | -35.40 | 1413 | 5k / 28k | 0.000 | 72 | 3.98e+03 | 0.87 |
| | (c) all except E | -35.79 | 1411 | 30k / 176k | 0.240 | 57 | 3.4e+03 | 0.42 |
| | all | H | -35.51 | 1420 | 6k / 29k | 0.000 | 53 | 3e+03 | 0.37 |
| drift + Australian non-recovery (SENSITIVITY) | (a)(i) module surface on the arc | -26.67 | 2093 | – | 0.931 | (no sampling) | – | – |
| | (a)(ii) alone, reweighted run J | -27.10 | 2046 | 48k / 171k | 0.959 | 542 | 588 | 0.03 |
| | (b) core + E | -34.20 | 1510 | 33k / 167k | 0.457 | 121 | 1.37e+03 | 0.43 |
| | (c) all except E | -37.05 | 1243 | 18k / 136k | 0.115 | 27 | 1.15e+04 | 0.60 |
| | all (with Australian term) | -28.88 | 1912 | 35k / 172k | 0.743 | 297 | 533 | 0.08 |
| hydroacoustics | all views | contributes nothing (0 by ruling, no P_D) | | | | | | |

| E | ln ER (a) vs core, (ii) / (i) | 90 % HPD: core mass in (a) / (a) mass in core | Bhattacharyya (a) vs core | median shift (a) − core, NM | ln E[L_E given all others] (c→all) | Bhattacharyya (c) vs all | KL(all ‖ all−E) nats / share of KL(all ‖ core) | Δ median, Δ 90 % area on removal |
|---|---|---|---|---|---|---|---|---|
| debris drift (finds) | -0.60 / -0.69 | 0.65 / 0.10 | 0.39 | 681 | -2.82 (-0.30 vs uniform) | 0.94 | 0.24 / 0.22 | -168 NM, -40k km² |
| searched areas | -1.55 / -1.63 | 0.04 / 0.02 | 0.26 | 914 | -1.53 (-1.25 vs uniform) | 0.89 | 0.58 / 0.52 **>0.5** | -173 NM, -98k km² |
| Pléiades (conditional on H) | +0.38 / +0.56 | 0.08 / 0.75 | 0.38 | 171 | -2.28 (+1.14 vs uniform) | 0.59 | 1.35 / 0.45 | -9 NM, +147k km² |
| drift + Australian non-recovery (SENSITIVITY) | -2.49 / -2.61 | 0.05 / 0.02 | 0.20 | 809 | -4.27 (-1.16 vs uniform) | 0.64 | 1.41 / 0.46 | -669 NM, -36k km² |

#### D5 00:19:37 BFO with start-up offset — four-stratum mixture, cause model q = 1/3 (other cause silent)

| evidence E | view | median lat | median along arc (NM from S tip) | 50 % / 90 % HPD km² | mass N of 33 S | effective sample N of 33 S | Kish ESS | on searched ground |
|---|---|---|---|---|---|---|---|---|
| core (satcom + flight + EoF) | = view (a) for the core | -37.28 | 1237 | 7k / 59k | 0.020 | 75 | 2.59e+04 | 0.92 |
| debris drift (finds) | (a)(i) module surface on the arc | -28.52 | 1961 | – | 0.765 | (no sampling) | – | – |
| | (a)(ii) alone, reweighted run J | -28.34 | 1952 | 72k / 238k | 0.778 | 407 | 657 | 0.17 |
| | (b) core + E | -37.21 | 1239 | 12k / 88k | 0.054 | 115 | 1.59e+04 | 0.85 |
| | (c) all except E | -36.99 | 1254 | 23k / 145k | 0.113 | 125 | 6.88e+03 | 0.55 |
| | all | -35.71 | 1415 | 35k / 180k | 0.224 | 180 | 3.13e+03 | 0.38 |
| searched areas | (a)(i) module surface on the arc | -25.98 | 2146 | – | 0.787 | (no sampling) | – | – |
| | (a)(ii) alone, reweighted run J | -25.09 | 2189 | 61k / 206k | 0.827 | 87 | 387 | 0.04 |
| | (b) core + E | -36.99 | 1254 | 23k / 145k | 0.113 | 125 | 6.88e+03 | 0.55 |
| | (c) all except E | -37.21 | 1239 | 12k / 88k | 0.054 | 115 | 1.59e+04 | 0.85 |
| | all | -35.71 | 1415 | 35k / 180k | 0.224 | 180 | 3.13e+03 | 0.38 |
| Pléiades (conditional on H) | (a)(i) module surface on the arc | -35.41 | 1407 | – | 0.003 | (no sampling) | – | – |
| | (a)(ii) alone, reweighted run J | -35.45 | 1409 | 6k / 27k | 0.006 | 1 | 2.68e+03 | 0.83 |
| | (b) core + E | -35.44 | 1411 | 6k / 29k | 0.000 | 6 | 2.52e+03 | 0.84 |
| | (c) all except E | -35.71 | 1415 | 35k / 180k | 0.224 | 180 | 3.13e+03 | 0.38 |
| | all | H | -35.53 | 1421 | 6k / 28k | 0.000 | 6 | 708 | 0.32 |
| drift + Australian non-recovery (SENSITIVITY) | (a)(i) module surface on the arc | -26.67 | 2093 | – | 0.931 | (no sampling) | – | – |
| | (a)(ii) alone, reweighted run J | -26.55 | 2079 | 52k / 159k | 0.965 | 440 | 473 | 0.03 |
| | (b) core + E | -34.22 | 1514 | 41k / 175k | 0.445 | 309 | 1.57e+03 | 0.42 |
| | (c) all except E | -36.99 | 1254 | 23k / 145k | 0.113 | 125 | 6.88e+03 | 0.55 |
| | all (with Australian term) | -30.03 | 1832 | 44k / 175k | 0.706 | 354 | 666 | 0.08 |
| hydroacoustics | all views | contributes nothing (0 by ruling, no P_D) | | | | | | |

| E | ln ER (a) vs core, (ii) / (i) | 90 % HPD: core mass in (a) / (a) mass in core | Bhattacharyya (a) vs core | median shift (a) − core, NM | ln E[L_E given all others] (c→all) | Bhattacharyya (c) vs all | KL(all ‖ all−E) nats / share of KL(all ‖ core) | Δ median, Δ 90 % area on removal |
|---|---|---|---|---|---|---|---|---|
| debris drift (finds) | -0.57 / -0.65 | 0.58 / 0.11 | 0.39 | 714 | -2.78 (-0.26 vs uniform) | 0.95 | 0.23 / 0.21 | -161 NM, -35k km² |
| searched areas | -1.51 / -1.56 | 0.05 / 0.03 | 0.26 | 952 | -1.45 (-1.20 vs uniform) | 0.88 | 0.59 / 0.52 **>0.5** | -175 NM, -92k km² |
| Pléiades (conditional on H) | +0.51 / +0.60 | 0.09 / 0.80 | 0.40 | 172 | -2.22 (+1.29 vs uniform) | 0.60 | 1.28 / 0.44 | -6 NM, +152k km² |
| drift + Australian non-recovery (SENSITIVITY) | -2.46 / -2.57 | 0.03 / 0.02 | 0.20 | 842 | -4.29 (-1.18 vs uniform) | 0.66 | 1.35 / 0.46 | -579 NM, -30k km² |

#### Headline products across the six 00:19 options (mixture)

| option | product | median lat (± seed SE) | 5 / 95 % lat | 50 / 90 / 95 % HPD km² | N of 33 S (± SE) | effective sample N of 33 S | ESS | on searched ground | waypoints share | A1 / A2 / B |
|---|---|---|---|---|---|---|---|---|---|---|
| D0 | core | -37.13 ± 0.02 | -38.41 / -33.87 | 19k / 162k / 262k | 0.032 ± 0.003 | 121 | 1.95e+06 | 0.724 | 0.9987 | 0.17 / 0.34 / 0.49 |
| D0 | ALL | -35.66 ± 0.07 | -38.46 / -27.68 | 87k / 437k / 581k | 0.190 ± 0.009 | 345 | 3.09e+05 | 0.148 | 0.9977 | 0.07 / 0.35 / 0.58 |
| D0 | ALL given H (conditional) | -35.40 ± 0.01 | -36.27 / -34.25 | 15k / 70k / 101k | 0.004 ± 0.000 | 219 | 6.53e+04 | 0.149 | 0.9966 | 0.06 / 0.31 / 0.63 |
| D0 | ALL + Australian term (sensitivity) | -31.63 ± 0.14 | -36.12 / -25.44 | 151k / 529k / 670k | 0.587 ± 0.009 | 1737 | 6.24e+04 | 0.033 | 0.9971 | 0.11 / 0.31 / 0.58 |
| D1 | core | -37.21 ± 0.02 | -38.48 / -34.58 | 15k / 116k / 182k | 0.018 ± 0.002 | 81 | 2.15e+06 | 0.774 | 0.9989 | 0.20 / 0.35 / 0.45 |
| D1 | ALL | -36.35 ± 0.13 | -38.63 / -27.86 | 52k / 306k / 416k | 0.130 ± 0.009 | 170 | 4.74e+05 | 0.202 | 0.9981 | 0.07 / 0.38 / 0.55 |
| D1 | ALL given H (conditional) | -35.56 ± 0.00 | -36.38 / -34.67 | 9k / 49k / 75k | 0.001 ± 0.000 | 32 | 7.14e+04 | 0.199 | 0.9971 | 0.05 / 0.33 / 0.62 |
| D1 | ALL + Australian term (sensitivity) | -31.48 ± 0.27 | -36.55 / -24.97 | 104k / 392k / 516k | 0.576 ± 0.012 | 941 | 8.99e+04 | 0.056 | 0.9973 | 0.10 / 0.34 / 0.57 |
| D2 | core | -37.13 ± 0.02 | -38.17 / -34.34 | 12k / 103k / 168k | 0.024 ± 0.002 | 90 | 9.22e+04 | 0.839 | 0.9988 | 0.24 / 0.23 / 0.53 |
| D2 | ALL | -35.82 ± 0.08 | -38.21 / -26.59 | 59k / 300k / 405k | 0.182 ± 0.012 | 186 | 1.86e+04 | 0.243 | 0.9979 | 0.08 / 0.31 / 0.61 |
| D2 | ALL given H (conditional) | -35.54 ± 0.01 | -36.27 / -34.65 | 8k / 42k / 64k | 0.000 ± 0.000 | 19 | 3.91e+03 | 0.218 | 0.9970 | 0.05 / 0.31 / 0.64 |
| D2 | ALL + Australian term (sensitivity) | -30.59 ± 0.26 | -36.20 / -24.69 | 83k / 325k / 435k | 0.635 ± 0.014 | 806 | 4.51e+03 | 0.056 | 0.9974 | 0.08 / 0.33 / 0.59 |
| D3 | core | -37.31 ± 0.02 | -38.03 / -34.74 | 6k / 57k / 84k | 0.015 ± 0.002 | 36 | 6.35e+03 | 0.917 | 0.9989 | 0.08 / 0.37 / 0.55 |
| D3 | ALL | -36.06 ± 0.19 | -37.89 / -26.78 | 25k / 150k / 204k | 0.165 ± 0.016 | 87 | 627 | 0.377 | 0.9979 | 0.04 / 0.34 / 0.62 |
| D3 | ALL given H (conditional) | -35.56 ± 0.03 | -36.32 / -34.86 | 6k / 26k / 39k | 0.000 ± 0.000 | 29 | 168 | 0.304 | 0.9976 | 0.02 / 0.31 / 0.67 |
| D3 | ALL + Australian term (sensitivity) | -29.97 ± 0.39 | -36.31 / -24.73 | 34k / 153k / 208k | 0.647 ± 0.021 | 142 | 289 | 0.081 | 0.9969 | 0.07 / 0.36 / 0.57 |
| D4 | core | -37.24 ± 0.03 | -37.99 / -34.67 | 5k / 51k / 83k | 0.019 ± 0.005 | 17 | 4.44e+04 | 0.935 | 0.9989 | 0.25 / 0.32 / 0.43 |
| D4 | ALL | -35.79 ± 0.26 | -37.86 / -26.20 | 30k / 176k / 235k | 0.240 ± 0.028 | 57 | 3.4e+03 | 0.419 | 0.9975 | 0.20 / 0.31 / 0.50 |
| D4 | ALL given H (conditional) | -35.51 ± 0.01 | -36.21 / -34.84 | 6k / 29k / 44k | 0.000 ± 0.000 | 53 | 3e+03 | 0.370 | 0.9972 | 0.07 / 0.33 / 0.60 |
| D4 | ALL + Australian term (sensitivity) | -28.88 ± 0.72 | -35.97 / -24.60 | 35k / 172k / 231k | 0.743 ± 0.021 | 297 | 533 | 0.078 | 0.9960 | 0.34 / 0.26 / 0.41 |
| D5 | core | -37.28 ± 0.02 | -38.00 / -34.48 | 7k / 59k / 92k | 0.020 ± 0.002 | 75 | 2.59e+04 | 0.921 | 0.9989 | 0.06 / 0.42 / 0.52 |
| D5 | ALL | -35.71 ± 0.07 | -37.86 / -26.24 | 35k / 180k / 235k | 0.224 ± 0.015 | 180 | 3.13e+03 | 0.382 | 0.9980 | 0.04 / 0.38 / 0.59 |
| D5 | ALL given H (conditional) | -35.53 ± 0.01 | -36.21 / -34.72 | 6k / 28k / 42k | 0.000 ± 0.000 | 6 | 708 | 0.317 | 0.9973 | 0.01 / 0.33 / 0.65 |
| D5 | ALL + Australian term (sensitivity) | -30.03 ± 0.17 | -36.01 / -24.79 | 44k / 175k / 230k | 0.706 ± 0.018 | 354 | 666 | 0.075 | 0.9975 | 0.06 / 0.37 / 0.58 |

#### Per end-of-flight family (D0' and D4), before the mixture

| option | family | product | median lat | 90 % HPD km² | N of 33 S | ESS | (a)(ii) drift alone median | (a)(ii) searches alone median |
|---|---|---|---|---|---|---|---|---|
| D0 | A1 | core | -37.04 | 31k | 0.026 | 9.99e+05 | -29.06 | -26.83 |
| D0 | A1 | ALL | -34.49 | 262k | 0.368 | 4.18e+04 | -29.06 | -26.83 |
| D0 | A1 | ALL given H (conditional) | -35.15 | 49k | 0.006 | 9e+03 | -29.06 | -26.83 |
| D0 | A2 | core | -37.28 | 157k | 0.029 | 7.44e+05 | -29.22 | -27.70 |
| D0 | A2 | ALL | -36.00 | 431k | 0.168 | 1.27e+05 | -29.22 | -27.70 |
| D0 | A2 | ALL given H (conditional) | -35.43 | 72k | 0.004 | 2.46e+04 | -29.22 | -27.70 |
| D0 | B | core | -37.15 | 187k | 0.037 | 7.22e+05 | -27.27 | -24.65 |
| D0 | B | ALL | -35.57 | 436k | 0.180 | 1.55e+05 | -27.27 | -24.65 |
| D0 | B | ALL given H (conditional) | -35.41 | 68k | 0.004 | 3.61e+04 | -27.27 | -24.65 |
| D4 | A1 | core | -37.05 | 17k | 0.031 | 4.59e+03 | -29.71 | -27.95 |
| D4 | A1 | ALL | -32.34 | 47k | 0.522 | 173 | -29.71 | -27.95 |
| D4 | A1 | ALL given H (conditional) | -35.21 | 12k | 0.000 | 243 | -29.71 | -27.95 |
| D4 | A2 | core | -37.32 | 51k | 0.014 | 4.27e+04 | -29.07 | -25.79 |
| D4 | A2 | ALL | -35.98 | 183k | 0.180 | 5.91e+03 | -29.07 | -25.79 |
| D4 | A2 | ALL given H (conditional) | -35.50 | 30k | 0.000 | 1.28e+03 | -29.07 | -25.79 |
| D4 | B | core | -37.38 | 56k | 0.016 | 2.82e+04 | -28.38 | -23.64 |
| D4 | B | ALL | -35.86 | 163k | 0.166 | 4.35e+03 | -28.38 | -23.64 |
| D4 | B | ALL given H (conditional) | -35.54 | 28k | 0.000 | 1.59e+03 | -28.38 | -23.64 |

#### Per flight family (core stratum), D0'

| stratum | core median | ALL median | ALL 90 % HPD km² | ALL N of 33 S | ALL ESS | share of ALL |
|---|---|---|---|---|---|---|
| run-j-waypoints | -37.13 | -35.67 | 437k | 0.190 | 3.08e+05 | 0.9977 |
| run-j-free | -36.42 | -35.35 | 465k | 0.226 | 1.03e+05 | 0.0016 |
| run-j-repro-radar | -36.45 | -35.18 | 485k | 0.299 | 8.71e+04 | 0.0004 |
| run-j-descent-climb | -36.98 | -35.61 | 441k | 0.187 | 8.3e+04 | 0.0003 |

#### Modes along the arc (impact latitude; D0', mixture; basins of the 0.15 deg-smoothed PDF with mass ≥ 0.001)

| product | modes: peak latitude (mass) |
|---|---|
| core | -37.14 (0.984); -29.48 (0.002); -28.93 (0.002); -27.48 (0.003); -26.76 (0.002); -26.20 (0.006) |
| ALL | -38.47 (0.079); -37.16 (0.280); -35.67 (0.305); -34.28 (0.194); -30.95 (0.051); -29.70 (0.017); -28.76 (0.013); -27.80 (0.021); -26.20 (0.040) |
| ALL given H (conditional) | -35.45 (0.998); -32.36 (0.002) |
| ALL + Australian term (sensitivity) | -35.59 (0.224); -34.14 (0.193); -32.61 (0.066); -30.88 (0.165); -29.70 (0.066); -28.79 (0.043); -27.59 (0.070); -26.20 (0.174) |

#### Labelled sensitivities on ALL (mixture)

| option | variant | median lat | 90 % HPD km² | N of 33 S | on searched ground |
|---|---|---|---|---|---|
| D0 | headline ALL | -35.66 | 437k | 0.190 | 0.148 |
| D0 | drift model error doubled (kernel 50 → 100 km) | -35.90 | 414k | 0.159 | 0.184 |
| D0 | searched-areas model error doubled (rho 0.05 → 0.10) | -35.76 | 425k | 0.178 | 0.200 |
| D0 | drift GLORYS12 only | -35.42 | 475k | 0.246 | 0.134 |
| D0 | drift GlobCurrent only | -35.88 | 369k | 0.132 | 0.163 |
| D0 | Australian populated-coast non-recovery added | -31.63 | 529k | 0.587 | 0.033 |
| D2 | headline ALL | -35.82 | 300k | 0.182 | 0.243 |
| D2 | drift model error doubled (kernel 50 → 100 km) | -36.11 | 288k | 0.150 | 0.301 |
| D2 | searched-areas model error doubled (rho 0.05 → 0.10) | -35.98 | 287k | 0.164 | 0.316 |
| D2 | drift GLORYS12 only | -35.63 | 334k | 0.249 | 0.230 |
| D2 | drift GlobCurrent only | -36.01 | 246k | 0.119 | 0.255 |
| D2 | Australian populated-coast non-recovery added | -30.59 | 325k | 0.635 | 0.056 |
| D4 | headline ALL | -35.79 | 176k | 0.240 | 0.419 |
| D4 | drift model error doubled (kernel 50 → 100 km) | -36.44 | 163k | 0.188 | 0.503 |
| D4 | searched-areas model error doubled (rho 0.05 → 0.10) | -36.12 | 163k | 0.202 | 0.511 |
| D4 | drift GLORYS12 only | -35.55 | 184k | 0.320 | 0.399 |
| D4 | drift GlobCurrent only | -35.99 | 154k | 0.157 | 0.440 |
| D4 | Australian populated-coast non-recovery added | -28.88 | 172k | 0.743 | 0.078 |
| D3 | core: production 24 seeds only (headline uses the both-burst supplementary waypoints) | -37.29 (headline -37.31) | 61k (57k) | 0.021 (0.015) | 0.914 |
| D3 | ALL: production 24 seeds only (headline uses the both-burst supplementary waypoints) | -35.67 (headline -36.06) | 162k (150k) | 0.225 (0.165) | 0.379 |
| D4 | core: production 24 seeds only (headline uses the both-burst supplementary waypoints) | -37.21 (headline -37.24) | 58k (51k) | 0.025 (0.019) | 0.927 |
| D4 | ALL: production 24 seeds only (headline uses the both-burst supplementary waypoints) | -35.50 (headline -35.79) | 181k (176k) | 0.323 (0.240) | 0.367 |

#### Not-computed share of the core weight, per factor column and 00:19 option

| option | PC | PG | h100C | h100G | h50C | h50G | no 00:19:29 crossing (weight 0 in arc-uniform views) | popC | popG |
|---|---|---|---|---|---|---|---|---|---|
| D0 | 5.29e-06 | 1.31e-06 | 1.67e-04 | 1.67e-04 | 1.67e-04 | 1.69e-04 | 4.70e-03 | 1.67e-04 | 1.69e-04 |
| D1 | 2.59e-10 | 3.20e-10 | 1.07e-04 | 1.07e-04 | 1.07e-04 | 1.09e-04 | 4.92e-03 | 1.07e-04 | 1.09e-04 |
| D2 | 6.82e-14 | 1.80e-12 | 1.76e-04 | 1.76e-04 | 1.76e-04 | 1.76e-04 | 6.21e-08 | 1.76e-04 | 1.76e-04 |
| D3 | 1.60e-66 | 5.31e-11 | 1.00e-05 | 1.00e-05 | 1.00e-05 | 1.00e-05 | 0.00e+00 | 1.00e-05 | 1.00e-05 |
| D4 | 1.14e-107 | 8.52e-16 | 7.46e-05 | 7.46e-05 | 7.46e-05 | 7.46e-05 | 0.00e+00 | 7.46e-05 | 7.46e-05 |
| D5 | 9.96e-35 | 2.39e-13 | 1.45e-04 | 1.45e-04 | 1.45e-04 | 1.45e-04 | 1.15e-286 | 1.45e-04 | 1.45e-04 |

#### Effective sample per 5° latitude band (D0', mixture): min(seed-scatter implied × band mass, Kish within band)

| product | -50…-45 | -45…-40 | -40…-35 | -35…-30 | -30…-25 | -25…-20 | -20…-15 | -15…-10 | -10…-5 |
|---|---|---|---|---|---|---|---|---|---|
| core | – | – | 1183 (m 0.89) | 145 (m 0.09) | 149 (m 0.01) | – | – | – | – |
| DS | – | – | 668 (m 0.61) | 414 (m 0.29) | 479 (m 0.08) | – | – | – | – |
| DSP | – | – | 18284 (m 0.78) | 5264 (m 0.22) | – | – | – | – | – |
| AS | – | – | 812 (m 0.19) | 1433 (m 0.46) | 1407 (m 0.32) | 343 (m 0.03) | – | – | – |
| a_D | – | 3 (m 0.01) | 136 (m 0.14) | 189 (m 0.24) | 212 (m 0.27) | 104 (m 0.11) | 19 (m 0.14) | 5 (m 0.08) | – |
| a_S | – | 4 (m 0.05) | 49 (m 0.12) | 89 (m 0.17) | 118 (m 0.20) | 72 (m 0.18) | 20 (m 0.17) | 7 (m 0.12) | – |
| a_P | – | – | 4389 (m 0.77) | 2340 (m 0.22) | – | – | – | – | – |
| a_A | – | – | 192 (m 0.02) | 200 (m 0.21) | 163 (m 0.39) | 159 (m 0.16) | 18 (m 0.15) | 4 (m 0.08) | – |