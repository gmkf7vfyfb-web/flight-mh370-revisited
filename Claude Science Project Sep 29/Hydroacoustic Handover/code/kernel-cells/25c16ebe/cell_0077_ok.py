wo = r"""# Work order — end-of-flight dynamics items 1 and 2

For the END_OF_FLIGHT_MODULE thread. Derived from the audit of 13 October 2026
(`eof-audit-2026-10-13.md`, `eof-audit-pushover-addendum.md`) and the costing
(`eof-dynamics-options-costing.md`). Governing contract: master prompt **version 7**
(`end-of-flight.md`), which must be in the repo at `threads/master-prompts/end-of-flight.md`
before this order is actioned — the repo copy is still version 4.

**Neither item can be started from the audit thread.** The engine source is not under any granted
path, and the Boeing traces (`ISO Sept 28 Status/inputs/end-of-flight/2018-08-19-eof-sims.zip`,
sha256 `e400ac73…`) are repo-resident and not reachable either. The clone is the first action.

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

The two items are **independent and can run in parallel**: item 1 adds parameters item 2 does not
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
"""
open("eof-work-order-items-1-2.md","w").write(wo)
print(len(wo))
