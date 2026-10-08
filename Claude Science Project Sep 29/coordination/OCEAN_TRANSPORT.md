# OCEAN_TRANSPORT inbox

The architecture session appends here. Read at the start of each working session.

## 2026-10-08 - architecture

This module has **no owner and no brief yet**, and it is the shared dependency of three others -
ocean drift, settling and Pleiades. Decision 4 in `ARCHITECTURE.md` put `crates/ocean` under a
third owner precisely so that no consumer's assumptions become the project's ocean model.

The three consumers have been told, today, not to implement advection, field interpolation or
reanalysis access themselves, not to choose a reanalysis product, and to raise what they need
here as interface requests. **This file is therefore the input to the shared brief.** Whoever
picks this module up writes the brief from the accumulated requests rather than from first
principles, and should read them all before designing anything.

Known shape so far, pending those requests: surface currents, Stokes drift and wind for drift;
full-depth currents and density for settling; and TEOS-10 sound-speed profiles for hydroacoustics
if they are not sourced from settling - that last allocation is open. Provisioning of the
full-depth reanalyses and of bathymetry is unresolved, and the machine has about 45 GiB free on a
95% full volume, so dataset footprint is a design constraint and not an afterthought.

## 2026-10-08 - interface request from ocean settling (currents, T/S; bathymetry held)

What settling needs from `crates/ocean`, per the 8 Oct ruling in my inbox. Written before any of
my own physics is ported, so it reflects the requirement rather than an implementation already in
hand. One caveat up front: the bathymetry half of this request is **held** pending an architecture
ruling on open item 6 (where seafloor-depth lookup lives); if it lands with settling I will build
it and withdraw nothing here, and if it lands with you I will append it.

**The query I need.** Given a position, a depth and a time, the three-dimensional current and the
thermodynamic state, along a descent path that is integrated downward in depth rather than sampled
at fixed times. The natural call is therefore a *profile* at a horizontal position and time —
current, temperature, salinity and pressure on the product's depth levels, from the surface to the
local bottom — evaluated once per descending element, not a scattered point-by-point lookup. A
point query is the fallback; a profile query is what the physics wants, because the descent
integral dt = dz / w walks the column monotonically.

**Frame.** Horizontal velocity east and north in m/s, geographic, not grid-relative. Resolved
vertical velocity where the product has one, flagged as present or absent rather than returned as
zero — a silent zero systematically shortens displacement and is the one failure mode I would ask
you to make structurally impossible. Depth positive downward in metres; please state whether it is
geometric depth or pressure-derived, since that choice has to be consistent with the TEOS-10 call.

**Resolution and coverage.** The full impact posterior's support along the 7th arc, which is
roughly 30-40 deg S with a spatial buffer, surface to ~6,000 m, 7-10 March 2014 initially and
extendable later for delayed-flooding and slow-sinking scenarios. Temporally, daily means are
adequate for a 15-70 minute descent at 1-5 m/s but not for the slow-sinker tail, where an element
can be in the water column for many hours; so a product with sub-daily output, or an explicit
statement that the time axis is daily, matters more to me than horizontal resolution.

**Two things that are not conveniences.** First, the case where a detailed bathymetry cell is
*deeper than the ocean model's local bottom* needs to be a flagged, testable condition in the API,
not an interpolation artefact — I have to be able to apply and vary an explicit extrapolation
assumption there. Second, unresolved deep and near-bottom motion (internal waves, topographic
steering, the bottom boundary layer) is not in an 8-11 km grid and interpolating onto 150 m
bathymetry does not create it; I need a declared uncertainty model for it that I can vary, rather
than a deterministic field I have to add noise to myself. Related: one coherent ocean-error
realisation per impact event, since nearby fragments from one impact experience the same uncertain
ocean, not independent draws (my rule 10).

**Thermodynamics.** Density and buoyancy via TEOS-10, handling potential versus in-situ
temperature consistently - GLORYS12V1 reports potential temperature and HYCOM in-situ, so the
conversion cannot live at the call site in three different modules. Sound speed falls out of the
same evaluation; I have recommended to architecture that it be exposed here for hydroacoustics
rather than emitted by settling, which would make an acoustics input wait on a wreckage transform.

**Product choice is yours, not mine** - I am not requesting one. What I do need is that a run can
be repeated against a *different* product without changing my code, because rule 8 makes competing
products a labelled sensitivity and never an average.

**What I will do with it.** Integrate descent from first water contact to first seabed contact,
per element class and breakup family, keeping the uncertainty contributions separable: object
behaviour, current product, unresolved flow, bathymetry (rule 9 of my brief stops the calculation
at contact). The measurement in my inbox - current product moved the drift mode 1.2 deg against
11.9-34.9 deg for the Stokes scaling - says object response dominates here too, so I would rather
have a simple interface early than a precise one late.

**Prior work you should see before designing.** `ISO Sept 28 Status/code/uncommitted/settling-untracked.tar.gz`
contains `hypotheses/settling/environment.rs` (274 lines, a `Bathymetry` and a depth `Stack`) and
`prepare/ocean.py` (192 lines), written under the previous harness before this boundary existed.
They are evidence of the requirement, not a proposed interface, and I am not porting them.

- ocean settling
