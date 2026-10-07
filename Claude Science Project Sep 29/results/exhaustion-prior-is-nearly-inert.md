# The 00:17:30 exhaustion term is nearly inert — re-measured on the fixed fuel model

The earlier version of this note reached the right conclusion from a run whose fuel burn was
defective. This version re-measures it on the fixed binary, where the burn is physical and
about half the posterior now reaches exhaustion. The conclusion survives, the number moves
from 0.09 to 0.17 nats, and the reason changes.

## The measurement

Matched smoke pair, 2 replicates × 999,000 particles, `6temper-realloc` allocation scaled
down, fixed fuel model, one variable — `exhaustion_target_utc = 00:17:30` with
`exhaustion_sd_s = 300` present or absent. Nothing else differs.

| | term present | term removed |
|---|---|---|
| median latitude at 00:19:37 | −37.144° | −37.187° |
| 50 % interval, shoulder mass | 0.2703 | 0.2571 |
| overlap with Davey Fig. 10.3 | 0.6968 | 0.6942 |
| split-half overlap | 0.6660 | 0.6559 |
| dry by 00:19:37 | 47.83 % | 51.53 % |
| log evidence | −105.644 | −98.852 |

The two posteriors differ by L1 = 0.043. The median moves 0.043°, which is **exactly** the
median's own half-to-half agreement at full scale. In other words the term changes the answer
by about as much as the sampler's own noise.

## Why the 6.79-nat evidence gap is not a 6.79-nat constraint

Removing the term raises log evidence by 6.792 nats, which looks like a strong constraint and
is not. The difference is `log E_posterior-without[L_exhaust]`, and a Gaussian **density** with
σ = 300 s carries a normalising constant of `−log(300√(2π)) = −6.623` nats that every path pays
regardless of how well it fits. Evaluating the term directly over the term-removed posterior
reproduces the observed gap to three decimal places:

```
observed   logZ(on) − logZ(off)              −6.792 nats
predicted  log E_off[L_exhaust]              −6.791 nats
  Gaussian density normalisation             −6.623 nats   (a constant, no discrimination)
  actual misfit                              −0.168 nats
```

So the term discriminates between trajectories by **0.17 nats**, a weight ratio of 0.85. It is
a nearly flat multiplier, not a constraint.

The reason has changed from the defective-binary measurement. Then, the term was flat because
almost nothing ran dry and a never-dry path was scored once, at the last step, 127 s from the
target — 0.42 σ, −0.0896 nats — so the term could not distinguish 100 kg remaining from 10 t.
Now half the posterior **does** run dry, and the term is flat for the opposite reason: the dry
paths land a mean 197 s from 00:17:30, which is 0.66 σ. The satcom arcs have already placed the
aircraft so precisely that the fuel it has left at 00:19 is nearly determined, and the
exhaustion term finds almost nothing left to say.

## The post hoc test, with an honest denominator

From the run with the term **removed**, so no hypothesis is forced on the ensemble:

| | share of all mass | share of the dry mass |
|---|---|---|
| runs dry by 00:19:37 | 51.53 % | 100 % |
| dry between the 6th and 7th arcs, 00:11–00:19:29 | **47.22 %** | **91.65 %** |
| dry within 00:17:30 ± 10 min | 51.22 % | 99.41 % |

Unforced, the fuel model puts **nearly half the posterior** running dry inside the 8.5-minute
window between the sixth and seventh arcs, and **92 % of everything that runs dry at all**
lands in that window. That is the quantity worth reporting in support of the flame-out
hypothesis, because it is measured without conditioning on it.

Two caveats on the table. First, the ±5 min window returns the same 47.22 % as the arc window
even though the two windows are not the same interval; that is an artifact of storage
resolution, not an equality — `fuel_exhausted_unix_s` is a float32 whose ulp at 1.394 × 10⁹ is
exactly **128 s**, so only 21 distinct times are representable and the populated ones
(00:10:40, 00:12:48, 00:14:56, 00:17:04, 00:19:12) fall inside both windows except the first.
This should be stored as an offset from a run-level epoch before the figure goes in the paper.
Second, this is smoke scale with split-half 0.656; the full-scale run is what gets quoted.

## The decision

Drop the term, as agreed. The case is now stronger than when the decision was taken:

- It is worth 0.17 nats and moves the median by less than the sampler's own noise.
- It conditions the ensemble on a disputed cause — that the 00:19 log-on followed engine
  failure rather than Lyne's or another mechanism — for no inferential gain.
- Removing it turns exhaustion time and position from an input into an **output**, so the
  00:11–00:19:30 hypothesis can be tested post hoc against a denominator that does not already
  assume it.

`require_power_until = "m0011"` is retained. That is an observation, not a hypothesis: the
aircraft transmitted at 00:11, so a path whose tank ran dry earlier contradicts the data.
