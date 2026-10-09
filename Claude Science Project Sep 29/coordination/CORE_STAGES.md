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
