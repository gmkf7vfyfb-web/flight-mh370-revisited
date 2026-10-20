# Early-flight families with radar scored inside the likelihood (9 Oct 2026 overnight run)

**Labels: uncorrected fuel model (fuel audit F1-F7); provisional sampler (core request 17); STK/SGP4 ephemeris.**
These results are superseded by the next large run (all fixes and extensions). They are reported for the
record and for the relative comparison between families, which shares all three defects.

Runs: `runs/families-{repro-radar,free,routes,descent-climb}`, binary `5aee2bb` (gated byte-identical),
seeds 1-4. Config stack: davey2016 + no-exhaustion-prior + reference-snapshots + radar-full + family overlay
(`config/sensitivity/early-families/overnight/*.toml`). Particles per seed: Davey dynamics + radar 0.875M,
free 3.5M, routes 1.75M, descent-climb 0.875M. Report: `engine/report/early_families.py` (now with family
probabilities, mixture and footnote); outputs in `results/families-289/`.

| Family | log mean Z | log Z by seed | P(family), equal prior odds | 00:19 median | 00:19 5-95% | 00:11 median |
|---|---|---|---|---|---|---|
| Davey dynamics + radar | -137.02 | -137.03 -136.95 -137.24 -136.90 | 0.19 | -36.59 | -38.03 .. -29.06 | -35.55 |
| free (wide early Mach, turn) | -135.83 | -135.78 -135.77 -135.74 -136.04 | **0.63** | -36.85 | -38.02 .. -29.69 | -35.94 |
| routes (published airways) | -139.88 | -139.90 -139.82 -140.01 -139.80 | 0.01 | -37.25 | -37.56 .. -32.04 | -36.31 |
| descent-climb | -137.19 | -136.98 -137.79 -137.05 -137.13 | 0.16 | -37.22 | -38.14 .. -34.61 | -36.26 |
| **mixture** | | | | **-37.00** | | **-36.02** |

Other quantities:
- free: P(turn at 18:22:12) 0.84, turn track 295.7 / 306.2 / 317.3 deg (5/50/95%), initial Mach median 0.815.
- descent-climb: P(turn) 0.90; the lowest excursion altitude is 6,800 / 9,400 / 9,800 ft, so the radar plus
  777 performance keep it shallow (no dip below about 7,000 ft survives); about 97 rejected excursion draws
  per accepted one.
- routes: VAMPI-MEKAR-NILAM-NOPEK-ISBIX 0.89, ANOKO-BEDAX 0.09. It is 4.05 nats below free.
- Cross-track at 18:22 from N571: 0.6-2.5 NM median in every family.

Reading:
- Radar inside the likelihood does not decide between the families sharply. Free is preferred, by about
  1.2 nats over Davey dynamics and 1.4 over descent-climb; routes are disfavoured by about 4 nats.
- The mixture's 00:19 median, -37.00, lies between the reference-289 value (-36.42, no radar, 7M per seed)
  and Davey's -37.53.
- Seed spread in log Z is 0.1-0.4 nats, which is small against the 1.2-4 nat differences. The descent-climb
  and Davey strata ran at only 0.875M per seed, so their posterior shapes are less well converged than free.
