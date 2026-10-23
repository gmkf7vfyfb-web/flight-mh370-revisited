cd out && python - <<'EOF'
p='evidence-sweep-2026-10-17.md'; s=open(p).read()
s=s.replace("Pléiades and COSMO-SkyMed imagery. WSPR (low priority). Antenna gain (parked).",
"Pléiades and COSMO-SkyMed imagery. WSPR and antenna gain (received power) are NOT in the estimate; see section 2D.")
s=s.replace("| C6 | WSPR | Already registered as low priority. |\n","")
add='''
### D. Registered but not in the estimate: WSPR and received power (antenna gain)

| # | Evidence | Observable and likelihood form | Informs | Status | Evidence so far |
|---|---|---|---|---|---|
| D1 | WSPR (amateur HF links as a passive radar) | Per link: P(anomaly \\| aircraft on the link path) against P(anomaly \\| no aircraft), from a receiver operating characteristic (ROC) calibrated on independent known flights. Path likelihood = product over links, with blocked (flight/day/station) dependence | whole track, including the end point | NOT IN ESTIMATE. Pete's prior control test exists; the pre-registered validation gate was proposed and not performed | Pete's control test (review manuscript §3.6, CLAIM-LEDGER): over 24,000 candidate paths the true path sat at the 43.6th weighted percentile, and choosing the top tenth by WSPR score raised mean path RMSE from 150.8 to 291.2 km. Published ROC areas under the curve are 0.59-0.67. No peer-reviewed Liverpool result found (Oct 2026) |
| D2 | Received power, C/N0 and BER per burst (SITA logs) | Per burst: rx dBm = constant + β·G(azimuth and elevation relative to the airframe; attitude) + noise. β = 0.63 ± 0.04 (Pete 2019, n = 937). The gain surface is a model alternative | mainly heading and attitude at each epoch, and through them the track; weak on 7th-arc position | NOT IN ESTIMATE (antenna-gain module parked). Used today only as a data-quality flag (the 18:25:27 burst) | The existing whole-path likelihood spans about 4.4 nat along the arc (−4.1 at 38-40° S, about −0.9 at 26-32° S), conditional on the gain surface and headings. At 00:19 alone, 37° S and 26° S differ by 0.1-0.9 dB of received power against a 0.5 dB noise floor; heading moves gain by 11.6-14.1 dB |

Assessment.
- D1 is quantifiable in principle, but no independent test has shown that it carries information, and Pete's own control test shows it does harm. It should enter only through the pre-registered gate (Downloads/resolution/agents/alternative_redteam/wspr_validation_protocol.md). Otherwise it is reported as "tested, carries no information", in the same format as a hydroacoustic null.
- D2 is real data, already held, and it is a per-epoch function of the state the core filter already samples. It belongs in core as a satcom-epoch likelihood, with gain-surface alternatives marginalised. It is not new information about position at the 7th arc. Its value is as a separate check on heading and attitude at every epoch, including the 00:19 attitude question and the no-precompensation conditional hypothesis. First step: decompose the 4.4 nat epoch by epoch along sampled paths, to find which epochs produce it before any integration.
'''
s=s.replace("\n## 3. Suggested order of work", add+"\n## 3. Suggested order of work")
s=s.replace("6. A8 and A9: hydroacoustics' existing prediction, power and coverage format.",
"6. A8 and A9: hydroacoustics' existing prediction, power and coverage format.\n7. D2: the epoch-by-epoch decomposition of received power first (cheap), then a core likelihood if one or more epochs are selective.\n8. D1: only through the pre-registered gate.")
open(p,'w').write(s)
EOF
grep -c "D2" out/evidence-sweep-2026-10-17.md