# Run I (core), 12 Oct 2026: first readings, waypoint family

Source: next-i-waypoints, deskstar job 80e619ca, build ee34559, 8 seeds × 7M, staged at mh370-exchange/core/run-i/.
Shares are posterior weights from final.npy, normalised within each seed, then averaged over the 8 seeds (sd across seeds).

- `waypoint-plan-shares.csv`: first fix, first-leg break-off and fly-by, last-leg change of mode part-way, equator decision, number of legs.
- `waypoint-plan-sequences-top40.csv`: fix sequences. A `*` marks a leg left part-way: on the last leg this is the change of mode before the fix; on an earlier leg it is the break-off.
- `waypoint-turn-start-*.csv`: the time the southward turn starts in the 2,000 posterior route draws per seed (40 s trace from 18:22:00). Start = the last 40 s interval before the track has turned more than 15° left of its 18:30:00 value, with less than 2° of turn in the interval before.

Headline: SAMAK first 0.943 (sd 0.023); IGOGU 0.041; NILAM 0.012; ANOKO 0.003. First leg fly-by 0.80; first-leg break-off at 40-80 % 0.19.
SAMAK then ISBIX (with or without a part-way change of mode): 0.70. Two legs 0.76.
Turn start median 18:37:40; 86.8 % between 18:37 and 18:39; 5th percentile 18:33:40.

## Added 12 Oct ~15:20Z
- `run-i-family-evidence.csv`: four families at equal prior: log-evidence, seed sd, Bayes factor against waypoints, posterior share with a seed-bootstrap 90 % interval, split-half, 00:19 median.
- `run-i-turn-zoom.png/.pdf`: posterior route draws 18:22-18:42 on Pete's chart (affine fit to 12 fixes, residual 1.4 px or less), by family and by turn area. The turn area is classified by the northernmost latitude reached.
- `traffic-separation-*.csv`: closest approach of each trace draw to IGO053 (estimated track) and UAE343 (ADS-C), 18:25-18:39. Lateral distance in NM; the vertical check uses 1,000 ft.
- `refresh-smoke.csv`: particle refresh at 23:15 changes nothing (see CORE_STAGES).
- `destination-diagnostic-*.csv`: post-run diagnostic only (Pete). For each posterior route draw, the great circle continued from the last 10-min segment, for draws that are straight within 5 NM over the last 3 h, and its closest approach to NZFX and to the South Pole.
  Caveat: any track near 180 deg points at the pole, so closeness to the pole is mostly geometric and is not evidence of a destination.
