# Item 2, round 3 — speed-tracking pitch law and state-dependent turn direction: design fixed BEFORE fitting

Pete's decision (14 Oct 2026, after round 2 failed with an out-of-sample improvement): round 3 with a speed-tracking pitch law, the turn
direction made state-dependent, pre-registered as round 2 was. Written before any round-3 fit. **Declared: this is the third fit to the same
ten cases; each round weakens the out-of-sample claim, and the note will say so beside every round-3 number.**

## Unchanged from round 2
Targets, tolerances (σ = tolerance/2), features and measurement code, the gate rule, initial conditions from the traces, the 4 Sobol
draws, the bank grid, the round-1 declared choices, no per-case nuisance; and from round 2: the dive trigger on EAS at the loss (e0, s)
and the fitted bank cap.

## Changes
1. **Lift-speed exponent n and path-angle damping k are REMOVED**, replaced by a lagged lift law. In free flight the lift relaxes towards
   L_t = L_ref [1 + g (q/q_ref − 1)] with time constant τ (exact exponential update per command step), where L_ref and q_ref are the
   trim lift and dynamic pressure at the start of free flight. g = 1, τ = 0 is the round-1 model exactly. Motivation, checked BEFORE
   fitting on a constant-density phugoid (no Boeing data): τ ≈ 10 s at g = 1 lengthens the period from Lanchester's 68 s to about 86 s
   at 150 m/s and brings the damping ratio near 0, the Boeing glide signature; a speed-exponent and a damping term could not do both.
   Bounds: τ [0, 30] s, g [0.3, 1.5].
2. **Turn direction depends on the propulsion state at the loss.** Boeing (Malaysian SIR App. 1.6E p. 8): the right engine runs dry first,
   TAC applies left rudder, and after the second flame-out about 0.2° of left rudder remains, so the aircraft rolls slowly left. Where
   control is lost during the asymmetry (one engine still thrusting, i.e. within the first seconds after the first flame-out), the
   aircraft instead yaws towards the dead engine. So: P(left) = p_sym when the loss comes with no engine thrusting; P(towards the dead
   engine) = p_dead when one is. Case covariate: loss within 2 s of the first flame-out (sim/boeing_events.py: cases 4, 6, 10; case 3's
   loss is 9 s after the first flame-out, at the second). Bounds both [0.02, 0.98].

## Parameter budget: 12 shared against 62 case-targets
spiral_doubling_s, trim_cl_offset, windmilling_per_engine, rat_increment, spiral_bank_cap_deg, τ, g (deterministic); residual_bank_deg
upper bound, p_sym, p_dead, e0, s (population). Bounds otherwise as round 2.

## Not addressed, declared
Case 5's late dive (a trigger on the state at the loss cannot see it).
— End of Flight Module
