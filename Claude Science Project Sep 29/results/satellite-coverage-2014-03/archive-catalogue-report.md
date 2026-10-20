# Archive catalogue check: satellite scenes over the MH370 search box, 7-28 March 2014

Question: which satellite scenes that actually exist in a public archive were acquired over 20-45 S, 70-110 E between 7 Mar 2014 16:00 UTC and 28 Mar 2014 00:00 UTC? Queried 20 Oct 2026 from the analysis sandbox. Scene table: `archive-scenes-2014-03.csv` (77 rows). Map: `archive-scenes-overlay-2014-03.png` / `.pdf`.

Continuous wide-swath sensors (MODIS, VIIRS, AVHRR class) are excluded by design: they image everything every day and say nothing about tasking. NASA CMR returned 574 MOD021KM granules for the box/time, which confirms MODIS is irrelevant for this purpose; they are not listed.

## 1. Per-catalogue results

| # | Catalogue | Endpoint | Query | Result | Access status |
|---|---|---|---|---|---|
| 1a | USGS Landsat (Collection 2) | `https://landsatlook.usgs.gov/stac-server/search` (POST) | bbox 70,-45,110,-20; datetime 2014-03-07T16:00Z/2014-03-28T00:00Z; collections landsat-c2l1, landsat-c2l2-sr | 5 scenes, all Landsat 8 OLI/TIRS, Tier 2 L1GT; 0 Landsat 7 | Open, answered |
| 1b | USGS EO-1 ALI / Hyperion | same STAC server; collections eo-1-ali-l1gst, eo-1-ali-l1t, eo-1-hyperion-l1gst, eo-1-hyperion-l1t | same bbox/time | 2 ALI + 2 Hyperion scenes (two passes: 9 Mar and 25 Mar 2014); L1T collections empty | Open, answered |
| 1c | USGS M2M API | `https://m2m.cr.usgs.gov/api/api/json/stable/dataset-search` | anonymous POST | HTTP 403 | Login needed (ERS account); not held. Not required: the STAC server exposes the same collections |
| 2 | NASA CMR, ASTER | `https://cmr.earthdata.nasa.gov/search/granules.json` | short_name AST_L1A (also AST_L1T, AST_L1B); bounding_box 70,-45,110,-20; temporal 2014-03-07T16:00:00Z,2014-03-28T00:00:00Z | 17 granules in each of L1A/L1T/L1B (same acquisitions): 7-granule strip 8 Mar 04:47 UTC, 10-granule strip 25 Mar 03:52 UTC | Open, answered |
| 3 | NRCan EODMS (RADARSAT-2) | `https://www.eodms-sgdot.nrcan-rncan.gc.ca/wes/rapi/search?collection=Radarsat2&format=json&footprint=POLYGON(...)&query=CATALOG_IMAGE.START_DATETIME>=...` | anonymous GET; also `/collections` and `/collections/Radarsat2` | `/collections` answers (200) but every search returns HTTP 500 "Search failed. Did not have valid permissions to contact Search Service"; `/collections/Radarsat2` returns 401 | Login needed (free EODMS account); not held |
| 4a | DLR EOWEB GeoPortal (TerraSAR-X / TanDEM-X) | `https://eoweb.dlr.de/egp/` | page load | HTML portal; archive search behind a login | Login needed; not held |
| 4b | DLR EOC geoservice CSW | `https://geoservice.dlr.de/catalogue/srv/eng/csw` GetRecords, AnyText like %TerraSAR% | 48 records, all collection-level descriptions (TerraSAR-X StripMap/ScanSAR/Spotlight product families, TanDEM-X DEMs, GUF); no scene footprints | Open, but no scene-level TerraSAR-X archive |
| 4c | DLR EOC STAC | `https://geoservice.dlr.de/eoc/ogc/stac/v1/collections` | list | 69 collections, none a TerraSAR-X scene archive | Open, not applicable |
| 5a | Maxar discovery | `https://discover.maxar.com/` | page load | redirects to `https://xpress.maxar.com/` (single-page app, sign-in required) | Login needed; not held |
| 5b | Maxar Geospatial Platform API | `https://api.maxar.com/discovery/v1/collections` | anonymous GET | HTTP 401 "No JWT bearer token found ... or API Key provided" | API key needed; not held |
| 6a | Airbus OneAtlas archive search | `https://search.foundation.api.oneatlas.airbus.com/api/v2/opensearch` (POST JSON) | bbox "70,-45,110,-20"; acquisitionDate "[2014-03-07T16:00:00Z,2014-03-28T00:00:00Z]"; itemsPerPage 50; startPage 1-2 | 51 items: Pleiades-1A 13, Pleiades-1B 20, SPOT-6 18. No SPOT-5 (not in OneAtlas) | Open (anonymous POST accepted), answered |
| 6b | Airbus GeoStore | `https://www.intelligence-airbusds.com/geostore/` | page load | host off the sandbox allowlist; not requested because GeoStore requires an account in any case | Not reached / login needed |
| 6c | CNES SPOT World Heritage (SPOT 1-5) | `https://regards.cnes.fr/api/v1/rs-catalog/engines/legacy/datasets/search`, `.../dataobjects/search`, `.../opensearch/datasets/search` | anonymous GET | HTTP 403 Access Denied on every API path; portal page `/user/swh/` loads | Login/token needed; not held |
| 7 | Planet Data API (RapidEye) | `https://api.planet.com/data/v1/quick-search` (POST) | item_types REOrthoTile; DateRangeFilter | HTTP 401 "Please provide valid credentials" | API key needed; not held |
| 8 | Copernicus Data Space (ESA) | `https://catalogue.dataspace.copernicus.eu/odata/v1/Products` | Collection SENTINEL-1, Intersects(box), ContentDate/Start < 2014-06-01 | count 0 (Sentinel-1A launched 3 Apr 2014). Any collection, box, 7-28 Mar: 2,900 products, all MODIS MCD43A4 mirrors | Open; nothing applicable, confirmed |
| 9a | CRESDA (Gaofen-1, ZY-3) | `http://www.cresda.com/`, `https://data.cresda.cn/` | page load | HTTP 502 and 403 (server-side refusal) | Not reachable / login needed |
| 9b | KARI KOMPSAT via SI Imaging Services | `https://www.si-imaging.com/`, `https://catalog.si-imaging.com/` | page load | corporate site loads; catalogue host off allowlist and account-based | Login needed; not held |
| 9c | GISTDA THEOS | `https://catalog.gistda.or.th/`, `https://www.gistda.or.th/` | page load | connection fails through the sandbox proxy even after allow-listing | Blocked; not reached |
| 9d | ISRO NRSC Bhoonidhi (Cartosat, Resourcesat) | `https://bhoonidhi.nrsc.gov.in/` | page load; probe of `/bhoonidhi-api/` | portal loads (HTML app); search needs a registered user; no anonymous JSON API found | Login needed; not held |

## 2. Scenes found (77 rows)

| Date (UTC) | Satellite | Scenes | Mean centre lat | Centre lon range | Mean cloud % |
|---|---|---|---|---|---|
| 2014-03-08 | Terra | 7 | -40.3 | 76.7-77.8 | 89 |
| 2014-03-09 | EARTH_OBSERVING_1 | 2 | -34.3 | 97.2-97.4 | 25 |
| 2014-03-09 | Pleiades-1B | 1 | -37.8 | 77.6-77.6 | 12 |
| 2014-03-21 | Pleiades-1A | 5 | -43.3 | 90.4-90.8 | 100 |
| 2014-03-21 | Pleiades-1B | 7 | -43.2 | 90.4-90.8 | 89 |
| 2014-03-21 | SPOT-6 | 6 | -43.3 | 89.3-91.9 | 97 |
| 2014-03-22 | Pleiades-1A | 4 | -43.1 | 91.7-92.3 | 93 |
| 2014-03-22 | SPOT-6 | 3 | -43.2 | 90.7-92.1 | 98 |
| 2014-03-23 | LANDSAT_8 | 1 | -37.5 | 78.0-78.0 | 94 |
| 2014-03-23 | Pleiades-1B | 4 | -45.0 | 89.9-90.5 | 100 |
| 2014-03-23 | SPOT-6 | 4 | -44.9 | 89.9-92.2 | 99 |
| 2014-03-24 | LANDSAT_8 | 2 | -43.9 | 89.5-90.0 | 84 |
| 2014-03-24 | Pleiades-1B | 4 | -45.0 | 89.9-90.5 | 71 |
| 2014-03-24 | SPOT-6 | 5 | -44.9 | 89.6-92.4 | 76 |
| 2014-03-25 | EARTH_OBSERVING_1 | 2 | -34.9 | 95.0-95.2 | 30 |
| 2014-03-25 | Terra | 10 | -42.9 | 90.6-92.3 | 87 |
| 2014-03-26 | LANDSAT_8 | 2 | -43.9 | 92.6-93.1 | 18 |
| 2014-03-26 | Pleiades-1A | 4 | -43.3 | 86.2-86.9 | 100 |
| 2014-03-27 | Pleiades-1B | 4 | -44.4 | 86.1-86.7 | 46 |

Notes by catalogue:

- **Landsat 8.** Four of the five scenes (paths 125 and 127, rows 90-91; 24 Mar 03:42 UTC and 26 Mar 03:29 UTC) are open-ocean scenes at 43.2-44.6 S, 89.5-93.1 E. Landsat 8 does not acquire open ocean on its routine long-term acquisition plan, so these are tasked acquisitions; they coincide in place and time with the 21-27 Mar Airbus tasking and the ASTER strip of 25 Mar. Cloud cover 7 % (path 125 row 91, 26 Mar) to 97 %. The fifth scene (path 136 row 86, 23 Mar) contains Ile Amsterdam and is a routine land target. No Landsat 8 scene exists anywhere in the box between 7 and 22 Mar, and no Landsat 7 scene at all.
- **EO-1.** Two tasked passes (ALI + Hyperion each): path 124 row 84 on 9 Mar 2014 (centre 34.3 S, 97.4 E, cloud 20-30 %, look angle -3 to -4 deg) and path 125 row 84 on 25 Mar 2014 (centre 34.9 S, 95.2 E, cloud 30 %, look angle -14 to -15 deg). Dates come from the day-of-year in the scene identifier; the STAC `datetime` field (10/11 Mar, 26/27 Mar) differs between the two instruments of one pass and is treated as a processing stamp. Time of day is not exposed; ~03:30 UTC is inferred from EO-1's ~10:00 local descending node and the 37 deg sun elevation (provisional). The 9 Mar scene is 230-245 km east of the 7th arc; the metadata does not say what it was tasked for.
- **ASTER (Terra).** Strip 1: 8 Mar 2014 04:47 UTC, 7 granules, 38.4-42.2 S along 76.5-78.3 E, cloud 68-100 %. It starts over Ile Saint-Paul / Amsterdam and continues ~400 km south over open ocean; it is 52-350 km from the 7th arc and about 4.5 h after the 00:19 UTC final transmission. Nobody was tasking for MH370 at that time, so it is most plausibly a scheduled island/ocean acquisition; its content has not been examined. Strip 2: 25 Mar 03:52 UTC, 10 granules, 40.2-45.6 S along 90.1-92.7 E, cloud 49-100 %, over the same southern zone as the Airbus and Landsat 8 scenes.
- **Airbus (Pleiades-1A/1B, SPOT-6).** One routine scene 9 Mar 05:07 UTC over Ile Amsterdam (37.8 S, 77.6 E, 12 % cloud). All other 50 scenes are 21-27 Mar at 42.5-45.0 S: 21 Mar (PHR1A x5, PHR1B x7, SPOT6 x6 at 42.5-44.0 S, 89.3-91.9 E), 22 Mar (PHR1A x4, SPOT6 x3 at 43.0-43.2 S, 90.7-92.3 E), 23 Mar (SPOT6 x4, PHR1B x4 at 44.9-45.0 S, 89.9-92.2 E), 24 Mar (SPOT6 x5, PHR1B x4 at 44.9-45.0 S, 89.6-92.4 E), 26 Mar (PHR1A x4 at 43.3 S, 86.2-86.9 E), 27 Mar (PHR1B x4 at 44.4 S, 86.1-86.7 E). Cloud cover is 59-100 % on 21-24 Mar, 99-100 % on 26 Mar, 7-72 % on 27 Mar. Acquisition times are taken from the product identifier (e.g. DS_PHR1A_201403210426444 = 04:26:44 UTC, 10:30 local solar at 90 E, consistent with the 10:30 descending node); the catalogue `acquisitionDate` field is 3-6 h later for these items and is not used. Pleiades footprints are ~20 x 20 km, SPOT-6 ~60 x 60 km. Geoscience Australia's 2017 report analysed four Pleiades-1A scenes of 23 Mar ~100 km apart supplied by French military intelligence; the OneAtlas archive shows Pleiades-1B (not 1A) on 23 Mar, 4 scenes along 44.96 S. Whether the GA scenes are these items or a separate defence tasking not held in the commercial archive cannot be settled from the catalogue.
- **RADARSAT-2, TerraSAR-X, WorldView/GeoEye/QuickBird/IKONOS, RapidEye, SPOT-5, Gaofen-1/ZY-3, KOMPSAT, THEOS, Cartosat/Resourcesat.** No scene list could be obtained; absence from the table is not evidence of absence.

## 3. What the actual acquisitions say

**7-15 Mar 2014 (first window).** Across the open catalogues there are 10 scenes in the whole box: the 8 Mar ASTER strip at 76.5-78.3 E (scheduled, 68-100 % cloud), the 9 Mar EO-1 pair at 34.3 S, 97.4 E, and the 9 Mar Pleiades-1B island scene. Nothing from Landsat 8 (whose Tier-2 ocean scenes show up readily when tasked, as the 24/26 Mar examples prove), nothing from Pleiades/SPOT-6 within 400 km of the 7th arc, no ASTER tasking near the arc. In the open record the 6th/7th-arc corridor between 20 and 45 S was not imaged by any pointable optical system from 10 to 20 Mar inclusive; the EO-1 9 Mar pass is the only medium-resolution scene within 250 km of the arc in this window, and it is the one item whose purpose is unexplained.

**16-27 Mar 2014 (second window).** 67 scenes, 64 of them in one cluster at 40.2-46.3 S, 85.9-94.5 E (all 16-27 Mar scenes except the Ile Amsterdam Landsat 8 scene and the two EO-1 scenes: 32 Pleiades, 18 SPOT-6, 10 ASTER, 4 Landsat 8; union of footprints ~208,000 km2, provisional: catalogue footprints, not cloud-free area). The cluster was built up from 21 Mar (Pleiades + SPOT-6), with Landsat 8 on 24 and 26 Mar and ASTER on 25 Mar added, then displaced west to 86-87 E on 26-27 Mar. It is 400-800 km south-west of the 7th arc: it sits where the 16-27 Mar surface search and the published satellite sightings were, not where the arc is. The only arc-proximal acquisition is the EO-1 pass of 25 Mar (137-150 km from the arc at 34.9 S). Cloud cover on 21-26 Mar is mostly above 85 %; only 27 Mar (Pleiades-1B, 7-72 %) and the 26 Mar Landsat 8 path 125 row 91 scene (7 %) offer largely clear views.

**Contrast with theoretical access.** The parent's access map gives near-complete (99 %) daily theoretical access to the arc from the combined fleet on every day 7-15 Mar. The archives show that, among the systems whose catalogues are open, that access was exercised over the arc essentially not at all in the first window and only once (EO-1, 25 Mar) in the second. The accounted-for tasking went to the 43-45 S zone from 21 Mar onward. The commercial and governmental systems with closed catalogues (WorldView, GeoEye, RADARSAT-2, TerraSAR-X, Gaofen-1, KOMPSAT, THEOS, RapidEye, SPOT-5) remain the open question for 7-15 Mar.

## 4. Deviations and caveats

- Catalogues 3, 4a, 5a-b, 6b-c, 7, 9a-d returned no scene lists (login, key or routing). Counts here are a lower bound restricted to USGS, NASA and Airbus holdings.
- EO-1 acquisition times are inferred, not read; Airbus times are read from identifiers rather than the catalogue date field.
- Landsat c2l2-sr duplicated the five c2l1 scenes and is listed once; ASTER AST_L1T/L1B duplicate AST_L1A and are listed once.
- No scene content was downloaded or inspected.
