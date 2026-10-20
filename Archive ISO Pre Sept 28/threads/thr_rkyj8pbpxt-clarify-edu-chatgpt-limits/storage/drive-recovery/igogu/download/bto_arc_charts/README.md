# MH370: E/F/G BTO arcs and airway-constrained BFO comparison

This revised package reproduces the two requested charts and the E/F/G BFO audit. Times are UTC on 7 March 2014. P267 in the request is interpreted as P627, the airway from the preceding charts.

- Detail extent: exactly 4-7.25 degrees N, 92-97 degrees E.
- Regional extent: 3.5-9 degrees N, 92-99.5 degrees E.
- IGOGU is at 7 degrees 31 minutes 01 second N, 94 degrees 25 minutes E, about 16.0 NM north of the requested detail frame. An edge annotation preserves the exact requested extent.
- Only the selected E, F and G arcs are plotted. Their six intersections with N571 and P627 are marked and enlarged in an inset.
- The last aircraft R-channel burst in the exchange is 18:28:14.904 UTC.

The Kuala Lumpur/Chennai boundary runs south along 94 degrees 25 minutes E to 6 degrees N. At that junction the Kuala Lumpur/Jakarta boundary turns **east** to 97 degrees 30 minutes E, then southeast toward 1 degree 39 minutes N, 102 degrees 10 minutes E. The segment running **west** from the junction toward 92 degrees E is the Chennai/Jakarta boundary. This distinguishes the two different choices of boundary branch discussed in the prior route scenarios.

## Reproduce

Use Python with numpy, scipy, matplotlib, pyproj and reportlab installed:

```bash
python analyze_efg.py
python plot_bto_exchange.py
python make_efg_report.py
```

These scripts use the supplied inputs and write the charts, a two-page analysis PDF, CSV tables and validation JSON into `output/`. The plotting script reads the intersection CSV produced by the analysis. No network access or particle-filter run is needed.

## Measurements and corrections

| Arc | UTC | Channel | Raw BTO, microseconds | Subtracted correction | Plotted BTO |
|---|---|---|---:|---:|---:|
| A | 18:25:27.421 | R600 | 17,120 | 4,600 | 12,520 |
| B | 18:25:34.461 | R1200 log-on acknowledgement | 51,700 | 5 x 7,820 | 12,600 |
| C | 18:27:03.905 | R1200 | 12,560 | 0 | 12,560 |
| D | 18:27:04.405 | R1200 | 12,520 | 0 | 12,520 |
| E | 18:27:08.404 | R1200 | 12,520 | 0 | 12,520 |
| F | 18:28:05.904 | R1200 | 12,500 | 0 | 12,500 |
| G | 18:28:14.904 | R1200 | 12,480 | 0 | 12,480 |

The complete A-G input table is preserved for traceability; only E/F/G are used in the revised map and analysis. None of E/F/G requires an additional timing correction. In the preceding map A used the published R600 adjustment and B used the empirical integer-multiple anomaly correction described in Davey et al. (Chapter 5).

The T-channel bursts at 18:28:10-18:28:11 are retained in the original project log but are not converted into R-channel arcs. Their timing calibration differs. Downlink P-channel messages do not supply aircraft-return BTO arcs.

The shaded regions show E and G's conditional plus/minus two-sigma BTO intervals, each plus/minus 58 microseconds. The adopted ordinary R1200 standard deviation is 29 microseconds. This is not a joint confidence region.

No BFO measurements or speed estimates determine the range-arc positions. The sidebar lists the corresponding BFO observations for reference.

## BFO comparison and interpretation

All predictions use level flight at 35,000 ft geometric altitude. N571 is flown northwest toward IGOGU and P627 southwest toward POVUS, following WGS-84 geodesic segments through the published fixes. Groundspeed is sampled at 450, 475, 500 and 520 kt. The model includes satellite motion, aircraft motion, the aircraft's nominal-satellite Doppler precompensation and the saved satellite AFC curve, with a fixed 152.5 Hz oscillator calibration. Uplink/downlink frequencies are 1,646,652,500 / 3,615,152,500 Hz. No extra constant offset or E warm-up correction is fitted. Full numerical calibration settings are in `output/efg_analysis.json` and the standalone analysis script.

E/F/G observed BFOs are 172 / 144 / 143 Hz. E is only about 101 seconds after the 18:25 log-on request. Holland's published analysis describes a settling interval of about three minutes: trusting E's timing measurement does not establish a settled frequency measurement. The all-three-point results deliberately retain E unchanged, as requested; the F/G comparison is a sensitivity analysis, not a replacement of the requested result. Later F/G values are nearer the end of the settling interval, but this alone does not prove that oscillator effects have vanished.

Residuals are predicted minus observed. RSS means sum of squared residuals, in Hz squared; RMS is sqrt(RSS / number of observations). Root-sum-square in Hz is also saved to eliminate ambiguity. The three observations have equal weights in these descriptive metrics; no route priors or posterior route probabilities are calculated here.

At the six nominal arc intersections, N571 has smaller absolute BFO residuals than P627 at every observation and sampled speed. N571's best raw E/F/G sample is 520 kt (RMS 15.606 Hz; RSS 730.645 Hz squared). Its formal common-speed minimum is 707.6 kt, an implausible cruise-speed compromise driven by E. F/G alone prefer 465.4 kt (RMS 0.567 Hz), or 475 kt among the requested samples (RMS 0.684 Hz). With the inherited 4.3 Hz BFO noise scale, the very small difference between the 450 and 475 kt F/G fits does not tightly identify the speed. A 1 Hz calibration change is equivalent to about 25 kt on this N571 leg.

Pointwise formal zero-residual N571 speeds are E 1193.1, F 479.6 and G 451.2 kt. Their best requested samples are respectively 520, 475 and 450 kt. The specified southwest direction on P627 has no positive zero-residual speed for these BFOs: increasing speed makes the residuals worse, so 450 kt is best at each point and for the aggregate among the four samples. Negative unconstrained P627 optima in the CSV mean reversing the specified direction; they are not accepted southwest flight solutions.

## Trajectory continuity

The nominal BTO intersections do not constitute a feasible constant-speed trajectory. On N571, E-F implies 216.5 kt and F-G 1315.7 kt; on P627, 192.0 and 1166.0 kt. These are consequences of treating noisy arc centres as exact positions, not evidence that the aircraft actually changed speed this way.

For the continuous comparison, the sole positional parameter is distance along the airway at E. Subsequent positions advance by the selected fixed speed times elapsed time. Each of E/F/G must remain inside its own plus/minus 58 microsecond BTO gate. The script minimizes raw BFO RSS over the feasible initial-position interval, including all waypoint-crossing breakpoints. All eight requested constant-speed airway alternatives satisfy those BTO gates. The best samples remain N571 at 520 kt (RMS 15.601 Hz) and P627 at 450 kt (RMS 48.540 Hz). For transparency a separate BTO least-squares initial-position fit is also saved, under a distinct objective label. These are conditional feasibility and residual comparisons, not probabilities or a full dynamic/fuel-constrained route reconstruction.

Outputs include exact coordinates, predicted BFOs, signed residuals, RMS, RSS, formal minima, timing checks, continuous-track positions and BTO residuals. The independently implemented BFO calculation was cross-checked against the saved project model for all 24 point/speed combinations; maximum disagreement was below 4e-13 Hz (`output/bfo_model_crosscheck.json`).

## Range geometry

Aircraft positions are on WGS-84 at a constant **35,000 ft geometric altitude** (10.668 km). This is an explicit map assumption, not an altitude estimate or a pressure flight level. Each curve solves the pinned project's range equation:

```text
BTO_us = 2e6 * (distance_aircraft_satellite_km + distance_ground_satellite_km)
         / 299792.458 - 495679
```

The Perth ground station ECEF coordinate is [-2368.8, 4881.1, -3342.0] km. Satellite ECEF positions and velocities are supplied in `inputs/satellite_ephemeris.csv`. The script uses a cubic Hermite spline, matching the saved project calculation. All plotted E/F/G epochs are inside the supplied state interval; no extrapolation is required.

The ephemeris is the saved public-workbook transcription used by the project, not independently authenticated operator ephemeris. The nominal last radar marker is the project's coordinate (6.577655 N, 96.340864 E), not an uncertainty-free radar position. The arcs are range loci, not an inferred flight path. Their positions depend on the stated altitude and calibration.

The numerical verification substitutes every generated coordinate back into the range equation. The maximum residual and the SHA-256 hashes of all inputs are saved in `output/validation.json`.

## Cartographic sources and choices

1. [Published SATCOM log](https://www.atsb.gov.au/sites/default/files/media/5772619/public_mh370-data-communication-logs.pdf): timestamps, BTOs and R600 correction; printed pages 39-40 and introductory correction note.
2. [Malaysia AIP ENR 2.1](https://aip.caam.gov.my/aip%20pdf/ENR/ENR%202/ENR%202.1/Air%20Traffic%20Services%20Airspace.pdf): Kuala Lumpur FIR limits, ENR 2.1-1 dated 22 November 2007.
3. [Malaysia AIP ENR 3.3, 3 June 2010](https://aip.caam.gov.my/aip%20pdf/AIP%20AMDT%202_2010/ENR/Enr3_3.pdf): N571, P627 and the intersecting P574 segments and waypoints.
4. [AAI AIP ENR 2.1](https://aim-india.aai.aero/eaip-v2/eAIP/EC-ENR-2.1-en-GB.pdf): Chennai southern boundary, ENR 2.1-2 dated 25 May 2017; also agrees with the saved 2024 Chennai page. This neighboring boundary is a later-publication cross-check, not independent authentication of a complete 2014 regional dataset.
5. [Davey et al., Bayesian Methods in the Search for MH370](https://link.springer.com/content/pdf/10.1007/978-981-10-0379-0.pdf), Chapter 5: measurement model, anomaly correction and timing error scales.
6. [Natural Earth land polygons](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_50m_land.geojson), public-domain coastline context.
7. [Ian Holland, The Use of Burst Frequency Offsets in the Search for MH370](https://arxiv.org/pdf/1702.02432): oscillator warm-up and approximately three-minute BFO settling behavior in the 18:25 log-on sequence.

Selected verified airway segments are shown; no unknown continuation west of IGOGU or southwest of POVUS is extrapolated. P574 is included as geographic context where it intersects P627 at IGEBO. FIR boundaries are dashed purple, airways are charcoal, and BTO arcs use the legend colors.

Waypoints use the cited historical AIP coordinates. That document lists NILAM at 0955836E in the N571 row and 0955835E in the P627 row. The shared plot marker uses the latter (one arcsecond difference). POVUS is plotted at the published 0943958E rather than the former model's rounded 0944000E. Airways are drawn with WGS-84 geodesic segments. Constant-latitude FIR edges follow their parallels; the oblique FIR edges are straight chart segments. The geographic chart aspect is corrected at each view's mean latitude, and scale bars use WGS-84 geodesic distance.
