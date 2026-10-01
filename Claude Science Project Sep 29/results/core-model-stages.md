# Three core-model stages: vertical rate, fuel, drifting bias

Each stage is a model the published method does not have, built so the previous one stays
available and the base estimate remains byte-reproducible. Every run carries the parameter table
against Davey, and the new page 3 of each report shows the 00:19 posterior as credible regions
with the run's differences from the book listed beside it.

## Stage 1 — vertical rate in the cruise BFO

### What was wrong

The aircraft's own Doppler compensation does not include the vertical component of its velocity
(book sec. 5.3), so a climbing or descending aircraft leaves an uncompensated vertical Doppler
term in the BFO. Davey's cruise state carries no vertical rate (sec. 7.2) and says so:

> The vertical rate will affect a BFO measurement but since the model only uses a nominal
> vertical rate it is unlikely to match any actual vertical manoeuvre in detail.

The engine inherited that. `crates/mh370/src/filter.rs` passed a literal `0.0` as the vertical
speed to the BFO function at every epoch.

### How small the change turned out to be

The machinery was already present and already used. `satcom::bfo_without_bias_hz` takes a
`v_up_fpm` argument and uses it correctly; `terminal.rs` passes the real value in the
end-of-flight stage; `Aircraft::vertical_speed_fpm` already computed the rate. Only the cruise
call site discarded it. The change is a config flag, `dynamics.bfo_vertical_rate`, defaulting to
false.

**The base run is untouched.** Seed 1 rebuilt after the change reproduces its stored log evidence
exactly — −96.20447573471249, difference 0.000e+00 — so the published model is still reproduced
bit for bit and `make regress` still means something.

### How large the term is

Computed from the engine's own constants and ephemeris at the 00:11 geometry (satellite elevation
38.8°):

**17.50 Hz per 1,000 ft/min**

against a 7 Hz measurement standard deviation, or 0.995 Hz for the genuinely random part. The
engine's 4,000 ft/min climb rate gives 70 Hz. So for a particle in a level change the omission is
an order of magnitude larger than the noise it was being scored against.

### What it did to the posterior: almost nothing, for a reason worth stating

| run | median °S | P(shoulder) | overlap Fig 10.3 | split-half | log Z |
|---|---|---|---|---|---|
| base | −38.160 | 0.0368 | 0.717 | 0.934 | −96.26 |
| base + vertical rate | −38.188 | 0.0359 | 0.709 | **0.945** | −96.30 |
| 4 Hz + 250 kt + 2° + 2,000 ft floor | −37.319 | 0.1970 | 0.764 | 0.927 | −98.02 |
| the same + vertical rate (**stage 1**) | −37.337 | 0.1762 | 0.721 | **0.916** | −98.05 |

The cause is exposure. Measuring the mean number of altitude changes per path from the runs and
the mean size of a change from the prior:

| run | altitude prior | mean changes/path | mean change | time per change | share of flight |
|---|---|---|---|---|---|
| base | 25,000–43,000 ft | 1.68 | 6,000 ft | 90 s | **0.67 %** |
| stage 1 | 2,000–43,000 ft | 1.23 | 13,667 ft | 205 s | **1.11 %** |

A given epoch therefore catches a particle mid-change about one time in a hundred. The term is
correct and the model is better for having it, but it cannot be a lever on the shoulder while
altitude changes are this brief.

**That is the finding, not a disappointment.** It says the descent hypothesis cannot be tested by
adding the term alone: it needs a model in which a descent is *sustained* — a declared
descent-onset latent with its own particle budget, which is the stratum already specified in
`waypoint-stratum-spec.md`. Until then the only place vertical rate changes an answer is the
end-of-flight stage, where it was already being used.

### What it unlocks

The two 00:19 BFO values are excluded from the cruise likelihood because the model could not
represent them. In equivalent vertical rate at 17.50 Hz per 1,000 ft/min:

| quantity | BFO | equivalent rate |
|---|---|---|
| 00:19:29 → 00:19:37 step (182 → −2 Hz, 8 s apart) | 184 Hz | **10,500 ft/min** |
| largest bias excursion in the book's Fig. 5.4 | 20 Hz | 1,140 ft/min |
| one book measurement sd | 7 Hz | 400 ft/min |
| one random-noise sd (0.995 Hz) | 1.0 Hz | 57 ft/min |

A 184 Hz change in eight seconds is about nine times the largest excursion the book's own figure
shows, so a bias excursion cannot produce it and a steep descent can. For the single 00:11 value
the two explanations are not separable: a ±20 Hz excursion and a ~1,100 ft/min descent give the
same signature. That matters because 00:11 is the epoch that decides the autopilot-mode mixture at
roughly 20:1, so part of the shoulder result rests on a quantity degenerate with an unmodelled
bias excursion — which is what stage 3 addresses.

## Stage 2 — the fuel model

### What it is

`crates/flight/src/fuel.rs` ports `.sources/fuel-performance/validate.py`, the version calibrated
against Boeing's figures in Appendix 1.6E of the Malaysian safety report: factor
**1.0085 ± 0.0178** (s.d.) over 11 in-range items, PASS. The port is deliberately literal so the
calibration carries over, and five unit tests check it against the tables, including that asking
for the holding Mach at FL350 and 200 t returns the tabulated holding flow with the 5 % racetrack
allowance removed.

Fuel flow is interpolated between the two bracketing speed schedules — holding, MRC, CI 52, LRC,
M0.84 — at the path's own flight level and gross weight, on a fitted `a M² + b / M²` drag law.
Fuel burns every integration step with the weight falling as it goes. The flow factor is drawn
once per path from N(1.0085, 0.0178), so the posterior integrates over how well the tables
describe this airframe rather than conditioning on the point estimate.

Initial fuel is **36,609 kg**, not the 43,800 kg of the ACARS report: the filter starts at
18:01:49 and the ACARS reading is at 17:06:43. Boeing's own burn for that segment is
43,800 − 33,524 = 10,276 kg over 78.73 min to arc 1, and 18:01:49 is 70.0 % of the way, giving
36,609 kg. An earlier draft used 43,800 at the prior epoch, which handed every path an extra
55 minutes of fuel.

### Three limits of the tables, now recorded per trajectory

1. **Below FL060 only holding is tabulated**, so there is no second point to interpolate against.
   Flow is taken at FL060 and the step flagged. On the holding schedule at 200 t that clamp
   changes the flow by 2.2 % (3,010 kg/h/engine at FL015 against 2,946 at FL060), inside the
   1.8 % spread of the calibration itself.
2. **A single covering schedule** is used directly with no Mach interpolation (FL250–FL290, where
   M0.84, MRC and CI 52 are absent and a filler cell can drop LRC).
3. **The empty cells at high level and high weight are the service ceiling, not a gap.** A 777 at
   210 t cannot reach FL430, which is why those cells are blank. An earlier draft treated them as
   "no coverage" and credited the step with *zero burn*, which made unflyable paths look more
   feasible than flyable ones — 73 % of weight affected, and a median 7,470 kg still in the tanks
   at 00:19. Flow is now taken at the highest level the aircraft could reach and the time is
   accumulated separately.

Limit 3 is worth keeping as a result in its own right: **the published altitude prior is uniform
on 25,000–43,000 ft independently of weight, so it places trajectories above the service ceiling
for part of the flight.** The fuel tables are the only thing in the model that notices.

### What the model says before being told anything

The burn-only run applies no fuel evidence — it just burns. Among paths that ran dry, the weighted
exhaustion quantiles are:

| quantile | exhaustion |
|---|---|
| 5 % | 21:09:20 |
| 25 % | 22:19:44 |
| 50 % | **23:17:20** |
| 75 % | 00:02:08 |
| 95 % | 00:19:12 |

79.2 % of posterior weight runs dry before 00:19:37, and the median does so **an hour before the
00:19 log-on**. That is the wide Mach range doing it: fast flight exhausts the tanks early. So
fuel is a strong constraint on the wide-Mach posterior, which is exactly the constraint Davey's
Assumption 4 substituted the 0.73 Mach floor for.

It also exposes how much of that posterior rests on extrapolation: **73.4 % of weight spends time
at a Mach outside the tabulated schedules**, weighted mean 2.6 hours. The holding Mach at FL350 is
0.749, so a particle at FL350 and Mach 0.50 is far below every schedule, and validation against
Boeing's own out-of-schedule items gave errors to −8.5 %. A wide-Mach run with fuel is therefore
constrained partly by extrapolated flow, and that belongs in the caveats rather than the
conclusions.

### Convergence: the evidence is fine, the sampler was not

| run | split-half | distinct surviving prior draws (TH / MH / TT / MT / LNAV) |
|---|---|---|
| stage 1 | 0.916 | 569 / 289 / 1,050 / 204 / 1,108 |
| fuel, burn only | 0.793 | 556 / 295 / 1,020 / 200 / 1,114 |
| fuel with evidence | **0.743** | **152 / 96 / 314 / 76 / 349** |

The burn model costs nothing in draws. The *evidence* cuts them about 3.3-fold, because the prior
proposes many paths that burn out before 00:11 and `require_power_until` correctly rejects them.
With tens of draws left in MH and MT — the two modes that carry the shoulder — the pooled curve
depends on the seed, and eight replicates did not fix it.

The response was to fix the proposal, not weaken the evidence: equalise the particle allocation
across modes (the base allocation gives MH and MT 0.5 M each against 2.5 M for TT and LNAV, which
starves exactly the two modes the fuel cut hits hardest) and double the total to 2.8 M per mode.
Softening `require_power_until` would have traded the observation that the aircraft transmitted at
00:11 for a convergence statistic.

## Stage 3 — a drifting BFO bias

### The argument

The book models the bias as an unknown constant and states plainly why that is a compromise
(p. 29): "This is a less reliable assumption than for BTO because the bias term changes. To
compensate for this, the measurement variance was inflated from the empirically derived variance."
Table 5.1 gives the measured sd as 4.0192 Hz including tarmac and 4.3177 Hz in flight, both
outliers excluded; 7 Hz was chosen "to be conservative". Fig. 5.4's within-flight variation
reaches ±20 Hz over minutes and "was found to have a geographic dependency" that could not be
quantified.

So the 25 Hz constant-bias prior and the σ inflation are **complementary, not redundant** — the
first handles this flight's offset differing from the tarmac value, the second stands in for the
bias moving during the flight. There is no double count. What there is, is a decorrelation
argument that does not hold everywhere: the book justifies white noise because the BFOs are
"generally at least an hour apart", but three of the eleven sit inside twelve minutes and two are
**nine seconds** apart, and those are the measurements that establish the turn south.

### The model

A random walk on the bias instead of a constant. The step stays linear-Gaussian, so the bias is
still marginalised exactly by the same Kalman recursion and no extra particles are needed — only
the variance grows between epochs, `variance += rate × gap`.

The measurement sd becomes the genuinely random part, **0.995 Hz** (95 % 0.859–1.183), estimated
in prior work in this repository from 78 successive differences inside the 18:39 and 23:14 call
clusters with each cluster's mean removed, so bias drift is excluded from it.

The drift rate is calibrated to reproduce the book's own total uncertainty where the book's
argument holds: with a 0.995 Hz random part and hourly handshakes,
`rate = (7² − 0.995²) / 3600 s = 0.01334 Hz²/s`. That gives

| gap | drift sd | total sd |
|---|---|---|
| 9 s (18:28:05 → 18:28:14) | 0.35 Hz | **1.05 Hz** |
| 701 s (18:28 → the 18:39 call) | 3.06 Hz | 3.22 Hz |
| 510 s (00:11 → 00:19) | 2.61 Hz | 2.79 Hz |
| 3,600 s (hourly arc) | 6.93 Hz | **7.00 Hz** |

It matches the published model exactly at an hourly spacing and is tighter only where the
decorrelation argument fails. Note the direction: the constant-bias model with a flat 7 Hz
*under-uses* the early cluster, because it inflates each of those three measurements independently
when they share almost the same bias realisation.

