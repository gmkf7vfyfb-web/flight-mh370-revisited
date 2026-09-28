# Reconstructed v12 / ERA5 results

These are actual weighted outputs of newly reconstructed code, not recovered historical v12 outputs. **A stable reproduction of Davey Fig. 10.3 has not been established.** The scientific target should not be marked complete merely because the batch finished.

| Run | Smoothed mode latitude | Southern probability | Largest initial ancestor weight | Effective initial ancestors |
|---|---:|---:|---:|---:|
| mh370_era5_100000_101_bto | 42.275° | 0.2233 | 0.5984 | 2.58 |
| mh370_era5_100000_101_bto_bfo | -36.625° | 1.0000 | 0.7814 | 1.59 |
| mh370_era5_100000_202_bto | -37.325° | 0.9812 | 0.7449 | 1.76 |
| mh370_era5_100000_202_bto_bfo | -37.225° | 1.0000 | 0.8569 | 1.35 |
| mh370_era5_300000_303_bto | -38.525° | 0.9385 | 0.5673 | 2.51 |
| mh370_era5_300000_303_bto_bfo | -38.525° | 1.0000 | 0.6827 | 2.05 |

Latitude is signed (negative = south). The mode uses a fixed 0.35° Gaussian display bandwidth. The probabilities and ancestor weights use the raw weighted particles. Initial ancestors are a useful depletion diagnostic, not a complete definition of independent trajectories: descendants continue to draw different later manoeuvres.

## Between-run differences at 00:19

| Treatment | Runs | Wasserstein distance (degrees) | Smoothed total variation |
|---|---|---:|---:|
| BTO only | N=100000, seed 101 / N=100000, seed 202 | 54.691 | 0.888 |
| BTO only | N=100000, seed 101 / N=300000, seed 303 | 57.114 | 0.833 |
| BTO only | N=100000, seed 202 / N=300000, seed 303 | 5.797 | 0.625 |
| BTO+BFO | N=100000, seed 101 / N=100000, seed 202 | 0.682 | 0.481 |
| BTO+BFO | N=100000, seed 101 / N=300000, seed 303 | 1.784 | 0.813 |
| BTO+BFO | N=100000, seed 202 / N=300000, seed 303 | 1.487 | 0.756 |

At 100,000 particles the two BTO-only runs place approximately 22% and 98% of their mass in the south. The two BTO+BFO runs both select the south but differ in shape (about 0.48 smoothed total variation); their largest initial ancestors carry approximately 78% and 86% of the weight. Similar mean latitudes therefore do not establish agreement. The larger-run results above must be assessed against both replicates, not selected because they resemble the published figure.

No stable northern shoulder is established by the present checks. Any small shoulder in an individual curve may reflect retained early trajectories. The refined comparator contains northern Gaussian components by construction and cannot independently confirm the feature.

The executable reconstruction, tests and dense MH371 checks are substantial progress, but the fixed-population accident sampler remains a numerical limitation. Broader, correctly weighted trajectory proposals or source-style branching, followed by new convergence tests, are needed if larger counts continue to show depletion. Arbitrary state jitter or pooling the curves would conceal rather than resolve the issue.

## Files

* `mh370_fig10_3_analogue.png`: BTO-only and BTO+BFO at 00:19, full latitude range plus southern detail; separate runs.
* `mh370_refined_comparison_0011.png`: same-epoch comparison with the recovered no-drift summary-based refined output.
* `latitude_pdfs.csv` and `posterior_summary.json`: plotted densities and numerical diagnostics.
* `../README.md`: assumptions, departures from Davey, inputs and rerun instructions.
* `../BFO_AND_CHECKPOINT_NOTES.md`: exact recovered BFO choices and the missing checkpoint limitation.
* `../../mh370_v12_reconstruction_era5.zip`: portable source/input/evidence/finished-checkpoint bundle, with SHA256 inventory.

The original full source was not recovered. ERA5, public TLE geometry and the reconstructed radar mean are disclosed substitutions; this is not an exact original-source or operator-data reproduction.
