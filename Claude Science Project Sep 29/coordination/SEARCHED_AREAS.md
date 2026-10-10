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
