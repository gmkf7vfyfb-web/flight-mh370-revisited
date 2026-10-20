# How the end-of-flight module computes impact energy

**Module-owned method, not interface.** The contract — what the columns mean, the five
qualifications, where `tau` matters acoustically — is ruled in `coordination/END_OF_FLIGHT.md` and
in `threads/master-prompts/hydroacoustics.md`, and those are the single source of truth. This note
says how the numbers are produced inside this module, so that a source model is built against stated
conventions rather than against guesses. Written by the end-of-flight session, 2026-10-08.

Status of the first pass: **contact energy is live; the energy-transfer columns are declared NaN
hooks.** Section 5 says exactly why, and what would remove the NaN.

## 1. Where the trajectory ends, and what the contact state is

The descent is integrated as an RK4 point mass with a configurable step (`step_s`, with
`fine_step_s` over a `fine_window_s` window through the flame-out transition). It terminates when
pressure altitude crosses `Air::surface_pressure_altitude_ft`.

The crossing is **solved inside the final step, not quantised to a step boundary**
(`integrator.rs`, the surface branch): the linear interpolant between the bracketing states is used
as a first guess and the crossing is then refined within the step. So contact time and contact state
are continuous in the dynamics rather than resolved to `step_s`. This matters for `t0`: every time
in the energy-transfer columns is measured from that solved crossing.

Two properties of the contact state that a consumer must know:

- **Velocity is ground-relative and includes wind.** The integrator carries true airspeed and
  heading, and the emitted impact velocity is the horizontal air-relative component rotated onto
  heading plus the local wind vector, with the vertical component as integrated. Ground-relative is
  the right frame for a water impact. Ocean surface current is not subtracted; at order 0.5 m/s
  against impact speeds of order 100 m/s this is below the model's other uncertainties, and it is
  declared here rather than silently neglected.
- **The surface is currently ISA sea level, not the local sea surface.** The integrator's doc
  comment says `surface_pressure_altitude_ft` comes from ERA5 mean-sea-level pressure where the grid
  carries it, but the runner hard-codes it to 0.0 (`crates/mh370/src/terminal.rs:380`, core request
  5). A 10 hPa anomaly is about 280 ft, so this is a small systematic bias on impact time and on
  vertical speed at contact, in the same direction for every sample. It is a core-owned fix.

An integration that reaches `max_flight_s` without crossing the surface has no contact state. It is
recorded in the `timed_out` latent and, with `emit_timed_out_descents` off — which it must be for
any reported impact PDF — is finished on a best glide rather than discarded. No energy column is
ever derived from such a sample.

## 2. Contact energy: already a field, and an upper bound

`ImpactView.kinetic_energy_j` **is** kinetic energy at contact. The runner derives it from this
module's own `Impact` at `terminal.rs:263`:

    speed2                   = ve^2 + vn^2 + vu^2
    kinetic_energy_j         = 0.5 * mass_kg * speed2
    vertical_kinetic_energy_j = 0.5 * mass_kg * vu^2

`mass_kg` is the integrated aircraft mass at the crossing — zero-fuel mass plus whatever fuel
remains, which for most of the population is zero by then. No separate `kinetic_energy_at_contact_j`
column is emitted, because it would be a second, module-private name for this number.

**Contact energy is an upper bound on energy transferred to the water, not an estimate of it.**
`impact_energy_transferred_j` is what the water received. They differ by whatever leaves the event
as fragment kinetic energy, structural deformation, and residual translation of pieces still moving
when the initial event ends. The bound is the useful thing a source model can hold onto while the
transfer columns are NaN: whatever `P(t)` turns out to be, its integral cannot exceed
`kinetic_energy_j` plus the small potential-energy term of material still above the surface.

The vertical/total split is carried deliberately. A ditching reduces vertical velocity while
retaining substantial horizontal kinetic energy, so the two numbers separate "how hard did it hit
the water downwards" from "how much energy was in the system" — and neither may be inferred from the
taxonomy family. That is the first of the ruled qualifications, and it is a property of this
module's output, not an instruction to the consumer.

## 3. The energy accounting convention

Let the **system** be the airframe together with every fragment separated from it, from the solved
surface crossing onward. `P(t)` is the rate at which mechanical energy leaves that system into the
water and into irreversible deformation.

Inside the accounting:

- work done against hydrodynamic pressure and shear on wetted surfaces, including the cavitation and
  ventilation regimes that dominate high-speed ditching;
- energy into bulk water motion and surface waves — it has left the aircraft even though it is not
  yet dissipated, which is why the quantity is named energy *transfer*;
- irreversible structural deformation and fragmentation work.

Outside the accounting:

- everything before first water contact: the descent's energy history is a separate budget and the
  two are never summed;
- kinetic energy still carried by intact pieces at the end of the initial event — it has not been
  transferred, and it is the main reason `impact_energy_transferred_j < kinetic_energy_j`;
- **everything after the initial entry event**: flooding, sinking, pressure-induced collapse and
  seabed contact. Those belong to settling, and the implosion-at-depth case is already queued in
  §13 of the end-of-flight brief as a distinct acoustic event tens of minutes later. Nothing in that
  sequence may lengthen `energy_transfer_tau90_s`.

## 4. Fragment tracking, and the boundary with settling

**The rule is that energy may not vanish from the budget because a fragment left the airframe.** A
separated fragment stays in the system; its kinetic energy remains untransferred until that fragment
decelerates in water, at which point it contributes to `P(t)` like any other wetted body.

**The first pass does not implement this, and says so rather than assuming it away.** The module has
no fragmentation model: the integrator carries a single point mass to the surface. So at first pass
the system is one body, and the accounting convention above is a specification for when a
water-entry model exists rather than a description of running code.

The handover to settling is defined on the event, not on a clock: the end-of-flight module owns the
initial water-entry and deceleration event, and settling owns everything from the end of that event
onward — breakup into its object ensemble, descent through the water column, seabed arrival.
Settling's first pass conditions on vertical and total kinetic energy plus flight-path angle, all of
which are contact-state quantities, so the two modules already meet at the surface crossing and
neither double-counts the other's energy.

## 5. Why `P(t)` is NaN, and what removes it

The integrator stops at the surface. There is no water-entry model, no hydrodynamic load model and
no fragmentation model, so `P(t)` is the power history of an event this module does not simulate.
Every column derived from it — `impact_energy_transferred_j`, `energy_transfer_t05_s`,
`energy_transfer_t95_s`, `energy_transfer_tau90_s`, `energy_transfer_peak_rate_w`,
`energy_transfer_n_pulses` — is therefore NaN, with `impact_tau_method` beside them recording why.
Under composition rule 4 NaN means "not computed"; the method flag exists so a consumer can separate
that from "computed as zero" mechanically rather than by reading prose.

The available shortcut, `tau ≈ Δv / ā` under constant deceleration, is admissible only if `ā` comes
from a justified impact model. Choosing `ā` so that steep entries come out short and ditchings long
would make `tau` a function of the taxonomy family by the back door, which is the one thing the
ruling forbids, and it would be unfalsifiable.

What would remove the NaN: a water-entry model giving a deceleration history as a function of entry
velocity, flight-path angle, attitude and airframe geometry, with declared parameter uncertainty.
The literature base is narrow — the two experimental and numerical studies closest to this problem
(Spinosa, Grizzi & Iafrati on high-speed ditching with cavitation and ventilation, arXiv:2408.06952;
Spinosa, Broglia & Iafrati on fuselage water landing at fixed attitude, arXiv:2208.01504) come from
the same group — so any `ā` drawn from it should carry generous declared uncertainty rather than
being treated as well-constrained. Whether that model belongs here or in settling is an open
architecture question; it should be one model with one parameter set, read by both consumers.

## 6. The `n_pulses` threshold

`energy_transfer_n_pulses` counts distinct peaks in `P(t)` — initial fuselage contact, engine or
wing contact, successive wave encounters — inside one otherwise prolonged deceleration. A count is
meaningless without the threshold that produced it, so the threshold is specified here and will be a
declared constant in `run.toml` rather than a literal in the code.

It is a threshold on two things jointly, and both are needed: a local maximum of `P(t)` counts as a
pulse when it **exceeds a stated fraction of `energy_transfer_peak_rate_w`** and is **separated from
the previously counted peak by a stated minimum interval**. The amplitude test alone counts
numerical ripple; the separation test alone counts a slow shoulder as a second event.

Both constants are reported with any figure that uses the count, and a run that changes either
produces a different quantity under the same column name. Until `P(t)` exists the column is NaN and
the constants are unset — deliberately, so that no default silently becomes the convention.

## 7. What a source model can rely on today

| available now | from |
|---|---|
| contact time and position | `ImpactView.unix_s`, `latitude_deg`, `longitude_deg` — solved crossing, not step-quantised |
| contact velocity vector, ground-relative | `velocity_east_mps`, `velocity_north_mps`, `velocity_up_mps` |
| flight-path angle at contact | `flight_path_angle_deg`, positive descending |
| mass at contact | `mass_kg` |
| total and vertical kinetic energy at contact | `kinetic_energy_j`, `vertical_kinetic_energy_j` — an **upper bound** on energy transferred |
| heading and bank at contact | `impact_heading_deg`, `impact_bank_deg` latents |
| whether the sample is a completed descent | `timed_out` latent |

Not available, and NaN rather than approximated: the six energy-transfer columns of §5.

A closing caution that belongs on this side of the interface as much as the other: energy and
duration together do not determine pressure amplitude, spectrum or directivity. Two impacts with
identical `kinetic_energy_j` and identical `energy_transfer_tau90_s` can radiate materially
different signals, and nothing in this module's output should be read as though they could not.
