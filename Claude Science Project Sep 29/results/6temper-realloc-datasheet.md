# Run datasheet: `6temper-realloc`

Written in simple English. Short sentences. One idea in each sentence.

The run is the project's current best model. It uses the book's priors, two extensions, and a
different sampler. This sheet lists every difference from Davey et al. (2016). It then lists the
run statistics.

Every page number is the printed page in the book. The page comes from the running header of the
page that carries the claim. The PDF-to-printed offset is not constant, so do not convert pages by
adding a number. See `results/davey-page-map.json`.

## 1. Differences from the book

`report/davey_reference.json` holds 43 rows. They divide as follows, and the three counts sum to
43.

| Row type | Count |
|---|---|
| Can be compared by value, and the run **matches** the book | 21 |
| Can be compared by value, and the run **differs** | 4 |
| Prose or identifier, so a value match has no meaning | 18 |
| — of those 18, recorded as departures | 7 |
| — of those 18, recorded as matching | 11 |

The four value differences are the manoeuvre integration step, the initial position standard
deviation, the vertical-rate term in the BFO, and the fuel model. The first three are in table 1a
below. The fuel model is an extension, so it is in table 1c.

The seven prose departures are the prior mean position and track, the R600 BTO noise, the weather
source, the declination source, the resampling scheme, the cost-index speed mode, and the fuel
proposal. The R600 noise is in table 1a because it is a number even though it is read per epoch
from the observations file rather than from a configuration field. The rest are in table 1b.

One inconsistency in the reference file itself, recorded here rather than silently relied on: the
initial Mach set point is stored with status "matching", but its own note calls it a known
departure. The note is right and the status field is wrong. It is listed as a difference in
table 1b.

Table 1b also lists two items that are not in the reference file at all, because they are sampler
changes with no published counterpart to compare against: the tempering and the particle
allocation.

### 1a. Parameter values that differ

| Item | Book | This run | Source | Why |
|---|---|---|---|---|
| Manoeuvre integration step | 1 s | 5 s | p. 59 | This is a fidelity gap. It is not a decision. A 1 s step does 5 times more integration work. Measure the cost before you change it. |
| Initial position standard deviation | 0.4 arcminutes | 0.5 NM | Table 8.2, p. 59 | The book gives 0.4 arcminutes in the table. The book gives 0.5 NM in the text on p. 21. The run uses the text value. |
| Vertical rate in the BFO model | Not modelled | Modelled | pp. 28–29 | This is an extension. See section 2. |
| BTO noise, R600 message | 62 µs | 63 µs | p. 27 | One epoch only, 00:19:29. This is a fidelity gap. The effect is very small. |

### 1b. Methodology that differs

| Item | Book | This run | Source | Why |
|---|---|---|---|---|
| Resampling scheme | Randomised branching. The population size changes. | One filter for each autopilot mode. Systematic resampling. The population size is fixed. | Eq. 8.6, pp. 55–57 | This is the largest methodological difference. It is also the leading candidate for the missing northern shoulder. See `results/shoulder-comparison.md`. |
| Tempering | None | Annealed SMC at six epochs. 16 stages each. | — | This is an extension of the sampler. The target is unchanged. |
| Particle allocation | 1.0 / 0.5 / 2.5 / 0.5 / 2.5 million | The same | Table 8.2, p. 59 | The run returns to the book's allocation. Allocation is a sampling design. It is not a prior. See `results/optimal-allocation.md`. |
| Weather data | ACCESS-G | ERA5 | p. 43 | ACCESS-G is not public. The difference between weather sources is 2–2.4 m/s. The model's own wind error is 5.68 kn. The data difference is smaller than the model error. |
| Magnetic declination | NOAA | IGRF-14 | Fig. 6.2, p. 41 | IGRF-14 is public and documented. |
| Cost-index speed mode | Written, but not used in most experiments | Not written | sec. 6.2.1, p. 39 | The tables are proprietary to Boeing. |
| Prior mean position and track | Shown in a figure only | 5.624829 N, 99.048157 E, track 295.66° | ch. 4, p. 21 | The book does not tabulate these. The values come from the book's own radar figures. |
| Initial Mach | Gaussian, mean 0.82, sd 0.03 | Uniform, 0.73 to 0.84 | Table 8.2, p. 59 | The book's uniform range applies after an acceleration (p. 62). It does not apply to the start. This was tested. The shoulder is 3.5 % either way. |

### 1c. Extensions beyond the book

| Item | What it adds | Source |
|---|---|---|
| Fuel model | The fuel state is carried in the filter. The aircraft must still have fuel at 00:11. The engines should stop near 00:17:30. The book assumes infinite fuel (Assumption 4, p. 60). | Boeing performance tables |
| Endurance proposal | The fuel state enters the proposal. A path stops when no continuation can reach the deadline. New Mach targets come from the speeds the fuel can pay for. The weight correction is exact. | — |
| Vertical rate in the BFO | The cruise BFO carries the vertical speed. The book's compensation omits it. The term is 17.5 Hz for each 1,000 ft/min. | pp. 28–29 |

## 2. Run statistics

| Item | Value |
|---|---|
| Particles in each replicate | 7,000,000 |
| Replicates | 8 |
| Trajectories simulated | **56,000,000** |
| Allocation across modes (M) | 1.0 / 0.5 / 2.5 / 0.5 / 2.5 |
| Measurement case | BTO and BFO |
| Tempered epochs | 18:39, 19:41, 20:41, 21:41, 22:41, 00:11 at 16 stages |
| Wall time | 9.42 h, 1.17–1.20 h for each replicate |
| Peak memory | 14,206 MiB |
| Log evidence | −104.678, range −104.829 to −104.383 |
| Pooling closure error | 8.9 × 10⁻¹⁶ |

### 2a. Convergence

| Item | Value |
|---|---|
| Split-half overlap, mean over all 35 partitions | **0.9109**, range 0.8738 to 0.9398 |
| Calibrated floor at 8 replicates | 0.924 |
| Verdict | Fails by 0.013 |
| Median, half-to-half agreement | 0.043° (2.6 NM) — **converged** |
| 50 % interval bounds, half-to-half | 0.064° and 0.124° — **converged** |
| Peak mass −38.5 to −37, half-to-half | 4.8 % |
| Shoulder mass, half-to-half | 9.2 % — **not converged** |
| Mode probabilities, half-to-half | 6.8 % to 12.9 % — **not converged** |

### 2b. Survival

Effective sample size, as a share of the population, at each epoch:

| Epoch | 18:25 | 18:28a | 18:28b | 18:39 | 19:41 | 20:41 | 21:41 | 22:41 | 23:15 | 00:11 | 00:19:29 | 00:19:37 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ESS | 12.9 % | 67.5 % | 54.5 % | 31.3 % | **5.7 %** | 25.9 % | 45.6 % | 38.5 % | 57.9 % | 11.6 % | 75.8 % | 53.4 % |

Distinct surviving prior draws, for each mode, across the 8 replicates:

| Mode | Particles | Distinct draws |
|---|---|---|
| True track | 2.5M | 1,562–1,754 |
| Lateral navigation | 2.5M | 1,673–1,835 |
| True heading | 1.0M | 922–985 |
| Magnetic heading | 0.5M | 359–429 |
| Magnetic track | 0.5M | 298–356 |

About 4,800 distinct draws survive in each replicate. Each replicate starts with 7,000,000.
Two modes hold 84 % of the probability. Those two modes rest on about 3,300 draws.

### 2c. Posterior at 00:19:29

| Item | Value |
|---|---|
| Median | −37.64° |
| Mode | −37.80° |
| 50 % HDI | [−38.15, −37.10] |
| 90 % HDI | [−39.60, −35.90], with a 0.15° gap near −39.4 |
| 99 % HDI | [−40.15, −33.35] and [−29.85, −26.75] |
| Overlap with Davey Fig. 10.3 | 0.7879 |
| Shoulder mass, −36.5 to −34.5 | 0.1018, which is 42.3 % of Davey's 0.2406 |
| Mode probabilities | True track 0.589, lateral navigation 0.252, true heading 0.103, magnetic track 0.045, magnetic heading 0.011 |

The second 99 % interval is the northern loitering population. It is not a second candidate
terminus. Those paths fly south, turn back, and satisfy the arcs by not covering ground.

### 2d. What the surviving trajectories look like

See `results/realloc-trajectory-statistics.pdf`. All shares are posterior-weighted.

| Item | Result |
|---|---|
| Turn manoeuvres | 1 for 82 %, 2 for 15 %, 3 or more for 2.4 %. Mean 1.22. The minimum recorded is 1. |
| Altitude changes | 0 for 36 %, 1 for 30 %, 2 for 17 %. Mean 1.29. |
| Mach changes | 0 for 35 %, 1 for 31 %, 2 for 17 %. Mean 1.33. |
| Altitude at 00:19:37 | Median 36,800 ft. 5–95 % is 26,900 to 42,000 ft. |
| Mach at 00:19:37 | Median 0.802. 5–95 % is 0.733 to 0.833. |
| Fuel exhausted by 00:19:37 | **36.8 % of the probability** |
| Fuel still aboard | 63.2 %. The mean amount is 6,462 kg over the whole posterior. |
| Exhaustion time, for the paths that ran dry | 95.4 % within 5 minutes of 00:17:30. 95.4 % between 00:11 and 00:19:29. |
| Latitude at 00:19:37 | The paths that ran dry sit near −37.7°. The paths that still held fuel sit near −38.07° and are broader. |

Three limits on the last table. State them with the figure.

1. The size of each manoeuvre is not recorded. Only the number of manoeuvres is recorded, and the
   final altitude and Mach. Two more output columns would record the size of each change.
2. The latitude at fuel exhaustion is not recorded. The figure shows the latitude at 00:19:37
   instead. The two differ by the distance flown between the two times. At the median that is
   about 4.7 minutes, or 0.6° of latitude.
3. The exhaustion time is stored at 128-second resolution. `final.npy` uses `float32`. The
   unit-in-last-place of a `float32` at 1.394 × 10⁹ is exactly 128 s. Only five time slots carry
   probability. The filter uses `f64` internally and is not affected. Store the column as an
   offset from a reference epoch to fix it.

A fourth point is a result, not a limit. 63 % of the posterior still holds fuel at 00:19:37. That
is not consistent with flame-out at 00:17:30. The reason is the shape of the exhaustion term. At
`exhaustion_sd_s = 300`, a path that never runs dry pays only 0.09 nats. See
`results/exhaustion-prior-is-nearly-inert.md`.
