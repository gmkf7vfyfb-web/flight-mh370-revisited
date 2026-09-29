# Antarctic waypoint-navigation sources

This bundle records the source boundary for two conditional point-to-point
navigation controls: Davis Plateau Ski Landing Area and Fossil Bluff. Their
identities and coordinates were frozen before the reported production run, but
the candidate set was selected post hoc after inspecting seventh-arc/186.2
degree geometry. It was not selected from a preregistered candidate universe.
This bundle contains no executable implementation and is not a product
dependency. The runner owns the hashed candidate configuration; this record
only establishes what the source coordinates mean and what they do not mean.

The retrospective candidate-selection history, including the legacy CTT
reference, simulator-catalogue boundary, coordinate substitutions, and R600
post-selection limitation, is recorded in
[`SELECTION-LEDGER.md`](SELECTION-LEDGER.md).

Retrieved and checked 31 August 2026. The source passages below were located in
the complete official documents or official institutional pages, not in search
snippets.

## Candidate reference points

| Candidate | Published latitude | Published longitude | Point meaning | Primary source |
| --- | ---: | ---: | --- | --- |
| Davis Plateau Ski Landing Area | -68.47060 | 78.84061 | Published centre of the landing area; the source says the seasonal location may move by a few hundred metres. | Australian Antarctic Data Centre Gazetteer ID 137992, GPS source epoch 2009/10 |
| Fossil Bluff | -71.3293333333 | -68.2670000000 | Published COMNAP facility/airfield reference point; not identified as a runway threshold. Decimal degrees are converted exactly from 71 degrees 19.76 minutes S, 68 degrees 16.02 minutes W. | ATCM XXXI Final Report, COMNAP facilities table, PDF p. 527 (printed p. 529) |

These points define deliberately narrow geometric hypotheses. They are not
evidence that either point was selected by the aircraft, that either name or
coordinate was present in 9M-MRO's March 2014 navigation database, or that
either facility could accept a Boeing 777. The source descriptions concern ski
operations by much smaller aircraft. Neither point source explicitly states a
horizontal datum; the control therefore declares that it treats the published
geographic coordinates as WGS84 for geodesic propagation.

## Citation ledger

| Claim supported | Source | Locator | Located passage (short excerpt) | Status |
| --- | --- | --- | --- | --- |
| A waypoint is a latitude/longitude position, and a direct-to leg is a track from the aircraft's initial area to that waypoint. | Federal Aviation Administration, *Aeronautical Information Manual*, effective 3 April 2014 | AIM 1-2-2, PDF pp. 71-72 | "predetermined geographical position ... defined in terms of latitude/longitude coordinates"; "track from an initial area direct to the next waypoint" | FOUND |
| The FAA's generic route-segment guidance supports geodesic, rather than constant-true-track, propagation between fixes. The implementation declares its actual calculation as a WGS84 geodesic. | Federal Aviation Administration, *Aeronautical Information Manual*, effective 3 April 2014 | Preflight, AIM 5-1-15, PDF p. 279 | "routes/route segments on Great Circle tracks" | FOUND |
| The Davis point is the centre of the landing area, sourced by handheld GPS in 2009/10, and the seasonal site may move by a few hundred metres. | Australian Antarctic Data Centre, "Davis Plateau Ski Landing Area," Gazetteer ID 137992 | Narrative; Location; Source; Comments | "location varies each season ... by up to a few hundred meters"; "coordinates are for the centre of the landing area" | FOUND |
| Whoop Whoop was an operating skiway immediately before the MH370 flight year. | Australian Antarctic Program, "This week at Davis: 7 June 2013" | "To Whoop Whoop we go" | "air operations ceased at the beginning of February" | FOUND |
| The older Davis coordinate is not interchangeable with the later Gazetteer point; AAD expected the site to vary with conditions. | Australian Antarctic Division, *IEE - Air Transport System 2007* | Section 3.7, PDF pp. 25-26 | "necessary to vary the site ... according to prevailing conditions and operational considerations" | FOUND |
| COMNAP published Fossil Bluff as a seasonal, ski-equipped, 1,200 m airfield camp at the coordinate used in the control. | COMNAP table in *Final Report of the Thirty-first Antarctic Treaty Consultative Meeting, Volume II* | Details of Antarctic Facilities, PDF p. 527 (printed p. 529), Fossil Bluff row | "71 degrees 19.76 minutes S ... 1200m ... ski ... Airfield Camp ... Seasonal" | FOUND |
| Fossil Bluff was an aircraft-refuelling facility with an unprepared snow runway in the 2014 BAS publication. | British Antarctic Survey, *Research stations and refuges of the British Antarctic Survey* (2014) | Field Stations - Fossil Bluff, PDF p. 14 | "forward facility for refuelling aircraft"; "1,200m unprepared snow runway" | FOUND |
| Either candidate was available as a named fix in 9M-MRO's March 2014 navigation database. | No admitted primary source | None | No located passage | NOT FOUND; do not claim |
| Either published coordinate is an exact historical runway threshold or proves suitability for a Boeing 777. | No admitted primary source | None | No located passage | NOT FOUND; do not claim |
| The generic FAA direct-to construction reproduces the exact Boeing 777 FMS/LNAV implementation fitted to 9M-MRO. | No admitted aircraft manual or certified implementation source | None | No located passage | NOT FOUND; report as a generic point-to-point conditional model |
| Either source explicitly identifies its horizontal datum as WGS84. | No located passage in either admitted coordinate source | None | No located passage | NOT FOUND; declare the WGS84 treatment as a model assumption |

## Coordinate-version decision

The 2007 AAD environmental assessment gives an older Davis Plateau site at
68 degrees 33 minutes 41 seconds S, 78 degrees 47 minutes 29 seconds E, and
explicitly says skiway sites may change with operating conditions. The AADC
Gazetteer later records the landing-area centre at 68 degrees 28 minutes 14.2
seconds S, 78 degrees 50 minutes 26.2 seconds E from a 2009/10 handheld-GPS
source and says the seasonal position varies by no more than a few hundred
metres. The conditional control therefore uses the later official centre
coordinate, not the 2007 site and not a simulator-airport coordinate.

The Fossil Bluff control uses the official COMNAP facility row. BAS corroborates
the existence and operational role of the skiway, but its public description
only places the runway approximately one kilometre south of the station. The
COMNAP coordinate must therefore be described as a facility/airfield reference
point, not a surveyed runway threshold.

Neither coordinate source names a horizontal datum. The runner uses WGS84
geodesy, so the configuration must identify its treatment of the published
latitude/longitude values as WGS84 as a model assumption rather than source
metadata.

## Source inventory

The documents are not copied into the repository. These are exact retrieval
locations and SHA-256 hashes of the bytes inspected on 31 August 2026.

| Source | Retrieval URL | Inspected-byte SHA-256 |
| --- | --- | --- |
| FAA, *Aeronautical Information Manual*, effective 3 April 2014 | https://www.faa.gov/air_traffic/publications/media/aim_basic_4-03-14.pdf | `22c0d1396fd0c9150a908dd7ef9d24e589c99d0e418d6c9797207a537827f4ce` |
| AADC Gazetteer ID 137992, Davis Plateau Ski Landing Area | https://data.aad.gov.au/aadc/gaz/display_name.cfm?gaz_id=137992 | `04217d542e420925d353bbeb85159f4befc071345ee902578bcde65b0e5ddf28` (retrieved HTML; mutable institutional page) |
| Australian Antarctic Program, "This week at Davis: 7 June 2013" | https://www.antarctica.gov.au/news/stations/davis/2013/this-week-at-davis-7-june-2013/ | `f08255317f49773d0a493e6ada036c914368eb7df58189bf86b99ad5f50999c9` (retrieved HTML; mutable institutional page) |
| AAD, *IEE - Air Transport System 2007* | https://documents.ats.aq/EIES/EIA/01155enAir%20Transport%20IEE%20Variation%20Final%20Sep%202007.pdf | `31ee9f0eec66fdce275affc26ae7d4a44fd342585fca3a14015083b657ee4c98` |
| *Final Report of the Thirty-first Antarctic Treaty Consultative Meeting, Volume II* | https://documents.ats.aq/ATCM31/fr/ATCM31_fr001_e.pdf | `e417f1d2f477f65cca123530b6c06f431fd928541b65ad32076b533fe947c750` |
| BAS, *Research stations and refuges of the British Antarctic Survey* (2014) | https://www.bas.ac.uk/wp-content/uploads/2015/05/public_information_leaflet_research_stations_2014.pdf | `6ff8bfa7123d4ace0d745f442cc891c5a3f2ff4413ad6cb9a79fe39d64a66d34` |

The AADC page is mutable and a fresh retrieval no longer reproduces the earlier
raw hash. A durable, field-level record of the current response, its safe
headers, normalization method, and both fresh-raw and normalized hashes is
linked in
[`data/aadc-gazetteer-137992.provenance.md`](data/aadc-gazetteer-137992.provenance.md).
It is explicitly a new retrieval record, not a reconstruction of the earlier
`04217d...` response.

## Reporting boundary

The retrospective candidate-selection history, including the simulator-
catalogue limitation, coordinate substitutions and R600 non-blinding, is
recorded in [`SELECTION-LEDGER.md`](SELECTION-LEDGER.md).

Call the runs **Davis Plateau reference-point** and **Fossil Bluff
reference-point** conditional controls. Do not call them airport-selection
posteriors. Compare each with the constant-true-track family as a separate
structural hypothesis; do not pool their particles or interpret a geometric fit
as evidence of intent. Call the implemented guidance a **WGS84-geodesic
direct-to conditional** and a generic approximation, not certified Boeing 777
LNAV. The candidate-selection universe, selection tolerance and navigation-
database availability are undocumented, and no look-elsewhere correction is
available. The figure and table must be generated solely from run artifacts and
must state that candidate selection was prompted by geometry.
