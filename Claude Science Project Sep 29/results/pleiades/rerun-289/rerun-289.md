# Pléiades: §11 / D1 / D4 on `reference-289`, with end of flight's displacement histograms

Pléiades module, 9 Oct 2026, under the architecture entry of ~14:45 UTC. **Reference: core `runs/reference-289`**
(289.7° prior, seeds 1–4, 7,000,000 particles each, per-particle positions at 00:19:37). The pooled 0.25° map
reproduces the run's own `summary.json` map to 5.0e-10. The 295.66° results are kept beside it as the comparison
(`results/pleiades/rerun-measured/`).

**Configuration.** As in `rerun-measured/`:
- the measured spread (GDP-replay OU fit per component, K off);
- two `ocean-model` options at equal weight, GLORYS12 + ERA5 and GlobCurrent daily + ERA5.

**New descent kernels.** End of flight's 2-D displacement histograms
(`results/eof-displacement-oct09/displacement-boeing-glide-dive-{on,off}-160.npz`) are resampled onto the 0.05° grid
(`kernel_from_hist`, `prepare/rerun_reference.py`).
- Status: **SMOKE, PROVISIONAL.** Seed 1, N = 16, generated on the **295.66° hand-off**. They are provisional on
  dive class (b) and on the Boeing-calibrated glide.
- They are applied to both references. They are replaced when end of flight regenerates them on reference-289.
- The resampled kernel reproduces the JSON radii: 45/112/145 NM against 48/114/150 NM for `none__other`. The
  JSON figures include the 0.4 % beyond ±160 NM, which the kernel drops.

**Domain.**
- The module domain (87–97 E, 41–31 S) holds 93–94 % of the 289 impact mass, against 97 % on 295.66.
- 4.4 % of the pooled mass lies outside the 85–99 E, 43–29 S analysis grid, mostly the northern tail. That mass
  is not scored, which bounds what any conclusion here says about the tail.

**Run provenance** (architecture convention of ~16:40 UTC; read from each run's `run.json`, not from memory):
- `reference-289`: prior track 289.7° (sd 1.0°) at 18:01:49 UTC; altitude 25,000–43,000 ft; Mach 0.73–0.84; five modes,
  particles per mode [1M, 0.5M, 2.5M, 0.5M, 2.5M]. `run.json` sha256 begins `a00732d53fb618df`.
- `reference-snapshots`: identical except the prior track, 295.66°. `run.json` sha256 begins `51b79fd50b24adc3`.

## Headline (ocean-model marginal, ρ4 = 0, equal weights, pooled 4 seeds)

| Descent kernel | ln S | d | p | mean shift NM (seed range) | conditional / unconditional 90 % HDR, km² | unconditional mass in conditional HDR | lobe ≥30 / ≥50 NM |
|---|---|---|---|---|---|---|---|
| disk-7.5nm | 0.38 | 1.06 | 0.61 | 85 (78-89) | 10,932 / 20,884 | 0.44 | 0.000 / 0.000 |
| disk-15nm | 0.38 | 1.02 | 0.61 | 84 (78-88) | 17,171 / 33,289 | 0.42 | 0.000 / 0.000 |
| disk-30nm | 0.33 | 0.99 | 0.56 | 84 (78-88) | 32,352 / 62,338 | 0.42 | 0.050 / 0.000 |
| disk-45nm | 0.31 | 0.97 | 0.54 | 83 (77-86) | 48,193 / 93,118 | 0.43 | 0.186 / 0.009 |
| disk-60nm | 0.32 | 0.87 | 0.57 | 81 (75-84) | 62,872 / 125,292 | 0.43 | 0.287 / 0.098 |
| disk-80nm | 0.31 | 0.79 | 0.58 | 78 (73-82) | 82,461 / 172,552 | 0.42 | 0.377 / 0.213 |
| disk-103.4nm | 0.28 | 0.78 | 0.54 | 77 (73-81) | 101,704 / 229,184 | 0.41 | 0.442 / 0.303 |
| eof-2f PROVISIONAL-OVERNIGHT | 0.36 | 0.86 | 0.64 | 83 (76-87) | 26,512 / 45,341 | 0.57 | 0.065 / 0.038 |
| dive-on none__other | 0.37 | 0.04 | 1.00 | 107 (101-111) | 66,795 / 173,688 | 0.39 | 0.112 / 0.056 |
| dive-on none__fuel-exhaustion | 0.42 | -0.12 | n/a (d ≤ 0) | 108 (102-112) | 65,066 / 172,685 | 0.39 | 0.101 / 0.051 |
| dive-on r600_inflated__other | -0.11 | 0.46 | 0.19 | 120 (114-125) | 62,433 / 146,023 | 0.31 | 0.066 / 0.035 |
| dive-on r1200_inflated__other | 0.52 | 1.92 | 0.63 | 86 (80-90) | 15,474 / 43,275 | 0.55 | 0.020 / 0.009 |
| dive-off none__other | 0.43 | 0.19 | 1.00 | 102 (96-106) | 71,586 / 182,824 | 0.41 | 0.147 / 0.073 |
| dive-off none__fuel-exhaustion | 0.36 | 0.20 | 1.00 | 106 (100-110) | 75,074 / 187,804 | 0.38 | 0.157 / 0.077 |
| dive-off r600_inflated__other | -0.21 | 0.81 | 0.21 | 120 (114-124) | 72,599 / 163,816 | 0.31 | 0.112 / 0.059 |
| dive-off r1200_inflated__other | 0.67 | 0.95 | 1.00 | 91 (85-95) | 39,570 / 124,953 | 0.55 | 0.066 / 0.021 |

On 295.66, for comparison (same kernels):

| Descent kernel | ln S | p | mean shift NM | lobe ≥30 / ≥50 NM |
|---|---|---|---|---|
| dive-on none__other | -0.89 | 0.10 | 139 | 0.124 / 0.066 |
| dive-on none__fuel-exhaustion | -0.85 | 0.10 | 140 | 0.112 / 0.061 |
| dive-on r600_inflated__other | -1.38 | 0.06 | 157 | 0.072 / 0.041 |
| dive-on r1200_inflated__other | -0.84 | 0.20 | 117 | 0.023 / 0.012 |
| dive-off none__other | -0.80 | 0.12 | 133 | 0.159 / 0.085 |
| dive-off none__fuel-exhaustion | -0.86 | 0.11 | 137 | 0.168 / 0.088 |
| dive-off r600_inflated__other | -1.46 | 0.07 | 156 | 0.119 / 0.065 |
| dive-off r1200_inflated__other | -0.64 | 0.20 | 121 | 0.064 / 0.022 |

## Reading: the conditional PDF and the tension, together

- **On reference-289 there is no tension.**
  - With eof-2f, ln S is +0.19 to +0.52 over all 16 arms (8 options × 2 ocean models) and p = 0.43–0.85.
  - With end of flight's histograms, ln S is −0.37 to +0.79 pooled and −0.56 to +0.94 across seeds. The two
    R600-inflated kernels are the only negative ones, at −0.11 and −0.21 on the headline arm.
  - The northern mode of the new posterior (about 36.2 S, 91.3 E) lies near the Pléiades-compatible part of the
    arc, so H and the flight posterior now broadly agree.
  - On 295.66 the same kernels give ln S −1.61 to −0.51 and p 0.05–0.25. The lowest p is R600-inflated, which sits
    at the moderate-tension threshold of 0.05 but not below it.
- **The calibration is fragile with the histogram kernels.** The Bayesian model dimensionality d falls to −0.27 to
  0.65 for the held-out (`none`) kernels on 289 (all arms; −0.12 to 0.19 on the headline arm). Then p is 1 (d − 2 ln S ≤ 0) or undefined (d ≤ 0).
  - Handley & Lemos warn that p is only a rough calibration for non-Gaussian posteriors. Here it is not usable for
    those rows.
  - ln S, the HDR overlap and the shifts are the quantities to quote.
- **The conditional PDF.**
  - With eof-2f, the conditional 90 % HDR is 21,977–27,081 km² against 45,341 km² unconditional (all arms).
  - The mean moves 75–89 NM north-east along the arc, against 99–126 NM on 295.66.
  - The mode is still unconverged (12–267 NM between seeds, over every kernel and arm), because the posterior is
    bimodal.
  - With the histogram kernels the mean shift is 78–126 NM. The unconditional HDR widens to 43,000–188,000 km²,
    because the glide reach is real: a median displacement of 45 NM and a 90 % radius of 112 NM.
- **§11, the western lobe, is now tested with a real reach distribution.** The conditional mass inside the H-alone
  HDR at ≥ 30 NM inside the arc is 1.7–16.5 %, and at ≥ 50 NM it is 0.6–8.5 % (all arms, all histogram kernels,
  289). On 295.66 the ≥ 30 NM figure is 1.8–17.3 %.
  - So under H, most of the western residual remains unreachable. At most about a sixth of the conditional mass
    reaches it, and only under the held-out kernels.
  - This conclusion is SMOKE-scale until the 289 histograms land.
- The absolute BF(H : not-H) is still not quoted (P1).

## Files

- `rerun-289-measured.csv/.json`: every kernel, field, arm and seed.
- `kernel-summary-289-vs-295.csv`: the headline-arm table above, both references.
- `d4-reference-289.png/.pdf`: (a) the unconditional PDF on 289; (b) the conditional PDF on 289, with the
  unconditional 90 % HDR dashed; (c) ln S by descent kernel, 289 against 295.66, with seed ranges.
- `results/pleiades/rerun-measured/rerun-measured.csv` was regenerated with the same histogram kernels added.
  Its eof-2f and disk rows are unchanged.
- Regenerate:
  `PLEIADES_EOF_HIST="<npz>:<key>,..." python prepare/rerun_reference.py <reference-289> <module> <repo> <out> "<label>"`.

— Pléiades module
