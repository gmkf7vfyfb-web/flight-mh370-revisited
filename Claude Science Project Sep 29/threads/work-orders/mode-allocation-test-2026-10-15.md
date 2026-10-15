# Mode-allocation test for run J (proposal; needs Pete's GO). 15 October 2026

**Question.** The northern posterior mass is noisy because each seed's mode probabilities are noisy (about 80% of the variance), and that noise enters at the 00:11 increment (`results/composer-north-ess-run-i.md`). Does it fall with more particles in a mode? If yes, re-allocating particles across modes is an exact, prior-neutral fix that run J can use. If no, only seeds help, and run J's seed budget must favour waypoints.

**Why it is exact.** Each guidance mode is a separate filter. The mixture is weighted by mode evidence × mode prior, so the number of particles per mode changes noise only, not the target. No latitude is named.

## Arms (repro-radar stratum, run I stack exactly as `job-run-i.sh STRATUM=repro`, BFO and data as run I so the comparison with run I's 8 seeds is like for like)
Mode order in `particles_per_mode`: [TrueHeading, MagneticHeading, TrueTrack, MagneticTrack, LateralNavigation]. Run I repro: [500k, 250k, 1.25M, 250k, 1.25M] = 3.5M.

| Arm | particles_per_mode | Total | Seeds | Purpose |
|---|---|---|---|---|
| I (exists) | run I | 3.5M | 1–8 | baseline, no new run |
| S (scaling) | run I × 2 = [1M, 0.5M, 2.5M, 0.5M, 2.5M] | 7M | 11–18 | does the per-mode ln Z noise fall like 1/√N? |
| R (re-allocated) | [0.35M, 0.75M, 1.1M, 0.75M, 0.55M] | 3.5M | 21–28 | same cost, 3× the magnetic modes |

New seed numbers make the arms independent of run I and of each other. One heavy job, under the lock. About 50 min (R) + 100 min (S) at 88 threads.

## Measurements (per arm, 8 seeds; script on the Mac from `diagnostics.json` and `handoff-m0011`)
1. ln Z seed sd per mode, and of the 00:11 increment per mode.
2. Mode probabilities: median and range.
3. Northern mass at the 00:11 hand-off (north of 33 S and of 30 S): mean, seed sd, implied effective sample (8 p(1 − p)/var × p).
4. The same split as in the note: seed sd with mode probabilities held fixed, and with within-mode shares held fixed.
5. Posterior median latitude and the stratum ln Z, against run I (must agree within seed noise: exactness check).

## Predictions (posted before the run)
- If the noise is particle-limited: S reduces every mode's ln Z sd by about ×0.71, and the northern sd by about ×0.71. R reduces the magnetic modes' ln Z sd by about ×0.58 and the northern sd by ×0.6–0.8, with the true-track and lateral-navigation sd up by about ×1.1–1.5.
- If it is structural (path-space, set before 00:11): S changes the per-mode ln Z sd by less than ×0.9, and R does not reduce the northern sd.

## Decision rule for run J
- **Particle-limited:** run J uses the re-allocated proportions in every stratum. Sized by Neyman allocation from the measured sd: n_m ∝ |∂(north)/∂ln Z_m| × σ_m √n_m, with a floor for the main-mode headline.
- **Structural:** run J keeps run I's allocation, and the seed budget moves to waypoints, which is 99.7% of the composed product. The northern result is reported with its seed-bootstrap interval.
