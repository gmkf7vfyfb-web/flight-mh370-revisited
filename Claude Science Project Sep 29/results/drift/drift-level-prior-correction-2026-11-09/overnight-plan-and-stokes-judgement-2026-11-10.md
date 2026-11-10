# Overnight plan (10 Nov 2026), higher-windage sensitivity and the Stokes drift judgement

Author: Claude Science (ocean drift thread). Pete approved all overnight stages on 10 Nov 2026 and asked for a rigorous, defensible judgement on the Stokes convention instead of a ruling. Companion to `windage-wide-run-and-sbc-smoke-2026-11-09.md`.

## 1. Summary

- The wide-windage run finishes at about 05:00 UTC on 10 Nov. Stage 1 (12 legs) finished at 03:26 UTC.
- Pete asked for a higher windage range as a minimum sensitivity, and said an expanded range must be supported by the physics and the literature. Both support a higher tail (section 3).
- Three unattended jobs wait on deskstar. They start after the wide run: a rescoring of the wide legs, and an overnight chain of 40 legs.
- The chain runs the higher-windage sensitivity first (18 legs), then the ocean-error length scale 50 km and 200 km (12 legs), a particle-noise check (4 legs) and extra ocean samples (6 legs). The estimate is about 13 hours; the first 8.5 hours cover the higher-windage and length-scale runs.
- The Stokes judgement: keep the implicit treatment (wave push inside the windage percentage) as the base. An independent calculation from the WAVERYS wave reanalysis supports the central value.
- No explicit-Stokes run is made. It needs 8.9 GB of wave data on deskstar, a new calibration of the direct windage, and a full re-run. The expected change is small against the spread already covered by the wide class.

## 2. Jobs on deskstar

| Job | Content | Starts | Estimate |
|---|---|---|---|
| 27b6e292 | wide-windage chain (stage 2 in progress) | running | ends about 05:00 UTC |
| ce85be22 | rescoring of the 18 wide legs (module rescorer, R3 configuration: 25 segments, 4 periods, bandwidths 50/25/100/200 km, 23 exterior finds and shadows), 6 processes | when `ALL-DONE` appears in `wide-chain.log` | 15 to 40 min (not measured) |
| 6496b915 | overnight chain v2: 5 start-up tests, then run 0, run 1, run 2, run 3 (replaces job 5159a954, cancelled before it started) | same gate | about 13 h |

Overnight chain: runs under the shared lock, one leg at a time. A leg with `nodes.csv` is skipped (resumable). It stops, and deletes nothing, if free disk space falls below 3 GB or two legs fail in a row. The four start-up tests (one node, two ocean samples, 100 particles each) must pass or the chain stops before any long leg.

| Run | Legs | Configuration | Question |
|---|---|---|---|
| 0 | 18 (`whigh2-*`: 42 southern points, seeds 217–232, 6 legs; `whigh-*`: 84 points, seeds 201–216, 12 legs) | exterior class, `c_wind` log-normal, median 2.4 %, σ(log) 0.35, truncated 0.8 to 6 % (5th to 95th percentile 1.35 to 4.3 %); everything else as the wide run | Does a higher windage range remove the early-arrival problem at Mossel Bay, and what does it do to the drift-alone curve and the tension? Estimate 1.6 h (first part) + 3.7 h (second part) |
| 1 | 12 (`wls50-*`, `wls200-*`) | wide exterior class, 42 southern points, seeds 217–232; ocean-error length scale 50 km and 200 km (production 100 km, assumed) | Does the early Mossel Bay tail depend on the assumed length scale? |
| 2 | 4 (`wseed23-*`, stage-2 legs 2 and 3, both models) | as the wide stage 2 but master seed 23 (stage 2 used 22) | How much of the early-tail result is particle noise? |
| 3 | 6 (`wide3-*`) | all three classes, wide exterior class, seeds 233–248, 42 southern points | Ocean-sample error of the headline p-value; the likelihood pairs the classes within one ocean sample, so all three classes are needed |

All configurations were checked against their source legs (same nodes, seeds, classes, levels, recovery, offsets; only the intended setting differs). Disk: 16 GB free at 03:40 UTC. The remaining wide stage 2 adds about 1.3 GB; run 0 about 3.8 GB; runs 1 to 3 about 6.5 GB; about 4 GB would remain. The guard stops the chain at 3 GB.

After the jobs: hybrid coefficients (`offline/build_hybrid.py`: flaperon and interior classes from the production rescoring, exterior class from the wide rescoring; self-test reproduces the input exactly), then smoothing and tension as for the headline.

## 3. Higher windage range: physics and literature (Pete's request)

Pete's position: the range may be too narrow; expand it only where physics and literature support it; test a higher range as a minimum. These are my findings; none is a ruling.

**Physics (my own first-order derivation; not from a reference).** The total effective windage of a floating part is the wave push plus the direct wind push. The wave push is measured in section 4: about 1.2 to 1.3 % of the wind, along the wind. A flat panel in edgewise drift has a direct windage of about 3.46 % × √((1 − d)/d) of the wind, where d is its relative density (air and water drag coefficients taken as equal). The total is then 2.1 % at d = 0.95, 2.4 % at 0.90, 3.0 % at 0.80 and about 6 % at 0.30. The current exterior class (0.5 to 2.0 %, centre 1.2 %) is the case d near 1: a part that is almost fully submerged and follows the water like a drifter.

**Literature supporting a higher tail.**
- The measured flaperon: extra leeway of about 10 cm/s above undrogued drifters (CSIRO Part II); my arithmetic gives 2 to 3 % at 8 m/s.
- DGA numerical modelling for the flaperon: 2.8 to 3.3 %; Nesterov (2018): about 3.3 %; Jansen et al. (2016): scenarios up to 2.5 %; IPRC tracers: up to 4 to 5 %.

**Evidence against a high centre for the Mossel Bay cowling.** The CSIRO replica trial (Part I, p. 8): the Roy replica drifted slightly less than the undrogued drifters (about 1.2 % total) in one 48-hour deployment. The fairing replica had a low-windage and a high-windage attitude. The trial is short and the replicas are not the real parts.

**Conclusion.** The physics and literature support extending the upper range to about 3 % or more, and they do not exclude values near 1.2 %. A mixture of a drifter-like mode and a buoyant-panel mode is physically the most natural description. The wide run (median 1.2 %, 95 % range 0.45 to 3.2 %) is symmetric and does not test a high centre. Run 0 does: median 2.4 % (the d = 0.9 case: wave push 1.3 % plus direct windage 1.1 %), σ(log) 0.35, 5th to 95th percentile 1.35 to 4.3 %. For the GlobCurrent legs the product offset (−0.75 to −0.60 %) is subtracted as before, so the effective values are 0.7 % lower. Run 0 is a scenario, not a prior. If the early-arrival problem disappears only at the high centre, the result shows how much of the tension depends on this one class parameter.

## 4. Stokes drift: what it is and the judgement

Waves push floating objects slowly forward (Stokes drift), in addition to the wind and the current. The module can include this push in two ways:

- **Method A, implicit (production; your ruling D-b, CSIRO's system):** the wave push is inside the windage percentage. No wave field is used. The 1.2 % value was measured by CSIRO on undrogued drifters in this system.
- **Method B, explicit:** the wave push comes from a wave model (WAVERYS surface Stokes drift), and the windage percentage covers only the direct wind push.

**Measurement (Mac, WAVERYS and ERA5, `scripts/stokes/stokes_diagnostic.py`).** Daily 00 UTC slabs from 7 Mar 2014 to 31 Dec 2016; every third grid point; wind speed 3 m/s or more; statistics weighted by wind speed. The along-wind Stokes fraction is (Us · U10) / |U10|².

| Region | Mean | Standard deviation | 5th to 95th percentile | Angle of Stokes drift clockwise of wind (mean; standard deviation) |
|---|---|---|---|---|
| Transit, 25–40° S, 40–110° E | 1.26 % | 0.34 % | 0.63 to 1.65 % | 3.2°; 20° |
| Approach to South Africa, 30–38° S, 15–35° E | 1.23 % | 0.40 % | 0.48 to 1.67 % | 3.7°; 25° |
| Broad, 20–45° S, 30–110° E | 1.29 % | 0.32 % | 0.69 to 1.65 % | 2.6°; 19° |

By wind speed (broad region): 3–6 m/s mean 0.92 % (standard deviation 0.51 %, angle standard deviation 40°); 6–9 m/s 1.26 % (0.25 %, 14°); 9–12 m/s 1.38 % (0.18 %, 10°); 12 m/s and above 1.48 % (0.14 %, 8°). Share of the wind-weighted samples outside 0.5 to 2 %: 3.3 % (broad region); outside 0.3 to 5 %: 1.8 %. Table: `tables/stokes-vs-wind-statistics.csv`.

**Judgement (mine; not a ruling by Pete).** Keep method A as the base, for four reasons.
1. The Stokes push alone averages 1.2 to 1.3 % of the wind in the drift region. This independent calculation agrees with the 1.2 % that CSIRO measured on drifters, and with their remark that the drifter value is mostly Stokes drift.
2. Adding the wave field to a windage value that already contains the wave push would double-count about 1.3 %. A consistent explicit arm needs a new direct-windage value for each class. That value is not measured (CSIRO states that the direct windage of a drifter is much smaller than 1.2 %).
3. The spread is consistent: 0.32 to 0.40 % in the real field against 0.3 % assumed per particle. The wide class (σ(log) = 0.5) covers the range between 0.45 % and 3.2 %.
4. The explicit field is 8.9 GB in module format. It is on the Mac only. Staging it and re-running everything is not an overnight job and would change the answer little.

What the explicit method would change: the Stokes fraction depends on wind speed (0.9 % in light winds, 1.5 % in strong winds), and the weighted mean is 2 to 8 % above 1.2 %. Light-wind periods also have wide direction scatter (about 40°). These are second-order effects compared with the unmeasured spread in object windage.

Limits: WAVERYS is a model product and was not validated here. The statistics are on a daily 00 UTC sample. The comparison tests the central value and the spread of the Stokes push, not the direct windage of the real parts. A referee who requires an explicit arm would need: the wave data staged on deskstar, a new direct-windage prior per class, and a full re-run (about 12 h for three classes).

## 5. Key assumptions and modelling choices

| Item | Value | Status |
|---|---|---|
| Stokes treatment | implicit (windage percentage carries the wave push), explicit arm not run | ruling D-b (Pete) kept as base; the decision not to run the explicit arm is my judgement |
| Wide exterior class | log-normal, median 1.2 %, σ(log) 0.5, truncated 0.3 to 5 % | design approved by Pete; numbers mine; provisional |
| Higher-windage scenario (run 0) | log-normal, median 2.4 %, σ(log) 0.35, truncated 0.8 to 6 % | Pete asked for a higher range as a minimum; numbers mine; provisional scenario, not a prior |
| Length scales | 50 and 200 km | sensitivities named in the production configuration |
| Particle-noise check | master seed 23, stage-2 legs 2 and 3 | my choice |
| Extra ocean samples | seeds 233–248, 42 southern points | my choice |
| Disk guard | stop below 3 GB free; nothing is deleted | my choice |
| Physics for the windage tail | total = wave push (about 1.3 %) + direct windage 3.46 % × √((1 − d)/d) | my first-order derivation, not from a reference |
| Stokes statistics | daily 00 UTC, wind 3 m/s or more, every third grid point, wind-speed weighted | my choice |
