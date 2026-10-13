# End-of-flight 6-DOF simulator, checked against Boeing's ten cases

9 October 2026, End of Flight Module. **IN PROGRESS.** Pete's task (~17:30 UTC): a simulator that checks against
Boeing.

## Rulings

- The ten Boeing traces may be fitted as full traces. This is Pete's licence judgement; the files are not
  redistributed.
- The architecture is a 6-DOF reference simulator plus a fast in-sweep model fitted to it.
- Running the full 6-DOF in the sweep is to be revisited once these results are in.

## Done

- `case-conditions.md` and `sources.md` cover phase 1.
- **Simulator** (`engine/hypotheses/end-of-flight/sim/`):
  - numba RK4 rigid body with quaternion attitude and Ixz;
  - ISA and the simulator's wind;
  - lift and drag from the module's Boeing-calibrated polar;
  - moments from the CR-2144 747 derivatives, recovered in stability axes and scheduled in Mach and altitude by
    cubic Hermite interpolation, with the data's own Cm_M and CL_M node slopes, extrapolated beyond M 0.90 and
    labelled;
  - per-engine thrust at its lateral arm;
  - the autopilot (altitude hold, then speed-floor driftdown; heading hold; autothrottle; rudder compensation of
    thrust asymmetry; yaw damper);
  - after the loss, a normal-like (C*U-like) law or a stick-fixed law.
- **Verification** (`sim/test_sim.py`, 4 pass). The 747 flown in the 6-DOF reproduces CR-2144's printed modes:
  - spiral, roll and Dutch roll at six conditions, including the divergent spirals at 40,000 ft;
  - the short period within 4%;
  - the phugoid within 6% at the interior conditions.
  - The two tuck-onset conditions are disclosed: the phugoid is 0.042 against 0.031 at M 0.90 / 40,000 ft, and
    the model is near-unstable as the data is at M 0.80 / 20,000 ft.
  - Energy is conserved without drag or thrust.
- **Event timeline and simulator wind.** Ported from the ISO snapshot's `prepare/boeing_runs.py` (credited) and
  re-run; it reproduces that work's targets exactly.

## Pilot (per-case parameters only, shared physics at defaults)

Figure: `pilot-overlay-case01-case03.png`.

- **Case 01 (glide, normal-like law).**
  - Reproduced: the driftdown, the glide slope and the endurance (sea at 2,511 s against Boeing's 2,503 s).
  - Not yet reproduced: Boeing's *growing* phugoid (the model damps out), and the bank (the model −31°, Boeing
    −10° to −12°).
- **Case 03 (dive, stick-fixed).**
  - Reproduced: the first dive's timing, about 450 s.
  - Not yet reproduced: the bank (the model over-banks to 105°, Boeing about 55°), so the model cannot pull out.
    Boeing's zoom back up to 17,000 ft is therefore missing.
- **Several per-case parameters sit on their bounds.** They are standing in for shared physics: lateral stability
  and damping, and the normal law's lag and stiffness. Those are what the joint fit frees.

## Queued (behind the heavy lock, from 18:31 UTC)

`sim/run_fit.sh`: three alternating rounds of the joint fit, then ten leave-one-out refits.

- In each refit the shared physics is fitted without one case. That case's own timings, mass and trim offsets are
  then refitted under that physics, and the result is its prediction.
- The refits start from the full-fit state.
- Outputs: `engine/runs/boeing/fit-oct09/{full,loo-caseNN}/state.json`.
