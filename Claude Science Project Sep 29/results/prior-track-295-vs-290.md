# The 18:01:49 prior track is about 6 degrees too far right

Found 9 Oct while overlaying posterior routes on a chart (Pete's question: why are all the routes
north of N571 and MEKAR at 18:22?). **It is in the model, not the plot.** The chart georeference is
good to 0.2 NM.

## What the runs use

`config/davey2016.toml [prior]`: 5.624829 N, 99.048157 E, track **295.66 deg**, sd 1.0 deg, position
sd 0.5 NM. The position and track are a **reconstruction from earlier project notes**. Davey et al.
do not tabulate them; `report/` page 8 flags this ("Prior mean position and track: not tabulated").

## What the evidence says

| Quantity | Value |
|---|---|
| Davey Fig. 4.2 smoothed radar track angle, digitised from the book's lower panel (frame +50 to -150 deg) | **-70.3 deg = 289.7 deg true at 18:02**; 289.0-290.3 from 17:55 to 18:22 |
| Bearing from the prior position to 10 NM past MEKAR on N571 (last radar, about 18:22, per ATSB; Ashton et al. 2015: "passed close to the MEKAR waypoint" at 18:22) | **289.6 deg** |
| Bearing from the prior position to MEKAR | 289.2 deg |
| Davey sec. 4: the 18:22 radar point is "clearly within the azimuth fan" of the prior (+/-1 deg) | consistent with about 289.7, not with 295.66 |
| Reference-run posterior at 18:21:49 | median 6.812 N 96.574 E; 19 NM from MEKAR; **12-26 NM right of N571** |
| 10 NM past MEKAR, relative to the 295.66 prior | 6.4 sigma off the mean track: excluded by the prior |

## Why it matters

The 18:25 and 18:28 BTO fit differently on the two tracks (engine measurement model, 35,000 ft):

| Ground speed after 18:22 | On 295.66 from 18:01:49 (sum z^2) | On N571 via MEKAR + 10 NM at 18:22:12 (sum z^2) |
|---|---|---|
| 400 kt | 175.6 | **5.5** |
| 450 kt | 35.5 | 14.7 |
| 480 kt | 2.8 | 22.5 |
| 500 kt | **1.9** | 28.6 |

On N571 the arcs need the aircraft to slow to about 400 kt or below. That is the slow-down Davey
sec. 4 describes ("the aircraft may have slowed down at some point between 18:02 and 18:22"). The
295.66 track lets cruise speed fit instead, so the reconstruction hides the slow-down. Every run in
the project so far, including `reference-snapshots` and its hand-offs, uses 295.66.

## What is not yet known

Whether it moves the 00:19 posterior. The later arcs and manoeuvres may absorb a 20 NM early
offset, or may not: 19:41 is the narrowest bottleneck. The next step is a smoke-scale A/B at
289.7 against 295.66 (logZ, the 18:25-18:28 residuals, the 00:19 median), and only then a decision
on a full re-run. The 18:01:49 prior POSITION is also a reconstruction and should be checked the
same way. The waypoint screen of 9 Oct started from the 295.66-propagated 18:21:49 position. Its
fixed-start results should be re-run from 10 NM past MEKAR; the coverage maps describe the runs
as they are and stand.
