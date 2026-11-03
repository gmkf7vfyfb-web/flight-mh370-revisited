# Pre-registration amendment A1 — network detection search (amends ns-prereg-2026-11-03a)

Date: 3 Nov 2026. Written after the PROVISIONAL dry run and BEFORE the real run. The final level_correction.json and pd_curves.json have not been received or seen.
Reason: decision of the lead session (model-error choice and path types). Language: ASD-STE100.

## A1.1 Path type for each dense path (replaces the nearest-point rule)
- Old rule: the type of the nearest sparse arc point (20, 25, 30, 35, 40 S) for the same station.
- New rule: the exact type of each dense path from path-classes-royer-dense.csv (artifact version b3106ff5, project rule on each section; columns set, name, path_class, shallow_inner_m, axis_m, land). The match is by path name, for example arc32.0S-H01W.
- All 341 water paths of the nine stations used are in the file.
- The old rule agreed with the new types on 76 % of paths (296 of 387 path entries), so this change can move results.
- This is a deviation from the pre-registration. We made it before the real run.

## A1.2 Model-error cases
- Primary: the top level of level_correction.json v2. This is the Indian Ocean fit with widened spread. We report the primary case as the result.
- Sensitivity: the 'zero_bias_wide' entry under 'alternatives' (bias 0 dB, sd about 12.6 dB).
- Labelled third check: the 'all_ocean_class_fit' entry. This fit failed its own test. It is NOT a result. Every output of this case has the label "check only, failed fit".
- Each case runs the full pre-registered search: the same grid, statistics and upper limits; null A (500 time slides, seed 20261103); null B (IMOS common shifts).
- When an entry gives only global values (bias, slope, sd), they apply to every path type.

## A1.3 Not changed
- Every other rule of ns-prereg-2026-11-03a stays as written. This includes the statistic, the window split (-1/3 : +2/3 of window_s from pd_curves.json), the missing-data rule, the likelihoods, the nulls and the known-event rules.
- If pd_curves.json has a 1/hour row, we run the binary 1/hour sensitivity, as the pre-registration says.
