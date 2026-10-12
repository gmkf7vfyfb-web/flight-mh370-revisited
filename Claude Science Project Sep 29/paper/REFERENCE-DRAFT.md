# Reference draft — MH370 Bayesian reconstruction

**Internal reference document. Not the paper. Not for circulation outside the project.**

Owner: paper drafting and citations module. Generated 12 October 2026 by `build_reference_draft.py`. Target journal: *The Journal of Navigation*; its verified rules are in `paper/JON-RULES.md`.

## 0. How to read this document

**This document is not the paper.** It is the internal reference from which the paper is
written. It may carry fuller mathematics than the paper will, and anything in it that is
not intended for the paper is marked **not for the paper**.

**What the labels mean.** Every element is classified on two axes, following the agreed
taxonomy:

- against the published work — **REPRODUCTION** (Davey et al. as published), **UPDATE**
  (same element, better data or product), **MODIFICATION** (same element, changed
  assumption or method), **EXTENSION** (an element the published work does not have);
- against reality — **BUILT** (in code and run), **SPECIFIED** (designed, not run),
  **INTENDED** (discussed only).

**Where the content comes from.** The classification, the equations, the result claims and
the caveat labels in sections 2 and 3 are extracted from the project notes under
`results/` and are reproduced as those notes state them. Caveat labels are **verbatim**.
The coverage register in section 4 and the open items in section 5 are copied from
`ARCHITECTURE.md`. The build status in section 2.1 is measured from the code in this
checkout. No equation appears unless a note gives it; no number is retyped from memory.

**Reading the result claims.** A claim carries its own labels and its source artifact. A
claim with a label such as "not converged" or "PROVISIONAL" is reported here as a finding
at that strength and not at any greater strength. Negative results are kept.

## 1. Literature summary

Every source named here is in `paper/CITATIONS-LEDGER.md` with its grade and its
verification status. Nothing is cited here that is not in that ledger.

### 1.1 The work this paper reproduces and extends

The direct antecedent is Davey, Gordon, Holland, Rutten and Williams (2016), the Defence
Science and Technology Group's Bayesian reconstruction of the flight, published open
access by Springer under CC BY-NC 4.0. It is a particle filter over aircraft state driven
by the Inmarsat burst timing and frequency offsets, with a prior formed from primary radar
and a manoeuvre model of random turns and speed changes. Its chapters carry separate
digital object identifiers and printed page ranges, so the paper can cite a specific
element precisely: the satellite communications measurement model is chapter 5, printed
pages 23 to 34; cruise dynamics chapter 6, 35 to 46; manoeuvre dynamics chapter 7, 47 to
54; the particle filter implementation chapter 8, 55 to 61; the validation experiments
chapter 9, 63 to 86; the application to the accident chapter 10, 87 to 100; and the
ongoing refinement chapter 11, 101 to 109.

Two features of that work set the agenda for this one. It assumes infinite fuel inside the
filter and applies fuel as an after-the-fact censor on trajectories. And it treats the two
transmissions at 00:19 unevenly: both burst timing offsets are used, neither burst
frequency offset is, and the anomalous second timing offset is used only after a log-on
correction.

The measurement models themselves come from Ashton, Shuster Bruce, Colledge and Dickinson
(2015) in this journal, which is the published account of the Inmarsat analysis and the
source of the satellite ephemeris and the offset definitions the filter uses.

The treatment of the final two transmissions rests on Holland (2018). That paper
establishes, from satellite data unit bench tests and four previous log-ons of the same
airframe, that this unit's frequency offset is initially too high at log-on and then
decays to a steady value over a few minutes; and it bounds the steady-state equivalent
offsets at 00:19 and the descent rates they imply. Its bench-test evidence is an
unpublished internal study of the flight path reconstruction group, inspectable only
through Holland's summary of it — a limitation this paper states rather than conceals.

### 1.2 Bayesian search and the comparable case

The methodological precedent for turning a posterior into a search plan is Stone, Keller,
Kratzke and Strumpfer (2014) on Air France 447, which is the standard reference for
combining dissimilar evidence — flight dynamics, acoustic beacons, drift of recovered
bodies and debris, and unsuccessful search coverage — into one probability map, and for
the proposition that the failure of a search is itself evidence. The treatment of searched
areas here follows that logic.

Model comparison follows Kass and Raftery (1995) for the interpretation of Bayes factors,
and the convergence and effective-sample-size diagnostics are reported against a
replicate-count-dependent split-half floor established within the project, because the
published work states no quantitative convergence criterion at all.

### 1.3 Drift of the recovered debris

The authoritative drift work for this accident is Griffin, Oke and Jones (2016, 2017), the
CSIRO reports that modelled the drift of recovered items with an ocean reanalysis and
measured the leeway of a genuine flaperon section. The treatment here is an update rather
than a new method: more recovered items, several ocean products rather than one, and
explicit marginalisation over windage and Stokes drift. The supporting literature is the
leeway and windage line — Breivik and colleagues, Sutherland and colleagues (2020) on
evaluating leeway coefficients against operational prediction systems, and Durgadoo and
colleagues (2021) on strategies for simulating marine debris drift. Ocean products used
are documented in the project's data manifest and cited as datasets.

### 1.4 Hydroacoustics

The possibility that the impact was recorded by the hydroacoustic stations of the
International Monitoring System has been examined by Duncan, Gavrilov and McCauley (2014)
for this accident, and the physics of impact-generated acoustic and acoustic-gravity waves
by Kadri (2019, 2024). Metz, Obana and Fukao (2023) is the clearest demonstration that a
remote hydroacoustic detection of an aircraft crash is achievable in principle, and Duncan
and Dall'Osto (2023) treat the dependence of long-range detection on propagation
conditions and impact parameters. Propagation modelling follows the standard references —
Jensen, Kuperman, Porter and Schmidt (2011) for computational ocean acoustics, Collins
(1993) for the split-step Pad\'e parabolic equation, Porter (1992) for normal modes, and
Francois and Garrison (1982) for absorption. Calibration sources are the explosive
source-level work of Gaspin and Shuler (1971) and the Indian Ocean calibration experiments
of Blackman and colleagues (2004).

This paper's hydroacoustic contribution is predictive, not evidential, and the Discussion
states the calibration gaps that make it so.

### 1.5 Remote sensing of debris

The official record of the satellite imagery analysis is Minchin, Mueller, Lewis, Byrne
and Tran (2017), Geoscience Australia Record 2017/013, which reports the analysis of the
Pl\'eiades 1A imagery. The conditional hypothesis in this paper is built on that record.

### 1.6 The official record

The Australian Transport Safety Bureau's series under investigation AE-2014-054 defines
the underwater search areas and reports the operational search, and the Malaysian safety
investigation report of 2018 is the factual record of the flight and of the recovered
debris. These are cited as the official sources for the data the estimator consumes and
for the searched areas it conditions on.

### 1.7 What the literature does not settle

Three things this paper must therefore argue rather than cite. First, whether the
reconstruction is sensitive to the fuel model, which the published filter did not carry
inside the likelihood. Second, whether the final two transmissions should be scored at
all, and under which cause, where the literature offers named hypotheses but no
resolution. Third, whether a hydroacoustic non-detection carries information, which
depends on a transmission-loss calibration that does not yet exist.

## 2. Methodology, end to end

The chain runs from the 18:01:49 radar prior, through the core particle filter on the Inmarsat handshakes, to the end-of-flight stage and impact, then to the impact-level modules and the composer. The order below follows that chain. The classification of each element against the published work is given first, because it determines how much the paper must say: a reproduction is cited, an extension is derived.

### 2.1 Build status, measured from the code in this checkout

| Element | Where | Lines of code | Files |
|---|---|---|---|
| Core filter | `engine/crates/geo/src` | 11,606 | 16 |
| End of flight | `engine/hypotheses/end-of-flight/**` | 7,297 | 8 |
| Pléiades | `engine/hypotheses/pleiades/**` | 1,099 | 3 |
| Searched areas | `engine/hypotheses/seabed-search/**` | 994 | 1 |
| Composer | `engine/crates/compose/src` | 2,745 | 4 |
| Shared ocean transport | `engine/crates/ocean/src` | 3,318 | 13 |
| Hydroacoustics | `results/hydroacoustics-audit/scripts` | 1,030 | 11 |
| Antenna gain (parked) | `engine/hypotheses/antenna-gain/**` | 610 | 1 |
| Arc kernel (placeholder) | `engine/hypotheses/arc-kernel/**` | 156 | 1 |

Hypothesis directories carrying a `hypothesis.toml`: `_template`, `altitude-prior`, `antenna-gain`, `arc-kernel`, `end-of-flight`, `initial-mach`, `pleiades`, `radar-fix`, `seabed-search`.

**No engine hypothesis module exists for `debris-drift`, `settling`, `hydroacoustics`.** Their methods are written up as drafts under `results/` and their analysis runs as Python under `results/`, so they are SPECIFIED as engine modules while being partly BUILT as analysis. The paper must not describe them as integrated modules.

**A discrepancy that must be resolved before any status claim is published.** `ARCHITECTURE.md` carries a table headed "Build status, honestly" which states:

| stage | interface | model |
|---|---|---|
| 1 core filter | **built**, 53 tests pass | **built and validated** against Fig. 10.3 |
| 2 end of flight | **built** — `Terminal` trait (`families`, `latent_columns`, `takeover_time`, `descend`), `handoff.npy`, `terminal.rs`, `impacts.rs` | **placeholder only** — `hypotheses/arc-kernel` is plumbing, not a model; it returns NaN impact energies |
| 3 impact modules | **built** — `ImpactView`, `impact_log_likelihood`, `predict`, `mh370 evaluate` | **none** |
| 4 composer | **not built** — `main.rs:71` rejects a `[[compose]]` section | **specified**, in `ISO Sept 28 Status/threads/master-prompts/core-stages.txt` §D6; needs no prompt of its own |

That table is **materially out of date** for stages 2 to 4, and the paper would be wrong to quote it. Measured against the code today: the end-of-flight module is 7,297 lines, not a placeholder; two impact-level modules exist as hypothesis crates (Pléiades and searched areas); and the composer exists as `engine/crates/compose` with worked `pass0` and `pass1` examples and two composed result notes under `results/`. The table's specific evidence remains true — `crates/mh370/src/main.rs` still rejects a `[[compose]]` section — but that is a statement about the runner's configuration path, not about whether a composer exists. Both facts need stating together: **the composer is built as a separate crate and has been run; it is not wired into the main runner's `[[compose]]` configuration.**

### 2.2 Reproduction (4 elements)

Davey et al. as published. **The paper gives a short summary and chapter citations here, not a re-derivation.** The fuller mathematics below is *not for the paper*.

#### Accident-flight initial prior (position, heading, Mach)

*Source note:* `results/davey-2016-reference.md` — Reproduction audit of the published model  
*Status:* **BUILT** — implemented in Parameters::default() and config/davey2016.toml  
*Classification:* REPRODUCTION -- engine values match Davey's Chapter 4 accident-flight prior exactly

*Relation to the published work:* p. 21: prior defined at 18:01 at the penultimate radar point from the Kalman filter output; "The position standard deviations were set to 0.5 nm and the direction standard deviation to 1°." p. 35: "An initial Mach number was selected from a uniform prior between 0.73 and 0.84; this was chosen on the basis of expert advice to ensure that the required flight endurance is achievable."

Sources the note cites: Davey et al. 2016 (pp. 21, 35; cf. Table 8.2 p. 59, and p. 64).

#### OU stationary initial deviations (Mach, angle, wind)

*Source note:* `results/davey-2016-reference.md` — Reproduction audit of the published model  
*Status:* **BUILT** — asserted by a test in crates/flight/src/lib.rs  
*Classification:* REPRODUCTION -- derived values reproduce Davey's tabulated figures to three significant figures

*Relation to the published work:* Table 8.2 (p. 59) tabulates Initial Mach deviation s.d. 0.00311, Initial angle deviation s.d. 0.0826°, Initial wind deviation s.d. 5.68 kn.

Governing equations, as the note gives them:

- derive the initial Mach/angle/wind deviation standard deviations from the OU constants and check them against Davey's Table 8.2 figures

  ```latex
  \sigma = \sqrt{q / 2\beta}
  ```
  Symbols: \sigma = stationary standard deviation of the OU process [Mach, degrees, or knots depending on state]; q = OU process noise intensity [state-dependent units]; \beta = OU reversion rate [s^{-1}]
  Implemented in: `crates/flight/src/lib.rs`


Sources the note cites: Davey et al. 2016 (Table 8.2, p. 59).

#### Mach acceleration rate

*Source note:* `results/davey-2016-reference.md` — Reproduction audit of the published model  
*Status:* **BUILT** — parameter already implemented and now correctly cited  
*Classification:* REPRODUCTION -- engine's mach_rate_per_s matches the rate Davey states

*Relation to the published work:* p. 49: "The assumed rate corresponds to a change of Mach of 0.1 in one minute."

Governing equations, as the note gives them:

- corroborate the engine's assumed Mach acceleration rate against Davey's stated rate of 0.1 Mach per minute

  ```latex
  mach\_rate\_per\_s = 0.1/60
  ```
  Symbols: mach\_rate\_per\_s = assumed maximum rate of Mach number change [Mach/s]


Sources the note cites: Davey et al. 2016 (p. 49).

#### Davey ch.11 §11.2 single-flaperon drift likelihood update (GDP drifter reproduction)

*Source note:* `results/davey-ch11-reproduction.md` — Reproduction of the published refinement chapter  
*Status:* **MIXED** — code, figures and numbers are built and run, but the whole result is marked PROVISIONAL pending the prior's convergence failure, the map-vs-impact-distribution gap, and two unprinted method steps  
*Classification:* REPRODUCTION -- the note is explicitly framed as a reproduction of Davey et al. (2016) ch.11 §11.2

*Relation to the published work:* Represented the final-position posterior as weighted particles and re-weighted them by a new observation's likelihood (Eq.11.3-11.4, p.103); described a Poisson debris field (Eqs.11.5-11.6) but left it qualitative because λ and P_I "cannot be adequately specified" (p.103-104); used undrogued GDP drifters passing through three boxed regions in Feb-Apr, with sub-18°C segments marked (Fig.11.1, p.104-105); joined pairs of trajectories that passed close together, with no printed distance or time criterion, to synthesize 4-segment paths where "each previous trajectory creates around 30 new trajectories" (p.106); formed the drifter start/end sample Eq.11.7 (x on 8 March 2014, y on 29 July 2015, 508 days) (p.106); defined the arrival likelihood as an integral over a region R "a small region ... surrounding Reunion Island" of unprinted size, Eq.11.8 (p.106); estimated it by a ratio-of-kernel-density estimator, Eq.11.9, with ε=10⁻⁴ and a fixed 1° isotropic kernel evaluated via a KDE toolbox (p.106-107); found the arrival-density variation "almost completely explained by" the starting distribution and the updated distribution "shifted very slightly to the North, but the effect is negligible" (p.108-109)

Governing equations, as the note gives them:

- particle-form representation of the final-position distribution (Eq.11.3)

  ```latex
  p(x_{final} \mid Z_K) \approx \sum_p w_p \delta(x_{final} - x_p)
  ```
  Symbols: x_{final} = final (impact) position; Z_K = observation set up to time K; w_p = weight of particle p; x_p = position of particle p; \delta = Dirac delta

- re-weight each particle by the new observation's likelihood (Eq.11.4)

  ```latex
  p(x_{final} \mid Z_K, y) \propto p(y \mid x_{final}) p(x_{final} \mid Z_K) \approx \sum_p w_p p(y \mid x_p) \delta(x_{final} - x_p)
  ```
  Symbols: y = new observation; p(y \mid x_{final}) = likelihood of y given the final position; w_p = particle weight; x_p = particle p position
  Implemented in: `engine/hypotheses/debris-drift/prepare/gdp/davey_ch11.py`

- empirical joint sample form of drifter start/end locations (Eq.11.7)

  ```latex
  p_{drifter}(x, y) \approx \frac{1}{P} \sum_p \delta(x - x_p) \delta(y - y_p)
  ```
  Symbols: x = drifter location on 8 March 2014; y = drifter location on 29 July 2015 (508 days later); P = number of drifter trajectories; x_p, y_p = p-th trajectory's start/end positions
  Implemented in: `engine/hypotheses/debris-drift/prepare/gdp/davey_ch11.py`

- define the likelihood of a final position as the probability of arriving in region R (Eq.11.8)

  ```latex
  l(x_{final}) = \int_R p(y \mid x_{final})\, dy
  ```
  Symbols: R = small region surrounding Reunion Island, size not printed; x_{final} = final position; y = arrival location
  Implemented in: `engine/hypotheses/debris-drift/prepare/gdp/davey_ch11.py`

- ratio-of-kernel-density estimator giving the relative likelihood surface (Eq.11.9)

  ```latex
  l(x) \approx \frac{\frac{1}{P}\sum_p K(x - x_p) + \epsilon}{\frac{1}{\tilde P}\sum_p K(x - \tilde x_p) + \epsilon}
  ```
  Symbols: K = fixed kernel, 1 degree standard deviation in latitude and longitude; \epsilon = floor constant, 10^{-4} as printed; x_p = trajectories passing through R in the right time window, joined ones included; \tilde x_p = overall set of drifter locations, February-April; P, \tilde P = respective sample counts
  Implemented in: `engine/hypotheses/debris-drift/prepare/gdp/davey_ch11.py`

- Kish effective sample fraction of the reweighting, used to summarize how much the update reshapes the posterior

  ```latex
  \text{ESS fraction} = \frac{(\sum w l)^2}{(\sum w \cdot \sum w l^2)}
  ```
  Symbols: w = particle weight; l = relative likelihood at that particle

- convert gridded density to a per-cell particle weight at 0.25 degree resolution, per the task's ruling

  ```latex
  w = \text{density} \times 0.0625
  ```
  Symbols: w = particle weight; density = per-deg^2 density at the cell centre; 0.0625 = area in deg^2 of a 0.25 degree cell
  Implemented in: `summary.rs::map_cell`

- mean relative likelihood by latitude band, used to characterize the gradient of the likelihood surface

  ```latex
  l / E_{prior}[l]
  ```
  Symbols: l = relative likelihood; E_{prior}[l] = expectation of l under the prior


Sources the note cites: Davey et al. 2016.

### 2.3 Update (2 elements)

The same model element with newer or better data or products. The paper describes what changed about the data, and cites the published method.

#### Expected manoeuvre count before 19:41 (look-ahead diagnosis)

*Source note:* `results/davey-2016-reference.md` — Reproduction audit of the published model  
*Status:* **BUILT** — the corrected computation (7.6 expected manoeuvres, 83% probability of at least one) is documented  
*Classification:* UPDATE -- corrects the project's own earlier figure, computed with the wrong tau range, not a Davey figure

*Relation to the published work:* p. 55: "A problem with sampling from the dynamics is that this can be a very diffuse distribution. In the MH370 case, the model allows for turns and speed and altitude changes, and potentially several of each can be sampled between measurements. The proportion of particles that sample a trajectory close to the measurements will be small and a very large number of samples will be required to capture the high probability regions."

Sources the note cites: Davey et al. 2016 (p. 55).

#### Composer pass 1 (run C) — Bayesian evidence/position composition pipeline

*Source note:* `results/composer-pass1-run-c.md` — Composer: first composed pass  
*Status:* **MIXED** — pipeline is BUILT and executed end-to-end (9/9 unit tests pass, 504 products written, checks reproduce EoF/searches/settling exactly) but every composed number is explicitly labelled UNCONVERGED, provisional, or not estimable  
*Classification:* UPDATE -- reruns the unchanged composer (`crates/compose` at 960b3147) on new run C inputs under a changed constraint (`+unpowered` vs pass 0's `+alive`) and an extended product set (ρ sensitivity, COSMO, 212 m/s filter, seabed resample)

Governing equations, as the note gives them:

- test whether drift and hydro evidence favour or conflict with the Pléiades hypothesis area (A_scene cancels in the ratio)

  ```latex
  \ln R = \ln E[L_P \mid \text{flight} + \text{EoF} + \text{drift} + \text{hydro}] - \ln E[L_P \mid \text{flight} + \text{EoF}]
  ```
  Symbols: R = evidence ratio of H (Pléiades-conditioned) against G [dimensionless]; L_P = per-row Pléiades likelihood [dimensionless]; E[\cdot] = expectation over composed impact rows [dimensionless]

- confirm that the 'after searches' row weights are exactly G (or H) multiplied row-wise by the search non-detection likelihood

  ```latex
  Ga = G \times L_{search}
  ```
  Symbols: Ga = product G after applying searched-area non-detection; G = composed flight+EoF+drift+hydro product; L_{search} = per-row point-target non-detection likelihood [dimensionless]

- define the per-row weight product handed to ocean settling for the aimed seabed resample (G12 fix)

  ```latex
  w = W_Q(\text{stratum}) \times w_{pooled}
  ```
  Symbols: w = composed per-row weight written to the exchange [dimensionless]; W_Q(\text{stratum}) = stratum mixture weight [dimensionless]; w_{pooled} = pooled within-stratum weight across the 8 replicate seeds [dimensionless]
  Implemented in: `mh370-exchange/composer/next-run-c/row-weights/<option>-<product>/`

- check that the ρ-surface construction is consistent with the constant it was built to omit

  ```latex
  H_{r0} - H_{c} = 2\ln A_{scene}
  ```
  Symbols: H_{r0} = evidence of product H with COSMO at correlated-error ρ=0; H_{c} = evidence of product H plus COSMO; A_{scene} = scene-area normalisation constant omitted by the ρ surfaces [dimensionless]


Open coverage gaps named by the note:

- G13 -- no structural limit / transonic drag; contact speeds > 212 m/s remain outside the feasible set, affecting every product (A1 above all); OPEN, 212 m/s version shown everywhere as a stop-gap
- rapid descents > 6,500 ft/min and unloading not reachable, affecting A1/A2 near the arc and Holland-type readings; OPEN (EoF plan item 4)
- B only reachable from the 00:11 hand-off, affecting B's share and position; OPEN (core run D)
- G10 -- drift support gap (13-28% of weight not computed, carried at the mean), moving G/H areas by up to ×3 (Gx/Hx); OPEN (drift run A extension is the fix)
- R600 BTO + Raw BFO under G/H is below the ESS floor and not estimable; NEW, OPEN, aimed proposal needed
- A1 under G after searches (R600 BTO Only) has only 320 rows in descent-climb; NEW, OPEN, family shares still estimable
- core routes stratum has only 14 of 48 routes distinct, affecting the routes stratum weight and its large ln R (+0.74); NEW (core's finding), OPEN
- G7 -- Holland H1/H2 not composed (1-7 effective impacts per seed); OPEN, reported as not estimable, not dropped
- G-H1 -- hydro coupling has no angle, speed or breakup dependence; OPEN; G and H also shown without hydro
- seabed PDF missing for R600 BTO + Raw BFO and the 212 m/s versions (budget: disk 23-27 GB free); OPEN (this pass)
- G12 -- seabed PDF from composed row weights; CLOSED for G, Ga, H and Ha of both options via settling's aimed resample

### 2.4 Modification (1 element)

A published element whose assumptions or method changed. The paper states the assumption that changed, why, and what it costs.

#### Resampling (branching scheme)

*Source note:* `results/davey-2016-reference.md` — Reproduction audit of the published model  
*Status:* **MIXED** — the engine's own resampling is built, but Davey's branching scheme is only specified (constants known), not yet implemented  
*Classification:* MODIFICATION -- engine's systematic resampling of a fixed population departs from Davey's adaptive branching resampler

*Relation to the published work:* "the filter used in this book is a form of SIR particle filter" (p. 16); Sect. 8 describes branching over independently propagated trajectories: a particle with weight w >= eta is duplicated into n-bar branches each carrying weight w/n-bar, while a particle below threshold survives with probability w at weight 1 or is pruned; "thus resampling can also be implemented through a randomised branching procedure, recursively adapting the number of particles" (p. 56); chosen because it "is not necessarily computationally efficient, but in this particular application it was more important to broadly explore the enormous state space." Table 8.2 gives branching rate n-bar 3-10 and likelihood threshold eta at e^-25 or e^-30.

Governing equations, as the note gives them:

- redistribute weight across branches when a particle with weight w >= eta is duplicated under Davey's branching resampler

  ```latex
  w' = w / \bar{n}
  ```
  Symbols: w' = weight of each branch after duplication [dimensionless]; w = weight of the parent particle before branching [dimensionless]; \bar{n} = number of branches spawned [dimensionless]


Sources the note cites: Davey et al. 2016 (pp. 16, 56, 59).

### 2.5 Extension (10 elements)

An element the published work does not have. **This is where the paper's words should go.** Each needs its purpose, its governing equations, its status and its open coverage gaps.

#### Vertical rate in cruise BFO

*Source note:* `results/core-model-stages.md` — Core filter: staged model changes  
*Status:* **BUILT** — config flag `dynamics.bfo_vertical_rate` (default false) added to `crates/mh370/src/filter.rs`, which previously passed a literal 0.0 for vertical speed; base run reproduces stored log evidence bit for bit after the change  
*Classification:* EXTENSION -- "a model the published method does not have, built so the previous one stays available and the base estimate remains byte-reproducible"

*Relation to the published work:* Davey's cruise state carries no vertical rate (sec. 7.2); book sec. 5.3 notes the aircraft's own Doppler compensation does not include the vertical velocity component; quoted: "The vertical rate will affect a BFO measurement but since the model only uses a nominal vertical rate it is unlikely to match any actual vertical manoeuvre in detail." No printed page number given, only section numbers.

Sources the note cites: Davey et al. 2016, sec. 7.2 and sec. 5.3; Fig. 5.4.

#### Fuel and endurance model

*Source note:* `results/core-model-stages.md` — Core filter: staged model changes  
*Status:* **MIXED** — `crates/flight/src/fuel.rs` is built, ported literally from the calibrated `.sources/fuel-performance/validate.py` and checked by five unit tests, but the combined posterior (fuel with evidence) has not converged  
*Classification:* EXTENSION -- "a model the published method does not have, built so the previous one stays available and the base estimate remains byte-reproducible"

*Relation to the published work:* Davey's model has no fuel/endurance model; Assumption 4 instead imposes a 0.73 Mach floor as a stand-in for the fuel constraint, and Assumption 7 notes that low speeds "cannot match the measurements." No page given.

Governing equations, as the note gives them:

- interpolate fuel flow between bracketing speed schedules at the path's flight level and gross weight

  ```latex
  \text{flow} = aM^2 + \frac{b}{M^2}
  ```
  Symbols: a = fitted drag-law coefficient [flow units]; b = fitted drag-law coefficient [flow units]; M = Mach number [dimensionless]; flow = fuel flow rate [kg/h per engine]
  Implemented in: `crates/flight/src/fuel.rs`

- set the filter's initial fuel state from the ACARS reading and Boeing's segment burn rate rather than from the ACARS epoch itself

  ```latex
  36{,}609 = 43{,}800 - 0.700 \times (43{,}800 - 33{,}524)
  ```
  Symbols: 43{,}800 = ACARS fuel reading at 17:06:43 [kg]; 33{,}524 = Boeing's computed fuel at arc 1 [kg]; 0.700 = fraction of the 78.73 min segment elapsed by 18:01:49 [dimensionless]; 36{,}609 = initial fuel at filter start 18:01:49 [kg]
  Implemented in: `crates/flight/src/fuel.rs`


Sources the note cites: Davey et al. 2016, Assumption 4 and Assumption 7; Boeing figures, Appendix 1.6E, Malaysian safety report.

#### Drifting BFO bias

*Source note:* `results/core-model-stages.md` — Core filter: staged model changes  
*Status:* **MIXED** — the random-walk mechanism is built and converges on its own (split-half 0.950); combined with the fuel model it does not converge (split-half 0.849) and the combined overlap result is called a lead rather than a result  
*Classification:* EXTENSION -- "a model the published method does not have, built so the previous one stays available and the base estimate remains byte-reproducible"

*Relation to the published work:* The book models the bias as an unknown constant and states the compromise (p. 29): "This is a less reliable assumption than for BTO because the bias term changes. To compensate for this, the measurement variance was inflated from the empirically derived variance." Table 5.1 gives measured sd as 4.0192 Hz (incl. tarmac) and 4.3177 Hz (in flight), outliers excluded; 7 Hz chosen "to be conservative." Fig. 5.4's within-flight variation reaches ±20 Hz over minutes and "was found to have a geographic dependency" that could not be quantified. Decorrelation to white noise is justified because the BFOs are "generally at least an hour apart."

Governing equations, as the note gives them:

- calibrate the drift rate to reproduce the book's total uncertainty where the book's hourly-spacing decorrelation argument holds

  ```latex
  \text{rate} = \frac{7^2 - 0.995^2}{3600} = 0.01334 \text{ Hz}^2/\text{s}
  ```
  Symbols: 7 = book's measurement standard deviation [Hz]; 0.995 = genuinely random part of the measurement sd [Hz]; 3600 = hourly handshake spacing [s]; rate = bias random-walk variance growth rate [Hz^2/s]

- grow the bias variance between epochs in the linear-Gaussian random walk so the bias is still marginalised exactly by the same Kalman recursion

  ```latex
  \text{variance} \mathrel{+}= \text{rate} \times \text{gap}
  ```
  Symbols: variance = bias random-walk variance [Hz^2]; rate = drift rate [Hz^2/s]; gap = time between successive BFO epochs [s]


Sources the note cites: Davey et al. 2016, p. 29; Davey et al. 2016, Table 5.1, Fig. 5.4.

#### Debris-drift likelihood term (ocean drift module)

*Source note:* `results/debris-drift-methods-draft.md` — Ocean surface drift of recovered debris  
*Status:* **MIXED** — interpolation, source grid, transport, beaching and the recovery-likelihood machinery are BUILT and tested (pilot and production runs completed, run A extension computed on 12 Oct), but several inputs remain PROVISIONAL or not yet run (identification-level priors pending the architect, error-field length scale assumed, most object-response priors, the explicit-Stokes arm, the dropped BRAN2016 arm)  
*Classification:* EXTENSION -- adds a recovery-observation/likelihood framework (kernel, block coefficients, latent identification levels, importance splitting, coverage-node grid extension, shared eddying error field) on top of the reproduced CSIRO/Davey drift system, plus a declared windage-offset correction

*Relation to the published work:* Davey et al. 2016 ch. 11's flaperon-only drifter-replay likelihood is reproduced: it moved the reference median 2.75 NM north with ESS 0.988 [davey2016, pp. 103-109]

Governing equations, as the note gives them:

- defines the drift module's single factor of the composed likelihood

  ```latex
  \ln p(D_{\text{drift}} \mid x)
  ```
  Symbols: x = impact location; D_drift = recovered-debris record (where and when each identified item was found)
  Implemented in: `interpolate.rs`

- weights a particle-find pair by spatial proximity, cut at 6 sigma

  ```latex
  k_{ij} = \phi(d(y_j, z_i)/h)/h
  ```
  Symbols: k_ij = kernel weight linking find j to particle i; d(y_j,z_i) = distance between find location y_j and particle beaching location z_i [km]; h = kernel bandwidth, 50 km [km]; \phi = kernel density function

- computes the per-find, per-block contribution to the recovery density

  ```latex
  a_{jb} = \frac{1}{N} \sum_i k_{ij} \cdot P(\text{discovery in } [t_j, t_j+w_j) \cap \text{period } b \mid \tau_i) / w_j
  ```
  Symbols: a_jb = block coefficient for find j, block b; N = particles in ensemble; k_ij = kernel weight; t_j = find time; w_j = width of discovery window [days]; \tau_i = beaching time of particle i

- supplies the conditioning denominator kept explicit in the likelihood

  ```latex
  A_{cb} = \frac{1}{N} \sum_i m_s(z_i) \cdot P(\text{discovery in period } b \text{ before the window end} \mid \tau_i)
  ```
  Symbols: A_cb = class c's recovery mass in block b; m_s(z_i) = membership of particle i's beaching location in segment s; \tau_i = beaching time

- specifies the marginalised prior on per-block identification levels

  ```latex
  \ln \nu_b \sim N(\mu_{\text{period}}, 1)
  ```
  Symbols: \nu_b = latent identification level for block b; \mu_period = period mean, ln 0.1, ln 0.5, ln 1 for I1-I3

- combines recovery density and conditioning denominator into the node-level likelihood

  ```latex
  L(x) = E_\eta E_\nu \prod_j \left[ \frac{\sum_b \nu_b a_{jb}(x)}{\sum_b \nu_b A_{c(j)b}(x)} \right]
  ```
  Symbols: L(x) = likelihood at source node x; E_\eta = expectation over environment draws; E_\nu = expectation over identification-level draws; a_jb(x) = block coefficient; A_c(j)b(x) = recovery mass for find j's class

- estimates the per-node Monte Carlo noise

  ```latex
  \mathrm{var}(\ln L_A - \ln L_B)/4
  ```
  Symbols: L_A, L_B = likelihood estimates from the two split halves

- sizes the shared eddying error field so the random walk plus field reproduce the replay's single-particle spread

  ```latex
  \sigma_{\mathrm{eff}}^2 = \sigma^2 - K_{\mathrm{ref}}/T
  ```
  Symbols: \sigma_eff = effective error-field standard deviation; \sigma = GDP drifter-replay error, about 0.09-0.12 m/s [m/s]; K_ref = reference diffusivity, 248 m^2/s; T = decorrelation time, about 5-15 days [days]


Open coverage gaps named by the note:

- G10 -- coverage gap: the 367 production nodes leave 13-20% of the weight not computed for 00:19 Held Out and R600 BTO Only, and 1.6-2.9% for R600 BTO + Raw BFO, on run C's impacts

Sources the note cites: Davey et al. 2016 (ch. 11, pp. 103-109) [davey2016].

#### Hydroacoustics module (SOFAR + AGW branches, detection/likelihood gating)

*Source note:* `results/hydroacoustics-methods-draft.md` — Hydroacoustics  
*Status:* **MIXED** — detectors, TL validation and calibration runs are built and committed, but the raw-IMS request and proxy-noise replacement are open and the module currently returns 0.0 to the composer  
*Classification:* EXTENSION -- adds a new acoustic-detection likelihood branch to the estimator, gated on P_D and data availability, not described as modifying a prior Davey component

Governing equations, as the note gives them:

- convert impact kinetic energy into a source acoustic energy flux density via the coupling efficiency

  ```latex
  E_s = \eta \cdot E \cdot \rho c / 2\pi
  ```
  Symbols: E_s = source energy flux density at 1 m [not stated]; \eta = acoustic coupling efficiency [dimensionless]; E = impact kinetic energy [J]; \rho = water density [kg/m^3]; c = sound speed [m/s]

- invert the F-35A observation along the Metz-consistent path to H11 to calibrate eta

  ```latex
  \eta_{cal} = (0.7^2/R) / [E \rho c/2\pi \cdot \Sigma_b S_b(\tau) 10^{(-TL_b/10)}]
  ```
  Symbols: \eta_{cal} = calibrated coupling efficiency [dimensionless]; 0.7 = observed peak pressure at H11 [Pa]; R = term in denominator (meaning not stated in note); E = impact kinetic energy [J]; \rho c = acoustic impedance; S_b(\tau) = source spectrum in band b; TL_b = transmission loss in band b [dB]
  Implemented in: `hydroacoustics-f35a-eta-calibration.md`

- classify each impact draw as impulsive, transitional or quasi-static

  ```latex
  T_c \approx 4H/c
  ```
  Symbols: T_c = AGW cut-off period [s]; H = local water depth [m]; c = sound speed [m/s]
  Implemented in: `agw_regime.py`

- drive the AGW amplitude estimate on an isovelocity, rigid-bottom waveguide

  ```latex
  J = m v_z
  ```
  Symbols: J = vertical surface-force impulse [N\cdot s]; m = impactor mass [kg]; v_z = vertical impact speed [m/s]
  Implemented in: `hydroacoustics-agw-scenarios.md`


Sources the note cites: Porter1992; Collins1993; Blackman2004UCRL, Fig. 23; Metz2023, p. 1348; Brown2026, p. 17; Jensen2011; Jeffreys1961; CMST2014, pp. 6 and 15.

#### Pléiades/COSMO-SkyMed conditional hypothesis module (positional likelihood, two-epoch windage calibration, tension statistics)

*Source note:* `results/pleiades-methods-draft.md` — Pléiades conditional hypothesis  
*Status:* **MIXED** — code and numeric outputs exist in `engine/hypotheses/pleiades/` and `results/pleiades/`, but the note states every number is PROVISIONAL for five listed reasons (tempered-sampler ancestry defect, provisional descent kernel, unverified COSMO source/time/footprint, grade-C OI tracings, unmeasured Pléiades-COSMO transport-error correlation)  
*Classification:* EXTENSION -- adds a new discrete hypothesis arm (`pleiades-origin`), a positional-only forward-transport likelihood, and a two-epoch windage calibration not present in the prior work, while also updating the prior work's transport-error spread (§6.3)

Governing equations, as the note gives them:

- positional compatibility likelihood of impact s against target c under forward transport only, with no identity information

  ```latex
  p(y_c \mid s) = \frac{1}{N_w} \sum_k N_2\!\left(y_c ; x_k(s, t_c), \mathrm{diag}(v_E, v_N)\right)
  ```
  Symbols: y_c = position of target object or cluster c [deg]; s = candidate impact location; N_w = number of windage nodes; x_k(s,t_c) = deterministic forward-transport endpoint of impact s under windage node k at scene time t_c; t_c = Pléiades/COSMO scene acquisition time [UTC]; v_E = east-component displacement variance [km^2]; v_N = north-component displacement variance [km^2]
  Implemented in: `export.rs (pleiades_export_likelihood_surface)`

- dispersion of a displacement driven by exponentially correlated velocity error, supplying the component variance used in the positional likelihood

  ```latex
  v_i(\Delta t) = 2\sigma_i^2 T_i\left[\Delta t - T_i\left(1 - e^{-\Delta t / T_i}\right)\right] + sd_{target}^2
  ```
  Symbols: v_i = variance of displacement component i (east or north) [km^2]; Δt = elapsed time from impact to scene acquisition [d]; σ_i = OU-process velocity-error standard deviation for component i [m/s]; T_i = OU velocity-error correlation time for component i [d]; sd_target = target position uncertainty [km]

- impact log-likelihood under hypothesis H, summing weighted candidate targets scaled by scene coverage

  ```latex
  L(s \mid H) = \sum_c w_c\, p(y_c \mid s) \cdot A_{scene}
  ```
  Symbols: w_c = declared weight of cluster/object c; p(y_c|s) = positional likelihood of target c given impact s; A_scene = scene area [km^2]
  Implemented in: `pleiades_export_likelihood_surface`

- quantify the effective number of parameters constrained by the data, per [HL2019 eq. 3]

  ```latex
  \tilde{d} = 2\,\mathrm{Var}_P\!\left[\log P/\pi\right]
  ```
  Symbols: d̃ = Bayesian model dimensionality; P = posterior density; π = prior density

- degrees of freedom entering the tension-probability calibration

  ```latex
  d = \tilde{d}_A + \tilde{d}_B - \tilde{d}_{AB}
  ```
  Symbols: d = shared Bayesian model dimensionality between data sets A and B; d̃_A, d̃_B = individual dimensionalities; d̃_AB = joint dimensionality

- calibrate the probability that observed tension between two conditioned posteriors arose by chance, per [HL2019 eq. 25, Proposition 2]

  ```latex
  p = P(\chi^2_d > d - 2\ln S)
  ```
  Symbols: p = tension probability between two posteriors; d = shared Bayesian model dimensionality; S = suspiciousness statistic

- define the suspiciousness statistic used alongside the conditional PDF to flag tension, per [HL2019 eqs. 9–10]

  ```latex
  \ln S = \ln R - \ln I
  ```
  Symbols: S = suspiciousness; R = Bayes ratio against a flat prior; I = information ratio

- per-impact probability that wreckage was missed by past search campaigns, used to weight the conditional mass retained after search

  ```latex
  \rho + (1-\rho)\prod_k (1 - q_k c_k)
  ```
  Symbols: ρ = shared miss-probability floor (0.05); q_k = search effectiveness of campaign k; c_k = coverage fraction of campaign k
  Implemented in: `mh370 evaluate (searched-areas module per-impact column)`


Open coverage gaps named by the note:

- P1 -- the absolute Bayes factor H:not-H is not interpretable until a Poisson and footprint term for scene coverage exists, so P(H | D) is never reported
- F1 -- the flight posterior uses the tempered sampler with the ancestry defect found by the filter audit (core request 17) and the uncorrected fuel model, both replaced by the overnight run of 10-11 October
- P2 -- COSMO has no known footprint or target size, so it is not in the impact likelihood and enters only the two-epoch calibration
- the overnight re-run on the new impacts (`prepare/rerun_next.py`), across every 00:19 option, when end of flight writes `next-run/READY`, replaces every flight-conditioned number in §6.2
- Holland H1 / H2 (the two-burst 00:19 options) are not estimable until end of flight settles the hand-off
- OSCAR comparison fields are not yet provisioned by ocean transport; OSCAR is a comparison only
- the P-C correlation (§6.4) awaits ocean transport measuring pair correlations from the GDP replay (requested 9 Oct ~22:40 UTC); ρ = 0 is the reference until then
- D7, the residual search PDF under H, beyond the searched-area factor, needs settling outputs under H
- the correlated multi-object likelihood is not done -- the targets enter as a mixture, so at most one object is treated as wreckage at a time

Sources the note cites: GA2017; COSMO-pos; CSIRO2017; Morph-archive; Orbits; ERA5; GLORYS12; OT-REC; OT-GDP; Taylor1921; HL2019; EoF-reach; EoF-glide; Ref-snapshots; Prior-Pleiades.

#### Non-detection likelihood for seabed search campaigns (searched-areas module)

*Source note:* `results/seabed-search-methods-draft.md` — Searched areas (disconfirming evidence)  
*Status:* **MIXED** — the likelihood, coverage layers and reduction test are BUILT and produce reported numbers, but q for Phase 2 rests on an unverified figure read, Ocean Infinity coverage is inferred, and the upstream prior-propagation row is an explicit placeholder  
*Classification:* EXTENSION -- makes Davey's coverage/detectability terms explicit and applies the construction to MH370 at full search scale, which chapter 11 never did

*Relation to the published work:* Davey, Gordon, Holland, Rutten and Williams set out p(x_final | S, Z_K) ∝ [1 − P_D(x_final)] p(x_final | Z_K) as equation (11.1) in chapter 11, with P_D "the probability that the cumulative search effort would have detected the aircraft at any particular location" (D-2, D-3), and named AF447 as the precedent (D-6); they do not apply it -- chapter 11 carries no search-conditioned posterior, and (11.1) appears twice without a computed result (D-10). No printed page is given.

Governing equations, as the note gives them:

- give the probability of non-detection at y as one log-likelihood column on the shared impact samples

  ```latex
  P(no find | y) = \rho + (1 - \rho) \prod_k [1 - c_k(y) g_k(W) q_k]
  ```
  Symbols: y = impact position [-]; W = wreckage field produced by the impact [-]; \rho = probability the field is of the undetectable class [-]; c_k(y) = fraction of ground around y on which campaign k holds valid data [-]; g_k(W) = size response of campaign k's sensor to field W [-]; q_k = probability of recognition given detectable data over the field, campaign k [-]

- Davey's published search-conditioned posterior update, equation (11.1), never computed in chapter 11

  ```latex
  p(x_final | S, Z_K) \propto [1 - P_D(x_final)] p(x_final | Z_K)
  ```
  Symbols: x_final = final (impact) position [-]; P_D = cumulative probability the search effort would have detected the aircraft at that location [-]; Z_K = search evidence up to increment K [-]

- show that for a point target, one campaign, and ρ = 0, equation (1) reduces exactly to Davey's (11.1) factor

  ```latex
  P(no find | y) = 1 - c(y) q = 1 - P_D(y)
  ```
  Symbols: c(y) = covered fraction of ground around y for a single campaign [-]; q = probability of recognition given detectable data [-]; P_D(y) = Davey's detection probability at y [-]
  Implemented in: `module test reduces_to_davey_eq_11_1_for_a_point_target_one_campaign_and_rho_zero`

- Davey's planning equation (11.2), used here only for the cumulative P(find)-against-area curve, never as a top-N block ranking

  ```latex
  P(find during search of A) = P_D \int_A p(x | Z_K) dx
  ```
  Symbols: A = candidate search area [km^2]; P_D = planning (constant) probability of detection [-]; p(x | Z_K) = residual impact density given evidence to date [-]


Sources the note cites: Davey, Gordon, Holland, Rutten and Williams, Bayesian Methods in the Search for MH370, chapter 11; Stone, Keller, Kratzke and Strumpfer (AF447 construction, S-1, S-2, S-3, S-5, S-6, S-7); ATSB Figure 73 (A-4, A-5, A-8); ATSB "in excess of 120,000 square kilometres" (A-1); Geoscience Australia backscatter mosaics and vector L0 footprint.

#### Wreckage settling (ocean-surface-impact-to-seabed transform)

*Source note:* `results/settling-methods-draft.md` — Impact to seafloor (settling)  
*Status:* **MIXED** — ocean physics (GLORYS12V1 column, surface current, ERA5 wind, AusSeabed/GEBCO bathymetry, TEOS-10) is BUILT since `bfb71d5`, but the breakup table remains a set of declared educated estimates, so every number is PROVISIONAL  
*Classification:* EXTENSION -- adds a new post-impact transform to the pipeline (impact to seabed/drift) not previously present

Governing equations, as the note gives them:

- set the probability that an impact produces the intact breakup family

  ```latex
  P(\text{intact}) = L(\ln(a/V_d)/s)\, L(\ln(c/V)/s)
  ```
  Symbols: L = logistic function [dimensionless]; a = intact-threshold speed, 8 m/s [m/s]; V_d = descent speed at first contact [m/s]; c = threshold total speed, 100 m/s [m/s]; V = total speed at first contact [m/s]; s = logistic scale parameter, 0.2 [dimensionless]
  Implemented in: `breakup.rs`

- set the probability that an impact produces the fragmented breakup family

  ```latex
  P(\text{fragmented}) = (1 - P(\text{intact}))\, L(\ln(V/b)/s)
  ```
  Symbols: b = fragmentation-threshold speed, 110 m/s [m/s]; V = total speed at first contact [m/s]; s = logistic scale parameter, 0.2 [dimensionless]
  Implemented in: `breakup.rs`

- assign the residual probability mass to the broken family

  ```latex
  P(\text{broken}) = \text{the remainder}
  ```
  Symbols: P(\text{broken}) = probability of the broken breakup family [dimensionless]
  Implemented in: `breakup.rs`

- compute each wreckage element's sinking speed relative to the water during descent

  ```latex
  w = k \sqrt{2 g s (1 - \rho_w/\rho_m) / (\rho_w C_d)}
  ```
  Symbols: w = descent speed relative to the water [m/s]; k = descent factor for fluttering/tumbling bodies, k >= 1 [dimensionless]; g = gravitational acceleration [m/s^2]; s = areal density [kg/m^2]; rho_w = water density [kg/m^3]; rho_m = material density [kg/m^3]; C_d = drag coefficient [dimensionless]

- convert water-relative sink speed to ground-relative sink speed wherever vertical velocity is resolved

  ```latex
  v_{ground} = w - w_{up}
  ```
  Symbols: v_{ground} = descent speed relative to the ground [m/s]; w = descent speed relative to water [m/s]; w_{up} = vertical water velocity [m/s]


Sources the note cites: ntsb2010; bea2012af447; tsb2003; andersen2005; field1997; lellouche2021glorys12; era5; gebco2026; AusSeabed; ioc2010teos10; mcdougall2011gsw; reagan2024woa23; atsb2017; af447seabed2011; mca2006fsh604; margo1990; dnv2010; mearns1994; thresher1963; mot2018mh370; metron2011.

#### Convergence criterion (split-half / ESS floor)

*Source note:* `results/davey-2016-reference.md` — Reproduction audit of the published model  
*Status:* **BUILT** — the floor is implemented and calibrated against a converged reference in split-half-threshold.md  
*Classification:* EXTENSION -- Davey published no quantitative convergence diagnostic, so the 0.90 floor is introduced by this project, not inherited

*Relation to the published work:* Procedural only: chose "to adaptively increase the number of particles used until it was possible to identify an adequate number of likely paths" (p. 56); "effective sample size" and "converged" do not occur in the book, "degeneracy" occurs once (p. 16), and there is no split-half statistic, ESS threshold, or numerical convergence test anywhere in the text.

Sources the note cites: Davey et al. 2016 (p. 56).

#### Fuel model

*Source note:* `results/davey-2016-reference.md` — Reproduction audit of the published model  
*Status:* **BUILT** — described as the project's existing in-filter fuel model  
*Classification:* EXTENSION -- in-filter fuel constraint goes beyond Davey's infinite-fuel assumption with post-hoc censoring

*Relation to the published work:* Assumption 4 (p. 60): infinite fuel; fuel constraints are applied afterwards as a censor.

Sources the note cites: Davey et al. 2016 (p. 60, §8.3).

## 3. Results and findings

Every claim below carries the caveat labels its note attaches, **verbatim**, and the artifact it came from. A claim with no artifact recorded is marked so: it is traceable to its note but not yet to a run directory, and must be before it is published.

### 3.1 Core filter: staged model changes

Source note: `results/core-model-stages.md`

**R1.** Seed 1 rebuilt after the vertical-rate change reproduces its stored log evidence exactly at −96.20447573471249, a difference of 0.000e+00, so the published model is still reproduced bit for bit and `make regress` still means something.

- *Labels, verbatim:* **The base run is untouched.**
- *Artifact:* **not recorded in the note**

**R2.** Adding the vertical-rate term to the widened-prior configuration (stage 1) changes the posterior from median −37.319°S, P(shoulder) 0.1970, overlap 0.764, split-half 0.927, log Z −98.02 without the term to median −37.337°S, P(shoulder) 0.1762, overlap 0.721, split-half 0.916, log Z −98.05 with it, while on the base configuration the term alone moves median −38.160→−38.188, shoulder 0.0368→0.0359, split-half 0.934→0.945.

- *Labels, verbatim:* the omission is an order of magnitude larger than the noise it was being scored against; it cannot be a lever on the shoulder while altitude changes are this brief; **That is the finding, not a disappointment.**
- *Artifact:* **not recorded in the note**

**R3.** The 00:19:29→00:19:37 BFO step of 184 Hz corresponds to an equivalent vertical rate of 10,500 ft/min, about nine times the largest bias excursion shown in the book's Fig. 5.4 (20 Hz / 1,140 ft/min), so a bias excursion cannot produce it and a steep descent can, while the single 00:11 value's ±20 Hz excursion and ~1,100 ft/min descent remain degenerate with each other.

- *Labels, verbatim:* part of the shoulder result rests on a quantity degenerate with an unmodelled bias excursion — which is what stage 3 addresses
- *Artifact:* **not recorded in the note**

**R4.** In the burn-only run with no fuel evidence applied, 79.2% of posterior weight runs dry before 00:19:37 and the weighted median exhaustion is 23:17:20, an hour before the 00:19 log-on.

- *Labels, verbatim:* fuel is a strong constraint on the wide-Mach posterior, which is exactly the constraint Davey's Assumption 4 substituted the 0.73 Mach floor for
- *Artifact:* **not recorded in the note**

**R5.** 73.4% of posterior weight spends time at a Mach outside the tabulated schedules, weighted mean 2.6 hours, and validation against Boeing's own out-of-schedule items gave errors to −8.5%.

- *Labels, verbatim:* that belongs in the caveats rather than the conclusions
- *Artifact:* **not recorded in the note**

**R6.** Restoring Davey's Mach range and altitude prior and adding the fuel model as evidence moves P(shoulder) from 0.0368 to 0.0868, a factor of 2.4, and improves overlap with the published curve from 0.717 to 0.791, the best of any run in the project, with split-half rising from 0.829 at four replicates to 0.862 at eight replicates while median, shoulder and overlap stay essentially unchanged (−37.828→−37.733; 0.0868→0.0864; 0.791→0.793).

- *Labels, verbatim:* **The shoulder is precisely the quantity that has not converged**; reportable only as "about 2–3 times the base"; the magnitude not yet an estimate; **0.79 stands.**; the wide-Mach fuel numbers — shoulder 0.24 — should be quoted as an upper bound, not an estimate
- *Artifact:* **not recorded in the note**

**R7.** Run on its own, the drifting bias reduces P(shoulder) from 0.0368 to 0.0260 and overlap from 0.717 to 0.634 with split-half 0.950, and the posterior BFO bias is estimated at 145.22 ± 1.47 Hz against 150.13 ± 0.37 Hz for the constant-bias base, while the stage-3 combination on the widened-prior fuel run instead gives the best overlap of any run so far (0.792) while raising the evidence relative to stage 2 (−104.57 against −106.15).

- *Labels, verbatim:* moves *away* from the published curve; the drift correctly declining to pin down a quantity that moves; It is **not converged**, so this is a lead rather than a result.; That agreement belongs to the combination, not to the drifting bias.
- *Artifact:* **not recorded in the note**

**R8.** Applying the drifting bias to the narrow-Mach fuel configuration pulls the result south (shoulder 0.0864→0.0648, overlap 0.793→0.728) and raises the log evidence from −104.49 to −101.65, a Bayes factor of about 17:1 in favour of the drifting-bias measurement model over the flat 7 Hz one.

- *Labels, verbatim:* The caveat is that this compares two *measurement-error* models, both of them modelling choices rather than measured quantities, so it is not evidence about the aircraft's path.
- *Artifact:* **not recorded in the note**

### 3.2 Ocean surface drift of recovered debris

Source note: `results/debris-drift-methods-draft.md`

**R9.** The pilot's 1,709-node run found no node resolved at 50 km, arrival probabilities at Réunion, Mauritius-Rodrigues and NE Madagascar 7-30x above the prediction committed before the run, and an unresolved correlation length.

- *Labels, verbatim:* PROVISIONAL, not evidence; No number below is evidence about the impact location.
- *Artifact:* `results/debris-drift-pilot.md`

**R10.** The 90% HPD region covered the true node in 58 of 60 synthetic-recovery trials (0.97), with a calibration ratio of 1.056.

- *Labels, verbatim:* No number below is evidence about the impact location.
- *Artifact:* `test `synthetic_recovery_coverage`, run 9 Oct`

**R11.** The flaperon-only drifter-replay likelihood moved the reference median 2.75 NM north with ESS 0.988, falling to a 1.16 NM shift with a 0.25-degree kernel.

- *Labels, verbatim:* No number below is evidence about the impact location.
- *Artifact:* `results/davey-ch11-reproduction.md`

**R12.** Land-mask stranding at Réunion ran at 1.43e6 particle-steps per second in the check, and 1.72e6 over the whole pilot.

- *Labels, verbatim:* No number below is evidence about the impact location.
- *Artifact:* `smoke-fields.toml`

**R13.** On run C's impacts the 367 production nodes leave 13-20% of the weight not computed for 00:19 Held Out and R600 BTO Only, and 1.6-2.9% for R600 BTO + Raw BFO.

- *Labels, verbatim:* coverage gap G10; No number below is evidence about the impact location.
- *Artifact:* `results/debris-drift-production-sizing.md`

**R14.** With the extension's 710 nodes, the not-computed weight including the off-grid part is below 1% for every stratum and standard 00:19 option: on run C at most 0.81% (Held Out), 0.64% (R600 BTO Only), 0.17% (R600 BTO + Raw BFO) and 0% (Holland H1/H2); on the H1/H2 sweep at most 0.64%, 0.52%, 0.16%, 0.10% and 0.29%.

- *Labels, verbatim:* No number below is evidence about the impact location.
- *Artifact:* `run A (12 Oct), 710 nodes`

**R15.** A -0.60% windage offset reduced the SD of the GlobCurrent-GLORYS12 node log-likelihood difference north of 30°S from 3.28 to 1.66, the mean deficit north of 25°S from -5.78 to -2.19 (9 nodes), and the mean excess south of 37°S from +3.56 to +0.86; with -0.75% the same three values were 1.44, -1.57 and -0.40.

- *Labels, verbatim:* No number below is evidence about the impact location.
- *Artifact:* `smoke test, 92 nodes`

**R16.** In the analytic importance-splitting test, brute force gave 1.285e-2 +/- 5.6e-4 and splitting gave 1.329e-2 +/- 9.2e-4.

- *Labels, verbatim:* No number below is evidence about the impact location.
- *Artifact:* `test `splitting_is_unbiased_and_resolves_a_rare_target``

### 3.3 Hydroacoustics

Source note: `results/hydroacoustics-methods-draft.md`

**R17.** By the pre-registered rule (median and RMS over 13–40 Hz), air9 is partly validated at both stations, with median residual −0.15 dB at H01W and +3.17 dB at H08S, RMS 7.93 and 7.91 dB.

- *Labels, verbatim:* partly validated; That rule cannot see a slope, and the slope is wrong; Absolute level and frequency slope are therefore NOT validated.
- *Artifact:* `hydroacoustics-blackman-validation.md`

**R18.** The station-to-station difference, which cancels the source term, fits to −1.5 dB median and 3.4 dB RMS.

- *Labels, verbatim:* This is the only part that is validated.
- *Artifact:* `hydroacoustics-blackman-validation.md`

**R19.** On the air9 → H01W path KRAKEN and RAM agree to a median |Δ| of 1.78 dB; to the seabed IMOS loggers KRAKEN is pessimistic by 13–47 dB at Perth Canyon and 23–132 dB at Portland; air8's ridge blockage weakens from 39.1 dB under KRAKEN to 18.3 dB under RAM; on the F-35A → H11 path KRAKEN is about 3.5 dB optimistic.

- *Labels, verbatim:* station difference validated; absolute slope not
- *Artifact:* `hydroacoustics-ram-tl-check.md, prereg 6b747a1`

**R20.** eta_cal under KRAKEN runs from 2×10⁻² at z_s = 2 m to 1×10⁻⁴ at 30 m (f⁻²); with the RAM correction for that path, the median rises from 1.3×10⁻³ to 2.7×10⁻³.

- *Labels, verbatim:* **NONE RECORDED — check the note before publishing this claim**
- *Artifact:* `hydroacoustics-f35a-eta-calibration.md, prereg 3ca9564`

**R21.** At false alarm 0.005, SNR₅₀ is 28.8 dB (3376), 18.6 dB (3274) and 38.5 dB (3250).

- *Labels, verbatim:* **NONE RECORDED — check the note before publishing this claim**
- *Artifact:* `hydroacoustics-item3-injection-recovery.md`

**R22.** With RAM-corrected TL, P_D at any open IMOS logger is 7.6 % at false alarm 0.005 and 32 % at 0.05 (stand-in prior); the windows recorded on 8 Mar 2014 show no detection.

- *Labels, verbatim:* Because P_D is low, the information from this non-detection is below 10⁻³ bit.
- *Artifact:* **not recorded in the note**

**R23.** No full-water-depth mode below 0.24 Hz (H01W) or 0.27 Hz (H08S) reaches the hydrophones; from 0.25 to 2 Hz the median noise is 12–110 dB above the upper end of the steep-entry signal range, and ditching is 40–110 dB below.

- *Labels, verbatim:* exploratory, prereg 55ebdcc; So the AGW branch carries P_D ≈ 0 for every scenario and adds no likelihood term.
- *Artifact:* `hydroacoustics-agw-scenarios.md`

### 3.4 Pléiades conditional hypothesis

Source note: `results/pleiades-methods-draft.md`

**R24.** Across the eight object-rating × cluster-weight arms (pooled seeds, eof-2f descent kernel), the tension probability p is 0.11–0.18 pooled and 0.10–0.22 across seeds, with ln S between −1.13 and −0.83 and d between 1.6 and 2.4, for either product and for their equal-weight mixture.

- *Labels, verbatim:* There is no significant tension. ; The conditional is broad.
- *Artifact:* `results/pleiades/rerun-measured/rerun-measured.md`

**R25.** 5.4–7.4% of the conditional mass lies at ≥ 30 NM and 2.9–4.9% at ≥ 50 NM inside the 7th arc, rising to 46% at 103.4 NM once disks are used instead of the eof-2f kernel.

- *Labels, verbatim:* The western lobe mostly does not survive the descent reach.
- *Artifact:* `results/pleiades/rerun-measured/rerun-measured.md`

**R26.** At the measured spread of 13–16 km per component over 40.5 h, the two-epoch windage calibration gives an information gain of only 0.001–0.07 bits for both products, with ln BF(free vs fixed windage) between −0.12 and −0.01 and P(dawn pass) 0.50–0.53, and F4 is never matched (60–115 km from every target).

- *Labels, verbatim:* The calibration carries no information.
- *Artifact:* `results/pleiades/rerun-measured/`

**R27.** With the 00:19 option held out, the unconditional 90% HDR is 620,510 km² before the search and 730,426 km² after, with the search retaining Z = 0.733 of the mass.

- *Labels, verbatim:* **NONE RECORDED — check the note before publishing this claim**
- *Artifact:* `results/pleiades/branch-289/branch-289.md; results/pleiades/closeup-289/closeup-289.md`

**R28.** P+C3 90% HDR falls from 50,821 to 49,925 km² under the base search, and P+C4 falls from 58,900 to 57,306 km² (base search) then rises to 59,316 km² once both OI layers are applied.

- *Labels, verbatim:* **NONE RECORDED — check the note before publishing this claim**
- *Artifact:* `results/pleiades/branch-289/branch-289.md; results/pleiades/closeup-289/closeup-289.md`

**R29.** Under H with OI applied, 87–88% of the conditional mass lies outside every past search envelope and 4.5–5.2% lies in the inferred north-west band, with ln S of +0.46 to +1.36 in every arm.

- *Labels, verbatim:* **NONE RECORDED — check the note before publishing this claim**
- *Artifact:* `results/pleiades/branch-289/branch-289.md`

**R30.** With 00:19 fixed to R600 raw, the search keeps only 0.35–0.39 of the conditional mass against 0.70–0.73 with 00:19 held out, with r600/inflated giving 0.385–0.435 and r1200/inflated giving 0.546–0.559.

- *Labels, verbatim:* The 00:19 option dominates the after-search result
- *Artifact:* `results/pleiades/branch-289/branch-by-0019-option.csv`

**R31.** Reproducing the prior work's settings on the two ocean models gives a 90% area of 57,436 km² (52,823–69,465 km² across the 27–37 km spread range) and a mode at 35.38 S 92.38 E, against the prior work's own 57,708 km² and mode near 35.3 S 92.2 E, while substituting the measured spread instead gives 233,802 km² with mode at 35.08 S 91.38 E.

- *Labels, verbatim:* The prior map is reproduced to within its spread setting.
- *Artifact:* `prepare/audit_closeup.py`

### 3.5 Searched areas (disconfirming evidence)

Source note: `results/seabed-search-methods-draft.md`

**R32.** On the reference-289 full-scale impacts, Z = 0.7335 at ρ = 0.05, with Phase 2 removing 0.2805 of the mass at ρ = 0, Ocean Infinity 2018 alone 0.0400, and the two together 0.3202.

- *Labels, verbatim:* **NONE RECORDED — check the note before publishing this claim**
- *Artifact:* **not recorded in the note**

**R33.** Measured at full scale on the held-out arm under +alive, ρ is worth 0.7059 to 0.8529 in Z over the range 0 to 0.5, more than every other measured input combined, and has no published value.

- *Labels, verbatim:* **no**; has no published value; reported as a bracket (for repeat-search dependence row)
- *Artifact:* `results/seabed-search-289-fullscale-alive/`

**R34.** On the residual, P(find) = 25% needs the best 21 blocks and 51,977 km², 50% needs 62 blocks and 152,587 km², and 75% needs 231 blocks and 580,334 km², while under +alive the same curve reads 24/59,005, 70/171,921 and 248/623,095.

- *Labels, verbatim:* the cumulative curve is the reportable object; no plan should be drawn from a ranking
- *Artifact:* **not recorded in the note**

**R35.** The search non-detection moves the residual median 0.20° north, from −36.78 to −36.58, and grows the 90% region, so the residual is usually wider than the input.

- *Labels, verbatim:* A non-detection is not a localisation.
- *Artifact:* **not recorded in the note**

**R36.** On the reference-289 run, arms that score both 00:19 bursts fall to 8–82 effective impacts out of 12.8 × 10^6 and their areas and medians are not estimable, while the module's own likelihood is converged throughout, split-half 0.968 on the held-out arm after the search evidence.

- *Labels, verbatim:* anything below 1,000 effective impacts is reported as unconverged, not as a result
- *Artifact:* **not recorded in the note**

**R37.** A field of 40 pieces between 0.5 and 8.3 m long and 0.1 to 2.05 m proud gives g_k within 10⁻⁹ of 1, and reading coverage at the impact position rather than over the whole settled field is worth 0.0003 in Z.

- *Labels, verbatim:* Runs made with the point target are the saturated limit of the full model, not a provisional stand-in.
- *Artifact:* `results/seabed-size-response.md; results/seabed-field-coverage-289/ (40,000 outcomes, 2.2 × 10^6 settled elements)`

**R38.** Treating the field as one object with a covered fraction removes 26.6% of the probability, while treating it as detected if any settled element fell on valid data removes 28.9%, with the difference carried entirely by the 2.3% of outcomes whose impact lies off searched ground while part of the field reaches onto it.

- *Labels, verbatim:* Nothing in the coverage data resolves it.
- *Artifact:* **not recorded in the note**

**R39.** Treating ATSB Phase 2 as one union campaign gives evidence Z = 0.4040 on the fixture; splitting it into its four sensors gives 0.4001 with shared misses and 0.3966 with independent misses, and the main estimate uses the union as the conservative (maximal-dependence) end.

- *Labels, verbatim:* **NONE RECORDED — check the note before publishing this claim**
- *Artifact:* `results/seabed-repeat-search-dependence.md`

### 3.6 Impact to seafloor (settling)

Source note: `results/settling-methods-draft.md`

**R40.** With the 00:19 bursts held out and no log-on cause, p10 / p50 / p90 seabed depth under the reference-289 impacts are 3,362 / 3,846 / 4,341 m.

- *Labels, verbatim:* PROVISIONAL, PROVISIONAL-OVERNIGHT, fuel uncorrected (fuel-model audit F1-F14 open)
- *Artifact:* `results/settling-d6-289/`

**R41.** On the real ocean at four impact points, engines and gear rest within 0.18-0.48 km (p90); broken and fragmented sections within 0.4-0.8 km, intact sections at about 5.6 km; cabin contents at about 9-13 km.

- *Labels, verbatim:* PROVISIONAL
- *Artifact:* `results/settling-d6-real-289/`

**R42.** On the provisional controlled-depth page at 3,850 m, engines and gear rest within 0.20-0.44 km (p90); wing box and fuselage sections within 0.45-0.82 km for broken/fragmented impacts but 5.4-5.7 km for intact ones; cabin contents about 11-12 km.

- *Labels, verbatim:* PROVISIONAL
- *Artifact:* `results/settling-d6-289/`

**R43.** The settled-offset kernel is the same under every 00:19 option, with half the settled mass resting within 0.34-0.36 km of its impact and 90 % within 2-3.6 km, so the seabed PDF of the main wreckage is the impact PDF to about 1 % in area.

- *Labels, verbatim:* Impacts north of 18° S (under 0.02 % of any panel) lie outside the ocean window and are excluded as not computed
- *Artifact:* `results/settling-wreckage-field-289/ and results/settling-wreckage-field-289-priorities/`

**R44.** Reading search coverage over the settled field instead of at the impact point changes the evidence by 0.0003 when the field counts as one object with a covered fraction, and by 2.3 points only if any single settled element on searched ground counts as a detection.

- *Labels, verbatim:* held out, 40,000 outcomes
- *Artifact:* `results/seabed-field-coverage-289/`

**R45.** The settled-offset kernel in core run (b) is unchanged from §6a: p50 0.36 km, p90 3.6-3.9 km, 7-8 % of settled mass beyond 5 km, and p99 about 21-22 km, with about 18 % of mass staying afloat.

- *Labels, verbatim:* Core (b) does not pass split-half; every area here inherits that, and none is evidence about where MH370 lies.
- *Artifact:* `results/settling-core-set-next-run-b/ and results/settling-family-next-run-b/`

**R46.** The 90 % seabed areas by type of flight end for Held Out are A1 393, A2 673 and B 529 thousand km², and for R600 BTO + Raw BFO they are A1 86, A2 245 and B 221 thousand km².

- *Labels, verbatim:* Read each family as a conditional result, not as evidence for that family., Core (b) does not pass split-half; every area here inherits that, and none is evidence about where MH370 lies.
- *Artifact:* `results/settling-family-next-run-b/`

### 3.7 Reproduction audit of the published model

Source note: `results/davey-2016-reference.md`

**R47.** The 0.90 split-half floor is ours, not Davey's, and the paper must say so.

- *Labels, verbatim:* asserted rather than derived; "what Davey used is not established"
- *Artifact:* `results/split-half-threshold.md`

**R48.** The accident-flight prior needs no correction: 0.5 NM, 1° and uniform Mach 0.73-0.84 are Davey's own values from Chapter 4.

- *Labels, verbatim:* Table 8.2's initialisation rows belong to the validation experiments and must not be applied here.; Table 8.2 and p. 64 disagree with each other -- 0.4 arcminutes against 0.4 degrees, a factor of sixty -- so the table alone cannot be trusted on these rows and the chapter text governs.
- *Artifact:* `config/davey2016.toml`

**R49.** The three initial deviation rows land on Davey's tabulated figures to three significant figures, which is a real check on the OU constants.

- *Labels, verbatim:* **NONE RECORDED — check the note before publishing this claim**
- *Artifact:* `crates/flight/src/lib.rs`

**R50.** The branching resampler moves from an idea on the list to the published method we are not yet reproducing, with its constants known: n-bar in 3-10, eta at e^-25 or e^-30.

- *Labels, verbatim:* structural; is not necessarily computationally efficient, but in this particular application it was more important to broadly explore the enormous state space
- *Artifact:* **not recorded in the note**

**R51.** Davey's filter assumes infinite fuel (assumption 4, p. 60) and applies fuel constraints afterwards as a censor; this project's in-filter fuel model is an extension beyond the published method, not a reproduction of it.

- *Labels, verbatim:* **NONE RECORDED — check the note before publishing this claim**
- *Artifact:* **not recorded in the note**

**R52.** Over the 4,267 s leg into 19:41, with three manoeuvre clocks each of mean tau and tau ~ Jeffreys(0.1, 10) h, the expected number of manoeuvres is 7.6 and the probability of at least one is 83%.

- *Labels, verbatim:* An earlier version of m1941-geometry-and-lookahead.md quoted 56%, computed against a tau range of 1-20 h that is neither Davey's nor the engine's; the engine has always used 0.1-10 h and the corrected figure is 83%.
- *Artifact:* `m1941-geometry-and-lookahead.md`

**R53.** The book gives the acceleration rate on p. 49 -- "The assumed rate corresponds to a change of Mach of 0.1 in one minute" -- which does corroborate mach_rate_per_s = 0.1/60.

- *Labels, verbatim:* One citation was worse than misnumbered: the acceleration rate was attributed to a page that does not state it.
- *Artifact:* `results/shoulder-comparison.md`

### 3.8 Reproduction of the published refinement chapter

Source note: `results/davey-ch11-reproduction.md`

**R54.** The pooled update (joined, 1 degree kernel, epsilon 1e-4) moves the median +2.7 NM north, about 0.05 degrees of latitude, with an ESS fraction of 0.988 and TV to prior of 0.032.

- *Labels, verbatim:* The reproduction gives Davey's direction and magnitude.
- *Artifact:* `results/davey-ch11-reproduction.json`

**R55.** Narrowing the kernel from 1 degree to 0.5 to 0.25 degrees does not enlarge the median shift (2.7, 1.6, 1.2 NM) while TV rises 0.032 to 0.061 and ESS falls 0.988 to 0.967, and at 0.25 degrees the seed-to-seed TV (mean 0.119) exceeds the prior-to-update TV (0.095).

- *Labels, verbatim:* The D3 test: how much of "negligible" is resolving power?, But the extra reshaping is not resolved., So with the GDP drifter record the narrower kernel buys noise, not signal.
- *Artifact:* `results/davey-ch11-reproduction.json`

**R56.** Epsilon of 1e-4 versus 1e-6 changes the pooled median little (+2.75 vs +3.02 NM at 1 degree) but the minimum relative likelihood over posterior mass falls from 0.43 to 0.03 as epsilon shrinks.

- *Labels, verbatim:* a lot to the likelihood floor
- *Artifact:* `results/davey-ch11-reproduction.json`

**R57.** The un-joined reconstruction is noise-dominated: only 14 real drifters arrive in the window, ESS falls to 0.701, the relative likelihood reaches 21 at 1 degree (583 at 0.25 degrees), and the median moves the opposite way, -2.7 NM.

- *Labels, verbatim:* The un-joined version is noise-dominated and not a usable likelihood.
- *Artifact:* `results/davey-ch11-reproduction.json`

**R58.** Sensitivities to the unprinted join and region choices all stay inside "negligible", with medians +1.6 to +7.2 NM north and no sign reversal.

- *Labels, verbatim:* Calibrated, not printed., Not printed.
- *Artifact:* `results/davey-ch11-reproduction.json`

**R59.** A partial bootstrap over start drifters, which does not resample the partner pool, gives +3.0 +/- 1.8 NM at 1 degree with 97.5% of replicates northward, and +2.3 +/- 3.7 NM at 0.25 degrees (epsilon 1e-6) with 72.5% northward.

- *Labels, verbatim:* partial, The bootstrap does not resample the partner pool, so the stated uncertainties are lower bounds.
- *Artifact:* `results/davey-ch11-reproduction.json`

**R60.** Mass north of 31.5 degrees S rises from 0.0246 before to 0.0358 after at 1 degree and 0.0428 after at 0.25 degrees, a rise that is stable across single seeds (0.035-0.038 at 1 degree, 0.040-0.048 at 0.25 degrees).

- *Labels, verbatim:* stable
- *Artifact:* `results/davey-ch11-reproduction.json`

**R61.** The posterior this update is applied to, no-exhaustion-prior, fails split-half convergence at 0.9020 against a floor of 0.924 at 8 replicates.

- *Labels, verbatim:* fails split-half convergence
- *Artifact:* `results/no-exhaustion-prior-datasheet.md §3`

### 3.9 Composer: first composed pass

Source note: `results/composer-pass1-run-c.md`

**R62.** Every product of every option, version and stratum is UNCONVERGED on the source split-half, with core run C mean over 35 partitions free 0.918, Davey dynamics + radar 0.910, descent-climb 0.892, routes 0.850 against the 8-replicate floor 0.924.

- *Labels, verbatim:* run C NOT CONVERGED (core split-half mean 0.850-0.918 against the 8-replicate floor 0.924)
- *Artifact:* `factor-split-half-summary.txt`

**R63.** For R600 BTO Only, product G (flight+EoF+drift+hydro) gives mixture median impact latitude −37.17° (95% −40.27 to −25.69) with 50%/90% regions 88/463 k km².

- *Labels, verbatim:* run C NOT CONVERGED (core split-half mean 0.850-0.918 against the 8-replicate floor 0.924) · EoF physics provisional; no structural limit (G13) · hydro predictive, not calibrated (stand-in L_hyd + audit F8) · drift GLORYS12 only, current nodes (367; not the run A extension) · GlobCurrent excluded (F1) · H products conditional on the Pléiades objects being MH370 debris · Holland H1/H2 not estimable
- *Artifact:* `mixtures.csv / pass1-results.json`

**R64.** For R600 BTO Only, product H (given H) gives mixture median impact latitude −36.04° (95% −40.15 to −28.94) with 50%/90% regions 18/175 k km².

- *Labels, verbatim:* run C NOT CONVERGED (core split-half mean 0.850-0.918 against the 8-replicate floor 0.924) · EoF physics provisional; no structural limit (G13) · hydro predictive, not calibrated (stand-in L_hyd + audit F8) · drift GLORYS12 only, current nodes (367; not the run A extension) · GlobCurrent excluded (F1) · H products conditional on the Pléiades objects being MH370 debris · Holland H1/H2 not estimable
- *Artifact:* `mixtures.csv / pass1-results.json`

**R65.** ln R (re-weighted strata) is +0.543 for R600 BTO Only and +0.336 for Held Out, meaning drift and the stand-in hydro mildly favour the Pléiades area (R≈1.7 and 1.4) but ln R is not resolved at the 0.1-0.2 nat level.

- *Labels, verbatim:* run C NOT CONVERGED (core split-half mean 0.850-0.918 against the 8-replicate floor 0.924) · EoF physics provisional; no structural limit (G13) · hydro predictive, not calibrated (stand-in L_hyd + audit F8) · drift GLORYS12 only, current nodes (367; not the run A extension) · GlobCurrent excluded (F1) · H products conditional on the Pléiades objects being MH370 debris · Holland H1/H2 not estimable
- *Artifact:* `pass1-results.json / tables.md`

**R66.** Family A1's weight under G is carried on very few effective rows (1,276 effective parents per seed in descent-climb, smallest over seeds/strata), and excluding over-speed rows raises A1's ESS to 33,883, so A1's latitude under G in the all-rows version is set by a handful of infeasible-speed impacts.

- *Labels, verbatim:* run C NOT CONVERGED (core split-half mean 0.850-0.918 against the 8-replicate floor 0.924) · no structural limit (G13)
- *Artifact:* `coverage-ess.csv`

**R67.** G12 is closed for G, Ga, H and Ha of both options: the aimed resample keeps 39,892-40,000 distinct impacts of 40,000 draws and a row ESS of 0.59-4.18 M, with each seabed PDF agreeing with its impact PDF to under 1% in area.

- *Labels, verbatim:* run C NOT CONVERGED (core split-half mean 0.850-0.918 against the 8-replicate floor 0.924) · hydro predictive, not calibrated (stand-in L_hyd + audit F8) · H products conditional on the Pléiades objects being MH370 debris
- *Artifact:* `settling/next-run-c-composed-aimed/ (settling's published samples); stand-in cross-check on copy of settling 9330d4c`

**R68.** Excluding not-computed rows (Gx/Hx) shrinks R600 BTO Only G's 90% region from 463k to 304k km² and H's from 175k to 53k km², moving the G median 0.33° north (−36.84), with not-computed drift weight 0.17-0.28 per seed (R600 BTO Only).

- *Labels, verbatim:* run C NOT CONVERGED (core split-half mean 0.850-0.918 against the 8-replicate floor 0.924) · drift GLORYS12 only, current nodes (367; not the run A extension)
- *Artifact:* `mixtures.csv (Gx/Hx rows)`

**R69.** Every stratum's P1 increment reproduces end of flight's family-evidence-run-c.json ln Ẑ to max |Δ| = 1.1×10⁻¹⁰, confirming correct carry-through of end-of-flight evidence into the composer.

- *Labels, verbatim:* run C NOT CONVERGED (core split-half mean 0.850-0.918 against the 8-replicate floor 0.924)
- *Artifact:* `family-evidence-run-c.json (end of flight's)`

## 4. Coverage register, copied from ARCHITECTURE.md

Pete's standing rule: any result carries its coverage statement — the feasible set, the model's reach, the proposal's coverage, and every open gap named in the result's label. The register is reproduced here unchanged so that the draft and the architecture cannot drift apart. Status values are as recorded there.

| # | Stage | Gap | Kind | Effect | Status |
|---|---|---|---|---|---|
| G1 | End of flight | Commanded descent rates capped at 6,500 ft/min | reach | Holland-type and other rapid descents unreachable | open (EoF physics plan) |
| G2 | End of flight | Free flight at fixed CL, cannot unload (no 6-DOF pitch dynamics) | reach | uncontrolled push-over / dive states unreachable | open (6-DOF fit gate) |
| G3 | End of flight | Boeing system sequence (TAC, autopilot loss, RAT, APU) absent | reach | post-FE behaviour range narrowed | open |
| G4 | End of flight | No g-bounded push-over in the controlled family | reach | controlled rapid descents missing | open |
| G5 | Core | One-engine phase after takeover (core request 11) | reach | early asymmetric-thrust trajectories missing | open |
| G6 | End of flight | Impact attitude: flight-path angle stands in for pitch | reach | impact nature partly modelled | declared for pass 1 |
| G7 | End of flight | Holland H1/H2 not estimable (ESS 86–219 of 51.2M on core (b)) | coverage | two standard 00:19 options unestimable | open (aimed proposal after G1/G2) |
| G8 | End of flight | Family B onset before 22:41 vs core strata | coverage | possible implicit bound on B | open (EoF to state) |
| G9 | Core | Free stratum split-half not converged (run (b) 0.709 vs floor 0.896) | coverage | free-flight space under-resolved | run C pending |
| G10 | Drift | 16–25 % of impact weight not computed (drift node coverage) | coverage | composed areas depend on carry vs exclude (Pléiades 90 %: 254k vs 62k km²) | open (node extension B, after run C chain) |
| G11 | Core | Hand-off rows not linked to 18:01 route / early record | coverage (diagnostic) | trajectory trace-back before 00:11 approximate | open (core request 19) |
| G12 | Settling | Seabed resample drawn from flight + EoF weights only; composed weights concentrate on a few hundred rows | coverage | seabed PDF under drift/Pléiades not estimable for R600 BTO Only (ESS 368–865) | open (settling resample from composed weights) |
| G13 | End of flight | No structural limit, too little transonic drag rise: contact speeds near/above Mach 1 (A1 34 % >= 340 m/s on run C free) | reach (infeasible states produced) | impact energy/nature, hydro detectability, fragment fields | open (6-DOF drag calibration + breakup end state); pass 1 shows with/without rows > 1.25 VMO |
| G14 | Composer / EoF | Under 00:19 R600 BTO + Raw BFO, composed G and H fall below the 1,000-effective-parent floor (506–971 per seed); A1 keeps 8 effective rows under G | coverage | Raw-BFO composed products not estimable on run C | open (aimed resampling / larger hand-off for that option) |
| G15 | Core | Routes prior: only 14 of 48 routes distinct (core, per-route pilot) | prior defect | routes stratum (weight 0.024–0.027) and its convergence | RESOLVED 11 Oct: turn_backs overshoot rule, all 48 distinct (core); turn model now fly-by + leg tracking (runs H, hybrid) |
| G16 | Hydroacoustics (audit C4) | Deep-SUS source spectrum below the bubble frequency unknown to better than 4–17 dB (G&S 1971 valid ≤ ~1,000 ft; SUS at 2,000/3,000 ft) | reach | C4 absolute level verdict depends on source route (A FAIL, B PARTIAL) | declared-conditional (results/hydroacoustics-audit-sus-absolute.md) |
| G17 | Hydroacoustics | No band below 16 Hz calibrated by any deep source; none below 31.5 Hz at H01W | coverage | impact-marker bands (< 12.5 Hz) uncalibrated | open |
| G18 | Hydroacoustics (audit) | SUS sites A1–A5 and station H08N not scored (no audit paths); A11 not scorable absolutely (charge not 1.8 lb) | coverage | 5 sites × 2 shots unused | open (module: paths.py) |
| G19 | Hydroacoustics | No near-surface calibration source with known spectrum; SUS places the air9 tilt at the near-surface end but cannot split airgun directivity from coupling | reach | C6 condition (2) unmet | open |
| G20 | Core | Initial-Mach prior capped at 0.84 (Davey Table 8.2, 0.73–0.84); 777-200ER MMO is 0.87. Run H route 43 (MEKAR–SAMAK–ISBIX) posterior presses the cap (95 % point 0.838) | bound narrower than feasible (sourced to Davey, but the feasible set reaches MMO) | route-family evidence and shares | Mach 0.86 arm: route 43 −120.70 vs −120.56 (< 0.5 nat). Pete ruling 12 Oct ~00:20Z: early phase keeps 0.45–0.87 within 210–330 KCAS to 18:40; cruise after the old reversion point 0.70–0.87 within 210–330 KCAS in all strata (engine 3c4ceeb3); smoke running. CLOSES on smoke pass + run I |
| G21 | Hydroacoustics | H08N: Chagos Bank blocks every impact path in the model (K4) | reach | an H08N non-detection carries no information; labelled G-N1 | declared |
| G22 | Hydroacoustics | Ridge cutting the sound-channel axis (air7 → H01W, about 29 S 98 E): module TL about 49–55 dB too lossy, not fixed by N×2D (K5) | reach | path-specific; checked not to reach run C → H01W predictions | declared (G-N2) |
| G23 | Core | Route turn model: fly-over + direct-to (runs G and audit) against fly-by + leg tracking (run H, hybrid). The model change moves route ln Z by up to 7.6 nats and 00:19 latitude by about 0.7° | model reach | every route-family result before run H | RESOLVED: fly-by + leg tracking adopted (core 18:46Z); bank-angle and cap sensitivity pending |
| G24 | End of flight | Piloted descents (A2, B) flew straight: no en-route turns, search orbits or ditching pattern (EoF found it, 12 Oct) | reach | A2/B impact spread and the run H southward shift | Pete ruled the full turn model, no cap on turns; built for run I |
| G25 | End of flight | 00:19 two-factor cells below the 1,000 gate on run D-he: D3×C1 443, D3×C2-silent 233, D4×C2-silent 59; A1 under D4×C1 136 | coverage | Holland's Hypothesis 2 cell and the C2 cells | fix in run I: burst proposal aimed at every D×C cell + aimed pitch-down for A1 |
| G26 | Ocean drift | Western Australia non-recovery not modelled: the beaching boxes cover S1–S6 only; 'coasts outside every box carry no identification' (run A configs, brief §13 defers the WA term) | reach | absence of finds in WA cannot down-weight impacts whose debris would beach there | open; Pete raised its priority 12 Oct; every drift result labelled 'Western Australia non-recovery not modelled' |

Of 26 registered gaps: 20 open, 4 declared or declared-conditional, 2 resolved.

## 5. Open items

### 5.1 From ARCHITECTURE.md, copied unchanged

1. The wreckage-draw count per impact, pending agreement with searched areas.
2. The freeze of the shared breakup field — the same object as the `ImpactView` debris class — pending requirements from settling, drift and hydroacoustics.
3. Provisioning of bathymetry and full-depth ocean reanalyses on this machine.
4. Whether the end-of-flight entry point stays the fuel-exhaustion-window conditional once the fuel burn defect is fixed and the dry fraction rises.
5. **Whether drift and Pleiades are downstream of settling.** Both need the sink-versus-float partition, and so does settling, from the same element-class physics. One partition owned by settling is correct on rules 3 and 4 but makes two modules wait; independent partitions give two incompatible answers to one physical question. A third arrangement — settling delivers the float partition first, ahead of its sinking physics — would unblock drift without splitting the physics. See `results/impact-interface-requirements.md` §6. This changes the merge order, so it is Pete's ruling, not the architect's.
6. Where seafloor-depth lookup lives in the shared layer: hydroacoustics and settling both need it, from one bathymetry surface, never computed twice.

### 5.2 Raised by this draft

1. **The build-status table in `ARCHITECTURE.md` is out of date** (section 2.1). No status claim should be published from it until it is corrected. Posted as a recommendation in `coordination/PAPER.md`.
2. **Result claims without a recorded artifact.** Several claims in section 3 are traceable to a note but not to a run directory. The project's own rule is that numbers come from the artifact; a claim that cannot name one cannot go in the paper.
3. **One methods note could not be summarised.** `results/eof-impact-tau-method-oct11.md` — the impact dissipation duration method — was refused by a content filter during automated extraction. It was left out rather than worked around, so the dissipation duration τ is **absent from section 2** even though the architecture lists it as a required `ImpactView` field. It must be written into the draft by hand.
4. **No element is classified as a pure reproduction except the audit notes.** If the paper is to begin with the baseline reproduction, as agreed, the reproduction needs its own methodology subsection drawn from `results/davey-2016-reference.md` and `config/davey2016.toml`, not only from the audit of contradictions.
5. **Hydroacoustics, settling and ocean drift have no engine module** (section 2.1). Their status in the paper is SPECIFIED as integrated modules, whatever their analysis has produced.

## 6. References

Generated from `paper/CITATIONS-LEDGER.md` in the journal's Harvard style. Only entries whose use in the project could be traced to a file are listed here; the full library is in the ledger.

Andersen, A., Pesavento, U. and Wang, Z. J. (2005). Unsteady aerodynamics of fluttering and tumbling plates. Journal of Fluid Mechanics, 541, 65–90.

Andersen, A., Pesavento, U. and Wang, Z. J. (2005). Analysis of transitions between fluttering, tumbling and steady descent of falling cards. Journal of Fluid Mechanics, 541, 91–104.

Anderson (2018). Report on two shipwrecks found during the MH370 search. Western Australian Museum, for the ATSB.

Arons, A. B. (1954). Underwater explosion shock wave parameters at large distances from the charge. J. Acoust. Soc. Am., 26, 343–346. https://doi.org/10.1121/1.1907339.

Ashton, C., Shuster Bruce, A., Colledge, G. and Dickinson, M. (2015). The Search for MH370. The Journal of Navigation, 68, 1–22. https://doi.org/10.1017/S037346331400068X.

Blackman, D. K., de Groot-Hedlin, C., Harben, P., Sauter, A. and Orcutt, J. A. (2004). Testing low/very low frequency acoustic sources for basin-wide propagation in the Indian Ocean. J. Acoust. Soc. Am., 116, 2057–2066. https://doi.org/10.1121/1.1786711.

Blackman, D. K., de Groot-Hedlin, C., Orcutt, J. A. and Harben, P. E. (2004). Methods for Calibrating Basin-Wide Hydroacoustic Propagation in the Indian Ocean. Lawrence Livermore National Laboratory, UCRL-TR-207323. https://doi.org/10.2172/15011808.

Brown, P., McFadden, L., McCormack, D., Adams, M. and Vida, D. (2026). A search for hydroacoustic signals from bolides. Icarus. https://doi.org/10.48550/arXiv.2604.12723.

Carver, R. W. and Merose, A. (2023). ARCO-ERA5: An Analysis-Ready Cloud-Optimized Reanalysis Dataset. 22nd Conference on Artificial Intelligence for Environmental Science, AMS Annual Meeting. https://github.com/google-research/arco-era5.

Chamberlain, M. A. and others (2021). Next generation of Bluelink ocean reanalysis with multiscale data assimilation: BRAN2020. Earth System Science Data, 13, 5663–5688. https://doi.org/10.5194/essd-13-5663-2021.

Collins, M. D. (1993). A split-step Padé solution for the parabolic equation method. J. Acoust. Soc. Am., 93, 1736–1742. https://doi.org/10.1121/1.406739.

Davey, S., Gordon, N., Holland, I., Rutten, M. and Williams, J. (2016). Bayesian Methods in the Search for MH370. Springer. https://doi.org/10.1007/978-981-10-0379-0.

Donnelly, M. (2025). pyram 1.3.0: Python adaptation of the Range-dependent Acoustic Model (RAM). https://github.com/marcuskd/pyram. Accessed [DATE NOT RECORDED].

Duncan, A. J. and Dall'Osto, D. R. (2023). Long-range underwater acoustic detection of aircraft surface impacts–-the influence of acoustic propagation conditions and impact parameters. J. Acoust. Soc. Am., 154, A49. https://doi.org/10.1121/10.0022761.

Duncan, A. J. and Dall'Osto, D. R. (2023). The loss of an F35 fighter aircraft and the search for Malaysian Airlines flight MH370. https://acoustics.org/the-loss-of-an-f35-fighter-aircraft-and-the-search-for-malaysian-airlines-flight-mh370/. Accessed [DATE NOT RECORDED].

Duncan, A. J., Gavrilov, A. N. and McCauley, R. D. (2014). Analysis of low frequency underwater acoustic signals possibly related to the loss of Malaysian Airlines Flight MH370. Centre for Marine Science and Technology, Curtin University, CMST 1308, Report 2014-30.

Durgadoo, J. V., Biastoch, A., New, A. L., Rühs, S., Nurser, Aylmer J. G., Drillet, Y. and Bidlot, J.-R. (2021). Strategies for simulating the drift of marine debris. Journal of Operational Oceanography, 14, 1–12. https://doi.org/10.1080/1755876X.2019.1602102.

E.U. Copernicus Marine Service Information (2018). Global Ocean Physics Reanalysis (GLOBAL_MULTIYEAR_PHY_001_030). Mercator Ocean International. https://doi.org/10.48670/moi-00021. Accessed [DATE NOT RECORDED].

E.U. Copernicus Marine Service Information (n.d.). Global Ocean Waves Reanalysis (GLOBAL_MULTIYEAR_WAV_001_032), dataset cmems_mod_glo_wav_my_0.2deg_PT3H-i, version 202411. https://doi.org/10.48670/moi-00022. Accessed [DATE NOT RECORDED].

ESR and Dohan, K. (2021). Ocean Surface Current Analyses Real-time (OSCAR) Surface Currents - Final 0.25 Degree (Version 2.0). PO.DAAC. https://doi.org/10.5067/OSCAR-25F20. Accessed [DATE NOT RECORDED].

Field, S. B., Klaus, M., Moore, M. G. and Nori, F. (1997). Chaotic dynamics of falling disks. Nature, 388, 252–254. https://doi.org/10.1038/40817.

Francois, R. E. and Garrison, G. R. (1982). Sound absorption based on ocean measurements: Part I: Pure water and magnesium sulfate contributions. J. Acoust. Soc. Am., 72, 896–907. https://doi.org/10.1121/1.388170.

Francois, R. E. and Garrison, G. R. (1982). Sound absorption based on ocean measurements. Part II: Boric acid contribution and equation for total absorption. J. Acoust. Soc. Am., 72, 1879–1890. https://doi.org/10.1121/1.388673.

Gaspin, J. B. and Shuler, V. K. (1971). Source Levels of Shallow Underwater Explosions. Naval Ordnance Laboratory, NOLTR 71-160.

GEBCO Bathymetric Compilation Group 2026 (2026). The GEBCO_2026 Grid – a continuous terrain model for oceans and land at 15 arc-second intervals. NERC EDS British Oceanographic Data Centre NOC. https://doi.org/10.5285/4f68d5c7-45eb-f999-e063-7086abc036fa. Accessed [DATE NOT RECORDED].

Griffa, A. (1996). Applications of stochastic particle models to oceanographic problems. Stochastic Modelling in Physical Oceanography. Birkhäuser.

Griffin, D. A. and Oke, P. R. (2017). The search for MH370 and ocean surface drift – Part III. CSIRO Oceans and Atmosphere, EP174155.

Griffin, D. A., Oke, P. R. and Jones, E. M. (2017). The search for MH370 and ocean surface drift – Part II. CSIRO Oceans and Atmosphere, EP172633.

Griffin, D. A., Oke, P. R. and Jones, E. M. (2016). The search for MH370 and ocean surface drift. CSIRO Oceans and Atmosphere, EP167888. https://doi.org/10.4225/08/5892224dec08c.

Handley, W. and Lemos, P. (2019). Quantifying tensions in cosmological parameters: Interpreting the DES evidence ratio. Physical Review D, 100, 043504. https://doi.org/10.1103/PhysRevD.100.043504.

Hersbach, H., Bell, B., Berrisford, P., Hirahara, S., Horányi, A., Muñoz-Sabater, J., Nicolas, J., Peubey, C., Radu, R., Schepers, D., Simmons, A., Soci, C., Abdalla, S., Abellan, X., Balsamo, G., Bechtold, P., Biavati, G., Bidlot, J., Bonavita, M., De Chiara, G., Dahlgren, P., Dee, D., Diamantakis, M., Dragani, R., Flemming, J., Forbes, R., Fuentes, M., Geer, A., Haimberger, L., Healy, S., Hogan, R. J., Hólm, E., Janisková, M., Keeley, S., Laloyaux, P., Lopez, P., Lupu, C., Radnoti, G., de Rosnay, P., Rozum, I., Vamborg, F., Villaume, S. and Thépaut, J.-N. (2020). The ERA5 global reanalysis. Quarterly Journal of the Royal Meteorological Society, 146, 1999–2049. https://doi.org/10.1002/qj.3803.

Holland, I. D. (2018). MH370 Burst Frequency Offset Analysis and Implications on Descent Rate at End-of-Flight (author's accepted version). https://arxiv.org/abs/1702.02432v3. Accessed 12 October 2026.

Holland, I. D. (2018). MH370 Burst Frequency Offset Analysis and Implications on Descent Rate at End-of-Flight. IEEE Aerospace and Electronic Systems Magazine, 33, 24–33. https://doi.org/10.1109/MAES.2018.170048.

Iannello, V. (2018). End-of-flight simulations (web article; VERIFY title and URL from the archive snapshot).

IMOS (2026). Australian National Mooring Network passive acoustic observatories (Curtin University CMST loggers). https://imos-data.s3-ap-southeast-2.amazonaws.com/IMOS/ANMN/Acoustic/. Accessed [DATE NOT RECORDED].

Jeffreys, H. (1961). Theory of Probability. Oxford University Press.

Jensen, F. B., Kuperman, W. A., Porter, M. B. and Schmidt, H. (2011). Computational Ocean Acoustics. Springer. https://doi.org/10.1007/978-1-4419-8678-8.

Kadri, U. (2024). Underwater acoustic analysis reveals unique pressure signals associated with aircraft crashes in the sea: revisiting MH370. Scientific Reports, 14, 10102. https://doi.org/10.1038/s41598-024-60529-1.

Kadri, U. (2019). Effect of sea-bottom elasticity on the propagation of acoustic–gravity waves from impacting objects. Scientific Reports, 9, 912. https://doi.org/10.1038/s41598-018-37626-z.

Kadri, U., Abdolali, A. and Kirby, J. T. (2025). Acoustic-gravity quantum tunnelling analogy. J. Fluid Mech., 1018, A18.

Karney, C. F. F. (2013). Algorithms for geodesics. J. Geodesy, 87, 43–55. https://doi.org/10.1007/s00190-012-0578-z.

Kass, R. E. and Raftery, A. E. (1995). Bayes Factors. J. Am. Stat. Assoc., 90, 773–795. https://doi.org/10.1080/01621459.1995.10476572.

Law-Chune, S. and others (2021). WAVERYS: a CMEMS global wave reanalysis during the altimetry period. Ocean Dynamics, 71, 357–378. https://doi.org/10.1007/s10236-020-01433-w.

Lellouche, J.-M. and others (2021). The Copernicus Global 1/12° Oceanic and Sea Ice GLORYS12 Reanalysis. Frontiers in Earth Science, 9, 698876. https://doi.org/10.3389/feart.2021.698876.

Locarnini, R. A. and others (2024). World Ocean Atlas 2023, Volume 1: Temperature. https://doi.org/10.25923/54bh-1613.

Lock, R. C. (1964). The prediction of the drag of aerofoils and wings at high subsonic speeds.

Lumpkin, R. and Centurioni, L. (2019). Global Drifter Program quality-controlled 6-hour interpolated data from ocean surface drifting buoys. NOAA National Centers for Environmental Information. https://doi.org/10.25921/7ntx-z961. Accessed [DATE NOT RECORDED].

McDougall, T. J. and Barker, P. M. (2011). Getting started with TEOS-10 and the Gibbs Seawater (GSW) Oceanographic Toolbox. SCOR/IAPSO WG127.

Mearns, D. L. (1994). MV Derbyshire survey report. International Transport Workers' Federation.

Metz, D., Obana, K. and Fukao, Y. (2023). Remote hydroacoustic detection of an airplane crash. Pure Appl. Geophys., 180, 1343–1351. https://doi.org/10.1007/s00024-022-03117-6.

Minchin, S., Mueller, N., Lewis, A., Byrne, G. and Tran, M. (2017). Summary of imagery analyses for non-natural objects in support of the search for Flight MH370: Results from the analysis of imagery from the PLEIADES 1A satellite undertaken by Geoscience Australia. Geoscience Australia, Record 2017/013. https://doi.org/10.11636/record.2017.013.

Oke, P. R. and others (2013). Evaluation of a near-global eddy-resolving ocean model. Geoscientific Model Development, 6, 591–615. https://doi.org/10.5194/gmd-6-591-2013.

Poll, D. I. A. and Schumann, U. (2021). An estimation method for the fuel burn and other performance characteristics of civil transport aircraft in the cruise. Part 1: fundamental quantities and governing relations for a general atmosphere. The Aeronautical Journal, 125, 257–295.

Porter, M. B. (1992). The KRAKEN Normal Mode Program. Naval Research Laboratory, NRL/MR/5120-92-6920.

Rahimi, A. and Recht, B. (2007). Random features for large-scale kernel machines. Advances in Neural Information Processing Systems 20.

Reagan, J. R., Boyer, T. P., García, H. E., Locarnini, R. A., Baranova, O. K., Bouchard, C., Cross, S. L., Mishonov, A. V., Paver, C. R., Seidov, D., Wang, Z. and Dukhovskoy, D. (2023). World Ocean Atlas 2023. NOAA National Centers for Environmental Information. https://doi.org/10.25921/va26-hv25. Accessed [DATE NOT RECORDED].

Reagan, J. R. and others (2024). World Ocean Atlas 2023, Volume 2: Salinity. https://doi.org/10.25923/70qt-9574.

Roquet, F., Madec, G., McDougall, T. J. and Barker, P. M. (2015). Accurate polynomial expressions for the density and specific volume of seawater using the TEOS-10 standard. Ocean Modelling, 90, 29–43. https://doi.org/10.1016/j.ocemod.2015.04.002.

Spinoccia, M. (2017). MH370 Phase 1 150m Bathymetry datasets (GA-4421, GA-4422 & GA-4430). Geoscience Australia. https://pid.geoscience.gov.au/dataset/ga/100315. Accessed [DATE NOT RECORDED].

Stone, L. D., Keller, C. M., Kratzke, T. M. and Strumpfer, J. P. (2014). Search for the Wreckage of Air France Flight AF 447. Statistical Science, 29, 69–80. https://doi.org/10.1214/13-STS420.

Stone, L. D., Keller, C. M., Kratzke, T. M. and Strumpfer, J. P. (2011). Search Analysis for the Location of the AF447 Underwater Wreckage. Metron Inc., Reston, Virginia. https://bea.aero/fileadmin/uploads/tx_elyextendttnews/metron.search.analysis_01.pdf.

Sutherland, G. and others (2020). Evaluating the leeway coefficient of ocean drifters using operational marine environmental prediction systems. Journal of Atmospheric and Oceanic Technology, 37, 1943–1954.

Sutherland, G., Soontiens, N., Davidson, F., Smith, G. C., Bernier, N., Blanken, H., Schillinger, D., Marcotte, G., Röhrs, J., Dagestad, K.-F., Christensen, K. H. and Breivik, Ø. (2020). Evaluating the leeway coefficient of ocean drifters using operational marine environmental prediction systems. Journal of Atmospheric and Oceanic Technology, 37, 1943–1954. https://doi.org/10.1175/JTECH-D-20-0013.1.

Taylor, G. I. (1921). Diffusion by continuous movements. Proceedings of the London Mathematical Society, s2-20, 196–212. https://doi.org/10.1112/plms/s2-20.1.196.

Various Institutions (1965). International Miscellaneous Stations (FDSN network IM; IMS hydroacoustic station metadata). International Federation of Digital Seismograph Networks. https://doi.org/10.7914/vefq-vh75. Accessed [DATE NOT RECORDED].

Vincenty, T. (1975). Direct and inverse solutions of geodesics on the ellipsoid with application of nested equations. Survey Review, 23, 88–93. https://doi.org/10.1179/sre.1975.23.176.88.

Wessel, P. and Smith, Walter H. F. (1996). A global, self-consistent, hierarchical, high-resolution shoreline database. Journal of Geophysical Research: Solid Earth, 101, 8741–8743. https://doi.org/10.1029/96JB00104.

*67 of 105 library entries are listed; 38 could not be traced to a use in the repository and are held in the ledger pending a decision.*

## 7. What is not in this draft

1. **The section and word budget for the paper**, and the ranked list of results that can carry one paper. These wait on the survey of recent papers in the journal, which is running.
2. **The figure and table list.** Same dependency.
3. **The audit of where Holland's work enters the method**, requested by architecture.
4. **The proposed full draft of the paper.** It follows this document and is a separate deliverable, labelled PROPOSED on every page.
5. **Style notes.** `paper/STYLE-NOTES.md` is not yet written; the dissertation Pete supplied on 12 October 2026 is the source for it, and its printed page is its PDF page minus 14.
6. **The impact dissipation duration method**, for the reason in section 5.2 item 3.

---

*Generated 12 October 2026. Regenerate with `python build_citation_library.py && python build_reference_draft.py`. Every regeneration should state what changed and why, in `coordination/PAPER.md`.*
