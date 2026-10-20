# Does the 00:19 evidence re-weight the families enough to matter here?

10 October 2026, searched-areas module, answering architecture's ruling C of ~19:10 UTC. Run: core (b)
through end of flight's sweep, four strata × 4 seeds, 51,200,096 impacts. **Unconverged throughout.**

Ruling C is that the strata must be mixed with
`P(family | all data, option) ∝ P0(family) × Z_core(family) × Ẑ_00:19(family, option)` rather than with
core's P(family) held fixed. End of flight's `run.json` already carries `log_evidence_increment` per
option column per seed, which is Ẑ_00:19 per family per option, so this is computable now.

## The 00:19 evidence does move the families

Posterior P(family) per option, against core's fixed 0.697 / 0.152 / 0.141 / 0.010 (the published
0.69 / 0.15 / 0.14 / 0.01 renormalised):

| 00:19 option | free | Davey dynamics + radar | descent-climb | routes |
|---|---|---|---|---|
| Held Out | 0.6970 | 0.1515 | 0.1414 | 0.0101 |
| R600 BTO + Raw BFO | 0.6563 | 0.1163 | **0.2171** | 0.0104 |
| R600, start-up offset | 0.6226 | 0.1177 | **0.2497** | 0.0101 |
| R1200, start-up offset | 0.6915 | 0.1433 | 0.1539 | 0.0113 |
| Both bursts, inflated | 0.6767 | 0.1346 | 0.1782 | 0.0105 |
| Holland H2 | 0.6510 | 0.1309 | 0.2079 | 0.0102 |
| Holland H1 | 0.6070 | 0.1063 | **0.2786** | 0.0082 |

Held Out is unchanged to four decimals, which is the check that the implementation is right: that
option scores no 00:19 value, so its evidence factor is 1 by construction. **Every option that uses a
00:19 value moves weight towards the descent-climb family**, which roughly doubles under the
start-up-offset arms, and away from free and from Davey dynamics + radar.

## But it barely moves the searched-areas evidence

| 00:19 option | Z, fixed weights | Z, re-weighted | shift | searches remove |
|---|---|---|---|---|
| Held Out | 0.6883 | 0.6883 | 0.0000 | 31.2 % |
| R600 BTO Only | 0.6713 | 0.6713 | — | 32.9 % |
| R600 BTO + Raw BFO | 0.5070 | 0.5058 | −0.0012 | 49.3 → 49.4 % |
| R600, start-up offset | 0.4890 | 0.4797 | **−0.0093** | 51.1 → 52.0 % |
| R1200, start-up offset | 0.3206 | 0.3194 | −0.0012 | 67.9 → 68.1 % |
| Both bursts, inflated | 0.5769 | 0.5756 | −0.0012 | 42.3 → 42.4 % |

**The largest shift is 0.0093, and the typical one is 0.0012.** The reason is visible in the
per-stratum table of `README.md`: the four families disagree about where the aircraft went, but they
agree closely about *what fraction of that probability sits on searched ground* — the held-out Z runs
only from 0.6497 to 0.7115 across them. Re-weighting families that agree on the quantity being
integrated cannot move the integral much.

So for this module ruling C is **correct and worth applying, and almost inconsequential**: its effect is
an order of magnitude below the 0.03–0.07 spread that (b)'s non-convergence already contributes, and
two orders below ρ. It will matter more to a module whose quantity differs strongly between families.

## Limits of this calculation

- **The log-on-cause factor is not included.** Ẑ_00:19 here is the option-level evidence increment.
  Arms under the fuel-exhaustion cause also carry the §6 log-on lag density, which end of flight has
  not published per family. The `other`-cause rows (Held Out, R600 BTO + Raw BFO, R600 start-up offset,
  Holland H2) are therefore exact; the fuel-exhaustion rows are approximate in the weights, though the
  shift is small enough that this cannot change the conclusion.
- **Holland H1 and H2 are shown for completeness only.** Ruling C excludes them until they are
  estimable, and at 255 and 311 effective impacts they are not.
- Both mixtures are reported, as the ruling requires while core is unconverged. The charts use the
  fixed weights, with this note as the declared alternative.
