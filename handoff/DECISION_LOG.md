# Decision log

## D-001 — Integrated rather than sequential point estimates

**Decision:** Combine BTO, BFO, received power, aircraft performance/trajectory,
drift and later search evidence within an integrated Bayesian framework.

**Reason:** Each observable is model-mediated and has correlated uncertainties;
sequential hard filtering can suppress valid trajectory families.

## D-002 — Stage-one cutoff at 00:11 UTC

**Decision:** Begin near the 18:11 radar position and end the initial airborne
estimator at the 00:11 arc.

**Reason:** The interpretation of the 00:19 data is entangled with end-of-flight
dynamics and should not prejudge the airborne solution.

## D-003 — No uncontrolled-flight prior assumption

**Decision:** Allow controlled flight, early descent, glide and ditching in both
airborne and terminal priors.

**Reason:** A pilot intending a controlled ocean arrival might descend before
fuel exhaustion and could travel substantially beyond the seventh arc.

## D-004 — Refine random BFO sigma separately from bias

**Decision:** Estimate fast BFO noise from within-cluster successive differences
without adding slow/intermittent bias variance in quadrature.

**Result:** Pooled sigma approximately 0.995 Hz.

## D-005 — Marginalize drift

**Decision:** Use a model-averaged/marginalized drift likelihood rather than a
single deterministic drift path.

## D-006 — Present Pleiades as a conditional analysis

**Decision:** Produce separate results with and without the assumption that the
Pleiades objects are MH370 debris.

**Reason:** No defensible probability/base rate is available for the premise.

## D-007 — Expand terminal seed area beyond the seventh arc

**Decision:** Bound terminal possibilities using aircraft maximum glide and
wind/performance feasibility, not the historical search-area mask.

## D-008 — Preserve no-precompensation sensitivity

**Decision:** Run the integrated estimator with no terminal power
precompensation as a substantive alternative.

## D-009 — Search coverage is probabilistic

**Decision:** Assimilate searched areas as uncertain detection fields. Assign
zero wreckage-detection value to ordinary bathymetric mapping and avoid hard
masks for sonar campaigns with uncertain swaths or holidays.

## D-010 — Pulau Perak as sensitivity, not fact

**Decision:** Test the combined radar loss/regain, disputed altitude label and
eyewitness report as a descent/re-climb scenario.

**Result:** Small net fuel and posterior effect under the tested anchoring.

## D-011 — Migration architecture

**Decision:** Preserve an immutable full snapshot plus a curated private
GitHub/Git-LFS working repository, exported conversation history, explicit
handoff dossier and locked environment.

**Reason:** Git alone does not preserve prior discussion, transient workspace
state, provenance or assurance that every binary transferred intact.

