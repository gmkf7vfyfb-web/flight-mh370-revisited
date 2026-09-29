# Hydroacoustics: open questions and proposed next steps (saved 29 Sep 2026)

This saves the next-step decisions and the questions for Kadri, together with Pete's comments of 29 Sep, so the work can be picked up later.
- **Thread:** "Hydroacoustics" (iso `thr_gbqx8u9yfp`).
- **Branch:** `hypothesis/hydroacoustics` (original head `7141e5d`; see `code/branches.tsv`), under review, not merged.
- **Status: on hold.** Nothing has been sent to Kadri, Metz or Royer.

## Where the module stands

- **[New analysis]** Predictive only: its log-likelihood is zero, so it cannot change the estimate. For each impact sample it predicts the following, at seven receivers (H01W, H08S, and the IMOS loggers 3315, 3376, 3250, 3274 and 3275):
  - range, back-azimuth and arrival window;
  - ETOPO blockage;
  - band transmission loss, calibrated on the Blackman et al. air9 airgun shots;
  - received level as a function of coupling η.
- **[New analysis]** The pre-registered IMOS search found:
  - 0 detections at 3315, 3376, 3274 and 3275;
  - 1 at Scott Reef, whose path is blocked (p = 0.51).

  P(any IMOS logger detects) is 0.24 at the F-35A-anchored η (8.7e-3), 0.095 at η/10 and 0.005 at η/1000.
- **[Reconstructed analysis]** Tests against Kadri (2024)'s published material are in `results/worktree-hydroacoustics/hydroacoustics/kadri-tests/kadri-tests.png`.
- **Kadri package:** a draft, not sent. It is not published here, because Pete has not approved it.

## Proposed next steps, with Pete's comments

### 1. Widen the listening windows for the new end-of-flight endings

**Proposal (29 Sep):** the endings "fuel exhausted after the 00:19 log-on" and "powered impact" allow impacts as late as about 01:40, and up to about 400–550 NM beyond the 7th arc. A placeholder estimate (impacts 00:19:37–01:40, moved 0–500 NM beyond the arc) gave these windows:

| Receiver | Registered window | Widened window |
| --- | --- | --- |
| H01W time | 00:42:49–01:24:02 | 00:38:13–02:10:48 |
| H01W bearing | 242.6–298.1° | 227.3–300.5° |
| H08S | – | 01:02:22–02:29:00 |
| IMOS 3315/3376 | – | 00:40:16–02:13:28 |
| Portland | – | 01:03:37–02:33:32 |
| Scott Reef | – | all paths blocked |

- The HA01 and Diego Garcia windows would stay blind, since nobody here has seen those data. A widened IMOS search would not be fully blind: 3315's 01:29:36 record and all records from 02:10 onwards were already opened. So it would be a labelled sensitivity, and the registered IMOS search remains the blind result.
- **[Diagnostic/sensitivity]** The Curtin event (01:33:44 at Perth Canyon, 01:34:50 at H01W, bearing 301.6°) stays a control, for three reasons:
  - it is 1.1° outside the widened bearing window;
  - only 7 of 20,000 impacts match its 66 s two-station timing, and none of those also matches its bearing;
  - this is consistent with Curtin's own fix at 5.9°S 77.2°E.

**Pete (29 Sep): "400 NM beyond the arc sounds fuel infeasible to me?"**

**Assessment.** Agreed in substance. The 400–550 NM support comes from End of flight's *placeholder* window:
- continued cruise until 01:16 at most, taken from Boeing SIR Table 4's longest endurance (6.8 h from arc 1, the most economical speed and altitude);
- flown in still air;
- before the core models fuel per path.

The fuel model will bound each path's exhaustion time. Its fuel-flow factor is N(1.009, 0.018), about ±6–7 minutes over 6 hours. That should cut the flight after 00:19, and the distance beyond the arc, to minutes and tens of NM in most cases. The long tail needs checking against fuel, not assuming.

**Proposed revision:**
- size the windows from the fuel-constrained end-of-flight hypotheses once the core's fuel state lands;
- until then, bound them by a stated tail of the fuel model's exhaustion time, not by the placeholder;
- keep the placeholder numbers above only as an upper bound.

### 2. Calibrate propagation with the Blackman 2001/2003 catalogue

**Proposal:** use all 41 shot–station records, including non-detections such as air8 at H01, to calibrate transmission loss and blockage at H01 and H08S. Today only air9 is used, 116 km from the arc.

**Pete (29 Sep): "Makes sense, except most of those shot locations are not near the arc. Some of them would be on the line of sight between the arc and DG."**

**Assessment.** Right. Most shots don't sample the source region, so they can't calibrate an arc-to-station path directly.

**Proposed revision: path-segment calibration.**
- For each shot, compute how much of the arc-to-station great circle (to H08S, Diego Garcia, and to H01) its own path to the station shares, measured as length within a stated corridor.
- Use the shots on the arc-to-Diego-Garcia line of sight to calibrate loss and blockage along that shared segment.
- Treat shots elsewhere as checks of the bathymetric blockage model, not as calibration. The non-detections test where ridges cut the path.
- Keep air9 as the one direct near-arc point.
- Report, per shot, the fraction of each arc-to-station path it samples.

### 3. Count the IMOS silence as weak evidence

**Proposal:** once the composer is merged, the IMOS non-detections enter as a weak likelihood, marginalised over η (log-uniform across about three decades). Detection probability is at most 0.24, so it will barely move the estimate, but it tests the whole chain before the H01W data arrive.

**Pete:** no comment yet.

### 4. No waveform modelling yet

**Proposal:** no waveform modelling until raw H01W data exist. This is for information.

## The draft Kadri package (not sent)

| Request | What it asks for |
| --- | --- |
| R0 | Units and calibration of the H01W and H08S channels |
| R1 | Historical crash signals, the F-35A first (our only loudness calibration): arrival time, back-azimuth, peak, RMS, exposure and noise, per band |
| R2 | The Blackman shots (air7, air8 and air9 on 15–19 Oct 2001; the SUS charge at A11 on 9 Jun 2003) at H01 and H08S |
| R3 | Same-night reference signals: Curtin's 01:34:50 arrival (a control); the clock-check arrivals at 04:59:21 and 05:14:28; H08S airgun shots and the small Java Trench earthquake |
| R4 | Noise percentiles, 22:00–02:00 UTC on 7–8 March and on other nights, 1–14 March |
| R5 | Injection-recovery with his detector unchanged, in 2 dB steps from 90 to 130 dB re 1 µPa²·s |
| R6 | Every detection inside our windows, plus background windows (±6 h, other nights, rotated bearings) for significance |

There are separate asks to Metz and Royer, who run the OHASISBIO array. Note that 4 of Kadri's 19 Table 1 transients lie inside the registered H01W window, and 9 would lie inside the widened one.

## Questions arising from the tests on Kadri's published material

These are proposed additions to the package, worded neutrally.

1. **In R1, also ask for the crash signals' arrival times and bearings**, not only their levels.
2. **00:39:02, bearing 268°.** Table 1 lists it as exactly on the arc (Δt = 0). Our model has it arriving 52 s earlier than sound from an impact on the arc at 00:19:29 could. How was it computed?
3. **00:42:02, bearing 254°.** His Δt is +3.93 min and ours is −3.81 min: the same size, with the opposite sign. Is this a typo?
4. **Crash-signal timing.**
   - AF447, Transair 810 and Yemenia 626 arrive 4–9 minutes later than a water path from the crash site allows.
   - Sriwijaya 182 arrives 12 minutes early, and its path to H08S crosses Sumatra and Java.

   Which signals and times were used?
5. **F-35A level.** His figure shows 1.0–1.1 Pa; the level we use (Brown, via Metz) is 0.7 Pa. What processing explains the 3–4 dB difference?

Test results behind these questions, all **[Reconstructed analysis]** on published, processed traces (not raw data, not blind):
- Our travel times reproduce 16 of 18 Table 1 offsets to about 7 s. His offsets imply arc positions about 28 km farther from H01W than ours.
- At the Table 1 times, the Figure 9 traces give our detector's S at most 3.2 dB. The strongest peak is 00:52:04 (5.4 dB), probably his 57° signal. None would count as a detection at our thresholds.
- Only the F-35A and Lion Air 904 crash signals fit a water path. Lion Air 904 is 8–15 dB louder than predicted. So η still rests on the F-35A alone.

## Decisions to pick up

- [ ] Step 1: how to size the windows (fuel-constrained hypotheses, or a stated fuel tail meanwhile), and whether to widen at all before fuel lands.
- [ ] Step 2: path-segment calibration with the shots on the arc-to-station lines of sight.
- [ ] Step 3: IMOS silence as a weak likelihood after the composer merges.
- [ ] The five questions above, added to the package.
- [ ] Pete reviews the whole package before anything is sent to Kadri, Metz or Royer.
