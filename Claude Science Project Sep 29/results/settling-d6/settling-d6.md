# Settling deliverable 6 - resting offsets by class and family at representative 7th-arc depths

**PROVISIONAL. Not evidence.** Analytic two-layer column and uniform surface fields (no gridded
product column exists yet), planar seabed at controlled depths, 256 draws per cell. Code:
`hypotheses/settling` at `7e4f29a` (branch `hypothesis/settling`), generator
`settling::tests::report` with `SETTLING_REPORT_DEPTHS=3500,3830,4070,5800`.

- `settling-d6.png` / `.pdf` - (a) 90th-percentile resting offset from the impact point by element
  class and breakup family; dot at 3,830 m, line over 3,500-5,800 m. (b) p90 offset under each
  variant divided by baseline, at 3,830 m.
- `settling-d6-baseline-by-depth.csv` - baseline median and p90 offset and median descent time by
  family, class and depth.
- `settling-d6-sensitivity.csv` - every variant, depth, family and class (settled share, median and
  p90 offset, median and p90 descent, field p90 radius, rows per draw).

**Depths.** 3,500 / 3,830 / 4,070 m are the p10 / p50 / p90 of seabed depth under the
no-exhaustion-prior 00:19:37 impact map (ETOPO 2022); 5,800 m is the Diamantina tail.

**Baseline inputs.** Surface current 0.13 m/s (GLORYS12V1 8 March 2014 median over 30-40 S,
88-106 E), wind 5 m/s, upper 0.05 / deep 0.02 m/s; ocean error banded 0.10 / 0.05 / 0.02 m/s with
0.03 m/s within 200 m of the seabed (independent bands); float phase through `mh370_ocean::integrate`
with per-particle end time, Stokes a = 0, diffusivity from the shared provisional prior.

**Results (p90 offset at 3,830 m).**

| class | intact | broken | fragmented |
|---|---|---|---|
| engine | 441 m | 202 m | 202 m |
| landing gear | 431 m | 214 m | 216 m |
| wing box | 5.4 km | 781 m | 445 m |
| fuselage section | 5.7 km | 825 m | 467 m |
| flat panel | 1.1 km | 1.1 km | 1.1 km |
| cabin contents | 11.0 km | 10.9 km | 12.2 km |

(At `7e4f29a` each element's descent has its own random stream, so these differ from `41c1f36`'s
by Monte Carlo noise at 256 draws, up to about 10 % for cabin contents.)

1. Depth barely matters: 3.5 to 5.8 km changes dense-class p90 by 1-24 %. The descent is short
   against the float phase and carry.
2. Dense classes (engines, gear) rest within 0.2-0.45 km: carry sets the intact case (no carry:
   x0.3-0.4), glide and carry the broken and fragmented ones. The order matches AF447's main field
   (about 600 x 200 m at 3,900 m).
3. Large intact sections that float for hours before sinking rest 5-6 km away; no float: x0.1-0.2.
   This is the intact family's detectable target, so float time is the input searched areas most
   needs settled.
4. Cabin contents spread about 11 km whatever the family; float time (x0.5 / x2 gives x0.5 / x1.9),
   surface current at its p90 (x1.5) and leeway (no wind x0.6) drive it. They are below sonar
   detection and matter to drift, not to the seabed search.
5. Sink rate x0.5 / x2 moves p90 by at most x1.5 / x0.8. Ocean-error structure (fully correlated vs
   banded) changes p90 by at most 18 %; removing the near-bottom band, by under 0.5 %.

**Pete's choices, 9 Oct, and what they show here.**

6. **Floating share x0.5 / x1.5** (declared sensitivity; the table stays the baseline). It changes
   what settles, not where: p90 offsets move by under 15 % everywhere. The afloat MASS share, which
   is what drift receives, moves 1:1:

   | variant | intact | broken | fragmented |
   |---|---|---|---|
   | baseline | 0.146 | 0.163 | 0.201 |
   | floating share x0.5 | 0.070 | 0.082 | 0.097 |
   | floating share x1.5 | 0.223 | 0.243 | 0.299 |

7. **Implosion at depth** (declared alternative, off in the baseline). With 80 % / 40 % / 0 % of cabin
   contents inside a fuselage section and collapse log-uniform over 10-1,000 m, cabin-contents p90
   falls to x0.6 (intact) and x0.5 (broken), because contents ride their section's float rather than
   their own longer, wind-driven one. Sections themselves are unchanged, and so is the afloat share
   (buoyant contents still reach the surface, later and from the collapse point). Neither the share
   inside nor the collapse depth has an airliner calibration case.
