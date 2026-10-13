# End of flight — mission and master prompt

**Version 7.1, 13 October 2026** (7.1 adds only the expertise paragraph in §1, at Pete's instruction). **Version 7, 13 October 2026.** Revises version 4 of 7 October against the audit of run I and
run-i-dive (`results/eof-audit-2026-10-13.md`, `results/eof-audit-pushover-addendum.md`) and the
independent literature pass (`results/eof-published-benchmarks.md`). Fourteen changes, listed in §0. Changes M and N correct factual errors — M one carried by versions 1 to 5, N one introduced by version 5 itself.
Version 4 was six days stale by the time the first full sweeps were reviewed and told a reader the
model did not exist; §3 is now updated per sweep rather than per revision.

Supersedes `ISO Sept 28 Status/threads/master-prompts/end-of-flight.txt`, which remains correct on
physics and calibration and is stale on build status and evidence handling. Read `common.txt` in
that directory first for the four-stage architecture and the eight composition rules; they are
unchanged and binding.

This document is split deliberately into what is **stable** and what is **expected to evolve**.
Pete will add prior work and research as this progresses and may change the line of enquiry. That
is anticipated and is not a conflict: §2 is the contract and must not drift; §4 onward is the line
of enquiry and is expected to.

---

## 0. What changed in version 5

Fourteen changes. A–C alter what the module is obliged to produce; D–H close places where a prose
requirement in version 4 was silently not honoured; I–L are additions from the audit and the
literature pass. Nothing was removed: §2's original ten rules, §5's fuel-coupling argument and its
case against conditioning on flame-out, §6's log-on treatment, §7's two sweep axes, §9's provenance
discipline and §11's two corrected tests were all honoured and stand as written.

| | change | where |
|---|---|---|
| A | build status rewritten and made a per-sweep obligation | §3 |
| B | the three arms become an acceptance condition, with what a V1a-only sweep may claim | §10.2 |
| C | the onset-boundary diagnostic becomes a gate with a statistic, a place and a threshold | §4 |
| D | level-off altitudes and sustained low-altitude flight become bounds with reported statistics | §4 |
| E | all four control outcomes in every family; weights stated per family; zero weights justified | §4 |
| F | **new rules 11 and 12**: a support change is logged and held-out-revalidated; the silent-exclusion review runs before every sweep | §2 |
| G | **new test 6**: prior recovery under the importance correction, reported per run | §11 |
| H | weight concentration reported beside ESS, per seed and per stratum | §2.6 |
| I | three emission rules: in-sample not sidecar, NaN not placeholder, energy partition declared | §2 interface |
| J | the uncontrolled-arm calibration gate is defined, with what may not be quoted while unpassed | §8 |
| K | four pitfalls added, including the Boeing-against-00:19 contradiction and the fit-failure asymmetry | §12 |
| L | the ordering — simulate, then test, never shape — leads the mission | §1 |
| M | **correction**: the two-engine flame-out structure is already built; the deferral narrows to asymmetric dynamics and first-flame-out emission | §5, §13, §10.9 |
| N | **correction**: the level-flight requirement is met on the fraction statistic, and the level-off altitude finding is withdrawn as unverified | §4 |

**A note on how two of these were got wrong.** Changes D and M were both written from the stored
configuration without reading the code or the module's own dynamics note, and both overstated a
failure: the configuration's `leveloff_altitude_ft` interval is not the whole candidate set, and an
absolute level-flight duration is not the right statistic for a requirement about proportion. A
configuration value is evidence about a bound, not about behaviour. Where a requirement is about
behaviour, **emit the column and measure it** — which is why the level-off altitude row above now
asks for exactly that. The three-engine-state correction in §5 came from measuring the output rather
than reading the configuration, and it held.

Measured results against version 4's own requirements are recorded in place rather than corrected
silently. One is a clear failure: the onset-boundary condition (§4, 21.6 per cent against a new
5 per cent gate). Two more were reported as failures in versions 5 and 6 of this document and are
**withdrawn in version 7**: sustained level flight within the descent is in fact **met** on the right
statistic, and the two named level-off altitudes are **unverified** rather than absent — both are
recorded as candidates in the dynamics note and the configured interval is the additional sampled
altitude. The lesson is in §0's closing note.

---

## 1. Mission

Establish the realistic uncertainty in what happened between the last reliable cruise state and
the aircraft reaching the sea — flight time after fuel exhaustion, distance, impact location,
impact energy and attitude — **without relying on unprovable assumptions**, and deliver an impact
probability distribution the downstream modules (settling, drift, hydroacoustics, searched areas)
can consume.

**The ordering is the method, and it is not negotiable.** Simulate what the aircraft is likely to
have actually done after fuel exhaustion, as faithfully as the available information and resources
allow. *Then* test those simulations against the evidence. Never shape the simulation to match the
evidence. Because the 00:19 measurements are questioned — the R1200 channel particularly — the
purpose of scoring subsets of them is to see which fit the simulated population and which do not,
and so to learn which data to use and which to set aside. That inference is only available if the
simulated population was built without reference to the fit. A model tuned until it matches 00:19
cannot then be used to ask whether 00:19 is trustworthy.

The module exists to produce an honest posterior, not to decide what happened. Simulations are for
learning physics, not for settling the question.

**Expertise (added 13 October at Pete's instruction; versions 1 to 7 omitted it).** Act as an expert
in aircraft flight dynamics and performance — the Boeing 777-200ER with Trent 892 engines in
particular — including flight outside the normal envelope: dual and single engine flame-out, thrust
asymmetry, loss of control, spiral and phugoid modes, high-speed upsets, structural limits, and
ditching. Work from the body of literature that sets world-class standards, not from this project's
own earlier code: flight-dynamics texts and NASA and FAA loss-of-control research, the Boeing and
ATSB analyses for this accident, and the investigation record of analogue events. **Weight most
heavily the cases where ground truth became available**: the recovered flight data and wreckage of
those events are the only independent check on a model of unpiloted and post-flame-out flight.
Examples to know and use where relevant include Air Transat 236 and the Gimli Glider (dual
flame-out glides), Helios 522 (unpiloted cruise to sequential flame-out, then a descending spiral
with thrust asymmetry), Ethiopian 961 (fuel exhaustion and ditching), US Airways 1549 (ditching),
AF447 and the Payne Stewart Learjet (unpiloted or uncontrolled descents), and BA38 (777-200ER dual
thrust rollback). Review the earlier work on this case critically, with the aim of making the
estimation more rigorous, and apply Bayesian methods from understanding, not by recipe.

Rule 11 of §2 and test 6 of §11 are the mechanisms that make the ordering demonstrable rather than
merely asserted. Neither existed in the previous version, and the first support change made without
them — the dive branch of 13 October — had to be audited after the fact to establish that it was
sound. It was; the point is that the contract could not have told you so.

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
6. **Measure ESS, the weight concentration, and split-half replicate agreement; report unconverged
   as unconverged.** ESS alone is not sufficient and has already misled once: under both 00:19
   bursts on the raw measurement model a stratum-seed shows ESS 38.8 over 100,000 parents **and**
   a largest-single-trajectory share of 12.3 per cent with a top-ten share of 33.5 per cent. The
   second pair is what tells you a shape is not estimated. Report **per seed and per stratum beside
   the pooled figure** — pooled "effective impacts" over 8 seeds × 4 strata reads an order of
   magnitude healthier than any replicate actually is. The fix is the sampler, never the smoothing.
   Use `skill("mh370-run-reporting")` for the conventions.
7. **Settle discrete choices by evidence, or carry them as declared alternatives with priors** and
   report per alternative. Never fixed-weight averages of normalised maps.
8. **One synthetic-recovery test plus hand-computed fixtures.**
9. **Piloted and unpiloted are treated without preference.** Neither is a default. Family priors
   are explicit; results are reported per family before any combination.
10. **Descent physics lives in this module**; the measurement model lives in `satcom`; composition
    lives in the composer. Do not reimplement a measurement model here.
11. **A change of proposal and a change of support are different events, and the second is logged.**
    §8's exact importance weighting makes a change of *proposal* harmless, and that is provable —
    see test 6 of §11. It says nothing about a change of what the model can *reach*. Every change to
    the model's reach — a new branch, a widened bound, a probability moved off zero — is recorded in
    the run note with: the physical justification; **whether it was prompted by a fit failure**; and
    the held-out log-evidence and held-out impact median before and after. A reach change that moves
    the held-out answer is a different event from one that does not, and the distinction is what
    settles a forcing question later rather than by argument.
12. **Run the silent-exclusion review before every sweep.** List every bound, every configured
    range and every zero weight in the envelope, and for each state whether its justification is
    independent of how well anything fits 00:19. This exists because the sampler's own diagnostics
    cannot find these: a fit failure makes the model press on the exclusions the data cares about,
    so those get found and removed, while exclusions the data is silent about survive indefinitely
    and quietly make one hypothesis better explored than its alternative. The review is the only
    procedure that corrects the asymmetry. §§4 and 10 name the current answers.

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

**Three emission rules, added 13 October after an audit found all three broken in the current
runs.** They are contract, not guidance.

- **Emitted means emitted in the impact sample.** The six energy-transfer columns are entirely
  non-finite in `impacts32.npy` and τ is carried in a per-seed sidecar joined by row order. A
  consumer that must join two arrays positionally to get a field the contract rules in does not
  have the field. Write them into the impact sample.
- **A quantity not computed for a family is NaN for that family.** Rule 4 already says NaN means
  "not computed"; a placeholder value breaks it, because a consumer cannot tell a placeholder from
  a measurement. Attitude at impact is currently assigned wings-level for the controlled families
  and 52 per cent of posterior weight carries exactly zero bank. Either compute it or emit NaN —
  not zero.
- **Energy delivered to the water is not total kinetic energy.** The transferred-energy field
  currently equals total kinetic energy to float32 precision, so the model delivers all of it to
  the sea with nothing going into structural deformation, fragmentation or airborne debris. Either
  carry the partition as a declared alternative with a sampled fraction, or label the field an
  upper anchor **everywhere it is quoted**, including in hydroacoustics' own figures.

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
| The EoF **model** | **built and run at full scale twice.** Run I (12 Oct, binary `mh370-eof-ri1`) and run-i-dive (13 Oct, `mh370-eof-ri3`), each 8 seeds × 4 strata × 100,000 m0011 hand-off rows, 6.40 M descents per stratum-seed. Run-i-dive supersedes run I. Notes: `results/eof-run-i-oct12.md`, `results/eof-run-i-dive-oct13.md` |
| Descent physics | **provisional on four counts, all declared in the run notes**: interim parametric pitch-down with the 6-DOF gate unpassed (§8), no transonic drag rise, provisional turn model, provisional in-flight structural model |
| Boeing calibration | **cruise half done, descent half not.** Burn and endurance reproduce the published tables over 27 items at −5.2 to +11.0 per cent; the phugoid period agrees at 78–86 s against 82–87 s when the module's own trim at loss of control is used. The ten engineering-simulator traces have **not** been fitted as traces — see the gate in §8 |
| The 22:41 arms (V1b, V2) | **not run on current physics.** Only the 11 Oct stand-in on core run D, itself unconverged, on physics that could not reach descent rates above 6,500 ft/min or unload the aircraft. Its Bayes factors are not to be carried forward |
| Stage-4 composer | **not built**; `main.rs` rejects `[[compose]]`. Until it exists, use `mh370 evaluate` on an impacts file |

So: the interface and the sampler are built; what is outstanding is descent fidelity, the 22:41
arms, and the sampling collapse of §8. **This table is updated at the end of every full sweep, not
at the next revision of this prompt.** It was six days stale on 13 October and told a reader the
model did not exist.

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

**The 00:17:30 anchor is gone and must not come back.** It was a configured
`exhaustion_target_utc`, worth 0.168 nats, and the reference run removes it precisely because it
forced a disputed hypothesis on the ensemble. Predicted exhaustion is now a *per-trajectory*
quantity computed from the handed-off fuel state under continued cruise — which is what core
request 1 exists to supply — so the onset window is per-trajectory too, not a single clock time.

For scale only, using the run's own implied flame-out quantiles: a 22:41 checkpoint gives roughly
a 96- to 104-minute onset window at the median, comfortably covering the 60- and 90-minute
alternatives. **A 120-minute window reaches back before 22:41 for much of the population and
requires the 21:41 (`m2141`) checkpoint instead.** Compute the window per trajectory and report the
distribution of its length; do not quote one number derived from one assumed exhaustion time.

Making the checkpoint *be* the earliest permitted onset removes an arbitrary horizon, but keep the
diagnostic: **if supported trajectories accumulate against the checkpoint boundary, the boundary is
influencing the answer** and the run must be repeated from an earlier checkpoint.

**The onset-boundary gate.** The previous version required this diagnostic "every time" and gave it
no statistic, no number and no consequence, so neither full sweep reported it and the condition was
met unnoticed. It is now a gate.

- **Statistic.** The weight fraction with descent onset within 60 s of the earliest permitted onset,
  computed **per family**, under the held-out weighting *and* under each 00:19 option.
- **Where.** The coverage section of every run note, as a named row. Not optional, not conditional
  on it looking small.
- **Consequence.** Above **5 per cent in any family under the held-out weighting**, the sweep does
  not support any statement about descent initiation and must be repeated from an earlier
  checkpoint. Between 1 and 5 per cent, the arm is reportable with the figure quoted beside every
  onset number. Below 1 per cent, the boundary is not influencing the answer.
- **Current value, measured 13 October on run-i-dive:** 21.6 per cent for the deliberate-descent
  family, with the earliest onset in the file at the hand-off epoch itself. The gate is failed. The
  anticipatory-onset support configured at 0 to 9,000 s of lead is almost entirely unreachable from
  an m0011 hand-off, so **what the current tables label a deliberate descent is a descent beginning
  in the last eight minutes of the flight**, flown by an aircraft required to be powered to 00:11.
  That is not the hypothesis this section describes.

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

**Two of the above were prose and failed quietly. They are now bounds with a reported statistic.**
Both were written as bullets with no corresponding number in any run note, and an audit on
13 October found neither honoured.

| requirement | checkable form | reported statistic | current value |
|---|---|---|---|
| level-offs including 10,000 ft and 4,000 ft | both altitudes in the candidate set, plus the sampled additional altitude whose interval is stated in the run note | the realised level-off altitude distribution — **currently not emitted as a column, so this cannot be checked from the output at all** | **unverified.** `leveloff_altitude_ft = [11000, 30000]` is the *additional sampled* altitude, and the dynamics note records 10,000 ft and 4,000 ft as always-present candidates alongside it. Reading the configuration alone suggests a gap that the code may not have. Emit the column and settle it |
| lower-altitude flight need not mean descending throughout | the realised time **fraction** spent descending between onset and impact | its quantiles and the weight fraction below 0.60, which must exceed **5 per cent** | **met.** Descending fraction 0.57 / 0.93 / 1.00 at the 5th, 50th and 95th percentiles; 5.8 per cent of weight below 0.60 and 41.5 per cent below 0.90; the longest level segment reaches 2,407 s against the configured 2,400 s cap |

**Use the fraction, not an absolute duration.** An earlier version of this table used "non-descending
seconds above 600 s" and recorded a failure at 1.75 per cent. That statistic was badly chosen: the
median onset-to-impact time is about 1,176 s, so 600 s of level flight is most of the flight and the
threshold was close to unsatisfiable. The fraction is the quantity the requirement is actually about.
The residual concern it leaves is narrower and worth keeping: among descents longer than 1,800 s from
onset — 10.8 per cent of weight — the median non-descending time is only 132 s, so a long descent in
this ensemble is predominantly a slow continuous one rather than descend-cruise-descend.

Keep the provenance note either way: the recovered simulator data is the reason for *including*
4,000 ft in the envelope, never support for it having been flown.

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

**All four, in every family, and the weights are stated per family in the run note.** A zero weight
is a modelling decision that needs writing down and justifying, not a configuration value. Measured
13 October: the control weights are 1, 1, 1, 1 for the two fuel-exhaustion families and
**0.5, 0.5, 0, 0 for the deliberate family**, so the two outcomes are absent from precisely the
family where the next paragraph's distinction decides the result. Nothing in the run notes recorded
it.

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

**Correction, 13 October: the two-engine structure is already built, and the previous versions of
this paragraph were wrong.** They said "single flame-out event for the first working version" and
"single-engine phase never modelled". Measurement of run-i-dive contradicts both. What exists:

- **Core** carries two tanks (`fuel.tanks = 2`), a single-engine fuel and performance phase
  (`fuel.single_engine = true`, `inop_flow_scale = 0.5`, a hold-taper driftdown at 207–227 KCAS,
  300–1,000 ft/min, 7–11 kt/min deceleration, L/D 20.7), and `require_power_until = "m0011"` with
  `hard_reject = true` — so **loss of the second engine before 00:11 is excluded by construction,
  while loss of the first is permitted**.
- **The hand-off carries real per-trajectory fuel state.** Core request 1 has landed. The
  `fallback_fuel_kg = 2000` path is not in use: realised flame-out times take 711,648 distinct
  values with no mass at the 00:31:48 the fallback would imply.
- **This stage takes over with two tank states** (`two_tank_takeover = true`) and tracks the engine
  count at onset. Measured, held-out weighting: 56.9 per cent no engine thrusting, **36.9 per cent
  exactly one**, 6.2 per cent both.
- **`t_realised_flameout_s` is the FINAL flame-out, not the first.** For the 325,071 rows that take
  over with no engine running it sits at takeover within a few seconds. For the 85,018 that take
  over with one engine running it is a median **288 s later**, reaching 1,113 s at the 95th
  percentile. So 22.5 per cent of the fuel-exhaustion families fly a real single-engine phase of
  several minutes inside this stage, and 46.2 per cent of the deliberate family begin their descent
  with one engine running.

So the first and second engine losses are both present **for fuel and gross performance**. Two
things are genuinely missing, and they are what the deferral should now refer to:

1. **The first flame-out time is not emitted.** Only the final one is. Takeover time is a proxy for
   it in the fuel-exhaustion families and is not one in the deliberate family, where takeover is the
   descent onset. Emit both, and name them so the distinction cannot be lost: this column has been
   described in the trait doc as "the first flame-out" and is the opposite.
2. **No asymmetric-thrust dynamics exist anywhere.** This stage's envelope contains no yaw, rudder,
   autopilot-response or thrust-asymmetry parameter — `windmilling_per_engine` is a symmetric drag
   increment and the core's `single_engine_*` parameters govern its own pre-00:11 phase, not this
   one. The single-engine minutes above are therefore flown as a symmetric point mass, against a
   ruling that assigned this module the yaw, autopilot response, drift-down and turn before the
   second flame-out in its 6-DOF simulation. Until that exists, every single-engine segment is a
   declared approximation and the 36.9 per cent figure above belongs beside it.

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

### The seed, and why you do not condition on flame-out

**`no-exhaustion-prior` is the seed.** It is the first full-scale run on the corrected fuel model
and it supersedes `6temper-realloc` for every result — 8 × 7M, 15.52 h, logZ −98.420,
`fuel_no_flow_s` exactly 0.000 s for every particle in every replicate. It also *removes* the
00:17:30 exhaustion term, so exhaustion time is an output rather than something the model was told
to produce. Do not seed from `6temper-realloc`: its fuel state is the burn defect of
`results/fuel-burn-gap.md`, not the aircraft.

Carry its limits with anything you derive. It **fails the convergence floor** — split-half mean
0.9020 over all 35 balanced partitions, range 0.8188 to 0.9495, against 0.924 at 8 replicates,
replicate median span 0.339°. Quote the median (−37.225°) and the 50% interval ([−37.85, −37.00],
width 0.85°). Do **not** quote the shoulder mass or the mode probabilities from it as converged.

**Now the part that decides your design: take the whole hand-off and condition on nothing.**

The temptation is to condition on flame-out, so that every particle has the event this module is
built around. The run says that buys almost nothing and costs real support. At 00:19:37 the
posterior divides as 56.86% already dry, 30.94% still running with under 10 minutes of fuel,
11.15% with 10 to 30 minutes, 1.05% with more than 30 and 0.01% with more than an hour — so
**98.9% is within thirty minutes of fuel exhaustion at the final transmission and 87.8% within
ten.** Over the 43.14% not yet dry the median remaining is 521 kg, about five and a half minutes
at the run's own 5,764 kg/h, with implied flame-out at 00:20:01, 00:21:58, 00:25:04, 00:30:24 and
00:42:47 at the 5th, 25th, 50th, 75th and 95th percentiles.

So a flame-out conditional does not separate a hypothesis from its alternative. It separates
trajectories that flamed out *before the model stopped looking* from trajectories that flame out a
few minutes later, and it discards the second group — which is exactly where a glide after
exhaustion and a descent begun before it differ most. Three further reasons it is the wrong cut:

- the window "between the arcs" is 509 s and `fuel_exhausted_unix_s` is `float32` with a 128 s ulp
  at this epoch, so the condition's own defining variable has about four distinguishable slots
  across it, and a straddling slot holds a few per cent of mass that belongs to neither side;
- 43.14% "never runs dry" only means "had not run dry by 00:19:37", because the model stops at the
  last measurement and says nothing about 00:19:38;
- conditioning obliges every figure to carry a condition label for the rest of the project.

**Instead: hand off everything, and let this stage compute flame-out itself.** A trajectory already
dry at the hand-off takes over at its own exhaustion; one still running burns its remaining fuel
inside this stage and flames out when it does, at your integration resolution rather than at 128 s.
That removes the window, the quantisation, the straddling slot and the post-hoc selection in one
move, and it is the same change as core request 1 — the hand-off must carry the fuel state. Until
that request lands you are running on configured fallbacks and every onset number is provisional;
say so on every figure.

The flame-out window remains worth **reporting** — 51.01% of all mass runs dry between the two
arcs, which is 89.73% of everything that runs dry at all, replicate range 86.7% to 91.9%. That is a
result of the model, not an assumption in it. Report it; do not condition on it.

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

**The uncontrolled-arm calibration gate.** The runs declare "6-DOF gate not passed" as a label and
proceed, which is the module inventing a gate the contract never defined. Define it here.

- **Passed** when the fast model reproduces the ten traces on all four targets with a per-case
  residual table published, the dive cases (3, 4, 5, 6, 10) included explicitly — they are tests of
  *uncontrolled dives* and are the only aircraft-specific validation data the uncontrolled arm has.
- **While unpassed**, the module may report impact *distributions* with the provisional labels
  attached, and may not report any impact *energy*, *attitude*, *flight-path angle* or
  *energy-transfer duration* as a physical prediction — only as a model output conditional on an
  uncalibrated descent. That restriction is heavier than it sounds and is the reason it is here: an
  independent literature pass on 13 October found **no retrievable source publishes an impact speed,
  flight-path angle, impact energy or energy-transfer duration for this accident**, per-case impact
  conditions having been withheld from the Boeing dataset. The trace fit is therefore not one
  validation among several; it is the only one available.
- **Current state.** Unpassed. The 6-DOF fit on the 747 aerodynamic base did not converge: joint
  misfit fell 4 per cent and the shared-physics stage made no progress at its evaluation cap. Where
  the 747-based reference cannot be made to converge, say so and fall back to per-case fitting of
  the fast model rather than leaving the arm labelled interim indefinitely. Transonic drag rise is
  required, because the steep arm routinely exceeds the crest Mach number.

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
   both set by config and empty onset support a legal setting. **This is an acceptance condition,
   not an instruction.** No result may be reported as the headline comparison unless all three arms
   ran on the **same binary, the same core run and the same evidence columns**. The previous version
   described V1a as "nearly free, because the hand-off is built anyway", and the consequence was
   that every full sweep since has been V1a alone: a V1a-only sweep is reportable as "the impact
   distribution under this configuration" and licenses **no** statement about the descent hypothesis
   or about the checkpoint, which §1 already says and which should have been a rule.
3. The evidence sweep of §7 as a sensitivity page per option × BFO model × family: impact area
   (50/90/99%), distance from flame-out and from the 7th arc, impact time, total and vertical energy,
   and ESS with the population beside it.
4. **The headline comparison: how the impact PDF differs across the three arms**, reported as the
   two attributable differences rather than one — V1a against V1b for the checkpoint and sampling,
   V1b against V2 for the descent hypothesis — with the onset-mass boundary diagnostic, the
   terminal-stage ESS at 00:11 beside the filter's, and a statement of what each difference does
   and does not establish.
5. Core requests for the missing `ImpactView` fields.
6. The tests of §11, including test 6.
7. **The dive-fraction hyper-prior as ruled.** The dive branch was ruled to carry a U[0,1]
   hyper-prior with a marginal of 0.5. As built it is a fixed probability of 0.5 drawn independently
   per descent: measured across 6,232 parents with 20.4 push-over draws each, the across-parent
   standard deviation of the dive share is 0.1140, against 0.1108 predicted for a fixed probability
   and 0.3025 for a per-parent draw from U[0,1]. The fixed form asserts that exactly half of piloted
   push-overs continue to the surface as a known quantity, and so understates the uncertainty on the
   latent that drives the R1200-conditioned result — the 90 per cent impact area moved from 59,000
   to 47,000 km² when the branch was added, and 64 per cent of the southern group are levelled-off
   push-overs. Implement the hyper-prior, re-run the R1200 cells, and report the posterior on the
   fraction as a result: it is directly estimable and currently pinned.
8. **The output of §2 rule 12**, the silent-exclusion review, as a table in each run note.
9. **The first flame-out time as an emitted column**, beside the final one, with the engine count
   through the terminal trajectory rather than only at onset — see §5. Without it the single-engine
   segment cannot be measured by a consumer or diagnosed by this module, and 36.9 per cent of weight
   has one engine running at descent onset.

## 11. Tests

Ballistic energy conservation. Level-flight equilibrium. BFO vertical-speed sensitivity against a
finite difference. One synthetic-recovery test: generate the data from a known descent and check
coverage. Plus hand-computed fixtures.

**Test 6, added 13 October — prior recovery under the correction.** For every aimed or targeted
proposal component, show that **the sampling weight alone recovers the uniform prior on the aimed
latent over its full configured support**, and report the statistic in every run note that uses an
aim. This is the test that settles whether a targeted proposal shaped the answer, and the previous
version did not ask for it even though the module had built the machinery and passed it.

Report two things: the maximum absolute deviation between the weighted cumulative distribution and
the uniform one, and the corrected share inside the aim window beside the share a uniform prior
would give. Measured on run-i-dive, as the worked example of a pass: push-over rate deviation
0.0030 with aim-window share 0.6615 against 0.6567 uniform; push-over load floor 0.0041 with
0.1650 against 0.1667; stored mean importance correction 1.000178 ± 0.000693. Beside it, report the
*posterior* share under the informative 00:19 options — 0.9438 and 0.3995 respectively — because the
pair is the evidence of selection: a demonstrably uniform prior, and the data moving it.

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
- **Holland's bounds are published by hypothesis, and the separation is routinely lost in
  quotation.** At 00:19:29 they are 3,900–14,800 ft/min under the satellite-data-unit-restart
  hypothesis against 2,900–6,800 ft/min under the no-warm-up hypothesis, with an 8 s mean downward
  acceleration of 0.68 g. §7's declared-alternative structure is already the right vehicle; compare
  against the **matching** hypothesis, never the merged range, and say which in every figure.
- **None of the ten Boeing cases is in a steep descent as the 7th arc is crossed.** So Boeing's own
  simulations of uncontrolled flight after dual fuel exhaustion and the descent rate derived from
  the 00:19 offsets **do not agree with each other**, a contradiction inside the official material
  rather than between it and this project. Report it as a result of the study; do not reconcile it,
  and do not let the steep arm inherit the authority of the Boeing simulations it does not
  reproduce. This is the most important framing fact available for the paper.
- **Beware the asymmetry a fit failure creates.** The steep, high-energy region of the envelope has
  been found, widened and well sampled because the 00:19 data kept pressing on it. The shallow,
  long-glide and sustained-low-altitude regions have had no comparable pressure applied, so their
  coverage reflects what nobody was forced to fix. A comparison between "a steep dive fits 00:19"
  and "a shallow approach does not" is not a comparison between two equally explored hypotheses
  until §2 rule 12 has been run and its answers closed.

## 13. Out of scope for now, by decision

- **Debris-configuration evidence** (flap and flaperon position, debris energy class). Agreed to come
  *after* a stable, convergent EoF dynamics and satellite-evidence model exists; it is a separate
  module in the architecture. When it arrives, note that it is contested on both strands: the ATSB's
  retracted-flap finding is qualified and disputed, and the absence of buoyant cabin material is
  confounded by detection bias. It enters as a likelihood with explicit model error and declared
  alternatives, never as a veto.
- **Per-engine flame-out** — superseded as written; see the correction in §5. The fuel and
  performance half is built in both stages. What remains deferred is narrower and should be stated
  as such: the **asymmetric-thrust dynamics** of the single-engine phase, and emission of the first
  flame-out time alongside the final one.
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
