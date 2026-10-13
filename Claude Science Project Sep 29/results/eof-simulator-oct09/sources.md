# 6-DOF simulator: aerodynamic, inertia and control-law sources

9 October 2026, End of Flight Module. This is step 3 of the simulator plan.

## Standing constraint

The archive's 777 audit (`Archive ISO Pre Sept 28/.../b777-end-of-flight-aerodynamics/README.md`) found no
public, redistributable model that spans the post-flame-out envelope: `NO_PUBLIC_REDISTRIBUTABLE_MODEL_SPANS_REQUIRED_ENVELOPE`.

- That audit rejected silent cross-aircraft transfers.
- **Pete's ruling of 9 Oct changes the logic, not the finding.** The Boeing traces may now be fitted in full.
  - A public large-transport model therefore supplies the **structure and the starting priors only**.
  - Every derivative that shapes the outcome is a fitted multiplier with a stated prior.
  - The methods must say this in these terms.

## Base airframe: Boeing 747, NASA CR-2144 Section IX

- **Source.** Heffley and Jewell (1972), NTRS 19730003312, US Government work, public use permitted.
- **Transcribed** to `engine/hypotheses/end-of-flight/sim/cr2144_747.py` from page images:
  - Table IX-3, mass, inertia and flight conditions (p. 229);
  - Table IX-4, longitudinal dimensional derivatives in body axes (p. 230);
  - Table IX-8, lateral-directional derivatives (p. 234);
  - geometry from Fig. IX-2 (p. 213).
- **Ten flight conditions**, including 40,000 ft at Mach 0.70, 0.80 and 0.90.
- **The transcription is verified against independently printed values.**
  - Rebuilding the phugoid and short-period roots from Table IX-4 reproduces Table IX-5's printed factors at all
    ten conditions, to within rounding. The largest gap is the phugoid damping at condition 7: 0.302 against
    0.323.
  - Rebuilding the spiral and roll roots and the Dutch roll from Table IX-8 reproduces Table IX-9 at all ten.
  - Three misreads (one sign, two digits) were found by this check and corrected.
- **A finding the fit can use:** the 747's spiral mode is divergent at 40,000 ft.
  - At M 0.70, 1/T = −0.00234 s⁻¹, a doubling time of 296 s.
  - At M 0.90, 1/T = −0.00777 s⁻¹, a doubling time of 89 s.
  - It is convergent at M 0.80.
  - Boeing's dive cases show bank doubling in 82–88 s.

## Transfer to the 777-200ER (stated, then fitted)

- **Geometry.** S = 427.8 m² and b = 60.93 m, as in `run.toml`.
  - The mean aerodynamic chord is estimated from the planform. **The primary-source ID for these values is still
    an open ledger item** (TCDS or ACAPS).
- **Inertias.** The 747's non-dimensional radii of gyration are carried over to the 777's mass and dimensions.
  - Multipliers on Ix, Iy and Iz are uncertain, with a prior of ±25%.
- **Derivatives.** The non-dimensional derivatives are recovered from Table IX-4 and Table IX-8 with Table IX-3's
  q, S, b, c̄, m and I, then scheduled in Mach at 40,000 ft and 20,000 ft.
- **Fitted multipliers** carry the parts that decide the outcome:
  - spiral stability: Clβ, Cnβ, Clr, Cnr;
  - Mach tuck: dCm/dM above M_cc;
  - pitch stiffness and damping: Cmα, Cmq;
  - transonic drag.
- **Beyond M 0.90, the limit of the table, every value is extrapolated and labelled as such.** The prior work
  found the dive cases at Mach 0.97–1.04.

## Thrust, drag and the engine-out phase

- Windmilling and RAT drag follow the module's glide calibration. Pete is still deciding the band.
- **Single-engine phase.** In the dive cases the second engine appears still to run after control is lost. The
  6-DOF therefore carries per-engine thrust at the engine's lateral arm, a fitted value of about 9.6 m.
  - Thrust follows the module's Trent 892 model, sea-level static 415,450 N.

## Control laws (a fitted or tested hypothesis, not an assertion)

- **No authorised primary source for the 777's control laws has been located in reach.**
  - The CRC *Avionics Handbook* chapter on 777 fly-by-wire was found only on a third-party mirror, so it is
    neither used nor cited.
  - FCOM material circulates only in unauthorised copies and is never cited.
- **The two candidate laws:**
  - a normal-mode-like pitch law with speed stability (C*U-like), with or without bank-angle protection;
  - a stick-fixed bare airframe with fixed trim.
- **Prior work.** The ISO snapshot's end-of-flight module
  (`ISO Sept 28 Status/code/branch-diffs/hypothesis__end-of-flight.patch`) found:
  - the long runs need the speed-stable law, because a stick-fixed phugoid would be 58 s against 81–86 s;
  - the short runs look stick-fixed.
- **ATSB 2016 states that some motion left the simulator's database.** Those trace segments are down-weighted in
  the fit, not discarded.

## Reused from prior work (credited)

From `prepare/boeing_runs.py` in the ISO snapshot:
- **the simulator-wind fit:** circle fits per loop, from 246°, 23.5 kt at sea level, +0.79 kt per 1,000 ft up to
  25,000 ft;
- **the per-run event timeline:** first flame-out, onset of uncontrolled flight, second flame-out.

Both are ported to `sim/` and re-run, not copied as numbers.
