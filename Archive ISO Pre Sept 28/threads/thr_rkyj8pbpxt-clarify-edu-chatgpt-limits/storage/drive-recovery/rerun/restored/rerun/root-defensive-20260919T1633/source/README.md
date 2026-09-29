# MH370 Bayesian estimator

A reproducible estimator for cruise through 00:11 UTC, followed by explicitly
selected end-of-flight and other evidence conditions. The current numerical
implementation is `estimate-cruise`. Its physical assumptions remain visible;
a normalized map is not a claim that the aircraft, fuel or optional evidence
models have been fully calibrated.

## Current result

Two different cruise models each have **1,020,000 initial candidates**. The
broader model allows at most **16 turn starts, 8 Mach changes and 8 altitude
changes after 18:25**, includes vertical-speed Doppler, and places about
**90.1% between 35–38°S**, **8.8% north of 35°S**, and **1.2% north of 30°S** at
00:11. These are conditional probabilities under the stated prior and inputs.
The original 4/2/2 model, with vertical Doppler disabled, puts 86.5% in the main
band. The two physical models are reported separately.

The broader pool contains six independently seeded runs of unequal sizes.
Adding the last 340,000 candidates moved its cumulative latitude/longitude
curves by at most 4.2/4.5 percentage points. The last batch alone and earlier
680,000-candidate pool differ by 13.9/14.7 points. This remaining sampling
variation must accompany the maps; a million initial candidates are not a
million independent posterior draws. No arbitrary five-point display veto is
used. Different physical families are never pooled to disguise disagreement.

The **35,000 ft arc is a geometric reference line only**. Each particle has its
own sampled altitude, including at 00:11. The broader gallery contains 102
faithfully replayed histories, covering every positive-mass 2.5° latitude bin
in the retained pool. Examples illustrate histories; their selection does not
change the probabilities.

Open the generated ISO reports without downloading a PDF:

- [Broader 00:11 density, complexity and sampling comparisons](mh370-broader-arc-density.html)
- [Exact broader trajectory examples every 2.5°](mh370-broader-route-examples.html)
- [Separate manoeuvre-limit comparisons](mh370-model-comparison.html)
- [Conditional antenna comparison](mh370-antenna-comparison.html)
- [End-of-flight and final-contact alternatives](mh370-impact-comparison.html)
- [Nine-debris drift](mh370-drift-comparison.html), [flaperon Stokes sensitivity](mh370-stokes-comparison.html), and [Pléiades conditions](mh370-pleiades-comparison.html)
- [Acoustic timing and energy](mh370-acoustic-comparison.html)
- [Godfrey route comparison](mh370-proposed-route-comparison.html)
- [7,500 km² search-budget sensitivity](mh370-search-comparison.html)

Full-precision CSV/JSON, probability-per-area grids, vector PDF/SVG figures,
input identities, seeds, source archives and measured runtimes live in the
[owner artifact directory](/jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/README.md).
The HTML files above are generated previews, not hand-edited scientific results.

## Reproduce a cruise run

The checked recipe starts 170,000 candidates across five initial navigation
modes. On the current six-core host its archived numerical runs took about
eight minutes each using four workers; compilation and report generation are
additional. This is measured throughput, not a convergence guarantee.

```bash
cargo run --profile iteration --locked --offline -p mh370-runner --   estimate-cruise --config configs/mh370-cruise-through-0011.json   --output /tmp/mh370-cruise --threads 4
```

The JSON recipe has paths relative to its own directory. It records its seed,
initial count, observation selection and physical assumptions. Its 3,600-second
per-run watchdog detects a runaway job; it is not a scientific stopping rule
or a total computation budget. Use distinct seeds for independent comparisons,
and preserve each resolved configuration rather than overwriting an output.

The report command compares at least two completed, compatible runs without
new sampling. Its Python interpreter needs NumPy and Matplotlib:

```bash
MH370_REPORT_PYTHON=/path/to/reporting-venv/bin/python   target/iteration/mh370 report-cruise   --runs /path/to/first-run /path/to/second-run   --output /tmp/mh370-cruise-comparison   --inline-output /tmp/mh370-cruise-comparison.html
```

The output includes raw weights, equal-area cell densities, cumulative curves,
cell-size sensitivity and independent-run comparisons. Replicates with unequal
initial counts combine using their counts and estimated normalizers. Retained
descendant multiplicity is not treated as independent sample size. Source and
physical-configuration checks prevent accidental pooling of unlike runs.

## Explicit model choices

- Mach 0.73–0.84; altitude 25,000–43,000 ft with 1,000 ft target levels.
  Finite-rate turns, speed changes and climbs/descents are simulated rather than
  jumping between contact positions. These are declared kinematic bounds,
  not a validated B777 performance deck at every sampled mass and condition.
- Initial modes are constant true/magnetic heading, constant true/magnetic
  track, and lateral navigation, with the recipe's stated prior weights.
  A mode generally persists; lateral navigation may switch once to a heading
  mode. Arbitrary repeated switching among all modes is not implemented.
- Manoeuvre waiting-time uncertainty and small correlated control/wind
  deviations are sampled. Direction, Mach and altitude counts are kept
  separate. More complicated paths are permitted, but their relative weights
  still depend on a manoeuvre prior; there is no assumption-free PDF.
- WGS-84 geometry, UTC contact epochs, pinned ERA5 temperature/wind and
  IGRF-14 declination are used. BFO has a shared analytically updated bias.
  Proposal guidance is divided out of the weights and is not evidence.
- Fuel is conditioned on an explicit 00:15–00:19 exhaustion window, an
  18:28 fuel interval and a correlated flow-scale uncertainty. The continuation
  back-propagates this condition to allowable fuel at 00:11. Its public fuel
  proxy and timing interval are hypotheses, not direct fuel measurements or a
  calibrated Boeing engine model. Fuel is counted once when composing impact.

## Conditional impact and other evidence

The current terminal ensemble starts from the full **1,020,000-candidate**
broader pool. It contains 109,767 records and 94,839 computed impacts under
twelve separate aerodynamic/control families, using 9,216 draws of cruise
parents. Sampling took 1,055.93 seconds on four workers; conditioning took
20.14 seconds. Peak measured child-process memory was 1.56 GiB. The earlier
680,000-candidate terminal ensemble remains an archived comparison.
Ten contact conditions per family distinguish neither final BFO, either one,
and both readings in time order, with or without the declared shared startup
frequency hypothesis. R600 uses the logged 00:19:29.416 time and 18,400 µs BTO
(23,000 raw minus 4,600 channel bias). R1200 is at 00:19:37.443; its anomalous
BTO is omitted. The startup ranges are not a calibrated probability law.

R600-only cases have substantially better sampling support than two-BFO cases:
the new ensemble gives about 137–878 effective weighted rows for R600, but
only 1.1–3.6 when both BFOs are used without a startup offset. These are weight
concentration diagnostics, not independent posterior sample counts. The earlier
control-only proposal did **not** resolve the latter. A joint fuel/control
alternative is being tested outside the product before any integration.
The terminal ERA5 grid now extends to 60,000 ft; all original cruise-grid
values and historical data objects are preserved exactly. This removes the
earlier weather-altitude exits. Near-vertical and minimum-speed model exits
remain unresolved mass, never silently counted as impossible impacts.
Public drag polars and lift/bank controls are sensitivity models, without
validated post-stall, breakup or body-attitude physics. Flight-path angle is
not impact pitch. Acoustic energy/coupling alternatives are labelled examples;
there is no calibrated pressure, detection or hydroacoustic association
likelihood.

Antenna surfaces, drift encounter models, Stokes factors and Pléiades object
identities are explicit conditional alternatives. Shared observations and
incompatible transport families are not multiplied together. Uncomputed
spatial likelihood is kept separate from zero likelihood. WSPR/Godfrey and
Kadri comparisons currently test attributed geometries and predicted arrivals;
they do not establish aircraft detections in the historical signals.

Search contours and coarse/AIS-derived outlines are contextual coverage, not
complete calibrated swath-level negative evidence. The search report ranks
cells under each conditional sample and checks the same selected cells in an
independent terminal draw where available. For one R600 example in the
full-million refresh, 7,500 km² captures 46.1% at the 25 km cell scale.
An earlier, separately retained 680,000-parent comparison captured 52.2% in
its design sample and 42.2% in an independent draw; it is not a matched
replicate of the new weather/parent set. These
figures are scenario-sensitive, exclude unresolved impact mass, and do not
establish an operational optimum. Detection-probability sliders are declared
planning illustrations, not inferred historical detection probabilities.

## Architecture and verification

```text
runner -> sequential particle filter + selected scientific spokes -> domain
runner -> reporting
```

The runner loads configuration, records identities, composes modules and emits
artifacts. Flight equations live in `dynamics`; SATCOM in `satcom`; fuel and
terminal propagation in `end-of-flight`; spatial likelihood interfaces in
`ocean-drift`; acoustic travel time/energy in `hydroacoustics`. Paper recreation
under `.sources/` is never a runtime code dependency. The runner may read an
explicitly selected, attributed dataset produced by a source investigation.

The cruise engine updates ordered observation blocks, uses deterministic
particle streams, corrects guided proposals, and retains ancestry for exact
history recovery. Tests include finite-state evidence enumeration, coordinate
and dimensional fixtures, biased-proposal controls, fuel balance, and
integration refinement. Before integration, 349 focused scientific checks
passed; the integrated workspace subsequently passed 500 tests, with five
explicitly ignored controls. A 1,000-candidate control reproduced the predecessor's posterior CSV,
trajectory histories and evidence exactly after removing failed alternatives.
The small control verifies compatibility, not geographic convergence.

```bash
CARGO_BUILD_JOBS=2 cargo test --workspace --locked --offline -- --test-threads=2
```

Two previously completed 200,000-candidate MH371 sequential-cruise controls
put the held-back endpoint near the middle of both coordinate distributions;
their own latitude/longitude CDFs differ by 6.6/5.4 percentage points. Fuel was
off, vertical Doppler was off, and the endpoint window had previously been
selected with truth visibility. This is encouraging numerical recovery, not
a blind or repeated-data coverage study, nor validation of accident fuel or
terminal physics. Further synthetic coverage and physical calibration remain
necessary. Earlier failed broad MH371 runs and the old narrow constant-heading
control use different implementations and must be distinguished from these
current controls.

The current prior-predictive control generates 24 independent cruise routes
and noisy SATCOM sequences before inference, then runs two independent
20,000-candidate estimates for each. Generating truth is read only by a scorer
after each pair finishes. Fuel and the accident-fitted initial proposal are
disabled; actual contact geometry, uncertainty scales and the 16/8/8 physical
process are retained. The generated-data check proves that changing the
accident measurements leaves the synthetic fixture unchanged and that a
shared bias shift changes all nine BFOs equally while preserving BTO and the
physical path. The browser reports finite-sample coordinate recovery and
replicate variation; it does not call interacting particle rows independent
SBC ranks or claim physical calibration.

```bash
target/iteration/mh370 generate-cruise-controls \
  --config configs/mh370-cruise-through-0011.json \
  --output /path/to/synthetic-cruise-recovery --seed 37091900 --fixtures 24
python crates/controls/verify_cruise_generator.py \
  --executable target/iteration/mh370 \
  --config configs/mh370-cruise-through-0011.json \
  --output /path/to/generator-control
```

Each generated inference configuration is supplied to `estimate-cruise`.
`crates/reporting/scripts/synthetic_cruise_report.py` scores only completed
pairs using the recorded design and per-run identities.

All 48 original controls completed, but their independent latitude/longitude
CDF differences have medians 28.7/25.1 percentage points. Larger runs test
sampling effort on every third original data set, chosen by index. A separate
check fits the existing initial Mach/altitude proposal from each data set's
own completed pilots, without reading its generating truth:

```bash
target/iteration/mh370 prepare-cruise-initial-proposal \
  --runs /path/to/pilot-one /path/to/pilot-two \
  --output /path/to/initial-proposal.json --centres-per-mode 256
```

Set `initial_operating_proposal` to that file in fresh inference configurations.
The preparer verifies original input identities and reconstructs initial
ancestors from deterministic streams. The proposal retains a 20% full-prior
component, corrects its density in the weights, and removes its temporary
guidance at the final observation. A mode absent from the pilot retains its
exact prior. The independent proposal-weight controls pass, and a 1,000-draw
existing-proposal run reproduces the original CSV, histories and evidence.
This establishes implementation compatibility, not convergence of new runs.

Not integrated: the unsuccessful tree-branching, random-input replay,
annealed command-space, ordered forward/reverse path-space and fixed-root
lookahead variants did not establish broad distribution recovery. Their code
is not part of the current cruise path. Frozen source archives and the owner
progress records preserve the failures and exact reproduction details. Older
runner commands remain historical controls and must not be relabelled as the
current estimator or as validation of it.

The original working-estimator and publishable-paper objective remains active.
The current results support transparent conditional comparisons; unresolved
numerical and physical limitations must be addressed in the final paper.
