# Glide calibration against Boeing's published driftdown (brief section 8, deliverable 1)

9 October 2026, End of Flight Module. **PROVISIONAL-OVERNIGHT choice; SMOKE-scale consequences, not evidence.**

## The check

- **What Boeing says.** The Malaysian SIR, Appendix 1.6E, p. 8, gives Boeing's driftdown: about 0.0034 NM per foot.
  - This is the additional range after a **dual-engine flame-out** "if manual control inputs were commanded from
    the flight deck to maintain wings level flight". That is about 120 NM from FL350 and 136 NM from FL400.
  - It is a dual-flame-out glide, so windmilling engines and the RAT are included. The implied still-air
    (L/D) is 20.66 if read per foot of altitude. It is 18.88 if read as energy height (120 NM over 35,000 ft plus
    the 3,623 ft kinetic term of brief section 8).
- **What the module had.**
  - Clean (L/D)max is U[20.8, 21.4]. That band was set against Boeing's ~20.7, but as a *clean* figure.
  - Windmilling at 0.0020–0.0060 per engine plus RAT at 0.0001–0.0006 was then added on top, ESDU scale.
  - Re-optimised dual-flame-out (L/D)max was 15.0 / 16.3 / 17.9 (5/50/95%, prior over the sampled bands). The
    altitude term from FL350 was 86 / 94 / 103 NM.
  - **This is inconsistent with Boeing under either reading.** Matching Boeing needs a total windmilling + RAT
    ΔC_D of 0.0002–0.0036. The smallest total in the ESDU band was 0.0041.
- **Why the old band was set there.** It was pinned to the ~100 NM recorded in the brief: the section 12 pitfall
  ("best glide ... about 100 NM out") and the section 8 energy-height worked example (103.4 NM).
  - Neither is a calibration target. The section 8 calibration targets include "Boeing's published range and
    endurance".

## The choice (PROVISIONAL-OVERNIGHT; Pete to confirm)

- **Windmilling per engine changes to U[0.0000, 0.0015]**, with the RAT unchanged.
  - At the band ends the dual-flame-out (L/D)max is 21.01 and 18.55 (reference clean 21.1, e = 0.80). That
    brackets both readings of Boeing, and the altitude term from FL350 runs 107–121 NM.
  - This is pinned by a unit test in `aero.rs`.
- **The ESDU band is kept as `smoke/glide-esdu.toml`.** With it, the current code reproduces `eof-dive-n4-s1`
  exactly in all 90 impact columns.
- **The lower windmilling bound of 0 is a modelling bound, not a physical claim.** It is where Boeing's
  altitude-only reading sends it. The windmilling drag of a Trent 892 is not public.

## Consequence at smoke scale

Seed 1, N = 4, dive class ON (0.5, cap 90°), on the `reference-snapshots` 00:11 hand-off. The runs are
`runs/eof-dive-n4-s1` (ESDU) and `runs/eof-glideB-n4-s1` (Boeing).

| option × log-on cause | ESS, ESDU / Boeing | median impact lat, lon (°), ESDU → Boeing | displacement 50/90/99% (NM), ESDU → Boeing | share beyond 110 NM, ESDU / Boeing |
|---|---|---|---|---|
| `none__other` | 310,041 / 310,041 | -37.28, 89.54 → -37.31, 89.52 | 42/95/137 → 48/114/150 | 0.041 / 0.108 |
| `none__fuel-exhaustion` | 34,054 / 33,696 | -37.37, 89.50 → -37.40, 89.47 | 41/100/119 → 45/123/142 | 0.033 / 0.170 |
| `r600_inflated__other` | 86,966 / 89,839 | -38.03, 89.39 → -38.24, 89.32 | 53/98/137 → 64/117/149 | 0.047 / 0.147 |
| `r600_inflated__fuel-exhaustion` | 14,717 / 14,775 | -37.81, 89.42 → -37.98, 89.39 | 46/100/118 → 54/124/141 | 0.033 / 0.193 |
| `r600_no-offset__other` | 7,168 / 6,899 | -37.75, 89.35 → -37.88, 89.33 | 40/93/114 → 45/112/136 | 0.015 / 0.106 |
| `r600_no-offset__fuel-exhaustion` | 2,339 / 2,089 | -37.55, 89.43 → -37.73, 89.46 | 37/96/115 → 43/120/140 | 0.024 / 0.154 |
| `r600_startup-offset__other` | 6,899 / 5,990 | -37.63, 89.44 → -37.65, 89.28 | 39/101/118 → 37/115/136 | 0.030 / 0.150 |
| `r600_startup-offset__fuel-exhaustion` | 2,942 / 2,323 | -37.95, 89.48 → -37.91, 89.48 | 53/105/120 → 47/122/138 | 0.047 / 0.232 |
| `r1200_inflated__other` | 2,272 / 1,994 | -37.06, 89.43 → -37.03, 89.44 | 2/55/106 → 2/26/109 | 0.003 / 0.008 |
| `r1200_inflated__fuel-exhaustion` | 685 / 576 | -37.15, 89.52 → -37.12, 89.51 | 2/76/106 → 2/46/113 | 0.003 / 0.012 |
| `r1200_no-offset__other` | 442 / 383 | -37.11, 89.29 → -37.03, 89.45 | 2/50/101 → 2/18/100 | 0.000 / 0.002 |
| `r1200_no-offset__fuel-exhaustion` | 131 / 103 | -37.23, 89.30 → -37.15, 89.51 | 2/69/101 → 2/18/106 | 0.000 / 0.004 |
| `r1200_startup-offset__other` | 1,151 / 1,054 | -36.95, 89.49 → -36.95, 89.47 | 2/21/85 → 2/4/53 | 0.000 / 0.000 |
| `r1200_startup-offset__fuel-exhaustion` | 331 / 298 | -37.03, 89.56 → -37.04, 89.53 | 2/13/85 → 2/3/49 | 0.000 / 0.000 |
| `both_inflated__other` | 154 / 125 | -37.38, 89.54 → -37.14, 89.65 | 15/98/116 → 6/71/120 | 0.021 / 0.014 |
| `both_inflated__fuel-exhaustion` | 84 / 36 | -37.76, 89.34 → -37.24, 89.57 | 37/98/116 → 9/95/121 | 0.022 / 0.022 |

By control axis (displacement from the own 00:19:37 position):

| option | control axis | weight share, ESDU / Boeing | displacement 50/90% (NM), ESDU → Boeing |
|---|---|---|---|
| `none__other` | ditching-attempt | 0.193 / 0.193 | 80/116 → 99/134 |
| `none__other` | maintained-then-lost | 0.198 / 0.203 | 34/79 → 36/89 |
| `none__other` | no-intervention | 0.126 / 0.127 | 9/31 → 10/32 |
| `none__other` | upset-then-recovery | 0.131 / 0.118 | 42/72 → 49/84 |
| `r600_inflated__fuel-exhaustion` | ditching-attempt | 0.305 / 0.329 | 89/111 → 113/134 |
| `r600_inflated__fuel-exhaustion` | maintained-then-lost | 0.393 / 0.422 | 41/83 → 45/97 |
| `r600_inflated__fuel-exhaustion` | no-intervention | 0.164 / 0.146 | 12/47 → 13/52 |
| `r600_inflated__fuel-exhaustion` | upset-then-recovery | 0.138 / 0.103 | 48/77 → 56/93 |
| `r1200_inflated__fuel-exhaustion` | ditching-attempt | 0.079 / 0.045 | 90/107 → 102/117 |
| `r1200_inflated__fuel-exhaustion` | maintained-then-lost | 0.442 / 0.498 | 2/63 → 2/25 |
| `r1200_inflated__fuel-exhaustion` | no-intervention | 0.409 / 0.434 | 2/3 → 2/3 |
| `r1200_inflated__fuel-exhaustion` | upset-then-recovery | 0.070 / 0.024 | 49/68 → 52/85 |

## Reading

- **Controlled glides reach further.**
  - The ditching-attempt median displacement rises from 80–90 to 99–113 NM.
  - The pooled 90% radius for held-out and R600 rises from 93–105 to 112–124 NM.
  - The share beyond 110 NM rises from 1.5–5% to 11–23%. The Pléiades histograms are therefore regenerated at
    ±160 NM (see `results/eof-displacement-oct09/`).
- **The R600 median impact moves south for inflated and no-offset**, by 0.13–0.21°.
  - Startup-offset moves by 0.04° or less.
  - The held-out median moves by about 0.03°.
- **R1200 is tighter at 90%.** The dive dominates it, and the glide-compatible tail shrinks. The median stays at
  about 2 NM.
- **`both/inflated` stays concentration-limited** (ESS 36–154 at N = 4).
- **Brief section 12 now reads differently.** "Best glide produces ditching-like impacts about 100 NM out"
  becomes about 100–120 NM out under the Boeing calibration. The pitfall itself, that a ditching-like impact is
  not evidence of a ditching, is unchanged.
