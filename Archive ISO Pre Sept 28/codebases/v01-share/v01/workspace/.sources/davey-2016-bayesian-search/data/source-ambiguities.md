# Davey reconstruction source ambiguities and substitutions

This file is part of the frozen audit trail. It separates reported parameters,
cross-source contradictions, and unavoidable substitutions.

## BTO calibration sign

`[SOURCE]` Davey Eq. 5.3 defines

    h_BTO = T(x, s) - T_nom + T_channel - T_anomaly,

then gives `T_nom = 499,962 μs` and `T_channel = -4,283 μs` for the accident-flight
R1200 messages. Read literally, the fixed term is `-504,245 μs`.
[S-davey-2016-bayesian-methods-mh370, pp. 38–39; chunks
S-davey-2016-bayesian-methods-mh370:p0038:c01,
S-davey-2016-bayesian-methods-mh370:p0039:c01]

`[SOURCE]` Ashton Table 3 independently reports an average empirical BTO bias of
`-495,679 μs`. [S-ashton-et-al-2015-search-for-mh370, p. 6; chunk
S-ashton-et-al-2015-search-for-mh370:p0006:c01]

`[DERIVED — DISPUTED]` With the released 17:07 aircraft state, ephemeris and BTO
15,660 μs, the effective `-495,679 μs` convention predicts 15,574.8 μs (85.2 μs
residual, within the declared 100 μs tolerance for rounded state and altitude). The
literal Davey sign predicts 7,008.8 μs, an 8,651.2 μs residual. The difference
between the two fixed terms is exactly 8,566 μs, twice 4,283 μs.

Decision: The reconstruction uses `T - 499962 + 4283`, equivalent to the independently
checkable effective bias `T - 495679`. The Davey sign is retained as a source
contradiction and is not silently described as reproduced. This decision is tested
by `test_released_bto_calibration_matches_1707_geometry`.

## Initial prior

`[SOURCE]` Chapter 4 states position SD 0.5 nm, direction SD 1°, and an initial
Mach drawn uniformly from 0.73 to 0.84. [S-davey-2016-bayesian-methods-mh370,
pp. 34–35; chunks p0034:c01, p0035:c01]

`[SOURCE — DISPUTED]` Table 8.2 instead lists latitude and longitude SD 0.4
arcmin and “Control Mach” Gaussian SD 0.03, without publishing the corresponding
mean. [S-davey-2016-bayesian-methods-mh370, p. 72; chunk p0072:c01]

Decision: the frozen primary run follows the more explicit Chapter 4 wording:
0.5 nm position SD and uniform Mach 0.73–0.84, with the separately reported OU
instantaneous-Mach deviation SD 0.00311. No 0.03 Gaussian is added because its
mean and relationship to the uniform initial Mach are not specified.

## Unavailable exact inputs and implementation substitutions

| Item | Status | Reconstruction treatment |
| --- | --- | --- |
| Numerical radar mean state and altitude prior | UNKNOWN | reconstructed mean; altitude uniform over published 25–43 kft manoeuvre bounds |
| Historical ACCESS-G temperature/wind cube | UNKNOWN | ISA temperature and zero nominal wind; published OU wind error retained |
| Autopilot-mode weights and LNAV destination | UNKNOWN | equal mode weights; no destination-conditioned LNAV path |
| Magnetic model/version | UNKNOWN | zero magnetic declination |
| Proprietary 10-second satellite oscillator/EAFC functions | UNKNOWN | `[CORRECTED 2026-08-20]` Frozen alternative regular-epoch values with inadequately recorded source; these are not exact ATSB Table 4 values. Frozen outputs remain unchanged. verified ATSB Table 4 interpolation supersedes them for future runs. |
| Variable-rate depth-first branching settings per run | PARTLY SOURCE | fixed-size bootstrap SMC; published dynamics and likelihood retained |

These substitutions are reasons to reject an exact-reproduction label even if a
future curve happens to agree visually.

