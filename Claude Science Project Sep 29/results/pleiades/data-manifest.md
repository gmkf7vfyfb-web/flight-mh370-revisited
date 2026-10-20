# Data manifest: GA Record 2017/13 object table

`engine/hypotheses/pleiades/data/ga-rec2017-13-objects.csv` holds all 70 objects from Tables 1-4 of

Minchin, S., Mueller, N., Lewis, A., Byrne, G., Tran, M., 2017. *Summary of imagery analyses for
non-natural objects in support of the search for Flight MH370: Results from the analysis of imagery
from the PLEIADES 1A satellite undertaken by Geoscience Australia.* Record 2017/13. Geoscience
Australia, Canberra. doi:10.11636/Record.2017.013. eCat 111041. CC BY 4.0, except images marked
(c) CNES.

| Item | Value |
|---|---|
| Retrieved | 2026-10-08, from `https://d28rz98at9flks.cloudfront.net/111041/Rec2017_013.pdf` (the eCat record's distribution link) |
| PDF sha256 | `1812498a5735463293cc125a3b7d964d823d2d581100af337d8650e1254220bd` (17,973,396 bytes, 51 pages) |
| Page numbers | The report's own printed page numbers, as in `source_pages` |
| Rating scale | GA's, footnoted under every table: 1 probably natural, 2 possible natural, 3 uncertain, 4 possible man-made, 5 probably man-made |

**What is committed and what is not.** Only the tabulated positions, pixel counts, areas and
ratings are committed; they are CC BY 4.0. The PDF is not committed, and nor is any figure or object
crop from it: every image in the report is (c) CNES. Read the PDF by path.

## Counts

| Scene | 1 | 2 | 3 | 4 | 5 | total |
|---|---|---|---|---|---|---|
| PHR_1 | 1 | 3 | 4 | 2 | 1 | 11 |
| PHR_2 | 1 | 4 | 1 | 6 | 0 | 12 |
| PHR_3 | 0 | 3 | 5 | 1 | 2 | 11 |
| PHR_4 | 0 | 2 | 7 | 18 | 9 | 36 |
| all | 2 | 12 | 17 | 27 | 12 | 70 |

- **Rating 5: 12 objects.** Identical, object by object, to the archived
  `pleiades-rating5-objects.csv` in position (to the 6th decimal) and area.
- **Rating 4: 27 objects**, 1,214 m2 in total, median 42 m2. PHR_2 contributes six rating-4 objects and
  no rating-5 object, so carrying rating 4 adds a scene the rating-5 analysis never used.
- **Discrepancy, recorded and not resolved:** CSIRO's 2017 press release and later press coverage
  report "28 possibly man-made". GA's own tables give 27. The table is the primary source and is
  used; the difference is noted wherever the count is quoted.

## Corrections and anomalies

1. **PHR_2 object 12: latitude and longitude transposed** in Table 2 (reported 91.29775, -35.275048).
   Swapped to -35.275048, 91.29775. The original values are kept in `lat_reported`, `lon_reported`.
   Brief section 5 rules this a typo; it is rating 4.
2. **PHR_2 object 11: area inconsistent with pixel count.** 199 pixels and 112 m2 gives 0.563 m2 per pixel
   against a median of 0.252 over the other 69 (about 0.5 m pixels). Area is kept as reported and
   flagged, not corrected: which of the two numbers is wrong cannot be told from the table. It is
   rating 2 and out of scope for H either way.
3. Two PHR_2 objects (11 and 12) are marked as also detected by the French Ministry of Defence.

---

# COSMO-SkyMed contacts and acquisition times (added 9 Oct 2026)

`engine/hypotheses/pleiades/data/cosmo-contacts.csv`: the four contacts exactly as ruled in `coordination/PLEIADES.md` (9 Oct). The
identifiers follow the source slide's coordinate order, not Iannello's article (whose first two are
reversed). Decimal values are checked against the degrees-minutes-seconds originals to 1e-7 deg.
The slide is headed "French Satellite Images sighted (23 March 2014)" and does not name the satellite;
Iannello (July 2021, private source) attributes **F1-F3** to COSMO-SkyMed on **21 March 2014**. Label:
"Possible COSMO-SkyMed contacts". **F1-F3 is the reference set; F1-F4 the extension.**
**Footprint and target sizes are missing and are carried as missing.**

`engine/hypotheses/pleiades/data/acquisition-times.csv`: from the satellites' orbits, not from a solar rule (architecture, 9 Oct):
- Pleiades-1A, descending node 10:30 LMST (eoPortal; WMO OSCAR): 04:24 UTC at PHR_4, 04:28 UTC at
  PHR_1 and PHR_3, 23 March, +/-25 min. **PHR_2 is assumed 04:24 (the east pair, with PHR_4)**; the
  ruling names no time for it. Moving a target 25 min shifts a track by at most 0.0011 deg (0.1 km),
  so the Pleiades times enter without quadrature.
- COSMO-SkyMed, dawn-dusk, ascending node 06:00 LT (eoPortal; ESA): alternative `cosmo-pass` =
  `dusk-21Mar` (11:52-12:00 UTC, mid 11:56) or `dawn-20Mar` (23:52 UTC 20 Mar - 00:00 UTC 21 Mar, mid
  23:56), equal prior, +/-25 min each (3-node quadrature, weights 1/4, 1/2, 1/4; the -25 to +25 min
  shift moves a track up to 0.016 deg, 1.5 km). Intervals to Pleiades 40.5 h and 52.5 h.
  `cosmo-date` (21 versus 23 March) is a separate alternative and is not merged with `cosmo-pass`.

# Flaperon identity check (9 Oct): closed for Pleiades objects

Condition 3 (size first) fails, so the check ends there. The archived morphology screen's flaperon
cut-out (a "DGA-dimensioned proxy", 2.59 m2, 1.68 x 2.32 m, about 10 pixels at 0.5 m) is seven to
nine times smaller than GA's smallest reported object at any rating (18 m2, rating 4; smallest
rating-5 23 m2). No imaged object is flaperon-sized. Caveats: 2.59 m2 is the archive's proxy, not a
sourced dimension (cite BEA/DGA when quoted); GA areas are pixel counts of the anomaly and may
include wake or foam, so the ratio is an order of magnitude. Not run on F1-F4: their sizes are unknown.

# Transport tables (gitignored; regenerate, do not commit)

`engine/runs/pleiades/`, written by `export.rs` through `mh370-ocean` (`ocean-model` =
`glorys12v1+era5-wind10`; GLORYS12V1 surface uo/vo + c_wind x ERA5 u10/v10; a_stokes 0; leeway angle
0; diffusion and ocean error OFF; RK2, 1 h step):
- `cosmo-tracks.csv` sha256 `cced4a95d796843d130543ef323258f992f21eff14de3b91146621fd2b470417`
- `release-grid.f32` sha256 `af04a2d7d0919b1ad44aa4b4a9fe417d5cd667e6527994b68d1f74e0e484c334`
  (0.1 deg, 87-97 E x 41-31 S, 21 windages, 4 output times; 0 non-afloat snapshots)

# Generated results in this directory

Moved here on 9 Oct 2026 from `engine/hypotheses/pleiades/results/` to comply with `engine/AGENTS.md`
(three markdown files only under `engine/`; generated output never committed there). `d5-real-*.csv`
were regenerated from `data/targets-3km.csv` (6-decimal positions and weights); they differ from the
pre-move run by at most 2e-5 relative. The injection and floor-scan summaries were produced before the
move, from the unrounded cluster means (differences under 1e-6 deg).
