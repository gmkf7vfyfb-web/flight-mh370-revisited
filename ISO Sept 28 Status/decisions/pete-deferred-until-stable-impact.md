---
name: pete-deferred-until-stable-impact
description: "Methodology items Pete deferred on 2026-09-28, and the milestones at which to remind him (stable engine to impact; hydro staged work done)"
metadata:
  node_type: memory
  type: project
  originSessionId: b321a56a-4f19-4c04-acbd-d5031b94cf81
  modified: 2026-09-28T18:25:06.769Z
---

On 2026-09-28 Pete answered the review of the ChatGPT methodology (materials in thr_4pbhvf3sxi's Attachments). His draft reply used my first-pass numbering (review of 14:49 UTC that day).

**Adopted and now in progress (managed by thr_4pbhvf3sxi):**
- Settling model as its own module, "Ocean impact to ocean floor". It should learn from AF447 (including its mistakes) and from other aircraft and non-aircraft cases.
- Core estimator: the feasible speed prior, then the 00:11 vertical speed, descent onset and altitude bands. One element at a time, with split-half and blind MH371 checks. Order: fuel state, speed prior, vertical speed and onset, altitude bands.
- End of flight:
  - powered-through-00:19, later-exhaustion and powered-impact hypotheses;
  - attitude, electrical state and configuration modelled there;
  - start from the actual stage-1 00:11 posterior;
  - no hard-coded family percentages.
- Composer: results per end-of-flight hypothesis first. Any average only beside a prior sensitivity.

**Remind Pete when the engine runs stably and convergently to impact:**
- the deferred adopt items, as I read "come back to 5, 6, 7":
  - breakup and energy state as a shared impact field (also the mechanism the settling module needs to reach seabed-search);
  - a start-up BFO offset conditioned on the power-outage duration;
  - leave-one-out results and per-module information gain;
- integrating Antenna gain (set up but parked);
- the paid aero options (see [[revisit-paid-aero-options]]).

**Remind Pete when Hydroacoustics finishes its staged work** (prediction, the detection protocol and controls, the Kadri package):
- discuss next steps;
- include the Blackman 2001/2003 airgun catalogue as a calibration set. The intact receiver table he attached is blackman_receiver_observations.csv in the Attachments.

**Parked:** the satellite-imagery acquisition census (Pete agreed it is data gathering, not a module).

**Why:** Pete wants one stable, convergent engine to impact before widening scope. He asked explicitly to be reminded at those points.

**How to apply:** check this list whenever a milestone is reported (e.g. the composer running end-to-end with converged split-halves, or the hydro thread reporting its three deliverables done). Remind him then, briefly, with the list. See [[thread-coordination]].
