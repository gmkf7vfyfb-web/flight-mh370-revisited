# The flaperon's drift response: provenance and circularity (review item 17)

Ocean drift module, 9 October 2026, for the architecture session's ruling (morning rulings, item 5).

**Source read.** Griffin, Oke and Jones (2017), *The search for MH370 and ocean surface drift - Part
II*, CSIRO Oceans and Atmosphere, report EP172633, 13 April 2017. Primary text, read from the
project Google Drive copy (`CSIRO II mh370_ocean_driftii_final.pdf`, Drive id
`1S-WCMaRKt0lRlV0Uv3bfVSKZvEd8TjDf`, 2,007,478 bytes; the ATSB server refuses automated clients).
**Pages are the report's printed page numbers, read from its running footers** (corrected 9 October: the first version read them as headers and cited every Part II page one too low; see the correction at the end). The secondary source that
raised the question (an mh370search.com comment of January 2021) is not used as evidence.

## What Part II measured, and how

1. **Speed: measured.** A genuine Boeing 777 flaperon, cut down to match 9M-MRO's, was drifted at sea
   beside drogued and undrogued drifters. Its extra leeway speed above the undrogued drifters was
   about 10 cm/s (p. 10). The authors judge it "better described as a constant" than as a function
   of wind speed. They also say the fit "is not very tight", and that they could not replicate the
   high-wind observation because the weather was mostly calm (p. 10).
2. **Reference system: implicit.** Leeway in the field figure is defined as the difference from the
   drogued drifters (Fig. 2.3.1, p. 11). The relationship used to model the flaperon is drift speed =
   10 cm/s + 1.2% of wind (p. 11). In CSIRO's system, 1.2% of wind is the undrogued-item baseline that
   stands in for Stokes drift on BRAN currents (Part III, p. 6). **So "10 cm/s in excess of the Stokes
   drift" (p. 17) means in excess of 1.2% wind, not in excess of a wave-model Stokes field.** This
   confirms review error E1.
3. **Angle: measured as a range; the modelled value was chosen from two trial values.** The genuine
   flaperon drifted left of the wind with a field mean of 16° (p. 10). The conclusion gives the
   measured range as between 0 and 30° left (p. 17). The trajectories use trial values of 10° and
   20°, with 20° described as agreeing with Pengam's (2016) numerical predictions (p. 10).
4. **What the arrival test was.** With either angle, the most common simulated path passes close to
   Réunion, especially with 20° (p. 12). July 2015 is close to the most likely arrival time "for all
   potential crash sites from 40°S to 30.5°S" (p. 12; also p. iv and p. 17). The authors draw the
   consequence themselves: the arrival of a single item is "not a precise guide to the location of
   the crash" (p. 17).

## Is the flaperon response partly constituted by the answer?

- **Speed and angle range: no.** Both come from field trials against drifters, with no reference to
  any source location (pp. 10-11).
- **The secondary claim that the parameters were estimated by assuming a 40-30.5°S source arrived on
  time: not supported.** In the primary text, 40-30.5°S is the band over which the measured
  parameters were *found to be* consistent with the arrival (pp. iv, 12, 17). It was not a
  constraint used to fit them.
- **Residual dependence: two soft points, both declared.**
  - (a) The investigation was prompted by the earlier model's misfit for a 36-32°S source, whose
    trajectories passed north of Réunion and arrived late (p. 12). That shaped the question asked, not
    the values measured.
  - (b) Choosing 20° over 10° coincides with the better Réunion path (p. 12), although Pengam is
    given as the reason (p. 10).
  - Neither point favours a latitude: the arrival match is flat across 40-30.5°S (p. 12).

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
3. **E15 is resolved, not an error.** A wind-independent extra speed is what CSIRO fitted (p. 10).
   The prior code's fixed 0.10 m/s was faithful in form. Its error was the reference system (E1) and
   the fixed values (E2).
4. **The shared API cannot yet express this term.** `ObjectResponse` has `c_wind · R(angle) · U10`,
   which scales with wind speed. A constant-magnitude speed along the rotated downwind direction is
   not representable. That is requested from ocean transport today as
   `leeway_speed_mps` (constant magnitude, direction = downwind rotated by `leeway_angle_deg`).
5. **For the paper:** cite the Réunion arrival as consistent with the whole 30.5-40°S band, as CSIRO
   do. It is not a latitude constraint. That matches this project's own Davey reproduction, where one
   find moves the median by under 6 NM in every seed.

## Genuine flaperon or replica, and measurement or tuned assessment

*Added 9 October, for the architecture entry "the flaperon response has one owner - you". Pléiades
takes the number from here.*

**The ruled response (D-a) is the genuine flaperon, at sea. It is not the replica.**

- **Genuine (Part II).** A genuine Boeing 777 flaperon, cut down to match photographs of 9M-MRO's.
  CSIRO found "no discernible difference" between its waterline and 9M-MRO's (p. 2). It was drifted
  in North West Bay and Storm Bay on field days 11-13, in seven deployments of about an hour each,
  alongside one replica, three undrogued and three drogued buoys (p. 7). The results: extra leeway
  about 10 cm/s, constant with wind; leeway angle 16° left of downwind, range 0-30° (pp. 10, 17).
  **These are measurements**, not values tuned to a source.
- **Replica (Part I, as summarised in Part II).** Wood-and-steel replicas whose shape and flotation
  did not match 9M-MRO's flaperon (p. 1). Their leeway exceeded the undrogued drifters', especially in
  low wind, but stayed below Pengam's 3.3% of wind (p. 7). Their drift angle was "not clearly
  non-zero": mean 4°, excluding day-7 outliers (p. 10). Part I modelled this as a downwind extra
  leeway falling linearly from 10 cm/s in calm to zero at 10 m/s of wind (p. 12). CSIRO superseded it
  with the genuine-flaperon response.
- **What is a modelling choice rather than a measurement:**
  - the 10° and 20° trial angles, with 20° used in the trajectories (pp. 10, 12);
  - the 1.2% wind baseline, which is calibrated on undrogued drifters relative to the water (p. 7).
    In CSIRO's simulations it is applied to a model surface layer: BRAN2015's 0-5 m layer in the
    Part III figure (Part III, p. 6). **Part II names no ocean model.**

**For Pléiades.** If its test is meant to be of "CSIRO's measured flaperon response", the number to
use is the genuine-flaperon one above. The replica numbers belong to the superseded Part I model and
should be labelled as such if they are used at all.

## Correction, 9 October

The first version of this note read Part II's page numbers as running headers. The Part III PDF shows
the CSIRO template puts them in the **footers**, and the Part II text confirms it: "1 Introduction"
falls before the footer of page 1. **Every Part II page cited above was one too low and is
corrected**: 9→10, 10→11, 11→12, 16→17, iii→iv. Part III p. 6 was read from the PDF page by page
and is unchanged. Ruling D-a quotes the range as "stated on p. 16"; it is on **p. 17**.

## Part I read in primary form, 9 October

Part I (EP167888, project Drive copy; pages checked against the PDF footers) confirms the replica
summary above and adds three points:

- The replicas were **six life-size wood-and-steel flaperons built by ATSB** to Pengam (2016)'s
  waterline. Their trailing edge rode lower than the real part's, and they lacked Pengam's preferred
  extrados-down orientation (p. 4). The trials were in North West Bay, Hobart, in July and August 2016
  (p. 6).
- Relative to undrogued drifters, the replicas moved about 10 cm/s downwind in light wind, and within
  5 cm/s and ±10° of them in strong wind (p. 7).
- Part I's model is the linear taper: 10 cm/s at 0 m/s of wind, falling to 0 at 10 m/s, **downwind, no
  angle** (p. 9). Part II cites this as its starting assumption (Part II p. 12).

Consequences for drift: none for the primary response, which stays the ruled genuine-flaperon one
(Part II). The Part I taper is recorded as a possible labelled sensitivity ("Part I taper"). It needs
a wind-dependent extra-leeway speed that the shared API does not offer, so it is deferred and not
requested now.
