# The evidence ladder, and the endurance-aware proposal

Four runs adding one measurement set at a time, all on Davey's own priors — Mach 0.73–0.84,
altitude 25–43 kft, track standard deviation 1°, 7 Hz BFO — with the fuel model and the vertical
rate in the cruise BFO throughout. Only the evidence admitted to the likelihood changes down the
ladder, so movement between rungs is attributable to the measurements added and not to a changed
model. Four replicates each, 14 million particles per replicate, allocation equalised across the
five autopilot modes.

Every rung flies every particle through to 00:19:37 whether or not that epoch is scored, so the
00:19 arc can be read as a prediction on the rungs that never saw it. The residual below is
recomputed from each run's own saved final positions with `report/satcom_model.py`'s forward
model — the same BTO equations as `crates/satcom`, checked against the core's fixture to 1e-6 —
rather than read from the run, so it does not depend on what the filter chose to weight.

## What each measurement set does

| rung | likelihood | median | P(shoulder) | overlap with Fig 10.3 | log evidence | split-half |
|---|---|---|---|---|---|---|
| 1 | fuel and endurance only | 13.8°**N** | 0.0018 | 0.005 | −7.73 | **0.996** |
| 2 | + BTO through 00:11 | 36.91°S | 0.0837 | 0.560 | −63.21 | 0.766 |
| 3 | + BFO through 00:11 | 37.57°S | 0.1211 | 0.757 | −93.94 | 0.857 |
| 4 | + BTO and BFO through 00:19 | 37.60°S | 0.0898 | 0.732 | −104.46 | 0.864 |
| — | reproduction, no fuel model | 38.16°S | 0.0368 | 0.717 | −96.26 | 0.934 |

### The 00:19 arc, predicted rather than fitted

| rung | range error, RMS | mean | weight inside the arc | weight within 5° of the median |
|---|---|---|---|---|
| 1 | **1,268 km** | +705 km | 79.4 % | 3.7 % |
| 2 | **36 km** | +6.6 km | 30.5 % | 60.1 % |
| 3 | **17 km** | −2.3 km | 21.0 % | 96.5 % |
| 4 (fitted) | 4.7 km | −2.6 km | 24.5 % | 98.1 % |

The measurement standard deviation is 43 µs, or 6.4 km of slant range. Rungs 2 and 3 never scored
the 00:19 arc and still predict it to 36 km and 17 km — under three times the measurement noise
from a posterior fitted only to the earlier arcs. That is the ladder's most useful single result:
the model generalises to a held-out arc, which no amount of agreement with a published figure
would establish.

### The BFO is what decides the hemisphere

| rung | north of the equator | south of 30°S |
|---|---|---|
| 1 | 77.5 % | 1.1 % |
| 2 | 22.1 % | 68.9 % |
| 3 | **0.00 %** | 98.4 % |
| 4 | **0.00 %** | 98.9 % |

Fuel alone bounds how far the aircraft could get and says nothing about direction, so rung 1 is a
disc about 47° of arc in radius centred on the 18:01 position, with 77 % of its weight north of
the equator and a visible concentration where the 18:01 track continues unturned — median turns
there is 0 against 4 across the posterior. The BTO collapses that disc radially onto the arcs but
leaves mass spread along them, including a northern branch over Asia. The BFO then removes the
northern hemisphere outright: 22.1 % to **nought**, to the precision 56 million particles can
express. This is the textbook statement that the Doppler breaks the north–south ambiguity,
measured in this engine rather than assumed.

Rung 3 also carries the ladder's largest shoulder, 0.1211. Adding the 00:19 epochs pulls it back
to 0.0898, so the last arc is a southward constraint on top of everything the earlier arcs say.

## Convergence, and what is reportable

Only rung 1 meets the declared 0.90 split-half floor, and it does so trivially at 0.996 — with no
BTO or BFO nothing ever resamples, effective sample size stays at 2.75 of 2.8 million per mode,
and 714,000 distinct prior draws survive against about 250 in the fully-conditioned baseline. It
is the cheapest statistical problem of the four and the most expensive computationally, at 49
minutes per replicate against about 10, because the particles stay spread over the globe and
every step pays for scattered ERA5 lookups.

Rung 2 is the worst at 0.766, and the reason is structural rather than a budget problem: the BTO
constrains range but not bearing, so the posterior is spread along a one-dimensional manifold
thousands of kilometres long and the sample along it is thin. The m1941 effective sample fraction
falls to 0.080 %. Its replicate median span is 1.69°, against 0.13–0.21° for the other three rungs
(0.130° at rung 1, 0.208° at rung 3, 0.202° at rung 4). **Rung 2's numbers should be read as
indicative only.**

Rungs 3 and 4 sit at 0.857 and 0.864 — short of the floor, in the way already documented for the
fuel runs, with the residual replicate disagreement concentrated in the northern tail that the
shoulder statistic measures.

## Does the endurance proposal change the answer?

The point of the new proposal is efficiency, not a different posterior, so rung 4 was run twice at
identical seeds and particle counts — once with the published reject-at-the-deadline sampler and
once with the endurance-aware one.

| | reject | endurance |
|---|---|---|
| split-half | 0.829 | **0.864** |
| replicate median span | 0.317° | **0.202°** |
| log evidence | −104.515 | −104.461 |
| median | 37.828°S | 37.603°S |
| 95 % interval | 39.386 to 34.854°S | 39.449 to 34.793°S |
| P(shoulder) | 0.0868 | 0.0898 |
| mode TT / LNAV | 0.559 / 0.307 | 0.590 / 0.280 |

**The two posteriors agree to within their own replicate noise.** The direct test is the overlap
between them: **0.844**, which sits inside the within-run replicate pairwise overlap range of both
runs (endurance 0.704–0.877, reject 0.722–0.849). In other words the two samplers differ from each
other no more than two replicates of the same sampler differ from each other. The log evidence —
a single number integrating the whole posterior, and the most global check available — agrees to
**0.054 nats**, and the 95 % bounds to 0.06°.

Against that, the efficiency gain is real but modest: split-half 0.829 to 0.864, and replicate
median span tightened by 36 %. Not enough to clear the floor on its own.

So the honest verdict on the proposal is: it is correct, it helps, and it is not sufficient. The
in-kernel tests establish correctness directly — `min_flow_is_a_true_lower_bound` sweeps
FL060–430 × M0.40–0.86 and confirms no tabulated state undercuts the pruning bound, and
`the_endurance_proposal_leaves_the_mach_prior_unchanged` draws 40,000 Mach targets at a fuel state
that splits the range, finding the raw draws skewed about tenfold toward slow cruise and the
reweighted distribution uniform to within 1.2 points per bin. This run is the same statement at
full scale.

## What would close the remaining gap

The endurance proposal fixes the part of the problem that was about the speed profile. What it does
not touch is the m1941 bottleneck, which is where every unconverged rung loses its effective
sample — 0.080 % at rung 2, 0.127 % at rungs 3 and 4. That epoch is early, the posterior there is
still broad, and no amount of knowing about fuel helps a proposal that is wrong about where the
aircraft was at 19:41. The next move is a look-ahead at that epoch specifically, or a backward
pass, rather than more particles: eight replicates and 14 million particles have both been tried
and neither closed it.
