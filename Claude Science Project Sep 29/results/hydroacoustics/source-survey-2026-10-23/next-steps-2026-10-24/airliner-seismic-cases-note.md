# Swissair 111 as a seismic ground-truth case for the energy of an airliner hitting the sea, and an open-archive check of nine other airliner sea impacts

EXPLORATORY. Nothing in this note returns a likelihood to the composer. Date: 24 Oct 2026.

## 1. Main findings

1. **The UTC date is 3 September 1998, not 2 September.** TSB A98H0003 footnote 1 says that in UTC the flight occurred on 3 September 1998. The impact time was 01:31:18 UTC on 3 Sep (22:31 ADT on 2 Sep). The task window (2 Sep 01:25-01:45) is one day early.
2. **The impact is in the Canadian national catalogue.** Earthquakes Canada event 19980903.0131003 has origin 01:31:17.0 UTC. Its epicentre is fixed at the wreck (44.4094 N, 63.9738 W) and its depth is 0 (operator assigned). The magnitude is 0.57: the FDSN service labels it "MwN", which is the Canadian Nuttli-type MN. The event type is "mining explosion" (the CN class for non-earthquakes) and the description reads "Swiss air crash flight 111". ISC and USGS ComCat have no event for 3 Sep 1998 near the site.
3. **One open waveform record holds the impact: CN.LMN (Caledonia Mountain NB, CMG-3T, 40 sps, 173.4 km).**
   - Onsets (AIC, 3-15 Hz): P at 27.5 s and S at 48.3-48.4 s after 01:31:18. S-P is 20.83 s, which gives a distance of 175-181 km (true distance 173.4 km).
   - Origin time from the picks: -1.4 to +0.9 s relative to 01:31:18. This agrees with the TSB time and with the CN catalogue time of 01:31:17.0.
   - Detection: empirical p = 0.022, at the p floor (0 of 44 noise windows exceed; floor 1/45). Peak SNR 17.3 on BHZ at 3-15 Hz.
   - Peak ground velocity: 17-39 nm/s per component, depending on band. The 3-component vector PGV is 40.5 nm/s (1.5-18 Hz).
   - Duration above noise (3-15 Hz power): 44 s at 3x the noise median and 64 s at 2x. This duration comes mostly from the Lg coda (propagation), not from the source. **It must not be used as an impact duration, and it must not go to end of flight.**
   - Spectrum: the signal sits in a band of about 2-12 Hz, with a sharp maximum in the 8 Hz third-octave band (amplitude SNR 7.1 in the S window and 6.6 in the P window). It is buried below about 1.5 Hz. The quarter-wave frequency of the 55 m water layer is 6.8 Hz, so the peak is *consistent with* a water-layer resonance. This is not tested, because no co-located land source was available for comparison.
   - A 2-sample impulse at +102.35 s appears on all three components at the same sample, with no dispersion and no coda. It is a probable instrumental glitch and is excluded.
   - No air-coupled arrival at LMN (0.31-0.35 km/s window, about 495-559 s). Smallest p = 0.22 (BHE, 1-15 Hz; p floor 0.031; 6 tests, uncorrected).
4. **Magnitude.** Five land events recorded at LMN in 1995-1999, at 134-169 km, were measured the same way: blasts near Bridgewater NS, in southern NB and near Oromocto NB, and an earthquake SE of Truro NS. On these events my Nuttli-formula value exceeds the catalogue MN by 0.57 ± 0.15, and for the impact the offset is 0.74. Scaling from each reference gives impact MN 0.74 ± 0.15 (1-15 Hz) and 0.58 ± 0.13 (3-15 Hz), which reproduces the catalogue value of 0.57. Hutton-Boore ML (California attenuation, indicative only) is 1.41. The average eastern-Canada offset MN − Mw = 0.5 (Bent 2011) gives Mw about 0.07-0.24. This is not a moment measurement.
5. **Radiated seismic energy and seismic coupling (NEW CLASS S1, provisional).**
   - Definition of S1: radiated seismic energy in regional P and S/Lg recorded on land, divided by the impact kinetic energy. **S1 is a different definition from the hydroacoustic coupling classes D1-D4 and from the Arons definition used by Brown et al. 2026 (about 1e-4). The values must not be mixed or compared as equals.**
   - Impact kinetic energy: 2.74e9 J (range 2.39e9 to 2.92e9 J), for 215-230 t at 290-310 kn.
   - Direct energy-flux estimate (1.5-17 Hz, noise-subtracted, 12 combinations of spreading, Q and free-surface factor): 1.5e3 to 3.7e4 J (median 7.8e3 J). This is band-limited and is a lower bound for the full band.
   - Earthquake magnitude-energy relations applied to MN 0.57-0.74 give 3.2e4 to 8.1e5 J.
   - On the five reference events, the same direct method gives log10(Es) − 1.5·MN = 3.55 ± 0.18. The impact gives 2.42. In 1.5-17 Hz the impact therefore radiates about 10× less energy than a land event of the same catalogue magnitude. Part of this difference can be a low-SNR effect (the noise subtraction removes most of the energy in bands where SNR is near 1). I do not interpret it further.
   - **S1 = 5e-7 to 1.5e-5 (direct method), 1.1e-5 to 3.4e-4 (magnitude relations), 5e-7 to 3.4e-4 overall.** The value is provisional and spans about three orders of magnitude.
6. **Non-detections for Swissair 111.** CN.GSQ (555 km): p = 1.0, p floor 0.056, predicted SNR 0.86. IU.HRV (649 km): p = 0.27, p floor 0.067, predicted SNR 0.36. The HRV window maximum is at +143.9 s, between the predicted Pg and Lg times. Both results are no significant detection with limited power.
7. **Halifax record.** The TSB names seismographs at Halifax and Moncton. CN.HAL has no 1998 epoch in the CNDC FDSN service; its metadata begin on 2003-01-13. The 1998 Halifax record is therefore not in the open archive. CN.GGN (240 km) returned no data. The TSB "Moncton" record is assumed to be LMN, about 70 km SW of Moncton. This is an assumption.
8. **Hydroacoustics, Swissair 111.** The TSB report holds no hydrophone or hydroacoustic record. Its acoustic content is: the submarine HMCS Okanagan homed in on the flight-recorder underwater locator beacons (ULB); a laser line scan and side-scan sonar survey mapped the wreckage; the ULBs were damaged and nearly detached. SOSUS is not public, and IMS hydroacoustic data are request-only (vDEC), which the standing rules exclude. I found no Canadian or US research hydrophone record for 1998 near Nova Scotia. **No hydroacoustic record found.**
9. **Nine other airliner sea impacts, open-archive check** (Figure 2 and the case table):
   - No catalogue event (ComCat or ISC) for any case. For Alaska 261 the SCSN catalogue lists only an unrelated earthquake (Ludlow) and a quarry blast (Johannesburg CA).
   - Open waveforms were returned and tested for 7 of the 9 cases (TWA 800, EgyptAir 990, Alaska 261, Flash 604, EgyptAir 804, Lion Air 610, Sriwijaya 182). Adam Air 574 (only II.KAPI, at 231 km) and Ethiopian 409 (50 stations listed at 62-340 km) returned no data (HTTP 204).
   - Smallest per-case p-values:

     | case | smallest p | station | p floor | Bonferroni |
     |---|---|---|---|---|
     | Alaska 261 | 0.032 | CI.TOV | 0.032 | 0.19 over 6 stations |
     | Flash 604 | 0.077 | ZR.JS07 | 0.038 | 0.31 |
     | EgyptAir 990 | 0.125 | US.LSCT, 327 km | 0.063 | — |
     | Lion Air 610 | 0.158 | AM.RA578 | — | — |
     | Sriwijaya 182 | 0.37 | GE.BBJI | — | — |
     | EgyptAir 804 | 0.50 | CQ.OSC1 | 0.167 | — |
     | TWA 800 | 0.74 | LD.PAL | — | — |

   - **Alaska 261, CI.TOV.** The window maxima at six stations imply origin times scattered from −58 to +67 s, so there is no coherent moveout. The two nearest stations (26-28 km) give p = 0.65. The open coastal stations are noisy: 64-1,590 nm/s RMS in 1-8 Hz, against 1.3-7 nm/s at LMN. A source the size of Swissair 111 would give a predicted SNR of only 0.05-2.2 at these stations (indicative, using eastern-Canada attenuation). The non-detection is therefore not informative about source size.
   - **Flash 604, ZR.JS07.** The value is below the 0.1 mark level but above the 0.05 report level. It is not corroborated at three other sites 9-62 km further away (p 0.57-0.73).
   - All of these are no significant detection with limited power. A likelihood ratio is not computed for any test, because no calibrated signal model exists for STA/LTA maxima.
10. **Literature.** About 10 web searches found no published seismic analysis of any of these airliner sea impacts. The TSB one-sentence statement for Swissair 111 is the only documentary record found. **The brief's statement that the TWA 800 seismic record is documented in the NTSB docket and literature was not confirmed by my searches. The NTSB docket was not searched item by item.** Kadri et al. 2024 (Sci. Rep., doi 10.1038/s41598-024-60529-1) report hydroacoustic signals at IMS stations for other crashes, including Sriwijaya 182 at H08S. That is the project's existing hydroacoustic analogue set, not a seismic record. Related land-impact context: Kim et al. (LDEO) found that the WTC aircraft impacts were recorded at 1.3-1.6 Hz, and that no clear signal could be associated with the Pentagon impact.

**Standing caveats.** (1) The project propagation model fails the frequency-slope check against the 2001 airguns (+10 dB/octave at H01W, +7 dB/octave at H08S), although levels pass. That model is not used here, but any later use of S1 with that model inherits this caveat. (2) Detection probability is a proxy and is not measured on real data. Every non-detection above is "no significant detection with limited power", not absence of signal.

## 2. Method

- **Data.** Earthquakes Canada CNDC FDSN (station, dataselect, event); EarthScope FDSN and the IRIS federated catalogue; SCEDC, GEOFON, NOA, KOERI and Raspberry Shake FDSN; ISC and USGS ComCat event services. All are open and need no registration.
- **Processing.** Demean and detrend, 2 % taper, removal of the full instrument response to velocity (pre-filter 0.3-0.5 Hz to 0.45-0.48 fs, water level 60). Band-pass filters are 4-pole Butterworth: zero-phase for amplitudes, causal for picks.
- **Picks.** AIC picker in 15-40 s (P) and 42-58 s (S) after 01:31:18.
- **Detection statistic.** Recursive STA/LTA (1 s/30 s). The statistic is the maximum in the window from P (6.4 km/s) minus 3 s to Lg (3.0 km/s) plus 15 s, widened by the impact-time uncertainty. The empirical p is (k+1)/(n+1), where the null is non-overlapping same-length windows from the ±40 min record (±17-20 min for Swissair). The p floor 1/(n+1) is reported for every value.
- **Magnitude.** Nuttli >4° formula mN = 3.30 + 1.66 log Δ + log(A/T), with A/T = peak vertical Lg velocity/2π in µm/s (Canadian usage: high frequency, >4° formula at all distances). The impact magnitude is computed relative to five catalogued events at the same station. Wood-Anderson ML uses the IASPEI form with gain 1.
- **Energy.** Es = 4πρβ ∫v² dt · exp(2πfr/(Qβ)) · free-surface factor / G(r)², in half-octave bands from 1.5 to 17 Hz, for P (6.1 km/s) and S/Lg (3.5 km/s) windows, with the noise energy subtracted. ρ = 2700 kg/m³. G is either 1/r, or trilinear (1/R to 70 km, flat to 130 km, R^-0.5 beyond; Atkinson-Boore type). Q is 680 f^0.36, 893 f^0.32 or 500 f^0.5. The free-surface energy factor is 0.25 or 1. These are literature-type values chosen for this work; they were not fitted to these data.
- **Kinetic energy.** ½mv². The mass is 230 t, the gross weight the crew reported at 01:21:20 (TSB), down to 215 t. The 215 t value is my allowance: fuel dumping began after 01:25:41 and stopped before impact, and the amount is not established. The speed is 300 kn indicated airspeed (TSB airspeed-indicator marks), with 290-310 kn assumed and IAS taken as TAS at sea level.
- **Archive scan.** For each case: the IRIS federated catalogue lists stations within 3°, kept to ≤ 340 km. The nearest stations are tried in order of distance (HHZ > BHZ > EHZ > SHZ, with a fallback to BHZ when a channel returns no data), until 4 stations have data or 14 have been tried. The Swissair detection statistic is then applied.

## 3. Deviations (scope reductions and substitutions)

1. Date corrected from 2 to 3 Sep 1998 UTC (from the TSB). The first downloads, for the wrong day, were discarded.
2. The Halifax 1998 record is not in the open archive (CN.HAL epochs start in 2003). "Moncton" is assumed to be CN.LMN. CN.GGN returned no data. No data were requested from any agency.
3. Energy is band-limited to 1.5-17 Hz. Spreading, Q and free-surface values are assumed, not fitted. The magnitude-energy relations are earthquake relations applied to a surface impact. S1 is provisional.
4. The impact mass of 215-230 t and the speed of 290-310 kn are assumed ranges (see Method).
5. Nine further cases were scanned. **Not scanned:** AF447 (no land station is near), Yemenia 626, AirAsia 8501, and any other airliner sea impacts. This was a time budget decision.
6. Scan limits: radius 340 km; at most 4 stations per case (Alaska 261 extended to 6 in a supplementary interactive run). Only vertical channels; one band per sample rate.
7. Positions and times for the nine cases come from Wikipedia infoboxes and texts. These quote the NTSB, the Lebanese report and others, but the primary reports were not opened. Time windows are widened by ±60 to ±300 s. The EgyptAir 804 position is the last known position, not the wreck. The Flash 604 position is given to 1 arcmin.
8. Raspberry Shake (AM) amplitudes and SNR predictions are not used, because the response was not verified (one station returns an implausible noise level of 1.4e11 nm/s). Their STA/LTA p-values do not depend on units and are kept.
9. A first parallel (threaded) scan mixed up station lists between cases. It was discarded and rerun one case at a time. ISC rate limits (HTTP 429) were handled with retries.
10. Water depths are given only where a source was seen (Swissair 111 55 m, TSB; EgyptAir 990 about 80 m, Canadian Encyclopedia; Sriwijaya 182 20-23 m, press report). The other depths are not compiled. Impact kinetic energy is computed only for Swissair 111.
11. The literature search was limited to about 10 web searches. The NTSB dockets (TWA 800, EgyptAir 990, Alaska 261) were not searched item by item.
12. A likelihood ratio is not computed for any test. Detection probability is not measured.

## 4. Files

- Summary table, Swissair 111: [swissair111-seismic.csv]({{artifact:652b61c4-60b1-4683-a229-801904a9b121}})
- Reference events at LMN: [swissair111-reference-events-lmn.csv]({{artifact:f3b18064-5e71-437a-9eb4-9c93aebef428}})
- Energy sensitivity grid: [swissair111-energy-sensitivity.csv]({{artifact:20e3cf81-6c68-4733-b2c0-8288f79d7873}})
- Third-octave band SNR: [swissair111-lmn-band-snr.csv]({{artifact:3348427a-cca4-400c-9a4b-80c1c9df052f}})
- Detection tests (LMN, GSQ, HRV, air-coupled): [swissair111-detection-tests.csv]({{artifact:7675d778-8c4e-4c9e-b5b4-87a26a074120}})
- Case table: [airliner-ocean-impacts-seismic-cases.csv]({{artifact:4aa5cc0f-1e6d-484f-b548-da60aed3ffcf}})
- Station tests (rank, p, p floor, SNR, LR column): [airliner-ocean-impacts-station-tests.csv]({{artifact:570ba94c-873a-41d4-92e3-c96ab1605ff5}})
- Figure 1, LMN record: [swissair111-lmn-record.png]({{artifact:f709f291-1508-499d-a97d-624d97ba6517}})
- Figure 2, archive check: [airliner-ocean-impacts-archive-check.png]({{artifact:4ca34d5c-4ba7-4f24-a695-883e31df5d30}})
- Scripts: [swissair111_seismic.py]({{artifact:f2e9c277-40f8-46c5-aa90-e4af232deb67}}), [airliner_archive_scan.py]({{artifact:a0f71f23-81e9-43b6-9a29-4a74e57e59f8}}), [make_figures.py]({{artifact:94f5c5bc-7f66-4f6a-bd7f-725906bef2bf}})
- Raw miniSEED and StationXML: [swissair111-waveforms-1998.tar.gz]({{artifact:560885ff-1182-481b-a908-9bba0c28efd1}})
