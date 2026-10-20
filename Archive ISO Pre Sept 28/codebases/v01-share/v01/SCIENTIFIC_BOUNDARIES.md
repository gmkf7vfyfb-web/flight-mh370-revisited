# Scientific boundaries of release v0.1

Release v0.1 is a reproducible checkpoint of a broad powered-flight particle
filter. It is designed to show how much the answer changes when unsupported
single-mode and single-turn restrictions are removed. It is not a declaration
that the remaining model choices constitute the aircraft's calibrated “true
uncertainty.”

## What is measured, declared, and calculated

| Class | Included here |
| --- | --- |
| Frozen observations | Selected SATCOM BTO and, in a separate family, BFO; satellite ephemeris; the exposed source state; frozen environmental grids |
| Declared model choices | Powered-flight limits, fuel/mass priors, five initial lateral modes, four recurring-event rate families, event-mark distributions, observation error models, resampling policy, and fixed plotting bounds |
| Calculated outputs | Conditional filtering populations, evidence-component scores, mode/rate posterior mass, recurring-event counts, particle and root ESS, independent-seed spread, display-smoothed spatial support, and MH371 held-back-truth diagnostics |

A published paper's conclusion is not treated as a measurement. Every
probability in the broad report is conditional on its named evidence family and
the declared model support.

## Control-history uncertainty

The runner does not assume one control law or one turn. Each configuration
declares equal, empirically uncalibrated prior weight over five initial lateral
modes:

- constant true heading;
- constant magnetic heading;
- constant true track;
- constant magnetic track;
- great-circle continuation.

It separately declares equal, empirically uncalibrated prior weight over four
recurring-event rate families. In every rate family, lateral, speed, and
altitude commands can renew repeatedly and independently. A lateral renewal can
reselect any of the five lateral modes and can draw over the configured course
change support. These are explicit structural alternatives, not random error
around a single preferred route.

The five-by-four support is broader than the superseded one-turn model, but it
is still a model. The equal weights and renewal rates have not been learned
from a representative population of comparable flights. Unmodelled pilot
intent, automation faults, aircraft damage, configuration changes, and other
control histories can remain outside support.

## Evidence families remain separate

Both flights are reported as two top-level scientific families:

- BTO only;
- BTO plus BFO using the declared published-error width.

These families are not pooled into a synthetic “best” posterior. Deterministic
seeds are combined with equal numerical weight only within the same evidence
family. Differences between evidence families, initial modes, and maneuver-rate
families are structural sensitivity and must not be described as Monte Carlo
sampling error.

Some MH370 rows contain BFO but no active BTO likelihood in the BTO-only
family. Those physical epochs are retained as propagation-only checkpoints and
are explicitly labelled `likelihood disabled`; they are not silently dropped
and are not pretended to be BTO updates.

## Filtering, not hindsight smoothing

Each page is built from the population immediately after the named physical
epoch. Later observations are not used to rewrite earlier pages. The maps are
therefore filtering diagnostics rather than smoothed full-flight trajectories.
Display density is kernel-smoothed for legibility; all reported masses,
effective sample sizes, truth errors, and coverage values use unsmoothed
particle weights.

## Numerical support is allowed to fail

The reporter evaluates particle ESS, prior-root ESS, maximum root mass,
material-stratum ESS, fixed-map captured mass, and between-seed spatial
agreement at every reported epoch. It fails closed when the configured support
is not represented reliably.

The companion release validator answers a different question. A validator
pass means that the broad model, producer, inputs, complete family/seed output
set, snapshot hashes, reporter source, and report outputs form one consistent
provenance chain. It does not override the report's numerical-support result.
Consequently, a fully valid capsule can and should retain a report watermarked
`FAILED NUMERICAL SUPPORT — DIAGNOSTIC ONLY`. Consult the authoritative
`broad_snapshot_diagnostic.json` rather than inferring status from the presence
of a PDF.

The reporter never marks these outputs as a calibrated true probability or as
publication-eligible flight-location maps. A milestone release records an
honest limitation; it does not need to hide a failed numerical assessment.

## MH371 truth separation

MH371 is a known-flight control of the technique, not evidence about MH370.
The broad runner receives no later aircraft positions. It uses only the exposed
initial state and SATCOM/satellite projections containing no later aircraft
state. The held-back file `inputs/controls/mh371-truth.csv` is opened only by
the reporter after the inference artifacts have been finalized.

This byte-level truth separation is not a claim that the experiment was a
fully prospective blind trial. A pilot inspection moved the final selected
window from 06:59 to 06:48 to avoid the known descent turn. The window and
epoch selection is therefore partly truth-informed, as recorded in
`.sources/mh371-known-flight-data/README.md`. Per-epoch control scores must be
interpreted with that design decision visible.

The MH371 report may therefore calculate per-epoch distance error and coverage
against held-back positions. Those scores diagnose this one known flight under
the declared model; one trajectory cannot calibrate general coverage for an
unknown accident flight. No MH371 position, Mach, altitude, heading, or fuel
state from the held-back interval is imported into MH370 inference.

MH371 has no exposed fuel anchor. Its source fuel and mass numbers reuse the
declared MH370 source proxy, but enter only as explicit conditional priors, not
as an MH371 measurement. Fuel-exhaustion selection guidance and persistent
fuel-exhaustion twists are disabled; no MH370 Arc-1 fuel anchor is imported.

## MH370 has no truth score

The MH370 reporter is invoked without a truth file. Its maps contain no truth
marker, distance-to-truth statistic, accuracy claim, or empirical coverage
claim. The configured Arc-1 fuel-state anchor is shown as a conditional state
reset with no positional likelihood. It does not establish a route or crash
location.

## Terminal flight and impact are withheld

This release reports powered-flight filtering through the configured final
SATCOM checkpoint. It does not extend the broad population through fuel
exhaustion, dual flameout, descent, glide, impact, drift, hydroacoustics, or
debris-image evidence. No impact distribution or operational search ranking is
released from the corrected broad run.

The search-area atlas in `views/search-areas` is independent context. Its
polygons are not a calibrated searched/not-searched mask, and no negative-search
likelihood is applied. The older planning surfaces and selected tiles depended
on the superseded narrow impact population and are excluded from current views.
They may remain as historical output inside the source annex.

## Davey material is reference context

The bundled Davey et al. paper and its source-recreation package are historical
and methodological references. The old canonical-versus-Davey comparison used
the superseded one-turn/frozen-continuation chain and is excluded from current
result views; the source annex retains it as historical output. The Davey result
is not silently imported as a prior, likelihood, or
truth value for the broad estimator.

## Environmental and source limits

ERA5 temperature and winds are reanalysis fields, not measurements at the
aircraft. IGRF-14 represents the main magnetic field and not local anomalies.
Their discretization, interpolation, altitude mapping, and frozen epochs are
documented model choices. Fuel flow and powered-flight feasibility use declared
proxy families and public-source constraints; they are not proprietary Boeing
performance tables.

Some raw MH371 workbooks are restricted and the public ERA5 store is mutable.
The capsule includes the exact normalized runtime bytes and their hashes, plus
source identities and reconstruction instructions. Reproducibility claims
apply exactly to those frozen runner inputs.
