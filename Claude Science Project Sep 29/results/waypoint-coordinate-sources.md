# Sourcing coordinates for the waypoint-constrained stratum

The waypoint stratum needs (a) coordinates for the named fixes, (b) the vertices
of the sampling polygon, and (c) the Kuala Lumpur / Jakarta FIR boundary segment
the polygon follows. This records what is available, what is not, and to what
standard each item can be cited.

## What is already citable from material in this repository

Ashton, Bruce, Colledge and Dickinson, "The Search for MH370", *Journal of
Navigation* 68(1), 2015, doi:10.1017/S037346331400068X — held as
`ISO Sept 28 Status/inputs/end-of-flight/report-text/ashton_search_for_mh370.txt`:

| Fix | Published coordinate | Located passage |
|---|---|---|
| MEKAR | N06 30, E096 30 | "the aircraft was at 18:22 UTC when it passed close to the MEKAR waypoint at N06 30, E096 30" |
| IGOGU | N07 31, E094 25 | "along airway N571 towards the IGOGU waypoint at N07 31, E094 25 at a ground speed of 480 knots" |
| ISBIX | N00 22, E093 40·5 | "turned south towards the ISBIX waypoint (N00 22, E093 40·5)" |

This is the best available provenance for these three: a peer-reviewed paper by
the Inmarsat team, published in the journal this work is aimed at, describing the
March 2014 airspace. It is preferable to a current navigation database even where
one is available, because it is contemporaneous.

The Malaysian Safety Investigation Report (`inputs/papers/aero/sir.pdf`, 495 pp)
names MEKAR, NILAM, VAMPI and IGARI repeatedly but publishes no fix coordinate
table. Its only coordinates are simulator re-enactment entry/exit points in
degrees-minutes-tenths form (e.g. "N07.05.7° E103.47.1°", p. 328) and an
additional waypoint at N05.15.6 E100.27.5. The ATSB flight path update text in
the same directory contains no coordinates for these fixes.

## AIP-sourced table supplied by the user

`MH370_waypoint_hypotheses_2014_boundary.csv` supplies ten fixes with per-row
provenance, now merged into `engine/data/waypoints.csv`. Its sourcing is stronger
than any of the three routes considered below: Malaysia DCA AIP Supplement
36/2008 and AIP AMDT 3/2011, India AIP archive effective 1 April 2012 ENR
1.9/4.3, and India NOTAM G0419/13 effective 22 August 2013 — all pre-dating March
2014 — with a `historical_status` column that records later NOTAM renamings at
unchanged coordinates (DOTEN → AMVUR in 2019, SADAP → DUMAR and ORARA → MANPU in
2018). That is the epoch problem raised below solved rather than caveated.

**It cross-checks against Ashton et al.** Computing the separation between the two
independent sources on the two fixes both carry:

| fix | AIP table | Ashton et al. (2015) | separation |
|---|---|---|---|
| IGOGU | 07°31′01″N 094°25′00″E | N07 31, E094 25 | **0.02 NM** |
| MEKAR | 06°30′14″N 096°29′28″E | N06 30, E096 30 | **0.58 NM** |

IGOGU is exact. The MEKAR difference is entirely Ashton's rounding to whole
minutes — 96°30′ against 96°29′28″ is 32″ of longitude, 0.53 NM at this latitude.
An AIP table and a peer-reviewed paper agreeing to the precision each states is
about as good as provenance gets here, and it raises confidence in the eight rows
Ashton does not cover.

**Two hypotheses, not one.** Six of the ten fixes — DOTEN, SADAP, ORARA, SUPLU,
NODAX and VVZ — are on airway N877 running north-west toward India, and the
table's `initial_true_bearing_from_NILAM_deg` and `within_296_to_316_screen`
columns show they were assembled for a bearing screen from NILAM, not for the
southern polygon. They must not be pooled into the polygon's sampling set. The
table's relevance to the polygon is MEKAR, NILAM, IGOGU and SAMAK; the other six
belong to the northern-route conditional and should be carried under their own
hypothesis with their own prior.

SAMAK is now sourced (07°58′42″N 094°25′00″E, India AIP archive effective 1 April
2012), which settles the point that it should be included north of IGOGU — it sits
27.7 NM due north of IGOGU on exactly the same meridian, 094°25′00″E, both on the
FIR boundary.

## Still needed to close the polygon

Twelve fixes and one boundary segment:

| fix | why it is needed |
|---|---|
| LAGOG | the phase-2 box's NW corner is defined as 10 NM NW of LAGOG on N571 |
| IVRAR | phase-2 box SE corner, and a polygon vertex |
| RUNUT | polygon vertex |
| YPCC | polygon vertex (Cocos aerodrome reference point) |
| PIPOV | named as the southern limit of useful waypoints, about 4°S |
| ANOKO, NOPEK, BEDAX, BULVA, MUTMI, POSOD, BEBIM | the archived shortlist's interior sampling set |

Plus the Kuala Lumpur / Jakarta FIR boundary between 6N 94E and 6N 92E, which the
polygon follows and which no source in hand describes. Without it the polygon's
southern-west edge cannot be closed, so the interior test "is this fix inside the
sampling region" cannot be evaluated for fixes near that edge.

## What is not in the repository

No coordinate is held for NILAM, VAMPI, SAMAK, LAGOG, IVRAR, RUNUT, PIPOV,
BULVA, ANOKO, NOPEK, BEDAX, MUTMI, POSOD or BEBIM. The archived waypoint work
(`Archive ISO Pre Sept 28/.../igogu_fir_followup/output/waypoint_exact_summary.json`)
carries only a name shortlist — IGOGU, ANOKO, NOPEK, BEDAX, BULVA, ISBIX, MUTMI,
RUNUT, POSOD, BEBIM — with importance-measure sums, not positions. There is no
`earth_fix.dat`-style dataset anywhere in the repository, and no FIR boundary
geometry.

The archived Antarctic destination bundle
(`.sources/antarctic-waypoint-navigation/`) is worth reading before this stratum
is built, because it set the source standard the project has been holding to. It
sources its two destination points to the Australian Antarctic Data Centre
Gazetteer (ID 137992, GPS epoch 2009/10) and a COMNAP facilities table in the
ATCM XXXI final report, records the located passage for every claim, and then
marks two claims explicitly unsupported:

> Either candidate was available as a named fix in 9M-MRO's March 2014
> navigation database. — No admitted primary source. NOT FOUND; do not claim.

That constraint applies to the whole stratum. We can establish where a published
fix is; we cannot establish from open sources which fixes were loaded in
9M-MRO's navigation database in March 2014. The stratum must therefore be
declared as conditional on a stated coordinate table, not presented as the set of
fixes the aircraft could actually have been commanded to.

## Authoritative source for the remainder

Fix coordinates are published by each state in its Aeronautical Information
Publication, ENR 4.4, "Name-code designators for significant points", and airway
definitions in ENR 3; FIR boundaries are in ENR 2.1. For this polygon that means
Malaysia (Kuala Lumpur FIR — NILAM, VAMPI, SAMAK, LAGOG), Indonesia (Jakarta FIR
— IVRAR, RUNUT, PIPOV and the FIR boundary segment from 6N 94E to 6N 92E), India
(Chennai FIR, for fixes near the northern boundary) and Australia (for YPCC
Cocos). ICAO's ICARD five-letter-name-code database is the registry behind these
designators, but its full query interface requires an ICAO Portal account; the
public view is limited.

Two problems with using current AIP data, both of which need stating in the paper
rather than solving:

1. **Epoch.** AIP ENR 4.4 is a current-cycle document. A fix can be renamed,
   moved or withdrawn between AIRAC cycles, and we would be reading a 2026 cycle
   to populate a March 2014 trajectory model. For the three fixes Ashton
   publishes we have a contemporaneous check; for the rest we would not.
2. **Polygon vertices are ours, not published.** The polygon corners you
   specified — 8N 94E, due south along 94E to 6N, the FIR boundary to 6N 92E,
   then RUNUT, YPCC, IVRAR, NILAM, 8N 92E — are a declared sampling region. Only
   the FIR segment and the three named vertices need sourcing; the rest are
   modelling choices and should be labelled as such.

## Recommended handling

Build `data/waypoints.csv` with one row per fix carrying `name`, `lat_deg`,
`lon_deg`, `source`, `source_locator`, `effective_date` and a `provenance` field
taking values `contemporaneous` (Ashton 2015), `current_aip` or `declared`
(polygon vertices). The filter reads the table; the report prints it with its
provenance column; the paper cites it as a declared conditional input. Any fix
whose coordinate cannot be sourced is omitted rather than estimated, and the
omission is recorded — the stratum's prior is then explicitly over the sourced
set, which is a defensible statement, where a silently interpolated coordinate is
not.

## Outstanding decision

Three routes to the remaining coordinates, in descending order of citation
strength:

1. Locate a contemporaneous published source — a 2014-era chart, an AIP
   supplement, or another peer-reviewed MH370 paper that prints coordinates.
   Strongest, least likely to be complete.
2. Read the current AIP ENR 4.4 for Malaysia and Indonesia and label the rows
   `current_aip` with the cycle date. Requires network access to the relevant
   AIP portals, some of which need registration.
3. Read coordinates off a current chart product (SkyVector or equivalent) and
   label them `chart_read` with the product and date. Weakest provenance, but
   honest if labelled, and sufficient for a sensitivity stratum whose purpose is
   to test whether waypoint-constrained trajectories are favoured at all.

Route 3 is adequate for the first pass, because the stratum's finding will be a
comparison against a null rather than a claim about a specific fix. If the
comparison favours waypoint navigation, route 1 or 2 becomes necessary before
publication.
