# Answers to the nine-part message of 15 October 2026

Family codes: **A1** = cruise to fuel exhaustion (FE), then uncontrolled descent. **A2** = cruise to FE, then controlled or arrested descent. **B** = planned descent with a ditching approach, begun before FE.
Data treatments: **D0** = 00:19 values held out. **D1** = R600 BTO only. **D2** = R600 BTO+BFO. **D3** = both BFOs, raw. **D4** = both BFOs with the Holland transient bias added.

## 1. BFO standard deviation 7 Hz and 4 Hz

- **Correction.** Davey et al. (2016) used 7 Hz in the filter. Their Table 5.1 gives empirical in-flight values of 4.0192 Hz and 4.3177 Hz. My earlier text said that our 4 Hz run "explains" Davey's shoulder. That is wrong. Our 4 Hz shoulder (0.2931, 122% of Davey's 0.2406) and Davey's 7 Hz shoulder are close, and we do not yet know why. Candidate causes: our bias-drift term adds 5.4 Hz² (effective sd at 7 Hz nominal is 7.3755 Hz; at 4 Hz it is 4.63 Hz); differences in bias marginalisation; the branching resampler. The resampler is excluded as a cause: it was tested on 4 October with the same posterior and evidence.
- **Why a narrower sd widens the PDF.** A tighter BFO likelihood penalises the systematic BFO residual pattern of the dominant constant-true-track mode more than it penalises the magnetic-heading and magnetic-track modes. Evidence weight moves into those modes: magnetic track 0.075→0.123 and magnetic heading 0.020→0.047. These modes put their mass on the northern shoulder. So the mixture becomes more multimodal and wider, even though each mode becomes narrower. The cost is +1.52 nat in ln Z.
- **Recommendation (agreed).** Run J uses the data-derived value, **4.32 Hz** (Davey Table 5.1, the larger of the two in-flight values), with 7 Hz as the declared sensitivity. Added to the run-J list as item 6. Also added is a short test to find our 4-vs-Davey's-7 difference: run our filter with the bias-drift term off at 7 Hz.

## 2. The 52.5° bank limit

- The production runs (run I) use a **fixed 90° cap**. The 52.5° cap is only in the round-3 sensitivity laws. It was fitted to the Boeing simulator traces, and it falls outside the leave-one-out range of 57.3–62.4°. So the data do not support it well.
- It does most of the work in round 3: the share of impacts steeper than 45° falls from 0.100 to 0.012, and the 10–45° band rises from 0.161 to 0.323. You are correct that a single fitted number must not decide the acoustic detectability.
- **Proposal (EoF work order).** Replace the fixed cap with a **sampled bank limit per trajectory**. Its prior comes from the maximum bank in each Boeing trace, widened to cover the leave-one-out spread, with an upper tail to 90°. The fixed 90° cap stays as a declared sensitivity. Report the steep-impact share and the 10–45° share under both.

## 3. Planned descent (B): does the result depend on the onset prior?

**How B is structured.** A planned descent starts at an onset time. It descends at 800–3,500 fpm, with one or two level-offs at 11,000–30,000 ft (each 1–40 min, second level-off probability 0.6), then makes a ditching approach. The onset prior has two equal parts:
- *anticipatory*: onset = predicted FE minus a lead of 0–150 min (uniform);
- *fuel-warning cue*: onset = predicted FE minus 30–70 min, plus recognition (0.2–5 min) and response (0.2–10 min) delays.

Both are truncated at 22:41. **No rule requires a descent to start before 00:11.** Onsets after 00:11 come from the separate 00:11 arm. The 22:41 arm holds the onsets before 00:11.

**Your concern is partly correct.** Because the prior is tied to predicted FE (about 00:17–00:20), 81% of the pre-00:11 onset mass is before 23:30. Most of those aircraft are on the sea before 00:11.

Evidence by onset time (run I joined-v2, 22:41 arm, D0, 8 seeds, median and range over seeds; ln BF vs cruise = ln of the mean likelihood of the 23:15 BFO plus the 00:11 BTO+BFO, minus the filter's own 22:41→00:11 increment):

| Onset (UTC) | Prior share | Flying at 00:11 | ln BF vs cruise, all | ln BF vs cruise, flying at 00:11 only |
|---|---|---|---|---|
| 22:41–23:00 | 0.424 | 0.001 | −18.5 (−21.9 to −11.5) | −10.9 |
| 23:00–23:15 | 0.218 | 0.004 | −10.8 | −5.2 |
| 23:15–23:30 | 0.165 | 0.020 | −7.3 | −3.3 |
| 23:30–23:45 | 0.113 | 0.100 | −5.0 | −2.7 |
| 23:45–00:00 | 0.062 | 0.303 | −3.4 (−3.8 to −2.9) | −2.2 (−2.6 to −1.7) |
| 00:00–00:11 | 0.021 | 0.505 | −3.6 | −2.9 |

What this tells us:
1. The statement "00:11 selects cruise" is **not circular**. Even a B aircraft that is still flying at 00:11, with a late onset, fits the 23:15 and 00:11 data 2–3 nat worse than cruise. Most of this comes from the BFO. Before weighting, the rms BFO innovation at 00:11 for late onsets is 35–111 Hz, because the aircraft is descending. Only level-off or slow-descent states fit.
2. The **size** of the effect depends on the prior. With the onset prior made uniform over 22:41–00:11, the evidence for pre-00:11 B rises by a factor of 2.90 (2.62–3.34). Under D0 the total B share moves from **0.108 to 0.225** (0.119–0.464 over seeds). So "overwhelmingly" was too strong for D0. It must be stated with the onset prior beside it.
3. Under **D2 and D4** the onset prior changes nothing. The pre-00:11 B share is 0.001 (D2) and below 0.001 (D4) before and after reweighting. With the 00:19 data, a descent begun before 00:11 is excluded at all onset times. The B share that remains (D2 0.077, D4 0.044) comes from onsets after 00:11.
4. Recommendation for the paper: report B with two onset priors (FE-tied, uniform), and run the uniform-onset prior as a declared sensitivity in run J (EoF order).

**Map (corrected 15 Oct, version 2).** `fig-planned-descent-map.png`. Version 1 was wrong: it drew lines from the descent-start position (the data column `takeover_*` is the descent start, not 22:41) and labelled them as 22:41. Version 2 draws each trajectory as two straight segments: the 22:41 position (taken from the core hand-off file through the `parent` index, waypoints stratum; implied cruise speed 22:41→descent start 423–481 kt, 5–95%, posterior), then descent start, then impact. The flown path between these points is not stored. The 22:41 positions lie along the 22:41 arc. The descents still flying at 00:11 come from its southern part (about 19–25 S) and start their descent mostly after 23:30.
**Do they all turn?** No. In the prior, 49% have no heading change during the descent (<0.5°), median 7.8°. In the D0 posterior of aircraft still flying at 00:11, 70% turn more than 10° during the descent (median cumulative 331°). The model samples these turns as circuits in the ditching approach. Why the data favour them is not yet measured.

## 4. Waypoints: is the narrow PDF conditional?

Yes. The narrow PDF (50% width 0.30° vs 1.90° free) is the posterior **conditional on the waypoint hypothesis**. The evidence does favour waypoints over free flight by 6.78 nat (P = 0.99822 for the pair). But that gain is an Occam factor: the waypoint prior puts its mass in a volume about 881× smaller, and the data accept it. The data do not show anything that free flight cannot fit, and the medians differ by only 0.32° (−37.15 vs −36.83). The defensible statement: *"Conditional on waypoint navigation, the posterior is narrow. The data support this specification over free flight by 6.78 nat, mostly through prior volume, so the result depends on the waypoint set chosen."* The paper reports both PDFs side by side.

## 5. Reach beyond the 121 NM glide bound

From run-i-dive waypoints, seed 1, aircraft flying at 00:19:37:
- **Fuel-feasible: yes.** The fuel model computes the flame-out, and 99.1% of these trajectories flame out before impact. 87% still had engines thrusting at descent onset, and 84% have their last flame-out **after** 00:19:37. They are powered flight that continues past the last transmission, then a glide (impact 17 min after flame-out, median; impact 29 min after 00:19:37).
- **Where along the arc:** at the south end, impact median 39.25 S (5–95%: 39.92–33.33 S), against 37.07 S for all aircraft flying at 00:19:37.
- **Which evidence decides it.** Under D0 (00:19 held out), 27.9% of all aircraft flying at 00:19:37 have their last flame-out after 00:19:37, and 1.75% reach beyond 121 NM. With the 00:19 BFOs this falls to 0.06% (D3). The q99 reach falls from 131 NM (D0) to 104 NM (D3) and 78 NM (D4). So the width difference between D0 and Holland is **determined by the 00:19 BFO evidence** (a high descent rate limits distance), not indeterminable. It is conditional on reading the 00:19 BFOs as descent. D0 also does not impose the reading that the 00:19 log-on was an APU start after both engines flamed out, so D0 allows powered flight after 00:19:37.

## 6. Impacts before the final transmission

Agreed. An aircraft that is on the sea cannot have sent the 00:19:29 and 00:19:37 bursts. Under D0, 32.8% of the weight impacts before 00:19, because D0 holds out the **values** of the 00:19 data and also, wrongly, the fact that the bursts were received. Change: **D0 becomes "values held out, transmission imposed" (airborne at 00:19:37 required)** in all treatments (EoF order).

On the feasible set, the loudness result is the other way round from my earlier "surviving statement". But **the ranking depends on the loudness measure** (corrected 15 Oct; my first version used the wrong treatment codes and gave one measure only). Share of weight in the loudest decile, threshold set on the held-out case, aircraft flying at 00:19:37 (run-i-dive waypoints, seed 1):

| 00:19 data used | by peak radiated power | by total energy | Kish ESS |
|---|---|---|---|
| held out | 0.100 | 0.100 | 793,038 |
| 00:19:29 burst (R600) BFO | 0.168 | 0.175 | 31,898 |
| 00:19:37 burst (R1200) BFO | 0.196 | 0.401 | 1,461 |
| both BFOs, raw | 0.243 | 0.297 | 274 |
| both BFOs, Holland transient bias added | **0.317** | 0.274 | 974 |

All four 00:19 readings make the impacts louder than the held-out case (1.7–4×). The Holland treatment is loudest by peak power, but not by total energy. Where the loud impacts are (`fig-impact-loudness-maps.png`): the loudest decile is on or very close to the 00:19 arc (median distance from the 00:19:37 burst position 7.5 NM held out, 9.9 NM Holland). The quieter half is further out (36.6 and 31.2 NM): these are glides that spread south and west. Standing caveat: the uncontrolled-descent dynamics are not calibrated, so these are sampling coordinates, not physical predictions. Hydroacoustics still gives no discrimination (H08S northern search LR 1.000).

## 7. Is the end-of-flight phase sampled adequately and defensibly?

**Adequate:**
- Impact latitude along the arc is stable across treatments (median −37.0 to −37.4).
- The distance from the arc is set by the 00:19 interpretation, and that dependence is now measured (question 5).
- The dive-probability coin vs hyper-prior makes no difference.
- The asymmetry tests are immaterial (≤0.031 nat).
- The onset boundary carries 0.00% of the mass.

**Not yet adequate:**
- With the 00:19 data on, Kish ESS falls to 274–1,461 per seed. 40–45 of 48 reach–energy cells inside the envelope have ESS < 100 under R1200 and both-BFO options.
- B has ESS of about 440 under D0.
- The Boeing gate failed in all three rounds.
- The bank limit (question 2) and the onset prior (question 3) are single choices that change the answer.
- Impact attitude and flight-path angle are prior-dominated. The 10–45° band moves 0.039→0.856 across the dive probability p.

**What it tells:** where along the arc, and how far from it, given each 00:19 reading.
**What it does not tell:** impact attitude, energy, and therefore acoustic detectability. These must be reported as conditional on declared priors.

Fuel feasibility check: approved. It is in the core order (run davey2016 with fuel tracked but not constraining; report the weighted share dry before 00:11, against the "one in eight" reading).

## 8. Received power and antenna gain

- **Correction.** My note said the gain test "rests on three points". That is wrong. Your 2019 all-sample variable-gain regression used **n = 937** samples (MH371 plus known-position MH370): β = 0.63 ± 0.04 (0.55–0.71), p(β=0) < 0.0001, F = 197.2, R² 0.15→0.30. The three-point same-channel test (β = 0.645) agrees with it. The doc reading stays indeterminate, so "no precompensation" stays a conditional hypothesis.
- **Selectivity along the 7th arc.** The 7th arc is a line of constant range, so satellite elevation is almost constant along it: 38.7° at 40 S to 41.2° at 28 S. The satellite azimuth is 306°–329°. For a southbound aircraft the satellite is behind and to the right (126°–149° relative), and this changes by only about 23° along the arc. Heading uncertainty of the same size mixes it up. So, as you thought, gain is weakly selective along the arc. The existing empirical received-power likelihood file spans 4.4 nat over 40–27 S (38–40 S about −4.1, 30–32 S about −1.0). That range is conditional on the gain-surface model and on the path headings, not on elevation.
- **Mode discrimination in mid-flight.** My earlier text overstated this. Gain only separates true-track from magnetic modes where their headings differ enough to move the satellite relative azimuth across a steep part of the Ball pattern. That is most likely near the pointing toward/away geometry, as you said. During the BFO epochs (19:41–00:11) the aircraft is level, so pitch and bank add little. MH371 climb and descent segments, and known MH370 phases, give the noise floor. Your previous work already did this across those flights.
- **37 S against 26 S (your question, 15 Oct).** `fig-gain-37s-vs-26s.png`. On the 00:19 arc both points have the same elevation (38.9° and 39.0°) and range (37,857 and 37,853 km). Only the satellite azimuth differs (322.3° and 301.1°). At the same heading, level flight, the antenna gain differs by 0.1–1.5 dB. Times β = 0.63 this gives 0.1–0.9 dB of received power, against the 0.5 dB noise floor. At the sampled 37 S track (185–187°) the gain difference is −0.41 to −0.48 dB, which is a received-power difference of about −0.3 dB after β. Heading moves the gain more than position does: 11.6–14.1 dB over headings 150–210° at 37 S. A 26 S path at 165° and a 37 S path at 185° predict almost the same gain (13.7 and 13.6 dB). Attitude at 00:19 also matters: a 20° change in body-frame elevation from bank or pitch changes the gain by −1.1 to +0.2 dB. Conclusion: one 00:19 burst cannot separate 37 S from 26 S on gain alone unless heading and attitude are constrained independently. The useful test is over the whole path (all level-flight epochs), and that is what the existing received-power likelihood does.
- **Prior work's own verdict** (review manuscript, September): antenna gain did not give a reliable additional localisation benefit. A lower position error at one gain endpoint came with a worse truth-density ranking. Status unchanged: conditional observable, not in the headline.

## 9. WSPR, Hugging Face and the SSD

- **Hugging Face.** I can read `peteabiome/flight-mh370-revisited-data` (13 entries). It has no WSPR material. It holds the SITA logs with C/N0, BTO, BFO and received power, the meta-analysis PDF, `MH370 calcs.xlsx`, and the 00:11 airborne posterior samples.
- **The WSPR work is not lost.** It is in `~/Downloads/review/` and `~/Downloads/resolution/`. Latest result: a truth-separated MH371 rerun with 24,000 trajectory candidates. The truth was at the 43.6th score percentile. Selecting the top tenth of the probability mass made the mean path RMSE worse, 150.8→291.2 km. Conclusion: no demonstrated localisation benefit, and WSPR is excluded from the main update. A preregistered gate (`resolution/agents/alternative_redteam/wspr_validation_protocol.md`) is proposed but not performed. `qtr901_wspr_calibration_report.pdf` is also there and not yet read.
- **SSD.** I cannot read `/Volumes` from the sandbox (a platform limit). The local disk now has 127 GiB free.
