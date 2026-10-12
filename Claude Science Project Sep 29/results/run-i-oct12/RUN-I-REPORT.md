# Core run I: free flight against the waypoint family at equal prior (12 Oct 2026)

Inputs are staged at `mh370-exchange/core/run-i/` (READY, 340 files, every file checked against SHA256SUMS). 8 seeds per family: 7M particles per seed for free flight and waypoints, 3.5M for descent-climb and reproduction. The 00:19 treatment is core, Davey both-BTO no-BFO.

## 1. Family result

| Family | ln Z | seed sd | ln BF against waypoints | Posterior share | Split-half (floor 0.924) | 00:19 median |
|---|---|---|---|---|---|---|
| waypoints | −129.00 | 0.23 | 0 | 0.9982 | 0.916 | −37.15° |
| free flight | −135.78 | 0.35 | −6.78 | 0.0011 | 0.830 | −36.83° |
| reproduction (Davey) | −136.73 | 0.18 | −7.73 | 0.0004 | 0.891 | −36.73° |
| descent-climb | −137.46 | 0.25 | −8.46 | 0.0002 | 0.794 | −37.06° |

Mixture over the four families: median −37.17°, 90 % interval −37.57° to −34.77°. Chart: [run-i-0019-latitude.png](/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/artifacts/proj_9cc1a5a85f63/28912f26-3709-4b73-b763-106c02b1bc0c/vd822ad70_run-i-0019-latitude.png). Table: [run-i-family-evidence.csv](/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/artifacts/proj_9cc1a5a85f63/2eec1d96-e5d4-4367-9747-f856178e66ab/vfa9acaad_run-i-family-evidence.csv).

## 2. Why the waypoint family takes 99.8 %

The sequential log-evidence increments, ln p(y_k | y_1..k−1), sum exactly to each family's ln Z. So the difference between two families splits by data item. Chart: [run-i-evidence-by-data-point.png](/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/artifacts/proj_9cc1a5a85f63/97b6b808-8f0f-4726-9f4b-e76130d961ea/v66e9b032_run-i-evidence-by-data-point.png). Table: [run-i-evidence-by-data-point.csv](/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/artifacts/proj_9cc1a5a85f63/70f77354-5db5-4035-8a8d-95631f6bbfab/vc7eb35a0_run-i-evidence-by-data-point.csv).

Waypoints against free flight (+6.78 in total):

| Data | Gain (nats) | What it means |
|---|---|---|
| Radar band VAMPI–MEKAR, 18:15–18:21 (4 across-track scores, sd 1.5 NM) | **+2.38** | The waypoint family flies the VAMPI–MEKAR line exactly, with no lateral randomness. The band is scored against that line. Free flight spreads across it. |
| 18:39 BFO (phone call, no BTO) | **+1.74** | The waypoint turn (18:37–18:39) puts the aircraft on a southerly heading by about 18:40, which matches the 18:39 BFO better. |
| 19:41 BTO+BFO | **+1.29** | The great circle to ISBIX after the turn fits the 19:41 arc. |
| 21:41–23:15, 00:11 | +0.76, +0.83 | Small gains that accumulate. 00:11 is noisy (seed sd 0.39). |
| Radar points 18:04–18:22 | +0.55 | |
| 18:25–18:28, 20:41 | −0.22, −0.63 | Small losses. |
| 00:19 (two handshakes) | +0.08 | Negligible. |
| **Total** | **+6.78** | The rows sum to the difference in log-evidence (−129.00 against −135.78). |

Approximate sensitivity: drop an item's increment, holding everything else, and recompute the four-family share. This ignores the effect of the item on later conditioning, so it is indicative only.
- No radar band: 0.981.
- No radar band and no 18:39 BFO: 0.90.
- Also no 19:41: 0.73.

So about a third of the result comes from a modelling choice: the family flies the published VAMPI–MEKAR segment exactly, and the radar band lies on that segment. The rest comes from the satellite data at 18:39 and 19:41. These favour a turn at about 18:38 followed by a steady great circle, and that is what the waypoint paths do by construction.

Caveats for the paper:
- The free-flight family puts prior mass on many paths the data reject (the Occam factor). The waypoint family puts its mass on fewer, structured paths that happen to fit, so part of the Bayes factor is prior concentration rather than better fit.
- The radar band's error model (sd 1.5 NM about the line) sets the size of the +2.38. A wider sd, or an offset fitted to the plots, would reduce it.
- No family is converged (split-half below 0.924). The family log-evidences are stable to ±0.35 nats across seeds, so the ranking is robust, but the shape of each latitude curve is not settled.

## 3. Turn and route
- Turn zoom on Pete's chart: [run-i-turn-zoom.png](/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/artifacts/proj_9cc1a5a85f63/29612956-e801-41ed-887b-2fb9de13f567/v157662e7_run-i-turn-zoom.png). 90 % ± 5 of waypoint draws turn south north of 7.55°N, between IGOGU and SAMAK. This is the fly-by of SAMAK, passing just west of IGOGU.
- Plan shares: [waypoint-plan-shares.csv](/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/artifacts/proj_9cc1a5a85f63/af16e083-821c-4ffb-982d-7ca276f61251/vf94f6022_waypoint-plan-shares.csv) and [waypoint-plan-sequences-top40.csv](/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/artifacts/proj_9cc1a5a85f63/a0ca2e0b-305c-4480-aff9-80a85e609334/v8c18aa1b_waypoint-plan-sequences-top40.csv).
  - SAMAK first 0.94; IGOGU 0.04.
  - First-leg fly-by 0.80; break-off at 40–80 % 0.19.
  - SAMAK then ISBIX 0.70; two legs 0.76.
- Turn start: [waypoint-turn-start-percentiles.csv](/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/artifacts/proj_9cc1a5a85f63/b5e5878f-69b6-4694-9f54-c09a4e44fed5/v31fc5c61_waypoint-turn-start-percentiles.csv). Median 18:37:40; 87 % start between 18:37 and 18:39.

## 4. Traffic and destinations
- Traffic: [traffic-separation-summary.csv](/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/artifacts/proj_9cc1a5a85f63/b026b3f4-be4d-40e5-b4dc-efa14e4d8e03/v5e4f484b_traffic-separation-summary.csv).
  - The main waypoint group passes IGO053 at a median 15.2 NM, 5th percentile 14.9 NM. IGO053's track is estimated.
  - The same group passes UAE343 (ADS-C) at about 30 NM.
  - The IGOGU-area draws (9 %) come within 5 NM and 1,000 ft of IGO053 in 1.2 % of cases.
- NZFX and South Pole diagnostic (post-run only): [destination-diagnostic-summary.csv](/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/artifacts/proj_9cc1a5a85f63/091f10e4-498b-409d-9b4c-09e20bf0fa44/v5154995f_destination-diagnostic-summary.csv). No final great circle passes within 100 NM of NZFX. Closeness to the pole is geometric.

## 5. Convergence and particle refresh
- Free flight's shortfall comes from the early lineages that survive 00:11. A particle refresh at 23:15 changed nothing: [refresh-smoke.csv](/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/artifacts/proj_9cc1a5a85f63/ac58eeaa-0a36-44ab-923c-dcc042f5ec01/v876f6220_refresh-smoke.csv).
- The remedy is more particles, about 2–5× for free flight. That is a long run, for Pete's agreement.

## 6. Standard family reports
Each report has the latitude pdf against Davey Fig. 10.3 and against run D's same family, plus maps, convergence and parameters:
- [run-i-waypoints-report.pdf](/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/artifacts/proj_9cc1a5a85f63/1f759c5f-53dd-46be-8f08-92b4f6eb3409/v6ec4c7bd_run-i-waypoints-report.pdf)
- [run-i-free-report.pdf](/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/artifacts/proj_9cc1a5a85f63/aa71f6c9-9728-49e3-9e78-b214eab1db58/vdd2e2b96_run-i-free-report.pdf)
- [run-i-repro-report.pdf](/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/artifacts/proj_9cc1a5a85f63/3acc963b-9016-492c-8675-fd6033e81568/v781875de_run-i-repro-report.pdf)
- [run-i-descent-climb-report.pdf](/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/artifacts/proj_9cc1a5a85f63/9ebf818b-666b-4afa-b31f-c2bef579806b/vcbc40d59_run-i-descent-climb-report.pdf)
