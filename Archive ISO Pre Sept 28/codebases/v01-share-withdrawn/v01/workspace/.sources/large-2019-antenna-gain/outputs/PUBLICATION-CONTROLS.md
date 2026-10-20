# Publication controls for the antenna-gain hypothesis

## Outcome

No scientifically defensible early-MH370 spatial posterior can be generated
from the present inputs. The requested 16:42 state is in climb at about 1,700
ft; the canonical known-flight dynamics and weather fixtures do not cover that
climb regime or 16–17 UTC, and the retained ADS-B control supplies ground track
rather than true heading. The known positions also cannot be used both to
construct per-arc candidate clouds and to claim a truth-separated trajectory
test. No 18:25 state is treated as observed truth.

The closest honest early-MH370 control is therefore the generated forward
received-power holdout: six channel-event points at 16:42 calibrate one common
offset per endpoint, then twelve channel-event points in the 16:55 and 17:07
bursts are predicted. Its pooled RMSE is 1.294 dB
for no precompensation and 1.456 dB for full
precompensation. The two bursts, not the repeated reports, are the replicate
units. This is not spatial inference.

The valid MH371 truth-separated spatial control keeps the medium-BFO model and
all non-antenna settings fixed. At the terminal 06:48 checkpoint, the
two-seed mean posterior-position error changes from
26.36 NM to
20.13 NM; mean mass within
100 NM changes from 0.6041
to 0.6208; and mean truth HPD
mass changes from 0.6701 to
0.7517. Lower truth HPD mass is
better; the endpoint does not improve that terminal calibration metric.

## Detectability boundary

The primary blocked comparison remains +0.1161
log-density units per point, with 95% event-bootstrap interval
[-0.1936, +0.4616]
and descriptive sign-flip p=0.5364.
Separated by flight, MH371 gives
+0.2944
over 13 events, whereas early MH370 gives
-0.6564
over only 3 events. The early-MH370
forward construction reverses direction again. The effect is therefore not
stably or transportably detected in the available controls.

## Recommended placement

- Main paper: `figure_6_gain_hypothesis_by_flight` with its flight-stratified
  table. It directly supports the boundary that detectability is unstable.
- Supplement: `figure_4_mh371_spatial_endpoint_comparison` and the existing
  MH371 posterior density panels, plus their long-form metric table.
- Supplement or methods: `figure_5_early_mh370_forward_power_control`, clearly
  labelled as a forward power holdout and not a position estimate.

All figures are generated as 300-dpi PNG and vector PDF. Seed ranges in the
MH371 table are numerical-replication sensitivity, not independent-aircraft
confidence intervals. Event-bootstrap intervals and sign-flip p-values are
descriptive because training sets overlap and epoch exchangeability is not
established.
