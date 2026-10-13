# Other traffic on N571, 18:25-18:39 UTC, 7 March 2014 (for the traffic check)

Source: ATC-Caption-2025 dataset, version 2 (15/18 Sep 2026), www.mh370-caption.net, decoded from Malaysian civil ATC
radar ASTERIX recordings and ADS-B/ADS-C. Raw files copied here as `source-*.csv`.

`n571-traffic-1825-1839.csv`: one row per aircraft per 60 s, 18:25:00-18:39:00 UTC.

- **UAE343** (KUL-DXB, FL340): **measured**. Positions are interpolated linearly between ADS-C position reports
  (18:22:57, 18:25:14, 18:26:30, 18:27:53, 18:29:26, 18:30:10, 18:32:49, 18:37:45, 18:42:14). Ground speed and track come
  from consecutive reports; the reported ADS-C ground speed and true track are in their own columns. Passes MEKAR 18:25:14,
  NILAM 18:29:26, IGOGU 18:42:14. Langkawi SSR positions differ from ADS-C by 2.5-3.6 NM at 18:25 (SSR azimuth error at
  about 198 NM range); ADS-C is used.
- **IGO053** (MAA-SIN, FL330, eastbound on N571): **estimated**. It is not in Malaysian radar cover until 18:43:57. A
  straight-line fit to Langkawi SSR, 18:44-18:54, gives MEKAR at 18:44:21, ground speed 457 kt, 0.7 NM from the N571
  centreline (Genting ADS-B at 18:57: 457 kt). Mach 0.775 is derived with the ERA5 wind. The track before 18:44 is flown
  backward along N571 (LAGOG-IGOGU-NILAM-MEKAR) at that Mach and FL330 with ERA5 winds: IGOGU 18:26:27, NILAM 18:39:52.
  Assumes the airway centreline and constant Mach.
- **Heading, TAS and Mach are derived for both**, as ground vector minus ERA5 wind (nearest grid point, linear in time;
  engine/report/satcom_model.py). No source records them. Wind at these levels is light (drift under 0.5 deg).
- UAE343 and IGO053 pass each other head-on on N571 at about 18:34:30, near 7.06N 95.35E, 1,000 ft apart.

`separation-run-h-routes.csv`: closest horizontal distance from MH370 (run H posterior samples, re-flown at 100 s
spacing; 400 per route) to each aircraft in the window. Preliminary: run H's route family is superseded by the reset,
and vertical separation is not included.
