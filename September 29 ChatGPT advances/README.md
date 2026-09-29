# September 29 ChatGPT advances

Working area for MH370 model development beginning 2026-09-29.

## Baseline

- Branch created from `main` on 2026-09-29.
- `ISO Sept 28 Status/` is the preserved reference snapshot and is not to be modified by work in this area.
- New code, validation artifacts, notes, and reproducibility records produced in this development phase belong under this folder unless there is a specific reason to keep executable source in a branch-level workspace.

## Immediate milestone

Integrate and validate the fuel/performance state in the pre-00:11 Bayesian trajectory filter before proceeding to end-of-flight modeling.

The 00:11 particle state should carry remaining fuel, burn-rate uncertainty, aircraft mass, and a forward prediction/distribution for total-fuel exhaustion without conditioning on the 00:19 log-on evidence.

## Provenance rule

Every material result should record the source commit/configuration and enough information to reproduce it and compare it directly with the September 28 baseline.
