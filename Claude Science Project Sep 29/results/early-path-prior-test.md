# Does the 18:01 prior suppress a better explanation of the early arcs?

## The question

Two competing explanations exist for the 18:25–18:28 BTO sequence, which is not
consistent with a path along airway N571 at cruise speed that also passes the
18:22:12 radar position:

1. the aircraft was on N571 but **slow**; or
2. the aircraft was at normal speed but **not on N571** — a more north-north-westerly
   heading, possibly north of the airway.

The base configuration can sample neither. It fixes the 18:01:49 track at 295.66°
with a **1.0° standard deviation** (Table 8.2), so a track 20–35° further north is
20–35 σ out at the prior; and it floors Mach at 0.73, which forbids the slow
branch. The question is whether those two restrictions are suppressing a better
explanation of the data.

## A diagnostic that did not work

The first attempt compared the per-epoch **misfit** — the gap between the best
achievable log-evidence increment at an epoch (all residuals zero) and the
increment the population actually achieved. The reasoning was that if the
population cannot reach the configurations an arc wants, the misfit at that arc
should be large, and should fall when the prior is widened.

The misfit did not fall. It rose:

| epoch | base | track sd 15° | track sd 15° + Mach ≥ 0.41 |
|---|---|---|---|
| m1825 | 1.34 | 1.85 | 2.85 |
| m1828a | 1.88 | 2.24 | 2.21 |
| m1839 | 3.71 | 3.85 | 4.43 |
| m1941 | 5.27 | 5.22 | 5.31 |
| **total** | **26.13** | **27.69** | **29.31** |

That is a property of the statistic, not an answer to the question. The misfit is
a population *average*: widening a prior adds both the configurations that fit
better and a great many that fit worse, and the average necessarily degrades even
if the good ones are now reachable. The diagnostic cannot distinguish "the
population still cannot reach a good explanation" from "it can, but is now diluted
by bad ones". It is recorded here because it was run and because the confound is
worth documenting, not as evidence either way.

## The statistic that does work

Only the prior changed; the observation model is untouched. Log evidence is
therefore directly comparable, and it is exactly the right quantity — the average
likelihood over the prior, which rises if a widened prior admits a genuinely
better explanation and falls if it merely adds mass over configurations that fit
no better.

| run | log evidence | Δ vs base | replicate sd | Bayes factor |
|---|---|---|---|---|
| base | −96.26 | — | 0.114 | — |
| track sd 15° | −97.89 | **−1.63** | 0.024 | 5.1× against |
| Mach ≥ 0.41 | −98.16 | **−1.89** | 0.120 | 6.6× against |
| both | −99.68 | **−3.42** | 0.132 | 30.6× against |

The differences are 12–140× the replicate standard deviation, so the ordering is
not seed noise even though neither widened run met the convergence floor (split-half
0.891 and 0.863 against 0.90).

**The data does not ask for either widening.** Neither a wider initial track nor a
lower Mach floor finds an explanation good enough to pay for the extra prior
volume, and combining them is worse than either alone.

## What this does and does not establish

It does **not** establish that the base prior is physically right, and the
distinction matters for how this is written up.

Log evidence compares *priors*, not truths. It penalises diffuseness. If the
actual trajectory lies in a small sub-region of the widened space, the evidence can
fall while the truth sits inside the space that was added — the average over a
mostly-bad region drowns a good corner. So the correct claim is narrow: **over the
regions added here, taken as a whole, there is no better explanation than the base
region already contained.** A targeted hypothesis — a lateral offset applied after
18:22:12 rather than a diffuse widening at 18:01:49 — is a different model and is
not tested by these runs. That is the right next implementation, because it puts
the freedom where the physical argument puts it: after the last radar return, not
before it.

## An uncomfortable finding

The widened priors agree *better* with Davey's published curve while scoring
*worse* under our own likelihood:

| run | overlap with Fig. 10.3 | P(shoulder) | log evidence |
|---|---|---|---|
| base | 0.717 | 0.0368 | −96.26 |
| Mach ≥ 0.41 | 0.764 | 0.0974 | −98.16 |
| track 15° + Mach ≥ 0.41 | **0.789** | **0.1507** | **−99.68** |

That is the best agreement with the published result any run has produced, and it
comes with the worst evidence. The mode mixture is what moves: MH rises 11× from
0.0032 to 0.0363 and MT 6.7× from 0.0146 to 0.0973, while TT falls from 0.5427 to
0.3645 — the same magnetic-mode reweighting the measurement-error sensitivity
found, reached by a different route.

Two readings, and they are not yet separable:

1. Davey's published curve reflects a **broader effective prior** than the stated
   one. This is consistent with the branching-resampler analysis: promotion to unit
   weight flattens the mode mixture, which mimics a wider prior. Under this reading
   our evidence is right and the published curve is partly a sampler artefact.
2. Our **likelihood is mis-specified** in a way that penalises exactly the
   trajectories Davey's curve contains — most plausibly the BFO model, which has no
   vertical-rate term and whose σ inflation is standing in for an unmodelled
   within-flight bias process.

Every change that moves us toward the published curve lowers our evidence, which
is the pattern reading 2 predicts and reading 1 tolerates. Separating them needs
the branching resampler run inside this engine and vertical rate in the BFO model
— both already queued, and both now with a sharper question to answer than before.
