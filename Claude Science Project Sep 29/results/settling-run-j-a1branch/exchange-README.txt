Ocean settling - seabed wreckage samples for end of flight's A1-branch conditional pass, combined with run J waypoints production
by the stratified estimator, 2026-10-19 04:43Z. CONDITIONAL on the waypoints stratum (core share 0.9982).
Settling hypothesis/settling 9330d4c (real ocean, 75-115 E, 45-10 S; unchanged since run I); end-of-flight tools 4605cc21, binary mh370-eof-rj1.
Work order: threads/work-orders/overnight-2026-10-19.md B1. Results note: Claude Science Project Sep 29/results/settling-run-j-a1branch/README.md.
Core run J split-half accepted as a pass by project ruling, 16 Oct 2026. D0 = D0' (impact after 00:19:37.443 imposed in every cell).
CAVEAT (end of flight, verbatim): the uncontrolled-arm dynamics are not calibrated: the Boeing leave-one-out gate failed in all three rounds.

INPUTS: production = end-of-flight/run-j/run-j-waypoints seeds 1-24 (stratum index 0 in the tables); A1-branch pass =
end-of-flight/run-j-a1branch/run-j-waypoints seeds 1-8 (stratum index 1; seeds 2-8 Horvitz-Thompson thinned to ~1M rows, normalised
by thinning.weight_sum_in). Branch = onset flame-out-associated AND control 'no intervention' (subset of A1 = cruise to fuel
exhaustion, then no control).
ROW MASS: run J settling recipe (option_table_0019 seed_terms, primary cell: both log-on causes q = 1/3, C2 silent), seeds pooled
equally within each source. Production rows IN the branch get mass 0; pass rows get mass x SCALE = 0.141077
= M_prod(D0', branch) / S_pass(D0'), one scalar for all treatments: Z(d, branch) = Z(D0') P_D0'(branch) E_D0'[L_d | branch].
P_D0'(branch) = 0.09348 (end of flight 0.09348).
Products per treatment: 'all families (A1 stratified)' N 40,000 and 'A1' N 10,000 (A1 = pass rows + production A1 rows outside the
branch, i.e. undemonstrated recoveries). Each product is a systematic resample, one settling draw each: AVERAGE over outcomes.
A2 and B products are unchanged from settling/run-j/run-j-waypoints (no new rows there); their shares rescale as in end of flight's combine.

Products (j indexes rja1_draws.npz rows_<j>, draws_<j>, stratum_<j>, seed_<j>); 90 % areas thousand km2 (resampled impacts -> seabed):
| j | 00:19 treatment | family | N | row ESS | share within the treatment | 90 % area | settled offset p50/p90/p99 km | not computed | estimable |
|---|---|---|---|---|---|---|---|---|---|
| P00 | 00:19 Held Out | all families (A1 stratified) | 40,000 | 1,885,402 | 100.00 % | 161.9 -> 162.3 | 0.36 / 3.74 / 21.02 | 0 | yes |
| P01 | 00:19 Held Out | A1 | 10,000 | 658,188 | 17.22 % | 34.8 -> 35.1 | 0.30 / 1.89 / 21.51 | 0 | yes |
| P02 | 00:19 R600 BTO Only | all families (A1 stratified) | 40,000 | 2,062,311 | 100.00 % | 116.4 -> 116.7 | 0.35 / 3.69 / 21.38 | 0 | yes |
| P03 | 00:19 R600 BTO Only | A1 | 10,000 | 823,034 | 19.68 % | 20.9 -> 21.1 | 0.30 / 1.93 / 21.91 | 0 | yes |
| P04 | 00:19 R600 BTO + Raw BFO | all families (A1 stratified) | 40,000 | 90,171 | 100.00 % | 103.0 -> 103.3 | 0.37 / 3.95 / 21.29 | 0 | yes |
| P05 | 00:19 R600 BTO + Raw BFO | A1 | 10,000 | 41,988 | 23.54 % | 18.9 -> 19.1 | 0.30 / 1.92 / 21.72 | 0 | yes |
| P06 | 00:19 R600 BTO + both BFOs as recorded | all families (A1 stratified) | 40,000 | 5,166 | 100.00 % | 63.1 -> 63.4 | 0.33 / 3.06 / 21.65 | 0 | yes |
| P07 | 00:19 R600 BTO + both BFOs as recorded | A1 | 10,000 | 5,283 | 8.60 % | 16.9 -> 17.1 | 0.30 / 1.96 / 22.05 | 0 | yes |
| P08 | 00:19 R600 BTO + both BFOs, Holland transient bias added | all families (A1 stratified) | 40,000 | 49,593 | 100.00 % | 58.3 -> 58.6 | 0.32 / 2.83 / 21.68 | 0 | yes |
| P09 | 00:19 R600 BTO + both BFOs, Holland transient bias added | A1 | 10,000 | 11,395 | 25.95 % | 23.2 -> 23.5 | 0.30 / 1.94 / 22.09 | 0 | yes |
| P10 | 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | all families (A1 stratified) | 40,000 | 26,031 | 100.00 % | 59.4 -> 59.6 | 0.33 / 3.02 / 21.47 | 0 | yes |
| P11 | 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | A1 | 10,000 | 2,920 | 5.51 % | 17.5 -> 17.7 | 0.33 / 1.97 / 21.78 | 0 | yes |

CHECKS (stratified shares against end of flight's results/eof-a1-branch-oct18/a1-branch-combined.json):
    D0: A1 share stratified 0.1722 (EoF 0.1722, diff +5.6e-17); production 0.1722; pass halves 0.1722 / 0.1722; branch row ESS pass 228,080 vs production 380,068
    D1: A1 share stratified 0.1968 (EoF nan, diff +nan); production 0.1990; pass halves 0.1953 / 0.1976; branch row ESS pass 277,994 vs production 471,831
    D2: A1 share stratified 0.2354 (EoF 0.2346, diff +8.6e-04); production 0.2382; pass halves 0.2269 / 0.2399; branch row ESS pass 15,102 vs production 18,454
    D3: A1 share stratified 0.0860 (EoF 0.0851, diff +8.5e-04); production 0.0950; pass halves 0.0814 / 0.0884; branch row ESS pass 5,281 vs production 368
    D4: A1 share stratified 0.2595 (EoF 0.2629, diff -3.4e-03); production 0.2497; pass halves 0.2454 / 0.2668; branch row ESS pass 19,468 vs production 1,261
    D5: A1 share stratified 0.0551 (EoF 0.0548, diff +3.2e-04); production 0.0604; pass halves 0.0518 / 0.0568; branch row ESS pass 2,920 vs production 2,178

COVERAGE
(a) Feasible set: fuel exhaustion with no pilot input, every descent the 777 can show (spiral up to 90 deg bank, phugoid, steep dive), as
    end of flight's A1-branch note; the rest of the flight-end families as end of flight's run J note.
(b) Settling's reach: every row reaching the water, settled as an intact impact. Reach gaps: G-bf (in-flight breakup rows settled from
    the intact impact point); attitude-dependent breakup (declared); impact pitch not used (G6).
(c) Proposal coverage (row Kish ESS per product above; gate 1,000). Products below the gate:
    - none
    Waypoints only: free flight, descent-climb and Davey dynamics with radar keep their run J A1 gaps under D3-D5 (no branch pass there).

Files: rja1_impacts.f64 (f64, 14 columns as run J; column 14 = stratum*10+seed is AMBIGUOUS here (production seeds run to 24) - use rja1_source.npy or the draws npz stratum_<j>/seed_<j> arrays);
rja1_source.npy (int64: stratum index 0/1, seed, ROW INDEX into impacts32.npy of end-of-flight/run-j/run-j-waypoints/seed-<k> (0) or
end-of-flight/run-j-a1branch/run-j-waypoints/seed-<k> (1)); rja1_elements.f64 (8 columns: table row, draw, breakup family, class, fate,
lat, lon, mass kg); rja1_draws.npz; rja1_info.json; rja1_pass0.json (estimator terms); figures settling-seabed-wreckage-run-j-a1branch-waypoints-{core,a1}.{png,pdf,json}.
