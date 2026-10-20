# Seabed field extent per wreckage draw (reference-289, held out)

Ocean settling, 10 Oct 2026 (overnight), for searched areas' size-response hook (`coordination/OCEAN_SETTLING.md`, ~23:30 UTC).
Searched areas reports that g_k saturates for any aircraft-sized piece, so what matters for it is the field's **extent** against the
coverage-gap scale, and burial. This note gives the extent.

**Source.** Set A of `results/settling-wreckage-field-289-priorities/`:
- 200,000 impacts resampled from `none__other` (held out), end of flight `eof-289-full-s1..4`, prior track 289.7°, source `runs/snap289-m0011`;
- each impact settled once on the real ocean (`settling::tests::wreckage_field`, `hypothesis/settling` 9823b4e);
- 199,964 draws have settled pieces; 36 lie outside the ocean window.

PROVISIONAL: breakup table, dive class (b), Boeing glide, uncorrected fuel. Samples: `/Users/pete/Downloads/mh370-exchange/settling/reference-289-wreckage-field/` (README there).

**Statistic.** Within each draw, the distance of every settled element from the draw's mass-weighted centroid:
- R50 and R90: the radii enclosing 50 % and 90 % of settled mass;
- structural R90: the same for engines, gear, wing box and fuselage sections only;
- R_max: the farthest settled piece of any class.

Each column gives p10 / p50 / p90 over draws, in km.

| family | draws | R50, all mass | R90, all mass | R90, structural | R_max, any piece |
|---|---|---|---|---|---|
| intact | 45,131 | 0.87 / 1.81 / 3.39 | 1.71 / 3.71 / 7.61 | 1.62 / 3.59 / 7.46 | 4.48 / 13.63 / 30.68 |
| broken | 30,501 | 0.27 / 0.73 / 1.71 | 0.77 / 1.64 / 4.08 | 0.54 / 1.06 / 2.05 | 3.77 / 13.80 / 31.09 |
| fragmented | 124,332 | 0.27 / 0.71 / 1.68 | 0.71 / 1.62 / 4.38 | 0.40 / 0.86 / 1.86 | 3.62 / 12.95 / 29.25 |
| all | 199,964 | 0.30 / 0.89 / 2.28 | 0.79 / 1.95 / 5.56 | 0.45 / 1.12 / 3.96 | 3.84 / 13.22 / 29.86 |

**Reading it.**
1. A broken or fragmented field is about **1 km** in radius for its structure (median structural R90 0.86-1.06 km). An intact
   field is about **3.6 km**, because intact wing-box and fuselage sections float for hours before sinking.
2. Every family has a sparse floated halo, out to a median of about **13 km** (p90 about 30 km). It is made of cabin contents and flat panels. Light pieces in the halo are
   detectable in principle, so a field is rarely confined to one coverage gap. That holds only if detection of a single light piece counts.
3. So the field extent sits on the coverage-gap scale searched areas named, from hundreds of metres to kilometres. The coarse-against-fine
   sensitivity is real for settling's output. A point target is a poor stand-in for an intact draw.
4. **Not provided:** height proud of the seabed and plan length per piece. Settling has a piece area but no height. Searched areas reports
   that neither moves g_k for aircraft-sized pieces, so I have not invented a height table.
5. **Burial and terrain shadow** are not in settling: there is no post-contact model (methods draft §8). They remain searched areas' ρ.
6. Extent here is that of settling's representative elements: 30-65 per draw, each standing for many pieces at one point. The spread
   of real pieces within a class at a point is not modelled, so R values are lower bounds at the 100-m scale.

**Method note.** The draws are equally weighted outcomes. Searched areas averages non-detection over them, as stated in its entry.
