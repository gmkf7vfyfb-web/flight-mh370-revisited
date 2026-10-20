# Searched areas: coverage sources and maps (seabed, aircraft and ships, beacon searches, sonobuoys) — posted 20 Oct 2026

Searched Areas (general session, default profile, to `threads/master-prompts/searched-areas.md`). Work of 17–20 Oct 2026, posted at
Pete's request (20 Oct). This folder is a map and source layer only: none of it is a likelihood term yet (the surface-search term is
listed as next work). Labels: Ocean Infinity coverage inferred (grade C), included as best estimate; the planned next Ocean Infinity
block is a map layer only, never evidence (ruling 18 Oct 00:41Z).

## Files
- `searched-areas-overview-map.png/.pdf` — everything searched and not searched, 82–117° E, 47.5–17° S (v3, 18 Oct).
- `uld-and-sonobuoy-searches-2014.png/.pdf` — the April 2014 searches for the recorder beacons (separate chart, formerly the inset).
- `searched-areas-spatial-detection-maps-north-of-33S.png/.pdf` — the per-cell detection maps north of 33° S (companion of
  `results/searched-areas-spatial-detection/`; corrected fields of 20 Oct, see that note's correction section).
- `aerial_surface_search_source_ledger.md` — sources for the aircraft, ship, satellite and radar searches (v2, corrected).
- `seabed-surveys-and-searches-sources-ledger.md` — sources for the seabed surveys and searches (v2).
- `data/` — GA/AMSA `Search_And_Rescue_Search_Area2014` (387 daily polygons, day n = 7 Mar + n) and the wide search area as GeoJSON;
  daily polygon summary; near-arc union by latitude; daily surface-search table; search elements; CSIRO POD-by-latitude curve
  (digitised); RNZAF P-3 image positions.

## Findings
1. **Near the 7th arc (±25 NM), seabed sonar left unsearched:** 20 % at 40.5–33° S, 18 % at 33–25° S, 98 % at 25–17° S.
2. **Aircraft and ship search (AMSA daily boxes):** union 1.72 M km², up to 9 days at one place. Near-arc share searched: 0.00–0.01 at
   35–37° S; about 0.5 at 33–35° S; 1.0 at 27–33° S and 20–22° S; 0.78–0.91 at 37–40° S; 0.00 at 23–26° S. Only the 19 Mar and 30 Mar
   boxes came within 100 NM of the arc at 34–37.5° S.
3. **The 35–37° S gap is real.** It agrees with CSIRO ("no search effort" at 35–37° S) and with ATSB (the 34–35.5° S satellite
   detections were never searched by air).
4. **Chinese task areas are not in the AMSA boxes.** 30 Mar–3 Apr: 26–34° S, 91–104° E (PRC MFA, 31 Mar; Haixun 01, Nan Hai Jiu 115 and
   Dong Hai Jiu 101 the northern half, four naval ships the southern half). 4–6 Apr: 20–26° S, 101–104° E (Xinhua, 5 Apr; Haixun 01,
   Jinggangshan, Kunlunshan). **Correction:** the 23–26° S near-arc gap in the AMSA boxes was searched by Chinese ships on 4–6 Apr; how
   much of the task area they covered is not known (only outlines were published). Drawn as dotted outlines.
5. **Haixun 01:** about 250,000 km² over a 216-day deployment (Sina 2018); no tracks published. Placed on the maps: the two task areas,
   the ULD contacts (ATSB 25.975° S 101.461° E and about 3 km west; Chinese reports 25.6° S 101.3° E) and the re-check boxes of 7 Apr
   (144 km²) and 8 Apr (432 km²). The inferred Ocean Infinity 2018 seabed coverage includes both ATSB contact positions.
6. **Sonobuoys:** RAAF AP-3C, up to 84 per sortie, about 3,000 km² per sortie, 6–16 Apr; positions never published. Fields drawn at the
   Ocean Shield contacts and at an inferred location (26.7° S, 100.7° E, from ATSB Jun 2014 p. 13); a field at Haixun 01 (ATSB 2017) is
   unconfirmed (dotted).
7. **Terminology:** charts use the ICAO Annex 6 term "underwater locating device (ULD)"; ATSB uses ULB.

## Next
- Surface-search likelihood term (GA daily polygons × CSIRO POD curve; Chinese task areas as a sensitivity layer).
- Ask ATSB / GA for the Phase 2 gap and lower-confidence polygons (closes G-LPD of the per-cell note).
