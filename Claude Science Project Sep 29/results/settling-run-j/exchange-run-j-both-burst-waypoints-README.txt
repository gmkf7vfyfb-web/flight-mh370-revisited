Ocean settling - seabed wreckage samples on end of flight's run J, stratum run-j-waypoints (CONDITIONAL on this stratum); both-burst set, 8 thinned seeds, D2-D5 only, 2026-10-18 05:59Z.
Settling hypothesis/settling 9330d4c (real ocean, 75-115 E, 45-10 S); end-of-flight tools 4605cc21, binary mh370-eof-rj1; 8 seeds.
Core run J convergence: split-half accepted as a pass by project ruling, 16 Oct 2026 (free flight 0.840 single split, 0.873
all-partition mean; waypoints 0.934 all-partition). Core posterior share of this stratum (run_j_maps_pass.STRATA): waypoints 0.9982,
free 0.0013, repro-radar 0.0003, descent-climb 0.0002. Mix strata by core share x Z per cell (per-seed ln Z below / in the info json).
D0 ('00:19 Held Out') is D0': the 00:19 values are held out but the transmission is imposed - every cell carries end of flight's
+alive factor (impact after 00:19:37.443; checked: 0 positive-mass rows at or before it, every seed, every product).

ROW MASS = end of flight's 00:19 two-factor table (smoke/option_table_0019.py seed_terms), per seed: hand-off weight / sum / K x
survival factor x L(D) x L(cause). Per-cell per-seed ln Z equals seed_terms' to 7e-15 (asserted, every seed, both passes).
Primary cell = both log-on causes, q = 1/3, C2 silent (q = prior odds C2:C1, so P(C1) = p = 1/(1+q) = 0.75, P(C2) = 0.25, option_table_0019 line 4), W = 00:10:58-01:15:56. D4 / D5: Holland transient bias added (wording rule 18:15Z).
Each product is a systematic resample over all rows of the 8 seeds: each (row, draw) outcome has weight 1/N - AVERAGE over outcomes.

Labels (carry): piloted rapid descent to 40,000 ft/min with unloading to -1.0 g; piloted-turn model and INTERIM pitch-down PROVISIONAL;
in-flight structural outcome PROVISIONAL (VD/MD declared; no transonic drag rise); EoF overlays round3-laws, bank-cap-uniform, dive-branch, c2-silent-aim;
BREAKUP ROWS SETTLED FROM THE INTACT IMPACT POINT (fragment field not modelled, gap G-bf); P(left) = 0.8 PROVISIONAL; breakup table PROVISIONAL.

Products (j indexes rj_bothburst_draws.npz rows_<j>, draws_<j>, stratum_<j>, seed_<j>); 90 % areas thousand km2 (resampled impacts -> seabed):
| j | 00:19 treatment | cause | family | N | row ESS | posterior share within the treatment (cause rows: prior p x Z ratio, p = 0.75 / 0.25) | 90 % area | settled offset p50/p90/p99 km | not computed | estimable |
|---|---|---|---|---|---|---|---|---|---|---|
| P00 | 00:19 R600 BTO + Raw BFO | total | all | 40,000 | 111,753 | 100.0 % | 97.5 -> 97.9 | 0.37 / 4.02 / 21.35 | 0 | yes |
| P01 | 00:19 R600 BTO + Raw BFO | total | A1 | 10,000 | 54,655 | 20.6 % | 18.2 -> 18.4 | 0.30 / 1.89 / 21.91 | 0 | yes |
| P02 | 00:19 R600 BTO + Raw BFO | total | A2 | 10,000 | 33,346 | 22.2 % | 117.4 -> 117.8 | 0.37 / 3.95 / 20.77 | 0 | yes |
| P03 | 00:19 R600 BTO + Raw BFO | total | B | 10,000 | 48,684 | 57.1 % | 106.6 -> 107.0 | 0.42 / 4.55 / 21.41 | 0 | yes |
| P04 | 00:19 R600 BTO + Raw BFO | C1 | all | 20,000 | 111,252 | 99.8 % | 97.4 -> 97.7 | 0.37 / 4.03 / 21.44 | 0 | yes |
| P05 | 00:19 R600 BTO + Raw BFO | C2 silent | all | 20,000 | 99,266 | 0.2 % | 52.0 -> 52.3 | 0.32 / 1.96 / 22.09 | 0 | yes |
| P06 | 00:19 R600 BTO + both BFOs as recorded | total | all | 40,000 | 6,334 | 100.0 % | 58.2 -> 58.4 | 0.33 / 3.05 / 21.71 | 0 | yes |
| P07 | 00:19 R600 BTO + both BFOs as recorded | total | A1 | 10,000 | 409 | 8.0 % | 15.7 -> 15.9 | 0.31 / 1.98 / 21.97 | 0 | NO |
| P08 | 00:19 R600 BTO + both BFOs as recorded | total | A2 | 10,000 | 5,302 | 37.0 % | 55.0 -> 55.3 | 0.33 / 3.08 / 21.83 | 0 | yes |
| P09 | 00:19 R600 BTO + both BFOs as recorded | total | B | 10,000 | 2,595 | 55.0 % | 59.8 -> 60.1 | 0.34 / 3.24 / 21.51 | 0 | yes |
| P10 | 00:19 R600 BTO + both BFOs as recorded | C1 | all | 20,000 | 6,290 | 99.6 % | 58.2 -> 58.4 | 0.33 / 3.07 / 21.62 | 0 | yes |
| P11 | 00:19 R600 BTO + both BFOs as recorded | C2 silent | all | 20,000 | 5,914 | 0.4 % | 43.0 -> 43.3 | 0.30 / 1.91 / 21.74 | 0 | yes |
| P12 | 00:19 R600 BTO + both BFOs, Holland transient bias added | total | all | 40,000 | 44,325 | 100.0 % | 51.9 -> 52.2 | 0.32 / 2.87 / 21.78 | 0 | yes |
| P13 | 00:19 R600 BTO + both BFOs, Holland transient bias added | total | A1 | 10,000 | 4,584 | 24.9 % | 19.8 -> 20.1 | 0.30 / 1.93 / 22.07 | 0 | yes |
| P14 | 00:19 R600 BTO + both BFOs, Holland transient bias added | total | A2 | 10,000 | 42,580 | 32.0 % | 51.6 -> 51.8 | 0.33 / 3.07 / 22.18 | 0 | yes |
| P15 | 00:19 R600 BTO + both BFOs, Holland transient bias added | total | B | 10,000 | 28,109 | 42.9 % | 56.9 -> 57.2 | 0.34 / 3.17 / 21.63 | 0 | yes |
| P16 | 00:19 R600 BTO + both BFOs, Holland transient bias added | C1 | all | 20,000 | 43,994 | 99.5 % | 52.8 -> 53.1 | 0.32 / 2.84 / 21.77 | 0 | yes |
| P17 | 00:19 R600 BTO + both BFOs, Holland transient bias added | C2 silent | all | 20,000 | 3,299 | 0.5 % | 49.7 -> 50.1 | 0.33 / 1.95 / 21.60 | 0 | yes |
| P18 | 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | total | all | 40,000 | 27,323 | 100.0 % | 54.5 -> 54.7 | 0.33 / 3.04 / 21.82 | 0 | yes |
| P19 | 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | total | A1 | 10,000 | 1,754 | 4.9 % | 17.6 -> 17.9 | 0.33 / 1.95 / 21.95 | 0 | yes |
| P20 | 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | total | A2 | 10,000 | 15,799 | 37.6 % | 54.0 -> 54.2 | 0.33 / 2.97 / 21.92 | 0 | yes |
| P21 | 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | total | B | 10,000 | 12,566 | 57.5 % | 56.0 -> 56.3 | 0.33 / 3.19 / 21.77 | 0 | yes |
| P22 | 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | C1 | all | 20,000 | 27,114 | 99.6 % | 54.1 -> 54.3 | 0.33 / 3.05 / 21.56 | 0 | yes |
| P23 | 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | C2 silent | all | 20,000 | 19,234 | 0.4 % | 39.0 -> 39.3 | 0.31 / 1.92 / 21.58 | 0 | yes |

COVERAGE
(a) Feasible set: as end of flight's run J note (piloted dives to about 40,000 ft/min, unloading, speeds past VMO/MMO, piloted turns,
    in-flight structural damage or breakup).
(b) Settling's reach: every row reaching the water as an intact impact. Declared reach gaps: G-bf (in-flight breakup rows settled from
    the intact impact point; real field spread along the descent, not modelled); attitude-dependent breakup (declared). Impacts
    refused by the ocean window are carried at the impact position (column 'not computed').
(c) Proposal coverage (row Kish ESS per product above; gate 1,000). Products below the gate (stamped not estimable in the figures):
    - 00:19 R600 BTO + both BFOs as recorded x total x A1: row ESS 409

Per-seed ln Z per cell (for mixing strata and for end of flight's cross-check):
{"run-j-waypoints|00:19 Held Out|C1": [-8.81001549860894, -8.598901482534625, -8.72050286394837, -9.039674913209653, -8.123602978008684, -8.058904849854551, -8.748319419851928, -8.479827877669901], "run-j-waypoints|00:19 Held Out|C2 silent": [-12.731316436486475, -12.750563990523212, -12.50512012367284, -12.925151103089725, -12.678397232337689, -12.751197256993136, -12.691481827912076, -12.908585463364199], "run-j-waypoints|00:19 Held Out|total": [-9.091114189319855, -8.881351191111705, -9.0006409453142, -9.320534297744468, -8.407785626005591, -8.343536363113175, -9.029560013677653, -8.763541401370457], "run-j-waypoints|00:19 R600 BTO Only|C1": [-14.119769450604554, -13.900818176816088, -14.004140862996158, -14.353324593270274, -13.413864889733063, -13.425478278251791, -14.143585197789198, -13.843903006278232], "run-j-waypoints|00:19 R600 BTO Only|C2 silent": [-18.18437500300611, -18.252907424360995, -17.835422069534435, -18.36966690506935, -18.010809197603635, -18.175667514955236, -18.31075258184714, -18.272277022265268], "run-j-waypoints|00:19 R600 BTO Only|total": [-14.401744585146128, -14.184216147416581, -14.284621654048664, -14.635018380833989, -13.698191731260659, -13.710281146878534, -14.426115200808319, -14.127615010489965], "run-j-waypoints|00:19 R600 BTO + Raw BFO|C1": [-18.8433622848114, -18.90696778574427, -18.882318836729418, -19.11016662764533, -18.6612050054706, -18.5822347400485, -19.19391137104074, -18.817171024871353], "run-j-waypoints|00:19 R600 BTO + Raw BFO|C2 silent": [-24.057179594809455, -24.235631020659405, -24.122087104150605, -22.721946595884774, -24.028117802703953, -24.03270687704076, -24.202325319860805, -24.225314335204303], "run-j-waypoints|00:19 R600 BTO + Raw BFO|total": [-19.129232378379285, -19.19303431398202, -19.168235307034283, -19.38888772375227, -18.94733211358662, -18.86848641043821, -19.47936875591428, -19.103360894421254], "run-j-waypoints|00:19 R600 BTO + both BFOs as recorded|C1": [-28.274697257536232, -28.372171355442685, -28.40775984502032, -28.702838077370032, -28.169123777084803, -27.96169951015507, -28.704197121880714, -28.143129950105], "run-j-waypoints|00:19 R600 BTO + both BFOs as recorded|C2 silent": [-32.74359310299086, -32.8887327361538, -32.470103619550976, -32.77411550258779, -32.83216002861355, -32.79863801214601, -32.86170772709595, -32.83026059382754], "run-j-waypoints|00:19 R600 BTO + both BFOs as recorded|total": [-28.558566620133465, -28.656217867451765, -28.689722094014424, -28.984851053773287, -28.453664866448904, -28.24674130501762, -28.986677261312714, -28.427745700568835], "run-j-waypoints|00:19 R600 BTO + both BFOs, Holland transient bias added|C1": [-28.291469816739404, -28.390118848153527, -28.403141172769818, -28.68908151972203, -28.176432448316028, -27.54738531435884, -28.63407233187502, -28.16944865239882], "run-j-waypoints|00:19 R600 BTO + both BFOs, Holland transient bias added|C2 silent": [-32.429579340062624, -32.350107984308224, -32.07283709849585, -32.54307010614234, -32.37824904937151, -32.189372334317206, -32.49566841377891, -32.33881039268974], "run-j-waypoints|00:19 R600 BTO + both BFOs, Holland transient bias added|total": [-28.573848317438816, -28.67146658447538, -28.682364383196006, -28.96972342262194, -28.45913747331919, -27.83185969474588, -28.91476740366709, -28.45198991952053], "run-j-waypoints|00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added|C1": [-28.861983807983627, -28.947384612387882, -28.950092542972925, -29.225318337027133, -28.82522490352536, -28.740066291042666, -29.279060149606412, -28.79906401458988], "run-j-waypoints|00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added|C2 silent": [-33.20978360499456, -33.29789575739292, -32.951786451378304, -33.3127211478344, -33.29906879045041, -33.3547597359118, -33.36713882933632, -33.279888059049306], "run-j-waypoints|00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added|total": [-29.145363402232707, -29.2307758313944, -29.231698234034084, -29.507421744201757, -29.109113049318996, -29.02445206245654, -29.56116731546676, -29.082978500728252]}

Files: rj_bothburst_impacts.f64 (f64, 14 columns: unix_s, lat, lon, v_east, v_north, v_up, flight-path angle, mass, KE, vertical KE, parent,
debris_class, draws, stratum*10+seed; stratum index is 0 in every folder, so this column is the seed number 1..K); rj_bothburst_source.npy (int64: stratum index, seed, ROW INDEX into end-of-flight/run-j/run-j-waypoints/seed-<k>/impacts32.npy);
rj_bothburst_elements.f64 (f64, 8 columns: table row, draw, breakup family, class, fate (0 settled, 1 afloat, 2 not computed, -1 refused), lat, lon,
mass kg); rj_bothburst_draws.npz; rj_bothburst_info.json; figures settling-seabed-wreckage-run-j-both-burst-waypoints-{core,cause,family}.{png,pdf,json}.
Key outcomes as row * 2**20 + draw.
