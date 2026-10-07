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
