# Geostationary imagers that viewed the aircraft's region, 7–8 March 2014

Track: continuously recording geostationary (GEO) imagers. The question is whether any of them imaged the aircraft's track, and where the data are held. The realistic signature is a condensation trail seen in thermal infrared. Notes written 21 Oct 2026.

## 0. Scope change (21 Oct 2026, after the contrail-physics result)

The parallel contrail-physics track ([contrail-notes.md]({{artifact:df5975a4-f83f-4243-a3bd-e3ebc993e003}})) found that ERA5 gives no ice supersaturation at FL300–FL400 along the run J posterior routes after 18:22. The posterior probability that a contrail formed and persisted is below 1e-6. Any short-lived contrail would be about 0.1 km wide and gone within minutes, so it would be narrower than every geostationary pixel here (4–10 km). On the known track 16:42–17:20 the air at FL350 was too warm for a contrail, but ice-supersaturated air existed at FL390–FL400 between Kuala Lumpur and IGARI.

What changed in this track:

1. **Unchanged:** the coincidence and geometry tables. All 148,000 routes, all 107 scan events and all archive checks are complete.
2. **Changed:** imagery is framed as a confirmation and positive-control check, not an open search. The two primary figures are:
   - [geo_top3_passes.png]({{artifact:057adca0-0033-4395-9225-90173f48c5ed}}): the two top-ranked passes plus the best-ranked MTSAT-2 pass, ranked by clear-sky fraction per effective pixel in [geo_top_pass_ranking.csv]({{artifact:22d77030-a2b7-4bb6-9982-0c26f81392ba}}). These are FY-2D 19:31 (rank 1; VZA 9.0°, 5.0 km), FY-2D 21:01 (rank 2; 18.6°, 5.2 km) and MTSAT-2 18:31 (rank 5; 58.4°, 5.9 km). MTSAT-2 was included so a second satellite is represented. FY-2D 21:31 (rank 3) and 20:31 (rank 4) appear only in the supplementary FY-2D figure.
   - [geo_positive_control_radar_segment.png]({{artifact:cea2dbbd-9c62-4560-9012-01e28bfe5dd6}}): the calibration case, FY-2D 16:31 and MTSAT-2 17:31 along the radar track, with the 16:42–17:20 Kuala Lumpur–IGARI segment highlighted.
3. **Visual result of the control check (not a detection test).** No straight linear feature is visible along the Kuala Lumpur–IGARI segment, or elsewhere in either control scene, at the rendered scale. MTSAT-2 at 17:31 shows patchy thin cloud with a positive split-window difference south-west of Kuala Lumpur (about 3–4° N, 99–101° E). Its link to the ERA5 ice-supersaturated layer was not tested. The control therefore shows that these images can show thin ice cloud. It does not establish that they could show a single aircraft contrail.
4. **Supplementary only:** the eight-scan FY-2D and nine-scan MTSAT-2 panel figures in section 4 were made before the scope change. They are kept for completeness.
5. **Archive checks for the gated holders, re-attempted.** The NSMC portal is reachable, but its file-level search is a login- and JavaScript-driven page with no scriptable endpoint. MOSDAC's archive catalogue needs a login. The KMA data service returned HTTP 503. These three remain "not verified".

## 1. Summary

1. Twelve GEO imagers were in orbit with a view of 10° N–45° S, 75–110° E. Nine of them were imaging operationally on 7–8 March 2014: FY-2D (86.5° E), FY-2E (104.1° E), INSAT-3A (93.4° E), INSAT-3D (82.0° E), Kalpana-1 (73.9° E), Elektro-L N1 (76.0° E, imager degraded), COMS-1 (128.2° E), Meteosat-7 (57.6° E) and MTSAT-2 (145.0° E). FY-2F (111.6° E) was on regional/on-demand duty. FY-2C (123.4° E) and MTSAT-1R (140.0° E) were standby units. Positions come from the space-track element set nearest 20:00 UTC 7 Mar 2014 (grade A).
2. View geometry along the posterior routes after 18:01:49 at FL350 (weighted median): FY-2D 8.6–42.0°, FY-2E 7.7–43.5°, INSAT-3A 0.3–42.2° and INSAT-3D 13.6–42.9° view zenith angle; MTSAT-2 was the most oblique at 53.2–70.8°. Effective IR pixel size at the aircraft was 4.1–4.9 km (INSAT-3D), 4.2–4.9 km (Elektro-L), 5.0–6.1 km (FY-2D/E) and 5.5–7.7 km (MTSAT-2). Kalpana-1 and INSAT-3A were coarser at 8.0–10.0 km (8 km nadir). Source: [geo_sensor_table.csv]({{artifact:379293ae-79d3-41f6-bdc2-db7893f6d9f2}}), [geo_view_geometry_vs_time.png]({{artifact:6b2e58e9-1425-4591-854b-30521d0b8df4}}).
3. Darkness: the Sun was below −6° at the aircraft until about 23:28 UTC; sunrise at the median position was about 23:56 UTC (at 10.7 km altitude). The Moon (43 % illuminated) was below the horizon at the aircraft for the whole period from 16:42 UTC (JPL DE421). **No moonlit-contrail opportunity existed.** Until twilight, only thermal-infrared channels could show a contrail.
4. Two archives were anonymously downloadable at full resolution, and both were fetched and rendered:
   - MTSAT-2: every scan 16:31–00:32 UTC, native HRIT plus 0.04° gridded, at Chiba University CEReS.
   - FY-2D: re-encoded full-resolution HRIT at CEReS.
5. Meteosat-7: the EUMETSAT Data Store catalogue (anonymous search) lists 14 MVIRI scans on 7–8 Mar 2014 from 16:00 to 01:00 UTC. The 19:00, 19:30, 20:00, 20:30 and 21:00 UTC slots are absent. Download needs a free account, so these scans are in the query list.
6. INSAT-3D/3A and Kalpana-1 (MOSDAC), FY-2E (NSMC), COMS-1 (KMA) and Elektro-L N1 (SRC Planeta) all need registration or a request. Their scans are in [geo_query_list.csv]({{artifact:39655a7b-dd85-4789-9bb9-01e3d58f97db}}) (87 rows) with time windows and search boxes.
7. The contrail-physics result makes a persistent contrail very unlikely (section 0), so the imagery is a check. It is for inspection only; **no detection test was run**. On visual inspection of the rendered panels, no conspicuous straight cold line is visible at the posterior positions at the rendered scale. That is a visual remark, not a finding: a young contrail is narrower than one 4–6 km pixel.

## 2. Sensors and scan schedules (see sensor table for every source and grade)

Grades: A = operator document, archive header or catalogue; B = secondary technical source (NASA GSFC, eoPortal, WMO OSCAR); C = assumption from instrument class or general description; D = nothing found.

| Satellite | Position (element set) | IR / VIS nadir | Cadence on 7–8 Mar 2014 | Scan | Schedule grade |
|---|---|---|---|---|---|
| FY-2D | 86.46° E | 5 / 1.25 km | archived scans 15:31, 16:31, 19:31, 20:31, 21:01, 21:31, 22:31, 23:31, 00:30 (no scans 16:31–19:31 in the archive) | N→S, 2500 lines × 0.6 s = 25 min | B |
| FY-2E | 104.10° E | 5 / 1.25 km | hourly (start HH:00 assumed) | N→S 25 min | C |
| INSAT-3D | 82.05° E | 4 / 1 km (split window 10.8/12.0) | HH:00, HH:30 | 25–26 min, N→S assumed | C |
| INSAT-3A | 93.44° E | 8 / 2 km; CCD 1 km at 03–11 UTC only | hourly | N→S assumed | B (cadence A) |
| Kalpana-1 | 73.85° E (4.2° incl.) | 8 / 2 km | half-hourly (IMD history page also mentions 3-hourly triplets) | N→S (MOSDAC) | C |
| Elektro-L N1 | 76.02° E | 4 / 1 km, MWIR/TIR degraded | 30 min | N→S assumed | C |
| COMS-1 | 128.21° E | 4 / 1 km (split window) | full disc 8 times a day, every 3 h; 17:40, 20:40 and 23:40 in the flight window; sun intrusion 13:25–17:15 on 7 Mar | 27 min, N→S assumed | A (KMA weekly plan) |
| Meteosat-7 | 57.57° E (8.9° incl.) | 5 / 2.5 km, no split window | HH:00/HH:30, 25 min (catalogue); slots 19:00–21:00 absent | S→N | A |
| MTSAT-2 | 145.00° E | 4 / 1 km (split window) | full disc HH:31:15; half discs HH:00:53 (+HH:14:10); southern half at 18 and 00 UTC | N→S, 0.580 s/line, 26.6 min | A (HRIT header) |

Notes:

- **MTSAT-2 line timing is measured.** It comes from the native HRIT observation-time header: 17:32 full disc, line 1 at 17:31:15.5 and line 2750 at 17:57:49.5 UTC; the residual of a linear fit is 0.04 s. The southern half disc starts at 18:00:53.4 (lines 1–1375) and ends at 18:14:10.1. Other hours use the same offsets (grade B).
- **Half-disc hemispheres were checked against the data.** At 17 and 23 UTC both half-disc scans (HH:01, HH:14) are northern. At 18 and 00 UTC both are southern. Count 0 is the fill value outside the sector.
- **Eclipse-season gaps (inference, not verified).** The FY-2D gap 16:31–19:31 brackets FY-2D local midnight (18:14 UTC). The Meteosat-7 gap 19:00–21:00 brackets Meteosat-7 local midnight (20:10 UTC). Both are consistent with equinox eclipse outages of spin-stabilised imagers. Local midnights of the other satellites are in the sensor table: INSAT-3D 18:32, Elektro-L 18:56, Kalpana-1 19:05, INSAT-3A 17:46 and FY-2E 17:04 UTC. Similar gaps may affect those archives, so the queries ask the operators to confirm.
- **MTSAT-1R label.** The Malaysian 2015/2018 reports call the 17:32 UTC image "MTSAT-1R". MTSAT-2 was the operational imager from 1 Jul 2010 (JMA, CGMS-39), and the CEReS archive holds the MTSAT-2 17:31:15 full disc but no MTSAT-1R data for March 2014. The label is probably the series name; this is unconfirmed.

## 3. View geometry, pixel size and scan crossings

Methods:

- **Aircraft.** FL350 (10.668 km) was used throughout.
- **Positions.** Before 18:01:49 UTC, the Geoscience Australia digital military radar track (sheet Data-Cleaned-Estim-Time). After that, all 148,000 core run J routes, with family weights waypoints 0.9982, free 0.0013, repro-radar 0.0003 and descent-climb 0.0002, interpolated linearly between 600 s vertices.
- **View zenith angle** is measured at the aircraft (WGS84 normal).
- **Effective pixel size** = nadir sampling × slant range / 35,786 km / √cos VZA (area-equivalent). The major axis (÷ cos VZA) is in [geo_scan_crossings.csv]({{artifact:e27d5d7b-4e05-4459-9ac6-798164b0c3d6}}) via the VZA.
- **Scan crossing.** The CGMS line angle of the aircraft is measured relative to the Earth-centre direction, which keeps the disc centred for inclined Meteosat-7 and Kalpana-1. It is solved iteratively against a linear line-angle-versus-time scan model.
- **Apparent position.** This is where the line of sight through the aircraft meets the ellipsoid. It is the parallax-displaced location at which a geolocated image shows a feature at FL350. The median parallax ranges from 0.7 km (INSAT-3A, 19:00 scan) to 30.9 km (MTSAT-2, 00:14 southern half disc).

Selected crossings (weighted median position at the moment the scan line reached the aircraft):

| Scan (start UTC) | Reached | Lat, lon | VZA | Archive |
|---|---|---|---|---|
| FY-2D 19:31 | 19:44 | −0.9, 93.6 | 9.0° | fetched |
| FY-2D 21:31 | 21:48 | −17.5, 91.9 | 22.8° | fetched |
| FY-2D 23:31 | 23:51 | −33.7, 90.2 | 39.5° | fetched |
| MTSAT-2 17:31:15 (radar track) | 17:43 | 5.8, 101.5 | 50.5° | fetched |
| MTSAT-2 22:31:15 | 22:51 | −25.8, 91.1 | 66.0° | fetched |
| MTSAT-2 00:00:53 southern half | 00:09:31 | −36.0, 89.9 | 70.7° | fetched |
| Meteosat-7 22:00 | 22:07 | −20.0, 91.7 | 48.0° | catalogued, account needed |
| COMS-1 20:40 | 20:56 | −10.5, 92.6 | 42.8° | query |

The full list of 107 events is in [geo_scan_crossings.csv]({{artifact:e27d5d7b-4e05-4459-9ac6-798164b0c3d6}}). It gives 5–95 % crossing-time ranges, 0.5–99.5 % apparent-position boxes, VZA, sun elevation and archive status.

## 4. Fetched imagery (MTSAT-2, FY-2D)

Figures, one panel per satellite and scan:

- [FY-2D infrared]({{artifact:fb79d4d5-0e67-4f2c-9181-f6f5e6d0950f}})
- [FY-2D split window]({{artifact:53caf9ce-6ecf-4116-8bf3-3aa184023c62}})
- [MTSAT-2 infrared]({{artifact:63ff5d6b-13e2-482c-82ed-cd8d50e17a2a}})
- [MTSAT-2 split window]({{artifact:e5c24e2b-46c8-4213-883e-d6d6ac71c0ed}})

Compact extracts (10° N–45° S, 80–110° E, IR1 and IR2) are in [geo_mtsat2_ir_subset_20140307.nc]({{artifact:079d66ee-2fcc-43cb-87d9-b6504081c2d3}}) and [geo_fy2d_ir_subset_20140307.nc]({{artifact:d13622d7-7eb1-4e4a-b205-0a76736b534a}}).

Background scene under the posterior apparent positions ([geo_cloud_at_posterior.csv]({{artifact:0d215078-7482-428a-92e3-d5f389cbf449}})):

- **18:42–21:48 UTC.** 95–100 % of the posterior weight lies over warm, mostly clear scenes (10.8 µm > 285 K). The exceptions are MTSAT-2 at 19:44 (78 %) and 20:46 (77 %), where convective cloud covers part of the area in the oblique MTSAT-2 view; FY-2D at the same times gives 99.7 % and 95 %. A contrail at about 220 K would have high thermal contrast here.
- **22:49–22:50 UTC.** 36 % (FY-2D) and 77 % (MTSAT-2) of the weight lies over 250–285 K scenes.
- **23:51 UTC onwards.** About 99 % of the weight lies over a 278–280 K scene (median), probably low/mid cloud, though cloud type was not classified. Contrast against a cold contrail would still be large; a contrail would be hidden only above a cold high cloud deck. Under 0.7 % of the weight was under cold cloud (< 250 K) in every fetched scan, except MTSAT-2 at 19:44 (6.6 %).

Calibration caveats:

- The split-window difference over clear tropical sea is +1.8 to +3.2 K (water vapour). The FY-2D field is systematically higher than MTSAT-2, which suggests an inter-calibration offset.
- FY-2D files are CEReS re-encodings with GEOS(86.0) navigation; the satellite was at 86.45° E. Their per-line times are placeholders (MJD 54558), so FY-2D crossing times are modelled.
- Navigation was checked only qualitatively, by consistency of cloud features with MTSAT-2 near Sumatra at 16:31–16:32 UTC.

## 5. Archives and access

| Satellite | Holder | Full-res for 7–8 Mar 2014 | Anonymous | Grade |
|---|---|---|---|---|
| MTSAT-2 | Chiba Univ CEReS (ftp://mtsat.cr.chiba-u.ac.jp/pub/MTSAT-2/HRIT and gridded_V2.0); also SSEC Data Center (order) | yes, verified by listing | yes | A |
| FY-2D | NSMC; copy at CEReS (ftp://fy.cr.chiba-u.ac.jp/FY2-D/HRIT/2014/) | yes for 9 scans, verified | yes (CEReS) | A |
| Meteosat-7 | EUMETSAT Data Store, EO:EUM:DAT:0881 MVIRI L1.5 CDR R2 57° | 14 slots listed, 5 missing | no (free account) | A |
| FY-2E, FY-2F | NSMC Fengyun Satellite Data Center | probable, not verified | no (real-name registration) | B |
| INSAT-3D, INSAT-3A, Kalpana-1 | MOSDAC (ISRO SAC) | probable, not verified | no (registration; open data only for anonymous users) | B |
| COMS-1 | KMA NMSC data service | probable, not verified | no (registration) | B |
| Elektro-L N1 | SRC Planeta / NTs OMZ | unknown | unknown | C |

The NOAA NCEI GridSat-B1 (3-hourly, 0.07°) and the NASA GES DISC merged 4 km IR (MERGIR, Earthdata login) are reduced-resolution composites of Meteosat-7 and MTSAT-2. They were not used, because the native data were available.

## 6. Classified infrared early-warning satellites

US infrared early-warning satellites (SBIRS and DSP) observe the region from geostationary and highly elliptical orbits. They are not civil data sources. The public record in the literature register is limited to anonymous statements from US officials on 12–14 March 2014:

- No midair explosion was detected at loss of contact or in the hours after it (NBC News, S01, grade C).
- The US intelligence community "archives the satellite system's infrared signals by type" (Malay Mail relaying NBC, S02, grade C).
- Had the satellites picked something up, ships would have been sent (AFP, S03, grade C).

These statements predate the southern-corridor finding of 15 March and do not address the end of flight. No official US statement and no public retention statement for national-security imaging systems was found (register R15). Nothing further is inferred here.

## 7. Queries for Pete

1. Open a free EUMETSAT account and download the 9 catalogued Meteosat-7 slots 16:30–18:30 and 21:30–00:30 UTC. Either supply the API key or accept a credential prompt, and these can be rendered like MTSAT-2.
2. Register with MOSDAC for INSAT-3D L1B full disc HH:00/HH:30 from 16:30 to 00:30 UTC. This is the best-resolution split-window imager at 14–43° VZA. The same registration covers INSAT-3A and Kalpana-1.
3. Register with NSMC for FY-2E hourly full disc, 17:00–00:00 UTC. Ask NSMC whether FY-2D scans exist for 17:31 and 18:31 UTC.
4. Request COMS-1 full disc at 17:40, 20:40 and 23:40 UTC from KMA NMSC.
5. Ask SRC Planeta about Elektro-L N1 MSU-GS 16:30–00:30 UTC, including IR channel quality.

The time windows and search boxes are in [geo_query_list.csv]({{artifact:39655a7b-dd85-4789-9bb9-01e3d58f97db}}).

## 8. Limitations

- **Scan models.** Scan start, duration and direction are assumed (grade C) for INSAT-3D, INSAT-3A, Kalpana-1, Elektro-L, FY-2E and COMS-1. Crossing times for these could be off by up to the scan duration (25–30 min) if the direction or start time is wrong. Positions in the query boxes are padded by 1°, but a start-time error of ±15 min corresponds to ±200 km along track.
- **Altitude.** FL300–FL400 changes the parallax by about −14 % to +14 % of the FL350 value; this was not separately tabulated.
- **Routes.** Positions were held at 00:11:49 UTC for later scans, so scans after 00:12 show the end-of-route position.
- **No detection test.** No contrail-detection algorithm or contrail-formation (Schmidt–Appleman, ERA5 humidity) check was run in this track.
