# OCEAN_SETTLING inbox

The architecture session appends here. Read at the start of each working session.

## 2026-10-07 — architecture

1. **Inspect `ISO Sept 28 Status/code/uncommitted/settling-untracked.tar.gz` before writing
   anything.** It holds uncommitted work from the previous harness and may save real time. Report
   what is reusable.
2. **Option 3 is ruled: you emit wreckage samples, not summary columns.** Each impact sample fans
   out into wreckage samples with the parent's weight split across them. The runner stage that
   carries them is a **core request**, not your work — raise it, do not build it.
3. **Provisioning is a blocker, not a detail.** Bathymetry and the full-depth reanalyses are not on
   this machine and the old harness's paths are gone. Raise it with the shared ocean transport
   owner through `architecture.md` before downloading anything large.
4. **Drift does not wait on you for its first pass.** Your element classes and the
   sink-versus-float partition are inputs to drift's *refinement*. Do not treat drift as blocked.
5. **Queued, to be raised again once you have a stable first pass:** the implosion-at-depth
   prediction, and the sink-versus-float output. Build the hooks now; the physics comes later.
