# Pléiades module review of the stand-in re-run on core (b), with close-ups for every headline option

10 Oct 2026 ~16:00 UTC, Pléiades module. Labels: **core (b): request-17 sampler fix in, split-half NOT converged** ·
**two-tank bookkeeping only** · **internal-v1 fuel (its one-engine flow is 2× its tables)** · Inmarsat ephemeris ·
descent idle floor ON · **EoF sweep and the per-stratum branch run by architecture stand-ins** · **PROVISIONAL-OVERNIGHT**.
Everything is conditional on H: the Pléiades objects (and, where shown, the COSMO-SkyMed contacts) are debris from
9M-MRO. There is no Bayes factor and no P(H | data).

## Review of `results/pleiades-next-run-b-standin.md`

**I agree with the stand-in's run and its reading.** The code is the module's own (`rerun_next.py` at `ed85311`),
and the inputs are the module's surfaces. My close-ups below reproduce its mixture numbers exactly, for example P+C3 after
Phase 2 + Bluefin-21 with the 00:19 data held out: 90 % area 52,145 km², share retained 0.702.

Three points on top of the stand-in's note:
1. **How the strata are mixed (checked, correct).** The stand-in mixes each stratum's flight posterior, normalised
   to one, by core's P(family). The after-search map keeps that stratum's search evidence, so the search re-weights
   the strata by itself. The conditional under H is then computed on the mixed flight posterior, not by averaging
   the per-stratum conditionals, which would be wrong. **One shared convention to note:** P(family) is fixed before
   any 00:19 option is scored, so the 00:19 data do not re-weight the families. End of flight and searched areas
   do the same. Under R600 or R1200 the families' 00:19 evidence differs, so this is a modelling choice, now
   declared in every footnote. I am raising it with architecture rather than changing it alone.
2. **The R600 and R1200 maps are noisy** (fragmented 50 % contours in the close-ups). These options keep far fewer
   effective impacts, and the strata are unconverged. Treat their 50 % shapes as sampling noise, not structure.
3. **Adopted into module code:** the stand-in's mixture method is now in `prepare/option_closeups.py`. `rerun_next.py`
   now handles strata itself (`--pfamily`) and always draws the close-ups.

## What the option names mean (used on every chart from now on)

- **00:19 data held out** (`none`): neither 00:19 satellite message is used to score the impacts.
- **Airborne at 00:19:37** (`+alive`): end of flight's constraint that the aircraft was still flying when it sent its
  last message (the R1200 acknowledge at 00:19:37.443). It removes impacts before that time. It is end of flight's
  provisional reference.
- **R600 as observed** (`r600/no-offset`): the 00:19:29 log-on request's BTO and BFO are used raw; the 00:19:37
  message is not used.
- **R1200, inflated BFO error** (`r1200/inflated`): the 00:19:37 message is used with an inflated, zero-mean BFO error;
  R600 is not used.
- **COSMO F1–F3 / F1–F4** (`C3` / `C4`): the COSMO-SkyMed radar contacts F1–F3, and the same set with F4 added
  (F4 is the westernmost, near 35.4 S 90.0 E).
- **"One debris field"** (`P+C`): the Pléiades and COSMO likelihoods multiplied, i.e. both sets of objects came from
  the same impact.

## Close-ups (`closeup-<option>.png/.pdf`; table `closeup-stats-by-option.csv`)

| 00:19 treatment | objects | search | 50 % area km² | 90 % area km² | mean | in NW band | outside past searches | search leaves, under H | search leaves, flight only |
|---|---|---|---|---|---|---|---|---|---|
| 00:19 data held out; airborne at 00:19:37 | Pléiades + COSMO F1–F3 | Phase 2 + Bluefin-21 | 9,370 | 61,164 | 35.21 S 91.70 E | 4.0 % | 70.0 % | 0.633 | 0.684 |
| 00:19 data held out; airborne at 00:19:37 | Pléiades + COSMO F1–F4 | Phase 2 + Bluefin-21 | 10,177 | 69,379 | 35.23 S 91.53 E | 3.4 % | 72.8 % | 0.656 | 0.684 |
| 00:19 data held out; airborne at 00:19:37 | Pléiades + COSMO F1–F3 | + OI 2018 + 2025-26 (grade C) | 8,635 | 64,744 | 35.23 S 91.58 E | 4.7 % | 83.5 % | 0.528 | 0.650 |
| 00:19 data held out; airborne at 00:19:37 | Pléiades + COSMO F1–F4 | + OI 2018 + 2025-26 (grade C) | 9,747 | 71,951 | 35.25 S 91.41 E | 3.9 % | 85.3 % | 0.557 | 0.650 |
| 00:19 data held out | Pléiades + COSMO F1–F3 | Phase 2 + Bluefin-21 | 5,911 | 52,145 | 35.18 S 91.66 E | 5.4 % | 73.8 % | 0.702 | 0.698 |
| 00:19 data held out | Pléiades + COSMO F1–F4 | Phase 2 + Bluefin-21 | 6,390 | 59,823 | 35.21 S 91.51 E | 4.7 % | 75.8 % | 0.721 | 0.698 |
| 00:19 data held out | Pléiades + COSMO F1–F3 | + OI 2018 + 2025-26 (grade C) | 4,699 | 54,480 | 35.19 S 91.55 E | 6.3 % | 86.7 % | 0.594 | 0.660 |
| 00:19 data held out | Pléiades + COSMO F1–F4 | + OI 2018 + 2025-26 (grade C) | 5,381 | 61,969 | 35.22 S 91.40 E | 5.4 % | 87.9 % | 0.618 | 0.660 |
| 00:19:29 request (R600) as observed | Pléiades + COSMO F1–F3 | Phase 2 + Bluefin-21 | 11,947 | 42,605 | 35.64 S 92.29 E | 1.2 % | 52.8 % | 0.353 | 0.504 |
| 00:19:29 request (R600) as observed | Pléiades + COSMO F1–F4 | Phase 2 + Bluefin-21 | 12,274 | 46,854 | 35.66 S 92.18 E | 1.1 % | 55.0 % | 0.362 | 0.504 |
| 00:19:29 request (R600) as observed | Pléiades + COSMO F1–F3 | + OI 2018 + 2025-26 (grade C) | 10,328 | 42,548 | 35.72 S 92.21 E | 1.4 % | 63.3 % | 0.293 | 0.463 |
| 00:19:29 request (R600) as observed | Pléiades + COSMO F1–F4 | + OI 2018 + 2025-26 (grade C) | 10,705 | 47,566 | 35.73 S 92.09 E | 1.3 % | 65.2 % | 0.303 | 0.463 |
| 00:19:37 acknowledge (R1200), inflated BFO error | Pléiades + COSMO F1–F3 | Phase 2 + Bluefin-21 | 4,698 | 22,817 | 35.12 S 91.72 E | 4.5 % | 51.3 % | 0.540 | 0.421 |
| 00:19:37 acknowledge (R1200), inflated BFO error | Pléiades + COSMO F1–F4 | Phase 2 + Bluefin-21 | 4,696 | 25,118 | 35.16 S 91.64 E | 4.0 % | 53.1 % | 0.554 | 0.421 |
| 00:19:37 acknowledge (R1200), inflated BFO error | Pléiades + COSMO F1–F3 | + OI 2018 + 2025-26 (grade C) | 4,547 | 26,738 | 35.14 S 91.58 E | 6.2 % | 71.4 % | 0.384 | 0.326 |
| 00:19:37 acknowledge (R1200), inflated BFO error | Pléiades + COSMO F1–F4 | + OI 2018 + 2025-26 (grade C) | 4,647 | 30,371 | 35.18 S 91.50 E | 5.5 % | 72.9 % | 0.399 | 0.326 |
| R600, inflated BFO error | Pléiades + COSMO F1–F3 | Phase 2 + Bluefin-21 | 13,530 | 46,711 | 35.72 S 92.38 E | 1.1 % | 56.9 % | 0.394 | 0.633 |
| R600, inflated BFO error | Pléiades + COSMO F1–F4 | Phase 2 + Bluefin-21 | 13,835 | 51,038 | 35.72 S 92.28 E | 1.0 % | 58.6 % | 0.401 | 0.633 |
| R600, inflated BFO error | Pléiades + COSMO F1–F3 | + OI 2018 + 2025-26 (grade C) | 11,835 | 46,694 | 35.80 S 92.31 E | 1.2 % | 67.8 % | 0.329 | 0.607 |
| R600, inflated BFO error | Pléiades + COSMO F1–F4 | + OI 2018 + 2025-26 (grade C) | 12,136 | 51,841 | 35.80 S 92.20 E | 1.1 % | 69.1 % | 0.338 | 0.607 |

**Reading.**
- **The core under H is close to where it was on reference-289 when the 00:19 data are held out.** P+C4 with every
  search layer has its mean at 35.22 S 91.40 E, against 35.22 S 91.43 E on reference-289, and 88 % of its mass lies
  outside past searches.
- **With R600 scored, the mass moves south-east toward the arc and Phase 2.** The mean is about 35.65–35.80 S,
  92.1–92.4 E. The searches then remove most of it: they leave 0.29–0.40 under H.
- **R1200 gives the tightest conditional** (90 % area 23,000–30,000 km²). Its HDR sits on and just inside the OI
  north-west band, with 4–6 % of the mass in the band itself.
- In every option, only 1–6 % of the conditional mass lies in the inferred north-west band.

— Pléiades
