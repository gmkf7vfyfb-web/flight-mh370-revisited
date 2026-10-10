# Boeing engineering-simulator cases: what is known of each case's conditions

9 October 2026, End of Flight Module. This is step 2 of the simulator plan.

## Sources

- **ATSB, *MH370 - Search and debris examination update*, 2 November 2016, pp. 11–12** (the extract in
  `ISO Sept 28 Status/inputs/end-of-flight/2018-08-19-sim-extract.pdf`).
  - In April 2016 ATSB defined scenarios with "reasonable values" for speed, fuel, electrical configuration and
    altitude, along with the turbulence level.
  - The engineering simulator uses the same aerodynamic model as a Level D simulator, with the accident
    aircraft's firmware and software.
  - In one electrical configuration, the loss of one engine also lost the autopilot. The descents turned both
    clockwise and anticlockwise.
  - Some motion went **outside the simulation database**. The manufacturer advised that data beyond that point
    be treated with caution.
  - Fuel-tank dynamics, APU relight and engine relight are not modelled.
- **ATSB, *Flight Path Analysis Update*, 8 October 2014, PDF p. 12.** The manufacturer and operator simulator
  activities had the right engine run out of fuel, then the left engine flame out, with no control inputs. That
  produced a descending, spiralling left turn at low bank.
- **Iannello (2018).** Legal restrictions prevented release of the per-case details. The public files carry only
  time, X, Y and integer-foot altitude.

## Per case, measured from the traces

Measured by `engine/hypotheses/end-of-flight/sim/boeing_cases.py`. Ground speed equals true airspeed only if
the simulator had no wind, which is not stated.

| case | group | start altitude (ft) | ground speed, first minute (kt) | Mach if no wind | altitude held, s (first fall of 100 ft) | net turn | duration (s) | last altitude (ft) | start-to-end range (NM) | path length (NM) |
|---|---|---|---|---|---|---|---|---|---|---|
| 01 | glide | 40000 | 450 | 0.785 | 482 | left | 2503 | 535 | 102.9 | 202.8 |
| 02 | glide | 40000 | 448 | 0.781 | 467 | left | 2461 | 517 | 103.4 | 199.2 |
| 03 | spiral dive | 40000 | 450 | 0.784 | 148 | left | 577 | 653 | 36.2 | 69.1 |
| 04 | spiral dive | 40000 | 451 | 0.785 | 147 | right | 453 | 484 | 22.4 | 59.0 |
| 05 | late dive | 35000 | 424 | 0.736 | 854 | left | 1891 | 658 | 107.8 | 160.5 |
| 06 | spiral dive | 35000 | 425 | 0.737 | 143 | left | 384 | 742 | 27.6 | 48.8 |
| 07 | glide | 40000 | 447 | 0.779 | 481 | left | 2434 | 496 | 104.6 | 197.7 |
| 08 | glide | 35000 | 409 | 0.709 | 772 | left | 2234 | 480 | 73.7 | 178.0 |
| 09 | glide | 40000 | 452 | 0.788 | 490 | left | 2249 | 473 | 85.5 | 184.5 |
| 10 | spiral dive | 40000 | 449 | 0.782 | 149 | right | 473 | 1131 | 24.2 | 56.9 |

## Reading, and what becomes a nuisance parameter

- **The hold duration separates the groups.**
  - The spiral-dive cases (3, 4, 6, 10) hold altitude for 143–149 s.
  - The glides at FL400 (1, 2, 7, 9) hold for 467–490 s.
  - Cases 5 and 8 at FL350 hold for 772–854 s.
- **Working hypothesis, to be tested by the fit rather than assumed:**
  - t = 0 is the first (right-engine) flame-out.
  - In the dive cases the autopilot is lost with the first engine, and the remaining engine's asymmetric thrust
    starts the bank and the spiral.
  - In the glide cases the autopilot keeps holding until the second flame-out, after which the aircraft glides
    with phugoids.
  - If this holds, the simulator must model the single-engine phase, thrust-asymmetry compensation and the
    autopilot. The present module starts at dual flame-out.
- **Two cases turn right** (4 and 10). The other eight turn left.
- **Per-case nuisance parameters:**
  - initial speed and Mach, or wind;
  - gross weight, fuel and centre of gravity;
  - the time of the second flame-out;
  - the autopilot state after the first flame-out (the electrical configuration);
  - the post-flame-out control-law mode;
  - turbulence level;
  - for the dive cases, the time beyond which the motion left the simulator's database. Fit weight is reduced
    there.
