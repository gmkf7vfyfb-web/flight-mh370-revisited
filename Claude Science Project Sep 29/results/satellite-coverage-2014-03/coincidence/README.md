# Space-time coincidence: satellites versus the aircraft, the impact and the debris (20 Oct 2026, PROVISIONAL)

Question (Pete): did any imaging satellite have MH370 inside its field of regard at the right time: in flight
(radar track 16:42-18:22 as calibration, posterior routes after 18:01:49), at impact (7th arc +/-100 NM,
+/-30 min), or along the debris drift paths (flaperon calibration sightings)? Has this been done before?

Rule (shared code `code/coincide.py`, `code/access_params.py`): a pass covers a target when the satellite's
zero-Doppler line (plane through the sub-satellite point normal to the ground track) sweeps over it and the
signed cross-track offset lies inside the access band (SAR: near-far incidence on an allowed look side;
optical: max off-nadir + half swath, sun >= 10 deg at the target). This is theoretical access, an upper bound.

## In flight (`inflight/`, parent session)
Run J routes.npy (2,000 posterior routes per seed, 10-min vertices; waypoints family 48,000 routes, family
mixture weights 0.9982/0.0013/0.0003/0.0002) and the Geoscience Australia radar track.
- Lacrosse 5 23:12 UTC P = 1.00 (aircraft 29.0-26.7 S), RISAT-1 23:20 P = 1.00 (30.0-27.4 S), Kondor
  (Kosmos 2487, NOT Kondor-E 1) 23:45 P = 0.80 (33.3-32.2 S), RADARSAT-2 23:59 P = 0.99 (35.1-32.0 S);
  COSMO-SkyMed 1 00:08 0.09; none 18:22-22:00.
- Calibration: Yaogan-13 17:59:40 with the radar-tracked aircraft at 5.5 N 99.3 E inside its band.
- Imaging geometry (`inflight-sar-geometry.csv`, `inflight-sar-smear.csv`): an airliner at FL350 appears
  7-18 km toward the sensor (height layover) and 2-18 km along track (line-of-sight speed) from its true
  position; azimuth smear about 200 m (RADARSAT-2 Fine) to about 1 km (1 m military modes), about 17 m in
  ScanSAR Wide. Grades: RADARSAT-2/RISAT-1 bands B; Lacrosse/Kosmos 2487 C.
- Sunrise (`sunrise-*.csv`): seen from the aircraft at FL350 at 23:38 UTC (median) near 32 S, between the
  5th and 6th arcs; at sea level 23:52. 6th/7th arcs crossed with the sun 2.9/4.5 deg up.

## Impact window (`impact-window/`, sub-agent)
Run J waypoints only; D0 '00:19 data not used' headline (D2, D4 sensitivities); 1.5 M draws, ln Z reproduced.
Impacts 00:20-00:47 UTC (median 00:32), 99 % within 100 NM of the 7th arc, sun 4.7-11.9 deg.
COSMO-SkyMed 3 00:35-00:37 covers 0.93 of the mass within +/-30 min (0.58 after impact); COSMO-SkyMed 2
00:54-00:56 0.49 after; first hour after impact, radar or daylight optical 0.855 (D2 0.91, D4 0.99).
`impact-window-query-list.csv`: 131 footprints (WKT) and UTC windows for archive operators. The impact sample
(89 MB) is artifact version 8711b4b8-9520-497b-9d01-62b7d0964c0c, not committed.

## Drift sightings (`drift-sightings/`, sub-agent; existing 4-snapshot binaries + Brownian bridge, provisional)
19,581 open-archive scenes meet the flaperon's 90 % drift envelope 8 Mar 2014-29 Jul 2015. Expected
detections across all of them 4.0e-4 (bracket 3e-5 to 1.6e-3); non-detection changes ln L between source
latitudes by < 2e-4: no usable power at sea. Exception: Pleiades imaged the Reunion find coast 13 times
31 May-10 Jul 2015; if the flaperon beached 30-60 days early, P(at least one scene shows it) = 0.87.
A planned 5-day snapshot run (needs the remote heavy lock) was not started.

## Literature (`literature/`, sub-agent; 91 sources graded 39 A / 14 B / 38 C; partly provisional)
ATSB 2017 (PDF p.125): imagery over the Malay Peninsula, Malacca Strait and later the Indian Ocean 'for the
flight time and some hours after' was examined and the aircraft not identified; no sensor or scene list.
NASA searched polar-orbiter imagery 19:00-05:00 UTC for contrails. Requests to states only ~15 Mar 2014.
Malaysian SIR silent. No prior orbital-coincidence analysis found (Hansard, FOI, PPRuNe, full IG archives
not crawled). Retention: DLR keeps all TerraSAR-X raw data; RADARSAT-2, COSMO-SkyMed, Maxar, Pleiades
archives long-lived; raw-signal retention for RADARSAT-2/COSMO/RISAT-1/Maxar undocumented; no operator
publishes acquisition logs; no military archive policy published.
