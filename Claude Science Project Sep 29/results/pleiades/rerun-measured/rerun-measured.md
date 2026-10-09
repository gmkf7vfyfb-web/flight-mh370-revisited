# Pléiades: §11 / D1 / D4 with the MEASURED transport error and two ocean models

**Label: "295.66° prior; superseded on re-run".** Reference: core `runs/reference-snapshots` (8 seeds × 7,000,000
particles, byte-identical to `no-exhaustion-prior`, which fails split-half). Re-run with
`prepare/rerun_reference.py` on core `reference-289` when it lands. Pléiades module, 9 Oct 2026.

## What changed from `rerun-295/`

1. **Spread is measured, not declared.** The analytic model error is now the per-component OU fit of ocean
   transport's GDP replay [OT-GDP] (undrogued drifters, box 80–110E 45–20S, March–May starts, current + 1 % ERA5):
   - GLORYS12 + ERA5: σ = 0.1153 / 0.1176 m/s, T = 6.13 / 4.20 d (east / north);
   - GlobCurrent + ERA5: σ = 0.1043 / 0.0955 m/s, T = 16.02 / 7.64 d.
   - The K prior (log-uniform 30–1000 m²/s) is switched off: the replay residual against real drifters already
     contains sub-grid dispersion, so adding K would count it twice.
   - Per-component sd over the 15.2 days from impact to Pléiades: 108 / 98 km (GLORYS12), 118 / 95 km (GlobCurrent),
     against 33–60 km under the declared σ_e 0.05 m/s, T_e 2 d.
   - The density is now anisotropic (diagonal east/north covariance; `likelihood.rs`, test
     `anisotropic_density_integrates_to_one_and_reduces_to_isotropic`).
2. **Second `ocean-model` option: Copernicus-GlobCurrent** (ocean transport's recommendation [OT-REC]), equal prior
   weight. The reference uses the DAILY table, label `globcurrent-my-p1d+era5-wind10`, so the label equals drift's
   (composition rule 7). PROVISIONAL-OVERNIGHT P4 (architecture.md, Pléiades tenth entry). The hourly table
   (`globcurrent-my-pt1h+era5-wind10`) is carried as a sensitivity: it changes ln S by ≤ 0.012 and the mean shift by
   ≤ 0.8 NM, pooled, over every kernel and arm (≤ 0.015 and ≤ 0.8 NM in any single seed).
3. **Tension is now calibrated.** Bayesian model dimensionality d̃ = 2 Var_P[log P/π] [HL2019 eq. 3], shared
   dimensionality d = d̃_A + d̃_B − d̃_AB [HL2019 Proposition 2, p. 6], tension probability
   p = P(χ²_d > d − 2 ln S) [HL2019 eq. 25]. HL2019 state that for non-Gaussian posteriors p is "only a rough
   calibration"; ours are non-Gaussian (an arc-aligned ridge and a multi-lobed likelihood).

## Result (eof-2f descent kernel, PROVISIONAL-OVERNIGHT; pooled 8 seeds; ranges over the 8 object-rating × cluster-weight arms)

| Spread | Ocean model | ln S | d (shared) | tension p, pooled (seed range) | mean shift NM, pooled (seed range) | conditional 90% HDR km² | H-alone 90% HDR km² | unconditional mass in conditional HDR | lobe ≥30 NM | lobe ≥50 NM |
|---|---|---|---|---|---|---|---|---|---|---|
| measured | glorys12v1+era5-wind10 | -0.98 to -0.84 | 1.56 to 2.24 | 0.121 to 0.168 (0.117–0.211) | 103 to 126 (90–143) | 30,349–33,267 | 185,122–192,141 | 0.60–0.71 | 0.054–0.068 | 0.029–0.040 |
| measured | globcurrent-my-p1d+era5-wind10 | -1.13 to -0.90 | 1.79 to 2.44 | 0.110 to 0.167 (0.105–0.207) | 99 to 121 (82–141) | 28,746–30,673 | 204,101–212,489 | 0.56–0.63 | 0.061–0.074 | 0.037–0.049 |
| measured | both (equal weight) | -1.00 to -0.83 | 1.62 to 2.32 | 0.124 to 0.175 (0.119–0.218) | 101 to 124 (86–142) | 30,522–33,044 | 213,590–219,781 | 0.60–0.69 | 0.057–0.071 | 0.033–0.045 |
| measured (sensitivity) | globcurrent-my-pt1h+era5-wind10 | -1.14 to -0.91 | 1.77 to 2.43 | 0.108 to 0.165 (0.103–0.205) | 99 to 122 (83–142) | 28,797–30,724 | 203,948–212,351 | 0.56–0.63 | 0.061–0.074 | 0.037–0.049 |
| declared (superseded) | glorys12v1+era5-wind10 | -0.75 to -0.45 | 2.36 to 3.27 | 0.190 to 0.280 (0.162–0.358) | 141 to 150 (133–163) | 8,641–11,353 | 51,263–60,621 | 0.07–0.10 | 0.033–0.053 | 0.012–0.023 |
| declared (superseded) | globcurrent-my-pt1h+era5-wind10 | -1.10 to -0.70 | 1.93 to 2.92 | 0.120 to 0.219 (0.096–0.289) | 147 to 159 (139–171) | 8,496–11,859 | 55,993–60,640 | 0.06–0.09 | 0.049–0.080 | 0.026–0.049 |
| declared (superseded) | both (equal weight) | -0.81 to -0.47 | 2.38 to 3.25 | 0.179 to 0.275 (0.146–0.353) | 144 to 154 (136–166) | 8,945–12,058 | 63,282–70,472 | 0.07–0.10 | 0.040–0.063 | 0.018–0.034 |

Unconditional 90 % HDR: 38,628 km². Prior volume (module domain): 988,761 km².

**Reading, conditional PDF and tension together (brief rule):**
- **No significant tension** under any spread, ocean model, arm or seed: p = 0.10–0.22 for the measured spread
  (moderate tension in HL2019 is p ≲ 0.05). ln S ≈ −0.8 to −1.1 against d ≈ 1.6–2.4.
- **With the measured spread the conditional PDF is no longer narrow:** its 90 % HDR is 28,700–33,300 km²
  (0.74–0.86 of the unconditional HDR) and holds 56–71 % of the unconditional mass. Under the declared spread the
  conditional HDR was 8,500–12,100 km² holding only 6–10 %. That narrowness came from the under-stated transport
  error, not from precision: the module now says much less about the impact point, which is the honest outcome.
- **H still relocates the mean** 99–126 NM pooled (82–143 across seeds), along the arc towards the NE, down from
  141–159 NM. The mode is unconverged: it moves 126–229 NM between seeds.
- **The western lobe stays small:** 5.4–7.4 % of the conditional mass lies ≥ 30 NM inside the arc within the
  H-alone HDR, and 2.9–4.9 % ≥ 50 NM, so most of the western H-alone region is still unreachable by the
  descent kernel.
- The absolute BF(H : not-H) is still not quoted (P1: q = 1/A_scene convention; no Poisson/footprint term).

### Dependence on the descent kernel (both ocean models, ρ4 = 0, equal weights, pooled)

| Descent kernel | ln S | d | p | mean shift NM | conditional HDR km² | unconditional HDR km² | uncond. mass in cond. HDR | lobe ≥30 | lobe ≥50 |
|---|---|---|---|---|---|---|---|---|---|
| disk-7.5nm | -0.97 | 2.06 | 0.141 | 116 | 13,802 | 17,014 | 0.54 | 0.000 | 0.000 |
| disk-15nm | -0.96 | 1.98 | 0.140 | 115 | 22,201 | 27,637 | 0.52 | 0.000 | 0.000 |
| disk-30nm | -0.97 | 1.93 | 0.137 | 114 | 41,220 | 52,430 | 0.48 | 0.044 | 0.000 |
| disk-45nm | -0.94 | 1.86 | 0.138 | 113 | 59,498 | 78,968 | 0.45 | 0.173 | 0.008 |
| disk-60nm | -0.87 | 1.69 | 0.139 | 111 | 75,407 | 106,435 | 0.42 | 0.277 | 0.096 |
| disk-80nm | -0.76 | 1.49 | 0.145 | 108 | 94,740 | 145,805 | 0.39 | 0.381 | 0.225 |
| disk-103.4nm | -0.61 | 1.27 | 0.157 | 105 | 111,723 | 192,394 | 0.36 | 0.458 | 0.326 |
| eof-2f (provisional) | -1.00 | 1.81 | 0.126 | 113 | 33,044 | 38,628 | 0.67 | 0.071 | 0.045 |

The tension does not depend on the kernel (p 0.13–0.16). The western lobe does (0 → 46 % at ≥ 30 NM): the §11
conclusion still rests on end of flight's 2-D displacement histogram, which replaces eof-2f when it lands.

## Two-epoch COSMO → Pléiades windage calibration at the measured spread

`d5-two-epoch-measured-spread.csv`. Isotropic approximation (rms σ, mean T per product: 0.1165 m/s, 5.17 d; 0.1000 m/s, 11.83 d), K off, rating-5 clusters,
equal weights. The per-component sd over 40.5 h is 16.1 km (GLORYS12) and 13.4–15.0 km (GlobCurrent).
- IG 0.001–0.07 bits, ln BF(free vs fixed windage) −0.12 to −0.01, P(dawn pass) 0.50–0.53, for F1–F3 and F1–F4,
  π_m 0.5 and 0.9, on the GLORYS12 and daily GlobCurrent tracks (hourly tracks as a sensitivity: same ranges).
- This confirms, independently of ocean transport's own finding [OT-GDP], that the calibration carries no information.
  The injection-recovery floor (`results/pleiades/d5-two-epoch.md`) needs sd ≲ 6 km; both products are above 13 km.
  **Negative result, closed for both products.**

## Files

- `rerun-measured.csv/.json` (reference), `rerun-pt1h.csv/.json` (hourly GlobCurrent), `rerun-declared.csv/.json`
  (superseded spread, both products), `d4-tension-summary.csv`, `d4-conditional-measured.png/.pdf`.
- Regenerate: export release tables (`PLEIADES_CURRENT`, `PLEIADES_EXPORT_TAG`), then the surface
  (`pleiades_export_likelihood_surface`, `PLEIADES_RUN_TOML` for sensitivities), then
  `rerun_reference.py` (`PLEIADES_SURFACE_DIR`), then `d4_figure.py`.
- sha256 (gitignored run tree): `release-grid.f32` af04a2d7…c334 (unchanged); `release-grid-globcurrent-p1d.f32`
  f400ad63…88f1; `release-grid-globcurrent.f32` (pt1h) dafea09c…63e3; reference `likelihood-surface.f32`
  5ffd4f4c…6d05.

## Caveats

- The OU parameters come from undrogued drifters, whose own leeway is not the objects'; the windage mixture
  (0–5 %) is still integrated on top. GlobCurrent's σ/T come from the replay of the DAILY product; they are applied
  unchanged to the hourly table in the sensitivity.
- The replay's 15-day window matches the 15.2-day transport here, so no extrapolation in lead time is needed.
- Isotropic approximation in the two-epoch check (anisotropy ≤ 9 % in σ).
- Reference run fails split-half; eof-2f is provisional; the mode is unconverged.

— Pléiades module
