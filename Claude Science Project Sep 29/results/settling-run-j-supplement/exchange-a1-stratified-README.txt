Ocean settling - A1 by end of flight's two conditional strata on the run J northern supplement (rule B), 2026-10-20 10:33Z.
CONDITIONAL on the waypoints stratum. Work order overnight-2026-10-20 B1 (part 2). Settling 9330d4c; end-of-flight tools 45ea4af0.
Use these A1 products (and the totals with A1 stratified, D3-D5 and D3s-D5s) in place of the unconditional A1 / totals in ../ruleB-waypoints
for A1 under D3-D5. A2 and B: ../ruleB-waypoints.
Stratified estimator (end of flight, results/eof-run-j-supplement-oct20 section 3): Z(d, A1) = Z(D0') [P1 E_D0'[L_d | b1] + P2 E_D0'[L_d 1_A1 | b2]],
P1 = 0.092769, P2 = 0.100835 (rule B, a1-strata.json); b1 = flame-out-associated onset + no intervention (passes run-j-a1branch seeds 1-8 and
north-k2-a1branch, rule B: u1 = w/8, beta1 = N1/(N1 + N2 r), u2 = 2w/16, beta2 = N2 r/(N1 + N2 r), N1 = 799,999, N2 = 800,004, r = core r_hat);
b2 = flame-out-associated + recovery attempted, A1 part (pass run-j-a1outside seeds 1-8, run J paths, production alone u = w/8).
Reduced-table rows inside b1 or inside (b2 and A1) get mass 0; the strata replace them. Row masses in the reduced table's normalised units.
CHECK (asserted to 1e-6 relative): the strata shares reproduce end of flight's a1-strata.json:
    D0: branch 1 share 0.092769 (EoF 0.09276867142962755), outside share 0.076402 (EoF 0.07640192016307681)
    D1: branch 1 share 0.103838 (EoF None), outside share 0.087066 (EoF None)
    D2: branch 1 share 0.124341 (EoF 0.12434062693252697), outside share 0.101584 (EoF 0.10158431304005293)
    D3: branch 1 share 0.084104 (EoF 0.08410417106397662), outside share 0.000027 (EoF 2.7373769569214256e-05)
    D4: branch 1 share 0.200457 (EoF 0.2004574242186257), outside share 0.075029 (EoF 0.07502938609151295)
    D5: branch 1 share 0.053006 (EoF 0.053006224489768314), outside share 0.000002 (EoF 1.8188281920963725e-06)
    D3s: branch 1 share 0.106477 (EoF 0.10647729665445645), outside share 0.007107 (EoF 0.007107194872224773)
    D4s: branch 1 share 0.295330 (EoF 0.29532983192666085), outside share 0.180649 (EoF 0.1806490362075801)
    D5s: branch 1 share 0.075653 (EoF 0.075653126957288), outside share 0.000193 (EoF 0.000193299554310134)

Products (j indexes rjsa_draws.npz); 90 % areas thousand km2 (resampled impacts -> seabed):
| j | 00:19 treatment | family | N | row ESS | share within the treatment | 90 % area | not computed | estimable |
|---|---|---|---|---|---|---|---|---|
| P01 | 00:19 Held Out | A1 | 10,000 | 410,962 | 16.96 % (EoF 16.92 %) | 39.4 -> 39.8 | 0 | yes |
| P03 | 00:19 R600 BTO Only | A1 | 10,000 | 414,137 | 19.24 % | 23.0 -> 23.2 | 0 | yes |
| P05 | 00:19 R600 BTO + Raw BFO | A1 | 10,000 | 43,703 | 22.84 % (EoF 22.59 %) | 19.2 -> 19.4 | 0 | yes |
| P06 | 00:19 R600 BTO + both BFOs as recorded | all families (A1 stratified) | 20,000 | 5,942 | 100.00 % | 65.4 -> 65.7 | 0 | yes |
| P07 | 00:19 R600 BTO + both BFOs as recorded | A1 | 10,000 | 6,022 | 8.50 % (EoF 8.41 %) | 19.4 -> 19.6 | 0 | yes |
| P08 | 00:19 R600 BTO + both BFOs, Holland transient bias added | all families (A1 stratified) | 20,000 | 65,811 | 100.00 % | 59.4 -> 59.7 | 0 | yes |
| P09 | 00:19 R600 BTO + both BFOs, Holland transient bias added | A1 | 10,000 | 39,473 | 26.75 % (EoF 27.55 %) | 24.5 -> 24.8 | 0 | yes |
| P10 | 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | all families (A1 stratified) | 20,000 | 19,346 | 100.00 % | 60.5 -> 60.8 | 0 | yes |
| P11 | 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | A1 | 10,000 | 4,636 | 5.33 % (EoF 5.30 %) | 20.5 -> 20.7 | 0 | yes |
| P12 | 00:19 R600 BTO + both BFOs as recorded, other log-on cause only | all families (A1 stratified) | 20,000 | 6,686 | 100.00 % | 50.1 -> 50.4 | 0 | yes |
| P13 | 00:19 R600 BTO + both BFOs as recorded, other log-on cause only | A1 | 10,000 | 2,551 | 11.07 % (EoF 11.36 %) | 31.6 -> 32.0 | 0 | yes |
| P14 | 00:19 R600 BTO + both BFOs, Holland transient bias added, other log-on cause only | all families (A1 stratified) | 20,000 | 19,662 | 100.00 % | 52.3 -> 52.7 | 0 | yes |
| P15 | 00:19 R600 BTO + both BFOs, Holland transient bias added, other log-on cause only | A1 | 10,000 | 11,539 | 43.81 % (EoF 47.60 %) | 36.0 -> 36.4 | 0 | yes |
| P16 | 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added, other log-on cause only | all families (A1 stratified) | 20,000 | 14,617 | 100.00 % | 44.8 -> 45.2 | 0 | yes |
| P17 | 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added, other log-on cause only | A1 | 10,000 | 2,947 | 7.45 % (EoF 7.58 %) | 30.9 -> 31.2 | 0 | yes |

COVERAGE (c): products below the row-ESS gate of 1,000:
    - none
    Branch 2 (A1 outside 'no intervention') rests on run J paths only: its northern tail is thin (end of flight: 191 / 45 / 36 distinct
    states in 35-30 / 30-25 / 25-20 S under D4). Under D3 and D5 branch 2 carries < 0.0001 of Z.
Files: rjsa_impacts.f64 (14 columns; column 14 AMBIGUOUS, use rjsa_source.npy: stratum 0 reduced table row index, 1 run-j-a1branch,
2 north-k2-a1branch, 3 run-j-a1outside, then seed, row index into that seed's impacts32.npy); rjsa_elements.f64; rjsa_draws.npz; rjsa_info.json;
figures settling-seabed-wreckage-run-j-supplement-a1-stratified-{a1,total}.{png,pdf,json}.

A1 SHARE CONVENTION (read before mixing): the totals here are self-normalised mixtures (reduced-table rows outside the strata + strata
rows), so their A1 share is strata / (rest + strata), which differs from end of flight's published stratified share (strata / Z_d of
the main set, other families rescaled to 1 - A1) by up to 3.8 points (D4s 0.438 vs 0.476; D4 0.268 vs 0.276; D3 0.085 vs 0.084).
To reproduce end of flight's convention exactly, weight each outcome of a 'total' product by eof-convention-weights.json
[d].outcome_weight_for_rest_rows_nonA1 if its source stratum (rjsa_source.npy column 0) is 0, and by 1 otherwise, then normalise.
There are no A1 rows outside the two strata in the reduced table (rest_A1_mass = 0), so the A1 products are unaffected.
Recommended for searched areas and the composer: end of flight's convention (one A1 share across modules).
