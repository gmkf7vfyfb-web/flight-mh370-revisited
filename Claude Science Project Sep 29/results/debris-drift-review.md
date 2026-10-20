# Debris drift: critical review of the prior work on this case, and the improvements proposed

Ocean Drift Module, review track, night of 8–9 October 2026. Brief deliverable 2
(`threads/master-prompts/ocean-drift.md` §10), written against brief §§1, 2, 4, 5, 8, 9 and 13,
`ISO Sept 28 Status/threads/master-prompts/common.txt`, `ARCHITECTURE.md`,
`results/davey-ch11-alignment.md` and `coordination/OCEAN_DRIFT.md`.

**Status of every number in this note.** Numbers taken from prior runs are quoted as the prior
work reported them, or recomputed from that work's own committed output files. No new transport
was run. Nothing here is evidence about the impact location; it is evidence about the methods. The
prior drift surfaces were all marked `diagnostic_only` by their authors and remain so.

**Bottom line.** The prior debris-drift work is careful about data provenance, field masking and
termination accounting, and several of its measurements are real. Its likelihood, however, is not
a likelihood of the debris observations: it is a product of nine bounded kernel-proximity scores
from one fixed object response per class, with a 1e-9 floor per find, no conditioning
denominator, scored on 77 points along the arc and read back by nearest cell. In the latitude band
where the core posterior has its mass (35.3–38.5°S) the minimum per-find effective sample size is
1.0–8.9 particles, so the old drift answer there is Monte Carlo noise. Of the seven measured
claims in brief §9, two are backed as stated, four are partly backed with material
qualifications, and one (the survivor-bias explanation of the old 34°S peak) is not found in the
archive. The three seed total-variation figures in brief §5 come from the Pléiades imagery work,
not from debris drift. Section 2 lists 16 further errors, the most consequential being a
reference-system mismatch in the flaperon response (E1), the absent conditioning denominator
(E6), and the treatment of recovered cabin panels as low-windage objects (E4).

---

## 1. What the prior work did

### 1.1 Inventory

`git ls-tree -r --name-only HEAD | grep -i drift` on `claude-science-sep29` (head `a90044d` at
the time of reading) returns 956 paths. They are four distinct bodies of work, and only the
first is a debris-drift likelihood.

1. **The v01 ocean-drift spoke and its input preparation (24 Aug – 6 Sep 2026).** Rust crate
   `Archive ISO Pre Sept 28/codebases/v01-share/v01/workspace/crates/ocean-drift/` (`transport.rs`,
   `field.rs`, `observations.rs`, `source_area.rs`, `sampling.rs`, `isotope.rs`), runner glue in
   `crates/runner/src/ocean_drift_{application,commands}.rs`, and the Python preparation tree
   `Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/ocean-drift-input-preparation/`
   (README.md, VALIDATION.md, DEBRIS-EVIDENCE.md, PUBLISHED-COMPARATORS.md, `outputs/`). The same
   DEBRIS-EVIDENCE.md and the evidence CSV are mirrored byte-identically under
   `ISO Sept 28 Status/inputs/recovered-v01/.sources/ocean-drift-input-preparation/`. The thread
   logs are `Archive ISO Pre Sept 28/threads/thr_pexmvwn97e-ocean-drift-new/` (final full-domain
   run), `thr_bsdvixiiae-old-analyze-mh370-object-list-ocean-drift/` (earlier object list and
   Gaussian proxy) and `thr_qpqec5d6kr-ocean-drift-sept-6-sensitivity-atlas/` (a five-density
   atlas whose outputs are not in the repository).
2. **The ISO Sept-28 `core/ocean-transport` branch**, preserved as
   `ISO Sept 28 Status/code/branch-diffs/core__ocean-transport.patch` (3,062 lines, 13 commits on
   28 Sep). A rewrite of transport as `crates/ocean` with a GSHHG land raster, per-class response
   ranges drawn once per object, a GDP replay by drogue state, a 7th-arc source band, and a
   dispersion replay for calibrating diffusivity. It produced no debris likelihood.
3. **The Pléiades transport bundle**
   (`.sources/pleiades-bran2016-forward-inversion/code/transport_core.mjs`), which the brief names
   as a cross-check. It scores satellite-image objects on 23 March 2014, not recovered debris.
4. **The ChatGPT backup `reverse_drift_v1`**
   (`Sept 27 2026 backup PL ChatGPT instance/2026-09-28_codex_drift_and_search_update/`). Despite
   its name, it is a forward-ensemble rerun of the Pléiades/COSMO-SkyMed imagery problem
   (`RESULTS.md` lines 1–7). It contains no recovered-debris likelihood and no reverse-drift
   estimator.

`ISO Sept 28 Status/results/` contains no drift result.

### 1.2 The v01 method as implemented

Read from the code and from the resolved configuration of the final full-domain run
(`outputs/cmems-full-domain-stringent-multi-debris/resolved-run-config.toml`, run seed 3700271,
1,024 particles per cell):

- **Source geometry.** 77 release points on the 7th arc itself (`outputs/source-cells.json`,
  `arc-116` at 10.05°S to `arc-192` at 43.58°S, latitude spacing 0.10–0.62°), each with prior
  weight 1/77. There is no cross-arc extent.
- **Release.** One release at 2014-03-08 00:19 UTC (`release_unix_seconds = 1394237940`).
- **Transport** (`transport.rs` lines 197–330). Midpoint RK2 on WGS-84 with a 6-hour step;
  velocity = GLORYS12 current + `stokes_velocity_scale` × WAVERYS Stokes + windage; an isotropic
  random walk with per-component standard deviation √(2Kdt) and K = 100 m²/s (`transport.rs:292`;
  config lines 43, 83); absorbing land wherever the union GLORYS12/WAVERYS mask has
  `land_fraction ≥ 0.5` (`transport.rs:374`), with no beaching rate and no refloating.
- **Object response, fixed per family.** Flaperon: Stokes ×1.0 plus a constant 0.10 m/s directed
  20° left of downwind (config lines 44–49; `transport.rs:437` divides by wind speed, so the term
  has fixed magnitude). Low-exposure exterior and, separately named, the two recovered cabin
  panels: Stokes ×1.0, zero windage. Unobserved high-windage population: Stokes ×0, 3% of 10 m
  wind. Nothing is sampled per particle; nothing is marginalised.
- **Sampler.** Adaptive SMC per recovery event (selection strength 4, 30-day resampling, starting
  365 days before the find), with exact correction weights; a 20,000-replicate synthetic fixture
  recovers a known 0.5 to within 0.01 (VALIDATION.md, "Adaptive source-area sampling").
- **Recovery score** (`observations.rs` lines 188–310). For each find, each particle scores the
  maximum over its daily output points of a Gaussian proximity kernel (σ = 100 km, unnormalised)
  times a discovery-delay compatibility normalised by its own maximum; the score is averaged over
  particles and floored: `p = 1e-9 + (1 − 1e-9)·mean` (`observations.rs:204`). Delay masses are
  0.85/0.15 over 0–30/30–90 days for the flaperon and 0.50/0.35/0.15 over 0–30/30–180/180–540
  days for the others. The nine logs are summed.
- **Western Australia non-recovery.** `log L = −0.5 × P(landfall in 110–130°E, 10–40°S, or
  unresolved anywhere)` for each of two hypothetical populations (`observations.rs:335–386`;
  config `expected_reportable_items = 0.50`).
- **Isotope screen** for the flaperon only: neutral-or-penalising, capped at ln 2 (marginal) and
  ln 100 (rejection).
- **Composition into the flight posterior**
  (`crates/runner/src/ocean_drift_application.rs`): the source prior is removed, the flight
  particle takes the log-score of the **nearest** arc cell, and particles more than 75 NM from
  any cell are refused.

The reported result (VALIDATION.md lines 33–40, 286–299; README.md line 140) is a prior-removed
surface over the 77 cells peaking at `arc-152` (30.70°S), 90% equal-tail 29.70–35.75°S, marked
`diagnostic_only` because missing/outside support was 1.746% (> 1%), no cell reached
every-find ESS ≥ 200, and the seed/doubled replicas differed by TV 0.394 with peaks at `arc-156`
and `arc-154`.

### 1.3 Audit of the brief's measured claims

| # | Claim as carried in the brief | Where it is in the archive | Verdict |
|---|---|---|---|
| 1 | Stokes ×0.5 / ×1 / ×1.5 moved the mode to 11.9 / 18.0 / 34.9°S | `VALIDATION.md` lines 266–281 ("Surface-response sensitivity"); `README.md` 421–430; `DEMO-RESULTS.md` 172–173 | **Partly backed.** The numbers are exact (`arc-119`, `arc-129`, `arc-161`). But: flaperon only; regional domain ending July 2015; zero windage; one seed at 2,048 per cell; 77 arc points. The 1× mode is not stable under seed: the 1,024-particle reference seed peaks at `arc-146` = 27.62°S, the alternate seed and doubled run at `arc-129` = 18.00°S (VALIDATION.md 250–252). The 18.0°S value is therefore a seed-dependent mode, ~9.6° from its own replicate. |
| 2 | Changing the current product moved it only 1.2° | `README.md` 414–419; `DEMO-RESULTS.md` 195 | **Partly backed.** 13.15°S (native HYCOM) vs 14.37°S (GLORYS12), both currents-only, matched doubled runs. The same passage reports TV **0.3925** between the two profiles — comparable to the 0.471 and 0.494 TV between adjacent Stokes factors. On the peak, response dominates; on the whole profile, the current product is of the same order as a ×0.5 response step. "Object response dominates" is therefore supported for the mode only. |
| 3 | The 1:110m mask omitted Réunion | The 1:110m Natural Earth layer appears only as a plotting basemap (`crates/reporting/assets/ne_110m_land.geojson`; thread `thr_qpqec5d6kr` log lines 51, 65). The transport masks were the model masks. The ISO branch's `crates/ocean/src/land.rs` (patch line 2552) introduces GSHHG explicitly so that "small islands on the drift paths (Réunion, Mauritius, Rodrigues, Nosy Boraha) are land". | **Partly backed.** The principle (coast resolution decides which paths survive) is backed by the ISO branch's motivation and by the 10.3% → 53.2% land-encounter swing with response (VALIDATION.md 278). No archived run used 1:110m as a transport mask, and no file records Réunion being dropped by it. |
| 4 | Multiplying rare arrivals is MC-noise dominated; floors and pseudocounts set the old modes | Floor: config line 55 (`probability_floor = 1e-9`), `observations.rs:204`. Noise: VALIDATION.md 66–70 (GDP "one-cell interval is rare-event collapse"), 78 ("no source mass has ESS at least 200 simultaneously for all nine"). | **Partly backed.** MC domination is backed and quantified below (§2, E8). The floor binds only where a find has ESS 0 — in the final run, `arc-184`…`arc-187` (42.4–42.9°S), log-score −132 to −179. The 30.70°S mode is set by low-ESS estimates (minimum per-find ESS 16.5 at `arc-152`), not by the floor. "Pseudocount" appears only as `alpha_or_pseudocount: 0.0` in an earlier admission rule (thread `thr_bsdvixiiae` log lines 185, 285). Floors setting *the* old mode is not demonstrated for the final run; it is plausible for the 64-particle demo runs (README.md 343: "rare-arrival ESS near one"). |
| 5 | Weight by termination or inherit survivor bias — that produced the old 34°S artefact | `README.md` 198–202, 418–419; `DEMO-RESULTS.md` 195–197; VALIDATION.md 235 | **Not found as stated.** The archive attributes the old ~34°S native-HYCOM peak to a confound — native currents *plus* the coarse 1° ERA5 Stokes field, with 72.63% importance-weighted termination — not to survivor conditioning. The v01 code keeps terminated paths in the denominator (`observations.rs:200–203`; VALIDATION.md 256–258). The lesson "weight by termination" is sound, but the causal attribution to the 34°S peak is not in the record. |
| 6 | Diffusivity never tested: 100 m²/s vs CSIRO 5 NM/day | Config lines 43, 83, 239; CSIRO Part III printed p. 6: random walks "with r.m.s values of 5NM/day", equated to 10 cm/s unresolved velocity | **Backed.** Read as a two-dimensional daily r.m.s., 5 NM/day is K = (5 NM/√2)²/(2 d) = **248 m²/s**; read per component, 496 m²/s. The ISO branch already adopted 248.2 m²/s in its test `random_walk_has_the_declared_daily_rms` (patch lines 2889–2892). 100 m²/s gives 3.2 NM/day two-dimensional r.m.s. No archived run varied K. |
| 7 | Old final answer 29.7–35.8°S, mode 30.7°S, unconverged | VALIDATION.md 33–40, 286–299; thread `thr_pexmvwn97e` final output | **Backed.** 29.70–35.75°S is the 90% equal-tail interval of a profile normalised over 77 arc points under a uniform prior — a display density, not a likelihood. Unconverged by the authors' own criteria. |
| §5 | Seed TV 0.065 (marginalised), 0.23 (best-fitting windage), 0.96–0.98 (four-object joint) | 0.065: `reverse_drift_v1/RESULTS.md` line 79 — the maximum pairwise seed TV for the Pléiades/COSMO-SkyMed `eastern3_21` imagery scenario. 0.23 and 0.96–0.98: not found anywhere in the repository. | **Mis-attributed.** These are imagery numbers (§9 of the brief itself warns that imagery averaging and debris combination are different problems). The debris-drift seed figures actually on record are TV 0.232–0.283 (flaperon-only, 1× Stokes; VALIDATION.md 262) and 0.394 (nine finds, full domain; VALIDATION.md 296). The 0.232 may be the source of "0.23", but it is a nominal-response seed comparison, not a best-fitting-windage one. |
| rule 4 | Enlarging the source domain moved 13% of mixture mass west of the boundary | `reverse_drift_v1/RESULTS.md` lines 5, 57: 0.130 for the Pléiades scenario | **Backed, but for Pléiades.** The lesson transfers; the number is not a debris-drift measurement. |

---

## 2. Errors not yet listed in brief §9

Each item names the file and line, the contract rule it bears on, and its consequence.

**E1. The flaperon's extra leeway was transplanted into a different reference system (rule 10).**
The flaperon family adds full WAVERYS Stokes and then CSIRO's "0.10 m/s in excess of Stokes, 20°
left of the wind" (config lines 44–49; DEBRIS-EVIDENCE.md, "Object-motion and environmental
families"). In CSIRO's own system the "Stokes" against which that excess was measured is not a wave
model: CSIRO Part III (printed p. 6) states that its 1.2%-of-wind items represent objects "subject
to Stokes Drift but not direct wind forcing" — Stokes is implicit in a wind fraction, on BRAN
currents. [Sutherland et al. 2020](https://doi.org/10.1175/JTECH-D-20-0013.1) (arXiv:2005.09527)
show that implicit and explicit leeway coefficients are different quantities, estimated per
modelling system. An excess fitted over "BRAN + 1.2% wind" is not an excess over "GLORYS12 +
WAVERYS". This is a subtler double-count than the one the prior work did catch and fix for the 3%
high-windage control (config lines 65–68). Consequence: the flaperon's total response in the
prior runs has no measured counterpart.

**E2. Response parameters were fixed, never marginalised (rule 9).** Each family has one value of
every response term for every particle (config; `transport.rs` `MotionConfig`). Uncertainty was
explored by separate runs (×0.5, ×1, ×1.5), which were then reported side by side rather than
integrated. This is neither "redrawn per step" nor "persistent per object"; it is a point
estimate. The ISO branch fixed this structurally — "a uniform range drawn once per object"
(patch line 1434) — but a uniform range is itself a prior and needs declaring as one.

**E3. Profiling inside a co-recovery episode (rule 9).** `profile_recovery_episodes`
(`source_area.rs:642–663`) takes the **maximum** log-score across motion families for an episode
whose objects have different laws, described as "least-suppressive … conservative"
(`source_area.rs:524`). Maximising over a nuisance parameter per source cell is selection of the
best-fitting response — the pathology brief §5 attributes the TV 0.23 to. It did not bind in the
stringent nine (every episode there holds one object) but it did in the 20-object, 17-episode
expanded sensitivity.

**E4. Recovered cabin panels were drifted as low-windage objects.** The evidence table classes
Rodrigues and Antsiraka as `high_windage_interior`, but the primary run drifts them in the family
`uncertain-interior-panels-low-exposure-comparator` with Stokes ×1 and zero windage (config
lines 233–250). The 3% alternative was a separate sensitivity file. Consequence: two of the nine
finds were scored under a response that the table itself says is the wrong class.

**E5. "Arrival" is closest daily approach, not beaching (brief §4).** `arrival_weights`
(`observations.rs:250–268`) scores each particle by the maximum over its daily positions of
kernel × delay-compatibility, treating every daily point as a candidate arrival time. A particle
that passes 100 km offshore and continues west scores as an arrival. Arrival and discovery are
nominally separated by the delay bins, but the arrival event itself is never defined.

**E6. The conditioning denominator is absent (brief §4; D5).** The per-find score is a bounded
compatibility in [0, 1], not `q(y_j | x) / Q(x)`. Nothing normalises by the probability that a
source sends identifiable debris anywhere, so a source that sends particles to many coasts is
not penalised for the coasts where nothing was found. The non-recovery term then re-introduces a
Poisson model with a fixed λ = 0.5 for Western Australia only. The two halves are different
observation models, and the λ that D5 shows can be cancelled exactly is instead fixed.

**E7. "Unresolved anywhere" is scored as possible Western Australian landfall.**
`evaluate_non_recovery` (`observations.rs:354–368`) counts a path as penalised if it lands in the
box **or** if it terminates by missing coverage, leaving the domain, or numerical failure
**anywhere**, before the observation end. A field failure off Somalia is penalised as if it were
a West Australian beaching. This is described as conservative (DEBRIS-EVIDENCE.md, "Australian
non-recovery") but it is a source-dependent bias. Bounded here at 1.0 nat in total by λ = 0.5 per
population, so small in this run; it would not be small with a fitted λ.

**E8. The southern tail is unconverged exactly where the core posterior lives (rules 5, 6).**
Recomputed from the run's own `source-area.csv`: the minimum per-find ESS is 8.5 at 35.33°S,
3.5–4.6 at 36.2–37.0°S, and **1.0–3.8 across 37.36–38.46°S**. The core reference posterior's 50%
interval is [−37.85, −37.00]. The old drift likelihood there rests on one to four effective
particles for the hardest find. The display profile put 0.53% of its mass in that band
(provisional, uniform display prior) — a number that should not be read as evidence against
the core, because it is noise.

**E9. Samples were moved onto cell centres (rule 3).** The runner gave each flight particle the
value of the nearest of 77 arc points within 75 NM. With 0.10–0.62° latitude spacing this is
piecewise-constant on the scale of the posterior's own 50% width (0.85°), ignores the cross-arc
coordinate entirely, and refuses rather than computes outside 75 NM.

**E10. The recovery kernel is a fixed 100 km isotropic Gaussian in open distance.** It is not
along-coast, ignores which side of an island a point is on, and is not related to the locality
uncertainty in the evidence table (locality points, not arrival points). Its width is a model
choice with a large effect on rare-arrival counts and was not varied in the final run.

**E11. Discovery-delay distributions were chosen, not modelled (brief §4).** The 0.85/0.15 and
0.50/0.35/0.15 masses have no recorded source. The flaperon's shorter delay is plausible (Réunion
is populated and the item conspicuous), but it is still a choice made per object.

**E12. The isotope term is one-sided.** It can only penalise ("no path receives a positive
boost", VALIDATION.md 324). A likelihood that can lower but never raise relative weight is a
screen, and its effect is biased towards whatever the arrival term already favours. Its measured
effect was tiny (TV 1.39e-7), so this is a design point for A2, not a material error in the
result.

**E13. A single fixed seed per configuration was reported as the result.** Replication was run
(alternate seed, doubled particles) but the headline used the reference seed. Brief §5's rule —
a frozen seed is reproducibility, not convergence — was the authors' own conclusion, but the
surfaces were still plotted and shared.

**E14. Assimilative validation was not held out.** Acknowledged in VALIDATION.md 176–178 and 211–214: GLORYS12
assimilates observations, WAVERYS uses GLORYS12 currents, and GDP replay shares the drifter
network. Drifter replay therefore checks mechanics, not predictive skill on unseen data.

**E15. A fixed-speed leeway term with no wind-speed dependence.** `transport.rs:437` makes the
flaperon's extra term exactly 0.10 m/s whatever the wind (a test pins this:
`fixed_wind_relative_leeway_is_not_rescaled_by_wind_speed`, line 543). Operational leeway models
regress leeway on 10 m wind speed ([Breivik & Allen 2008](https://doi.org/10.1016/j.jmarsys.2007.02.010);
[Breivik et al. 2011](https://doi.org/10.1016/j.apor.2011.01.005)). A pure intercept can be
defensible if that is what CSIRO fitted, but the CSIRO Part II functional form was not
re-read tonight (the ATSB server refused connections), so this is flagged rather than ruled.

**E16. The leeway angle is inconsistent across the prior work.** The run uses 20° left
(config line 49, README.md 346); the archive's own citation ledger reads Part II as "a mean 16°
leftward angle" (README.md 496); the ISO branch's test uses 16° (patch line 2881); Nesterov cites
the DGA tank value of 18° left with a 3.29% total leeway factor
([Nesterov 2018](https://doi.org/10.5194/os-14-387-2018), p. 388 and §2). The angle sets which side
of Madagascar and the Mascarenes particles pass, so this needs one sourced prior, not three
constants.

Two items the task asked to check were **not** found to be errors in the debris-drift archive:
reverse drift was not used as an estimator (the only "reverse drift" directory is the Pléiades
forward rerun), and termination was carried in the denominator rather than survivor-conditioned.

---

## 3. Literature, weighted to ground truth

### 3.1 AF447

AF447 is the calibration case, because the wreck was found in April 2011 and every earlier drift
product can be scored against it. Two findings matter here. First, the 2010 drift committee
reverse-drifted bodies and debris, discarded outlier trajectories, and summarised the remainder as
a weighted-mean bivariate normal with a 95% rectangle; the searches in that rectangle failed
([Stone et al. 2014](https://doi.org/10.1214/13-STS420), §2 of the arXiv reprint). Mercator Océan's account of the same
committee is explicit about why: the wreck lay a few miles north of the last known position,
outside the consensus small zone but "not inconsistent with the ensemble", and had the committee
mapped "the envelope of all probable locations instead of the envelope of mean deterministic
locations" the truth would have been inside it
([Drévillon et al. 2013](https://doi.org/10.1007/s10236-012-0580-2), printed p. 80). The drift
evidence was not wrong; collapsing its ensemble was. Second, in the successful 2011 analysis
Stone et al. used reverse-drifted bodies only as one of three prior components with a subjective
weight of 0.3, did not reverse-drift debris "because we lacked good leeway models for them", and
wrote in retrospect that it "would have been more appropriate to view D3 as a likelihood function
and multiply" (§3 of the arXiv reprint arXiv:1405.4720, whose pagination differs from the
journal's). Drévillon et al. also found the best fits to fishermen's buoys came from trajectories
with no windage effect (printed p. 78), i.e. the response model had to be calibrated per object.

Implications for this module: contract rule 1 (likelihood, not a mixture component), rule 7
(do not collapse an ensemble to its mean or its best member), brief §1 (forward physics, Bayes for
the inverse), and an object-response calibration per class before any find is scored.

### 3.2 MH370 drift studies

The MH370 finds are partial ground truth: there is no wreck, but finds after a prediction test
that prediction. [Trinanes et al. 2016](https://doi.org/10.1080/1755876X.2016.1248149) used
historical drifters and model runs across windage scenarios and reported, in their abstract, that
the later Mozambique, South Africa, Mauritius and Tanzania finds were consistent with their
predicted westward drift and travel times — a forward prediction later borne out, though only in
the coarse sense of coast and season. CSIRO's three reports (Griffin, Oke & Jones 2016, Part I,
CSIRO report EP167888, DOI 10.4225/08/5892224dec08c; Griffin, Oke & Jones 2017, Part II,
EP172633, 13 April 2017; Griffin & Oke 2017, Part III, EP174155, 26 June 2017) are the most
physically grounded: Part II measured the drift of a real 777 flaperon cut down to match the
Réunion item, and Part III (printed p. 6) states the implicit-Stokes convention and the 5 NM/day
random walk used above. Part I's DOI is taken from Part III's reference list (printed p. 25, PDF p. 31) and resolves;
Part I itself was not re-read. Part III was read from the copy in this repository (SHA-256
`66df719b…`, matching the prior ledger). **Part II was not re-read tonight** because the ATSB server refused connections, so its numbers here are as the
prior archive's ledger quotes them.

The peer-reviewed MH370 studies disagree with each other by more than their stated uncertainties,
and the disagreements are traceable to response and independence assumptions.
[Durgadoo et al. 2021](https://doi.org/10.1080/1755876X.2019.1602102) (online 2019, J. Oper.
Oceanogr. 14:1–12) found Stokes drift critical, compared forward and backward tracking, and argued
that at least five items are needed under timing uncertainty (abstract); the prior archive's
ledger records that their method assumes the same drift properties for every item (DEBRIS-EVIDENCE.md,
citing PDF pp. 9 and 12 — not re-read tonight, full text not open-access). [Jansen et al. 2016](https://doi.org/10.5194/nhess-16-1623-2016)
used an implicit leeway that "accounts for both direct and indirect (e.g. Stokes drift)
wind-induced motion" with K_h = 2 m²/s (printed p. 1624), and fitted superensemble weights "to best
represent the discovered debris" before inferring the origin from the same debris (abstract) —
a double use of the observations that contract rule 7 forbids. [Nesterov 2018](https://doi.org/10.5194/os-14-387-2018)
used the DGA tank leeway of 3.29% and 18° left for the flaperon, single-point releases at 40 arc
locations, and the barnacle temperature history, concluding 25.5–30.5°S (abstract).
[Miron et al. 2019](https://doi.org/10.1063/1.5092132) built a Markov chain from undrogued GDP
drifters, treated the finds as "mutually independent observations" (Fig. 3 caption), and reported
a maximum-likelihood box near 31°S with bimodal single-find posteriors. Pattiaratchi & Wijeratne
(2016) is cited by Nesterov as a 25-location screening, but the citation is to an article in *The
Conversation*, not a peer-reviewed paper; it is context only.

Davey et al. themselves re-weighted the Inmarsat posterior with a single flaperon likelihood built
from joined undrogued GDP trajectories reaching Réunion in 508 ± 30 days, with a 1° kernel and
ε = 10⁻⁴, and found the shift "negligible"
([Davey et al. 2016, ch. 11](https://doi.org/10.1007/978-981-10-0379-0_11), printed pp. 102, 106–107,
109). They declined to quantify the absence of other debris because the parameters "cannot be
reliably determined" (p. 103), and marked drifter segments colder than 18 °C because the flaperon
showed accelerated barnacle growth (pp. 104–105, Fig. 11.1).

What the MH370 literature collectively implies: (i) the answer moves with the object-response
assumption more than with anything else, and every study fixed that response rather than
marginalising it; (ii) every multi-object study either assumed independence or tuned weights to
the finds; (iii) the only physical response measurement for a recovered item is CSIRO's flaperon
trial, and it is defined in CSIRO's implicit-Stokes system.

### 3.3 Leeway and Stokes drift

The operational search-and-rescue practice is an ensemble that draws leeway coefficients per
object from empirically derived categories — 63 categories compiled by the US Coast Guard — and
propagates forcing and initial-position uncertainty by Monte Carlo
([Breivik & Allen 2008](https://doi.org/10.1016/j.jmarsys.2007.02.010), abstract; the categories
are Allen & Plourde 1999, *Review of Leeway: Field Experiments and Implementation*, USCG R&D
Center report CG-D-08-99, NTIS ADA366414). Leeway is measured in the field as downwind and
crosswind components regressed on wind speed
([Breivik et al. 2011](https://doi.org/10.1016/j.apor.2011.01.005)). Sutherland et al.'s
comparison of implicit and explicit leeway models across two operational systems is the direct
authority for contract rule 10: both coefficients are estimable, they are not interchangeable, and
the largest variance in fitted leeway sits at the inertial frequency, i.e. in current error
([Sutherland et al. 2020](https://doi.org/10.1175/JTECH-D-20-0013.1); arXiv:2005.09527).
Wave effects on trajectory skill are evaluated observationally by
[Röhrs et al. 2012](https://doi.org/10.1007/s10236-012-0576-y), and satellite-derived versus
modelled current skill by [Dagestad & Röhrs 2019](https://doi.org/10.1016/j.rse.2019.01.001); the
OpenDrift framework ([Dagestad et al. 2018](https://doi.org/10.5194/gmd-11-1405-2018)) is the
reference open implementation of current + Stokes + leeway transport.

### 3.4 Transfer operators

Markov-chain transfer operators built from drifters or model trajectories give smooth,
reusable transition probabilities ([van Sebille et al. 2012](https://doi.org/10.1088/1748-9326/7/4/044040);
[Froyland et al. 2014](https://doi.org/10.1063/1.4892530)); Miron et al. 2019 is the MH370
application. The method is the natural form of A1 (`gdp-empirical`), and it shares Davey's
assumption of time-homogeneity. Undrogued drifters are the analogue for surface objects, but
their slip and dispersion properties are drogue-dependent
([Lumpkin et al. 2017](https://doi.org/10.1146/annurev-marine-010816-060641)). General Lagrangian
practice, including the treatment of unresolved dispersion, is reviewed by
[van Sebille et al. 2018](https://doi.org/10.1016/j.ocemod.2017.11.008).

### 3.5 Japan tsunami debris

The 2011 Japan tsunami debris is the clearest calibration of windage against arrival ground
truth: the source is known, arrivals on North American coasts were logged, and
[Maximenko et al. 2018](https://doi.org/10.1016/j.marpolbul.2018.03.056) ran five ocean models with
15 windage values between 0% and 5% and verified them against observational reports
(Marine Pollution Bulletin 132:5–25). The implication for this module is that windage class is
identifiable from *where and when* objects arrive when the source is known — which is exactly the
synthetic-recovery test of rule 11 run in reverse, and a reason to treat windage per class as a
marginalised parameter rather than a constant.

---

## 4. Improvements

Each item names the contract rule or measured failure it answers and whether it belongs in the
**first pass** (brief §6) or the **refinement**.

1. **Score the shared impact samples by linear interpolation of relative likelihood on a 2-D
   source grid** (rules 1, 3; E9). First pass. No cell-mass or area factor in the sample score;
   areas only for display. Already the brief's method; listed because the prior composition did
   the opposite.
2. **Replace the compatibility score with the D5 conditional likelihood**
   `Π_j q(y_j, t_j | x) / Q(x)^N` with λ cancelled (E6, D5). First pass. `q` is the density of
   *identified arrivals* at locality `y_j` and discovery time `t_j`: an arrival (beaching) event
   from transport, convolved with a modelled discovery delay and a relative identification
   probability `P_I(segment, interval)`. `Q(x)` sums the same over **all** coasts and the whole
   observation window, including Western Australia, Indonesia, Sri Lanka and East Africa.
3. **Define arrival as a beaching event on a GSHHG-resolution coastline**, not closest approach
   (E5; §9 claim 3). First pass. Take the arrival time as the first land contact in the shared
   transport's land raster, with retention as a declared parameter.
4. **Treat unresolved paths as model error inside Q(x), not as landfall anywhere** (E7, rule 4).
   First pass. A path that leaves support contributes to a flagged "not computed" mass that is
   reported, and the support is enlarged if that mass is material where the core posterior has
   weight.
5. **No floor; explicit model error instead** (rule 4; §9 claim 4). First pass. Write
   `q = (1 − ε_m) q_transport + ε_m q_broad`, where `q_broad` is a declared broad arrival model
   (e.g. uniform over the coast segment within ±90 days) and `ε_m` is a declared model-error
   weight with its own sensitivity. This is a regulariser and should be named as one; unlike a
   floor it is source-independent and has a physical reading (probability the transport model is
   wrong for this object).
6. **Marginalise object response per object class, persistent per particle** (rules 9, 10; E1, E2,
   E4, E15, E16). First pass. Response draws once at release and persists (an Ornstein–Uhlenbeck
   evolution of the leeway angle with a timescale of days is a refinement). Classes and priors in
   §4.1.
7. **One response definition per reference system** (rule 10; E1). First pass. For each declared
   `ocean-model` member, the response is either *implicit* (Stokes scale 0, total wind fraction
   α) or *explicit* (Stokes scale s from the wave model, residual windage α_r), never both
   without a refit. The CSIRO flaperon excess is used only in an implicit-Stokes system; in an
   explicit-Stokes system it is replaced by a refit or carried as a labelled sensitivity.
8. **Marginalise the shared environment once, outside the product** (rule 8; D4). First pass:
   `L(x) = Σ_m π_m ∫ p(η|m) Π_j L_j(x|m,η) dη` with `η` = (diffusivity K, a current-error scale,
   and the detection-block levels of item 13). In practice: one forward ensemble collection per
   cell per `m`, with η drawn per **ensemble replicate** (not per particle), so that the product
   over finds is taken inside a replicate and the replicates are averaged afterwards. Per-object
   response `ψ_j` is integrated inside `L_j`.
9. **Diffusivity test** (§9 claim 6). First pass, as the first measurement after the pilot's
   throughput. (a) Undrogued GDP 6-hourly drifters 2014–16 in 10°E–120°E, 5–45°S, split by drogue
   state; release model particles at each drifter's position on a schedule of segment starts,
   advect with the shared ocean's current + Stokes under the low-exposure response, and score the
   observed drifter position at 1, 5, 15 and 30 days with the **logarithmic score** of the model
   ensemble density (Gaussian-kernel KDE of 256 particles per start) and the CRPS of along- and
   cross-track separation. (b) Sweep K ∈ {0, 25, 100, 248, 500} m²/s (248 m²/s is CSIRO's 5 NM/day
   two-dimensional r.m.s.). (c) Report the score-optimal K and the score curvature by horizon; a
   K that keeps rising with horizon is absorbing model current error rather than sub-grid
   turbulence, and that is a finding. (d) Carry K into η as a **declared** distribution:
   log K ~ N(ln K*, 0.5²), truncated to [10, 1000] m²/s, where K* is the 30-day optimum; until
   measured, provisional K* = 248 m²/s. (e) Downstream: report the change in the updated impact
   posterior between K = 100 and K = 248 m²/s on the pilot grid, which is the quantity the
   answer depends on. The ISO branch's `config/drift/gdp-dispersion.toml` and commit `20a9fbd`
   ("diffusivity per class; GDP dispersion replay for calibrating it") are the starting point and
   belong to the shared ocean owner; the drift module consumes K, it does not implement the walk.
10. **Measure Monte Carlo adequacy where the core posterior has mass** (rules 5, 6; E8, E13).
    First pass. Acceptance is seed-to-seed and refinement stability of the *updated impact
    posterior*, plus per-find ESS reported in the core's 50% and 90% bands, not over the drift
    peak. The prior run's 1.0–3.8 per-find ESS at 37.4–38.5°S is the failure to beat.
11. **Discovery delay modelled from search effort, not chosen per object** (E11; brief §4).
    Refinement. A hazard model in which detection rate on a coast segment rises after the
    flaperon publicity of 29 July 2015 and again with organised beach searches; parameters
    shared across finds on the same segment (item 13).
12. **The isotope/temperature channel as a two-sided likelihood** (E12; A2). Refinement. A
    Gaussian or Student-t likelihood of the reconstructed SST series given the simulated path SST,
    with the age-model chronologies marginalised — so it can raise as well as lower relative
    weight. Source the biology for the 18 °C threshold separately from Davey; [Al-Qattan et al.
    2023](https://doi.org/10.1029/2023AV000915) supplies the calibrated δ¹⁸O–temperature relation
    and a 50,000-path matching method, and reports a drift path "far south of a previous
    isotope-based reconstruction".
13. **Find episodes enter as detection blocks, not as collapsed observations** (rules 2, 8). First
    pass for the structure, refinement for the levels. See the companion draft
    `results/debris-drift-find-episodes.md`.
14. **Reproduce Davey first (A1), then carry `gdp-empirical` as a declared `ocean-model` member.**
    First pass. The review supports A1, with one addition: Davey's arm is an *implicit-response*
    system (undrogued drifter leeway), so the flaperon's response in that arm is the drifter's,
    not the flaperon's. That is part of why the shift is small, alongside D3.
15. **The Western Australia term enters only through Q(x)** (brief §13; D5). First pass for the
    structure; the relative identification probability for Australian coasts is the deferred
    modelling task, and the reminder to Pete stands.
16. **Response-sensitivity results are reported as a sensitivity mixture over declared priors,
    never as three modes** (rule 7; §9 claim 1). First pass.
17. **Prior work on the flaperon response is checked for circularity before use.** First pass,
    blocking for the flaperon class. A secondary source (an mh370search.com comment, January
    2021, not used as evidence) states that CSIRO Part II's flaperon parameters were assessed
    under the assumption that the source lay at 30.5–40°S on the 7th arc. If Part II's primary
    text confirms that the response was tuned to make a 7th-arc source reach Réunion on time, the
    flaperon's leeway is partly constituted by the answer, exactly as the expanded identity set
    is, and must enter as a labelled sensitivity rather than a measurement.

### 4.1 Object response by motion class

All terms drawn **once per particle at release** and held for the trajectory. "Implicit" means
Stokes scale 0 and leeway as a fraction of 10 m wind; "explicit" means wave-model Stokes plus a
residual. Each class carries both forms as a declared alternative named `object-response`, with
equal prior weight until the drifter-replay scores (item 9) support a different split. All values
provisional until the sources marked † are re-read in primary form.

| motion_class (stringent nine) | Form | Parameter | Sampling distribution | Source |
|---|---|---|---|---|
| `flaperon` (Réunion) | implicit, CSIRO system | total wind fraction α | α = 1.2% fixed (CSIRO's Stokes proxy) | CSIRO Part III p. 6 |
| | | extra leeway speed c₀ | N(0.10, 0.03²) m/s, truncated at 0 | CSIRO Part II† via archive ledger |
| | | angle θ, left of downwind | N(18°, 4²) | Part II† (16°/20° in the archive), DGA 18° via Nesterov 2018 |
| | implicit, DGA system | total leeway factor α | N(3.29%, 0.5%²), truncated [1.5%, 5%] | Nesterov 2018 (DGA tank, Daniel 2016) |
| | | angle θ | N(18°, 4²) | Nesterov 2018 |
| | explicit | Stokes scale s; residual α_r | s ~ N(1.0, 0.25²) truncated [0.4, 1.6]; α_r ~ U(0, 1%) | Durgadoo et al. 2021 (100% central, 50–150% range); residual unmeasured |
| `low_exposure_exterior` (Paindane, Vilanculos, Mossel Bay, Mauritius, Chidenguele, Pemba) | implicit | α | N(1.2%, 0.3%²), truncated [0.5%, 2%] | CSIRO Part III p. 6 |
| | | θ | N(0°, 10²) | no measurement; symmetric |
| | explicit | s; α_r | s ~ N(1.0, 0.25²) truncated [0.4, 1.6]; α_r ~ U(0, 0.5%) | Durgadoo et al. 2021 |
| `high_windage_interior` (Rodrigues, Antsiraka) | implicit | α | log α ~ N(ln 2.5%, 0.35²), truncated [1%, 5%] | CSIRO Part III p. 6 (3% for items "floating higher"); Maximenko et al. 2018 (0–5% range) |
| | | θ | N(0°, 15²) | no measurement |
| | explicit | s; α_r | s ~ N(1.0, 0.25²); α_r ~ log-N(ln 1.5%, 0.4²) truncated [0.3%, 4%] | as above; residual unmeasured |

The prior work's DEBRIS-EVIDENCE.md notes, correctly, that CSIRO never measured a 3% law for the
recovered cabin panels; the high-windage prior above is wide on purpose, and a low-exposure
response is retained as one end of it rather than as the class default.

---

## 5. Against the Davey alignment note

- **D1 (2014–16 forward transport)** — supported, with a condition: the response must be refitted
  per reference system (E1, item 7), or D1 imports a response defined in a different system.
  AF447 is the precedent for refined, observation-fitted currents mattering
  ([Drévillon et al. 2013](https://doi.org/10.1007/s10236-012-0580-2)).
- **D2 (no density denominator, no ε)** — supported for the release density; questioned in
  wording. Controlled releases remove the drifter-sampling denominator, but rare-arrival zeros
  remain and must be handled by the model-error term of item 5. That term is a regulariser, and
  the paper should say so rather than claim none is needed.
- **D3 (resolution)** — supported, with the qualification that the prior run's resolving power in
  the core band was set by per-find ESS of 1–9, not by kernel width. Resolution is limited by the
  ensemble before it is limited by the grid.
- **D4 (many objects, shared ocean)** — supported. Miron et al. 2019 and the prior archive both
  assumed independence across finds; Jansen et al. 2016 tuned weights to the finds.
- **D5 (λ cancelled, Q(x) explicit)** — strongly supported; it repairs E6 and E7. Two additions:
  (a) unresolved paths must enter Q(x) as flagged model error, not be dropped (otherwise Q is
  survivor-conditioned); (b) `P_I(segment, interval)` with **unknown** block levels does not
  cancel — only a global constant does — so the block levels are latent and are marginalised as
  part of η (item 13).
- **A1 (`gdp-empirical`)** — supported; note it is an implicit-response arm (item 14).
- **A2 (biofouling temperature)** — supported; make it two-sided (item 12).

---

## 6. Open questions for the architect

1. Rule on the flaperon response's provenance (item 17) once Part II is re-read; until then, the
   flaperon class carries the three alternatives of §4.1 as a labelled sensitivity.
2. Confirm that the `object-response` alternative is module-local (it is not shared with Pléiades,
   whose objects are unidentified) or whether Pléiades should declare the same name.
3. Confirm that diffusivity K is an η component owned by the shared ocean (drawn per ensemble
   replicate) and not a per-module choice.
4. The brief's §5 seed-TV figures should be corrected in the brief to the debris-drift values
   (0.232–0.283 and 0.394), with the imagery figures attributed to Pléiades.

## References

Allen, A. A. & Plourde, J. V. (1999). *Review of Leeway: Field Experiments and Implementation*.
USCG R&D Center report CG-D-08-99, NTIS ADA366414. (No DOI.)

[Al-Qattan et al. 2023](https://doi.org/10.1029/2023AV000915) · [Breivik & Allen 2008](https://doi.org/10.1016/j.jmarsys.2007.02.010) ·
[Breivik et al. 2011](https://doi.org/10.1016/j.apor.2011.01.005) · [Dagestad et al. 2018](https://doi.org/10.5194/gmd-11-1405-2018) ·
[Dagestad & Röhrs 2019](https://doi.org/10.1016/j.rse.2019.01.001) · [Davey et al. 2016, ch. 11](https://doi.org/10.1007/978-981-10-0379-0_11) ·
[Drévillon et al. 2013](https://doi.org/10.1007/s10236-012-0580-2) · [Durgadoo et al. 2021](https://doi.org/10.1080/1755876X.2019.1602102) ·
[Froyland et al. 2014](https://doi.org/10.1063/1.4892530) · [Jansen et al. 2016](https://doi.org/10.5194/nhess-16-1623-2016) ·
[Lumpkin et al. 2017](https://doi.org/10.1146/annurev-marine-010816-060641) · [Maximenko et al. 2018](https://doi.org/10.1016/j.marpolbul.2018.03.056) ·
[Miron et al. 2019](https://doi.org/10.1063/1.5092132) · [Nesterov 2018](https://doi.org/10.5194/os-14-387-2018) ·
[Röhrs et al. 2012](https://doi.org/10.1007/s10236-012-0576-y) · [Stone et al. 2014](https://doi.org/10.1214/13-STS420) ·
[Sutherland et al. 2020](https://doi.org/10.1175/JTECH-D-20-0013.1) · [Trinanes et al. 2016](https://doi.org/10.1080/1755876X.2016.1248149) ·
[van Sebille et al. 2012](https://doi.org/10.1088/1748-9326/7/4/044040) · [van Sebille et al. 2018](https://doi.org/10.1016/j.ocemod.2017.11.008)

Griffin, D. A., Oke, P. R. & Jones, E. M. (2016). *The search for MH370 and ocean surface drift.*
CSIRO report EP167888. DOI 10.4225/08/5892224dec08c.
Griffin, D. A., Oke, P. R. & Jones, E. M. (2017). *The search for MH370 and ocean surface drift —
Part II.* CSIRO report EP172633, 13 April 2017. (Not re-read in primary form for this note.)
Griffin, D. A. & Oke, P. R. (2017). *The search for MH370 and ocean surface drift — Part III.*
CSIRO report EP174155, 26 June 2017.
