# Release notes — corrected v0.1 broad-flight milestone

Release v0.1 freezes the first reproducible, end-to-end checkpoint of the
canonical broad powered-flight filter with multiple control modes and repeated
maneuver events. The milestone records both what now works and why the current
calculation must stop short of a location claim.

## Scientific outcome

The MH371 known-flight diagnostic and the MH370 accident-flight diagnostic are
both complete across their configured seeds and evidence families. Both pass
the release validator's provenance and model-closure checks. Both independently
fail the reporter's numerical-support criteria and are marked
`FAILED NUMERICAL SUPPORT — DIAGNOSTIC ONLY`; neither is publication eligible.

The consequence is unambiguous: v0.1 publishes no MH370 coordinate, crash-site
posterior, terminal/impact distribution, credible search box, or operational
search recommendation. The failure is itself a release result, not a gap to be
filled with an older narrow calculation.

Exact status, per-epoch diagnostics, and any MH371 accuracy values live in each
native `broad_snapshot_diagnostic.json`. Human documentation deliberately does
not copy those changing metrics.

## Canonical inference now represented

- `estimate-broad-flight` is the release runner.
- `broad-powered-marked-jump-v1` is the required model family.
- Five initial lateral modes are explicit structural alternatives.
- Four maneuver-rate families are explicit structural alternatives.
- Lateral, target-speed, and target-altitude events can recur independently.
- BTO-only and BTO-plus-BFO remain separate evidence families rather than being
  blended into a synthetic preferred posterior.
- Multiple deterministic seeds expose numerical and genealogical instability.
- Powered-flight feasibility, environmental coverage, units, time bases, and
  source identities remain configuration- and manifest-bound.

The equal weights over modes and rate families are declared sensitivity
weights. They were not learned from representative flights and must not be
called calibrated probabilities of pilot or automation behavior.

## Reporting and audit changes

- The runner can export a manifest-hashed snapshot population at every
  observation and physical checkpoint.
- The broad snapshot reporter consumes only those exported populations,
  per-seed summaries, its report specification, and optional held-back truth.
- The reporter shows every epoch, family-specific observation role, recurring
  event counts, particle and root ESS, seed spread, and per-mode/per-rate
  spatial sensitivity.
- Physical BFO-only rows remain visible as propagation-only,
  likelihood-disabled checkpoints in the BTO-only family.
- With MH371 truth, the reporter adds per-epoch distance and coverage only
  after the inference run. Without truth, it makes no accuracy claim.
- The release configurations suppress the runner's ungated built-in spatial
  reports. Only the fail-closed snapshot report is exposed as a current view.
- The release validator verifies the broad model, exact binary and config,
  complete family/seed output set, snapshot hashes, report provenance, truth
  role, and publication gate.

Validator success and numerical success are intentionally distinct. A valid
release can preserve a failed diagnostic without presenting it as a posterior
location product.

## MH371 control boundary

The MH371 inference bytes contain no later aircraft truth, and the reporter is
the only component that opens `inputs/controls/mh371-truth.csv`. The control is
not fully prospective, however: after pilot inspection, the final window was
moved from 06:59 to 06:48 to avoid the known descent turn. The selected window
is partly truth-informed. MH371 scores therefore diagnose this particular
experiment; they do not calibrate general MH370 coverage.

MH371 has no exposed fuel anchor. Its source fuel and mass values are explicit
conditional priors, not MH371 measurements. Fuel-exhaustion selection and
persistent fuel-exhaustion twists are disabled for that control.

## Context included with the capsule

The capsule exposes the Davey et al. paper and its independent recreation
materials as reference context. It does not expose the stale
canonical-versus-Davey plot as a current comparison because the canonical side
of that plot came from the withdrawn one-turn chain.

It also exposes a search-evidence atlas assembled independently of the flight
posterior. The atlas distinguishes official footprints, reported totals,
display geometry, and approximate contextual outlines. It supplies neither a
calibrated negative-search likelihood nor a replacement search ranking.

## Deliberately withheld or excluded

- terminal fuel-exhaustion, flameout, descent, glide, impact, drift,
  hydroacoustic, and debris-image inference downstream of the unresolved broad
  filter;
- any crash coordinate, impact credible region, or search box;
- the old MH371 medium-BFO and final-arc sensitivity products;
- the old MH370 00:11 BTO/BFO/gain PDFs;
- the R600 frozen continuation and seventh-arc result;
- downstream impact-family and full-overview PDFs;
- the old canonical-versus-Davey latitude comparison; and
- baseline search-planning surfaces and selected tiles derived from the narrow
  impact chain.

Historical source packages may retain some of these files for audit, but they
are excluded from curated release views and must remain explicitly labelled as
superseded.

## Supersession notice

The earlier package also labelled v0.1 is withdrawn. A release-selection
regression allowed artifacts from the one-turn/frozen-continuation
implementation to satisfy the older package manifest. Although those artifacts
were repeatable under their narrow assumptions, they did not represent the
current broad technique and conveyed false precision when presented as such.

This corrected capsule is identified by its byte hashes, native manifests, and
release validations—not by the `v0.1` filename alone. Never repair or complete
it by importing a file from the withdrawn package.

## Remaining work after v0.1

Future work must improve particle/root support and independent-seed agreement
without collapsing structural families, then repeat the known-flight test
under a prospectively fixed selection protocol. Only a numerically supported
broad powered-flight population can be considered for separately validated
terminal/impact and search-detection work.

