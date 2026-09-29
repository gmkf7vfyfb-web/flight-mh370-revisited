# Antenna gain and RxGain conditional control

Source: Large (2019), bundled at `paper/paper.pdf`, SHA-256
`7fbc853d9903b3769fce18bd9f5e08da17f459a4fa6507333231df28afb222ee`.

This source recreation has three separable parts:

1. blocked prediction of event/channel RxGain under full target-EIRP
   precompensation versus no gain precompensation;
2. direct reconstruction of the event/channel full-precompensation prediction
   and directional gain departure; and
3. an uncommissioned first-pass two-dimensional active-antenna gain surface.

Run the blocked prediction with NumPy, pandas, SciPy, and Matplotlib:

```bash
python code/blocked_prediction.py
python -m unittest code/test_blocked_prediction.py
```

Compile the archived first-pass CSV to the lean runtime format with only the
Python standard library:

```bash
python code/build_runtime_grid.py \
  data/mh370-aes-gain-surface-first-pass-grid.csv.gz \
  ../../../inputs/evidence/mh371-first-pass-antenna-gain.bin
```

The compiler verifies the decompressed CSV SHA-256
`d60d14c6c137a1898c8e77336d7bdec5039b87b50269b1f723e676c0f92a3c15`.
Its 65,341-cell output is 261,412 bytes with SHA-256
`971b4c08c6e010857b5cda3af0d16f395da7e8d97660e8ff2f008f4ca0e7d0cd`.

## Result and integration boundary

The primary held-out mean log-density difference is +0.116 per point, with a
paired bootstrap interval of [-0.194, +0.462] and sign-flip p = 0.536. A
forward-only diagnostic reverses direction. The available sample therefore
does not identify a stable endpoint preference or a defensible mixture weight.

A likelihood is integrated only as an explicitly enabled conditional control.
The two canonical MH371 configurations keep the medium BFO model fixed and run
the endpoints separately:

- `directional_departure_scale = 0`: full target-EIRP precompensation;
- `directional_departure_scale = 1`: no precompensation.

The event-level observation SD is 1.72 dB from the blocked no-precompensation
point RMSE; it is not tuned to held-back MH371 truth. The full-precompensation
event/channel prediction is frozen, so the conditional likelihood contributes
only the candidate particle's directional gain departure and does not count
BTO range twice.

This is not admission of antenna evidence to the core estimator. The surface
is not verified as the installed 9M-MRO pattern, lacks commissioned
port/starboard handoff behaviour, and does not reproduce every workbook event
gain. In particular, the first MH371 event exposes a material active-envelope
versus workbook-gain discrepancy. Reports and run artifacts state these
conditions, and no prior probability is assigned between the endpoints.

## Not integrated: C-channel received power

The 18:39 and 23:14 call-channel BFO observations remain part of the normal
SATCOM likelihood. Their received-power values are not integrated as an
antenna likelihood. The known-flight calibration contains no matching
channel-21000 report, and a free call-channel offset absorbs nearly all of the
location signal over each short call. Integration requires identified beam
metadata, an independently calibrated call-to-R1200 receive-chain offset, and
one call-level observation model that accounts for serial dependence within a
burst. Until then, the raw call power is retained as source material rather
than a core observable.

## Publication controls

Generate the flight-separated statistical comparison, the paired MH371
spatial metrics, and the early-MH370 forward received-power control with:

```bash
.venv/bin/python \
  .sources/large-2019-antenna-gain/code/publication_controls.py
.venv/bin/python .sources/large-2019-antenna-gain/code/test_publication_controls.py
```

The generated summary is `outputs/PUBLICATION-CONTROLS.md`; every input and
output hash is recorded in `outputs/publication_controls_manifest.json`.
Figures 4–6 are emitted as 300-dpi PNG and vector PDF.

The early-MH370 input is an exact 18-row snapshot from the preserved
pre-refactor known-flight power-residual output: six channel-event points at
16:42 calibrate one common offset per endpoint and twelve points at 16:55 and
17:07 are forward holdouts. The source CSV SHA-256 is
`eed477aac9b81950c99c9f72e078079cbe7d840db7304a12b3d2ba778ae33859`;
the flight-only snapshot SHA-256 is
`948bc874e6c144e021d43acd88378983f17baf8a348b2ce7215e706afbb3174d`.
Raw reports are aggregated to exact-channel/minute points and the two later
bursts are the replicate units.

No early-MH370 spatial posterior is reported. The 16:42 state is a low-altitude
climb outside the current known-flight dynamics and weather fixtures, and the
retained ADS-B control has ground track rather than true heading. Using the
early-MH370 points to validate the directional surface would therefore
conflate climb attitude and track-heading error with gain precompensation. They
remain a received-power forward control, not a spatial-estimator validation.

## Attitude-aware geometry boundary

The antenna spoke now accepts an explicit aircraft attitude: true heading,
nose-up pitch and right-wing-down roll. It rotates the Earth-local satellite
line of sight into forward/right/down aircraft axes with an aerospace
yaw-pitch-roll transform before querying the aircraft-coordinate gain surface.
Independent level, pitch and roll limiting cases protect the sign convention.

All current estimator callers explicitly use zero pitch and roll, preserving
the validated level-flight behaviour. The geometry can evaluate a supplied
non-level attitude, but no current final-flight candidate provides a uniquely
determined pitch or roll. Vertical speed does not determine pitch without
angle of attack, and turn rate determines bank only under an assumed
coordinated-turn family. MH371 ACARS and early-MH370 ADS-B provide useful
track, speed and vertical-rate proxies but no measured attitude.

The full-precompensation endpoint currently assumes that the requested EIRP
is achieved; it does not impose an HPA output/headroom ceiling. End-of-flight
use must also calculate the required amplifier output from commanded EIRP and
body-frame gain, apply the verified HPA-600 channel/duty-cycle limit, and carry
any resulting EIRP shortfall into the received-power prediction.

End-of-flight received power therefore remains inactive. Before enabling it,
run a prior-marginalized climb/descent sensitivity control and resolve antenna
side selection, installation calibration and restart-channel power
calibration. The full- and no-precompensation cruise endpoints remain valid as
separate fixed conditional hypotheses; no prior or mixture weight is inferred.
