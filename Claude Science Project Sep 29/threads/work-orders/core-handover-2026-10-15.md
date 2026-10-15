# Core handover — 15 October 2026

Written by the outgoing core thread from its own record and checked against the committed tree at
`e9457f4`. It replaces `core-handover-2026-10-15-DRAFT.md`, which was checked and corrected here.
A fresh core thread should read this first. Statements marked **UNCERTAIN** have not been verified
since the swept workspace was lost.

---

## GAP 1 — core request 9 exists as code, under a different name

**Neither reading (a) nor reading (b) in the draft is correct.** Core request 9 was built,
committed and pushed in **`d4e67b09`** (11 Oct 2026). It is still in the tree. `git grep
burst_target_weight` finds nothing because that name was never used.

- **What request 9 was.** Architecture's definition, 11 Oct 01:45 −0600 (CORE_STAGES.md about line
  2812): *"unnormalised within-parent weights"* in the terminal stage (stage 2, end of flight). It
  is the device that lets end of flight's within-parent targeted sampler for H1/H2 have unbiased
  weights.
- **Code.**
  - Config key: `[terminal] within_parent = "self-normalised" | "unnormalised"`. It is
    `Option<String>`; unset means self-normalised, the old behaviour.
    (`crates/mh370/src/config.rs` about line 77.)
  - `crates/mh370/src/terminal.rs`: field `unnormalised` (about line 42), parsed at about line 149.
    `pub fn child_weights(row_weight, log_weights, children, unnormalised)` is at about line 596.
  - `run.json` records `"within_parent_weights"`.
  - In the unnormalised rule, child k of a hand-off row gets
    `row.weight × exp(ln q_k) / (M × children)`. This is unbiased whenever the module's ln(p/q) is
    exact. Per-parent sums equal `row.weight` only in expectation.
- **Tested.**
  - Unit test `terminal::tests::within_parent_weights_self_normalised_and_unnormalised`: the
    unnormalised rule is unbiased, and the self-normalised rule shows the expected small-K bias.
  - Gates B and C byte-identical. The smoke's terminal module has ln(p/q) = 0, so the two rules
    agree.
- **Never run** in any production or module run. Using it was held for Pete's GO and never given.
- **What it is NOT.** It is not a core-side hand-off proposal that draws 00:11 parents with the
  00:19 bursts in hand. That device, which is what the item 10 work order describes, **was never
  specified in core and never built**.
  - The end-of-flight `score_select_k` aimed proposal (alpha = 0.2, run-i-dive) belongs to end of
    flight. It is a separate thing.
  - The item 10 work order calls its device "core request 9". That is a renaming. The successor
    should give it a new request number to avoid confusion with `d4e67b09`.
- **What to expect first if the unnormalised rule is used.** Per-parent weight sums will scatter
  around `row.weight`, and the composer's per-parent assumptions may break. Check that every
  consumer reads weights as weights, not as shares that sum to one per parent.

## GAP 2 — `results/run-j-change-list.md` was never written

Architecture asked for it on 12 Oct at 18:40Z and 20:35Z. This thread had no turn between 12 Oct
18:32Z and this handover, so it was never created. Its contents, reconstructed from the committed
coordination record (Pete's 13 Oct 00:40Z ruling cuts it to the core items only):

| # | Item | Source | Evidence | State |
|---|---|---|---|---|
| 1 | Waypoint and free-flight convergence. All-partition split-half: waypoints 0.916, free 0.830, against the 8-replicate floor 0.924. | Run I; composer pass 2 §8 | Run I report. A 23:15 refresh smoke changed nothing (Δln Z −0.01). More particles (estimated 2.2–5×) is the only tested remedy. | Deferred, no date |
| 2 | Aimed proposal for the northern arc, about 34–25 S. Searched-area evidence moves weight north. | Composer pass 2 §8 | No smoke yet | Not designed |
| 3 | 18:25:27 R600 epoch: BFO 142 Hz as observed (sd 7); BTO 12,520 µs (sd 62), included but flagged; only the last two R1200 BFOs (18:28:05 and 18:28:14), which run I already uses. | Pete's ruling, 12 Oct | Smoke f529c67a, `results/run-i-oct12/r600-1825-smoke.csv` | Data file committed: `engine/data/variants/satcom-observations-r600-1825.csv` + `config/sensitivity/obs-r600-1825.toml` (4297f3bc) |
| 3a | For item 3: record the BER and C/N0 of the 18:25:27 burst from the Inmarsat log, if the project holds it. Holland excluded it for signal quality, and arm E's −89 assumes it is trustworthy. | PAPER.md 19:05Z, via architecture | — | Open |
| 4 | Wording rules for charts and notes (Pete's language rule; "Holland transient bias added"). | Architecture, 12 Oct | — | Applies to reports, not to config |

Run J needs **Pete's own explicit GO**; no delegated GO applies. Before it starts, post a proposal
with size, ETA, disk and predictions. The successor should commit this table as
`results/run-j-change-list.md`.

## GAP 3 — what lived only in the swept workspace

| Item | Where it was | Status | Recovery |
|---|---|---|---|
| Gate reference outputs `regress/gate/tb-B` (8 npy), `tb-C` (4 npy), `f12-*`, `regress/hoe/mh370-head` | workspace | **LOST** | Regenerate from an unmodified build of the current HEAD **before** touching code (section 2) |
| `deskstar/job-run-i-chain.sh`, `job-r600-smoke.sh`, older `job*.sh` | workspace | Lost on the Mac | A copy of each job's inputs is in its deskstar job directory: chain in `J/6a2ec01f-…/`, R600 smoke in `J/f529c67a-…/`. `job-run-i.sh` is committed in `engine/config/sensitivity/next-run/`. |
| `compact_c.py` (compacts a finished stratum's per-seed outputs) | deskstar `J/53d0d251-e343-4b9a-8a2c-cafdfacce879/compact_c.py` | On deskstar only | Copy it into the repo before that job directory is cleaned |
| `tools/stage_run_i.py` (joins 250 MB parts, verifies SHA256, moves into the exchange) | workspace | **LOST** | Rewrite (section 5). The other chart scripts are committed in `results/run-i-oct12/`. |
| `out/next-run-d` (run D small files; `engine/report/build_run_i_reports.py` uses them as its baseline) | workspace | **LOST**; the Downloads copy was removed earlier | Re-fetch from deskstar if still there (**UNCERTAIN**), or drop the run D comparison |
| `hpc/f529c67a-…/r600-smoke.tar.gz` (R600 smoke `run.json`/`summary.json`) | workspace | Lost on the Mac | Reduced table committed. Originals probably still in deskstar job dir `f529c67a` (**UNCERTAIN**). |
| `out/reports-i` (run I report PDFs, charts) | workspace | Safe | Saved as artifacts, and charts committed in `results/run-i-oct12/` |
| Run I raw outputs (34 GB, 340 files) | `~/Downloads/mh370-exchange/core/run-i/` | Present (`README.md`, `READY`, `SHA256SUMS` checked 15 Oct) | — |
| Runs E and F (7506176a, 4ac6da02) | Pete's SSD only | Deleted from deskstar and Downloads | The SSD is the only copy |
| Run I raw strata on deskstar (waypoints, descent-climb, repro) | deskstar | Kept "for now"; about 16 GB was free | Delete only after confirming the exchange copy |
| Engine source | — | Nothing known uncommitted: tau_h `5500e5e8`, R600 variants `4297f3bc`, request 9 `d4e67b09` are all pushed | — |

---

## 1. Build environment — checked

```
export PATH=/Users/pete/.rustup/toolchains/1.98.0-aarch64-apple-darwin/bin:$PATH
export RUSTUP_HOME=/Users/pete/.rustup
export CARGO_HOME=/Users/pete/.cargo          # the old thread used $W/.cargo; either works
export HOME=$PWD XDG_CONFIG_HOME=$PWD/.xdg; mkdir -p .xdg/git && : > .xdg/git/ignore
export CARGO_TARGET_DIR=<ABSOLUTE path outside the repo tree>
git config --local core.excludesFile ""
cargo build -j 2 --release      # from engine/; -j 2 on the Mac outside the heavy lock
```

- Toolchain 1.98.0 is present (checked 15 Oct). `cargo` is not on PATH by default.
- `XDG_CONFIG_HOME` is redirected because `~/.config/git` is unreadable from the sandbox.
- A relative target directory inside `engine/` breaks `make scope`.
- `fatal: failed to store: -50` is a harmless keychain warning.
- Building needs `index.crates.io` and `static.crates.io`.
- **Mac thread rule:** 12 threads inside the heavy lock (`/tmp/.mh370-heavy.lock`) plus at most 2
  outside it. Local engine runs outside the lock use `RAYON_NUM_THREADS=2`.
- **Push loop:** commit, `git pull -q --rebase`, push, then check `HEAD == origin/claude-science-sep29`.
  - A rebase flattens local merges.
  - Concurrent appends to `CORE_STAGES.md` conflict often. Resolve by keeping both sides.

## 2. Regression gates — CORRECTED

- **The −96.66146918417472 value is stale.** It was seed 1 of `davey2016.toml` as it stood on
  about 1–2 Oct. On 9 Oct `davey2016.toml`'s base prior track changed to 289.7° (see
  `early-families/track-289.toml`), so the current tree will not reproduce it. **UNCERTAIN:** the
  current value of `config/sensitivity/regress-seed1.toml` was never re-recorded. Record it once
  from an unmodified HEAD build and use that.
- **The gates in use from 9 Oct.** Byte comparison of every non-`.json`, non-`.log` output file
  against reference outputs from the previous binary, with `RAYON_NUM_THREADS=6`:

  ```
  # from engine/, after building the reference (unmodified) binary and the candidate binary:
  $BIN config/davey2016.toml config/sensitivity/handoff-smoke.toml config/smoke.toml $OUT/tb-B   # 8 npy files
  $BIN config/davey2016.toml config/sensitivity/ladder/fuel.toml   config/smoke.toml $OUT/tb-C   # 4 npy files
  # compare with filecmp.cmp(shallow=False) file by file; expect an empty diff list
  ```

  - B covers the filter, hand-offs and the terminal stage.
  - C covers the fuel ladder.
  - The references were lost with the workspace (GAP 3), so **regenerate both from HEAD before
    any change**.
- **Unit tests.** `cargo test --release --workspace` gave 235 passing at `5500e5e8`. The deskstar
  job runs `-p mh370-flight -p mh370` and stops on any failure.
- **The rest of the draft's table stands.** `make scope H=<name>` (with `--relative`, and BASE
  `origin/claude-science-sep29`) checks a branch's footprint. `make smoke H=<name>` checks code
  paths only and is never evidence. `make hypothesis H=<name>` runs at full scale and is not to be
  run casually.
- **Gates added since the draft's list:**
  - tiny routes runs with and without `turn_backs`;
  - the R600 variant local check;
  - the tau_h merge, which was gated with B and C.

## 3. Determinism and random-number discipline

**How streams are built** (`crates/mh370/src/filter.rs`): every draw comes from
`stream(seed, stratum, step, particle)`, a ChaCha8Rng seeded with the replicate seed. The stream id
is `((stratum << 16 | step) << 32) | particle`.

- Each (stratum, step tag, particle) has its own independent stream. Thread scheduling therefore
  does not change any draw.
- Parallel reductions use a fixed-order chunked sum. A plain `par_iter().sum()` would change the
  last bits from run to run.

**Step tags in use.** These are reserved offsets; keep new tags clear of them and below 65,536:

| Tag | Use |
|---|---|
| 0 | prior draw |
| small integers | step index for propagation |
| 2000+k | resample at epoch k |
| 3000 | route samples |
| 4000+k | residual snapshot (output only) |
| 5000 / 5100+k / 5150+k | hand-off and look-ahead |
| 6000+k | tempering stage resample |
| 8000 / 8100 / 8200 | branching |
| 9100 / 9200 | moves |
| 9500 / 9600 / 9800 | rejuvenation |
| `u64::MAX`, `−1`, `−2−e` | route draw and stop hand-off |

**Preserves byte identity:**
- a new feature whose off path makes no extra draw and changes no floating-point operation order;
- a new draw on a **new** tag;
- output-only diagnostics on their own stream (as `residual_snapshot` does);
- pure refactors that keep the arithmetic order (the `step_update` closure was byte-identical).

Off-by-default `Option` keys have always passed the gates (`within_parent`, `tau_h`,
`rejuvenate_epochs`, `turn_backs`, `handoff_epochs`, fuel C-1..C-n). **But this is not guaranteed
by construction. Prove it with gates B and C every time.**

**Silently breaks byte identity:**
- an extra draw, or a reordered draw, inside an existing (step, particle) stream;
- any change to the epoch or step schedule. Adding an epoch renumbers every later step and shifts
  every later stream. **So run J, with the m1825r600 epoch, can never be byte-compared with run I.**
  Compare statistically.
- a change to particle order before propagation, such as a different resampler or a branching
  population change;
- a reused tag;
- reassociating sums or likelihood terms, or changing the fixed-sum chunk size;
- changing a default value in `config.rs`.
- Thread count: by design it does not matter. In practice the gates always used 6 threads.
  **UNCERTAIN:** byte identity across different thread counts was not separately recorded.

## 4. Configuration lineage — checked against `engine/config/`

- **Production stack** (`config/sensitivity/next-run/driver.sh`, COMMON):
  - `davey2016-inmarsat.toml` (base `davey2016.toml` with Inmarsat's published satellite states);
  - `no-exhaustion-prior.toml`;
  - fuel fixes `s1-factor`, `s2-temperature`, `s3-internal`, `s4-ceiling`, `s5-hard-reject`,
    `s6-tanks`;
  - `reference-snapshots.toml`;
  - `early-families/radar-full.toml`.

  Then EXTRA, then the family overlay, then `server-<run>-<stratum>.toml`.
  - Run I's EXTRA: `s7-single-engine`, `s8-hold-taper`, `inop-flow-fix`,
    `early-families/speed-envelope-throughout` (not for repro), `handoff-lookahead-d`.
  - Family overlays: `free.toml`, `waypoints.toml`, `route-sampler.toml`, `descent-climb.toml`;
    the repro stratum has none.
- **Names.**
  - "reference-289" is not a file. The 289.7° track became the base of `davey2016.toml` on 9 Oct,
    and `early-families/track-289.toml` is kept as a no-op.
  - The other names in the draft are on the branch as listed: `tempered-1839-1941.toml`,
    `tempered-three.toml`, the `stage2-fuel*` and `stage3-bias-drift*` families, `track-wide*`,
    `vr-only`, `wind-off`, `no-exhaustion-prior`, `6temper-realloc`, `best-model*`, `bfo4hz-fixed`.
- **Model changes against sampler changes in the chain.**
  - Sampler only: tempering at 18:39 and 19:41.
  - Model changes:
    - fuel and endurance (about 8.3–8.45 nat);
    - `no-exhaustion-prior` (00:17:30 term removed);
    - the 289.7° prior track;
    - the Inmarsat ephemeris;
    - fuel fixes s1–s8;
    - Pete's speed envelope (cruise 0.70–0.87 within 210–330 KCAS; repro stays exactly Davey);
    - the four early-flight families (a prior over families).
  - Sampler: the run C sampler (`sampler-ad50`, `resample_ess_fraction = 0.2`) and look-ahead
    hand-offs.
- **Withdrawn:** 6temper-realloc results (defective fuel model; its sampler statistics stand).
- **F1 (request 17).** Every run with tempered epochs made before the fix carries the
  tempered-move ancestry defect. The fix was delivered in `b60cbb7` / `34ef6bc` on 10 Oct about
  01:45Z. Runs C to I postdate it. **UNCERTAIN** for reference-289-era runs made on 9 Oct: check the
  binary revision in their `run.json`.

## 5. Deskstar

`ssh:deskstar`: 94 threads, 36 GiB cgroup, 59 GB loop volume.

**Submit** (repl):

```python
c = host.compute.create("deskstar")
job = c.submit_job(command="STRATUM=<free|sampler|dc|repro> sh job-run-i.sh",
    intent="...", inputs=[{"src": "<workspace>/job-run-i.sh", "dst": "job-run-i.sh"}],
    outputs=["timeline.txt", "monitor.txt", "tests.txt", "REVISION", "run-i-<stratum>-small.tar.gz"],
    run_timeout_s=10800)
```

- `job-run-i.sh` is committed at `engine/config/sensitivity/next-run/job-run-i.sh`.
- Each job:
  - fetches and hard-resets `$HOME/mh370/repo` to origin `claude-science-sep29`;
  - unpacks the engine data from J7 = `J/7ba3b89b-e955-45a6-90d5-a28d3164673b/engine-data.tar.gz`
    (**never delete J7**);
  - builds with `-j 48` and runs the unit tests;
  - copies the binary to `$HOME/mh370/bin-<rev>`;
  - runs a tiny preflight at 40 threads;
  - checks for at least 12 GB free;
  - then runs at 88 threads.
- J = `/home/pete/.claude-science-scratch/.claude-science/jobs`.

**Logs, all in `J/<job_id>/`:**
- `timeline.txt` (milestones);
- `build.log`, `tests.txt`, `REVISION`;
- `monitor.txt` (disk and memory every 300 s while running);
- `runs-i/next-run-driver.log` (start and end lines for each stratum, with exit code);
- `runs-i/<name>.log` (engine stdout);
- `runs-i/<name>/run.json`, `summary.json`, and `bto-bfo/seed-*/`.

**Finished or dead.** Finished means all four of these:
1. `DONE` exists;
2. the timeline shows `RUN I <s> END` and `packed small files`;
3. the driver log shows `end <name> exit 0`;
4. `runs-i/<name>/run.json` exists.

- **`DONE` is touched even if the engine failed**, so `DONE` alone proves nothing.
- Dead: `STARTED` without `DONE`, `monitor.txt` more than 10 min old, and no `pgrep -af mh370`
  process.
- Timeline exit codes:
  - 2: fetch failed;
  - 3: build or tests failed;
  - 5: preflight NO-GO;
  - 6: disk NO-GO;
  - 7: the chain's wait timed out.
- `memory.events` `oom_kill 2` is cumulative from run B and not new; compare against 2.
- The platform's `compute_done` also reports state and exit code.

**Chaining.** A chain job is itself a submitted job. It:
1. polls the previous job's `J/<prev>/DONE` every 60 s for at most 5 h;
2. sleeps 120 s;
3. runs `python3 J/53d0d251-…/compact_c.py <runs dir>`;
4. runs `STRATUM=<next> sh job-run-i.sh` and compacts that;
5. touches `CHAIN-DONE`.

Its source survives only in `J/6a2ec01f-…/job-run-i-chain.sh`.

**Limits.**
- `call_command` is limited to 60 s. Detach anything longer with
  `(setsid nohup … < /dev/null > log 2>&1 &)`.
- Downloads are limited to 256 MB per file. Split into 250 MB parts in
  `/home/pete/.claude-science-scratch/xfer`, download, join, verify SHA256, then move into
  `~/Downloads/mh370-exchange/core/<run>/` with `SHA256SUMS`, `README.md` and `READY` last.
- Staging needs a live session; the old `stage_run_i.py` is lost (GAP 3).

## 6. Traps that have cost time

The draft's list stands. Added:

- **`driver.sh` skips a stratum whose `run.json` exists.** Remove the directory to rerun it.
- **Adding an epoch shifts every later stream** (section 3). Never expect byte identity across
  observation sets.
- **The first BFO epoch carries the 25 Hz bias prior.** Its zero-residual increment is −4.18 nats,
  not −2.86. A prediction was missed this way.
- **Per-epoch evidence across modes:** combine with log-sum-exp over modes weighted by
  `prior_weight` and cumulative increments. Do not sum each mode separately.
- **Smoke-scale free-flight medians move by up to 1.4°** (420k × 4). Never quote smoke values.
- **18:25 BTO corrections:**
  - R600: −4,600 µs (Ashton et al. 2015 p. 7, not Holland).
  - R1200 log-on acknowledge: −5 × 7,820 µs (Davey sec. 5.2).
  - Raw bursts: `engine/data/satcom-1825-sequence.csv`.
- **Do not reuse the lineage code of chart artifact `3ccd0dba`.** Its fix-coordinate table is
  wrong. Georeference Pete's chart from `results/waypoints-2014-epoch-oct11/waypoints-2014-epoch.csv`
  plus MEKAR and NILAM.
- **Sparse clone:** use `git ls-tree -r --name-only` only. `git ls-tree -l` fetches every blob.
  Read single files with `git show HEAD:<path>`.
- **The repo is public.** Check staged files for `*.bin`, `fuel-tables.json` and `*.xlsm` before
  every push.

## 7. Open core items — CORRECTED

- **Deferred on Pete's 13 Oct ruling** (no date; Pete's own GO only): the table in GAP 2.
- **Item 10 work order:** needs a new request number (GAP 1) and Pete's GO.
- **Audit findings:**
  - **F1** fixed 10 Oct (section 4).
  - **F2 (ephemeris)** affects only runs on `davey2016.toml` itself, which uses STK/SGP4: the gates
    and Davey-reproduction comparisons. The production stack uses `davey2016-inmarsat.toml` and
    is consistent with the −495,679 µs calibration.
  - **F3 (step size, 5 s against Davey's 1 s):** still open. `cruise_step_s` and
    `manoeuvre_step_s` exist as optional keys, but no production overlay sets them.
    **UNCERTAIN:** the code default was not re-read for this handover.
  - **F4 (bias drift 00:11 → 00:19)** is implemented: with request 14 on 10 Oct, the bias is drifted
    from the last cruise BFO to the first 00:19 burst when `[bfo_bias] drift_hz2_per_s` is set. No
    production overlay sets it, so **it is off in run I**. Whether to switch it on is a run J
    decision.
- **Holland audit (12 Oct):**
  - No Holland parameters in the core crates.
  - The start-up offset model (D4/H1) and the H1/H2 arms are labelled options only.
  - The descent-rate windows are a diagnostic only, as Pete ruled.
  - Holland's shared start-up offset fails at 18:25: ln BF −89
    (`results/run-i-oct12/holland-startup-test-1825.csv`).
  - Open: the source of the "BFO in warm-up transient" labels in `satcom-1825-sequence.csv`.
