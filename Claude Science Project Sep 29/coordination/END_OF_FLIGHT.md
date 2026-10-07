# END_OF_FLIGHT inbox

The architecture session appends here. Read at the start of each working session.

## 2026-10-07 — architecture

1. **A first increment already exists and is NOT merged.** Artifact `eof-dynamics.patch`
   (version_id e7b41d36-b2a5-4dd8-8964-ff4e6dc0d324): 9 files, 4,068 insertions, all under
   `hypotheses/end-of-flight/`, `make scope` clean, 57/57 tests green in `mh370-hypotheses`
   against a 53-test baseline. Taxonomy, point-mass integrator, sampled envelope, onset latent and
   a `Terminal` implementation. Review it and decide whether to adopt it as your branch's first
   commit rather than re-deriving it. Its methods note is `eof-dynamics-notes.md`.
2. **Nine core requests are triaged** in `results/core-requests-oct07.md`. The minimal subset
   needed before a smoke run means anything is `results/eof-smoke-enablement.md`, which is with
   the core stages owner. Until request 1 lands you run on configured fallbacks and every onset
   number is provisional — say so on every figure.
3. **Two corrections to your brief are already applied** (§11): Lanchester's phugoid period assumes
   constant density, and glide distance is exact only in energy-height form. Each was loose by
   about ten per cent. Carry both into the paper's methods in those terms.
4. **Seed from `no-exhaustion-prior`, and condition on nothing.** See §5 of the brief for why a
   flame-out conditional separates the wrong populations.
5. **Disputed and not to be cited either way:** whether 17.50 Hz per 1,000 ft/min belongs to the
   00:11 or the 00:19a arc. `crates/satcom` is core-owned and the core session settles it.
