# Exploratory waypoint-selection ledger

This ledger records how the Davis Plateau and Fossil Bluff reference-point
controls were chosen. It is a retrospective reconstruction from the publication
thread and surviving artifacts, not a prospective registration. The screen was
geometry-led, non-exhaustive, and conducted after the constant-true-track (CTT)
result was known. It must not be used to assign either candidate a prior
probability or to infer intent.

## Legacy reference that prompted the screen

The user asked whether continuing the estimated CTT of about 186.2 degrees from
the second arc could intersect a named waypoint or airport to the south. The
screen used the then-current, legacy 19:41:02 UTC (`m1941`) CTT reconstruction:

| Quantity | Legacy reference |
| --- | ---: |
| Mean position | 0.612051 degrees S, 93.646547 degrees E |
| Mean CTT | 186.243261 degrees T |
| Central 90% CTT interval | 185.0883--187.8510 degrees T |
| Central 90% latitude marginal | 1.20587--0.18416 degrees S |
| Central 90% longitude marginal | 93.56368--93.73162 degrees E |

The equal-seed 90,000-particle temporary sample was reported with SHA-256
`48f93e205240dc1d7cb06cdab235d8782ecec24fa4d2c93c5bd10a04c05f0367`.
The temporary CSV and the temporary replay source were subsequently removed.
The reconstruction also predates the later absolute control-update-lattice
correction in the canonical dynamics. Consequently the exploratory screen
cannot now be rerun byte for byte from a durable input artifact; the numbers
above identify the historical selection reference, not a current production
posterior.

## Screens and sources actually consulted

Two different geometries were examined:

1. a literal constant-bearing/rhumb continuation of the CTT estimate; and
2. the initial and changing WGS84-geodesic course to a fixed point, as a generic
   direct-to/LNAV-like conditional model.

The surviving thread record identifies the following inputs. Items expressly
described below as thread recollections are selection-history evidence only;
they are not admitted source citations because their exact retrieved bytes and
located passages were not preserved in this bundle.

- The thread reports that the ATSB's 2015 MH370 search-area analysis,
  pp. 41--43, was consulted when distinguishing B777 LNAV waypoint legs from
  true-track hold and considering pilot-entered latitude/longitude waypoints.
  The exact ATSB response bytes, hash, and located passage were not retained
  here, so this is an unreverified thread recollection. The admitted generic
  direct-to construction instead rests on the located FAA passages in
  [`README.md`](README.md).
- A local **X-Plane cycle-2012.08 simulator fix/airport catalogue** was searched
  for named fixes and airports. The screen reported no named en-route fix and
  no catalogue airport whose literal rhumb bearing fell inside the legacy 90%
  CTT interval. It also surfaced simulator identifiers AT07, AT10, and AT01.
  This was a simulator catalogue, **not** 9M-MRO's certified March 2014
  navigation database. The catalogue files, retrieval URL, byte hashes, query
  code, exact geographic bounds, and complete result set were not retained.
- The thread reports consultation of public institutional material for
  Antarctic candidates: AADC and Australian Antarctic Program/AAD material,
  an ATSB 2013 Davis occurrence, COMNAP/Antarctic Treaty facility tables, BAS
  material, PRIC material, and a contemporary Xinhua report concerning Kunlun.
  Only the sources with exact retrieval locations, hashes, and located
  passages in [`README.md`](README.md) are admitted support for the production
  coordinates or facility descriptions; the remainder are unverified thread
  recollections.
- The thread also reports checking public discussions by Godfrey, Iannello,
  and a later Davis-route author for prior art. Their retrieved bytes and
  located passages were not retained here. They are not admitted coordinate,
  navigation-database, or intent evidence.

No source inspected established that any candidate name or coordinate was
loaded in 9M-MRO's FMC, that a candidate could accept a Boeing 777, or that the
aircraft had the range, systems state, or crew intent required to fly there.

## Candidate set and ranking used at the time

The recorded screen considered, at minimum, Kunlun Station, the South Pole,
Davis Plateau skiway, Davis sea-ice landing area, Fossil Bluff skiway, Progress
old skiway, Zhongshan, Bharati, Taishan, Mirny, and Rothera. Published-online
comparators at South Pole, Pegasus, and Wilkins were also noted. This list must
not be represented as the complete universe searched because neither the
complete catalogue output nor a frozen inclusion rule survives.

Kunlun was the strongest literal-rhumb coincidence: its required fixed track
was reported as 186.68 degrees T, with a posterior median miss of about 18.7 NM.
It was rejected as the LNAV test because a geodesic direct-to leg began at only
about 182.76 degrees T and its first documented aircraft landing was in 2017.
The 2017 statement is itself an unverified recollection from the exploratory
thread's Xinhua check, not an admitted source claim in this bundle. The South
Pole began at 180 degrees T. No conventional or 777-suitable airport was found
on the literal 186.2-degree continuation.

The direct-to screen was reported as follows:

| Candidate | Initial course at m1941 | Course near R600 | Miss from legacy CTT R600 mean |
| --- | ---: | ---: | ---: |
| Davis Plateau skiway | 185.80 degrees T | 187.32 degrees T | 3.0 NM |
| Fossil Bluff skiway | 186.02 degrees T | 187.59 degrees T | 10.9 NM |
| Davis sea-ice landing area | 186.08 degrees T | 187.67 degrees T | 13.3 NM |
| Progress old skiway | 186.40 degrees T | 188.07 degrees T | 24.6 NM |

Davis was frozen because it had the smallest reported full-path geometric miss
and an initial course inside the legacy CTT interval. Fossil Bluff was frozen
as a second, geographically distinct, longstanding named facility with a close
initial course and the next-smallest reported miss among the two ultimately
selected controls. That choice was analyst judgement, not the result of a
predeclared statistical threshold. No formal tolerance, candidate-universe
prior, multiplicity correction, or tie-breaking rule was frozen. In particular,
the record does not explain through a prospective rule why the Davis sea-ice
point was not retained alongside or instead of Fossil Bluff.

## Coordinate substitutions before production

The exploratory screen used catalogue/publicly quoted candidate locations. A
later source audit found that Davis coordinates from different sites or seasons
had been mixed. Production therefore substituted the official AADC Gazetteer
ID 137992 landing-area centre, `-68.47060, 78.84061`, sourced by handheld GPS in
2009/10 and explicitly subject to seasonal movement. This is not a runway
threshold. It differs from both the older 2007 AAD site and the simulator
coordinate used during screening.

Production uses the COMNAP Fossil Bluff facility/airfield reference point,
`-71.3293333333, -68.2670000000`, converted from the published degrees and
minutes. It is also not a surveyed runway threshold. The exact Fossil Bluff
coordinate bytes used in the first exploratory calculation were not preserved,
so any numerical coordinate substitution cannot be reconstructed exactly.
The production coordinates and their passage-level provenance are recorded in
[`README.md`](README.md).

## Selection and R600 boundary

R600 was excluded from fitting the new fixed-waypoint families, but it was not
selection-blind. The exploratory ranking explicitly inspected each candidate's
course near the R600 travel distance and its miss from the already available
legacy CTT R600 mean. The later R600 likelihood is therefore a forward
predictive compatibility calculation for frozen fitted families, but it is not
an untouched prospective discriminator for the candidate-selection process.
It must not be described as independent validation, preregistered confirmation,
or evidence for waypoint-selection intent.

## Unrecoverable or unknown details

- The exact simulator-catalogue release bytes, filenames, hashes, licence, and
  complete searched fix/airport universe.
- The query implementation, geographic limits, numeric tolerances, ranking
  weights, rejected-row output, and exact time at which each criterion entered
  the screen.
- The deleted legacy m1941 particle CSV and replay source; only the reported
  summary and SHA-256 remain.
- A byte-for-byte reproduction of the exploratory bearings after later dynamics
  and coordinate corrections.
- The contents of 9M-MRO's March 2014 navigation database and whether any named
  or manually entered candidate was available or selected.
- Candidate-universe probabilities, intent probabilities, aircraft range/fuel
  feasibility, Boeing 777 landing suitability, and exact B777 FMS behaviour.

These unknowns do not prevent a conditional geometric sensitivity run. They do
prevent interpreting relative evidence, endpoint compatibility, or an R600
score as a probability that either target was selected.
