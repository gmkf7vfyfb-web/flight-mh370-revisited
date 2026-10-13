# Run I (core): free flight against the reset waypoint family, equal family prior

All four strata staged, 12 Oct 2026 ~14:45Z. READY is written. 340 files; every file re-checked against SHA256SUMS after staging.

- **Stack**: run D stack (run C sampler, fuel fixes s7 + s8 + inop-flow, two tanks, Inmarsat ephemeris, radar in the likelihood,
  look-ahead hand-offs at m2241 (horizon m0011) and m0011 (horizon m0019b)), plus Pete's speed rule for free, waypoints and
  descent-climb (`speed-envelope-throughout.toml`: early phase Mach 0.45-0.87 within 210-330 KCAS to 18:40, cruise Mach 0.70-0.87
  within 210-330 KCAS). The reproduction stratum is Davey exactly (Mach 0.73-0.84 throughout, no cruise CAS clip).
- **Seeds 1-8 in every stratum. 100,000 hand-off rows per seed** at m2241 and m0011.
- **Compact layout as for runs C and D:** `handoff.toml.gz` (gzipped; sha256 of the uncompressed file in COMPACT.txt);
  `tanks32.npy` (float32; the three time columns are seconds after 2014-03-08 00:00:00 UTC). Look-ahead rows: multiply each
  row's weight by exp(log_correction) (column 14 of handoff.npy); in Rust use `handoff::read_corrected`.
- `trace.npy`: up to 32 points, 18:22:00-18:42:40 every 40 s, columns lat, lon, alt_ft, track_deg, GS_kt, mach, heading_deg.
- next-i-waypoints also has `route_plans.npy` (one plan per final row) and `route_plan_fixes.txt` (fix index -> name).
- `handoff.npy` column 5 is `tau_h` (the particle's own manoeuvre time constant, hours).

## Staged

| Stratum | Deskstar job | Build | Particles per seed | Files | Size |
|---|---|---|---|---|---|
| next-i-free | c975a85f | 1ff4d1d | 7M | 83 | 10.6 GB |
| next-i-waypoints | 80e619ca | ee34559 | 7M | 99 | 16.5 GB |
| next-i-descent-climb | 18b756b6 | 8d7cf7a | 3.5M | 83 | 5.5 GB |
| next-i-repro-radar | 6a2ec01f | 1da8c7c | 3.5M | 75 | 3.7 GB |

SHA256SUMS lists every staged file (paths relative to this folder), from deskstar, verified after transfer.

## First results (equal prior over the four families; canonical split-half = mean over all 35 balanced partitions, 8-seed floor 0.924)

| Family | ln Z | seed sd | ln BF against waypoints | Posterior share | Split-half | 00:19 median | P(north of 30°S) |
|---|---|---|---|---|---|---|---|
| free flight | -135.78 | 0.35 | -6.78 | 0.0011 | 0.830, not converged | -36.83 | 0.023 |
| waypoints | -129.00 | 0.23 | 0 | 0.9982 | 0.916, just below floor | -37.15 | 0.009 |
| descent-climb | -137.46 | 0.25 | -8.46 | 0.0002 | 0.794, not converged | -37.06 | 0.022 |
| reproduction (Davey) | -136.73 | 0.18 | -7.73 | 0.0004 | 0.891, not converged | -36.73 | 0.057 |

00:19 medians: core, Davey both-BTO no-BFO 00:19 treatment. Shares: seed-bootstrap 90 % interval for waypoints 0.9978-0.9985.
The build differs between strata (1ff4d1d, ee34559, 8d7cf7a, 1da8c7c); none of the commits between them changes the filter outside the route sampler (gates B/C byte-identical throughout).
