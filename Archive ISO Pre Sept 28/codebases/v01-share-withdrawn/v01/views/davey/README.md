# Davey et al. Bayesian search reconstruction

Paper: *Bayesian Methods in the Search for MH370* (Davey et al., 2016).
The bundled PDF SHA-256 is
`37554ca5f0c0ef14fddb825748d9f9dc9059a26563f783a3e4dfafcd0ced91b2`.

The located-passage audit of fuel, final SATCOM treatment, and the descent
kernel is in `citation-ledger.md`.

## Recreated claim

The Python implementation reconstructs the published-parameter flight model
from frozen SATCOM observations, ephemeris, and declared substitutes. A scalar
reference implementation supplies the hash-pinned forward-model fixture used
by the canonical Rust control.

Example historical run:

```bash
python code/run_filter.py --particles 10000 --seed 370023 \
  --case bto_bfo --tag local-check
```

## Result

The central latitude is similar to the digitized published curve, but the
predeclared full-distribution comparison fails. Across the three retained
runs, pairwise density overlap falls as low as 0.331 and median latitude differs
by as much as 0.835 degrees. The southern tail is seed-sensitive.

Not integrated: this stochastic reconstruction is not the canonical estimator.
The product uses adaptive likelihood tempering over a smaller, explicit
one-turn model and checks cross-seed geography and log evidence directly.

## Canonical comparison

`code/compare_canonical_latitude.py` generates a two-panel comparison from the
canonical run artifacts. Davey et al. publish their aircraft-position PDF at
00:19 UTC (Figures 10.2 and 10.3), but not a separate 00:11 position PDF.
Accordingly, the 00:11 panel shows only the canonical marginal and states that
the Davey comparison is unavailable; the 00:19 panel overlays the canonical
latitude marginal with the digitized bottom panel of Figure 10.3.

```bash
.venv/bin/python \
  .sources/davey-2016-bayesian-search/code/compare_canonical_latitude.py
```

The comparison is one-dimensional because the published Davey result available
for digitization is a latitude marginal, not a numerical two-dimensional
particle set. It is descriptive rather than a reproduction test: the canonical
00:19 continuation uses the 00:19:29 R600 BTO only, whereas Davey's full filter
used both 00:19 BTO messages.

The raw public inputs do not recover proprietary oscillator correction,
weather, magnetic-field, or maneuver-history inputs. See
`data/source-ambiguities.md`.

## Why the canonical 00:19 curve is narrower

The canonical 95% latitude width is 0.94°, versus 4.47° for the digitized Davey
curve: Davey is about 4.8 times wider, although the medians differ by only
0.059°. The canonical interval even contracts by about 7.5% from 00:11 to
00:19 because the eight-minute continuation adds no new manoeuvre, speed,
altitude, or process uncertainty and then conditions on one BTO.

This is a model-scope difference, not evidence that the aircraft position is
known five times more precisely. Davey considered five autopilot modes, a
possible later mode switch, and stochastic turn, speed, and altitude changes.
Because the 00:19 BFO was excluded, the final-interval manoeuvre count was not
constrained; Davey also used both mutually inconsistent final BTO values. See
book pages 60, 90, and 94 (PDF pages 73, 102, and 106) in `paper/paper.pdf`.
The canonical result must therefore be labelled a one-turn,
frozen-continuation conditional posterior until richer trajectory families are
implemented and compared explicitly.

## Prior identity and final-radar boundary

Davey's numerical trajectory prior starts at 18:01:49 UTC, at the penultimate
radar estimate, with 0.5 NM position SD and 1 degree direction SD. The isolated
18:22:12 military point is described but not used quantitatively in that prior.
Accordingly, configurations labelled Davey-style use 18:01:49 rather than
18:11. The separate final-radar/N571 configurations are sensitivity controls,
not Davey recreations: they use the published last-radar locus and an explicitly
reconstructed covariance because the underlying numerical radar series is not
publicly available here.
