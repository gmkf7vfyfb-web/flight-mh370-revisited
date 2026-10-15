
# Core handover — DRAFT, pre-filled by the coordinating session 15 October 2026

**Status: INCOMPLETE. Sections marked VERIFIED were reconstructed from the durable project
record and the committed tree and should be checked, not rewritten. Sections marked GAP can only
be answered by the core thread itself.**

Why this draft exists: the core session's workspace
(`workspaces/386151e9-859f-412a-8d9d-b8da48899575`) has been **swept** — it is no longer on
disk — and the two things most needed are **not in the committed tree**. So the core thread's own
recollection may be the only surviving record. Answer the three gaps first; everything else here
is already written.

---

## GAP 1 — the one that matters most: does core request 9 exist as code?

`git grep burst_target_weight` over the whole committed branch returns **nothing**, and
`git ls-tree -r` finds **no `results/run-j-change-list.md`** anywhere. The project record says
the targeted sampler is "built, unused". Two readings, and the thread must say which:

- (a) It was built in the working copy and **never committed**, in which case it is **lost** with
  the workspace and must be rebuilt from the design.
- (b) "Built" referred to the **end-of-flight** aimed proposal — `score_select_k` in
  `hypotheses/end-of-flight/lib.rs`, with the defensive share alpha = 0.2, which is committed and
  was used in run-i-dive — and the **core-side** hand-off proposal was only ever specified.

The distinction is decisive. The end-of-flight device only helps descents beginning before 00:11;
the 22:41-to-00:11 cruise loss is core-flown and cannot be fixed in the module. If (a), say what
the design was. If (b), say so plainly so nobody looks for code that never existed.

## GAP 2 — `results/run-j-change-list.md`

Not committed, and there is no artifact of it. Pete's 13 October ruling names it as the holding
place for the deferred core items. Reproduce its contents, or state that it was never written.

## GAP 3 — anything else uncommitted

List any other work that lived only in the working copy, so it can be rebuilt or written off
deliberately rather than discovered missing later.

---

## 1. Build environment — VERIFIED, check

```
PATH=/Users/pete/.rustup/toolchains/1.98.0-aarch64-apple-darwin/bin:$PATH
CARGO_HOME=/Users/pete/.cargo
RUSTUP_HOME=/Users/pete/.rustup
XDG_CONFIG_HOME=<a writable dir in the session workspace, containing an empty git/ignore>
CARGO_TARGET_DIR=<ABSOLUTE path OUTSIDE the repo tree>
```
Rust is pinned to 1.98. `cargo` is not on PATH by default. `XDG_CONFIG_HOME` must be redirected
because `~/.config/git` is unreadable from the sandbox and cargo's git file listing otherwise
fails with "Could not read repository exclude / Operation not permitted"; also run
`git config --local core.excludesFile ""` in a fresh clone. A **relative** `target-eof` inside
`engine/` makes `make scope` fail, which is why the target directory must be absolute and
outside the tree. `fatal: failed to store: -50` on clone or push is a harmless macOS keychain
warning. Building needs `index.crates.io` and `static.crates.io`; a clean build is about 25 s.

## 2. Regression gates — VERIFIED, check and add anything missing

| gate | command | expected |
|---|---|---|
| Byte identity | seed 1 of `config/davey2016.toml` | log evidence **−96.66146918417472**, every digit |
| Scope | `make scope H=<name>` | fails if a branch touches anything outside `hypotheses/<name>/`; `BASE ?= origin/claude-science-sep29`, and `--relative` is required or root-relative paths never match `^hypotheses/` |
| Smoke | `make smoke H=<name>` | about one minute, code paths only; **a smoke run is never evidence** |
| Full scale | `make hypothesis H=<name>` | full scale — not to be run casually |

The byte-identity check is the cheapest regression test in the project: 1 M particles, one seed,
seconds. It caught the `step_update` refactor cleanly. **State whether any gate has been changed
or added since.**

## 3. Determinism and random-number discipline — GAP, partially VERIFIED

Known: the `step_update` closure factoring left seed 1 byte-identical, and two identically
configured arms of the early-families run came out byte-identical. **What the thread must add:**
what in practice breaks byte-identity when the step loop is touched — ordering of draws, number
of draws per particle, per-mode streams, and whether adding a config key that is off by default
is guaranteed safe.

## 4. Configuration lineage — VERIFIED from the committed config directory, check the reasons

Committed: `davey2016.toml`, `davey2016-inmarsat.toml`, `fixture.toml`, `integrated.toml`,
`smoke.toml`, plus `control/` and `sensitivity/`. In `sensitivity/` the lineage runs through
`tempered-1839-1941.toml`, `tempered-three.toml`, the `stage2-fuel*` and `stage3-bias-drift*`
families, `track-wide*`, `vr-only`, `wind-off`.

The reference chain, with what each step changed:
`davey2016` → tempering at 18:39 and 19:41 (sampler only, posterior unmoved) → fuel and endurance
(a model change, costing about 8.3 nat) → `no-exhaustion-prior` (fixed fuel tables, 00:17:30 term
removed, so exhaustion time became an output) → `reference-289` (prior track 289.7 rather than the
reconstructed 295.66) → run C → run I (four early-flight families) → `run-i-dive`.

**What the thread must confirm:** which of these are still on the branch under those names, which
were renamed, and which results are withdrawn. The 6temper-realloc results are withdrawn (defective
fuel model) while its sampler statistics stand.

## 5. Deskstar — VERIFIED, check

`ssh:deskstar`, Pete's internal Tailscale host: 94 threads, 36 GiB cgroup cap, 59 GB home. Core
runs smoke tests and large runs there; drift production and the other modules stay on the Mac.
Sequential strata are chained in one job (`job-run-i-chain.sh`) so no live session is needed
between strata: wait for the previous job's DONE marker, compact, run the next. Only the
deskstar-to-Mac staging needs a session. **Add: the exact submit command, where logs land, and
how to tell a finished job from a dead one.**

## 6. Traps that have cost time — VERIFIED, add to it

- `cargo test --release` does **not** rebuild `target/release/mh370`. Always `cargo build
  --release` immediately before copying a binary for a run; a stale binary was shipped once.
- `final.npy` is float32, so a unix time at 1.394e9 quantises to **128 s**. Column 21
  `fuel_exhausted_s_after_0000` holds seconds after 2014-03-08 00:00 to under a millisecond —
  read it by name. Runs before commit e319a4f have only 20 columns.
- `summary.json`'s `split_half_overlap` is **one** first-half-against-second-half partition.
  Never quote it. The canonical statistic is the mean over all balanced partitions, against the
  replicate-count-dependent floor: 0.896 at four, 0.914 at six, 0.924 at eight.
- A `nohup ... &` process launched from a bash cell is **unreachable** from later cells and does
  not survive a session interrupt or daemon restart. Per-seed outputs are the real checkpoint.
- Never edit a shell script while bash is executing it: bash reads by byte offset.
- Tempering resamples **inside** the epoch, so reading effective sample size at the usual place
  reports the population size. The honest number is the worst per-stage value.
- The runner does not wipe an existing output directory, so an interrupted multi-seed run can be
  resumed into it — but the second launch overwrites `run.json` with only its own seed list.
- `/tmp` is cleared at boot; binaries referenced by sha256 in recipes live there.
- `engine/AGENTS.md` allows exactly three markdown files under `engine/`; write-ups go to
  project-level `results/`.

## 7. Open core items — VERIFIED from the record, confirm and correct

Deferred to a future core run on Pete's 13 October ruling, which starts only on his own explicit
GO: free-flight and waypoint convergence; the aimed northern-arc proposal over about 34–25 S; and
the 18:25:27 R600 epoch (Pete's ruling: use the R600 BFO as observed at 142 Hz, include the R600
BTO of 12,520 us sd 62 flagged, and take only the last two R1200 BFOs of the 18:25–18:28 sequence
at 18:28:05 and 18:28:14).

Known open audit findings: F2, the ephemeris mismatch — `davey2016.toml` uses STK/SGP4 although
the −495,679 us calibration was made with Inmarsat states, giving a −6 to +10 us time-varying
swing; F3, the 5 s manoeuvre step against Davey's 1 s; F4, bias drift omitted from 00:11 to 00:19
in the terminal stage. **Confirm the state of the F1 tempered-move ancestry fix (core request 17)
and which runs carry the defect.**

---

## What to do with this draft

Fill the three gaps, correct anything wrong, add what is missing, and commit it as
`core-handover-2026-10-15.md` in this folder. Do not start any run, build or core request.
