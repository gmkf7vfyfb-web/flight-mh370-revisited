# Architecture inbox

Module sessions append here. Newest last.

## 2026-10-08 — end of flight

Review of `8ccb105` read and accepted. Four items back, one of which is a correction.

**1. The defect is confirmed independently.** `lib.rs:288-291`: `predicted_exhaustion_unix_s` is
taken from `state.fuel_exhaustion_unix_s` when finite and otherwise from
`fallback_predicted_exhaustion_unix_s`, which `run.toml` sets to `1394237850.0` — 00:17:30 UTC.
Since `f07e9f0` renamed the field to `realised_flameout_unix_s`, and that value is NaN for every
trajectory not yet dry at the hand-off, the fallback is the live path for about 43% of the
posterior. Nothing records it: `mass_assumed` covers the mass fallback only. Taking the fix as
specified — predicted exhaustion derived per trajectory from `fuel_kg` and a cruise fuel flow,
with the reference run's 5,764 kg/h as the sanity bound — plus a latent per fallback and the
acceptance rule that on a real hand-off no fallback may fire.

**2. Correction: attitude and tau are NOT in named latents.** The review credits the module with
putting "attitude, tau and debris class in named latents". Only two of those exist. The `LATENTS`
const at `lib.rs:197` has 27 entries; `debris_class` and `sinks_not_floats` are there, attitude
and tau are not, and neither appears anywhere else in the module — the only `tau` in the tree is
an 8 s control lag at `integrator.rs:375` and `std::f64::consts::TAU` in a spiral test. The
module's own `hypothesis.toml` says the same: core request 4 lists attitude and tau as "Confirmed
missing" and scopes the latents to "the last two".

Two consequences. Smoke acceptance item 4 — `impacts.npy` carries attitude and tau — cannot be
met by core request 4 alone, because there is no module-side quantity for request 4 to lift. I am
therefore adding `impact_heading_deg`, `impact_bank_deg` and `dissipation_tau_s` as latents in the
same commit as the fuel fix, so that request 4 stays a lift-into-`ImpactView` rather than a new
derivation, and so hydroacoustics and settling have something to read by name meanwhile. Tau will
be derived, not stubbed; if it cannot be derived defensibly at first pass it ships as a documented
NaN hook and is declared as such rather than quietly filled.

**3. Acceptance item 4 needs one word changed.** It asks that "the 27 latent columns are present
and finite". Two of the 27 are the deferred hooks and are always NaN by design, which is the
behaviour §2 of the brief asks for (NaN means "not computed"). Suggest "present, and finite except
the deferred hooks", so a correct run cannot fail its own acceptance test.

**4. `make scope H=end-of-flight` is measured against the wrong base.** The target diffs
`main...HEAD`, and `main` is behind the working branch, so on a module branch cut from
`claude-science-sep29` the check fails and lists architecture-owned documentation — `ARCHITECTURE.md`,
the four master prompts, `results/waypoint-stratum-spec.md` — as out of scope. Against the actual
base it is clean: 9 files, all under `hypotheses/end-of-flight/`. `engine/Makefile` is core-owned
so I have not touched it. Either it takes a `BASE` variable defaulting to `claude-science-sep29`,
or the convention records that module sessions run the check against the working branch; a module
session that trusts the red output will think it has broken scope when it has not.

**Housekeeping.** Before the review reached me I had pushed the same patch as
`eof/dynamics-oct08`. Its module tree is byte-identical to `hypothesis/end-of-flight`; the branch
is deleted and I am working on yours.

**Not waiting for core.** Taking the smoke hand-off at `runs/handoff-smoke/bto-bfo/seed-1/` as
advised. The full-scale snapshots change the row count and the effective parent count, nothing
else in the contract.

## 2026-10-08 — end of flight, second entry

**The dissipation duration tau now has a written definition:
`results/impact-energy-transfer-tau.md`.** Pete asked for it in writing so that hydroacoustics and
settling rule on a specification rather than on a forwarded conversation. Summary of what it fixes
and what it leaves to you.

Settled inside this module, and implemented as part of the fuel-state fix:

- The field is `impact_energy_transfer_tau90_s` — the interval containing the central 90% of the
  mechanical energy transferred during the initial water-entry event, with `impact_tau_method`
  beside it. The percentile convention is in the field name on purpose: a bare `tau` would change
  meaning silently if the convention were ever revised, and runs either side would become
  incomparable.
- It is "energy transfer", not "dissipation" — energy into wave motion has left the aircraft
  without being irreversibly dissipated. The brief's wording is kept only as the pointer.
- It ships NaN for now. The integrator terminates AT the sea surface, so `P(t)` is the power
  history of an event this module does not simulate. The `tau = delta_v / a_bar` shortcut needs a
  justified `a_bar`; choosing one to make nosedives short and ditchings long would be circular.

Two properties in that note are load-bearing rather than stylistic, and I would like them ruled
rather than merely noted:

- **tau is computed from the impact state, never from the family label.** Assigning it per family
  would make the hydroacoustic likelihood a function of this module's family prior, so that prior
  would enter the posterior twice. That is a composition-rule violation, not an approximation. It
  also contradicts §12 of my brief: a ditching-like impact is not evidence of a ditching.
- **tau is deterministic given state, not an independent latent.** An independent draw invites
  oversampling long-tau events to give hydroacoustics more signal, which breaks the §8 weighting
  rules in a way that is close to undetectable downstream.

**Two questions that are yours, not mine.**

1. **Scalar, or a fixed number of energy-transfer bins?** A long event can contain short intense
   pulses, and one scalar cannot separate one pulse from several. A time history is the natural
   fix and §2 forbids it — the impact sample is not to be variable-length. Proposal: a fixed,
   small number of bins alongside `tau90`, ruled once as an interface constant, same pattern as
   the debris class. Until you rule, the field is a lone scalar and no consumer should build
   against a history that does not exist.
2. **Who owns the water-entry model?** Settling already conditions on vertical and total kinetic
   energy plus flight-path angle, so the energy-transfer physics sits between my impact state and
   its breakup families. Wherever it lands it should be one model with one declared parameter set,
   read by both consumers rather than built twice.

Bibliography is in the note and all three references were verified against arXiv and Crossref
rather than quoted on trust. Worth knowing that two of the three share authors, so the
experimental base for high-speed ditching hydrodynamics is one group's programme — any `a_bar`
drawn from it wants generous declared uncertainty.
