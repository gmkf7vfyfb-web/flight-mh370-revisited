# ISO Sept 28 Status: MH370 integrated estimator (iso threads)

Recovery and continuation package, snapshot of 28–29 September 2026. It is written so that another agent, AI model or person can pick up every workstream without access to the iso host.

- **Built by:** the iso thread "Modular Architecture", which owns the architecture and reviews every branch.
- **Researcher:** Pete Large.
- **Code snapshot:** MH370 `main` at original commit `3214289` (published as `f6f8873`, see [Commit identities](#8-commit-identities-and-what-is-not-here)).
- **What it isn't:** nothing here is an integrated impact estimate. The estimator is still being assembled. Every number below is labelled with the provenance classes of this repository's AGENTS.md.

## Contents

| Path | What it holds |
| --- | --- |
| `STATUS.json` | Machine-readable version of this report: threads, branches, module states, results with labels, decisions, next steps |
| `code/mh370.bundle` | Git bundle of all 14 branches of the MH370 code repository (121 commits) |
| `code/main/` | Browsable copy of `main`, including its own `README.md`, `AGENTS.md` (engineering contract) and `status.md` (core state) |
| `code/branch-diffs/` | Each unmerged branch as a diff against `main`, with its commit list |
| `code/uncommitted/` | Work in progress that is on no branch yet: tracked changes as patches, new files as tarballs, plus `checkouts.json` |
| `code/branches.tsv`, `code/commit-map.tsv` | Branch heads, and original-to-published commit hashes |
| `results/` | Small outputs of every run and module report: JSON summaries, CSV tables, PNG report pages, PDFs of 15 MB or less |
| `results/NOT_COPIED.csv` | Every run output left out (particle arrays and similar, 4.0 GB; two plots of the Boeing runs, now in `inputs/`), with size and SHA-256 |
| `data/` | Manifests of every external input (244 files, 14.7 GB) with SHA-256, what it is; the inputs index; the weather-grid manifest |
| `inputs/` | The downloaded third-party inputs themselves (198 files, 373 MB), copied as obtained, plus the small weather grids. `data/INPUTS_PUBLICATION.csv` gives every input's status (copied, redacted, linked, or too large) and source. **`inputs/acars/` contains the MH371 truth track: it is off-limits to the MH371 control (`inputs/MH371-TRUTH-WARNING.txt`)** |
| `threads/` | The master prompts that set up each thread, the approved stage-API design (`design/d1-api-proposal.txt`), and the iso thread registry |
| `decisions/` | The standing decisions and rulings made in conversation, one note per topic |
| `environment/` | Toolchain versions, Python package freeze, make targets, host layout |
| `build_export.py` | The script that assembled this folder (the report and STATUS.json were written by hand) |
| `MANIFEST.sha256` | Checksums of every file in this folder |

## 1. Methodology architecture

### 1.1 The product

The product is one reproducible Bayesian estimate of where MH370 entered the water, and where its wreckage lies. It is built as a lean core filter plus modules for each further evidence type or conditional hypothesis. Modules can be switched on individually or together. The list of modules is open-ended.

### 1.2 The core

The core is a recreation of Davey et al. (2016), *Bayesian Methods in the Search for MH370*.

- One particle filter runs per autopilot mode (true or magnetic heading, true or magnetic track, lateral navigation), and the modes are combined by evidence.
- The filter uses a manoeuvre model with a Gibbs-refreshed time constant.
- It uses a Gaussian BTO likelihood, and a BFO likelihood with a per-particle Kalman-filtered bias.
- Weather comes from ERA5 winds and temperatures; declination from IGRF-14.

It is the reference against which every change is checked, and it stays byte-identical unless a change is meant to alter it (`make regress`).

### 1.3 The integrated estimator runs in four stages

1. **Flight filter to 00:11 UTC.** For the integrated estimate the filter stops at the 00:11 handshake. A *hand-off* then resamples the full stage-1 posterior, stratified by mode and keeping each trajectory's complete state, as the starting distribution for stage 2. No preliminary "family percentages" are imposed.
2. **End of flight.** Each trajectory continues on the core dynamics until the end-of-flight module takes over. That is either a first flame-out or the start of a powered descent. The module simulates descents to the water. The runner then scores whichever 00:19 observations the configuration selects: the 00:19:29 log-on and the R600 and R1200 BTO/BFO, individually, together or not at all. Three BFO measurement models are available: no offset, a start-up offset, and inflated error.
3. **Impact modules.** Each module returns a log-likelihood per impact sample (or named predictions only). Examples are drift of debris to the finds, the seabed search, satellite sightings and hydroacoustics.
4. **Composer.** It combines any chosen set of modules. It reports:
   - evidence, effective sample sizes over descents and trajectories, split-half agreement, and the share of prior mass a module could not compute;
   - results per end-of-flight hypothesis first;
   - any average across hypotheses only beside a prior sensitivity.

### 1.4 Hook API between core and modules

The API lives in `crates/hypothesis`.

- **In the filter:**
  - adjust the prior, per stratum;
  - request extra epochs;
  - epoch log-likelihood;
  - final-state log-likelihood.
- **After it:**
  - impact log-likelihood per sample;
  - named predictions per sample;
  - or the `Terminal` trait (end of flight): `takeover_time` then `descend`, with an `Atmosphere` served by the runner.
- **Declarations:**
  - the observation IDs consumed, where each observation may be used once per run;
  - discrete alternatives with priors. An alternative shared by name (e.g. `ocean-model`) is marginalised jointly;
  - whether the likelihood is on an absolute scale;
  - prediction columns.

### 1.5 Composition rules

These are binding on every module.

1. Return likelihoods, never posteriors, and say whether they are on an absolute scale.
2. Use each observation once.
3. All impact modules share the same impact samples, with no private smoothing over location.
4. No floors. NaN means "not computed", never "impossible". Where a module cannot compute, it is treated as uninformative there (filled with its stratum's mean likelihood). The share and location of such rows are reported, and a hypothesis above tolerance is excluded from averages and Bayes factors.
5. Be accurate where the flight evidence puts its mass.
6. Measure Monte Carlo adequacy. Unconverged results are reported as unconverged.
7. Settle discrete choices by evidence, or show them as labelled sensitivities. Never average normalised maps with fixed weights.
8. Each module has a synthetic-recovery test and hand-computed fixtures.

### 1.6 Three outputs, not one

The estimator reports three outputs:
- the first water contact (end of flight);
- the acoustic source (hydroacoustics);
- the wreckage resting place on the seabed (the "Ocean impact to ocean floor" module).

The seabed search scores the resting place.

### 1.7 Engineering rules

The code repository's `AGENTS.md` (in `code/main/`) sets the engineering rules:
- one implementation, changed in place;
- exactly three markdown files in the code tree;
- generated output never committed;
- seed-stable estimates, and smoke runs are never evidence;
- published work is input, not truth;
- modules touch only their own directory and never depend on core crates or on each other.

Large or licensed inputs live outside git.

## 2. Threads and their state at the snapshot

Branch heads are original hashes; `code/branches.tsv` maps them to the published ones. "Ahead" counts commits not yet on `main`.

| Thread (iso ID) | Role | Branch @ head | State |
| --- | --- | --- | --- |
| Modular Architecture (`thr_4pbhvf3sxi`) | Architecture, reviews, merges, core requests | none | Reviews of the composer, Pleiades, hydroacoustics and ocean transport were interrupted by usage limits and must be resumed |
| Investigate persistent agent issue (`thr_mgewhqvb78`) | Core estimator: filter, dynamics, fuel, MH371 control | `main` | Stratum-weighting fix committed; corrected full base run (`make report`) in progress; MH371 control queued |
| Core stages & composer (`thr_6wkhvpqx8k`) | Stage API, hand-off, end-of-flight stage, composer | `core/stages` @ `3833f97` (2 ahead) | M3–M5 and M7 merged; composer (M6) in review, being changed to the neutral fill; should-fix list pending |
| End of flight (`thr_kaycpkjz9k`) | Terminal module: descents, 00:19 timing, endings | `hypothesis/end-of-flight` @ `3e11c21` (11 ahead) plus uncommitted latents | Three endings with a declared other-cause log-on rate; latents in progress; integration (E5) next |
| Ocean drift (`thr_faie5jqc7p`) | Shared surface-drift transport (`crates/ocean`), drift maps, GDP replay | `core/ocean-transport` @ `25818b6` (13 ahead) | Rebased and regress-clean; review pending; widened debris ensembles approved |
| Pleiades (`thr_ec96wswyz6`) | Satellite sightings (Pleiades, possible COSMO-SkyMed) | `hypothesis/pleiades` @ `0cd3bad` (8 ahead) | Review pending; exact-Poisson rework approved; refactor to `satellite-sightings` with COSMO next |
| Searched areas (`thr_uduhvqttbk`) | Seabed-search negative evidence | `hypothesis/seabed-search` @ `b73541a` (5 ahead) | Approved; merges after the composer |
| Hydroacoustics (`thr_gbqx8u9yfp`) | Predicted arrivals, IMOS search, Kadri package | `hypothesis/hydroacoustics` @ `7141e5d` (14 ahead) | Staged scope done; review pending; next steps await Pete |
| Ocean impact to ocean floor (`thr_7e786pehut`) | Settling: contact point to wreckage resting place | `hypothesis/settling` (work untracked, in `code/uncommitted/settling-untracked.tar.gz`) | First-pass physics, breakup table, readers; full-depth BRAN2016 subset approved |
| Antenna gain (`thr_vimeq9ezrd`) | Received power of the R1200 log-ons | `main` (merged) | Parked by Pete until the engine runs stably to impact |
| Implement executable core filter (`thr_dkvnnfnn3b`) | Local app (`describe.rs`, `ui/`) | `main` checkout, uncommitted | Its edits are in `code/uncommitted/main-checkout.patch` |

The master prompt that set up each module thread is in `threads/master-prompts/assembled-<name>.txt`.

## 3. Results so far

Provenance labels follow this repository's AGENTS.md. "Stand-in" and "placeholder" results exercise code paths and are **not evidence**.

### 3.1 Core flight estimate

- **[Reproduced result]** Davey et al. Fig. 10.3, the latitude PDF at 00:19 (BTO + BFO, 8 replicates of 7 million particles):
  - median 38.16°S, 95% interval 35.91–39.53°S, against the book's 37.53°S and 34.90–39.38°S;
  - the two curves overlap by 71%, and the split-half overlap is 93%;
  - the BTO-only northern mode is at 44.7°N and holds 7%.
- **[Diagnostic/sensitivity]** A pooling defect was found in review: rows were weighted by the current autopilot mode instead of their stratum. It is fixed in `47ff1b1`. Exact reweighting of the stored run gives:
  - shoulder (34.5–36.5°S) 3.5% → 3.6%, with the median unchanged;
  - complex-manoeuvres 17.7% → 17.9%, and mach-wide 10.6% → 11.1%.
  No conclusion changes. The corrected full rerun was in progress at the snapshot.
- **[Diagnostic/sensitivity]** The missing northern shoulder: the book has 25% there and this recreation 3.6%. What was ruled out:
  - weather: ERA5, NCEP FNL and MERRA-2 all agree, and wind-off doesn't restore it;
  - the satellite ephemeris;
  - the altitude and initial-Mach priors;
  - declination errors.
  A sparse-filter test reproduces a ≥25% shoulder in about 1 run in 7–12 at 7–35k particles and never at 140k. The leading explanation is that Davey's shoulder is an artefact of a filter with few surviving roots. The remaining direct test is ACCESS-G, the weather model Davey used; it has been requested. Details are in `code/main/status.md`.

### 3.2 Fuel and performance

- **[New analysis]** Fuel-flow factor from the Ulich/Boeing performance tables: about 1.009 ± 0.018 (11 in-range items), i.e. ±6–7 minutes over 6 hours from arc 1. An older public proxy over-burned Boeing's Table 3 by 41%.
- The tables themselves are Boeing-confidential and are not included.
- The fuel state enters the core next, one change at a time.

### 3.3 End of flight (placeholder; not evidence)

- **[New analysis]** An open aerodynamic baseline (Poll–Schumann B772 plus windmilling drag), calibrated to a 118.5 NM glide against Boeing's about 120 NM.
- **[New analysis]** Three endings:
  - exhausted before the log-on;
  - exhausted after it (powered through 00:19);
  - powered impact.
  "Other-cause" SDU log-ons arrive at a declared rate λ, swept.
- The log-on alone, in still air with placeholder windows, gives posterior weights from equal priors:

  | λ | Before log-on | After log-on | Powered impact |
  | --- | --- | --- | --- |
  | 0.1/h | 0.977 | 0.014 | 0.009 |
  | 0.3/h | 0.934 | 0.039 | 0.026 |
  | 1/h | 0.811 | 0.114 | 0.075 |

  With fuel, each path's exhaustion time will replace the placeholder windows.
- Impact distance beyond the arc, 1–99%:
  - before the log-on: 111 NM beyond to 79 NM inside;
  - after the log-on: up to about 418 NM beyond;
  - powered impact: up to about 349 NM beyond.

### 3.4 Ocean drift

- **[New analysis]** Shared transport: currents plus windage times ERA5 10 m wind, a midpoint step on WGS-84, and a GSHHG coastline.
- GDP-replay transport kernels (Student-t ν and scale) and skill:
  - GLORYS12: 2.73, 77 km;
  - OSCAR v2: 2.62, 72 km;
  - BRAN2016: 3.68, 94 km;
  - skill 0.49–0.60, against 0.10 for currents only.
- **[Diagnostic/sensitivity]** A threading bug in the ERA5 wind extraction had corrupted 143 of 14,544 slices of the 3-hourly file (31 of 4,128 in the hourly one). It is fixed, and the drift maps were rebuilt.

### 3.5 Pleiades and possible COSMO-SkyMed sightings (conditional)

- **[Reproduced result]** Griffin & Oke's BRAN2016 endpoints from 35.6°S 92.8°E land 20–30 km from PHR_4.
- **[New analysis, stand-in on the 00:19 positions]**
  - marginal Z_H = 6.4e-4;
  - P(H | D) = 0.0006, 0.006 and 0.06 at an expected number of detectable objects K·η = 1, 10 and 100;
  - given H, the median is 36.8°S, with 45% in 34.5–36.5°S.
- **[New analysis]** With transport errors of about 75 km and scenes of about 20 km, the chance that MRO debris drifts into the scenes (P_in) is about as large as the cluster-match term (median ratio 1.15–1.24). So in the *mixed* (H or not-H) result the cluster positions barely discriminate impact sites. The information is in the posterior *given* H and in P(H | D). An exact Poisson formulation (rate grid; Jeffreys prior on the background rate) is approved.
- **[New analysis]** Four possible COSMO-SkyMed radar targets, 21 March, from a briefing slide used by Iannello:
  - each lies 49–81 km from the nearest Pleiades cluster;
  - the attribution is unverified;
  - dawn-dusk SAR orbits put a pass near 00:00 or 12:00 UTC at 91.5°E, not 04:00.
  The joint model links a target to a Pleiades cluster through a 2-day drift, so shared drift is counted once. An impact-free link test is planned. Provenance, acquisition time and footprint are still needed.

### 3.6 Seabed search

- **[New analysis]** P(no find | y) = ρ + (1 − ρ)·Π_k(1 − q_k c_k(y)), using coverage rasters from the GA/AusSeabed Phase 2 5 m mosaics (CC BY 4.0).
  - The Ocean Infinity 2018 outline is a labelled, inferred variant only.
  - Outside every searched area the likelihood is exactly 1.
- **[Diagnostic/sensitivity, stand-in]** Phase 2 coverage (120,487 km²) held 96.3% of the 00:19 mass. 60–87% of the mass stays on searched ground for ρ = 0–0.2. On placeholder impacts spread ±50 NM around the arc, only 17% stays there at ρ = 0.05. The spread of real impacts will decide.

### 3.7 Hydroacoustics (predictive only)

- **[New analysis]** Pre-registered IMOS search, with windows fixed by rule before any data were opened:
  - 0 detections at the Perth Canyon and Portland loggers;
  - 1 at Scott Reef, whose path is blocked (p = 0.51).
- P(any IMOS logger detects) is 0.24 at the F-35A-anchored coupling, 0.095 at a tenth of it and 0.005 at a thousandth. The silence is weak evidence.
- **[Diagnostic/sensitivity]** The Curtin 01:33–01:34 event, checked against impacts up to 500 NM beyond the arc and up to 01:40, fails both the bearing and the two-station timing tests. It stays a control.
- **[Reconstructed analysis, on Kadri (2024) published figures and table]**
  - Our travel times reproduce 16 of 18 Table 1 offsets to about 7 s.
  - One row looks like a sign typo, and one "on the arc" transient (00:39:02) arrives 52 s too early for an impact on the arc.
  - None of the Table 1 transients stands out in the published Figure 9 traces (at most 3.2 dB).
  - Of six crash examples, only the F-35A and Lion Air 904 are timing-consistent. So the loudness scale rests on the F-35A alone, whose level depends on processing by 3–4 dB.

### 3.8 Antenna gain (parked)

- **[Reconstructed analysis]** The earlier MH371 preference for "no precompensation" (+2.45 log-evidence) falls to +1.46 with a free receive-chain offset, and to −0.23 once the 02:00 burst is dropped. It rested on calibration and a single burst.

### 3.9 MH371 known-flight control

- Built and committed before any run: window by rule (Davey Fig. 9.7), BTO only, regional ERA5, pass rule declared.
- A pre-fix run was stopped unscored. It runs once, after the fix.

## 4. Decisions in force

Full notes are in `decisions/`.

- **Framing** (Pete):
  - no unpiloted end of flight is assumed;
  - Boeing/ATSB unpiloted runs and Holland's BFO reading are conditional hypotheses, never anchors;
  - the 00:19 reboot caused by fuel exhaustion is a hypothesis, not an axiom.
- **Methodology decisions of 28 Sep:**
  - Adopted:
    - a settling module ("Ocean impact to ocean floor");
    - a speed prior limited to flyable speeds;
    - the 00:11 vertical speed inferred, with descent-onset and altitude options;
    - wider end-of-flight hypotheses (powered through 00:19, later exhaustion, powered impact);
    - attitude and electrical state modelled in end of flight.
  - Deferred until the engine runs stably to impact:
    - a breakup field shared across modules;
    - a start-up BFO offset conditioned on outage duration;
    - leave-one-out and information-gain reporting;
    - the Blackman calibration set.
  - Parked: the satellite census, and antenna-gain integration.
- **Core changes:** one at a time, each checked for split-half stability and against the blind MH371 control. The order is fuel state, then speed prior, then vertical speed and descent onset, then 00:11 altitude bands.
- **Rulings:**
  - the seabed-search bilinear coverage is part of the data model;
  - Ocean Infinity geometry is never committed;
  - off searched ground, the search likelihood is 1.
- **MH371 stays blind:** only its scorer reads the ACARS truth. Files that contain MH371 truth must not be opened by anyone building or tuning the estimator.

## 5. Intended next steps

1. Resume the interrupted reviews: composer, Pleiades, hydroacoustics, ocean transport. Then merge in this order: composer (with the neutral fill, `family_groups`, takeover documentation, should-fix items 1–7), then the reviewed modules.
2. Core estimator:
   - finish the corrected base report;
   - run the MH371 control once;
   - then fuel state, speed prior, vertical speed and descent onset, and 00:11 altitude bands, each on its own branch and each checked.
3. End of flight:
   - latents: electrical configuration, APU and RAT timing, SDU outage, attitude, envelope and breakup risk;
   - integration with the real stage;
   - per-hypothesis previews with ERA5;
   - fuel-state exhaustion times replacing the placeholders.
4. Settling:
   - first-pass physics and survey (AF447 and other analogues);
   - the transform-column API, so the seabed search scores resting positions;
   - the same mechanism later serves the deferred breakup field.
5. Satellite sightings:
   - exact-Poisson rework;
   - refactor with COSMO as a second set (two candidate acquisition times);
   - 21 March drift maps.
6. Hydroacoustics, awaiting Pete's go-ahead:
   - widen the windows for the new endings;
   - Blackman calibration;
   - IMOS non-detection as a weak likelihood;
   - review of the Kadri package, with questions arising from the published-material tests. Nothing is sent without Pete.
7. The first integrated run to impact. Then remind Pete of the deferred items and the paid aerodynamic-model options.

## 6. How to continue

```bash
# Code: every branch, with history (hashes are the published ones; see code/commit-map.tsv)
git clone "code/mh370.bundle" MH370 && cd MH370   # checks out main
git branch -r                                     # all 14 branches

# Uncommitted work (apply to the branch named in code/uncommitted/checkouts.json)
git switch hypothesis/end-of-flight && git apply "../code/uncommitted/end-of-flight.patch"
tar -xzf "../code/uncommitted/settling-untracked.tar.gz"   # on hypothesis/settling

# Toolchain: Rust 1.98 and Python 3.14 (environment/); then
make venv && cargo test --release    # under a minute
make fixture                         # integrated run at smoke scale, about 20 s
make regress                         # base byte-identical to main
```

Inputs are not in git. For each input, `data/MH370-inputs-manifest.csv` gives its path, size, SHA-256 and origin, and `data/MH370-inputs-INDEX.txt` gives the sources.
- The public ones are re-fetched by the scripts in `code/main/.sources/`: ERA5, ocean reanalyses, drifters, bathymetry and IMOS.
- The weather grids that live in `data/*.bin` are listed with checksums in `data/data-grids-manifest.csv`. They are rebuilt by `.sources/era5-weather/`, `.sources/weather-sensitivity/` and `.sources/igrf14-declination/`.

Work rules are in `code/main/AGENTS.md`:
- a hypothesis branch touches only `hypotheses/<name>/` (`make scope`);
- core changes must pass `make regress`;
- an intended estimate change gets its own commit, `make report` and a `status.md` update.

The iso set-up used one git worktree per thread and serialised heavy jobs with `flock`. Any equivalent works.

## 7. Results files worth opening first

- `results/core-main-checkout/davey2016/summary.json`: the base estimate, before the stratum fix; the reweighted numbers are in `code/main/status.md`.
- `results/worktree-hydroacoustics/hydroacoustics/report-page-1.png` to `report-page-6.png`, and `kadri-tests/kadri-tests.png`.
- `results/worktree-searched-areas/seabed-search-analysis/*.png`.
- `results/worktree-pleiades/pleiades-standin/*.png` (stand-in).
- `results/worktree-end-of-flight/end-of-flight/preview/` (placeholder).
- `results/worktree-core-stages/fixture/`: the composer's report pages on placeholder impacts, with their banner.
- `results/architecture-thread/airgun-2001-air9.png`: calibration geometry, HA01 and Diego Garcia.

## 8. Commit identities and what is not here

**Commit identities.** Author and committer identities in the published history are replaced by `MH370 iso agents <mh370-iso@invalid>`, because the originals contain a personal email address. Rewriting changes the commit hashes; `code/commit-map.tsv` maps every original hash to its published one. Hashes quoted in thread messages and `status.md` are originals.

**Inputs (added 29 Sep, at Pete's request).** The downloaded third-party inputs are now in `inputs/`, copied as obtained. That includes the ACARS workbook (MH371 truth, off-limits to the MH371 control), the raw SITA log, the Boeing end-of-flight simulator runs and their plots, the Ocean Infinity 2018 community outline, and papers. The exceptions are listed in `data/INPUTS_PUBLICATION.csv` with their public sources.
- **Linked, not copied, because they carry an explicit restrictive notice:**
  - the Ulich fuel workbook, whose tables say they come "from a Boeing FPPM from a confidential source"; the author's public copy is linked;
  - Appendix 1.6E of the Malaysian Safety Investigation Report ("Copyright © Boeing"); the report itself is on the Malaysian MOT website;
  - EUROCONTROL BADA documents, a MathWorks page and the Lissys Piano-X guide, all marked all rights reserved.
- **Redacted:** the Ball antenna compilation is included with its page of ARINC Characteristic 741 (a paid standard) removed.
- **Too large for plain Git; public and regenerable:**
  - the ocean fields (about 13 GB);
  - the IMOS recordings zip (566 MB);
  - the ERA5 and MERRA-2 weather grids;
  - the particle arrays (4 GB).
  These can go to the Hugging Face companion dataset on request.

**Still left out:**
- drafts of correspondence not yet approved by Pete: the Kadri cover letter and requests, and the Metz/Royer asks;
- raw conversation transcripts. Their content is carried by this report, `STATUS.json`, `decisions/` and the master prompts.

This repository's AGENTS.md asks that it be kept private until source rights, personal data and unpublished analysis have been reviewed. This folder contains unpublished analysis.
