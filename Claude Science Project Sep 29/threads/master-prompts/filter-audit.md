# Independent audit of the core filter's flight dynamics and satellite measurement model: brief

Modular Architecture, 9 October 2026, at Pete Large's request. This is the second audit, after the
fuel-model audit (`threads/master-prompts/fuel-audit.md`). The same rules apply, and the brief is given
to an architecture sub-agent and to Pete's own agent independently.

## Why

The project reproduces Davey et al., *Bayesian Methods in the Search for MH370* (Springer 2016, CC
BY-NC 4.0), and extends it. Everything downstream rests on the core filter. It must be shown faithful
to Davey where it claims to reproduce him, and correct where it extends him.

## What to audit

The code is on GitHub `gmkf7vfyfb-web/flight-mh370-revisited`, branch `claude-science-sep29`, folder
`Claude Science Project Sep 29/engine/`.

**1. The satellite measurement model** (`crates/satcom` and its use in `crates/mh370/src/filter.rs`).
- **BTO:**
  - the satellite ephemeris and its interpolation;
  - the aircraft position at altitude, on WGS84;
  - the bias and its sign;
  - the per-epoch σ, including the R1200 log-on values;
  - the 18:25 and 00:19 log-on handling.
- **BFO:**
  - the uplink and downlink Doppler;
  - the AES compensation, and the satellite and ground-station terms;
  - EAFC;
  - the fixed bias and its prior (Davey's 25 Hz prior sd, and the 7 Hz σ against the 4.3 Hz measured in
    Table 5.1);
  - the vertical-rate term;
  - the drifting-bias option.
- Reproduce Davey's and Holland's published worked examples where they exist, and Inmarsat's
  (Ashton et al. 2015) calibration flights.
- Check the observation table `data/satcom-observations.csv` against the published Inmarsat logs: times,
  channel types (R600 and R1200), and values.

**2. Flight dynamics and guidance** (`crates/flight/src/lib.rs`, `environment.rs`).
- The five autopilot modes, against Davey ch. 4 to 8, with printed pages. True and magnetic track and
  heading, and LNAV great circles:
  - the declination source (IGRF-14 against Davey's NOAA, p. 41);
  - winds and temperatures (ERA5 against Davey's ACCESS-G, pp. 37 and 44);
  - TAS, Mach and temperature conversions;
  - the turn dynamics and bank;
  - the manoeuvre clocks (τ) and the Mach, altitude and turn draws, against Davey ch. 8, pp. 57-59;
  - the integration step (5 s and 10 s, against Davey's 1 s, 10 s and 60 s, p. 59).
- The prior at 18:01:49: position, track 289.7° (Fig. 4.2), and the sds.

**3. The sampler** (`filter.rs`): weights, resampling, tempering, look-ahead and reallocation, the
mode probabilities from the evidence, the hand-off snapshot, and the split-half statistic. Does any
step bias the posterior, or count an observation twice?

**4. Each "Davey-faithful" claim.** Compare the configuration `config/davey2016.toml` with the book,
setting by setting, with printed pages. List every difference.

## Rules

These are the same as for the fuel audit:
- Form your findings independently, before reading the project's notes.
- Read-only: change no code and no config.
- Light compute only. Do not run the filter at scale and take no heavy lock; unit tests and small
  reproductions are fine.
- Cite printed pages, and grade each source as primary or secondary.
- Upload no local or confidential data to a third-party service.
- Every chart carries a footnote giving its run, parameters and assumptions.

## Deliverable

`results/filter-audit-<auditor>.md`, containing:
- a findings table: id, severity, file:line, evidence, fix;
- the reproduction tables;
- the Davey-fidelity table;
- a verdict;
- what was not checked.


## Sampling coverage (standing rule, Pete, 10 Oct 2026)

The aim is to sample the whole kinematically feasible space of the 777-200ER, within its performance and limits, and let the evidence select. Under-sampling silently conditions the result on an assumption nobody made. Earlier studies may have done this, for example by sampling mainly cruise at altitude to fuel exhaustion followed by an uncontrolled descent.
1. Keep three sets apart and state each one: (a) the **feasible set**: what the aircraft can physically do, with sources; (b) the **model's reach**: what your physics and parameter ranges can produce at all; (c) the **proposal's coverage**: where your samples actually land, with ESS per region.
2. Any part of (a) that (b) cannot produce, or that (c) does not reach with adequate ESS, is a **gap**. Close it, or declare it as an explicit conditional hypothesis and name it in the label of every result it affects. A silent gap is a defect.
3. You may concentrate samples for precision (importance sampling, aimed proposals, tempering, strata). The prior must still cover the feasible set, and the weights must carry the proposal correction. Sampling may follow a hypothesis; weight comes only from the evidence.
4. Do not limit the scenarios to those that fit one reading of the data. Example: sampling descents only for the R600 BFO and not the Holland-type or other rapid descents. Every standard 00:19 option and every hypothesis family (A1, A2, B) must be estimable from the same sample set. If one is not estimable (low ESS), report it as a coverage gap and propose the fix; do not drop it.
5. A parameter bound narrower than the feasible range is a gap unless it has a source. A model cap (for example on descent rate or on unloading) is a reach gap, not a sampling choice.
6. Every results note has a **COVERAGE** section: the three sets, the gaps and their status, ESS per option, family and declared region, and parameter bounds with sources. Every review checks coverage first.

This rule is in every module profile from your next turn, and in the master prompts. Architecture keeps the gap register in ARCHITECTURE.md (section "Coverage register").
