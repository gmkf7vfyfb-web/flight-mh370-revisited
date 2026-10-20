# §11, deliverable 1 and deliverable 4 on per-particle positions — "295.66° prior; superseded on re-run"

2026-10-09, Pléiades module, overnight. **PROVISIONAL.** One command:

    python engine/hypotheses/pleiades/prepare/rerun_reference.py <reference run dir> engine/hypotheses/pleiades <repo root> <outdir>

It was run on core's `runs/reference-snapshots` (8 seeds × 7,000,000 particles, byte-identical to
`no-exhaustion-prior`). It re-runs unchanged on the new reference. Numbers: `rerun-reference.csv`
(every kernel × H field × option, pooled and per seed) and `rerun-reference.json` (inputs and checks).
Figure: `d4-conditional.png`.

**Inputs and checks**
- Per-particle 00:19:37 positions, pooled exactly as `summary.rs` does. The pooled 0.25° map
  reproduces the run's own map to 5e-10 in density. Each seed alone uses its stored weights. 1.4-1.9 %
  of mass lies outside the 85-99 E, 43-29 S grid.
- **H field (a), prior-work mixture grid**, kept for continuity with the 8 Oct numbers.
- **H field (b), this module's own D3 likelihood**, exported by the hook itself
  (`pleiades_export_likelihood_surface`) for all 8 object-rating × cluster-weight options.
  ocean-model = `glorys12v1+era5-wind10`, the only option so far.
- **Descent:** a uniform disk of declared reach R, and **eof-2f**. eof-2f is **PROVISIONAL-OVERNIGHT**.
  It is built from end of flight's two published fractions (6.6 % of weight ≥ 30 NM NW, 3.4 % ≥ 50 NM):
  93.4 % on a 15 NM disk, 3.2 % on the NW-quadrant annulus 30-50 NM, and 3.4 % on 50-103.4 NM. The core
  and the quadrant are my assumptions. **End of flight's impacts are stable-glide only; the dive class
  is absent** (Pete, 9 Oct).
- The reference run fails split-half (0.9020 against 0.924). The seed ranges below are therefore the
  honest uncertainty: direction-robust, magnitude unconverged.

## §11: does the western lobe survive? Mostly not.

Share of the H × flight mass in the H 90 % HDR at ≥ 30 NM inside the arc. Pooled, with the range
over 8 seeds:

| descent | prior-work field | module D3, equal weights | module D3, count weights |
|---|---|---|---|
| R 15 NM | 0.000 | 0.000 | 0.000 |
| R 30 NM | 0.046 (0.041-0.049) | 0.044 (0.041-0.046) | 0.034 |
| R 60 NM | 0.283 (0.280-0.288) | 0.366 (0.361-0.370) | 0.309 |
| R 103.4 NM | 0.385 (0.383-0.388) | 0.469 (0.464-0.472) | 0.382 |
| **eof-2f** | **0.042 (0.040-0.045)** | **0.053 (0.050-0.057)** | **0.035 (0.034-0.038)** |

- At ≥ 50 NM inside the arc, eof-2f gives 0.019 (prior-work field) and 0.023 (D3).
- The 8 Oct histogram numbers (5.9 % at 30 NM, 28.7 % at 60, 38.6 % at 103.4) are reproduced within
  ±1.3 points on the prior-work field. Seed scatter is under ±0.5 points.
- **With end of flight's measured reach, about 4-5 % of the conditional mass remains in the western
  lobe, and about 2 % beyond 50 NM.** Most of the residual mass the prior work moved to ~91 E under H is
  not reachable from the flight and fuel evidence.
- Two conditions are not yet settled: the two-fraction kernel, and that dives are absent. A dive
  should travel less far, so if anything it lowers these numbers further.

## Deliverables 1 and 4: the conditional and its tension, always paired

Module D3, rating 5, equal weights. Pooled, with the range over 8 seeds:

| descent | ln S | ln R (volume 988,800 km²) | uncond. in cond. HDR | cond. in uncond. HDR | cond. HDR km² | mean shift NM |
|---|---|---|---|---|---|---|
| R 7.5 | −0.73 (−1.12 to −0.42) | +0.83 | 0.077 | 0.68 | 4,930 | 148 (140-161) |
| R 30 | −0.87 (−1.14 to −0.54) | +0.49 | 0.069 | 0.57 | 13,470 | 149 (142-162) |
| R 60 | −0.74 (−0.93 to −0.43) | +0.42 | 0.061 | 0.60 | 21,820 | 142 (134-155) |
| R 103.4 | −0.62 (−0.78 to −0.29) | +0.24 | 0.064 | 0.77 | 33,060 | 134 (126-145) |
| **eof-2f** | **−0.71 (−1.05 to −0.38)** | +0.72 | 0.082 | 0.89 | 10,200 | **147 (139-160)** |

The domain is the hook's table, 87-97 E, 41-31 S. Unconditional HDR (eof-2f) 38,630 km²; H-alone
HDR 55,870 km².

1. **H relocates the impact estimate 130-150 NM north-east along the arc** at every reach. The seed
   range is ±10 NM.
2. **ln S is negative in every seed, kernel and option**: from −0.3 to −1.1 in the reference arm, and
   no higher than −0.11 in any arm. The tension is
   direction-robust and magnitude-unconverged.
3. **Only 6-8 % of the unconditional mass lies inside the conditional's HDR.** The conditional sits in
   the unconditional's north-east tail.
4. **The mode is not converged.** It moves 99-233 NM between seeds, so quote the mean shift.
5. **Across the D4 alternatives (eof-2f):**
   - ρ4 ∈ {0, 0.25, 0.5, 1} × cluster-weight ∈ {equal, count} gives ln S −0.45 to −0.75, mean shift
     141-150 NM, and the lobe at 3.3-5.3 %. The conclusion is the same in every arm.
   - `cosmo-contact-set`: no effect, see question P2.
   - `ocean-model`: one option until ocean transport supplies a second.
6. The prior-work field gives the same picture (mean shift 150-157 NM; ln S −0.91 to −1.14 pooled).

## Not a result: the absolute BF(H : not-H)

E_flight[L_H] over the domain is 0.6-2.0 × 10⁻³ across every arm, kernel and seed. **It is not quoted as evidence against
H.** It follows from the declared q_c = 1/A_scene: a 15-day transport spread of about 33-60 km can never
place an object in a particular 500 km² scene more precisely than uniform. It says nothing about whether
debris was present. That needs the Poisson and footprint term (brief §13). See question P1.
