# Correlation of transport errors between two nearby drifting objects (ocean transport, 10 October 2026)

**Status: measured. The sample is small and the intervals are wide.** This answers Pléiades' request of
9 October, ~22:40 UTC. The full table is in `ocean-transport-error-pairs.json`, and the script is
`engine/crates/ocean/prepare/replay_pairs.py`.

## What was measured

- **Input:** the drifter replay residuals already measured (`ocean-transport-error-gdp-replay.md`), each
  residual being model minus drifter, in km.
- **Pairs:** two undrogued drifters (different drifters), with starts not more than 100 km apart.
- **Leads:** 13 and 15 days. The cross-lag value pairs one drifter at 13 days with the other at 15 days, which
  matches the COSMO-SkyMed / Pléiades geometry.
- **Statistic:** Pearson correlation per component (east, north), pooling both member orders.
- **Interval:** 95% bootstrap over drifters, 1,000 resamples, in which a pair is weighted by the product of
  its two members' resample counts.
- **Configurations:** GLORYS12 + 1% ERA5 wind, and GlobCurrent daily + 1% ERA5 wind.

## The requested set is too small

Pléiades asked for undrogued pairs with the same start, starting in the search box (80–110 E, 45–20 S) in
March–May. **That set has only 7 pairs, from 4 drifters**, and gives no useful estimate. Two wider sets are
therefore reported:
- **Same start, whole domain** (15–120 E, 50–0 S): 184 pairs, 64 drifters.
- **Starts within 2 days, whole domain:** 884 pairs, 187 drifters.

## Results: cross-lag correlation (one drifter at 13 d, the other at 15 d), east / north

| Initial separation | Set | Pairs (drifters) | GLORYS12 + 1% ERA5 | GlobCurrent + 1% ERA5 |
|---|---|---|---|---|
| 0–25 km | same start | 46 (16) | 0.82 / 0.81 | 0.68 / 0.60 |
| 0–25 km | within 2 d | 100 (62) | 0.65 (0.14–0.85) / 0.40 (−0.45–0.79) | 0.48 (−0.09–0.80) / 0.43 (−0.28–0.73) |
| 25–50 km | same start | 32 (25) | 0.23 (−0.58–0.72) / 0.27 (−0.61–0.57) | −0.16 (−0.76–0.43) / 0.05 (−0.62–0.52) |
| 25–50 km | within 2 d | 175 (100) | 0.41 (0.00–0.69) / 0.37 (−0.13–0.68) | 0.31 (−0.01–0.60) / 0.17 (−0.09–0.43) |
| 50–100 km | same start | 106 (63) | 0.30 (−0.18–0.64) / 0.32 (0.00–0.57) | 0.14 (−0.29–0.48) / 0.17 (−0.20–0.50) |
| 50–100 km | within 2 d | 609 (185) | 0.07 (−0.11–0.24) / 0.10 (−0.07–0.27) | 0.14 (−0.07–0.30) / 0.07 (−0.13–0.24) |

- **Intervals:** the 0–25 km same-start intervals are not shown because they cover nearly −1 to 1. Those 46
  pairs come from only 16 drifters, mostly drifters deployed together.
- **Same-lead values** (13 d with 13 d, 15 d with 15 d) are within about 0.1 of the cross-lag values; they are
  in the JSON.

## What this means for Pléiades (finding, not ruling)

- **At Pléiades' separations of 40–80 km**, the point estimates are 0.07–0.41 for GLORYS12 and −0.16–0.31 for
  GlobCurrent.
- **The bootstrap upper limits** are 0.24–0.72 in the bins that cover 40–80 km.
- **ρ = 0.5 is inside the measured range as an upper sensitivity. ρ = 0.8 is above every 25–100 km upper
  limit** (the largest is 0.72), so the data do not support it at these separations.
- **ρ = 0** is inside several intervals, but most point estimates are positive.
- **A central value of about 0.2–0.3**, with 0.5 as the upper sensitivity, describes the measurements best.
- **Limits:** these are drifters, not debris, and drifters deployed together dominate the closest bins. The
  set that matches the request exactly is too small, so the estimates come from the whole domain and all
  seasons.

— ocean transport (architecture sub-agent)
