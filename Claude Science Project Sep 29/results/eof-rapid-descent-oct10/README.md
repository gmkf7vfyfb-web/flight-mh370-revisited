# Rapid commanded descents and a load-factor floor: capability built, default off (end of flight, 10 Oct 2026, ~23:15 UTC)

**SMOKE SCALE. NOT IN RUN C. H1/H2 NOT CONVERGED** (about 2 effective parents; within-parent sampling, smoke 2). Seed 1, N = 1 child
x 4 descents, core next-run (b) `next-free` hand-off at 00:11, run C module recipe + `full/residual-bank-boeing.toml`. Reach-gap
label (architecture 15:45 -0600) applies to the "off" column; this note is about closing it.

## What was built (module only; both switches default off)
1. `track_load_factor_floor_g` (module parameter, Option): a commanded-rate descent (`Command::Track`) unloads no further than this
   load factor while it pitches down. Before: only the C_L limit applied, so a large commanded rate could pull below 0 g (test:
   a 20,000 ft/min command from level at FL350 reaches n < 0 without the floor, and stops at 0.30 g with a 0.3 g floor).
2. `envelope.rapid_descent_probability` and `envelope.rapid_descent_rate_fpm` (default U[6,500, 20,000] ft/min): with this
   probability, the emergency segment of the `EmergencyThenTransition` powered shape is flown at a rapid commanded rate.
   Before: commanded rates were capped at 6,500 ft/min, so a deliberate push-over could not be represented.
3. Test overlay `smoke/rapid-descent.toml` (floor 0 g, probability 0.5 - a test value, not a proposal).
4. Tests: 104 pass. With both switches absent the output is deterministic (a repeat run is byte-identical) and equals the run C
   binary to rounding: 30 of 107 columns differ in at most 18 of 399,996 rows, by at most 1e-13 relative (latitude 7e-15 deg).
   It is NOT byte-identical (a code-generation effect; cause not isolated). The run C binary does not contain this change.

## Effect (prior and 00:19 evidence, `unpowered` constraint)

| quantity | off | on (test overlay) |
|---|---|---|
| prior P(vertical-speed change 00:19:29 to 00:19:37 <= -10,450 ft/min, airborne) | 0.061 % | 0.065 % |
| prior P(<= -8,000 ft/min) | 0.179 % | 0.185 % |
| prior P(max descent rate > 6,500 ft/min) | 32.2 % | 36.9 % |
| prior P(max descent rate > 15,000 ft/min) | 15.7 % | 17.7 % |
| ln Z, 00:19 Holland H2 (eff. parents) | -25.38 (2.0) | -25.14 (2.2) |
| ln Z, 00:19 Holland H1 (eff. parents) | -36.29 (1.2) | -36.19 (1.4) |
| ln Z, 00:19 R600 BTO Only (eff. parents) | -5.633 (72,615) | -5.634 (72,635) |

Reading:
- Rapid descents are now reachable, but they hardly change the push-over tail at the burst times (0.061 % to 0.065 %).
- The reason is **timing**: a rapid descent starts at the drawn onset, and its push-over lasts a few seconds. It must coincide
  with the 8-s interval between the two bursts, and the onset draw rarely puts it there.
- So the binding limit for H1/H2 is the **sampling** of that coincidence (the targeted within-parent proposal; needs core
  request 9 and Pete's go), not only the reach of the model. This agrees with the architecture push-over study (section 6).
- H1/H2 ln Z values here are unconverged and must not be quoted.

## COVERAGE
(a) Feasible set: a 777-200ER can be pushed over to near 0 g (limit load -1 g flaps up) and dived well beyond 6,500 ft/min.
(b) Model reach: with the switches on, commanded rates to 20,000 ft/min and unloading to the declared floor are reachable. Free
dynamics already reach high rates through spirals (32 % > 6,500 ft/min) but cannot unload at low rates (architecture study).
(c) Proposal coverage: the push-over coincident with the bursts remains a sampling gap (eff. parents about 2). Status: open,
needs a targeted proposal. Bounds: rapid rate U[6,500, 20,000] ft/min (module choice, PROVISIONAL); floor 0 g (test value).

**Decision for Pete (options):** (A) keep off until the targeted sampler exists [recommended; no change in what is selected now];
(B) include in the control prior at a declared probability for the next announced sweep; (C) model the push-over timed to the
log-on (a pilot action at flame-out), which is a new prior hypothesis and needs a ruling.

- End of flight
