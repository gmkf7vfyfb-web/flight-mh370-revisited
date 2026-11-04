# Reverse sensing: data held, arrival windows and known events (8 March 2014)

Folder: `results/hydroacoustics/reverse-windows-data-2026-11-04/`. Built 4 Nov 2026.

This folder gives the three inputs for the reverse-sensing screen. Propagation gives travel time only. No signal level is used anywhere.

1. What data we hold at each station, and its exact UTC coverage (`station-data/`).
2. When sound from an impact near the 7th arc can arrive at each station (`windows/`).
3. Which known events can put sound into each station at the same time (`events/`).

## 1. Data held per station (`station-data/`)

`inventory_0019_0230.csv` lists each station and data form. It gives the coverage from 00:19:00 to 02:30:00 UTC, the sample rate, the band, the file location and the caveat. `coverage_blocks.csv` gives each record or figure panel as one row. The package covers 00:00 to 03:00 UTC. Every time axis is true UTC: `utc` (datetime) and `t_s` (seconds after 2014-03-08 00:00:00 UTC).

| Station | Form held | Coverage 00:19-02:30 |
|---|---|---|
| Cape Leeuwin (H01W) | Kadri 2024 Fig. 9 digitised trace, 5-40 Hz, about 14.5 vertices/s | 00:27:00-00:57:00 |
| Cape Leeuwin (H01W) | Royer 2016 digitised spectrogram (colour readings) | 00:19:00-02:02:59 continuous |
| Cape Leeuwin (H01W) | CMST 2014 Fig. 2 digitised band series | 01:31:40-01:35:50 |
| Diego Garcia South (H08S) | Kadri 2024 Fig. 9 digitised trace, 5-40 Hz, about 15 vertices/s | 01:00:00-01:19:59 |
| Diego Garcia North (H08N) | none held; blocked from 100 of 110 grid points | - |
| IMOS loggers 3315, 3376, 3250, 3274, 3275 | raw 6000 Hz, 307 s in every 15 min, 8 Hz hardware high-pass | 9-10 records each, 32-35 % of the time |
| South-west Amsterdam 3 (SWAMS3), South-east Indian Ridge (SSEIR) | Royer 2016 digitised spectrogram | 00:19-02:03 and 00:19-01:54 |
| SWAMS2, Madagascar (MAD), North Crozet (NCRO), West Kerguelen (WKER) | Royer spectrogram excerpts, 3 min each | 3, 10, 6 and 3 min |
| SWAMS1-3, SSEIR, MAD, NCRO, WKER, Cape Leeuwin | Royer 2016 Table 5 picks (located events only) | 143 picks |
| North-east Amsterdam (NEAMS) | none (data lost on recovery) | - |

Files:

- `imos<id>_waveform_250hz.npz`: logger volts per record, decimated from 6000 to 250 Hz (FIR anti-alias). The file holds record start times, SHA-256 of the source `.DAT`, the clock error, the system gain curve and the hydrophone sensitivity. The SHA-256 of every source file was checked against the database.
- `imos_band_power_1s.parquet`: calibrated band power, 1 s Hann windows, 0.5 s hop, 5-40 Hz and 10-40 Hz (uPa^2). Medians at 10-40 Hz: 93.7-99.8 dB re 1 uPa^2.
- `kadri2024_fig9_vertices.parquet`: digitised pressure vertices (Pa) for panels a-c (Cape Leeuwin) and d-e (Diego Garcia South).
- `royer2016_spectrogram_bands.parquet`: band-mean PSD readings, 5-40, 10-15 and 2-60 Hz. The colour scale saturates. The level offset is not calibrated.
- `cmst2014_digitised_traces.parquet`, `picks_all.parquet` (all picks held: Royer, Kadri, CMST, airgun shots).
- Built by `build_station_package.py` from `hydro_data.sqlite` (artifact v321ea0f6) and `~/Downloads/mh370-inputs/hydroacoustics/imos`.

## 2. Arrival windows (`windows/`)

Grid: the 7th arc from `inputs/arcs-sea-level.csv` (the sea-level arc at 00:19, column `lon_arc7`). Points at every 1 degree from 20 S to 41 S (22 points). Offsets of -50, -25, 0, +25 and +50 NM along the geodesic normal to the arc. Positive is to the north-west, away from Australia. Total 110 points. At 30 S the arc point is 98.132 E. The fitted small circle in the database lies 0.07-0.22 degrees east of this arc. That difference is smaller than the 25 NM grid step.

Impact (source) time: 00:19:38 to 00:29:44 UTC.

Travel time: WGS84 geodesic length L (pyproj). Earliest = 00:19:38 + L / 1.56 km/s. Latest = 00:29:44 + 1.05 L / 1.40 km/s.

Why 1.40-1.56 km/s:

- Sea-water sound speed on these paths is 1.439 km/s (water at the freezing point) to 1.558 km/s (abyssal water at 6000 m). See `sound_speed_bounds.csv` (Mackenzie 1981).
- For a ray, the horizontal speed at each point is c^2 / c_v, where c_v is the speed at the turning point. Thus the time-averaged horizontal speed cannot be more than the maximum water speed. 1.56 km/s is above 1.558 km/s.
- Sound-channel energy travels near the channel axis speed, 1.48-1.49 km/s. 1.40 km/s is 2.7 % below the slowest water speed (1.439 km/s). It also covers slow shelf legs near the IMOS loggers. For example, 100 km of shelf at 1.2 km/s adds 16 s. At 3000 km, the step from 1.48 to 1.40 km/s adds 116 s.
- The 143 Royer 2016 picks give 1.467-1.519 km/s (median 1.482 km/s). We used Royer's origins and a WGS84 geodesic (`royer_implied_speeds.csv`). All picks are inside the bracket.

Why 0-5 % detour: the geodesic is the shortest path. A path that goes around an obstacle of half-width w at mid-path is longer by sqrt(1 + (2w/L)^2) - 1. Thus 5 % covers a sideways offset of up to 0.16 L, about 480 km on a 3000 km path. Horizontal refraction by currents and fronts is much less than 1 %.

Mixed path (separate sensitivity): a crustal leg next to the receiver replaces Lc km of water at 3.5-8.1 km/s (Lg/Sn to Pn). Lc = 100 km (`earliest_mixed100`) and Lc = 300 km (`earliest_mixed300`). This applies to island and margin receivers (Cape Leeuwin, Diego Garcia, IMOS shelf loggers). It is shown for the deep moorings only for completeness. A crustal leg only makes the arrival earlier. Thus only the earliest bound changes, by up to 2 min 35 s for Lc = 300 km. For blocked paths, a third case (`*_mixed_blocked`) uses Lc = the measured blocked span.

Blocking: `paths_lib.screen` uses GEBCO 2026 15 arc-second depths along the geodesic at about 1 km steps. It uses the same rule as the database table `arc_path`. Blocked = land, or water shallower than min(receiver depth, 200 m), more than 20 km from the receiver. It gives the same class as the database on 352 of 352 test paths, with distance differences of less than 0.09 km (`blocking_screen_validation.csv`). Blocked points: Diego Garcia North 100/110, Scott Reef 59/110, Portland 50/110 (each logger), Madagascar 2, North Crozet 6, SSEIR 1.

Union window per station (grid points with clear or partly obstructed paths only) and part covered by data of any continuous form:

| Station | Points | Earliest | Latest | Earliest, 300 km rock leg | Length (min) | Covered |
|---|---|---|---|---|---|---|
| Cape Leeuwin | 110 | 00:35:20.6 | 01:06:49.7 | 00:32:45.4 | 31.5 | 100 % |
| Diego Garcia South | 110 | 00:57:36.1 | 01:18:24.0 | 00:55:00.9 | 20.8 | 88 % |
| Diego Garcia North | 10 | 00:59:56.6 | 01:19:15.0 | 00:57:21.4 | 19.3 | 0 % |
| Perth Canyon 3315 | 110 | 00:34:36.0 | 01:09:27.0 | 00:32:00.7 | 34.8 | 30 % |
| Perth Canyon 3376 | 110 | 00:34:36.1 | 01:09:28.7 | 00:32:00.8 | 34.9 | 42 % |
| Scott Reef 3250 | 51 | 00:38:34.1 | 01:07:31.1 | 00:35:58.8 | 29.0 | 35 % |
| Portland 3274 | 60 | 01:01:51.9 | 01:33:20.7 | 00:59:16.6 | 31.5 | 37 % |
| Portland 3275 | 60 | 01:01:50.7 | 01:33:19.2 | 00:59:15.4 | 31.5 | 33 % |
| SWAMS1 | 110 | 00:26:10.6 | 01:17:21.7 | 00:23:35.3 | 51.2 | 0 % (picks only) |
| SWAMS2 | 110 | 00:26:13.0 | 01:17:22.9 | 00:23:37.7 | 51.2 | 6 % |
| SWAMS3 | 110 | 00:26:07.4 | 01:17:16.8 | 00:23:32.1 | 51.2 | 100 % |
| SSEIR | 109 | 00:32:08.8 | 01:15:55.9 | 00:29:33.6 | 43.8 | 100 % |
| Madagascar | 108 | 00:47:48.0 | 01:30:16.9 | 00:45:12.7 | 42.5 | 16 % |
| North Crozet | 104 | 00:44:45.8 | 01:37:23.4 | 00:42:10.5 | 52.6 | 11 % |
| West Kerguelen | 110 | 00:38:42.5 | 01:31:59.0 | 00:36:07.2 | 53.3 | 6 % |
| North-east Amsterdam | 110 | 00:27:41.5 | 01:01:23.9 | 00:25:06.2 | 33.7 | 0 % (data lost) |

The 100 % at Cape Leeuwin, SWAMS3 and SSEIR comes from the Royer spectrogram colour readings. At Cape Leeuwin the Kadri trace covers 69 % of the window.

Files: `arrival_windows_grid.csv` (station x point: path class, distance, back-azimuth, blocking km, windows, coverage by form), `arrival_windows_station_union.csv`, `grid_points.csv`, `parameters.json`, `arrival-window-coverage.png/.pdf` (chart), `validation_summary.json`. Scripts: `arrival_windows.py`, `paths_lib.py`, `validate_paths_speeds.py`, `coverage_chart.py`.

## 3. Known events (`events/`)

`known_events.csv`: 67 located events. These are 20 Royer 2016 events (6 icequakes, 12 unclassified, 2 earthquakes) and 47 catalogue earthquakes from 7 Mar 21:00 to 8 Mar 03:30 UTC. Of the 47, 17 come from the project merged catalogue (USGS, EMSC, ISC, GEOFON, GCMT) and 30 are new. The new events come from USGS, EMSC and ISC FDSN queries on 4 Nov 2026 (box 75 S-30 N, 20-160 E, any magnitude; raw replies in `eq/`). Most new ISC events are small land events in Taiwan, the Ryukyu Islands and southern Africa.

`known_event_arrivals.csv` (one row per event, station and phase):

- T (water-borne sound): origin time and its error, then a rock leg from the epicentre to the first point with water deeper than 1000 m, and the hypocentre depth, at 3.5-8.1 km/s. Then water at 1.40-1.56 km/s with up to 5 % detour. The location error is taken at the centre and at the 4 corners of the error box. A coda is added to the latest time: 60 s + 60 s per magnitude unit above 3 (60-600 s) for earthquakes, and 120 s for Royer events.
- P to S (earthquakes): first P to first S, IASP91 (obspy TauP), plus coda. This is energy that enters the water at the receiver.
- Columns give path class, overlap with the station's impact window, and overlap with the data held.
- Check: all 143 Royer picks (105 event-station rows) are inside their predicted T windows.
- 13 events have a T window on a clear or partly obstructed path that overlaps an impact window where data is held: 10 Royer unclassified events, 1 Royer icequake and 2 earthquakes. 14 earthquakes have body-wave windows that overlap.

`observed_transients.csv` and `observed_transient_arrivals_elsewhere.csv`: 31 observations with a bearing but no position. These are Kadri 2024 Table 1 (19, Cape Leeuwin), Kadri 2019 Table 3 (6, Diego Garcia South), CMST 2014 detections of interest (5) and the airgun shot series. The source lies on the bearing line (bearing ±1 degree), in water, inside the line of sight of the observing station. From this, we give the window at every other station. The Kadri 2019 signal at 01:58 has no water point in line of sight within its printed range (2860 ± 900 km). Its printed position is on Madagascar.

Airgun shots at Diego Garcia South: 110 shots, 01:00:03.8-01:19:09.2 (`h08s_airgun_shots.csv`). Rule (Pete, 23 Oct 2026): label and interference test, never removed. On the CMST bearing (34.9-35.4 degrees), the line of sight goes from 500 km to 3725 km. On clear paths, the same shots arrive at the other stations after their impact windows. They overlap the impact window only at Diego Garcia North (blocked, no data), Madagascar (paths blocked) and Scott Reef (16 s, mostly blocked).

`persistent_sources_paths.csv`: continuous or repeated sources (labels only), with distance, path class and travel time to every station. These are seismic surveys (4 NOPTA surveys, shooting on 8 Mar not confirmed), the H08S survey of unknown position, 76 icebergs, 25 whale-call daily counts and 13 volcanoes.

Treatment column: located events are removed only at association probability >= 0.95 (screening step). Airgun shots are labelled and tested, never removed. Bearing-only observations are labelled only.

Script: `known_events.py`.

## Limits

- The digitised spectrogram and trace data are readings of published figures. They are not recordings. Coverage by these forms is timing coverage, not equal sensitivity.
- Royer Table 5 picks exist only for events that Royer located. An absent pick is not evidence of no arrival.
- The catalogue completeness offshore is low below about mb 4.2 (project source table). Small oceanic events can be missing.
- Bearing-only windows are wide, because the range is unknown.
