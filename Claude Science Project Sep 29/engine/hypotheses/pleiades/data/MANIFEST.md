# Data manifest: GA Record 2017/13 object table

`ga-rec2017-13-objects.csv` holds all 70 objects from Tables 1-4 of

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
