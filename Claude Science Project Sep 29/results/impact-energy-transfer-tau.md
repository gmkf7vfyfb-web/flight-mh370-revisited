# The impact energy-transfer duration: a definition for the ImpactView interface

**Status: proposed definition, agreed in principle, value not yet derivable.** Written by the
end-of-flight session, 2026-10-08, for ruling by architecture and for use by hydroacoustics and
settling. The field named here is ruled into `ImpactView` by §2 of the end-of-flight brief as "the
dissipation duration tau for the hydroacoustic source term". This note fixes what it means, says
why it is currently NaN, and raises the two questions that are not the end-of-flight module's to
settle.

The conceptual decision is taken now and the numerical derivation is deferred. Those are separable,
and deferring the definition as well is the thing to avoid: a field whose meaning is settled only
when someone first fills it will be filled inconsistently.

## 1. The definition

Let `P(t) >= 0` be the modelled rate at which mechanical energy is transferred out of the aircraft
and its fragments during the initial water-entry and deceleration event, under a stated energy
accounting convention, with `t0` the moment of first water contact. Write

    E       = integral of P(t) over the initial impact event
    F(t)    = (1/E) * integral of P(s) ds from t0 to t
    tau90   = t95 - t05,  where F(t05) = 0.05 and F(t95) = 0.95

`tau90` is the interval containing the central 90% of the transferred mechanical energy. The field
is `impact_energy_transfer_tau90_s`.

**The convention is named in the field, deliberately.** A field called `tau` whose percentile
convention lives only in a doc comment changes meaning silently if the convention is ever revised,
and runs made either side of that revision become incomparable without anyone noticing. The 90%
figure is an interface choice, not an established aircraft-impact standard; naming it in the field
makes a future change visible in every file that carries it.

**It is "energy transfer", not "dissipation".** Energy put into bulk water motion, waves and
structural deformation has left the aircraft but has not necessarily been irreversibly dissipated.
The brief's wording "dissipation duration" is retained here only as the pointer to what is meant.

Accounting rules that travel with the definition:

- `t0` is first water contact.
- Separated fragments are tracked consistently. Energy must not leave the accounting merely because
  a fragment leaves the airframe.
- Subsequent gravitational settling, flooding and any implosion at depth are **not** part of this
  event and must not lengthen it. They are settling's, and the implosion case is already queued in
  §13 of the end-of-flight brief as a separate acoustic event tens of minutes later.
- An incomplete event is recorded as incomplete. Energy accumulated before a simulation terminates
  is never renormalised and reported as a complete duration.
- Where transfer is negligible or not computable, the duration is undefined — NaN, meaning "not
  computed", per composition rule 4.

## 2. Two properties that are load-bearing, not stylistic

### 2.1 tau is a function of the impact state, never of the family label

The intuition that a steep fast entry gives a short tau and a well-executed ditching a long one is
right in direction and wrong as an implementation. Energy and duration are separate variables: a
ditching reduces vertical velocity while retaining substantial horizontal kinetic energy, so
"piloted" does not imply "low energy".

More seriously, assigning tau per taxonomy family would make the hydroacoustic likelihood a
function of the end-of-flight family prior. That prior would then enter the posterior twice — once
as the family weight this module reports, and once through hydroacoustics' score on a quantity
derived from the label rather than from the dynamics. That is a violation of the composition rules,
not an approximation.

It also contradicts evidence already recorded in the end-of-flight brief: best glide or fixed trim
produces ditching-like impacts about 100 NM out, so a ditching-like impact is not evidence of a
ditching (§12), and an attempted ditching must be distinguished from an achieved low-speed water
contact (§4). The same discipline applies to tau.

**Required: tau is computed from the impact state — velocity, attitude, mass, geometry — and from
the water-entry model's own parameters. Never from the family.**

### 2.2 tau is deterministic given state, not an independent latent

tau must be a deterministic function of the impact state and the water-entry model's uncertain
parameters, with those parameters drawn inside the module's existing proposal. It must not be an
independently drawn latent.

The reason is the weighting rules of §8: a parent's weight is split across its descendants, and
deliberate oversampling of any family or interval must be corrected with exact importance weights.
An independently drawn tau invites a later optimisation — oversampling long-tau events so
hydroacoustics has more signal to score — which would break those weights in a way that is close
to undetectable downstream. Making tau a function of state removes the opportunity.

## 3. Three durations, three owners

A single unqualified tau must not stand for all three of the following.

| quantity | owner | note |
|---|---|---|
| mechanical energy-transfer duration | **end of flight** | this note; `impact_energy_transfer_tau90_s` |
| acoustic source duration | hydroacoustics | mechanical loss is not all radiated as sound; it also goes to bulk water motion, waves, deformation, fragmentation and heat |
| received signal duration at a hydrophone | hydroacoustics | includes propagation broadening; not to be read back as impact duration |

This follows §2.10 of the end-of-flight brief: descent physics lives in the end-of-flight module and
the measurement model lives with the module that owns the measurement. The conversion from a
mechanical event to an acoustic source is hydroacoustics' measurement model and is not to be
reimplemented here.

Two events with identical energy and tau can radiate materially different signals. Energy and tau
together do not determine pressure amplitude, spectrum or directivity, and nothing downstream should
be built as though they did.

## 4. What the end-of-flight module emits today, and why it is NaN

`impact_energy_transfer_tau90_s` ships now as a documented hook, always NaN, with
`impact_tau_method` beside it recording how the value was obtained. The method flag is not
decoration: under composition rule 4 NaN means "not computed", and a consumer must be able to
separate "not computed" from "computed as zero" mechanically rather than by reading prose. This is
the treatment already used for `debris_class` and `sinks_not_floats`, and endorsed in the
architecture review of `8ccb105`.

The reason it is NaN is specific and removable. The module's integrator terminates **at** the sea
surface: it solves the surface crossing and stops. There is no water-entry model, no hydrodynamic
load model and no fragmentation model, so `P(t)` is the power history of an event the module does
not currently simulate.

The available shortcut is `tau ~ delta_v / a_bar` under a constant-deceleration approximation. It is
only admissible if `a_bar` comes from a justified impact model. Choosing `a_bar` to produce short
nosedives and long ditchings would reintroduce §2.1 through the denominator, and would be circular
in exactly the way that makes a result unfalsifiable. **A plausible-looking number here would be
worse than an explicit missing one.**

What would remove the NaN: a water-entry model giving a defensible deceleration history as a
function of entry velocity, flight-path angle, attitude and airframe geometry, with declared
parameter uncertainty. The starting bibliography is in §6. Note that two of those three papers come
from the same group, so the experimental base for high-speed ditching hydrodynamics is narrow and
any `a_bar` derived from it should carry generous declared uncertainty rather than being treated as
well-constrained.

## 5. Two questions for architecture

**5.1 Scalar, or a fixed number of energy-transfer bins?** A long event can contain short intense
pulses — initial fuselage contact, engine or wing contact, successive wave encounters — and a single
scalar cannot distinguish one pulse from several. The natural fix is to pass an energy-transfer time
history, but §2 of the end-of-flight brief settles granularity the other way: the impact sample is
not to be variable-length.

Proposed resolution: keep the sample rectangular and emit a **fixed, small** number of
energy-transfer bins alongside `tau90`. That preserves the distinction hydroacoustics needs without
breaking the fixed-width rule, and it is the same pattern as the debris class — a compact summary on
the impact sample, the detailed ensemble generated by the consumer. The bin count is an interface
constant and should be ruled once rather than per module.

**5.2 Who owns the water-entry model?** It is not obviously the end-of-flight module's. Settling
owns the breakup families and already conditions on vertical and total kinetic energy plus
flight-path angle, so the energy-transfer physics sits between the end-of-flight impact state and
settling's breakup. Wherever it lands, it should be one model with one set of declared parameters,
read by both consumers, rather than two.

Until 5.1 is ruled, `impact_energy_transfer_tau90_s` is a single scalar hook and no consumer should
build against a history that does not yet exist.

## 6. Sources

Verified against arXiv and Crossref on 2026-10-08.

- Spinosa, Grizzi & Iafrati, *High-speed ditching of double curvature specimens with cavitation and
  ventilation*, arXiv:2408.06952; *Ocean Engineering* 341.
- Spinosa, Broglia & Iafrati, *Hydrodynamic analysis of the water landing phase of aircraft
  fuselages at constant speed and fixed attitude*, arXiv:2208.01504; *Aerospace Science and
  Technology*.
- Kadri, *Underwater acoustic analysis reveals unique pressure signals associated with aircraft
  crashes in the sea: revisiting MH370*, *Scientific Reports* 14 (2024),
  doi:10.1038/s41598-024-60529-1.

All three are citable in their own right, unlike the operational descent figures discussed in §9 of
the end-of-flight brief, which circulate via unauthorised copies of copyrighted manuals and are used
as modelling parameters without citation.
