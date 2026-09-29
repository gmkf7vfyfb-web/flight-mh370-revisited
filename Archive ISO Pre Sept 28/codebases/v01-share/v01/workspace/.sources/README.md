# Paper-to-code sources

This directory holds source-specific recreations outside the product workspace.
Nothing here is imported by the runner or executed by the root test suite.

| Bundle | Independent result | Estimator use |
| --- | --- | --- |
| `davey-2016-bayesian-search` | Published-parameter reconstruction agrees near the central latitude but fails the full-distribution and cross-seed comparison. | Not integrated; the canonical flight estimator uses a smaller tempered model. |
| `iannello-2016-end-of-flight` | Five public simulator cases reproduce the reported high-rate classification and a 4.707–7.974 NM distance to the last recorded point. | Available only as an explicitly selected conditional displacement model. |
| `ulich-2023-ocean-drift` | Compact HYCOM and GDP family surfaces are preserved separately. The latest surface remains a diagnostic because rare-event and isotope refinement did not complete. | Loaded for comparison, but `admitted = false` in production. |
| `kadri-2024-hydroacoustics` | Publication-vector traces show a periodic airgun coincidence and substantial method sensitivity. | Geometry overlay only; never treated as an independent detection likelihood. |
| `large-2019-antenna-gain` | Held-out prediction does not stably distinguish the two gain-precompensation endpoints. | Excluded from unconditional core use; MH371 can explicitly run the full- and no-precompensation endpoint likelihoods as separate conditional controls. |
| `godfrey-wspr-passive-radar` | The published 48-flight data show weak target-conditioned discrimination, but blind spatial ranks, trajectory controls, BTO-arc controls and known-flight controls do not localize aircraft above matched noise. | Not integrated; WSPRnet spot metadata have no calibrated blind aircraft-location likelihood under the publicly specified method. |
| `pleiades-bran2016-forward-inversion` | The primary conditional BRAN mode is 35.4179°S, 92.8858°E with a 24,309 km² 90% HPD; diffusion and object-set sensitivities are material. OSCAR v2 Final remains unevaluated pending authenticated access. | Not integrated; image identity/detection calibration and the independent current-family control are incomplete. |

Every bundle uses the same layout: `paper/`, `code/`, `data/`, and
`outputs/`, plus a local README and SHA-256 inventory. Large historical
workspaces and raw collections are kept outside this lean repository; bundle
READMEs state the exact boundary.
