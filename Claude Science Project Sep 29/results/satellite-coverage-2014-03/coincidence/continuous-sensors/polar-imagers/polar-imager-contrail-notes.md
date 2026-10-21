# Continuously recording polar imagers vs the posterior aircraft routes, 7-8 March 2014

## Deviations (read first)
1. **DMSP F15**: no ephemeris found. Space-Track bulk export (Hugging Face) has no DMSP objects at all; CDAWeb SSJ positions exist for F16, F17 and F18 only. F15 passes were not computed.
2. **DMSP F16-F18 ephemerides** are CDAWeb SSJ spacecraft positions (geocentric, converted to geodetic), not TLEs. This is a substitute source.
3. **DMSP F19** was launched 3 Apr 2014. It is excluded as not in orbit in March 2014.
4. **FY-1D** passes are computed, but the satellite was inactive (WMO OSCAR: end of life 1 Apr 2012). Its passes are void.
5. **Images checked: only 4 of 10 coincident passes.** Checked: VIIRS 18:55, MODIS 19:10, NOAA-18 20:48 and NOAA-18 22:33. Not checked: NOAA-19 19:12 (FIDUCEO gap 7-20 Mar 2014), FY-3B 19:44 (NSMC login), NOAA-15 22:05 (FIDUCEO ends 2010), DMSP F16 22:26 and F17 23:24 (OLS archive not reached).
6. **AVHRR imagery is the FIDUCEO FCDR v1.00 (GAC-based)**, used in place of NOAA CLASS GAC/LAC L1b. CLASS was blocked by the sandbox. I did not request access, because retrieval needs a CLASS account order.
7. **The ATSB 2017 report was read from the project Google Drive copy.** www.atsb.gov.au accepted the connection but sent no reply (two attempts).
8. **Contrail-in-swath metrics use a weighted resample of 4,000 routes per pass.** The aircraft-in-swath probability uses all 148,000 routes. ERA5 statistics use 1,500 routes per 10 min (timeline) and 1,500 or 600 routes per pass.
9. **After 00:11:49 UTC** (last route vertex) the aircraft is held at the last vertex until 00:20.
10. **Run-J families repro-r600 and repro-r600bfo are not used.** They were not in the weight list given.
11. **Coincidence time is the zero-Doppler (Earth-fixed) approximation.** It differs from the actual scan time by -2.6 s (MODIS), -4.7 s (VIIRS) and -13 to +14 s (AVHRR). Image overlays use the granules' own scan times.
12. **VIIRS I-band (VNP02IMG/VNP03IMG) granules** were confirmed in CMR but not downloaded. The M-band split window is the contrail test used.
13. **Scope change** (instruction from the parallel contrail-physics track, received after the image work): coincidence/geometry tables and archive checks kept in full (148,000 routes, all 37 passes); image work limited to the top coincidences plus the calibration case, framed as a confirmation / positive-control check rather than an open search. Rendered: VIIRS 18:55 (split window and Day/Night Band), MODIS 19:10, NOAA-18 20:48 and 22:33, plus one positive-control figure for the FL400 ice-supersaturated layer. No further downloads.

## Method
- **Posterior.** Run J BTO+BFO, `routes.npy` (lat, lon), 2000 routes x 38 vertices from 18:01:49 at 600 s spacing. Family weights are waypoints 0.9982 (24 seeds), free 0.0013 (18), repro-radar 0.0003 (16) and descent-climb 0.0002 (16). Seeds have equal weight within a family, giving 148,000 routes. Positions are linearly interpolated in time. From 16:42:27 to 18:22:12 the Geoscience Australia digital radar track (sheet Data-Cleaned-Estim-Time, 467 points) is used for all routes, with zero uncertainty.
- **Ephemerides.** Space-Track GP elements from the HF export `tle_2014.parquet`. SGP4 is initialised from the parsed fields (WGS72), using the element set nearest in epoch (all within 17 h). TEME to Earth-fixed uses GMST. Check: SGP4 sub-satellite points lie 1.2-3.4 km from the VIIRS nadir-pixel geolocation, with timing within 1 s.
- **Coincidence.** For each half-orbit, the zero-Doppler crossing of every moving route is found (coincide.py, spherical R = 6371 km). The aircraft is "in swath" when |cross-track offset| <= ground offset at the maximum scan angle. Scan limits: VIIRS 56.28 deg, MODIS 55.0, AVHRR/3 55.37, VIRR/MERSI 55.4, MVISR 55.4, MSU-MR 54.0, OLS 1500 km half-swath, CALIPSO IIR 69 km. Model half-swaths were checked against granule geolocation. VIIRS: 1531.5 km measured vs 1532.8 km model. MODIS: 1161.8 vs 1165.3. AVHRR GAC: the edge on the aircraft side is 1468-1471 km at 18-26 S against 1500 km nominal, with a ~20 km left/right asymmetry. P is weighted by posterior weight.
- **Contrail metric.** Past track points at 1 min steps (0-60 min) are tested as static points for being inside the swath when the scan passes them, with age = scan time minus formation time. Wind advection and spreading are ignored in this metric.
- **Sun and Moon** at the aircraft (10.67 km) use JPL DE421 (skyfield). The Moon illuminated fraction agrees with the VIIRS VNP03DNB field (ephemeris 0.426; VNP03DNB 41.9 %).
- **Pixel size** is from the constant-IFOV geometry. VIIRS M-band aggregation zones are 3/2/1 at 31.59 and 44.68 deg. OLS is 2.7 km (smooth data). AVHRR GAC sampling was measured from the FIDUCEO geolocation: 3.7 km across-scan at nadir, 19-23 km at the edge.
- **Contrail physics.** ERA5 (anonymous ARCO zarr mirror) T, q, u, v at 300, 250, 225, 200 and 175 hPa, interpolated in log-p to FL300 (300 hPa), FL350 (238.4) and FL400 (187.5). The Schmidt-Appleman threshold uses EI(H2O) = 1.25, LHV = 43.2 MJ/kg, cp = 1004, and overall efficiency 0.3 (sensitivity 0.4), with the ambient-humidity correction. Persistence is defined as ice relative humidity >= 100 %. Saturation pressures follow Murphy and Koop (2005).
- **Imagery.** VIIRS M15-M16 brightness temperatures come from the L1B look-up tables. MODIS bands 31-32 use inverse Planck at band-centre wavelengths (11.017, 12.032 um). AVHRR ch4-ch5 use the FIDUCEO BT. Images are gridded by nearest neighbour (0.01 deg or 0.02 deg) and the split-window difference is high-passed (minus a 21-pixel running median). Posterior samples (2,000) are placed at the granule's scan time, iterated three times, with an FL350 parallax shift away from the sub-satellite point (8.1 km VIIRS, 5.5 km MODIS). Expected contrail lines are advected with ERA5 wind times age (median drift 33 km at 60 min and 76 km at 120 min for VIIRS 18:55).

## Results
**Calibration case (radar track, 16:42-18:22).** No polar imager swath contained the radar-tracked aircraft at the moment of a pass. The nearest were Aqua 17:31 (2,107 km off track), S-NPP 17:14 (2,322 km) and NOAA-19 17:30 (2,435 km). However, the whole radar-tracked flight lies inside the S-NPP 18:55 and Aqua 19:10 swaths, with contrail ages 33-133 min and 48-148 min. Its contrail, had one formed, is therefore imaged with zero position uncertainty. Nothing linear is visible along the expected lines in either image. ERA5 says that at FL350 the air over the radar track was 228.0-228.6 K, against a threshold of about 222 K: no formation.

**Coincident passes (P aircraft in swath > 0.01):**

| UTC | Satellite / sensor | P in swath | Aircraft (median) | Scan angle | Pixel (km) | Moon elev | Assessment |
|---|---|---|---|---|---|---|---|
| 18:55:38 | Suomi NPP VIIRS | 1.000 | 5.63 N 94.19 E | 32.4 | 0.90 x 0.79 (DNB 0.74) | -23.6 | IR: nothing visible; DNB: not assessable (moonless) |
| 19:10:33 | Aqua MODIS | 1.000 | 3.64 N 93.99 E | 24.4 | 1.11 x 1.25 | -27.5 | nothing visible |
| 19:12:33 | NOAA-19 AVHRR | 1.000 | 3.37 N 93.97 E | 32.7 | GAC | -28.0 | not assessed (FCDR gap; CLASS query) |
| 19:44:07 | FY-3B VIRR/MERSI | 1.000 | 0.84 S 93.56 E | 2.1 | 1.1 | -36.2 | not assessed (NSMC login) |
| 20:34:59 | FY-1D MVISR | void | 7.66 S 92.90 E | 18.6 | - | -49.3 | satellite inactive |
| 20:48:42 | NOAA-18 AVHRR | 1.000 | 9.49 S 92.72 E | 53.5 | GAC edge 19-23 | -52.8 | not assessable (edge sampling) |
| 22:05:33 | NOAA-15 AVHRR | 1.000 | 19.82 S 91.69 E | 46.7 | GAC | -71.1 | not assessed (CLASS query) |
| 22:26:14 | DMSP F16 OLS | 1.000 | 22.57 S 91.41 E | 16.2 | 2.7 | -75.1 | not assessed (archive query) |
| 22:33:11 | NOAA-18 AVHRR | 0.678 nominal / 0.067 measured edge | 23.51 S 91.31 E | 55.2 | GAC edge 19-23 | -76.2 | not assessable (probably outside archived swath) |
| 23:24:26 | DMSP F17 OLS | 1.000 | 30.20 S 90.58 E | 15.9 | 2.7 | -78.4 | not assessed (archive query) |

- **Moon and Sun.** The Moon was below the horizon at every coincidence (the maximum elevation over all samples is in the CSV, at -22 deg or lower), with 43-44 % illumination. The Sun was below -6.9 deg. **No Day/Night Band or OLS visible-channel contrail test is possible in this window.**
- **Contrail formation (ERA5).** At every coincidence, P(forms) = 0 at FL300 and FL350 with efficiency 0.3. With 0.4 the FL350 margin is +3.1 to +5.6 K too warm, except DMSP F17 at 23:24 (+0.8 K; P = 0.02). At FL400 contrails form, but the median ice relative humidity is 0.19-0.55, so no persistence: trails would be short and narrow, below the 0.75-1 km pixels. Along the whole posterior, FL350 first allows formation near 00:00 UTC at about 35 S (timeline, lower panel).
- **Positive controls.** Neither the VIIRS nor the MODIS scene (91.5-105 E, 0-9.5 N) contains any long, straight, narrow linear feature from any aircraft. The NW-SE streaks over the Andaman Sea (96-99 E, 6-8.5 N) are present in both images 15 min apart and are numerous and parallel. I judge them natural cirrus bands. So detectability in these scenes cannot be demonstrated. This agrees with ERA5: contrails were not forming at common cruise levels.
- **Positive control in the ice-supersaturated layer (FL400).** ERA5 puts ice-supersaturated air at 187.5 hPa over 8.6 % of the VIIRS scene at 18:55 (175 hPa 6.5 %, 200 hPa 4.8 %, 225 hPa 0 %; maximum RHi 1.22), at 100.3-105 E, 1.5-7.3 N, i.e. beneath and east of the radar-tracked KL-IGARI leg. Neither VIIRS 18:55 nor MODIS 19:10 shows cold cloud (BT11 < 235 K) inside it (fraction 0.000) or any linear contrail-like feature (visual). So even where contrails could have persisted, no aircraft trail is visible; detectability cannot be demonstrated from these scenes. (ERA5 humidity uncertain; contour position uncertain by tens of km.) This agrees with the parallel contrail-physics track (notes df5975a4).
- **Interpretation.** The infrared "nothing visible" results at 18:55 and 19:10 are honest negatives. They carry almost no evidential weight against the posterior, because the atmosphere did not support contrails at FL300-FL350. **No likelihood update is warranted from these passes.**

## ATSB (2017) pp.126-127, "Contrails analysis" (read from the project Drive copy)
- **What NASA did.** In April 2014, NASA scientists (Minnis, Bedka, Spangenberg, Duda) examined "all available polar-orbiting satellite imagery" along possible tracks from 19:00 UTC 7 Mar to 05:00 UTC 8 Mar. They also examined temperature and moisture profiles for contrail potential.
- **The candidate.** One possible contrail was found in Terra MODIS at 04:45 UTC on 8 Mar at 45.5 S 84 E, oriented NNE-SSW. Conditions there were judged suitable for contrail formation, and the position (with four hours of cloud motion) was broadly consistent with the assumed path. Multi-wavelength and other imagery led to the conclusion "probably a shadow from some other feature or a cloud edge".
- **Later review.** A later NASA review of a third-party Sumatra contrail claim judged it a near-linear discontinuity in stratocumulus.
- **Not published.** No sensor list, pass times or footprints were published.
- **What this adds:**
  1. A pass-by-pass list with posterior probabilities, scan angle, pixel size, Sun and Moon.
  2. The S-NPP VIIRS 18:55 pass, which falls just before NASA's 19:00 start. It also images the whole radar-tracked segment at known positions.
  3. A quantitative Schmidt-Appleman/ERA5 test, showing that FL300-FL350 contrails were not expected at any coincidence.
  4. The finding that DNB/OLS contrail tests were impossible (moonless).
  5. Measured archived-swath edges (NOAA-18 22:33 drops from P 0.68 to 0.07).
  6. Explicit archive status.
- **Window caveat.** Our window ends at 00:20 UTC, so the NASA 04:45 Terra candidate lies outside it.

## Granules
See `polar-pass-granules.csv`. Downloaded and checked: VNP02MOD/VNP03MOD/VNP02DNB/VNP03DNB A2014066.1854 (C2), MYD021KM/MYD03 A2014066.1905 and .1910 (C6.1), and FIDUCEO N18 orbits 19:54-21:36 and 21:36-23:18. The raw files were deleted after extraction; gridded subsets are in `polar-pass-image-subsets.npz`.

## Queries for Pete
1. NOAA CLASS order (account needed): AVHRR GAC L1b for NOAA-19 19:12, NOAA-15 22:05 and NOAA-18 20:48/22:33 on 7 Mar 2014. Ask also for any HRPT/LAC from Australian (BoM/GA/CSIRO), Singapore or Indonesian stations, at 1.1 km.
2. DMSP OLS F16 22:26 and F17 23:24: NCEI/CLASS or EOG Mines (registration). These are thermal only (no split window) at 2.7 km, and moonless, so their value is low.
3. FY-3B VIRR 19:44 (nadir pass over 0.8 S 93.6 E): CMA NSMC data service (registration).
4. DMSP F15 ephemeris (Space-Track login) to complete the DMSP set.
5. Should the window be extended to 05:00 UTC 8 Mar to match NASA, including the Terra 04:45 candidate? That would need a surface-impact/drift-free posterior beyond 00:19, so it is mostly debris/smoke rather than contrails.

## Caveats
- ERA5 upper-tropospheric humidity has known biases for ice supersaturation. The formation verdict depends mainly on temperature, where the margins are 3-6 K, so it is robust. The persistence verdict is less certain.
- Contrail spreading and wind shear are not modelled. Real lines would be wider and displaced by additional shear.
- These assessments are visual only. No automated linear-feature detector (e.g. Mannstein-type) was run.
