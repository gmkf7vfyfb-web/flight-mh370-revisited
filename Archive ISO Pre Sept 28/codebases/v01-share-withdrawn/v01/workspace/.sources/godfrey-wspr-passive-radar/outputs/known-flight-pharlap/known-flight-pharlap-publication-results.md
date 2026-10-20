# PHaRLAP-filtered known-flight control results

Counts in each triplet are minus 60 minutes / arc-time window / plus 60 minutes. The effect is the arc-time residual count minus the mean of the two controls.

| Scope / BTO epoch | Propagation screen | Raw clusters | Residual clusters | Residual effect | Withheld reference recovered | One-sided actual-excess p |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Pooled (six epochs) | Surface endpoint | 7 / 0 / 6 | 7 / 0 / 6 | -6.5 | 0/6 | 1.000 |
| Pooled (six epochs) | Common aircraft altitude | 14 / 7 / 25 | 9 / 6 / 22 | -9.5 | 0/6 | 1.000 |
| MH371 04:04:09 UTC | Surface endpoint | 0 / 0 / 0 | 0 / 0 / 0 | +0.0 | 0/1 | — |
| MH371 04:04:09 UTC | Common aircraft altitude | 1 / 0 / 0 | 1 / 0 / 0 | -0.5 | 0/1 | — |
| MH371 06:11:01 UTC | Surface endpoint | 0 / 0 / 3 | 0 / 0 / 3 | -1.5 | 0/1 | — |
| MH371 06:11:01 UTC | Common aircraft altitude | 0 / 0 / 3 | 0 / 0 / 3 | -1.5 | 0/1 | — |
| MH371 06:48:31 UTC | Surface endpoint | 0 / 0 / 2 | 0 / 0 / 2 | -1.0 | 0/1 | — |
| MH371 06:48:31 UTC | Common aircraft altitude | 0 / 0 / 6 | 0 / 0 / 6 | -3.0 | 0/1 | — |
| MH370 16:42:32 UTC | Surface endpoint | 3 / 0 / 1 | 3 / 0 / 1 | -2.0 | 0/1 | — |
| MH370 16:42:32 UTC | Common aircraft altitude | 5 / 3 / 9 | 2 / 3 / 7 | -1.5 | 0/1 | — |
| MH370 16:55:53 UTC | Surface endpoint | 2 / 0 / 0 | 2 / 0 / 0 | -1.0 | 0/1 | — |
| MH370 16:55:53 UTC | Common aircraft altitude | 2 / 2 / 6 | 1 / 2 / 5 | -1.0 | 0/1 | — |
| MH370 17:07:19 UTC | Surface endpoint | 2 / 0 / 0 | 2 / 0 / 0 | -1.0 | 0/1 | — |
| MH370 17:07:19 UTC | Common aircraft altitude | 6 / 2 / 1 | 5 / 1 / 1 | -2.0 | 0/1 | — |

The p-values are exact sign-flip diagnostics across epoch effects and are reported only for pooled rows. They are exploratory because radio windows overlap; the dependence-conservative three-connected-window sensitivity gives one-sided actual-excess p = 1.000 for both screens. The two-sided epoch values (0.0625 surface; 0.03125 altitude) describe actual-time deficits, not aircraft-specific excesses.
