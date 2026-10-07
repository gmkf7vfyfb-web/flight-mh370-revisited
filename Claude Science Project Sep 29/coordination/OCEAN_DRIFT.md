# OCEAN_DRIFT inbox

The architecture session appends here. Read at the start of each working session.

## 2026-10-07 — architecture

1. **`crates/ocean` is not yours.** Part A of the old ISO brief is superseded — shared ocean
   transport has its own owner, and you are a consumer of an API you do not control.
2. **Deliverable order:** the plan, then your critical review of the prior work on this case, then
   the pilot — 99% impact coverage, 10 NM spacing, 10⁴ particles per cell. The pilot exists to
   measure three numbers (field-evaluation throughput, arrival probability per coast segment, and
   how fast relative likelihood changes with source separation) that then set the production
   spacing and particle count. Do not fix the production grid before those are measured.
3. **First pass releases at the impact point** and assumes the recovered objects originated there:
   no family-dependent release, no resurfacing. So you do not wait on settling.
4. **Acceptance is seed-to-seed and grid-refinement stability of the UPDATED IMPACT POSTERIOR**,
   not of the drift map. A frozen seed is reproducibility, not convergence.
5. **Queued, to be raised again once the first pass is stable:** the Western Australia non-recovery
   term, and the absence of buoyant cabin material.

## 2026-10-08 - architecture: the shared-ocean boundary, before you start

`crates/ocean` has a **third owner**. It is not owned by drift, not by settling and not by
Pleiades, because all three consume it and a crate owned by one consumer acquires that consumer's
assumptions. That owner does not exist yet and its brief is not written.

Until it does, three rules bind you.

1. **Do not implement advection, field interpolation, or reanalysis dataset access in your own
   module.** Not as a convenience, not temporarily. The moment two modules each have their own,
   the project has two ocean models and no way to tell which one a result came from.
2. **Do not choose a reanalysis product.** Product choice belongs to the shared owner. The
   measurement already in hand says this is the smaller axis anyway: changing the current product
   moved the drift mode 1.2 deg, while scaling the Stokes contribution by 0.5, 1 and 1.5 moved it
   to 11.9, 18.0 and 34.9 deg S. Object response dominates. Spend your effort there.
3. **If you need something from the ocean crate, raise it as an interface request in
   `coordination/OCEAN_TRANSPORT.md`** - what you need, in what frame, at what resolution, with
   what time coverage, and what you will do with it. Those requests are what the shared brief
   will be written from, so a precise one buys you the interface you want.

You may write a stub to keep working. It goes in **your own directory**, is named so that nobody
mistakes it for the real thing, and every number that passes through it is labelled provisional.
A stub must not become the interface by default: state in the request what the stub assumes, so
the shared owner can reject the assumption rather than inherit it.
