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
   - **Cause: a constant bank cannot diverge.** Boeing's dives grow bank to 53–60°; its glides hold
     11–14°. The module holds whatever bank it drew.
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
