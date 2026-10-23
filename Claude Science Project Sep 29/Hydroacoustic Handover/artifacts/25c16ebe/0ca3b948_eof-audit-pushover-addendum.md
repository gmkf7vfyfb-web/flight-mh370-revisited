# Addendum — was the dive branch a fix to force a match to 00:19?

Answer: **no for the mechanism you are worried about, and yes for a related one that is still
operating.** The two changes bundled into run-i-dive have different status, and separating them
settles it. Everything below is measured from
`run-i-dive/next-i-waypoints/seed-1/impacts32.npy` in this audit.

---

## 1. The aimed proposals did not touch the prior — measured

The run aims sampling at the 00:19 burst window and at steep, unloaded push-overs: 40 per cent of
push-over rate draws are taken from 18,000–40,000 ft/min, 50 per cent of load-floor draws from
0.15–0.45 g, and the pitch-down is aimed at two windows around the burst. If those aims had leaked
into the prior, the sampling weight alone would show the ensemble tilted into the aim windows.

It does not. Under the sampling weight only, every aimed latent is recovered uniform on its full
configured support:

| Aimed latent | Support | Largest deviation from uniform (weighted CDF) | Share inside the aim window, corrected | Share if uniform |
|---|---|---|---|---|
| Push-over rate | 6,500 to 40,000 ft/min | 0.0030 | 0.6615 | 0.6567 |
| Push-over load floor | −1.0 to 0.8 g | 0.0041 | 0.1650 | 0.1667 |
| Pitch-down load factor | −0.31 to 0.69 g | 0.0048 | — | — |
| Pitch-down delay | 0 to 900 s | 0.0011 | — | — |

The aim put 40 and 50 per cent of *draws* inside those windows; after correction the ensemble holds
66.15 and 16.50 per cent, against 65.67 and 16.67 per cent for an exactly uniform prior. The
residual is Monte Carlo noise, not a tilt. Two independent checks agree: the run's own stored
proposal self-check gives a mean correction of 1.000178 with a standard error of 0.000693, and the
module reports log-evidence agreeing with the unaimed run to within 0.06 nat in the cells that do
not use 00:19.

**So the targeted sampling is a precision device, not a thumb on the scale.** It buys effective
samples in a region the prior already contained, and the importance correction removes the aim
exactly.

## 2. The 00:19 data, not the sampler, does the selecting — measured

The same latents move hard once both 00:19 bursts are scored on the raw measurement model:

| Latent | Share inside the steep window, corrected prior | Same, under both 00:19 bursts |
|---|---|---|
| Push-over rate in 18,000–40,000 ft/min | 0.6615 | **0.9438** |
| Push-over load floor in 0.15–0.45 g | 0.1650 | **0.3995** |

That is the behaviour you asked for: a prior offering the full feasible range, and the evidence
pulling a steep, unloaded push-over out of it. The selection is visible as a posterior shift away
from a demonstrably uniform prior, which is exactly what makes it reportable as evidence rather
than as an assumption.

## 3. The dive branch is a support change, and it moved the answer *away* from the 00:19 data

The dive branch is a different kind of change. It is not proposal-only: before it, a piloted
push-over always recovered between 8,000 and 15,000 ft, and the earlier run is explicitly labelled
conditional on that recovery. The branch removed the recovery assumption and let a push-over
continue to the sea.

If that had been a fix to force a match, the 00:19 data would favour the new outcome. It does the
opposite:

| Weighting | P(push-over continued to the surface, given a push-over was drawn) |
|---|---|
| Corrected prior | **0.4949** |
| 00:19 R600 burst only | 0.2543 |
| 00:19 R1200 burst only | 0.4460 |
| Both bursts, raw model | 0.3105 |
| Both bursts, start-up offset model | 0.3088 |

Every 00:19 option moves the dive share **down** from its prior value. The held-out answer also
barely moved when the branch was added — impact latitude median −37.06 before, −37.07 after. A
change that forced a match would show a posterior preference for the new region and would not leave
the no-00:19-data answer untouched.

What the branch did do is make the previously unestimable cells estimable, because a powered
aircraft that reaches the sea explains the absence of a later log-on. The Bayes factor between the
two log-on causes *fell* from about 5.5 to about 4.5 nats as a result — the change made the
less-favoured hypothesis less disfavoured, which is the opposite direction from confirmation.

## 4. The real version of your concern, which is still live

Removing an unjustified exclusion is the right move, and the weights confirm it was done cleanly.
But **the trigger for noticing it was a fit failure**, and that is a selection process on the
*support* rather than on the weights. The importance correction cannot protect against it, because
it operates one level up: exclusions the data complains about get found and removed; exclusions the
data is silent about stay in place indefinitely.

That mechanism is currently operating, and the audit already names where. All four of these are
exclusions no 00:19 cell has complained about, and none has been removed:

1. **Descent onset truncated at the hand-off.** The configuration offers an anticipatory lead of up
   to 9,000 s before predicted exhaustion; from a 00:11 hand-off almost none of it is reachable, and
   21.6 per cent of the deliberate family's weight sits as a point mass against the boundary.
2. **Level-off altitudes confined to 11,000–30,000 ft**, excluding the 10,000 ft and 4,000 ft the
   brief requires.
3. **Sustained low-altitude flight effectively absent** — 1.75 per cent of weight has more than
   600 s of non-descending flight between onset and impact.
4. **Two of four control outcomes carry zero weight in the deliberate family.**

The asymmetry matters for exactly the inference you want to make. The steep, high-energy region of
the envelope has been found, widened and well sampled because the 00:19 data kept pressing on it.
The shallow, long-glide and low-altitude regions have not had the same pressure applied, so their
coverage reflects what nobody has been forced to fix rather than what the aircraft could do. A
comparison between "steep dive fits 00:19" and "shallow approach does not" is therefore not yet a
comparison between two equally well-explored hypotheses.

## 5. One implementation gap found while checking this

The dive probability does not match the ruling. The run note records a U[0,1] hyper-prior with a
marginal of 0.5; the stored configuration holds a fixed `pushover_to_surface_probability = 0.5`,
and the realised draws behave as an independent coin per descent, not as a per-parent fraction:

| Statistic across 6,232 parents with 20.4 push-over draws each | Value |
|---|---|
| Observed standard deviation of the per-parent dive share | **0.1140** |
| Predicted, independent probability 0.5 per descent | 0.1108 |
| Predicted, per-parent probability drawn from U[0,1] | 0.3025 |
| Observed mean share | 0.4975 |

So the run asserts that exactly half of piloted push-overs continue to the surface, as a known
quantity, rather than carrying ignorance about the fraction. This **understates** the uncertainty on
the latent that the run note identifies as driving the R1200-conditioned result — the 90 per cent
impact area moved from 59,000 to 47,000 km² when the branch was added, and 64 per cent of the
southern group are levelled-off push-overs. With the hyper-prior implemented, the evidence could
learn the fraction and the impact distribution would inherit the spread of that uncertainty instead
of averaging over a fixed coin.

## 6. What to do about it

**a. Implement the ruled hyper-prior and re-run the R1200 cells.** Draw the dive fraction per
hand-off trajectory from U[0,1], not per descent at 0.5. Report the posterior on the fraction as a
result — it is a directly estimable quantity and currently it is pinned.

**b. Adopt a support-change log and a held-out re-validation rule.** Every change to what the model
can reach gets an entry recording the physical justification, whether the change was prompted by a
fit failure, and the held-out log-evidence and impact median before and after. A support change that
moves the held-out answer is a different event from one that does not, and the distinction is
exactly what settles a forcing question later. The dive branch would pass this test on the record
above; it is worth having the record for the next one.

**c. Run a silent-exclusion review before the next sweep.** List every bound, probability of zero,
and configured range in the envelope, and for each ask whether its justification is independent of
how well anything fits 00:19. The four items in §4 are the current answers. This is the only
procedure that corrects the asymmetry, because the sampler's own diagnostics cannot see it.

**d. Keep the aim.** It is working as designed and it is the thing making the contested cells
estimable at all. The honest framing for the paper is that the aim resolves regions the prior
already contained, demonstrated by the recovery of the uniform prior under the correction, with the
measured numbers in §1 quoted as the evidence.
