# Antarctic moorings (AADC) as extra public receivers for 8 March 2014

Status: **exploratory**. Nothing here returns a likelihood to the composer. No waveform was analysed. Date: 24 Oct 2026.

## 1. Verdict

1. **The recordings exist, but you cannot download them without a request.** Casey2014 and Kerguelen2014 recorded continuously, in 1-h WAV files at 12 kHz. All 12 hourly files for 7 Mar 18:00 - 8 Mar 06:00 UTC exist at each site. The AADC portal gives an anonymous file listing. File download (WAV, README, LICENSE, `.meta`) returns HTTP 401. The download page shows an email form. AADC then sends a one-time zip link or S3 keys for `transfer.data.aad.gov.au`. This is an email-gated request. It does not need an account. I did not submit it on your behalf (standing rule). Therefore I stopped at step 1, plus the geometric assessment (step 4 of the brief).
2. **The IWC-SORP annotated library uses the same gate.** It also has no file in the window. Its nearest sub-sampled hours are Casey 8 Mar 06:00 (which starts at the end of the window) and Kerguelen 8 Mar 19:00.
3. **The moorings are a weak test of an impact on the arc.** Paths from the arc (20-40 S) are 2,496-5,023 km long. At 20-32.5 S that is 8-14 dB more spreading plus attenuation than to H01W; at 37.5-40 S it is close to the H01W value. That figure does not include the polar transition. Both hydrophones sit near the seabed, far below the polar sound-speed minimum (65-70 m deep in WOA23 Jan-Mar):
   - **S Kerguelen (2,000 m):** every path from the arc first crosses a rise with seafloor at 1,176-1,515 m depth, 190-359 km before the mooring. With a conserved turning speed, sound from the arc cannot reach 2,000 m without touching the seafloor at that rise (0 % refracted-only band, at all 9 arc points).
   - **Casey (2,700 m):** for 7 of 9 arc points, the shallowest seafloor south of 50 S is 2,918-3,347 m, which is deeper than the hydrophone. For those points, only source-axis launch angles from 5.7-6.3° up to 8.3-9.9° reach 2,700 m without seafloor contact. That is 16-36 % of the source channel's refracted angle band, and it excludes the low-angle (axial) energy. The paths from 35 S and 37.5 S cross rises at 2,489 m (59.79 S 107.14 E) and 2,272 m (55.52 S 101.06 E), so for them the refracted-only band is 0 %. These two are single ETOPO1 nodes and need a check at full resolution.
   - Both receivers are also reached only by rays that reflect from the surface south of the Polar Front (c_t > 1,445 m/s surface speed), so surface and sea-ice scattering add loss.
4. **The moorings would be a strong independent check on Royer's southern events.** For all 10 Royer 2016 events south of 50 S, one of the moorings is closer than Royer's nearest receiver: 260-1,427 km against 1,150-3,572 km. The moorings are also south of the events, but all of Royer's receivers are north or west. Their timing would therefore reduce the location ambiguity that Royer reports. Example: icequake A (57.30 S 88.965 E, 00:16:29.4) is 693 km from S Kerguelen (predicted arrival 00:24:17) and 1,435 km from Casey (00:32:38). These arrivals fall in the `201_2014-03-08_00-00-00.wav` and `200_2014-03-08_00-00-00.wav` files.
5. **What it takes:** you submit one email request to AADC (free, no account). Then download 6 files (00:00-03:00 UTC, two sites, about 0.52 GB) or 24 files (18:00-06:00, about 2.07 GB) by S3 from the listed object names. The calibration to Pa also needs the ADC full-scale voltage or the `.meta` sidecars (see section 3).

Standing caveats for any later hydroacoustic use: (1) the propagation model fails the frequency-slope check against the 2001 airguns (+10 dB/octave at H01W, +7 dB/octave at H08S), although levels pass; (2) detection probability is a proxy unless it is measured on real data. Here no data were analysed. So there is no detection claim, no upper limit and no p-value in this note.

## 2. Data access (table: aadc-2014-access.csv)

| Item | Casey2014 | Kerguelen2014 |
|---|---|---|
| AADC EDS id / uuid | 4501 / 0de1a2b9-80b7-44e5-8b33-be0c65dedeba | 4502 / 4ab9d372-f6e8-4fd0-bbc5-1b039400513e |
| Collection DOI | 10.26179/fhsv-ft93 (Ver. 9, Miller, Milnes & Whiteside) | same |
| Position, depth | 63.7955 S 111.7871 E, 2,700 m | 62.3801 S 81.7968 E, 2,000 m (1,980 m in Front Mar Sci 2022 Table 1) |
| ETOPO1 depth at that node | 2,895 m | 1,754 m (3-arc-min slope node; published depth used) |
| WAV files / size | 8,471 / 729.4 GB | 10,445 / 897.1 GB |
| First / last file | 200_2013-12-25_01-20-36.wav / 200_2014-12-12_23-00-00.wav | 201_2014-02-10_00-18-36.wav / 201_2015-04-21_04-00-00.wav |
| Window files | 12 of 12 (200_2014-03-07_18-00-00.wav ... 200_2014-03-08_05-00-00.wav) | 12 of 12 (201_...) |
| Sample rate, duty cycle | 12 kHz nominal, continuous, 1-h files (86.4 MB each, consistent with 16-bit mono) | same |
| Anonymous listing / download | yes / no (HTTP 401) | yes / no (HTTP 401) |

File naming: `<deployment code>_<YYYY-MM-DD>_<HH-MM-SS>.wav`, start time UTC from the recorder's real-time clock (AADC record). Each WAV has a `.meta` sidecar in `<code>_<site>_meta/` (about 400 bytes; not readable without access). Note that the Kerguelen recording starts on 10 Feb 2014. Miller et al. 2021 Table 2 gives 22 Feb 2014, which is the start of the annotation subset.

## 3. Calibration (what is public)

- Hydrophone HTI-90-U, nominal sensitivity −165 dB re 1 V/µPa, flat 2 Hz-20 kHz. Preamplifier gain +20 dB. AC coupling with a −3 dB corner at 6.6 Hz (Miller et al. 2018, Sci Rep, PMC5882826).
- ADC: AD7683B, 16-bit, 86 dB SINAD (AADC record).
- **Not found in public, readable form:** the ADC full-scale voltage and the per-unit calibration. Without them, counts cannot be converted to Pa. The `.meta` sidecars may hold them, but they are behind the same gate.
- Effect on this work: the band below about 6.6 Hz is reduced by the AC coupling. Impact and T-phase energy is often strongest at 2-10 Hz, so a correction would be needed.

## 4. Geometry and propagation screening (tables: aadc-arc-path-geometry.csv, aadc-receiver-depth-screening.csv, aadc-extra-loss-vs-H01W.csv)

Method: 9 arc points (20-40 S every 2.5°) on the ATSB 7th arc at FL400 (repo backup `seventh_arc_fl400.geojson`). WGS84 great circles, sampled every 10 km. Seafloor from ETOPO1 (ERDDAP `etopo180`, 3 arc-min stride, nearest node). Sound speed from WOA23 decav 1.00°, season 13 (Jan-Mar), Mackenzie (1981), nearest cell every 50 km. The Polar Front is fixed at 50 S for screening only.

- Distances (km): Casey 3,197 (40 S) to 4,895 (20 S); Kerguelen 2,496 (40 S) to 5,023 (20 S). H01W: 1,551-2,680.
- Back-azimuths at the moorings: Casey 313-350°; Kerguelen 5-31°.
- No path crosses land. No path has seafloor shallower than the local sound-speed-minimum depth north of 50 S. The Casey paths from 20, 27.5 and 30 S cross local highs at 1,285-2,117 m between 22 S and 32.5 S. These are below the axis (900-1,100 m there), but they limit the lower channel.
- Extra loss relative to H01W (spreading 10 log r plus 0.003 dB/km, the Thorp constant term at 10 Hz): Casey 2.3-13.1 dB, Kerguelen −0.9 to 13.6 dB. The largest values are for the northern arc. This excludes the polar-transition loss, which is not modelled here.
- Receiver-depth screening (declared rule, range-independent): c_t = c_axis / cos θ is held constant along the path. A ray reaches receiver depth z_r if c_t ≥ c(z_r). It touches the seafloor at a rise if c_t > c(rise depth). Casey: c(2,700 m) = 1,493.4 m/s against a source-axis speed of 1,484.5-1,486.1 m/s. The rise search covers the whole path south of 50 S, excluding the last 20 km. Kerguelen: c(2,000 m) = 1,484.8 m/s, but c at the rise depth is 1,473.9-1,477.4 m/s, so no refracted-only ray reaches 2,000 m. This screening is an approximation. In a range-dependent channel the turning speed is not exactly conserved (mode or action invariance applies instead). The qualitative result is the same: low-order (axial) energy goes into the polar surface duct, which is far above both hydrophones.

## 5. Predicted arrivals (tables: aadc-predicted-arrivals-known-events.csv, aadc-royer-southern-events-ranges.csv)

Rule: great-circle distance / 1.48 km/s, with no seismic leg for earthquakes. Note that south of the Antarctic convergence the sound channel is shallow or at the surface, so the true group speed can be lower. A second time uses the path-mean WOA23 minimum sound speed, which is 0.3-1.1 % later on the arc paths.

- Impact on the arc (core 00:15-01:05 UTC, tail to 02:00): S Kerguelen 00:43-02:01 (tail to 02:56); Casey 00:50-02:00 (tail to 02:55). Files 00, 01 and 02 UTC at both sites.
- The same window holds predicted arrivals of all 20 Royer 2016 events and 15 catalogued earthquakes (23:00-04:00 span at each mooring). Royer #6 to Kerguelen is blocked by land. Royer #6 to Casey crosses the shelf (minimum depth 80 m).
- Catalogued earthquakes with an arrival in 7 Mar 18:00 - 8 Mar 06:00 at either mooring: 43 (86 event-receiver rows). Paths from the Banda Sea, New Guinea and SW Pacific are blocked by land.
- Antarctic blue whale Z-calls: no cross-check was possible. The SEANOE OHASISBIO file has 65 Z-call detections at WKER in 00:25-02:50 UTC. The library annotation table `Kerguelen2014.Bm.Ant-Z.selections.txt` exists, but its 8 Mar hour is 19:00, and it is gated.

## 6. Deviations

- Steps 2(a)-(c) were not done: no WAV, `.meta` or README could be downloaded without the email request. `aadc-8mar2014-detections.csv` was therefore not produced. No spectrograms, band levels, detections, p-values, SNRs or likelihood ratios exist for these moorings.
- Calibration to Pa was not possible: the ADC full-scale voltage is not public in a readable record.
- Recorder depths come from published tables (Miller et al. 2018; Front Mar Sci 2022), not from the gated `.meta` files.
- Substituted environment: WOA23 Jan-Mar climatology, not in-situ 2014 profiles. ETOPO1 at a 3-arc-min stride, not full 1-arc-min resolution.
- A first pass searched for rises only in the last 500 km. It missed the two Casey rises (35 and 37.5 S). The tables and figures here use the whole-path search.
- Arc: the ATSB 7th arc at FL400 from a repo backup file, not the project's run-J impact PDF. The arc was sampled at 9 points; no prior-weighted sampling was done.
- The Polar Front was fixed at 50 S, a simplification.
- Earthquake arrivals use epicentral distance at 1.48 km/s, with no seismic-leg term (the catalogue review used one).

## 7. Sources

- AADC metadata AAS_4102_longTermAcousticRecordings, doi:10.26179/fhsv-ft93; EDS API `https://data.aad.gov.au/eds/api/dataset/<id>` and `/objects`; library AcousticTrends_BlueFinLibrary, doi:10.26179/5e6056035c01b (EDS 5091).
- Miller B.S. et al. 2021, Sci Rep 11:806, doi:10.1038/s41598-020-78995-8 (Table 2 positions).
- Miller B.S. et al. 2018, Sci Rep, sperm whale occupancy (PMC5882826), Table 3 depths and hydrophone details.
- Front Mar Sci 2022, doi:10.3389/fmars.2022.864153, Table 1 (Kerguelen2014 depth 1,980 m).
- Royer 2016 LDO-201608 Table 4 (via hydro_data.sqlite `dg_royer_2016_royer_events`, `dg_royer_2016_royer_stations`).
- ETOPO1 via NOAA CoastWatch ERDDAP `etopo180`; WOA23 via NCEI THREDDS OPeNDAP.

## 8. Files

Scripts: `aadc_access_table.py`, `aadc_geometry.py`, `aadc_royer_check.py`, `aadc_figures.py` (run in the kernel after the figure-style skill). Raw API returns: `aadc-api-returns.zip`.
