# Settling: section collapses for hydroacoustics' implosion branch

Hydroacoustics asked for this in its ~04:15 entry (9 Oct): "per large sealed piece, a volume and a
depth-time sink path". Code: `hypotheses/settling` at `8492de7`, `Settling::emit_with_events`;
generator `settling::tests::implosion_events_real` (ignored), on the real ocean (GLORYS12 column,
ERA5, AusSeabed/GEBCO), at the four posterior impact points of `results/settling-d6-real/`, with
1,024 draws for each of intact and broken. Fragmented has no sealed sections.

**Every input that decides the answer is a DECLARED ASSUMPTION with no calibration case.** This is
the implosion alternative (Pete, 9 Oct: declared, off in the baseline):
- 80 % / 40 % of cabin contents inside a section (intact / broken);
- collapse depth log-uniform over 10-1,000 m, drawn once per section;
- trapped air log-uniform over 10-500 m3 per section at the surface, compressed isothermally to the
  collapse pressure.

So the depth and volume columns reproduce these priors. What settling adds is the **timing and
position**: each section's own float time, then its descent through the real column to its collapse
depth.

`implosion_events.csv.gz`: one row per section representative that collapses in the water column
(sections that meet the seabed first emit none). Columns: impact point, family, draw, multiplicity
(sections represented), east/north offset and latitude/longitude, depth, time since impact, TEOS-10
pressure, surface and in-situ volume, mean sink speed. A draw's rows are one wreckage configuration
and carry weight 1/1,024 of its impact; average over draws and do not sum across them.

| family | sections collapsing per draw | time since impact, q05 / q50 / q95 | depth q05 / q50 / q95 | in-situ volume q05 / q50 / q95 |
|---|---|---|---|---|
| intact | 2.5 | 815 s / 1.0 h / 5.1 h | 12 / 96 / 777 m | 0.4 / 6.0 / 85 m3 |
| broken | 13.6 (11.6 representatives) | 10 s / 2.7 min / 34 min | 13 / 99 / 791 m | 0.4 / 6.0 / 86 m3 |

Quantiles are weighted by multiplicity and pooled over the four points.

**Reading.** In this model, an intact contact's sections collapse 14 min to 5 h after impact, because
they float first. A broken contact's sections collapse within about half an hour. Whether either is
audible is hydroacoustics' question.

**Not modelled:** partial flooding during descent; collapse driven by structure rather than by depth;
more than one collapse per section; any acoustic source term.
