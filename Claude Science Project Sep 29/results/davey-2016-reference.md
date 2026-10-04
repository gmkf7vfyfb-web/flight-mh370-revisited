# What Davey et al. (2016) actually specifies, and where this engine departs from it

The book was absent from the working tree for most of this project's life — `paper.pdf` is
gitignored and was never fetched — so a number of things had been inferred from secondary
sources and from the previous ChatGPT-era threads. It has now been obtained from the publisher
(see `.sources/davey-2016/README.md`). This note records what the original says, and audits the
engine against it. Page numbers are PDF pages of the 124-page Springer file.

## The convergence criterion: Davey published none that is quantitative

This was an open question in `results/split-half-threshold.md`, which could only observe that
the project's 0.90 split-half floor was asserted rather than derived and that "what Davey used
is not established". It is now established, and the answer is that he used nothing of the kind.

The phrase "effective sample size" does not occur in the book. Neither does "converged".
"Degeneracy" occurs once, in the generic description of particle filters (p. 30). There is no
split-half statistic, no ESS threshold, and no numerical convergence test anywhere in the text.

What the book does say is procedural (p. 70): rather than running a pre-specified number of
particles, they chose "to adaptively increase the number of particles used until it was possible
to identify an adequate number of likely paths". That is the criterion — a qualitative judgement
about the number of surviving high-weight trajectories, made by the analyst, not a statistic
with a threshold.

**Consequence for the paper.** The 0.90 floor cannot be attributed to Davey and should not be.
The honest statement is that the published work reports no quantitative convergence diagnostic,
that this project introduces one, and that the floor is calibrated against a converged reference
rather than inherited. The calibration in `split-half-threshold.md` stands on its own and is now
the only justification the number has — which is a stronger position than citing a precedent
that turns out not to exist.

## Table 8.2, and the engine audit

Table 8.2 (p. 73) is the authoritative parameter summary. Every row, against the engine's
`Parameters::default()` and `config/davey2016.toml`:

| Table 8.2 | published | engine | |
|---|---|---|---|
| Initial latitude s.d. | 0.4 arcmin † | 0.5 NM | matches Ch. 4, see below |
| Initial longitude s.d. | 0.4 arcmin † | 0.5 NM | matches Ch. 4, see below |
| Initial control Mach s.d. | Gaussian 0.03 † | uniform 0.73–0.84 | matches Ch. 4, see below |
| Initial control angle s.d. | 1° | 1.0° | matches |
| Initial BFO bias s.d. | 25 Hz | 25 Hz | matches |
| Initial Mach deviation s.d. | 0.00311 | 0.003113 (derived) | matches |
| Initial angle deviation s.d. | 0.0826° | 0.0826° (derived) | matches |
| Initial wind deviation s.d. | 5.68 kn | 5.684 kn (derived) | matches |
| Mach reversion β | 1.06 × 10⁻² | 1.058 × 10⁻² | matches |
| Mach noise q | 2.05 × 10⁻⁷ s⁻¹ | 2.05 × 10⁻⁷ | matches |
| Angle reversion β | 9.8 × 10⁻³ | 9.792 × 10⁻³ | matches |
| Angle noise q | 4.07 × 10⁻⁸ rad² s⁻¹ | 4.074 × 10⁻⁸ | matches |
| Wind reversion β | 1.09 × 10⁻³ | 1.087 × 10⁻³ | matches |
| Wind noise q | 7.02 × 10⁻² kn² s⁻¹ | 7.021 × 10⁻² | matches |
| Mean manoeuvre time τ | Jeffreys(0.1, 10) h | Jeffreys(0.1, 10) h | matches |
| New Mach | uniform 0.73–0.84 | uniform 0.73–0.84 | matches |
| Turn angle | uniform ±180° | uniform ±180° | matches |
| New altitude | uniform 25,000–43,000 ft | uniform 25,000–43,000 ft | matches |
| Branching rate n̄ | 3–10 | n/a | **structural**, see below |
| Likelihood threshold η | e⁻²⁵ or e⁻³⁰ | n/a | **structural**, see below |

The three initial *deviation* rows are not configured values in the engine; they are drawn from
the stationary distribution of the corresponding OU process, `sqrt(q / 2β)`. That they land on
Davey's tabulated figures to three significant figures is a real check on the OU constants, and
`crates/flight/src/lib.rs` already carries a test asserting it.

### † Table 8.2's "Initialisation" block is the validation setup, not the accident prior

An earlier revision of this note read the first three rows as specifications for the accident
flight and listed two of them as departures this engine should correct. That was wrong, and
Chapter 4 says so in plain words.

On the accident flight the prior is defined at the penultimate radar point, and p. 34 states:
"a prior was defined at 18:01 at the penultimate radar point using the output of the Kalman
filter described above. **The position standard deviations were set to 0.5 nm and the direction
standard deviation to 1°.**" Page 35 then states: "**An initial Mach number was selected from a
uniform prior between 0.73 and 0.84**; this was chosen on the basis of expert advice to ensure
that the required flight endurance is achievable."

Those are the engine's values exactly — 0.5 NM, 1°, uniform 0.73–0.84. Nothing to change.

Table 8.2's initialisation rows describe instead how the filter was started for the *validation*
flights, where it is initialised on known truth with Gaussian error. Chapter 9 confirms it
(p. 77): "The filter was initialised using the true aircraft location, speed and control angle
with a Gaussian random error. The standard deviation of the initialisation error was chosen to
be the same as the prior for the accident flight, that is 0.4° in latitude and longitude, 1° in
angle and Mach 0.03 in air speed."

Two cautions follow. First, Table 8.2 and p. 77 disagree with each other — 0.4 arcminutes against
0.4 degrees, a factor of sixty — so the table alone cannot be trusted on these rows and the
chapter text governs. Second, p. 77's claim that the validation initialisation is "the same as
the prior for the accident flight" is not consistent with Chapter 4 either, on either reading.
The accident-flight prior is the one Chapter 4 states, and that is what this engine implements.

The general lesson, worth keeping: **Table 8.2 is a summary, and where it conflicts with the
chapter that defines a quantity, the chapter wins.** The OU constants and manoeuvre rows in the
table are corroborated by Chapters 6 and 7 and are safe; the initialisation rows are not.

### The one genuine departure: resampling

The engine uses systematic resampling of a fixed population when ESS falls below half. Davey's
filter is also an SIR particle filter — p. 30 is explicit, "the filter used in this book is a
form of SIR particle filter" — but its resampling step is implemented differently. Sect. 8
describes a *branching* scheme over independently propagated trajectories: each particle is
treated separately, and at each step a particle with weight `w ≥ η` is duplicated into n̄
branches each carrying weight `w/n̄`, while a particle below the threshold survives with
probability `w` at weight 1 and is otherwise pruned. The book frames this explicitly as a way of
resampling, not as an alternative to it: "thus resampling can also be implemented through a
randomised branching procedure, recursively adapting the number of particles" (p. 70). The
weights are left unnormalised until the very end, and the population size is not fixed — it
grows and is pruned adaptively, which is what makes "increase particles until enough likely
paths appear" implementable.

They are explicit that this was chosen for exploration rather than efficiency: the scheme "is not
necessarily computationally efficient, but in this particular application it was more important
to broadly explore the enormous state space". Table 8.2 pins the constants we would need, n̄ in
3–10 and η at e⁻²⁵ or e⁻³⁰.

## Davey states this project's 19:41 problem, in advance

The passage at p. 69 is worth quoting against the three failed interventions:

> A problem with sampling from the dynamics is that this can be a very diffuse distribution. In
> the MH370 case, the model allows for turns and speed and altitude changes, and potentially
> several of each can be sampled between measurements. The proportion of particles that sample a
> trajectory close to the measurements will be small and a very large number of samples will be
> required to capture the high probability regions.

"Potentially several of each can be sampled between measurements" is quantifiable from Table
8.2's own τ prior. Over the 4,267 s leg into 19:41, with three manoeuvre clocks each of mean τ
and τ ~ Jeffreys(0.1, 10) h, the expected number of manoeuvres is **7.6** and the probability of
at least one is **83 %**. (An earlier version of `m1941-geometry-and-lookahead.md` quoted 56 %,
computed against a τ range of 1–20 h that is neither Davey's nor the engine's; the engine has
always used 0.1–10 h and the corrected figure is 83 %.)

That is the common cause of the look-ahead, bridge and rejuvenation failures, and the book
anticipates it. It also says what they did about it — branch wide and prune — which is neither
of the two families this project has tried.

## What this changes

1. The 0.90 split-half floor is ours, not Davey's, and the paper must say so.
2. The accident-flight prior needs **no** correction: 0.5 NM, 1° and uniform Mach 0.73–0.84 are
   Davey's own values from Chapter 4. Table 8.2's initialisation rows belong to the validation
   experiments and must not be applied here.
3. Davey's filter assumes **infinite fuel** (assumption 4, p. 74) and applies fuel constraints
   afterwards as a censor. This project's in-filter fuel model is an extension beyond the
   published method, not a reproduction of it, and should be presented that way.
4. The branching resampler moves from "an idea on the list" to "the published method we are not
   yet reproducing", with its constants known. It is the one remedy for the 19:41 bottleneck that
   has the original authors' endorsement.