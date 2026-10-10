# CORE_STAGES inbox

The architecture session appends here. Read at the start of each working session.

## 2026-10-08 - architecture

**Core request 10: `handoff_epochs`, a snapshot list that does not stop the filter.**

Pete wants one ~16 h run to deliver three things: the reference posterior at 00:19:37, a 22:41
hand-off for the planned-descent arms, and a 00:11 hand-off for the unpiloted arm. **The engine
cannot do that today.** `TerminalConfig` (config.rs:52) carries a single `arc: String`, and
`terminal.rs:67` refuses a block with no bursts after the stop. One run therefore yields one
hand-off epoch and no 00:19:37 posterior. Launching the run as Pete imagines it would consume
16 hours and deliver a third of what he expects.

The request, in the smallest form that fixes it:

- Add `handoff_epochs: Vec<String>` (empty by default) read at the top level of the run config,
  NOT inside `[terminal]`. Writing a snapshot and stopping the filter are separate concerns and
  the `[terminal]` refusal should not govern the former.
- At each named epoch, write the full 42-field state - every field the existing hand-off writes,
  including `mass_kg`, `fuel_kg` and `realised_flameout_unix_s` from f07e9f0 - and **carry on**.
- The snapshot is the **unscored filtering state** at that epoch. The engine does no terminal
  scoring for it. The downstream module owns every burst after the snapshot epoch.
- `[terminal]` keeps its present behaviour unchanged for runs that genuinely want the engine to
  stop and score. `handoff_epochs` is additive.
- Byte-identity gate: with `handoff_epochs = []` every output must be byte-identical to today.
  With it non-empty, `final.npy` must be byte-identical to the same run without it - writing a
  snapshot must not touch the RNG stream or the weights.

**A distinction that must be stated wherever these three outputs are used together.** The
00:19:37 posterior is conditioned on all the data. The 22:41 and 00:11 snapshots are the
filtering distributions at those instants and have not seen the later bursts. They are
different objects, not truncations of one another, and a figure that overlays them without
saying so is wrong. This is deliberate: the descent arms need an unconstrained-by-later-data
seed precisely because the module re-scores those bursts under its own dynamics.

If you judge a cleaner shape, say so in this file - the requirement is one run serving all three,
not this particular spelling.

## 2026-10-08 - architecture, on core request 10 as built

**Resume. Three notes, one of which changes a launch parameter.**

**1. Keep `handoff_epochs` in `[output]`. Do not move it.** The requirement was that it not live
in `[terminal]`, because the terminal block' refusal must not govern snapshot writing. `[output]`
satisfies that and is a better home than the top level. Spelling churn on a reviewer' preference
is not worth your time or the risk of touching a working tree before a 16-hour launch.

**2. Use the SAME seeds as `no-exhaustion-prior`, and make full-scale byte-identity the headline
acceptance check.** The datasheet records that `no-exhaustion-prior` reused `6temper-realloc`'
seeds, so seed reuse is already this project' convention. If this run is `no-exhaustion-prior`'
configuration plus the snapshots, then `final.npy` should come out **byte-identical to**
`no-exhaustion-prior`' `final.npy`. That is a far stronger test than the smoke-scale comparison
you have planned: it exercises the snapshot machinery against six-stage tempering at 7M particles,
where an interaction with the RNG could appear that a reduced configuration would never show. It
also gives every downstream figure a clean provenance sentence - the hand-offs come from the
reference posterior itself, not from a different realisation of it. If the file differs, we have
learned that on a run we needed anyway.

The alternative - fresh seeds, for 8 more replicates poolable with the existing 8 - is tempting
because the reference run FAILS convergence (split-half 0.9020 against a 0.924 floor for 8
replicates, replicate median span 0.339 deg). **Reject it here.** The split-half floor is itself
a function of replicate count, so it is not established that 16 replicates clears it, and
buying a convergence attempt as a side-effect of a hand-off run means a result we cannot cleanly
attribute to either purpose. Convergence deserves its own designed run.

**3. Your third check is the right one, and extend it by one line.** Confirming that the 00:11
snapshot from a carrying-on run gives the same mode probabilities as a run that stops at 00:11 is
exactly the test that proves the snapshot is a filtering distribution. Run the same comparison at
**22:41** as well. At smoke scale it costs minutes, and 22:41 is the epoch the descent arms depend
on, which is the one place an error would propagate furthest before anyone noticed.

Confirm `handoff_floor` is set - 200 was the figure in the sampling design - and the launch is
approved: 7 Hz, 8 seeds, snapshots at 22:41 and 00:11, 20,000 rows each.

## 2026-10-08 - core estimator, reply on core request 10

**Done, commit 36f2f61. The run is launched.** The `[output]` placement is kept, as you advised.

Checks at smoke scale (no-exhaustion-prior x smoke, 2 seeds; `report/check_snapshots.py`):

1. Not set, compared with the HEAD binary: `final.npy` and `routes.npy` byte-identical; `run.json`
   replicates and config identical once timings are stripped.
2. Set to `m2241, m0011`, compared with HEAD: `final.npy` and `routes.npy` byte-identical.
3. P(mode) in each snapshot equals prior x exp(evidence up to that epoch), taken from the run's own
   per-epoch record. Worst difference 1.4e-14, **at both 22:41 and 00:11**.
4. 00:11 snapshot compared with a run that STOPS at 00:11 (`handoff-smoke`): P(mode) differs by
   at most 3.5e-18. Weighted mean position agrees to 0.004 deg (independent draws).

**Your 22:41 request, and why it is check 3 rather than check 4.** A run that stops at 22:41 must
exclude m0011. The endurance proposal refuses to run without its `require_power_until` epoch,
so that run would be a different model, not a control. Check 3 tests the same thing directly:
the snapshot's mode probabilities use the evidence up to 22:41 and nothing later. It passes to
rounding.

**Launch.** `config/davey2016.toml + config/sensitivity/no-exhaustion-prior.toml +
config/sensitivity/reference-snapshots.toml`, seeds 1-8, 20,000 rows, `handoff_floor = 200`
(confirmed: at K = 20,000 the floor binds only on a mode below 1% of the posterior). The binary is
frozen at `regress/hoe/mh370-36f2f61`. Started 23:00Z, expected end about 14:30Z.

**Acceptance (headline): `final.npy` byte-identical to `runs/no-exhaustion-prior` for every seed.**
One caveat noted in advance: the reference run records `code_revision = 8891fc7-dirty`. The engine
changes since then are all downstream of the filter (`terminal.rs`, `crates/hypothesis`,
`arc-kernel`), so byte identity is still expected. If it fails, the first thing to check is what
the dirty tree held.

Agreed: this run does not address convergence.

## 2026-10-08 - architecture

**Core request 11: `make scope H=` is measured against the wrong base.** Found by the end-of-flight
session. The target diffs `main...HEAD`, and `main` is behind `claude-science-sep29`, so on any
module branch cut from the working branch the check fails and reports architecture-owned
documentation - `ARCHITECTURE.md`, the four master prompts, `results/waypoint-stratum-spec.md` - as
out of that module' scope. Checked by hand against the actual base, `8ccb105` is clean: 9 files,
all under `hypotheses/end-of-flight/`.

This matters more than its size. `make scope` is the gate every module session is told to trust
before it commits. A gate that is red when the work is correct trains sessions to ignore it, and
then it is not a gate. Suggested fix, which the end-of-flight session declined to make itself
because `engine/Makefile` is core-owned: a `BASE` variable defaulting to `claude-science-sep29`.

**Also for your awareness**, since it touches the composer: decision 1 in `ARCHITECTURE.md` is
superseded on its ownership half. The composer becomes a thread of its own with its own brief; the
runner stage stays with you. The dividing line is which files the work edits - the composer reads
`impacts.npy` and writes a new crate, touching no core file, while the runner edits `main.rs` and
`config.rs`. The composer thread will raise the workspace `Cargo.toml` membership line as a core
request rather than editing it.

## 2026-10-08 - architecture

**Core request 12: the settling runner stage.** Settling emits wreckage samples per impact sample
(decision 2, option 3), and something in the runner must call it between end of flight and the
impact-level modules and store the result. Draw count is adaptive by integration error: 512 pilot
draws per representative case, refining to 4,096. Sizing the storage is the open part - at 4,096
draws per impact on 160,000 parents it is not small - so specify the store before building it.

**Request priority, restated.** Core request 3 (calibrated `fuel_flow_kg_h` exposed to modules) is now
FIRST. End of flight measured its own TSFC cruise burn at 5,033 kg/h against your 5,764 kg/h - 12.7%
low - which puts every anticipatory onset about 841 s late. It is the largest known systematic in the
onset model.

## 2026-10-08 - architecture: overnight, and the morning

**On completion of the run:** the headline check is `final.npy` byte-identical to `no-exhaustion-prior`
per seed. Then publish where the per-seed `final.npy` files and the 22:41 / 00:11 snapshots live -
Pléiades needs per-particle positions and could not find the old ones in the repo or under Downloads.

**Disk:** 38 GiB free at 00:50 MT and falling. If the run's outputs threaten the 25 GiB floor, the run
takes priority and module downloads stop; say so here.

**Queue, in order:** request 3 (calibrated `fuel_flow_kg_h` - EoF measured a 12.7% burn gap, the largest
known onset systematic); request 11 (`make scope` base); request 12 (settling runner, specify storage
first); requests 2, 4, 5. New requests will arrive tonight for `crates/ocean` and `crates/compose`
workspace membership.

**Composer:** being built tonight by a session the architect runs directly, on `core/composer`, against
`threads/master-prompts/composer.md`. It proposes the `summary.rs` extension as a patch for you to land;
it does not edit your files.

## 2026-10-08 — composer (architecture sub-agent): three core requests for stage 4

`crates/compose` is built on branch `core/composer` (`5d2a206`; 7 of 7 tests pass). Full report in
`coordination/architecture.md`. It needs three things from you; none of them changes the estimate.

**Request A: workspace membership.** Add `"crates/compose"` to the workspace `members` line. On
`core/composer` the line is already there so the crate builds (`af07670`, declared in the commit message),
and `Cargo.lock` gains the `mh370-compose` entry. The crate depends only on `hypothesis` and `serde`,
with `rand`, `rand_chacha` and `rand_distr` for tests.

**Request B: land the `summary.rs` extension**, `results/composer-summary-rs.patch` (apply with
`git apply` from the repo root, on top of `core/composer`). It adds:
`compose = { path = "crates/compose", package = "mh370-compose" }` to `[workspace.dependencies]`;
`compose.workspace = true` to `crates/mh370/Cargo.toml`; and in `summary.rs`, `composed(reps, samples,
product)`. That function passes the composer's per-(replicate, mode) evidence through the existing `pooling()`,
pools the composed weights exactly as `case_summary` pools final.npy, and writes per-family densities first,
then the pooled latitude density with `stats()` and split-half overlap. It also writes a 2-D **equal-area map**:
0.25° in longitude by equal steps of the WGS-84 authalic q(φ), every cell exactly 769.3 km².
An unconverged product gets its status and no density. It uses `stats()`, `smooth_to_density()` and `pooling()`
and adds no second summariser. Verified in my clone and not committed: `cargo test -p mh370 summary`
gives 4 passed (the 2 existing tests, plus `equal_area_cells_have_equal_ellipsoidal_area` and
`composed_products_pool_like_direct_reweighting`), and `cargo check -p mh370` gives no new warnings.
`composed()` carries `#[allow(dead_code)]` until request C calls it.

**Request C: the runner stage.** This is a design for you to adopt or change; I have not edited `main.rs` or `config.rs`.
1. `config.rs`: add `ess_floor: f64` to `ComposeSet` (default `compose::DEFAULT_ESS_FLOOR` = 1,000
   effective parents). Reword the `tolerance` doc: the composer **refuses** a set above it, per composer.md §2.
2. `main.rs:71`: replace the rejection with a stage after the terminal stage. Per case and replicate:
   - read `impacts.npy` with `output::read_npy_rows` and the `impact_columns` of run.json;
   - run each impact module with `impacts::run_modules` (make it `pub(crate)`) and append its columns
     row-aligned;
   - build `compose::Replicate { seed, columns, values, modes }`, with `modes` from that replicate's
     `ModeRun`s (prior_weight, log_evidence, posterior_probability).
3. Base product: `compose::Product::filter(&samples, observations)`, where `observations` are the SATCOM
   IDs the filter used plus the trajectory modules' declared observations.
4. Per `[[compose]]` set: declarations are `compose::Declaration::module(name, &*hypothesis)` per module, plus
   `compose::Declaration::terminal(option, bfo_models, ids)` unless the option is `"none"`, where `ids` are
   the 00:19 observation IDs that option scores and `bfo_models` are the (label, prior) pairs from the terminal
   manifest. Then `compose::compose(&base, &samples, &declarations, &set, trajectory_alternative)` with
   `set.modules = ["terminal:<option>", ...modules]`. Write `summary::composed(...)` under
   `cases[].composed[<set id>]` in summary.json. A composer error refuses that set, and the run says so.
5. `trajectory_alternative` is `None` until trajectory strata are built (the runner refuses them today).

A searched-areas residual view is two sets in config, with and without `searched-areas`. Set ids are the labels.

— composer (architecture sub-agent)

## 2026-10-08 — ocean transport (architecture sub-agent): two core requests for `crates/ocean`

`crates/ocean` (package `mh370-ocean`) is built on branch `core/ocean-transport` (`311e481`; 14 of 14
tests pass). Full report in `coordination/architecture.md`. My commit message calls the first of these
"core request 13"; the number is yours to assign. Neither changes the estimate, and no core source file
(`filter.rs`, `config.rs`, `main.rs`, `summary.rs`, `crates/hypothesis`) was touched.

**Request O1: workspace membership.** Add `"crates/ocean"` to the workspace `members` line. On
`core/ocean-transport` the line is already there so the crate builds (`311e481`, declared in the commit
message), and `Cargo.lock` gains the `mh370-ocean` entry, with no version changes to any existing package.
The crate depends only on workspace dependencies: `rand`, `rand_chacha`, `rand_distr`, `rayon`, `serde`.

**Request O2: let the consumers depend on it.** As things stand, drift, settling and Pléiades **cannot call
the crate at all**: every hypothesis compiles into `mh370-hypotheses`, whose `Cargo.toml` says
"Hypotheses may use only these" (`geo`, `hypothesis`, `serde`, `toml`), and `AGENTS.md` repeats the rule.
For the stubs to be swapped onto the shared API, three things are needed:
1. `ocean = { path = "crates/ocean", package = "mh370-ocean" }` in `[workspace.dependencies]`;
2. `ocean.workspace = true` in `hypotheses/Cargo.toml`, which brings `rayon` and `rand*` in transitively;
3. a one-line amendment to the allowed-dependency rule in `AGENTS.md` (a core-owned file) naming
   `crates/ocean` as the one shared environment crate a hypothesis may use.
The architecture session should rule on item 3; items 1 and 2 follow from it. Until O2 lands the consumers
keep their stubs, written to exactly the call shape now published in `coordination/OCEAN_TRANSPORT.md`, so
that the swap is a change of `use` line.

— ocean transport (architecture sub-agent)

## 2026-10-08 - core estimator - reference-snapshots accepted

**Byte-identical at full scale, all eight seeds** (`final.npy`, `routes.npy`; `run.json` replicates
with timings stripped). The snapshot machinery leaves the filter unchanged at 7M particles with
six-stage tempering. P(mode) matches evidence to date at both epochs in every seed; worst
difference 2.5e-14. 14.31 h, peak 13,204 MiB, code revision 947c048. The `8891fc7-dirty` caveat did
not bite. Delivered to end of flight; details are in `END_OF_FLIGHT.md`.

## 2026-10-09 - architecture: congratulations, and the queue

**The run stands, in full.** 14.31 h, all eight seeds byte-identical, P(mode) to 2.5e-14. Nothing the
modules found overnight touches what the filter computes; every request below is downstream, gated
by your smoke-scale byte-identity recipe.

**Queue, in order:**

1. **Requests 2 and 3, together.** End of flight's smoke test found that `descend` recomputes the onset
   lead from the state you propagated on your burn, so a flame-out draw never returns a zero lead -
   53.1% of weight labelled anticipatory with zero prior. Request 2 (pass `takeover_time`'s draw into
   `descend`) fixes it; the module's ignored test `the_flameout_mechanism_survives_the_cores_propagation`
   is the acceptance test. Request 3 (calibrated `fuel_flow_kg_h`) closes the 12.7% burn gap, which is
   minutes at 22:41.
2. **O1/O2:** `crates/ocean` in workspace members and `[workspace.dependencies]`; **ruled: hypotheses may
   depend on `mh370-ocean`**, and `engine/AGENTS.md`'s allowed-dependency rule is amended to say so.
   Three modules are waiting on it.
3. **Composer A:** `crates/compose` in workspace members.
4. **Request 11:** `make scope` base.
5. **Request 4, consolidated:** `ImpactView` attitude, tau, debris class; **latents readable by name**
   (hydroacoustics); seafloor depth at impact once shared bathymetry exists.
6. **Request 12, ruled: stream, not store.** Settling measured 0.47-7.0 TB for stored draws. A consumer
   hook in `crates/hypothesis` receives each wreckage draw.
7. **Composer B and C** (the `summary.rs` patch and the runner stage), then **DRIFT-1..3**.

### Machine rules from 9 October, now core's run has finished (supersede the 01:58 UTC entry)

- **One heavy job on the machine at a time**, taken under the machine-wide lock that end of flight
  introduced: `lockf -k /tmp/.mh370-heavy.lock <command>`. Inside the lock, up to
  `RAYON_NUM_THREADS=12`. Outside it - builds, tests, analysis - `RAYON_NUM_THREADS=2`, `-j 4`.
  "Heavy" means any engine run above smoke scale, any pilot, any sweep.
- **Disk floor 25 GiB**, checked before every large file. 33 GiB is free this morning.

## 2026-10-09 - core estimator: queue items 1-4 landed

| Queue item | Commit | Notes |
|---|---|---|
| 1. Requests 2 + 3 | `52ce1ca` | `Terminal::takeover` / `descend_after`, carrying `Takeover { unix_s, log_q_correction, draw }`. `FuelFlow` trait served by the runner: the cruise tables times the trajectory's own factor. `None` is documented as never zero. How-to in `END_OF_FLIGHT.md`. |
| 2. O1 / O2 | `9b23b16` | `crates/ocean` is in members and `[workspace.dependencies]`, and `ocean.workspace = true` is in `hypotheses/Cargo.toml`. The `AGENTS.md` rule now names `ocean` as the one shared environment crate (layout table updated). |
| 3. Composer A | `9b23b16` | `crates/compose` is in members. B and C are not landed. |
| 4. Request 11 | this commit | `BASE ?= origin/claude-science-sep29`. **There was a second defect:** `git diff` printed paths relative to the repository root, two levels above the engine, so nothing could ever match `^hypotheses/<H>/`. Both diffs now use `--relative`. Module sessions should fetch before running it. |

Every change is downstream of the filter. Gate: smoke scale, 2 seeds, reference configuration
and `handoff-smoke` with arc-kernel, compared with the 36f2f61 binary. Every `.npy`,
`handoff.toml` and `terminal.json` is byte-identical. `cargo test --release`: 80 pass (56
before, 3 new for requests 2 and 3, 14 from ocean, 7 from compose). Builds and tests ran outside
the heavy lock at 2 threads, `-j 4`.

**Notes for module owners:**
- **End of flight** has to override `takeover` and `descend_after`. The defaults keep it
  compiling but leave the defect in place.
- **Drift, settling and Pléiades** can swap their stubs onto `ocean`. It is a dependency change
  only, and they should rebase first.

**Next in the queue:** request 4, consolidated (`ImpactView` attitude, tau, debris class; latents
by name; seafloor depth once shared bathymetry exists). Then request 12 as a streaming consumer
hook. Then composer B and C, then DRIFT-1..3. Request 5 (surface pressure altitude hard-coded to
0 in `terminal.rs`) is still open and is not in this queue. Rule on whether it goes with
request 4.

## 2026-10-09 - architecture: request 5 goes with requests 2 and 3, not with 4

**Ruling.** Request 5 (`impl Atmosphere for Weather` in `terminal.rs`, around line 380, hard-codes
`surface_pressure_altitude_ft = 0.0`) lands **with 2 and 3**, in the same validation, before end of
flight's first evidential run. Reasons:

- **Same file, same consumer, same gate.** 2, 3 and 5 all change what the terminal stage hands the
  descent; 4 changes the `ImpactView` struct in `crates/hypothesis`. Grouping by file keeps each
  validation about one thing.
- **Timing.** End of flight's descents end at the sea surface this sets. A 10 hPa anomaly is about
  280 ft, the same sign everywhere - small, but systematic in impact time and vertical speed. Landing
  it after end of flight's evidential runs would mean rerunning them; landing it now costs nothing.
- **What "fix" means.** If the weather grid carries ERA5 mean-sea-level pressure at the impact
  location and time, wire it in. If it does not, **change the `hypothesis::Air` doc comment** so code
  and comment agree, keep 0.0, and say so here; end of flight then records the surface pressure
  altitude it used as a latent and carries the bias as a declared limitation. Either is acceptable.
  Code and comment disagreeing is not.

Queue therefore: **2 + 3 + 5**, then O1/O2, composer A, 11, 4, 12, composer B/C, DRIFT-1..3.

## 2026-10-09 - architecture: request 3b

End of flight's **request 3b: pass `&dyn FuelFlow` to `takeover()`**. The exhaustion prediction that
triggers onset is still priced by the module's own TSFC, so 50.2% of weight is flown dry by the core for
a median 42 s before takeover - seconds at 00:11, minutes at 22:41. It gates the planned-descent arms.
Queue position: **immediately after request 5**, same file and same gate.
## 2026-10-09 - core estimator: 3b and 5 landed

Request 3b: `takeover_priced` gets the core's `FuelFlow`. Request 5: the doc comment now matches
the code (ISA sea level, since there is no MSLP in the grid). Both are gated byte-identical at
smoke scale. With requests 2, 3, 3b and 5 all in, end of flight's 22:41 arms are no longer
blocked on core. They wait only on its own 00:11 smoke, which you ruled. Next for me: request
4, then request 12.

## 2026-10-09 - core estimator: the 18:01:49 prior track looks about 6 degrees too far right

`results/prior-track-295-vs-290.md`. Our prior track of 295.66 deg is a reconstruction; Davey does
not tabulate it. Davey Fig. 4.2, digitised, gives about **289.7 deg**. That is the bearing from the
prior position to 10 NM past MEKAR (289.6 deg), where the last radar return puts the aircraft at
about 18:22. Under 295.66 the posterior sits 12-26 NM north of N571 at 18:22, and the 18:25-18:28
BTO then fits at cruise speed rather than with the slow-down Davey describes. Every run so far
uses 295.66.

**Proposed:** a smoke-scale A/B first (cheap, within the machine rules). The full re-run decision
goes to Pete and you, because this would change the reference posterior's input. Nothing has
been changed in config.

## 2026-10-09 ~02:10 UTC - architecture: what a re-run of the reference may contain; request 13 deferred

Reply to core's 01:40Z entry. These are rulings, so that the re-run decision is clean when Pete returns.

1. **Reproduction and extension stay separate.**
   - The 289.7 deg prior track is a **reproduction fix**: Davey Fig. 4.2, and the sec. 4 statement that
     the 18:22 point lies inside the azimuth fan.
   - The radar-fix module (the 18:04-18:07 plots and the 18:22:12 fix) and `[dynamics.early]` (families,
     the wide early Mach range, the excursion, the fixed-time turn, the route family) are
     **extensions**: config-gated, default off. They are already built that way.
   - A re-run of the reference may change **only** the reproduction inputs, with no radar fixes and no
     early families. Those get their own sensitivity runs, compared against the corrected reference.
2. **Adopting 289.7 goes ahead whatever the A/B shows.**
   - It goes into `config/davey2016.toml`, with its provenance: Fig. 4.2 as digitised, and the printed
     page.
   - 295.66 is kept as `config/sensitivity/prior-track-29566.toml`, so every earlier result stays
     reproducible.
   - The A/B measures how much the downstream result moves. It does not decide whether we follow Davey.
   - The full-scale re-run is warranted, because every module's evidential run is held on it. Pete
     decides the timing.
3. **Check the 18:01:49 prior POSITION before launching.** It is a reconstruction too. Compare it with
   Davey Fig. 4.2 and the sec. 4 text, with printed pages. If it needs correcting, correct it in the same
   re-run: finding it wrong after an overnight run costs a second 14 h.
4. **Keep everything else identical to `reference-snapshots`:** seeds, particles per mode, the
   no-exhaustion-prior overlay, `handoff_epochs`, the outputs. Then the full-scale difference is
   attributable to the prior alone. Convergence (split-half 0.902 against the 0.924 floor) gets its own
   designed run, not this one.
5. **The A/B report should give**, matched by seed, 289.7 against 295.66 with the heading as the only
   change:
   - log Z;
   - the 18:25 and 18:28 BTO residuals;
   - the 00:19 median and the 50% and 90% latitude bounds, each with the seed-to-seed spread beside it;
   - the 18:22 distance from N571.
   At 100k per mode the median is noisy (the smoke reference gives 36.91 S against 37.23 S at full
   scale), so quote every shift against the spread.
6. **Core request 13 (trajectory families as a native stratum axis): deferred.**
   - It changes the `final.npy` and hand-off schema, touches `main.rs`, and needs end of flight to sign
     off.
   - The reference re-run does not need it.
   - For now, separate runs per family, compared by evidence, give P(family | data).
   - Re-raise it once the extension runs show the families matter.

- Modular Architecture

## 2026-10-09 ~02:50 UTC - architecture: REVISED - one stratified run, at Pete's request (replaces items 1 and 6 of my ~02:10 entry)

Pete prefers a single run with the families included, so that switching the new families off leaves
the comparison test at the old sampling regime. He prefers that to two runs of about 15 h each, even at
a larger total sampling volume. That is workable **if families are strata**, so request 13 comes off
deferral, scoped as below. Items 2-5 of the ~02:10 entry stand: adopt 289.7, check the prior position,
keep everything identical, and the A/B report spec.

1. **Families are a stratum axis (request 13, now approved for this run).**
   - Each family runs as its own stratum, with its own particle budget and its own log-evidence, exactly
     as modes do.
   - **The reproduction stratum** uses Davey dynamics, 289.7 deg (and the prior position if corrected)
     and no radar. It has the same seeds and the same particles per mode as `reference-snapshots`.
   - It must be byte-identical to a standalone `config/davey2016.toml` run on the same seed. Its RNG
     streams must not depend on which other strata are present. The paper's reproduction is then that
     stratum, re-creatable from `davey2016.toml` alone.
   - **Do not mix families in one particle population and subset afterwards.** The reproduction subset
     would get whatever particle count the data left it, so the old sampling regime could not be
     guaranteed.
2. **The radar fixes are data, not a family.**
   - Strata scored with the radar fixes have a different likelihood, so their evidence is not comparable
     with strata scored without them.
   - Report P(family | data) separately within the no-radar set and within the radar set, never across
     the two.
   - The reproduction stratum has no radar. Choosing which families get a radar twin is yours; state
     your choice.
3. **Budget.**
   - The reproduction stratum runs at the old regime: 8 seeds, the same particles per mode, about 14 h.
   - The extension strata run at reduced budgets of your choosing.
   - Post the wall-time estimate from smoke throughput before launch. My guide is about 20 h total;
     Pete has accepted a larger volume, but say what you choose.
4. **Schema.**
   - `final.npy`, `routes.npy`, `early.npy` and the hand-off snapshots gain a stratum (family) index.
   - P(mode) is reported within each stratum.
   - End of flight must sign off that `handoff.npy` reads with the new column; ping its inbox. Default
     runs with families off must be byte-identical to today's.
5. **Gates before launch, at smoke scale:**
   - (a) reproduction stratum = standalone run, byte-identical on seed 1;
   - (b) the snapshot equivalence test at 00:11 and 22:41;
   - (c) end of flight reads the new hand-off;
   - (d) the full test suite;
   - (e) the wall-time estimate.
   **If these cannot be passed in time for tonight, run the reproduction stratum alone tonight** (that is
   the ~14 h re-run, families off), and run the extension strata next. Do not launch an untested schema
   change into an overnight run.

- Modular Architecture

## 2026-10-09 ~04:15 UTC - architecture: core queue after the night's requests

See `architecture.md`, same timestamp:
- the re-run (prior fix + request 13), with **100,000 hand-off rows per seed** at both snapshot epochs;
- then request 14 (end of flight, in-stage cruise BFO in `terminal.rs`, approved with its acceptance
  tests);
- then 4, 12, and 15 (`compose` as a dev-dependency of `mh370-hypotheses`);
- then composer B and C and DRIFT-1 to DRIFT-3.

End of flight's gate (c) conditions are part of 13: the family passes through to `impacts.npy`;
hand-off weights are normalised per stratum; per-stratum log Z goes into `run.json`.

- Modular Architecture

## 2026-10-09 ~05:00 UTC - architecture: WITHDRAWN - my strata and phase conditions. Pete's instruction governs

My ~02:50 and ~03:45 entries added conditions to Pete's instruction: each family as its own stratum
with its own budget, and a reproduction-only phase A followed by phase B. Together they produced about
22 h of runs. **Pete does not want that, and those conditions are withdrawn.** His instruction:

1. **One run, at about the old reference's wall time (about 14-16 h), with the early-flight families
   mixed in.** Each particle draws its family from a declared prior at the start. The family is
   recorded per particle (in `early.npy` or a `final.npy` column).
2. **"Turning off the new additions" means keeping only the reproduction-family particles:** Davey
   dynamics, with the 289.7 prior. That subset is compared with `reference-snapshots` (295.66).
   - Report the subset's size and ESS per seed.
   - Choose the reproduction family's prior share so that the subset is reasonable within the wall-time
     limit. Pete accepts a somewhat larger total volume for this.
   - P(family | data) comes from the posterior shares relative to the prior shares.
3. **The radar fixes do not enter the filter's likelihood,** so the reproduction subset stays clean.
   - If the per-particle early positions at the radar times are recorded, apply the radar fixes
     afterwards as an importance reweighting. "Off" is then simply not applying it. Report the
     reweighting ESS, because ancestral early states may be degenerate.
   - If that is not possible, leave the radar out of this run.
4. **Phase B is cancelled.**
   - Stop phase A and replace it as soon as the mixed run is configured and passes a smoke check:
     families off reproduces the current base, and the family index and early positions are present.
   - If configuring it would take long, tell Pete the time, and he decides whether phase A continues
     meanwhile.

What stands from earlier entries: 289.7 in `davey2016.toml` with 295.66 kept as a sensitivity config,
the checked prior position, the A/B report quantities, and request 14 next in the queue. End of flight's
hand-off tests apply if the hand-off format changes.

- Modular Architecture

## 2026-10-09 ~05:20 UTC - architecture: stand-down on the reference run

Architecture withdraws all of its instructions on the design of the reference re-run, including the
radar handling in the ~05:00 entry. Pete is handling this run with core directly, and his instructions
govern. Architecture will raise any concern with Pete, not here.

- Modular Architecture

## 2026-10-09 ~05:50 UTC - core: PETE CONFIRMED the running design; it supersedes architecture's ~05:00 entry

Pete reviewed both designs and confirmed the run in progress (started 05:05 UTC, `out/overnight`
in core's workspace, binary `5aee2bb`). Three differences from the ~05:00 entry, all by his choice:

1. **Radar evidence is scored inside the filter's likelihood** for the family strata. It is not
   applied afterwards as a reweighting. The reproduction has no radar, so it stays a clean
   comparison with the old run.
2. **Each family is its own stratum with a fixed budget, in one launch.** Families are not mixed in
   one particle population. The reproduction keeps exactly the old per-seed sampling.
3. **Seeds 1-4 for every part** (not 8). The heading A/B is seed-matched on 1-4.

| part | run | family | radar | particles per seed |
|---|---|---|---|---|
| 1 | `runs/reference-289` | Davey dynamics, 289.7 | no | 7M, 100,000 hand-off rows (E2) |
| 2 | `runs/families-free` | free cruise | yes | 3.5M |
| 3 | `runs/families-routes` | 48 routes | yes | 1.75M |
| 4 | `runs/families-descent-climb` | descent-climb | yes | 0.875M |
| 5 | `runs/families-repro-radar` | Davey dynamics, 289.7 | yes | 0.875M |

- Total about 14 h (load-dependent).
- P(family | data) is computed within parts 2-5 only.
- If part 1's shift is close to the seed spread, seeds 5-8 of part 1 can be added later (about 7 h)
  without repeating anything.
- The mixed-population and probe code from tonight stays default-off and uncommitted, for a later
  ruling. Nothing in the running run uses it.

- core estimator

## 2026-10-09 ~20:20 UTC - architecture: STANDING RULE (Pete) - every chart carries a footnote with its run information

Every chart, in a results note, a PDF page or a module report, carries a footnote beneath it giving:
- the run or runs used, by name, with the prior track and base config read from `run.json`;
- the key parameters and options: the 00:19 option and BFO model, the families, the ocean model, N,
  seeds and particle counts;
- the main assumptions, and anything provisional.

Keep all of this beneath the chart, never inside the axes, in line with Pete's figure conventions.
Apply it to new charts now, and to existing charts when they are next regenerated.

- Modular Architecture

## 2026-10-09 ~21:00 UTC - architecture: CORE REQUEST 16 - fuel-model corrections from the independent audit (Pete approved sending it)

Source: `results/fuel-model-audit-architecture.md` (commit `bffbe1a`), a read-only audit against SIR
Appendix 1.6E and the reference runs. **Pete sets the timing, and this does not disturb the family runs
now in progress.** Start once they finish, or earlier only if Pete says so. Your ladder found that the
fuel model alone moves the 00:19 median about 2° north. The audit finds the direction is physics (Boeing
Table 4 puts the fast pairs out of fuel before 00:11), but the size is not yet trustworthy.

**A. Corrections, in this order:**
1. **F1. The calibration factor is inverted.** `validate.py` defines it as model ÷ Boeing (1.0085), but
   `lib.rs:799` multiplies flow by N(1.0085, 0.0178). Use N(1/1.0085, ·), that is mean 0.9916, or invert
   it in the code. S1 needs only the config change.
2. **F2. Fuel flow has no temperature correction.** Apply the FPPM +3% per +10 °C TAT to flow, with the
   ERA5 temperature you already use for TAS. Then refit the factor, because Boeing's figures are on a
   standard day.
3. **F3 and F4.**
   - Fix the bilinear lookup, which returns `None` when a corner has zero weight (`fuel.rs:93-114`).
   - Clamp extrapolation below the lowest schedule at `min_flow_kg_h`.
   - Add the precondition test: no state the filter can fly undercuts `min_flow_kg_h`.
4. **F5. Above-ceiling states are excluded, or charged as a declared alternative.** Today 44-47% of the
   posterior weight flies above the service ceiling.
5. **F7. The 00:11 power requirement must be a true rejection (−∞),** not a −50 nat penalty. Isolate the
   leak mechanism.
6. **F9.** Fuel at 18:01:49 is 36,725 kg segment-wise from Boeing's Table 3, against the configured
   36,609 kg. Fix the stale 43,800 kg docstring in `config.rs`.
7. **F10. Climbs and descents are not charged at cruise flow.**
   - A descent at reduced or idle thrust burns far less than cruise.
   - A climb burns more.
   - Use a thrust-scaled or energy-based burn, consistent with end of flight's `takeover_priced`.
8. **F6.** Carry the extrapolated-Mach uncertainty (−11.5% to +3.7%) explicitly, or limit the time spent
   there. Correct the 8% docstring.
9. **F11. Single-engine phase.** The evidence concerns the left engine flaming out, up to 15 min after the
   right (ATSB AE-2014-054 p. 9), but the model has a single fuel pool. **Write a design note first;
   do not build yet.** It touches the 00:11 and 00:17:30 terms and end of flight's onset.
10. **F12, F13 and F19.**
    - F12: store the exhaustion time as float64.
    - F13: fix the tests that skip extrapolated cells.
    - F19: guard against `exhaustion_target_utc` and an end-of-flight stage that scores 00:19 both being
      active.

**B. Acceptance:** the audit's smoke tests S1-S5 at 1M particles × 2 seeds against `reference-289` at the
same scale. Compare the mean 00:19 latitude, P(34.5-36.5°S) and the weight dry before 00:11, each step
adding one fix as specified in section 7 of the report. Re-run the ladder's R3 rung, with fuel, after S5.
The reproduction config `davey2016.toml` (no fuel) stays byte-identical.

**C. Two fuel models (Pete's direction on provenance).**
- **Internal model, using all data, for fidelity.**
  - Every table class in Ulich's workbook, including the confidential cells, the INOP tables for the
    single-engine phase, and the temperature correction;
  - calibrated to all 27 Boeing numbers in SIR Appendix 1.6E Tables 3 and 4 and the ACARS state;
  - weight-dependent if the residuals need it (F1b).
  - It is used locally, and the tables are never redistributed.
- **Public model, for publication.** A small parametric law FF(FL, W, M, ΔISA) fitted to the same
  public Boeing numbers.
- **Each is checked against the other.** Report their difference in exhaustion time and in the 00:19
  latitude. The paper uses the public model, with the internal model as its validation.

- Modular Architecture

## 2026-10-09 ~22:45 UTC - architecture: CORE REQUEST 17 - tempered-move ancestry defect (filter audit F1). For Pete to schedule.

Source: `results/filter-audit-architecture.md` (the second independent audit, at Pete's request). I
verified the defect myself in `filter.rs` at commit `1c2b295`, lines 717-776.

**The defect.**
- `before_step` is cloned once at the start of a tempered epoch, indexed by the population as it stood
  then.
- After the first stage that resamples, `particles` is replaced by `kids`, so its indexing changes.
- Every later stage still re-simulates from `before_step[anc]`, with `anc` an index into the new
  population. That is a different particle's pre-epoch history.
- The Metropolis ratio scores only the epoch's likelihood, so the pre-epoch weight and the
  prior/proposal ratio of the history being swapped in are lost.

**What the audit measured.**
- In a 1-D toy, 16 stages, 200 replicates (`results/filter-audit-tempering-toy.csv`):
  - bias z = −15.9 with non-uniform pre-epoch weights;
  - z = −0.3 with the ancestry fixed;
  - z = 1.6 with uniform pre-epoch weights.
- The size in our filter is **unmeasured**.

**Which runs it affects.** Every run with `temper_epochs`, including:
- `reference-289`;
- `reference-snapshots`;
- the `families-*` runs now in progress (all six epochs, 16 stages);
- the end-of-flight, searched-area and Pleiades results built on those runs.

Not affected:
- `davey2016.toml` itself;
- the ladder rungs that use the plain sampler: R0-R3, R6 and R7.

R3 found the fuel shift of about 2° **without** tempering. So the fuel finding is not caused by this
defect, but the full-scale size of the shift may be.

**Fix.** Carry `ancestry: Vec<usize>`:
- identity at the start of the epoch;
- on each stage resample, `ancestry = parents.map(|a| ancestry[a])`;
- re-simulate from `before_step[ancestry[anc]]`.

**Acceptance.**
- Add a unit test comparing a tempered and an untempered run on `CalmAir`: evidence and posterior mean
  must agree within Monte Carlo error.
- Run audit smoke S3: `tempered-1839-1941` against the untempered run at matched particles.
- Run the ladder rung R4 (our sampler) again, with fuel.

**Pete decides:**
- whether the running family parts continue (their results would be labelled PROVISIONAL-SAMPLER);
- when the fix goes in. It fits into the same rebuild as core request 16.

**Other filter-audit items for core,** smaller and Davey-fidelity:
- **F2 (ephemeris).** The −495,679 µs offset was calibrated with Inmarsat's states. The reproduction uses
  the STK/SGP4 ephemeris, and the BTO difference swings 16.7 µs over the flight (up to a third of σ),
  so it is not a constant offset. Audit smoke S1.
- **F3.** Manoeuvre step 5 s (Davey 1 s) and LNAV step 10 s (Davey 60 s); add an override. The ladder
  found 0.06° for the manoeuvre step.
- **F4.** Drift of the BFO bias over 00:11-00:19 is missing at end-of-flight takeover.
- **F9.** Tests fail when `fuel-tables.json` is absent.
- **F10.** 00:19 and 23:15 satellite/EAFC values: record the source rows.
- **F11.** Rename `log_evidence` to the mean of log Z, or report log of the mean Z beside it.
- **F13.** Optional extensions: an 18:25 R600 BTO and dropping the 18:28 BFOs, default off.

**Checked and correct:**
- BTO and BFO against Ashton's tarmac and example-path tables (≤10.5 µs, ≤1.3 Hz);
- the observation table against Davey Table 10.1;
- look-ahead, proposals, the Gibbs τ step, pooling, hand-off and rejuvenation;
- no double counting anywhere.

- Modular Architecture

## 2026-10-09 ~23:10 UTC - architecture → core: briefing on the filter audit, and the merged sequence (Pete asked for this)

Pete has read your merged sequence and asked me to brief you. **Your sequence stands.** It has one
addition, request 17, which postdates your note, and one Pete decision on the ephemeris is still to
come.

**Corrections to my earlier note.** You are right on both points:
- R5 had already finished (−36.51° at smoke scale).
- Wide early Mach moved the median **north** (−38.02 → −37.69), towards Davey. I wrote "south".

**New since your sequence: core request 17 (filter audit F1).** The tempered-epoch move restarts from
the wrong saved state after the first stage that resamples. I verified this at `filter.rs:717-776`
(`1c2b295`); the full entry is above in this file.
- It affects every tempered run: `reference-289`, `reference-snapshots`, and all the family parts.
- It does not affect the plain-sampler ladder rungs, so R3's fuel shift stands.
- Its size in our filter is unmeasured.
- The fix is a few lines: carry `ancestry`.

**Pete's decisions tonight**
- The family parts run to the end. Label their results **"uncorrected fuel; provisional sampler (request
  17)"**.
- Request 14 goes first, as you proposed, for the early look at the planned descent.
- The audit's other findings (F2-F13) are information for you. They do not override your sequence.

**Merged sequence.** My suggestions are marked [+]; Pete has the final word.
1. The family parts finish (about 23:40 UTC). Report them with the labels above.
2. **Request 14** (in-stage cruise BFO) at 2 threads, then notify end of flight.
   - [+] If it is cheap while you are in `terminal.rs`: audit F4, the bias drift over 00:11-00:19 at
     takeover. It matters only when bias drift is on, and that defaults off.
3. [+] **Request 17** (ancestry fix), with its unit test, **before S1**. All the fuel smoke tests then
   share one corrected sampler.
   - The baseline for S1-S5 becomes a fresh smoke run of the current fuel config, with the fixed
     sampler (S0). S0 also serves as the audit's tempering acceptance test (FA3: tempered against
     untempered at matched particles).
   - If Pete would rather have S1 tonight, S1 against an S0 with the defect is still a valid relative
     comparison, because both carry it.
4. S1 (F1 factor only, config change).
5. F2-F5, F7, F9, F10 and the build-time revision stamp. Then S2-S5 and the R3 repeat.
6. [+] **FA1, the ephemeris** (smoke, in any lock gap): `davey2016.toml` against
   `config/sensitivity/inmarsat-ephemeris.toml`. See the ephemeris note below.
7. Request 15 goes into any gap.
8. A separate fuel session builds the internal and public fuel models. I will write its master prompt
   once Pete confirms.
9. The F11 design note, then F6, F12, F13 and F19.
   - Audit minor items: tests that skip when `fuel-tables.json` is absent; the source rows for the
     satellite/EAFC values; a `mean_log_evidence` label.
10. **One bundled full re-run:**
    - corrected fuel;
    - the fixed sampler;
    - the ephemeris Pete chooses;
    - the families;
    - wide early Mach, if S3 supports it;
    - 100,000 hand-off rows;
    - the look-ahead, if end of flight supports it;
    - seeds, or more particles per seed, as you will propose.
11. Interface work (requests 4 and 12, composer B and C, DRIFT-1 to DRIFT-3) and the two sensitivity
    studies.

**To keep the names apart:** the fuel audit's smoke tests are S1-S5. The filter audit's are FA1
(ephemeris), FA2 (step size), FA3 (tempering) and FA4 (bias drift).

**The ephemeris (audit F2).** `data/satellite-ephemeris-inmarsat.csv` holds Inmarsat's published states
(Ashton et al. 2015, Table 4, p. 10, DOI 10.1017/S037346331400068X), Hermite-interpolated to the
epochs; the auditor reproduced the interpolation independently.
- The −495,679 µs BTO offset and the satellite+EAFC terms were derived with these states.
- The STK/SGP4 file differs from them by 1.9-3.9 km, which gives a BTO swing of 16.7 µs over the flight.
- My recommendation to Pete: the Inmarsat states for every extension run, and so for the bundled
  re-run. Whether `davey2016.toml` itself changes is his decision, because that config must stay
  byte-identical. One option is a separate `davey2016-inmarsat` reproduction variant, with FA1
  measuring the difference.

**Provenance housekeeping (Pete's decisions):**
- `results/davey-2016.pdf` stays, with the notice `results/davey-2016.LICENSE.md`.
- The `tmp/` avionics files stay and may be used internally. Any use is recorded in
  `results/restricted-sources-ledger.md`.

- Modular Architecture

## 2026-10-09 ~23:30 UTC - architecture: Pete's confirmations

1. **Request 17 (sampler ancestry fix) before S1.** Confirmed. Core's order becomes: request 14, then
   request 17 with its unit test, then S0 (baseline, fixed sampler), then S1-S5.
2. **A separate fuel session builds the internal and public fuel models.** Confirmed. Its brief is
   `threads/master-prompts/fuel-model.md`; it owns `engine/fuel-model/` and `results/fuel-model/`.
   Core integrates its outputs under request 16.
3. **The Inmarsat ephemeris** (`data/satellite-ephemeris-inmarsat.csv`, Ashton Table 4) is used for all
   extension runs, including the bundled re-run. The reproduction variant is still open with Pete.
4. **Pete wants one overnight run with all the fixes in, if possible.** Core: when S1-S5 show the run
   time, size the bundled run against a single night. Bring Pete the options: seeds, particles, and
   whether the families come in the same run or a second one. Do not start it without his agreement.

- Modular Architecture

## 2026-10-09 ~23:40 UTC - architecture → core: go-ahead (Pete confirmed all three)

Your reply of ~23:15 UTC is agreed in full, including your two additions:
- **the guard:** no epoch may be both tempered and rejuvenated;
- **the bound before the fix:** use the weight unevenness at each tempered epoch, taken from the
  existing diagnostics.

Pete has confirmed:
1. request 17 before S1, with S0 as the baseline;
2. a separate fuel session, now running from `threads/master-prompts/fuel-model.md`;
3. the Inmarsat ephemeris for extension runs and the bundled re-run, with `davey2016.toml`
   byte-identical and a separate `davey2016-inmarsat` variant beside it.

Please check which satellite states Davey used before the paper calls either variant the faithful one.

You can start now:
1. Request 14, with F4 included.
2. Request 17, with the guard and its unit test.
3. The family report.
4. S0, then S1, when the lock frees.

Pete wants **one overnight run with all the fixes in**. Once S0-S5 give you run times, bring him the
sizing options. The previous reference took 8.7 h; the families made the last run 20+ h. Do not start
the run without his agreement.

Note on line numbers: you cite `filter.rs:740` and `:787`; the committed `1c2b295` has them at `:717`
and `:776`. If your working tree is ahead of git, commit before the rebuild, so the build stamp means
something.

- Modular Architecture

## 2026-10-09 ~23:55 UTC - architecture: the single-engine phase (audit F11), from Pete's direction. Who owns what.

**End of flight owns the single-engine dynamics.** One engine runs dry before the other, the
second up to 15 min later (ATSB AE-2014-054 p. 9). That sets up the uncontrolled phase:
- asymmetric thrust and yaw;
- the autopilot's response;
- the drift-down and turn before the second engine stops.

End of flight models this in the 6-DOF simulator, consistent with the Boeing end-of-flight cases, and
reports how it changes the impact distribution against the single-pool baseline.

**Core keeps a narrow part:**
- It carries two fuel states, left and right, in place of the single pool.
- It passes both at the hand-off, with per-engine exhaustion times.
- If the first engine stops before 00:11, the cruise segment up to 00:11 must fly on one engine (lower
  and slower). Core writes the design note for that case under request 16 item 9.

**The fuel session supplies:**
- the one-engine-inoperative tables;
- the left/right imbalance at 18:01:49, with sources.

**Status.** This is not in tomorrow's bundled run unless its design and tests are ready. The bundled
run is now **gated on the internal fuel model** (Pete).

- Modular Architecture

## 2026-10-09 ~23:25 UTC - fuel model: ETA for the internal model (core request 16 C)

Brief: `threads/master-prompts/fuel-model.md` at `74e2e15`. Work goes to `engine/fuel-model/` and
`results/fuel-model/`; no `crates/` edits.

**ETA (UTC):**
1. **Internal model: tables + calibration, by ~03:00 on 10 Oct.** All table classes (confidential and
   INOP included, local only), the factor defined as Boeing ÷ model and applied as a multiplier, the
   temperature term, the bilinear-edge and floor fixes (F3, F4), a weight-dependent ceiling table (F5),
   and residual-based uncertainty. Delivered as a git-ignored JSON in core's `FuelFlow` schema plus a
   dense calibrated grid, a Python reference implementation and test vectors. Schema changes come as
   core requests.
2. **Left/right imbalance at 18:01:49 and the INOP tables: with item 1.**
3. **Cross-check against the coded model along `reference-289` paths: by ~06:00 on 10 Oct.**
4. **Public parametric model: later on 10 Oct.** It does not gate the run.

**New input found, internal use only.** `library_full_audit/MH370/` holds 9M-MRO's previous flight,
MH371 on 7 Mar 2014. It has 5-minute ACARS position reports (pressure altitude, Mach, SAT, gross weight,
FQIS fuel) and EHM snapshots with per-engine fuel flow. That gives about 2.6 h at FL400 and 1.5 h at
FL276 on the same airframe and engines at measured temperature, so it is a second calibration source
next to Boeing's standard-day figures, and a direct test of the temperature term. At FL400 one EHM
snapshot shows the right engine burning ~3.4 % more than the left at equal EPR. That bears on the
imbalance. I will record its provenance in the restricted-sources ledger.

- Fuel model
## 2026-10-10 ~00:20 UTC - architecture: what the next large core run is (Pete)

**The next large run is the updated model, with every fix and extension in.** It is not a repeat of the
reference-289 configuration. It contains:
- **fixes:**
  - request 17 (sampler);
  - the corrected fuel model, gated on the fuel session's internal model;
  - the Inmarsat ephemeris;
- **extensions:**
  - radar scoring;
  - the families (free, routes, descent-climb);
  - wide early Mach (unless S3 shows a problem);
  - the vertical rate in the BFO;
  - 100,000 hand-off rows;
  - the look-ahead, if end of flight supports it.

It replaces `reference-289` and tonight's family results as the base for every module.

Pete and core design and size it: overnight, or a night plus a morning. Core brings the timings after
S0-S5. A full-scale Davey-only baseline (no fuel, plain sampler) is optional and lower priority.

- Modular Architecture

## 2026-10-10 - fuel model: DELIVERY 1 - internal fuel model `internal-v1` (core request 16 C), ready for integration

Report: `results/fuel-model/internal-model.md`. Code: `engine/fuel-model/`. No `crates/` edits; no filter run.
**Model file (LOCAL ONLY, git-ignored by `/data/external`):** `engine/data/external/fuel-model/internal-v1.json`
(8.3 MB, sha256 `c5fe32e3…`). Core can copy it from the fuel session's workspace (readable cross-session)
or from local artifact `2ee08c24-f528-46f2-b945-c10c7f38dcb8`. It holds the 16 extract grids unchanged
(`FuelTables::from_json` still parses it), the dense calibrated-shape grid, the INOP grid, a ceiling table,
the parameters and 300 test vectors. Rebuild: `python fuel-model/build_internal.py` from `engine/` (about 40 s).

**Result.**
- **FF = κ_traj · τ(ΔISA, M) · G(FL, W, M)**, where:
  - G: standard-day grid with F3 (zero-weight corners), F4 (back-side rule bounded at 0.95 × holding; close
    pairs clamped) and a drag-rise term above M0.84;
  - **τ = 1 + 0.003 · ΔISA · (1 + 0.2 M²)**, the FPPM rule in SAT terms (0.34 %/°C at M0.82);
  - **κ_traj ~ N(1.0004, 0.0196), a MULTIPLIER.** F1 is gone by construction.
- **Calibration, κ as a multiplier:**

  | evidence | κ |
  |---|---|
  | Boeing only (16 envelope items; standard day, so identical with or without the temperature term) | 0.9893 ± 0.0037, residual s.d. 0.014 |
  | MH371 measured cruise, with the temperature term | 1.0073 |
  | MH371 measured cruise, without it | 1.0172 |
  | **Joint, with the temperature term** | **1.0004 ± 0.0085**, between-group τ 0.014 |
  | Joint, without it | 1.0030, τ 0.018 |

- **Boeing Table 3 (1.010) and Table 4 (0.985) disagree by 2.5 %.** MH371 sides with Table 3. The
  tension is carried in the s.d., not resolved.
- **No weight-dependent factor.** F1b's trend is the Table 3 against Table 4 contrast. MH371 at FL400,
  186-200 t, shows no trend.
- **The temperature term is supported by MH371.** A free fit gives 0.0031 ± 0.0012 /°C, against the
  rule's 0.0034. This is internal and confounded with FL.
- **Exhaustion against the code as coded,** on constant profiles from 18:01:49 (**provisional**; the
  cross-check along posterior paths follows):

  | FL | ERA5 route ΔISA | internal minus coded |
  |---|---|---|
  | 300 | +11.9 °C | −10 to −12 min |
  | 350 | +9.1 °C | −8 to −9 min |
  | 370 | +5.5 °C | −4 min |
  | 390-400 at M ≥ 0.82 | about 0 °C | +0 to +2 min |
  | 400 at M ≤ 0.80 | | −10 to −58 min (the F3/F4 pocket removed) |

- **Single engine (Pete's item 3).**
  - **L − R at 18:01:49 = +221 kg** (L 18,395, R 18,174 kg), range +47 to +421. Sources: Ulich v5.6 tank
    estimate at 17:06:43 (+146 kg); R/L flow ratio **1.021** (range 1.013-1.035, from Ulich's tank-rate value
    and the MH371/MH370 EHM per-engine WF); SIR App. 1.6E p. 5.
  - The right engine runs dry first, and the left runs on for 3-14 min (best 7-8). That is consistent with
    ATSB AE-2014-054 p. 9.
  - The INOP grid is in the file. Single-engine flow is 0.79-0.99 of the twin flow, so the pooled
    exhaustion and the left flame-out differ by only about 0.1-1.5 min (less than the audit's F11
    estimate of 0-6 min).

**Core requests (16 C-1 to C-8; details in report §7). Schema changes are marked.**
1. **C-1:** grid reader, with trilinear interpolation and OR'ed corner flags. Config-gated:
   `fuel.model = "internal-v1"`. Default unchanged; `davey2016.toml` byte-identical. Unit test against
   `test_vectors`.
2. **C-2 (schema):** `fuel_flow_kg_h(fl, weight_t, mach, delta_isa_k)`, with ΔISA from the ERA5 temperature
   already used for TAS. This reaches end of flight's `takeover_priced` through `FuelFlow`.
3. **C-3:** `factor_mean = 1.0004`, `factor_sd = 0.0196`, as a multiplier. Arms: Boeing-only N(0.9893,
   0.0143); MH371-only N(1.0073, 0.0110); no-temperature N(1.0030, 0.0236).
4. **C-4:** `initial_kg = 36,569` when the temperature term is on (36,725 is the standard-day figure), or
   better `43,800 − κ_traj × 7,228`.
5. **C-5:** use `ceiling_fl(weight_t)` for F5 (FL430 at ≤ 190 t, FL400 at 215-220 t).
6. **C-6:** extra s.d. of 0.021 on steps above M0.84 (F6). Elsewhere none is needed.
7. **C-7 (schema, two fuel states):** initial L − R = +221 kg (s.d. ≈ 120); R : L = 1.021 (s.d. ≈ 0.008);
   `grid_inop` after the first flame-out.
8. **C-8 (F10):** the end-of-flight form, flow × (1 + (L/D) sin γ) with the idle floor, and the climb factor
   capped at climb thrust.

**Restricted use** is recorded in `results/restricted-sources-ledger.md`: the confidential cells; the MH371
ACARS and EHM data (provenance unverified); Ulich's workbook notes. Committed files are model outputs only.

**Next:** delivery 2 (the cross-check along `reference-289` hand-off states), then delivery 3 (the public
parametric model).

- Fuel model

## 2026-10-10 - fuel model: DELIVERY 2 - cross-check on `reference-289` (PROVISIONAL, not a filter run)

`results/fuel-model/crosscheck-reference289.md`. The sample is 2,000 weighted m0011 hand-off states
(seeds 1-4), each held at its constant 00:11 state. Only the difference between the models is applied to
the filter's own 00:11 fuel. Medians of internal-v1 minus coded:

| band | Δ exhaustion, route ΔISA | dry before 00:11 |
|---|---|---|
| FL250-290 | −11.8 min | 68 % |
| FL300-330 | −10.5 min | 58 % |
| FL340-370 | −7.2 min | 26 % |
| FL380-400 | −1.5 min | 16 % |
| FL410-430 | −33.9 min (F3/F4 pocket) | 61 % |
| all | −9.3 min | **42 %** |

- With the 00:11 point temperature, which is colder, 25 % of the weight is dry before 00:11; on the
  standard day, 18 %.
- Median exhaustion: 00:23 as coded; 00:13-00:21 internal, depending on the temperature case.
- **Reading.** The reference posterior's FL410-430 mass is largely a fuel artefact (F3-F5). The warm
  low/mid paths lose 7-12 min to the temperature term.
- Crude path removal moves the mean 00:11 latitude by −0.15° to +0.06°, so the direction is not
  determined. The 00:19 shift needs the filter: smoke tests S2-S4. Expect S2 and S3 to dominate S1.

- Fuel model

## 2026-10-10 - fuel model: DELIVERY 3 - the public parametric law, and internal against public (does not gate the run)

`results/fuel-model/public-model.md`; `engine/fuel-model/public.py`; `results/fuel-model/public-model.json`.

**The law.** FF = TSFC · D, made of:
- a parabolic polar;
- Lock's wave drag with a Korn C_L term (sweep 31.6°);
- TSFC = c_T (1 + b_M M)(T_ISA/288.15)^a (T/T_ISA)^0.5.

It is fitted to Boeing's 27 numbers only and needs no tables.
- **rms 1.74 % over all 27 numbers, 1.48 % over the 15 envelope items.**
- Factor N(1.0, 0.017).
- 36,609 kg at 18:01:49 with temperature.

**Internal against public, along the same 2,000 `reference-289` states with route ΔISA** (provisional):
- median exhaustion **−11.5 min [−19.9, +5.6]**, internal earlier (00:13 against 00:21);
- 42 % against 25 % of the weight dry before 00:11.

The difference has three parts:
1. **Calibration level, about −5 min.** MH371's measured burn is in the internal model; the public law sees
   Boeing only.
2. **Temperature coefficient, −3 to −5 min** at ISA +5 to +12 °C. The FPPM rule is 0.34 %/°C; √θ is
   0.23 %/°C.
3. **Shape at FL400,** −17 to +14 min, slow to fast.

**Core request 16 C-9 (low priority, not for tonight):** add a `fuel.model = "public-v1"` closed-form arm for
the paper.

**Correction to delivery 1.** The local artifact `2ee08c24…` (internal-v1.json) stays in the local artifact
store by Pete's choice, and the ledger records it. It is never committed and never sent to a third party.

- Fuel model
## 2026-10-10 ~01:10 UTC - architecture: confidential items are authorised (Pete)

Pete states that the project holds authorisation for all the confidential items: the FPPM-confidential
fuel cells and the `tmp/` material.
- **Internal use is authorised in full.** The internal fuel model uses every cell without penalty.
- **Publication and redistribution scope** are being confirmed with Pete. Until then, the tables stay
  git-ignored (the repo is public), and the restricted-sources ledger keeps recording uses.

- Modular Architecture

## 2026-10-10 ~01:30 UTC - architecture: authorisation scope (Pete)

Pete: **"that authorization applies to all confidential items in the repo."** Any session may use any
confidential item in the repo internally.
- Publication and public redistribution are settled at the paper's provenance review.
- Until then, confidential tables stay git-ignored, and uses are recorded in
  `results/restricted-sources-ledger.md`.

- Modular Architecture

## 2026-10-10 ~01:40 UTC - architecture: SSH host coming (Pete)

Pete is adding an SSH host so that the core and ocean big runs can go in parallel. My proposal to
Pete: core's S0-S5 and the bundled run go to the host, and drift stays on the Mac. Details are in
`architecture.md`. Wait for the host details and Pete's agreement before moving anything.

- Modular Architecture

## 2026-10-10 ~02:00 UTC - architecture → all modules: second machine (Pete's SSH host)

Pete has brought up an internal SSH host on his premises: `abiome-deskstar`, port 2222.
- It is authorised for all restricted items, including the confidential fuel cells and the internal
  fuel model. The restricted-sources concern applies only to third-party or metered compute.
- **Credentials are not recorded here.** Use the platform's Compute panel connection once Pete has added
  it. Never write a password into the repo, the notes or memory.
- **Status:** the host is up, but it is not yet registered in the session Compute panel, and its name
  does not resolve from inside the session sandboxes. Until it is registered, no session can reach it.

**Planned split** (proposal; nothing moves until the host is listed and Pete agrees):
- **Host:** core's S0-S5 and the bundled updated-model run.
- **This Mac:** drift production, end of flight, and the downstream re-runs.

Comparison rules: both sides of any A/B run on the same machine, and every `run.json` records its
platform.

- Modular Architecture
