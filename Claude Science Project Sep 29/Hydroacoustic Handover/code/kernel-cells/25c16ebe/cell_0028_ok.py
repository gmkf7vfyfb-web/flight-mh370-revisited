rep = r"""# End-of-flight module — audit against intent, 13 October 2026

**Scope.** Audit of what the end-of-flight module has actually built and run, measured against the
stated intent: take trajectories from the core posterior (nominally 00:11 UTC, optionally 22:41 for
a planned-descent hypothesis), run a Monte Carlo simulation of 777-200ER behaviour before and after
fuel exhaustion, and produce an ensemble of impact locations, times and characteristics covering
the feasible range under both controlled and uncontrolled descent, with high fidelity to expected
aircraft behaviour and checked against published Boeing and other simulations.

**Evidence base for this audit.** The module brief (`end-of-flight.md`), the interface-requirements
pass (`impact-interface-requirements.md`), the two latest full-sweep notes (`eof-run-i-oct12`,
`eof-run-i-dive-oct13`), the 22:41 stand-in note (`eof-a-vs-b-2241-run-d-standin`), the stored run
configuration (`run.json`), and direct measurement of the delivered impact ensemble
(`run-i-dive/next-i-waypoints/seed-1/impacts32.npy`, 6.40 M simulated descents from 100,000
hand-off trajectories; 914,286-row systematic subsample, every 7th row). Every number below headed
"measured" was computed from that file in this audit, not quoted from a prior note.

---

## 1. Verdict in one page

The module is **architecturally close to intent and physically incomplete**. The interface, the
evidence sweep and the sampling machinery are built and working at full scale. The two things the
intent rests on — fidelity to what the aircraft would have done, and coverage of the feasible
kinematic space — are both only partly delivered, and in each case the shortfall is specific and
fixable rather than structural.

| Intent | Status | Evidence |
|---|---|---|
| Take trajectories from the core posterior at 00:11 | **Delivered** | 100,000 hand-off rows per seed × 8 seeds × 4 strata, full sweep twice (run I, run-i-dive) |
| Optionally branch at 22:41 for a planned descent | **Not delivered on current physics** | Only the 11 Oct stand-in on core run D, with pre-dive-branch physics that could not reach descent rates above 6,500 ft/min |
| Monte Carlo over 777-200ER behaviour before and after fuel exhaustion | **Delivered** | Fuel burn continued in-stage, flame-out derived in-stage, 2 s step with 0.2 s refinement through the transition |
| Cover controlled and uncontrolled descent without preference | **Partly** | Three families produced and reported separately; two of four control outcomes carry zero weight in the deliberate-descent family |
| High fidelity to expected aircraft behaviour | **Partly** | Cruise burn and endurance calibrated to Boeing tables; descent dynamics still labelled interim, and the 6-DOF fit to the Boeing dive cases has not converged |
| Check against published Boeing and other simulations | **Partly** | Calibrated against the published burn and endurance tables and the phugoid period; not yet against the ten engineering-simulator traces as traces |
| Produce impact location, time and characteristics | **Delivered, with one interface defect** | 110 columns including attitude, energy and breakup probabilities; the six energy-transfer columns are empty in the impact file and the quantity lives in a sidecar |
| Adequately sample the feasible kinematic space | **No, in three identified places** | Onset support truncated at the hand-off; level-off altitudes exclude 10,000 ft and 4,000 ft; sustained low-altitude flight is effectively absent |

---

## 2. What has actually been done

### 2.1 The simulation that exists

Each core trajectory handed over at 00:11 UTC spawns children, and each child flies four sampled
descents, giving 6.40 M simulated descents per stratum per seed. Within the stage the aircraft
continues to burn fuel, so flame-out time is computed rather than read from the core filter's
quantised column, and the integration refines from a 2 s step to 0.2 s in a 30 s window around the
transition.

The sampled envelope, read from the stored configuration, is wide. Descent rates run from 800 to
3,500 ft/min for normal profiles, 3,000 to 6,500 ft/min for emergency-style profiles, 6,500 to
40,000 ft/min for rapid descents, with load factors unloaded to −1.0 g and a piloted ceiling of
1.5 to 5.0 g. Turns are available at any time with 10 to 30 degrees of bank, plus orbits and a
ditching circuit. Windmilling and ram-air-turbine drag increments, maximum lift-to-drag ratio of
20.8 to 21.4, Oswald efficiency, thrust-specific fuel consumption and wave-drag coefficients are
all sampled rather than fixed.

Three descent families are produced and reported separately, which satisfies the requirement to
treat piloted and unpiloted without preference: uncontrolled after fuel exhaustion, piloted after
fuel exhaustion, and deliberate descent with a ditching approach. Measured weight shares in the
dominant stratum, with no 00:19 data used: 15.6 per cent, 32.1 per cent and 52.3 per cent.

### 2.2 The evidence sweep

Both axes the intent asked for are built and exercised. Ten likelihood columns are computed from
the same children, crossing which 00:19 bursts are scored (none, R600 only, R1200 only, both)
against how the burst frequency offset is interpreted (raw, inflated, start-up offset). The 00:19
options are reported as a two-factor table with Bayes factors, and the spread across cells is
reported rather than one preferred interpretation. This is the part of the module that most fully
matches intent.

### 2.3 The impact sample

110 columns per impact, including position, time, three velocity components, flight-path angle,
mass, heading and bank at impact, total and vertical kinetic energy, breakup probabilities, a
debris class, the take-over position and altitude, and 60 or so sampled latents. Every field the
interface-requirements pass ruled in is present as a column. Measured non-finite fractions are
small and explained — 6.9 per cent for realised flame-out time, around 11 per cent for the 00:19
residuals and likelihoods (trajectories that had already impacted), and around 33 per cent for the
00:19 state columns.

---

## 3. What the current posterior does and does not tell us

### 3.1 It is directionally informative and numerically fragile

Measured effective sample size over the 100,000 hand-off trajectories of one stratum and seed:

| 00:19 evidence option | Effective sample size | Largest single trajectory's share |
|---|---|---|
| None used (held out) | 50,966 | 0.03 % |
| R600 burst frequency offset only | 3,983 | 0.7 % |
| R1200 burst frequency offset only | 216 | — |
| Both bursts, start-up offset model | 170 | — |
| Both bursts, raw measurement model | **38.8** | **12.3 %** |

Under the option that actually discriminates a descent — both 00:19 bursts on the raw measurement
model — the top ten trajectories out of 100,000 carry 33.5 per cent of the weight. The module's own
stored diagnostic agrees: 272 effective parents and 273 effective rows out of 6.40 M descents. The
published tables pool eight seeds and four strata, which is why they can show thousands of
"effective impacts" in the same cells; the per-seed figure is what governs whether a *shape* is
estimated or a *location* is.

So the honest reading of the current posterior is: **the impact latitude band and its direction of
movement under each 00:19 interpretation are supported; the shape, the shoulder mass and the
family shares under the informative options are not.** The latitude medians are stable across
options at roughly −37.1 to −37.4 degrees, and the published 90 per cent impact areas move from
135,000 km² held out to 47,000 km² with the R1200 reading — but both of those numbers inherit an
unconverged core run (split-half 0.902 against a 0.924 floor) and a few dozen effective
trajectories.

### 3.2 What it does tell us, robustly

Measured, held-out weighting, dominant stratum:

- **Impact time is wide and option-dependent.** Quantiles 00:16:46 / 00:25:18 / 00:35:31 /
  00:43:04 / 00:52:21 held out, tightening and moving earlier to 00:19:54 / 00:20:56 / 00:26:55 /
  00:33:55 / 00:42:19 when both 00:19 bursts are scored. This is a genuine result of the model, not
  an assumption, and it matters to hydroacoustics because the arrival window is a time window.
- **Impact severity spans four orders of magnitude.** Vertical kinetic energy at impact runs from
  6.3 × 10⁵ J at the 5th percentile to 7.4 × 10⁹ J at the 95th; total kinetic energy from 0.35 to
  11.0 GJ. Flight-path angle below the horizontal runs 1.7 / 4.2 / 56.2 degrees at the 5th, 50th
  and 95th percentiles, and surface speed 63 / 119 / 355 m/s.
- **The arrival regimes are separated, not continuous.** Shallow arrivals cluster near 3 to 5
  degrees and 60 to 130 m/s; steep arrivals near 30 to 60 degrees and 300 to 360 m/s, with sparse
  occupancy between. That bimodality is the physically expected signature of controlled approach
  against developed dive, and it is the single most useful property of the ensemble for downstream
  work.
- **Energy transfer duration.** Measured 90 per cent transfer time 0.11 / 3.62 / 11.31 s at the
  5th, 50th and 95th percentiles, with deceleration 0.86 to 2.89 g and effective crush length 33 to
  62 m.

### 3.3 What it cannot tell us

- **Whether a deliberate descent was planned before 00:11.** The hand-off is at 00:11, so by
  construction it cannot. See §4.1.
- **Family probabilities under the informative 00:19 options**, because of §3.1.
- **Anything about attitude for the controlled families** — 52.1 per cent of the weight carries
  exactly zero bank, assigned rather than computed.
- **The partition of impact energy.** Measured: the energy-transferred field equals total kinetic
  energy to float32 precision in every row. The model therefore delivers all kinetic energy to the
  water, with no fraction going into structural deformation, fragmentation or airborne debris. For
  hydroacoustics that is an upper anchor, not an estimate, and should be labelled as one.

---

## 4. Does it adequately sample the feasible kinematic space?

Not yet. Three specific gaps, all measured, all closable.

### 4.1 The onset support is truncated at the hand-off — this is the significant one

The configuration samples an anticipatory lead of up to 9,000 s before predicted fuel exhaustion,
and a fuel-caution lead of 1,800 to 4,200 s. With a 00:11 hand-off and predicted exhaustion a few
minutes later, almost all of that support lies before the hand-off and is unreachable. Measured:
the earliest descent onset in the entire file is 00:10:59, the hand-off epoch itself; 13.3 per cent
of all weight and **21.6 per cent of the deliberate-descent family's weight sits within 30 s of that
boundary**, as a point mass rather than a tail.

The module's own brief states the diagnostic and the remedy: if supported trajectories accumulate
against the checkpoint boundary, the boundary is influencing the answer and the run must be repeated
from an earlier checkpoint. The diagnostic is firing, and at 21.6 per cent it is not marginal.

The consequence is that **the hypothesis labelled "deliberate descent" in the current tables is not
the hypothesis the intent describes.** What is being tested is a descent beginning in the last
eight minutes of the flight, flown by an aircraft whose entire preceding trajectory was fitted
under cruise assumptions and required to be powered to 00:11. A descent planned in anticipation of
fuel exhaustion — which changes burn, speed, wind exposure, altitude in the timing geometry and
vertical rate in the frequency offset from the moment it starts — has not been simulated on current
physics. The brief is explicit that such a trajectory must be re-scored rather than extended.

### 4.2 Two of four control outcomes carry zero weight in the deliberate family

The intent requires four control outcomes within either initiation branch: control maintained
through an attempted ditching, control maintained then lost, no effective intervention, and upset
followed by demonstrated recovery. Measured configuration: control weights are 1, 1, 1, 1 for the
fuel-exhaustion families but **0.5, 0.5, 0, 0 for the deliberate family**. Two outcomes are
therefore absent from exactly the family where the distinction between an attempted and an achieved
ditching matters most.

### 4.3 Level-off altitudes and sustained low-altitude flight

- Configured level-off altitudes are 11,000 to 30,000 ft. The intent explicitly requires 10,000 ft
  and 4,000 ft inside the envelope: 10,000 ft falls just below the lower bound and 4,000 ft is well
  outside it. The approach band of 500 to 2,000 ft and the transition band of 8,000 to 15,000 ft
  cover the altitudes in passing but not as *level-off* options.
- The intent states that an hour between onset and impact need not mean an hour descending.
  Measured: the non-descending time between onset and impact is 53 s at the median and 411 s at the
  95th percentile, and only **1.75 per cent** of the weight has more than 600 s of non-descending
  flight. Sustained low-altitude cruise after a descent is in the configuration but not in the
  realised ensemble.

### 4.4 Where coverage is adequate

The descent-rate span, the load-factor span, the turn and circuit structure, the aerodynamic
parameter ranges, the three onset mechanisms (sampled at measured shares of 47.1, 5.0 and 47.7 per
cent of rows) and the five profile shapes are all genuinely sampled rather than assumed, and the
module reports its own coverage gaps honestly in both run notes. No trajectory in the file hit the
simulation time limit.

---

## 5. Fidelity to expected aircraft behaviour, and the published-simulation check

**What has been calibrated.** Cruise fuel burn and endurance against the published Boeing tables:
27 items, agreement from −5.2 to +11.0 per cent as coded, with the larger errors in cells flagged
as extrapolated beyond the tabulated Mach range. The free-dynamics phugoid period matches the
Boeing traces at 78 to 86 s against 82 to 87 s, provided the module's own trim at loss of control
is used rather than best-glide lift coefficient. The dual-flame-out glide is anchored to roughly
120 NM from FL350 per the investigation report appendix.

**What has not.** The ten Boeing engineering-simulator traces are tests of *uncontrolled dives*,
and the module's descent dynamics have not been fitted to them as traces. The 6-DOF fit ran on a
747 aerodynamic base — there is no public 777 6-DOF data — and did not converge: joint misfit fell
only 4 per cent and the shared-physics stage made no progress at its evaluation cap. The runs
accordingly carry four standing labels: interim parametric pitch-down with the 6-DOF gate not
passed, no transonic drag rise, provisional turn model, provisional in-flight structural model.

This is the heart of the fidelity concern. The ensemble's steep, high-energy arm — the half of the
distribution that the 00:19 evidence selects — is generated by the component that is least
calibrated. The bank point mass of §3.3 and the absent transonic drag rise both sit in that same
arm.

**The 22:41 comparison.** The headline deliverable — how the impact distribution differs between a
cruise-to-exhaustion arm and a planned-descent arm — exists only as the 11 Oct stand-in run on core
run D, which was itself unconverged, and on physics that explicitly could not reach descent rates
above 6,500 ft/min or unload the aircraft. It reported Bayes factors of +0.3 to +1.4 nats favouring
cruise-to-exhaustion. Those numbers should not be carried forward: the physics they were computed
on has since been superseded twice, and the thing they test is restricted by §4.1 in any case.

---

## 6. Usefulness to the downstream modules

| Consumer | Needs | Status |
|---|---|---|
| Hydroacoustics | Position, impact time, total and vertical kinetic energy, flight-path angle, attitude, energy-transfer duration | **Usable with two caveats.** Energy-transfer fields are empty in the impact file and must be joined from a sidecar array by row order; attitude is a placeholder for half the weight; transferred energy is total kinetic energy, an upper anchor |
| Ocean drift | Position, time, object class with enough structure for a leeway response per class, and which debris floats | **Partly.** Debris class is emitted with three levels; the sink-versus-float partition is a documented stub with no physics behind it, and the interface pass concluded it is a dependency rather than an improvement |
| Settling | Vertical and total kinetic energy, flight-path angle; attitude and duration carried through | **Usable.** These are the fields settling's first pass actually conditions on, and all are populated and well spread |
| Searched areas | A wreckage position, not an impact position | **Indirect, correctly.** Depends on settling, as designed |
| Pleiades | Position and time only | **Usable** |

The spread in vertical kinetic energy and flight-path angle is the property that makes the sample
genuinely useful downstream — settling's seabed displacement spans two orders of magnitude over
that range, and the ensemble covers it. The limiting factor for all five consumers is not the
fields, it is §3.1: an impact sample whose informative-option weight concentrates on a few dozen
trajectories propagates that concentration into every consumer likelihood.

Two interface items should be closed before the next consumer run: write the energy-transfer fields
into the impact file rather than a sidecar, and either implement the float partition or state in
each consumer's method that drift and Pleiades integrate over an unpartitioned population.

---

## 7. Recommendations, in priority order

**1. Re-run the planned-descent arm from an earlier checkpoint, and measure the boundary mass every
time.** This is the one change that alters what the module can conclude rather than how precisely.
Take the 22:41 hand-off, and if the measured onset mass within a few minutes of the boundary stays
above a few per cent, go to 21:41. Run the three arms the brief defines — 00:11 with
flame-out-associated onset only, 22:41 with flame-out-associated onset only, 22:41 with anticipatory
onset enabled — so that the checkpoint-and-sampling effect is separated from the descent hypothesis
and the headline comparison is attributable. Report the onset-mass boundary diagnostic as a standing
figure.

**2. Close the Boeing dive-case calibration before any impact distribution is quoted as physics.**
The ten traces are the only aircraft-specific validation data available for the uncontrolled arm.
Fit the fast model to them as traces on the targets already identified — phugoid period, bank
growth rate, time to 15,000 ft/min, distance and time to impact — and report a per-case residual
table. Where the 747-based 6-DOF reference cannot be made to converge, say so and fall back to
per-case fitting of the fast model rather than leaving the arm labelled interim. Add transonic drag
rise, since the steep arm routinely exceeds the crest Mach number.

**3. Fix the sampling collapse under the informative 00:19 options rather than the smoothing.**
The run notes already name the fix for the worst cells: an aimed proposal on the powered push-over
start time within the burst window, with more children on the parents that reach it. Extend it to
the uncontrolled family, which is the one below the gate in every silent-cause cell. Target a
per-seed effective parent count in the hundreds rather than the tens, and re-measure the top-ten
weight share as the acceptance test — effective sample size alone hides a 12 per cent single
trajectory.

**4. Open the two closed control outcomes in the deliberate family** and give the deliberate family
the same four-way control weighting the fuel-exhaustion families already have. Attempted-but-failed
ditching is the population the hypothesis has to be tested against, and it is currently absent.

**5. Extend the level-off support to 10,000 ft and 4,000 ft**, and add a sampled sustained
low-altitude segment so that the measured non-descending time has real mass beyond ten minutes.
Both are configuration changes, not model changes. Keep the provenance note: the simulator-data
altitude is a reason for including 4,000 ft in the envelope, never support for it having been flown.

**6. Compute attitude at impact for the controlled families** rather than assigning wings level.
Half the weight currently carries a placeholder in a field the interface pass ruled in specifically
because nothing downstream can recover it. Until it is computed, mark the field as not estimated
for those families so no consumer conditions on it.

**7. Partition the impact energy.** Replace the identity between transferred energy and total
kinetic energy with a sampled fraction, and give hydroacoustics the fraction as a declared
alternative. The current field is a defensible upper anchor and should be labelled as one in the
meantime.

**8. Widen the fine-step window through the flame-out transition** from 30 s to cover the full
systems sequence. Thrust loss, ram-air-turbine deployment and auxiliary-power-unit start span about
a minute to two; a 30 s refinement window smears the second half of it.

**9. Then, and only then, re-run the headline three-arm comparison** on a converged core run, and
report the two attributable differences separately with the effective sample size and the top-weight
share beside each.

---

## 8. Two things to decide

- **The deferred hooks.** The debris class is emitted but the sink-versus-float partition is a stub.
  The interface pass concluded it is a dependency of drift and Pleiades rather than an optional
  improvement, and recommended settling deliver a float partition first as an early deliverable.
  That decision is outstanding and blocks two modules.
- **Whether to carry the 22:41 stand-in numbers at all.** They are the only cruise-against-planned
  comparison in existence, and they were computed on physics that has been superseded twice. The
  options are to repeat the comparison on current physics before any write-up cites it, or to cite
  it explicitly as a stand-in with its reach limits quoted in the same sentence.
"""
open("eof-audit-2026-10-13.md","w").write(rep)
print(len(rep))
