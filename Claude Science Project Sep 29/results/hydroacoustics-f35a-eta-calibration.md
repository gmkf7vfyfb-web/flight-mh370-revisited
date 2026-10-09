# Hydroacoustics: coupling efficiency η calibrated on the F-35A → H11 path, and stage C - PROVISIONAL

**Pre-registration:** `prepare/f35a_eta_calibration.py`, committed `3ca9564` before any transmission loss
on these paths was computed. A wording correction to its source citation followed in `ebfaae7`.

**Outputs:** `engine/hypotheses/hydroacoustics/results-data/f35a_cal/`.

**Paths:** the shared ocean transport export `f35a-H11S` (3,341.5 km) and `f35a-H11N` (3,248.8 km) from
merge `61b50a5`. Source 40.64 N 142.96 E is the module's working point; Metz et al. (2023, p. 1348) place
the epicentre within 8 km of the 135 km circle from Misawa.

## Why this was needed

Stage B anchored η at 2.1×10⁻⁴, an inversion of Brown et al. (2026, p. 17) through Arons' explosive law,
which is an equivalent-yield coupling. This module's η is a different quantity: the fraction of impact
energy radiated into the water as acoustic energy. This calibration measures η in the module's own
definition, through the same engine, on the one aircraft impact with a published far-field level.

## Method

- **Transmission loss:** exactly as stage B (KRAKEN adiabatic modes, hard bottom, 5–40 Hz third octaves,
  source depths 2/10/30 m), to the H11 hydrophone depths (731/739 m).
- **Observation:** Brown's 0.7 Pa peak at H11 is applied to both triads.
- **Peak-to-exposure ratio,** measured on the module's own far-field templates:
  R = p_pk²/SE = 3.0 s⁻¹ (C2) and 1.4 s⁻¹ (C1).
- **Inversion:** η_cal = (0.7²/R) / [E ρc/2π · Σ S_b(τ) 10^(−TL_b/10)], with E = 900 MJ (700–1,100 MJ).

## Part 1: the calibrated coupling η_cal

Transmission loss to H11 is 100–138 dB, with 3–5 trapped modes across the Japan Trench. Most of the spread
comes from the near-surface source: TL rises by about 24 dB between source depths of 30 m and 2 m.

Geometric mean over the two triads; template C2; E = 900 MJ; f⁻² roll-off.

| source depth | η_cal |
|---|---|
| 2 m | 2×10⁻² |
| 10 m | 8×10⁻⁴ |
| 30 m | 1×10⁻⁴ |

- **Short source durations:** at τ = 0.05 s, across all cases (depth, triad, template, energy), η_cal
  spans 2×10⁻⁵ to 1.6×10⁻².
- **The f⁻⁴ roll-off with τ ≥ 0.9 s at 2 m** needs η_cal of 0.1–0.4. That is implausible as an acoustic
  energy fraction, so the F-35A observation itself disfavours that corner of source parameters
  (exploratory remark, not pre-registered).
- **Comparison with Brown:** Brown's 2.1×10⁻⁴ falls inside this range. The two numbers are of different
  quantities, so their agreement is a consistency check, not a confirmation.

## Part 2: stage C, the IMOS detectability with η calibrated

**Set-up:**
- **Draws:** the same seed and draws as stage B.
- **η:** replaced by η_cal(τ, source depth), paired with the same τ and source depth as each MH370 draw.
  The dipole factor and most of the spectral dependence therefore cancel.
- **Transfer term C_site** ~ N(0, 10 dB), for the F-35A → MH370 impact difference.
- **Receiver term C_rcv** ~ N(0, 10 dB), for seabed receivers versus the SOFAR-axis calibration.

| roll-off | P_D (any open logger), false alarm 0.005 | false alarm 0.05 | best-logger SNR, median / 95 % |
|---|---|---|---|
| f⁻² | **0.14 %** | **2.8 %** | −13.8 / +9.8 dB |
| f⁻⁴ | 0.45 % | 6.4 % | −8.0 / +15.8 dB |

Stage B's prior gave a marginal P_D of about 10⁻⁴. Calibration moves η up about one decade, and P_D with
it, but detection still needs +19 to +29 dB. **The IMOS recorders remain effectively blind to the
impact.** Their non-detection stays uninformative, which agrees with the 0.003-bit bound.

## Caveats (each would have to fail by about 20 dB to change the conclusion)

1. **Seabed-receiver TL is still adiabatic and pessimistic,** so P_D is a lower bound. The coupled-mode
   or RAM check is pending.
2. **0.7 Pa is an unrefereed preprint value.** No H11 waveform or band is published. A broader-band
   value would bias η_cal HIGH, which favours detectability.
3. **One aircraft, one path.** The transfer to a 200 t airliner at shallow descent is the ±10 dB term,
   not a measurement.

**Gate:** the likelihood stays 0.0. This result confirms that IMOS carries no likelihood weight; it does
not validate P_D at H01W/H08S, whose raw data are not held.

*Hydroacoustics module, 2026-10-09.*

## Addendum, 9 Oct ~17:30 UTC: RAM cross-check (`hydroacoustics-ram-tl-check.md`)

**The H11 path:** on the deep F-35A → H11S path, adiabatic TL is about 3.5 dB *optimistic*. The
RAM-corrected η_cal median rises from 1.3×10⁻³ to 2.7×10⁻³.

**The IMOS seabed paths:** adiabatic TL there is 13–132 dB pessimistic. Stage C with both corrections
gives P_D **7.6 %** at false alarm 0.005 and **32 %** at 0.05; the table above is superseded.

**Withdrawn:** "The IMOS recorders remain effectively blind to the impact". The recorders are marginal;
the non-detection remains uninformative (under 10⁻³ bit).
