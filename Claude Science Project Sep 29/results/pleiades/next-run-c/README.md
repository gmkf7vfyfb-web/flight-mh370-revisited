# Pléiades conditional on core run C (11 Oct 2026), Pléiades module

**Labels (every number):**
- Core run C is **split-half NOT converged** (floor 0.924: free 0.918, Davey dynamics + radar 0.910, descent-climb 0.892, routes 0.850).
- End-of-flight physics PROVISIONAL: descents above 6,500 ft/min and unloading not reachable; no structural limit (G13).
- Pléiades/COSMO transport errors independent (ρ = 0; ρ sensitivity in `../next-run-b-unpowered/rho-sensitivity/`); GlobCurrent windage as
  run (drift audit F1); Holland H1/H2 not estimable and not run.
- Wide Pléiades grid 78-115 E, 45-5 S (not computed ≤ 1e-4 of weight). Strata mixed by end of flight's re-weighted P(family)
  (`family-evidence-run-c.json`, exact keys), fixed beside them in `closeups/closeup-stats.csv`.
- Conditional on H; no identity likelihood, no Bayes factor or P(H | D).

**Common to every row:** after Phase 2 + Bluefin-21 + OI 2018 + 2025-26 (OI layers grade C), Pléiades + all four COSMO-SkyMed contacts,
one debris field, both ocean models at equal weight. ± is the split-half σ (rms over three 4 + 4 seed partitions; `splithalf.csv`).

| 00:19 option | version | 50 % km² | 90 % km² | 90 % km², GLORYS12 only | mean under H | outside past searches | searches leave, under H | tension ln S (p) | mean shift NM | flight PDF in 90 % under H |
|---|---|---|---|---|---|---|---|---|---|---|
| 00:19 Held Out | reference (b) unpowered, all rows | 15,734 | 82,614 ± 315 | 67,914 | 35.37 S 91.62 E | 81.1 % | 0.493 | -0.57 (p 0.28) | 81 | 11 % |
| 00:19 Held Out | impacts > 212 m/s removed | 15,759 | 82,792 ± 465 | 68,092 | 35.37 S 91.62 E | 81.2 % | 0.496 | -0.58 (p 0.28) | 81 | 11 % |
| 00:19 Held Out | declared (c) silent | 14,593 | 71,286 | 56,828 | 35.48 S 91.81 E | 76.2 % | 0.428 | -0.21 (p 0.35) | 46 | 15 % |
| 00:19 Held Out | silent, > 212 m/s removed | 14,716 | 71,502 | 57,002 | 35.48 S 91.82 E | 76.1 % | 0.428 | -0.24 (p 0.34) | 47 | 15 % |
| 00:19 R600 BTO Only | reference (b) unpowered, all rows | 9,794 | 45,709 ± 270 | 32,252 | 35.93 S 92.40 E | 72.8 % | 0.387 | -1.36 (p 0.14) | 102 | 7 % |
| 00:19 R600 BTO Only | impacts > 212 m/s removed | 9,819 | 45,885 ± 391 | 32,378 | 35.93 S 92.40 E | 73.1 % | 0.390 | -1.38 (p 0.14) | 102 | 7 % |
| 00:19 R600 BTO Only | declared (c) silent | 7,960 | 32,009 | 23,424 | 35.98 S 92.55 E | 65.0 % | 0.309 | -0.75 (p 0.23) | 59 | 11 % |
| 00:19 R600 BTO Only | silent, > 212 m/s removed | 8,009 | 32,232 | 23,548 | 35.98 S 92.55 E | 65.2 % | 0.312 | -0.78 (p 0.22) | 59 | 11 % |
| 00:19 R600 BTO + Raw BFO | reference (b) unpowered, all rows | 7,614 | 37,887 ± 222 | 28,478 | 35.90 S 92.36 E | 68.3 % | 0.351 | -0.49 (p 0.26) | 41 | 15 % |
| 00:19 R600 BTO + Raw BFO | impacts > 212 m/s removed | 7,511 | 37,886 ± 236 | 28,402 | 35.90 S 92.36 E | 68.9 % | 0.358 | -0.50 (p 0.26) | 41 | 15 % |
| 00:19 R600 BTO + Raw BFO | declared (c) silent | 6,364 | 26,014 | 22,460 | 35.84 S 92.48 E | 52.6 % | 0.238 | +0.20 (p 0.46) | 10 | 23 % |
| 00:19 R600 BTO + Raw BFO | silent, > 212 m/s removed | 6,412 | 26,215 | 22,561 | 35.84 S 92.48 E | 52.7 % | 0.239 | +0.18 (p 0.45) | 11 | 23 % |

**Against core (b)** (`unpowered`, re-weighted strata, 90 % region under H; core (b) on the 85-103 E grid):

| 00:19 option | core (b) km² | run C km² | core (b) mean | run C mean | mean shift NM, (b) → C |
|---|---|---|---|---|---|
| 00:19 Held Out | 71,925 | 82,614 | 35.25 S 91.41 E | 35.37 S 91.62 E | 97 → 81 |
| 00:19 R600 BTO Only | 53,594 | 45,709 | 35.78 S 92.19 E | 35.93 S 92.40 E | 137 → 102 |
| 00:19 R600 BTO + Raw BFO | 47,744 | 37,887 | 35.73 S 92.09 E | 35.90 S 92.36 E | 92 → 41 |

## Findings
1. **On run C the conditional is narrower and lies further south-east than on core (b).** R600 BTO + Raw BFO goes from 47,744 to
   37,887 km², and the mean moves 0.17° south and 0.27° east, to 35.90 S 92.36 E. Its 50 % region is now about one lobe at 35.6-36.8 S,
   92.0-93.1 E, over the Phase 2 / OI 2018 boundary. The northern lobe near the objects has faded.
2. **The tension falls on run C** for the R600 options: the mean shift drops from 92 to 41 NM for BTO + Raw BFO, and from 137 to
   102 NM for BTO Only. The flight posterior itself has moved towards the drift-back region. So the narrower conditional is not a symptom
   of more tension.
3. **The searches leave 0.35-0.39 under H for the R600 options, and 68-73 % of the conditional lies outside past searches.**
4. **Monte Carlo noise in this module is small:** σ is 0.5-0.6 % of the 90 % area and ≤ 0.017° in the mean. The binding limit is core run
   C's own non-convergence, not this module's sampling.
5. **The infeasible-speed version (`~v212`) barely changes the conditional** (≤ 0.4 % in area, ≤ 0.004° in the mean), even though it
   removes 18-26 % of the weight under H in the free and Davey dynamics + radar strata (`speed-filter-removed*.csv`). The fast rows lie in the same places as the slow ones.
6. **GLORYS12 only is 18-29 % narrower**, because it leaves out the between-model spread (composer passes 0-1). The **declared variant
   `silent`** narrows the conditional by a further 14-31 % and lowers the tension again.

Files: `closeups/` (colour and seabed close-ups for all 12 arms, faint points), `closeups/closeup-stats.csv`, `splithalf.csv`,
`<stratum>/by-0019-option.csv`. Per-impact columns, ρ surfaces and the source packages for hydroacoustics are in
`mh370-exchange/pleiades/hydro-test/next-run-c/`.
