# Why the northern shoulder is missing: this code against Davey et al. (2016)

> **Citation audit, 5 October.** This file was written before the book was obtained and cited
> **PDF positions**, not printed pages. Every page reference has been re-derived by locating the
> cited claim's anchor text in the book and reading off its printed page; the corrections are not
> a uniform offset: the PDF-to-printed offset is itself 13 in chapters 4–6 and 10, and 14 in
> chapters 7–8, and the original numbers carried a further one to two pages of slop. Each page
> below was read off the running header of the page carrying the anchor text. Figure,
> table and equation numbers are unaffected. The acceleration rate, previously cited to a page
> that does not state it, is verified at p. 49: "The assumed rate corresponds to a change of Mach
> of 0.1 in one minute."

A line-by-line comparison of `crates/flight`, `crates/satcom` and `crates/mh370` against the
book's chapters 3, 5–8 and 10, plus a re-check of the eliminations recorded in
`engine/status.md`. Book page references are to `.sources/davey-2016/paper.pdf` (124 pp.).

**The gap.** Base run, 8 replicates × 7M particles: 3.68% of probability in 34.5–36.5°S; the
book has 25%. Median 38.160°S against the book's 37.53°S; the two curves overlap by 0.717.

## 1. Parameters that agree exactly

Every published constant I could check is transcribed correctly. These are not candidate causes.

| Quantity | Book | This code |
|---|---|---|
| Mach OU β, q | 1.058e-2, 2.05e-7 (p. 38) | identical; steady-state sd 0.0031126 vs book 0.003113 |
| Control-angle OU β, q | 9.792e-3, 4.074e-8 (p. 39) | identical; sd 0.0826° vs Table 8.2's 0.0826° |
| Wind-error OU β, q | 1.087e-3, 0.07021 (Table 8.2, p. 59) | identical; sd 5.683 kn vs book 5.684 kn |
| Manoeuvre clock | three independent exponential processes sharing one τ, `exp(-3T/τ)` (Eq. 7.5) | three clocks (`next_turn`, `next_acceleration`, `next_climb`), exposure summed over all three in the τ Gibbs update |
| τ prior | Jeffreys on 0.1–10 h, one draw per trajectory (Eq. 7.6) | `tau_range_h = (0.1, 10.0)`, drawn once, log-uniform |
| Turn extent | uniform ±180°, 15° bank (p. 49) | identical |
| Acceleration rate | Mach 0.1 per minute (p. 49) | `mach_rate_per_s = 0.1/60` |
| Vertical rate | 4,000 ft/min (p. 49) | `climb_rate_ft_per_s = 4000/60` |
| Altitude | uniform 1,000 ft steps, 25,000–43,000 ft (p. 49) | identical |
| LNAV reversion | exponential, mean 6/ln2 h, to true or magnetic heading (p. 43) | `lnav_switch_mean_s = 6/LN_2 * 3600`; P(switch in 6 h) = 0.5000 |
| BTO fixed term | T_nom 499,962 µs, T_channel(R1200) −4,283 µs (p. 26) | 495,679 µs = T_nom + T_channel, the combination that reproduces logged BTOs |
| BTO noise | R1200 29 µs, anomalous R1200 43 µs (p. 27) | 29 and 43 µs |
| Cruise time step | 10 s (p. 45) | `cruise_step_s = 10.0` |

## 2. Discrepancies found, all too small to matter

- **R600 BTO sd is 63 µs here, 62 µs in the book** (p. 27). Affects only the 00:19:29 R600
  message. A 1.6% change in one σ on one epoch.
- **Manoeuvre integration step is 5 s; the book uses 1 s** (p. 59, "a sequence of 1 s steps").
  At 500 kt and 15° bank the turn rate is ~0.6°/s, so a step turns 3°; the chord-versus-arc
  error over a 90° turn is on the order of 0.1 NM, against a 29 µs BTO σ of about 2.3 NM.
- **Initial position sd is 0.5 NM; Table 8.2 gives 0.4 arcminutes.** Slightly wider.

None of these is worth 3.68% → 25%. Fixing the first two is cheap and worth doing for fidelity,
not as a shoulder hypothesis.

## 3. Prior eliminations: re-checked

Confirmed as genuinely eliminated, and for the right reason:

- **Initial Mach.** `hypotheses/initial-mach` already tests exactly Table 8.2's initialisation —
  Gaussian N(0.82, 0.03) rather than uniform 0.73–0.84 — and records shoulder 3.5% vs 3.5%.
  This is the correct reading of the book: the uniform 0.73–0.84 applies to Mach *after an
  acceleration* (p. 49), while initialisation is Gaussian (Table 8.2). The distinction was not
  missed.
- **Altitude prior, declination sign, satellite ephemeris, weather model.** All tested; the
  ephemeris result in particular is the informative one — a near-uniform offset moves every arc
  together and every mode with it, so it cannot change the mode mix.

One elimination has now been completed that was previously only partial:

- **Declination generation — tested, and it is not the cause.** `status.md` recorded only that the
  grid "matches IGRF-14 exactly" and a sign-reversal diagnostic; the *generation* had never been
  varied. Davey's reference [31] is NOAA's IGRF grid calculator
  (`ngdc.noaa.gov/geomag-web/#igrfgrid`), not the World Magnetic Model, and in 2014 that
  calculator served **IGRF-11**, whose last main-field epoch is 2010.0 — a March 2014 value was
  extrapolated 4.19 years on predicted secular variation. IGRF-12 was agreed only in December
  2014. The official NOAA package already in `.sources` ships `SHC_files/IGRF1..14.SHC`, so the
  field the book's source would have returned is reproducible exactly;
  `.sources/igrf14-declination/build_generation.py` builds it with `build.py`'s own synthesis.

  The difference looked promising a priori. At FL350 on 2014-03-08, IGRF-11 minus IGRF-14 is mean
  −0.108° and at most 0.154° over 40°S–8°N/85–105°E, and mean −0.088° over the 30–37°S corridor,
  against a control-angle OU steady-state sd of 0.0826° — a spatially coherent bias of about one
  sigma of the angle process, sustained for six hours, and applied only to the two magnetic modes
  that carry P(shoulder | mode) of 0.52 and 0.55. IGRF-12 minus IGRF-14 is at most 0.010°.

  The run says no. `declination-igrf11` (4 × 7M, converged, split-half 0.923): shoulder
  **0.0369 against the base's 0.0368**, overlap with the book 0.714 against 0.717, median
  −38.180° against −38.160°, log-evidence +0.035. The magnetic modes gain almost nothing —
  combined weight 0.0178 → 0.0205. The reason is arithmetic: those modes hold under 2% of the
  posterior, and closing a 3.7%-to-25% gap needs them to gain +1.6 to +2.8 in log-evidence, which
  0.09° of declination bias does not come close to delivering. Declination is eliminated as a
  candidate, and IGRF-14 remains the better model for the epoch on its own merits.

One elimination is weaker than it looks:

- **Turn counts.** `status.md` uses the turn-count histogram as evidence for the sparse-filter
  explanation (this recreation 12% with ≥2 turns, the book 49%). But the book says of that same
  figure: around half the paths made more than one turn, and this "would appear to be of interest
  but is in fact misleading" — Fig. 10.5 shows the double turns are single turns split into two
  segments, and there are "very few genuine turns later in the flight" (p. 92). So the 49% is
  not a count of genuine manoeuvres and the 12-vs-49 gap is partly definitional. The
  sparse-filter argument should not lean on it.

One elimination rests on a global statistic where a local one is needed:

- **Weather.** ERA5, NCEP FNL and MERRA-2 were compared by global RMS wind difference (2–2.4 m/s,
  below the model's own 2.9 m/s wind-error sd) and declared equivalent. That is an average over
  the globe. The shoulder is made by wind-drifted heading paths in a specific corridor — roughly
  30–37°S, 85–95°E, FL300–400, 19:41–00:11 — and a few knots of *correlated* difference there,
  in the right direction, is not excluded by a global RMS. ACCESS-G remains the direct test and
  is still outstanding. A cheaper interim check: compare the three fields restricted to that
  corridor and those hours, along the shoulder-bound paths themselves.

## 4. The lever nobody has pulled: the BTO error model

The book names it explicitly. Assumption 2 (p. 60): the BTO and BFO standard deviations are
"provided to the algorithm as a known input", and "minor inflation of the assumed BTO variance
would lead to incremental changes in the filter output". No run in this project has inflated the
BTO variance, and no hypothesis directory tests it.

It is the mechanically right knob. The measured late-arc penalties are −2.2 (true heading), −5.1
(magnetic heading) and −3.6 (magnetic track) in log-evidence relative to true track, arising at
the 22:41, 00:11 and 00:19 arcs. The mode mix that reproduces the book's curve (92% overlap)
needs heading and magnetic modes to gain +1.6 to +2.8 — "almost exactly the late-arc penalty we
measure". Penalties of that size come from BTO residuals of a few hundred µs against a 29 µs σ.
Inflating σ shrinks all three penalties toward zero and flattens the mode mix, which is what
restores the shoulder.

The book also supplies a physical reason to think the assumed σ is too tight, and it is not white
noise. Fig. 5.2's residual histogram "has an underlying mean of 10 µs… due to the channel
dependent calibration term T_channel not being stationary", and Fig. 5.3 plots BTO errors
drifting across the 20 flights over six days (p. 27). A non-stationary channel calibration is a
*slowly varying bias*, and this filter marginalises a BFO bias but no BTO bias at all.

The distinction matters, and it is what makes this different from the ephemeris test already run:

- a **constant** BTO offset moves every arc the same way, so all modes shift together — already
  tested via the Inmarsat-versus-STK ephemeris (shoulder 2.9% vs 3.5%, no effect on the mix);
- a **drifting** BTO bias lets a path sit off the 22:41 arc one way and off the 00:11 arc the
  other. That is precisely the freedom a wind-drifted heading path needs, and it has never
  been tested.

Two concrete runs, in order:

1. `bto-inflated`: σ_BTO × k for k ≈ 1.5, 2, 3, everything else fixed. Cheap, no core change
   (a sensitivity config), and it bounds how much of the gap the BTO error model can explain.
2. `bto-bias-walk`: a per-flight BTO bias as a random walk (or OU) marginalised per particle by
   Kalman filter, exactly as the BFO bias already is. This is a core change and needs the change
   protocol. Calibrate its process noise on the 20 prior flights in Fig. 5.3 rather than fitting
   it to the accident flight — that keeps it non-circular.

Do (1) first: if σ inflation alone moves the shoulder materially, (2) becomes the principled
version of the same effect rather than a speculation.

## 5. A methodological difference in the sampler, with a predictable direction

This is not a bug in either implementation, but it does explain a flatter mode mix in the book.

The book's resampler is not the conventional one. Per Eq. 8.6 and step 4e (pp. 56–57): a particle
whose accumulated weight is at least η is branched n̄ times with weight w/n̄; a particle below η
is branched **once with probability w and given weight 1**, otherwise pruned. Table 8.2 gives
n̄ = 3–10 and η = e⁻²⁵ or e⁻³⁰. Weights are unnormalised until the final step (p. 58).

Two consequences:

- The scheme is unbiased — E[Σw̃f] = Σwf, as the book shows in Eq. 8.5 — but promoting a survivor
  to **unit weight** makes it heavy-tailed. A path from a low-evidence mode that wins the
  roulette carries the same weight as the best path in the population, and a handful of such
  survivors can carry visible mass in the final normalised pdf.
- With weights unnormalised and η absolute, essentially every path is in the roulette regime.
  A single BTO epoch at σ = 29 µs contributes at most ln(1/(29√2π)) = −4.286 even at zero
  residual, and the ten epochs that carry a BTO have σ = 29 µs (seven), 43 µs (two) and 63 µs
  (one), so a *perfect* path accumulates ln L = −44.43 on the BTO terms alone, and −75.94 once
  the eleven BFO terms at 7 Hz are included. Either figure is already past both e⁻²⁵ and e⁻³⁰.
  So survival is being decided by roulette, and in that regime the mode mix is set by survival
  counts rather than by likelihood ratios.

This code does the opposite, and does it deliberately: one fixed-size filter per autopilot mode,
systematic resampling whenever ESS falls below 50%, and modes combined in proportion to their
estimated marginal likelihood. That is the cleaner Bayesian combination, and it applies the full
e^(−2.2) to e^(−5.1) mode penalty. The book's roulette largely does not.

The predicted direction is exactly what is observed: reweighting this project's particles to
**equal** mode weights gives a shoulder of 27% and 86% overlap with the book — against 3.68% and
0.717 as combined by evidence. The book's own sampler sits somewhere between "by evidence" and
"equal", and closer to equal than this one.

This subsumes rather than contradicts the existing leading explanation. The sparse-filter test
(≥25% shoulder in 14% of runs at 7k particles, 8% at 35k, 0% at 140k) measures the variance of a
small filter; the roulette mechanism explains *why* the book's filter behaves like a small one in
the mode dimension regardless of how many trajectories it constructs. Note also that the book's
mode is a state element fixed per particle (Table 8.1, Assumption 3), never refreshed, so mode
diversity can only decay — it is never regenerated.

Caveat, stated rather than hidden: Eq. 8.2 defines w as the unnormalised product of likelihoods,
which is what makes the arithmetic above bite, but the book does not say explicitly whether η is
applied to that product or to a per-step or rescaled weight. If it is rescaled, the roulette
regime is less universal and this mechanism weakens, though the unit-weight promotion still
flattens the mix. Resolving it needs either the DSTG implementation or a reimplementation of the
branching filter.

**Testable without ambiguity:** implement the book's branching/pruning resampler as an
alternative sampler and run the same model through it. If the shoulder appears at 7M
trajectories with everything else held fixed, the sampler is the cause and no physical
explanation is needed. This is the single most decisive experiment available, and more
informative than further physical sensitivities.

## 6. On the 0.73 Mach floor, and what a wider one buys

The book's stated justification does not survive the recreation. Assumption 7 (p. 60): speeds are
limited to Mach 0.73–0.84 because fuel consumption is very inefficient above and "at lower speeds
the aircraft is not able to match the measurements". The second clause is contradicted here. Low
speeds do match the measurements in this implementation.

What the floor was actually doing is stated in Assumption 4 (p. 60): "Infinite fuel: the fuel
constraints on the aircraft can be applied to the pdf afterwards… Broad information about the
fuel consumption rate of the aircraft has been used to inform the range of allowable Mach
numbers." The floor is a stand-in for endurance — as
`decisions/fuel-performance-plan.md` already concluded: "the wide-Mach sensitivity revived the
shoulder with slow paths. Endurance is the missing constraint that Davey's 0.73 Mach floor stood
in for."

### The `mach-250kt` run

New sensitivity at Mach 0.41–0.86, chosen so that 250 kt true airspeed is reachable anywhere in
the 25,000–43,000 ft altitude prior (250 kt is Mach 0.415 at 25,000 ft and 0.436 at 43,000 ft;
`mach-wide`'s 0.50 floor bottoms out at 287–301 kt and cannot reach it).

| | base, 8 × 7M | `mach-250kt`, 4 × 7M | `mach-250kt`, 8 × 7M |
|---|---|---|---|
| P(34.5–36.5°S) | 0.0368 | 0.0865 | 0.0974 |
| overlap with book | 0.717 | 0.749 | 0.764 |
| median | 38.160°S | 38.004°S | 38.006°S |
| 95% interval | 35.880–39.533°S | 33.938–39.580°S | 33.859–39.577°S |
| split-half | 0.934 | 0.887 | 0.886 |
| P(Mach < 0.73) | 0.0000 | 0.1858 | — |

The shoulder roughly triples and the overlap with the published curve improves. Three
qualifications, all measured rather than assumed.

**It does not converge, and more replicates do not fix it.** Split-half overlap is 0.887 at four
replicates and 0.886 at eight — flat, against the 0.90 floor, while the base run reaches 0.934.
Per-replicate shoulder mass runs 0.075–0.125 across the eight seeds, and the replicate median
span *widens* from 0.188° to 0.253° as replicates are added. So the limiting quantity is not the
number of replicates but the resolution of each one. The reason is visible in the ancestry: the
34.5–36.5°S band holds 8.66M particles with a particle ESS of 4.4M, but only **13,412 distinct
prior draws** — about 1,700 independent root trajectories per replicate. Particle ESS is inflated
by resampled copies sharing ancestors; the Monte Carlo error on the shoulder is set by the root
count. Widening the Mach prior from 0.11 wide to 0.45 wide dilutes prior density about fourfold
while the paths that make the shoulder occupy a narrow band near Mach 0.69, so they are sampled
less densely exactly where they matter most. The fix is more particles per replicate, or a better
proposal at the two bottleneck epochs (m1839 at 2.2% ESS, m1941 at 1.0%) — `status.md`'s open
problem 2. **This run is not quotable as it stands.**

**The data does not want 250 kt.** P(TAS < 250 kt) = 0.001 and P(TAS < 300 kt) = 0.010. Within
the shoulder band the median Mach is 0.693 — about 400 kt at the band's median 37,000 ft — and
P(Mach < 0.73 | shoulder) = 0.83, reproducing the 84% recorded for `mach-wide`. The posterior
preference is for roughly Mach 0.69, not the floor. Widening from `mach-wide`'s 0.50 to 0.41 did
not raise the shoulder further (8.65% here against 10.6% recorded for `mach-wide` at the same
four replicates), so the effect saturates well above the new floor.

**At 00:19, most of the new shoulder is below the tabulated speed envelope.** This compares each
particle's Mach **at the 00:19 stopping state** against the **holding** Mach interpolated from the
Ulich/FPPM grid at that particle's own flight level — holding being the slowest speed the
aircraft is normally flown at, so a defensible public lower bound — bracketing gross weight
because the fuel state is not yet modelled.

Read it as a statement about the terminal state only. It is **not** a statement about sustained
cruise: Mach is redrawn uniformly from the range at every acceleration, so a path's speed varies
over the flight, and this compares one snapshot. A path decelerating into a controlled descent
*should* be below holding Mach at 00:19, so a low reading here is as consistent with a planned
approach as with an infeasible cruise. The trajectory-level version — the time-weighted fraction
of each path spent below the envelope, from the recorded manoeuvre histories and the 10-minute
route vertices — is the measurement that would separate those, and it has not been made yet.

| assumed gross weight | P(below holding Mach) | P(below holding \| shoulder) | median shoulder margin |
|---|---|---|---|
| 190 t | 0.120 | 0.563 | −0.017 |
| 200 t | 0.145 | 0.642 | −0.037 |
| 216 t | 0.181 | 0.737 | −0.063 |
| 230 t | 0.171 | 0.700 | −0.041 |

(74% of posterior mass falls inside the holding grid's usable cells at 190–216 t, 44% at 230 t;
Ulich's filler cells are excluded.) So at the plan's 216 t, roughly three quarters of the
shoulder this run recovers is, at 00:19, below the aircraft's own minimum-drag schedule by a
median of 0.063 Mach.

Two readings are open and this run cannot separate them: the paths are flying an infeasibly slow
cruise, or they are decelerating into a descent. Both put the 00:19 Mach below holding. Deciding
between them needs the trajectory-level measurement above, and the second reading is only
representable at all once the altitude floor is opened and vertical rate enters the BFO model
(§8) — at present a descent below 25,000 ft cannot be sampled and a descending particle is
scored as though level.

What is clear either way is that the wide-Mach shoulder is not yet an estimate. The 336–400 kt
the 18:25–18:28 BTOs prefer is a local, early-flight feature. The feasible speed prior — item 2
of the core change protocol, specified in `decisions/fuel-performance-plan.md` as "the envelope
from the tables plus a documented public buffet margin" — and the fuel likelihood are what turn
this upper bound into a number.

Read the `mach-250kt` shoulder as an **upper bound** on what slow flight can contribute, pending
the envelope and the fuel likelihood.

## 7. What the prior can and cannot generate

Speed, heading and altitude are **not** fixed over a flight. Three independent exponential clocks
(`next_turn`, `next_acceleration`, `next_climb`) share the time constant τ and are redrawn from
the Gibbs update after every resampling; at an acceleration the Mach target is redrawn uniformly
from the whole range, at a climb the altitude is redrawn in 1,000 ft steps, at a turn the control
angle changes by a uniform ±180°. Multi-manoeuvre paths are generated freely, and the posterior's
preference for few manoeuvres is inference, not a constraint — it is Davey's own explanation
(p. 92) that a sequence of random turns rarely cancels out when a straight path would fit.

Three limits are real, and all three matter for a piloted end-of-flight scenario:

- **The altitude floor is 25,000 ft** (`altitude_range_ft`, book p. 49). A descent begun before
  00:11, or any low-altitude leg, cannot be generated at all — it is excluded a priori rather
  than tested, which sits badly with `AGENTS.md` rule 6.
- **Vertical rate is absent from the BFO model** (book p. 50, stated explicitly). So even with
  the floor opened, a descending particle would be scored with a level-flight BFO: the descent
  would be unfalsifiable rather than tested, and 00:11 is exactly where a planned descent shows.
  This must land before, or with, any altitude change.
- **The three manoeuvre types are independent** (book p. 47: simultaneity is "not precluded but
  not favoured") and **turns are undirected**. A coordinated slow-turn-descend sequence therefore
  carries the product of three independent coincidences, and goal-directed flight is penalised
  relative to how likely a piloted scenario makes it. This is prior *shape*, so no amount of
  ensemble size fixes it.

## 8. Proposed changes, in order

1. **Parameters table in every report** — done; `report/davey_reference.json` and
   `report/parameters.py`, rendered as a page of every PDF and written as `parameters.csv`.
2. **Vertical rate into the state and the BFO model.** The line-of-sight vertical term is what
   makes a descent testable. Core change; split-half and the blind MH371 control after it.
3. **Altitude as a declared stratum, not a wider uniform prior.** Widening to 0–43,000 ft at a
   1,000 ft step turns 19 levels into 44 and halves the prior mass on every cruise level, spending
   particles on paths the 19:41–22:41 arcs reject. The engine already solves this for autopilot
   mode — five filters with a deliberately unequal allocation, combined by marginal likelihood.
   Add a `planned-descent` stratum carrying a descent-onset latent, with its own particle budget
   and declared prior, and report P(low at 00:11 | data) as a conditional beside the
   unconditional result. Floor the filter at 500 ft, the lowest node of the ERA5 grid; below that
   `locate()` clamps silently (§ "Observations", and the grid manifest's own contract), and the
   terminal stage already owns 500 ft to the surface. The recovered simulator points
   (`inputs/end-of-flight/2018-08-19-sim-extract.pdf`) motivate the support; they must not become
   evidence for it.
4. **One manoeuvre clock with a categorical over manoeuvre type**, replacing three independent
   clocks, with declared mass on the joint combinations (slow+descend, turn+slow,
   turn+slow+descend). This *nests* the book exactly: set the clock rate to 3/τ and the
   categorical to the three singletons at 1/3 each and Eq. 7.5's `exp(-3T/τ)` and `(τδ)^-N` are
   recovered identically, so `make regress` keeps a defined reference and the coordinated model
   becomes a labelled prior choice tested against it.
5. **A `piloted` stratum** flying a sampled flight plan under lateral navigation instead of
   random-walking through uniform turns. The machinery exists — there is a route-following unit
   test, and the turn clock is already suspended while a plan steers. What is missing is a prior
   over plans, which must stay independent of BTO/BFO (a documented reachable-waypoint set or a
   uniform prior over bearings) or the class will fit anything. Report its marginal likelihood,
   keep it a declared conditional.
6. **`bto-inflated`** — σ_BTO × 1.5, 2, 3, config only; bounds the largest untested physical
   lever. (§4)
7. **The book's branching resampler as an alternative sampler** — the decisive test of whether
   the shoulder gap is methodological rather than physical. (§5)
8. **Fuel endurance, then re-run the wide-Mach sensitivity with it.** (§6)
9. **Corridor-restricted weather comparison** along shoulder-bound paths, pending ACCESS-G. (§3)
10. **Fidelity fixes**: R600 σ 63 → 62 µs; manoeuvre step 5 s → 1 s. Not shoulder hypotheses. (§2)

Fuel belongs before the altitude work if the wide-Mach question is to be settled, since endurance
is what disciplines slow flight; items 2–3 are what make a planned descent representable at all.