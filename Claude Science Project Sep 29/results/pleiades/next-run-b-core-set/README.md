# Pléiades close-ups on core (b), in the ruled core set of 00:19 options

10 Oct 2026 ~16:10 UTC, Pléiades module. These use the names from architecture's ruling of ~16:30 UTC (Pete).
Labels: core (b) with the request-17 sampler fix in, split-half NOT converged; two-tank bookkeeping only;
internal-v1 fuel (its one-engine flow is 2x its tables); Inmarsat ephemeris; descent idle floor ON; EoF sweep run
by an architecture stand-in; PROVISIONAL-OVERNIGHT. Everything is conditional on H, with no Bayes factor.

All options use log-on cause "not fuel exhaustion" and end of flight's `alive` constraint (transmitting at 00:19:37).
Strata are mixed by core's P(family), held fixed. Panels: Pléiades with COSMO F1–F3, and with F1–F4, each after
Phase 2 + Bluefin-21 and after + OI 2018 + 2025-26 (grade C). Numbers: `closeup-stats-by-option.csv`.

| option | objects | search | 50 % km² | 90 % km² | mean | outside past searches | search leaves, under H |
|---|---|---|---|---|---|---|---|
| 00:19 Held Out | Pléiades + F1–F4 | + OI 2018 + 2025-26 | 9,747 | 71,951 | 35.25 S 91.41 E | 85.3 % | 0.557 |
| 00:19 R600 BTO Only | Pléiades + F1–F4 | + OI 2018 + 2025-26 | 12,669 | 53,544 | 35.78 S 92.20 E | 69.4 % | 0.341 |
| 00:19 R600 BTO + Raw BFO | Pléiades + F1–F4 | + OI 2018 + 2025-26 | 10,705 | 47,591 | 35.73 S 92.09 E | 65.2 % | 0.304 |
| 00:19 Holland H1 / H2 | — | — | not yet estimable: targeted sampler in progress (end of flight) | | | | |

**What changes.**
- Scoring the R600 BTO alone already moves the conditional mass south-east, toward the arc and Phase 2: the mean
  goes from 35.25 S 91.41 E to 35.78 S 92.20 E.
- Adding the raw R600 BFO changes little beyond that.
- So the shift with R600 comes mainly from its BTO, not its BFO.

`00:19 R600 BTO Only` is new here. End of flight derives it from the R600 BTO residual; it was not in the stand-in
run. It was computed through end of flight's own `option_posteriors` (read-only), per stratum, using the stand-in's
per-impact search columns.

— Pléiades
