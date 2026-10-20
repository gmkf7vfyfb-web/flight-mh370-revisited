# MH370 received-power graphics: option index

This is a selection index for the visual storyboard. A gold star in the PDF marks the initial recommended shortlist.

The MH371 phase values are data-anchored. Other thumbnail lobes, attitude cases and posterior shapes are schematic and will be regenerated from the full model after figure selection.

## Geometry

### 01. Perspective geometry triad ★

Toward, broadside and away at low satellite elevation, with the side-mounted arrays called out.

Best use: Opening figure; immediate intuition.  Status: EXPLAIN + MODEL.

### 02. Rotate the aircraft, hold the satellite fixed

Three headings at one ground point isolate why heading—not position alone—changes antenna gain.

Best use: Opening alternative / animation.  Status: EXPLAIN.

### 03. Aircraft-space coordinate frame

Defines relative azimuth and elevation, body axes, attitude and the satellite line-of-sight vector.

Best use: Technical inset beside equations.  Status: EXPLAIN + DEFINITIONS.

### 04. Same map position, different received power

A plan-view counterexample: identical aircraft and satellite positions, but different headings and gains.

Best use: General-reader bridge.  Status: EXPLAIN.

### 05. Port/starboard antenna hand-off

Shows the two canted side arrays and which panel supplies the larger gain as the look direction moves.

Best use: Hardware/geometry explanation.  Status: EXPLAIN + MODEL.

### 06. Horizon compass of strong and weak sectors

A top-down coverage ring makes the low-elevation nose/tail weakness visible without a 3-D surface.

Best use: Compact main-text alternative.  Status: MODEL.

## Gain

### 07. Twin gain lobes mounted on the airframe

An aircraft carries the two directional gain volumes, connecting the side-mounted hardware to the pattern.

Best use: Hero alternative / graphical abstract.  Status: EXPLAIN + MODEL.

### 08. 3-D gain hemisphere ★

A colour-coded upper-hemisphere surface shows broadside maxima and low-elevation nose/tail valleys.

Best use: Primary gain-pattern figure.  Status: MODEL.

### 09. Polar slices at several elevations

Azimuthal gain curves at 0°, 15°, 30° and 45° elevation improve the dissertation's two-slice plot.

Best use: Quantitative main or supplement.  Status: MODEL + DATA.

### 10. Elevation–azimuth gain heat map

A rectangular aircraft-space map is easiest for readers to query and for particles to interpolate.

Best use: Methods figure / model validation.  Status: MODEL + DATA.

### 11. Beam steering and scan loss

A three-step diagram follows the beam from boresight toward the array edge as peak gain falls.

Best use: Phased-array explainer.  Status: EXPLAIN.

### 12. Boresight-to-horizon gain profile

A single annotated curve turns the 3-D pattern into the one-dimensional quantity used in the link budget.

Best use: Compact quantitative inset.  Status: MODEL + DATA.

## Attitude

### 13. Pitch–bank–yaw coverage matrix ★

Small multiples show how the same spacecraft direction moves across the gain map under attitude changes.

Best use: Controlled/unusual-flight discussion.  Status: MODEL.

### 14. Bank-angle sweep

A continuous sweep shows when a low-elevation spacecraft enters a strong lobe, weak sector or hand-off region.

Best use: Sensitivity figure.  Status: MODEL.

### 15. Climb and descent sweep

Contrasts level flight, descent and climb without conflating flight-path angle with aircraft-space elevation.

Best use: Controlled-flight scenario inset.  Status: MODEL.

### 16. Normal versus unusual attitude sky domes

Two hemispheres compare routine cruise coverage with a steep bank/pitch case, including no-coverage regions.

Best use: End-of-flight caveat / supplement.  Status: MODEL.

### 17. Coverage ribbon through a controlled turn

A route ribbon is coloured by predicted gain while heading and bank evolve through a turn.

Best use: Trajectory-model integration.  Status: MODEL + TRAJECTORY.

### 18. Operational envelope and edge cases

A two-panel map separates well-constrained normal-attitude behaviour from extrapolative unusual attitudes.

Best use: Uncertainty disclosure.  Status: MODEL + UNCERTAINTY.

## MH371

### 19. MH371 route as a natural experiment ★

The route map marks 01:55, 03:21 and 03:29, where heading changes produced large predicted gain changes.

Best use: Primary validation figure.  Status: DATA.

### 20. Three matched geometry snapshots

At each phase, a plane, line of sight, heading, predicted gain and path-corrected power are shown together.

Best use: General-reader validation figure.  Status: DATA + MODEL.

### 21. Time-aligned heading, gain and power

Stacked traces show whether received-power changes occur where the geometry model predicts them.

Best use: Technical validation figure.  Status: DATA + MODEL.

### 22. Same-channel counterfactual test ★

The three phase means are compared with complete, partial and zero gain-precompensation predictions.

Best use: Core hypothesis-test figure.  Status: DATA + INFERENCE.

### 23. Observed change versus predicted gain change

A change-on-change plot removes the arbitrary power intercept and makes agreement or attenuation visible.

Best use: Robustness / supplement.  Status: DATA + INFERENCE.

## Inference

### 24. Gain-precompensation coefficient β ★

A visual continuum links β=0 (complete compensation), the estimate, and β=1 (none).

Best use: Hypothesis-test summary.  Status: INFERENCE.

### 25. End-to-end received-power chain

A left-to-right link budget separates AES gain, space loss, satellite/ground terms and recorded power.

Best use: Methods overview.  Status: EXPLAIN + MODEL.

### 26. Causal graph and nuisance separation

Geometry drives gain; channel, path, terminal control and slower RF offsets also influence the observation.

Best use: Statistical-model architecture.  Status: INFERENCE + MODEL.

### 27. How power intersects the BTO/BFO solution ★

Layered likelihood ridges show power narrowing—but not independently locating—the satellite-constrained path.

Best use: Integrated-estimator explanation.  Status: INFERENCE.

### 28. Posterior before and after received power ★

Side-by-side 00:11 maps reveal which modes are reweighted when the received-power likelihood is added.

Best use: Results figure.  Status: INFERENCE + DATA.

## Data anchors used in the MH371 thumbnails

- 01:55 UTC: heading 236°T; reconstructed gain approximately 10.4 dBic.
- 03:21 UTC: heading 158°T; reconstructed gain approximately 14.1 dBic.
- 03:29 UTC: right turn of more than 60°; heading approximately 219°T; reconstructed gain approximately 11.7 dBic.
- Same-channel test: R1200-0-36E3; free-space-path-corrected phase means.
- β=0 denotes complete gain precompensation; β=1 denotes no gain precompensation.
