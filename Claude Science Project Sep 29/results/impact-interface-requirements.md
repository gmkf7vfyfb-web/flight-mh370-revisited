# What each consumer needs from an impact sample

The interface-requirements pass, taken from the four existing consumer briefs in
`ISO Sept 28 Status/threads/master-prompts/` rather than from first principles. Its purpose is to
freeze `ImpactView` and the shared breakup field **once**, before five modules code against them.
Read with `ARCHITECTURE.md`; it does not restate the composition rules.

This is a requirements document, not a decision. One conclusion in §6 changes the dependency
graph and needs Pete's ruling.

## 1. Hydroacoustics

Predictive-only to begin with: it contributes **zero log-likelihood until calibrated**, and per
impact sample it predicts arrival windows, bearings, transmission loss, and received levels across
a coupling range of at least three decades in η, log-uniform, with the F-35A value as an upper
anchor. Stations are IMS HA01 (H01W, Cape Leeuwin), HA08 (H08S, Diego Garcia) and the IMOS
recorders.

Needs from the impact sample: position; **impact time**, because the arrival window is a time
window; total and vertical kinetic energy; and the coupling term η(γ, ż, attitude, breakup, τ) —
so **flight-path angle, attitude and τ**, which is the requirement that put all three into
`ImpactView`.

It also needs **seafloor depth at the impact point**: it appears as a column of the Kadri
`predictions.csv` alongside weight, latitude, longitude, impact-time range and kinetic energy. That
is a bathymetry lookup rather than an end-of-flight output, and settling needs the same quantity,
so it belongs in the shared layer and must not be computed twice from two different grids.

Its likelihood form, once calibrated, is (1 − P_D) + P_D × (match to detections ÷ background
rate), under Pete's rule that an absence counts only where a signal should have been detectable.
That makes P_D a function of predicted received level, hence of η, hence of attitude and τ — so
those fields stay load-bearing after calibration, not only before it.

## 2. Ocean drift

Part B returns the log-likelihood of the recovered-debris evidence given the impact location, over
a 2-D source region around the 7th arc at ±100–150 NM, with one likelihood per ocean model carried
as the shared alternative `ocean-model`.

The decisive requirement is in its own measured learnings: **object response dominates.** A Stokes
factor of ×0.5, ×1 and ×1.5 moved the drift mode to 11.9, 18.0 and 34.9°S, while changing the
current product moved it only 1.2°. The brief's instruction follows directly — integrate object
response *per object class* inside the likelihood. So drift needs an **object class**, which is the
same object as the breakup field, and it needs it with enough structure to carry a windage or
leeway response per class.

It also needs, implicitly but unavoidably, **which debris floats at all**. A fragment that sinks
never reaches a beach, so the sink-versus-float partition sets the population drift is integrating
over. See §6.

Two further points constrain the shared field rather than the module: find *episodes* are the unit,
not objects, and results must be weighted by termination to avoid the survivor bias that produced
the old 34°S artefact.

**One correction the drift brief needs:** its Part A assigns `crates/ocean` to the drift module on
branch `core/ocean-transport`. That is superseded — the shared ocean transport now has a third
owner, with drift, settling and Pleiades all as consumers.

## 3. Searched areas

The likelihood is

```
P(no find | y) = ρ + (1 − ρ)·Π_k (1 − q_k·c_k(y))
```

with `c_k` campaign k's coverage probability at y as a raster, `q_k` its detection probability, and
ρ the probability the wreck was undetectable through terrain, burial or misclassified contacts.

**`y` must be a wreckage position, not an impact position.** The brief writes it as impact y
because settling did not exist when it was written; that substitution is the whole reason settling
is on the critical path.

What it needs from a wreckage sample is position **and piece size or class**, because detection
depends on the extent and piece sizes of the field rather than only on its centre. Its own
sensitivity analysis sharpens the requirement usefully: uncertainty in `q` barely matters for
location, since for a single campaign the likelihood is linear in q. What matters is coverage
completeness, the dependence between overlapping campaigns, and ρ. So the wreckage sample needs to
resolve *extent*, and does not need a finely calibrated per-piece detectability.

That is also what sets the open draw-count question: the number of wreckage draws per impact is
whatever resolves the coverage rasters, which are built at about 1 km or finer.

## 4. Pleiades

Returns the log-likelihood ratio of the object data under H against not-H, given the impact
location, with the prior π on H swept rather than fixed:

```
log L = ln[(1 − π) + π Σ_c w_c p(y_c|s)/q_c]
```

summed over object clusters — the 12 rating-5 objects reduce to about four locations. It needs
transport from impact time to **23 March 2014**, so it is a consumer of the shared ocean transport,
and it declares the same `ocean-model` alternative as drift, which the composer aligns by name and
marginalises jointly.

From the impact sample it needs position and time only. From the breakup field it needs the same
object response as drift — its prior work swept windage at 0, 1.2 and 3% — plus the same float
partition, for the same reason.

Its recorded failure is a warning about the interface rather than about the physics: integration
collapsed to an effective sample size of 5.6–9.1 out of 150,000 with one particle holding 22–36% of
the mass, because the likelihood was an unnormalised 10 km kernel with no model-error term. Rule 5
exists for that case.

## 5. Proposed freeze

`ImpactView` gains exactly three fields, fixed-size:

| field | consumer | why not computed downstream |
|---|---|---|
| attitude at impact (heading, bank) | hydroacoustics, and settling later | it is a property of the terminal trajectory; nothing downstream can recover it |
| dissipation duration τ | hydroacoustics | same |
| debris class — a **breakup-family identifier** | settling, drift, Pleiades | it is selected by impact energy and flight-path angle, which only the impact sample has |

What does **not** go on the impact sample: per-element-class composition, hydrodynamic descriptors,
counts and mass fractions. Those are a function of the breakup family, they are settling's physics,
and putting them on `ImpactView` would make it variable-length and oblige every consumer to
understand airframe breakdown. Settling emits them as part of the wreckage sample.

Seafloor depth at the impact point is a shared-layer lookup, requested by hydroacoustics and
settling, computed from one bathymetry surface with a provenance flag per cell.

## 6. The finding that needs a ruling: drift is downstream of settling

Drift and Pleiades both need to know **which debris floats and which sinks**, because that
partition defines the population each integrates over. Settling needs the same partition, from the
same element-class physics, to know what descends.

There are only two ways to arrange it, and they are not equivalent:

- **One partition, in settling, consumed by drift and Pleiades.** Settling emits both the
  sink-bound wreckage samples and a float manifest. This is consistent — one physics, one answer —
  but it makes **drift and Pleiades downstream of settling**, which the current merge order does
  not reflect: settling and drift have been treated as parallel.
- **Each module partitions independently.** Cheaper to schedule, and it will produce two
  incompatible answers to the same physical question from the same impact sample, which is the
  failure mode rules 3 and 4 exist to prevent.

The first is correct on the rules. Its cost is real: drift waits on settling's element classes,
having already been made to wait on the shared ocean transport. Noting also that the sink-versus-
float output was deferred as a "potential improvement, not core" — on this reading it is not an
improvement, it is a dependency, and the deferral should be re-examined on that basis.

A third arrangement exists and is worth considering: settling delivers the **float partition
first**, as a small early deliverable ahead of its sinking physics, so drift unblocks early. The
partition needs element classes and buoyancy, not the descent integration, so it is genuinely
separable.

## 7. Still open after this pass

1. Wreckage draws per impact, to be agreed with searched areas against its ~1 km coverage rasters.
2. Whether drift and Pleiades take settling's float partition, partition independently, or receive
   an early partition-only deliverable (§6).
3. Where seafloor-depth lookup lives in the shared layer.
4. Whether TEOS-10 sound-speed profiles are emitted by settling or built in hydroacoustics.
