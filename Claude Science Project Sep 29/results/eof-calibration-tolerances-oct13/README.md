# Item 2 — proposed acceptance tolerances for the Boeing-trace calibration (for Pete's sign-off)

**Status: PROPOSAL. No fit has been run against these numbers.** 13 Oct 2026. Contract v7.1 §8 names four targets and no numbers;
the work order says the tolerances must be fixed before fitting. Proposed here from the published standard for matching a flight
model to reference data, adapted to what 1 Hz position-and-altitude traces can show.

## The standard used, and why

The world reference for "how close must a flight model be to its validation data" is the FAA flight-simulator qualification
standard, **14 CFR Part 60, Appendix A, Attachment 2, Table A2A** (Level A–D full flight simulators; ICAO Doc 9625 sets
comparable criteria internationally, not cross-checked here row by row). Its tolerances are the result of decades of practice in matching aircraft models to flight test data, and Part 60
states why tolerances exist at all: "mathematical modeling and acquisition and development of reference data are often inexact".
The rows that apply to this problem were read from the 1 Jan 2024 edition and are in `faa-part60-table-a2a-extract.csv`:

| Part 60 test | Part 60 tolerance |
|---|---|
| 2.c.9 Phugoid dynamics (cruise) | ±10 % of period; ±10 % of time to half or double amplitude, or ±0.02 damping ratio |
| 2.d.4 Spiral stability (cruise) | correct trend, and ±2° or ±10 % of roll angle in 20 s |
| 2.d.5 Engine-inoperative trim | ±1° rudder, ±2° sideslip (applies to item 1, not item 2) |
| 1.d.4 Idle descent | ±3 kt; ±200 ft/min or ±5 % of rate of descent |
| 1.d.5 Emergency descent | ±5 kt; ±300 ft/min or ±5 % of rate of descent |
| 1.d.2 Level-flight deceleration | ±5 % of time |
| general rule | where two tolerances are given, the less restrictive may be used |

Two adaptations are needed and are stated, not hidden:
1. **The Boeing traces are not flight test.** They are an engineering-simulator export, so a residual measures model difference, not
   measurement error, and is strongly autocorrelated. Matching is therefore done on **features** (one value per case per target),
   not on the 1 Hz points: about 4–6 features per case, ≈ 45 features in total, against 2,400+ points per long case.
2. **Two targets are not directly observed.** Bank angle and vertical acceleration are derived (bank from the coordinated-turn
   relation tan φ = V ψ̇ / g, with no wind stated; acceleration from a second derivative of 1 ft-quantised altitude). Their
   derivation error **will be measured before fitting** — the spread of the derived value across smoothing windows of 11, 21 and
   31 s — and added in quadrature to the Part 60 tolerance, so the inflation comes from the data, not from a choice.

## Proposed tolerances, per case

| target | applies to | tolerance (pass if inside) | basis |
|---|---|---|---|
| T1 phugoid period | glide cases 1, 2, 7, 8, 9 and the glide part of 5 | ±10 % | Part 60 2.c.9 directly |
| T2 phugoid damping | same | ±0.02 damping ratio, or ±10 % of time to half amplitude | Part 60 2.c.9 directly |
| T3 bank growth | all ten cases, from the first sustained roll-off | correct direction and trend, and ±2° or ±10 % of bank 20 s later, whichever is larger, plus the measured derivation spread | Part 60 2.d.4 + derivation term (measured) |
| T4 time to 15,000 ft/min | dive cases 3, 4, 5, 6, 10 | correct yes/no in all ten cases; time from first flame-out ±10 % or ±10 s, whichever is larger | Part 60 timing tolerances are ±5–10 %; ±10 s is the 21 s smoothing window's half-width, below which 1 Hz data cannot resolve a crossing |
| T5 peak descent rate | all ten | ±300 ft/min or ±5 % in the glides (Part 60 1.d.5); **±10 %** in the dives | Part 60 1.d.5 for glides; doubled for dives, because no Part 60 test covers flight beyond M0.87 and the model is labelled extrapolated there (§8) |
| T6 distance and time from first flame-out to impact | all ten | ±10 % of distance, or ±1 NM for the dives; ±10 % of time, or ±10 s | Part 60 distance tests ±10 %; the ±1 NM floor is a proposal, to be checked against the traces' position noise before fitting |
| T7 chord after the 15,000 ft/min crossing | dive cases | ±10 % or ±0.5 NM, against Boeing's traces; reported beside Iannello's published 4.7–7.9 NM | the one published comparison (secondary source, provenance logged in `eof-published-benchmarks.csv`) |

**Gate rule (§8).** The uncontrolled-arm gate passes when every case passes every target that applies to it **out of sample**
(leave-one-out), with the per-case residual table published. A case that fails is reported as failed with its residuals; it is not
dropped and not refitted on its own.

## Fit design that goes with the tolerances (from the work order)

- **Likelihood:** each feature residual is Gaussian with σ = tolerance / 2, so a tolerance is a 2σ band; features are independent
  across targets, and each case counts once per target. Effective observation count ≈ 45, stated, not the ~17,000 points.
- **Parameter budget, fixed before fitting:** the six existing phenomenological parameters — `spiral_doubling_s`,
  `residual_bank_deg`, `residual_bank_left_probability`, `trim_cl_offset` (with trim at loss of control), `windmilling_per_engine`,
  `rat_increment` — plus `spiral_divergent_weight`: 7 shared parameters against ≈ 45 features. Initial conditions (altitude, speed,
  track) are read from each trace, not fitted. Per-case nuisance parameters are not allowed, because they would let each case be fitted
  separately and destroy the leave-one-out test.
- **Leave-one-out on all ten cases;** cases 3, 4, 5, 6 and 10 reported by name.
- **Declared limitation for the methods:** all ten cases are uncontrolled. The piloted and deliberate families have no trace data,
  so this calibration validates the uncontrolled arm only.

## What Pete is asked to approve

The table above as the acceptance standard (or changes to any row), **before** any fit is run. In particular: (i) the doubled ±10 %
on dive descent rate (T5); (ii) the ±10 s floor on time to 15,000 ft/min (T4); (iii) σ = tolerance / 2 in the fit likelihood.
