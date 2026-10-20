# The planned-descent run: what is planned, and what I must ask you

Written in simple English. Short sentences. One idea in each sentence.

## 1. What the question is

We want to know if the aircraft made a planned descent before the fuel ran out.

We cannot answer that by looking at one run. We must compare runs. The comparison must separate
two different things:

- the effect of the **descent hypothesis** itself;
- the effect of **where we restart the filter**, which is a sampling choice and not physics.

A two-run comparison mixes those two things together. A three-run comparison separates them.

## 2. The three arms

| Arm | What it is | What it costs |
|---|---|---|
| **V1a** | The reference run `no-exhaustion-prior`, continued from where it stopped. No descent. | Almost nothing. The filter run is done. |
| **V1b** | A new filter run that branches at 22:41. The descent support is set to zero. | One full filter run. |
| **V2** | The same 22:41 branch, with the full descent sampling switched on. | Terminal-stage sweeps only. |

Compare V1a with V1b. The physics is the same in both. So the difference is the effect of the
restart point and the sampling. That is a control, not a result.

Compare V1b with V2. The restart point is the same in both. So the difference is the effect of the
descent hypothesis. That is the result.

Without V1b you cannot say which of the two caused a change. You can only say that the two
configurations differ.

## 3. What the filter must produce

The filter must write a **hand-off** at the branch epoch. The hand-off is the state of every
surviving trajectory. The end-of-flight module reads it and continues each trajectory.

**The reference run did not write one.** Its configuration has no `[terminal]` block. So the
15.52-hour run cannot feed the end-of-flight module as it stands. This is a gap in the
configuration, not a defect in the run.

From now, every full-scale run carries a `[terminal]` block. This costs almost nothing during a run
that is happening anyway. Without it the run is unusable downstream.

### A finding that changes the plan

I tried to add a `[terminal]` block to the reference configuration and run it. The engine refused:

> `[terminal]: no bursts after the stop; list them in exclude_epochs`

**A run that writes a hand-off must stop before the bursts the terminal stage will handle.** So it
carries `exclude_epochs = ["m0019a", "m0019b"]` and its posterior is at **00:11**, not 00:19:37.

This matters for the plan. V1a is not "the reference run plus a block". It is a **different run**:

| | Reference run | Hand-off run |
|---|---|---|
| Last epoch the filter scores | 00:19:37 | 00:11 |
| Who scores 00:19:29 and 00:19:37 | The filter | The terminal stage |
| Posterior we quote | Latitude at 00:19:37 | Latitude at 00:11, then impacts |

Both are valid. They answer different questions. The reference run is the right thing to quote for
the position at the last transmission. It is the wrong thing to hand to the end-of-flight module,
because the module exists to model what happens after the filter stops, and the filter did not
stop early enough to leave it anything to do.

So V1a needs its own filter run, stopping at 00:11, with the `[terminal]` block. That is about 16
hours at full scale, or about 1 minute at smoke scale to prove the plumbing. I have run the smoke
version. It writes `handoff.toml` and `handoff.npy`, and the fuel state is real: the first row
carries `fuel_kg = 170.2` with `fuel_exhausted_unix_s = nan`.

## 4. What the hand-off carries, after the change made today

The hand-off now carries the fuel state. Before today it carried `NaN` for mass, for fuel and for
flame-out time.

| Field | Meaning |
|---|---|
| `fuel_kg` | Fuel remaining at the hand-off. |
| `mass_kg` | Zero-fuel mass plus fuel. The integrator needs this for wing loading. |
| `realised_flameout_unix_s` | The time the tanks ran dry, if they did. `NaN` if they did not. |

The third field was renamed today. It used to be called `fuel_exhaustion_unix_s`. That name invited
a reader to treat it as a prediction. It is not a prediction. It is what happened.

**The end-of-flight module must compute predicted endurance itself, from `fuel_kg`.** A descent
that starts because the fuel actually ran out assumes the crew knew the future. That is circular.
The onset must trigger on what the crew could estimate, not on what happened.

## 5. Where the branch epoch comes from

The onset window is the time between the branch epoch and predicted fuel exhaustion.

Predicted exhaustion is different for every trajectory. So the window length is different for every
trajectory. There is no single number.

At 22:41, and using the reference run's own implied exhaustion times, the window is about 96 to 104
minutes at the median. That covers a 60-minute and a 90-minute descent.

A 120-minute window does not fit. For much of the posterior it starts before 22:41. That needs the
21:41 branch instead.

**The diagnostic to report every time:** where the supported onset mass sits against the branch
boundary. If trajectories pile up at the boundary, the boundary is deciding the answer. The run
must then be repeated from 21:41.

## 6. What this run is conditional on

Every result from these arms is conditional on one assumption: **no major descent happened before
the branch epoch.** State that on every figure. It is not a free choice. It is what branching at
22:41 means.

## 7. Cost

| Item | Time | Status |
|---|---|---|
| Hand-off smoke run, to prove the plumbing | ~15 minutes at 200,000 × 5 × 2 | **done** |
| V1a, the 00:11-stop filter run, 8 × 7M | About 16 hours | needed, not started |
| V1b, the 22:41-branch filter run, 8 × 7M | About 16 hours | needed, not started |
| V2 and later variants | Terminal-stage sweeps off a stored hand-off | no filter run |

So the descent question costs **two** full filter runs, not one — about 32 hours — because V1a
also needs rerunning to produce a hand-off. That was not clear before today.

The fixed fuel model costs 1.65 times the old one for each replicate. That is measured, not
estimated. The reference run took 15.52 hours for 8 × 7M.

## 8. Questions for you

**Q1. Do we condition the end-of-flight module on fuel exhaustion between the arcs?**

You said you would start the module on that conditional. The architecture session rules against it,
and the argument uses our own numbers. I agree with the architecture session.

The reason is that the conditional does not separate a hypothesis from its alternative. At 00:19:37
the posterior is 56.9 % already dry and 30.9 % more within ten minutes of dry. So the cut does not
divide "ran out of fuel" from "did not". It divides "ran out before the model stopped looking" from
"runs out a few minutes later". It then discards the second group. That group is exactly where a
glide after exhaustion and a descent begun before it differ most.

Two further problems. The window is 509 seconds and the stored exhaustion time has a 128-second
step, so the condition's own variable has about four steps across the window. And conditioning on a
latent is admissible but must be labelled on every figure, which a whole-hand-off run avoids.

**I recommend taking the whole hand-off and conditioning on nothing.** Please confirm, because this
reverses what you said.

**Q2. Branch at 22:41 or at 21:41?**

22:41 covers 60 and 90-minute onsets and costs one run. 21:41 covers 120 minutes and costs the same
per run, but every trajectory must be carried an hour further, so the hand-off is further from the
evidence.

I recommend 22:41 first, with the boundary diagnostic reported. Move to 21:41 only if the
diagnostic shows mass piling at the boundary. That spends one run to find out rather than assuming.

**Q3. Which 00:19 scoring for the first run?**

`target = "none"` holds the 00:19 bursts out. Every later burst then becomes a prediction rather
than a fit. That is the strongest test and the right default for a first run.

You previously asked to sweep the full range of 00:19 interpretations. That sweep is cheap, because
it runs in the terminal stage off a stored hand-off. So the first run can hold out, and the sweep
can follow at no extra filter cost.

**Q4. Do we rerun the reference at full scale to get a hand-off, and when?**

This question changed today, so please read section 4 first. A hand-off run must stop at 00:11, so
it is not the reference run with a block added. It is a second run.

The smoke hand-off is already written and is enough for the module to develop against. The
full-scale version is 16 hours.

My recommendation is to **wait**. Let the module run once against the smoke hand-off and measure
its own effective sample size at 00:11. If the terminal stage turns out to be the thinner sampler,
a 56-million-trajectory hand-off buys nothing and the 16 hours is wasted. Measure first.

There is also a sequencing choice. The 22:41 run for V1b needs the same `[terminal]` block, and a
run stopping at 22:41 hands over *more* of the flight. If both runs are needed anyway, running V1b
first tests the branch machinery on the harder case.

**Q5. How many particles should the terminal stage use?**

Unknown, and it must be measured rather than assumed. The documented example uses 10 hand-off rows
and 1 child each. That is illustrative only.

The terminal stage does not carry the filter's population forward. So its 00:11 marginal comes from
a much thinner sample than the filter's. The first measurement to make is the terminal stage's
effective sample size at 00:11, against the filter's own 11.6 % there.
