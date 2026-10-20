# Track B — satellite coverage of the impact window (PROVISIONAL)

Satellite-coverage module, 20 Oct 2026. Results go to the parent session, not the repo yet. Everything here is **theoretical access** (an upper bound). It is not evidence that an image exists.

## 1. Impact ensemble and weights
- Source: end-of-flight run J, **waypoints family only** (24 seeds, 153.6 M impact rows). The family posterior at equal prior is 0.9982. Free, repro-radar and descent-climb (together 0.0018) are **not included**, so any mass figure here can be off by at most 0.002.
- Weights rebuilt with the project recipe. I exec'd `option_table_0019.seed_terms` (branch hypothesis/end-of-flight, smoke/, HEAD 5d060f0) unchanged except for its final reduction (`return cells, f4, g`). SATCOM_CSV is engine/data/satcom-observations.csv, and the per-seed script is `rebuild_seed.py`.
- **Reproduction check:** pooled ln Z matches end of flight's table-0019-run-j-waypoints.json to 4 decimals for D0–D5. Examples: D0 −7.5246, D2 −19.1203, D4 −28.5118. The D0 weighted impact latitudes 5/50/95 % are [-38.41, -37.13, -33.87], against the table's [-38.4, -37.12, -33.87].
- **00:19 option (headline): D0 total, q = 1/3, other log-on cause silent ('00:19 data not used').** Sensitivities: D2 ('00:19:29 range and frequency') and D4 ('both 00:19 frequencies, shared start-up offset'). D3 and D5 were rebuilt but not thinned; their ESS is 4.7k and 26k.
- **Thinning:** two-stage resampling, 1,500,000 equal-weight draws per option. Seeds are drawn by multinomial on seed evidence, and rows within each seed by multinomial on the rebuilt weights. Distinct rows: D0 1,235,961, D2 462,574, D4 293,038. Sample file: impact-window-impact-sample.parquet (weight = 1/1.5 M per draw).

## 2. Impact time and spread (weighted)
| option | impact UTC 5/25/50/75/95 % | cross-arc NM 5/25/50/75/95 % (+ = east/outside) | within 100 NM | within 50 NM |
|---|---|---|---|---|
| D0 | 00:20:27 / 00:23:12 / 00:32:02 / 00:41:20 / 00:46:42 | -40.9 / -0.9 / 12.0 / 32.1 / 69.3 | 0.990 | 0.848 |
| D2 | 00:20:30 / 00:22:33 / 00:31:41 / 00:35:39 / 00:46:16 | -18.6 / 2.1 / 11.9 / 29.3 / 53.9 | 0.995 | 0.932 |
| D4 | 00:20:10 / 00:20:30 / 00:21:02 / 00:27:27 / 00:35:34 | -5.8 / 3.6 / 10.1 / 19.2 / 40.7 | 1.000 | 0.986 |

The D0 impact range is 00:19:37–01:15:26 UTC. Cross-arc distance is measured from the shared sea-level 7th arc in arcs-sea-level.csv. That polyline departs by up to 14 km from the spherical small circle (0.570 N 64.252 E, r 44.501°). Draws north of 15 S, where the arc file ends, are measured to its end point; they are a negligible share.

**Dawn.** At impact the local solar time is about 6.33–6.92 h (5–95 %). The sun elevation at the impact point at impact time is 5/25/50/75/95 % = [4.7, 5.6, 7.6, 9.5, 11.9] deg (D0). The sun is above the horizon at every draw. 83 % of the mass has the sun below 10° at impact, and 60 min later the median is 19.5°. Sun elevations use the Meeus low-precision formula in satgeom (about 0.1°), computed at the target and the crossing time.

## 3. Coincidence
- 89 satellites have March 2014 element sets (SGP4, 5 s steps, 7 Mar 23:00 – 8 Mar 08:30 UTC). This reproduces the parent's 5 s track file exactly where they overlap (max difference 0.0°). **19 classified satellites in the specs table have no element sets and are excluded:** TecSAR, SAR-Lupe 1/2/4, Lacrosse 4, Topaz 1/2, IGS Optical 3/4/5-demo, IGS Radar 3/4, KH-11 USA 224 and USA 161, Helios-2A/2B, Ofeq-5/7/9. The 28 Flock-1 rows are ignored.
- 346 pass segments were taken where nadir is inside 62 S–2 N, 50–135 E. For each, the zero-Doppler crossing was found for every distinct impact point (static targets; 1,944,686 unique points). Coverage rule as given: SAR near ≤ |offset| ≤ far on an allowed side; optical |offset| ≤ ground offset at max off-nadir + half swath, sun ≥ 10° at the target at crossing (0–10° reported as low sun). The near/far altitude is the pass median.
- 113 passes have impact points inside their band at some time. 12 qualify inside 30 min before to 60 min after impact.

**Union over passes, share of posterior mass** (pre = 30 min to 0 before impact; post = after impact):
| option | radar ±30 min | radar −30/+60 | optical day ±30 | optical day −30/+60 | optical low sun (all pre-impact) | radar pre-impact only | radar post 0–30 | radar post 0–60 | optical day post 0–60 | **radar or optical day, post 0–60** |
|---|---|---|---|---|---|---|---|---|---|---|
| D0 | 0.970 | 0.970 | 0.075 | 0.105 | 0.510 | 0.801 | 0.770 | 0.770 | 0.105 | **0.855** |
| D2 | 0.978 | 0.978 | 0.061 | 0.090 | 0.597 | 0.692 | 0.839 | 0.839 | 0.090 | **0.908** |
| D4 | 0.987 | 0.987 | 0.023 | 0.081 | 0.822 | 0.862 | 0.929 | 0.929 | 0.081 | **0.986** |

**Pre-impact crossings test a fixed point, not the aircraft.** A crossing of a draw's impact point before that draw's impact time sees open sea, unless the aircraft was already over that point. That holds only in the last minutes of a steep descent. In-flight coincidence needs the moving trajectory, which is the parent's track. Only post-impact crossings can support elimination by surface evidence (aircraft, debris, fuel, foam). The RADARSAT-2 pass (23:57–00:02) and the COSMO-SkyMed 1 pass (00:07–00:09) come before the earliest impact (00:19:37). The single low-sun optical pass (Proba-1, about 00:04, sun −2 to 4° at the targets) is also pre-impact.

**Seed stability (D0, radar or optical day, post 0–60):** pooled 0.855, per-seed range 0.79–0.90, SD of the 12/12 split-half difference 0.012. Radar post 0–60: 0.770 (seeds 0.68–0.84, split-half SD 0.016). Quote these to two decimals.

**Time to first post-impact access (D0):** median radar 13 min, daylight optical 96 min, either 13 min. Every draw has access by radar or daylight optical within 120 min, and by radar within 240 min. The first broad daylight optical pass is Yaogan-11 at 01:11–01:18 UTC. Cartosat-2 (02:02–02:08) and Yaogan-4 (02:07–02:11) follow. See impact-window-cumulative.png.

## 4. Strongest passes (top 8 by D0 mass, −30/+60 window)
| satellite | type | crossing over corridor (UTC) | footprint lat | mass 30 min before | mass 0–60 min after | sun at targets (deg) | band |
|---|---|---|---|---|---|---|---|
| COSMO-SkyMed 3 | radar | 00:35:10–00:36:49 | -40.2 to -32.6 | 0.347 | 0.582 | 5–11 | near 209 km, far 894 km (right) |
| COSMO-SkyMed 2 | radar | 00:54:26–00:55:49 | -42.1 to -35.4 | <0.001 | 0.494 | 6–12 | near 209 km, far 894 km (right) |
| RADARSAT-2 | radar | 23:57:19–00:02:37 | -43.7 to -28.0 | 0.427 | 0.000 | -9–6 | near 126 km, far 1083 km (left,right) |
| Beijing-1 | optical | 00:52:37–00:55:21 | -36.7 to -25.2 | <0.001 | 0.092 | 14–21 | 0 to 419 km either side |
| Yaogan-11 | optical | 01:11:52–01:18:29 | -37.4 to -15.0 | 0.000 | 0.085 | 18–33 | 0 to 470 km either side |
| COSMO-SkyMed 1 | radar | 00:07:23–00:09:31 | -36.5 to -27.1 | 0.055 | 0.000 | 4–10 | near 209 km, far 894 km (right) |
| Yaogan-8 | optical | 01:35:13–01:41:52 | -34.9 to -15.0 | 0.000 | 0.006 | 26–39 | 0 to 750 km either side |
| KOMPSAT-5 | radar | 01:01:14–01:02:38 | -43.7 to -36.5 | <0.001 | 0.005 | 2–12 | near 186 km, far 684 km (left,right) |

COSMO-SkyMed 3 (corridor crossing 00:35:10–00:36:49 UTC) dominates, at a median of 4 min after impact. Its right-looking 209–894 km band covers 0.93 of D0 mass inside ±30 min. That is 0.58 after impact and 0.35 for draws whose impact comes after the crossing. COSMO-SkyMed 2 (00:54:26–00:55:49) covers 0.49 after impact. **Theoretical access only.** One SAR acquisition covers one beam: with the specs table's nominal swath, about 1.5 % of the CSK band and 0.9 % of RADARSAT-2's. Wide ScanSAR modes (100–500 km) would cover far more, but nothing says a sensor was on or tasked here.

**Elimination needs all three of:** (a) the scene exists; (b) a detection probability for the target class (intact aircraft or large section: SAR yes at metre resolution; floating debris or flaperon: needs ≤ 1–3 m; fuel slick or foam: SAR sea-surface damping, wind dependent); (c) the scene was examined. None of (a)–(c) is known for any pass here.

**Query list** (`impact-window-query-list.csv`, 131 rows: 22 SAR, 108 optical daylight, 1 optical low sun). It holds every pass whose band meets the ±100 NM corridor from 23:49:37 UTC on 7 Mar to 08:00 UTC on 8 Mar. Optical passes entirely at night are dropped. Each row has the satellite, NORAD id, UTC window (corridor crossing ±60 s), the footprint (band ∩ corridor) as WKT in lon/lat simplified to 0.01°, the access band, sun range, and covered posterior mass. Archive operators: ASI/e-GEOS (COSMO-SkyMed), MDA (RADARSAT-2), KARI (KOMPSAT-5), DMC/21AT (Beijing-1), ISRO (Cartosat), and national agencies for Yaogan and KH-11. Element-set age at the pass: KH-11 USA 186 is 211 h, Lacrosse 5 198 h and SAR-Lupe 5 89 h, so their timing is uncertain by minutes or more. The next oldest is 19 h (KH-11 USA 245), and the dominant commercial and dual-use passes are within about 4 h. Column tle_age_h in the query list carries this for every row.

## 5. Open-archive scenes (77) against the impact window
- Within 24 h of 00:19:37 there are 7 scenes, all from one ASTER strip on 8 Mar at 04:47:06–04:47:59 UTC (Terra, centres 38.75–41.91 S, 77.8–76.7 E). Edge-to-arc distances are 7–394 km; the per-scene minima run 308, 259, 209, 159, 108, 58 and 7 km from north to south. 4 of the 7 touch the ±100 NM corridor, all at 40.3–42.25 S. **Overlap with the impact posterior is zero: 0 of 1.5 M draws under D0, D2 and D4.** The strip is south and west of the 99 % region. The parent's expected 52–350 km came from a different distance definition; here distances are from footprint edges to the shared sea-level arc.
- At any date, 6 scenes touch the corridor. The largest posterior overlap is EO-1 on 25 Mar (about 03:30, time inferred), at 9.5e-4 and 7.3e-4 of D0 mass. That is 17 days after impact and relevant only to drifted debris, not the impact window. Table: archive-scenes-impact-check.csv.

## Caveats
1. Theoretical access is an upper bound: band, not beam; no tasking, duty-cycle, downlink or archive knowledge.
2. Classified systems without element sets (19) are missing, so true access is higher, not lower.
3. Specs (incidence ranges, off-nadir limits, look side) come from satellite-specs-expanded.csv, with spec_grade per row in the CSVs. COSMO-SkyMed is right-looking only per the table.
4. The static-target treatment means pre-impact coverage is not physical.
5. Waypoints family only (0.9982).
6. Sun elevation uses the low-precision formula (about 0.1°). The 10° daylight threshold is the module convention.
7. Monte Carlo: split-half SD about 0.01–0.02 on union masses, and seed-to-seed spread is large, so quote two decimals.
8. Cross-arc distance uses the shared sea-level arc polyline. End of flight's arc_distance_nm column agrees with it to a median of −0.05 NM.
