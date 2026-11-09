# Ocean drift: status (updated 9 November 2026)

Read after `threads/master-prompts/ocean-drift.md`. Replace entries when they change; history is in git and in `coordination/OCEAN_DRIFT.md`.

## Current base
- Impact samples: core run J, end of flight run J, families pooled; 00:19 data held out unless stated.
- Drift code: `hypothesis/debris-drift` at 6f75971 (adds `write_arrivals`, shadow finds with freshness marks, and the offline `rescore` entry; node tables byte-identical).
- Drift run: 84 arc-latitude release points, both ocean models, 16 ocean samples (32 south of 33.25° S), finds window to 30 Jan 2017, every beaching stored (8.0 GB on deskstar).
  Transport and coefficients: `results/drift/drift-extended-window-2026-11-08/` (valid). Scoring, tables and figures: `results/drift/drift-level-prior-correction-2026-11-09/`.
- **9 Nov correction:** the 8 Nov offline rescoring used detection levels constant in time (a default in `rescore_cfg.meta_for`). The module prior
  (period medians 0.1 / 0.5 / 1) is restored; the offline scorer now reproduces module ln L at all 84 points to 1e-6. All 8 Nov rescored numbers are superseded.
- Level marginalisation: use 16,384 draws. The module default of 256 scatters the shift by up to about 0.6°.

## Headline numbers (two ocean models, 50 km kernel, 16,384 level draws)
| Quantity | Value |
|---|---|
| Drift alone, uniform prior along the arc (headline) | median −30.29°, mean −30.57°, 5–95 % −36.37° to −25.15°, 75 % north of 33° S |
| Drift alone vs core: ln R / ln S / p | −0.57 / −1.39 / 0.078 (1.8 σ) |
| Shift of the core mean, headline (twelve identity-weighted items) | +0.82° (mean −35.90°, median −36.69°, north of 33° S 8.5 %) |
| Same, detection constant in time (sensitivity; the 8 Nov defect) | −0.15° |
| Mossel Bay alone; all but Mossel Bay; all but Mossel Bay and Paindane | +1.61°; +0.22°; −0.07° |
| Headline and Australian non-finds, ratio 0.05 / 0.25 / 1 | +1.10° / +1.72° / +2.68° |
| GlobCurrent alone / GLORYS12 alone | +0.78° / +2.35° |
| Satellite fit only (best χ² per band, uniform prior) | median −31.25°; Δχ² ≤ 2.5 from 37.75° to 23.75° S: the core's 36–38° S peak is prior volume and fuel |

## Open items
1. Drift-alone median is uncertain by about ±2° (four-sample subsets 30.4–36.5° S): more ocean samples, or more particles per sample, in the north.
2. Detection-level prior in time is a first-order lever (about 1° on the combined mean): state it as a provisional prior; consider a hierarchical period level.
3. Ocean-model disagreement (GLORYS12 alone further north) and Mossel Bay leverage.
4. Mossel Bay early arrival still under-predicted; wide exterior-panel windage needs a new particle run (separate wide-windage class).
5. Sandravinany and later finds need ocean and wind data after 31 Jan 2017 (GLORYS12, WAVERYS, ERA5) and a new run; GlobCurrent is already downloaded to 31 Dec 2018 (Mac and deskstar).
6. Clean-item time-ashore model: delay-binned rescore (no new particles); fresh-arrival marks reduce the headline shift to +0.22° to +0.32°.
7. Evidence-ledger and suspiciousness figures: recompute with these surfaces, the corrected prior and 16,384 draws.
8. Headline Australian detection ratio: Pete's decision.
9. Biofouling temperature term: needs per-particle temperature along paths (not stored).
