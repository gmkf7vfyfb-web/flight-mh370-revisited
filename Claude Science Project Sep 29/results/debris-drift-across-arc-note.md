# Why the drift-only 50 % region leans west of (inside) the 7th arc

12 Oct 2026 ~13:30 UTC, ocean drift module. Interim; run A surfaces (710 nodes); not evidence by itself. Question from Pete on
`debris-drift-source-pdf-mixture.png`.

Mean node log-likelihood, west (inside) minus east (outside) of the 7th arc (core run D reference arc m0019a), same latitude band:

| latitude band | GLORYS12 | GlobCurrent |
|---|---|---|
| 37-42 S | +2.27 | +0.73 |
| 34-37 S | +0.23 | -0.06 |
| 31-34 S | +0.02 | +0.45 |
| 28-31 S | +0.41 | +0.36 |
| 25-28 S | +0.15 | +0.14 |
| 20-25 S | -0.11 | -0.99 |

- North of 37 S: with latitude-band fixed effects, ln L falls 0.20 (GLORYS12) / 0.12 (GlobCurrent) per 100 NM east across the arc.
  Small, but the surface varies by only about 1 unit over 28-36 S, so it decides the 50 % contour; the 90 % contour hardly moves.
  Physical reading (hypothesis, not yet tested): release further west sits deeper in the gyre's westward limb, giving earlier arrivals
  at Reunion and Africa (flaperon July 2015). Test: arrival-time output by side.
- South of 37 S: east-side nodes are worse resolved (split-half noise 1.73 vs 0.82 GLORYS12; zero-environment fraction 0.35 vs 0.17).
  ln of a noisy Monte Carlo mean is biased low by about sigma^2/2 (about 1.5 east vs 0.3 west), so most of the +2.3 may be resolution,
  not evidence. Not separable with these runs (likelihood and effective particle count are confounded); the targeted southern
  resolution run (pending Pete) would settle it.
- Grid shape (wider inside the arc where flight-model impacts reach) does not create the lean; it enlarges the area the 50 % band covers.

## Follow-up check (~13:45 UTC): where the debris beaches, west vs east, 28-37 S

Mean per-node beaching probabilities by detection segment (S1 Reunion ... S6 Pemba) are the same on both sides to within 0.005
(flaperon class: e.g. S1 0.028 west vs 0.026 east, S5 NE Madagascar 0.051 vs 0.054, GLORYS12; GlobCurrent alike). So the lean does not
come from which monitored coasts the debris reaches. It must come from arrival times and places within the find kernels, which the node
tables do not store (the timing test needs a small rerun with arrival-time output).
East-side releases beach more often overall (any coast: flaperon 0.566 vs 0.520 GLORYS12, 0.399 vs 0.344 GlobCurrent), outside the
monitored segments. The likelihood normalises within monitored segments, so this extra beaching has no effect now; the deferred
Western Australia non-recovery term would act on it (not assessed).
