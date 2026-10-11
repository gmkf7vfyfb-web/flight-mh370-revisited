# 6-DOF refit with the 10 Oct objective: stationary, but the calibration gate FAILS (end of flight, 11 Oct 2026, ~02:35 UTC)

**NEGATIVE RESULT. The 6-DOF model is NOT calibrated and must not enter any sweep.** Kept behind its flags (nothing deleted).

Run: `runs/boeing/fit-oct10` (`sim/run_refit_oct10.sh`), 22:21:49 to 01:36:01 UTC under the heavy lock, 10 workers, 3 rounds, initialised from
fit-oct09. Objective (results/eof-diagnostic-smokes-oct10): altitude-error growth 0.5, vertical-speed s.d. 1,500 ft/min, mass box
172-178 t, per-case least squares, shared stage least squares (max 400 evaluations). Case-by-case run afterwards (deferred by the
wrapper while run C waited; 5 s at 1 thread). Files: `state.json`, `case-by-case.json`.

## Convergence
- Shared stage: the objective falls 549,932 → 548,205 in round 0, then by 2 in 540,000 per round. **Stationary.** (The jump from the 9 Oct
  total, 308,639, is the change of objective, not a worsening.)
- Shared parameters moved only in round 0: m_Clb 1.29, m_Cnb 1.29, m_Clr 0.91, m_Cnr 0.94, m_Cma 0.98, m_Cmq 0.93, kw 20.96, Mcc 0.869,
  u_stiff 1.23, Cm_bias −0.0012. Before (9 Oct) every multiplier was 1.0: the 10 Oct optimiser change did make the shared stage move.

## Case by case (Boeing / model)

| case | regime | peak descent, ft/min | peak g (unloading proxy) | high-rate end | Holland H2 8-s windows | H1 windows |
|---|---|---|---|---|---|---|
| 1 | long | 4,800 / 3,163 | 0.34 / 0.04 | no / no | 0 / 0 | 0 / 0 |
| 2 | long | 6,300 / 3,179 | 0.34 / 0.04 | no / no | 0 / 0 | 0 / 0 |
| 3 | short | 53,460 / 59,414 | 1.24 / 0.72 | yes / yes | 1 / 0 | 9 / 8 |
| 4 | short | 33,600 / 24,073 | 0.87 / 0.29 | yes / **no** | 2 / 0 | 14 / 8 |
| 5 | long | 24,180 / 3,074 | 0.90 / 0.04 | yes / **no** | 3 / 0 | 15 / 0 |
| 6 | short | 43,380 / 55,568 | 1.21 / 0.68 | yes / yes | 0 / 0 | 11 / 8 |
| 7 | long | 4,920 / 2,696 | 0.31 / 0.05 | no / no | 0 / 0 | 0 / 0 |
| 8 | long | 7,140 / 3,544 | 0.34 / 0.05 | no / no | 0 / 0 | 0 / 0 |
| 9 | long | 6,900 / 2,979 | 0.31 / 0.04 | no / no | 0 / 0 | 0 / 0 |
| 10 | short | 58,020 / 27,261 | 1.31 / 0.29 | yes / **no** | 0 / 0 | 9 / 8 |

## Verdict
- **Fails the gate on the same three points as 9 Oct:** the dives of cases 4, 5 and 10 are missed, the glide phugoids are damped
  (peak g 0.04-0.05 against Boeing's 0.31-0.34), and no case reproduces an H2 window (Boeing: 6 windows in cases 3, 4 and 5).
- End times and distances are matched to within about 10-20 % in most cases, so the trajectory-error objective is satisfied while the
  dynamics that matter for the 00:19 bursts are not. **The objective, not the optimiser, is now the limit**: it is insensitive to the
  phugoid and to the dive onset (10 Oct diagnosis: tripling the phugoid changes the NLL by 5 in 38,426).

## Next (proposal; module-internal)
- Replace the trajectory-error objective by Boeing **summary statistics as acceptance targets** (architecture push-over study, section 6):
  peak descent rate, peak unloading, high-rate end yes/no, phugoid period and amplitude in the glides, 8-s window counts, end time and
  distance; fit by simulated likelihood over these features, then leave-one-out.
- Add the Boeing system sequence to the 6-DOF runs (TAC flag, autopilot loss at the first or second flame-out, residual rudder): cases 4
  and 10 chose the TAC flag, and are two of the three missed dives.
- The point-mass model in the sweeps is unchanged; the reach-gap label stays.

## COVERAGE
(a) Feasible set: Boeing's 10 no-input cases. (b) Model reach: dives in 3 of 6 high-rate cases and no glide phugoid at Boeing's
amplitude: gaps OPEN. (c) Not a sampling question. Bounds: mass 172-178 t (box), multipliers unbounded in the shared stage.

- End of flight
