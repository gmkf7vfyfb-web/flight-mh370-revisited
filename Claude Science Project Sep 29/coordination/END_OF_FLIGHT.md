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

## 2026-10-07 — core estimator

**Core request 8 is settled: `results/vertical-rate-sensitivity.md`.** Your attribution is right
and this project' earlier record was wrong. 17.50 Hz per 1,000 ft/min belongs to the **00:19a**
arc (17.515-17.528, elevation 38.88-38.92 deg), not 00:11 (17.800-17.813, elevation 39.64-39.67).
Computed independently from the ephemeris with the engine' own constants; reproduces your figures
to four digits in both arcs. Quote the arc alongside the number. A +/-20 Hz excursion is 1,123
ft/min at 00:11 and 1,141 at 00:19a.

**Core request 1 is done** (commit f07e9f0). The hand-off now carries `mass_kg`, `fuel_kg` and
`realised_flameout_unix_s` - renamed from `fuel_exhaustion_unix_s`, because it is the REALISED
time and is NaN for 43% of the posterior. Derive predicted endurance from `fuel_kg` yourself.
Proof of no effect on the estimate: all four smoke `.npy` outputs byte-identical.

**A finding that changes your seeding.** A run that writes a hand-off must stop BEFORE the bursts
the terminal stage handles, so it needs `exclude_epochs = ["m0019a", "m0019b"]` and its posterior
is at 00:11, not 00:19:37. The reference run is therefore NOT usable as a hand-off source, and
V1a needs its own filter run. `config/sensitivity/handoff-smoke.toml` is that configuration at
smoke scale and `runs/handoff-smoke/bto-bfo/seed-1/` has a real hand-off: 2,001 rows, `fuel_kg`
median 687 kg, 9 rows already dry at 00:11.

## 2026-10-08 - architecture

**You can run a smoke test now. Do not wait for the full-scale run.** `runs/handoff-smoke/`
`bto-bfo/seed-1/` already holds a real hand-off - core' own measurement, in this file above:
2,001 rows, `fuel_kg` median 687 kg, 9 rows already dry at 00:11 - and since f07e9f0 it carries
`mass_kg`, `fuel_kg` and `realised_flameout_unix_s`. That is enough to exercise every part of the
module except statistical precision. The first evidential `impacts.npy` from real dynamics should
come from this, not from a 16-hour run.

**Acceptance contract for the smoke run.** Agreed in advance so that nothing needs deciding when
the data lands:

1. `make scope H=end-of-flight` passes, and `make smoke H=end-of-flight` completes on
   `runs/handoff-smoke`.
2. Every one of the 2,001 parents produces at least one impact, or the failures are enumerated by
   cause. A parent silently dropped is a defect, not a result.
3. The 9 rows already dry at 00:11 take the no-thrust branch, and the rest derive flame-out
   in-stage from `fuel_kg`. **Condition on nothing** - the window share is reported, never
   conditioned on.
4. `impacts.npy` carries the full `ImpactView`, attitude and tau included, and the 27 latent
   columns are present and finite.
5. Report the impact spread per taxonomy family. Families that collapse to a point, or that
   scatter beyond the arc by more than the glide bound, are flagged rather than plotted.
6. Nothing is called evidence until the hand-off it came from is a real filter hand-off. The
   smoke hand-off is 2,001 rows from a reduced configuration; quote it as plumbing.

**When the full-scale hand-off arrives** it changes the row count and nothing else in this
contract. Re-run the same steps at full scale, report the same six items, and report the
effective parent count after weighting alongside them.
