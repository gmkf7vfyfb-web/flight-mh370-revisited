# End of flight, deliverable 1 (first pass): free dynamics against the ten Boeing simulator cases

9 October 2026. **Calibration diagnostic, not evidence.**
- Script: `engine/hypotheses/end-of-flight/smoke/boeing_calibration.py`.
- Module traces: the ignored test `free_dynamics_traces_for_calibration` in `integrator.rs`, module code
  `2b60df4`.
- Numbers: `calibration.json`. Figure: `eof-boeing-calibration-v0.png` (both regenerated with the corrected trim).

## The data, and what may be done with it

- **The ten Boeing engineering-simulator exports**, `Case 01.csv` to `Case 10.csv`:
  - time, X, Y and integer-foot altitude at 1 Hz, nothing else;
  - archive `ISO Sept 28 Status/inputs/end-of-flight/2018-08-19-eof-sims.zip`, sha256
    `e400ac73478dff8698cd344a69d7969804f6adb0eb2121d5cacd3b58d63111db`, identical to the hash pinned
    by the archive's aerodynamics audit.
- **Licence:** shared publicly by Iannello with ATSB permission; no general downstream licence was
  located. So the files are **validation-only**: only summary statistics are used here, and nothing is
  fitted into the model's structure or redistributed.
- **Per-case conditions were withheld.** ATSB says speed, fuel, electrical configuration, altitude and
  turbulence were "selected" (*Search and debris examination update*, Nov 2016, pp. 11–12, per the
  archive ledger; the project extract carries folios 7–8).
- **Every run starts in powered level flight.** The two flame-outs appear as separate vertical-speed
  dips (case 1: 489 s and 1,088 s, with single-engine driftdown between). So durations and distances
  "from flame-out" are **not measured here**. I tried two detectors, a dip rule and an energy-rate rule,
  and neither was reliable without the case metadata.
- **Everything below is event-free**, and both sets are measured by the same code. The method uses
  1-s backward differences; a case is high-rate if it exceeds 15,000 ft/min down **and** 0.67 g down.
  Phugoid period is the median spacing of vertical-speed extrema (prominence ≥ 1,000 ft/min) before any
  15,000 ft/min crossing. Bank comes from the ground track as atan(Vω/g), in still air.
- **Check:** the method reproduces Iannello's published partition, cases 3, 4, 5, 6 and 10, and the
  published chord from the first 15,000 ft/min crossing to the last row: here 4.71–7.92 NM, published
  4.7–7.9 NM.

| case | high-rate | peak descent, ft/min | peak downward acceleration, g | chord after first 15,000 ft/min, NM | phugoid period, s | peak bank from track, deg |
|---|---|---|---|---|---|---|
| Case 01 | no | 4,800 | 0.34 | – | 85.5 | 11.6 |
| Case 02 | no | 6,300 | 0.34 | – | 85.5 | 12.1 |
| Case 03 | yes | 53,460 | 1.24 | 4.71 | 188.0 | 54.5 |
| Case 04 | yes | 33,600 | 0.87 | 6.71 | – | 60.2 |
| Case 05 | yes | 24,180 | 0.90 | 5.11 | 87.0 | 12.8 |
| Case 06 | yes | 43,380 | 1.21 | 7.92 | – | 57.4 |
| Case 07 | no | 4,920 | 0.31 | – | 85.0 | 11.4 |
| Case 08 | no | 7,140 | 0.34 | – | 82.0 | 13.8 |
| Case 09 | no | 6,900 | 0.31 | – | 83.0 | 13.8 |
| Case 10 | yes | 58,020 | 1.31 | 7.32 | – | 53.2 |

**The module traces:** 60 no-intervention, unpowered free-dynamics descents.
- Starts: 35,000 and 40,000 ft, TAS 240 m/s, 174 t, ISA, still air.
- Constant residual bank 0, 2, 5, 8, 12, 15, 20, 25, 30, 35°, across the prior U[0°, 35°].
- Trimmed C_L at (L/D)max, offset −0.08, 0 and +0.08, across the prior trim offset.

## Findings

*[Corrected after a fixture error: the first version of this note used C_L at (L/D)max as the free trim. The
module trims to the LEVEL C_L at the takeover state plus the offset (`profile.rs`, `Shape::FreeTrim`). Its
findings 2 and 3, "phugoid too short" and "phugoid too large", were artefacts of that error and are
withdrawn. The fixture now uses the module's own trim, code `free_dynamics_traces_for_calibration` after
`2b60df4`.]*

1. **The module has no high-rate class.**
   - None of the 60 traces is high-rate; Boeing has 5 of 10.
   - Module peaks reach 15,573 ft/min and 0.36 g, at trim offset −0.08. Boeing's high-rate cases reach
     24,000–58,000 ft/min and 0.87–1.31 g, ending 4.7–7.9 NM after the first 15,000 ft/min crossing.
   - In the 00:11 smoke impacts, `flame-out/none-thrusting/no-intervention` reaches 15,000 ft/min for
     0.6% of its weight.
   - **A constant bank cannot diverge.** Four of Boeing's five high-rate cases (3, 4, 6, 10) grow bank
     to 53–60°. Case 5 is high-rate at only 12.8° peak bank: a late dive after a long phugoid. The
     non-high-rate cases hold 11–14°. The module holds whatever bank it drew.
   - **But bank is not the whole cause;** see the addendum.
2. **The phugoid is consistent.** It runs 78–86 s against 82–87 s for Boeing's six non-high-rate cases,
   with the shortest periods at trim offset +0.08 and small bank.
3. **The amplitude is consistent at nominal trim.** Peak descent at offset 0 is 3,900–8,600 ft/min,
   against 4,800–7,100 for Boeing's glides. At offset −0.08 the module reaches 7,400–15,600 ft/min.

## What this implies, and what is not yet settled

- **Proposed module change (within the brief's calibration mandate; not yet made):**
  - replace the constant residual bank with a bank that evolves as a spiral mode,
    φ(t) = φ0·exp(t/τ_s), capped where the simulator database ends;
  - τ_s is a sampled uncertain parameter whose range brackets Boeing's neutral behaviour (glides,
    τ_s → ∞) and its divergent behaviour (dives, bank doubling in roughly 60–90 s);
  - re-run this comparison as the acceptance test.
- **Ruled by Pete (9 Oct): equal prior weight on divergent and neutral spirals,** a stated indifference prior, with sensitivity runs at 25/75 and 75/25. The reasoning below is why it was his call.
- **Background to the ruling:** ATSB chose the ten
  scenarios, so 5 of 10 is not a frequency. This weight moves impact mass toward the 7th arc, since
  dives end within about 8 NM of their 15,000 ft/min crossing. It is a scientific choice the brief does
  not make, so it goes to Pete with options before any headline uses it.
- **Two Boeing statements are not reproduced from these ten files:**
  - "rearward approximately 21 NM": no case travels behind its position 120 s into the record;
  - "up to about 20 minutes airborne after the second flame-out": not measurable without the
    flame-out times.
  - Both may refer to the December 2015 set.


## Addendum: the spiral mode, built and tested, FAILS acceptance (not enabled)

- **Built:** module `envelope.spiral_divergent_weight`, `spiral_doubling_s`, `spiral_bank_cap_deg` and
  `spiral_bank_floor_deg`.
  - A divergent descent doubles its bank every T₂ from the start of free flight, to a 60° cap.
  - T₂ ~ U[60, 120] s brackets the Boeing doubling times of 82–88 s. Those come from the bank ratio
    between 60 and 180 s in cases 3, 4, 6 and 10, which does not depend on where the flame-out falls.
  - At weight 0, which is the default, the original impact columns are bit-identical (00:11, seed 1,
    N = 4).
- **Tested:** 54 divergent fixture traces (`calibration-with-spiral.json`, the `-div` traces).
  - Starts: 35,000 and 40,000 ft; drawn bank 2, 10, 20°; T₂ 60, 85, 120 s; trim offset −0.08, 0, +0.08.
  - Result: **0 of 54 high-rate.**
  - Peak descent 6,900–17,100 ft/min and at most 0.28 g, against Boeing's 24,000–58,000 ft/min and
    0.87–1.31 g. Durations of 4.9–14.4 min and peak bank of 63–65° are in Boeing's range.
- **Why:** peak Mach in these traces is 0.81–0.94, median 0.85.
  - Boeing's dives at up to 58,000 ft/min imply about M0.92–1.0 in thick air.
  - The module's fixed-C_L free dynamics pitch up as speed builds, and the Lock drag rise above the
    M0.87 crest holds the speed near the crest.
  - This is exactly the region the brief labels **extrapolated** (drag rise and pitch above M0.87, NASA
    CRM data not in this tree). Boeing's own simulator left its database there.
- **Consequence:**
  - Pete's 50/50 ruling is recorded in `run.toml` comments, but the weight stays **0** until a model
    passes acceptance. A spiral that cannot reach the dive class would move impact mass without
    reproducing the behaviour it stands for.
  - **Next:** sweep the two declared extrapolated parameters, the Mach-tuck shift `cl_shift_per_mach`
    and the drag-rise coefficient `k_w`, within ranges that can be defended. Then report whether the
    high-rate class is reachable at all in a point-mass model. If it is not, the dive class has to be
    represented as a declared kinematic family (Boeing's 4.7–7.9 NM chord) rather than as physics; that
    question goes to the architect.

## Addendum 2 (05:31 UTC): what it takes to reach Boeing's dives in this model

Pete, 9 Oct: the Boeing runs were tests of **uncontrolled dives**, so calibration against cases 3, 4, 5, 6
and 10 comes first. Until it is done, every impact result covers only the stable-glide regime, and must
say the dive class is absent.

**Sweep** (`calibration-sweep-cap-tuck-kw.json`, 432 divergent traces, measured as above):
- the divergent-spiral bank cap at 60, 75, 90 and 120°;
- the two extrapolated parameters, Mach tuck `tuck_cl_per_mach` at 0, 0.3, 0.6 and wave drag
  `wave_drag_coefficient` at 10, 20, 40;
- doubling time 85 s; drawn bank 5 and 15°; three trims; two altitudes.

| bank cap | high-rate | peak descent, ft/min | peak downward g | peak bank read from the track | chord after 15,000 ft/min |
|---|---|---|---|---|---|
| 60° | 0 / 108 | 12,600–12,700 | 0.25 | 63° | – |
| 75° | 0 / 108 | 25,000–27,200 | 0.32–0.35 | 77–78° | – |
| 90° | 99 / 108 | 56,400–58,600 | 0.78–0.80 | 78–80° | 1.0–2.7 NM, all 198 high-rate traces |
| 120° | 99 / 108 | 65,200–67,700 | 1.03–1.10 | 78–80° | (same pool) |
| **Boeing, cases 3, 4, 6, 10** | **4 / 4** | **33,500–58,000** | **0.87–1.31** | **53–60°** | **4.7–7.9 NM** |

**Findings:**
1. **The bank cap governs; the extrapolated parameters do not.** Mach tuck and wave drag move the peak
   descent by under 10% at every cap.
2. **The rates come only with too much bank.** The module reaches Boeing's descent rates only by banking
   to about 90°, which reads as 78–80° on the track. Boeing dives at a track-read 53–60°, and the
   estimator is consistent: a module cap of 60° reads 63°. My guess that the track formula under-reads
   Boeing's bank is therefore wrong.
3. **And the dives are about three times too short.** The chord after 15,000 ft/min is 1.0–2.7 NM against
   4.7–7.9 NM. Boeing's vertical-speed traces swing from about +20,000 to −58,000 ft/min, which is pitch
   dynamics: the aircraft unloads and pulls up again. A fixed-C_L point mass cannot represent that.
4. **Conclusion: the present free-dynamics model cannot reproduce Boeing's uncontrolled dives
   consistently, for any setting of its declared parameters.** That is a negative result, kept: the
   spiral flag stays at 0, and the fixture and sweep stay in the tree.

**Options, sent to the architect for a ruling:**
- (a) Elevator-fixed longitudinal pitch dynamics: angle of attack and pitching moment with Mach, a
  3-DOF longitudinal model. Physically right, but the B777 pitching-moment data are not public, so the
  parameters would be assumed and swept. A larger build.
- (b) A declared empirical dive family, parameterised only from **published** values: Iannello's
  4.7–7.9 NM after 15,000 ft/min, ATSB's "within 15 NM of the arc", and the published high-rate
  thresholds. It is flagged as empirical, not physics; the simulator files themselves stay
  validation-only.
- (c) Leave the dive class out, and report every impact result as conditional on the non-dive regime,
  with ATSB's published 15 NM statement alongside.
- **Recommended: (b) now, so the dive class enters at all; (a) as later work; (c)'s disclosure until (b)
  lands.**
