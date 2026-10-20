# MH370 Bayesian estimator

This repository now has one product: a lean, deterministic Rust estimator for
the final flight of MH370, plus focused controls and publication-quality vector
reports. The canonical scientific path model is now
`broad-powered-marked-jump-v1`, run with `estimate-broad-flight`. It does not
assume one post-radar turn or one fixed lateral-control mode.

## Corrected v0.1 release status

The full-M0011 broad-flight calculation is numerically unresolved. Severe
particle-genealogy concentration and material between-seed disagreement mean
that its present samples do not support a releaseable geographic probability
surface. Consequently there is currently **no releaseable MH370 crash
coordinate, terminal-impact posterior, or search box** from the broad method.
Reports made from the unresolved run must be labelled diagnostic and fail
closed; a smooth map or narrow interval cannot override failed numerical
support checks.

The earlier v0.1 package was withdrawn after a release-selection regression.
Packaging selected the older one-turn runner and artifacts because they
matched the previous manifest instead of rebuilding the current broad-flight
source. That made conditional, numerically repeatable one-turn results look
like the current answer. The former package and run tree have been withdrawn;
`runs/mh370/release-v0.1/README.md` is only a tombstone pointing to the
corrected broad diagnostic.

This is a milestone release, not a claim that every physical behavior has been
calibrated. A corrected release may publish failed-support diagnostics and the
inputs needed to reproduce them; it must not manufacture precision to fill a
missing result.

| Calculation | Path model | Corrected v0.1 status |
| --- | --- | --- |
| MH370 through M0011 | Broad marked-jump powered flight | Completed across 8 seeds × 2 evidence families; failed numerical support, diagnostic only |
| MH370 terminal/impact | Broad handoff plus end-of-flight | Withheld because the parent filter is unresolved |
| MH371 truth-separated validation | Same broad marked-jump powered flight | Completed; failed numerical support and failed to recover the known flight reliably |
| MH371 legacy validation | Single constant magnetic heading | Historical regression control only |

The corrected runs use 20,000 particles per seed. At the final checkpoint,
MH370 BTO-only seeds have prior-root ESS 1.07–5.81 and maximum single-root
mass 31.6–96.6%; BTO+BFO seeds have root ESS 1.01–1.99 and maximum-root mass
54.2–99.6%. Their maximum between-seed map total variations are 0.995 and
1.000. The corresponding maximum separations between seed posterior means
are 4,673.5 NM and 1,333.6 NM. No equal-seed pooled mean is a location estimate
under disagreement of this magnitude.

The MH371 control fails in the same direction. At 06:48, BTO-only root ESS is
1.67–7.21 across seeds, maximum-root mass is 19.6–76.4%, and the equal-seed
pool puts 0.09% of mass within 100 NM of held-back truth. BTO+BFO root ESS is
1.04–4.12, maximum-root mass is 37.7–97.8%, and 14.18% of the equal-seed pool
is within 100 NM. The pooled-mean errors are 1,350.4 NM and 559.9 NM, but those
accuracy summaries are themselves conditional on numerically failed particle
populations. Passing release validation means that this failure is faithfully
bound to the broad code, inputs, reports, and hashes; it does not turn the
failed diagnostic into a publishable posterior.

## What uncertainty the technique can report

The uncertainty has three distinct parts, and reports must keep them visible:

1. **Within-family trajectory uncertainty.** Particle spread conditional on a
   specified dynamics model, observation model, and declared priors.
2. **Structural sensitivity.** Changes caused by lateral-mode, manoeuvre-rate,
   SATCOM-error, fuel, end-of-flight, or other incompatible model choices.
   Structural alternatives are reported separately or as a clearly labelled
   prior sensitivity; their spread is not ordinary sampling error.
3. **Numerical and genealogical uncertainty.** Variation among independent
   seeds, root-particle concentration, effective sample size, stratum loss,
   fixed-grid total variation, and convergence under increased computation.
   Failure here invalidates posterior-location claims even when a plot looks
   well behaved.

There is no empirically calibrated probability over unknown MH370 control
histories. Therefore "true uncertainty" cannot honestly mean a single
calibrated credible region: the broad model's trajectory probabilities remain
conditional on analyst-declared, uncalibrated structural priors and on a
dynamics family not yet validated for this use. The honest output is the
conditional spread, structural-family sensitivity, and numerical stability
together. At present the last of these fails for the full-M0011 calculation.

## Canonical broad-flight model

The current configuration declares five possible initial lateral modes:
constant true heading, constant magnetic heading, constant true track,
constant magnetic track, and great-circle continuation. During flight, three
independent renewal processes can repeatedly change lateral control, target
speed, and target altitude. A lateral event can choose any of the five modes
again and can request a course change anywhere within the declared
±180-degree support. Finite bank, roll rate, acceleration, vertical-rate,
capture, aerodynamic, and fuel limits are applied during propagation.

Four explicit manoeuvre-rate families use mean renewal intervals of 640,
2,024, 6,402, and 20,243 seconds. The v0.1 diagnostic configurations assign equal weights to
the five initial modes, equal lateral-mode probabilities after each lateral
renewal, and equal weights to the four rate families. Those weights define a
reproducible sensitivity calculation; they are analyst declarations, not
measurements or calibrated probabilities of pilot behavior. BTO-only and
BTO+BFO error treatments remain separate top-level evidence families rather
than being averaged into one posterior.

The support is deliberately much broader than the old one-turn model, but it
is still a declared model family rather than the set of every physically
possible flight. Every report must state these boundaries and the enabled
evidence.

Both v0.1 runs use seam-closed environmental grids broad enough that leaving
an old regional corridor cannot reject a control history. MH370 ERA5 and
IGRF-14 span every latitude and longitude, 500–43,000 ft, and the full run
time; MH371 spans every longitude and a conservatively proved reachable
latitude domain, 10,000–43,000 ft, and its full run time. Missing environmental
coverage is an input failure, never trajectory evidence. The manifests in
`inputs/environment/` record exact axes, hashes, regeneration checks, reach
bounds, pole caveats, and the circular magnetic-declination interpolation used
across the ±180-degree seam.

## Withdrawn one-turn release calculation (historical control only)

The following table records the former v0.1 numerical-control result so that
the regression remains auditable. Configuration:
`configs/mh370-0011-core-comparison.toml`; 30,000 particles per seed and five
seeds per evidence family. These coordinates are conditional on the obsolete
one-turn/fixed-control path family. They are **not** current location estimates,
do not bound the broad model, and must not be used to plan a search.

The obsolete coordinate table has been removed from the current product
documentation. It conveyed precision conditional on unsupported control-history
restrictions and was repeatedly mistaken for a current estimate. The frozen
historical artifacts, where retained for audit, carry their own withdrawal
notice and are rejected by corrected release validation.

Passing the old numerical checks established repeatability only for that narrow
model. It did not establish physical completeness or calibrated uncertainty.

## Historical staged one-turn controls through 00:11 UTC

These preserved historical controls used 10,000 particles across three seeds
and the medium 4 Hz BFO observation model where BFO is enabled. This entire
section documents the superseded one-turn implementation; none of its endpoint
coordinates is a current MH370 result.

The staged endpoint coordinate table is intentionally omitted here. These
controls remain useful only for testing the legacy implementation.

Each endpoint is the aircraft state at its final included SATCOM observation;
no end-of-flight displacement is applied. The 18:25 result uses its BTO at
18:25:34 UTC; the two long runs exclude the 00:19 restart observations.

The conditional gain family keeps the SATCOM model fixed, keeps the time-varying
satellite/GES correction separate from the latent aircraft BFO bias, and adds
five exact-channel regular R1200 power observations. It uses the uncommissioned
first-pass gain reconstruction at the no-precompensation endpoint, with true
ground track as an airframe-heading proxy. Restart and telephony power rows are
excluded, and the conditional family has no assigned core model weight.

Relative to the medium-BFO run, conditional gain shifts the pooled mean by only
0.75 NM but widens the marginal 90% intervals; their latitude/longitude bounding
rectangle is 37% larger. Treat that reshaping as a conditional sensitivity,
rather than evidence that the uncommissioned gain family should enter the core.

## Historical recovered-prior, continuation, and autopilot controls

Davey's numerical starting prior is at 18:01:49 UTC, not 18:11. The normal
00:11 result is one joint sequential particle inference from that radar prior
through all included SATCOM epochs; it does not replace the 18:25 posterior
with a fitted Gaussian. A separate final-radar/N571 sensitivity starts at the
published last-radar locus with a deliberately reconstructed covariance because
the public numerical radar series is unavailable.

The recovered-prior coordinate table is intentionally omitted from current
product documentation because it belongs to the withdrawn narrow chain.

The 18:25 report overlays N571, the published final-radar locus, and an
airway/BTO-constrained 18:25 reference with heading arrow. That reference is
not represented as a known fix.

The former one-turn 00:11 posterior was also continued to 00:19 in two
deliberately separate historical controls:

The 00:19 continuation coordinate table is intentionally omitted. No corrected
broad terminal handoff exists while the M0011 parent filter is unresolved.

The startup-power control excludes the 00:19 BTO and BFO, applies the documented
-3.6 dB R600-to-R1200 adjustment with 2.2 dB SD, and retains the unverified
antenna surface/no-precompensation endpoint label. Its high ESS shows that it
is weakly selective. C-channel BFO at 18:39 and 23:14 remains in the medium
SATCOM run; C-channel received power is not integrated because its regional
beam/channel offset is not identified.
### Raw final-BFO feasibility control

The two reported 00:19 BFOs can be inverted without applying a startup
correction. Conditional on the existing R600-BTO continuation, prior true track,
and no turn between bursts, the weighted medians are -4,451 ft/min at the R600
request and -14,995 ft/min at the R1200 acknowledgement. The implied change is
-10,543 ft/min over 8.027 s, or -0.680 g Earth-vertical acceleration. Ordinary
independent 7 Hz measurement error alone corresponds to about 0.037 g standard
deviation; it does not represent uncertainty from an unidentified startup
transient.

A deterministic feasibility grid over headings, five local altitudes, and turn
rates through +/-6 degrees/s cannot remove the need for rapid downward
acceleration: its minimum is about 0.647 g and occurs on the declared turn-rate
boundary. With no turn, the minimum is about 0.679 g. These are existence tests,
not probabilities or a validated 777 envelope. Adding the second, inconsistent
BTO reduces ESS from 24,324 to 7,428. Adding the conditional R600 power model
after both BTOs changes ESS only to 7,421 and changes the median dynamics by
less than 0.1 ft/min.

Reproduce the JSON summary and particle-level CSV artifacts with:

```bash
cargo run --release -p mh370-runner -- analyze-final-bfo \
  --config configs/mh370-final-bfo-raw-feasibility.toml \
  --output /tmp/mh370-final-bfo-raw-feasibility
```

The command explicitly records zero R600/R1200 channel-bias terms. The broad
heading/altitude grid, ordinary BFO error, and uncommissioned gain result remain
diagnostic and are not applied to the core posterior.

The run writes three paired vector-table controls, each with a matching JSON
artifact:

- `raw-bfo-match-tables.svg`: the original six heading by six vertical-speed
  coarse view;
- `raw-bfo-match-tables-zoom.svg`: ten 2,000 ft/min rows spanning the union of
  coarse rows that contained a match, -23,333 to -3,333 ft/min; and
- `raw-bfo-linked-match-tables-zoom.svg`: the same zoom rows after requiring a
  single continuous 8.027-second central-BFO path to connect the two epochs.

All tables use six 60-degree true-heading sectors, a 5-degree heading grid,
the same 512 weighted-posterior systematic samples, and +/-14 Hz (two ordinary
BFO standard deviations). A number in a cell is a unique-sample existence
count, not a candidate count or probability.

The linked screen propagates each candidate between transmissions, searches
turn rates in 0.5 degree/s increments, requires nonnegative altitude, limits
earth-vertical acceleration to 1 g, and applies a configured 2.5 g generic
total-specific-load screen using ground speed as a proxy. The linked marginal
counts are identical to the independent zoom counts: every sample/sector with
an instantaneous match retains at least one low-turn connected path. This is a
result of the permissive kinematic screen and coarse marginal projection, not
validation of every path or of Boeing 777 dynamics.

For the prior southbound horizontal state, the raw-BFO descent predicts a
median BTO change of +8.265 microseconds: +6.610 from horizontal/satellite
geometry and +1.655 from descending about 1,300 ft. The corrected observations
change by -20 microseconds. Across all headings at the prior particle speeds,
even the most negative constant-altitude change has median -11.315
microseconds; descent has the opposite sign. The -28.265 microsecond
prior-track mismatch is only about 0.37 standard deviations if the published
63 and 43 microsecond errors are independent, so the second BTO belongs in a
likelihood sensitivity rather than a hard dynamic constraint.

A source-reproduction warning is explicit. Large (2019) reports 1,400-1,800
ft/min, with mean 1,662 ft/min, for raw R600 under Mach 0.78, FL300 and a
southerly residual-minimum construction. This historical control does not
reproduce that value. Ashton et al. (2015), Table 9, instead predicts 256 Hz
against the raw 182 Hz at 00:19 for its level, southerly example with a 150 Hz
bias and -38 Hz combined satellite/AFC term; that 74 Hz residual is consistent
with the historical roughly 4,451 ft/min inversion. Until the roughly 45 Hz
disagreement with the dissertation implementation is recreated from its calculation files,
the model families must remain separate and neither value should be treated as
a direct measurement of descent.

Four fixed-mode ERA5/IGRF families were evaluated under the superseded
one-turn implementation. Each result below uses medium BFO and the same
explicitly conditional antenna-gain endpoint. True heading and magnetic track
required a focused 30,000-particle-per-seed refinement; all final rows passed
the numerical criteria declared for that narrow control.

The fixed-mode coordinate table is intentionally omitted. Reporting those
conditional modes side by side did not account for mode changes and does not
bound the repeated-event model.

These fixed-mode families were structural alternatives and were not pooled.
They remain useful regression controls but cannot describe later mode changes
and are not the current broad-flight result. LNAV is refused unless an explicit
waypoint route is provided.


## Architecture

```text
runner
├── broad estimator ── powered marked-jump dynamics + SATCOM + particle filter
├── optional evidence ── end-of-flight, ocean-drift, hydroacoustics, antenna
├── controls ── synthetic closure + truth-separated broad MH371 + legacy controls
└── reporting ── deterministic PDF and SVG generation
                         │
                         └── domain: units, states, WGS-84 geometry
```

The runner owns configuration, deterministic streams, input and binary
identity, evidence-family separation, observation sequencing, and outputs.
The broad estimator owns the `broad-powered-marked-jump-v1` equations and
propagates each state between observations with ERA5 winds and temperature and
IGRF-14 declination. It carries the selected control mode, pending independent
lateral/speed/altitude renewal clocks, finite state transitions, fuel state,
particle root, and structural stratum. SATCOM potentials are applied
sequentially; ancestry and per-seed behavior are retained so a plausible
endpoint cloud cannot conceal genealogical collapse.

The old `estimate` one-turn command remains only for focused regression and
historical comparisons. `estimate-broad-flight` is the canonical accident-path
command. `infer-broad-terminal` exists as a typed continuation from a broad
handoff, but a terminal result is not admissible while its full-M0011 parent
filter fails numerical-support checks.

Structural SATCOM/BFO choices are emitted as separate evidence families and
never silently averaged. Initial-mode and manoeuvre-rate weights inside the
broad process are declared priors and must be exposed in the report with
sensitivity to those choices. Ocean drift, hydroacoustics, antenna gain, and
searched-area context do not currently carry estimator weight in the broad
checkpoint. The full-domain CMEMS GLORYS12+WAVERYS family executes, but its
source contract is `admitted=false`: it failed the declared support,
every-recovery ESS, and replication-stability checks. Native HYCOM and GDP are
also diagnostics, and drift families are never averaged. Four Pléiades
transport surfaces likewise remain display-only because their importance
reweighting is unresolved even at 150,000 particles.

The legacy MH371 antenna control can enable separate full- and
no-precompensation endpoint likelihoods using the labelled uncommissioned gain
reconstruction. It does not validate the broad manoeuvre process.

Not integrated: independently refreshing the three shape-one pending
manoeuvre clocks inside every fixed-root transition-pool candidate. The move
was target-invariant and added 2.4% runtime in a matched 160,000-particle
control through 19:41 UTC, but root ESS improved only 1.61x, the largest-root
mass fell only to 0.73x its control value, and split-root total variation
worsened from 0.430 to 0.521. The experimental interfaces were removed rather
than retained as an unused production option.

Not integrated: fixed-root intermediate SATCOM potentials at approximately
19:10, 19:29, and the 19:41 physical endpoint of the 18:39-to-19:41 interval.
The exact telescoping proposal improved endpoint half-split root total
variation from
0.307 to 0.144, but in the matched 160,000-particle control root ESS changed
only from 30.07 to 30.95, largest-root mass only from 9.58% to 8.92%, and
physical outcome-signature ESS fell from 50.14 to 49.25. It therefore did not
solve lineage concentration and its runner interface was removed.

Not integrated: treating fixed-root L32 transition pools at both 18:39 and
19:41 as a production sampler. In the matched 160,000-particle experiment the
extra 18:39 pool raised final root ESS from 33.27 to 123.55 and reduced the
largest-root mass from 9.18% to 3.56%, but the endpoint replicate halves still
had root total variation 0.533 and the control-versus-active posterior had
root, stratum, and one-degree spatial total variations of 0.923, 0.328, and
0.229. The schedule was therefore rejected without an L64 escalation. The
general fixed-root pool remains as an exact, focused diagnostic control.

Not integrated: one exact whole-interval independence-MH source-replay sweep
after each fixed-root L32 transition pool at 18:39 and 19:41. In the
predeclared matched 20,000-particle seed-370023 smoke experiment, 81.2% of the
19:41 replay proposals were finite, but only 1.36% of posterior mass accepted
a proposal and only 0.550% switched roots, below the respective 2.5% and 1.0%
continuation floors; replay changed root ESS only from 14.15 to 14.21. The
fail-closed protocol therefore stopped before the matched 160,000-particle
experiment, and the source-replay interfaces were removed.

## Build and run

Rust 1.98.0 is pinned by `rust-toolchain.toml`.

```bash
cargo fmt --all -- --check
cargo test --workspace

# Canonical broad-flight filtering checkpoint. A completed process is not by
# itself a passed scientific report; inspect the numerical-support audit.
cargo run --release -p mh370-runner -- estimate-broad-flight \
  --config configs/mh370-broad-powered-flight-diagnostic.toml \
  --output runs/mh370/broad-flight-uncertainty-diagnostic \
  --threads 6

cargo run --release -p mh370-runner -- estimate-broad-flight \
  --config configs/mh371-broad-powered-flight-control.toml \
  --output runs/mh371/broad-flight-truth-control \
  --threads 6

.venv/bin/python crates/reporting/scripts/broad_snapshot_report.py \
  --spec configs/mh370-broad-snapshot-report.json \
  --output runs/mh370/broad-flight-uncertainty-diagnostic/diagnostic-report

.venv/bin/python crates/reporting/scripts/broad_snapshot_report.py \
  --spec configs/mh371-broad-snapshot-report.json \
  --truth inputs/controls/mh371-truth.csv \
  --output runs/mh371/broad-flight-truth-control/diagnostic-report

.venv/bin/python crates/reporting/scripts/validate_broad_release.py \
  --manifest runs/mh370/broad-flight-uncertainty-diagnostic/run-manifest.json \
  --summary runs/mh370/broad-flight-uncertainty-diagnostic/summary.json \
  --config configs/mh370-broad-powered-flight-diagnostic.toml \
  --binary target/release/mh370 \
  --report-audit runs/mh370/broad-flight-uncertainty-diagnostic/diagnostic-report/broad_snapshot_diagnostic.json \
  --output runs/mh370/broad-flight-uncertainty-diagnostic/diagnostic-report/release-validation.json

.venv/bin/python crates/reporting/scripts/validate_broad_release.py \
  --manifest runs/mh371/broad-flight-truth-control/run-manifest.json \
  --summary runs/mh371/broad-flight-truth-control/summary.json \
  --config configs/mh371-broad-powered-flight-control.toml \
  --binary target/release/mh370 \
  --report-audit runs/mh371/broad-flight-truth-control/diagnostic-report/broad_snapshot_diagnostic.json \
  --output runs/mh371/broad-flight-truth-control/diagnostic-report/release-validation.json

# Historical narrow-model regression commands follow.
cargo run --release -p mh370-runner -- estimate \
  --config configs/accident-smoke.toml \
  --output /tmp/mh370-smoke \
  --threads 4

cargo run --release -p mh370-runner -- estimate \
  --config configs/accident-production.toml \
  --output /tmp/mh370-production \
  --threads 4

cargo run --release -p mh370-runner -- estimate \
  --config configs/mh370-through-1825.toml \
  --output /tmp/mh370-through-1825 \
  --threads 4

cargo run --release -p mh370-runner -- estimate \
  --config configs/mh370-through-0011-medium.toml \
  --output /tmp/mh370-through-0011-medium \
  --threads 4

cargo run --release -p mh370-runner -- estimate \
  --config configs/mh370-through-0011-antenna-medium.toml \
  --output /tmp/mh370-through-0011-antenna-medium \
  --threads 4
cargo run --release -p mh370-runner -- estimate \
  --config configs/mh370-through-0011-antenna-autopilot-modes-medium.toml \
  --output /tmp/mh370-autopilot-modes \
  --threads 8

cargo run --release -p mh370-runner -- estimate \
  --config configs/mh370-through-0011-antenna-autopilot-evidence-refinement.toml \
  --output /tmp/mh370-autopilot-refinement \
  --threads 8

cargo run --release -p mh370-runner -- continue-to-contact \
  --config configs/mh370-0011-to-0019-seventh-arc-bto.toml \
  --output /tmp/mh370-seventh-arc

cargo run --release -p mh370-runner -- continue-to-contact \
  --config configs/mh370-0011-to-0019-startup-power-conditional.toml \
  --output /tmp/mh370-startup-power
```

Output directories must be absent or empty. Broad-flight output records the
model family, enabled evidence family, seed, structural stratum, observation
checkpoints, particle ancestry, runtime, configuration and input hashes, exact
executable hash, configured all-epoch particle snapshots, and numerical
diagnostics. The v0.1 diagnostic configurations deliberately suppress the
terminal handoff and the runner's ungated legacy report files. Publication
reporting must validate those identities and diagnostics and must emit a
failed-support diagnostic instead of an unqualified probability map when any
release criterion fails. The PDF/SVG/PNG description below applies only to the
legacy `estimate` reports.

## Independent controls

The 8,192-particle synthetic closure completes in roughly 0.03 seconds and
places 94.1% posterior mass within 100 NM of truth, with a 15.2 NM posterior
mean error.

```bash
cargo run --release -p mh370-runner -- validate \
  --config configs/synthetic-control.toml \
  --output /tmp/mh370-synthetic --threads 4
```

### Broad MH371 truth-separated control

The corrected MH371 validation runs the same broad marked-jump path model used
for MH370, including all five initial modes and recurring independent
lateral/speed/altitude changes across the four manoeuvre-rate families. It
starts at 01:48 UTC and uses six deterministically selected R1200 BTO/BFO
observations through 06:48 UTC. Later ACARS position, trajectory, Mach,
altitude, and heading values remain held back until reporting/scoring.

The broad runner consumes
`inputs/controls/mh371-broad-satcom.csv` and
`inputs/controls/mh371-broad-satellite.csv`. They are deterministic projections
with no later aircraft-state fields from `inputs/controls/mh371-inference.json`;
field
mappings and hashes are recorded in
[`inputs/controls/README.md`](inputs/controls/README.md). Propagation uses the
pinned ERA5 temperature/wind cube and IGRF-14 declination grid.
Satellite-oscillator and Perth-GES AFC corrections remain separate from the
analytically estimated aircraft BFO bias.

The corrected report must show per-arc error against held-back truth only after
inference, along with seed spread, root ESS/concentration, retained structural
support, and sensitivity to the declared mode/rate priors. The completed v0.1
run fails those checks: final pooled-mean errors are 1,350.4 NM for BTO-only
and 559.9 NM for BTO+BFO, final maximum between-seed mean separations are
668.3 NM and 1,356.7 NM, and both families have severe root concentration.
These are failed-control diagnostics, not accuracy claims. The 06:48 endpoint
was selected after a pilot inspection showed that the originally considered
06:59 window mixed the later descent turn, so this is also not a fully
preregistered blind trial. A failed control is not repaired by narrowing its
control history.

### Legacy constant-magnetic-heading MH371 control

The older `infer-known-flight` command is truth separated, but its propagation
is a single constant-magnetic-heading family with Gaussian heading, Mach, and
altitude perturbations at observation boundaries. It does not allow the five
lateral modes or recurring marked-jump manoeuvres and therefore cannot validate
the current broad method. The following settings, metrics, commands, and PDFs
are retained as narrow regression controls only.

The strict family samples Mach 0.65-0.89 and altitude 10,000-43,000 ft. Three
explicit MH370-analog alternatives use Davey's Mach 0.73-0.84 and
25,000-43,000 ft ranges with BFO observation SDs of 7, 4, and 1.5 Hz. Each
12,000-particle, two-seed family completes in about 0.8 seconds on eight
threads. In the final control the tighter families place at least 48.5%, 57.2%,
and 73.4% of terminal mass within 100 NM of held-back truth respectively.
These are comparative metrics for the legacy single-heading control, not
acceptance thresholds, broad-method validation, or MH370 accident-flight
results.

~~~bash
cargo run --release -p mh370-runner -- infer-known-flight \
  --config configs/known-flight-inference.toml \
  --inference inputs/controls/mh371-inference.json \
  --weather inputs/environment/mh371-era5-grid.bin \
  --magnetic inputs/environment/mh371-igrf14-grid.bin \
  --output /tmp/mh371-inference --threads 8

cargo run --release -p mh370-runner -- score-known-flight \
  --config configs/known-flight-scoring.toml \
  --truth inputs/controls/mh371-truth.csv \
  --run /tmp/mh371-inference/inference-seed-37102001.json \
  --run /tmp/mh371-inference/inference-seed-37102002.json \
  --output /tmp/mh371-assessment
~~~

For the legacy conditional antenna control, keep the medium BFO family fixed
and run each compensation endpoint separately. The no-precompensation endpoint
is:

~~~bash
cargo run --release -p mh370-runner -- infer-known-flight \
  --config configs/mh371-antenna-no-precomp-medium.toml \
  --inference inputs/controls/mh371-inference.json \
  --weather inputs/environment/mh371-era5-grid.bin \
  --magnetic inputs/environment/mh371-igrf14-grid.bin \
  --antenna-observations inputs/evidence/mh371-conditional-antenna-power.json \
  --antenna-surface inputs/evidence/mh371-first-pass-antenna-gain.bin \
  --output /tmp/mh371-antenna-inference --threads 4

cargo run --release -p mh370-runner -- score-known-flight \
  --config configs/known-flight-scoring.toml \
  --truth inputs/controls/mh371-truth.csv \
  --run /tmp/mh371-antenna-inference/inference-seed-37102001.json \
  --run /tmp/mh371-antenna-inference/inference-seed-37102002.json \
  --output /tmp/mh371-antenna-assessment
~~~

Use `configs/mh371-antenna-full-precomp-medium.toml` for the other endpoint.
Neither endpoint has an assigned core model weight.

Use configs/mh371-analog-loose.toml, configs/mh371-analog-medium.toml, or
configs/mh371-analog-observed.toml in the legacy inference command for the
three MH370-analog families. Legacy scoring emits a JSON assessment and a
seven-page vector PDF: one summary page and one map for every selected arc,
each with held-back position and true-heading arrow. It also emits a 2,800 x
1,900 PNG containing all six arcs as paper-style map panels. Smoothing affects
only that visualization, not inference or scoring. These polished legacy PDFs
must not be relabelled as validation of the broad method.

## Repository map

- `crates/`: the complete canonical product and focused checks.
- `configs/`: canonical broad checkpoints plus historical, synthetic, and
  known-flight control configurations.
- `inputs/`: compact immutable runtime and truth-separated control inputs,
  with local provenance in `inputs/controls/README.md`.
- `.sources/`: paper, paper-as-code, data, outputs, hashes, and explicit
  integration decisions; never a runtime dependency.
- `AGENTS.md`: the lean engineering contract.

The pre-refactor research workspace is preserved in an external legacy archive,
not in this repository. Rebuildable targets, dependency trees, environments,
and caches were deleted; the archive contains the unique legacy code, papers,
datasets, and results.
