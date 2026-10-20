# Assumptions, constraints and scenario boundaries

## Binding modelling constraints

- Do not assume absence of human control at any phase.
- Permit controlled descent before fuel exhaustion, controlled glide after
  engine flameout, terminal manoeuvring and an attempted ditching.
- Permit impact locations at least 100 NM from the seventh arc where aircraft
  performance, altitude and winds support them.
- Do not force cruise altitude or high Mach number after the last radar point.
- Test lower-altitude solutions against ground-speed, BTO, BFO, fuel and
  performance constraints instead of excluding them categorically.
- Keep the 00:11 estimator independent of the 00:19 observation likelihood.

## Current baseline assumptions

- Post-radar trajectory proposal is reconstructed from available refined-v3
  summaries because the original particle checkpoint is absent.
- The stage-one model uses equal prior mass across the three principal control
  families; cruise-heavy and descent-open alternatives are sensitivities.
- The primary vertical-BFO likelihood in the older stage-one run used an
  effective 12 Hz scale with 8 Hz and 18 Hz sensitivities; the later fast-noise
  study estimates the random component separately at approximately 0.995 Hz.
- Vertical-rate-to-BFO coefficient uncertainty remains important; the stage-one
  value was 0.009 Hz/fpm.
- Drift is model-averaged 50/50 between a normalized Davey digitization and a
  12-study meta-analysis latitude likelihood in the principal stage-one run.
- Terminal state/control priors contribute materially to impact-posterior width.

## Conditional scenarios

### Pleiades

The selected objects are either assumed to be MH370 debris or excluded. The
project does not assign a prior probability to that premise, so unconditional
and conditional maps must be displayed separately.

### Power precompensation

Terminal power precompensation is treated as an estimable hypothesis. Preserve
results with a marginalized gain-compensation coefficient and with no
precompensation. Do not conflate received-power random scatter with the
precompensation question.

### Pulau Perak descent/re-climb

The eyewitness report, radar loss/regain and disputed 4,800-ft label motivate a
sensitivity scenario. Radar altitude readouts are not treated as reliable
measurements. The scenario is not asserted as historical fact.

### Search non-detection

Search likelihood requires a coverage field and detection probability. Neither
is assumed binary. Unpublished Ocean Infinity AUV swaths are latent; AIS vessel
tracks are only location proxies.

