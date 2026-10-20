# Debris drift and satellite "calibration sightings": feasibility study (track C)

Status: provisional. Results go to the parent session, not the repository. Prepared 20 Oct 2026.

## Question
Can archived satellite scenes act as "calibration sightings" of the large recovered debris (the flaperon, found at Réunion on 29 Jul 2015, and the outboard flap section) along their drift paths, so that a sighting or a confirmed non-sighting narrows the drift path and the source latitude on the 7th arc?

## Short answer
No, not for the open-ocean drift. One narrow case is the exception.
- **Open-ocean drift (8 Mar 2014 to 29 Jul 2015).** The open archives hold 6,263 Airbus scenes (2,770 Pleiades, 3,493 SPOT-6/7) and 13,318 medium-resolution scenes inside the flaperon's 90 % drift envelope. The expected number of flaperon detections summed over all of them is about **0.0004** (central detection model, run J weighting), with a bracket of 3e-05 to 0.0016. Per source latitude the values are 25 S 0.00062, 30 S 0.00054, 35 S 0.00036 and 40 S 0.00044. Non-detection in every scene therefore changes the log-likelihood between any two source latitudes by less than 2 × 10⁻⁴. A single hypothetical detection is also uninformative, because at 0.5-0.7 m a flaperon cannot be told apart from the about 0.3 flaperon-sized-or-larger false candidates per km² reported in the Mar 2014 Pleiades analysis.
- **Réunion find coast (the exception).** Pleiades imaged the find coast (Étang de Bois Rouge, Saint-André) 13 times between 31 May and 10 Jul 2015, and the 10 Jul scene has 0 % cloud. Suppose the flaperon had beached 30-60 days before the find, as the barnacle-over-abrasion sensitivity (BIO-06) suggests, and stayed in place. Then the probability that at least one of these scenes shows it on the beach is **0.87** (bracket 0.47-0.99). Inspecting about 6-8 archived Pleiades scenes would therefore test BIO-06 with real power: an empty beach in all of them gives a likelihood ratio of about 0.13 against BIO-06. It still says little about source latitude. In the drift ensemble, moving the beaching date from late July to June changes the 30 S : 40 S odds by a factor of only about 1.3-1.6, and that estimate is noisy (11-52 particles per bin).
- **What would change the answer.** Better data access would not open the open-ocean case either: Maxar's 0.31-0.46 m archive and Planet's SkySat would raise the per-scene detection probability by perhaps 2-5×, still far from the 10⁴× needed. The lever is the Réunion beach series (Airbus archive purchase), plus Maxar's archive over the same beach.

## 1. Detectability
Object classes (project drift module): the flaperon is about 2.3 × 1.7 m in plan, ~2.6 m² (DGA-dimensioned proxy, 1.68 × 2.32 m, 2.59 m²). It floats low and is barnacle-fouled. The CSIRO cut-down real flaperon floated with part of the trailing edge clear of the water. Its drift class is wind factor 0.012 plus leeway 0.10 ± 0.03 m/s at 0-30° left of the wind. The outboard flap section (found at Pemba on 20 Jun 2016) is treated as a "large panel" with the low-exposure-exterior class (wind factor 0.012 ± 0.003, no leeway). Its dimensions were not found in the sources read here, so it gets the flaperon detection model, which is conservative for a larger object.

Critical dimension √A ≈ 1.6 m. Pixels across it at native GSD: WorldView-3 0.31 m (from Aug 2014; 0.31 m product sales from 2015) ≈ 5.2 px; GeoEye-1 0.41 m ≈ 3.9; WorldView-2 0.46 m ≈ 3.5; WorldView-1 0.5 m ≈ 3.2; **Pleiades 0.70 m native (resampled to a 0.5 m product)** ≈ 2.3; KOMPSAT-3 0.7 m ≈ 2.3; SkySat ~0.9 m ≈ 1.8; SPOT-6/7 1.5 m ≈ 1.1; Sentinel-1 WV 5 m, Sentinel-2 10 m, ASTER 15 m and Landsat 15/30 m are all sub-pixel. By Johnson-criterion reasoning (detection ≈ 1 cycle ≈ 2 px across the critical dimension; recognition ≈ 4 cycles ≈ 8 px), only ≤ 0.5 m systems can *detect* a flaperon-sized anomaly in ideal conditions. No 2014-15 commercial system could *recognise* it as aircraft structure. Military optical systems (KH-11 class 0.1-0.15 m, Helios-2 0.35 m) could, but their archives are closed.

Scene conditions reduce detection well below the ideal-background value:
- low freeboard and partial awash cut contrast (factor ~0.5);
- whitecaps at the usual 8-12 m/s winds of 25-45 S give bright patches of the same size, at a coverage of order 1 % (Monahan-type whitecap laws);
- sun glint;
- cloud, applied per scene as (1 − catalogue cloud fraction). The median Pleiades cloud cover in the envelope is 21 %.

The empirical false-alarm density is high. Malaysia's analysis of the 23 Mar 2014 Airbus Pleiades imagery reported 122 potential objects of 1-23 m in about 400 km², and none was confirmed.

Detection probability per scene, given the object is inside the footprint and the sky is clear (low / central / high):

| Sensor class | Open ocean | On a known beach, multi-date change detection |
|---|---|---|
| Pleiades (0.7 m native, 0.5 m product) | 0.01 / 0.05 / 0.20 | 0.10 / 0.30 / 0.60 |
| SPOT-6/7 (1.5 m) | 0 / 0.005 / 0.02 | 0.01 / 0.03 / 0.10 |
| ≥ 5 m (Landsat, ASTER, Sentinel-1/2) | 0 | 0 |

These are judgement-based brackets, not measured values. A measured detection curve would need a planted-target experiment.

## 2. Drift ensemble
**New run not made.** The snapshot harness accepts a list of times, but the remote machine's heavy lock was held by Pete's staged calibration run (calib_driver.sh, which holds the lock for its whole run: pool build, then 31 cases on two lanes). That run also uses most of the 36 GiB memory limit, and the drift harness loads about 17 GB of ocean fields. The local Mac was at load 28 on 18 cores with 3.9 GiB disk free. As the task allows, the **existing 4-snapshot per-particle binaries were used** (full-globcurrent.bin sha256 237538d1…, full-glorys12.bin sha256 8f451f28…). These are releases at 25/30/35/40 S on the 7th arc (102.098/97.775/92.826/89.579 E) on 8 Mar 2014 00:19:37 UTC, with 33,336 flaperon-class and 33,336 large-panel-class particles per release per model (4 environment seeds × 8,334). Only two snapshots fall inside the window: 8 Mar 2015 (day 365) and 29 Jul 2015 (day 508.0). There is no release at the run J posterior median (37.14 S, 89.87 E, computed from the run J D0 impact histogram, mean latitude −36.717). The four releases are instead weighted by the run J latitude posterior mapped to the nodes (25 S 0.009, 30 S 0.028, 35 S 0.573, 40 S 0.390).

Positions between snapshots use a per-particle **Brownian bridge**: linear in lon/lat between the release point and the day-365 position (or the first-beaching point and time), then between day 365 and day 508. The bridge variance is 2K(t−a)(b−t)/(b−a) with K = 10⁴ m²/s, plus a 25 km kernel floor. Particles lost to the domain or to model error before a snapshot (0-10 %) are dropped. The bridge represents path ignorance, not ocean physics. Masses for scenes in the first 60 days rest entirely on it and are flagged `positions_by_bridge_only` in the table. The 90 % afloat region covers 1.1 × 10⁶ km² at day 20, 1.4 × 10⁷ km² at day 365 and 1.3 × 10⁷ km² at day 508.

Staged for a later run (not started): a SNAP_SPEC with times every 5 days from 8 Mar 2014 to 29 Jul 2015 (102 times), releases at the four arc points plus 37.14 S 89.87 E, 25,000 particles per class per environment (1 × 10⁵ per class per release per model). Measured harness speed is about 2 × 10⁵ particles per minute at 88 threads, so the job needs about 7-8 min per model. Output is about 0.8-1.3 GB per model. It needs the heavy lock to be free.

## 3. Expected yield
**(a) Open archives.** Catalogues were queried over monthly 90 % envelope polygons, 8 Mar 2014 to 29 Jul 2015. Each scene was then kept only if its footprint meets the envelope at the scene's own date (5-day envelope grid, one-cell dilation).

| Archive | Scenes in envelope | Detection class |
|---|---|---|
| Airbus OneAtlas (anonymous POST) | 2770 Pleiades, 3493 SPOT-6/7 | sub-metre / 1.5 m |
| USGS LandsatLook STAC | 8,569 (5,139 Landsat 8, 3,430 Landsat 7) | 0 |
| NASA CMR (AST_L1T) | 3,176 | 0 |
| Copernicus Data Space | 1,569 Sentinel-1A (IW, EW, WV, stripmap) + 4 Sentinel-2A | 0 |

The OneAtlas tile query returned 48,787 items in total; Maxar, Planet, KOMPSAT and EODMS need logins and were not queried. Most envelope-intersecting Pleiades scenes are coastal (Madagascar, Mascarenes, East Africa, Western Australia). The open southern Indian Ocean is almost never imaged: 60-70 E × 20-30 S has 4 Airbus scenes in Jan-Jul 2015. The largest per-scene masses are in the Mar-Apr 2014 search-area tasking, for example the SPOT-6 strips of 28 Mar 2014 at 37.4 S, 94-95 E (35 S and 40 S masses 0.03-0.04) and the Pleiades scenes of 30 Mar-1 Apr 2014 near 38.7 S, 95.3 E (40 S mass ~2 × 10⁻³). These scenes are 90-100 % cloud, and their masses are bridge-only. After day 60 the largest Pleiades mass (run J weighting) is 6e-05, and the median is 3e-08.

Expected flaperon detections, summed over scenes (central model; model-mean masses):

| | 25 S | 30 S | 35 S | 40 S | run J weighted |
|---|---|---|---|---|---|
| Flaperon, all scenes | 0.00062 | 0.00054 | 0.00036 | 0.00044 | 0.0004 |
| Large panel, all scenes | 0.00063 | 0.00069 | 0.00018 | 0.00027 | 0.00023 |
| Flaperon, Pleiades only | 0.00038 | 0.00033 | 0.00015 | 0.00013 | 0.00015 |
| Flaperon, SPOT-6/7 only | 0.00024 | 0.00021 | 0.00021 | 0.00031 | 0.00025 |

Bracket for the run J weighted flaperon total: 3e-05 (low) to 0.0016 (high). The large-panel class is assessed only up to 29 Jul 2015, so the Pemba flap's last 11 months of drift are not covered.

**(b) Theoretical field of regard.** Eight commercial optical satellites of ≤ 0.7 m (WorldView-1/2, GeoEye-1, QuickBird, Pleiades-1A/1B, KOMPSAT-3, EROS-B) were propagated over 24 h with the March 2014 element sets (satgeom/coincide/access_params, sun ≥ 10° at the target). Their access bands reach **100 %** of the afloat flaperon mass, on both 8 Mar 2015 and 29 Jul 2015 positions. The local-time geometry is shifted to those dates, which is valid for sun-synchronous orbits. Single satellites reach 35-100 % (GeoEye-1 100 %, Pleiades-1A 67 %, Pleiades-1B 69 %). This result is uninformative. Field of regard is pointing capacity, not acquisition: each satellite images at most a few hundred 15-20 km scenes a day, chosen by customers and almost never over open ocean. Only the archive acquisitions in (a) count.

## 4. Réunion windward coast
100 scenes over Réunion were found for 29 May-29 Jul 2015, 52 of them in the last 30 days ({{artifact:7e81fec8-038d-4ce1-8ba5-25d1537a9baf}}). In the last 30 days the Pleiades acquisitions number 32, of which 25 cover part of the windward strip (the sea within 30 km of the east coast) and 3 contain the find site. The last Pleiades scene containing the find site is PHR1A 10 Jul 2015 06:38 UTC, 0 % cloud. Two scenes over the windward sea fall in the last week: PHR1B 23 Jul (5.9 days before the find) and PHR1B 28 Jul 06:48 UTC (0.9 days before the find, 11 % of the strip, 18 % cloud). Neither covers the find site. Landsat 8, ASTER and Sentinel-1A also imaged the coast but cannot resolve the object; no Sentinel-2A scene was found.

The final approach was modelled as a straight path ending at the find site, from a bearing uniform 30-120°, at a speed uniform 0.15-0.35 m/s. After beaching the object sits at the find site.
- **Fresh arrival (beached 0-3 days before the find):** no sub-metre scene contains the approaching object (P = 0 for every Pleiades and SPOT scene). An offshore calibration sighting near Réunion is therefore not available in the open archive.
- **BIO-06 (beached 30-60 days before the find and left in place):** P(at least one scene shows it) = 0.87 (bracket 0.47-0.99). This is driven by the Pleiades scenes of 8, 14, 15, 21, 26 and 27 Jun and 5, 9 and 10 Jul 2015. Caveats: beach-cleaning crews and waves could have moved the object; the detection model is a judgement; the find-site position is the étang coast, not a surveyed point.
- **What it would constrain.** It would fix the beaching date and so test the barnacle sensitivity. It would not fix the final approach direction (no offshore coverage) or the source latitude. Ratio of the June to late-July Réunion beaching rate per source latitude in the ensemble (particles per bin in brackets):
```
      model   lat  n_448_478  n_493_508    ratio
globcurrent -25.0          1          1 0.500000
globcurrent -30.0         22         22 0.500000
globcurrent -35.0         34         40 0.425000
globcurrent -40.0         16         25 0.320000
   glorys12 -25.0          8          4 1.000000
   glorys12 -30.0         30         11 1.363636
   glorys12 -35.0         52         33 0.787879
   glorys12 -40.0         25         15 0.833333
```

## 5. Conclusion: power to narrow source latitude
For a scene s with flaperon mass m_s(L) under source latitude L and detection probability p_s:
- Non-detection gives ln LR(L₁:L₂) = −Σ(m_s(L₁) − m_s(L₂)) p_s, which is the negative difference in expected yields. Measured here: 25 S vs 40 S **-1.8e-04**; 35 S vs 40 S **+7.9e-05**. This is negligible.
- A detection gives LR = (m₁p + f)/(m₂p + f), where f is the per-scene probability of a flaperon-like false candidate. At Pleiades resolution f ≈ 1 (122 candidates per 400 km² in Mar 2014), so LR ≈ 1. Only a *recognised* object (f → 0) would give LR = m₁/m₂. That ratio can be large: in the best Pleiades scenes of 30 Mar-1 Apr 2014, 40 S:35 S ≈ 4-30, and 25 S is effectively excluded. But the chance of such an event is ~10⁻⁶ per scene, and recognition needs ≤ 0.2 m GSD.
- **Data access that would change the answer:** (1) the Airbus archive Pleiades scenes of the Saint-André coast, 8 Jun-10 Jul 2015, read as a dated sequence for an object on the beach; (2) the Maxar (WorldView-2/3, GeoEye-1) and Planet SkySat archives over the same beach and the windward sea for 20-29 Jul 2015; (3) military optical holdings. None of these would make the open-ocean drift informative.

## Deliverables
- Figure: {{artifact:be2eee58-a101-48ee-9e81-89341052356e}} (PDF {{artifact:0243ef40-361d-417b-88a5-d6ce61c6845f}})
- Candidate scenes (19,581 rows; footprint WKT, per-latitude and per-model masses, detection probabilities, expected yields): {{artifact:3ad0ac8c-3c4b-42bc-a43a-673fa90623cd}}
- Réunion scenes (100 rows): {{artifact:7e81fec8-038d-4ce1-8ba5-25d1537a9baf}}

## Deviations and caveats
1. No new drift run. The existing 4-snapshot binaries were used, with Brownian-bridge interpolation; masses before day 60 rest on the bridge alone.
2. No release at the run J median; the run J posterior weights over the four arc nodes are used instead.
3. Archives searched: OneAtlas, USGS STAC (Landsat 7/8), NASA CMR (ASTER L1T only), Copernicus Data Space (Sentinel-1/2). Maxar, Planet, KOMPSAT, RADARSAT-2 and TerraSAR-X were not reachable without logins. Scene counts are lower bounds.
4. The detection probabilities are judgement brackets, not measurements.
5. Masses are Gaussian-kernel integrals over sea points of each footprint, sampled every 8 km for Airbus and every 25 km for medium-resolution scenes. Summed masses can exceed 1, because they count expected (scene, object) coincidences across time.
6. The large-panel class runs only to 29 Jul 2015.
