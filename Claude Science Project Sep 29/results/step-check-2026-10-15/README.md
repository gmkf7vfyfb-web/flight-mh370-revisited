# Audit F3: propagation step size (1 s against the default 10 s cruise / 5 s manoeuvre)

Pure reproduction (`config/davey2016-inmarsat.toml`, BFO sd 7 Hz), 4 seeds x 7M, deskstar 88 threads.
1 s: job cae37735, bin-b857425, `config/sensitivity/step-check/repro-step1.toml` (46 min).
Default steps: job ac952234 (`repro-bfo7`, 8 min). Same base and seeds; not byte-comparable.

| Step | ln Z | Shoulder 34.5–36.5 S | Median | 2.5% | 97.5% | Overlap with Davey | Split-half |
|---|---|---|---|---|---|---|---|
| 10 s / 5 s (default) | −97.128 | 0.0783 | −37.952 | −39.438 | −34.876 | 0.750 | 0.936 |
| 1 s (Davey et al. 2016) | −97.163 | 0.0769 | −37.968 | −39.422 | −34.872 | 0.754 | 0.945 |

- Difference in ln Z −0.035 nat; standard error from the seed spread 0.026 (z = −1.3).
- PDF overlap 1 s against default: 0.966, the same level as Monte Carlo noise (split-half 0.94).
- Mode probabilities agree to within 0.005.

**Result:** no step-size effect is detectable. The default steps stay for run J. The step size does
not explain why the reproduction's shoulder (0.08) is a third of Davey's (0.24).

STE100 note: we flew the same test with 1-second steps. The answer did not change.
Technical note: 4 x 7M particles; differences are within seed-to-seed Monte Carlo noise.
