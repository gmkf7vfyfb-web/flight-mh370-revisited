# MH370 position at the final satellite arc

A compact, reproducible recreation of the DSTG Bayesian estimate of where MH370
was at 00:19 UTC on 8 March 2014: Davey, Gordon, Holland, Rutten & Williams,
*Bayesian Methods in the Search for MH370* (Springer, 2016), Fig. 10.3.

```bash
make venv                        # once: numpy + matplotlib for the report
make app                         # macOS: build "MH370 Particle Filter.app", then open it
make serve                       # the same app from a terminal, on http://127.0.0.1:8370
make report                      # base estimate (config/davey2016.toml) and its PDF
make hypothesis H=altitude-prior # one hypothesis, full scale, compared with the base
make sensitivity S=wind-off      # core sensitivity (config/sensitivity/), compared with the base
make smoke [H=<name>]            # one-minute code-path check
make fixture                     # impact fixture: integrated run at smoke scale, placeholder impacts (~20 s)
make evaluate H=<name>           # an impact module on the fixture's impacts, in seconds
make test                        # unit checks, under a minute
```

`make report` writes run artifacts to `runs/davey2016/` and the report to
`mh370-davey2016-reproduction.pdf`. The report states the result, compares it
with the published curve, shows replicate agreement, and records the seeds,
configuration, runtime and memory.

Each run also writes `summary.json`: the latitude densities, the numbers quoted
with them, and the weights that pool replicates. The runner computes it once
(`crates/mh370/src/summary.rs`); the report and the app both read it, so a
figure and a panel cannot disagree about the same run. `mh370 summarise <run>`
rebuilds it for an older run.

## The app

`make app` wraps the runner in a macOS application; `make serve` is the same
thing in a terminal. It runs this filter — there is no second, faster estimator
behind it — and every run it makes is an ordinary run: the controls are merged
over a configuration exactly like an override file, the app shows the override
it will apply, and the artifacts land in `runs/<name>/` where the report can
read them.

What it exposes: the configuration to run (the base estimate, the sensitivities
in `config/sensitivity/`, each hypothesis); the run size, seeds and measurement
case, with the run time and memory they imply; the published dynamics constants,
the prior and the measurement constants, each editable and each marked when it
departs from the published value; the hypotheses on disk with their parameters
and recorded status; and the measured inputs with their provenance. A new
hypothesis directory appears by itself, marked as unavailable until the binary
is rebuilt.

Interactive sizes, measured on six threads: 100k particles take about 10 s, 1M
about 1 min, and a 7M-particle replicate about 9 min. Anything under a million
particles is a smoke run, and the app says so; it also flags a result whose
replicate halves disagree as unconverged rather than quoting it.

## What is estimated

The aircraft state is filtered from the penultimate radar point (18:01:49 UTC)
through every Inmarsat BTO and BFO measurement to 00:19:37 UTC. There are two
cases: BTO only, and BTO + BFO. No fuel, debris, drift, search, acoustic or
end-of-flight evidence is used.

- `crates/flight` holds the chapters 6–7 dynamics. There are five autopilot
  modes. Mach, control angle and wind error follow OU processes. Turns, speed
  changes and climbs are driven by an exponential clock with a Jeffreys τ.
  Winds and temperatures come from ERA5, magnetic declination from IGRF-14.
- `crates/satcom` holds the chapter 5 measurement model. BTO is Gaussian; BFO
  uses a per-trajectory Kalman-marginalised bias.
- `crates/mh370` holds the filter. It draws particles from the prior,
  propagates, weights, and resamples systematically when ESS is low.

## After the filter: the end of flight

`config/integrated.toml` stops the filter at 00:11 and continues each posterior
trajectory to impact. This is the integrated estimate, not the base estimate.

- **Hand-off.** Per replicate, K trajectories are drawn from the 00:11
  posterior, stratified by autopilot mode (each mode with posterior mass keeps
  at least `handoff_floor`). `handoff.toml` holds each one's full state, which
  continues bit-identically; `handoff.npy` is a row-aligned numeric index.
- **Hand-off look-ahead (optional, off by default).** The overlay
  `config/sensitivity/handoff-lookahead.toml` sets
  `[output.handoff_lookahead]`. At the hand-off epoch the filter draws
  `oversample` × K candidates from the filtered posterior. At the stated
  horizon (a later epoch, for example m0011 for the 22:41 hand-off and the
  00:19 BTO for the 00:11 hand-off) it computes g = smoothed / filtered
  weight for each candidate. It then draws the K rows with probability
  proportional to (1−ε)g + ε, where ε is `defensive`. Each row then carries
  `log_correction = ln Z − ln((1−ε)g + ε)`, with Z the normalising sum.
  The rows are then an importance sample: **multiply each row's weight by
  exp(log_correction)**, and the corrected weights estimate the unproposed
  hand-off exactly in expectation. `handoff.toml` gets a `[lookahead]`
  table with `version` (now 1), `horizon`, `defensive`, `oversample`,
  `g_source` and `rule`, and `handoff.npy` gets a 14th column that holds
  `log_correction`. The contract is that a consumer which ignores the
  correction is wrong, so `handoff::read` refuses a look-ahead hand-off.
  Use `handoff::read_corrected`, which applies the correction and checks
  the version. With `oversample = 1, defensive = 1` the hand-off is the
  same as with the look-ahead off, row for row, and the 14th column is
  zero. `g_files` (with `{seed}`/`{mode}` in the path) takes g from an
  external module instead of from smoothing. This is the hook for
  conditioning on later evidence, for example the end-of-flight
  likelihood.
- **End of flight.** For each trajectory and each of `children` draws, the
  terminal module picks the takeover time (the first flame-out), the core
  dynamics fly the aircraft to it, and the module descends to impact.
- **The 00:19 bursts.** The runner scores them with the core measurement model
  at their logged millisecond times. Each data option in `[terminal] options`
  (none, either, both, BTO only, ...) is a separate log-likelihood column of
  `impacts.npy`, computed from the same descents. Options with a BFO are scored
  under each BFO model: no offset; a start-up offset from Holland (2018,
  arXiv:1702.02432v3, sec. V-A/B: 17–130 Hz, the first burst 0–6 Hz higher,
  uniform as an analyst choice); or independent 34 Hz errors, a declared
  sensitivity.
- **Diagnostics.** `terminal.json` gives, per data option, the log-evidence
  increment and the effective sample size over descents and over trajectories,
  plus a self-check that the module's proposal corrections average one.
- **Rerunning.** `mh370 terminal <run> <config> [<override>...] <out>` reruns
  this stage from a finished run's hand-off in seconds.

Until the end-of-flight model is ready, the terminal module is `arc-kernel`, a
placeholder whose impacts are plumbing, not a result.

## Hypotheses

The base estimate is conditional on the book's model and nothing else. Every
further assumption is a **hypothesis** in its own directory:

```text
hypotheses/<name>/
  hypothesis.toml   question, status (open | supported | not-supported | inconclusive), summary
  lib.rs            the assumption, its source, and its hook implementations + tests
  run.toml          base config + `[hypotheses.<name>]` parameters (and run size)
```

A hypothesis acts only through the hooks in `crates/hypothesis`. Its role in a
run comes from the config:
- a trajectory module (any enabled hypothesis not named below) acts in the
  filter: it adjusts the prior, requests extra epochs, and adds epoch and
  final-state log-likelihood;
- an impact module, named in a `[[compose]]` evidence set, returns the
  log-likelihood of its data for each impact sample (NaN where not computed),
  and may add named predictions;
- the terminal module, named in `[terminal]`, models the end of flight from the
  first flame-out to impact.

Every module declares the observations it uses (the runner refuses a run that
uses one twice) and any discrete alternatives. `mh370 evaluate <config>
<samples> <out>` runs the impact modules of a config on a samples file (CSV or
impacts.npy), so a module can be tested against fixtures in seconds.

The build discovers hypothesis directories automatically, so adding one
touches no shared file. `make scope H=<name>` checks that a branch touched
nothing else. The run manifest and every report page state which hypotheses
were enabled. Hypothesis reports overlay the base estimate.

| Hypothesis | Question |
|---|---|
| `altitude-prior` | Does a cruise-level altitude prior at 18:01 restore the published northern shoulder? |
| `arc-kernel` | Placeholder end-of-flight model for the integrated run: plumbing, not a result |

## Departures from the paper

- **Weather**: ERA5 replaces ACCESS-G, which is not public. Declination comes
  from IGRF-14; the book used NOAA's model.
- **Prior mean**: the 18:01:49 position and track are reconstructed from the
  book's radar figures (Ch. 4), because the book does not tabulate them. The
  altitude prior is uniform on 25–43 kft.
- **BTO calibration sign**: Eq. 5.3 printed literally gives a fixed term of
  −504,245 µs. The implemented offset is −495,679 µs, which reproduces logged
  BTOs at known positions and matches Ashton et al. (2015).
- **Sampler**: the book used variable-rate branching. Here, fixed-size
  particle filters handle the two static parameters exactly:
  - one filter per autopilot mode, combined by evidence;
  - a Gibbs refresh of τ from its path conditional after each resampling.

  The book warns (sec. 10.4) that plain resampling collapses static
  parameters. Measured here, a 1M-particle bootstrap filter kept about 100
  distinct prior draws.
- **Cost-index speed mode** (book sec. 6.2.1) is proprietary and omitted, as
  in most of the book's experiments.

**Known difference in the result.** The recreated pdf matches the published
curve's southern edge and its peak near 38°S. It is centred about 0.6° further
south and has less of the northern shoulder at 34.5–36.5°S. The difference
does not shrink with more particles, so it comes from the unpublished inputs
above, not from sampling. The report quantifies it.

## Why the previous codebase was replaced

The earlier repository (~100k lines of Rust, 19k lines of Python, 126 markdown
files, 32 generated HTML reports and ~16 GB of runs in the tree) never produced
a stable pdf. The causes, so they are not repeated:

1. **Sampler degeneracy was never addressed.** Bootstrap resampling collapsed
   the static parameters (mode, τ) onto a few ancestors. Tails and turn counts
   then changed with the seed, and each unstable result triggered another
   layer of conditional evidence instead of a sampler fix.
2. **Scope outran the core.** Fuel, drift, debris, antenna gain, acoustics,
   imagery and search coverage were stacked onto an estimator that did not yet
   reproduce the paper it started from.
3. **Process documents replaced version control.** There was no `git` on the
   machine. Ledgers, hash manifests, "withdrawn" copies and status files took
   the place of history and contradicted each other.

The old tree is preserved unchanged in `.archive/` for reference. Nothing
here depends on it.

## Data

`data/` holds the measured inputs. `.sources/` holds the paper, the digitised
reference curve and the scripts that built the environment grids.

| File | Content | Source |
|---|---|---|
| `satcom-observations.csv` | BTO/BFO per burst (C-channel calls: mean of 51 and 29 BFOs), message-type error SDs, satellite+EAFC frequency term; the log time to the millisecond (`logged_utc`), the measurements the cruise model applies to (`cruise`) and log-on events. `time_utc` is the log time truncated to the second, which the cruise filter uses. The 00:19 BFOs (182 and −2 Hz) were sent during the SDU start-up: they are kept for the end-of-flight stage and the cruise filter does not use them | Released unredacted SITA/Inmarsat logs (`Unredacted Raw 35200217 Logs for SITA 08Mar2014`). The anomalous 18:25 and 00:19:37 BTOs are corrected by 5 and 4 × 7,820 µs (Davey sec. 5.2), the 00:19:29 R600 BTO by −4,600 µs. SDs from Davey Table 10.1; satellite+EAFC values from ATSB tables |
| `satellite-ephemeris.csv` | Inmarsat-3F1 ECEF position/velocity at each burst | Released `Inmarsat3F1_23839 Fixed Position Velocity` workbook (one-second STK/SGP4 states), interpolated linearly |
| `era5-wind-temperature.bin` | Temperature, u/v wind; 17:00–02:00 UTC hourly, 12 pressure altitudes, 0.5° global | ECMWF ERA5 via `gs://gcp-public-data-arco-era5`; `.sources/era5-weather/extract.py` (17:00–01:00), `extend.py` (02:00, same selection and interpolation, after re-extracting 01:00 byte-identically). The cruise filter reads nothing after 00:19 |
| `igrf14-declination.bin` | Magnetic declination, 12 altitudes, 0.5° global, epoch 2014.18 | IGRF-14 (`pyIGRF14.zip`); `.sources/igrf14-declination/build.py` |
| `fuel-tables.json` (not in git; never commit or redistribute) | 777-200ER / Trent 892 FPPM grids by flight level and weight: LRC, M0.84, holding, MRC, CI 52, engine-out; per-cell source class | Ulich 9M-MRO fuel model V5.6 (public copy), Boeing-derived and partly marked confidential; raw tables only, not its endurance model; `.sources/fuel-performance/extract.py`. `.sources/fuel-performance/validate.py` checks a fuel model against SIR App. 1.6E Tables 3–4 |
| `.sources/davey-2016/fig10-3-bfo-latitude-pdf.csv` | Digitised Fig. 10.3 (bottom), density per degree | `paper.pdf`, book p. 90 |

Binary layouts are documented in `crates/flight/src/environment.rs`.

The two `.bin` grids (~350 MB) are not in git. Rebuild them with the scripts in
`.sources/era5-weather/` and `.sources/igrf14-declination/`, or copy them from
an existing checkout.
