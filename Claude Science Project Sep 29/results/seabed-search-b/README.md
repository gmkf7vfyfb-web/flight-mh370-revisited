# The seabed searches on core (b): the pre-approved overnight re-run

10 October 2026, searched-areas module. **Every number here is UNCONVERGED** — see the labels.

Source: end of flight's sweep on core (b)'s 00:11 hand-offs,
`mh370-exchange/end-of-flight/next-run/`, released 08:36Z. Four strata, 4 seeds each,
**51,200,096 impacts**, 106 columns. Mixed by core's P(family) — free 0.69, Davey dynamics + radar
0.15, descent-climb 0.14, routes 0.01, as given (they sum to 0.99 and are renormalised to 1), held
fixed. 00:19 options under end of flight's `+alive` existence constraint. `impact-map-b-mixture.*`
is the mixture; `impact-map-b-<stratum>.*` are the four strata.

**Labels, required of every number here:** core (b) split-half NOT converged; two-tank bookkeeping
only; one-engine phase about half its true length (internal-v1's live-engine flow is twice its source
tables); PROVISIONAL-OVERNIGHT; the sweep was run by an architecture stand-in on end of flight's
behalf and is theirs to review; deskstar; track 289.7°; Inmarsat ephemeris; internal-v1 fuel.

## The mixture

| # | arm | Z | searches remove | median before → after | 90 % area before → after (km²) | mass on Phase 2 | ESS before → after | estimable |
|---|---|---|---|---|---|---|---|---|
| 1 | Held out — no 00:19 observation | **0.6883** | 31.2% | 37.24°S → 37.26°S | 430,138 → 533,063 | 0.347 → 0.055 | 44,034,132 → 31,649,305 | yes |
| 1a | R600 BTO arc only | **0.6713** | 32.9% | 37.93°S → 38.48°S | 258,236 → 308,944 | 0.366 → 0.059 | 28,007,636 → 19,631,885 | yes |
| 2 | R600 BTO + BFO as observed | **0.5070** | 49.3% | 37.43°S → 37.66°S | 184,631 → 247,833 | 0.549 → 0.117 | 1,073,678 → 617,816 | yes |
| 3 | **Holland H1** — start-up transient, fuel exhaustion | **0.4575** | 54.3% | 37.14°S → 37.50°S | 58,775 → 55,823 | 0.604 → 0.170 | 255 → 219 | **NO** |
| 4 | **Holland H2** — both BFOs raw, other cause | **0.3581** | 64.2% | 37.14°S → 37.15°S | 58,254 → 68,560 | 0.715 → 0.241 | 311 → 159 | **NO** |
|  | R1200 only, Holland offset | **0.3206** | 67.9% | 36.79°S → 35.44°S | 123,588 → 221,325 | 0.757 → 0.257 | 54,745 → 22,677 | yes |
|  | Both, inflated | **0.5769** | 42.3% | 37.37°S → 38.19°S | 116,143 → 124,363 | 0.471 → 0.088 | 8,872 → 5,229 | yes |

## The same arms per stratum, which is how much (b)'s non-convergence is worth

| arm | free (69 %) | Davey dyn. + radar (15 %) | descent-climb (14 %) | routes (1 %) | spread |
|---|---|---|---|---|---|
| Held out — no 00:19 observation | 0.6878 | 0.7115 | 0.6686 | 0.6497 | 0.0618 |
| R600 BTO arc only | 0.6697 | 0.6932 | 0.6577 | 0.6493 | 0.0439 |
| R600 BTO + BFO as observed | 0.5042 | 0.5279 | 0.4993 | 0.4948 | 0.0331 |
| **Holland H1** — start-up transient, fuel exhaustion | 0.4762 | 0.4014 | 0.4251 | 0.4588 | 0.0748 |
| **Holland H2** — both BFOs raw, other cause | 0.3521 | 0.3736 | 0.3675 | 0.4074 | 0.0554 |

## Reading

1. **The searches remove 31 % to 68 % of the probability**, depending entirely on how the 00:19
   transmissions are interpreted: 31.2 % with them held out, 49.3 % with the R600 burst at face value,
   67.9 % with the R1200 burst under Holland's start-up offset. On reference-289 under `+alive` the
   held-out figure was 27.9 %, so **(b) puts more of the impact distribution on searched ground** —
   0.347 against 0.311.
2. **The spread across strata is 0.03 to 0.07 in Z**, which is the price of (b)'s non-convergence and
   is larger than every one of this module's own sensitivities except ρ. The held-out arm runs from
   0.6497 (routes) to 0.7115 (Davey dynamics + radar). Until core converges, **the uncertainty in this
   module's headline is dominated by the source posterior, not by anything the module does.**
3. **Holland H1 and H2 are again NOT ESTIMABLE**, at 219 and 159 effective impacts of 51.2 × 10⁶.
   This was predicted from the run's own `run.json` before the sweep was consumed: end of flight now
   reports per-column ESS, and the free stratum's `both/no-offset` showed 8.3 effective parents. The
   new hand-offs did not move the wall, because it is posterior concentration at 00:11 rather than
   anything a terminal-stage proposal reaches.
4. **The widening holds.** Every estimable arm has a larger 90 % region after the search evidence than
   before: held out 430,138 → 533,063 km², R600 as observed 184,631 → 247,833, R1200 with Holland's
   offset 123,588 → 221,325. A non-detection removes a contiguous block from the middle of the corridor
   and leaves the ring.
5. **The BTO arc alone remains weak.** Row 1a narrows the 90 % region by a factor of 1.7 and the
   searches then remove 32.9 % — barely more than with the 00:19 data held out entirely.

## What is not here

- The ρ sweep and the Davey eq. (11.2) planning curve on (b): the reference versions are on
  reference-289 (`results/seabed-search-289-fullscale-alive/`). They need a per-stratum pass and a
  pooled one, and the machine was at load 24 with drift holding it, so they are the next thing to run.
- The field-coverage check over settling's wreckage samples for (b): settling's own re-run landed
  while this was being written and has not been read.
- Core's (a) variant. (b) is the base tonight by architecture's ruling; (a) moves the source 00:19
  median 0.26°, which is larger than several terms in this module's budget and is **not yet
  propagated**.
