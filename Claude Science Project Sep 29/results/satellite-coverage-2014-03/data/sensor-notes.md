# Sensor specification and MH370-use tables: method note

Prepared 20 Oct 2026 for the satellite-coverage study (SENSORS track). Companion files: `satellite-specs.csv` (105 rows) and `satellite-mh370-use.csv` (21 rows).

## 1. What the specification table contains

One row per platform (RapidEye 1-5 and the 28 Flock-1 Doves are each one aggregate row; COSMO-SkyMed, SAR-Lupe, KH-11, IGS and Yaogan are one row per spacecraft because the Elements track needs one NORAD id per row). Multi-sensor platforms carry the sensor most useful for debris (e.g. Terra = ASTER VNIR, Resourcesat = LISS-IV, RADARSAT-2 = Spotlight) with the other modes in `notes`.

Row counts by family: {'optical_mr': 28, 'optical_hr': 24, 'recon_optical': 24, 'recon_sar': 23, 'sar': 6}. Grade counts: {'C': 59, 'B': 43, 'A': 3}.

Catalogue fields (`norad_id`, `intl_designator`, `launch_date`, `inclination_deg`, decay dates in `end_of_ops_date`) were read from the CelesTrak SATCAT records API on 20 Oct 2026 for every row except Flock-1, so they are grade A. `altitude_km` is the SATCAT mean of apogee and perigee only where the satellite is still station-kept and the orbit is near-circular (`altitude_source` says which); for retired, lowered or elliptical orbits the nominal operational altitude is used instead (IKONOS is at 574 km today but flew at 681 km in 2014; RISAT-1 has decayed to 313 km). The Elements track should replace all of these with the March 2014 TLE values.

Sensor fields (`best_gsd_m`, `nominal_swath_km`, `max_off_nadir_deg`, SAR incidence range, look side, node time) come from operator datasheets and ESA eoPortal mission pages. Grades:

- **A** = read in this project (THEOS from the GISTDA page, WorldView-2 from the PGC Maxar guide, Gaofen-1 from the 2022 *J. Remote Sensing* review, all read for the 17 Oct research note) or read in this session (SATCAT).
- **B** = official or eoPortal value cited from the author's knowledge of the datasheet but not re-read in this session. These are the values most worth spot-checking before publication; the URL in `spec_source` is where to check.
- **C** = community, encyclopaedic or open-literature estimate, including every reconnaissance satellite and every "assumed" field-of-regard value.

`max_off_nadir_deg` is the *maximum* roll the platform can use for a data take (the "possible" swath), not the standard product limit. Where both are known the standard limit is in `notes` (Pleiades 30 deg standard / 47 deg maximum; SPOT-6 30 / 45; IKONOS and GeoEye-1 products are normally cut at 26-40 deg although the bus can reach 60 deg). Nadir-only pushbrooms (Landsat 7/8, HJ-1A/B, Flock-1) have 0. For SAR the field of regard is the incidence range of any imaging mode (not just the best-resolution mode) and `sar_look_side` says whether the far side needs a roll manoeuvre. Where the operator has published nothing (SAR-Lupe, Lacrosse, Topaz, IGS, Yaogan SAR) the range 20-55/60 deg is an assumption and is graded C.

## 2. How detection_class was assigned

Rule given by the researcher: flaperon (2 m object) needs GSD <= 1 m; a fuselage or wing section (10-30 m) needs 1-5 m; an intact aircraft (64 m x 61 m) needs 5-30 m. The class is a direct function of `best_gsd_m`:

- `best_gsd_m` <= 1.0 -> "flaperon (<=1 m)"
- 1.0 < `best_gsd_m` <= 5.0 -> "section (1-5 m)"
- 5.0 < `best_gsd_m` <= 30 -> "aircraft (5-30 m)"; rows at 22-30 m (UK-DMC2, Deimos-1, NigeriaSat-X, HJ-1A/B) are flagged "marginal".

Counts: {'flaperon (<=1 m)': 60, 'section (1-5 m)': 32, 'aircraft (5-30 m)': 8, 'aircraft (5-30 m) - marginal at 22-30 m': 5}.

Three caveats on the rule. (i) For SAR the class uses the best spotlight resolution, which applies to a 5-10 km scene; the wide modes that would actually be used to sweep ocean (ScanSAR 30-100 m) are below the aircraft threshold, so SAR "possible" swaths on the map should be read as the field of regard, not as a detection footprint. The 21 Mar COSMO-SkyMed detections were reportedly from a wide-angle, low-resolution capture, so radar detection of 5-25 m objects at coarse resolution is possible when the object is a strong scatterer. (ii) A 1 m optical GSD puts about 2 pixels across a flaperon; detection at that scale depends on contrast and sea state, so the flaperon class means "possible", not "likely". (iii) GA (Record 2017/13) found that 0.5 m Pleiades objects were spectrally similar to sun glint; false-alarm rates were never calibrated for any sensor in this table.

## 3. Candidates dropped or flagged, and why

Dropped (not yet launched): Sentinel-1A (3 Apr 2014), ALOS-2 (24 May 2014), KazEOSat-1 (30 Apr 2014), SPOT-7 (30 Jun 2014), Deimos-2 (19 Jun 2014), WorldView-3 (13 Aug 2014), Gaofen-2 (19 Aug 2014), Ofeq-10 (9 Apr 2014), SkySat-2 (8 Jul 2014), ASNARO-1 (Nov 2014), Yaogan-20 and later (Aug 2014 on), Bars-M (2015), KOMPSAT-3A (2015), Sentinel-2A (2015), PAZ (2018).

Dropped (retired before March 2014): RADARSAT-1 (ended 29 Mar 2013), Envisat ASAR (Apr 2012), ALOS-1 PALSAR/PRISM (Apr 2011), ERS-2 (2011), CBERS-2B (2010), RazakSAT (Malaysia; failed ~2011), EgyptSat-1 (2010), Sich-2 (contact lost Dec 2012), Monitor-E, IGS Radar-1 (failed 2007), IGS Radar-2 (power failure 2010; decayed 13 Apr 2014), IGS 1A/1B (first generation), Yaogan-1 (believed failed 2010), Persona-1 / Kosmos 2441 (failed 2008), Lacrosse 2/3 (de-orbited 2008-2011), Resurs-F / Kobalt-M film-return satellites (none in orbit in March 2014; Kosmos 2495 launched 6 May 2014), CBERS-3 (launch failure Dec 2013).

Dropped (sensor class excluded by the researcher): MODIS, VIIRS, AVHRR, Fengyun-3, Oceansat-2, SPOT-5 VEGETATION, Proba-V, Landsat TIRS alone, all geostationary imagers, Yaogan-9/16/17 ELINT triplets (not imaging), ISS crew photography. Terra and Aqua MODIS and the ISS ISERV camera appear only in the use table because NASA was tasked via the Charter.

Kept but flagged `status_mar_2014 = unknown`: Beijing-1, SJ-9A, EROS-A, Ofeq-5, Persona-2, Kondor-E, HJ-1C, Lacrosse 4/5, Topaz 1/2, KH-11 USA 161, Yaogan 2/3/4/5, and all Japanese IGS and Yaogan rows regarding exact attribution. Kept but partially covering the box because of inclination: Ofeq-5/7/9 (retrograde 141.8-143.5 deg: nadir limit 36.5-38.2 S, about 40-42 S with roll), TecSAR and RISAT-2 (41 deg: about 45 S with 45 deg incidence), Flock-1 and ISS sensors (51.6 deg), Lacrosse 5 (57 deg), Topaz (123 deg retrograde, i.e. 57 deg), Resurs-DK1 (70 deg), Kondor-E (74.7 deg). Formosat-2 is in an exact 1-day repeat orbit, so its access is confined to strips within 45 deg of 14 fixed ground tracks.

Added beyond the starting list: Kanopus-V 1, BKA, Resurs-P 1, Resurs-DK1 (Russia); VNREDSat-1 (Vietnam); SSOT/FASat-Charlie (Chile); RASAT (Turkey); TecSAR/Ofeq-8 (Israel SAR); Topaz 1/2 and Lacrosse 4 (USA); IGS Optical 5 demonstrator (IGS 8B); Yaogan 3, 6, 10, 15 (catalogue review); Flock-1 (Planet, experimental).

## 4. Main uncertainties

1. **Reconnaissance estimates.** No official specification exists for KH-11, Lacrosse, Topaz, SAR-Lupe, Helios-2, Ofeq, IGS, Persona or Yaogan. The GSD values are open-literature estimates (KH-11 ~0.1-0.15 m from the 2.4 m aperture and perigee height; SAR-Lupe 0.5 m spotlight from OHB statements; IGS 0.6 m / 0.4 m from Japanese press as quoted in the CIA CSI review; Helios-2 0.35 m; Ofeq ~0.5 m; Yaogan 0.7-3 m by series). Swaths (~5-20 km) and agility (45-60 deg) are assumptions chosen so that the "possible" swath on the map is generous. All are grade C and should be drawn with a distinct line style.
2. **Yaogan attribution.** The optical/SAR split and the sub-series assignment (Jianbing-5/6/8/10 classes) follow Gunter's Space Page and are contested; a Yaogan row may be a different sensor type from the one listed. The 1,200 km Yaogan 8/15/19 class is particularly uncertain.
3. **Operational status.** Design lives and amateur-tracking reports were used for status; several satellites launched in late 2013 (KOMPSAT-5, DubaiSat-2, SkySat-1, Topaz 2, Yaogan 18/19, USA 245) were within or just out of commissioning in March 2014.
4. **Node local time.** `ltdn_or_ltan` is nominal; actual node times drift by tens of minutes over a mission (EO-1, Resourcesat-1, Landsat 7 in 2014). The Elements track should derive the local time from the 2014 TLE rather than this column.
5. **Field of regard versus practice.** Commercial operators seldom task beyond 30-35 deg; the maximum values in the table define the outer "possible" swath. The dawn-dusk SAR satellites (RADARSAT-2, TerraSAR-X/TanDEM-X, COSMO-SkyMed, KOMPSAT-5, RISAT-1) pass at about 06:00 and 18:00 local time, so their passes never coincide with the optical 09:30-13:30 passes; the map should group them by local time of day as well as by family.
6. **What is not published for MH370.** Image footprints and non-detection reports for every agency; the spacecraft behind the Airbus "122 objects" scene, the Japanese IGS image and the "French radar" images; RADARSAT-2, TerraSAR-X and SAR-Lupe involvement; the Chinese satellites beyond Gaofen-1; the Tomnod tile footprints; and the acquisition times for Gaofen-1 (18 Mar) and the Airbus scene. The Charter activation page lists no satellites and no products.

## 5. Sources read in this session

CelesTrak SATCAT records API (https://celestrak.org/satcat/records.php); Charter activation page (Internet Archive capture of https://disasterscharter.org/web/guest/activations/-/article/missing-malaysia-airlines-jet); project note research-satellite-imagery-2014.md (17 Oct 2026); press and secondary pages cited by URL in `satellite-mh370-use.csv` (ABC News 13 and 22 Mar 2014 and 21 Mar 2014 DigitalGlobe statement; Malay Mail 11, 13, 18, 23, 28 Mar 2014; NBC 20, 26, 27 Mar 2014; Quartz 12 Mar 2014; IBTimes 13 Mar 2014; Universe Today 23 Mar 2014; Iannello 23 Jul 2021; Airline Ratings 2021; CSIRO news Aug 2017; ATSB news 2017). eoPortal and operator datasheets listed in `spec_source` were cited, not re-read (grade B).
