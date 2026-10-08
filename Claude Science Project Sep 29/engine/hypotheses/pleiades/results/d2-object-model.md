# Deliverable 2, first part: object clusters and their sensitivity (PROVISIONAL)

2026-10-08, Pléiades module. Script: `prepare/d2_object_model.py`. Inputs: `data/ga-rec2017-13-objects.csv`
(see `data/MANIFEST.md`). Outputs: `d2-cluster-sensitivity.csv`, `d2-clusters-3km.csv`.

Declared configuration: single linkage on great-circle distance; default threshold **3 km**; cluster
position = unweighted mean of members; `object-rating` arms rating 5 only, and rating 5 + rating 4 at
weight ρ4 ∈ {0, 0.25, 0.5, 1}. No shape or size enters as identity evidence.

## Rating 5 reproduces the brief

At 3 km the 12 rating-5 objects form the brief's **six clusters**, matching its table to 5e-5° in
position and exactly in area.

## The cluster count is a parameter, and it moves

| threshold (km) | 0.5 | 1 | 2 | 3 | 5 | 10–50 | ≥ 100 |
|---|---|---|---|---|---|---|---|
| rating 5 | 9 | 8 | 6 | 6 | 5 | 3 | 1 |
| rating 5 + 4 | 30 | 23 | 18 | 12 | 7 | 4 | 1 |

- Between 10 and 50 km the clusters are the scenes. **Rating 5 alone gives three, not four**: PHR_2 holds
  no rating-5 object. The ISO brief's four-location reading only appears when rating-4 objects are
  carried. It is a legitimate alternative threshold, but it is also implicitly a rating-4 choice.
- Carrying rating 4 **changes the rating-5 structure**, not just adds to it. At 3 km, rating-4 objects
  PHR_4:24 and :25 chain PHR_4 18/19 and 26/27 into a single 14-object cluster. This is single linkage
  doing what single linkage does, and it is why rating 4 is an `object-rating` alternative and is
  never folded silently into the default.
- Rating 5 + 4 at 3 km gives 12 clusters, of which seven contain no rating-5 object: three in PHR_4,
  one in PHR_3 and three in PHR_2. The PHR_2 three, about 35.3°S 91.3°E, are in a scene the rating-5
  analysis never used.

## Cluster weights: two declared forms, no ruling yet

For rating 5 at 3 km the two forms differ by up to 2.5×. 'Equal' gives every cluster 1/6. 'Count' gives
the five-object PHR_4 cluster 0.42 and each single-object cluster 0.08. 'Count' leans on multiplicity,
which is defensible — debris fields cluster — but it is a modelling choice, not data. Both are carried
until architecture rules.

## Two-epoch matching space (for deliverable 5)

Injective partial assignments of the 4 COSMO-SkyMed contacts, Σ_k C(4,k)·n!/(n−k)!:

| target set | n | assignments |
|---|---|---|
| rating-5 clusters at 3 km | 6 | 1,045 |
| rating-5 objects | 12 | 18,001 |
| rating 5 + 4 clusters at 3 km | 12 | 18,001 |
| rating 5 + 4 objects | 39 | 2,202,409 |

All are exhaustively enumerable; the largest is about 2.2 M. The brief's two counts are confirmed.

## Not done here

- Background density `q_c`. GA gives each scene as about 25 km × 20 km, about 100 km apart, all
  significantly cloud and glint affected. The effective (cloud-free) footprint is what `q_c` needs, and
  footprints are not assembled (brief §13).
- COSMO-SkyMed contact positions. These are not in this project's data yet.
