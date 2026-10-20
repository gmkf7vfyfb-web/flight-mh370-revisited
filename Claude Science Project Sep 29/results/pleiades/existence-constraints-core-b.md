# Pléiades conditional on core (b): the three existence constraints after 00:19

10 Oct 2026, Pléiades module. **Labels:** core (b) request-17 sampler fix IN, split-half NOT converged; two-tank bookkeeping only;
internal-v1 fuel; EoF sweep by an architecture stand-in (`3c6319f`); PROVISIONAL-OVERNIGHT.

**Ruling ~19:10 UTC B:**
- (b) `unpowered` is the reference: airborne at 00:19:37 and not powered at 01:15:56, the two observed facts.
- (a) `alive` was used until end of flight exposed (b).
- (c) `silent` adds end of flight's "no further APU log-on" factor under `other`. It is shown beside (b) as a declared variant.

**Common to every row:**
- Pléiades rating-5 objects + all four COSMO-SkyMed contacts, one debris field, after Phase 2 + Bluefin-21 + OI 2018 + OI 2025-26
  south-east band (OI layers grade C).
- GLORYS12 + ERA5 and GlobCurrent daily + ERA5 at equal weight; measured transport error.
- Strata re-weighted by the 00:19 evidence (ruling C) through end of flight's `+alive` key. For (b), the 01:15:56 factor acts within strata
  only, as in ocean settling. For (c), weights are fixed: end of flight publishes no `+silent` factors.
- **Tension** is the module's measure (`rerun_reference.tension`): ln S, Handley-Lemos p, mean shift of the impact PDF without H → under H,
  and the share of the impact PDF without H that lies inside the 90 % region under H. It is always reported with the conditional.

| 00:19 option | existence constraint | strata | 50 % km² | 90 % km² | mean under H | searches leave, under H | ln S | p | mean shift NM | flight PDF in 90 % under H |
|---|---|---|---|---|---|---|---|---|---|---|
| 00:19 Held Out | alive (a) | reweighted-0019 | 9,747 | 71,951 | 35.25 S 91.41 E | 0.557 | +0.18 | 0.45 | 97 | 15 % |
| 00:19 R600 BTO Only | alive (a) | reweighted-0019 | 12,668 | 53,595 | 35.78 S 92.19 E | 0.341 | -1.44 | 0.16 | 137 | 7 % |
| 00:19 R600 BTO + Raw BFO | alive (a) | reweighted-0019 | 10,730 | 47,744 | 35.73 S 92.09 E | 0.303 | -1.12 | 0.20 | 92 | 11 % |
| 00:19 Held Out | unpowered (b), reference | reweighted-0019 | 9,747 | 71,925 | 35.25 S 91.41 E | 0.557 | +0.18 | 0.45 | 97 | 15 % |
| 00:19 R600 BTO Only | unpowered (b), reference | reweighted-0019 | 12,668 | 53,594 | 35.78 S 92.19 E | 0.341 | -1.44 | 0.16 | 137 | 7 % |
| 00:19 R600 BTO + Raw BFO | unpowered (b), reference | reweighted-0019 | 10,730 | 47,744 | 35.73 S 92.09 E | 0.303 | -1.12 | 0.20 | 92 | 11 % |
| 00:19 Held Out, no further APU log-on before impact (declared variant) | silent (c), declared | fixed | 6,772 | 62,121 | 35.17 S 91.40 E | 0.560 | +1.11 | 1.00 | 21 | 32 % |
| 00:19 R600 BTO Only, no further APU log-on before impact (declared variant) | silent (c), declared | fixed | 10,882 | 47,575 | 35.73 S 92.27 E | 0.249 | -0.23 | 0.33 | 40 | 14 % |
| 00:19 R600 BTO + Raw BFO, no further APU log-on before impact (declared variant) | silent (c), declared | fixed | 6,540 | 34,033 | 35.56 S 92.13 E | 0.183 | +0.28 | 0.49 | 26 | 20 % |

## Findings
1. **(b) `unpowered` equals (a) `alive` to within 26 km².** The impacts after 01:15:56 are 0.06-0.30 % (end of flight). Switching the
   reference to (b), as ruled, changes nothing in this module. Results from here on use (b).
2. **(c) `silent` narrows the conditional strongly, and the tension falls with it.**
   - R600 BTO + Raw BFO: the 90 % area goes from 47,744 to 34,033 km², the mean moves 0.16° north, and the mean shift falls from 92 to 26 NM.
   - In this case the narrower conditional is NOT a symptom of tension. `silent` removes the later, southern impacts from the flight PDF
     itself, which then agrees more closely with the drift-back region.
   - The term is strong and model-dependent: it removes 44-90 % of the `other` weight, through end of flight's log-on lag model. It stays a
     declared variant until end of flight documents that model and Pete agrees (ruling B (c)).
3. **The searches leave less under (c):** 0.18-0.25 for the R600 options, against 0.30-0.34 under (b). More of the conditional lies
   inside past searches.
4. All rows come from core (b), which is not converged. Run C will replace them.

Close-ups: `next-run-b-unpowered/closeups/`, `next-run-b-silent/closeups/` (colour + seabed, faint points); stats in each `closeup-stats.csv`.
