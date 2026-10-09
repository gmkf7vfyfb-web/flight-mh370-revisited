# Impact displacement from the 00:19:37 position, dive class on and off (for Pléiades)

9 October 2026, End of Flight Module. **SMOKE SCALE, PROVISIONAL. Not evidence.** Relay (i) of the architecture
entry of ~06:45 UTC, 9 Oct.

- **Inputs.** Seed 1, N = 16 children per parent, the `reference-snapshots` 00:11 hand-off (295.66° prior, about 20,000
  parents), run outside the heavy lock at 2 threads.
  - Dive ON: `runs/eof-dive-n16-s1`. This is the PROVISIONAL-OVERNIGHT option (b) dive class: divergent spiral,
    weight 0.5 (Pete's equal weight), bank cap 90°, from `run.toml`.
  - Dive OFF: `runs/eof-s6-n16-s1`, revision 9d109c8.
- **Dive OFF is valid against current code.** A current-binary N = 4 run with `smoke/spiral-off.toml` reproduces
  `eof-s6-n4-s1` bit for bit in all 87 shared impact columns. It differs only by the 3 new latent columns.
- **Definition.** Δnorth and Δeast in NM are measured on the local tangent plane at the trajectory's own position
  when it flew through 00:19:37 (`latent:last_burst_*`), with 1 NM = 1 arc-minute of latitude.
  - Bins are 5 NM over ±110 NM. The weighting is the option's posterior: hand-off weight × burst likelihood, ×
    the §6 log-on lag density for the fuel-exhaustion cause.
  - Rows with no 00:19:37 position are excluded, and `included_share` reports what that leaves. They are mostly
    trajectories that were down before the burst, under the held-out option.
  - Each histogram is normalised to the included weight. Mass beyond 110 NM is not in the histogram; it is
    `outside_range_share`, and the radius percentiles include it.
- **Files.**
  - `displacement-dive-{on,off}.npz` holds arrays keyed `<option>__<cause>__<pooled|control axis>`, shape 44 × 44
    as [north bin, east bin], with the edges in the JSON.
  - `displacement-dive-{on,off}.json` holds shares, ESS, and the 50/90/99% radii.
  - The figure is `displacement-dive-on-off.png`.
  - The generator is `engine/hypotheses/end-of-flight/smoke/displacement_hist.py`.

## Pooled summary

| option × log-on cause | ESS off / on | share with a 00:19:37 position, off / on | radius 50/90/99% (NM), dive OFF | radius 50/90/99% (NM), dive ON | share beyond 110 NM, off / on |
|---|---|---|---|---|---|
| `none__other` | 1,227,897 / 1,227,897 | 0.766 / 0.647 | 40/93/135 | 42/95/137 | 0.036 / 0.041 |
| `none__fuel-exhaustion` | 138,762 / 135,196 | 0.999 / 0.965 | 44/99/119 | 42/100/120 | 0.031 / 0.033 |
| `r600_inflated__other` | 351,677 / 344,373 | 0.911 / 0.909 | 55/99/137 | 52/99/137 | 0.047 / 0.047 |
| `r600_inflated__fuel-exhaustion` | 59,377 / 58,352 | 1.000 / 1.000 | 50/100/119 | 47/100/119 | 0.034 / 0.035 |
| `r600_no-offset__other` | 28,635 / 28,120 | 1.000 / 1.000 | 44/93/114 | 40/93/114 | 0.015 / 0.015 |
| `r600_no-offset__fuel-exhaustion` | 9,050 / 9,112 | 1.000 / 1.000 | 41/97/117 | 37/96/116 | 0.029 / 0.027 |
| `r600_startup-offset__other` | 24,258 / 27,616 | 1.000 / 1.000 | 48/102/120 | 38/100/119 | 0.035 / 0.031 |
| `r600_startup-offset__fuel-exhaustion` | 9,662 / 11,544 | 1.000 / 1.000 | 71/107/122 | 52/105/121 | 0.057 / 0.050 |
| `r1200_inflated__other` | 3,055 / 9,061 | 1.000 / 1.000 | 18/97/114 | 2/57/106 | 0.013 / 0.004 |
| `r1200_inflated__fuel-exhaustion` | 994 / 2,723 | 1.000 / 1.000 | 64/100/117 | 2/77/107 | 0.017 / 0.004 |
| `r1200_no-offset__other` | 476 / 1,776 | 1.000 / 1.000 | 14/88/107 | 2/50/101 | 0.003 / 0.000 |
| `r1200_no-offset__fuel-exhaustion` | 147 / 537 | 1.000 / 1.000 | 51/91/107 | 2/70/102 | 0.003 / 0.000 |
| `r1200_startup-offset__other` | 805 / 4,615 | 1.000 / 1.000 | 11/81/97 | 2/20/89 | 0.003 / 0.000 |
| `r1200_startup-offset__fuel-exhaustion` | 204 / 1,374 | 1.000 / 1.000 | 21/88/97 | 2/11/89 | 0.000 / 0.000 |
| `both_inflated__other` | 543 / 614 | 1.000 / 1.000 | 37/101/118 | 16/100/116 | 0.019 / 0.023 |
| `both_inflated__fuel-exhaustion` | 191 / 260 | 1.000 / 1.000 | 64/100/115 | 40/99/116 | 0.017 / 0.020 |

## R1200/inflated, fuel-exhaustion log-on, by control axis

| control axis | R1200/inflated fuel-exh. weight share, off / on | median radius (NM), off / on |
|---|---|---|
| ditching-attempt | 0.336 / 0.090 | 88 / 90 |
| maintained-then-lost | 0.613 / 0.447 | 26 / 2 |
| no-intervention | 0.031 / 0.398 | 9 / 2 |
| upset-then-recovery | 0.020 / 0.065 | 39 / 46 |

## Reading

- **Held-out, R600 inflated and R600 no-offset barely move.** Their median displacement changes by 4 NM or less.
  - R600 startup-offset is the exception: with the dive class on, its median is 10 NM shorter (48 → 38 NM,
    other cause) and 19 NM shorter (71 → 52 NM, fuel-exhaustion). *(Corrected 9 Oct: the first version said
    "3 NM or less" for all R600.)*
  - The 90% radius stays at 93–107 NM throughout.
- **R1200 collapses onto its 00:19:37 position with the dive class on.** The median falls from 11–64 NM to about
  2 NM, and the 90% radius falls from 81–100 NM to 11–77 NM.
  - This is the provisional dive class at work. An R1200 burst sees a descent that the glide-only model can only
    fit far from the burst. The divergent spiral fits it within a few NM.
  - It is conditional on Pete's 50/50 weight and on option (b). The chord misfit is declared: the dive ends
    1.0–2.7 NM after the 15,000 ft/min crossing, against 4.7–7.9 NM in the Boeing cases. The near-zero R1200
    displacement is therefore probably too tight by a few NM.
- **`both/inflated` remains concentration-limited** (ESS 191–614 at one seed), so its histogram is not
  interpretable at this scale.
- **ESS is single-seed.** The E2 target is 1,000 pooled over 8 seeds, about 125 per seed; on this seed every row
  except `both/inflated` meets it.
- **The dive class also moves weight between control axes under R1200.** With fuel-exhaustion log-on:
  - `no-intervention` rises from 3.1% to 39.8% and `ditching-attempt` falls from 33.6% to 9.0%.
  - Before the dive class existed, an R1200-compatible descent was only reachable through the ditching
    and maintained-then-lost families. The control-axis shares are therefore provisional on the dive class, as is
    the displacement.


## Superseding files: Boeing-calibrated glide, ±160 NM (added 9 Oct, later the same day)

- **Why these supersede the files above.** The module's dual-flame-out glide is now calibrated to Boeing's
  driftdown (SIR App. 1.6E, 0.0034 NM/ft). This is PROVISIONAL-OVERNIGHT and Pete is to confirm it; see
  `results/eof-glide-calibration-oct09/`.
  - The files above use the former ESDU-scale band. Under it, controlled glides fell about 20 NM short of Boeing.
  - With the longer glides, ±110 NM would leave 11–23% of the mass outside the histogram, so these use ±160 NM
    (64 × 64 bins). That leaves 0.4% or less outside.
- **Runs.**
  - Dive ON: `runs/eof-glideB-n16-s1`.
  - Dive OFF: `runs/eof-glideB-off-n16-s1`, which is `smoke/spiral-off.toml`.
  - Both are seed 1, N = 16, on the same hand-off.
- **Files.** `displacement-boeing-glide-dive-{on,off}-160.{npz,json}` and the figure
  `displacement-boeing-glide-on-off-160.png`.
  - `displacement-esdu-glide-dive-on-160.*` is the former band at the same extent, for a like-for-like comparison.

| option × log-on cause | ESS off / on | radius 50/90/99% (NM), dive OFF | radius 50/90/99% (NM), dive ON | share beyond 160 NM, off / on |
|---|---|---|---|---|
| `none__other` | 1,227,897 / 1,227,897 | 46/111/148 | 48/114/150 | 0.004 / 0.004 |
| `none__fuel-exhaustion` | 137,316 / 133,698 | 49/122/142 | 46/123/142 | 0.000 / 0.000 |
| `r600_inflated__other` | 363,091 / 355,627 | 66/118/149 | 64/117/149 | 0.004 / 0.004 |
| `r600_inflated__fuel-exhaustion` | 58,766 / 58,452 | 59/124/142 | 55/124/141 | 0.000 / 0.000 |
| `r600_no-offset__other` | 26,835 / 26,942 | 50/113/138 | 45/111/138 | 0.001 / 0.001 |
| `r600_no-offset__fuel-exhaustion` | 7,911 / 8,266 | 48/121/142 | 43/120/141 | 0.000 / 0.000 |
| `r600_startup-offset__other` | 20,817 / 23,959 | 50/117/137 | 38/115/136 | 0.000 / 0.000 |
| `r600_startup-offset__fuel-exhaustion` | 7,361 / 8,969 | 68/124/139 | 48/122/139 | 0.000 / 0.000 |
| `r1200_inflated__other` | 2,082 / 7,897 | 14/96/121 | 2/26/111 | 0.000 / 0.000 |
| `r1200_inflated__fuel-exhaustion` | 538 / 2,195 | 43/104/123 | 2/48/114 | 0.000 / 0.000 |
| `r1200_no-offset__other` | 329 / 1,536 | 14/99/118 | 2/16/106 | 0.000 / 0.000 |
| `r1200_no-offset__fuel-exhaustion` | 82 / 413 | 33/103/116 | 2/11/106 | 0.000 / 0.000 |
| `r1200_startup-offset__other` | 563 / 4,279 | 11/61/109 | 2/5/66 | 0.000 / 0.000 |
| `r1200_startup-offset__fuel-exhaustion` | 102 / 1,238 | 13/97/107 | 2/3/72 | 0.000 / 0.000 |
| `both_inflated__other` | 341 / 465 | 15/99/129 | 7/91/121 | 0.000 / 0.000 |
| `both_inflated__fuel-exhaustion` | 98 / 168 | 77/102/121 | 9/98/121 | 0.000 / 0.000 |

- **The R1200 collapse under the dive class survives the recalibration.** The median falls from 11–43 NM to
  about 2 NM.
- **The R600 startup-offset median is still 12–20 NM shorter with the dive class on.** Held-out, R600 inflated
  and R600 no-offset change by 5 NM or less.
- **Concentration-limited at this seed** (below about 125, the per-seed share of the pooled 1,000):
  `r1200_no-offset__fuel-exhaustion` with the dive off (ESS 82), `r1200_startup-offset__fuel-exhaustion` with the
  dive off (102), and `both_inflated__fuel-exhaustion` (98 / 168).

## Project-convention figure (added 9 Oct, Pete's request)

- **Files.** `displacement-boeing-glide-greyscale.{pdf,png}`, with `.json` holding the per-panel ESS and an
  enclosed-mass check. The generator is `engine/hypotheses/end-of-flight/smoke/displacement_greyscale.py`.
- **Convention.** The figure follows `report/epoch_map.py`: greyscale highest-posterior-density bands at
  50/90/99% with dark contour edges.
  - The density is a weighted 1 NM histogram, Gaussian-smoothed at σ = 2 NM, and the levels are taken on the
    smoothed density.
  - The axes are displacement from each trajectory's own 00:19:37 position, not latitude and longitude, so no
    arcs are drawn.
- **Reading the R1200 panels.** They break into islands because R1200 is concentration-limited on one seed
  (ESS 538 with the dive class off, 2,195 with it on). This is a property of the sample, not of the plotting.
- **Status.** This is the 295.66° hand-off at smoke scale. It is superseded when the reference-289 sweep lands.

**Update 9 Oct 19:50 UTC.** The reference-289 summary/histogram files here were regenerated with all 24 option x cause arms (both/no-offset and both/startup-offset had been dropped by a hard-coded OPTIONS list; r600-bto and both-bto added, derived from BTO residual columns). 15 of 24 converge. Evidence per option and Holland H1:H2: results/eof-two-burst-oct09/README.md.
