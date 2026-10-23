# Work order — end-of-flight: the 22:41 arm, then dynamics items 1 and 2

For the END_OF_FLIGHT_MODULE thread. Derived from the audit of 13 October 2026
(`eof-audit-2026-10-13.md`, `eof-audit-pushover-addendum.md`) and the costing
(`eof-dynamics-options-costing.md`). Governing contract: master prompt **version 7**
(`end-of-flight.md`), which must be in the repo at `threads/master-prompts/end-of-flight.md`
before this order is actioned — the repo copy is still version 4.

**Neither item can be started from the audit thread.** The engine source is not under any granted
path, and the Boeing traces (`ISO Sept 28 Status/inputs/end-of-flight/2018-08-19-eof-sims.zip`,
sha256 `e400ac73…`) are repo-resident and not reachable either. The clone is the first action.

---

## Item 0 — the 22:41 arm, and why it goes first

Run I has `handoff-m2241` hand-offs, so the V1b and V2 arms can be repeated on current physics
without a core re-run. Nothing has been started.

**Sizing confirmed against measured cost.** The 11 October stand-in ran 51.2 M descents in 3 h 11 min
at 8 threads, which is 1,791 µs of CPU per descent against run-i-dive's measured 1,179 µs — a cost
ratio of **1.52×**, not the 6× the flight time alone would suggest. The pre-onset cruise segment is
cheap because it carries no descent machinery. So at 12 threads:

| configuration | descents | CPU-hours | wall-hours |
|---|---|---|---|
| 16 children, as run-i-dive | 128.0 M | 63.7 | **5.3** |
| 8 children, as run I | 102.4 M | 50.9 | **4.2** |
| 4 children × 4 descents, 8 seeds × 4 strata | 51.2 M | 25.5 | **2.1** |

The module thread's own 3–5 h estimate is right.

**Run it before items 1 and 2, not after, and not combined.** Three reasons:

1. **It is the failed gate.** The onset-boundary statistic is 21.6 per cent against the contract's
   new 5 per cent threshold, and it is the only outstanding item that changes what the module can
   *conclude* rather than how precisely it concludes it.
2. **Rule 11 needs a "before".** Adding asymmetric thrust is a change to the model's reach, so the
   contract requires held-out log-evidence and impact median before and after. The 22:41 arm lands
   on exactly the population item 1 touches — 46.2 per cent of the deliberate family begins its
   descent with one engine running, and from a 22:41 start the single-engine phase is longer than
   from 00:11. Without the arm measured on unchanged physics, a later difference cannot be
   attributed between the checkpoint and the asymmetry.
3. **Running it twice is not waste.** The second run, after item 1, answers "how much does
   asymmetric thrust move the impact distribution?" — a question that would otherwise need its own
   experiment.

**Label it** as conditional on symmetric single-engine flight, which is the honest statement until
item 1 lands.

**What the run must emit, or it does not settle the thing it is for:**

- the **onset-boundary statistic per family**, under held-out weighting and under each 00:19 option,
  measured against the 22:41 boundary;
- the **support-truncation fraction** from `takeover_time` — currently a NaN column because the hook
  does not pass its result to `descend` (a core request). If that is still unlanded, say so and
  report the boundary statistic alone;
- the distribution of the per-trajectory onset-window length, since predicted exhaustion is now a
  per-trajectory quantity rather than the removed 00:17:30 anchor.

**The testable prediction.** The earlier 22:41 smoke on core run D gave ln BF (A against B) of about
+0.27, with evidence against deliberate onsets before 23:15 and weak evidence for later ones. If
that holds, the supported onset mass will concentrate at the **late** end of the window rather than
against the 22:41 boundary — which would mean 22:41 is a sufficient checkpoint and 21:41 is
unnecessary. If instead mass piles at 22:41, the run has told you to go to 21:41, and that is a
result rather than a failure.

---

## Smoke gates before any of the three runs

Yes — and the sequence matters, because three of these four cannot be substituted for each other.
Standing rule from `AGENTS.md`: **a smoke run is never evidence.**

1. **`make smoke H=end-of-flight`** — about a minute, code paths only. Catches a parse or API break,
   nothing else. Rebuild first: a stale binary fails immediately on an unknown field.
2. **The unit tests, including the new closed-form ones for item 1** — zero thrust asymmetry
   reproduces the current model to machine precision, one-engine straight flight balances
   `T · y_engine_m`, and the uncorrected yaw rate matches the analytic turn rate. These are the real
   check on item 1 and they are not smoke.
3. **The effective-sample-size measurement at the parent and child counts you intend to use** —
   §7 of the contract requires this *before* any end-of-flight run, and it is the gate that would
   have caught the both-00:19-burst collapse to 38.8 effective parents before a full sweep rather
   than after. For the 22:41 arm, measure it at both the 22:41 hand-off and at 00:11, and compare
   against what the filter achieves at 00:11. Choose the counts from the measurement, not from the
   illustrative values in `config.rs`.
4. **A reduced-scale 22:41 run** that reports the boundary statistic, the support-truncation
   fraction and — for any new aimed proposal component — test 6, the recovery of the uniform prior
   under the sampling weight alone. This gates the full run and is not evidence for any impact
   distribution, log-evidence or family share.

Gate 3 is the one most likely to be skipped and the most expensive to skip.

---

## Item 1 — asymmetric thrust in the point-mass model

**Why.** Measured on run-i-dive: 36.9 per cent of posterior weight has exactly one engine thrusting
at descent onset, 22.5 per cent of the fuel-exhaustion families fly a single-engine phase with a
median of 288 s and a 95th percentile of 1,113 s between takeover and the final flame-out, and
46.2 per cent of the deliberate family begins its descent with one engine running. All of it is
currently flown as a symmetric point mass: the module's envelope contains no yaw, rudder,
autopilot-response or thrust-asymmetry parameter, only `windmilling_per_engine`, a symmetric drag
increment. The core's `single_engine_*` parameters govern the core's own pre-00:11 phase, not this
stage.

**Scope.** `engine/hypotheses/end-of-flight/` only. `make scope H=end-of-flight` must pass. No core
crates, no `config/`, no `report/`. New parameters go in the module's own `run.toml`.

**What to add.** Three parameters and one state, in the existing
`(V, γ, h, ψ, m)` air-relative system — this does **not** need a smaller integration step, because
trim drag and an uncorrected yaw rate are slow effects:

1. **Engine moment arm** `y_engine_m`. From published 777-200ER geometry, which is measurable and
   citable — treat it as known, not sampled, and record the provenance in the `lib.rs` doc comment
   with the wing area and span.
2. **Trim-drag increment** as a function of thrust asymmetry — the drag penalty of holding a
   straight path with rudder and a small bank into the live engine. Sample a coefficient band; label
   it a modelling parameter with a declared sensitivity, as §9 of the contract requires for anything
   not traceable to a primary source.
3. **Yaw state: corrected or uncorrected.** Under autopilot or pilot control the path is held and
   the cost is the trim drag of (2). With no effective intervention the aircraft yaws and turns
   toward the dead engine, so `ψ` acquires a rate. This maps onto the existing control axis — do not
   add a family.

**Tests, all closed-form.** Straight-flight equilibrium with one engine inoperative: rudder and bank
balance `T·y_engine_m` and the resulting drag matches the analytic trim penalty. Zero asymmetry
reproduces the current model exactly, to machine precision — this is the regression test that keeps
the change inert where it should be. The uncorrected yaw rate matches the analytic turn rate for the
residual sideslip.

**Emit.** The first flame-out time as its own column beside `t_realised_flameout_s`, and the engine
count through the terminal trajectory rather than only at onset — deliverable 9 of the contract.
Note for whoever writes it: `t_realised_flameout_s` is the **final** flame-out despite the trait doc
calling it the first; fix the doc in the same change.

**Cost.** Full sweep goes from 3.5 to 4.2–5.2 wall-hours at 12 threads. One to two sessions.

---

## Item 2 — calibrate the existing phenomenological parameters against the ten Boeing traces

**Why.** This closes the §8 calibration gate on the uncontrolled arm, which is what currently
forbids quoting any impact energy, attitude, flight-path angle or energy-transfer duration as a
physical prediction. It is plan phase 2 applied directly to the fast model, **skipping phases 0 and
1 of the 6-DOF plan**: the reasoning is in the costing note, and it is that the traces are 1 Hz
position and altitude only, so a reduced parameter set that is observable beats 25–35 derivatives
that are not. The existing non-convergence (4 per cent misfit reduction) is an under-determination
symptom, not a tuning problem.

**Parameters to fit**, all already in the model:

- `spiral_doubling_s`, currently sampled 60–120 s. The published 747 figures the 6-DOF base would
  be rescaled from give 296 s at Mach 0.70 and 89 s at Mach 0.90, so the existing band already
  brackets the high-Mach case the Boeing dives sit in. This is the parameter that carries bank
  growth.
- `residual_bank_deg` (0–35°) and `residual_bank_left_probability` (0.8).
- `trim_cl_offset` (−0.08 to 0.08) with `trim_reference_at_loss = true`. The phugoid already matches
  at 78–86 s against Boeing's 82–87 s **only** when the module's own trim at loss of control is used
  rather than best-glide lift coefficient; keep that and fit around it.
- `windmilling_per_engine` (0–0.0015 under the standing ruling) and `rat_increment`
  (0.0001–0.0006).
- `spiral_divergent_weight` (0.5) — the mix of neutral phugoid glide and divergent spiral.

**Targets, per case, with tolerances to be set before fitting** — the contract's gate names the four
quantities and no numbers, and that must be fixed first: phugoid period, bank growth rate, time to
15,000 ft/min, and distance and time to impact. Add the chord after the 15,000 ft/min crossing, for
which a published comparison exists.

**Method requirements**, from the gaps the 6-DOF plan left open and which apply here too:

- **A discrepancy-aware likelihood.** The 1 Hz traces are a simulator export, so the residual is
  model error, not measurement noise; an independent Gaussian on position will be wildly
  overconfident given the autocorrelation. State the effective observation count, not the nominal
  one.
- **A parameter budget** fixed before fitting: how many free parameters against that effective
  count, with per-case initial conditions counted in.
- **Leave-one-out on all ten cases**, so each gets an out-of-sample prediction, with an honest
  pass or fail per case including any case not reproduced.
- The dive cases **3, 4, 5, 6 and 10** named explicitly — they are the uncontrolled-dive tests and
  the reason the gate exists. In those cases control is lost within 1–9 s of the first flame-out and
  altitude is held only 143–149 s.

**Write the limitation down.** All ten cases are uncontrolled. The piloted and deliberate families
carry 32 and 52 per cent of posterior weight and have no trace data of any kind, so this calibration
validates the uncontrolled arm and cannot validate the others. That belongs in the methods as a
declared limitation, not left to emerge from a missing figure.

**Cost.** A few CPU-hours for the fit, 53–164 CPU-hours with leave-one-out — 4 to 14 wall-hours at
12 threads. Above smoke scale, so under `lockf -k /tmp/.mh370-heavy.lock` at up to
`RAYON_NUM_THREADS=12`; build and test outside the lock at 2 threads and `cargo -j 4`, with
`CARGO_TARGET_DIR=target-eof` so a rebuild cannot disturb a run executing from `target/release`.
Two to three sessions.

---

## Sequencing

Item 0 first, on its own, on unchanged physics. Then items 1 and 2, which are
**independent and can run in parallel**: item 1 adds parameters item 2 does not
fit, and item 2 fits parameters item 1 does not touch. If run sequentially, item 2 first is the
better order, because it closes the gate that is currently blocking what may be reported.

**Do not start a full sweep on either.** The contract requires the onset-boundary gate and the
silent-exclusion review before a sweep, and the onset gate is currently failed at 21.6 per cent.
Item 1 and item 2 are development and calibration; the next full sweep is a separate decision and
is Pete's.

## Reference artifacts to carry into the module thread

| artifact | why |
|---|---|
| `end-of-flight.md` version 7 | the governing contract; the repo copy is version 4 |
| `eof-audit-2026-10-13.md` | what was measured and what is outstanding |
| `eof-audit-pushover-addendum.md` | the proposal-against-support distinction, and the prior-recovery test to repeat |
| `eof-audit-measurements.csv` | every figure quoted above, traceable |
| `eof-dynamics-options-costing.md` | why phases 0 and 1 are skipped, and the compute scaling |
| `eof-published-benchmarks.csv` | the calibration targets, with provenance strength per row |
