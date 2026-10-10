# SEARCHED_AREAS inbox

The architecture session appends here. Read at the start of each working session.

## 2026-10-08 - architecture: start here

`threads/master-prompts/searched-areas.md` is authoritative and supersedes the ISO `.txt`.

**Four things before you design anything.**

1. **Average alternative settling draws; never multiply them.** They are alternative outcomes, not
   extra wreckage. There is a test for it in section 8 and it is the easiest error in the module.
2. **The residual PDF is a view in the composer, not a pipeline of yours.** You return one
   likelihood column. Never ingest a posterior that already contains it.
3. **Your first deliverable is a citation task.** Davey ch. 11 sets out the update and does not apply
   it; Stone et al. 2014 applied it to AF447. Both PDFs are in the artifact store. Get the printed pages
   into the ledger before anyone writes the novelty sentence.
4. **The surface search is drift's, not yours; bathymetric mapping excludes nothing.**

**Much is already built and approved** - the M3 migration at `b73541a`, the 0.01 deg bilinear coverage,
`ln L = 0` off searched ground. Port and reproduce before you change anything.

**Shared-ocean boundary applies:** bathymetry for terrain masking comes from the shared ocean-transport
owner. Raise what you need in `coordination/OCEAN_TRANSPORT.md`.

## 2026-10-08 - architecture: Davey ch. 11 alignment - read `results/davey-ch11-alignment.md`

Two required additions to your brief:

1. **The reduction test.** With rho = 0, a point target at the impact location and a single cumulative
   campaign, your likelihood must reproduce Davey's eq. 11.1, `[1 - P_D(x)]`, to numerical precision.
   That is what makes "we extend Davey" checkable.
2. **Report Davey's eq. 11.2, probability of success per candidate area, as an output** of every
   residual-PDF view. It is the quantity a search planner uses and it costs nothing.

## 2026-10-08 - architecture: overnight work plan

1. **The citation task**: Davey ref. [40] against the book's reference list; ch. 11 pp. 101-102 and Stone
   et al. 2014 into a project citation ledger at `results/citation-ledger.md`, by printed page.
2. **The detectable-target definition**, to `results/`, before code.
3. **Port the M3 module** onto `hypothesis/seabed-search` and reproduce the fixture numbers.
4. **The reduction test** to Davey eq. 11.1.
5. No downloads.

### Overnight rules for every module, 8-9 October (binding until Pete is back, ~08:30 MT)

- **CPU:** core's 16-hour run is live until about 08:30 MT. Build with `cargo ... -j 4` and run nothing
  heavier than 4 threads. If the core run is slowed, everything downstream waits on it.
- **Disk:** 38 GiB free and falling while core writes. **Download nothing** unless your entry below
  says you may, and then only within the stated cap. Never save a multi-GB file as an artifact. Never
  let free space fall below 25 GiB - check `df` before each file.
- **Nobody can answer you tonight.** If you hit a question only Pete or the architect can answer,
  write it in `coordination/architecture.md`, choose the more reversible option, label the work
  provisional, and keep going. Do not stop and wait.
- **Concurrent appends:** if a push conflicts on a coordination file, keep BOTH entries in
  chronological order. Never resolve by taking one side.
- **Finish the night with a dated entry in `coordination/architecture.md`**: what landed, with commit
  hashes; what is provisional and why; what you need in the morning.

## 2026-10-09 01:58 UTC - architecture: URGENT - CPU, read before your next run or build

**Machine load is 112 / 142 / 154 on 18 cores** (1/5/15-minute averages). Core's 16-hour run is on
seed 2 of 8 and every minute of oversubscription moves its 08:30 MT finish later.

**My overnight rule was incomplete.** `cargo -j 4` limits compilation only. Engine binaries and test
suites use every core through Rayon regardless. From now until core posts DELIVERED:

1. **Every engine run and test: `RAYON_NUM_THREADS=2`**, and `cargo test ... -- --test-threads=2`.
2. **No full-scale or pilot runs.** Smoke-scale only. End of flight: the children-per-parent pilot waits
   for the morning. Settling: first-pass runs at smoke scale only.
3. **No more than one heavy process per module at a time**, sub-agents included. If you have spawned a
   sub-agent that runs code, tell it the same.
4. **Disk:** free space fell to about 1.2 GiB around 01:45 UTC and has recovered to 41 GiB; the writer
   is not identified. If your session wrote and deleted large files in that window, say so here. The
   25 GiB floor stands.

Code-reading, writing, review, literature work and small tests are unaffected. Keep going on those.

## 2026-10-09 ~00:30 UTC - architecture: start now; your sequence (initiative rule: see architecture.md, same date)

**CPU clearance.** Core's 14 h reference run finished this morning (07:19 MT), so the normal rules apply:
- heavy work goes under the lock, with up to 12 threads;
- everything else runs at 2 threads.

Core may take the lock tonight for a re-run. If it does, stay at 2 threads; nothing in steps 1 to 4
needs more.

**Your coordination mechanism is as you described it.** Confirmed.

**The two items your brief marks for architecture:**
- **Residual view:** it is a composer view. Comparing the posterior with this module enabled and
  disabled is sufficient, and no dedicated output is needed.
- **Bathymetry:** owned by ocean transport, as one surface shared with settling and hydroacoustics.
  If you need it before then, use a stub and disclose it in `OCEAN_TRANSPORT.md`.

**Settings carried from earlier rulings:**
- ρ = 0.05 as the reference, with a sweep;
- 0.01° coverage resolution;
- an ATSB-only arm;
- settling draws are averaged, never multiplied;
- never ingest your own likelihood;
- the method must reduce to Davey eq. 11.1, and you report eq. 11.2.

**Sequence, your brief §7:**
1. The citation task (Davey ref. [40] against Stone et al. 2014).
2. The detectable-target definition, written to `results/` before any code.
3. Port M3 and reproduce its fixture numbers.
4. Repeat-search dependence, dependent and independent.
5. Run on end-of-flight impact samples with a point-target placeholder:
   - now on smoke-scale samples, labelled "295.66° prior";
   - at full scale once the end-of-flight sweep exists;
   - then on settling's wreckage samples.
6. The residual-PDF views. Build them against `crates/compose` directly in a module-local test, since
   the runner stage is not yet wired.
7. The 2025-26 inferred variant, reported separately.

- Modular Architecture


## 2026-10-09 ~04:15 UTC - architecture: rulings for searched areas (S1-S5)

Your rulings are in `architecture.md` under this timestamp. Carry on with your sequence.

- Modular Architecture

## 2026-10-09 ~06:00 UTC - architecture: overnight rule, agreed by Pete

Read the ~06:00 UTC entry in `architecture.md`. Overnight, a question for Pete is recorded with its
options, and your recommended option is taken PROVISIONALLY and reversibly; then carry on. It does not
cover irreversible, licence, outreach, third-party or long-run decisions. Do not take the heavy lock
(core's run).

- Modular Architecture

## 2026-10-09 ~14:45 UTC - architecture: reference-289 delivered; your next step

Read the ~14:45 UTC entry in `architecture.md`. Your item is listed there by module.

- Modular Architecture

## 2026-10-09 ~16:40 UTC - architecture: exchange directory and the run-provenance convention

Impacts and other cross-session data go through `/Users/pete/Downloads/mh370-exchange/`. Every results
note records the prior track and base config from `run.json`. See `architecture.md` ~16:40 UTC.

- Modular Architecture

## 2026-10-09 ~18:30 UTC - architecture: Pete's decisions

Pete's decision: use and commit the OI 2018 and 2025-26 outlines, footnoted with the source (the MH370-CAPTION community tracing, grade C) and as inferred from vessel tracks. The brief's 'never commit' line is withdrawn. See `architecture.md` ~18:30 UTC.

- Modular Architecture

## 2026-10-09 ~19:50 UTC - architecture: 00:19 priority order

Pete's order is held out, R600, Holland H1, Holland H2, with `inflated` after them. Build your panels
in that order. End of flight supplies the H1 against H2 evidence first.

- Modular Architecture

## 2026-10-09 ~20:20 UTC - architecture: STANDING RULE (Pete) - every chart carries a footnote with its run information

Every chart, in a results note, a PDF page or a module report, carries a footnote beneath it giving:
- the run or runs used, by name, with the prior track and base config read from `run.json`;
- the key parameters and options: the 00:19 option and BFO model, the families, the ocean model, N,
  seeds and particle counts;
- the main assumptions, and anything provisional.

Keep all of this beneath the chart, never inside the axes, in line with Pete's figure conventions.
Apply it to new charts now, and to existing charts when they are next regenerated.

- Modular Architecture

## 2026-10-10 ~02:00 UTC - architecture: second machine (Pete's SSH host)

Pete has brought up an internal SSH host, `abiome-deskstar`, authorised for all restricted items.
It is not yet registered in the session Compute panel, so no session can reach it yet.

- Planned split: core runs on the host; drift, end of flight and the downstream modules stay on the Mac.
- Details are in `architecture.md` (~02:00 UTC). No credentials are kept in the repo.

- Modular Architecture

## 2026-10-10 ~03:45 UTC - architecture → all: OVERNIGHT PLAN

Read `coordination/OVERNIGHT-2026-10-10.md` in full. It sets out the sequence, the pre-approved runs and
their triggers, the routing table for posting, and the inbox watcher (`threads/inbox-watch.sh`), which keeps
sessions awake. Pete's paste of the overnight instruction into your thread is his approval of it.

- Modular Architecture


## 2026-10-10 04:05 UTC - end of flight: impact times vs 00:19:37 and the unanswered 01:15:56 handshake (answers architecture ~03:20)

`results/eof-impact-time-oct10/README.md` (reference-289, 4 seeds). PROVISIONAL-OVERNIGHT.
- **Held out does not enforce that the 00:19:37 burst was sent:** 10.2% of `none__other` weight impacts before 00:19:37. Every option that scores a 00:19 burst enforces it already.
- **Defect, mine:** the fuel-exhaustion log-on term does not require the aircraft to be airborne at 00:19:29. `none__fuel-exhaustion` puts 3.0% of its weight before 00:19:37.
- **Two declared variants, default off:** `+alive` (airborne at 00:19:37.443) and `+silent` (`+alive`; not powered at 01:15:56; under `other`, no unseen APU log-on after a later flame-out).
  - `+alive` changes only held out: 36.78 -> 36.95 S.
  - `+silent` keeps 10-56% of the weight under `other` and moves medians 0.4-1.2 deg north.
- **Question for Pete** (options: plain / `+alive` / `+silent`): which constraint is the reference for downstream modules? **Taken provisionally: `+alive`, with `+silent` as a labelled sensitivity.**
- **For hydroacoustics:** under `+alive` no impact precedes 00:19:37.443. Impacts after 01:15:56 are <= 1.9%, and none is powered at 01:15:56 under `+silent`.

- End of Flight Module
## 2026-10-10 ~23:30 UTC - searched areas (own note): g_k implemented, point target unchanged

Size response and field model landed in `lib.rs`; `results/seabed-size-response.md`. Default path is
byte-identical, so no run is invalidated. Settling's fields can now be swapped in: average the draws.

## 2026-10-10 ~05:00 UTC - ocean settling: wreckage-field update (reference-289, Pete's four 00:19 options, plain and +alive)

`results/settling-wreckage-field-289-priorities/`. These are the seabed wreckage PDFs (settled mass-weighted, real ocean) for held out, R600 as observed, H1 and H2.
- The plain map is unchanged. A new `-alive` version follows end of flight's recommended `+alive` reference: held out's 90 % area becomes 739,000 km², against 701,000 plain.
- Settling adds 0.1-0.3 % to the 90 % area wherever the option is estimable. H1 and H2 are NOT ESTIMABLE (impact ESS 36 and 82).
- The settled-offset kernel is unchanged: p50 0.35 km, p90 2.9-3.6 km.
- For your likelihoods: the seabed wreckage PDF is the impact PDF to about 1 % in area, so the impact PDF can stand in for it at 6 NM resolution.
- A re-run on `end-of-flight/next-run/READY` is pre-approved, and the driver `wreckage_field_rerun.sh` is ready.

- Ocean Settling

## 2026-10-10 ~05:30 UTC - ocean settling -> searched areas: field extent and wreckage samples (answers your ~23:30 entry)

`results/settling-field-extent-289/`: the field extent per wreckage draw, from held out on reference-289 (200,000 draws). It is measured from the draw's mass centroid, in km, as p10 / p50 / p90 over draws:

| family | structural R90 (km) | any settled piece, R_max (km) |
|---|---|---|
| broken | 0.54 / 1.06 / 2.05 | 3.8 / 13.8 / 31 |
| fragmented | 0.40 / 0.86 / 1.86 | 3.6 / 12.9 / 29 |
| intact | 1.6 / 3.6 / 7.5 | 4.5 / 13.6 / 31 |

- So the extent is on your coverage-gap scale. A point target understates intact fields in particular.
- **Samples** for your g_k integration are in `/Users/pete/Downloads/mh370-exchange/settling/reference-289-wreckage-field/` (README.txt there). They cover all four priority options.
  - One (row, draw) is one equally weighted outcome. The files give per-element positions, class, family, fate and mass.
  - `+alive` is a filter on impact time.
- **No height or plan length** is given: settling has no height model, and your saturation result says it is not needed.
- **Burial and terrain shadow** are not modelled by settling; they stay in your ρ.
- PROVISIONAL: breakup table, dive class (b), Boeing glide, uncorrected fuel.

- Ocean Settling

## 2026-10-10 ~04:45 UTC — Pléiades: branch re-run under end of flight's `+alive` reference (held out). PROVISIONAL-OVERNIGHT

`results/pleiades/branch-289-alive/` (README, `plain-vs-alive.csv`, footnoted figure). Run on reference-289 / eof-289-full, 4 seeds, with the labels provisional sampler (F1) and uncorrected fuel. The `+alive` factor is end of flight's own, imported read-only.
- **The conditional under H widens by 8-19 %.** P+C4 after Phase 2 + Bluefin-21 + OI 2018 + 2025-26 goes from 59,316 to 70,424 km². The median moves 0.02-0.05° south.
- **Under H the searches remove more.** The share of P+C4 mass they leave is 0.555 under `+alive`, against 0.625 plain; the unconditional share goes 0.686 → 0.676. This runs the same way as searched areas' 04:20 finding: the removed early impacts sat off searched ground.
- **Still no tension.** ln S is 0.54-0.85 (plain: 0.77-1.31).
- **For searched areas and hydroacoustics:** the Pléiades conditional now uses the same `+alive` impact weights as yours. The overnight driver (`prepare/rerun_next.py`) runs every option both plain and `+alive` when `next-run/READY` appears.

— Pléiades

## 2026-10-10 ~05:30 UTC - core: (b) LARGE RUN COMPLETE, hand-offs ready (trigger written)

**`/Users/pete/Downloads/mh370-exchange/core/next-run/READY` is written.** Four strata, seeds 1-4, 3.5M per
seed, hand-offs at m2241 and m0011 (100,000 rows; `handoff.toml` carries both tanks), `tanks.npy` (float64).
Combine strata by P(family): free 0.69, Davey dynamics 0.15, descent-climb 0.14, routes 0.01.
Mixture 00:19 median -37.15 (00:11 -36.23). **Split-half not converged in any stratum** (0.71-0.88 against
0.896). Right engine dry before 00:11: 22-37 % of weight by stratum (one engine ~4 min before 00:11).
Note `results/next-run-b.md`. Labels: PROVISIONAL-OVERNIGHT, deskstar, track 289.7.
- **End of flight:** the pre-approved sweep can start on this trigger. Hand-off rows can carry a stopped
  right engine (tanks.right_kg = 0, right_exhausted_unix_s finite) with the aircraft still flying twin-engine
  speed and level, because (b) does not model one-engine flight; please treat those rows per your design and
  label them.
- **Davey-only baseline** done (converged; median -37.95; overlap 0.750).
- **(a)** passed its smoke and preflight and is running (two lanes x 44 threads); comparison when it lands.

- Core

## 2026-10-10 ~05:45 UTC - architecture: review of core's (b) landing. GO for the pre-approved downstream work, with labels

I read `results/next-run-b.md` and the trigger (`core/next-run/READY`, 05:29Z, 14 GB). **Go** for end of
flight's pre-approved sweep, and after it for the downstream re-runs. Every result built on (b) carries these
labels:

- **`core (b): split-half NOT converged`.**
  - Every stratum is under the 0.896 floor at four seeds: free 0.709, routes 0.812, descent-climb 0.785,
    Davey dynamics + radar 0.878.
  - The free stratum carries P(family) 0.69. Its seed medians span −36.61 to −37.42, and its log Z spans
    1.5 nats across seeds.
  - So **P(family) and the mixture median of −37.15 are not converged.** Report them as such, never as the
    answer.
- **`two-tank bookkeeping only`.**
  - 22-37% of the weight has the right engine dry before 00:11, a median of about 4 min, and still flies
    twin-engine speed and level.
  - End of flight treats those rows per its design and labels them. A comparison with C-7(a) follows when
    (a) lands.
- Plus the usual labels: deskstar, track 289.7, Inmarsat ephemeris, internal-v1 fuel, PROVISIONAL-OVERNIGHT.

**The full-scale Davey-only baseline is converged** (split-half 0.939; median −37.95; overlap with Davey
Fig. 10.3 0.750). It is the paper's without-fuel comparison.

**Not changed overnight:** nobody re-runs core for convergence tonight, because that would reshape a run.
I will put the convergence options to Pete in the morning, for example 8 seeds or more particles in the
free stratum.

- Modular Architecture

## 2026-10-10 ~07:20 UTC - core: (a) against (b), for information; (b) stays your base tonight

- **(a)** (C-7(a): one-engine flight after the first flame-out) is complete: `mh370-exchange/core/next-run-a/READY`,
  note `results/next-run-a.md`. Mixture 00:19 median **-36.89** against (b)'s -37.15 (00:11: -35.96 against
  -36.23); P(family) free 0.55, Davey dynamics 0.25, descent-climb 0.18, routes 0.02. The weight on one engine
  at 00:11 falls from 0.22-0.37 to 0.15-0.28 by stratum. Do not switch to it tonight.
- **Fuel-model finding that touches both runs:** internal-v1's one-engine (live-engine) flow is 2x its source
  tables, so every one-engine phase in (a) and (b) is about half its true length (CORE_STAGES ~06:10). The
  twin-engine burn is unaffected. Treat (b)'s and (a)'s exhaustion times and engine states as carrying this label.

- Core

## 2026-10-10 ~08:40 UTC - architecture (stand-in for end of flight): new impacts on core (b) are ready

**`/Users/pete/Downloads/mh370-exchange/end-of-flight/next-run/READY` is written** (08:36Z). End of flight was idle, so an architecture stand-in ran its pre-approved sweep on core (b) m0011 hand-offs, with no code changes. Labels: **core (b) split-half NOT converged; two-tank bookkeeping only; PROVISIONAL-OVERNIGHT; run by an architecture stand-in on EoF's behalf; EoF to review.**

- Layout as `eof-289-full`: `<stratum>/seed-<1..4>/{impacts.npy, run.json, terminal.json, COLUMNS.txt, SHA256SUMS}` for `next-free`, `next-repro-radar`, `next-descent-climb`, `next-routes`. Now 106 columns: the 16 burst-state latents are new. Read `impact_columns` from run.json.
- EoF `3c6319f`, binary sha256 `bcb6b252...`. Recipe: eof-289-full (N = 8 children x 4 descents, same 00:19 options). Two changes: the descent idle floor is ON, and core's `s6-tanks.toml` is dropped because EoF's schema has no `fuel.tanks`. EoF reads the single pool only; no one-engine phase is modelled.
- Combine strata by core's P(family): free 0.69, Davey dynamics + radar 0.15, descent-climb 0.14, routes 0.01 (unconverged, held fixed). Mixture medians (deg): held out -37.03; R600 inflated -37.83 (other) / -37.60 (fuel-exhaustion); R600 no-offset -37.42; R1200 inflated -36.60; both inflated -37.14.
- Split-half: no option passes 0.896 in the free stratum (best 0.880) or in descent-climb. Davey dynamics + radar passes 10 of 24 rows and routes 2. Every mixture number is unconverged. Full tables are in `next-run/README.md`.
- **Searched areas:** your pre-approved re-run can start on this trigger. Carry both labels into the chart footnote.

- Modular Architecture

## 2026-10-10 ~10:08 UTC - architecture (stand-in for hydroacoustics): search windows re-derived on core (b) impacts. PROVISIONAL-OVERNIGHT

`results/hydroacoustics-next-run-b-standin.md` (+ `.png/.pdf`, data in `results/hydroacoustics-next-run-b-standin/`). **Labels:** core (b) split-half NOT converged; two-tank bookkeeping only; PROVISIONAL-OVERNIGHT; EoF sweep run by a stand-in; uncorrected fuel; provisional sampler. **Run by an architecture stand-in on the module's behalf; module to review.**
- **Recipe:** the module's `prepare/search_windows.py` @ `438c9e9` (unchanged, sha256 `1b05492b…`). Weights: EoF `option_posteriors` @ `15ba915` (byte-identical at `3c6319f`). It ran once per stratum on `end-of-flight/next-run/`, at 1-2 threads, with no code changes. A stand-in wrapper combines strata by core's P(family) (0.6948 / 0.1527 / 0.1376 / 0.0149, held fixed) and reproduces the script per stratum exactly (0 of 4,896 quantiles differ).
- **Validation:** the pre-registered gate was NOT run, because EoF has no impact-time-shares JSON for next-run. ESS matches EoF's sweep summaries and `mixture.json` to ≤ 1e-13 relative.
- **Held out +alive (mixture):** 0.5 / 50 / 99.5 % at 00:19:58 / 00:40:16 / 01:11:26 UTC (ref-289: 00:19:58 / 00:40:18 / 01:29:24). Share after 01:15:56 is 0.26 % (ref-289 2.1 %). Medians and early edges are within about 1 min; the late tails of `other`-cause arms are 3-21 min shorter. The descent idle floor is now ON; the cause of the shift has not been attributed.
- **Recommended SOFAR windows, +alive / +silent:**
  - H01W 00:25-02:05 / 00:25-01:50
  - H08S 00:45-02:30 / 00:45-02:15
  - H08N 00:50-02:30 / 00:50-02:15
  - Perth Canyon 00:25-02:05 / 00:25-01:55
  - Scott Reef 00:35-02:25 / 00:35-02:10
  - Portland 00:50-02:30 / 00:50-02:20
  - Starts are unchanged and ends are 5-20 min earlier than on reference-289. **The module's raw IMS request (H01W 00:25-02:20, H08S/H08N 00:45-02:50) still covers everything; no change is needed.**
- **The end edges are still UNCONVERGED:** 134 of 640 estimable +alive/+silent rows, all `other`-cause, with a replicate spread of 5.0-13.9 min.
- **H1 and H2 are NOT ESTIMABLE:** ESS 86 and 124.

- Modular Architecture (stand-in for Hydroacoustics)

## 2026-10-10 ~10:23 UTC - architecture (stand-in for ocean settling): wreckage-field update on end of flight's next-run (core (b)) impacts

`results/settling-next-run-b-standin.md` with figures in `results/settling-next-run-b-standin/`. Labels: **core (b) split-half NOT converged; two-tank bookkeeping only; PROVISIONAL-OVERNIGHT; EoF sweep run by a stand-in; run by an architecture stand-in on settling's behalf; settling to review.**
- Settling's own recipe (`wreckage_field_rerun.sh`, scripts at d3b2d24; settling 9823b4e, bit-identical on settling's 500-impact check; EoF tools 3c6319f) ran once per stratum, plain and `+alive`, at the reference scale (200,000 / 40,000 per option), 2 threads, no lock, no code changes. The P(family) mixture (0.6948/0.1527/0.1376/0.0149, held fixed, unconverged) was composed by a stand-in script around settling's unchanged renderer.
- **Settling still adds under 0.5 % to the 90 % area** where estimable: mixture +0.13 % (held out), +0.34 % (R600 as observed); strata +0.17-0.44 %. The settled-offset kernel is unchanged (p50 0.34-0.37 km, p90 3.4-3.9 km). The seabed PDF of the main wreckage is still the impact PDF to under 1 % in area.
- **90 % seabed areas in the mixture:** held out 552,300 km² (reference-289: 701,300; `+alive` 577,500 against 739,000); R600 as observed 235,400 (266,500). The change comes from core (b) and end of flight, and is unconverged: held out spans 314,100-621,500 km² across strata.
- **H1 and H2 remain NOT ESTIMABLE** (mixed-weight impact ESS 86 and 124; 34-125 per stratum).
- For settling: impacts outside the ocean window (not computed, excluded) reach 0.035-0.048 % in some estimable single-stratum panels and 0.30 % in routes-H1, above the "<0.02 %" note. The mixture share is 0.016 %. The window was not changed.

- Modular Architecture (stand-in for Ocean Settling)

## 2026-10-10 ~11:45 UTC - architecture (stand-in for Pléiades): conditional branch on end of flight's next-run (core (b)) impacts. PROVISIONAL-OVERNIGHT

`results/pleiades-next-run-b-standin.md`, figures and tables in `results/pleiades/next-run-b-standin/`. Labels: **core (b) split-half NOT converged; two-tank bookkeeping only; PROVISIONAL-OVERNIGHT; EoF sweep run by a stand-in; run by an architecture stand-in on the Pléiades module's behalf; module to review.**

- **Recipe:** Pléiades' own `prepare/rerun_next.py` at `ed85311`, with no code changes, run once per stratum on 4 strata x 4 seeds (51.2 M impacts), all 20 options (10 plain + `+alive`), 2 threads. Strata are mixed afterwards by core's P(family), held fixed, using the module's own `summarise()`; the mixture check against each stratum's `branch.csv` is exact.
- **The conditional location is unchanged from reference-289.** P+C3 after the base search, mixture median: held out −35.20 (ref −35.20); `+alive` −35.22 (−35.22); R1200 inflated −35.19 (−35.19); R600 raw −35.63 (−35.57).
- **The search share under H is unchanged.** Retained: held out 0.702 (0.709); `+alive` 0.633 (0.634); R600 raw 0.353 (0.346); R600 inflated 0.394 (0.385); R1200 inflated 0.540 (0.546).
- **ln S falls**, because (b)'s flight posterior is narrower and lies further south (flight 90 % HDR 610,655 against 730,427 km²; mean shift 78 against 62 NM).
  - Held out: 0.77 (ref 1.30); still no tension, p 0.74.
  - `+alive`: 0.34 (0.84).
  - R600 raw −0.84 (−0.34); R600 inflated −1.26 (−0.64); R600 start-up offset −0.93 (new). p is 0.19-0.24 for all three.
  - The routes stratum is negative even when the 00:19 data are held out (−0.94 to −0.33), but it carries P(family) 0.01.
- **Not estimable:** `both/no-offset` and `both/startup-offset`, which are parent-limited.
- **Deviations:** the search column was built at `ed85311` rather than the reference's `abc3062`, because the seabed-search code changed in between. Unconditional `+alive` retained is 0.684, against searched areas' 0.688. The mixture step and its figures come from stand-in scripts, committed beside the results. No H01W table was produced.
- **Pléiades: please review, and re-run if you disagree.**

- Modular Architecture (stand-in for Pléiades / COSMO-SkyMed)

## 2026-10-10 ~16:00 UTC — Pléiades: stand-in re-run on core (b) reviewed (agree); close-ups for every headline option; plain-language chart labels

`results/pleiades/next-run-b-closeups/` (README, 5 close-ups as png and pdf, `closeup-stats-by-option.csv`). Labels: core (b) with the request-17 sampler fix in, split-half NOT converged; two-tank bookkeeping only; internal-v1 fuel (its one-engine flow is 2x its tables); stand-in runs, now reviewed; PROVISIONAL-OVERNIGHT.
- **Review: agree.** The close-ups reproduce the stand-in's mixture numbers exactly. Its mixture method is correct: the search re-weights the strata by their own evidence. It is now adopted as module code (`prepare/option_closeups.py`), and `rerun_next.py --pfamily` handles strata and always draws the close-ups.
- **Held out, all search layers, Pléiades + COSMO F1–F4:** 90 % area 61,969 km², mean 35.22 S 91.40 E, 88 % outside past searches, 5 % in the north-west band. Close to reference-289.
- **With R600 scored:** the mass moves south-east (mean about 35.7 S 92.2 E), and the searches leave only 0.29-0.40 of it under H.
- **For architecture, a question:** every mixture (end of flight, searched areas, Pléiades) holds P(family) fixed under every 00:19 option, so the 00:19 data never re-weight the families. Should options that score a 00:19 burst use P(family | 00:19 data) ∝ P(family) × Z_family(option)? I keep the shared convention until you rule; it is declared in every footnote.
- Charts now say what was run in words: "00:19 data held out; airborne at 00:19:37" rather than `none+alive`, and "Pléiades + COSMO F1–F3, one debris field" rather than P+C3 (Pete's request).

— Pléiades

## 2026-10-10 ~16:30 UTC - architecture → ALL MODULES: RULING - the standard 00:19 option set and its names (Pete)

From now on every module reports **the same core set** of 00:19 options, in this order, under these
**plain names**. Use the names on every chart, table and note. Internal arm codes may appear only in a
footnote or in code.

| # | Name to use | What it scores | Internal arm today |
|---|---|---|---|
| 1 | **00:19 Held Out** | none of the 00:19 BTO/BFO values | `none` |
| 2 | **00:19 R600 BTO Only** | R600 BTO (18,400 µs) | `r600-bto` |
| 3 | **00:19 R600 BTO + Raw BFO** | R600 BTO + R600 BFO (182 Hz) at face value | `r600_no-offset` |
| 4 | **00:19 Holland H1** | both bursts, Holland's start-up offset, fuel-exhaustion log-on | `both_startup-offset` × fuel-exhaustion |
| 5 | **00:19 Holland H2** | both bursts at face value (R600 BTO + R600 BFO + R1200 BFO, no R1200 BTO), log-on not from fuel exhaustion | `both_no-offset` × other |

1. **Pete's conditional option.** "R600 BTO + Raw BFO, then R1200 Raw BFO (no BTO)" is the same data
   treatment as Holland H2, as end of flight has mapped it. So it is not a separate option, **unless** Holland
   added a bias term or otherwise adjusted the raw observations in H2.
   - **End of flight:** confirm this against Holland arXiv:1702.02432, citing the page. Post the answer.
   - If Holland did adjust them, add option 6, **"00:19 R600 BTO + Raw BFO + R1200 Raw BFO"**, to the core set.
2. **Log-on cause.**
   - Options 1-3 use the log-on cause with no lag term (`other`).
   - The fuel-exhaustion-lag versions of options 1-3 are **optional, on request**.
   - H1 and H2 carry their own causes, as defined above.
3. **Existence constraints.**
   - Every core option applies the facts that the aircraft was transmitting at 00:19:37 and did not answer at
     01:15:56 (end of flight's `+alive`). These are observations of the log-on events, not of the BTO/BFO
     values.
   - The unconstrained version is optional, on request.
4. **Optional, on request only (Pete):**
   - **"00:19 Inflated BFO Noise"** (all `inflated` arms);
   - **"00:19 Both BTOs"** (`both-bto`);
   - the R1200-only arms;
   - the fuel-exhaustion-lag variants of options 1-3;
   - unconstrained (not `+alive`).

   These are no longer reported by default.
5. **Holland H1 and H2 must become estimable. They are not to be reported as "not estimable" indefinitely.**
   - The diagnosis is already agreed: settling `results/settling-h1h2-estimability.md`, end of flight
     ~15:24, searched areas.
   - Both bursts need a ~0.6 g push-over between 00:19:29 and 00:19:37. End of flight's descent proposal
     produces one for 0.8 % of its weight (about 300 of 100,000 parents).
   - This is now **end of flight's top priority**. Its entry is below.
   - Until it lands, report options 4 and 5 as **"not yet estimable - targeted sampler in progress"**.

Results already published keep their old labels. Re-label at your next re-run.

- Modular Architecture

## 2026-10-10 ~16:15 UTC — Pléiades: close-ups on core (b) in the ruled core set (Held Out, R600 BTO Only, R600 BTO + Raw BFO)

`results/pleiades/next-run-b-core-set/` (README, three close-ups as png and pdf, stats CSV). The ruling's names are now used on every chart (`prepare/describe.py`). Labels as in my ~16:00 entry. Holland H1/H2 are reported as "not yet estimable: targeted sampler in progress".
- **Pléiades + COSMO F1–F4, after Phase 2 + Bluefin-21 + OI 2018 + 2025-26:**
  - Held Out: 90 % area 71,951 km², mean 35.25 S 91.41 E, search leaves 0.557 under H.
  - R600 BTO Only: 53,544 km², 35.78 S 92.20 E, leaves 0.341.
  - R600 BTO + Raw BFO: 47,591 km², 35.73 S 92.09 E, leaves 0.304.
  - **The south-east shift with R600 comes mainly from its BTO.**
- **Question for architecture on ruling item 3.** The ruling describes the constraint as "transmitting at 00:19:37 **and** did not answer at 01:15:56", but names it `+alive`. In end of flight's code `+alive` covers 00:19:37 only; 01:15:56 is `+silent`. I have used `+alive` as named. Which is meant? If `+silent`, I will re-run.

— Pléiades

## 2026-10-10 ~17:30 UTC - architecture → end of flight (cc all): Pete on Holland H1/H2. Investigate, do not force. Supersedes item 1 of my ~16:30 entry

Pete does **not** want the push-over forced into the simulation. He wants to know:
1. Whether the low share (about 0.8 % of proposal weight reaching Δv < −8,000 ft/min) is physical evidence or an
   artefact of how our descent model is set up.
2. How plausible such a trajectory is, given:
   - the aircraft's performance;
   - the trajectories that fit the data at 00:11;
   - what is known about the operating modes at the first and second flame-outs;
   - the kinematically feasible set under no control, and under human control.
3. How the R600-then-R1200 pair serves as evidence, compared with a large sample of the possibilities.
4. Other explanations: for example, the second burst coinciding with ocean impact or rapid deceleration,
   break-up, or attitude, antenna or oscillator effects.

**My correction.** I wrote that "the sampler has to aim at it". To be precise:
- An exactly weighted importance sampler leaves the prior, and the answer in expectation, unchanged. It only
  makes the estimate precise.
- **Whether our prior covers the feasible kinematics is a separate modelling question.** That question
  comes first.

**Now:**
- An independent read-only study (architecture sub-agent) is answering 1-4 from the existing (b) impacts, which
  carry the burst-state latents, together with your model code and the literature. Report:
  `results/burst-0019-plausibility-architecture.md`.
- **End of flight: do not build the targeted proposal yet.** Keep the two tanks, the impact-time shares and the
  option-name work going. Any change to the descent prior or proposal waits for the study and Pete.
- Pete is discussing the simulation's intent with you directly; the study does not pre-empt that.

- Modular Architecture

## 2026-10-10 ~17:40 UTC - debris drift: PRODUCTION COMPLETE (both ocean models); GlobCurrent arm F1-labelled

- 367/367 nodes scored at 50 km on GLORYS12 and on GlobCurrent; split-half noise 1.42 / 0.68 ln units. Note
  `results/debris-drift-production-complete.md`; node table `results/debris-drift-two-model-nodes.csv`.
- **Use:** the GLORYS12 surface is complete and unaffected by audit F1. The GlobCurrent surface carries
  "GlobCurrent windage not product-relative (audit F1)": do not compose the pair at equal weight yet. A
  product-relative GlobCurrent arm follows only if the F1 smoke passes and Pete agrees.
- F1 smoke (go from Pete for the smoke only) takes the lock now: two arms, ~2 h each, done ~21:30 UTC.

- Ocean Drift Module

## 2026-10-10 ~19:10 UTC - architecture → ALL MODULES: RULING (Pete) - language on charts and reports; and two answers

### A. Charts and reports (Pete). Applies to everything produced from now on.

1. **Titles, headings, axis labels and legends:** no project jargon and no cryptic abbreviations.
   - Describe what is unique to our work in **ASD-STE100** (Simplified Technical English). Examples: "Impact
     positions when the 00:19 R600 BTO is used", not "r600-bto+alive, core (b)".
   - **Use normally accepted statistical and scientific terms as they are:** posterior, log-likelihood, Bayes
     factor, split-half, standard deviation, 2σ, Monte Carlo noise, and so on. Do not paraphrase them.
   - Internal codes (arm names, stratum codes, commit ids) go only in the technical footnote or in code.
2. **Footnotes come in two short versions, one under the other:**
   - **(i) STE100:** what the chart shows, from which run, and the main assumptions, in plain words.
   - **(ii) Technical:** standard statistical and scientific language with the identifiers: run, build, seeds,
     particles, 00:19 option, log-on cause, ocean model, labels such as "not converged".
   - **Both together take no more than the bottom 25 % of the image.** Keep to the essentials.
3. The standard 00:19 option names still apply (ruling ~16:30 UTC).

### B. The facts after 00:19 in the core options (hydroacoustics' question, item 3)

My ruling intended **(b)**: aircraft transmitting at 00:19:37, **and** not powered at 01:15:56. These are the two
facts that were directly observed.
- **End of flight:** please expose (b) as its own variant.
- Until then, modules use **(a)** (`+alive`) and say so.
- **(c)** `+silent` adds the "no second APU log-on" factor under `other`. That absence is also an observation, but
  its likelihood depends on end of flight's model of when a further log-on would occur.
  - It removes 44-90 % of the `other` weight, so it is a strong, model-dependent term.
  - Show (c) **beside** (b) as a declared variant.
  - It becomes default only after end of flight documents that model and its sources, and Pete agrees.

### C. Should the 00:19 data re-weight the strata? (Pléiades' question, also hydroacoustics')

**Yes. That is Bayes' rule.** For each 00:19 option:

    P(family | all data, option) ∝ P0(family) × Z_core(family) × Ẑ_00:19(family, option)

where Ẑ_00:19 is end of flight's per-family evidence factor for that option. Holding core's P(family) fixed across
options would ignore part of the data. Under "00:19 Held Out" the factor is 1, so nothing changes there.
- **End of flight:** publish Ẑ_00:19 per family and per option, with its Monte Carlo error. Modules mix strata with
  these weights.
- **While core is unconverged:** show the fixed-weight mixture beside the re-weighted one, both labelled.
- Not for Holland H1 or H2 until they are estimable.

- Modular Architecture

## 2026-10-10 ~19:25 UTC - architecture → ALL MODULES: RULING (Pete) - "00:19 Both BTOs (Davey)" for selective use only

- **"00:19 R600 BTO Only" stays in the core set.**
  - It is Inmarsat's recommended treatment: the R600 Log-on Request with its fixed 4,600 µs offset, found from
    the terminal's own history (Ashton et al. 2015, §3.3, p. 7, and p. 16).
  - Inmarsat says the later log-on-sequence BTOs "should be ignored" (p. 7).
- **"00:19 Both BTOs (Davey)"** is the R600 BTO (σ 63 µs) plus the anomalous R1200 BTO (σ 43 µs), corrected by
  −4 × 7,820 µs, with no BFOs. That is Davey et al. 2016, Table 10.1, p. 88. Use it **only** for:
  - comparisons with Davey;
  - the reproduction section.

  Elsewhere it is optional, on request.
- **When it is shown, the technical footnote states:**
  - the 7,820 µs correction is empirical, from logs not published (Davey pp. 26-27), and its origin is not
    fully determined;
  - 7,812.5 µs would shift the corrected value by 30 µs (about 0.7σ);
  - under these σ values the R1200 BTO carries more weight than the R600 BTO;
  - the two residuals have opposite signs (Davey p. 93).
- Internal arm: `both-bto` (footnote only).

- Modular Architecture

## 2026-10-10 ~19:10 UTC — Pléiades: own re-run on core (b) (core options, standard close-ups); drift audit F1 is small for Pléiades

- **Re-run by this module on core (b):** 00:19 Held Out, R600 BTO Only, R600 BTO + Raw BFO. All use transmitting at 00:19:37 and log-on not from fuel exhaustion. Search columns are rebuilt, because the stand-in workspace is gone. The numbers reproduce the stand-in-based mixture exactly. Results: `results/pleiades/next-run-b-core/` (`closeups/` holds colour and seabed for each option; `closeup-stats.csv`). Labels as before.
  - Pléiades + all four COSMO contacts, after every search: Held Out 71,951 km², mean 35.25 S 91.41 E, leaves 0.557; R600 BTO Only 53,544 km², 35.78 S 92.20 E, leaves 0.341; R600 BTO + Raw BFO 47,591 km², 35.73 S 92.09 E, leaves 0.304.
- **Drift audit F1 for Pléiades:** lowering GlobCurrent windage by 0.6-0.75 % changes the two-model 90 % area by −1.4 to −2.0 % and the mean by under 1 km (`results/pleiades/windage-relative/`). The as-run configuration stays the reference; the product-relative case is a declared sensitivity until drift's smoke test and Pete settle one convention for both modules.

— Pléiades


## 2026-10-10 13:53 -0600 — Architecture → all modules: standing rule on side questions

Pete, 10 Oct 2026: when he asks a side question, answer it and then go back at once to the work you were doing. If that work is complete, start the next item in your backlog. Do not end your turn after a side answer while you have work in progress or a backlog. End your turn only when the backlog is empty or every item is blocked on something you cannot do yourself. Before you end it, write here which items are blocked and on what. An approved run whose gates you can execute is not blocked: start it.

This rule is also in your profile, from your next turn.

## 2026-10-10 14:05 -0600 — architecture → searched areas: stand-in running now (do not duplicate)

Your next items (ρ sweep, equation (11.2) curve on (b), field-coverage check against settling's (b) wreckage samples) have been idle about 8 h, so an architecture stand-in is running them now with your scripts, under the heavy lock, with a peak-RAM cap of 10 GB. Output: results/searched-areas-next-run-b-rho-eq11-2-coverage-standin.md. Please review it when it lands. If settling's '-wider' samples arrive, re-run the coverage check on them yourself.

## 2026-10-10 ~20:15 UTC - end of flight: the three diagnostic smokes are in (SMOKE, one seed, core (b) unconverged)

Note: `results/eof-diagnostic-smokes-oct10/README.md`. No default changed. Option names follow the core set, with `+alive`.

1. **Trim referenced to the state at loss** (new switch `envelope.trim_reference_at_loss`, default off and byte-identical).
   - The prior push-over tail P(Δv ≤ −10,450 ft/min) falls **0.274 % → 0.222 % (−19 %)**.
   - 00:19 Holland H2 effective parents 8.3 → 3.0, and H1 13.2 → 3.4. These counts are too small to read further.
   - Every other option is unchanged.
   - Ruling item 3 is ready for the next re-sweep.
2. **Within-parent saturation: within-parent sampling IS the binding limit.**
   - With 1,024 descents on the 32-descent top parents, their ln Z *falls* (H2 −1.29, H1 −2.05; the winner's curse).
   - A random 2,000 of the other parents at 1,024 descents shows that **~83 % of the H1/H2 evidence lies in parents that score nothing at
     32 descents**.
   - Even at 1,024 descents, only ~10 (H2) / ~2 (H1) of 2,000 random parents carry it.
   - The total ln Z agrees between 32 and 1,024 descents (H2 −23.97 against −23.55; H1 −31.25 against −31.52). The posterior is what cannot
     be estimated.
   - **Implication:** brute force needs at least 100 M descents per seed. The efficient route is an exact within-parent sampler on the
     burst-time regime (study B2/B3) after core request 9.
   - **That is a sampling change for Pete to approve; not built.**
3. **Boeing 8-s window occupancy.** The estimator reproduces the study's Table 6 exactly (Boeing H2 0.12 %, H1 1.61 %).
   - **Point mass (current base): 0 H2 windows in all 114 fixture traces.** H1 windows appear only in the divergent spiral (3.4 %).
   - **6-DOF fit (unconverged): 0 H2 windows in all ten cases** (Boeing 6). It misses the dives in cases 4, 5 and 10, and damps the glide
     phugoids (peak g 0.05 against 0.31-0.34). **The ruling item 1 gate is not passed.** The case-by-case table is in the note. Next: diagnose
     the shared-stage stall; the refit under the heavy lock will be announced first.

**For Settling, Searched Areas, Hydroacoustics and Pléiades:**
- 00:19 Holland H1 / H2 stay **"not yet estimable - targeted sampler in progress"**.
- The cause is now measured: within-parent sampling, not the hand-off.
- Nothing you hold changes.

**Next, in order:**
- the impact-time-shares files for next-run (running), with the late-tail attribution;
- the `unpowered` constraint variant (b) and the 00:19 evidence factor per stratum;
- then the two tanks.

- End of flight

## 2026-10-10 ~20:40 UTC - end of flight: impact-time shares on next-run (with `unpowered`), late-tail attribution, and the 00:19 evidence factor per family

Both products are on the exchange, under `end-of-flight/next-run/summary/`. Notes are in `results/eof-impact-time-next-run-oct10/` and
`results/eof-family-evidence-oct10/`.

Labels: core (b) split-half NOT converged; two-tank bookkeeping only; idle floor ON; dive class (b) PROVISIONAL.

1. **Impact-time shares** (`summary/impact-time/<stratum>-impact-time-shares.json`, `<stratum>-constraints.json`).
   - Same keys as reference-289, so **Hydroacoustics' gate can run**. The legacy `*_plain_alive_silent` keys are kept.
   - New variant **`unpowered`** = ruling B (b): airborne at 00:19:37 and not powered at 01:15:56. `silent` is shown beside it.
   - **00:19 Held Out, `other`:** 9.6-10.7 % of impacts fall before 00:19:37 and 0.06-0.30 % after 01:15:56. `unpowered` keeps 0.90, the same
     as `alive`; `silent` keeps 0.11.
2. **Late-tail attribution (for Hydroacoustics): the hand-offs, not the idle floor.**
   - The idle floor off/on on the same reference-289 hand-off gives 1.69 % against 1.72 %.
   - The (b) free-stratum seeds give **0.945 / 0.035 / 0.214 / 0.007 %**, carried by 4,913 / 243 / 1,394 / 62 parents. Reference-289 has
     1.6-2.2 % and 7,400-10,200 parents in every seed.
   - This is core (b)'s non-convergence. Treat the (b) late tail as not estimable seed to seed.
3. **00:19 evidence factor per family** (`summary/family-evidence-next-run-b.json`), with the seed-s.e. stated.
   - **00:19 R600 BTO Only:** the families agree within 0.2 nat. The re-weighted mixture median is −37.94, against −37.93 at fixed weights.
   - **00:19 R600 BTO + Raw BFO:** descent-climb is +0.48 ± 0.21 nat against free. Its weight goes 0.138 → 0.204, and the median moves
     −37.42 → −37.46.
   - **00:19 Held Out:** factor 1 (P(alive) = 0.90 everywhere).
   - **H1/H2 are not re-weighted** (not yet estimable).
   - **For Pléiades, Hydroacoustics, Searched Areas and Settling:** mix by `p_family_reweighted` per option, and show the fixed-weight mixture
     beside it (ruling C).

**Core request 11 (new, in `hypothesis.toml`), for core:**
- (a) `FlightState` gains `fuel_left_kg`, `fuel_right_kg` and `first_flameout_unix_s`;
- (b) `FuelFlow` gains `fuel_flow_inop_kg_h_at` (live-engine flow from `grid_inop` × `inop_flow_scale`).

Without these, my module cannot know at takeover that the right engine is already out. Meanwhile, with core's s6/s7/s8 in the chain, **the
core flies the one-engine phase up to the takeover**, and I continue right-dry rows twin-engine on the left pool (disclosed stub).

**For the fuel session:** internal-v1.1 is not reachable from this workspace, and it cannot be rebuilt here: the MH371 ACARS workbook is
absent. Please place it on the exchange (e.g. `mh370-exchange/fuel-model/internal-v1.1.json`). Until then I use **v1 + `inop_flow_scale =
0.5`**, which your ~07:00 entry states is exactly equivalent. I will never combine v1.1 with 0.5.

- End of flight

## 2026-10-10 ~20:45 UTC - end of flight: run C compact impact format, column list and size, for consumers to check BEFORE I write

Architecture ~14:30 -0600 (Pete): compact is required.
- **Writing:** each seed is written full in my workspace, converted, verified, and only the compact file goes to the exchange. The full file is
  then removed from my own workspace. Peak extra disk is about 2.7 GB, one seed at a time.
- **Layout:** `end-of-flight/next-run-c/<stratum>/seed-<k>/{impacts32.npy, parents32.npy, run.json, COLUMNS.txt, SHA256SUMS}`, plus a README.

**Encoding.**
- **float32 throughout.**
- **Times are seconds after 2014-03-08 00:00:00 UTC** (`T0 = 1394236800`), because float32 cannot hold unix time: 1.39e9 s would be resolved
  only to 128 s. At these offsets the resolution is ≤ 1 ms.
- **Integers are exact** (parent < 2^24).
- **`weight` is the impact-row prior weight with the within-parent correction already applied**, as today. `log_q_correction` is therefore
  dropped.

**Parent-level fields go to `parents32.npy`** (one row per hand-off parent: `parent`, hand-off `weight`, `mode`, `alternative`). They are not
repeated per descent.

**`impacts32.npy`: 53 core columns.**
1. `parent`, `family`, `weight`;
2. `t_impact_s`, `t_takeover_s`, `t_realised_flameout_s`, `t_onset_s`;
3. `latitude_deg`, `longitude_deg`, `arc_distance_nm`;
4. `velocity_east_mps`, `velocity_north_mps`, `velocity_up_mps`, `flight_path_angle_deg`, `mass_kg`. Kinetic energy is dropped: it is
   ½ m |v|² from these, and the vertical part is ½ m v_up²;
5. `takeover_latitude_deg`, `takeover_longitude_deg`, `takeover_altitude_ft`;
6. `bto_residual_us:m0019a`, `bto_residual_us:m0019b`, `bfo_innovation_hz:m0019a`, `bfo_innovation_hz:m0019b`. The BTO-only options are
   derived from these;
7. `loglik:r600/no-offset`, `loglik:both/no-offset`, `loglik:both/startup-offset` (the core set). `loglik:none` is identically 0, so it is
   dropped;
8. `latent:onset_mechanism`, `latent:control_realised`, `latent:profile_shape`, `latent:engines_thrusting_at_onset`,
   `latent:spiral_divergent`, `latent:free_dynamics_started_s`, `latent:max_descent_rate_fpm`, `latent:time_descending_s`, `latent:timed_out`;
9. `latent:last_burst_latitude_deg`, `latent:last_burst_longitude_deg` (Pléiades §11);
10. `latent:state_m0019a_altitude_ft`, `latent:state_m0019a_vertical_speed_fpm`, `latent:state_m0019b_altitude_ft`,
    `latent:state_m0019b_vertical_speed_fpm` (the H1/H2 diagnostics);
11. `latent:impact_heading_deg`, `latent:impact_bank_deg`, `latent:impact_energy_transferred_j`, `latent:energy_transfer_t05_s`,
    `latent:energy_transfer_t95_s`, `latent:energy_transfer_tau90_s`, `latent:energy_transfer_peak_rate_w`, `latent:energy_transfer_n_pulses`,
    `latent:impact_tau_method`;
12. `latent:breakup_p_intact`, `latent:breakup_p_broken`, `latent:breakup_p_fragmented`, `latent:debris_class`.

**Optional: 6 more columns, the on-request 00:19 arms.**
- `loglik:r600/inflated`, `loglik:r600/startup-offset`, `loglik:r1200/inflated`, `loglik:r1200/no-offset`, `loglik:r1200/startup-offset`,
  `loglik:both/inflated`.
- **Recommended: keep them.** They cannot be recomputed without re-running, and they cost about 0.1 GB per stratum-seed set.

**Dropped (45 columns; the exact list is in `COLUMNS.txt` and in the README).**
- The fuel and onset bookkeeping latents (`fuel_*`, `mechanism_*`, `onset_prediction_*`, `powered_after_core_exhaustion_s`, the `*_assumed`
  flags).
- The aero draws (`ld_max_clean`, `windmilling_per_engine`, `rat_increment`).
- `weather_clamped`, `max_mach`, `max_altitude_ft`, `time_extrapolated_s`, `surface_pressure_altitude_ft`, `spiral_doubling_s`,
  `control_requested`, `recovery_*`, `family_prior`, `impact_vertical_speed_mps` (it duplicates `velocity_up_mps`), kinetic energy (both columns), `log_q_correction` and `loglik:none`.
- The takeover ground velocity.
- `state_m2315_*` and `state_m0011_*` (NaN, or the takeover state, at a 00:11 hand-off).
- The m0019a/m0019b burst latitude and longitude: m0019b equals `last_burst_*`, and m0019a is within metres of it.

**I report these per seed in `run.json` as summary statistics** (counts, shares and quantiles), so nothing silent is lost.

**Size**, assuming run C = 4 strata × 8 seeds × 100,000 parents × 32 descents:

| set | per seed | total |
|---|---|---|
| 53 core columns | 0.68 GB | 21.7 GB |
| with the 6 optional columns (59) | 0.76 GB | **24.2 GB** |
| old format, for comparison | 2.7 GB | about 87 GB |

At N = 4 children (16 descents) these sizes halve; that is the lever if 24.2 GB is too much. The 5 GB disk floor holds either way: the volume has about 83 GiB free.

**Tested** on `next-run/next-free/seed-1` (3.2 M rows):
- Conversion takes 21 s and gives 0.755 GB with the optional columns.
- The worst time error is 0.24 ms; the worst relative error elsewhere is 6e-8.
- `loglik:none` is proved identically 0 at write time, and the reader restores it.
- **`option_posteriors` gives the same answer on the compact file as on the full one:** across all 96 option × cause × constraint
  combinations, median latitude, ESS and mean displacement agree to ≤ 5e-6 (relative).
- `displacement_hist.option_posteriors` now reads either format, so code that imports it (Searched Areas, Hydroacoustics) needs no change.

**Consumers (Settling, Searched Areas, Pléiades, Hydroacoustics):** please flag any column you read that is dropped above. I will also ship a
reader, `smoke/compact_impacts.py`, which returns the same names as today; the time columns come back as unix seconds.

- End of flight
