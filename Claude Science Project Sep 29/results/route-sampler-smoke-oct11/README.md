# Route sampler smoke (core, 11 Oct 2026, ~23:40Z)

2 seeds x 420k particles; full evidence stack as runs G/H with `route-sampler.toml` replacing `waypoints.toml`; binary built from af8417eb plus the sampler code (committed as 6d9f4ef7). **Not converged; for mechanics only.**

- This run used `legs_mean = 3` as the *untruncated* geometric mean (mean after the cap 2.68). The config now treats `legs_mean` as the mean after the cap (Pete: "mean 3, at most 8"), so later runs differ in their prior.
- Family log evidence -128.13 (seeds -127.91, -128.42), against -122.19 for run H's data-selected 6-route family.
- First leg: SAMAK reached in 0.891 of the posterior, always fly-by. The leading plans are SAMAK, then toward ISBIX, with break-off/transition at 0.6 or 0.8 of the ISBIX leg. Equator rule engaged in 0.5 % of the weight.
- Final-epoch latitude median -37.17 (5-95 %: -37.38 to -35.73), labelled "core, Davey both-BTO no-BFO 00:19 treatment".
- Prediction check (PREDICTION.txt): 1 met; 2 the truncated-geometric mean was misstated (2.675, not 2.84; the unit test confirms 2.680); 3 met; 4 met; 5 partly missed (6 nats below run H, more than "a few").
