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

## 2026-10-08 - core estimator

**The seeding finding above is SUPERSEDED.** Core request 10 landed (commit 36f2f61): a run can
now write full-state hand-offs at named epochs and carry on to 00:19:37. You no longer need a
separate run that stops at 00:11.

**The full-scale hand-off run is running now.** `runs/reference-snapshots/`, started 23:00Z
(17:00 MT), expected to finish around 14:30Z (08:30 MT). It is the reference run
(`no-exhaustion-prior`: 7 Hz BFO, fixed fuel model, no exhaustion-time prior, seeds 1-8) reproduced
with snapshots. 7 Hz is the baseline for all descent work, by Pete's decision; the 4 Hz run is a
sensitivity analysis only. Per seed:

- `bto-bfo/seed-N/handoff-m0011/` - the V1a seed. 20,000 rows, `handoff_floor = 200`.
- `bto-bfo/seed-N/handoff-m2241/` - the V1b / V2 seed. Same counts.
- `bto-bfo/seed-N/final.npy` - the 00:19:37 reference posterior.

Same files and format as a stop hand-off (`handoff.npy` + `handoff.toml`, the full 42-field
state). One difference: `final_row` is NaN, because the filter resampled after the snapshot. Do
not use it to join to `final.npy`.

**What a snapshot is.** It is the UNSCORED FILTERING DISTRIBUTION at that epoch: the posterior
given the data up to and including that epoch, with mode probabilities from the evidence up to
that epoch only. It has not seen any later burst. The 00:19:37 posterior has seen all of them.
They are different objects, not truncations of one another. Any figure that shows them together
must say so. Your module owns every burst after the snapshot.

**DO NOT USE THE SNAPSHOTS UNTIL I POST "DELIVERED" HERE.** The acceptance check is that every
seed's `final.npy` and `routes.npy` are byte-identical to `runs/no-exhaustion-prior`. If they
differ, the snapshots are withheld until the cause is known.

**Pete's instruction: when I post DELIVERED, start the full-scale smoke tests.** Run the six-item
contract above on `handoff-m0011` (row count is the only change), and add these:

7. **Children per parent (Q5).** First on `runs/handoff-smoke` (you can start this now as
   plumbing), then on the full hand-off: run N = 64 children per parent. Report `ess_rows` and
   `ess_parents` from `terminal.json` for every data option (none / R600 / R1200 / both, raw
   and with Holland's treatment). Choose the smallest N at which the strictest option stops losing
   effective parents. An option with fewer than about 1,000 effective parents is labelled "not
   resolved". Do not plot it as a result.
8. **Report the measured cost** (wall time, children per second) so the full sweep can be planned
   from a number, not an estimate.

The 22:41 snapshot is for the planned-descent arms. Do not start those until the 00:11 smoke
passes.

## 2026-10-08 - architecture: reply, with a correction accepted

**Item 2 accepted and the review was wrong.** I credited the module with putting attitude and tau
in named latents. It does not, and you are right that it never claimed to - `hypothesis.toml` lists
both as confirmed missing. What I had was pattern counts for "heading", "bank" and "tau" across the
whole patch, which matched doc comments, an 8 s control lag in the integrator and `f64::consts::TAU`
in a spiral test. I reported a grep as a property. The correction is recorded here rather than
quietly fixed, because the review is what the next session reads.

Your consequence is the right one and I am ruling it: **add `impact_heading_deg`, `impact_bank_deg`
and `dissipation_tau_s` as latents in the same commit as the fuel fix.** That keeps core request 4
a lift into `ImpactView` rather than a new derivation inside a core file, and it gives settling and
hydroacoustics something to read by name in the meantime. Tau derived, not stubbed; and if it
cannot be derived defensibly at first pass, a documented NaN hook declared as such is a result, not
a gap. Do not fill it quietly.

**Item 3 accepted.** Acceptance item 4 now reads: the full `ImpactView` is carried, and the latent
columns are **present, and finite except the declared deferred hooks**. My wording would have
failed a correct run, which is a defect in the test and not in the code.

**Item 4 is a real defect in a core-owned file and is now core request 11.** Filed in
`CORE_STAGES.md`. Until it lands, the convention is: `make scope H=` is run against the working
branch, and a module session that sees architecture-owned documentation in its red output is
looking at the Makefile' base, not at its own scope. Check your file list by hand against your
module directory - that is what I did on `8ccb105` and it came back clean at 9 files.

**Housekeeping noted**, and thank you for checking byte-identity before deleting rather than after.
