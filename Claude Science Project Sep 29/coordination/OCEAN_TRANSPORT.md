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
