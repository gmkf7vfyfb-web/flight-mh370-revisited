# End of flight: the single-engine phase from the right engine's flame-out, design (10 Oct 2026, overnight item 3)

**DESIGN ONLY; no smoke run yet.** Architecture ~23:55 UTC 9 Oct and ~02:25 UTC 10 Oct (Pete's C-7 decision (b)).

## What is already there

The 6-DOF reference simulator (`hypotheses/end-of-flight/sim/sixdof.py`) already flies:
- **two engines** at y = +/- `y_eng` with separate flame-out times `t1` (right) and `t2` (left);
- **thrust asymmetry**, with rudder compensation (TAC) active under the autopilot and, after the loss of control, stick-fixed;
- the **autopilot laws** fitted to the ten Boeing engineering-simulator cases.

Those cases start at the first flame-out. In the glide cases the autopilot is kept through the first flame-out and lost at the second, 790-1,075 s later.
So the Boeing set already contains a single-engine phase, and the joint fit (finished 00:35 UTC, not yet converged) includes it.

## What changes for the two-tank hand-off (core (b), `fuel.tanks = 2`)

1. **Hand-off fields.** Core passes both pools and both realised exhaustion times, NaN until each runs dry. End of flight predicts forward from the
   pools:
   - right dry first (R:L burn ~ 1.021, L - R ~ +221 kg at 18:01:49);
   - then the left burns at the `grid_inop` live-engine flow.

   This gives t1 and t2 per parent. Hand-off rows with a stopped engine are accepted, but the one-engine phase is modelled **only when the first
   flame-out comes after 00:11** (OVERNIGHT §3, core item 2).
2. **Point-mass model (sweep).** A new phase between the two flame-outs:
   - autopilot engaged, lateral mode unchanged;
   - the drift-down follows the fuel session's one-engine model (`results/fuel-model/one-engine.md`, ~05:30 UTC 10 Oct, PROVISIONAL-OVERNIGHT),
     not a constant rate from flame-out:
     - altitude held while the speed decays to the drift-down speed (2-7 min at 175 t);
     - then 350-830 ft/min, tapering to zero at the ceiling (FL290 LRC-INOP at 175 t, about -2 FL for the ISA deviation at 00:11).

     In a 3-14 min single-engine phase this loses only ~0-700 ft from FL350 (~3,000-4,500 ft from FL400), and holds altitude from FL300 or
     below. Core's C-7(a) constant U(300, 1,000) ft/min would lose 2,250-7,500 ft over 7.5 min from FL350. End of flight therefore reads
     `one-engine-v1.json` when it lands on the branch; until then, a parametric hold-then-taper with those bands;
   - the live engine at maximum continuous thrust, burning `grid_inop`;
   - the residual yaw and turn as a drawn bank, its range taken from the 6-DOF single-engine ensemble (still to be measured; Boeing case 01 reaches 11.6 deg maximum bank over the whole case).

   The second flame-out then hands over to the existing descent families.
3. **6-DOF reference.** Initialise at t1 with both pools; t2 from the left pool at `grid_inop`; autopilot law per the fitted cases.
   - Ensemble over (t2 - t1), weight, the altitude at t1 and the autopilot mode.
   - The fast model's single-engine phase is fitted to this ensemble, as for the rest of the descent.
4. **The log-on.** The APU log-on follows the **second** flame-out. The `+silent` constraint and the fuel-exhaustion lag use t2, and the 00:19:29 lag
   likelihood moves to t2. Right flame-outs before 00:19 with the left running keep the SDU powered on the left generator, so no log-on is predicted.

## Smoke plan (next, at 2 threads, after the V2-broad runs)

- A 6-DOF from a representative 00:11 state with t1 = 0 and t2 in {600, 900} s.
- Compare against Boeing cases 1-2: the altitude lost between flame-outs, the speed decay, bank and heading change.
- Then the point-mass phase against the same, and report the impact displacement against the single-pool baseline.
