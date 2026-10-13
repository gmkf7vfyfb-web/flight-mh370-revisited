# RUN-STATE — Hydroacoustics
Updated: 13 October 2026, by the run J Task 1 thread (Kadri northern conditional, smoke scale)
Branch: hypothesis/hydroacoustics   Commit at close: see the closing line of this file

## Deliverable state
BUILT:
- Pre-registration and implementation of the Kadri northern conditional, both of Kadri's times,
  `prepare/kadri_northern_conditional.py`, prereg commit 6ecbb0a.
- Amendment A1, the Cape Leeuwin two-time discriminant plus the two H08S trace plots,
  `prepare/kadri_h01w_time_discriminant.py`, prereg commit 011ec84.
- Results: `results-data/kadri_northern/` — candidates.csv (34 rows, 28 computable),
  likelihood_ratio.csv, h01w_time_discriminant.csv, summary.json, three figures.
- Write-up: `results/hydroacoustics-kadri-northern-run-j.md`.
- Carried from earlier runs and used unchanged: the H08S cycle statistics
  (`h08s_shot_outliers.py`, `h08s_shot_template.py`), the IMOS detectors D1/D2 and their window null
  (`imos_detectors.py`), the T_C2 real-transient template, the stage-A injection curves, and the
  committed transmission loss in `kadri_package/next-run-b/predictions.csv`.
STUBBED:
- D4, the matched filter against T_C2, is new in this run and has no injection-recovery curve of its
  own, so it reports p but contributes no detection probability.
- Detection probability below −20 dB relative to the median shot is an extrapolation to the curve's
  floor, not a measurement.
NOT STARTED:
- Task 2 of the work order, Option B, the main predictive and power pass on run I dive.
- Task 3, updating the Kadri collaboration package with the worked results.

## Inputs in use
`Archive ISO Pre Sept 28/.../kadri-figure-extraction/figure9-vector-traces/` — digitised Kadri (2024)
  figure 9 panels a–e; panel c H01W, panels d and e H08S — tracked on this branch
`/Users/pete/Downloads/mh370-inputs/hydroacoustics/imos` — IMOS/Curtin raw recordings and the
  same-night role-B null, indexed in `data/imos/recordings.csv`
`/Users/pete/Downloads/mh370-exchange/end-of-flight/run-i-dive` — impact set, 4 strata x seed-1 read at
  this smoke scale; columns 2, 65 and 105 plus the `tau90_v1.npz` sidecar
`results-data/kadri_package/next-run-b/predictions.csv` — committed transmission loss
`results-data/h08s_template/h08s_template.json` — committed injection curve for the cycle statistics

## Pre-registration
6ecbb0a — Task 1: windows for both of Kadri's times at Perth Canyon and H08S, the seven cycle
  statistics with their directions, D1/D2/D4 at Perth Canyon, the sliding-block and window nulls, the
  0.3/0.1/0.05 levels, the retirement of the 0.005 tier, and the likelihood-ratio form.
011ec84 — amendment A1: the Cape Leeuwin two-point comparison, its four statistics, its null, and the
  decision rule, all fixed before the statistic ran.

## Declared gaps
No transmission loss on the 26.2 S to Perth Canyon path — BLOCKING for a Perth Canyon likelihood ratio,
  belongs to Task 2
P_D extrapolated below −20 dB relative to the median shot — not blocking for a null result
Seven of eight seeds per stratum unread at this smoke scale — not blocking, energy quantiles stable
Caption-option H08S window has no closed airgun cycle — permanent on these data, Kadri's raw record only
G16–G19 (SUS depth extrapolation, A1–A5 paths) — carried from the audit, untouched this run

## Agreed caveat wording (verbatim, do not paraphrase)
> Peak radiated mechanical power is not an acoustic source level; the coupling is a declared
> alternative with a prior, not a constant.

> The propagation model passes a level check against the 2001 airguns and fails a frequency-slope
> check by +10 dB per octave at Cape Leeuwin and +7 at Diego Garcia South; the airgun data cannot
> separate the source spectrum, the array pattern and the propagation.

> Detection probability is measured in IMOS logger noise and shifted by +4.8 dB to stand in for a
> three-element IMS station. It is a proxy.

> In the predicted windows no transient exceeded the pre-registered false-alarm level; the smallest
> resolvable p is 0.0101. That is no significant detection with limited power, not an absence.

> Module likelihood remains zero until injection-recovery gives detection probability against
> received level.

## Open rulings awaited
Whether run I dive replaces run I or the two are declared alternatives — the work order rules that run I
  dive SUPERSEDES run I and that run I is the p = 0 point of the same prior. Applied here. No action.
Which of Kadri's two times is correct — now answered from his own figure as 00:52:03; the question to
  him becomes a confirmation. Architecture to note in the package.
The 0.005 'strict' tier — retired by the work order, the null cannot resolve it. Applied.

## Next three actions
1. Task 2, Option B: build the 26.2 S to Perth Canyon path and run the predictive and power pass on run
   I dive, with the selection rule on predicted signal-to-noise at the best unblocked receiver.
2. Task 3: add the northern-bearing conditional to the Kadri package as its own hypothesis, with the
   confirmed 00:52:03 time, the windows at all three unblocked receivers, and the caption-time H08S
   window as the one request we cannot meet ourselves.
3. Settle or set aside the Perth Canyon 00:53:27.9 band-power excursion by checking the flagged source
   classes — ship, whale chorus, swell — against the same recording.
