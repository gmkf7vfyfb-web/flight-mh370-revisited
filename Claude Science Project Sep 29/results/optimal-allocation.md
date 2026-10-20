# How many particles each mode should get, measured rather than argued

`6temper-realloc` copied the allocation that the fuel-free runs converge under. It worked, but
copying is not deriving. Two runs now exist with the same model and different per-mode particle
counts, which is enough to measure how each mode's sampling error responds to its own particle
count and then solve for the allocation that minimises the total.

Allocation is a **stratified sampling design**, not a prior: `summary.rs` computes
`P(mode) = prior[m] × mean_replicates(Z[m]) / Σ`, where `prior[m]` is Davey's uniform 1/5 and
`Z[m]` is the mode's marginal likelihood estimated inside its own stratum. The particle count
appears nowhere in the target, only in the precision of `Z[m]`. The empirical check agrees:
raising true track from 1.4M to 2.5M, a 79% increase, moved its posterior probability from 0.5809
to 0.5890, 1.4%, well inside its own 6.8% half-to-half noise.

## The measurement

For each mode, the within-mode conditional density was formed per replicate, pooled over every
balanced half, and the mean absolute difference between halves taken as that mode's sampling
error. Fitting `error = c · n^−p` through the two available points:

| mode | n (M) | error | n (M) | error | fitted p | theoretical |
|---|---|---|---|---|---|---|
| true track | 1.4 | 0.4395 | 2.5 | 0.3386 | **0.450** | 0.5 |
| magnetic heading | 1.4 | 0.1418 | 0.5 | 0.2453 | **0.532** | 0.5 |
| magnetic track | 1.4 | 0.1696 | 0.5 | 0.2576 | **0.406** | 0.5 |
| true heading | 1.4 | 0.1228 | 1.0 | 0.1256 | 0.065 | 0.5 |
| lateral navigation | 1.4 | 0.4751 | 2.5 | 0.4563 | **0.069** | 0.5 |

Three modes scale as Monte Carlo theory says they should. Two do not, and the two are the ones
that matter most for how to spend the next 7M particles.

**Lateral navigation barely responds to particle count.** Going from 1.4M to 2.5M — 79% more
particles — reduced its error by 4%. At the theoretical exponent it should have fallen to 0.3555;
it measured 0.4563. That is far outside what the measurement noise can explain, so the weak
scaling is real.

**True heading's exponent is not determined.** Its particle count changed by only 1.4M → 1.0M, so
two points that close together cannot fit an exponent. Treat 0.065 as unmeasured, not as weak.

The cause of lateral navigation's behaviour is **not established**, and the obvious candidate does
not survive a look. If its conditional density were a mixture over a few discrete geometries whose
weights are evidence-estimated, particles would not help. But it has three peaks above 2% of its
maximum, the same count as true track; it is simply broader — participation ratio 69.8 bins
against true track's 46.2, within-mode standard deviation 1.35° against 0.80°. Its distinct
surviving draws also nearly doubled, 929–1017 → 1673–1835, so the origin pool did scale even
though the error did not. Something else sets the floor, and this note does not know what.

## The optimisation

Minimising the posterior-weighted sum of conditional-density errors, `Σ P_m c_m n_m^−p_m`, at
fixed total:

| allocation | TH | MH | TT | MT | LNAV | predicted error | vs current |
|---|---|---|---|---|---|---|---|
| equal (`best-model`) | 1.4 | 1.4 | 1.4 | 1.4 | 1.4 | 0.4002 | +17.2% |
| current (`6temper-realloc`) | 1.0 | 0.5 | 2.5 | 0.5 | 2.5 | 0.3415 | — |
| **moderate step** | 0.6 | 0.3 | 4.0 | 0.4 | 1.7 | 0.3091 | **−9.5%** |
| aggressive | 0.4 | 0.25 | 5.0 | 0.35 | 1.0 | 0.2995 | −12.3% |
| unconstrained optimum | 0.25 | 0.25 | 5.35 | 0.42 | 0.73 | 0.2973 | −13.0% |

The objective reproduces what was already observed — equal allocation is 17% worse than the
current one — which is the only validation available for it, and it is a weak one, since the same
two runs supplied the exponents.

## Recommendation: the moderate step, and why not the optimum

The unconstrained optimum says to put 5.35M of 7M into true track and strip lateral navigation to
0.73M. Three reasons not to do that yet.

1. **It extrapolates 2.1× beyond the measured range.** True track has been run at 1.4M and 2.5M.
   The optimum assumes the 0.450 exponent holds to 5.35M.
2. **The objective omits the mode-probability term.** It minimises the error of the conditional
   densities only. `P(mode)` is estimated from each stratum's own evidence, and those estimates
   are the quantity already furthest from converged — 6.8% to 12.9% half-to-half, worse than any
   other reported number. Stripping true heading from 1.0M to 0.25M would make its contribution
   worse, and nothing in this objective notices.
3. **It bets the whole allocation on the one exponent that is both load-bearing and unexplained.**
   Everything that distinguishes the optimum from the current allocation follows from lateral
   navigation's 0.069.

The moderate step banks 9.5% of the available 13% while keeping lateral navigation at 1.7M, which
sits between the two measured points and therefore **supplies a third point on the curve that the
optimisation most needs**. It is simultaneously the conservative choice and the informative one.
If 1.7M confirms the weak exponent, the aggressive allocation is justified on three points instead
of two; if it does not, the optimum was an artefact and nothing was lost.

Floors: no stratum below 0.25M, so the shoulder stays estimable and `P(mode)` stays defined for
every mode. That constraint is what keeps the optimum from collapsing onto a single stratum.
