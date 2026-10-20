# Scientific interpretation boundaries

These boundaries are part of the v0.1 result, not optional caveats.

## What the release estimates

The release calculates posterior locations under declared flight-dynamics,
SATCOM, noise, lateral-control, fuel, and terminal-behaviour assumptions. It
reports numerical-seed stability and model-family sensitivity. It also
provides reproducible report artifacts and machine-readable particle outputs.

## What the release does not establish

- It does not observe the crash location.
- It does not provide calibrated posterior probabilities over incompatible
  structural model families.
- It does not justify pooling those families as if their spread were sampling
  error.
- It does not admit the present ocean-drift or hydroacoustic products as
  likelihood terms.
- It does not resolve the Pléiades imagery comparison at sufficient numerical
  resolution to update the estimator.
- It does not turn searched areas into a calibrated negative-search
  likelihood because exact swaths, holidays, and probability of detection are
  incomplete.
- It does not convert the MH371 known-flight control into evidence about
  MH370.

## Arcs

SATCOM arcs shown in the reports are calculated equal-BTO geometry under the
stated satellite, aircraft-altitude, and timing assumptions. The corrected
R600 seventh-arc report is a typed conditional continuation from the 00:11
posterior. Arc lines are not direct observations of the aircraft position.

## Davey comparison

The Davey material is an independently recreated comparison to a published
Bayesian-search result. The digitized Figure 10.3 latitude density is a paper
result, not a measured input. Agreement or disagreement with it must not be
used as self-validation of either implementation.

## Searched areas

The evidence atlas separates official geometries, reported totals that lack
publishable geometry, approximate Ocean Infinity outlines, and vessel-track
context. The baseline planning sensitivity ranks twelve 625 square-kilometre
tiles and contains 38.51% of its input KDE mass. It is a non-operational
planning sensitivity only. It does not say the remaining probability is
excluded by earlier searches, and it is not a recommendation to conduct a
search without independent operational review.

## End of flight

The primary impact family and every sensitivity family are conditional on a
named systems/fuel/control/aerodynamic scenario. The primary proxy's reported
mean, 38.1596 degrees south and 89.4088 degrees east, must remain attached to
that family label. Better B777-specific data could change the family and the
result.
