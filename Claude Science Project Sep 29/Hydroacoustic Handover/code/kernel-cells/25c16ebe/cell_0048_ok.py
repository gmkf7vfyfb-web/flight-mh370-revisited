# --- C. Boundary gate ---
ed("""Making the checkpoint *be* the earliest permitted onset removes an arbitrary horizon, but keep the
diagnostic: **if supported trajectories accumulate against the checkpoint boundary, the boundary is
influencing the answer** and the run must be repeated from 21:41. Report where the supported onset
mass sits relative to the boundary, every time.
""",
"""Making the checkpoint *be* the earliest permitted onset removes an arbitrary horizon, but keep the
diagnostic: **if supported trajectories accumulate against the checkpoint boundary, the boundary is
influencing the answer** and the run must be repeated from an earlier checkpoint.

**The onset-boundary gate.** The previous version required this diagnostic "every time" and gave it
no statistic, no number and no consequence, so neither full sweep reported it and the condition was
met unnoticed. It is now a gate.

- **Statistic.** The weight fraction with descent onset within 60 s of the earliest permitted onset,
  computed **per family**, under the held-out weighting *and* under each 00:19 option.
- **Where.** The coverage section of every run note, as a named row. Not optional, not conditional
  on it looking small.
- **Consequence.** Above **5 per cent in any family under the held-out weighting**, the sweep does
  not support any statement about descent initiation and must be repeated from an earlier
  checkpoint. Between 1 and 5 per cent, the arm is reportable with the figure quoted beside every
  onset number. Below 1 per cent, the boundary is not influencing the answer.
- **Current value, measured 13 October on run-i-dive:** 21.6 per cent for the deliberate-descent
  family, with the earliest onset in the file at the hand-off epoch itself. The gate is failed. The
  anticipatory-onset support configured at 0 to 9,000 s of lead is almost entirely unreachable from
  an m0011 hand-off, so **what the current tables label a deliberate descent is a descent beginning
  in the last eight minutes of the flight**, flown by an aircraft required to be powered to 00:11.
  That is not the hypothesis this section describes.
""", "C boundary gate")

# --- D. Level-off and low-altitude as checkable bounds ---
ed("""- randomly sampled trigger points and profile shapes, so the ensemble is not a handful of
  hand-chosen archetypes;
- substantial lower-altitude flight as a possibility: **an hour between onset and impact need not
  mean an hour descending.**
""",
"""- randomly sampled trigger points and profile shapes, so the ensemble is not a handful of
  hand-chosen archetypes;
- substantial lower-altitude flight as a possibility: **an hour between onset and impact need not
  mean an hour descending.**

**Two of the above were prose and failed quietly. They are now bounds with a reported statistic.**
Both were written as bullets with no corresponding number in any run note, and an audit on
13 October found neither honoured.

| requirement | checkable form | reported statistic | current value |
|---|---|---|---|
| level-offs including 10,000 ft and 4,000 ft | the sampled level-off altitude support **must contain both**; state the interval in the run note | the realised level-off altitude distribution | **failed** — support is 11,000 to 30,000 ft, excluding both |
| lower-altitude flight need not mean descending throughout | the realised non-descending time between onset and impact | its median and 95th percentile, and the weight fraction above 600 s, which must exceed **5 per cent** | **failed** — median 53 s, 95th percentile 411 s, 1.75 per cent above 600 s |

Keep the provenance note either way: the recovered simulator data is the reason for *including*
4,000 ft in the envelope, never support for it having been flown.
""", "D envelope bounds")

# --- E. Control weights per family ---
ed("""Within either initiation branch allow: control maintained through an attempted ditching; control
maintained then lost; no effective intervention during the terminal descent; and upset followed by
recovery and renewed control — which must be *dynamically demonstrated*, including sufficient
altitude, not merely asserted.
""",
"""Within either initiation branch allow: control maintained through an attempted ditching; control
maintained then lost; no effective intervention during the terminal descent; and upset followed by
recovery and renewed control — which must be *dynamically demonstrated*, including sufficient
altitude, not merely asserted.

**All four, in every family, and the weights are stated per family in the run note.** A zero weight
is a modelling decision that needs writing down and justifying, not a configuration value. Measured
13 October: the control weights are 1, 1, 1, 1 for the two fuel-exhaustion families and
**0.5, 0.5, 0, 0 for the deliberate family**, so the two outcomes are absent from precisely the
family where the next paragraph's distinction decides the result. Nothing in the run notes recorded
it.
""", "E control weights")
print(EDITS)
