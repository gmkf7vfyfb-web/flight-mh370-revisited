# MH370 Bayesian estimator

This repository now has one product: a lean, deterministic Rust estimator for
the final flight of MH370, plus focused controls and publication-quality vector
reports. The canonical production run completes three model families across
five independent seeds with 30,000 particles per seed and records its runtime,
inputs, binary identity, and convergence diagnostics.

The current release checkpoint, all seven work-item outcomes, figures,
reproduction commands, limitations, and exact artifact hashes are collected in
the [v0.1 release index](runs/mh370/release-v0.1/index.html).

The results below are model-conditional estimates, not observed crash
coordinates or searched-area eliminations.

The reported intervals condition on the named one-turn and lateral-control
family. They do not marginalize over arbitrary later manoeuvres or across
structural model families, so they must not be read as full MH370 path
uncertainty.

## Current production baseline

Configuration: `configs/mh370-0011-core-comparison.toml`; 30,000 particles per
seed, five seeds per family, 450,000 total evaluated posterior particles.

| SATCOM family | Pooled mean | 90% latitude | 90% longitude | Max seed separation | Log-evidence range |
| --- | --- | --- | --- | ---: | ---: |
| BTO only | 36.4895°S, 89.3491°E | 37.5036–35.4517°S | 87.7005–90.9319°E | 2.49 NM | 0.029 nats |
| BTO + medium BFO | 36.4086°S, 89.4961°E | 37.0997–35.9028°S | 88.3874–90.2627°E | 3.33 NM | 0.136 nats |
| BTO + medium BFO + gain (conditional) | 36.4095°S, 89.4923°E | 37.1070–35.8944°S | 88.3763–90.2705°E | 1.36 NM | 0.110 nats |

All three families pass the declared numerical criteria. This establishes
numerical repeatability for the declared model; it does not establish that the
one-turn trajectory family or evidence choices are physically complete.

## Earlier staged controls through 00:11 UTC

These preserved historical controls used 10,000 particles across three seeds and
the medium 4 Hz BFO observation model where BFO is enabled.

| Endpoint and evidence | Pooled mean | 90% latitude | 90% longitude | Max seed separation | Log-evidence range |
| --- | --- | --- | --- | ---: | ---: |
| Radar epoch through 18:25, BTO | 6.9047°N, 96.1778°E | 6.3463–7.0786°N | 96.0611–96.3084°E | 0.47 NM | 0.023 nats |
| Through 00:11, BTO + medium BFO | 36.5451°S, 89.3273°E | 37.0221–36.2134°S | 88.5499–89.8042°E | 1.32 NM | 0.337 nats |
| Through 00:11, BTO + medium BFO + conditional gain | 36.5472°S, 89.3121°E | 37.1238–36.1567°S | 88.4070–89.8448°E | 10.95 NM | 0.799 nats |

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

## Recovered prior, continuation, and autopilot controls

Davey's numerical starting prior is at 18:01:49 UTC, not 18:11. The normal
00:11 result is one joint sequential particle inference from that radar prior
through all included SATCOM epochs; it does not replace the 18:25 posterior
with a fitted Gaussian. A separate final-radar/N571 sensitivity starts at the
published last-radar locus with a deliberately reconstructed covariance because
the public numerical radar series is unavailable.

| Prior/control | Endpoint | Pooled mean | Max seed separation | Log-evidence range |
| --- | --- | --- | ---: | ---: |
| Davey-style radar prior, BTO only | 18:25 | 6.9047°N, 96.1778°E | 0.47 NM | 0.023 nats |
| Final-radar/N571 sensitivity, BTO only | 18:25 | 6.7686°N, 95.9725°E | 0.08 NM | 0.017 nats |
| Davey-style radar prior, medium BFO | 00:11 | 36.5451°S, 89.3273°E | 1.32 NM | 0.337 nats |
| Final-radar/N571 sensitivity, medium BFO | 00:11 | 36.5419°S, 89.2810°E | 20.89 NM | 0.551 nats |

The 18:25 report overlays N571, the published final-radar locus, and an
airway/BTO-constrained 18:25 reference with heading arrow. That reference is
not represented as a known fix.

The canonical 00:11 posterior was also continued to 00:19 in two deliberately
separate controls:

| New 00:19 selection | Mean | 90% latitude | 90% longitude | ESS |
| --- | --- | --- | --- | ---: |
| R600 seventh-arc BTO only, v0.1 typed handoff | 37.4546°S, 89.3735°E | 38.1197–36.9658°S | 88.2524–90.1515°E | 135,729 |
| Adjusted R600 startup power only, historical conditional | 37.6749°S, 89.1784°E | 38.1582–37.3384°S | 88.3754–89.6694°E | 29,479 |

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
southerly residual-minimum construction. The current result does not reproduce
that value. Ashton et al. (2015), Table 9, instead predicts 256 Hz against the
raw 182 Hz at 00:19 for its level, southerly example with a 150 Hz bias and
-38 Hz combined satellite/AFC term; that 74 Hz residual is consistent with the
current roughly 4,451 ft/min inversion. Until the roughly 45 Hz disagreement
with the dissertation implementation is recreated from its calculation files,
the model families must remain separate and neither value should be treated as
a direct measurement of descent.

Four ERA5/IGRF lateral-mode families are now available. Each result below uses
medium BFO and the same explicitly conditional antenna-gain endpoint. True
heading and magnetic track required a focused 30,000-particle-per-seed
refinement; all final rows pass the declared numerical criteria.

| Lateral mode | Pooled mean | 90% latitude | 90% longitude | Max seed separation | Evidence range |
| --- | --- | --- | --- | ---: | ---: |
| Constant true track | 36.4547°S, 89.4229°E | 37.1116–35.9261°S | 88.3669–90.2294°E | 2.91 NM | 0.419 nats |
| Constant true heading | 35.8211°S, 90.5730°E | 36.4521–35.3370°S | 89.6269–91.2683°E | 5.87 NM | 0.460 nats |
| Constant magnetic track | 33.3056°S, 93.9904°E | 33.5332–33.0849°S | 93.7743–94.1870°E | 4.51 NM | 0.769 nats |
| Constant magnetic heading | 31.7725°S, 96.0120°E | 31.9349–31.6508°S | 95.8602–96.1291°E | 9.34 NM | 0.618 nats |

The mode families are structural alternatives and are never pooled. LNAV is
refused unless an explicit waypoint route is provided.


## Architecture

```text
runner
├── estimator ── dynamics + satcom + particle-filter
├── optional evidence ── end-of-flight, ocean-drift, hydroacoustics, antenna
├── controls ── synthetic closure + truth-separated known flight
└── reporting ── deterministic PDF and SVG generation
                         │
                         └── domain: units, states, WGS-84 geometry
```

The accident model samples radar-state uncertainty, one instantaneous turn,
post-turn lateral control, Mach, and altitude. The control is interpreted by
an explicit true-track, true-heading, magnetic-track, or magnetic-heading
family; environment-aware families interpolate ERA5 and IGRF-14 along the
trajectory. It evaluates all SATCOM observations as one static likelihood and
uses adaptive likelihood-tempered sequential Monte Carlo with deterministic
keyed random streams and MCMC rejuvenation.

Structural BFO choices are emitted as separate families and never averaged.
The v0.1 production baseline leaves ocean drift and hydroacoustics at exactly
zero estimator weight. The full-domain CMEMS GLORYS12+WAVERYS family executes,
but its source contract is `admitted=false`: it failed the declared support,
every-recovery ESS, and replication-stability checks. Native HYCOM and GDP are
also diagnostics, and drift families are never averaged. Four Pléiades
transport surfaces likewise remain display-only in v0.1 because their
importance reweighting is unresolved even at 150,000 particles. The
[release index](runs/mh370/release-v0.1/index.html) links the fail-closed audit
and the separately labelled conditional figures.
The MH371 control can explicitly enable separate full- and no-precompensation
endpoint likelihoods using the labelled uncommissioned gain reconstruction.

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

Output directories must be absent or empty. Each family receives a three-page
vector PDF, SVG and 2,800 x 1,900 PNG posterior maps, conditional-evidence
record, per-seed posterior
CSV, checkpoints, and summary. The suite manifest hashes the config, inputs,
the exact executable, and published artifacts.

## Independent controls

The 8,192-particle synthetic closure completes in roughly 0.03 seconds and
places 94.1% posterior mass within 100 NM of truth, with a 15.2 NM posterior
mean error.

```bash
cargo run --release -p mh370-runner -- validate \
  --config configs/synthetic-control.toml \
  --output /tmp/mh370-synthetic --threads 4
```

The truth-separated MH371 cruise control starts at 01:48 UTC and uses six
deterministically selected R1200 BTO/BFO observations through 06:48 UTC. Later
ACARS position, trajectory, Mach, altitude, and heading values are available
only to the scorer. Propagation uses the pinned ERA5 temperature/wind cube and
IGRF-14 declination grid. Satellite-oscillator and Perth-GES AFC corrections
remain separate from the analytically estimated aircraft BFO bias.

The strict family samples Mach 0.65-0.89 and altitude 10,000-43,000 ft. Three
explicit MH370-analog alternatives use Davey's Mach 0.73-0.84 and
25,000-43,000 ft ranges with BFO observation SDs of 7, 4, and 1.5 Hz. Each
12,000-particle, two-seed family completes in about 0.8 seconds on eight
threads. In the final control the tighter families place at least 48.5%, 57.2%,
and 73.4% of terminal mass within 100 NM of held-back truth respectively.
These are comparative control metrics, not acceptance thresholds or MH370
accident-flight results.

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

For the conditional antenna control, keep the medium BFO family fixed and run
each compensation endpoint separately. The no-precompensation endpoint is:

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
configs/mh371-analog-observed.toml in the inference command for the three
MH370-analog families. Scoring emits a JSON assessment and a seven-page vector
PDF: one summary page and one map for every selected arc, each with held-back
position and true-heading arrow. It also emits a 2,800 x 1,900 PNG containing
all six arcs as paper-style map panels. The panels use the established DejaVu
Sans typography, near-white map field, very light nested density shading,
50%, 90%, 95%, and 99% highest-posterior-density contours, yellow actual-state
star, cyan spatial-mode marker, true-heading arrow, Natural Earth land context,
and a locally scaled nautical-mile bar. Smoothing affects only this
visualization, not inference or scoring.

## Repository map

- `crates/`: the complete canonical product and focused checks.
- `configs/`: smoke, production, synthetic, and known-flight configurations.
- `inputs/`: compact immutable runtime and control inputs.
- `.sources/`: paper, paper-as-code, data, outputs, hashes, and explicit
  integration decisions; never a runtime dependency.
- `AGENTS.md`: the lean engineering contract.

The pre-refactor research workspace is preserved in an external legacy archive,
not in this repository. Rebuildable targets, dependency trees, environments,
and caches were deleted; the archive contains the unique legacy code, papers,
datasets, and results.
