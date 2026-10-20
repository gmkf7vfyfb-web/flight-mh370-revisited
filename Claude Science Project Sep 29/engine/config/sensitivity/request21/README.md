# Core request 21: fuel-flow factor on extrapolated steps (kappa_x)

`[fuel] extrapolation_factor = [mean, sd]` draws one factor per path (after every other prior draw)
and multiplies the flow ONLY on steps whose flow is extrapolated (Mach outside the bracketing
schedules, a single schedule, or a fit fallback). Absent: no draw, factor 1, outputs byte-identical.

Provisional prior, from the fuel audit's Boeing Table 3/4 reproduction
(results/fuel-model-audit-architecture/boeing-table3-table4-reproduction.csv), true flow / model flow:
- 11 in-table items: mean 0.9833, log-sd 0.0176 (the in-table calibration, carried by fuel_factor);
- 15 extrapolated items, relative to the in-table mean: mean 1.0265, log-sd 0.0463 (extra 0.0429).

Those items were computed on the TABLES model, not on internal-v1. Until the fuel session posts the
internal-v1 residuals: production uses the spread only, `kx-on.toml` = [1.0, 0.046] (PROVISIONAL);
`kx-shift.toml` = [1.027, 0.043] is the declared sensitivity. Note: the EoF terminal module
(terminal.rs CoreFuel) uses fuel_factor only and does not see kappa_x; the INOP (one-engine) flow
after the first flame-out is not scaled either.
