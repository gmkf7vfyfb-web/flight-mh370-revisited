# Conservative debris-event provenance

The archived inventory contains 42 reports, mostly transcribed from user
screenshots. They are not 42 independent confirmed MH370 recoveries. Repeated
site/date clusters and coordinate proxies must be collapsed or represented
explicitly before they are used as evidence.

Three rows have a `confirmed` identity classification:

| Inventory ID | Object | Discovery position | Normalized date | Provenance and date caveat |
|---|---|---:|---:|---|
| IMG-001 | Right flaperon structure | 20.916180°S, 55.649150°E | 2015-07-29 | User screenshot; point is reported Saint-André, Réunion. Screenshot gives only July 2015; day completed from official literature. |
| IMG-009 | Left outboard aft-flap section | 20.023383°S, 57.701386°E | 2016-05-10 | User screenshot; point is reported Îlot Bernache, Mauritius. Screenshot month conflicts with the date in Durgadoo et al. (2021) Table 1; normalized date follows that table. |
| IMG-023 | Right outboard-flap inboard section | 5.056071°S, 39.868086°E | 2016-06-23 | User screenshot; point is reported Kojani Island, Pemba, Tanzania. Screenshot says 20 June; normalized date follows Durgadoo et al. (2021) Table 1. |

Raw row source:
`analyses/D-0042-hierarchical-debris-drift/inputs/debris_inventory.csv`
in the read-only pre-refactor archive. The sequential archive directory is
recorded only as data provenance and is not imported by product code.

The demonstration configurations deliberately use only IMG-001. A flaperon,
an aft-flap section, and an outboard-flap section do not share one defensible
leeway distribution merely because their identities are confirmed. Adding
IMG-009 or IMG-023 requires an explicit object-motion family and discovery-
versus-beaching interval; treating all three as exchangeable would create
spurious precision.

