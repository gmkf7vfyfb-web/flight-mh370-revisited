# BTO-only check against Davey et al. (2016) Fig. 10.3 top panel (18 Oct 2026, core)

Run: tag run-j (1244b7c) built on the Mac (aarch64, Rust 1.98.0; deskstar heavy lock was busy with hydroacoustics), 
`mh370 config/davey2016-inmarsat.toml repro-btoonly.toml out`, 8 seeds x 7M particles, use_bfo = false, 18 threads, 25 min.
Inputs (ERA5, IGRF, satcom, ephemeris) copied from the deskstar run-J checkout; SHA256 verified. ln Z -66.188, split-half 0.907.

All values below are renormalised over latitudes south of 0 (exact interval integrals, 0.001 deg grid).

| curve | median | IQR | 95% | P(34.5-36.5 S) | P(south of 0), whole range |
|---|---|---|---|---|---|
| Davey top, BTO only (vector) | 38.88 S | 39.48-36.84 | 40.52-35.96 | 0.114 | 0.886 |
| ours, BTO only | 37.91 S (SE 0.055) | 38.65-36.81 | 40.58-15.81 | 0.084 (SE 0.004) | 0.866 (SE 0.005) |
| Davey bottom, BTO+BFO (vector) | 37.43 S | 38.16-36.33 | 39.21-34.82 | 0.271 | 1.0 |
| ours, BTO+BFO 7 Hz (F3 baseline, 4 seeds) | 37.95 S | 38.46-37.46 | 39.44-34.88 | 0.078 | 1.0 |

Peaks (south): Davey BTO only 39.23 S (tip clipped) and 36.70 S; ours 38.65 S with a smaller peak at 39.45 S.
Davey BTO+BFO 37.75 S and 36.26 S; ours 37.85 S only.

Finding: adding BFO moves Davey's southern median 1.44 deg north and raises the 34.5-36.5 S mass 0.114 -> 0.271. In our model BFO moves
the median -0.04 deg and the mass 0.084 -> 0.078. Thus about 0.16 of the 0.19 shoulder gap appears when BFO is added (BFO side); about 0.03 is
already present with BTO only. (Davey's text, ch. 10.1, says BFO "does not significantly change the shape of the Southern mode"; the recovered
curves show a large change.) In our model the 36-37 S mass belongs to the heading-type steering modes (true heading, magnetic heading/track);
true track + lateral navigation carry 0.81 (BTO only) and 0.86 (BTO+BFO) of the posterior.

Correction: shoulder values for reference curves computed earlier on a 0.05 deg grid were low by about 0.01 (the 36.5 S edge is on a steep flank).
Exact values: Davey bottom vector 0.271 (was 0.261), old hand CSV 0.250 (was 0.2406). Engine posterior shoulders are particle-weight sums and are exact.
