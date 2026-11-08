# Ocean drift: status (updated 8 November 2026)

Read after `threads/master-prompts/ocean-drift.md`. Replace entries when they change; history is in git and in `coordination/OCEAN_DRIFT.md`.

## Current base
- Impact samples: core run J, end of flight run J, families pooled; 00:19 data held out unless stated.
- Drift code: `hypothesis/debris-drift` at 6f75971 (adds `write_arrivals`, shadow finds with freshness marks, and the offline `rescore` entry; node tables byte-identical).
- Drift run: 84 arc-latitude release points, both ocean models, 16 ocean samples (32 south of 33.25° S), finds window to 30 Jan 2017, every beaching stored (8.0 GB on deskstar).
  Results and scripts: `results/drift/drift-extended-window-2026-11-08/`. Segments, periods, window, items, freshness marks and kernel width are exact offline rescorings.
- Level marginalisation: use 16,384 draws. The module default of 256 scatters the shift by up to about 0.6°.

## Headline numbers (shift of the core mean, two ocean models, 50 km kernel, 16,384 level draws)
| Quantity | Value |
|---|---|
| Headline: all coasts, four periods, twelve identity-weighted items | −0.15° (mean −36.87°, median −37.19°, north of 33° S 0.9 %) |
| ln R, core vs uniform on the arc (headline) | +0.85 |
| Mossel Bay alone | +1.11° |
| Headline and Australian non-finds, ratio 0.05 / 0.25 / 1 | −0.05° / +0.19° / +0.57° |
| GlobCurrent alone / GLORYS12 alone | −0.16° / +0.50° |
| Nine finds, old window (to 30 Jun 2016), two independent runs | −0.31° / −0.38° |
| Superseded | +0.61° (7 Nov), +1.17° (8 Nov, 256 draws, three periods) |

## Open items
1. Ocean-model disagreement (GLORYS12 alone north, GlobCurrent alone south) is the largest single uncertainty.
2. Mossel Bay early arrival still under-predicted; wide exterior-panel windage needs a new particle run (separate wide-windage class).
3. Sandravinany and later finds need ocean and wind data after 31 Jan 2017 (GLORYS12, WAVERYS, ERA5) and a new run; GlobCurrent is already downloaded to 31 Dec 2018 (Mac and deskstar).
4. Clean-item time-ashore model: delay-binned rescore (no new particles).
5. Evidence-ledger and suspiciousness figures: recompute with these surfaces and 16,384 draws.
6. Headline Australian detection ratio: Pete's decision.
7. Biofouling temperature term: needs per-particle temperature along paths (not stored).
