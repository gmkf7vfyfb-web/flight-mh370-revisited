# End of flight — mission and master prompt

Supersedes `ISO Sept 28 Status/threads/master-prompts/end-of-flight.txt`, which remains correct on
physics and calibration and is stale on build status and evidence handling. Read `common.txt` in
that directory first for the four-stage architecture and the eight composition rules; they are
unchanged and binding.

This document is split deliberately into what is **stable** and what is **expected to evolve**.
Pete will add prior work and research as this progresses and may change the line of enquiry. That
is anticipated and is not a conflict: §2 is the contract and must not drift; §4 onward is the line
of enquiry and is expected to.

---

## 1. Mission

Establish the realistic uncertainty in what happened between the last reliable cruise state and
the aircraft reaching the sea — flight time after fuel exhaustion, distance, impact location,
impact energy and attitude — **without relying on unprovable assumptions**, and deliver an impact
probability distribution the downstream modules (settling, drift, hydroacoustics, searched areas)
can consume.

The module exists to produce an honest posterior, not to decide what happened. Simulations are for
learning physics, not for settling the question.

**Three arms, run and compared.** This is the experiment, not three separate products:

| | hand-off | onset of major descent | what it isolates |
|---|---|---|---|
| **V1a** | the filter's own stop epoch (00:11, continuing through 00:19) | flame-out-associated only | the best-sampled cruise-to-exhaustion case; nearly free, because the hand-off is built anyway |
| **V1b** | 22:41 (`m2241`) | flame-out-associated only — anticipatory support set to **zero** | against V1a: the checkpoint-and-sampling effect, with the physics held fixed |
| **V2** | 22:41 (`m2241`) | anticipatory, any time from the checkpoint onward, **plus** flame-out-associated | against V1b: the descent hypothesis, with the sampling held fixed |

The headline result is **how the impact PDF differs**, and what that implies for how defensible
cruise-to-exhaustion-then-uncontrolled-descent is against the evidence relative to the
alternatives.

### Why three arms rather than two, and what each comparison licenses

An earlier version of this prompt ruled that *both* versions must branch from 22:41, on the
grounds that V1-from-00:11 against V2-from-22:41 would differ in *where 00:11 was scored* — inside
the filter for one, inside the terminal stage for the other — as well as in the descent
hypothesis, so the difference in impact PDFs would not be attributable to the thing under test.
**That objection is correct and the remedy was wrong.** Forcing both arms through 22:41 discards
the best-sampled estimate we have and settles the attribution question by assumption instead of
measuring it.

The three-arm decomposition measures it. V1a against V1b isolates the checkpoint and the sampling
with the physics held fixed; V1b against V2 isolates the descent hypothesis with the sampling held
fixed. The cost is one extra terminal-stage sweep off a hand-off being built anyway, not another
filter run.

Three consequences for how you build and report:

- **Do not hard-code a checkpoint.** The descent-onset latent's support is a config-settable
  interval, and *empty support* — flame-out-associated onset only — must be a legal setting. That
  is what makes V1b V2 with one switch thrown, which is the cleanest nesting a hypothesis test can
  have.
- **The hand-off epoch is a config choice, not a property of the module.** The configurable filter
  stop epoch and "bursts after the stop" scoring are already built. V1a and V1b differ only in
  which epoch the hand-off was taken at.
- **If V1b has not been run, say what the V1a-against-V2 difference does and does not establish.**
  It is reportable as "the impact PDF differs by X between these two configurations". It does not
  license "X is caused by the descent hypothesis". Only the third arm licenses that sentence.

---

## 2. The contract — stable; changes need architecture review

1. **Return likelihoods, never posteriors.** Declare whether yours is on an absolute scale.
2. **Each observation is used exactly once per run**, with declared IDs. List them.
3. **All impact-level modules consume the same impact samples.** Never smooth privately over
   impact location: the product of separately smoothed likelihoods is not the smoothed product.
4. **Likelihoods are smooth, with explicit model error. No floors.** NaN means "not computed", not
   "impossible". Cover the prior's support or refuse.
5. **Be accurate where the other evidence has mass**, roughly 30–40°S along the 7th arc, not only
   near your own peak.
6. **Measure ESS and split-half replicate agreement; report unconverged as unconverged.** The fix
   is the sampler, never the smoothing. Use `skill("mh370-run-reporting")` for the conventions.
7. **Settle discrete choices by evidence, or carry them as declared alternatives with priors** and
   report per alternative. Never fixed-weight averages of normalised maps.
8. **One synthetic-recovery test plus hand-computed fixtures.**
9. **Piloted and unpiloted are treated without preference.** Neither is a default. Family priors
   are explicit; results are reported per family before any combination.
10. **Descent physics lives in this module**; the measurement model lives in `satcom`; composition
    lives in the composer. Do not reimplement a measurement model here.

### Interface

The `Terminal` trait — `families`, `latent_columns`, `takeover_time`, `descend`. Impacts are
emitted as `ImpactView`. `mh370 terminal <run-dir> <config> [overrides] <out-dir>` re-runs this
stage alone from a stored `handoff.npy`, which is what makes variant sweeps cheap.

`ImpactView` carries parent, time, position, ENU velocity, flight-path angle, mass, total and
vertical kinetic energy, descent family, takeover time/place/altitude, mode, alternative and module
latents. **Three additions are ruled in and this module emits all three**: attitude at impact
beyond flight-path angle (at least heading and bank), the dissipation duration τ for the
hydroacoustic source term, and a debris class. They are required because the module's stated
purpose is the position *and attitude* of arrival, the energy, the *duration* of the surface-impact
event, and outputs that seed drift and hydroacoustics.

What you emit is not the same as what a consumer conditions on. Settling's first pass conditions
its breakup families on vertical and total kinetic energy plus flight-path angle only, carrying
attitude and τ through unused, because sink rate spans two orders of magnitude of seabed
displacement and attitude at impact comes out of the least-constrained part of the dynamics. **Emit
them anyway** — a sensitivity test that the fields make possible is cheap; retrofitting the fields
later is not.

Granularity is settled: `ImpactView` carries a debris **class**, and settling generates the
object ensemble from class plus energy and attitude. Do not make the impact sample
variable-length.

Two further hooks exist, stubbed and documented, with no physics behind them yet: a debris-class
output and a **sink-versus-float** flag. Both are deferred by decision, and both are expected to be
a light lift once the element classes exist, which is the whole reason the hooks go in now.
Per-engine state and configuration come later, after the single-flame-out version works.

### Scope and reporting rules, from `engine/AGENTS.md`

These are not advisory. `make scope H=end-of-flight` fails if the branch touches anything outside
`hypotheses/end-of-flight/`, and it must pass before you hand back: no core crates, no `config/`,
no `report/`, no `README.md` or `status.md`. Use your own `run.toml` inside your directory rather
than adding to `config/`. Changing the hook API in `crates/hypothesis` is a core change.

Write **no new `.md` files inside `engine/`** — that tree allows exactly three, `README.md`,
`AGENTS.md` and `status.md`, and forbids all other reports there. The assumptions, their sources
and how they enter the estimate belong in the `lib.rs` doc comment, with at least one test against
an independently computed value. Status goes in `hypothesis.toml`: a `status` field and a one-line
`summary` quoting the numbers. Longer write-ups go one level up, in the project's `results/`
directory, which is a sibling of `engine/` and is where the analysis notes live.

Iterate with `make smoke H=end-of-flight`, about a minute, code paths only. **`make hypothesis
H=end-of-flight` runs at full scale** — that is not a smoke test and is not yours to start
unilaterally.

---

## 3. Build status — what exists now that did not when the previous prompt was written

Correcting that prompt, which told you to work against a flat flame-out prior and to raise the
start-up-offset model as a core request. Both are now done.

| thing | status |
|---|---|
| Fuel model, Boeing-calibrated tables, endurance proposal, exhaustion-time term | **built**, 16 of 51 configs exercise it, and **a burn defect found 6 Oct**: a failed flow lookup returned without burning, for 19.55% of every trajectory on average. Fix written, Boeing calibration re-validated, re-run pending. Absolute fuel states from earlier runs are not usable — see §5 |
| `Terminal` trait, `handoff.npy`, `terminal.rs`, `impacts.rs`, `mh370 terminal` | **built** |
| `TerminalConfig.options` — named sets of bursts after the stop, each one log-likelihood column computed from the **same** children | **built** |
| `TerminalConfig.bfo_models` + `satcom::FinalBfoModel` (`NoOffset`, `Inflated{sd_hz}`, `StartupOffset{second_hz, first_minus_second_hz, points}`) | **built, with tests** |
| Configurable filter stop epoch; "bursts after the stop" scoring | **built** |
| `dynamics.bfo_vertical_rate` | **built and on**; inert in cruise because only ~0.7% of flight is in a level change — which is exactly why a *sustained* descent is needed for it to matter |
| Annealed-SMC tempering at named epochs | **built**; six-epoch configuration under test |
| The EoF **model** | **does not exist.** `hypotheses/arc-kernel` is plumbing whose own docs say "not a model"; its impact energies are NaN |
| Stage-4 composer | **not built**; `main.rs` rejects `[[compose]]`. Until it exists, use `mh370 evaluate` on an impacts file |

So: build the model, not the interface.

---

## 4. Version 2 — the deliberate-descent conditional hypothesis

### Onset

Separate three things rather than enumerating flat families: **descent initiation**, **propulsion
state**, **subsequent control**.

Initiation has two mechanisms, both sampled:

| mechanism | treatment |
|---|---|
| **Anticipatory planning** | onset when *estimated remaining endurance under continued cruise* falls below a sampled threshold |
| **Fuel-cue response** | onset at a modelled low-fuel cue, with uncertainty in recognition and response time |

**Trigger on predicted endurance, never on realised flame-out.** Defining onset as "actual
flame-out minus an hour" is circular and assumes foreknowledge no crew had. Compute remaining
endurance continuously from the fuel state *under continued cruise*, trigger on that, and let the
actual flame-out emerge from the resulting trajectory.

A candidate cue with legitimate provenance: an FAA rulemaking records the 777 `FUEL QTY LOW`
caution appearing below 4,500 lb (~2,040 kg) **per main tank**. Compute what that corresponds to in
time from our own fuel tables, including imbalance and unusable fuel — do not substitute a nominal
burn rate.

### Onset support and the checkpoint

With our configured anticipated exhaustion of 00:17:30 UTC, a 22:41 checkpoint gives a ~96-minute
onset window, covering the 60- and 90-minute alternatives. **A 120-minute window begins at 22:17:30
and requires the 21:41 (`m2141`) checkpoint instead.**

Making the checkpoint *be* the earliest permitted onset removes an arbitrary horizon, but keep the
diagnostic: **if supported trajectories accumulate against the checkpoint boundary, the boundary is
influencing the answer** and the run must be repeated from 21:41. Report where the supported onset
mass sits relative to the boundary, every time.

Sample the early part of the window adequately even if the prior puts most mass near exhaustion,
and describe every result as conditional on excluding major descents before the checkpoint.

### Descent profiles

A constant descent is **sampled, never assumed**. The envelope must include:

- continuous descents at rates generated from aircraft state and configuration;
- emergency-descent-style upper segments (idle thrust, speedbrakes, airspeed toward MMO/VMO subject
  to damage and turbulence limits) **followed by a separate transition** — a rapid descent to
  breathable altitude is not a complete sea-level approach;
- level-offs and changes of descent rate within the envelope, **including 10,000 ft and 4,000 ft**.
  10,000 ft is the operationally meaningful emergency level-off; 4,000 ft is included because it
  appears in the recovered simulator data. Cite the simulator only as the *reason for including*
  the altitude, never as support for it having been flown — that data's provenance is contested and
  it is evidence about what was rehearsed, not what happened;
- randomly sampled trigger points and profile shapes, so the ensemble is not a handful of
  hand-chosen archetypes;
- substantial lower-altitude flight as a possibility: **an hour between onset and impact need not
  mean an hour descending.**

Reference idle-thrust rates below 20,000 ft, for sanity-checking our own model rather than as
prescription: ~2,200 ft/min clean at 0.84M/310 kt and ~5,300 with speedbrakes; ~1,400/3,300 at
250 kt; ~1,000/2,300 at VREF30+80; roughly 3 NM per 1,000 ft lost. Ditching guidance gives
200–300 ft/min on final before flare and advises against burning fuel to a critical minimum,
because available thrust improves touchdown control. **See §9 on how to use these numbers.**

### Propulsion and control

Treat propulsion as an evolving state: two engines producing thrust, one, or neither. Keep **fuel
remaining** distinct from **power available** — fuel can be present but inaccessible, isolated, or
unavailable to a particular engine.

Within either initiation branch allow: control maintained through an attempted ditching; control
maintained then lost; no effective intervention during the terminal descent; and upset followed by
recovery and renewed control — which must be *dynamically demonstrated*, including sufficient
altitude, not merely asserted.

**Distinguish attempted ditching from achieved low-speed water contact.** The first is a control
objective, the second an outcome. Defining "controlled ditching" by a successful low vertical speed
silently discards every failed attempt — which is exactly the population the hypothesis must be
tested against.

**Vocabulary.** The words used in discussion map onto the three axes rather than forming a fourth
list, and the mapping belongs in a doc comment so nobody re-invents a flat family set:
"controlled" and "uncontrolled" are the *control* axis; "arrested" and "unarrested" describe
whether a developing upset or descent was checked, which is also the control axis; "phugoid" is
an *outcome* of a particular propulsion-and-control combination, not a family of its own, and it
appears in the tests (period ≈ π√2·V/g) and in the pitfalls (phugoids climbing above the 43,000 ft
weather grid). If a term in discussion does not map onto initiation × propulsion × control, raise
it rather than adding a family.

Post-flame-out systems logic is unchanged: RAT deploys, APU starts in about a minute, secondary
flight-control mode with no envelope protection or thrust-asymmetry compensation and degraded yaw
damping, no autopilot on RAT power, flaps unresponsive to the handle on RAT power alone, residual
rudder random. Outcomes depend mostly on starting asymmetry — trim, electrical configuration, pilot
input — rather than aerodynamic detail, so make those explicit uncertain inputs.

---

## 5. Fuel coupling — not optional

A trajectory that fitted 00:11 under cruise assumptions **must be re-scored, not extended**.
Descent changes fuel burn and therefore actual flame-out time; it changes horizontal speed, wind
exposure and distance covered; it changes altitude, which enters the BTO geometry; and it changes
vertical velocity, which enters the BFO. An idle descent can save fuel over that segment while
subsequent low-altitude powered flight spends the saving — the net must be computed, not assumed.

Position, altitude, speed, mass, fuel state, engine state and configuration evolve jointly. This is
why a descent cannot be bolted onto a cruise-only posterior.

**Single flame-out event for the first working version.** Per-engine flame-out (right engine first,
gap unpublished, single-engine phase never modelled) is agreed in principle and comes after, so its
effect on the impact PDF can be measured rather than assumed.

### Three time resolutions, and only one of them is yours

Keep these separate; running them together has already caused one wrong diagnosis.

1. **The core filter's manoeuvre integration step** is 5 s, against the book's 1 s on printed
   p. 59. It is a known fidelity gap in the cruise dynamics, its cost is unmeasured, and **it does
   not constrain you.** The end-of-flight stage runs its own integration.
2. **Your own step is a parameter, and it must be able to go fine through the flame-out
   transition.** Thrust loss, RAT deployment and the APU start all happen inside about a minute;
   a step chosen for cruise will smear them. State the step you used with every result.
3. **The stored exhaustion-time column in `final.npy` is `float32`**, whose unit in the last place
   at 1.394 × 10⁹ is exactly 128 s. So the recorded flame-out time is quantised at 128 s, and only
   a handful of slots carry probability. **Derive flame-out time inside this stage from the handed
   -off fuel state; do not read the stored column.** That keeps the quantity at the resolution the
   physics was integrated at. If the hand-off turns out not to carry fuel state at adequate
   precision, that is a core request — raise it, do not work around it.

### The seed is provisional, and you must say so

`6temper-realloc` is the current best core run and the natural seed. Its **absolute fuel numbers
are not usable**: `results/fuel-burn-gap.md` records a defect in which `Aircraft::burn_fuel`
returned without burning anything whenever the flow lookup failed, for 19.55% of every trajectory
on a mass-weighted average, so the dry fraction, the mean fuel remaining and anything conditioned
on exhaustion are artefacts of that defect rather than results. A fix has been written and the
Boeing Appendix 1.6E calibration survives it, but the re-run is not yet done.

Consequences while that is true: do not quote a dry fraction or a fuel-remaining figure from that
run; treat any flame-out-conditioned subset as a **test fixture rather than a scientific result**;
and expect the dry fraction to rise substantially once the fix lands, which will make conditioning
on exhaustion select much less strongly than it appears to now. Re-derive before you report.

---

## 6. The log-on at 00:19:29

The log-on is **one observation, used once**, through a flame-out → APU start → SDU log-on lag
likelihood. ATSB gives roughly 60 s for the APU and 60 s for the SDU; the archive's
`systems_timing.rs` used Erlang(8, 14.875 s), mean 119 s, which was analyst-declared and should be
treated as a parameter to question rather than a constant.

**Whether the log-on was caused by fuel exhaustion at all is a declared alternative.** This bites
hardest on the powered branches: a branch cannot simultaneously require dual-engine fuel exhaustion
to explain the log-on and allow engines still producing thrust. Each branch carries an explicit
mechanism for the power interruption — and "some other outage" is not a mechanism, it is a
residual. If a branch has no mechanism, say so and let it be penalised.

The R600 time is 00:19:29.416, not .000; the difference matters for BFO in a rapid descent.

---

## 7. The 00:19 and 00:11 evidence sweep

**Do not pick an interpretation.** The data are questioned, so sweep the full range and report the
magnitude of the uncertainty across it. This is already implemented, as two orthogonal axes.

**Axis 1 — `[[terminal.options]]`: which bursts to score.** Each option names observation IDs of
bursts after the stop and becomes one log-likelihood column of `impacts.npy`, **all computed from
the same children**. Required options:

- `none` — score nothing after the stop. This **is** the held-out case, and it makes every later
  burst a prediction rather than a fit.
- `m0011` — 00:11 BTO and BFO only.
- `m0011+m0019a`, `m0011+m0019b`, `m0011+both` — the 00:19 bursts singly and together.
- The R1200 BTO at 00:19:37 is anomalous; the usable set is R600 BTO, R600 BFO, R1200 BFO.

**Where 00:11 is scored differs by arm, and that is the point.** In V1a it is scored inside the
filter, by a population carried through that epoch with tempering. In V1b and V2 it is scored
inside the terminal stage, off a hand-off that is resampled and spawns children. Declare which,
per arm, in every result. The V1b-against-V2 comparison is attributable because both score it in
the same place; the V1a-against-V1b comparison is the one that *measures* what that difference is
worth.

The risk there is Monte Carlo, not physics. The terminal stage does not carry the filter's
population forward, and 00:11 sets the autopilot-mode mixture at roughly 20:1 on a problem that is
not well sampled at current budgets — so the relative magnitudes are unknown and must not be
guessed. **First smoke test, before any end-of-flight run: measure the terminal stage's effective
sample size at 00:11 at whatever hand-off and child counts you intend, and compare it against what
the filter achieves at that epoch.** Choose the counts from that measurement rather than from the
illustrative values in `config.rs`.

**Axis 2 — `[terminal.bfo_models]`: how to interpret them.** Declared as the alternative
`final-bfo-model` with a prior each, marginalised jointly across modules:

- `NoOffset` — raw, as observed, cruise measurement model.
- `Inflated { sd_hz }` — the measurement is suspect; widen it rather than reject it.
- `StartupOffset { second_hz, first_minus_second_hz, points }` — a **uniform prior over the
  start-up offset**: the second burst's offset over a range, the first larger by a further range
  from one shared start-up event, integrated by Gauss-Legendre quadrature.

The `StartupOffset` form is why this design is preferred to applying a published bias estimate:
**Holland's reading is the degenerate special case** of a narrow range centred on his values, so the
sweep contains it without ever selecting it. The implemented test uses `second_hz: [17, 130]` and
`first_minus_second_hz: [0, 6]`. **Those bounds need a sourced justification before they carry a
result** — establish where they came from, or re-derive them, and record it.

The cross product of the two axes is the sweep. Report impact PDF, impact area, energy and ESS per
cell, and report the **spread across cells** as the honest statement of what the 00:19 data can and
cannot support.

### Two things to state explicitly in the method

- **For the planned-descent test, no BFO bias excursion is assumed.** This is not neutral: it forces
  the 00:11 BFO to be explained by geometry and vertical rate, which is what *admits* the descent
  reading. The assumption therefore favours the hypothesis under test, so report fit and impact-PDF
  sensitivity under both it and its alternative, and name the pairing a conditional rather than a
  finding.
- **00:11 alone cannot discriminate a descent.** The sensitivity is about 17.5–17.8 Hz per
  1,000 ft/min, so a ~1,100 ft/min descent and a ±20 Hz bias excursion give the same signature, and
  00:11 is a single value rather than a pair.
  **Which arc the figure 17.50 belongs to is DISPUTED and must be settled before it reaches the
  paper.** The project previously recorded 17.50 Hz per 1,000 ft/min at the 00:11 geometry
  (38.16°S 88°E, satellite elevation 38.8°). The end-of-flight session, computing from
  `data/satellite-ephemeris.csv` with the engine's own `UPLINK_HZ` and `SPEED_OF_LIGHT_KM_S`, gets
  17.81 at the 00:11 arc (BTO 18,040 µs) and 17.52 at the 00:19a arc (BTO 18,400 µs), and reports
  the value as nearly constant along each arc — 17.800–17.813 from 30°S to 40°S at 00:11,
  17.515–17.528 at 00:19a — because the BTO fixes the slant range and hence the elevation angle.
  The two computations disagree by 1.8% on the attribution, not on the physics. The substance of
  the argument above survives either way (a ±20 Hz excursion matches 1,123 ft/min at 00:11 against
  1,143 at 00:19). **`crates/satcom` is core-owned, so the core session settles this**; until it
  does, quote the range rather than the single figure, and cite neither attribution. Yet 00:11 sets the autopilot-mode mixture at roughly
  20:1. So scoring 00:11 mostly re-weights modes, and the descent discrimination lives in the 00:19
  pair — whose 184 Hz step in 8 s is about nine times the largest bias excursion in Davey's own
  Fig. 5.4, and whose interpretation is exactly what is contested. State this tension as a result of
  the study, not as a late discovery.

---

## 8. Physics, calibration and sampling

Physics and calibration carry over from the previous prompt and are not repeated in full. The
essentials: Poll–Schumann B772 point-mass energy budget (clean (L/D)max 20.8–21.4 at 174 t against
Boeing's ~20.7:1 from the SIR App 1.6E driftdown); windmilling-engine and RAT drag increments as
uncertain parameters via ESDU methods, there being no public Trent 892 figures; drag-rise and pitch
above M0.87 shaped from NASA CRM data and **labelled extrapolated**, as every model including
Boeing's is beyond M0.87–0.91; MMO 0.87 from the type certificate. Calibrate against the 10 Boeing
engineering-simulator runs (1 Hz X/Y/altitude only; targets phugoid period, bank growth, time to
15,000 fpm, distance) and against Boeing's published range and endurance.

**Sampling adequacy is the thing most likely to sink this.** The old runs collapsed to 1–4 effective
samples with both BFOs. A defensive mixture of plain and targeted proposals with exact importance
weights is required, and the weighting rules are not optional:

- a parent's weight is **split** across its descendants; creating more descendants must never create
  more probability;
- correct for deliberately oversampled families or onset intervals;
- retain family evidence *before* normalising any within-family map;
- preserve parameters shared between the common history and the terminal trajectory — fuel state and
  the correlated navigation and BFO-bias uncertainties especially;
- validate the modular result against a smaller joint-filter calculation. This is the check that
  branching from a checkpoint has not changed the conditioning.

Equal Monte Carlo allocation across families is a **computational** choice, not a statement of equal
prior probability. Say which is which.

---

## 9. Source provenance

Some operational descent figures in circulation come from mirrored copies of copyrighted manuals
(777 FCTM, operator QRHs). **Use the values as modelling parameters with a declared sensitivity; do
not cite the mirrors.** A *Journal of Navigation* paper cannot rest on an unauthorised copy. If a
reviewer presses for provenance the legitimate routes are Boeing's published performance data, the
SIR appendices we already hold, or obtaining the manual through proper channels. Record in the
methods that these are modelling choices consistent with published operational practice.

The FAA/CASA rulemaking (fuel caution threshold) and Holland's arXiv paper are citable. ATSB and
Malaysian SIR material is citable — and is evidence to be weighed, not fact: the ATSB's own flap
analysis is qualified as "not fully conclusive" and is contested in the literature.

---

## 10. Deliverables

1. The calibrated open-baseline aerodynamic model, with its calibration report against the Boeing
   runs and the published range and endurance.
2. V1a, V1b and V2 as config-gated arms, with the hand-off epoch and the descent-onset support
   both set by config and empty onset support a legal setting.
3. The evidence sweep of §7 as a sensitivity page per option × BFO model × family: impact area
   (50/90/99%), distance from flame-out and from the 7th arc, impact time, total and vertical energy,
   and ESS with the population beside it.
4. **The headline comparison: how the impact PDF differs across the three arms**, reported as the
   two attributable differences rather than one — V1a against V1b for the checkpoint and sampling,
   V1b against V2 for the descent hypothesis — with the onset-mass boundary diagnostic, the
   terminal-stage ESS at 00:11 beside the filter's, and a statement of what each difference does
   and does not establish.
5. Core requests for the missing `ImpactView` fields.
6. The tests of §11.

## 11. Tests

Ballistic energy conservation. Level-flight equilibrium. BFO vertical-speed sensitivity against a
finite difference. One synthetic-recovery test: generate the data from a known descent and check
coverage. Plus hand-computed fixtures.

**Two of these were stated loosely in earlier versions and are corrected here, because asserting
them as written would have asserted a ten per cent error in each case.**

- **Phugoid period.** Lanchester's closed form π√2·V/g assumes **constant density**. Under the real
  ISA gradient the same equations give a period about 10% shorter, because climbing into thinner
  air removes lift and stiffens the oscillation. So test the closed form against a **frozen
  atmosphere**, and record the ISA figure separately rather than asserting agreement with it.
- **Still-air glide distance.** `altitude × L/D` is exact only in the energy-height form
  `R = (L/D)·(E₀ − E_f)` with `E = h + V²/2g`. From 35,000 ft the altitude term is 93.7 NM and the
  kinetic energy traded into denser air adds 9.7 NM, giving 103.4 NM. Test the energy-height form.

Both corrections must be carried into the paper's methods in these terms, not quietly fixed in the
code.

## 12. Pitfalls

- The old flame-out time came from a fuel anchor (00:11:19) that contradicted the log-on.
- Best glide or fixed trim produces ditching-like impacts about 100 NM out — so a ditching-like
  impact is **not** evidence of a ditching.
- Phugoids climbed above the 43,000 ft weather grid. If needed, request a grid to ~60,000 ft and past
  01:00 as a core request.
- 95th-percentile airspeeds of 362–443 m/s in the old runs were unphysical.
- Do not let the model be built around the 00:19 values. They are scored, not assumed.
- Do not import Holland's descent-rate bounds as a constraint. They are conditional on the transient
  assumption this project declines to treat as established, and importing them would kill the
  deliberate-descent branch by assumption rather than by evidence.

## 13. Out of scope for now, by decision

- **Debris-configuration evidence** (flap and flaperon position, debris energy class). Agreed to come
  *after* a stable, convergent EoF dynamics and satellite-evidence model exists; it is a separate
  module in the architecture. When it arrives, note that it is contested on both strands: the ATSB's
  retracted-flap finding is qualified and disputed, and the absence of buoyant cabin material is
  confounded by detection bias. It enters as a likelihood with explicit model error and declared
  alternatives, never as a veto.
- **Per-engine flame-out.** After the single-event version works.
- **Paid simulator options.** Confirmed: build and test the open baseline first, and treat a
  commercial simulator as a validation target rather than as the generator. Revisit then — 4–8
  hours in a rented Level-D 777-200ER simulator with written publication rights, or X-Plane 12
  Professional with the FlightFactor 777-200ER for scripted desktop exploration.
- **Sink-versus-float prediction** as a secondary input to the drift module. Deferred, hook
  present. It is the natural output of the same element-class physics settling needs, so it is
  expected to be a light lift once those classes exist.
- **An implosion event at depth** as a hydroacoustic prediction. Deferred to keep the first pass
  simple, and it belongs to settling rather than here, but it is in the queue deliberately: a
  flooding section imploding at depth would produce an acoustic event *tens of minutes* after the
  7th arc rather than at it, which is a timing signature nothing else in the evidence set
  provides.

**Both deferred items above are to be put back in front of Pete once a stable first pass exists.**
That is an instruction, not a note: he asked to be reminded rather than to have them quietly
dropped.
