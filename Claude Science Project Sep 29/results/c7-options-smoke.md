# C-7 options at smoke scale, and the doubled one-engine flow (10 Oct 2026, core)

**Labels: PROVISIONAL-OVERNIGHT (not reviewed by Pete); SMOKE (config/smoke.toml, 2 seeds, Mac, 2 threads);
prior track 289.7 not applied (davey2016-inmarsat prior); binary = working tree after `8fd2084` (this commit).**
Seed-to-seed spread of the 00:19 median at this scale is ~1.6 deg, so only the tank columns are informative.

## 1. Finding: internal-v1 `grid_inop` is 2.00x its own source tables

`tables.lrc_ff` is "kg/h per engine" and `grid` is 2x it (correct, both engines). `tables.lrc_inop_ff` and
`holding_inop_ff` are "kg/h, one engine inoperative" (the live engine), yet `grid_inop` is also 2x them:
ratio 1.99-2.01 at all 16 states in `c7-options-smoke/grid-inop-vs-table.csv` (170-200 t, FL150-270, at the
table's own LRC INOP Mach). Probable cause: the shared lookup's `2.0 * per` (tables.py line 199).
Physics check: the live engine should burn about the twin total at the same state (5,110 kg/h at FL250
M0.60 176 t), not ~10,000. Consequence: every one-engine phase in runs with `tanks = 2` is half as long as
it should be, and the last flame-out comes correspondingly early.

Core-side correction until the fuel model is rebuilt: `[fuel] inop_flow_scale` (default 1.0 = as delivered),
overlay `config/sensitivity/fuel-fixes/inop-flow-fix.toml` = 0.5. Not used in any large run.

## 2. Hold-then-taper drift-down (architecture suggestion 2; built, NOT run at scale)

`[fuel] single_engine_profile = "hold-taper"`, overlay `fuel-fixes/s8-hold-taper.toml` (layer on s7). From the
fuel session's one-engine.md 5.1: above the one-engine ceiling the altitude is held while KCAS decays at
U(7, 11) kt/min to a drift-down KCAS U(207, 227); then ROD = V_TAS/20.7 x (1 - 1.038 (delta(h)/delta(h_c))^0.864),
anchored on core's ceiling h_c at the present weight, so the rate starts near 350 ft/min from FL350 and
tapers to a level-off ~1,000 ft above h_c. At or below the ceiling: altitude held, slowing at the same rate to
the LRC INOP Mach. Unit tests: `drift_down_rate_tapers_to_zero_just_above_the_ceiling`,
`one_engine_hold_then_taper`. The constant profile (s7) is byte-identical to `e65b0e7`; gates B and C
byte-identical.

## 3. Smoke comparison

| | (b) as delivered | (b) INOP x0.5 | (a) constant, as delivered | (a) constant, INOP x0.5 | (a) hold-taper, INOP x0.5 |
|---|---|---|---|---|---|
| weight with first flame-out before 00:11 | 0.34 | 0.46 | 0.28 | 0.54 | 0.53 |
| median one-engine time, min | 3.3 | 6.7 | 3.6 | 7.3 | 7.3 |
| 00:19 median (seed medians) | -36.21 (-37.38 -35.75) | -36.42 (-37.40 -35.77) | -36.25 (-37.27 -35.72) | -36.40 (-37.34 -35.65) | -36.44 (-37.35 -35.69) |
| log Z by seed | -99.61 -99.28 | -99.25 -99.18 | -99.38 -99.39 | -98.72 -99.12 | -98.87 -99.18 |

Reading: correcting the flow doubles the one-engine phase (about 3.5 -> 7 min) and raises the weight whose
first flame-out precedes 00:11 from ~0.3 to ~0.5, so the one-engine question matters more than (b)'s diagnostic
said. Evidence moves by under 1 nat. Hold-taper against constant is not separable at this scale.
