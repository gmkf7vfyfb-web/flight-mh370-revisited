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

**Two versions, run and compared.** This is the experiment, not two separate products:

| | onset of major descent | what it represents |
|---|---|---|
| **V1** | flame-out-associated only | cruise continues to engine failure, then descent; the altitude and Mach sampling already implemented still applies |
| **V2** | anticipatory, any time from the checkpoint onward, **plus** flame-out-associated | a deliberate descent commenced before exhaustion, in preparation for a terminal event |

The headline result is **how the impact PDF differs between them**, and what that implies for how
defensible cruise-to-exhaustion-then-uncontrolled-descent is against the evidence relative to the
alternatives.

### A correction to the obvious design, and it matters

The tempting arrangement is V1 branching from the existing 00:11 posterior and V2 from 22:41.
**Do not do that.** The two would then differ in *where 00:11 was scored* — inside the filter for
V1, inside the terminal stage for V2 — as well as in the descent hypothesis, and the difference in
impact PDFs would not be attributable to the thing under test.

**Both versions branch from the same 22:41 (`m2241`) checkpoint**, score the same observations in
the same place, and differ only in the support of the descent-onset latent. V1 is then V2 with the
anticipatory branch switched off, which is the cleanest nesting a hypothesis test can have. One
filter run to 22:41 serves both.

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
latents. **It is missing fields the downstream modules need** — attitude beyond flight-path angle,
the dissipation duration τ for the hydroacoustic source term, a debris class, and later per-engine
state and configuration. Raise these as core requests; do not work around them.

---

## 3. Build status — what exists now that did not when the previous prompt was written

Correcting that prompt, which told you to work against a flat flame-out prior and to raise the
start-up-offset model as a core request. Both are now done.

| thing | status |
|---|---|
| Fuel model, Boeing-calibrated tables, endurance proposal, exhaustion-time term | **built and validated**; 16 of 51 configs exercise it |
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

Because both versions branch from 22:41, **00:11 is scored in the terminal stage in both**, which is
what keeps the V1/V2 comparison attributable.

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
- **00:11 alone cannot discriminate a descent.** At that geometry the sensitivity is 17.50 Hz per
  1,000 ft/min, so a ~1,100 ft/min descent and a ±20 Hz bias excursion give the same signature, and
  00:11 is a single value rather than a pair. Yet 00:11 sets the autopilot-mode mixture at roughly
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
2. V1 and V2, both branching from 22:41, as config-gated families.
3. The evidence sweep of §7 as a sensitivity page per option × BFO model × family: impact area
   (50/90/99%), distance from flame-out and from the 7th arc, impact time, total and vertical energy,
   and ESS with the population beside it.
4. **The headline comparison: how the impact PDF differs between V1 and V2**, with the onset-mass
   boundary diagnostic, and a statement of what the difference does and does not establish.
5. Core requests for the missing `ImpactView` fields.
6. The tests of §11.

## 11. Tests

Ballistic energy conservation. Level-flight equilibrium. Phugoid period ≈ π√2·V/g. Still-air glide
distance = altitude × L/D. BFO vertical-speed sensitivity against a finite difference. One
synthetic-recovery test: generate the data from a known descent and check coverage. Plus
hand-computed fixtures.

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
- **Paid simulator options.** Revisit when the open baseline is built and tested: 4–8 hours in a
  rented Level-D 777-200ER simulator with written publication rights, or X-Plane 12 Professional with
  the FlightFactor 777-200ER for scripted desktop exploration.
