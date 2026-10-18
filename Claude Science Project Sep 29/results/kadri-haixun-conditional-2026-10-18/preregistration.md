# Kadri preferred signal and Haixun 01 contact: conditional hypothesis, pre-registration

Committed 18 Oct 2026 before any statistic named here is computed. Prior: run J (end of flight
`~/Downloads/mh370-exchange/end-of-flight/run-j/`, four route families, headline key
`D{d} total q=0.333 (C2 silent)`; planned descents starting before 00:11 in `run-j-joined-v2/J0011`, `J2241`).
Run J is not yet formally declared final by end of flight; Pete ruled (18 Oct) that enough is done to proceed.
Every result is labelled with the run and the 00:19 option it uses.

## 1. Fixed geometry (kadri_geom.py, kadri_geom_output.txt in this folder)

| Quantity | Value |
|---|---|
| H01W position (FDSN IM.H01W1-3 centroid) | 34.8903 S, 114.1426 E |
| Kadri bearing (Table 1) | 306.18 deg; sigma 0.5 deg core, 1.0 deg wide |
| 7th arc (sea level, corrected R600 BTO 18,400 us, m0019a) on the bearing | R7 = 1,591.3 km, 25.732 S 101.369 E |
| Same, BTO +/-63 us | 1,578.9-1,603.7 km |
| Kadri's own R7 | 1,586 km (agrees within 5 km) |
| Haixun 01 first contact (ATSB 2017 p.38) | 25.975 S 101.461 E; az 305.68 deg; 1,566 km; 28.5 km from the crossing, OUTSIDE the arc |
| Superseded figure | 26.2 S 101.9 E (R about 1,517 km) used in hydro work of 13-14 Oct: WRONG by about 74 km along the bearing |

Kadri reception time, two branches carried in parallel:
- **T (text)**: 00:52:03 at H01W. Largest independent excursion in his Fig. 9c (hydro amendment A1).
- **C (caption / Table 1)**: 00:54:30 at H01W. A smaller real excursion.

Kadri eq. 4 check: impact lies Dr = c*Dt/(1+c/v) beyond the arc along the bearing at Delta T = Dt/(1+v/c)
after 00:19:29. With c = 1.48 km/s, v = 0-250 m/s: T gives impact 00:34:07-00:32:00, 0-188 km inside the arc;
C gives 00:36:34-00:34:06, 0-219 km inside. Kadri errata: he uses 00:54:00; 1,586 km/1.5 km/s = 17.62 min, not 17.45;
'1450 m/s' must be 450 m/s. Haixun as acoustic source: 00:34:24 (T) or 00:36:51 (C).

## 2. Hypotheses

- **H_K^T, H_K^C**: the 306.18 deg H01W arrival at time T or C is the sound of MH370 entering the water.
- **H_H**: the Haixun 01 37.5 kHz contact of 4-5 Apr 2014 came from an MH370 recorder beacon on the seabed within 2 km of 25.975 S 101.461 E.
- **Locality L**: the bearing strip from R7 - 60 km to R7 + 250 km (half-width = range x tan(1 deg)), plus discs of 50/100/200/400 km around the arc crossing and around Haixun.
- Complement in every case: the rest of the run J posterior.

## 3. Quantities and statistics (fixed now)

Q1 Flight: run J posterior mass in L (each disc, the strip), by 00:19 option, family (A1/A2/B), log-on cause; effective sample size and distinct parents in L; impact time distribution in L.
Q2 Per-row acoustic likelihood: for each run J impact row i, predicted H01W arrival t_i + d_i/c and bearing b_i;
   L_i = N(t_obs - t_pred; 0, s_t) x N(b_obs - b_i; 0, s_b); s_t^2 = (d_i x 0.015/1.48)^2/1.48^2 + 5^2 s; s_b = 0.5 deg (core) / 1.0 deg (wide).
   Background: a chance arrival uniform over the 00:36-00:57 window and over bearings 200-340 deg, rate taken from Kadri Table 1 (18 transients in 21 min).
   Report Bayes factor B = sum_i w_i L_i / L_background for T and C, and the conditional PDF given each branch.
Q3 Trajectory character of the best-fitting rows (top 1 % of w_i L_i): BTO/BFO residuals at every arc, fuel-exhaustion time, minutes aloft after exhaustion, turns, descent family, impact speed, angle, energy, tau90, attitude.
Q4 Other stations: predicted arrival windows (95 %) at Perth Canyon IMOS 3376/3315, H08S and the OHASISBIO moorings (Royer LDO-201608 Table 1) for both branches and both centres; path blockage; tested with the existing statistics and levels (0.3 screen, 0.1 mark, 0.05 report; floor 1/n_background).
Q5 Haixun beacon physics: P(detect | beacon at seabed depth under Haixun) from the sonar equation (DK100 source level, 37.5 kHz absorption, sound-speed profile refraction, ambient and boat noise, hand-held hydrophone bandwidth and gain); geometry test of two contacts 2-3 km apart; P(HMS Echo / HMS Tireless / Ocean Shield miss | beacon present). Report B_H = P(data | H_H) / P(data | not H_H).
Q6 Searched areas: 2014 surface-search boxes covering L by day (GA/AMSA polygons) with the CSIRO POD treatment; seabed sonar coverage (ATSB Phase 2, OI 2018, OI 2025-26) and bathymetry-only coverage in L; likelihood terms per hypothesis.
Q7 Drift: finds likelihood (flaperon and other items with beaching windows) and WA / northern-coast non-detection for releases in L, against the run J reference; forward drift from L to 4-5 Apr 2014 and to the white-object sighting.
Q8 Settling: seabed displacement of recorders and heavy parts from impacts in L; seabed depth at Haixun and the crossing.

## 4. Combination and reporting rules

- Composed: P(H | all) proportional to prior mass in L x product of module likelihood ratios; each evidence type enters once (surface search is never folded into drift).
- Hydroacoustic caveats travel with every hydro number (propagation slope misfit; coupling uncertainty).
- Absences from partial coverage are reported as 'not assessed', not as non-detections.
- Charts: no project codes in titles, axes or legends; two footnotes (plain ASD-STE100 and technical) listing source posterior, 00:19 option, physics status, search case, ocean model, exclusions.
