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

## All runs

Overlap is against the digitised Davey Fig. 10.3. Log evidence is comparable only within a fixed
observation model, so the fuel and bias rows are not comparable with the rows above them: both
change the likelihood's normalisation.

| run | median °S | P(shoulder) | overlap | split-half | log Z | draws MH / MT |
|---|---|---|---|---|---|---|
| base | −38.160 | 0.0368 | 0.717 | **0.934** | −96.26 | 251 / 181 |
| vertical rate only | −38.188 | 0.0359 | 0.709 | **0.945** | −96.30 | 223 / 168 |
| **stage 1** | −37.337 | 0.1762 | 0.721 | **0.916** | −98.05 | 289 / 203 |
| fuel, burn only | −37.319 | 0.1713 | 0.719 | 0.793 | −98.04 | 295 / 200 |
| **stage 2**, 7 M/mode | −37.306 | 0.1954 | 0.636 | 0.743 | −106.19 | 96 / 76 |
| stage 2, 14 M equal | −37.319 | 0.2479 | 0.625 | 0.755 | −106.15 | 531 / 380 |
| **stage 3**, 14 M equal | −37.721 | 0.1720 | **0.792** | 0.669 | −104.57 | 600 / 399 |

Two things stand out.

**The stage-3 combination gives the best agreement with the published curve of any run so far** —
overlap 0.792 against the base 0.717 and the previous best 0.789 — and it does so while *raising*
the evidence relative to stage 2 (−104.57 against −106.15, comparable because both use the same
observation model). It is **not converged**, so this is a lead rather than a result.

That agreement belongs to the combination, not to the drifting bias. Run on its own, the drifting
bias does the opposite:

| run | median °S | P(shoulder) | overlap | split-half | posterior BFO bias |
|---|---|---|---|---|---|
| base (constant bias, 7 Hz) | −38.160 | 0.0368 | 0.717 | 0.934 | 150.13 ± 0.37 Hz |
| drifting bias alone (0.995 Hz + drift) | −38.373 | **0.0260** | **0.634** | **0.950** | 145.22 ± 1.47 Hz |

The drifting bias **reduces** the shoulder, from 0.0368 to 0.0260, and moves *away* from the
published curve. The mechanism is the one the calibration predicts: it makes the early cluster
more informative, because three measurements nine seconds and twelve minutes apart share one bias
realisation instead of being inflated independently. Used efficiently, that cluster constrains the
turn south more tightly and pushes the posterior slightly south. The posterior bias is estimated
5 Hz lower than under the constant model and with four times the spread, which is the drift
correctly declining to pin down a quantity that moves.

**Stage 1 converged; stage 3's mechanism converges on its own, better than anything else tried
(split-half 0.950); stages 2 and 3 as cumulative runs did not.** The honest boundary is that the
fuel evidence, not the vertical-rate term and not the drifting bias, is what breaks convergence.

## Why stages 2 and 3 did not converge, and what was tried

Three attempts, in order:

1. **More replicates.** Stage 2 at 8 seeds: split-half 0.743.
2. **More particles and a fairer allocation.** The base allocation gives MH and MT 0.5 M each
   against 2.5 M for TT and LNAV, which starves the two modes carrying the shoulder — and those
   are the modes the fuel cut hits hardest. Equalising at 2.8 M per mode, 14 M total, did exactly
   what it was meant to: surviving prior draws in MH went 96 → 531 and in MT 76 → 380. Split-half
   moved 0.743 → 0.755. So the draw count was not the binding constraint.
3. **Drop the weaker evidence term.** The exhaustion-timing Gaussian targets 00:17:30 ± 300 s
   while the burn model's own weighted median exhaustion is 23:17:20 — twelve standard deviations
   away, keeping a 14.6 % slice of weight — so it looked like the culprit. It is not: removing it
   and keeping only the hard requirement gives split-half 0.740, no better than 0.755 with it.

   The binding cut is the hard requirement itself. Measured on the burn-only run,
   **69.0 % of posterior weight sits on paths whose tank ran dry before 00:10:59**, so
   `require_power_until = m0011` discards about seven paths in ten. That is the correct thing to
   do — those paths cannot have sent the 00:11 transmission — but it leaves a small, seed-dependent
   survivor set, and no particle budget fixes a proposal that is wrong about most of its mass.

| attempt | split-half |
|---|---|
| stage 1, no fuel | **0.916** |
| fuel burn, no evidence | 0.793 |
| fuel + both terms, 7 M/mode, 8 seeds | 0.743 |
| fuel + both terms, 14 M equal | 0.755 |
| fuel + hard requirement only, 14 M equal | 0.740 |

The underlying conflict is between the fuel model and the wide-Mach prior. The prior proposes
fast paths; fuel says fast paths cannot reach 00:19. The posterior is the narrow intersection, and
the prior is a poor proposal for it. Davey's Assumption 4 made the 0.73 Mach floor a stand-in for
the fuel constraint, so with fuel modelled the floor and the fuel model are two statements of one
thing — which means the self-consistent configuration is fuel *with* a feasible speed prior, not
fuel fighting a deliberately widened one.

Two further runs follow from that diagnosis rather than from trial and error:

- `stage2-fuel-hardonly` keeps only the hard observation — the aircraft transmitted at 00:11, so a
  path whose tank ran dry earlier contradicts the data — and drops the timing Gaussian, which is
  an inference about APU and SDU start-up rather than a measurement.
- `stage2-fuel-narrowmach` restores the book's Mach range and altitude floor, so the fuel model
  replaces the role Assumption 4 gave the Mach floor instead of competing with a widened prior.

### The narrow-Mach result, and what it says about Assumption 4

Restoring the book's own Mach range and altitude prior, so fuel takes over the role Assumption 4
gave the 0.73 Mach floor instead of fighting a widened one:

| run | median °S | P(shoulder) | overlap | split-half | weight rejected at 00:11 | draws MH / MT |
|---|---|---|---|---|---|---|
| base, no fuel | −38.160 | 0.0368 | 0.717 | 0.934 | — | 251 / 181 |
| fuel, wide Mach | −37.328 | 0.2406 | 0.622 | 0.740 | 6.2 % | 531 / 380 |
| **fuel, book's Mach range** | −37.828 | **0.0868** | **0.791** | **0.829** | 1.9 % | **978 / 711** |

This is the most informative run of the three stages. With **no prior widened at all** — Davey's
Mach range, Davey's altitude prior, Davey's track standard deviation, Davey's 7 Hz BFO — simply
adding the fuel model moves the shoulder from 0.0368 to **0.0868**, a factor of 2.4, and improves
agreement with the published curve from 0.717 to **0.791**, the best of any run in the project.

That is fuel acting as *evidence* rather than as a relaxed assumption, and it bears directly on
Assumption 4. The book substitutes the Mach floor for a fuel constraint and then notes
(Assumption 7) that low speeds "cannot match the measurements". With the real constraint in place
the two are not equivalent: endurance admits a different set of trajectories than a speed floor
does, and the set it admits sits further north.

It is still short of the 0.90 convergence floor at four replicates, but the diagnostics say the
remaining gap is pooling noise rather than a starved sampler: 978 and 711 surviving draws in MH and
MT, the most of any fuel run, and only 1.9 % of weight rejected by the power requirement against
6.2 % under the wide prior. An eight-replicate run is in progress, together with stage 3 applied to
this configuration rather than to the wide one.

### Reportable position

The fuel model is implemented, ported literally from the version calibrated against Boeing's own
figures, validated by unit tests against the tables, and produces a physically sensible burn:
median exhaustion 00:14:56 with the evidence applied, 359 kg remaining at the final step, and a
weighted median of 23:17:20 before any fuel evidence is applied at all.

Combining it with a *widened* speed prior does not converge at this particle budget, and the
wide-Mach fuel numbers — shoulder 0.24 — should be quoted as an upper bound, not an estimate.
Combining it with the book's own priors is close to converged and is the result worth carrying
forward.

