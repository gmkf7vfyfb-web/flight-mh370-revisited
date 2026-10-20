# Satellite imaging access over the 6th and 7th arcs, March 2014

Module: satellite coverage (theoretical access and known use). Session 20 Oct 2026. Status: PROVISIONAL, first pass.

## Question

Which imaging satellites (optical or radar, ground resolution 30 m or better) passed within reach of the 6th/7th-arc area
(20-45 S, 70-110 E) between MH370's take-off (7 Mar 2014 16:42 UTC) and 16 Mar 2014, where did their ground tracks run,
and what could their sensors have reached? A second window, 16-27 Mar 2014, covers the period of the published imagery.

## What the maps show and do not show

The maps show geometric ACCESS: where a sensor could have looked, given its orbit and its published field of regard. They
do not show where images were taken. No agency has published footprints for the 2014 southern Indian Ocean imagery, and
no agency has stated that any satellite imaged this area before 16 Mar 2014. The result is therefore an upper bound on
what imaging was possible, to be narrowed by archive-catalogue checks (see `archive-catalogue-report.md` when present).

## Method

1. Element sets: Space-Track general-perturbation sets with epochs 1-28 Mar 2014 from the public bulk export of the
   Space-Track history (Hugging Face dataset juliensimon/space-track-tle-history, 2014 file), 6,568 sets for 77 catalogued
   objects (`data/tle-2014-03.csv`), plus 2,736 sets for 35 further objects extracted by the parent session from the same
   export (`data/tle-2014-03-extra.csv`: Kanopus-V 1, BKA, Resurs-P 1, Resurs-DK1, VNREDSat-1, SSOT, RASAT and the 28
   Flock-1 Doves). Classified satellites: amateur-tracker sets from Mike McCants' classfd.tle (Wayback capture 19 Mar 2014)
   for USA 186, USA 245, Lacrosse 5, SAR-Lupe 3 and 5. Lines were regenerated from the export's parsed fields (float32
   angles; round-trip error <= 2e-5 deg). Objects without a March 2014 set (`data/tle-2014-03-missing.csv`): IGS Optical
   3/4/5 and Radar 3/4, Helios-2A/2B, Ofeq-5/7/9, SAR-Lupe 1/2/4, USA 224, Topaz 1/2. They are absent from all maps.
2. Propagation: SGP4 (python sgp4 2.x), 10 s steps, 7 Mar 16:40 to 28 Mar 00:00 UTC, element set nearest in epoch to each
   step. TEME to ECEF by GMST (IAU 1982) only; polar motion and nutation neglected (sub-km on the ground). Code:
   `code/satgeom.py`. Sun elevation at the sub-satellite point from a low-precision solar ephemeris (about 0.1 deg).
3. Access bands (`data/satellite-specs.csv`, one row per satellite with sources and grades): optical = across-track ground
   offset at the operator's maximum off-nadir angle plus half the nominal swath, on both sides of the track; SAR = ground
   offsets at the minimum and maximum incidence angle on the look side(s) (both sides where the satellite can roll).
   Spherical-Earth geometry at the propagated altitude. The 'nominal swath' strip is the swath at nadir.
4. Pass rules: a pass is a contiguous run of steps whose access band touches the study box; passes are split at gaps
   > 60 s. Optical passes count as usable only when the sun is >= 10 deg above the horizon at the sub-satellite point;
   radar passes always count. '7th arc in reach' means the possible-access polygon intersects the sea-level 7th arc
   (`data/arcs-sea-level.csv`, from the 00:19:29 BTO of 18,400 us, Inmarsat ephemeris, offset -495,679 us).
5. Validation (`data/tle-validation.md`): THEOS 24 Mar 2014, closest approach of the sub-satellite point to 46.5 S 89.5 E
   at 03:08:00 UTC against 03:07:56 published, nadir offset 371-372 km, implied incidence 26.91 deg against 26.98 deg
   published; the DigitalGlobe image of 16 Mar 04:16 UTC can only be WorldView-2 (closest approach 04:15:40, 114-119 km,
   8.3 deg off-nadir); WorldView-1, GeoEye-1 and QuickBird were over North America at that time.

## Results, window 1 (7 Mar 16:42 to 16 Mar 00:00 UTC)

- 1719 usable passes by 89 named satellites crossed the study box; 1460 of them had the 7th arc inside the
  sensor's field of regard. Daily: about 45 passes by 23-24 optical satellites of 2 m or better, 24-28 by 14 reconnaissance
  optical satellites, 77-85 by 20 radar satellites, 55-60 by 30 civil optical satellites of 2-30 m.
- During the flight (7 Mar 16:42 to 8 Mar 00:19 UTC) the area was in darkness (local 21:00-05:00). Only radar could have
  imaged: 22 passes by 17 radar satellites crossed the box, and on 20 of them (16 satellites: COSMO-SkyMed 1/2/4,
  HJ-1C, KOMPSAT-5, Kondor-E 1, Lacrosse 5, RADARSAT-2, RISAT-1, TanDEM-X, TerraSAR-X, Yaogan-3/6/10/13/18) some part
  of the 7th arc lay inside the incidence band. Only one of these (RADARSAT-2, 22:15 UTC) had the arc inside the band at
  the point of closest approach; for the others the band reached the arc only along part of the pass.
- From 8 Mar onward the whole 7th arc from 20 S to its southern limit (43.7 S) was inside the field of regard of several
  1 m-class optical satellites in daylight and of several radars every day. Each 0.25-deg cell of the box lay inside a
  1 m-class access band 191-293 times over the eight days (53-89 times with optical pointing limited to 30 deg off-nadir;
  115-189 times for radar alone). Access was saturated; what was imaged depends only on tasking.
- Nominal (nadir) swaths of the <= 5 m optical sensors covered each cell 0-17 times, with gaps: without off-nadir tasking
  the high-resolution sensors would have imaged only narrow strips.

## Results, window 2 (16-27 Mar 2014)

Known imaging passes located by propagation: WorldView-2 16 Mar 04:13 UTC (nadir track 115 km from the DIGO objects at
43.98 S 90.96 E); Gaofen-1 18 Mar 04:10 (38 km from 44.95 S 90.22 E); Pleiades-1A 23 Mar 04:09 (115 km from the GA
rating-5 cluster at 34.85 S 90.95 E); THEOS 24 Mar 03:02-03:08 (372 km from 46.5 S 89.5 E). See
`figures/known-use-satellites-16-27mar2014.png`.

## Files

- `figures/satellite-access-counts-7-15mar2014.png|pdf` - composite access-count map, four panels.
- `figures/daily-2014-03-07-flight.png`, `daily-2014-03-08.png` ... `daily-2014-03-15.png` - daily maps, four sensor
  families, one colour per satellite, ground tracks, nominal swaths and fields of regard.
- `figures/per-satellite-*.png` - one panel per satellite, all usable passes over window 1.
- `figures/known-use-satellites-16-27mar2014.png|pdf` - window 2 with the reported object positions.
- `tables/satellite-passes-2014-03.csv` - every pass, both windows (12738 rows): times, nadir point, altitude,
  heading, distance and side of the 7th arc at closest approach, access band edges, sun elevation, usable flag,
  arc-in-reach flag (polygon test) and the earlier closest-approach-based flag, known MH370 use.
- `tables/satellite-summary-7-15mar2014.csv` - passes and arc-in-reach counts per satellite, window 1.
- `tables/arc-daily-access-fraction.csv` - fraction of the 7th arc (20 S to 43.7 S) inside at least one usable access
  band per day, by sensor class.
- `data/satellite-specs.csv`, `data/satellite-mh370-use.csv`, `data/sensor-notes.md` - specification table (grades A/B/C),
  record of known tasking and released imagery, method note.
- `data/tle-2014-03*.csv`, `data/norad-ids.csv`, `data/tle-validation.md` - element sets and validation.

## Caveats

- Specification values graded B (43 rows) were cited from operator/eoPortal datasheets without re-reading them in this
  session; the maximum off-nadir angles for KOMPSAT-3, Gaofen-1 (35 deg), ZY-3 (32 deg), Kanopus-V (40 deg) and the SAR
  incidence ranges should be spot-checked before publication. All reconnaissance rows are open-literature estimates (C).
- Amateur element sets: a few km to tens of km along-track within a week of epoch (USA 245 recovery set against classfd:
  187 km after 5 days). Lacrosse 5 uses an epoch of 27 Feb 2014. Catalogued objects: about 1 km cross-track, 1-10 km
  along-track within an update interval.
- Yaogan optical/SAR attribution follows open sources and is contested. IGS 8A/8B assignment is unverified.
- The 28 Flock-1 Doves (3.5 m, nadir only, 51.6 deg orbit, commissioning) are in the pass table but not drawn.
- Weather and ocean sensors (MODIS, VIIRS, AVHRR, Fengyun) are excluded as imagers; cloud cover from ERA5/MODIS is a
  separate layer (see `cloud-*` files when present).

## Cloud layer (separate; not an imaging term)

`figures/cloud-cover-daily-8-15mar2014.png`, `figures/cloud-cover-daily-16-27mar2014.png`, `tables/cloud-daily-summary.csv`,
`data/cloud-era5-04utc-2014-03-08-27.nc`, `data/cloud-modis-mod08d3-2014-03-08-27.nc`, `cloud-notes.md`. ERA5 hourly total cloud
cover at 04:00 UTC (the hour the sun-synchronous optical satellites crossed, about 10:00-10:45 local solar), 0.25 deg, from the
public ARCO ERA5 mirror (the CDS API route was not usable: the stored Copernicus credential is an account login, not a CDS token).
MODIS Terra MOD08_D3 v6.1 daily cloud fraction (1 deg) as an independent check (r = 0.86 with ERA5 over the arc band).
Over the band within 150 km of the 7th arc, 8-15 Mar: mean total cloud cover 0.68-0.86
(ERA5); the fraction of the band with cloud cover below 0.3 was 0.017-0.123,
i.e. at most about 12 % of the arc band was clear enough for optical imaging on any day of the first window. Radar is unaffected.

## Archive catalogue check (actual scenes)

`archive-catalogue-report.md`, `tables/archive-scenes-2014-03.csv` (77 scenes), `figures/archive-scenes-overlay-2014-03.png`,
`figures/access-vs-archived-scenes-2014-03.png`. Open catalogues that answered: USGS LandsatLook STAC (Landsat 8, EO-1), NASA
CMR (ASTER L1A), Airbus OneAtlas (Pleiades-1A/1B, SPOT-6), Copernicus (no Sentinel-1 before Apr 2014). Catalogues needing an
account the project does not hold: EODMS (RADARSAT-2), DLR EOWEB (TerraSAR-X), Maxar, Planet, CNES SPOT World Heritage, CRESDA,
KOMPSAT, Bhoonidhi; GISTDA unreachable. Scene counts are therefore a LOWER BOUND.
- 7-15 Mar: 10 scenes in the whole box, none within 50 km of the arc: ASTER strip 8 Mar 04:47 UTC at 38-42 S, 76.5-78.3 E
  (7 granules, 68-100 % cloud, 4.5 h after the last transmission; most plausibly a scheduled acquisition), EO-1 ALI+Hyperion 9 Mar
  at 34.3 S 97.4 E (230-245 km east of the arc, 20-30 % cloud; purpose not stated), Pleiades-1B 9 Mar over Ile Amsterdam.
- 16-27 Mar: 67 scenes; 64 form one cluster at 40-46 S, 86-94 E built from 21 Mar (32 Pleiades, 18 SPOT-6, 10 ASTER, 4 Landsat 8),
  where the surface search and satellite sightings were, 400-800 km south-west of the arc; mostly > 85 % cloud. Only EO-1 on
  25 Mar (34.9 S, 95.2 E) is within 150 km of the arc.
- Caveats from the archive track: EO-1 acquisition times are inferred from the orbit (dates from scene-id day-of-year); Airbus
  times read from product identifiers; GA's Pleiades-1A scenes of 23 Mar are not obviously the same as the Pleiades-1B items in
  the commercial archive.

## Reading for the paper

Theoretical access says nothing about non-detection on its own: every point of the arc was reachable many times a day, so
"no satellite saw debris" carries weight only where a scene exists and was examined. In the open archives there is no such scene
near the arc in 7-15 Mar, and the 16-27 Mar effort went to 40-46 S. A satellite non-detection term therefore remains
unavailable for the arc; the evidence this module adds is the location of the known imaging passes and the saturation of access.

## Space-time coincidence study (20 Oct 2026)

See `coincidence/README.md`: in-flight radar coincidences, impact-window coverage and query list, drift-sighting feasibility, literature sweep.
