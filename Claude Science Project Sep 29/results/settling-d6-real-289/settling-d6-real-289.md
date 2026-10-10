# Settling deliverable 6 on the real ocean, at reference-289 impact points

The architecture entry of ~14:45 UTC, 9 Oct, asked for this. The 295.66° page (`results/settling-d6-real/`)
stays as the comparison. Run provenance, weighting and the PROVISIONAL-OVERNIGHT caveat are as in
`results/settling-d6-289/settling-d6-289.md` (end of flight `eof-289-full-s1..s4`; prior track 289.7;
`source_run` `runs/snap289-m0011`).

**Points**, from the none × other posterior: the highest-mass 0.25° cell within 0.125° of the p10 and p90
latitude quantiles, the same for p50, and the densest cell overall.

| point | lat, lon | median contact depth | GLORYS floor above seabed (median) |
|---|---|---|---|
| p10 latitude | 39.125 S, 89.125 E | 3,746 m | 0 m |
| p50 latitude | 36.875 S, 89.125 E | 4,346 m | 262 m |
| densest cell | 35.125 S, 91.375 E | 4,034 m | 0 m |
| p90 latitude | 32.875 S, 94.125 E | 4,511 m | 0 m |

Code: `settling::tests::report_real` at `d1e32ab`, with `SETTLING_REPORT_POINTS` set to these four
points. GLORYS12V1 column and surface current and ERA5 wind are read through `load_window`; the seabed
is AusSeabed, then GEBCO; density is TEOS-10 on GLORYS T and S. 1,024 draws per point and family.

**p90 resting offset at the p50 point:**

| class | intact | broken | fragmented |
|---|---|---|---|
| engine | 403 m | 190 m | 184 m |
| landing gear | 403 m | 190 m | 190 m |
| wing box | 5.6 km | 715 m | 395 m |
| fuselage section | 5.6 km | 818 m | 444 m |
| flat panel | 876 m | 883 m | 953 m |
| cabin contents | 9.3 km | 9.4 km | 9.3 km |

Over the four points: dense classes 0.18-0.48 km; floated pieces 0.4-13 km.

**Variants** (median over points of variant ÷ baseline at matched draws 0-511):

| variant | effect |
|---|---|
| **provisional column and uniform surface fields** | now **over**-estimates: dense classes x1.07-1.10, floated up to x1.27 (x1.45 at one point) |
| GlobCurrent surface current | floated classes x1.00-1.23 (x1.37 at one point); dense unchanged |
| no ocean error | x0.87-1.00 |
| density from WOA23, GEBCO only, below-floor rule | under 1.5 % |

On the 295.66° points the provisional column had **under**-estimated (x0.88-0.96). Its 0.13 m/s uniform
surface current and two-layer column are neither systematically high nor low: they sit inside the
spread of the real ocean between these two sets of points.

- So the provisional page is within about ±25 % of the real ocean, with a location-dependent sign, and
  the real-ocean page is the one to quote.
- **Ocean-model choice** (GLORYS12 against GlobCurrent) is the largest real-ocean uncertainty for
  floated classes, at up to about 25 %.

**Monte Carlo:** the 512-draw halves differ by a median of 2.7 % in p90, and by up to 11 %.

**PROVISIONAL:** the breakup table, and end of flight's two overnight choices in the impacts.
