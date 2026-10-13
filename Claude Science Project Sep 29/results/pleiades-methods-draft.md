# Methods draft: the Pléiades / COSMO-SkyMed conditional hypothesis

Pléiades module. First draft 9 October 2026; revised overnight 10 October 2026 (OVERNIGHT-2026-10-10.md, "until then:
work the methods draft and the citation ledger"). Keys in square brackets refer to `results/pleiades-references.md`.
Code is in `engine/hypotheses/pleiades/` on branch `hypothesis/pleiades`; results are in `results/pleiades/`.

**Status.** Every number is PROVISIONAL. Five things make it so:
- the flight posterior (`reference-289`, end of flight's `eof-289-full` impacts) uses the tempered sampler with the
  ancestry defect found by the filter audit (F1, core request 17) and the uncorrected fuel model. Both are replaced
  by the overnight run of 10-11 October, and every flight-conditioned number here is superseded when it lands;
- end of flight's dive class (b) and the Boeing-calibrated glide are provisional;
- the COSMO-SkyMed source, time and footprint are unverified [COSMO-pos];
- the Ocean Infinity 2018 and 2025-26 layers are community tracings (grade C);
- the Pléiades-COSMO transport-error correlation is unmeasured (§6.4).

**Nothing here is evidence that any imaged object came from 9M-MRO.** Every PDF is conditional on H.

## 1. The hypothesis and what the module returns

H states that at least one object imaged by Pléiades-1A on 23 March 2014 [GA2017], or detected by COSMO-SkyMed on
21 March 2014 [COSMO-pos], came from 9M-MRO.
- H is a **conditional** hypothesis. The module enters the estimator through a single discrete alternative,
  `pleiades-origin` = {not-H, H}, and the composer sweeps its prior.
- Under H the module returns an impact log-likelihood ln L(s | H) from **positional compatibility under forward
  transport only**. Under not-H it returns 0, the background against which H is measured.
- **There is no identity likelihood.** Shape and size were screened and give none:
  - the archived morphology screen is a negative result;
  - its "PCA loss" is a mask-overlap score, not a class probability;
  - the flaperon size check uses a proxy dimension [Morph-archive].
- Object ratings therefore enter only as a declared **weight** on which objects to treat as candidates (§2), never
  as evidence for H.
- The module never filters or pre-selects impact samples (composition rule 2).

## 2. Observations

**Pléiades.**
- There are 70 objects in four scenes, PHR_1 to PHR_4, from GA Record 2017/13 Tables 1–4, pp. 13–19 [GA2017].
- Rating 5 ("probably man-made") covers 12 objects (p. 6), and rating 4 covers 27. A CSIRO press release says
  28 [CSIRO2017]; it is not used.
- One transcription correction was made: the latitude and longitude of PHR_2 object 12 are transposed in Table 2.
- One anomaly is flagged and left uncorrected: PHR_2 object 11 has an area-per-pixel 2.2 times the median of the
  other 69 objects.
- Scene times are 04:24 UTC (PHR_4, and PHR_2 by assumption) and 04:28 UTC (PHR_1, PHR_3)
  (`data/acquisition-times.csv`; [Orbits], unverified).

**Object model** (`results/pleiades/d2-object-model.md`).
- Objects closer than 3 km are merged into clusters, because they may be fragments of one break-up.
- Rating 5 gives 6 clusters. Ratings 5 + 4 give 12 clusters, seven of which contain no rating-5 object.
- Two alternatives are carried rather than chosen:
  - `object-rating`: the rating-4 weight ρ4 ∈ {0, 0.25, 0.5, 1};
  - `cluster-weight`: equal per cluster, or proportional to object count.

**COSMO-SkyMed.**
- Contacts F1–F3 form the reference set, and F1–F4 the extension (`data/cosmo-contacts.csv`) [COSMO-pos].
- The pass is uncertain, so it is a two-option alternative `cosmo-pass`: dusk on 21 March (11:56 UTC) or dawn on
  20 March (23:56 UTC), each ±25 min. That gives a COSMO-to-Pléiades interval of 40.5 h or 52.5 h [Orbits].
- No footprint or target size is known. COSMO is therefore **not** in the impact likelihood (P2, endorsed
  9 Oct ~06:45 UTC). It enters only the two-epoch calibration of §5.

## 3. Forward transport

- Each impact location is released at 00:20 UTC on 8 March 2014 and advected deterministically to the scene times
  with the shared `mh370-ocean` integrator:
  - RK2 with a 1 h step;
  - surface current plus c_wind × ERA5 10 m wind [ERA5];
  - Stokes drift absorbed in the windage (the leeway-absorbs-Stokes system);
  - no coastline, and no stochastic terms.
- Two current products form the `ocean-model` alternative at equal prior weight, as ruled 9 Oct ~07:00 UTC [OT-REC]:
  - GLORYS12V1 [GLORYS12];
  - Copernicus-GlobCurrent, daily total current [OT-REC].
- Using the daily GlobCurrent table makes the option label equal drift's, so the two are marginalised jointly
  (rule 7). The hourly table is a sensitivity (§6).
- Tracks are tabulated on a 0.1° release grid over 85–103 E, 43–25 S, at 21 windage nodes from 0 to 5 %
  (`export.rs`). They are interpolated bilinearly in release position.
- **Verification.** An independent RK4 oracle (1 h step, bilinear in space, linear in time) on the raw daily
  current fields plus c·ERA5 reproduces the tables to a median 0.007 km and at most 0.073 km, over 60 random
  origin / windage / output-time cases per product (`results/pleiades/closeup-289/audit/audit-integrator.csv`).
  At these step sizes, integration error is therefore negligible against a transport spread of about 100 km.
- The explicit-Stokes (WAVERYS) object response is **not** an arm. It would need a windage prior refitted for that
  system (ruled 9 Oct ~06:45 UTC).

## 4. The positional likelihood (deliverable 3)

For impact s and target c (an object or cluster at y_c, scene time t_c):

  p(y_c | s) = (1/N_w) Σ_k N₂(y_c ; x_k(s, t_c), diag(v_E, v_N)),

where x_k is the deterministic endpoint under windage node k. Each component variance is

  v_i(Δt) = 2σ_i²T_i [Δt − T_i(1 − e^(−Δt/T_i))] + sd_target²,

the dispersion of a displacement with exponentially correlated velocity error [Taylor1921; equation location to
be checked].

**Measured parameters.** σ_i and T_i are ocean transport's OU fit to its replay of GDP drifters through the same
integrator [OT-GDP], subset undrogued, box 80–110 E 45–20 S, March–May starts, current + 1 % ERA5: 808 segments
from 60 drifters.
- GLORYS12: σ = 0.1153 / 0.1176 m/s and T = 6.13 / 4.20 d (east / north).
- GlobCurrent: σ = 0.1043 / 0.0955 m/s and T = 16.02 / 7.64 d.
- The replay residual against real drifters already contains sub-grid dispersion, so no separate diffusivity
  is added.
- Over the 15.2 days from impact to Pléiades, the per-component sd is 95–118 km.
- **Check against the replay.** At every lead time from 1 to 15 days the fitted variance reproduces the replay's
  empirical rms to within about 5 %; it runs about 20 % low at 6–12 h. At 15 d the replay gives 95–120 km rms per
  component; the bootstrap 95 % range over drifters is 81–137 km (`audit-spread-vs-gdp.csv`).
- sd_target = 0.5 km.
- **Verification.** An independent evaluation of p(y|s) from the release tables reproduces the hook's exported
  surfaces to |Δ ln L| ≤ 8 × 10⁻⁵ (Pléiades) and ≤ 1 × 10⁻⁴ (COSMO) at 300 random grid points each
  (`audit-summary.json`).

**Likelihood under H.**

  L(s | H) = Σ_c w_c p(y_c | s) · A_scene,  with A_scene = 500 km².

- A_scene is the scene area, "approximately 25 km × 20 km" (p. 8) [GA2017].
- w_c are the declared cluster weights.
- The factor A_scene sets the scale of q_c = 1/A_scene, the density of a target under not-H.
- The likelihood is analytic and seed-free. The hook's own values are exported on a 0.05° grid
  (`pleiades_export_likelihood_surface`), and every downstream analysis uses that surface.
- **The absolute Bayes factor H : not-H is not interpretable** until a Poisson and footprint term for scene coverage
  exists (P1, endorsed). We report the conditional PDF and its tension, never P(H | D).

## 5. Two-epoch windage calibration (deliverable 5)

If COSMO contacts and Pléiades objects were the same items, observing them 40.5–52.5 h apart could calibrate
their windage.
- The object matching is **enumerated exactly, not sampled.** We enumerate all partial injective assignments of
  contacts to targets, with prior π_m·w per match and likelihood ratio p · A_scene.
- The matching spaces are small: 229 (F1–F3 × 6 clusters), 1,045, 1,753, 18,001, and 2,202,409 for the largest
  arm (`results/pleiades/d5-two-epoch.md`, `d2-object-model.md`).
- The model error is treated two ways, independent or shared between epochs. The pass time is either known or
  marginalised.

**Validation by injection–recovery** (`d5-two-epoch.md`):
- Coverage is nominal: 0.65–0.76 at 68 % and 0.85–0.93 at 90 %.
- At the declared spread, three true matches give 0.003–0.008 bits.
- Recovery needs sd ≲ 6 km and π_m = 0.9 (1.7 bits at 3.4 km). Marginalising the pass costs 24–39 % of the
  information, and the true pass is identified with P ≤ 0.80.

**Real data.**
- At the measured spread, which is 13–16 km per component over 40.5 h, the information gain is 0.001–0.07 bits for
  both products. ln BF(free vs fixed windage) lies between −0.12 and −0.01, and P(dawn pass) is 0.50–0.53
  (`results/pleiades/rerun-measured/`).
- F4 is never matched: it lies 60–115 km from every target.
- **The calibration carries no information.** Ocean transport reached the same conclusion independently from the
  replay [OT-GDP].

## 6. Conditional PDF and tension (deliverables 1 and 4)

**The two are always reported together.** A narrow conditional PDF can be a symptom of tension rather than of
precision.

### 6.1 First run: reference-snapshots and the provisional descent kernel (superseded by §6.2)

**Unconditional input.** The impact distribution is the reference flight posterior: per-particle positions at
00:19:37, 8 seeds × 7,000,000 particles [Ref-snapshots]. It is convolved with a descent kernel, the provisional
eof-2f [EoF-reach]:
- 0.934 on a 15 NM disk;
- 0.032 on the north-west quadrant of the 30–50 NM annulus;
- 0.034 on the north-west quadrant of the 50–103.4 NM annulus;
- disks of 7.5–103.4 NM as a sweep [EoF-glide].

**Statistics.** On the module domain we compute:
- the Bayes ratio R against a flat prior;
- the information ratio ln I and suspiciousness ln S = ln R − ln I [HL2019 eqs. 9–10];
- Bayesian model dimensionalities d̃ = 2 Var_P[log P/π] [HL2019 eq. 3] and the shared d = d̃_A + d̃_B − d̃_AB;
- the tension probability p = P(χ²_d > d − 2 ln S) [HL2019 eq. 25, Proposition 2]. Moderate tension is p ≲ 0.05.
  For non-Gaussian posteriors p is only a rough calibration;
- two-way 90 % HDR overlap, mode and mean shift;
- the conditional mass in the "western lobe": the H-alone HDR at ≥ 30 and ≥ 50 NM inside the 7th arc (§11).

**Results** (`results/pleiades/rerun-measured/rerun-measured.md`; ranges over the eight object-rating ×
cluster-weight arms, pooled seeds, eof-2f):
- **There is no significant tension.** p = 0.11–0.18 pooled and 0.10–0.22 across seeds, with ln S between −1.13 and
  −0.83 and d between 1.6 and 2.4, for either product and for their equal-weight mixture.
- **The conditional is broad.**
  - Its 90 % HDR is 28,700–33,300 km², against 38,628 km² unconditional, and contains 56–71 % of the unconditional
    mass.
  - The mean moves 99–126 NM north-east along the arc (82–143 NM across seeds).
  - The mode is unconverged: it moves 126–229 NM between seeds.
- **The western lobe mostly does not survive the descent reach.** 5.4–7.4 % of the conditional mass lies at
  ≥ 30 NM, and 2.9–4.9 % at ≥ 50 NM. With disks the share rises from 0 at 15 NM to 46 % at 103.4 NM, so this result
  waits on end of flight's displacement histogram.
- **Sensitivities:**
  - Hourly instead of daily GlobCurrent changes ln S by ≤ 0.012 and the mean shift by ≤ 0.8 NM.
  - The superseded declared spread (σ_e 0.05 m/s, T_e 2 d, K 30–1000 m²/s) gave an apparently precise
    conditional: an HDR of 8,500–12,100 km² holding only 6–10 % of the unconditional mass. Its p was still
    0.10–0.36. That precision was an artefact of the under-stated transport error.

### 6.2 The conditional branch on end of flight's impacts

**Input.** End of flight's reference-289 impacts (`eof-289-full`): 4 seeds × 100,000 parents × 8 children × 4
descents, 12,799,968 impacts. Each impact is weighted by its weight × exp(loglik:<option>), where <option> is the
00:19 data option. Options are never mixed by evidence. The log-on cause is "other".

**Fields** (`prepare/branch_eof289.py`). The fields are P (Pléiades), C3 (COSMO F1–F3), C4 (F1–F4), and the joint
P+C3 and P+C4. The COSMO likelihood marginalises the dawn-20 / dusk-21 March pass with equal weight inside each
ocean model. Each joint is formed per ocean model (L_P,m · L_C,m), because one ocean drives both, and then averaged
over models with equal weight. COSMO enters only as these prediction fields: it has no Bayes factor and no
provenance probability.

**Search evidence.** We use the searched-areas module's own per-impact column from `mh370 evaluate`, never a
recomputation. That column is the miss probability ρ + (1 − ρ) Π_k (1 − q_k c_k), with ρ = 0.05 shared between
campaigns. Three variants are run:
- base: Phase 2, q = 0.945; Bluefin-21, q = 0.9;
- + OI 2018: q = 0.9, coverage fraction 0.889;
- + OI 2025-26 south-east band: q = 0.9, coverage fraction 0.7808.

The OI layers are grade-C community tracings. The inferred north-west band is drawn but is never negative evidence.

**Results, 00:19 held out** (`branch-289/branch-289.md`, `closeup-289/closeup-289.md`):
- Unconditional 90 % HDR: 620,510 km² before the search, 730,426 km² after; the search retains Z = 0.733.
- P+C3: 90 % HDR 50,821 → 49,925 km². P+C4: 58,900 → 57,306 km² (base search), then 59,316 km² with both OI layers.
- Under H with OI applied, 87–88 % of the conditional mass lies outside every past search envelope. 4.5–5.2 % lies in
  the inferred north-west band.
- The 50 % region of P+C4 is 4,698 km². It lies around 35.1 S 91.3 E, about 49 NM inside the 7th arc.
- ln S is +0.46 to +1.36 in every arm, so there is no tension.
- Common origin of P and C: ln S ≈ +1.04 to +1.09, a low-power test.

**The 00:19 option dominates the after-search result** (`branch-289/branch-by-0019-option.csv`):
- R600 only, raw: the search keeps only 0.35–0.39 of the conditional mass, against 0.70–0.73 with 00:19 held out.
- r600/inflated: 0.385–0.435. r1200/inflated: 0.546–0.559.
- The results are reported by option, never pooled.

### 6.3 Comparison with the prior work

The prior work's residual origin density [Prior-Pleiades] had:
- a 90 % area of 57,708 km² and a mode near 35.3 S 92.2 E;
- a 50:50 sensor pool, the 21 March pass and windages 0 / 1.25 / 3 %;
- a 5 NM/day random walk plus a 10 km endpoint kernel, which gives 27–37 km per component at 15 d.

Putting those settings on our two ocean models (`prepare/audit_closeup.py`) gives a 90 % area of 57,436 km²
(52,823–69,465 km² across 27–37 km) and a mode at 35.38 S 92.38 E. **The prior map is reproduced to within its
spread setting.** Changing only the spread to the measured one gives 233,802 km², with the mode at 35.08 S 91.38 E.

The difference between the two analyses is therefore the transport error, not the ocean models. The measured
error is 3–4 times the prior work's assumption. With an error of about 105 km per component against a drift of
60–120 km, origins north-west of the objects remain compatible. That is why the measured conditional is broad.

### 6.4 Correlated transport errors (open)

The joint P × C treats the transport errors of the two object sets as independent. The objects are 40–80 km apart,
come from one impact and are observed about 2 days apart, so their errors are probably positively correlated.

Re-scoring the joint with a per-component correlation ρ between the two residuals:
- the flight-conditioned 90 % area grows from 59,316 km² to 75,821 km² at ρ = 0.5 and 82,106 km² at ρ = 0.8;
- the mean moves ≤ 12 km;
- the share outside past searches changes by ≤ 1 point (`audit-correlation.csv`).

ρ = 0 is the reference until ocean transport measures pair correlations from the GDP replay (requested 9 Oct
~22:40 UTC).

### 6.5 Debris drift under H

Inside the 50 % region the model drift to the scene time is 52–114 km (q10–q90; median 63 km). None of the mass
moves less than 30 km. The tracks end a median 31 km from a rating-5 cluster (`audit-drift.csv`). The conditional
therefore does not place origins where the debris would have barely moved.

## 7. Not done, and why

- **The overnight re-run** on the new impacts (`prepare/rerun_next.py`), across every 00:19 option, when end of flight
  writes `next-run/READY`. It replaces every flight-conditioned number in §6.2.
- **Holland H1 / H2** (the two-burst 00:19 options) are not estimable until end of flight settles the hand-off.
- **OSCAR comparison**: fields not yet provisioned by ocean transport. OSCAR is a comparison only.
- **The P-C correlation** (§6.4) awaits ocean transport.
- **The Poisson / scene-footprint term** needs footprints that do not exist. Without it the absolute Bayes factor
  stays uninterpretable, so P(H | D) is never reported.
- **D7, the residual search PDF under H**, beyond the searched-area factor above, needs settling outputs under H.
- **The correlated multi-object likelihood** is not done: the targets enter as a mixture, so at most one object is
  treated as wreckage at a time.

— Pléiades module
