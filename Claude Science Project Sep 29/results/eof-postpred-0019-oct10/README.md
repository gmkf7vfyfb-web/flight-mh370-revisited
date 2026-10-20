# End of flight: are the two 00:19 BFOs consistent with the trajectories the other evidence selects? (posterior-predictive check, core (b), 10 Oct 2026)

**Why this check.** Pete asked which 00:19 options the evidence favours, or whether it is indeterminate, when we sample over the feasible
space.
- **Options that use different data cannot be ranked by a Bayes factor:** Held Out, R600 BTO Only and R600 BTO + Raw BFO.
- Instead, each observation is checked against the trajectories selected **without** it, the standard posterior-predictive check.
- It is the companion of the Bayes factors between models of the **same** data (H1 against H2, raw against inflated noise), which are
  reported elsewhere.

**Inputs and labels:**
- Inputs: `end-of-flight/next-run/<stratum>/seed-1..4` (the accepted stand-in sweep on core (b)) and core's `handoff.npy` (bias variance);
  code `smoke/postpred_0019.py`.
- Labels: core (b) split-half NOT converged; two-tank bookkeeping only; idle floor ON; dive class (b) PROVISIONAL; trim from the takeover
  state (current base); point-mass free dynamics that cannot unload (smoke 3).

**Statistic.**
- For each row, the predictive density of the burst's BFO, f, comes from the selected trajectory's predicted BFO, the hand-off bias
  (variance 5.4 Hz²) and the BFO model's noise and offsets.
- For R1200 the shared bias, and Holland's offsets, are first updated by the observed R600 BFO, exactly as the terminal stage does.
- **p = P(f(replicate) ≤ f(observed))**, averaged over the posterior (one replicate per row). A small p means the observation lies in the tail
  of what the selected trajectories predict.

| core family | BFO model | p(R600 BFO = 182 Hz \| data to 00:11 + R600 BTO): mean (range over 4 seeds) | p(R1200 BFO = −2 Hz \| data to 00:11 + R600 BTO + R600 BFO) |
|---|---|---|---|
| free | no offset, σ 7 Hz | 0.013 (0.010-0.015) | 1.4e-04 (1e-04-2e-04) |
| free | inflated noise, σ 34 Hz | 0.128 (0.102-0.153) | 4.3e-04 (3e-04-5e-04) |
| free | Holland start-up offset | 0.010 (0.008-0.011) | 6.4e-04 (5e-04-7e-04) |
| Davey dynamics + radar | no offset, σ 7 Hz | 0.014 (0.013-0.015) | 1.1e-04 (8e-05-1e-04) |
| Davey dynamics + radar | inflated noise, σ 34 Hz | 0.133 (0.124-0.140) | 4.8e-04 (4e-04-7e-04) |
| Davey dynamics + radar | Holland start-up offset | 0.012 (0.010-0.013) | 5.1e-04 (4e-04-6e-04) |
| descent-climb | no offset, σ 7 Hz | 0.020 (0.013-0.030) | 1.3e-04 (7e-05-3e-04) |
| descent-climb | inflated noise, σ 34 Hz | 0.148 (0.128-0.169) | 4.4e-04 (3e-04-5e-04) |
| descent-climb | Holland start-up offset | 0.013 (0.009-0.020) | 5.9e-04 (5e-04-8e-04) |
| routes | no offset, σ 7 Hz | 0.015 (0.013-0.021) | 1.3e-04 (4e-05-2e-04) |
| routes | inflated noise, σ 34 Hz | 0.135 (0.115-0.183) | 4.5e-04 (3e-04-5e-04) |
| routes | Holland start-up offset | 0.011 (0.010-0.011) | 4.9e-04 (3e-04-7e-04) |

**Reading.**
- **The R600 BFO is in the 1-3 % tail** of what the trajectories selected without it predict, under the nominal 7 Hz noise; 10-18 % under the
  inflated 34 Hz noise.
  - The cause: most selected trajectories are in level or gently descending flight at 00:19:29. 182 Hz needs a descent of about 4,500 ft/min
    at that moment (Holland Table VI).
  - That is tension, not an anomaly.
- **The R1200 BFO, given the R600, is at the 1e-4 tail under every BFO model** (0.4-7.6 × 10⁻⁴). It needs the ~0.6 g push-over in 8 s.
- **This does not yet say the R1200 is physically anomalous.**
  - The diagnostic smokes and the architecture study show that our current feasible space under-produces exactly this manoeuvre. The point
    mass cannot unload; there is no Boeing system sequence and no controlled push-over.
  - Boeing's no-input simulator met H2's bounds in 3 of 10 cases.
  - So today's 1e-4 is a statement about **our model's feasible space**. It will be re-measured when the 6-DOF dynamics pass the gate (ruling
    item 1).
- **Consistency across the four core families and 16 seeds is good** (the ranges above). The check is not limited by the core's
  non-convergence.
- Monte Carlo error: about ±4e-5 on the R1200 p (binomial, from the ESS of the R600 posteriors: 46,000-85,000 effective rows per seed) and ≤ ±0.002 on the R600 p.

- End of flight
