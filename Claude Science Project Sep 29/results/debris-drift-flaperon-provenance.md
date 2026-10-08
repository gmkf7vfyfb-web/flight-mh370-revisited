# The flaperon's drift response: provenance and circularity (review item 17)

Ocean drift module, 9 October 2026, for the architecture session's ruling (morning rulings, item 5).

**Source read.** Griffin, Oke and Jones (2017), *The search for MH370 and ocean surface drift - Part
II*, CSIRO Oceans and Atmosphere, report EP172633, 13 April 2017. Primary text, read from the
project Google Drive copy (`CSIRO II mh370_ocean_driftii_final.pdf`, Drive id
`1S-WCMaRKt0lRlV0Uv3bfVSKZvEd8TjDf`, 2,007,478 bytes; the ATSB server refuses automated clients).
**Pages are the report's printed page numbers from its running headers.** The secondary source that
raised the question (an mh370search.com comment of January 2021) is not used as evidence.

## What Part II measured, and how

1. **Speed: measured.** A genuine Boeing 777 flaperon, cut down to match 9M-MRO's, was drifted at sea
   beside drogued and undrogued drifters. Its extra leeway speed above the undrogued drifters was
   about 10 cm/s (p. 9). The authors judge it "better described as a constant" than as a function
   of wind speed. They also say the fit "is not very tight", and that they could not replicate the
   high-wind observation because the weather was mostly calm (p. 9).
2. **Reference system: implicit.** Leeway in the field figure is defined as the difference from the
   drogued drifters (Fig. 2.3.1, p. 10). The relationship used to model the flaperon is drift speed =
   10 cm/s + 1.2% of wind (p. 10). In CSIRO's system, 1.2% of wind is the undrogued-item baseline that
   stands in for Stokes drift on BRAN currents (Part III, p. 6). **So "10 cm/s in excess of the Stokes
   drift" (p. 16) means in excess of 1.2% wind, not in excess of a wave-model Stokes field.** This
   confirms review error E1.
3. **Angle: measured as a range; the modelled value was chosen from two trial values.** The genuine
   flaperon drifted left of the wind with a field mean of 16° (p. 9). The conclusion gives the
   measured range as between 0 and 30° left (p. 16). The trajectories use trial values of 10° and
   20°, with 20° described as agreeing with Pengam's (2016) numerical predictions (p. 9).
4. **What the arrival test was.** With either angle, the most common simulated path passes close to
   Réunion, especially with 20° (p. 11). July 2015 is close to the most likely arrival time "for all
   potential crash sites from 40°S to 30.5°S" (p. 11; also p. iii and p. 16). The authors draw the
   consequence themselves: the arrival of a single item is "not a precise guide to the location of
   the crash" (p. 16).

## Is the flaperon response partly constituted by the answer?

- **Speed and angle range: no.** Both come from field trials against drifters, with no reference to
  any source location (pp. 9-10).
- **The secondary claim that the parameters were estimated by assuming a 40-30.5°S source arrived on
  time: not supported.** In the primary text, 40-30.5°S is the band over which the measured
  parameters were *found to be* consistent with the arrival (pp. iii, 11, 16). It was not a
  constraint used to fit them.
- **Residual dependence: two soft points, both declared.**
  - (a) The investigation was prompted by the earlier model's misfit for a 36-32°S source, whose
    trajectories passed north of Réunion and arrived late (p. 11). That shaped the question asked, not
    the values measured.
  - (b) Choosing 20° over 10° coincides with the better Réunion path (p. 11), although Pengam is
    given as the reason (p. 9).
  - Neither point favours a latitude: the arrival match is flat across 40-30.5°S (p. 11).

## Proposed ruling and its consequences for drift

1. **Treat the flaperon's speed and angle as measurements, not as answer-dependent.** The angle enters
   as the measured range, not as the selected 20°: θ ~ U(0°, 30°) left of downwind, or N(16°, 8²)
   truncated to [0°, 30°]. Either replaces the review's §4.1 prior N(18°, 4²), which was too narrow
   for the evidence. The speed enters as c0 ~ N(0.10, 0.03²) m/s truncated at 0, as in the review;
   the "not very tight" fit supports the width.
2. **Use them only in the system they were measured in.** That system is the implicit form: current +
   1.2% wind + a constant 10 cm/s at θ left of downwind, with no wave-model Stokes. With an explicit
   Stokes field (WAVERYS), the excess has no measured counterpart. It must be refitted, for example by
   undrogued-drifter replay in that system, or carried as an unmeasured residual with a wide prior.
   It must not be transplanted (E1).
3. **E15 is resolved, not an error.** A wind-independent extra speed is what CSIRO fitted (p. 9).
   The prior code's fixed 0.10 m/s was faithful in form. Its error was the reference system (E1) and
   the fixed values (E2).
4. **The shared API cannot yet express this term.** `ObjectResponse` has `c_wind · R(angle) · U10`,
   which scales with wind speed. A constant-magnitude speed along the rotated downwind direction is
   not representable. That is requested from ocean transport today as
   `leeway_speed_mps` (constant magnitude, direction = downwind rotated by `leeway_angle_deg`).
5. **For the paper:** cite the Réunion arrival as consistent with the whole 30.5-40°S band, as CSIRO
   do. It is not a latitude constraint. That matches this project's own Davey reproduction, where one
   find moves the median by under 6 NM in every seed.
