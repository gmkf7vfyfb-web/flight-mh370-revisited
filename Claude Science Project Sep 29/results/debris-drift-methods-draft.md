# Methods draft: the debris-drift likelihood

Ocean drift module, 9 October 2026. A first draft of the paper's drift methods section, per the
architecture entry of 9 Oct ~04:15 UTC ("for any module that runs out of unblocked steps"). Every
value is cited to the module ledger `results/debris-drift-references.md` (keys in square brackets)
or to a module file and commit. Values marked PROVISIONAL are working choices that the production
run may change. **Updated 9 Oct ~11:00 UTC** with the pilot (`results/debris-drift-pilot.md`) and the
production sizing (`results/debris-drift-production-sizing.md`). No number below is evidence about
the impact location.

## 1. What the term is

The drift module supplies one factor of the composed likelihood: ln p(D_drift | x), where x is an
impact location and D_drift is the recovered-debris record (where and when each identified item was
found). It does not move or resample the impact samples. It is computed once on a grid of source
nodes and read at each shared impact sample by bilinear interpolation **in likelihood** (not in log
likelihood), with land and unresolved corners renormalised out and flagged
(`interpolate.rs`; tests `interpolation_is_linear_in_likelihood_and_exact_at_nodes`,
`land_corners_renormalise_and_missing_corners_flag`).

The posterior decides where nodes go, never what the likelihood is worth: the impact posterior sets
the grid's extent, and nothing from it enters the likelihood.

## 2. Evidence

Nine items, the "stringent" set: those Malaysia's Ministry of Transport classed as confirmed or
almost certain from MH370, with dated discoveries in the western Indian Ocean [mot2018], in the order
and with the dates of [durgadoo2021, p. 2, Fig. 1]:

| item | found | status | motion class |
|---|---|---|---|
| right flaperon, Réunion | 29 Jul 2015 | confirmed | flaperon |
| engine cowling "Roy", Mossel Bay | 23 Dec 2015 (reported 22 Mar 2016) | almost certain | low-exposure exterior |
| right flap fairing, Paindane (Daghatane) | 27 Dec 2015 | almost certain | low-exposure exterior |
| horizontal stabiliser panel, Vilanculos | 27 Feb 2016 [mot2017, p. 2] (evidence table: 28 Feb; recorded conflict) | almost certain | low-exposure exterior |
| door closet panel, Rodrigues | 30 Mar 2016 | almost certain | high-windage interior |
| right fan cowling, Chidenguele | 24 Apr 2016 | almost certain | low-exposure exterior |
| left outboard flap, Mauritius | 10 May 2016 | confirmed | low-exposure exterior |
| cabin interior panel, Antsiraka | 12 Jun 2016 | almost certain | high-windage interior |
| right outboard flap, Pemba | 23 Jun 2016 (MOT: 20 Jun [mot2017, p. 10]; recorded conflict) | confirmed | low-exposure exterior |

The table is `data/debris-evidence-audit.csv` (41 rows, sha256 `f8ab96a9…5a332f69`), filtered on
`stringent_nine`. None of the nine has an identification that used prior drift modelling (column
`identity_uses_prior_drift` = no for all nine), so the evidence is not partly constituted by a drift
answer. Two date conflicts, Vilanculos (1 day) and Pemba (3 days), sit inside a 60-day delay prior;
they are carried as a `date_overrides` sensitivity, not as edits to the table.

**Find episodes.** Items are grouped into detection blocks by coast segment and period (ruling G1,
`results/debris-drift-find-episodes.md`). Six segments: S1 Réunion; S2 Mauritius and Rodrigues;
S3 southern Mozambique; S4 the South African south coast; S5 north-east Madagascar; S6 Pemba.
Three periods: I1 before 29 Jul 2015; I2 to the end of February 2016; I3 March to June 2016.

## 3. Source grid

Nodes lie on a regular latitude-longitude grid at a configured spacing (10 NM for the pilot) over
the smallest region holding a configured fraction of impact-posterior mass (99%), plus a margin
(100 NM). Connected components are linked at 40 NM. A detached northern island of mass is a
separate, optional patch, which is reported as a labelled sensitivity (`source_grid.rs`;
`results/debris-drift-pilot-sizing.md`). On the no-exhaustion-prior reference map, the main band
has 1,709 nodes and holds 0.971 of mass. The island patch has 1,390 nodes. PROVISIONAL: the extent
is re-derived from the final impact samples before production.

## 4. Transport

Each node releases particles at the end-of-flight epoch (8 Mar 2014, 00:19:37 UTC) and integrates
them forward with the shared ocean transport (`crates/ocean`, RK2, 6 h step) to 30 Jun 2016. Fields:
- surface currents from GLORYS12V1, daily means at 0.494 m [glorys12];
- 10 m wind from ERA5, 3-hourly [era5].

A particle's velocity is the water velocity plus a wind-driven term. This is CSIRO's implicit system
(ruling D-b). Its wind fraction carries Stokes drift and true windage together, as CSIRO
calibrated it on undrogued drifters [griffin2016parti, pp. 3, 11]. So no separate Stokes field is
added (`leeway_absorbs_stokes = true`) [sutherland2020].

**Transport-model error.** The shared ocean transport's GDP drifter replay measures each product's
error against undrogued drifters in the search box: σ about 0.09-0.12 m/s, with a decorrelation time T
of about 5-15 days (`results/ocean-transport-error-gdp-replay.md`). That is an order of magnitude more
spread than CSIRO's 5 NM/day random walk, K = 248 m²/s [griffin2017partiii, p. 6].

Production represents this error as the shared eddying error field, with one realisation per
environment draw.
- It uses σ_eff² = σ² − K_ref/T, with K_ref = 248 m²/s. The random walk and the error field together
  then reproduce the replay's single-particle spread.
- The field's length scale, 100 km, is assumed rather than measured (PROVISIONAL).
- K itself becomes a sub-mesoscale prior, log-uniform over 100-1,000 m²/s, drawn per environment
  (ruling 4).
- The pilot used K = 248 m²/s and no error field.

**Ocean models.** GLORYS12 + ERA5 is the reference. Copernicus-GlobCurrent + ERA5 is the second
`ocean-model` value, at equal prior weight (ruling of 9 Oct ~07:00 UTC). OSCAR is a comparison product only and enters no likelihood (Pete, 9 Oct ~17:50 UTC).
**Declared difference from CSIRO:** CSIRO's 1.2% windage was applied to BRAN2015's 0-5 m layer
[griffin2017partiii, p. 6]; this term applies it to GLORYS12 (0.494 m) and GlobCurrent surface currents.
BRAN2016 is not used (Pete, 9 Oct ~18:30 UTC).

**Object response by class** (`production-glorys12.toml`; PROVISIONAL priors except the flaperon's):
- **Flaperon.** 1.2% of wind [griffin2017partiii, p. 6], plus an extra leeway of 0.10 ± 0.03 m/s at
  0-30° left of downwind. These are the at-sea measurements on a genuine cut-down 777 flaperon
  [griffin2017partii, pp. 10, 17; ruling D-a]. They are not the earlier replica-based taper
  [griffin2016parti, p. 9; `results/debris-drift-flaperon-provenance.md`]. The angle rotates only
  the extra leeway, and the 1.2% term is downwind, which is what CSIRO does [griffin2017partii, p. 13;
  ruling D-f; shared API `07cced0`]. The pilot predates that API: it rotated both terms by one angle,
  and declared it.
- **Low-exposure exterior parts** (flaps, fairings, cowlings, panels): wind fraction N(1.2%, 0.3%)
  truncated to 0.5-2%, and a windage angle (`wind_angle_deg`) N(0°, 10°). These are the 1.2% items "subject to Stokes Drift but
  not direct wind forcing" [griffin2017partiii, p. 6].
- **High-windage interior parts:** a log-normal wind fraction with median 2.5% (σ = 0.35), truncated
  to 1-5%, and a windage angle N(0°, 15°). This brackets CSIRO's 3% for items floating higher
  [griffin2017partiii, pp. 6, 8].

Each class's response is drawn per particle, so the response is integrated inside the likelihood.
It is not a global factor; an earlier study found the response to dominate the answer
(brief §9).

**Beaching.** Production beaches particles on the shared GSHHG 2.3.7 full-resolution coastline
(ocean transport deliverable 6, `4eba004`). Each beaching is at the crossing point, with the line and
chainage of the hit. A product land-mask stranding within 25 km of the shore snaps to that shore; any
other land gap is model error.

The pilot instead read land-mask stranding itself as beaching, and that reading has a blind spot. The
shared field reports a land gap only when every interpolation corner is land. Rodrigues is a single
GLORYS12 land cell, so it could never strand a particle, and the pilot's Rodrigues term was a
structural zero (`results/debris-drift-production-sizing.md`).

Particles that leave the domain or meet a field gap are kept
in the denominator as not recovered (weight by termination, brief §9). They are never dropped.

## 5. Recovery-observation model

For find j, of class c(j), found at place y_j in the interval [t_j, t_j + w_j) in block b(j), and
particle i of class c beaching at place z_i and time τ_i:

- **Kernel:** k_ij = φ(d(y_j, z_i)/h)/h, with h = 50 km (25, 100 and 200 km reported from the same
  ensembles), cut at 6σ. A pair beyond the cut-off contributes zero; a find with no particle inside
  the cut-off makes the node Monte Carlo unresolved, which is reported, never floored.
- **Delay:** discovery follows beaching after an exponential delay with mean 60 days. The delay is
  declared a priori and never fitted (brief §4), with sensitivities at 30 and 120 days.
- **Block coefficients:**
  a_jb = (1/N) Σ_i k_ij · P(discovery in [t_j, t_j + w_j) ∩ period b | τ_i) / w_j,
  and the class's recovery mass A_cb = (1/N) Σ_i m_s(z_i) · P(discovery in period b before the
  window end | τ_i), with m_s the particle's membership of segment s.
- **Identification levels:** ν_b ≥ 0 per block, latent and marginalised. ln ν_b ~ N(μ_period, 1),
  with μ = ln 0.1, ln 0.5 and ln 1 for I1-I3, independent by block (PROVISIONAL, pending values from
  the architect). A global constant in ν cancels; block ratios do not (ruling D5;
  test `a_global_constant_in_the_levels_cancels_but_block_ratios_do_not`).
- **Likelihood at a node:**
  L(x) = E_η E_ν Π_j [ Σ_b ν_b a_jb(x) / Σ_b ν_b A_c(j)b(x) ].
  Each factor is the density of the find's place and date, given that an item of its class was
  recovered somewhere identified within the window. The conditioning denominator depends on the
  source and is kept explicitly (brief §4). Coasts outside the six segments carry ν = 0. The
  Western Australian non-recovery term is deferred (brief §13).

## 6. Monte Carlo estimation

- **Ensembles.** One forward ensemble per node per class is shared by every find of that class
  (brief §9), with N/2 particles in each split half.
- **Common random numbers.** Every node uses the same response draws, the same diffusion seeds per
  environment realisation, and the same 256 level draws. The surface's Monte Carlo error is
  therefore smooth across nodes (test `level_draws_are_common_and_declared`).
- **Combination.** E_η and E_ν are taken outside the product, by log-sum-exp over environment and
  level draws (test `environment_and_levels_are_marginalised_outside_the_product`).
- **Noise.** The split halves give a per-node noise estimate, var(ln L_A − ln L_B)/4.
- **Kernel resolution.** Kish effective sizes and hit counts per find are written for every node
  (`9475ae5`).
- **Importance splitting** (`fbaad33`, `84b6f85`, `ec20f78`).
  - A low-exposure or high-windage particle whose daily position first comes within R of a rare find
    is replaced there by M children of weight 1/M.
  - The children keep the parent's response and ocean-error realisation, and get their own diffusion.
  - Settings: Rodrigues R = 150 km, M = 20; Mossel Bay R = 500 km, M = 100.
  - Expectations are unchanged. In the analytic test, brute force gave 1.285e-2 ± 5.6e-4 and splitting
    1.329e-2 ± 9.2e-4 (test `splitting_is_unbiased_and_resolves_a_rare_target`).
- **Zero environment terms.**
  - An environment realisation whose product is zero enters the mean over environments as zero, which
    is its unbiased estimate.
  - A node is Monte Carlo unresolved only when every realisation is zero.
  - The zero fraction is reported per node (test
    `a_zero_environment_enters_the_mean_but_all_zero_is_unresolved`).
- **Sizing** (step 4).
  - 10⁵ particles per node (4 environments × 3 classes × 8,334), at 30 NM spacing: 193 main-band
    nodes.
  - The target is a split-half SD of about 0.5 in ln L.
  - The likelihood surface changes by at most ~2 ln units over ~100 NM, so linear interpolation at
    30 NM costs well under one unit.

## 7. Checks

- **Synthetic recovery.** Finds are generated from a node drawn uniformly on a small analytic grid.
  The 90% HPD region covered the true node in 58 of 60 trials (0.97). The calibration ratio was
  1.056, where 1.0 is ideal: the summed posterior probability at the true node divided by its
  expectation under the posteriors themselves (Σ_trials Σ_k p_k²) (test `synthetic_recovery_coverage`, run
  9 Oct).
- **Reproduction of Davey et al. ch. 11.** The flaperon-only drifter-replay likelihood moved the
  reference median 2.75 NM north with ESS 0.988 [davey2016, pp. 103-109; gdp6h]. With a 0.25°
  kernel the shift was 1.16 NM (`results/davey-ch11-reproduction.md`).
- **Real-field checks.** Land-mask stranding at Réunion works on the GLORYS12 + ERA5 series
  (`smoke-fields.toml`). At 2 threads, throughput was 1.43 × 10⁶ particle-steps per second in the
  check, and 1.72 × 10⁶ over the whole pilot.
- **Pilot** (`results/debris-drift-pilot.md`; PROVISIONAL, not evidence).
  - Scale: 1,709 nodes and 1.7 × 10⁷ trajectories.
  - No node resolved at 50 km.
  - Arrival probabilities at Réunion, Mauritius-Rodrigues and NE Madagascar were 7-30× above the
    prediction committed before the run.
  - The correlation length was not resolved.

## 8. Not yet in the term

- the Western Australian non-recovery term (brief §13);
- the 2014 surface-search observation (deferred; ruling of 9 Oct ~04:15 UTC);
- refloating;
- biofouling;
- a BRAN2016 arm: dropped (Pete, 9 Oct ~18:30 UTC). CSIRO applied the 1.2% windage to BRAN2015's 0-5 m layer [griffin2017partiii, p. 6]; here CSIRO's system runs on GLORYS12's 0.494 m currents and on GlobCurrent, and that difference from CSIRO's configuration is declared;
- the explicit-Stokes arm (WAVERYS);
- a wind-dependent extra leeway (the Part I taper) as a sensitivity.
